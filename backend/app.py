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
from backend import main

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
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 注册路由
app.include_router(data.router)
app.include_router(sync.router)
app.include_router(export.router)

# 注册main.py中的路由
app.include_router(main.app.router)


@app.get("/")
async def root():
    """根路径"""
    return {"message": "KSX数据查询API服务", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18888)


