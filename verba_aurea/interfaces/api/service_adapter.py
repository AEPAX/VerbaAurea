#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API服务适配器

为现有的API提供新架构的适配层，确保API接口的兼容性。
"""

import os
import sys
import time
import tempfile
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from verba_aurea.services.document_service import DocumentService
from verba_aurea.config.settings import get_settings
from verba_aurea.core.models.config import ProcessingConfig


class APIServiceAdapter:
    """API服务适配器"""
    
    def __init__(self):
        """初始化适配器"""
        self.settings = get_settings()
        self.document_service = DocumentService(self.settings)
    
    async def process_document(
        self,
        input_file_path: str,
        config: Optional[Dict[str, Any]] = None,
        debug_mode: bool = False
    ) -> Tuple[str, Dict[str, Any]]:
        """
        处理文档（异步接口）
        
        返回: (output_file_path, processing_result)
        """
        try:
            # 转换路径
            input_path = Path(input_file_path)
            
            # 准备配置
            processing_config = self._prepare_config(config, debug_mode)
            
            # 生成输出文件路径
            output_path = self._generate_output_path(input_path, processing_config)
            
            # 获取输入文件信息
            input_file_size = input_path.stat().st_size
            
            # 处理文档
            result = self.document_service.process_document(
                input_path, output_path, processing_config
            )
            
            # 转换结果格式以兼容现有API
            processing_result = {
                'split_count': result.split_count,
                'processing_time': result.processing_time,
                'file_size_before': input_file_size,
                'file_size_after': result.file_size_after,
                'elements_stats': result.elements_stats,
                'success': result.success,
                'message': result.message
            }
            
            if not result.success:
                processing_result['error'] = result.error_details
            
            return str(output_path), processing_result
            
        except Exception as e:
            # 返回错误结果
            error_result = {
                'split_count': 0,
                'processing_time': 0.0,
                'file_size_before': 0,
                'file_size_after': 0,
                'elements_stats': {},
                'success': False,
                'message': f"处理失败: {str(e)}",
                'error': str(e)
            }
            return "", error_result
    
    async def analyze_document(self, file_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """分析文档结构"""
        try:
            input_path = Path(file_path)
            processing_config = ProcessingConfig.from_dict(config)
            
            # 分析文档
            document = self.document_service.analyze_document(input_path, processing_config)
            
            # 转换为兼容格式
            return {
                'total_elements': document.total_elements,
                'paragraphs': document.paragraph_count,
                'tables': document.table_count,
                'images': document.image_count,
                'total_text_length': document.total_text_length,
                'total_weighted_length': document.total_weighted_length,
                'metadata': document.metadata
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_elements': 0,
                'paragraphs': 0,
                'tables': 0,
                'images': 0
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        try:
            # 检查依赖
            dependencies = {}
            try:
                import docx
                dependencies['python-docx'] = True
            except ImportError:
                dependencies['python-docx'] = False
            
            try:
                import jieba
                dependencies['jieba'] = True
            except ImportError:
                dependencies['jieba'] = False
            
            try:
                import nltk
                dependencies['nltk'] = True
            except ImportError:
                dependencies['nltk'] = False
            
            try:
                import pandas
                dependencies['pandas'] = True
            except ImportError:
                dependencies['pandas'] = False
            
            try:
                import openpyxl
                dependencies['openpyxl'] = True
            except ImportError:
                dependencies['openpyxl'] = False
            
            # 检查配置
            config = self.settings.get_config()
            config_valid = True
            
            # 检查支持的格式
            supported_formats = self.document_service.get_supported_formats()
            
            return {
                'status': 'healthy' if all(dependencies.values()) and config_valid else 'degraded',
                'version': '2.0.0',
                'dependencies': dependencies,
                'supported_formats': supported_formats,
                'config_valid': config_valid
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        try:
            config = self.settings.get_config()
            return config.to_dict()
        except Exception as e:
            return {'error': str(e)}
    
    def update_config(self, config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新配置"""
        try:
            self.settings.update_config(**config_updates)
            return {'success': True, 'message': '配置更新成功'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _prepare_config(self, config: Optional[Dict[str, Any]], debug_mode: bool) -> ProcessingConfig:
        """准备处理配置"""
        if config is None:
            processing_config = self.settings.get_config()
        else:
            processing_config = ProcessingConfig.from_dict(config)
        
        # 设置调试模式
        processing_config.processing_options.debug_mode = debug_mode
        
        return processing_config
    
    def _generate_output_path(self, input_path: Path, config: ProcessingConfig) -> Path:
        """生成输出文件路径"""
        # 使用临时目录作为输出目录
        temp_dir = Path(tempfile.gettempdir()) / "verba_aurea_api_output"
        temp_dir.mkdir(exist_ok=True)
        
        # 生成唯一的输出文件名
        timestamp = int(time.time() * 1000)
        output_filename = f"{input_path.stem}_{timestamp}_processed{input_path.suffix}"
        
        return temp_dir / output_filename


# 全局适配器实例
_api_adapter = None


def get_api_adapter() -> APIServiceAdapter:
    """获取API适配器实例"""
    global _api_adapter
    if _api_adapter is None:
        _api_adapter = APIServiceAdapter()
    return _api_adapter


# 兼容函数，供现有API代码调用
async def process_document_api(
    input_file_path: str,
    config: Optional[Dict[str, Any]] = None,
    debug_mode: bool = False
) -> Tuple[str, Dict[str, Any]]:
    """处理文档的API兼容函数"""
    adapter = get_api_adapter()
    return await adapter.process_document(input_file_path, config, debug_mode)


async def analyze_document_api(file_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """分析文档的API兼容函数"""
    adapter = get_api_adapter()
    return await adapter.analyze_document(file_path, config)


def get_health_status_api() -> Dict[str, Any]:
    """获取健康状态的API兼容函数"""
    adapter = get_api_adapter()
    return adapter.get_health_status()


def get_config_api() -> Dict[str, Any]:
    """获取配置的API兼容函数"""
    adapter = get_api_adapter()
    return adapter.get_config()


def update_config_api(config_updates: Dict[str, Any]) -> Dict[str, Any]:
    """更新配置的API兼容函数"""
    adapter = get_api_adapter()
    return adapter.update_config(config_updates)
