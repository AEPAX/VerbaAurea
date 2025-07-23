#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VerbaAurea - 智能文档预处理工具
主程序入口
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """主函数"""
    print("========================================")
    print("           VerbaAurea v2.0")
    print("        智能文档预处理工具")
    print("========================================")

    try:
        # 测试核心功能
        from verba_aurea.services import DocumentService
        from verba_aurea.config import get_settings

        settings = get_settings()
        doc_service = DocumentService(settings)

        print("核心模块加载成功！")
        print(f"支持的文件格式: {doc_service.get_supported_formats()}")

        # 显示基本信息
        config = settings.get_config()
        print(f"输入目录: {config.input_folder}")
        print(f"输出目录: {config.processing_options.output_folder}")

        print("\n项目已准备就绪！")
        print("使用 'python start_api.py' 启动API服务")

    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
