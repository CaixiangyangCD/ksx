#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KSX数据查询API服务
基于FastAPI的后端服务，提供数据查询接口
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import sys
import os
from loguru import logger

# 添加项目根目录到路径，以便导入services模块
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from services.database_manager import get_db_manager

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
logger.add(
    "logs/api_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}",
    level="DEBUG",
    rotation="1 day",
    retention="30 days",
    compression="zip",
    encoding="utf-8"
)

# 响应模型
class PageResponse(BaseModel):
    """分页响应模型"""
    data: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int
    success: bool = True
    message: str = "查询成功"

class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    message: str
    error_code: Optional[str] = None

# API路由
@app.get("/", response_model=Dict[str, str])
async def root():
    """根路径"""
    return {
        "message": "KSX数据查询API服务",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/api/health", response_model=Dict[str, str])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/data", response_model=PageResponse)
async def get_data(
    date_str: Optional[str] = Query(None, description="查询日期 (YYYY-MM-DD)，默认为今天"),
    mdshow: Optional[str] = Query(None, description="门店名称模糊查询"),
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页记录数，最大100")
):
    """
    获取KSX数据
    
    - **date_str**: 查询日期，格式YYYY-MM-DD，默认为今天
    - **mdshow**: 门店名称模糊查询，可选
    - **page**: 页码，从1开始
    - **page_size**: 每页记录数，最大100
    """
    try:
        # 解析日期
        if date_str:
            try:
                query_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="日期格式错误，请使用YYYY-MM-DD格式"
                )
        else:
            query_date = datetime.now()
        
        # 获取数据库管理器
        db_manager = get_db_manager()
        
        # 查询数据
        result = db_manager.query_data(
            date=query_date,
            mdshow_filter=mdshow,
            page=page,
            page_size=page_size
        )
        
        logger.info(f"查询数据: 日期={query_date.date()}, 门店={mdshow}, 页码={page}, 返回{len(result['data'])}条记录")
        
        return PageResponse(
            data=result['data'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size'],
            total_pages=result['total_pages']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@app.get("/api/database/info", response_model=Dict[str, Any])
async def get_database_info():
    """获取数据库信息"""
    try:
        db_manager = get_db_manager()
        info = db_manager.get_database_info()
        
        logger.info("获取数据库信息")
        return {
            "success": True,
            "data": info
        }
        
    except Exception as e:
        logger.error(f"获取数据库信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@app.get("/api/data/search", response_model=PageResponse)
async def search_data(
    q: str = Query(..., description="搜索关键词（门店名称）"),
    date_str: Optional[str] = Query(None, description="查询日期 (YYYY-MM-DD)，默认为今天"),
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页记录数，最大100")
):
    """
    搜索门店数据
    
    这是一个便捷的搜索接口，等同于在get_data接口中设置mdshow参数
    """
    return await get_data(
        date_str=date_str,
        mdshow=q,
        page=page,
        page_size=page_size
    )

@app.get("/api/dates", response_model=Dict[str, Any])
async def get_available_dates():
    """获取有数据的日期列表"""
    try:
        db_manager = get_db_manager()
        info = db_manager.get_database_info()
        
        dates = []
        for month_info in info['months']:
            for db_info in month_info['databases']:
                # 从数据库文件名提取日期
                if db_info['name'].startswith('ksx_') and db_info['name'].endswith('.db'):
                    date_str = db_info['name'][4:-3]  # 移除 'ksx_' 前缀和 '.db' 后缀
                    dates.append(date_str)
        
        dates.sort(reverse=True)  # 按日期倒序排列
        
        logger.info(f"获取可用日期列表: {len(dates)}个日期")
        return {
            "success": True,
            "dates": dates,
            "total": len(dates)
        }
        
    except Exception as e:
        logger.error(f"获取日期列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

# 异常处理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404错误处理"""
    return {
        "success": False,
        "message": "接口不存在",
        "error_code": "NOT_FOUND"
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """500错误处理"""
    logger.error(f"服务器内部错误: {exc}")
    return {
        "success": False,
        "message": "服务器内部错误",
        "error_code": "INTERNAL_ERROR"
    }

if __name__ == "__main__":
    import uvicorn
    
    # 创建logs目录
    os.makedirs("logs", exist_ok=True)
    
    logger.info("启动KSX数据查询API服务...")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        log_level="info"
    )
