#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KSX数据查询API服务
基于FastAPI的后端服务，提供数据查询接口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from loguru import logger

# 添加项目根目录到路径，以便导入services模块
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 导入API路由
from backend.api import data, sync, export

# 创建FastAPI应用
app = FastAPI(
    title="KSX数据查询API",
    description="KSX门店数据查询服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置日志
try:
    logger.remove()
    
    # 确定日志目录
    if getattr(sys, 'frozen', False):
        # 打包环境：使用exe同目录下的logs文件夹
        from pathlib import Path
        log_dir = Path(sys.executable).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = str(log_dir / "api_{time:YYYY-MM-DD}.log")
    else:
        # 开发环境：使用项目根目录下的logs文件夹
        log_file = "logs/api_{time:YYYY-MM-DD}.log"
    
    # 添加控制台日志处理器（仅在开发环境）
    if not getattr(sys, 'frozen', False):
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
            level="INFO"
        )
    
    # 添加文件日志处理器
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )
    
    logger.info("后端日志系统初始化成功")
    
except Exception as e:
    # 如果日志配置失败，使用基本的print输出
    # print(f"日志系统初始化失败: {e}", file=sys.stderr)
    # 创建一个简单的logger包装器
    class SimpleLogger:
        def info(self, msg): print(f"INFO: {msg}", file=sys.stderr)
        def error(self, msg): print(f"ERROR: {msg}", file=sys.stderr)
        def warning(self, msg): print(f"WARNING: {msg}", file=sys.stderr)
        def debug(self, msg): print(f"DEBUG: {msg}", file=sys.stderr)
    logger = SimpleLogger()

# 注册路由
app.include_router(data.router)
app.include_router(sync.router)
app.include_router(export.router)


@app.get("/", response_model=dict)
async def root():
    """根路径"""
    return {
        "message": "KSX数据查询API服务",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/api/health", response_model=dict)
async def health_check():
    """健康检查"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    # 创建logs目录
    os.makedirs("logs", exist_ok=True)
    
    logger.info("启动KSX数据查询API服务...")
    
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=18888,
        reload=True,
        log_level="info"
    )


