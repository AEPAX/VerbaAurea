#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一配置设置

提供应用程序的配置管理功能，支持多种配置源。
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import asdict

from ..core.models.config import ProcessingConfig


class Settings:
    """统一配置管理类"""
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """初始化配置管理器"""
        self.config_file = Path(config_file) if config_file else self._get_default_config_path()
        self._config: Optional[ProcessingConfig] = None
    
    def _get_default_config_path(self) -> Path:
        """获取默认配置文件路径"""
        # 优先使用当前工作目录
        current_dir = Path.cwd()
        config_path = current_dir / "config.json"
        
        if config_path.exists():
            return config_path
        
        # 如果当前目录没有，尝试脚本目录
        script_dir = Path(__file__).parent.parent.parent
        return script_dir / "config.json"
    
    def load_config(self) -> ProcessingConfig:
        """加载配置"""
        if self._config is not None:
            return self._config
        
        if not self.config_file.exists():
            # 创建默认配置
            self._config = ProcessingConfig()
            self.save_config(self._config)
            return self._config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self._config = ProcessingConfig.from_dict(config_data)
            return self._config
        
        except Exception as e:
            print(f"加载配置文件时出错: {str(e)}")
            print("使用默认配置")
            self._config = ProcessingConfig()
            return self._config
    
    def save_config(self, config: ProcessingConfig):
        """保存配置"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换为字典并保存
            config_data = config.to_dict()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            self._config = config
            
        except Exception as e:
            raise ValueError(f"保存配置文件时出错: {str(e)}")
    
    def get_config(self) -> ProcessingConfig:
        """获取当前配置"""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def update_config(self, **kwargs) -> ProcessingConfig:
        """更新配置"""
        config = self.get_config()
        
        # 更新文档设置
        if 'document_settings' in kwargs:
            for key, value in kwargs['document_settings'].items():
                if hasattr(config.document_settings, key):
                    setattr(config.document_settings, key, value)
        
        # 更新处理选项
        if 'processing_options' in kwargs:
            for key, value in kwargs['processing_options'].items():
                if hasattr(config.processing_options, key):
                    setattr(config.processing_options, key, value)
        
        # 更新高级设置
        if 'advanced_settings' in kwargs:
            for key, value in kwargs['advanced_settings'].items():
                if hasattr(config.advanced_settings, key):
                    setattr(config.advanced_settings, key, value)
        
        # 更新性能设置
        if 'performance_settings' in kwargs:
            for key, value in kwargs['performance_settings'].items():
                if hasattr(config.performance_settings, key):
                    setattr(config.performance_settings, key, value)
        
        # 更新其他设置
        for key, value in kwargs.items():
            if key not in ['document_settings', 'processing_options', 'advanced_settings', 'performance_settings']:
                if hasattr(config, key):
                    setattr(config, key, value)
        
        self.save_config(config)
        return config
    
    def reset_to_defaults(self) -> ProcessingConfig:
        """重置为默认配置"""
        self._config = ProcessingConfig()
        self.save_config(self._config)
        return self._config
    
    def get_legacy_config_dict(self) -> Dict[str, Any]:
        """获取兼容旧版本的配置字典格式"""
        config = self.get_config()
        return config.to_dict()
    
    def load_from_legacy_dict(self, config_dict: Dict[str, Any]) -> ProcessingConfig:
        """从旧版本配置字典加载"""
        self._config = ProcessingConfig.from_dict(config_dict)
        return self._config
    
    @property
    def config_file_path(self) -> Path:
        """获取配置文件路径"""
        return self.config_file
    
    def __str__(self) -> str:
        """字符串表示"""
        config = self.get_config()
        return f"Settings(config_file={self.config_file}, config={config})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()


# 全局配置实例
_global_settings: Optional[Settings] = None


def get_settings(config_file: Optional[Union[str, Path]] = None) -> Settings:
    """获取全局配置实例"""
    global _global_settings
    
    if _global_settings is None or config_file is not None:
        _global_settings = Settings(config_file)
    
    return _global_settings


def load_config(config_file: Optional[Union[str, Path]] = None) -> ProcessingConfig:
    """加载配置（兼容旧版本接口）"""
    settings = get_settings(config_file)
    return settings.load_config()


def save_config(config: ProcessingConfig, config_file: Optional[Union[str, Path]] = None):
    """保存配置（兼容旧版本接口）"""
    settings = get_settings(config_file)
    settings.save_config(config)
