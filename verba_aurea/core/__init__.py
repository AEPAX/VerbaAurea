#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
核心业务逻辑层

包含文档处理的核心算法和业务逻辑，独立于具体的接口实现。
"""

from .processors.base import BaseProcessor
from .models.document import Document, ProcessingResult

__all__ = [
    "BaseProcessor",
    "Document",
    "ProcessingResult"
]
