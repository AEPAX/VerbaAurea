#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VerbaAurea - 智能文档预处理工具

将原始文档转化为"黄金"般的知识，为知识库构建提供高质量的文本数据。
专注于文档智能分割，确保语义完整性，为知识库检索和大语言模型微调提供优质素材。
"""

__version__ = "1.0.0"
__author__ = "VerbaAurea Team"
__description__ = "智能文档预处理工具 - 为知识库构建提供高质量的文档切分服务"

# 导出主要接口
from .services.document_service import DocumentService
from .core.models.document import Document, ProcessingResult
from .config.settings import Settings

__all__ = [
    "DocumentService",
    "Document", 
    "ProcessingResult",
    "Settings",
    "__version__",
    "__author__",
    "__description__"
]
