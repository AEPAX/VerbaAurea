@echo off
chcp 65001 >nul
title VerbaAurea Web服务启动器

echo.
echo 🏛️ VerbaAurea Web服务启动器
echo ================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8或更高版本
    echo 📥 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ 检测到Python环境
echo.

REM 启动Web服务
echo 🚀 正在启动VerbaAurea Web服务...
python start_web_service.py

echo.
echo 👋 服务已停止
pause
