#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
并行处理模块
使用多进程技术实现真正的并行处理，突破GIL限制，充分利用多核CPU
"""

import os
import sys
import time
import traceback
from multiprocessing import Pool, cpu_count, Manager
from utils import get_script_dir, setup_logger, log_error, log_info, log_warning

# 设置日志记录器
import logging
_logger = logging.getLogger('VerbaAurea')


def collect_files_to_process(config):

    """收集需要处理的文件列表"""
    # 获取脚本当前路径
    current_dir = get_script_dir()

    # 创建输出目录
    output_folder = config["processing_options"]["output_folder"]
    output_base_dir = os.path.join(current_dir, output_folder)
    os.makedirs(output_base_dir, exist_ok=True)

    files_to_process = []

    # 遍历当前目录及子目录
    for root, dirs, files in os.walk(current_dir):
        # 跳过输出文件夹和跳过隐藏目录
        if output_folder in root or os.path.basename(root).startswith('.'):
            continue

        # 创建相对路径
        rel_path = os.path.relpath(root, current_dir)
        if rel_path == ".":  # 当前目录
            rel_path = ""

        # 收集当前目录下的所有Word文档和PDF文档
        for file in files:
            if file.endswith(('.docx', '.doc', '.pdf')) and not file.startswith('~$'):  # 排除临时文件
                # 构建输入和输出路径
                input_path = os.path.join(root, file)

                # 构建输出路径，保持原始目录结构
                if rel_path:
                    output_dir = os.path.join(output_base_dir, rel_path)
                    os.makedirs(output_dir, exist_ok=True)
                else:
                    output_dir = output_base_dir

                # 如果输入是PDF，输出应该是DOCX格式
                if file.lower().endswith('.pdf'):
                    output_filename = os.path.splitext(file)[0] + '.docx'
                else:
                    output_filename = file
                
                output_path = os.path.join(output_dir, output_filename)

                # 添加到待处理文件列表
                files_to_process.append((input_path, output_path))

    return files_to_process


def _process_file(args):
    """
    处理单个文件的工作函数
    避免顶层导入，在函数内部导入document_processor
    """
    input_path, output_path, config = args

    # 将导入放在函数内部，避免循环导入问题
    try:
        # 导入处理模块
        from document_processor import insert_split_markers

        # 处理文件
        success = insert_split_markers(input_path, output_path, config)
        
        # 如果处理失败但没有抛出异常，记录到日志
        if not success:
            error_msg = "处理失败: insert_split_markers返回False"
            log_error(_logger, input_path, error_msg, "ProcessingError")
        
        return {
            'input_path': input_path,
            'output_path': output_path,
            'success': success,
            'error': None if success else error_msg
        }
    except Exception as e:
        # 记录错误信息
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"处理文件 {input_path} 时出错: {error_msg}")
        # 记录到日志文件
        log_error(_logger, input_path, e, type(e).__name__, traceback.format_exc())
        return {
            'input_path': input_path,
            'output_path': output_path,
            'success': False,
            'error': error_msg
        }


def _process_batch(batch_args):
    """处理一批文件，减少进程创建开销"""
    batch_files, config = batch_args
    results = []

    for input_path, output_path in batch_files:
        try:
            # 导入处理模块
            from document_processor import insert_split_markers

            # 处理文件
            success = insert_split_markers(input_path, output_path, config)
            
            # 如果处理失败但没有抛出异常，记录到日志
            if not success:
                error_msg = "处理失败: insert_split_markers返回False"
                log_error(_logger, input_path, error_msg, "ProcessingError")
            
            results.append({
                'input_path': input_path,
                'output_path': output_path,
                'success': success,
                'error': None if success else error_msg
            })
        except Exception as e:
            # 记录错误信息
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"处理文件 {input_path} 时出错: {error_msg}")
            # 记录到日志文件
            log_error(_logger, input_path, e, type(e).__name__, traceback.format_exc())
            results.append({
                'input_path': input_path,
                'output_path': output_path,
                'success': False,
                'error': error_msg
            })

    return results


def process_all_documents(config):
    """
    并行处理所有Word文档
    使用多进程处理以突破GIL限制
    """
    debug_mode = config["processing_options"].get("debug_mode", False)

    # 收集需要处理的文件
    files_to_process = collect_files_to_process(config)
    total_files = len(files_to_process)

    if total_files == 0:
        log_info(_logger, "没有找到需要处理的文档（支持.docx、.doc和.pdf格式）")
        return 0, 0, []

    # 获取性能设置
    perf_settings = config.get("performance_settings", {})
    use_parallel = perf_settings.get("parallel_processing", True)

    # 如果不使用并行，则顺序处理
    if not use_parallel:
        return process_sequentially(config)

    # 确定工作进程数
    num_workers = perf_settings.get("num_workers", 0)
    if num_workers <= 0:
        num_workers = max(1, cpu_count() - 1)  # 默认使用CPU核心数-1

    # 为避免过多进程带来的开销，根据文件数量调整工作进程数
    num_workers = min(num_workers, max(1, total_files), 8)

    # 批处理大小
    batch_size = perf_settings.get("batch_size", 1)
    use_batch = batch_size > 1

    log_info(_logger, f"启用{'批处理' if use_batch else ''}多进程并行处理，使用 {num_workers} 个工作进程")

    processed_files = 0
    failed_files = []

    try:
        if use_batch:
            # 批处理模式
            batches = []
            current_batch = []

            # 将文件分组为批次
            for file_pair in files_to_process:
                current_batch.append(file_pair)
                if len(current_batch) >= batch_size:
                    batches.append((current_batch.copy(), config))
                    current_batch = []

            if current_batch:  # 添加最后一个不完整的批次
                batches.append((current_batch.copy(), config))

            with Pool(processes=num_workers) as pool:
                # 使用进程池处理批次
                for batch_results in pool.imap(_process_batch, batches):
                    for result in batch_results:
                        if result['success']:
                            processed_files += 1
                        else:
                            failed_files.append(result['input_path'])
                            # 如果result中有error信息，也记录到日志
                            if result.get('error'):
                                log_error(_logger, result['input_path'], result['error'], "ProcessingError")
        else:
            # 单文件处理模式
            work_items = [(input_path, output_path, config) for input_path, output_path in files_to_process]

            with Pool(processes=num_workers) as pool:
                for result in pool.imap(_process_file, work_items):
                    if result['success']:
                        processed_files += 1
                    else:
                        failed_files.append(result['input_path'])
                        # 如果result中有error信息，也记录到日志
                        if result.get('error'):
                            log_error(_logger, result['input_path'], result['error'], "ProcessingError")
                        # 如果result中有error信息，也记录到日志
                        if result.get('error'):
                            log_error(_logger, result['input_path'], result['error'], "ProcessingError")

    except Exception as e:
        log_error(_logger, "并行处理", e, type(e).__name__, traceback.format_exc())

    return total_files, processed_files, failed_files


def process_sequentially(config):
    """顺序处理所有Word文档（非并行方式）"""
    debug_mode = config["processing_options"].get("debug_mode", False)

    # 收集所有需要处理的文件
    files_to_process = collect_files_to_process(config)
    total_files = len(files_to_process)

    if total_files == 0:
        log_info(_logger, "没有找到需要处理的文档（支持.docx、.doc和.pdf格式）")
        return 0, 0, []

    # 将导入移到函数内部，避免循环导入
    from document_processor import insert_split_markers

    log_info(_logger, f"使用单线程顺序处理 {total_files} 个文件")

    processed_files = 0
    failed_files = []

    # 顺序处理文件
    for i, (input_path, output_path) in enumerate(files_to_process):
        try:
            # 处理文件
            result = insert_split_markers(input_path, output_path, config)

            if result:
                processed_files += 1
            else:
                failed_files.append(input_path)
                # 记录到日志
                error_msg = "处理失败: insert_split_markers返回False"
                log_error(_logger, input_path, error_msg, "ProcessingError")

            # 显示进度
            progress = (i + 1) / total_files * 100
            status = "成功" if result else "失败"
            log_info(_logger, f"进度: [{i + 1}/{total_files}] {progress:.1f}% - {os.path.basename(input_path)} {status}")

        except Exception as e:
            error_msg = f"处理 {input_path} 时出错: {str(e)}"
            print(error_msg)
            # 记录到日志文件
            log_error(_logger, input_path, e, type(e).__name__, traceback.format_exc())
            failed_files.append(input_path)

    return total_files, processed_files, failed_files