#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
核心数据模型

定义文档处理过程中使用的核心数据结构。
"""

from .document import Document, ProcessingResult, ElementInfo
from .config import ProcessingConfig

__all__ = [
    "Document",
    "ProcessingResult", 
    "ElementInfo",
    "ProcessingConfig"
]
