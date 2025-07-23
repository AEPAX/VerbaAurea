#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件处理器抽象基类

定义所有文件处理器必须实现的接口，确保插件化架构的一致性。
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from ..models.document import Document, ProcessingResult, ElementInfo
from ..models.config import ProcessingConfig


class BaseProcessor(ABC):
    """文件处理器抽象基类"""
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """返回支持的文件扩展名列表"""
        pass
    
    @property
    @abstractmethod
    def processor_name(self) -> str:
        """返回处理器名称"""
        pass
    
    @abstractmethod
    def can_process(self, file_path: Path) -> bool:
        """检查是否可以处理指定文件"""
        pass
    
    @abstractmethod
    def extract_elements(self, file_path: Path, config: ProcessingConfig) -> Document:
        """从文件中提取元素信息"""
        pass
    
    @abstractmethod
    def process_document(
        self, 
        input_file: Path, 
        output_file: Path, 
        config: ProcessingConfig
    ) -> ProcessingResult:
        """处理文档，插入分隔符并保存"""
        pass
    
    def validate_file(self, file_path: Path) -> bool:
        """验证文件是否有效"""
        if not file_path.exists():
            return False
        if not file_path.is_file():
            return False
        return self.can_process(file_path)
    
    def get_output_filename(self, input_file: Path, suffix: str = "_processed") -> str:
        """生成输出文件名"""
        stem = input_file.stem
        extension = input_file.suffix
        return f"{stem}{suffix}{extension}"
    
    def calculate_element_length(
        self, 
        text_length: int, 
        element_type: str,
        config: ProcessingConfig,
        **kwargs
    ) -> int:
        """计算元素的加权长度"""
        if element_type == 'table':
            return int(text_length * config.document_settings.table_length_factor)
        elif element_type == 'image' or kwargs.get('has_images', False):
            image_count = kwargs.get('image_count', 1)
            return text_length + (image_count * config.document_settings.image_length_factor)
        else:
            return text_length
