#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本分析器模块

提供文本分析相关的功能，包括句子边界检测、标题识别等。
"""

from .text_analyzer import TextAnalyzer
from .structure_analyzer import StructureAnalyzer

__all__ = [
    "TextAnalyzer",
    "StructureAnalyzer"
]
