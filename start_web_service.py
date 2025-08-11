#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VerbaAurea Web服务启动脚本
简化启动流程，自动检查依赖和配置
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"   当前版本: {sys.version}")
        return False
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """检查并安装依赖"""
    print("🔍 检查依赖包...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ 找不到requirements.txt文件")
        return False
    
    try:
        # 检查是否需要安装依赖
        result = subprocess.run([
            sys.executable, "-m", "pip", "check"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("📦 安装依赖包...")
            install_result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True)
            
            if install_result.returncode != 0:
                print("❌ 依赖安装失败:")
                print(install_result.stderr)
                return False
            print("✅ 依赖安装完成")
        else:
            print("✅ 依赖检查通过")
        
        return True
    except Exception as e:
        print(f"❌ 依赖检查失败: {e}")
        return False

def check_files():
    """检查必要文件"""
    print("📁 检查必要文件...")
    
    required_files = [
        "web_service.py",
        "document_processor.py",
        "config_manager.py",
        "config.json",
        "templates/index.html",
        "static/style.css",
        "static/script.js"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ 文件检查通过")
    return True

def create_directories():
    """创建必要目录"""
    print("📂 创建必要目录...")
    
    directories = ["uploads", "processed", "templates", "static"]
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
    
    print("✅ 目录创建完成")

def start_web_service():
    """启动Web服务"""
    print("🚀 启动VerbaAurea Web服务...")
    print("=" * 50)
    
    try:
        # 启动Web服务
        process = subprocess.Popen([
            sys.executable, "web_service.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
           universal_newlines=True, bufsize=1, encoding='utf-8', errors='replace')
        
        # 等待服务启动
        print("⏳ 等待服务启动...")
        time.sleep(3)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ Web服务启动成功!")
            print("📍 服务地址: http://localhost:18080")
            print("🌐 正在打开浏览器...")
            
            # 打开浏览器
            time.sleep(1)
            webbrowser.open("http://localhost:18080")
            
            print("\n" + "=" * 50)
            print("🎉 VerbaAurea Web服务已启动!")
            print("📖 使用说明:")
            print("   1. 在浏览器中拖拽或选择DOCX文件上传")
            print("   2. 等待处理完成")
            print("   3. 下载ZIP压缩包获取处理结果")
            print("   4. 在'处理历史'中查看所有文件")
            print("\n⚠️  按 Ctrl+C 停止服务")
            print("=" * 50)
            
            # 保持进程运行并显示输出
            try:
                for line in process.stdout:
                    print(line.rstrip())
            except KeyboardInterrupt:
                print("\n🛑 正在停止服务...")
                process.terminate()
                process.wait()
                print("✅ 服务已停止")
        else:
            print("❌ Web服务启动失败")
            output, _ = process.communicate()
            print("错误信息:")
            print(output)
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 用户中断启动")
        return False
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🏛️ VerbaAurea Web服务启动器")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        input("按Enter键退出...")
        return
    
    # 检查依赖
    if not check_dependencies():
        input("按Enter键退出...")
        return
    
    # 检查文件
    if not check_files():
        input("按Enter键退出...")
        return
    
    # 创建目录
    create_directories()
    
    # 启动服务
    start_web_service()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 启动器异常: {e}")
        input("按Enter键退出...")
    except KeyboardInterrupt:
        print("\n👋 再见!")
