#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具函数模块
包含各种辅助函数
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path


def get_script_dir():
    """获取脚本当前路径"""
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    if not current_dir:  # 如果为空，使用当前工作目录
        current_dir = os.getcwd()
    return current_dir


def check_dependencies():
    """检查必要的依赖库"""
    required_libs = ['nltk', 'jieba', 'python-docx']
    missing_libs = []

    for lib in required_libs:
        try:
            # 特殊处理 python-docx (import名称是docx)
            if lib == 'python-docx':
                __import__('docx')
            else:
                __import__(lib)
        except ImportError:
            if lib == 'python-docx':
                missing_libs.append('python-docx')
            else:
                missing_libs.append(lib)

    if missing_libs:
        print(f"\n警告: 未安装以下库: {', '.join(missing_libs)}")
        print("为获得最佳分割效果，建议安装这些库:")
        for lib in missing_libs:
            print(f"  pip install {lib}")
        print()

    return len(missing_libs) == 0


def format_time(seconds):
    """格式化时间，将秒数转为人类可读形式"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)}分{int(remaining_seconds)}秒"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        return f"{int(hours)}时{int(minutes)}分{int(remaining_seconds)}秒"


def get_file_size(file_path):
    """获取文件大小（MB）"""
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except:
        return 0


def get_timestamped_log_name(base_name='verbaaurea', extension='.log'):
    """
    生成带时间戳的日志文件名

    Args:
        base_name: 日志文件基础名称
        extension: 文件扩展名

    Returns:
        带时间戳的文件名，格式: base_name_YYYY-MM-DD_HH-MM-SS.extension
    """
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return f"{base_name}_{timestamp}{extension}"


def setup_logger(log_dir='logs', log_name=None, level=logging.INFO):
    """
    设置日志记录器
    返回配置好的logger对象

    Args:
        log_dir: 日志目录
        log_name: 日志文件名，如果为None则自动生成带时间戳的文件名
        level: 日志级别，默认INFO
    """
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # 如果没有指定文件名，生成带时间戳的文件名
    if log_name is None:
        log_name = get_timestamped_log_name('verbaaurea', '.log')

    # 日志文件路径
    log_file = log_path / log_name

    # 配置日志格式
    log_format = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # 创建logger
    logger = logging.getLogger('VerbaAurea')
    logger.setLevel(level)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 文件handler - 记录到文件（记录所有级别）
    file_handler = logging.FileHandler(
        log_file,
        mode='a',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 控制台handler - 输出到控制台（只显示WARNING及以上）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)  # 控制台只显示警告和错误
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 保存日志文件路径到logger对象，方便后续获取
    logger.log_file_path = str(log_file)

    return logger


def setup_error_logger(log_dir='logs', log_name=None):
    """
    设置错误日志记录器（只记录ERROR级别）
    返回配置好的logger对象

    Args:
        log_dir: 日志目录
        log_name: 日志文件名，如果为None则自动生成带时间戳的文件名
    """
    # 如果没有指定文件名，生成带时间戳的错误日志文件名
    if log_name is None:
        log_name = get_timestamped_log_name('verbaaurea_error', '.log')

    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # 日志文件路径
    log_file = log_path / log_name

    # 配置日志格式
    log_format = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # 创建独立的错误logger
    error_logger = logging.getLogger('VerbaAureaError')
    error_logger.setLevel(logging.ERROR)

    # 避免重复添加handler
    if error_logger.handlers:
        return error_logger

    # 文件handler - 只记录ERROR级别
    file_handler = logging.FileHandler(
        log_file,
        mode='a',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.ERROR)
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)
    error_logger.addHandler(file_handler)

    # 控制台handler - 输出ERROR到控制台
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.ERROR)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    error_logger.addHandler(console_handler)

    # 保存日志文件路径到logger对象
    error_logger.log_file_path = str(log_file)

    return error_logger


# 全局错误日志记录器
_error_logger = None


def get_error_logger():
    """获取错误日志记录器（单例模式）"""
    global _error_logger
    if _error_logger is None:
        _error_logger = setup_error_logger()
    return _error_logger


def log_error(logger, file_path, error, error_type=None, traceback_str=None):
    """
    记录错误信息到日志文件（同时记录到主日志和错误日志）

    Args:
        logger: 主日志记录器对象
        file_path: 出错的文件路径
        error: 错误对象或错误消息
        error_type: 错误类型（可选）
        traceback_str: 堆栈跟踪字符串（可选）
    """
    try:
        file_name = os.path.basename(file_path) if file_path else "未知文件"
        error_msg = str(error) if error else "未知错误"
        error_type = error_type or type(error).__name__ if hasattr(error, '__name__') else "Exception"

        # 构建详细错误消息
        log_message = f"处理文件失败: {file_name}\n"
        log_message += f"  文件路径: {file_path}\n"
        log_message += f"  错误类型: {error_type}\n"
        log_message += f"  错误信息: {error_msg}"

        if traceback_str:
            log_message += f"\n  堆栈跟踪:\n{traceback_str}"

        # 记录到主日志（如果存在）
        if logger:
            logger.error(log_message)

        # 同时记录到错误日志
        error_logger = get_error_logger()
        if error_logger:
            error_logger.error(log_message)

    except Exception as e:
        # 如果日志记录本身出错，至少打印到控制台
        print(f"日志记录失败: {str(e)}")


def log_info(logger, message):
    """记录INFO级别日志"""
    if logger:
        logger.info(message)


def log_warning(logger, message):
    """记录WARNING级别日志"""
    if logger:
        logger.warning(message)


def log_debug(logger, message):
    """记录DEBUG级别日志"""
    if logger:
        logger.debug(message)


def get_log_file_path(logger=None):
    """
    获取当前日志文件路径

    Args:
        logger: 日志记录器对象，如果为None则尝试获取默认logger

    Returns:
        日志文件路径，如果无法获取则返回None
    """
    if logger and hasattr(logger, 'log_file_path'):
        return logger.log_file_path

    # 尝试从全局logger获取
    try:
        default_logger = logging.getLogger('VerbaAurea')
        if default_logger.handlers:
            for handler in default_logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    return handler.baseFilename
    except:
        pass

    return None


def get_error_log_file_path():
    """
    获取当前错误日志文件路径

    Returns:
        错误日志文件路径，如果无法获取则返回None
    """
    try:
        error_logger = get_error_logger()
        if error_logger and hasattr(error_logger, 'log_file_path'):
            return error_logger.log_file_path

        # 尝试从错误logger获取
        error_logger = logging.getLogger('VerbaAureaError')
        if error_logger.handlers:
            for handler in error_logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    return handler.baseFilename
    except:
        pass

    return None