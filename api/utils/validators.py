#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
输入验证工具
"""

import os
import mimetypes
from typing import List
from fastapi import UploadFile

from .exceptions import FileValidationError, FileTooLargeError, UnsupportedFileTypeError


class FileValidator:
    """文件验证器"""
    
    def __init__(self, max_size: int, allowed_types: List[str]):
        self.max_size = max_size
        self.allowed_types = allowed_types
        
        # MIME类型映射
        self.mime_type_mapping = {
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword'
        }
    
    async def validate_file(self, file: UploadFile) -> None:
        """验证上传的文件"""
        
        # 检查文件是否为空
        if not file.filename:
            raise FileValidationError("文件名不能为空")
        
        # 检查文件扩展名
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in self.allowed_types:
            raise UnsupportedFileTypeError(file_ext, self.allowed_types)
        
        # 检查MIME类型
        if file.content_type:
            expected_mime = self.mime_type_mapping.get(file_ext)
            if expected_mime and file.content_type != expected_mime:
                raise FileValidationError(
                    f"文件MIME类型不匹配: 期望 {expected_mime}, 实际 {file.content_type}",
                    details={
                        "expected_mime": expected_mime,
                        "actual_mime": file.content_type,
                        "file_extension": file_ext
                    }
                )
        
        # 检查文件大小
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > self.max_size:
            raise FileTooLargeError(file_size, self.max_size)
        
        if file_size == 0:
            raise FileValidationError("文件不能为空")
        
        # 重置文件指针
        await file.seek(0)
    
    def validate_filename(self, filename: str) -> str:
        """验证并清理文件名"""
        if not filename:
            raise FileValidationError("文件名不能为空")
        
        # 移除危险字符
        dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
        clean_filename = filename
        
        for char in dangerous_chars:
            clean_filename = clean_filename.replace(char, '_')
        
        # 限制文件名长度
        if len(clean_filename) > 255:
            name, ext = os.path.splitext(clean_filename)
            clean_filename = name[:255-len(ext)] + ext
        
        return clean_filename


def validate_config_parameters(config_dict: dict) -> None:
    """验证配置参数的合理性"""
    
    # 检查长度参数
    max_length = config_dict.get('document_settings', {}).get('max_length', 1000)
    min_length = config_dict.get('document_settings', {}).get('min_length', 300)
    
    if min_length >= max_length:
        raise FileValidationError(
            "最小长度不能大于或等于最大长度",
            details={"min_length": min_length, "max_length": max_length}
        )
    
    # 检查权重参数
    sentence_weight = config_dict.get('document_settings', {}).get('sentence_integrity_weight', 8.0)
    if sentence_weight < 0 or sentence_weight > 20:
        raise FileValidationError(
            "句子完整性权重必须在0-20之间",
            details={"sentence_integrity_weight": sentence_weight}
        )
    
    # 检查高级设置
    advanced = config_dict.get('advanced_settings', {})
    min_split_score = advanced.get('min_split_score', 7.0)
    if min_split_score < 0 or min_split_score > 20:
        raise FileValidationError(
            "最小分割得分必须在0-20之间",
            details={"min_split_score": min_split_score}
        )
