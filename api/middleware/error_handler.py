#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
错误处理中间件
"""

import logging
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.exceptions import VerbaAureaAPIException
from ..models.response_models import ErrorResponse, ErrorDetail


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("verba_aurea_api.error")
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            return await self._handle_exception(request, e)
    
    async def _handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """处理异常并返回标准化错误响应"""
        
        # 获取请求ID
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        if isinstance(exc, VerbaAureaAPIException):
            # 自定义API异常
            error_response = ErrorResponse(
                success=False,
                message=exc.message,
                request_id=request_id,
                error=ErrorDetail(
                    error_code=exc.error_code,
                    error_type=type(exc).__name__,
                    details=exc.details
                )
            )
            
            # 记录错误日志
            self.logger.warning(
                f"API Exception: {exc.error_code} - {exc.message}",
                extra={
                    "request_id": request_id,
                    "error_code": exc.error_code,
                    "status_code": exc.status_code,
                    "details": exc.details
                }
            )
            
            return JSONResponse(
                status_code=exc.status_code,
                content=error_response.model_dump()
            )
        
        elif isinstance(exc, HTTPException):
            # FastAPI HTTP异常
            error_response = ErrorResponse(
                success=False,
                message=exc.detail,
                request_id=request_id,
                error=ErrorDetail(
                    error_code="HTTP_ERROR",
                    error_type="HTTPException",
                    details={"status_code": exc.status_code}
                )
            )
            
            self.logger.warning(
                f"HTTP Exception: {exc.status_code} - {exc.detail}",
                extra={
                    "request_id": request_id,
                    "status_code": exc.status_code
                }
            )
            
            return JSONResponse(
                status_code=exc.status_code,
                content=error_response.model_dump()
            )
        
        else:
            # 未预期的异常
            error_response = ErrorResponse(
                success=False,
                message="服务器内部错误",
                request_id=request_id,
                error=ErrorDetail(
                    error_code="INTERNAL_SERVER_ERROR",
                    error_type=type(exc).__name__,
                    details={"message": str(exc)}
                )
            )
            
            # 记录严重错误
            self.logger.error(
                f"Unhandled Exception: {type(exc).__name__} - {str(exc)}",
                extra={
                    "request_id": request_id,
                    "exception_type": type(exc).__name__
                },
                exc_info=True
            )
            
            return JSONResponse(
                status_code=500,
                content=error_response.model_dump()
            )
