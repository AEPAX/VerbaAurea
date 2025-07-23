#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
语义分割器

基于语义结构和内容特征进行文档分割的策略实现。
"""

from typing import List, Dict, Any
from ..models.document import Document, ElementInfo
from ..models.config import ProcessingConfig
from ..analyzers.text_analyzer import TextAnalyzer
from .base_splitter import BaseSplitter


class SemanticSplitter(BaseSplitter):
    """语义分割器"""
    
    def __init__(self, config: ProcessingConfig):
        """初始化语义分割器"""
        super().__init__(config)
        self.text_analyzer = TextAnalyzer(config)
    
    @property
    def splitter_name(self) -> str:
        """返回分割器名称"""
        return "SemanticSplitter"
    
    def find_split_points(self, document: Document) -> List[int]:
        """找到文档的分割点"""
        if not document.elements:
            return []
        
        split_points = []
        current_length = 0
        
        for i, element in enumerate(document.elements):
            current_length += element.length
            
            # 检查是否应该在此处分割
            if self._should_split_here(element, current_length, i, document):
                split_points.append(i + 1)  # 在下一个元素前分割
                current_length = 0
        
        # 优化分割点
        refined_points = self.refine_split_points(document, split_points)
        
        # 合并标题与正文
        final_points = self._merge_heading_with_body(document, refined_points)
        
        return final_points
    
    def _should_split_here(
        self, 
        element: ElementInfo, 
        current_length: int, 
        position: int, 
        document: Document
    ) -> bool:
        """判断是否应该在此处分割"""
        # 获取下一个元素
        next_element = None
        if position + 1 < len(document.elements):
            next_element = document.elements[position + 1]
        
        # 检查基本分割条件
        if not self.is_valid_split_point(element, current_length, next_element):
            return False
        
        # 计算分割评分
        score = self.calculate_split_score(element, current_length, position, len(document.elements))
        
        # 应用句子完整性权重
        if not element.ends_with_period:
            score -= self.config.document_settings.sentence_integrity_weight
        
        # 检查是否达到分割阈值
        if score >= self.config.advanced_settings.min_split_score:
            return True
        
        # 强制分割条件
        if current_length > self.config.document_settings.max_length * 1.5:
            return True
        
        # 标题前强制分割
        if (next_element and next_element.is_heading and 
            self.config.advanced_settings.force_split_before_heading):
            return True
        
        return False
    
    def _merge_heading_with_body(self, document: Document, split_points: List[int]) -> List[int]:
        """合并标题与正文，避免孤立的标题"""
        if not split_points:
            return split_points
        
        merged_points = []
        
        for point in split_points:
            # 检查分割点是否会产生孤立的标题
            if self._would_create_isolated_heading(document, point):
                # 尝试向后移动分割点
                new_point = self._find_next_suitable_point(document, point)
                if new_point != -1:
                    merged_points.append(new_point)
                # 如果找不到合适的点，跳过这个分割点
            else:
                merged_points.append(point)
        
        return sorted(list(set(merged_points)))
    
    def _would_create_isolated_heading(self, document: Document, split_point: int) -> bool:
        """检查分割点是否会创建孤立的标题"""
        if split_point >= len(document.elements):
            return False
        
        # 检查分割点后的第一个元素是否为标题
        if document.elements[split_point].is_heading:
            # 检查标题后是否紧跟另一个分割点
            next_split_distance = self._distance_to_next_split(document, split_point)
            if next_split_distance <= 2:  # 标题后很快又分割，可能产生孤立标题
                return True
        
        return False
    
    def _distance_to_next_split(self, document: Document, current_point: int) -> int:
        """计算到下一个可能分割点的距离"""
        # 这里简化实现，实际可以更复杂
        for i in range(current_point + 1, min(current_point + 5, len(document.elements))):
            element = document.elements[i]
            if element.is_heading or element.ends_with_period:
                return i - current_point
        return float('inf')
    
    def _find_next_suitable_point(self, document: Document, start_point: int) -> int:
        """寻找下一个合适的分割点"""
        search_limit = min(start_point + 10, len(document.elements))
        
        for i in range(start_point + 1, search_limit):
            element = document.elements[i]
            
            # 寻找句子结束点
            if element.ends_with_period and not element.is_heading:
                return i + 1
        
        return -1
    
    def calculate_split_score(
        self, 
        element: ElementInfo, 
        current_length: int, 
        position: int,
        total_elements: int
    ) -> float:
        """计算分割点的评分（重写以添加语义特征）"""
        # 调用基类方法获取基础评分
        score = super().calculate_split_score(element, current_length, position, total_elements)
        
        # 添加语义特征评分
        
        # 段落类型奖励
        if element.type == 'para':
            score += 1.0
        elif element.type == 'table':
            score += 2.0  # 表格通常是好的分割点
        
        # 图片处理
        if element.has_images:
            score += 1.5  # 包含图片的段落通常是重要内容
        
        # 列表项处理
        if element.is_list_item:
            score -= 2.0  # 避免在列表中间分割
        
        # 位置评分
        position_ratio = position / total_elements if total_elements > 0 else 0
        if 0.1 < position_ratio < 0.9:  # 避免在文档开头或结尾分割
            score += 0.5
        
        return score
