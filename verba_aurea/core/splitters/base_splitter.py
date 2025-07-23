#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分割策略抽象基类

定义文档分割策略的统一接口。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..models.document import Document, ElementInfo
from ..models.config import ProcessingConfig


class BaseSplitter(ABC):
    """分割策略抽象基类"""
    
    def __init__(self, config: ProcessingConfig):
        """初始化分割器"""
        self.config = config
    
    @property
    @abstractmethod
    def splitter_name(self) -> str:
        """返回分割器名称"""
        pass
    
    @abstractmethod
    def find_split_points(self, document: Document) -> List[int]:
        """找到文档的分割点"""
        pass
    
    def calculate_split_score(
        self, 
        element: ElementInfo, 
        current_length: int, 
        position: int,
        total_elements: int
    ) -> float:
        """计算分割点的评分"""
        score = 0.0
        
        # 基础评分
        if element.is_heading:
            score += self.config.advanced_settings.heading_score_bonus
        
        if element.ends_with_period:
            score += self.config.advanced_settings.sentence_end_score_bonus
        
        # 长度评分
        target_length = (self.config.document_settings.max_length + 
                        self.config.document_settings.min_length) / 2
        length_ratio = current_length / target_length if target_length > 0 else 0
        
        if length_ratio > 1.0:
            # 超过目标长度，增加分割倾向
            score += (length_ratio - 1.0) * self.config.advanced_settings.length_score_factor
        elif length_ratio < 0.5:
            # 太短，减少分割倾向
            score -= (0.5 - length_ratio) * self.config.advanced_settings.length_score_factor
        
        return score
    
    def is_valid_split_point(
        self, 
        element: ElementInfo, 
        current_length: int,
        next_element: ElementInfo = None
    ) -> bool:
        """检查是否为有效的分割点"""
        # 检查最小长度限制
        if current_length < self.config.document_settings.min_length:
            return False
        
        # 检查是否在标题后强制分割
        if (self.config.advanced_settings.force_split_before_heading and 
            next_element and next_element.is_heading):
            return True
        
        # 检查最大长度限制
        if current_length > self.config.document_settings.max_length:
            return True
        
        return True
    
    def refine_split_points(
        self, 
        document: Document, 
        initial_split_points: List[int]
    ) -> List[int]:
        """优化分割点，确保句子完整性"""
        refined_points = []
        
        for point in initial_split_points:
            # 在搜索窗口内寻找更好的分割点
            search_window = self.config.advanced_settings.search_window
            best_point = self._find_best_nearby_point(document, point, search_window)
            
            if best_point != -1:
                refined_points.append(best_point)
            else:
                refined_points.append(point)
        
        return sorted(list(set(refined_points)))
    
    def _find_best_nearby_point(
        self, 
        document: Document, 
        target_point: int, 
        search_window: int
    ) -> int:
        """在目标点附近寻找最佳分割点"""
        best_point = target_point
        best_score = -float('inf')
        
        start = max(0, target_point - search_window)
        end = min(len(document.elements), target_point + search_window + 1)
        
        for i in range(start, end):
            if i >= len(document.elements):
                continue
                
            element = document.elements[i]
            
            # 计算到目标点的距离惩罚
            distance_penalty = abs(i - target_point) * 0.5
            
            # 计算元素的分割适合度
            element_score = 0.0
            if element.ends_with_period:
                element_score += 5.0
            if element.is_heading:
                element_score += 3.0
            
            total_score = element_score - distance_penalty
            
            if total_score > best_score:
                best_score = total_score
                best_point = i
        
        return best_point if best_score > -float('inf') else -1
