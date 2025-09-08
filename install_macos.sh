#!/bin/bash
echo "🚀 安装KSX门店管理系统..."

# 检查是否存在应用文件
if [ ! -f "KSX门店管理系统" ]; then
    echo "❌ 未找到应用文件，请先运行构建脚本"
    exit 1
fi

# 创建Applications目录（如果不存在）
sudo mkdir -p /Applications

# 复制应用到Applications目录
echo "📦 正在安装应用..."
sudo cp -R "KSX门店管理系统.app" /Applications/

# 设置权限
sudo chmod +x "/Applications/KSX门店管理系统.app/Contents/MacOS/KSX门店管理系统"

echo "✅ 安装完成！"
echo "🎉 您现在可以在Applications文件夹中找到KSX门店管理系统"
echo "💡 首次运行时会自动安装Playwright浏览器，请耐心等待"
