#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件处理器模块

实现插件化的文件处理器架构，支持不同文件格式的处理。
"""

from .base import BaseProcessor
from .docx_processor import DocxProcessor

# 处理器注册表
PROCESSORS = {
    '.docx': DocxProcessor,
    '.doc': DocxProcessor,  # 使用相同的处理器
}

def get_processor(file_extension: str) -> BaseProcessor:
    """根据文件扩展名获取对应的处理器"""
    processor_class = PROCESSORS.get(file_extension.lower())
    if processor_class is None:
        raise ValueError(f"不支持的文件格式: {file_extension}")
    return processor_class()

def register_processor(file_extension: str, processor_class: type):
    """注册新的文件处理器"""
    PROCESSORS[file_extension.lower()] = processor_class

def get_supported_extensions() -> list:
    """获取支持的文件扩展名列表"""
    return list(PROCESSORS.keys())

__all__ = [
    "BaseProcessor",
    "DocxProcessor", 
    "get_processor",
    "register_processor",
    "get_supported_extensions",
    "PROCESSORS"
]
