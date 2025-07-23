#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分割策略模块

实现不同的文档分割策略，支持可配置的分割算法。
"""

from .base_splitter import BaseSplitter
from .semantic_splitter import SemanticSplitter

__all__ = [
    "BaseSplitter",
    "SemanticSplitter"
]
