#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件处理工具
"""

import os
import uuid
import tempfile
import shutil
from typing import Tuple, Optional
from pathlib import Path
from fastapi import UploadFile

from .exceptions import DocumentProcessingError
from .validators import FileValidator


class FileHandler:
    """文件处理器"""
    
    def __init__(self, temp_dir: str = None):
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.upload_dir = os.path.join(self.temp_dir, "verba_aurea_uploads")
        self.output_dir = os.path.join(self.temp_dir, "verba_aurea_outputs")
        
        # 确保目录存在
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def save_upload_file(self, file: UploadFile) -> Tuple[str, str]:
        """
        保存上传的文件到临时目录
        
        Returns:
            Tuple[str, str]: (文件路径, 文件ID)
        """
        try:
            # 生成唯一文件ID
            file_id = str(uuid.uuid4())
            
            # 清理文件名
            validator = FileValidator(max_size=50*1024*1024, allowed_types=['.docx'])
            clean_filename = validator.validate_filename(file.filename)
            
            # 构建文件路径
            file_path = os.path.join(self.upload_dir, f"{file_id}_{clean_filename}")
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            return file_path, file_id
            
        except Exception as e:
            raise DocumentProcessingError(
                f"保存上传文件失败: {str(e)}",
                details={"filename": file.filename}
            )
    
    def create_output_path(self, file_id: str, original_filename: str) -> str:
        """
        创建输出文件路径
        
        Args:
            file_id: 文件ID
            original_filename: 原始文件名
            
        Returns:
            str: 输出文件路径
        """
        # 在原文件名前添加processed_前缀
        name, ext = os.path.splitext(original_filename)
        output_filename = f"processed_{name}{ext}"
        
        return os.path.join(self.output_dir, f"{file_id}_{output_filename}")
    
    def get_file_size(self, file_path: str) -> int:
        """获取文件大小"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    def cleanup_file(self, file_path: str) -> None:
        """清理临时文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass  # 忽略清理错误
    
    def cleanup_files(self, *file_paths: str) -> None:
        """批量清理临时文件"""
        for file_path in file_paths:
            self.cleanup_file(file_path)
    
    def get_file_info(self, file_path: str) -> dict:
        """获取文件信息"""
        try:
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "exists": True
            }
        except OSError:
            return {"exists": False}
    
    def ensure_directory_exists(self, directory: str) -> None:
        """确保目录存在"""
        os.makedirs(directory, exist_ok=True)
    
    def copy_file(self, src: str, dst: str) -> None:
        """复制文件"""
        try:
            # 确保目标目录存在
            dst_dir = os.path.dirname(dst)
            self.ensure_directory_exists(dst_dir)
            
            shutil.copy2(src, dst)
        except Exception as e:
            raise DocumentProcessingError(
                f"复制文件失败: {str(e)}",
                details={"src": src, "dst": dst}
            )
    
    def move_file(self, src: str, dst: str) -> None:
        """移动文件"""
        try:
            # 确保目标目录存在
            dst_dir = os.path.dirname(dst)
            self.ensure_directory_exists(dst_dir)
            
            shutil.move(src, dst)
        except Exception as e:
            raise DocumentProcessingError(
                f"移动文件失败: {str(e)}",
                details={"src": src, "dst": dst}
            )
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """清理旧的临时文件"""
        import time
        
        cleaned_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for directory in [self.upload_dir, self.output_dir]:
            try:
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > max_age_seconds:
                            os.remove(file_path)
                            cleaned_count += 1
            except OSError:
                pass
        
        return cleaned_count
