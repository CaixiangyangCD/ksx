#!/bin/bash

echo "🚀 KSX门店管理系统 - 桌面应用"
echo "================================================"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3"
    echo "请先安装Python 3.8或更高版本"
    exit 1
fi

# 启动应用
python3 ksx_desktop_app.py
