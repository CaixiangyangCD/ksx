#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理器
负责SQLite数据库的创建、管理和清理
"""

import sqlite3
import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, base_dir: str = None):
        """
        初始化数据库管理器
        
        Args:
            base_dir: 数据库根目录，默认为项目根目录下的database
        """
        if base_dir is None:
            # 查找项目根目录
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent  # services/database_manager.py -> project_root
            base_dir = project_root / "database"
            
            # 确保使用绝对路径
            base_dir = base_dir.resolve()
        
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # 固定的数据表结构定义
        self.schema = self._get_schema()
        
    def _get_schema(self) -> List[Dict[str, Any]]:
        """获取数据表结构定义 - 根据data.json完整设计"""
        return [
            # 基础字段
            {"name": "rawId", "label": "原始数据ID", "type": "TEXT"},
            {"name": "area", "label": "区域", "type": "TEXT"},
            {"name": "createDateShow", "label": "日期", "type": "TEXT"},
            {"name": "MDShow", "label": "门店名称", "type": "TEXT"},
            {"name": "totalScore", "label": "最终得分", "type": "REAL"},
            
            # 取消和退单相关
            {"name": "monthlyCanceledRate", "label": "月累计取消率", "type": "TEXT"},
            {"name": "dailyCanceledRate", "label": "当日取消率", "type": "TEXT"},
            {"name": "monthlyMerchantRefundRate", "label": "月累计商责退单率", "type": "TEXT"},
            {"name": "monthlyOosRefundRate", "label": "月累计缺货退款率", "type": "TEXT"},
            {"name": "monthlyJdOosRate", "label": "月累计京东秒送缺货出率", "type": "TEXT"},
            {"name": "monthlyBadReviews", "label": "月累计差评总数", "type": "TEXT"},
            {"name": "monthlyBadReviewRate", "label": "月累计差评率", "type": "TEXT"},
            {"name": "monthlyPartialRefundRate", "label": "月累计部分退款率", "type": "TEXT"},
            
            # 评分相关
            {"name": "dailyMeituanRating", "label": "当日美团评分", "type": "TEXT"},
            {"name": "dailyElemeRating", "label": "当日饿了么评分", "type": "TEXT"},
            {"name": "dailyMeituanReplyRate", "label": "当日美团近7日首条消息1分钟人工回复率", "type": "TEXT"},
            {"name": "effectReply", "label": "有效回复", "type": "TEXT"},
            {"name": "monthlyMeituanPunctualityRate", "label": "月累计美团配送准时率", "type": "TEXT"},
            {"name": "monthlyElemeOntimeRate", "label": "月累计饿了么及时送达率", "type": "TEXT"},
            {"name": "monthlyJdFulfillmentRate", "label": "月累计京东秒送订单履约率", "type": "TEXT"},
            {"name": "meituanComprehensiveExperienceDivision", "label": "美团综合体体验分", "type": "TEXT"},
            
            # 库存相关
            {"name": "monthlyAvgStockRate", "label": "月平均有货率", "type": "TEXT"},
            {"name": "monthlyAvgTop500StockRate", "label": "月平均TOP500有货率", "type": "TEXT"},
            {"name": "monthlyAvgDirectStockRate", "label": "月平均直配直送有货率", "type": "TEXT"},
            {"name": "dailyTop500StockRate", "label": "当日TOP500有货率", "type": "TEXT"},
            {"name": "dailyWarehouseSoldOut", "label": "当日仓配售罄数", "type": "TEXT"},
            {"name": "dailyWarehouseStockRate", "label": "当日仓配有货率", "type": "TEXT"},
            {"name": "dailyDirectSoldOut", "label": "当日直送售罄数", "type": "TEXT"},
            {"name": "dailyDirectStockRate", "label": "当日直送有货率", "type": "TEXT"},
            {"name": "dailyHybridSoldOut", "label": "当日直配售罄数", "type": "TEXT"},
            {"name": "dailyStockAvailability", "label": "当日有货率", "type": "TEXT"},
            {"name": "dailyHybridStockRate", "label": "当日直配有货率", "type": "TEXT"},
            {"name": "stockNoLocation", "label": "有库存无库位数", "type": "TEXT"},
            {"name": "expiryManagement", "label": "效期管理", "type": "TEXT"},
            {"name": "inventoryLockOrders", "label": "库存锁定单数", "type": "TEXT"},
            {"name": "trainingCompleted", "label": "培训完结", "type": "TEXT"},
            
            # 工时和损耗相关
            {"name": "monthlyManhourPer100Orders", "label": "月累计百单编制工时", "type": "REAL"},
            {"name": "monthlyTotalLoss", "label": "月累计综合损溢额", "type": "REAL"},
            {"name": "monthlyTotalLossRate", "label": "月累计综合损溢率", "type": "TEXT"},
            {"name": "monthlyAvgDeliveryFee", "label": "本月累计单均配送费", "type": "REAL"},
            {"name": "dailyAvgDeliveryFee", "label": "当日单均配送费", "type": "REAL"},
            
            # 得分相关
            {"name": "monthlyCumulativeCancelRateScore", "label": "月累计取消率得分", "type": "TEXT"},
            {"name": "monthlyMerchantLiabilityRefundRateScore", "label": "月累计商责退单率得分", "type": "TEXT"},
            {"name": "monthlyStockoutRefundRateScore", "label": "月累计缺货退款率得分", "type": "TEXT"},
            {"name": "monthlyNegativeReviewRateScore", "label": "月累计差评率得分", "type": "TEXT"},
            {"name": "monthlyPartialRefundRateScore", "label": "月累计部分退款率得分", "type": "TEXT"},
            {"name": "dailyMeituanRatingScore", "label": "当日美团评分得分", "type": "TEXT"},
            {"name": "dailyElemeRatingScore", "label": "当日饿了么评分得分", "type": "TEXT"},
            {"name": "monthlyMeituanDeliveryPunctualityRateScore", "label": "月累计美团配送准时率得分", "type": "TEXT"},
            {"name": "monthlyElemeTimelyDeliveryRateScore", "label": "月累计饿了么及时送达率得分", "type": "TEXT"},
            
            # 降权相关
            {"name": "validReplyWeightingPenalty", "label": "有效回复降权", "type": "TEXT"},
            {"name": "monthlyAverageStockRateWeightingPenalty", "label": "月平均有货率降权", "type": "TEXT"},
            {"name": "monthlyAverageTop500StockRateWeightingPenalty", "label": "月平均TOP500有货率降权", "type": "TEXT"},
            {"name": "monthlyAverageDirectStockRateWeightingPenalty", "label": "月平均直配直送有货率降权", "type": "TEXT"},
            {"name": "newProductComplianceListingWeightingPenalty", "label": "新品合规上新降权", "type": "TEXT"},
            {"name": "expiryManagementWeightingPenalty", "label": "效期管理降权", "type": "TEXT"},
            {"name": "inventoryLockWeightingPenalty", "label": "库存锁定降权", "type": "TEXT"},
            {"name": "monthlyCumulativeHundredOrdersManhourWeightingPenalty", "label": "月累计百单编制工时降权", "type": "TEXT"},
            {"name": "totalScoreWithoutWeightingPenalty", "label": "总得分（不含降权）", "type": "TEXT"},
            {"name": "monthlyCumulativeMerchantLiabilityRefundRateWeightingPenalty", "label": "月累计商责退单率降权", "type": "TEXT"},
            {"name": "monthlyCumulativeOutOfStockRefundRateWeightingPenalty", "label": "月累计缺货退款率降权", "type": "TEXT"},
            {"name": "meituanComplexExperienceScoreWeightingPenalty", "label": "美团综合体体验分降权", "type": "TEXT"},
            {"name": "meituanRatingWeightingPenalty", "label": "美团评分降权", "type": "TEXT"},
            {"name": "elemeRatingWeightingPenalty", "label": "饿了么评分降权", "type": "TEXT"},
            {"name": "partialRefundWeightingPenalty", "label": "部分退款降权", "type": "TEXT"},
            {"name": "trainingCompletedWeightingPenalty", "label": "培训完结降权", "type": "TEXT"},
            {"name": "totalWeightingPenalty", "label": "总降权", "type": "TEXT"}
        ]
    
    def _generate_create_table_sql(self) -> str:
        """生成创建表的SQL语句"""
        sql_parts = [
            "CREATE TABLE IF NOT EXISTS ksx_data (",
            "    id INTEGER PRIMARY KEY AUTOINCREMENT,",  # 自增主键
            "    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,"
        ]
        
        # 添加其他字段
        for column in self.schema:
            column_name = column.get('name', '')
            column_type = column.get('type', 'TEXT')
            if column_name and column_name.lower() != 'id':
                sql_parts.append(f"    {column_name} {column_type},")
        
        # 移除最后一个逗号并添加结束括号
        if sql_parts[-1].endswith(','):
            sql_parts[-1] = sql_parts[-1][:-1]
        
        sql_parts.append(")")
        
        return "\n".join(sql_parts)
    
    def get_database_path(self, date: datetime = None) -> Path:
        """
        获取指定日期的数据库文件路径
        
        Args:
            date: 日期，默认为今天
            
        Returns:
            数据库文件路径
        """
        if date is None:
            date = datetime.now()
            
        year_month = date.strftime("%Y-%m")
        day = date.strftime("%d")
        
        # 创建年月目录
        month_dir = self.base_dir / year_month
        month_dir.mkdir(exist_ok=True)
        
        # 数据库文件名：ksx_YYYY-MM-DD.db
        db_filename = f"ksx_{date.strftime('%Y-%m-%d')}.db"
        return month_dir / db_filename
    
    def create_database(self, date: datetime = None) -> str:
        """
        创建数据库和表
        
        Args:
            date: 日期，默认为今天
            
        Returns:
            数据库文件路径
        """
        db_path = self.get_database_path(date)
        
        try:
            # 创建数据库连接
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # 创建表
            create_sql = self._generate_create_table_sql()
            cursor.execute(create_sql)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON ksx_data(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mdshow ON ksx_data(MDShow)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rawid ON ksx_data(rawId)")
            
            conn.commit()
            conn.close()
            
            logger.info(f"数据库创建成功: {db_path}")
            return str(db_path)
            
        except Exception as e:
            logger.error(f"创建数据库失败: {e}")
            raise
    
    def insert_data(self, data: List[Dict[str, Any]], date: datetime = None) -> int:
        """
        插入数据到数据库
        
        Args:
            data: 要插入的数据列表
            date: 日期，默认为今天
            
        Returns:
            成功插入的记录数
        """
        if not data:
            logger.warning("没有数据需要插入")
            return 0
            
        db_path = self.get_database_path(date)
        
        # 如果数据库不存在，先创建
        if not db_path.exists():
            self.create_database(date)
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            inserted_count = 0
            
            for item in data:
                # 确保有原始ID字段
                raw_id = item.get('ID') or item.get('id') or item.get('rawId')
                if not raw_id:
                    logger.warning("数据项缺少原始ID字段，跳过")
                    continue
                
                # 检查是否已存在（基于rawId去重）
                cursor.execute("SELECT COUNT(*) FROM ksx_data WHERE rawId = ?", (raw_id,))
                if cursor.fetchone()[0] > 0:
                    logger.debug(f"记录已存在，跳过: {raw_id}")
                    continue
                
                # 准备插入数据，确保rawId字段
                item_copy = item.copy()
                item_copy['rawId'] = raw_id
                
                # 准备插入的列和值
                columns = []
                values = []
                
                for col in self.schema:
                    col_name = col['name']
                    if col_name in item_copy:
                        columns.append(col_name)
                        values.append(item_copy[col_name])
                    else:
                        # 对于缺失的字段，插入空值
                        columns.append(col_name)
                        values.append(None)
                
                placeholders = ','.join(['?'] * len(columns))
                sql = f"INSERT INTO ksx_data ({','.join(columns)}) VALUES ({placeholders})"
                
                cursor.execute(sql, values)
                inserted_count += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"成功插入 {inserted_count} 条记录到 {db_path}")
            return inserted_count
            
        except Exception as e:
            logger.error(f"插入数据失败: {e}")
            raise
    
    def query_data(self, 
                   date: datetime = None, 
                   mdshow_filter: str = None,
                   page: int = 1, 
                   page_size: int = 20) -> Dict[str, Any]:
        """
        查询数据
        
        Args:
            date: 日期，默认为今天
            mdshow_filter: MDShow字段的模糊查询条件
            page: 页码，从1开始
            page_size: 每页记录数
            
        Returns:
            查询结果，包含数据和分页信息
        """
        db_path = self.get_database_path(date)
        
        if not db_path.exists():
            return {
                'data': [],
                'total': 0,
                'page': page,
                'page_size': page_size,
                'total_pages': 0
            }
        
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            cursor = conn.cursor()
            
            # 构建查询条件
            where_clause = ""
            params = []
            
            if mdshow_filter:
                where_clause = "WHERE MDShow LIKE ?"
                params.append(f"%{mdshow_filter}%")
            
            # 计算总记录数
            count_sql = f"SELECT COUNT(*) FROM ksx_data {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()[0]
            
            # 计算分页
            total_pages = (total + page_size - 1) // page_size
            offset = (page - 1) * page_size
            
            # 查询数据
            data_sql = f"""
                SELECT * FROM ksx_data 
                {where_clause}
                ORDER BY created_at ASC
                LIMIT ? OFFSET ?
            """
            cursor.execute(data_sql, params + [page_size, offset])
            
            rows = cursor.fetchall()
            data = [dict(row) for row in rows]
            
            conn.close()
            
            return {
                'data': data,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages
            }
            
        except Exception as e:
            logger.error(f"查询数据失败: {e}")
            raise
    
    def cleanup_old_databases(self, keep_months: int = 1):
        """
        清理旧的数据库文件
        
        Args:
            keep_months: 保留最近多少个月的数据
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=30 * keep_months)
            cutoff_month = cutoff_date.strftime("%Y-%m")
            
            deleted_dirs = []
            
            for month_dir in self.base_dir.iterdir():
                if month_dir.is_dir() and month_dir.name < cutoff_month:
                    shutil.rmtree(month_dir)
                    deleted_dirs.append(month_dir.name)
                    
            if deleted_dirs:
                logger.info(f"已删除旧数据库目录: {deleted_dirs}")
            else:
                logger.info("没有需要清理的旧数据库")
                
        except Exception as e:
            logger.error(f"清理旧数据库失败: {e}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        info = {
            'base_dir': str(self.base_dir),
            'months': [],
            'total_databases': 0,
            'total_size_mb': 0
        }
        
        try:
            total_size = 0
            total_dbs = 0
            
            for month_dir in sorted(self.base_dir.iterdir()):
                if not month_dir.is_dir():
                    continue
                    
                month_info = {
                    'month': month_dir.name,
                    'databases': [],
                    'size_mb': 0
                }
                
                month_size = 0
                for db_file in month_dir.glob("*.db"):
                    db_size = db_file.stat().st_size
                    month_size += db_size
                    total_size += db_size
                    total_dbs += 1
                    
                    month_info['databases'].append({
                        'name': db_file.name,
                        'size_mb': round(db_size / 1024 / 1024, 2),
                        'created': datetime.fromtimestamp(db_file.stat().st_ctime).isoformat()
                    })
                
                month_info['size_mb'] = round(month_size / 1024 / 1024, 2)
                info['months'].append(month_info)
            
            info['total_databases'] = total_dbs
            info['total_size_mb'] = round(total_size / 1024 / 1024, 2)
            
        except Exception as e:
            logger.error(f"获取数据库信息失败: {e}")
            
        return info


# 单例模式
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """获取数据库管理器单例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


if __name__ == "__main__":
    # 测试代码
    db_manager = DatabaseManager()
    
    # 创建数据库
    db_path = db_manager.create_database()
    print(f"数据库创建成功: {db_path}")
    
    # 测试插入数据
    test_data = [
        {
            'ID': 'test001',
            'MDShow': '测试门店1',
            'area': '1区',
            'totalScore': 85.5
        },
        {
            'ID': 'test002', 
            'MDShow': '测试门店2',
            'area': '2区',
            'totalScore': 90.0
        }
    ]
    
    inserted = db_manager.insert_data(test_data)
    print(f"插入记录数: {inserted}")
    
    # 测试查询数据
    result = db_manager.query_data(mdshow_filter="测试")
    print(f"查询结果: {result}")
    
    # 获取数据库信息
    info = db_manager.get_database_info()
    print(f"数据库信息: {info}")
