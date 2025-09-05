# KSX门店管理系统

一个基于Vue3 + TypeScript + Ant Design Vue的门店管理系统，支持桌面应用和Web应用两种使用方式。

## ✨ 功能特性

- 🏪 **门店管理**: 基于data.json的126条门店数据
- 🔍 **智能搜索**: 支持区域、门店名称、日期范围等多维度搜索
- 📊 **数据展示**: 完整的门店指标数据表格展示
- 📤 **数据导出**: 支持CSV格式数据导出
- 🎨 **现代UI**: 基于Ant Design Vue 4.x的现代化界面设计
- 💻 **桌面应用**: 使用PySide6封装的独立桌面应用
- 🌐 **Web应用**: 支持传统Web浏览器访问

## 🚀 快速开始

### 桌面应用（推荐）

1. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动桌面应用**
   ```bash
   # Windows
   start_desktop.bat
   
   # 或直接运行
   python ksx_desktop_app.py
   ```

### Web应用

1. **安装项目依赖**
   ```bash
   npm install
   ```

2. **开发模式**
   ```bash
   npm run dev
   ```

3. **构建生产版本**
   ```bash
   npm run build
   ```

## 🏗️ 项目结构

```
ksx/
├── dist/                    # Vue构建输出目录
│   └── index.html         # 主页面文件
├── src/                    # Vue源代码
│   ├── components/        # Vue组件
│   │   ├── SearchBar.vue  # 搜索栏组件
│   │   └── DataTable.vue  # 数据表格组件
│   ├── data/              # 数据相关
│   │   └── mockData.ts    # 模拟数据生成
│   ├── types/             # TypeScript类型定义
│   │   └── index.ts       # 接口定义
│   ├── App.vue            # 主应用组件
│   └── main.ts            # 应用入口
├── data.json              # 原始数据文件
├── ksx_desktop_app.py     # PySide6桌面应用
├── requirements.txt        # Python依赖
├── start_desktop.bat      # Windows启动脚本
└── README.md              # 项目说明
```

## 🎯 桌面应用特性

### 核心功能
- **本地HTTP服务器**: 自动启动本地服务器，正确加载Vue应用
- **原生体验**: 使用PySide6 QtWebEngine提供原生桌面应用体验
- **智能检测**: 自动检测构建文件状态，提供友好的错误提示
- **端口管理**: 自动查找可用端口，避免端口冲突

### 界面组件
- **顶部工具栏**: 应用标题、刷新按钮、开发者工具
- **Web视图**: 嵌入式浏览器，显示Vue应用
- **状态栏**: 显示应用状态和加载信息

### 技术特点
- **HTTP协议**: 使用本地HTTP服务器正确加载Vue应用
- **资源管理**: 自动处理CSS、JS、图片等静态资源
- **模块支持**: 支持ES模块和现代JavaScript特性
- **安全设置**: 配置WebEngine允许本地服务器访问
- **错误处理**: 完善的错误检测和用户提示

## 🔧 技术栈

### 前端
- **Vue 3**: 使用Composition API
- **TypeScript**: 类型安全的JavaScript
- **Ant Design Vue 4.x**: 企业级UI组件库
- **Vite**: 现代化构建工具

### 桌面应用
- **PySide6**: Qt for Python
- **QtWebEngine**: 嵌入式Web浏览器引擎
- **Python 3.8+**: 运行时环境

## 📋 环境要求

### 桌面应用
- Python 3.8+
- PySide6 >= 6.5.0
- PySide6-WebEngine >= 6.5.0

### Web应用
- Node.js 16+
- npm 8+

## 🚀 使用流程

1. **构建Vue项目**
   ```bash
   npm run build
   ```

2. **启动桌面应用**
   ```bash
   python ksx_desktop_app.py
   ```

3. **应用将自动启动本地HTTP服务器并加载Vue应用**

## ❓ 常见问题

### Q: 桌面应用无法启动？
A: 请检查：
- Python版本是否为3.8+
- 是否安装了PySide6和PySide6-WebEngine
- dist文件夹是否存在且包含index.html

### Q: 应用显示空白页面？
A: 请检查：
- dist文件夹是否完整
- 是否运行了`npm run build`
- 浏览器控制台是否有错误信息

### Q: 如何更新应用？
A: 重新构建Vue项目后，刷新桌面应用即可

## 📝 开发说明

### 数据字段
系统基于`data.json`文件，包含以下主要字段：
- 门店基本信息（区域、名称、创建日期）
- 评分指标（最终得分、各项评分）
- 业务指标（取消率、退款率、评分等）
- 库存指标（有货率、缺货情况等）

### 组件设计
- **SearchBar**: 支持多条件搜索，包含区域选择、门店名称、日期范围
- **DataTable**: 响应式数据表格，支持分页、排序、自定义渲染

## 📄 许可证

MIT License

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

---

**注意**: 桌面应用需要先构建Vue项目（`npm run build`），然后才能正常启动。


这样还是有问题，你现在获取的数据数量明显不对，而且没有办法做去重，因为缺少了id字段；你可以抓取网页的网络请求吗？它有一个/UIProcessor的请求，它的返回消息里格式如下：{success: true, data: [], pageInfo: {
  "pageSize": 50,
  "pageNo": 1,
  "hasMore": true,
  "total": 346
}}，其中data就是当前页数据，也就是我们之前通过dom元素抓取的数据，pageInfo里是当前页信息，通过hasMore就知道是否是最后一页，同时total就是此次符合查询条件的数据总条数