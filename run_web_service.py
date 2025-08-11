#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VerbaAurea Web服务简单启动脚本
"""

import os
import sys
import time
import webbrowser
import subprocess

def main():
    """主函数"""
    print("VerbaAurea Web Service Launcher")
    print("=" * 40)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("Error: Python 3.8+ required")
        print(f"Current: {sys.version}")
        input("Press Enter to exit...")
        return
    
    print(f"Python version: {sys.version.split()[0]}")
    
    # 安装依赖
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        input("Press Enter to exit...")
        return
    
    # 创建必要目录
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("processed", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    print("Starting VerbaAurea Web Service...")
    print("Service URL: http://localhost:18080")
    print("Opening browser...")
    
    # 延迟打开浏览器
    def open_browser():
        time.sleep(3)
        webbrowser.open("http://localhost:18080")
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动Web服务
    try:
        # 直接导入并运行
        import web_service
        web_service.app.run(host='0.0.0.0', port=18080, debug=False)
    except KeyboardInterrupt:
        print("\nService stopped by user")
    except Exception as e:
        print(f"Error starting service: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
