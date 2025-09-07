#!/bin/bash

echo "正在安装KSX门店管理系统..."

# 检查是否已安装
if [ -d "/Applications/KSX门店管理系统.app" ]; then
    echo "检测到已安装的版本，正在卸载..."
    rm -rf "/Applications/KSX门店管理系统.app"
fi

# 复制应用到Applications目录
cp -R "dist/KSX门店管理系统.app" "/Applications/"

# 设置权限
chmod +x "/Applications/KSX门店管理系统.app/Contents/MacOS/KSX门店管理系统"

echo "安装完成！"
echo "您可以在Applications文件夹中找到KSX门店管理系统"
