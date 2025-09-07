#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据查询API路由
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import sys
import os
from loguru import logger

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from services.database_manager import get_db_manager
from backend.models.schemas import DataResponse

router = APIRouter(prefix="/api", tags=["data"])


@router.get("/data", response_model=DataResponse)
async def get_data(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    mdshow: str = Query("", description="门店名称筛选"),
    date_str: Optional[str] = Query(None, description="日期筛选")
):
    """
    获取数据列表
    """
    try:
        db_manager = get_db_manager()
        
        # 构建查询条件
        conditions = []
        params = {}
        
        if mdshow:
            conditions.append("MDShow LIKE :mdshow")
            params["mdshow"] = f"%{mdshow}%"
        
        if date_str:
            conditions.append("createDateShow = :date_str")
            params["date_str"] = date_str
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 计算偏移量
        offset = (page - 1) * size
        
        # 使用DatabaseManager的query_data方法
        from datetime import datetime
        query_date = None
        if date_str:
            try:
                query_date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        result = db_manager.query_data(
            date=query_date,
            mdshow_filter=mdshow if mdshow else None,
            page=page,
            page_size=size
        )
        
        data = result.get('data', [])
        total = result.get('total', 0)
        
        return DataResponse(
            success=True,
            data=data,
            total=total,
            page=page,
            page_size=size
        )
        
    except Exception as e:
        logger.error(f"获取数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/stores", response_model=DataResponse)
async def get_stores():
    """
    获取门店列表
    """
    try:
        logger.info("=== 开始获取门店列表 ===")
        logger.info("当前文件: backend/api/data.py")
        db_manager = get_db_manager()
        
        # 获取原始门店数据
        raw_stores = db_manager.get_stores()
        logger.info(f"原始门店数据: {raw_stores}")
        
        # 转换为前端期望的格式
        stores = []
        for i, store in enumerate(raw_stores):
            stores.append({
                'id': i + 1,  # 生成唯一ID
                'store_name': store['name'],
                'created_at': '',  # 暂时为空
                'updated_at': ''   # 暂时为空
            })
        
        logger.info(f"转换后的门店数据: {stores}")
        logger.info("=== 门店列表获取完成 ===")
        
        return DataResponse(
            success=True,
            data=stores
        )
        
    except Exception as e:
        logger.error(f"获取门店列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取门店列表失败: {str(e)}")
