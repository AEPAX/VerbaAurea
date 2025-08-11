#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具函数模块
包含各种辅助函数
"""

import os
import sys


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