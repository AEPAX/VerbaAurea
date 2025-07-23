#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文档服务

提供高级的文档处理服务，协调各个组件完成文档处理任务。
"""

import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from ..core.processors import get_processor, get_supported_extensions
from ..core.models.document import Document, ProcessingResult
from ..core.models.config import ProcessingConfig
from ..config.settings import Settings


class DocumentService:
    """文档处理服务"""
    
    def __init__(self, settings: Optional[Settings] = None):
        """初始化文档服务"""
        self.settings = settings or Settings()
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        return get_supported_extensions()
    
    def can_process_file(self, file_path: Path) -> bool:
        """检查是否可以处理指定文件"""
        try:
            processor = get_processor(file_path.suffix)
            return processor.can_process(file_path)
        except ValueError:
            return False
    
    def analyze_document(
        self, 
        file_path: Path, 
        config: Optional[ProcessingConfig] = None
    ) -> Document:
        """分析文档结构"""
        if config is None:
            config = self.settings.get_config()
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not self.can_process_file(file_path):
            raise ValueError(f"不支持的文件格式: {file_path.suffix}")
        
        processor = get_processor(file_path.suffix)
        return processor.extract_elements(file_path, config)
    
    def process_document(
        self,
        input_file: Path,
        output_file: Optional[Path] = None,
        config: Optional[ProcessingConfig] = None
    ) -> ProcessingResult:
        """处理单个文档"""
        if config is None:
            config = self.settings.get_config()
        
        if not input_file.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_file}")
        
        if not self.can_process_file(input_file):
            raise ValueError(f"不支持的文件格式: {input_file.suffix}")
        
        # 生成输出文件路径
        if output_file is None:
            output_file = self._generate_output_path(input_file, config)
        
        # 检查是否跳过已存在的文件
        if (config.processing_options.skip_existing and 
            output_file.exists() and 
            output_file.stat().st_mtime > input_file.stat().st_mtime):
            
            return ProcessingResult(
                success=True,
                message="文件已存在且较新，跳过处理",
                split_count=0,
                processing_time=0.0
            )
        
        # 获取处理器并处理文档
        processor = get_processor(input_file.suffix)
        return processor.process_document(input_file, output_file, config)
    
    def process_batch(
        self,
        input_files: List[Path],
        config: Optional[ProcessingConfig] = None
    ) -> Dict[str, ProcessingResult]:
        """批量处理文档"""
        if config is None:
            config = self.settings.get_config()
        
        results = {}
        
        for input_file in input_files:
            try:
                result = self.process_document(input_file, config=config)
                results[str(input_file)] = result
            except Exception as e:
                results[str(input_file)] = ProcessingResult(
                    success=False,
                    message=f"处理失败: {str(e)}",
                    error_details=str(e)
                )
        
        return results
    
    def process_directory(
        self,
        input_dir: Path,
        config: Optional[ProcessingConfig] = None,
        recursive: bool = True
    ) -> Dict[str, ProcessingResult]:
        """处理目录中的所有文档"""
        if config is None:
            config = self.settings.get_config()
        
        if not input_dir.exists() or not input_dir.is_dir():
            raise ValueError(f"输入目录不存在或不是目录: {input_dir}")
        
        # 收集文件
        files_to_process = self._collect_files(input_dir, recursive)
        
        if config.processing_options.debug_mode:
            print(f"找到 {len(files_to_process)} 个文件需要处理")
        
        # 批量处理
        return self.process_batch(files_to_process, config)
    
    def get_document_stats(self, file_path: Path) -> Dict[str, Any]:
        """获取文档统计信息"""
        try:
            document = self.analyze_document(file_path)
            
            return {
                'file_path': str(file_path),
                'file_size': file_path.stat().st_size,
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
                'file_path': str(file_path),
                'error': str(e)
            }
    
    def _generate_output_path(self, input_file: Path, config: ProcessingConfig) -> Path:
        """生成输出文件路径"""
        output_dir = Path(config.processing_options.output_folder)
        
        # 保持相对目录结构
        if config.input_folder and config.input_folder != ".":
            input_base = Path(config.input_folder)
            try:
                relative_path = input_file.relative_to(input_base)
                output_file = output_dir / relative_path
            except ValueError:
                # 如果无法计算相对路径，直接使用文件名
                output_file = output_dir / input_file.name
        else:
            output_file = output_dir / input_file.name
        
        # 确保输出目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        return output_file
    
    def _collect_files(self, directory: Path, recursive: bool) -> List[Path]:
        """收集目录中的文件"""
        files = []
        supported_extensions = set(get_supported_extensions())
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in directory.glob(pattern):
            if (file_path.is_file() and 
                file_path.suffix.lower() in supported_extensions):
                files.append(file_path)
        
        return sorted(files)
    
    def validate_processing_request(
        self, 
        input_file: Path, 
        config: ProcessingConfig
    ) -> List[str]:
        """验证处理请求"""
        errors = []
        
        # 检查输入文件
        if not input_file.exists():
            errors.append(f"输入文件不存在: {input_file}")
        elif not input_file.is_file():
            errors.append(f"输入路径不是文件: {input_file}")
        elif not self.can_process_file(input_file):
            errors.append(f"不支持的文件格式: {input_file.suffix}")
        
        # 检查文件大小（如果有限制）
        if input_file.exists():
            file_size = input_file.stat().st_size
            max_size = 100 * 1024 * 1024  # 100MB限制
            if file_size > max_size:
                errors.append(f"文件过大: {file_size / (1024*1024):.1f}MB > {max_size / (1024*1024)}MB")
        
        # 检查输出目录权限
        output_dir = Path(config.processing_options.output_folder)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            # 尝试创建临时文件测试写权限
            test_file = output_dir / ".write_test"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            errors.append(f"输出目录无写权限: {output_dir} ({str(e)})")
        
        return errors
