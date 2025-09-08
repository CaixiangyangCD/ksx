#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建 DMG 安装包
"""

import os
import subprocess
import shutil
from pathlib import Path

def create_dmg():
    """创建 DMG 安装包"""
    print("🚀 开始创建 DMG 安装包...")
    
    # 检查 dist 目录
    dist_dir = Path("dist")
    app_path = dist_dir / "KSX门店管理系统.app"
    
    if not app_path.exists():
        print("❌ 找不到应用文件，请先运行 python build.py")
        return False
    
    # 创建临时目录
    temp_dir = Path("temp_dmg")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # 复制应用到临时目录
    print("📁 复制应用到临时目录...")
    shutil.copytree(app_path, temp_dir / "KSX门店管理系统.app")
    
    # 创建 DMG
    dmg_name = "KSX门店管理系统.dmg"
    dmg_path = dist_dir / dmg_name
    
    print("📦 创建 DMG 文件...")
    try:
        # 删除已存在的 DMG
        if dmg_path.exists():
            dmg_path.unlink()
        
        # 使用 hdiutil 创建 DMG
        cmd = [
            "hdiutil", "create",
            "-volname", "KSX门店管理系统",
            "-srcfolder", str(temp_dir),
            "-ov", "-format", "UDZO",
            str(dmg_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ DMG 创建成功: {dmg_path}")
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
            
            # 显示文件大小
            size_mb = dmg_path.stat().st_size / (1024 * 1024)
            print(f"📊 DMG 文件大小: {size_mb:.1f} MB")
            
            return True
        else:
            print(f"❌ DMG 创建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 创建 DMG 时出错: {e}")
        return False
    finally:
        # 清理临时目录
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    success = create_dmg()
    if success:
        print("\n🎉 DMG 安装包创建完成！")
        print("💡 现在可以将 DMG 文件分发给其他用户")
        print("📋 用户使用说明：")
        print("   1. 双击 DMG 文件")
        print("   2. 将应用拖拽到 Applications 文件夹")
        print("   3. 在 Applications 中启动应用")
        print("   4. 首次运行可能需要右键点击 → 打开")
    else:
        print("\n❌ DMG 创建失败")
