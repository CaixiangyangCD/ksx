# KSX门店管理系统

## 项目概述

KSX门店管理系统是一个集数据采集、存储、查询和导出于一体的综合性管理平台。系统采用前后端分离架构，支持桌面应用和Web应用两种使用方式。

## 项目结构

```
ksx/
├── backend/                    # 后端服务
│   ├── api/                   # API路由模块
│   │   ├── data.py           # 数据查询API
│   │   ├── export.py         # 数据导出API
│   │   └── sync.py           # 数据同步API
│   ├── models/               # 数据模型
│   │   └── schemas.py        # Pydantic模型
│   ├── utils/                # 工具模块
│   │   └── excel_export.py   # Excel导出工具
│   ├── app.py                # FastAPI应用主文件
│   └── main.py               # 旧版主文件（待删除）
├── desktop/                   # 桌面应用
│   ├── ksx_desktop_app.py    # 桌面应用主程序
│   ├── start_desktop_app.bat # Windows启动脚本
│   ├── start_desktop_app.sh  # Linux/Mac启动脚本
│   └── README.md             # 桌面应用说明
├── frontend/                  # 前端应用
│   ├── src/                  # 源代码
│   │   ├── components/       # Vue组件
│   │   ├── types/           # TypeScript类型定义
│   │   ├── App.vue          # 主应用组件
│   │   └── main.ts          # 应用入口
│   ├── dist/                # 构建输出
│   └── 配置文件
├── services/                  # 服务模块
│   ├── crawler/             # 爬虫服务
│   │   ├── core/            # 核心模块
│   │   ├── utils/           # 工具模块
│   │   ├── crawler.py       # 爬虫主逻辑
│   │   ├── main.py          # 爬虫入口
│   │   └── README.md        # 爬虫说明
│   ├── database_manager.py  # 数据库管理
│   └── config_database_manager.py # 配置数据库管理
├── database/                 # 数据库文件
│   ├── 2025-08/            # 按月份组织的数据
│   ├── 2025-09/
│   └── config.db           # 配置文件数据库
├── pyproject.toml          # Python项目配置
├── uv.lock                 # 依赖锁定文件
└── README.md               # 项目说明
```

## 功能特性

### 🖥️ 桌面应用
- 基于PySide6的现代化桌面界面
- 集成Web浏览器显示前端界面
- 自动启动后端服务
- 跨平台支持（Windows、macOS、Linux）

### 🌐 Web应用
- 基于Vue 3 + TypeScript的现代化前端
- 响应式设计，支持移动端
- Ant Design Vue组件库
- 实时数据查询和展示

### 🔧 后端服务
- 基于FastAPI的高性能API服务
- 模块化架构，易于维护和扩展
- 完整的API文档
- 支持数据导出（CSV、Excel）

### 🕷️ 爬虫服务
- 多平台数据采集
- 自动化数据清洗和存储
- 完善的错误处理和重试机制
- 详细的日志记录

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- uv（Python包管理器）

### 安装依赖

```bash
# 安装Python依赖
uv sync

# 安装前端依赖
cd frontend
npm install
```

### 启动应用

#### 方式一：桌面应用（推荐）

```bash
# Windows
cd desktop
start_desktop_app.bat

# Linux/Mac
cd desktop
./start_desktop_app.sh
```

#### 方式二：分别启动

```bash
# 启动后端服务
cd backend
python app.py

# 启动前端服务
cd frontend
npm run dev
```

## 使用指南

### 数据同步

1. 在Web界面点击"同步数据"按钮
2. 选择要同步的日期
3. 系统自动启动爬虫程序获取数据

### 数据查询

- 支持按门店名称筛选
- 支持按日期筛选
- 分页显示，支持自定义每页数量

### 数据导出

- **CSV导出**: 支持按门店规则导出
- **Excel导出**: 支持按日期导出，自动格式化

### 配置管理

- **门店配置**: 设置需要导出的门店
- **字段配置**: 自定义导出字段

## 开发指南

### 添加新的API接口

1. 在 `backend/api/` 目录下创建新的路由文件
2. 在 `backend/models/schemas.py` 中定义数据模型
3. 在 `backend/app.py` 中注册路由

### 添加新的爬虫数据源

1. 在 `services/crawler/crawler.py` 中添加新的爬虫类
2. 实现必要的方法：`crawl()`, `parse()`, `save()`
3. 在 `services/crawler/main.py` 中注册新的爬虫

### 前端组件开发

1. 在 `frontend/src/components/` 目录下创建新组件
2. 使用TypeScript和Vue 3 Composition API
3. 遵循Ant Design Vue设计规范

## 部署说明

### 生产环境部署

1. 构建前端应用：
   ```bash
   cd frontend
   npm run build
   ```

2. 配置环境变量：
   ```bash
   export DATABASE_PATH=/path/to/database
   export API_HOST=0.0.0.0
   export API_PORT=18888
   ```

3. 启动服务：
   ```bash
   cd backend
   python app.py
   ```

### Docker部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync

EXPOSE 18888
CMD ["python", "backend/app.py"]
```

## 故障排除

### 常见问题

1. **端口占用**
   - 检查18888端口是否被占用
   - 修改配置文件中的端口设置

2. **数据库连接失败**
   - 检查数据库文件路径
   - 确保有足够的磁盘空间

3. **爬虫执行失败**
   - 检查网络连接
   - 查看爬虫日志文件

### 日志查看

```bash
# 查看API日志
tail -f logs/api_$(date +%Y-%m-%d).log

# 查看爬虫日志
tail -f services/crawler/logs/crawler_$(date +%Y-%m-%d).log
```

## 贡献指南

1. Fork 项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 更新日志

### v2.0.0 (2025-01-15)
- 🎉 重构项目结构，采用模块化架构
- ✨ 新增桌面应用支持
- 🔧 优化FastAPI服务，拆分代码模块
- 📚 完善文档和README
- 🗂️ 整合数据库文件到统一目录
- 🧹 清理无用文件和代码

### v1.0.0 (2025-01-01)
- 🎉 初始版本发布
- ✨ 基础数据查询功能
- 🕷️ 爬虫数据采集
- 📊 数据导出功能