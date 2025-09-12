# KSX门店管理系统 - Windows构建指南

## 概述

本指南将帮助您在Windows系统上构建和运行KSX门店管理系统。

## 系统要求

- Windows 10/11 (64位)
- Python 3.8+ 
- Node.js 16+
- pnpm (推荐) 或 npm
- Git (可选，用于克隆代码)

## 快速开始

### 1. 自动设置开发环境

运行自动设置脚本：

```batch
setup_windows_dev.bat
```

这个脚本会自动：
- 检查Python和Node.js环境
- 安装所有必要的依赖
- 构建前端项目
- 安装Playwright浏览器
- 创建启动脚本

### 2. 启动应用

#### 开发模式
```batch
start_dev.bat
```

#### 生产模式
```batch
start_windows_app.bat
```

## 手动设置

如果自动设置失败，可以手动执行以下步骤：

### 1. 安装Python依赖

```batch
pip install -r requirements.txt
```

或者使用uv：
```batch
uv sync
```

### 2. 安装前端依赖

```batch
cd frontend
pnpm install
# 或者
npm install
```

### 3. 构建前端

```batch
pnpm run build
# 或者
npm run build
```

### 4. 安装Playwright浏览器

```batch
python -m playwright install chromium
```

## 构建Windows可执行文件

### 1. 构建应用

```batch
python build_windows.py
```

这将创建：
- `dist/KSX门店管理系统.exe` - 可执行文件
- `install_windows.bat` - 安装脚本

### 2. 创建安装包

```batch
python create_installer.py
```

这将创建：
- 便携版ZIP压缩包
- NSIS安装包（如果安装了NSIS）

## 文件说明

### 构建脚本
- `build_windows.py` - Windows构建脚本
- `ksx_app_windows.spec` - PyInstaller配置文件
- `create_installer.py` - 安装包创建脚本

### 启动脚本
- `start_windows_app.bat` - 生产环境启动脚本
- `start_dev.bat` - 开发环境启动脚本
- `setup_windows_dev.bat` - 开发环境设置脚本

### 安装脚本
- `install_windows.bat` - Windows安装脚本

## 常见问题

### 1. Python环境问题

**问题**: 提示"未找到Python"
**解决**: 
- 确保Python已正确安装
- 将Python添加到系统PATH
- 重启命令行窗口

### 2. Node.js环境问题

**问题**: 提示"未找到Node.js"
**解决**:
- 下载并安装Node.js: https://nodejs.org/
- 确保npm可用

### 3. 前端构建失败

**问题**: 前端构建失败
**解决**:
- 检查Node.js版本（需要16+）
- 删除`node_modules`文件夹重新安装
- 使用管理员权限运行

### 4. PySide6安装失败

**问题**: PySide6安装失败
**解决**:
- 升级pip: `python -m pip install --upgrade pip`
- 使用国内镜像: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple PySide6`

### 5. Playwright浏览器问题

**问题**: Playwright浏览器安装失败
**解决**:
- 检查网络连接
- 使用管理员权限运行
- 手动下载浏览器文件

### 6. 端口占用问题

**问题**: 端口被占用
**解决**:
- 应用会自动清理端口占用
- 手动关闭占用端口的程序
- 重启计算机

## 性能优化

### 1. 减少启动时间
- 预安装Playwright浏览器
- 使用SSD硬盘
- 关闭不必要的后台程序

### 2. 减少内存占用
- 关闭其他应用程序
- 使用64位Python
- 定期重启应用

## 部署说明

### 1. 便携版部署
- 解压ZIP文件到目标目录
- 运行`启动KSX门店管理系统.bat`
- 无需安装，直接使用

### 2. 安装版部署
- 运行NSIS安装包
- 按提示完成安装
- 从开始菜单或桌面启动

### 3. 企业部署
- 使用组策略部署
- 配置自动更新
- 设置防火墙规则

## 技术支持

如遇到问题，请：
1. 查看错误日志
2. 检查系统要求
3. 联系技术支持团队

## 更新日志

### v1.0.0
- 初始Windows版本
- 支持Windows 10/11
- 自动环境检测和设置
- 便携版和安装版支持
