#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
处理服务

提供高级的处理协调功能，包括并行处理、进度跟踪等。
"""

import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count

from ..core.models.document import ProcessingResult
from ..core.models.config import ProcessingConfig
from ..config.settings import Settings
from .document_service import DocumentService


class ProcessingService:
    """处理服务"""
    
    def __init__(self, settings: Optional[Settings] = None):
        """初始化处理服务"""
        self.settings = settings or Settings()
        self.document_service = DocumentService(settings)
    
    def process_files_parallel(
        self,
        input_files: List[Path],
        config: Optional[ProcessingConfig] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, ProcessingResult]:
        """并行处理多个文件"""
        if config is None:
            config = self.settings.get_config()
        
        if not config.performance_settings.parallel_processing:
            return self._process_files_sequential(input_files, config, progress_callback)
        
        # 确定工作进程数
        num_workers = config.performance_settings.num_workers
        if num_workers <= 0:
            num_workers = max(1, cpu_count() - 1)
        
        results = {}
        completed = 0
        total = len(input_files)
        
        # 使用进程池处理
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            # 提交任务
            future_to_file = {
                executor.submit(self._process_single_file, file_path, config): file_path
                for file_path in input_files
            }
            
            # 收集结果
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                completed += 1
                
                try:
                    result = future.result()
                    results[str(file_path)] = result
                except Exception as e:
                    results[str(file_path)] = ProcessingResult(
                        success=False,
                        message=f"处理失败: {str(e)}",
                        error_details=str(e)
                    )
                
                # 调用进度回调
                if progress_callback:
                    progress_callback(completed, total)
        
        return results
    
    def process_files_batch(
        self,
        input_files: List[Path],
        config: Optional[ProcessingConfig] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, ProcessingResult]:
        """批量处理文件（按批次分组）"""
        if config is None:
            config = self.settings.get_config()
        
        batch_size = config.performance_settings.batch_size
        results = {}
        total = len(input_files)
        completed = 0
        
        # 分批处理
        for i in range(0, len(input_files), batch_size):
            batch = input_files[i:i + batch_size]
            
            if config.performance_settings.parallel_processing:
                batch_results = self.process_files_parallel(batch, config)
            else:
                batch_results = self._process_files_sequential(batch, config)
            
            results.update(batch_results)
            completed += len(batch)
            
            # 调用进度回调
            if progress_callback:
                progress_callback(completed, total)
        
        return results
    
    def process_directory_with_progress(
        self,
        input_dir: Path,
        config: Optional[ProcessingConfig] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """处理目录并提供进度反馈"""
        if config is None:
            config = self.settings.get_config()
        
        start_time = time.time()
        
        # 收集文件
        files_to_process = self.document_service._collect_files(input_dir, recursive=True)
        
        if not files_to_process:
            return {
                'results': {},
                'summary': {
                    'total_files': 0,
                    'processed_files': 0,
                    'failed_files': 0,
                    'processing_time': 0.0,
                    'files_per_second': 0.0
                }
            }
        
        # 处理文件
        results = self.process_files_batch(files_to_process, config, progress_callback)
        
        # 计算统计信息
        processing_time = time.time() - start_time
        total_files = len(results)
        processed_files = sum(1 for r in results.values() if r.success)
        failed_files = total_files - processed_files
        files_per_second = total_files / processing_time if processing_time > 0 else 0
        
        return {
            'results': results,
            'summary': {
                'total_files': total_files,
                'processed_files': processed_files,
                'failed_files': failed_files,
                'processing_time': processing_time,
                'files_per_second': files_per_second
            }
        }
    
    def _process_files_sequential(
        self,
        input_files: List[Path],
        config: ProcessingConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, ProcessingResult]:
        """顺序处理文件"""
        results = {}
        total = len(input_files)
        
        for i, file_path in enumerate(input_files):
            try:
                result = self.document_service.process_document(file_path, config=config)
                results[str(file_path)] = result
            except Exception as e:
                results[str(file_path)] = ProcessingResult(
                    success=False,
                    message=f"处理失败: {str(e)}",
                    error_details=str(e)
                )
            
            # 调用进度回调
            if progress_callback:
                progress_callback(i + 1, total)
        
        return results
    
    def _process_single_file(self, file_path: Path, config: ProcessingConfig) -> ProcessingResult:
        """处理单个文件（用于多进程）"""
        try:
            # 在子进程中创建新的服务实例
            document_service = DocumentService()
            return document_service.process_document(file_path, config=config)
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"处理失败: {str(e)}",
                error_details=str(e)
            )
    
    def estimate_processing_time(
        self,
        input_files: List[Path],
        config: Optional[ProcessingConfig] = None
    ) -> Dict[str, float]:
        """估算处理时间"""
        if config is None:
            config = self.settings.get_config()
        
        # 基于文件大小的简单估算
        estimates = {}
        
        for file_path in input_files:
            try:
                file_size = file_path.stat().st_size
                # 简单的线性估算：每MB大约需要0.1秒
                estimated_time = (file_size / (1024 * 1024)) * 0.1
                
                # 考虑并行处理的加速
                if config.performance_settings.parallel_processing:
                    num_workers = config.performance_settings.num_workers or max(1, cpu_count() - 1)
                    estimated_time /= min(num_workers, len(input_files))
                
                estimates[str(file_path)] = estimated_time
            
            except Exception:
                estimates[str(file_path)] = 1.0  # 默认估算1秒
        
        return estimates
    
    def get_processing_statistics(self, results: Dict[str, ProcessingResult]) -> Dict[str, Any]:
        """获取处理统计信息"""
        total_files = len(results)
        successful_files = sum(1 for r in results.values() if r.success)
        failed_files = total_files - successful_files
        
        total_processing_time = sum(r.processing_time for r in results.values())
        total_split_count = sum(r.split_count for r in results.values() if r.success)
        
        avg_processing_time = total_processing_time / total_files if total_files > 0 else 0
        avg_split_count = total_split_count / successful_files if successful_files > 0 else 0
        
        return {
            'total_files': total_files,
            'successful_files': successful_files,
            'failed_files': failed_files,
            'success_rate': successful_files / total_files if total_files > 0 else 0,
            'total_processing_time': total_processing_time,
            'average_processing_time': avg_processing_time,
            'total_split_count': total_split_count,
            'average_split_count': avg_split_count,
            'files_per_second': total_files / total_processing_time if total_processing_time > 0 else 0
        }
