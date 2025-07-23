#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康检查路由
"""

import time
import sys
import platform
from typing import Dict, Any
from fastapi import APIRouter, Depends, Request

from ..config.settings import get_settings, APISettings
from ..models.response_models import HealthResponse, HealthStatus
from ..utils.monitoring import get_metrics_collector

# 尝试使用新架构
try:
    from verba_aurea.interfaces.api.service_adapter import get_health_status_api
    USE_NEW_ARCHITECTURE = True
except ImportError:
    USE_NEW_ARCHITECTURE = False

router = APIRouter()

# 应用启动时间
_start_time = time.time()


def check_dependencies() -> Dict[str, bool]:
    """检查依赖库是否可用"""
    dependencies = {}
    
    # 检查核心依赖
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
    
    return dependencies


def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "hostname": platform.node()
    }


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="健康检查",
    description="检查API服务的健康状态，包括依赖库和系统信息"
)
async def health_check(request: Request, settings: APISettings = Depends(get_settings)):
    """健康检查端点"""

    if USE_NEW_ARCHITECTURE:
        # 使用新架构的健康检查
        try:
            health_data = get_health_status_api()

            # 计算运行时间
            uptime = time.time() - _start_time

            # 获取系统信息
            system_info = get_system_info()

            health_status = HealthStatus(
                status=health_data.get('status', 'unknown'),
                version=health_data.get('version', settings.app_version),
                uptime=round(uptime, 2),
                dependencies=health_data.get('dependencies', {}),
                system_info=system_info
            )

            # 获取请求ID
            request_id = getattr(request.state, 'request_id', None)

            return HealthResponse(
                success=True,
                message=f"服务状态: {health_data.get('status', 'unknown')}",
                request_id=request_id,
                data=health_status
            )

        except Exception as e:
            # 降级到旧版本检查
            pass

    # 使用旧架构的健康检查
    # 检查依赖
    dependencies = check_dependencies()

    # 计算运行时间
    uptime = time.time() - _start_time

    # 获取系统信息
    system_info = get_system_info()

    # 确定整体状态
    all_deps_ok = all(dependencies.values())
    status = "healthy" if all_deps_ok else "degraded"

    health_status = HealthStatus(
        status=status,
        version=settings.app_version,
        uptime=round(uptime, 2),
        dependencies=dependencies,
        system_info=system_info
    )

    # 获取请求ID
    request_id = getattr(request.state, 'request_id', None)

    return HealthResponse(
        success=True,
        message=f"服务状态: {status}",
        request_id=request_id,
        data=health_status
    )


@router.get(
    "/health/dependencies",
    summary="依赖检查",
    description="检查所有依赖库的可用性"
)
async def check_dependencies_endpoint():
    """依赖检查端点"""
    dependencies = check_dependencies()
    
    return {
        "success": True,
        "message": "依赖检查完成",
        "data": {
            "dependencies": dependencies,
            "all_available": all(dependencies.values()),
            "missing_count": sum(1 for available in dependencies.values() if not available)
        }
    }


@router.get(
    "/health/system",
    summary="系统信息",
    description="获取系统和运行环境信息"
)
async def system_info_endpoint():
    """系统信息端点"""
    system_info = get_system_info()
    uptime = time.time() - _start_time

    return {
        "success": True,
        "message": "系统信息获取成功",
        "data": {
            "uptime": round(uptime, 2),
            "uptime_formatted": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
            "system": system_info
        }
    }


@router.get(
    "/health/metrics",
    summary="性能指标",
    description="获取API服务的性能指标和统计信息"
)
async def metrics_endpoint():
    """性能指标端点"""
    metrics_collector = get_metrics_collector()
    metrics = metrics_collector.get_metrics()

    return {
        "success": True,
        "message": "性能指标获取成功",
        "data": metrics
    }
