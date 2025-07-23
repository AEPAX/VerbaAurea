#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API配置设置
"""

import os
from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class APISettings(BaseSettings):
    """API配置类"""
    
    # 应用基础配置
    app_name: str = "VerbaAurea Document Processing API"
    app_version: str = "1.0.0"
    app_description: str = "高质量文档预处理API服务，为知识库构建提供智能文档切分功能"
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # 文件处理配置
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [".docx"]
    upload_temp_dir: str = "temp/verba_aurea_uploads"
    
    # 安全配置
    cors_origins: list = ["*"]  # 生产环境应该限制具体域名
    cors_methods: list = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: list = ["*"]
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "json"  # json 或 text
    
    # 性能配置
    request_timeout: int = 300  # 5分钟超时
    max_concurrent_requests: int = 10
    
    # 文档处理默认配置
    default_max_length: int = 1000
    default_min_length: int = 300
    default_sentence_integrity_weight: float = 8.0
    default_preserve_images: bool = True
    
    class Config:
        env_prefix = "VERBA_"
        case_sensitive = False


# 全局设置实例
settings = APISettings()


def get_settings() -> APISettings:
    """获取设置实例"""
    return settings
