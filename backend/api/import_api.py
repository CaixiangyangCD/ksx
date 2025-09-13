"""
导入相关API接口
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from loguru import logger

from backend.utils.file_scanner import scan_excel_files, get_excel_file_info, validate_excel_file
from backend.utils.excel_reader import StoreMetricsReader
from backend.utils.data_comparator import DataComparator
from services.config_database_manager import config_db_manager

router = APIRouter()


class ExcelFileInfo(BaseModel):
    """Excel文件信息模型"""
    name: str
    path: str
    size: int
    size_mb: float
    modified_time: float
    extension: str


class ExcelFileListResponse(BaseModel):
    """Excel文件列表响应模型"""
    success: bool
    message: str
    files: List[ExcelFileInfo]
    count: int
    selected_file: str = None


class ExcelFileValidationResponse(BaseModel):
    """Excel文件验证响应模型"""
    success: bool
    message: str
    columns: List[str] = []
    rows_preview: int = 0


@router.get("/excel-files", response_model=ExcelFileListResponse)
async def get_excel_files():
    """
    获取import文件夹中的Excel文件列表
    """
    try:
        logger.info("收到获取Excel文件列表请求")
        
        result = scan_excel_files()
        
        if not result["success"]:
            logger.warning(f"扫描Excel文件失败: {result['message']}")
            return ExcelFileListResponse(
                success=False,
                message=result["message"],
                files=[],
                count=0,
                selected_file=None
            )
        
        # 转换文件信息为模型
        file_models = []
        for file_info in result["files"]:
            file_models.append(ExcelFileInfo(
                name=file_info["name"],
                path=file_info["path"],
                size=file_info["size"],
                size_mb=file_info["size_mb"],
                modified_time=file_info["modified_time"],
                extension=file_info["extension"]
            ))
        
        logger.info(f"成功返回 {len(file_models)} 个Excel文件")
        
        return ExcelFileListResponse(
            success=True,
            message=result["message"],
            files=file_models,
            count=result["count"],
            selected_file=result["selected_file"]
        )
        
    except Exception as e:
        logger.error(f"获取Excel文件列表异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取Excel文件列表失败: {str(e)}")


@router.get("/excel-file-info/{file_path:path}", response_model=Dict[str, Any])
async def get_excel_file_detail(file_path: str):
    """
    获取指定Excel文件的详细信息
    """
    try:
        logger.info(f"收到获取Excel文件信息请求: {file_path}")
        
        result = get_excel_file_info(file_path)
        
        if not result["success"]:
            logger.warning(f"获取文件信息失败: {result['message']}")
            raise HTTPException(status_code=404, detail=result["message"])
        
        logger.info(f"成功获取文件信息: {result['name']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Excel文件信息异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取Excel文件信息失败: {str(e)}")


@router.post("/validate-excel", response_model=ExcelFileValidationResponse)
async def validate_excel_file_endpoint(request: Dict[str, str]):
    """
    验证Excel文件格式
    """
    try:
        file_path = request.get("file_path")
        if not file_path:
            raise HTTPException(status_code=400, detail="缺少file_path参数")
        
        logger.info(f"收到验证Excel文件请求: {file_path}")
        
        result = validate_excel_file(file_path)
        
        if not result["success"]:
            logger.warning(f"Excel文件验证失败: {result['message']}")
            return ExcelFileValidationResponse(
                success=False,
                message=result["message"]
            )
        
        logger.info(f"Excel文件验证成功: {file_path}")
        return ExcelFileValidationResponse(
            success=True,
            message=result["message"],
            columns=result.get("columns", []),
            rows_preview=result.get("rows_preview", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"验证Excel文件异常: {e}")
        raise HTTPException(status_code=500, detail=f"验证Excel文件失败: {str(e)}")


@router.post("/select-excel-file")
async def select_excel_file(request: Dict[str, str]):
    """
    选择Excel文件（用于后续处理）
    """
    try:
        file_path = request.get("file_path")
        if not file_path:
            raise HTTPException(status_code=400, detail="缺少file_path参数")
        
        logger.info(f"收到选择Excel文件请求: {file_path}")
        
        # 验证文件是否存在
        result = get_excel_file_info(file_path)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        # 验证文件格式
        validation_result = validate_excel_file(file_path)
        if not validation_result["success"]:
            raise HTTPException(status_code=400, detail=validation_result["message"])
        
        logger.info(f"成功选择Excel文件: {result['name']}")
        
        return {
            "success": True,
            "message": f"已选择Excel文件: {result['name']}",
            "file_info": result,
            "validation": validation_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"选择Excel文件异常: {e}")
        raise HTTPException(status_code=500, detail=f"选择Excel文件失败: {str(e)}")


@router.post("/read-excel-content")
async def read_excel_content(request: Dict[str, Any]):
    """
    读取Excel文件内容并提取指标数据
    """
    try:
        file_path = request.get("file_path")
        reading_mode = request.get("reading_mode", "full")  # full 或 incremental
        target_month = request.get("target_month")  # 格式：2025-09
        
        if not file_path:
            raise HTTPException(status_code=400, detail="缺少file_path参数")
        
        # 验证读取模式
        if reading_mode not in ["full", "incremental"]:
            raise HTTPException(status_code=400, detail="reading_mode必须是'full'或'incremental'")
        
        # 增量模式需要指定目标月份
        if reading_mode == "incremental" and not target_month:
            raise HTTPException(status_code=400, detail="增量读取模式需要指定target_month参数")
        
        logger.info(f"收到读取Excel内容请求: {file_path}, 模式: {reading_mode}, 月份: {target_month}")
        
        # 创建Excel读取器
        reader = StoreMetricsReader(file_path, reading_mode, target_month)
        
        # 读取Excel内容
        result = reader.read_excel()
        
        if not result["success"]:
            logger.warning(f"读取Excel内容失败: {result['message']}")
            raise HTTPException(status_code=400, detail=result["message"])
        
        # 获取门店汇总信息
        summary = reader.get_all_stores_summary()
        
        logger.info(f"成功读取Excel内容: {result['message']}")
        
        return {
            "success": True,
            "message": result["message"],
            "stores": result["stores"],
            "data": result["data"],
            "summary": summary,
            "reading_mode": reading_mode,
            "target_month": target_month
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"读取Excel内容异常: {e}")
        raise HTTPException(status_code=500, detail=f"读取Excel内容失败: {str(e)}")


@router.get("/store-metrics/{store_name}")
async def get_store_metrics(store_name: str, file_path: str):
    """
    获取特定门店的指标数据
    """
    try:
        logger.info(f"收到获取门店指标请求: {store_name}, 文件: {file_path}")
        
        # 创建Excel读取器
        reader = StoreMetricsReader(file_path)
        
        # 读取Excel内容
        result = reader.read_excel()
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        # 获取特定门店的数据
        if store_name not in result["data"]:
            raise HTTPException(status_code=404, detail=f"门店不存在: {store_name}")
        
        store_data = result["data"][store_name]
        
        logger.info(f"成功获取门店指标: {store_name}")
        
        return {
            "success": True,
            "message": f"成功获取门店 {store_name} 的指标数据",
            "store_name": store_name,
            "metrics": store_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取门店指标异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取门店指标失败: {str(e)}")


@router.get("/metric-daily-data/{store_name}/{metric_name}")
async def get_metric_daily_data(store_name: str, metric_name: str, file_path: str):
    """
    获取特定门店和指标的每日数据
    """
    try:
        logger.info(f"收到获取每日数据请求: {store_name}, {metric_name}, 文件: {file_path}")
        
        # 创建Excel读取器
        reader = StoreMetricsReader(file_path)
        
        # 获取每日数据
        daily_data = reader.get_daily_data(store_name, metric_name)
        
        if not daily_data:
            raise HTTPException(status_code=404, detail=f"未找到数据: {store_name} - {metric_name}")
        
        logger.info(f"成功获取每日数据: {store_name} - {metric_name}")
        
        return {
            "success": True,
            "message": f"成功获取 {store_name} - {metric_name} 的每日数据",
            "store_name": store_name,
            "metric_name": metric_name,
            "data": daily_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取每日数据异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取每日数据失败: {str(e)}")


@router.get("/store-tracking")
async def get_store_tracking():
    """
    获取所有门店数据跟踪信息
    """
    try:
        logger.info("收到获取门店跟踪信息请求")
        
        tracking_data = config_db_manager.get_all_store_tracking()
        
        return {
            "success": True,
            "message": f"成功获取 {len(tracking_data)} 个门店的跟踪信息",
            "tracking_data": tracking_data
        }
        
    except Exception as e:
        logger.error(f"获取门店跟踪信息异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取门店跟踪信息失败: {str(e)}")


@router.get("/store-tracking/{store_name}")
async def get_store_tracking_by_name(store_name: str):
    """
    获取指定门店的数据跟踪信息
    """
    try:
        logger.info(f"收到获取门店跟踪信息请求: {store_name}")
        
        tracking_data = config_db_manager.get_all_store_tracking()
        store_tracking = [item for item in tracking_data if item['store_name'] == store_name]
        
        return {
            "success": True,
            "message": f"成功获取门店 {store_name} 的跟踪信息",
            "store_name": store_name,
            "tracking_data": store_tracking
        }
        
    except Exception as e:
        logger.error(f"获取门店跟踪信息异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取门店跟踪信息失败: {str(e)}")


@router.get("/reading-mode-suggestions")
async def get_reading_mode_suggestions():
    """
    获取读取模式建议
    """
    try:
        suggestions = {
            "incremental": {
                "title": "增量读取",
                "description": "只读取数据库中最新日期之后的新数据",
                "advantages": [
                    "处理速度快，适合日常更新",
                    "避免重复处理已有数据",
                    "减少系统资源消耗"
                ],
                "recommended_for": [
                    "日常数据更新",
                    "定期导入新数据",
                    "数据量较大的情况",
                    "需要快速处理的场景"
                ]
            },
            "full": {
                "title": "全量读取",
                "description": "读取Excel文件中的所有数据",
                "advantages": [
                    "确保数据完整性",
                    "可以重新处理所有数据",
                    "适合数据修复和验证"
                ],
                "recommended_for": [
                    "首次导入数据",
                    "数据修复和重新处理",
                    "数据验证和检查",
                    "Excel文件格式发生变化"
                ]
            }
        }
        
        return {
            "success": True,
            "message": "成功获取读取模式建议",
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"获取读取模式建议异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取读取模式建议失败: {str(e)}")


@router.post("/export-matched-data")
async def export_matched_data(request: Dict[str, Any]):
    """
    导出已匹配的门店对比数据
    """
    try:
        comparison_data = request.get("comparison_data", {})
        target_month = request.get("target_month")
        
        if not comparison_data:
            raise HTTPException(status_code=400, detail="缺少对比数据")
        
        logger.info(f"开始导出已匹配门店数据，门店数量: {len(comparison_data)}")
        
        # 导入数据对比服务
        from backend.utils.data_comparator import DataComparator
        
        # 创建数据对比器
        comparator = DataComparator(target_month)
        
        # 生成Excel文件
        export_result = await comparator.export_comparison_excel(comparison_data)
        
        return {
            "success": True,
            "file_path": export_result["file_path"],
            "file_name": export_result["file_name"],
            "summary": export_result["summary"],
            "message": "已匹配门店数据导出成功"
        }
        
    except Exception as e:
        logger.error(f"导出已匹配数据异常: {e}")
        raise HTTPException(status_code=500, detail=f"导出已匹配数据失败: {str(e)}")


@router.post("/extract-month-from-filename")
async def extract_month_from_filename(request: Dict[str, Any]):
    """
    从文件名中提取月份信息
    """
    try:
        filename = request.get("filename", "")
        
        if not filename:
            raise HTTPException(status_code=400, detail="缺少文件名参数")
        
        logger.info(f"提取文件名月份信息: {filename}")
        
        # 导入数据对比服务
        from backend.utils.data_comparator import DataComparator
        
        # 创建数据对比器实例来使用月份提取方法
        comparator = DataComparator()
        detected_month = comparator._extract_month_from_filename(filename)
        
        return {
            "success": True,
            "filename": filename,
            "detected_month": detected_month,
            "has_month": bool(detected_month),
            "message": f"成功提取月份信息: {detected_month}" if detected_month else "未检测到月份信息"
        }
            
    except Exception as e:
        logger.error(f"提取文件名月份信息异常: {e}")
        raise HTTPException(status_code=500, detail=f"提取月份信息失败: {str(e)}")


class CompareDataRequest(BaseModel):
    """数据对比请求模型"""
    excel_data: Dict[str, Any]
    stores: List[Dict[str, Any]]
    target_month: str
    excel_filename: str = ""


@router.post("/compare-and-export")
async def compare_data(request: CompareDataRequest):
    """
    对比Excel数据与数据库数据
    """
    try:
        logger.info(f"收到数据对比请求，目标月份: {request.target_month}")
        logger.info(f"Excel文件名: {request.excel_filename}")
        logger.info(f"门店数量: {len(request.stores)}")
        
        # 验证请求参数
        if not request.excel_data or not request.stores:
            raise HTTPException(status_code=400, detail="缺少必要的Excel数据或门店信息")
        
        if not request.target_month:
            raise HTTPException(status_code=400, detail="缺少目标月份信息")
        
        # 创建数据对比器
        comparator = DataComparator(
            target_month=request.target_month,
            excel_filename=request.excel_filename
        )
        
        # 执行数据对比
        result = await comparator.process_comparison(
            excel_data=request.excel_data,
            stores=request.stores,
            selected_fields=None  # 使用默认字段
        )
        
        # 调试日志：检查返回结果
        logger.info("API返回结果检查:")
        logger.info(f"  - has_errors: {result.get('has_errors', 'N/A')}")
        logger.info(f"  - errors count: {len(result.get('errors', []))}")
        logger.info(f"  - warnings count: {len(result.get('warnings', []))}")
        logger.info(f"  - comparison_data keys: {list(result.get('comparison_data', {}).keys())}")
        logger.info(f"  - database_info: {result.get('database_info', {})}")
        logger.info(f"  - database_info type: {type(result.get('database_info', {}))}")
        logger.info(f"  - database_info keys: {list(result.get('database_info', {}).keys()) if isinstance(result.get('database_info', {}), dict) else 'Not a dict'}")
        
        # 返回对比结果
        return {
            "success": True,
            "has_errors": result.get("has_errors", False),
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", []),
            "comparison_data": result.get("comparison_data", {}),
            "database_info": result.get("database_info", {}),
            "message": "数据对比完成"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"数据对比异常: {e}")
        raise HTTPException(status_code=500, detail=f"数据对比失败: {str(e)}")
