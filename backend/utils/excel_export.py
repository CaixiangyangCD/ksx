#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel导出工具模块
"""

import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
import pandas as pd
import io
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger


def create_excel_file(data: List[Dict[str, Any]], filename: str) -> str:
    """
    创建Excel文件
    
    Args:
        data: 要导出的数据列表
        filename: 文件名
    
    Returns:
        str: 文件路径
    """
    try:
        # 创建工作簿
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "KSX数据"
        
        if not data:
            logger.warning("没有数据可导出")
            return ""
        
        # 获取列名
        columns = list(data[0].keys())
        
        # 设置表头样式
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        # 写入表头
        for col_idx, column in enumerate(columns, 1):
            cell = ws.cell(row=1, column=col_idx, value=column)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # 写入数据
        for row_idx, row_data in enumerate(data, 2):
            for col_idx, column in enumerate(columns, 1):
                value = row_data.get(column, "")
                # 处理特殊字符
                if isinstance(value, str):
                    value = re.sub(r'[^\x00-\x7F]+', '', value)  # 移除非ASCII字符
                ws.cell(row=row_idx, column=col_idx, value=value)
        
        # 设置列宽
        for col_idx, column in enumerate(columns, 1):
            max_length = len(str(column))
            for row_data in data:
                cell_value = str(row_data.get(column, ""))
                if len(cell_value) > max_length:
                    max_length = len(cell_value)
            ws.column_dimensions[get_column_letter(col_idx)].width = min(max_length + 2, 50)
        
        # 添加边框
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        for row in ws.iter_rows(min_row=1, max_row=len(data) + 1, min_col=1, max_col=len(columns)):
            for cell in row:
                cell.border = thin_border
        
        # 保存文件
        file_path = f"backend/exports/{filename}"
        wb.save(file_path)
        logger.info(f"Excel文件已保存: {file_path}")
        
        return file_path
        
    except Exception as e:
        logger.error(f"创建Excel文件失败: {e}")
        return ""


def create_csv_content(data: List[Dict[str, Any]]) -> str:
    """
    创建CSV内容
    
    Args:
        data: 要导出的数据列表
    
    Returns:
        str: CSV内容
    """
    try:
        if not data:
            return ""
        
        # 使用pandas创建CSV
        df = pd.DataFrame(data)
        
        # 处理列名，移除特殊字符
        df.columns = [re.sub(r'[^\x00-\x7F]+', '', str(col)) for col in df.columns]
        
        # 转换为CSV字符串
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()
        
        return csv_content
        
    except Exception as e:
        logger.error(f"创建CSV内容失败: {e}")
        return ""


def generate_filename(prefix: str = "ksx_export", extension: str = "xlsx") -> str:
    """
    生成文件名
    
    Args:
        prefix: 文件名前缀
        extension: 文件扩展名
    
    Returns:
        str: 生成的文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


