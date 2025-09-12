#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据同步API路由
"""

from fastapi import APIRouter, BackgroundTasks
import sys
import os
import asyncio
import subprocess
import shutil
from backend.models.schemas import SyncRequest, SyncResponse, BatchSyncRequest

# 尝试导入loguru，如果失败则使用标准logging
try:
    from loguru import logger
    LOGGER_AVAILABLE = True
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    LOGGER_AVAILABLE = False
    # print("警告: loguru不可用，使用标准logging模块")

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

router = APIRouter(prefix="/api", tags=["sync"])


async def run_crawler_internal(target_date: str = None):
    """在打包环境中使用子进程运行爬虫，避免Qt冲突"""
    try:
        # 设置爬虫数据库目录环境变量
        from services.database_manager import get_database_dir
        main_db_dir = get_database_dir()
        os.environ['KSX_DATABASE_DIR'] = main_db_dir
        logger.info(f"设置爬虫数据库目录环境变量: {main_db_dir}")
        
        # 在打包环境中，使用子进程运行爬虫，避免与Qt主线程冲突
        
        # 构建爬虫命令 - 使用外部Python进程完全隔离
        if getattr(sys, 'frozen', False):
            # 打包环境：直接在当前进程中执行爬虫，避免子进程问题
            logger.info("打包环境：在当前进程中执行爬虫")
            logger.info(f" 执行爬虫命令: 直接在当前进程中调用 services.crawler.main.main(target_date='{target_date}')")
            
            try:
                # 设置环境变量
                env = os.environ.copy()
                env['KSX_DATABASE_DIR'] = main_db_dir
                logger.info(f" 设置数据库目录环境变量: {main_db_dir}")
                
                # 调试系统路径信息
                logger.info(f" 当前工作目录: {os.getcwd()}")
                logger.info(f" sys.executable: {sys.executable}")
                logger.info(f" hasattr(sys, '_MEIPASS'): {hasattr(sys, '_MEIPASS')}")
                if hasattr(sys, '_MEIPASS'):
                    logger.info(f" sys._MEIPASS: {sys._MEIPASS}")
                logger.info(f" sys.path前5项: {sys.path[:5]}")
                
                # 确保模块路径正确
                if hasattr(sys, '_MEIPASS'):
                    # 添加打包环境的路径
                    if sys._MEIPASS not in sys.path:
                        sys.path.insert(0, sys._MEIPASS)
                        logger.info(f" 已添加MEIPASS到sys.path: {sys._MEIPASS}")
                    
                    # 检查services目录是否存在
                    services_path = os.path.join(sys._MEIPASS, 'services')
                    crawler_path = os.path.join(sys._MEIPASS, 'services', 'crawler')
                    main_path = os.path.join(sys._MEIPASS, 'services', 'crawler', 'main.py')
                    logger.info(f" services目录存在: {os.path.exists(services_path)}")
                    logger.info(f" crawler目录存在: {os.path.exists(crawler_path)}")
                    logger.info(f" main.py文件存在: {os.path.exists(main_path)}")
                    
                    if os.path.exists(services_path):
                        logger.info(f" services目录内容: {os.listdir(services_path)}")
                    if os.path.exists(crawler_path):
                        logger.info(f" crawler目录内容: {os.listdir(crawler_path)}")
                
                logger.info(" 尝试导入爬虫模块...")
                # 直接导入并执行爬虫
                from services.crawler.main import main as crawler_main
                logger.info(" 爬虫模块导入成功")
                
                # 在新的asyncio事件循环中运行爬虫
                import asyncio
                
                async def run_crawler_async():
                    try:
                        result = await crawler_main(target_date)
                        # 解析爬虫返回的结果
                        if isinstance(result, dict):
                            if result.get('success', False):
                                message = result.get('message', '爬虫执行完成')
                                # 尝试从消息中提取数据条数
                                new_count = 0
                                if '新增' in message and '条' in message:
                                    import re
                                    match = re.search(r'新增\s*(\d+)\s*条', message)
                                    if match:
                                        new_count = int(match.group(1))
                                        logger.info(f" 成功解析新增数据条数: {new_count}")
                                    else:
                                        logger.warning(f" 无法从消息中解析数据条数: {message}")
                                elif '数据已是最新状态' in message or '无新记录' in message:
                                    # 这种情况是成功的，但没有新数据
                                    message = "数据已是最新"
                                    new_count = 0
                                return True, message, new_count
                            else:
                                # 爬虫执行失败的情况
                                error_message = result.get('message', '爬虫执行失败')
                                if '没有业务数据' in error_message or '没有数据' in error_message:
                                    return False, "当前同步日期没有数据", 0
                                else:
                                    return False, error_message, 0
                        else:
                            return True, "爬虫执行完成", 0
                    except Exception as e:
                        error_msg = str(e).encode('ascii', errors='ignore').decode('ascii')
                        logger.error(f"Crawler execution error: {error_msg}")
                        return False, f"Crawler execution error: {error_msg}", 0
                
                # 直接在当前事件循环中运行爬虫
                result = await run_crawler_async()
                return result
                    
            except Exception as e:
                error_msg = str(e).encode('ascii', errors='ignore').decode('ascii')
                logger.error(f"Crawler module import or execution failed: {error_msg}")
                return False, f"Crawler execution failed: {error_msg}", 0
            
            # 这里不需要设置cmd，因为我们直接在当前进程执行了
            cmd = None
        else:
            # 开发环境：使用Python模块方式
            cmd = [sys.executable, "-m", "services.crawler.main"]
            if target_date:
                cmd.extend(["--date", target_date])
            logger.info(f" 执行爬虫命令: {' '.join(cmd)}")
        
        # 如果是打包环境且已经在当前进程执行了爬虫，直接返回结果
        if getattr(sys, 'frozen', False) and cmd is None:
            # 在打包环境中，爬虫已经在当前进程执行完成
            return result
        
        logger.info(f"执行爬虫命令: {' '.join(cmd[:2])}...")
        
        # 设置环境变量
        env = os.environ.copy()
        env['KSX_DATABASE_DIR'] = main_db_dir
        
        # 运行爬虫程序
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        # 实时读取输出
        stdout_lines = []
        stderr_lines = []
        
        async def read_stdout():
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                line_text = line.decode('utf-8', errors='ignore').strip()
                if line_text:
                    stdout_lines.append(line_text)
                    logger.info(f"爬虫输出: {line_text}")
                    # print(f"爬虫输出: {line_text}")
        
        async def read_stderr():
            while True:
                line = await process.stderr.readline()
                if not line:
                    break
                line_text = line.decode('utf-8', errors='ignore').strip()
                if line_text:
                    stderr_lines.append(line_text)
                    # 根据日志级别分类显示
                    if "ERROR" in line_text:
                        logger.error(f"爬虫错误: {line_text}")
                        # print(f"爬虫错误: {line_text}")
                    elif "WARNING" in line_text:
                        logger.warning(f"爬虫警告: {line_text}")
                        # print(f"爬虫警告: {line_text}")
                    else:
                        logger.info(f"爬虫信息: {line_text}")
                        # print(f"爬虫信息: {line_text}")
        
        # 启动读取任务
        stdout_task = asyncio.create_task(read_stdout())
        stderr_task = asyncio.create_task(read_stderr())
        
        # 等待进程完成
        return_code = await process.wait()
        
        # 等待读取任务完成
        await stdout_task
        await stderr_task
        
        stdout = '\n'.join(stdout_lines).encode('utf-8')
        stderr = '\n'.join(stderr_lines).encode('utf-8')
        
        # 注意：在打包环境中，爬虫是在当前进程执行的，不会到达这里
        
        if return_code == 0:
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
            stdout_text = stdout.decode('utf-8', errors='ignore')
            stderr_text = stderr.decode('utf-8', errors='ignore')
            
            logger.error(f"爬虫程序执行失败，返回码: {return_code}")
            logger.error(f"标准输出: {stdout_text}")
            logger.error(f"标准错误: {stderr_text}")
            
            # 组合错误信息
            error_msg = f"返回码: {return_code}"
            if stdout_text:
                error_msg += f"\n输出: {stdout_text}"
            if stderr_text:
                error_msg += f"\n错误: {stderr_text}"
            
            return False, f"爬虫执行失败: {error_msg}", 0
        
    except Exception as e:
        error_msg = str(e).encode('ascii', errors='ignore').decode('ascii')
        logger.error(f"Internal crawler execution failed: {error_msg}")
        return False, f"Internal crawler execution failed: {error_msg}", 0


async def run_crawler_external(target_date: str = None, project_root: str = None):
    """在开发环境中使用外部进程运行爬虫"""
    try:
        # 构建爬虫命令
        crawler_script = os.path.join(project_root, "services", "crawler", "main.py")
        
        # 检查是否可以使用uv命令，如果不行则直接使用python
        if shutil.which("uv"):
            cmd = ["uv", "run", "python", crawler_script]
        else:
            cmd = ["python", crawler_script]
        
        # 如果指定了日期，添加日期参数
        if target_date:
            cmd.extend(["--date", target_date])
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 设置环境变量，让爬虫使用正确的数据库目录
        env = os.environ.copy()
        # 获取主应用的数据库目录
        from services.database_manager import get_database_dir
        main_db_dir = get_database_dir()
        env['KSX_DATABASE_DIR'] = main_db_dir
        logger.info(f"设置爬虫数据库目录环境变量: {main_db_dir}")
        
        # 运行爬虫程序 - 使用更兼容的方式
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=project_root,
                env=env
            )
        except NotImplementedError:
            # Windows兼容性处理：使用同步方式
            logger.info("异步子进程创建失败，使用同步方式")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project_root,
                env=env,
                text=True
            )
            # 等待进程完成
            stdout, stderr = process.communicate()
            return_code = process.returncode
            
            if return_code == 0:
                logger.info("爬虫执行成功")
                # 尝试从输出中解析爬取的数据条数
                total_count = 0
                if stdout:
                    # 查找 "Total Records: X" 的模式
                    import re
                    match = re.search(r'Total Records:\s*(\d+)', stdout)
                    if match:
                        total_count = int(match.group(1))
                    else:
                        # 如果没有找到，尝试查找其他模式
                        match = re.search(r'(\d+).*?条.*?数据', stdout)
                        if match:
                            total_count = int(match.group(1))
                
                logger.info(f"爬虫输出: {stdout}")
                return {"success": True, "message": "爬虫执行成功", "total": total_count}
            else:
                logger.error(f"爬虫执行失败，返回码: {return_code}")
                logger.error(f"错误输出: {stderr}")
                return {"success": False, "message": f"爬虫执行失败: {stderr}"}                                                                                                                                                                                                            
        
        # 实时读取输出
        stdout_lines = []
        stderr_lines = []
        
        async def read_stdout():
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                line_text = line.decode('utf-8', errors='ignore').strip()
                if line_text:
                    stdout_lines.append(line_text)
                    logger.info(f"爬虫输出: {line_text}")
                    # print(f"爬虫输出: {line_text}")  
        
        async def read_stderr():
            while True:
                line = await process.stderr.readline()
                if not line:
                    break
                line_text = line.decode('utf-8', errors='ignore').strip()
                if line_text:
                    stderr_lines.append(line_text)
                    # 根据日志级别分类显示
                    if "ERROR" in line_text or "" in line_text:
                        logger.error(f"爬虫错误: {line_text}")
                        # print(f"爬虫错误: {line_text}")
                    elif "WARNING" in line_text or "" in line_text:
                        logger.warning(f"爬虫警告: {line_text}")
                        # print(f"爬虫警告: {line_text}")
                    else:
                        logger.info(f"爬虫信息: {line_text}")
                        # print(f"爬虫信息: {line_text}")
        
        # 启动读取任务
        stdout_task = asyncio.create_task(read_stdout())
        stderr_task = asyncio.create_task(read_stderr())
        
        # 等待进程完成
        return_code = await process.wait()
        
        # 等待读取任务完成
        await stdout_task
        await stderr_task
        
        stdout = '\n'.join(stdout_lines).encode('utf-8')
        stderr = '\n'.join(stderr_lines).encode('utf-8')
        
        if return_code == 0:
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
            
            return {"success": True, "message": message, "total": new_count}
        else:
            error_msg = stderr.decode('utf-8', errors='ignore')
            logger.error(f"爬虫程序执行失败: {error_msg}")
            return {"success": False, "message": f"爬虫执行失败: {error_msg}", "total": 0}
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Crawler execution exception: {error_msg}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {"success": False, "message": f"Crawler execution exception: {error_msg}", "total": 0}


async def run_crawler(target_date: str = None):
    """运行爬虫程序"""
    try:
        if target_date:
            logger.info(f"开始运行爬虫程序，目标日期: {target_date}")
        else:
            logger.info("开始运行爬虫程序，使用默认日期")
        
        # 根据环境选择不同的执行方式
        if getattr(sys, 'frozen', False):
            # 打包环境：直接调用爬虫模块，不依赖外部Python
            logger.info("打包环境：使用内置爬虫模块")
            return await run_crawler_internal(target_date)
        else:
            # 开发环境：使用外部进程
            logger.info("开发环境：使用外部进程")
            return await run_crawler_external(target_date, project_root)
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Crawler execution failed: {error_msg}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {"success": False, "message": f"Crawler execution failed: {error_msg}", "total": 0}


async def run_crawler_batch_external(start_date: str, end_date: str = None, project_root: str = None):
    """在开发环境中使用外部进程运行批量爬虫（后台执行，不等待结果）"""
    try:
        # 构建爬虫命令
        crawler_script = os.path.join(project_root, "services", "crawler", "main.py")
        
        # 检查是否可以使用uv命令，如果不行则直接使用python
        if shutil.which("uv"):
            cmd = ["uv", "run", "python", crawler_script, "--start-date", start_date]
        else:
            cmd = ["python", crawler_script, "--start-date", start_date]
        
        # 如果指定了结束日期，添加结束日期参数
        if end_date:
            cmd.extend(["--end-date", end_date])
        
        logger.info(f"执行批量爬虫命令: {' '.join(cmd)}")
        logger.info(f"命令详细参数 - start_date: {start_date}, end_date: {end_date}")
        
        # 设置环境变量
        env = os.environ.copy()
        
        # 获取主应用的数据库目录
        from services.database_manager import get_database_dir
        main_db_dir = get_database_dir()
        env['KSX_DATABASE_DIR'] = main_db_dir
        logger.info(f"设置爬虫数据库目录环境变量: {main_db_dir}")
        
        # 使用Popen启动后台进程，不等待结果
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project_root,
            env=env,
            text=True
        )
        
        logger.info(f"批量爬虫已启动，进程ID: {process.pid}")
        return {"success": True, "message": "批量爬虫已开始执行", "pid": process.pid}
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Batch crawler execution exception: {error_msg}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {"success": False, "message": f"批量爬虫启动失败: {error_msg}"}


async def run_crawler_batch(start_date: str, end_date: str = None):
    """运行批量爬虫程序（后台执行）"""
    try:
        logger.info(f"开始运行批量爬虫程序，日期范围: {start_date} 到 {end_date or start_date}")
        
        # 根据环境选择不同的执行方式
        if getattr(sys, 'frozen', False):
            # 打包环境：使用内置模块（这里暂时返回不支持，因为批量处理在打包环境中可能有问题）
            logger.warning("打包环境暂不支持批量爬取")
            return {"success": False, "message": "打包环境暂不支持批量爬取"}
        else:
            # 开发环境：使用外部进程
            logger.info("开发环境：使用外部进程执行批量爬虫")
            return await run_crawler_batch_external(start_date, end_date, project_root)
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Batch crawler execution failed: {error_msg}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {"success": False, "message": f"批量爬虫执行失败: {error_msg}"}


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
        result = await run_crawler(target_date)
        
        if isinstance(result, dict):
            # 新的字典格式
            return SyncResponse(
                success=result["success"],
                message=result["message"],
                total=result["total"]
            )
        else:
            # 兼容旧的元组格式
            success, message, new_count = result
            return SyncResponse(
                success=success,
                message=message,
                total=new_count
            )
            
    except Exception as e:
        error_msg = str(e).encode('ascii', errors='ignore').decode('ascii')
        logger.error(f"Data sync failed: {error_msg}")
        return SyncResponse(
            success=False,
            message=f"数据同步失败: {str(e)}",
            total=0
        )


@router.post("/batch-sync-data", response_model=SyncResponse)
async def batch_sync_data(request: BatchSyncRequest, background_tasks: BackgroundTasks):
    """
    批量同步数据接口
    
    启动批量爬虫程序获取指定日期范围的数据，后台执行不等待结果
    """
    try:
        start_date = request.start_date
        end_date = request.end_date or request.start_date  # 如果没有结束日期，使用开始日期
        
        logger.info(f"收到批量同步数据请求，日期范围: {start_date} 到 {end_date}")
        
        # 运行批量爬虫程序（后台执行）
        result = await run_crawler_batch(start_date, end_date)
        
        if isinstance(result, dict):
            return SyncResponse(
                success=result["success"],
                message=result["message"],
                total=0  # 批量执行时无法立即返回总数
            )
        else:
            return SyncResponse(
                success=False,
                message="批量爬虫启动失败",
                total=0
            )
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Batch data sync failed: {error_msg}")
        return SyncResponse(
            success=False,
            message=f"批量数据同步失败: {error_msg}",
            total=0
        )