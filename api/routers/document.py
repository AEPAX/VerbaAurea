#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文档处理路由
"""

import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse

from ..config.settings import get_settings, APISettings
from ..models.request_models import ProcessingConfig
from ..models.response_models import ProcessingResponse
from ..services.document_service import DocumentProcessingService
from ..utils.validators import FileValidator
from ..utils.file_handler import FileHandler
from ..utils.exceptions import VerbaAureaAPIException

router = APIRouter()


def get_file_validator(settings: APISettings = Depends(get_settings)) -> FileValidator:
    """获取文件验证器"""
    return FileValidator(
        max_size=settings.max_file_size,
        allowed_types=settings.allowed_file_types
    )


def get_document_service() -> DocumentProcessingService:
    """获取文档处理服务"""
    return DocumentProcessingService()


def get_file_handler() -> FileHandler:
    """获取文件处理器"""
    return FileHandler()


@router.post(
    "/process-document",
    response_model=ProcessingResponse,
    summary="处理文档",
    description="上传Word文档并进行智能分割处理，在适当位置插入分隔符"
)
async def process_document(
    file: UploadFile = File(..., description="要处理的Word文档文件"),
    config: Optional[str] = Form(None, description="处理配置（JSON格式，可选）"),
    debug_mode: bool = Form(False, description="是否启用调试模式"),
    file_validator: FileValidator = Depends(get_file_validator),
    document_service: DocumentProcessingService = Depends(get_document_service),
    file_handler: FileHandler = Depends(get_file_handler)
):
    """
    处理文档端点
    
    - **file**: Word文档文件（.docx格式）
    - **config**: 可选的处理配置参数（JSON格式）
    - **debug_mode**: 是否启用调试模式，启用后会输出详细的处理日志
    
    返回处理后的文档文件和处理统计信息。
    """
    
    input_file_path = None
    output_file_path = None
    
    try:
        # 验证文件
        await file_validator.validate_file(file)
        
        # 解析配置
        processing_config = None
        if config:
            try:
                import json
                config_dict = json.loads(config)
                processing_config = ProcessingConfig(**config_dict)
            except (json.JSONDecodeError, ValueError) as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"配置参数格式错误: {str(e)}"
                )
        
        # 保存上传的文件
        input_file_path, file_id = await file_handler.save_upload_file(file)
        
        # 处理文档
        output_file_path, processing_result = await document_service.process_document(
            input_file_path=input_file_path,
            config=processing_config,
            debug_mode=debug_mode
        )
        
        # 构建响应
        response = ProcessingResponse(
            success=True,
            message="文档处理成功",
            data=processing_result,
            filename=os.path.basename(output_file_path)
        )
        
        return response
        
    except VerbaAureaAPIException:
        # 重新抛出自定义异常
        raise
    except Exception as e:
        # 处理其他异常
        raise HTTPException(
            status_code=500,
            detail=f"文档处理失败: {str(e)}"
        )
    finally:
        # 清理临时文件
        if input_file_path:
            file_handler.cleanup_file(input_file_path)


@router.post(
    "/process-document/download",
    summary="处理文档并下载",
    description="上传Word文档进行处理，直接返回处理后的文件供下载"
)
async def process_and_download_document(
    file: UploadFile = File(..., description="要处理的Word文档文件"),
    config: Optional[str] = Form(None, description="处理配置（JSON格式，可选）"),
    debug_mode: bool = Form(False, description="是否启用调试模式"),
    file_validator: FileValidator = Depends(get_file_validator),
    document_service: DocumentProcessingService = Depends(get_document_service),
    file_handler: FileHandler = Depends(get_file_handler)
):
    """
    处理文档并直接下载结果文件
    
    这个端点会处理文档并直接返回处理后的文件，适合需要立即下载结果的场景。
    """
    
    input_file_path = None
    output_file_path = None
    
    try:
        # 验证文件
        await file_validator.validate_file(file)
        
        # 解析配置
        processing_config = None
        if config:
            try:
                import json
                config_dict = json.loads(config)
                processing_config = ProcessingConfig(**config_dict)
            except (json.JSONDecodeError, ValueError) as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"配置参数格式错误: {str(e)}"
                )
        
        # 保存上传的文件
        input_file_path, file_id = await file_handler.save_upload_file(file)
        
        # 处理文档
        output_file_path, processing_result = await document_service.process_document(
            input_file_path=input_file_path,
            config=processing_config,
            debug_mode=debug_mode
        )
        
        # 生成下载文件名
        original_name = os.path.splitext(file.filename)[0]
        download_filename = f"processed_{original_name}.docx"
        
        # 返回文件
        return FileResponse(
            path=output_file_path,
            filename=download_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "X-Processing-Time": str(processing_result.processing_time),
                "X-Split-Count": str(processing_result.split_count),
                "X-File-Size-Before": str(processing_result.file_size_before),
                "X-File-Size-After": str(processing_result.file_size_after)
            }
        )
        
    except VerbaAureaAPIException:
        # 重新抛出自定义异常
        raise
    except Exception as e:
        # 处理其他异常
        raise HTTPException(
            status_code=500,
            detail=f"文档处理失败: {str(e)}"
        )
    finally:
        # 清理输入文件（输出文件由FileResponse处理后自动清理）
        if input_file_path:
            file_handler.cleanup_file(input_file_path)
