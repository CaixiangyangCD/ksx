"""
Excel文件内容读取器
专门处理门店激励数据的Excel文件格式
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger
import re

from backend.constants.field_config import EXCEL_METRICS_MAPPING, get_excel_metric_key
from services.config_database_manager import config_db_manager
from datetime import datetime


class StoreMetricsReader:
    """门店指标数据读取器"""
    
    def __init__(self, file_path: str, reading_mode: str = "full", target_month: str = None):
        """
        初始化门店指标读取器
        
        Args:
            file_path: Excel文件路径
            reading_mode: 读取模式 ("full" 全量, "incremental" 增量)
            target_month: 目标月份 (格式：2025-09)，用于增量读取时确定数据库月份
        """
        self.file_path = Path(file_path)
        self.workbook = None
        self.store_data = {}
        self.reading_mode = reading_mode
        self.target_month = target_month
        
        # 从配置表获取需要提取的指标
        self._load_metrics_config()
    
    def _load_metrics_config(self):
        """从配置表加载指标配置"""
        try:
            # 获取字段导出规则
            field_rule = config_db_manager.get_export_field_rule()
            if field_rule and field_rule.get('selected_fields'):
                # 使用配置的字段，转换为Excel中的指标名称
                selected_fields = field_rule['selected_fields']
                self.metrics_names = []
                
                # 将字段键名转换为Excel中的指标名称
                for field_key in selected_fields:
                    # 查找对应的Excel指标名称
                    for excel_name, field_name in EXCEL_METRICS_MAPPING.items():
                        if field_name == field_key:
                            self.metrics_names.append(excel_name)
                            break
                
                logger.info(f"从配置表加载了 {len(self.metrics_names)} 个指标")
            else:
                # 如果没有配置，使用默认的指标列表
                self.metrics_names = list(EXCEL_METRICS_MAPPING.keys())
                logger.info(f"使用默认指标列表，共 {len(self.metrics_names)} 个指标")
                
        except Exception as e:
            logger.warning(f"加载指标配置失败，使用默认配置: {e}")
            self.metrics_names = list(EXCEL_METRICS_MAPPING.keys())
    
    def _filter_dates_by_mode(self, dates: List[str], store_name: str) -> List[str]:
        """
        根据读取模式过滤日期
        
        Args:
            dates: 所有可用日期列表
            store_name: 门店名称
            
        Returns:
            List[str]: 过滤后的日期列表
        """
        if self.reading_mode == "full":
            logger.info(f"全量读取模式：读取所有 {len(dates)} 个日期")
            return dates
        
        elif self.reading_mode == "incremental":
            if not self.target_month:
                logger.warning("增量读取模式但未指定目标月份，使用全量读取")
                return dates
            
            # 获取该门店在目标月份数据库中的最新日期
            latest_date = config_db_manager.get_store_latest_date(store_name, self.target_month)
            
            if not latest_date:
                logger.info(f"门店 {store_name} 在 {self.target_month} 月无历史数据，使用全量读取")
                return dates
            
            # 过滤出最新日期之后的数据
            filtered_dates = []
            for date in dates:
                if date > latest_date:
                    filtered_dates.append(date)
            
            logger.info(f"增量读取模式：门店 {store_name} 最新日期 {latest_date}，读取 {len(filtered_dates)} 个新日期")
            return filtered_dates
        
        else:
            logger.warning(f"未知的读取模式: {self.reading_mode}，使用全量读取")
            return dates
    
    def _update_store_tracking(self, store_data: Dict[str, Any]):
        """
        更新门店数据跟踪信息
        
        Args:
            store_data: 门店数据字典
        """
        if not self.target_month:
            logger.warning("未指定目标月份，跳过跟踪更新")
            return
        
        try:
            for store_name, metrics_data in store_data.items():
                # 获取该门店的所有日期
                all_dates = set()
                for metric_name, metric_info in metrics_data.items():
                    if 'daily_data' in metric_info:
                        all_dates.update(metric_info['daily_data'].keys())
                
                if all_dates:
                    # 找到最新日期
                    latest_date = max(all_dates)
                    total_records = len(all_dates)
                    
                    # 更新跟踪信息
                    config_db_manager.update_store_data_tracking(
                        store_name, self.target_month, latest_date, total_records
                    )
                    
                    logger.info(f"更新门店跟踪: {store_name} - {self.target_month} - {latest_date} ({total_records}条记录)")
                
        except Exception as e:
            logger.error(f"更新门店跟踪信息失败: {e}")
        
    def read_excel(self) -> Dict[str, Any]:
        """
        读取Excel文件内容
        
        Returns:
            Dict: {
                "success": bool,
                "message": str,
                "stores": List[Dict],  # 门店列表
                "data": Dict  # 门店数据
            }
        """
        try:
            logger.info(f"开始读取Excel文件: {self.file_path}")
            
            if not self.file_path.exists():
                return {
                    "success": False,
                    "message": f"文件不存在: {self.file_path}"
                }
            
            # 读取Excel文件的所有工作表
            self.workbook = pd.read_excel(self.file_path, sheet_name=None, engine='openpyxl')
            
            if not self.workbook:
                return {
                    "success": False,
                    "message": "Excel文件中没有找到工作表"
                }
            
            logger.info(f"发现 {len(self.workbook)} 个工作表")
            
            # 处理每个工作表（每个工作表对应一个门店）
            stores = []
            store_data = {}
            
            for sheet_name, df in self.workbook.items():
                logger.info(f"处理工作表: {sheet_name}")
                
                # 过滤工作表：只处理包含"店"字的工作表
                if "店" not in sheet_name:
                    logger.info(f"跳过工作表 {sheet_name}（不包含'店'字）")
                    continue
                
                # 提取门店信息
                store_info = self._extract_store_info(sheet_name, df)
                if store_info:
                    stores.append(store_info)
                    store_data[store_info['name']] = self._extract_metrics_data(df, store_info['name'])
            
            # 更新门店数据跟踪信息
            self._update_store_tracking(store_data)
            
            return {
                "success": True,
                "message": f"成功读取 {len(stores)} 个门店的数据",
                "stores": stores,
                "data": store_data,
                "reading_mode": self.reading_mode
            }
            
        except Exception as e:
            logger.error(f"读取Excel文件失败: {e}")
            return {
                "success": False,
                "message": f"读取Excel文件失败: {str(e)}"
            }
    
    def _extract_store_info(self, sheet_name: str, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """提取门店信息"""
        try:
            # 提取日期信息
            dates = self._extract_dates(df)
            
            # 从工作表名称或数据中提取门店信息
            store_info = {
                "name": sheet_name,
                "sheet_name": sheet_name,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "total_days": len(dates),
                "dates": dates
            }
            
            return store_info
            
        except Exception as e:
            logger.warning(f"提取门店信息失败: {sheet_name}, 错误: {e}")
            return None
    
    def _extract_metrics_data(self, df: pd.DataFrame, store_name: str = None) -> Dict[str, Any]:
        """提取指标数据（包含所有日期的数据）"""
        try:
            # 首先提取日期信息
            dates = self._extract_dates(df)
            logger.info(f"提取到日期: {dates}")
            
            metrics_data = {}
            
            # 根据读取模式过滤日期
            filtered_dates = self._filter_dates_by_mode(dates, store_name)
            
            # 查找指标数据
            for metric_name in self.metrics_names:
                metric_data = self._find_metric_data_with_dates(df, metric_name, filtered_dates)
                if metric_data:
                    metrics_data[metric_name] = metric_data
            
            return metrics_data
            
        except Exception as e:
            logger.error(f"提取指标数据失败: {e}")
            return {}
    
    def _extract_dates(self, df: pd.DataFrame) -> List[str]:
        """提取日期信息（基于Excel结构分析）"""
        try:
            dates = []
            
            # 根据分析，数据结构是每6列代表一天
            # 从第4列开始，每6列为一组
            start_col = 4  # 第4列开始
            group_size = 6  # 每6列为一组
            
            # 计算有多少天
            total_cols = len(df.columns)
            max_days = (total_cols - start_col) // group_size
            
            # 生成日期列表
            for day in range(1, max_days + 1):
                dates.append(f"{day}日")
            
            logger.info(f"基于Excel结构提取到 {len(dates)} 个日期: {dates}")
            return dates
            
        except Exception as e:
            logger.error(f"提取日期失败: {e}")
            return []
    
    def _find_metric_data_with_dates(self, df: pd.DataFrame, metric_name: str, dates: List[str]) -> Optional[Dict[str, Any]]:
        """查找特定指标的所有日期数据"""
        try:
            # 在DataFrame中查找包含指标名称的行
            for idx, row in df.iterrows():
                for col_idx, cell_value in enumerate(row):
                    if pd.isna(cell_value):
                        continue
                    
                    cell_str = str(cell_value).strip()
                    
                    # 检查是否包含指标名称
                    if metric_name in cell_str:
                        # 找到指标行，提取该行所有日期的数据
                        return self._extract_metric_row_with_dates(df, idx, dates, metric_name)
            
            logger.warning(f"未找到指标: {metric_name}")
            return None
            
        except Exception as e:
            logger.error(f"查找指标数据失败: {metric_name}, 错误: {e}")
            return None
    
    def _extract_metric_row_with_dates(self, df: pd.DataFrame, row_idx: int, dates: List[str], metric_name: str) -> Dict[str, Any]:
        """提取指标行的所有日期数据"""
        try:
            row_data = df.iloc[row_idx]
            daily_data = {}
            
            # 根据Excel结构，每6列代表一天的数据
            # 第4列开始，每6列为一组：是否超过黄线、数据、整改计划 + 3个空列
            start_col = 4  # 第4列开始
            group_size = 6  # 每6列为一组
            
            # 提取每个日期的数据
            for i, date in enumerate(dates):
                # 计算该日期对应的列索引
                base_col = start_col + i * group_size
                
                # 数据列是每组的第1列（base_col）
                data_col = base_col
                
                if data_col < len(row_data):
                    data_value = row_data.iloc[data_col]
                    if not pd.isna(data_value):
                        daily_data[date] = self._parse_data_value(data_value)
                    else:
                        daily_data[date] = None
                else:
                    daily_data[date] = None
            
            logger.info(f"指标 {metric_name} 提取到 {len(daily_data)} 天的数据")
            
            return {
                "metric_name": metric_name,
                "daily_data": daily_data,
                "total_days": len([v for v in daily_data.values() if v is not None]),
                "row_index": row_idx
            }
            
        except Exception as e:
            logger.error(f"提取指标行数据失败: {metric_name}, 错误: {e}")
            return {}
    
    def _find_metric_data(self, df: pd.DataFrame, metric_name: str) -> Optional[Dict[str, Any]]:
        """查找特定指标的数据"""
        try:
            # 在DataFrame中查找包含指标名称的行
            for idx, row in df.iterrows():
                for col_idx, cell_value in enumerate(row):
                    if pd.isna(cell_value):
                        continue
                    
                    cell_str = str(cell_value).strip()
                    
                    # 检查是否包含指标名称
                    if metric_name in cell_str:
                        # 找到指标行，提取相关数据
                        return self._extract_metric_row_data(df, idx, col_idx, metric_name)
            
            logger.warning(f"未找到指标: {metric_name}")
            return None
            
        except Exception as e:
            logger.error(f"查找指标数据失败: {metric_name}, 错误: {e}")
            return None
    
    def _extract_metric_row_data(self, df: pd.DataFrame, row_idx: int, col_idx: int, metric_name: str) -> Dict[str, Any]:
        """提取指标行的数据"""
        try:
            row_data = df.iloc[row_idx]
            
            # 提取"是否超过黄线"列的数据
            yellow_line_exceeded = None
            if col_idx + 1 < len(row_data):
                yellow_line_value = row_data.iloc[col_idx + 1]
                if not pd.isna(yellow_line_value):
                    yellow_line_exceeded = str(yellow_line_value).strip() == "是"
            
            # 提取"数据"列的数据
            data_value = None
            if col_idx + 2 < len(row_data):
                data_value = row_data.iloc[col_idx + 2]
                if not pd.isna(data_value):
                    data_value = self._parse_data_value(data_value)
            
            # 提取"整改计划"列的数据
            rectification_plan = None
            if col_idx + 3 < len(row_data):
                rectification_plan = row_data.iloc[col_idx + 3]
                if pd.isna(rectification_plan):
                    rectification_plan = ""
                else:
                    rectification_plan = str(rectification_plan).strip()
            
            return {
                "metric_name": metric_name,
                "yellow_line_exceeded": yellow_line_exceeded,
                "data_value": data_value,
                "rectification_plan": rectification_plan,
                "row_index": row_idx,
                "column_index": col_idx
            }
            
        except Exception as e:
            logger.error(f"提取指标行数据失败: {metric_name}, 错误: {e}")
            return {}
    
    def _parse_data_value(self, value) -> Any:
        """解析数据值"""
        try:
            if pd.isna(value):
                return None
            
            value_str = str(value).strip()
            
            # 尝试解析为数字
            if re.match(r'^\d+\.?\d*%?$', value_str):
                if value_str.endswith('%'):
                    return float(value_str[:-1]) / 100
                else:
                    return float(value_str)
            
            # 尝试解析为整数
            if re.match(r'^\d+$', value_str):
                return int(value_str)
            
            # 返回原始字符串
            return value_str
            
        except Exception as e:
            logger.warning(f"解析数据值失败: {value}, 错误: {e}")
            return str(value)
    
    def get_daily_data(self, store_name: str, metric_name: str) -> Optional[Dict[str, Any]]:
        """获取特定门店和指标的每日数据"""
        try:
            if store_name not in self.store_data:
                logger.warning(f"门店不存在: {store_name}")
                return None
            
            store_metrics = self.store_data[store_name]
            if metric_name not in store_metrics:
                logger.warning(f"指标不存在: {metric_name}")
                return None
            
            # 这里需要根据实际的Excel格式来提取每日数据
            # 目前返回基础指标数据
            return store_metrics[metric_name]
            
        except Exception as e:
            logger.error(f"获取每日数据失败: {store_name}, {metric_name}, 错误: {e}")
            return None
    
    def get_all_stores_summary(self) -> Dict[str, Any]:
        """获取所有门店的指标汇总"""
        try:
            summary = {
                "total_stores": len(self.store_data),
                "stores": []
            }
            
            for store_name, store_metrics in self.store_data.items():
                store_summary = {
                    "name": store_name,
                    "metrics_count": len(store_metrics),
                    "metrics": {}
                }
                
                for metric_name, metric_data in store_metrics.items():
                    store_summary["metrics"][metric_name] = {
                        "value": metric_data.get("data_value"),
                        "yellow_line_exceeded": metric_data.get("yellow_line_exceeded"),
                        "has_rectification_plan": bool(metric_data.get("rectification_plan"))
                    }
                
                summary["stores"].append(store_summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"获取门店汇总失败: {e}")
            return {"total_stores": 0, "stores": []}
