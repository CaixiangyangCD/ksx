# KSX门店管理系统 - 桌面应用

## 简介

KSX门店管理系统桌面版是一个基于PySide6的桌面应用程序，集成了前端Vue.js界面和FastAPI后端服务。用户可以通过桌面应用直接访问完整的门店数据管理系统。

## 功能特性

- 🖥️ **桌面应用界面**: 基于PySide6的现代化桌面界面
- 🌐 **集成Web服务**: 自动启动前端和后端服务
- 📊 **数据管理**: 门店数据查询、搜索、导出
- 📈 **Excel导出**: 支持增量Excel导出功能
- ⚙️ **配置管理**: 门店配置和字段配置
- 🔄 **服务管理**: 内置服务重启和状态监控

## 系统要求

- Python 3.8 或更高版本
- 操作系统：Windows 10+, macOS 10.14+, Ubuntu 18.04+
- 内存：至少 4GB RAM
- 磁盘空间：至少 1GB 可用空间

## 安装和启动

### 方法一：使用启动脚本（推荐）

#### Windows用户
```bash
# 双击运行
start_desktop_app.bat

# 或在命令行运行
start_desktop_app.bat
```

#### macOS/Linux用户
```bash
# 运行启动脚本
./start_desktop_app.sh

# 或使用Python直接运行
python3 start_desktop_app.py
```

### 方法二：手动启动

1. **安装依赖**
```bash
pip install PySide6 PySide6-WebEngine uv
```

2. **构建前端**
```bash
cd frontend
npm install
npm run build
cd ..
```

3. **启动桌面应用**
```bash
python ksx_desktop_app_with_api.py
```

## 使用说明

### 启动应用

1. 运行启动脚本后，系统会自动：
   - 检查并安装必要的依赖包
   - 构建前端项目（如果需要）
   - 启动FastAPI后端服务（端口8080）
   - 启动前端静态文件服务（随机端口）
   - 打开桌面应用窗口

2. 应用启动后，您会看到：
   - 顶部工具栏显示服务状态
   - 主窗口显示Vue.js前端界面
   - 状态栏显示当前操作状态

### 界面功能

#### 顶部工具栏
- **标题**: 显示应用名称
- **API状态**: 显示FastAPI服务状态（端口8080）
- **前端状态**: 显示前端服务状态
- **刷新按钮**: 刷新当前页面
- **重启服务按钮**: 重启所有服务
- **开发者工具按钮**: 打开浏览器开发者工具

#### 主界面
- 完整的Vue.js前端界面
- 支持所有Web版本的功能
- 包括数据查询、搜索、导出等

### 服务管理

#### 自动启动
- FastAPI服务自动在端口8080启动
- 前端服务自动在可用端口启动
- 两个服务都会在应用启动时自动运行

#### 手动重启
- 点击"重启服务"按钮可以重启所有服务
- 系统会先停止现有服务，然后重新启动

#### 服务状态监控
- 实时显示API和前端服务的运行状态
- 绿色表示运行中，红色表示未启动，黄色表示启动中

## 故障排除

### 常见问题

#### 1. 依赖安装失败
```bash
# 手动安装依赖
pip install --upgrade pip
pip install PySide6 PySide6-WebEngine uv
```

#### 2. 前端构建失败
```bash
# 清理并重新构建
cd frontend
rm -rf node_modules dist
npm install
npm run build
cd ..
```

#### 3. 端口被占用
- FastAPI默认使用8080端口
- 如果端口被占用，请关闭占用该端口的程序
- 或修改代码中的端口配置

#### 4. 应用无法启动
- 检查Python版本（需要3.8+）
- 检查所有依赖是否正确安装
- 查看控制台错误信息

### 日志查看

应用运行时的日志信息会显示在控制台中，包括：
- 服务启动状态
- 错误信息
- 调试信息

## 开发说明

### 项目结构
```
ksx_desktop_app_with_api.py    # 主桌面应用文件
start_desktop_app.py           # 启动脚本
start_desktop_app.bat          # Windows启动脚本
start_desktop_app.sh           # macOS/Linux启动脚本
frontend/dist/                 # 前端构建文件
backend/                       # FastAPI后端
```

### 自定义配置

#### 修改端口
在`ksx_desktop_app_with_api.py`中修改：
```python
self.api_port = 8080  # 修改为其他端口
```

#### 修改窗口大小
```python
self.setGeometry(100, 100, 1400, 900)  # 修改窗口大小
```

## 技术支持

如果遇到问题，请：
1. 查看控制台错误信息
2. 检查系统要求是否满足
3. 确认所有依赖已正确安装
4. 联系技术支持团队

## 更新日志

### v1.0.0
- 初始版本发布
- 集成FastAPI和Vue.js
- 支持桌面应用界面
- 自动服务管理
