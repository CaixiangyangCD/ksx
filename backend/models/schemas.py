#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic数据模型定义
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date


# 请求模型
class SyncRequest(BaseModel):
    """同步请求模型"""
    date: Optional[str] = None  # 可选，如果不提供则使用默认日期


class SyncDataRequest(BaseModel):
    """同步数据请求模型"""
    date: str


class BatchSyncRequest(BaseModel):
    """批量同步请求模型"""
    start_date: str
    end_date: Optional[str] = None  # 如果不提供，默认等于start_date


class ExportDataRequest(BaseModel):
    """导出数据请求模型"""
    selected_stores: List[int]
    rule_name: str


class ExportExcelRequest(BaseModel):
    """导出Excel请求模型"""
    date: Optional[str] = None


class ExportRuleRequest(BaseModel):
    """导出规则请求模型"""
    selected_stores: List[int]  # 前端传递的是ID数组


class ExportFieldRuleRequest(BaseModel):
    """导出字段规则请求模型"""
    selected_fields: List[str]


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


class SyncResponse(BaseModel):
    """同步响应模型"""
    success: bool
    message: str
    total: Optional[int] = None
    error_code: Optional[str] = None


class DataResponse(BaseModel):
    """数据响应模型"""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    message: Optional[str] = None


class ExportResponse(BaseModel):
    """导出响应模型"""
    success: bool
    message: Optional[str] = None
    filename: Optional[str] = None
    csv_content: Optional[str] = None
    file_path: Optional[str] = None
    excel_content: Optional[str] = None  # Excel文件的十六进制内容
    count: Optional[int] = None


class StoresResponse(BaseModel):
    """门店响应模型"""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    message: Optional[str] = None


class ConfigResponse(BaseModel):
    """配置响应模型"""
    success: bool
    data: Optional[Union[Dict[str, Any], List[Any]]] = None
    message: Optional[str] = None


class DatabaseInfoResponse(BaseModel):
    """数据库信息响应模型"""
    success: bool
    data: Optional[Dict[str, Any]] = None


class DatesResponse(BaseModel):
    """日期列表响应模型"""
    success: bool
    dates: Optional[List[str]] = None
    total: Optional[int] = None
