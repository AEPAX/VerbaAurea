#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理路由
"""

import sys
import os
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 使用新架构的配置管理
try:
    from verba_aurea.config import get_settings
    from verba_aurea.core.models.config import ProcessingConfig as NewProcessingConfig
    USE_NEW_CONFIG = True
except ImportError:
    # 创建默认配置作为后备
    DEFAULT_CONFIG = {
        "document_settings": {
            "max_length": 1000,
            "min_length": 300,
            "sentence_integrity_weight": 8.0,
            "table_length_factor": 1.2
        },
        "processing_options": {
            "debug_mode": False,
            "output_folder": "输出文件夹",
            "skip_existing": True
        },
        "advanced_settings": {
            "min_split_score": 7,
            "heading_score_bonus": 10,
            "sentence_end_score_bonus": 6,
            "length_score_factor": 100,
            "search_window": 5,
            "heading_after_penalty": 12,
            "force_split_before_heading": True
        }
    }
    USE_NEW_CONFIG = False

from ..models.request_models import ConfigUpdateRequest, ProcessingConfig
from ..models.response_models import ConfigResponse
from ..utils.validators import validate_config_parameters
from ..utils.exceptions import ConfigurationError

router = APIRouter()


@router.get(
    "/config",
    response_model=ConfigResponse,
    summary="获取当前配置",
    description="获取系统当前的处理配置参数"
)
async def get_config():
    """获取当前配置"""
    try:
        if USE_NEW_CONFIG:
            settings = get_settings()
            config = settings.get_config()
            config_dict = config.to_dict()
        else:
            config_dict = DEFAULT_CONFIG

        return ConfigResponse(
            success=True,
            message="配置获取成功",
            data=config_dict
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取配置失败: {str(e)}"
        )


@router.get(
    "/config/default",
    summary="获取默认配置",
    description="获取系统默认的处理配置参数"
)
async def get_default_config():
    """获取默认配置"""
    return {
        "success": True,
        "message": "默认配置获取成功",
        "data": DEFAULT_CONFIG
    }


@router.put(
    "/config",
    response_model=ConfigResponse,
    summary="更新配置",
    description="更新系统的处理配置参数"
)
async def update_config(request: ConfigUpdateRequest):
    """更新配置"""
    try:
        # 转换为现有系统的配置格式
        new_config = request.config.to_legacy_config()
        
        # 验证配置参数
        validate_config_parameters(new_config)
        
        # 加载当前配置
        current_config = load_config()
        
        # 合并配置（保留其他未修改的配置项）
        for section, settings in new_config.items():
            if section in current_config:
                current_config[section].update(settings)
            else:
                current_config[section] = settings
        
        # 保存配置
        success = save_config(current_config)
        
        if not success:
            raise ConfigurationError("配置保存失败")
        
        return ConfigResponse(
            success=True,
            message="配置更新成功",
            data=current_config
        )
        
    except ConfigurationError:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新配置失败: {str(e)}"
        )


@router.post(
    "/config/reset",
    response_model=ConfigResponse,
    summary="重置配置",
    description="将配置重置为默认值"
)
async def reset_config():
    """重置配置为默认值"""
    try:
        # 保存默认配置
        success = save_config(DEFAULT_CONFIG)
        
        if not success:
            raise ConfigurationError("配置重置失败")
        
        return ConfigResponse(
            success=True,
            message="配置已重置为默认值",
            data=DEFAULT_CONFIG
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"重置配置失败: {str(e)}"
        )


@router.get(
    "/config/validate",
    summary="验证配置",
    description="验证当前配置的有效性"
)
async def validate_config():
    """验证当前配置"""
    try:
        config = load_config()
        
        # 验证配置
        validate_config_parameters(config)
        
        # 检查配置完整性
        missing_sections = []
        for section in DEFAULT_CONFIG.keys():
            if section not in config:
                missing_sections.append(section)
        
        missing_keys = {}
        for section, default_settings in DEFAULT_CONFIG.items():
            if section in config:
                for key in default_settings.keys():
                    if key not in config[section]:
                        if section not in missing_keys:
                            missing_keys[section] = []
                        missing_keys[section].append(key)
        
        validation_result = {
            "valid": len(missing_sections) == 0 and len(missing_keys) == 0,
            "missing_sections": missing_sections,
            "missing_keys": missing_keys,
            "config": config
        }
        
        return {
            "success": True,
            "message": "配置验证完成",
            "data": validation_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"配置验证失败: {str(e)}",
            "data": {"valid": False, "error": str(e)}
        }
