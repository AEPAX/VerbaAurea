#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API响应数据模型
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, field_serializer


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(description="操作是否成功")
    message: str = Field(description="响应消息")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        """序列化时间戳为ISO格式字符串"""
        return value.isoformat()


class ProcessingResult(BaseModel):
    """文档处理结果模型"""
    split_count: int = Field(description="插入的分隔符数量")
    processing_time: float = Field(description="处理耗时（秒）")
    file_size_before: int = Field(description="处理前文件大小（字节）")
    file_size_after: int = Field(description="处理后文件大小（字节）")
    element_count: int = Field(description="文档元素总数")
    paragraph_count: int = Field(description="段落数量")
    table_count: int = Field(description="表格数量")
    image_count: int = Field(description="图片数量")
    has_images: bool = Field(description="是否包含图片")
    
    # 处理统计
    heading_count: int = Field(default=0, description="标题数量")
    split_points: List[int] = Field(default=[], description="分割点位置列表")
    
    # 质量指标
    avg_segment_length: Optional[float] = Field(description="平均段落长度")
    min_segment_length: Optional[int] = Field(description="最小段落长度")
    max_segment_length: Optional[int] = Field(description="最大段落长度")


class ProcessingResponse(BaseResponse):
    """文档处理响应模型"""
    data: Optional[ProcessingResult] = Field(description="处理结果数据")
    filename: Optional[str] = Field(description="处理后的文件名")


class HealthStatus(BaseModel):
    """健康状态模型"""
    status: str = Field(description="服务状态")
    version: str = Field(description="应用版本")
    uptime: float = Field(description="运行时间（秒）")
    dependencies: Dict[str, bool] = Field(description="依赖检查结果")
    system_info: Dict[str, Any] = Field(description="系统信息")


class HealthResponse(BaseResponse):
    """健康检查响应模型"""
    data: HealthStatus = Field(description="健康状态数据")


class ConfigResponse(BaseResponse):
    """配置响应模型"""
    data: Dict[str, Any] = Field(description="配置数据")


class ErrorDetail(BaseModel):
    """错误详情模型"""
    error_code: str = Field(description="错误代码")
    error_type: str = Field(description="错误类型")
    details: Optional[Dict[str, Any]] = Field(description="错误详细信息")


class ErrorResponse(BaseResponse):
    """错误响应模型"""
    error: ErrorDetail = Field(description="错误详情")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "文件处理失败",
                "request_id": "req_123456789",
                "timestamp": "2025-01-21T10:30:00Z",
                "error": {
                    "error_code": "PROCESSING_FAILED",
                    "error_type": "DocumentProcessingError",
                    "details": {
                        "reason": "文档格式不支持",
                        "file_type": "unknown"
                    }
                }
            }
        }


class FileUploadResponse(BaseResponse):
    """文件上传响应模型"""
    data: Dict[str, Any] = Field(description="上传结果数据")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "文件上传成功",
                "request_id": "req_123456789",
                "timestamp": "2025-01-21T10:30:00Z",
                "data": {
                    "filename": "document.docx",
                    "size": 1024000,
                    "upload_id": "upload_123456789"
                }
            }
        }
