#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导出API路由
"""

from fastapi import APIRouter, HTTPException
import sys
import os
from loguru import logger

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from services.database_manager import get_db_manager
from services.config_database_manager import config_db_manager
from backend.models.schemas import (
    ExportDataRequest, ExportExcelRequest, ExportResponse,
    ExportRuleRequest, ExportFieldRuleRequest, ConfigResponse
)
from backend.utils.excel_export import create_excel_file, create_csv_content, generate_filename

router = APIRouter(prefix="/api", tags=["export"])


@router.post("/export-data", response_model=ExportResponse)
async def export_data(request: ExportDataRequest):
    """
    导出CSV数据
    """
    try:
        db_manager = get_db_manager()
        
        # 构建查询条件
        if request.selected_stores:
            placeholders = ",".join([f":store_{i}" for i in range(len(request.selected_stores))])
            where_clause = f"MDShow IN ({placeholders})"
            params = {f"store_{i}": store for i, store in enumerate(request.selected_stores)}
        else:
            where_clause = "1=1"
            params = {}
        
        # 查询数据
        query = f"""
        SELECT * FROM ksx_data 
        WHERE {where_clause}
        ORDER BY createDateShow DESC, ID DESC
        """
        
        data = db_manager.execute_query(query, params)
        
        if not data:
            return ExportResponse(
                success=False,
                message="没有数据可导出"
            )
        
        # 生成CSV内容
        csv_content = create_csv_content(data)
        filename = generate_filename(f"ksx_csv_export_{request.rule_name}", "csv")
        
        return ExportResponse(
            success=True,
            filename=filename,
            csv_content=csv_content,
            count=len(data)
        )
        
    except Exception as e:
        logger.error(f"导出CSV数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出CSV数据失败: {str(e)}")


@router.post("/export-excel", response_model=ExportResponse)
async def export_excel(request: ExportExcelRequest):
    """
    导出Excel数据
    """
    try:
        db_manager = get_db_manager()
        
        # 构建查询条件
        conditions = []
        params = {}
        
        if request.date:
            conditions.append("createDateShow = :date")
            params["date"] = request.date
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 查询数据
        query = f"""
        SELECT * FROM ksx_data 
        WHERE {where_clause}
        ORDER BY createDateShow DESC, ID DESC
        """
        
        data = db_manager.execute_query(query, params)
        
        if not data:
            return ExportResponse(
                success=False,
                message="没有数据可导出"
            )
        
        # 生成文件名
        filename = generate_filename("ksx_excel_export", "xlsx")
        
        # 创建Excel文件
        file_path = create_excel_file(data, filename)
        
        if not file_path:
            return ExportResponse(
                success=False,
                message="创建Excel文件失败"
            )
        
        return ExportResponse(
            success=True,
            filename=filename,
            file_path=file_path,
            count=len(data)
        )
        
    except Exception as e:
        logger.error(f"导出Excel数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出Excel数据失败: {str(e)}")


@router.get("/export-rule", response_model=ConfigResponse)
async def get_export_rule():
    """
    获取导出规则
    """
    try:
        rule = config_db_manager.get_export_rule()
        
        if rule and rule.get('selected_stores'):
            # 获取门店列表以将门店名称转换为ID
            db_manager = get_db_manager()
            raw_stores = db_manager.get_stores()
            
            # 创建门店名称到ID的映射
            store_name_to_id = {}
            for i, store in enumerate(raw_stores):
                store_name_to_id[store['name']] = i + 1
            
            # 将门店名称转换为ID
            selected_store_ids = []
            for store_name in rule['selected_stores']:
                if store_name in store_name_to_id:
                    selected_store_ids.append(store_name_to_id[store_name])
            
            # 更新规则中的selected_stores为ID数组
            rule['selected_stores'] = selected_store_ids
        
        return ConfigResponse(
            success=True,
            data=rule
        )
    except Exception as e:
        logger.error(f"获取导出规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取导出规则失败: {str(e)}")


@router.post("/export-rule", response_model=ConfigResponse)
async def save_export_rule(request: ExportRuleRequest):
    """
    保存导出规则
    """
    try:
        # 获取门店列表以将ID转换为门店名称
        db_manager = get_db_manager()
        raw_stores = db_manager.get_stores()
        
        # 将门店ID转换为门店名称
        selected_store_names = []
        for store_id in request.selected_stores:
            if 1 <= store_id <= len(raw_stores):
                selected_store_names.append(raw_stores[store_id - 1]['name'])
        
        config_db_manager.save_export_rule(selected_store_names)
        return ConfigResponse(
            success=True,
            message="导出规则保存成功"
        )
    except Exception as e:
        logger.error(f"保存导出规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存导出规则失败: {str(e)}")


@router.get("/export-fields", response_model=ConfigResponse)
async def get_export_fields():
    """
    获取导出字段配置
    """
    try:
        logger.info("=== 开始获取导出字段配置 ===")
        logger.info("当前文件: backend/api/export.py")
        
        # 获取原始字段数据
        raw_fields = config_db_manager.get_export_fields()
        logger.info(f"原始字段数据: {raw_fields}")
        
        # 转换为前端期望的格式：Record<string, {name: string, comment: string}>
        field_config = {}
        for field in raw_fields:
            field_key = field['name']  # 使用name作为key
            field_config[field_key] = {
                'name': field['label'],  # 使用label作为显示名称
                'comment': field.get('type', '')  # 使用type作为注释
            }
        
        logger.info(f"转换后的字段数据: {field_config}")
        logger.info("=== 导出字段配置获取完成 ===")
        
        return ConfigResponse(
            success=True,
            data=field_config
        )
    except Exception as e:
        logger.error(f"获取导出字段配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取导出字段配置失败: {str(e)}")


@router.get("/export-field-rule", response_model=ConfigResponse)
async def get_export_field_rule():
    """
    获取导出字段规则
    """
    try:
        rule = config_db_manager.get_export_field_rule()
        return ConfigResponse(
            success=True,
            data=rule
        )
    except Exception as e:
        logger.error(f"获取导出字段规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取导出字段规则失败: {str(e)}")


@router.post("/export-field-rule", response_model=ConfigResponse)
async def save_export_field_rule(request: ExportFieldRuleRequest):
    """
    保存导出字段规则
    """
    try:
        config_db_manager.save_export_field_rule(request.selected_fields)
        return ConfigResponse(
            success=True,
            message="导出字段规则保存成功"
        )
    except Exception as e:
        logger.error(f"保存导出字段规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存导出字段规则失败: {str(e)}")
