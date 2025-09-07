#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据同步API路由
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
import sys
import os
import subprocess
import asyncio
from loguru import logger

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from backend.models.schemas import SyncDataRequest, SyncResponse

router = APIRouter(prefix="/api", tags=["sync"])


@router.post("/sync-data", response_model=SyncResponse)
async def sync_data(request: SyncDataRequest, background_tasks: BackgroundTasks):
    """
    同步数据
    """
    try:
        # 启动爬虫进程
        crawler_script = os.path.join(project_root, "services", "crawler", "main.py")
        
        if not os.path.exists(crawler_script):
            raise HTTPException(status_code=404, detail="爬虫脚本不存在")
        
        # 构建命令
        cmd = [
            sys.executable,
            crawler_script,
            "--date", request.date
        ]
        
        logger.info(f"启动爬虫进程: {' '.join(cmd)}")
        
        # 在后台运行爬虫
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_root
        )
        
        # 等待进程完成
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            # 解析输出，获取同步的数据量和状态
            total = 0
            has_data = False
            no_data_reason = ""
            
            if stdout:
                for line in stdout.split('\n'):
                    # 检查是否有数据保存
                    if "成功保存" in line and "条记录" in line:
                        try:
                            # 提取数字
                            import re
                            match = re.search(r'(\d+)条记录', line)
                            if match:
                                total = int(match.group(1))
                                has_data = True
                                break
                        except:
                            pass
                    # 检查是否因为没有数据而失败
                    elif "当前日期没有业务数据" in line:
                        no_data_reason = "该日期没有业务数据"
                    elif "没有数据需要保存" in line:
                        no_data_reason = "没有新数据需要保存"
            
            # 根据情况返回不同的消息
            if has_data and total > 0:
                message = f"数据同步完成，新增 {total} 条数据"
            elif no_data_reason:
                message = f"数据同步完成，{no_data_reason}"
            else:
                message = "数据同步完成，未获取到新数据"
            
            return SyncResponse(
                success=True,
                message=message,
                total=total
            )
        else:
            error_msg = stderr if stderr else "爬虫执行失败"
            logger.error(f"爬虫执行失败: {error_msg}")
            return SyncResponse(
                success=False,
                message=f"数据同步失败: {error_msg}"
            )
            
    except Exception as e:
        logger.error(f"同步数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步数据失败: {str(e)}")
