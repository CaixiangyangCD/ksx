#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的KSX应用构建脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🚀 开始构建KSX应用 (简化版)")
    
    # 项目根目录
    project_root = Path(__file__).parent
    
    # 清理构建目录
    print("🧹 清理构建目录...")
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # 构建前端项目
    print("🏗️ 构建前端项目...")
    frontend_dir = project_root / "frontend"
    os.chdir(frontend_dir)
    
    result = subprocess.run(["pnpm", "run", "build"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 前端构建失败: {result.stderr}")
        return False
    
    print("✅ 前端构建完成")
    
    # 回到项目根目录
    os.chdir(project_root)
    
    # 使用PyInstaller和.spec文件构建
    print("🔨 使用PyInstaller构建应用...")
    
    # 使用.spec文件构建，这样可以更好地控制构建过程
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "ksx_app.spec"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 构建失败: {result.stderr}")
        return False
    
    print("✅ 应用构建完成")
    
    # 创建安装脚本
    print("📝 创建安装脚本...")
    install_script = project_root / "install_macos.sh"
    with open(install_script, "w", encoding="utf-8") as f:
        f.write("""#!/bin/bash
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
""")
    
    # 设置执行权限
    os.chmod(install_script, 0o755)
    
    print("✅ 安装脚本创建完成")
    print(f"📁 输出目录: {dist_dir}")
    print(f"📱 应用程序: {dist_dir}/KSX门店管理系统.app")
    print(f"📜 安装脚本: {install_script}")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 构建成功！")
        print("💡 提示：首次运行时会自动安装Playwright浏览器")
    else:
        print("\n❌ 构建失败！")
        sys.exit(1)

