#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志中间件
"""

import time
import uuid
import json
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..config.settings import get_settings


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志记录中间件"""
    
    def __init__(self, app, logger: logging.Logger = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger("verba_aurea_api")
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "content_type": request.headers.get("content-type", ""),
            "content_length": request.headers.get("content-length", 0),
            "timestamp": time.time()
        }
        
        self._log_request(request_info)
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            response_info = {
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
                "response_size": response.headers.get("content-length", 0),
                "timestamp": time.time()
            }
            
            self._log_response(response_info)
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 记录错误
            process_time = time.time() - start_time
            error_info = {
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "process_time": round(process_time, 4),
                "timestamp": time.time()
            }
            
            self._log_error(error_info)
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _log_request(self, request_info: dict) -> None:
        """记录请求日志"""
        if self.settings.log_format == "json":
            self.logger.info(json.dumps({
                "type": "request",
                **request_info
            }, ensure_ascii=False))
        else:
            self.logger.info(
                f"REQUEST {request_info['request_id']} "
                f"{request_info['method']} {request_info['url']} "
                f"from {request_info['client_ip']}"
            )
    
    def _log_response(self, response_info: dict) -> None:
        """记录响应日志"""
        if self.settings.log_format == "json":
            self.logger.info(json.dumps({
                "type": "response",
                **response_info
            }, ensure_ascii=False))
        else:
            self.logger.info(
                f"RESPONSE {response_info['request_id']} "
                f"status={response_info['status_code']} "
                f"time={response_info['process_time']}s"
            )
    
    def _log_error(self, error_info: dict) -> None:
        """记录错误日志"""
        if self.settings.log_format == "json":
            self.logger.error(json.dumps({
                "type": "error",
                **error_info
            }, ensure_ascii=False))
        else:
            self.logger.error(
                f"ERROR {error_info['request_id']} "
                f"{error_info['error_type']}: {error_info['error']} "
                f"time={error_info['process_time']}s"
            )
