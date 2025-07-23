#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本分析器

负责文本内容的分析，包括句子边界检测、标题识别等功能。
"""

import re
import functools
import jieba
import nltk
from nltk.tokenize import sent_tokenize
from typing import List, Optional
from ..models.config import ProcessingConfig

# ---------- NLTK 资源初始化 ----------
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# ---------- 默认标题识别正则 ----------
DEFAULT_HEADING_REGEX = [
    r'^第[一二三四五六七八九十百千]+[章节]',      # 第一节 / 第二章
    r'^[一二三四五六七八九十]+[、\.]',          # 一、 / 二.
    r'^\d+(\.\d+)*\s*[\u4e00-\u9fff]{0,30}$', # 1. / 1.1 标题
    r'^[\(（][一二三四五六七八九十]+[\)）]',    # （二）/ (三)
    r'^[\(（]?\d+[\)）]'                       # (2) / （3）
]


class TextAnalyzer:
    """文本分析器类"""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        """初始化文本分析器"""
        self.config = config
        self._heading_patterns = self._compile_heading_patterns()
    
    def _compile_heading_patterns(self) -> List[re.Pattern]:
        """编译标题识别正则表达式"""
        patterns = DEFAULT_HEADING_REGEX.copy()
        
        # 如果有配置，添加自定义正则
        if self.config and self.config.advanced_settings.custom_heading_regex:
            patterns.extend(self.config.advanced_settings.custom_heading_regex)
        
        return [re.compile(pat) for pat in patterns]
    
    def looks_like_heading(self, text: str) -> bool:
        """判断文本是否像标题"""
        if not text:
            return False
        
        # 过长或明显以句号等结束的视为正文
        if len(text) > 50 or text.endswith(('。', '！', '？', '.', '!', '?', '；', ';')):
            return False
        
        stripped = text.strip()
        for pattern in self._heading_patterns:
            if pattern.match(stripped):
                return True
        
        return False
    
    @functools.lru_cache(maxsize=1024)
    def is_sentence_boundary(self, text_before: str, text_after: str) -> bool:
        """判断两段文本之间是否为句子边界"""
        if text_before.endswith(('。', '！', '？', '.', '!', '?', '；', ';')):
            return True
        
        combined_text = text_before + " " + text_after
        
        try:
            # 检查是否包含中文字符
            if any(u'\u4e00' <= c <= u'\u9fff' for c in combined_text):
                # 中文用 jieba 分词
                segments = list(jieba.cut(combined_text))
                for i, word in enumerate(segments[:-1]):
                    if word in ['。', '！', '？', '.', '!', '?', '；', ';']:
                        before_segment = ''.join(segments[:i+1])
                        if abs(len(before_segment) - len(text_before)) < 5:
                            return True
            else:
                # 英文用 NLTK 句子分割
                sentences = sent_tokenize(combined_text)
                for sentence in sentences:
                    if text_before.endswith(sentence) or text_after.startswith(sentence):
                        return True
        except Exception:
            pass
        
        return False
    
    def find_nearest_sentence_boundary(
        self, 
        elements_info: List[dict], 
        current_index: int, 
        search_window: int = 5
    ) -> int:
        """寻找最近的句子边界"""
        best_index = -1
        min_distance = float('inf')
        
        # 向前搜索
        for i in range(max(0, current_index - search_window), current_index + 1):
            if i > 0 and self.is_sentence_boundary(
                elements_info[i-1]['text'], 
                elements_info[i]['text']
            ):
                distance = current_index - i
                if distance < min_distance:
                    min_distance = distance
                    best_index = i
        
        # 向后搜索
        for i in range(current_index + 1, min(len(elements_info), current_index + search_window + 1)):
            if i > 0 and self.is_sentence_boundary(
                elements_info[i-1]['text'], 
                elements_info[i]['text']
            ):
                distance = i - current_index
                if distance < min_distance:
                    min_distance = distance
                    best_index = i
        
        return best_index
    
    def analyze_text_properties(self, text: str) -> dict:
        """分析文本属性"""
        return {
            'is_heading': self.looks_like_heading(text),
            'is_list_item': self._is_list_item(text),
            'ends_with_period': text.endswith(('。', '！', '？', '.', '!', '?', '；', ';')),
            'length': len(text),
            'has_chinese': any(u'\u4e00' <= c <= u'\u9fff' for c in text),
            'is_empty': not text.strip()
        }
    
    def _is_list_item(self, text: str) -> bool:
        """判断是否为列表项"""
        text = text.strip()
        if not text:
            return False
        
        # 检查常见的列表标记
        if text.startswith(('•', '-', '*')):
            return True
        
        # 检查数字列表
        if len(text) > 2 and text[0].isdigit() and text[1] in '.、)':
            return True
        
        return False
