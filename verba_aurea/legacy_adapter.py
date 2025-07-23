#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
遗留代码适配器

提供与旧版本代码的兼容性，确保现有的API和CLI能够无缝使用新架构。
"""

import os
from pathlib import Path
from typing import Dict, Any, List

from .services.document_service import DocumentService
from .config.settings import load_config, save_config
from .core.models.config import ProcessingConfig


# 全局服务实例
_document_service = None


def get_document_service() -> DocumentService:
    """获取文档服务实例"""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service


def insert_split_markers(input_file: str, output_file: str, config: Dict[str, Any]) -> bool:
    """
    兼容旧版本的insert_split_markers函数
    
    这是主要的向后兼容接口，现有的API和CLI代码可以直接调用。
    """
    try:
        # 转换路径
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        # 转换配置格式
        if isinstance(config, dict):
            processing_config = ProcessingConfig.from_dict(config)
        else:
            processing_config = config
        
        # 使用新架构处理文档
        service = get_document_service()
        result = service.process_document(input_path, output_path, processing_config)
        
        # 返回布尔值以兼容旧接口
        return result.success
        
    except Exception as e:
        if config.get("processing_options", {}).get("debug_mode", False):
            print(f"处理文档时出错: {str(e)}")
        return False


def extract_elements_info(doc, table_factor=1.0, debug_mode=False, image_factor=100):
    """
    兼容旧版本的extract_elements_info函数
    
    注意：这个函数需要docx.Document对象，主要用于现有的测试和分析代码。
    """
    try:
        from .core.analyzers.structure_analyzer import StructureAnalyzer
        from .core.models.config import ProcessingConfig, DocumentSettings
        
        # 创建配置
        doc_settings = DocumentSettings(
            table_length_factor=table_factor,
            image_length_factor=image_factor
        )
        config = ProcessingConfig(document_settings=doc_settings)
        
        # 创建分析器
        analyzer = StructureAnalyzer(config)
        
        # 提取元素信息（需要临时保存文档以获取路径）
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
            doc.save(tmp_file.name)
            tmp_path = Path(tmp_file.name)
            
            try:
                document = analyzer.analyze_document(tmp_path)
                
                # 转换为旧格式
                elements_info = []
                for element in document.elements:
                    element_dict = {
                        'type': element.type,
                        'i_para': element.index if element.type == 'para' else None,
                        'i_table': element.index if element.type == 'table' else None,
                        'text': element.text,
                        'length': element.length,
                        'base_text_length': element.base_text_length,
                        'is_heading': element.is_heading,
                        'is_list_item': element.is_list_item,
                        'ends_with_period': element.ends_with_period,
                        'has_images': element.has_images,
                        'image_count': element.image_count,
                        'image_info': element.image_info
                    }
                    elements_info.append(element_dict)
                
                if debug_mode:
                    print(f"[extract] elements={len(elements_info)} (tables={document.table_count}, images={document.image_count})")
                
                return elements_info
                
            finally:
                # 清理临时文件
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
    except Exception as e:
        if debug_mode:
            print(f"提取元素信息时出错: {str(e)}")
        return []


def is_sentence_boundary(text_before: str, text_after: str) -> bool:
    """兼容旧版本的is_sentence_boundary函数"""
    try:
        from .core.analyzers.text_analyzer import TextAnalyzer
        analyzer = TextAnalyzer()
        return analyzer.is_sentence_boundary(text_before, text_after)
    except Exception:
        return False


def find_nearest_sentence_boundary(elements_info: List[Dict], current_index: int, search_window: int = 5) -> int:
    """兼容旧版本的find_nearest_sentence_boundary函数"""
    try:
        from .core.analyzers.text_analyzer import TextAnalyzer
        analyzer = TextAnalyzer()
        return analyzer.find_nearest_sentence_boundary(elements_info, current_index, search_window)
    except Exception:
        return -1


def looks_like_heading(text: str) -> bool:
    """兼容旧版本的looks_like_heading函数"""
    try:
        from .core.analyzers.text_analyzer import TextAnalyzer
        analyzer = TextAnalyzer()
        return analyzer.looks_like_heading(text)
    except Exception:
        return False


# 兼容旧版本的配置管理函数
def load_config_legacy():
    """兼容旧版本的load_config函数"""
    config = load_config()
    return config.to_dict()


def save_config_legacy(config_dict: Dict[str, Any]):
    """兼容旧版本的save_config函数"""
    config = ProcessingConfig.from_dict(config_dict)
    save_config(config)


# 导出兼容接口
__all__ = [
    'insert_split_markers',
    'extract_elements_info', 
    'is_sentence_boundary',
    'find_nearest_sentence_boundary',
    'looks_like_heading',
    'load_config_legacy',
    'save_config_legacy'
]
