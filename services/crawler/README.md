# KSX爬虫服务

## 概述

KSX爬虫服务是一个用于抓取门店数据的自动化工具，支持多平台数据采集和存储。

## 项目结构

```
services/crawler/
├── README.md              # 项目说明文档
├── main.py               # 主程序入口
├── config.py             # 配置文件
├── crawler.py            # 核心爬虫逻辑
├── init_database.py      # 数据库初始化脚本
├── core/                 # 核心模块
│   └── __init__.py
├── utils/                # 工具模块
│   ├── __init__.py
│   └── utils.py          # 通用工具函数
└── logs/                 # 日志目录（运行时生成）
```

## 功能特性

- **多平台支持**: 支持美团、饿了么、京东等多个平台的数据抓取
- **数据清洗**: 自动清洗和标准化数据格式
- **数据库存储**: 支持SQLite数据库存储
- **日志记录**: 完整的操作日志记录
- **错误处理**: 完善的错误处理和重试机制
- **配置管理**: 灵活的配置管理

## 安装依赖

项目使用 `uv` 作为包管理器，请确保已安装 `uv`：

```bash
# 安装uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

## 使用方法

### 1. 基本使用

```bash
# 爬取昨天的数据
python main.py

# 爬取指定日期的数据
python main.py --date 2025-01-15

# 查看帮助
python main.py --help
```

### 2. 配置说明

编辑 `config.py` 文件来配置爬虫参数：

```python
# 数据库配置
DATABASE_PATH = "database/ksx_data.db"

# 爬虫配置
CRAWLER_CONFIG = {
    "retry_times": 3,
    "timeout": 30,
    "delay": 1
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
}
```

### 3. 数据库初始化

首次运行前，可以使用 `init_database.py` 生成测试数据：

```bash
python init_database.py
```

## API接口

爬虫服务通过以下API接口与前端和后端服务交互：

- `GET /api/data` - 获取数据列表
- `POST /api/sync-data` - 同步数据
- `GET /api/stores` - 获取门店列表

## 开发指南

### 添加新的数据源

1. 在 `crawler.py` 中添加新的爬虫类
2. 实现必要的方法：`crawl()`, `parse()`, `save()`
3. 在 `main.py` 中注册新的爬虫

### 自定义数据处理

在 `utils/utils.py` 中添加自定义的数据处理函数。

### 日志配置

日志文件保存在 `logs/` 目录下，按日期自动分割。

## 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   # 清理缓存重新安装
   uv cache clean
   uv sync
   ```

2. **数据库连接失败**
   - 检查数据库文件路径是否正确
   - 确保有足够的磁盘空间
   - 检查文件权限

3. **爬虫执行失败**
   - 检查网络连接
   - 查看日志文件了解详细错误信息
   - 确认目标网站是否可访问

### 日志查看

```bash
# 查看最新日志
tail -f logs/crawler_$(date +%Y-%m-%d).log

# 查看错误日志
grep "ERROR" logs/crawler_*.log
```

## 性能优化

- 调整并发数量以平衡性能和稳定性
- 使用适当的延迟避免被反爬虫机制检测
- 定期清理日志文件释放磁盘空间

## 安全注意事项

- 遵守网站的robots.txt规则
- 不要过于频繁地请求同一网站
- 保护敏感配置信息
- 定期更新依赖包以修复安全漏洞

## 版本历史

- v1.0.0 - 初始版本，支持基本的数据抓取功能
- v1.1.0 - 添加多平台支持和数据清洗功能
- v1.2.0 - 优化性能和错误处理机制

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。