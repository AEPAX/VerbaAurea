#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文档相关数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class ElementInfo:
    """文档元素信息"""
    type: str  # 'para', 'table', 'image'
    index: int  # 在文档中的索引
    text: str  # 文本内容
    length: int  # 长度（包含权重计算）
    base_text_length: int  # 纯文本长度
    is_heading: bool = False  # 是否为标题
    is_list_item: bool = False  # 是否为列表项
    ends_with_period: bool = False  # 是否以句号结尾
    has_images: bool = False  # 是否包含图片
    image_count: int = 0  # 图片数量
    image_info: List[Dict[str, Any]] = field(default_factory=list)  # 图片详细信息
    table_info: Optional[Dict[str, Any]] = None  # 表格信息


@dataclass
class ProcessingResult:
    """文档处理结果"""
    success: bool
    message: str
    split_count: int = 0
    processing_time: float = 0.0
    file_size_before: int = 0
    file_size_after: int = 0
    elements_stats: Dict[str, int] = field(default_factory=dict)
    split_points: List[int] = field(default_factory=list)
    error_details: Optional[str] = None


@dataclass
class Document:
    """文档数据模型"""
    file_path: Path
    elements: List[ElementInfo] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_elements(self) -> int:
        """总元素数量"""
        return len(self.elements)
    
    @property
    def paragraph_count(self) -> int:
        """段落数量"""
        return sum(1 for elem in self.elements if elem.type == 'para')
    
    @property
    def table_count(self) -> int:
        """表格数量"""
        return sum(1 for elem in self.elements if elem.type == 'table')
    
    @property
    def image_count(self) -> int:
        """图片数量"""
        return sum(elem.image_count for elem in self.elements)
    
    @property
    def total_text_length(self) -> int:
        """总文本长度"""
        return sum(elem.base_text_length for elem in self.elements)
    
    @property
    def total_weighted_length(self) -> int:
        """总加权长度"""
        return sum(elem.length for elem in self.elements)
