#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VerbaAurea Document Processing API
FastAPI应用主入口
"""

import logging
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .config.settings import get_settings
from .middleware.logging import LoggingMiddleware
from .middleware.error_handler import ErrorHandlerMiddleware
from .routers import document, health, config as config_router


# 配置日志
def setup_logging():
    """设置日志配置"""
    settings = get_settings()
    
    # 配置根日志器
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 创建API专用日志器
    logger = logging.getLogger("verba_aurea_api")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    return logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger = logging.getLogger("verba_aurea_api")
    logger.info("VerbaAurea API 服务启动中...")
    
    # 检查依赖
    try:
        import docx
        import jieba
        import nltk
        logger.info("所有依赖检查通过")
    except ImportError as e:
        logger.error(f"依赖检查失败: {e}")
        raise
    
    # 创建必要的目录
    settings = get_settings()
    os.makedirs(settings.upload_temp_dir, exist_ok=True)
    logger.info(f"临时目录已创建: {settings.upload_temp_dir}")
    
    logger.info("VerbaAurea API 服务启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("VerbaAurea API 服务正在关闭...")


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    
    # 设置日志
    logger = setup_logging()
    
    # 获取配置
    settings = get_settings()
    
    # 创建FastAPI应用
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # 添加受信任主机中间件（生产环境建议启用）
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # 生产环境应该配置具体的主机名
        )
    
    # 添加自定义中间件
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(LoggingMiddleware, logger=logger)
    
    # 注册路由
    app.include_router(
        health.router,
        prefix="/api/v1",
        tags=["健康检查"]
    )
    
    app.include_router(
        document.router,
        prefix="/api/v1",
        tags=["文档处理"]
    )
    
    app.include_router(
        config_router.router,
        prefix="/api/v1",
        tags=["配置管理"]
    )
    
    # 根路径重定向到文档
    @app.get("/", include_in_schema=False)
    async def root():
        """根路径重定向到API文档"""
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/docs")
    
    logger.info("FastAPI应用创建完成")
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
