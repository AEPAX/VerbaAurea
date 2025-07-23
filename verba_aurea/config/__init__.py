#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块

提供统一的配置管理功能。
"""

from .settings import Settings
from .manager import ConfigManager

# 创建全局设置实例
_global_settings = None

def get_settings() -> Settings:
    """获取全局设置实例"""
    global _global_settings
    if _global_settings is None:
        _global_settings = Settings()
    return _global_settings

__all__ = [
    "Settings",
    "ConfigManager",
    "get_settings"
]
