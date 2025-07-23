#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自定义异常类
"""

from typing import Optional, Dict, Any


class VerbaAureaAPIException(Exception):
    """VerbaAurea API基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class FileValidationError(VerbaAureaAPIException):
    """文件验证错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="FILE_VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class FileTooLargeError(VerbaAureaAPIException):
    """文件过大错误"""
    
    def __init__(self, file_size: int, max_size: int):
        message = f"文件大小 {file_size} 字节超过最大限制 {max_size} 字节"
        super().__init__(
            message=message,
            error_code="FILE_TOO_LARGE",
            status_code=413,
            details={"file_size": file_size, "max_size": max_size}
        )


class UnsupportedFileTypeError(VerbaAureaAPIException):
    """不支持的文件类型错误"""
    
    def __init__(self, file_type: str, supported_types: list):
        message = f"不支持的文件类型: {file_type}，支持的类型: {', '.join(supported_types)}"
        super().__init__(
            message=message,
            error_code="UNSUPPORTED_FILE_TYPE",
            status_code=400,
            details={"file_type": file_type, "supported_types": supported_types}
        )


class DocumentProcessingError(VerbaAureaAPIException):
    """文档处理错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DOCUMENT_PROCESSING_ERROR",
            status_code=422,
            details=details
        )


class ConfigurationError(VerbaAureaAPIException):
    """配置错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=400,
            details=details
        )


class ServiceUnavailableError(VerbaAureaAPIException):
    """服务不可用错误"""
    
    def __init__(self, message: str = "服务暂时不可用"):
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            status_code=503
        )


class RequestTimeoutError(VerbaAureaAPIException):
    """请求超时错误"""
    
    def __init__(self, timeout: int):
        message = f"请求处理超时（{timeout}秒）"
        super().__init__(
            message=message,
            error_code="REQUEST_TIMEOUT",
            status_code=408,
            details={"timeout": timeout}
        )
