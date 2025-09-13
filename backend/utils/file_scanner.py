"""
文件扫描工具模块
用于扫描import文件夹中的Excel文件
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger

from backend.constants.field_config import EXCEL_METRICS_MAPPING
from services.config_database_manager import config_db_manager


def _get_target_metrics() -> List[str]:
    """获取需要检查的指标列表"""
    try:
        # 获取字段导出规则
        field_rule = config_db_manager.get_export_field_rule()
        if field_rule and field_rule.get('selected_fields'):
            # 使用配置的字段，转换为Excel中的指标名称
            selected_fields = field_rule['selected_fields']
            target_metrics = []
            
            # 将字段键名转换为Excel中的指标名称
            for field_key in selected_fields:
                for excel_name, field_name in EXCEL_METRICS_MAPPING.items():
                    if field_name == field_key:
                        target_metrics.append(excel_name)
                        break
            
            logger.info(f"从配置表获取了 {len(target_metrics)} 个验证指标")
            return target_metrics
        else:
            # 如果没有配置，使用默认的指标列表
            target_metrics = list(EXCEL_METRICS_MAPPING.keys())
            logger.info(f"使用默认验证指标列表，共 {len(target_metrics)} 个指标")
            return target_metrics
            
    except Exception as e:
        logger.warning(f"获取验证指标配置失败，使用默认配置: {e}")
        return list(EXCEL_METRICS_MAPPING.keys())


def get_import_directory() -> Path:
    """获取import文件夹路径"""
    if getattr(sys, 'frozen', False):
        # 生产环境：exe文件所在目录
        exe_dir = Path(sys.executable).parent
        return exe_dir / "import"
    else:
        # 开发环境：项目根目录
        project_root = Path(__file__).parent.parent.parent
        return project_root / "import"


def scan_excel_files() -> Dict[str, any]:
    """
    扫描import文件夹中的Excel文件
    
    Returns:
        Dict: {
            "success": bool,
            "message": str,
            "files": List[Dict],  # 文件信息列表
            "count": int,         # 文件数量
            "selected_file": Optional[str]  # 自动选择的文件路径
        }
    """
    try:
        import_dir = get_import_directory()
        logger.info(f"扫描Excel文件，目录: {import_dir}")
        
        # 检查目录是否存在
        if not import_dir.exists():
            logger.warning(f"import目录不存在: {import_dir}")
            return {
                "success": False,
                "message": f"import文件夹不存在: {import_dir}",
                "files": [],
                "count": 0,
                "selected_file": None
            }
        
        # 扫描Excel文件
        excel_files = list(import_dir.glob("*.xlsx"))
        excel_files.extend(list(import_dir.glob("*.xls")))  # 支持旧版Excel格式
        
        if not excel_files:
            logger.warning(f"import目录中未找到Excel文件: {import_dir}")
            return {
                "success": False,
                "message": f"import文件夹中未找到Excel文件，请将Excel文件放入 {import_dir}",
                "files": [],
                "count": 0,
                "selected_file": None
            }
        
        # 构建文件信息列表
        file_list = []
        for file_path in excel_files:
            try:
                stat = file_path.stat()
                file_info = {
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "modified_time": stat.st_mtime,
                    "extension": file_path.suffix.lower()
                }
                file_list.append(file_info)
            except Exception as e:
                logger.warning(f"获取文件信息失败: {file_path}, 错误: {e}")
                continue
        
        # 按修改时间排序（最新的在前）
        file_list.sort(key=lambda x: x["modified_time"], reverse=True)
        
        # 自动选择策略
        selected_file = None
        if len(file_list) == 1:
            selected_file = file_list[0]["path"]
            logger.info(f"发现1个Excel文件，自动选择: {file_list[0]['name']}")
        elif len(file_list) > 1:
            selected_file = file_list[0]["path"]  # 选择最新的文件
            logger.info(f"发现{len(file_list)}个Excel文件，自动选择最新的: {file_list[0]['name']}")
        
        return {
            "success": True,
            "message": f"成功扫描到 {len(file_list)} 个Excel文件",
            "files": file_list,
            "count": len(file_list),
            "selected_file": selected_file
        }
        
    except Exception as e:
        logger.error(f"扫描Excel文件失败: {e}")
        return {
            "success": False,
            "message": f"扫描Excel文件失败: {str(e)}",
            "files": [],
            "count": 0,
            "selected_file": None
        }


def get_excel_file_info(file_path: str) -> Dict[str, any]:
    """
    获取指定Excel文件的详细信息
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        Dict: 文件信息
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {
                "success": False,
                "message": f"文件不存在: {file_path}"
            }
        
        stat = path.stat()
        return {
            "success": True,
            "name": path.name,
            "path": str(path),
            "size": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "modified_time": stat.st_mtime,
            "extension": path.suffix.lower()
        }
        
    except Exception as e:
        logger.error(f"获取文件信息失败: {file_path}, 错误: {e}")
        return {
            "success": False,
            "message": f"获取文件信息失败: {str(e)}"
        }


def validate_excel_file(file_path: str) -> Dict[str, any]:
    """
    验证Excel文件是否有效且符合门店激励数据格式
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        Dict: 验证结果
    """
    try:
        import pandas as pd
        
        path = Path(file_path)
        if not path.exists():
            return {
                "success": False,
                "message": f"文件不存在: {file_path}"
            }
        
        # 尝试读取Excel文件
        try:
            # 读取所有工作表
            workbook = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
            
            if not workbook:
                return {
                    "success": False,
                    "message": "Excel文件中没有找到工作表"
                }
            
            # 检查是否有包含"店"字的工作表
            store_sheets = [name for name in workbook.keys() if "店" in name]
            
            if not store_sheets:
                return {
                    "success": False,
                    "message": "Excel文件中没有找到包含'店'字的工作表，请确保文件格式正确"
                }
            
            # 检查第一个门店工作表的格式
            first_sheet = store_sheets[0]
            df = workbook[first_sheet]
            
            # 检查基本格式要求
            if df.empty:
                return {
                    "success": False,
                    "message": f"工作表 '{first_sheet}' 为空"
                }
            
            # 检查是否有足够的列（至少应该有日期列）
            if len(df.columns) < 10:
                return {
                    "success": False,
                    "message": f"工作表 '{first_sheet}' 列数不足，可能不是正确的门店激励数据格式"
                }
            
            # 获取需要检查的指标列表
            target_metrics = _get_target_metrics()
            
            found_metrics = 0
            for metric in target_metrics:
                # 在DataFrame中查找包含指标名称的单元格
                metric_found = False
                for idx, row in df.iterrows():
                    for col_idx, cell_value in enumerate(row):
                        if pd.isna(cell_value):
                            continue
                        cell_str = str(cell_value).strip()
                        if metric in cell_str:
                            found_metrics += 1
                            metric_found = True
                            break
                    if metric_found:
                        break
            
            # 更宽松的验证逻辑：允许部分匹配
            if found_metrics == 0:
                return {
                    "success": False,
                    "message": f"工作表 '{first_sheet}' 中没有找到预期的指标数据，请检查文件格式是否正确"
                }
            
            # 如果找到的指标数量较少，给出警告但不阻止处理
            if found_metrics < 3:
                logger.warning(f"工作表 '{first_sheet}' 中只找到 {found_metrics} 个指标，可能不是完整的门店激励数据")
                return {
                    "success": True,
                    "message": f"文件验证通过，但只找到 {found_metrics} 个指标，建议检查数据完整性",
                    "columns": list(df.columns),
                    "rows_preview": len(df)
                }
            
            return {
                "success": True,
                "message": f"Excel文件格式验证通过，发现 {len(store_sheets)} 个门店工作表，{found_metrics} 个指标",
                "store_sheets": store_sheets,
                "metrics_found": found_metrics,
                "columns": list(df.columns) if not df.empty else [],
                "rows_preview": len(df)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Excel文件格式无效: {str(e)}"
            }
            
    except ImportError:
        return {
            "success": False,
            "message": "缺少pandas库，无法验证Excel文件"
        }
    except Exception as e:
        logger.error(f"验证Excel文件失败: {file_path}, 错误: {e}")
        return {
            "success": False,
            "message": f"验证Excel文件失败: {str(e)}"
        }
