#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据同步API路由
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
import sys
import os
import asyncio
from loguru import logger

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from backend.models.schemas import SyncRequest, SyncResponse

router = APIRouter(prefix="/api", tags=["sync"])


async def run_crawler(target_date: str = None):
    """运行爬虫程序"""
    try:
        if target_date:
            logger.info(f"开始运行爬虫程序，目标日期: {target_date}")
        else:
            logger.info("开始运行爬虫程序，使用默认日期")
        
        # 构建爬虫命令
        crawler_script = os.path.join(project_root, "services", "crawler", "main.py")
        
        # 使用uv运行爬虫
        cmd = ["uv", "run", "python", crawler_script]
        
        # 如果指定了日期，添加日期参数
        if target_date:
            cmd.extend(["--date", target_date])
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 运行爬虫程序
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=project_root
        )
        
        # 等待进程完成
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            output = stdout.decode('utf-8', errors='ignore')
            logger.info("爬虫程序执行成功")
            logger.info(f"输出: {output}")
            
            # 解析输出，获取最终数据条数和消息
            new_count = 0
            message = "数据同步完成"
            
            # 从输出中提取信息
            if "没有业务数据" in output or "当前日期没有业务数据" in output:
                message = "当前日期没有业务数据，请核查日期"
                new_count = 0
            elif "ERROR_TYPE: BROWSER_START_FAILED" in output:
                message = "浏览器启动失败，请检查浏览器安装或权限设置"
                new_count = 0
            elif "ERROR_TYPE: LOGIN_FAILED" in output:
                message = "登录失败，请检查用户名密码或网络连接"
                new_count = 0
            elif "ERROR_TYPE: DATA_EXTRACTION_FAILED" in output:
                message = "数据提取失败，请检查网络连接或稍后重试"
                new_count = 0
            elif "ERROR_TYPE: USER_INTERRUPTED" in output:
                message = "用户中断操作"
                new_count = 0
            elif "ERROR_TYPE: UNKNOWN_ERROR" in output:
                message = "未知错误，请查看日志或联系管理员"
                new_count = 0
            elif "共获取" in output:
                # 尝试从输出中提取数据条数
                import re
                match = re.search(r'共获取\s*(\d+)\s*条', output)
                if match:
                    new_count = int(match.group(1))
            elif "数据库记录" in output:
                # 尝试从输出中提取数据库记录数
                import re
                match = re.search(r'数据库记录:\s*(\d+)条', output)
                if match:
                    new_count = int(match.group(1))
            
            return True, message, new_count
        else:
            error_msg = stderr.decode('utf-8', errors='ignore')
            logger.error(f"爬虫程序执行失败: {error_msg}")
            return False, f"爬虫执行失败: {error_msg}", 0
            
    except Exception as e:
        logger.error(f"运行爬虫程序异常: {e}")
        return False, f"运行爬虫程序异常: {str(e)}", 0


@router.post("/sync-data", response_model=SyncResponse)
async def sync_data(request: SyncRequest, background_tasks: BackgroundTasks):
    """
    同步数据接口
    
    启动爬虫程序获取指定日期的数据
    """
    try:
        target_date = request.date
        if target_date:
            logger.info(f"收到同步数据请求，目标日期: {target_date}")
        else:
            logger.info("收到同步数据请求，使用默认日期")
        
        # 运行爬虫程序
        success, message, new_count = await run_crawler(target_date)
        
        if success:
            logger.info(f"数据同步完成，共 {new_count or 0} 条数据")
            return SyncResponse(
                success=True,
                message=message,
                total=new_count
            )
        else:
            logger.error(f"数据同步失败: {message}")
            return SyncResponse(
                success=False,
                message=message,
                error_code="CRAWLER_ERROR"
            )
        
    except Exception as e:
        logger.error(f"同步数据接口异常: {e}")
        return SyncResponse(
            success=False,
            message=f"同步数据失败: {str(e)}",
            error_code="INTERNAL_ERROR"
        )
