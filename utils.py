#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具函数模块
统一日志系统（单 logger + handler 分流）
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path


# =========================
# 基础工具
# =========================

def get_script_dir():
    """获取脚本当前路径"""
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    if not current_dir:
        current_dir = os.getcwd()
    return current_dir


def check_dependencies():
    """检查必要的依赖库"""
    required_libs = ['nltk', 'jieba', 'python-docx']
    missing_libs = []

    for lib in required_libs:
        try:
            if lib == 'python-docx':
                __import__('docx')
            else:
                __import__(lib)
        except ImportError:
            missing_libs.append(lib)

    if missing_libs:
        print(f"\n警告: 未安装以下库: {', '.join(missing_libs)}")
        for lib in missing_libs:
            print(f"  pip install {lib}")
        print()

    return not missing_libs


def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        return f"{int(seconds // 60)}分{int(seconds % 60)}秒"
    else:
        return f"{int(seconds // 3600)}时{int((seconds % 3600) // 60)}分{int(seconds % 60)}秒"


def get_file_size(file_path):
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except Exception:
        return 0


# =========================
# 日志系统（核心）
# =========================

def setup_logger(log_dir='logs', level=logging.INFO):
    """
    初始化全局唯一 logger：VerbaAurea
    - INFO+ → verbaaurea.log
    - ERROR → verbaaurea.log + verbaaurea_error.log
    """
    logger = logging.getLogger('VerbaAurea')

    # 已初始化直接返回（防止重复 handler）
    if getattr(logger, "_initialized", False):
        return logger

    logger.setLevel(level)
    logger.propagate = False

    Path(log_dir).mkdir(exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )

    # ===== 主日志（INFO+）=====
    main_handler = logging.FileHandler(
        Path(log_dir) / 'verbaaurea.log',
        encoding='utf-8'
    )
    main_handler.setLevel(logging.INFO)
    main_handler.setFormatter(formatter)

    # ===== 错误日志（ERROR only，自动复制）=====
    error_handler = logging.FileHandler(
        Path(log_dir) / 'verbaaurea_error.log',
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # ===== 控制台 =====
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    logger.addHandler(main_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    logger._initialized = True
    return logger


# =========================
# 日志封装（你项目里用的）
# =========================

def log_info(logger, message):
    if logger:
        logger.info(message)


def log_warning(logger, message):
    if logger:
        logger.warning(message)


def log_debug(logger, message):
    if logger:
        logger.debug(message)


def log_error(logger, file_path, error, error_type=None, traceback_str=None):
    """
    统一错误日志入口（只写一次）
    ERROR 会自动进入：
    - verbaaurea.log
    - verbaaurea_error.log
    """
    try:
        file_name = os.path.basename(file_path) if file_path else "未知文件"
        error_msg = str(error) if error else "未知错误"
        error_type = error_type or type(error).__name__

        log_message = (
            f"处理文件失败: {file_name}\n"
            f"  文件路径: {file_path}\n"
            f"  错误类型: {error_type}\n"
            f"  错误信息: {error_msg}"
        )

        if traceback_str:
            log_message += f"\n  堆栈跟踪:\n{traceback_str}"

        if logger:
            logger.error(log_message)

    except Exception as e:
        print(f"日志记录失败: {e}")


# =========================
# 日志文件路径获取（可选）
# =========================

def get_log_file_path():
    try:
        logger = logging.getLogger('VerbaAurea')
        for h in logger.handlers:
            if isinstance(h, logging.FileHandler) and h.level <= logging.INFO:
                return h.baseFilename
    except Exception:
        pass
    return None


def get_error_log_file_path():
    try:
        logger = logging.getLogger('VerbaAurea')
        for h in logger.handlers:
            if isinstance(h, logging.FileHandler) and h.level == logging.ERROR:
                return h.baseFilename
    except Exception:
        pass
    return None
