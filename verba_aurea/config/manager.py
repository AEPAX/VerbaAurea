#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理器

提供配置的高级管理功能，包括验证、迁移等。
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from ..core.models.config import ProcessingConfig
from .settings import Settings


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, settings: Optional[Settings] = None):
        """初始化配置管理器"""
        self.settings = settings or Settings()
    
    def validate_config(self, config: ProcessingConfig) -> List[str]:
        """验证配置的有效性"""
        errors = []
        
        # 验证文档设置
        doc_settings = config.document_settings
        if doc_settings.max_length <= doc_settings.min_length:
            errors.append("最大长度必须大于最小长度")
        
        if doc_settings.min_length < 50:
            errors.append("最小长度不能小于50")
        
        if doc_settings.max_length > 50000:
            errors.append("最大长度不能超过50000")
        
        if not (0.1 <= doc_settings.table_length_factor <= 10.0):
            errors.append("表格长度因子必须在0.1到10.0之间")
        
        if not (0 <= doc_settings.image_length_factor <= 10000):
            errors.append("图片长度因子必须在0到10000之间")
        
        # 验证高级设置
        adv_settings = config.advanced_settings
        if not (1 <= adv_settings.min_split_score <= 100):
            errors.append("最小分割评分必须在1到100之间")
        
        if not (1 <= adv_settings.search_window <= 20):
            errors.append("搜索窗口必须在1到20之间")
        
        # 验证性能设置
        perf_settings = config.performance_settings
        if perf_settings.num_workers < 0:
            errors.append("工作进程数不能为负数")
        
        if perf_settings.cache_size < 0:
            errors.append("缓存大小不能为负数")
        
        if perf_settings.batch_size < 1:
            errors.append("批处理大小必须至少为1")
        
        return errors
    
    def auto_fix_config(self, config: ProcessingConfig) -> ProcessingConfig:
        """自动修复配置中的问题"""
        # 修复文档设置
        doc_settings = config.document_settings
        if doc_settings.max_length <= doc_settings.min_length:
            doc_settings.max_length = doc_settings.min_length * 2
        
        if doc_settings.min_length < 50:
            doc_settings.min_length = 50
        
        if doc_settings.max_length > 50000:
            doc_settings.max_length = 50000
        
        doc_settings.table_length_factor = max(0.1, min(10.0, doc_settings.table_length_factor))
        doc_settings.image_length_factor = max(0, min(10000, doc_settings.image_length_factor))
        
        # 修复高级设置
        adv_settings = config.advanced_settings
        adv_settings.min_split_score = max(1, min(100, adv_settings.min_split_score))
        adv_settings.search_window = max(1, min(20, adv_settings.search_window))
        
        # 修复性能设置
        perf_settings = config.performance_settings
        perf_settings.num_workers = max(0, perf_settings.num_workers)
        perf_settings.cache_size = max(0, perf_settings.cache_size)
        perf_settings.batch_size = max(1, perf_settings.batch_size)
        
        return config
    
    def migrate_config(self, old_config_dict: Dict[str, Any]) -> ProcessingConfig:
        """迁移旧版本配置"""
        # 处理可能的配置格式变化
        migrated_dict = old_config_dict.copy()
        
        # 添加缺失的默认值
        default_config = ProcessingConfig()
        default_dict = default_config.to_dict()
        
        for section, settings in default_dict.items():
            if section not in migrated_dict:
                migrated_dict[section] = settings
            else:
                for key, value in settings.items():
                    if key not in migrated_dict[section]:
                        migrated_dict[section][key] = value
        
        # 创建新配置对象
        config = ProcessingConfig.from_dict(migrated_dict)
        
        # 自动修复问题
        config = self.auto_fix_config(config)
        
        return config
    
    def backup_config(self, backup_path: Optional[Path] = None) -> Path:
        """备份当前配置"""
        if backup_path is None:
            backup_path = self.settings.config_file_path.with_suffix('.backup.json')
        
        config = self.settings.get_config()
        config_dict = config.to_dict()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
        
        return backup_path
    
    def restore_config(self, backup_path: Path) -> ProcessingConfig:
        """从备份恢复配置"""
        if not backup_path.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")
        
        with open(backup_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        config = self.migrate_config(config_dict)
        self.settings.save_config(config)
        
        return config
    
    def export_config(self, export_path: Path, format: str = 'json') -> Path:
        """导出配置到指定格式"""
        config = self.settings.get_config()
        
        if format.lower() == 'json':
            config_dict = config.to_dict()
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
        
        return export_path
    
    def import_config(self, import_path: Path) -> ProcessingConfig:
        """从文件导入配置"""
        if not import_path.exists():
            raise FileNotFoundError(f"导入文件不存在: {import_path}")
        
        with open(import_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        config = self.migrate_config(config_dict)
        
        # 验证配置
        errors = self.validate_config(config)
        if errors:
            print("配置验证发现问题:")
            for error in errors:
                print(f"  - {error}")
            print("正在自动修复...")
            config = self.auto_fix_config(config)
        
        self.settings.save_config(config)
        return config
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        config = self.settings.get_config()
        
        return {
            'config_file': str(self.settings.config_file_path),
            'document_settings': {
                'length_range': f"{config.document_settings.min_length}-{config.document_settings.max_length}",
                'preserve_images': config.document_settings.preserve_images,
                'table_factor': config.document_settings.table_length_factor
            },
            'processing_options': {
                'debug_mode': config.processing_options.debug_mode,
                'output_folder': config.processing_options.output_folder,
                'skip_existing': config.processing_options.skip_existing
            },
            'performance': {
                'parallel_processing': config.performance_settings.parallel_processing,
                'num_workers': config.performance_settings.num_workers,
                'batch_size': config.performance_settings.batch_size
            }
        }
