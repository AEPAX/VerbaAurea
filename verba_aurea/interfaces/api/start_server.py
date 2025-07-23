#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VerbaAurea API服务器启动脚本

使用新架构的API服务器实现。
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


def check_dependencies():
    """检查依赖"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'python-docx',
        'jieba',
        'nltk',
        'pandas',
        'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'python-docx':
                import docx
            elif package == 'uvicorn':
                import uvicorn
            elif package == 'fastapi':
                import fastapi
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖检查通过")
    return True


def install_dependencies():
    """安装依赖"""
    print("🔧 正在安装依赖...")
    
    # 查找requirements文件
    project_root = Path(__file__).parent.parent.parent.parent
    requirements_files = [
        project_root / "requirements-api.txt",
        project_root / "requirements.txt"
    ]
    
    requirements_file = None
    for req_file in requirements_files:
        if req_file.exists():
            requirements_file = req_file
            break
    
    if requirements_file:
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            print("✅ 依赖安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False
    else:
        print("❌ 找不到requirements文件")
        return False


def start_api_server(host="0.0.0.0", port=8000, reload=False, log_level="info"):
    """启动API服务器"""
    print(f"🚀 启动VerbaAurea API服务...")
    print(f"📍 地址: http://{host}:{port}")
    print(f"📖 API文档: http://{host}:{port}/docs")
    print(f"📚 ReDoc文档: http://{host}:{port}/redoc")
    print("按 Ctrl+C 停止服务")
    
    # 设置环境变量
    os.environ.setdefault("PYTHONPATH", str(Path(__file__).parent.parent.parent.parent))
    
    try:
        import uvicorn
        
        # 使用现有的API应用，但通过适配器使用新架构
        uvicorn.run(
            "api.main:app",  # 仍然使用现有的API应用
            host=host,
            port=port,
            reload=reload,
            log_level=log_level
        )
    except ImportError:
        print("❌ uvicorn未安装，尝试使用subprocess启动...")
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "api.main:app",
            "--host", host,
            "--port", str(port),
            "--log-level", log_level
        ] + (["--reload"] if reload else []))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="VerbaAurea API服务器")
    parser.add_argument("--host", default="0.0.0.0", help="服务器地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--reload", action="store_true", help="启用自动重载")
    parser.add_argument("--log-level", default="info", help="日志级别")
    parser.add_argument("--install-deps", action="store_true", help="自动安装依赖")
    parser.add_argument("--check-only", action="store_true", help="仅检查依赖")
    
    args = parser.parse_args()
    
    # 安装依赖（如果需要）
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        if not args.install_deps:
            print("💡 提示: 使用 --install-deps 参数自动安装依赖")
        sys.exit(1)
    
    # 仅检查模式
    if args.check_only:
        print("✅ 所有检查通过，可以启动API服务")
        return
    
    # 启动服务器
    try:
        start_api_server(
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
