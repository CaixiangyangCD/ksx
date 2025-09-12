#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据查询API路由
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import sys
import os
# 尝试导入loguru，如果失败则使用标准logging
try:
    from loguru import logger
    LOGGER_AVAILABLE = True
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    LOGGER_AVAILABLE = False
    # print("警告: loguru不可用，使用标准logging模块")
from datetime import datetime, timedelta
import re

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from services.database_manager import get_db_manager
from services.config_database_manager import config_db_manager
from backend.models.schemas import PageResponse, DatabaseInfoResponse, DatesResponse

router = APIRouter(prefix="/api", tags=["data"])


@router.get("/data", response_model=PageResponse)
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
        # 调试：记录接收到的参数
        logger.info(f"接收到的参数: date_str={date_str}, mdshow={mdshow}, page={page}, page_size={page_size}")
        
        # 解析日期
        if date_str:
            try:
                query_date = datetime.strptime(date_str, "%Y-%m-%d")
                logger.info(f"解析日期参数: {date_str} -> {query_date}")
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="日期格式错误，请使用YYYY-MM-DD格式"
                )
        else:
            query_date = datetime.now()
            logger.info(f"使用默认日期: {query_date}")
        
        # 获取数据库管理器
        db_manager = get_db_manager()
        
        # 调试：检查数据库路径
        db_path = db_manager.get_database_path(query_date)
        logger.info(f"查询数据库路径: {db_path}")
        logger.info(f"数据库文件是否存在: {db_path.exists()}")
        
        # 查询数据
        result = db_manager.query_data(
            date=query_date,
            mdshow_filter=mdshow,
            page=page,
            page_size=page_size
        )
        
        logger.info(f"查询数据: 日期={query_date.date()}, 门店={mdshow}, 页码={page}, 返回{len(result['data'])}条记录")
        
        # 调试：检查返回数据的日期
        if result['data']:
            first_record_date = result['data'][0].get('createDateShow', 'N/A')
            logger.info(f"返回的第一条记录日期: {first_record_date}")
        
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


@router.get("/database/info", response_model=DatabaseInfoResponse)
async def get_database_info():
    """获取数据库信息"""
    try:
        db_manager = get_db_manager()
        info = db_manager.get_database_info()
        
        logger.info("获取数据库信息")
        return DatabaseInfoResponse(
            success=True,
            data=info
        )
        
    except Exception as e:
        logger.error(f"获取数据库信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/data/search", response_model=PageResponse)
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


@router.get("/dates", response_model=DatesResponse)
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
        return DatesResponse(
            success=True,
            dates=dates,
            total=len(dates)
        )
        
    except Exception as e:
        logger.error(f"获取日期列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/stores")
async def get_stores():
    """获取所有门店列表"""
    try:
        logger.info("开始获取门店列表")
        # 首先从配置数据库获取已存储的门店
        raw_stores = config_db_manager.get_all_stores()
        logger.info(f"原始门店数据: {raw_stores[:3] if raw_stores else '无数据'}")
        
        # 如果配置数据库中没有门店，从业务数据中提取门店列表
        if not raw_stores:
            db_manager = get_db_manager()
            
            # 获取最近30天的数据来提取门店
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            all_stores = set()
            current_date = start_date
            while current_date <= end_date:
                try:
                    result = db_manager.query_data(date=current_date, page=1, page_size=1000)
                    for item in result.get('data', []):
                        mdshow = item.get('MDShow', '')
                        if mdshow:
                            # 清理HTML标签
                            clean_name = re.sub(r'<[^>]+>', '', mdshow)
                            if clean_name.strip():
                                all_stores.add(clean_name.strip())
                except Exception as e:
                    logger.warning(f"查询日期 {current_date.date()} 的数据失败: {e}")
                
                current_date += timedelta(days=1)
            
            # 将提取的门店添加到配置数据库
            for store_name in sorted(all_stores):
                config_db_manager.add_store(store_name)
            
            # 重新获取门店列表
            raw_stores = config_db_manager.get_all_stores()
        
        # 转换为前端期望的格式
        stores = []
        for store in raw_stores:
            stores.append({
                'id': store['id'],  # 使用配置数据库中的真实ID
                'store_name': store['store_name'],  # 使用name字段作为store_name
                'created_at': store.get('created_at', '2025-01-01T00:00:00Z'),  # 使用真实时间
                'updated_at': store.get('updated_at', '2025-01-01T00:00:00Z')   # 使用真实时间
            })
        
        logger.info(f"转换后的门店数据: {stores[:3] if stores else '无数据'}")
        
        return {
            "success": True,
            "data": stores
        }
    except Exception as e:
        logger.error(f"获取门店列表失败: {e}")
        return {
            "success": False,
            "message": f"获取门店列表失败: {str(e)}"
        }
