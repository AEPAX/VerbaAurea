#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
安全工具
"""

import hashlib
import secrets
from typing import Optional


def generate_request_id() -> str:
    """生成请求ID"""
    return secrets.token_urlsafe(16)


def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> Optional[str]:
    """计算文件哈希值"""
    try:
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    except Exception:
        return None


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除危险字符"""
    import re
    
    # 移除路径分隔符和其他危险字符
    dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
    clean_name = re.sub(dangerous_chars, '_', filename)
    
    # 移除前后空格和点
    clean_name = clean_name.strip(' .')
    
    # 限制长度
    if len(clean_name) > 255:
        name, ext = clean_name.rsplit('.', 1) if '.' in clean_name else (clean_name, '')
        max_name_len = 255 - len(ext) - 1 if ext else 255
        clean_name = name[:max_name_len] + ('.' + ext if ext else '')
    
    return clean_name or "unnamed_file"


def is_safe_path(path: str, base_path: str) -> bool:
    """检查路径是否安全（防止路径遍历攻击）"""
    import os
    
    try:
        # 规范化路径
        abs_path = os.path.abspath(path)
        abs_base = os.path.abspath(base_path)
        
        # 检查是否在基础路径内
        return abs_path.startswith(abs_base)
    except Exception:
        return False
