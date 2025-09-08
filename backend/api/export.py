#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导出API路由
"""

from fastapi import APIRouter, HTTPException
import sys
import os
from loguru import logger
from datetime import datetime
import re
import csv
import io
import hashlib

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

def get_app_data_dir():
    """获取应用数据目录，支持打包后的应用"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的情况
        # 从可执行文件路径找到dist目录
        executable_path = sys.executable
        if "KSX门店管理系统" in executable_path:
            # 找到dist目录
            parts = executable_path.split(os.sep)
            for i, part in enumerate(parts):
                if part == "dist":
                    dist_dir = os.sep.join(parts[:i+1])
                    return os.path.join(dist_dir, "data")
        # 如果找不到dist目录，使用默认路径
        return os.path.join(os.path.dirname(sys.executable), "data")
    else:
        # 开发环境
        return os.path.join(project_root, "backend", "exports")

from services.database_manager import get_db_manager
from services.config_database_manager import config_db_manager
from backend.models.schemas import (
    ExportDataRequest, ExportExcelRequest, ExportResponse,
    ExportRuleRequest, ExportFieldRuleRequest, ConfigResponse
)
from backend.utils.excel_export import create_incremental_excel

router = APIRouter(prefix="/api", tags=["export"])

# 字段配置和中文名称映射
FIELD_CONFIG = {
    "area": {"name": "区域", "comment": "门店所属区域"},
    "createDateShow": {"name": "创建日期", "comment": "数据创建日期"},
    "MDShow": {"name": "门店名称", "comment": "门店显示名称"},
    "totalScore": {"name": "总分", "comment": "门店综合评分"},
    "monthlyCanceledRate": {"name": "月度取消率", "comment": "月度订单取消率"},
    "dailyCanceledRate": {"name": "日取消率", "comment": "日订单取消率"},
    "monthlyMerchantRefundRate": {"name": "月度商家退款率", "comment": "月度商家责任退款率"},
    "monthlyOosRefundRate": {"name": "月度缺货退款率", "comment": "月度缺货退款率"},
    "monthlyJdOosRate": {"name": "月度京东缺货率", "comment": "月度京东缺货率"},
    "monthlyBadReviews": {"name": "月度差评数", "comment": "月度差评数量"},
    "monthlyBadReviewRate": {"name": "月度差评率", "comment": "月度差评率"},
    "monthlyPartialRefundRate": {"name": "月度部分退款率", "comment": "月度部分退款率"},
    "dailyMeituanRating": {"name": "美团评分", "comment": "美团平台日评分"},
    "dailyElemeRating": {"name": "饿了么评分", "comment": "饿了么平台日评分"},
    "dailyMeituanReplyRate": {"name": "美团回复率", "comment": "美团平台回复率"},
    "effectReply": {"name": "有效回复", "comment": "有效回复状态"},
    "monthlyMeituanPunctualityRate": {"name": "美团准时率", "comment": "美团月度准时送达率"},
    "monthlyElemeOntimeRate": {"name": "饿了么准时率", "comment": "饿了么月度准时送达率"},
    "monthlyJdFulfillmentRate": {"name": "京东履约率", "comment": "京东月度履约率"},
    "meituanComprehensiveExperienceDivision": {"name": "美团综合体验分", "comment": "美团综合体验评分"},
    "monthlyAvgStockRate": {"name": "月度平均库存率", "comment": "月度平均库存率"},
    "monthlyAvgTop500StockRate": {"name": "月度TOP500库存率", "comment": "月度TOP500商品库存率"},
    "monthlyAvgDirectStockRate": {"name": "月度直营库存率", "comment": "月度直营商品库存率"},
    "dailyTop500StockRate": {"name": "日TOP500库存率", "comment": "日TOP500商品库存率"},
    "dailyWarehouseSoldOut": {"name": "日仓库售罄数", "comment": "日仓库售罄商品数"},
    "dailyWarehouseStockRate": {"name": "日仓库库存率", "comment": "日仓库库存率"},
    "dailyDirectSoldOut": {"name": "日直营售罄数", "comment": "日直营售罄商品数"},
    "dailyDirectStockRate": {"name": "日直营库存率", "comment": "日直营库存率"},
    "dailyHybridSoldOut": {"name": "日混合售罄数", "comment": "日混合售罄商品数"},
    "dailyStockAvailability": {"name": "日库存可用率", "comment": "日库存可用率"},
    "dailyHybridStockRate": {"name": "日混合库存率", "comment": "日混合库存率"},
    "stockNoLocation": {"name": "无位置库存数", "comment": "无位置库存商品数"},
    "expiryManagement": {"name": "保质期管理", "comment": "保质期管理状态"},
    "inventoryLockOrders": {"name": "库存锁定订单", "comment": "库存锁定订单数"},
    "trainingCompleted": {"name": "培训完成", "comment": "培训完成状态"},
    "monthlyManhourPer100Orders": {"name": "月度百单工时", "comment": "月度每百单工时"},
    "monthlyTotalLoss": {"name": "月度总损失", "comment": "月度总损失金额"},
    "monthlyTotalLossRate": {"name": "月度总损失率", "comment": "月度总损失率"},
    "monthlyAvgDeliveryFee": {"name": "月度平均配送费", "comment": "月度平均配送费"},
    "dailyAvgDeliveryFee": {"name": "日平均配送费", "comment": "日平均配送费"},
    "monthlyCumulativeCancelRateScore": {"name": "月度累计取消率得分", "comment": "月度累计取消率得分"},
    "monthlyMerchantLiabilityRefundRateScore": {"name": "月度商家责任退款率得分", "comment": "月度商家责任退款率得分"},
    "monthlyStockoutRefundRateScore": {"name": "月度缺货退款率得分", "comment": "月度缺货退款率得分"},
    "monthlyNegativeReviewRateScore": {"name": "月度差评率得分", "comment": "月度差评率得分"},
    "monthlyPartialRefundRateScore": {"name": "月度部分退款率得分", "comment": "月度部分退款率得分"},
    "dailyMeituanRatingScore": {"name": "美团评分得分", "comment": "美团评分得分"},
    "dailyElemeRatingScore": {"name": "饿了么评分得分", "comment": "饿了么评分得分"},
    "monthlyMeituanDeliveryPunctualityRateScore": {"name": "美团配送准时率得分", "comment": "美团配送准时率得分"},
    "monthlyElemeTimelyDeliveryRateScore": {"name": "饿了么及时配送率得分", "comment": "饿了么及时配送率得分"},
    "validReplyWeightingPenalty": {"name": "有效回复权重惩罚", "comment": "有效回复权重惩罚"},
    "monthlyAverageStockRateWeightingPenalty": {"name": "月度平均库存率权重惩罚", "comment": "月度平均库存率权重惩罚"},
    "monthlyAverageTop500StockRateWeightingPenalty": {"name": "月度TOP500库存率权重惩罚", "comment": "月度TOP500库存率权重惩罚"},
    "monthlyAverageDirectStockRateWeightingPenalty": {"name": "月度直营库存率权重惩罚", "comment": "月度直营库存率权重惩罚"},
    "newProductComplianceListingWeightingPenalty": {"name": "新品合规上架权重惩罚", "comment": "新品合规上架权重惩罚"},
    "expiryManagementWeightingPenalty": {"name": "保质期管理权重惩罚", "comment": "保质期管理权重惩罚"},
    "inventoryLockWeightingPenalty": {"name": "库存锁定权重惩罚", "comment": "库存锁定权重惩罚"},
    "monthlyCumulativeHundredOrdersManhourWeightingPenalty": {"name": "月度累计百单工时权重惩罚", "comment": "月度累计百单工时权重惩罚"},
    "totalScoreWithoutWeightingPenalty": {"name": "无权重惩罚总分", "comment": "无权重惩罚总分"},
    "monthlyCumulativeMerchantLiabilityRefundRateWeightingPenalty": {"name": "月度累计商家责任退款率权重惩罚", "comment": "月度累计商家责任退款率权重惩罚"},
    "monthlyCumulativeOutOfStockRefundRateWeightingPenalty": {"name": "月度累计缺货退款率权重惩罚", "comment": "月度累计缺货退款率权重惩罚"},
    "meituanComplexExperienceScoreWeightingPenalty": {"name": "美团综合体验分权重惩罚", "comment": "美团综合体验分权重惩罚"},
    "meituanRatingWeightingPenalty": {"name": "美团评分权重惩罚", "comment": "美团评分权重惩罚"},
    "elemeRatingWeightingPenalty": {"name": "饿了么评分权重惩罚", "comment": "饿了么评分权重惩罚"},
    "partialRefundWeightingPenalty": {"name": "部分退款权重惩罚", "comment": "部分退款权重惩罚"},
    "trainingCompletedWeightingPenalty": {"name": "培训完成权重惩罚", "comment": "培训完成权重惩罚"},
    "totalWeightingPenalty": {"name": "总权重惩罚", "comment": "总权重惩罚"}
}


@router.post("/export-data")
async def export_data(export_config: dict = {}):
    """导出数据到CSV文件"""
    try:
        # 获取导出规则
        rule = config_db_manager.get_export_rule()
        if rule:
            selected_stores = rule.get('selected_stores', [])
            rule_name = rule.get('rule_name', '默认导出规则')
        else:
            selected_stores = []
            rule_name = '全部数据'
        
        # 获取数据库管理器
        db_manager = get_db_manager()
        
        # 查询数据
        if selected_stores:
            # 根据选中的门店查询数据
            # selected_stores 已经是门店名称列表，不需要转换
            store_names = selected_stores
            
            logger.info(f"选中的门店名称: {store_names}")
            
            if not store_names:
                return {
                    "success": False,
                    "message": "未找到有效的门店名称"
                }
            
            # 使用现有的query_data方法，但需要修改为支持多个门店
            # 暂时导出所有数据，然后在前端过滤
            from datetime import datetime
            result = db_manager.query_data(date=datetime.now(), page=1, page_size=10000)  # 获取今天的数据
            all_data = result.get('data', [])
            
            # 过滤选中的门店
            data = []
            for item in all_data:
                mdshow = item.get('MDShow', '')
                # 清理HTML标签
                clean_mdshow = re.sub(r'<[^>]+>', '', mdshow)
                if clean_mdshow in store_names:
                    data.append(item)
        else:
            # 导出所有数据
            from datetime import datetime
            result = db_manager.query_data(date=datetime.now(), page=1, page_size=10000)  # 获取今天的数据
            data = result.get('data', [])
        
        if not data:
            return {
                "success": False,
                "message": "没有找到数据"
            }
        
        # 生成CSV内容
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ksx_export_{rule_name}_{timestamp}.csv"
        except Exception as e:
            logger.error(f"生成文件名失败: {e}, rule_name: {rule_name}, type: {type(rule_name)}")
            raise
        
        # 确保导出目录存在
        export_dir = get_app_data_dir()
        os.makedirs(export_dir, exist_ok=True)
        
        # 生成CSV内容到内存
        csv_buffer = io.StringIO()
        if data:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()
        
        # 同时保存到文件
        file_path = os.path.join(export_dir, filename)
        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
            f.write(csv_content)
        
        logger.info(f"数据导出成功: {filename}, 共 {len(data)} 条记录, 保存到: {file_path}")
        
        return {
            "success": True,
            "message": f"数据导出成功，共 {len(data)} 条记录",
            "filename": filename,
            "file_path": file_path,
            "csv_content": csv_content,
            "count": len(data)
        }
        
    except Exception as e:
        logger.error(f"导出数据失败: {e}")
        return {
            "success": False,
            "message": f"导出数据失败: {str(e)}"
        }


@router.post("/export-excel")
async def export_excel(export_config: dict = {}):
    """导出数据到Excel文件"""
    try:
        # 获取导出规则
        rule = config_db_manager.get_export_rule()
        if rule:
            selected_stores = rule.get('selected_stores', [])
            rule_name = rule.get('rule_name', '默认导出规则')
        else:
            selected_stores = []
            rule_name = '全部数据'
        
        # 获取要导出的字段
        field_rule = config_db_manager.get_export_field_rule()
        if field_rule:
            selected_fields = field_rule.get('selected_fields', list(FIELD_CONFIG.keys()))
        else:
            selected_fields = export_config.get('selected_fields', list(FIELD_CONFIG.keys()))
        
        logger.info(f"选中的字段: {selected_fields}")
        
        # 获取日期参数
        export_date = export_config.get('date')
        
        # 获取数据库管理器
        db_manager = get_db_manager()
        
        # 查询数据
        data = []
        
        # 如果没有指定日期，默认查询今天
        if not export_date:
            export_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Excel导出查询日期: {export_date}")
        
        # 查询指定日期的数据
        query_date = datetime.strptime(export_date, '%Y-%m-%d')
        result = db_manager.query_data(date=query_date, page=1, page_size=10000)
        day_data = result.get('data', [])
        
        if selected_stores:
            # 根据选中的门店过滤数据
            # selected_stores 已经是门店名称列表，不需要转换
            store_names = selected_stores
            
            logger.info(f"Excel导出选中的门店名称: {store_names}")
            
            if not store_names:
                return {
                    "success": False,
                    "message": "未找到有效的门店名称"
                }
            
            # 过滤选中的门店
            for item in day_data:
                mdshow = item.get('MDShow', '')
                clean_mdshow = re.sub(r'<[^>]+>', '', mdshow)
                if clean_mdshow in store_names:
                    data.append(item)
        else:
            # 导出所有数据
            data = day_data
        
        if not data:
            return {
                "success": False,
                "message": "没有找到数据"
            }
        
        # 按月份分组数据
        monthly_data = {}
        for item in data:
            create_date = item.get('createDateShow', '')
            if create_date:
                # 提取年月
                try:
                    date_obj = datetime.strptime(create_date, '%Y-%m-%d')
                    month_key = date_obj.strftime('%Y-%m')
                    if month_key not in monthly_data:
                        monthly_data[month_key] = []
                    monthly_data[month_key].append(item)
                except:
                    continue
        
        # 生成文件名（基于字段配置的哈希值，确保相同配置使用相同文件名）
        fields_hash = hashlib.md5(''.join(sorted(selected_fields)).encode()).hexdigest()[:8]
        # 获取当前日期，格式化为YY_MM
        current_date = datetime.now().strftime("%y_%m")
        filename = f"ksx_{current_date}_{fields_hash}.xlsx"
        
        # 确保导出目录存在
        export_dir = get_app_data_dir()
        os.makedirs(export_dir, exist_ok=True)
        
        # 生成Excel内容（支持增量更新）
        excel_content = create_incremental_excel(monthly_data, selected_fields, rule_name, filename)
        
        # 保存Excel文件到磁盘
        file_path = os.path.join(export_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(excel_content)
        
        logger.info(f"Excel数据导出成功: {filename}, 共 {len(data)} 条记录, 保存到: {file_path}")
        
        return {
            "success": True,
            "message": f"Excel数据导出成功，共 {len(data)} 条记录",
            "filename": filename,
            "file_path": file_path,
            "excel_content": excel_content.hex(),  # 转换为十六进制字符串
            "count": len(data)
        }
        
    except Exception as e:
        logger.error(f"导出Excel数据失败: {e}")
        return {
            "success": False,
            "message": f"导出Excel数据失败: {str(e)}"
        }


@router.get("/export-rule")
async def get_export_rule():
    """获取导出规则"""
    try:
        rule = config_db_manager.get_export_rule()
        
        if rule and rule.get('selected_stores'):
            # 将门店名称转换为门店ID
            all_stores = config_db_manager.get_all_stores()
            store_name_to_id = {store['store_name']: store['id'] for store in all_stores}
            
            selected_store_ids = []
            for store_name in rule['selected_stores']:
                if store_name in store_name_to_id:
                    selected_store_ids.append(store_name_to_id[store_name])
            
            # 更新规则中的selected_stores为ID数组
            rule['selected_stores'] = selected_store_ids
        
        return {
            "success": True,
            "data": rule
        }
    except Exception as e:
        logger.error(f"获取导出规则失败: {e}")
        return {
            "success": False,
            "message": f"获取导出规则失败: {str(e)}"
        }

@router.post("/export-rule")
async def save_export_rule(rule_data: dict):
    """保存导出规则"""
    try:
        selected_store_ids = rule_data.get("selected_stores", [])
        
        # 将门店ID转换为门店名称
        all_stores = config_db_manager.get_all_stores()
        store_id_to_name = {store['id']: store['store_name'] for store in all_stores}
        
        selected_store_names = []
        for store_id in selected_store_ids:
            if store_id in store_id_to_name:
                selected_store_names.append(store_id_to_name[store_id])
        
        logger.info(f"保存导出规则，选中的门店: {selected_store_names}")
        
        success = config_db_manager.save_export_rule(selected_store_names)
        
        if success:
            return {
                "success": True,
                "message": "导出规则保存成功"
            }
        else:
            return {
                "success": False,
                "message": "导出规则保存失败"
            }
    except Exception as e:
        logger.error(f"保存导出规则失败: {e}")
        return {
            "success": False,
            "message": f"保存导出规则失败: {str(e)}"
        }

@router.get("/export-fields")
async def get_export_fields():
    """获取可导出的字段配置"""
    try:
        # 使用FIELD_CONFIG常量，确保与Excel导出功能一致
        # FIELD_CONFIG已经是Record格式，直接返回
        return {
            "success": True,
            "data": FIELD_CONFIG
        }
    except Exception as e:
        logger.error(f"获取导出字段失败: {e}")
        return {
            "success": False,
            "message": f"获取导出字段失败: {str(e)}"
        }

@router.get("/export-field-rule")
async def get_export_field_rule():
    """获取字段导出规则"""
    try:
        rule = config_db_manager.get_export_field_rule()
        return {
            "success": True,
            "data": rule
        }
    except Exception as e:
        logger.error(f"获取字段导出规则失败: {e}")
        return {
            "success": False,
            "message": f"获取字段导出规则失败: {str(e)}"
        }

@router.post("/export-field-rule")
async def save_export_field_rule(field_rule: dict = {}):
    """保存字段导出规则"""
    try:
        selected_fields = field_rule.get('selected_fields', [])
        config_db_manager.save_export_field_rule(selected_fields)
        return {
            "success": True,
            "message": "字段导出规则保存成功"
        }
    except Exception as e:
        logger.error(f"保存字段导出规则失败: {e}")
        return {
            "success": False,
            "message": f"保存字段导出规则失败: {str(e)}"
        }
