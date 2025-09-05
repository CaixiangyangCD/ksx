# KSX数据爬虫

基于Playwright的KSX网站数据爬虫，通过拦截API网络请求获取数据。

## 功能特点

- 🔐 **自动登录** - 自动完成网站登录流程
- 🌐 **API拦截** - 拦截/UIProcessor网络请求获取原始数据
- 📄 **智能分页** - 基于API返回的hasMore字段判断分页结束
- 🔄 **数据去重** - 基于ID字段自动去重
- 📊 **CSV导出** - 自动保存数据到CSV文件
- 🎯 **准确提取** - 获取完整的67个字段，包含ID等关键字段

## 项目结构

```
crawler/
├── main.py              # 主程序入口
├── crawler.py           # 核心爬虫类
├── config.py           # 配置文件
├── utils.py            # 工具函数
├── start.bat           # Windows启动脚本
├── requirements.txt    # Python依赖
├── data/              # 数据输出目录
├── logs/              # 日志目录
└── screenshots/       # 截图目录
```

## 快速开始

### 1. 环境准备

确保已安装Python 3.8+，然后安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 安装Playwright浏览器

```bash
playwright install chromium
```

### 3. 运行爬虫

**Windows用户：**
双击运行 `start.bat`

**命令行用户：**
```bash
python main.py
```

## 配置说明

### 基本配置 (config.py)

```python
# 登录信息
WEBSITE_URL = "https://ksx.dahuafuli.com:8306/"
USERNAME = "fsrm001"
PASSWORD = "fsrm001"

# 浏览器设置
HEADLESS = False  # 是否无头模式
TIMEOUT = 30000   # 超时时间(毫秒)
```

### 日期范围

默认抓取昨天的数据，可在 `crawler.py` 中的 `set_date_and_search()` 方法中修改：

```python
# 计算目标日期
yesterday = datetime.now() - timedelta(days=1)  # 昨天
# yesterday = datetime.now() - timedelta(days=2)  # 前天
```

## 输出数据

### 数据格式

爬虫会在 `data/` 目录下生成CSV文件，文件名格式：
`ksx_api_data_YYYYMMDD_HHMMSS.csv`

### 数据字段

包含67个字段，主要包括：
- **ID** - 记录唯一标识符
- **MDShow** - 门店信息
- **area** - 区域
- **createDateShow** - 创建日期
- **dailyXXX** - 日度指标
- **monthlyXXX** - 月度指标
- **totalScore** - 总评分
- 等等...

### 数据统计

每次运行后会显示：
- 总记录数
- 字段数量
- 去重前后对比
- 文件保存路径

## 技术实现

### API拦截机制

1. **请求监听** - 监听所有网络响应
2. **URL过滤** - 筛选包含`/UIProcessor`的请求
3. **数据解析** - 解析JSON响应获取data和pageInfo
4. **状态判断** - 通过`hasMore`字段判断是否还有更多页

### 分页策略

```python
# 基于API返回信息进行分页
{
    "success": true,
    "data": [...],  # 当前页数据
    "pageInfo": {
        "pageSize": 50,
        "pageNo": 1,
        "hasMore": true,  # 是否还有更多页
        "total": 346      # 总记录数
    }
}
```

### 错误处理

- **连接超时** - 自动重试机制
- **元素未找到** - 等待和重试
- **数据为空** - 记录日志并跳过
- **浏览器崩溃** - 自动清理资源

## 日志系统

### 日志文件

- `crawler.log` - 主要运行日志
- `api_extraction.log` - API提取详细日志

### 日志级别

- **INFO** - 正常操作信息
- **WARNING** - 警告信息
- **ERROR** - 错误信息

### 日志示例

```
2025-09-04 17:49:03,566 - crawler - INFO - ✅ 成功获取数据: 50 条记录
2025-09-04 17:49:03,566 - crawler - INFO - 📄 分页信息: {'pageSize': 50, 'pageNo': 1, 'hasMore': True, 'total': 346}
```

## 故障排除

### 常见问题

1. **登录失败**
   - 检查用户名密码是否正确
   - 确认网站是否正常访问

2. **数据为空**
   - 检查日期范围是否有数据
   - 确认搜索条件是否正确

3. **浏览器启动失败**
   - 运行 `playwright install chromium`
   - 检查系统环境变量

4. **网络请求超时**
   - 增加超时时间设置
   - 检查网络连接

### 调试模式

在 `main.py` 中设置：

```python
crawler = KSXCrawler(headless=False)  # 显示浏览器窗口
```

## 更新日志

### v2.0.0 (2025-09-04)
- ✨ 重构为API拦截模式
- 🔄 移除DOM解析方法
- 📊 新增完整字段支持(67个字段)
- 🎯 基于ID字段的数据去重
- 📄 智能分页判断
- 🧹 清理项目结构

### v1.0.0
- 🎉 初始版本
- 🔐 基本登录功能
- 📄 DOM元素数据提取

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交Issue和Pull Request！