#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
处理配置数据模型
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class DocumentSettings:
    """文档处理设置"""
    max_length: int = 1000
    min_length: int = 300
    sentence_integrity_weight: float = 8.0
    table_length_factor: float = 1.2
    image_length_factor: int = 100
    preserve_images: bool = True


@dataclass
class ProcessingOptions:
    """处理选项"""
    debug_mode: bool = False
    output_folder: str = "输出文件夹"
    skip_existing: bool = True


@dataclass
class AdvancedSettings:
    """高级设置"""
    min_split_score: int = 7
    heading_score_bonus: int = 10
    sentence_end_score_bonus: int = 6
    length_score_factor: int = 100
    search_window: int = 5
    heading_after_penalty: int = 12
    force_split_before_heading: bool = True
    custom_heading_regex: List[str] = field(default_factory=list)


@dataclass
class PerformanceSettings:
    """性能设置"""
    parallel_processing: bool = True
    num_workers: int = 0  # 0表示自动选择
    cache_size: int = 1024  # 缓存大小(MB)
    batch_size: int = 50


@dataclass
class ProcessingConfig:
    """完整的处理配置"""
    document_settings: DocumentSettings = field(default_factory=DocumentSettings)
    processing_options: ProcessingOptions = field(default_factory=ProcessingOptions)
    advanced_settings: AdvancedSettings = field(default_factory=AdvancedSettings)
    performance_settings: PerformanceSettings = field(default_factory=PerformanceSettings)
    input_folder: str = "."
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（兼容旧配置格式）"""
        return {
            "document_settings": {
                "max_length": self.document_settings.max_length,
                "min_length": self.document_settings.min_length,
                "sentence_integrity_weight": self.document_settings.sentence_integrity_weight,
                "table_length_factor": self.document_settings.table_length_factor,
                "image_length_factor": self.document_settings.image_length_factor,
                "preserve_images": self.document_settings.preserve_images
            },
            "processing_options": {
                "debug_mode": self.processing_options.debug_mode,
                "output_folder": self.processing_options.output_folder,
                "skip_existing": self.processing_options.skip_existing
            },
            "advanced_settings": {
                "min_split_score": self.advanced_settings.min_split_score,
                "heading_score_bonus": self.advanced_settings.heading_score_bonus,
                "sentence_end_score_bonus": self.advanced_settings.sentence_end_score_bonus,
                "length_score_factor": self.advanced_settings.length_score_factor,
                "search_window": self.advanced_settings.search_window,
                "heading_after_penalty": self.advanced_settings.heading_after_penalty,
                "force_split_before_heading": self.advanced_settings.force_split_before_heading,
                "custom_heading_regex": self.advanced_settings.custom_heading_regex
            },
            "performance_settings": {
                "parallel_processing": self.performance_settings.parallel_processing,
                "num_workers": self.performance_settings.num_workers,
                "cache_size": self.performance_settings.cache_size,
                "batch_size": self.performance_settings.batch_size
            },
            "input_folder": self.input_folder
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingConfig':
        """从字典创建配置对象（兼容旧配置格式）"""
        doc_settings = DocumentSettings(**data.get("document_settings", {}))
        proc_options = ProcessingOptions(**data.get("processing_options", {}))
        adv_settings = AdvancedSettings(**data.get("advanced_settings", {}))
        perf_settings = PerformanceSettings(**data.get("performance_settings", {}))
        
        return cls(
            document_settings=doc_settings,
            processing_options=proc_options,
            advanced_settings=adv_settings,
            performance_settings=perf_settings,
            input_folder=data.get("input_folder", ".")
        )
