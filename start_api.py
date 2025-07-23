#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VerbaAurea API 启动脚本
提供便捷的API服务启动方式
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("OK - 核心依赖检查通过")
        return True
    except ImportError as e:
        print(f"ERROR - 缺少依赖: {e}")
        print("请运行: pip install -r requirements-api.txt")
        return False


def install_dependencies():
    """安装依赖"""
    print("正在安装API依赖...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements-api.txt"
        ])
        print("OK - 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("ERROR - 依赖安装失败")
        return False


def start_api_server(host="0.0.0.0", port=8000, reload=False, log_level="info"):
    """启动API服务器"""
    print(f"启动VerbaAurea API服务...")
    print(f"地址: http://{host}:{port}")
    print(f"API文档: http://{host}:{port}/docs")
    print(f"ReDoc文档: http://{host}:{port}/redoc")
    print("按 Ctrl+C 停止服务")
    
    try:
        import uvicorn
        uvicorn.run(
            "api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level
        )
    except ImportError:
        print("ERROR - uvicorn未安装，尝试使用subprocess启动...")
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "api.main:app",
            "--host", host,
            "--port", str(port),
            "--log-level", log_level
        ] + (["--reload"] if reload else []))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="VerbaAurea API 启动脚本")
    parser.add_argument("--host", default="0.0.0.0", help="服务器地址 (默认: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="端口号 (默认: 8000)")
    parser.add_argument("--reload", action="store_true", help="启用自动重载 (开发模式)")
    parser.add_argument("--log-level", default="info", 
                       choices=["critical", "error", "warning", "info", "debug"],
                       help="日志级别 (默认: info)")
    parser.add_argument("--install-deps", action="store_true", help="安装依赖后启动")
    parser.add_argument("--check-only", action="store_true", help="仅检查依赖，不启动服务")
    
    args = parser.parse_args()
    
    # 检查当前目录
    if not os.path.exists("api/main.py"):
        print("ERROR - 请在项目根目录下运行此脚本")
        sys.exit(1)
    
    # 安装依赖（如果需要）
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        if not args.install_deps:
            print("提示: 使用 --install-deps 参数自动安装依赖")
        sys.exit(1)
    
    # 仅检查模式
    if args.check_only:
        print("OK - 所有检查通过，可以启动API服务")
        return
    
    # 设置环境变量
    os.environ.setdefault("PYTHONPATH", os.getcwd())
    
    # 启动服务器
    try:
        start_api_server(
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level
        )
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"ERROR - 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
