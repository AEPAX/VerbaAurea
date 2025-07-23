#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API请求数据模型
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class ProcessingConfig(BaseModel):
    """文档处理配置模型"""
    
    # 文档设置
    max_length: Optional[int] = Field(
        default=1000,
        ge=100,
        le=10000,
        description="最大段落长度（字符数）"
    )
    min_length: Optional[int] = Field(
        default=300,
        ge=50,
        le=5000,
        description="最小段落长度（字符数）"
    )
    sentence_integrity_weight: Optional[float] = Field(
        default=8.0,
        ge=0.0,
        le=20.0,
        description="句子完整性权重"
    )
    table_length_factor: Optional[float] = Field(
        default=1.2,
        ge=0.1,
        le=5.0,
        description="表格长度因子"
    )
    image_length_factor: Optional[int] = Field(
        default=100,
        ge=0,
        le=1000,
        description="图片长度因子（每个图片按多少字符计算）"
    )
    
    # 处理选项
    debug_mode: Optional[bool] = Field(
        default=False,
        description="是否启用调试模式"
    )
    preserve_images: Optional[bool] = Field(
        default=True,
        description="是否保留图片"
    )
    skip_existing: Optional[bool] = Field(
        default=False,
        description="是否跳过已存在的文件"
    )
    
    # 高级设置
    min_split_score: Optional[float] = Field(
        default=7.0,
        ge=0.0,
        le=20.0,
        description="最小分割得分"
    )
    heading_score_bonus: Optional[float] = Field(
        default=10.0,
        ge=0.0,
        le=50.0,
        description="标题加分"
    )
    sentence_end_score_bonus: Optional[float] = Field(
        default=6.0,
        ge=0.0,
        le=20.0,
        description="句子结束加分"
    )
    length_score_factor: Optional[int] = Field(
        default=100,
        ge=10,
        le=1000,
        description="长度评分因子"
    )
    search_window: Optional[int] = Field(
        default=5,
        ge=1,
        le=20,
        description="搜索窗口大小"
    )
    heading_after_penalty: Optional[float] = Field(
        default=12.0,
        ge=0.0,
        le=50.0,
        description="标题后惩罚分数"
    )
    force_split_before_heading: Optional[bool] = Field(
        default=True,
        description="是否在标题前强制分割"
    )
    heading_cooldown_elements: Optional[int] = Field(
        default=2,
        ge=0,
        le=10,
        description="标题后冷却元素数量"
    )
    
    @validator('min_length')
    def validate_min_length(cls, v, values):
        """验证最小长度不能大于最大长度"""
        if 'max_length' in values and v >= values['max_length']:
            raise ValueError('min_length必须小于max_length')
        return v
    
    def to_legacy_config(self) -> Dict[str, Any]:
        """转换为现有系统的配置格式"""
        return {
            "document_settings": {
                "max_length": self.max_length,
                "min_length": self.min_length,
                "sentence_integrity_weight": self.sentence_integrity_weight,
                "table_length_factor": self.table_length_factor,
                "image_length_factor": self.image_length_factor,
                "preserve_images": self.preserve_images
            },
            "processing_options": {
                "debug_mode": self.debug_mode,
                "skip_existing": self.skip_existing,
                "output_folder": "/tmp"  # API模式下使用临时目录
            },
            "advanced_settings": {
                "min_split_score": self.min_split_score,
                "heading_score_bonus": self.heading_score_bonus,
                "sentence_end_score_bonus": self.sentence_end_score_bonus,
                "length_score_factor": self.length_score_factor,
                "search_window": self.search_window,
                "heading_after_penalty": self.heading_after_penalty,
                "force_split_before_heading": self.force_split_before_heading,
                "heading_cooldown_elements": self.heading_cooldown_elements
            }
        }


class ConfigUpdateRequest(BaseModel):
    """配置更新请求模型"""
    config: ProcessingConfig = Field(description="新的处理配置")
