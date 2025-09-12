#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于API网络请求的数据提取脚本
使用Playwright拦截/UIProcessor请求获取数据
"""

import asyncio
import logging
import os
import sys
import argparse
# 智能导入机制，同时支持开发环境和生产环境

def import_crawler():
    """智能导入爬虫类，支持开发环境和生产环境"""
    try:
        # 首先尝试相对导入（开发环境）
        from .crawler import KSXCrawler
        return KSXCrawler
    except ImportError:
        try:
            # 尝试绝对导入（生产环境）
            from services.crawler.crawler import KSXCrawler
            return KSXCrawler
        except ImportError:
            # 如果都失败，尝试添加路径后导入
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            project_root = os.path.dirname(parent_dir)
            
            # 添加项目根目录到Python路径
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            try:
                from services.crawler.crawler import KSXCrawler
                return KSXCrawler
            except ImportError as e:
                raise ImportError(f"无法导入KSXCrawler类: {e}")

# 导入爬虫类
KSXCrawler = import_crawler()


async def main(target_date: str = None):
    """主函数 - 执行基于API的数据提取"""
    if target_date:
        logging.info(f"开始基于API的KSX数据提取，目标日期: {target_date}")
        logging.info(f"main函数接收到的target_date参数：{target_date}")
    else:
        logging.info("开始基于API的KSX数据提取...")
    
    # 创建爬虫实例（使用配置文件中的设置）
    # 智能导入配置
    try:
        from .config import get_config
        config = get_config()
        crawler = KSXCrawler(headless=config['browser']['headless'], timeout=30000)
    except ImportError:
        try:
            # 尝试绝对导入
            from services.crawler.config import get_config
            config = get_config()
            crawler = KSXCrawler(headless=config['browser']['headless'], timeout=30000)
        except ImportError:
            logging.warning("配置导入失败，使用默认设置")
            # 如果配置导入失败，使用默认设置
            crawler = KSXCrawler(headless=True, timeout=30000)  # 默认使用无头模式
    
    # 如果指定了日期，设置爬虫的目标日期
    if target_date:
        crawler.target_date = target_date
    
    try:
        # 启动浏览器
        logging.info(" 正在启动浏览器...")
        browser_success = await crawler.start_browser()
        if not browser_success:
            logging.error(" 浏览器启动失败")
            logging.error("ERROR_TYPE: BROWSER_START_FAILED")
            return {"success": False, "message": "浏览器启动失败"}
        
        logging.info(" 浏览器启动成功")
        
        # 执行登录
        logging.info(" 正在登录...")
        login_success = await crawler.login()
        if not login_success:
            logging.error(" 登录失败")
            logging.error("ERROR_TYPE: LOGIN_FAILED")
            return {"success": False, "message": "登录失败"}
        
        logging.info(" 登录成功")
        
        # 执行完整的API数据提取流程
        logging.info(" 开始API数据提取...")
        extraction_result = await crawler.full_api_data_extraction()
        
        if extraction_result.get('success', False):
            message = extraction_result.get('message', '数据提取完成')
            logging.info(f" {message}")
            # 同时输出到stdout，让后端能看到（使用英文避免编码问题）
            print(f"Crawler Result: {message}")
            if 'total' in extraction_result:
                print(f"Total Records: {extraction_result['total']}")
            # 返回完整的结果，以便后端能够正确解析
            return extraction_result
        else:
            error_msg = extraction_result.get('message', '数据提取失败')
            if '没有业务数据' in error_msg or '没有数据' in error_msg:
                logging.info(f" {error_msg}")
                logging.info("INFO_TYPE: NO_DATA_FOR_DATE")
                # 同时输出到stdout（使用英文避免编码问题）
                print(f"Crawler Result: {error_msg}")
                print("Total Records: 0")
            else:
                logging.error(f" {error_msg}")
                logging.error("ERROR_TYPE: DATA_EXTRACTION_FAILED")
                # 同时输出到stdout（使用英文避免编码问题）
                print(f"Crawler Failed: {error_msg}")
            # 返回失败结果
            return extraction_result
        
        # 自动关闭，无需用户确认
        logging.info(" 程序执行完成，正在自动关闭...")
        
    except KeyboardInterrupt:
        logging.error("\n 用户中断操作")
        logging.error("ERROR_TYPE: USER_INTERRUPTED")
        print("Crawler Failed: User interrupted")
        return {"success": False, "message": "用户中断操作"}
    except Exception as e:
        logging.error(f" 程序异常: {e}")
        logging.error("ERROR_TYPE: UNKNOWN_ERROR")
        logging.error(f"程序异常: {e}", exc_info=True)
        print(f"Crawler Failed: Exception: {str(e)}")
        return {"success": False, "message": f"程序异常: {str(e)}"}
    finally:
        # 清理资源
        logging.info(" 正在清理资源...")
        await crawler.close()
        logging.info(" 资源清理完成")


async def main_range(start_date: str, end_date: str = None):
    """主函数 - 执行日期范围的数据提取（一次浏览器会话处理整个日期范围）"""
    logging.info(f"开始基于API的KSX日期范围数据提取，开始日期: {start_date}, 结束日期: {end_date or start_date}")
    
    # 创建爬虫实例（使用配置文件中的设置）
    # 智能导入配置
    try:
        from .config import get_config
        config = get_config()
        crawler = KSXCrawler(headless=config['browser']['headless'], timeout=30000)
    except ImportError:
        try:
            # 尝试绝对导入
            from services.crawler.config import get_config
            config = get_config()
            crawler = KSXCrawler(headless=config['browser']['headless'], timeout=30000)
        except ImportError:
            logging.warning("配置导入失败，使用默认设置")
            # 如果配置导入失败，使用默认设置
            crawler = KSXCrawler(headless=True, timeout=30000)  # 默认使用无头模式
    
    try:
        # 启动浏览器
        logging.info(" 正在启动浏览器...")
        browser_success = await crawler.start_browser()
        if not browser_success:
            logging.error(" 浏览器启动失败")
            print("Crawler Failed: Browser start failed")
            return {"success": False, "message": "浏览器启动失败"}
        
        logging.info(" 浏览器启动成功")
        print("Browser started successfully")
        
        # 执行登录
        logging.info(" 正在登录...")
        login_success = await crawler.login()
        if not login_success:
            logging.error(" 登录失败")
            print("Crawler Failed: Login failed")
            return {"success": False, "message": "登录失败"}
        
        logging.info(" 登录成功")
        print("Login successful")
        
        # 执行日期范围数据提取
        logging.info(f" 开始日期范围API数据提取，从 {start_date} 到 {end_date or start_date}...")
        print(f"Starting date range extraction: {start_date} to {end_date or start_date}")
        extraction_result = await crawler.full_api_data_extraction_range(start_date, end_date)
        
        if extraction_result.get('success', False):
            message = extraction_result.get('message', '数据提取完成')
            logging.info(f" {message}")
            # 同时输出到stdout，让后端能看到
            print(f"Crawler Result: {message}")
            if 'total' in extraction_result:
                print(f"Total Records: {extraction_result['total']}")
            # 返回完整的结果，以便后端能够正确解析
            return extraction_result
        else:
            error_msg = extraction_result.get('message', '数据提取失败')
            logging.error(f" {error_msg}")
            print(f"Crawler Failed: {error_msg}")
            return extraction_result
        
    except KeyboardInterrupt:
        logging.error("\n 用户中断操作")
        print("Crawler Failed: User interrupted")
        return {"success": False, "message": "用户中断操作"}
    except Exception as e:
        logging.error(f" 程序异常: {e}")
        logging.error(f"程序异常: {e}", exc_info=True)
        print(f"Crawler Failed: Exception: {str(e)}")
        return {"success": False, "message": f"程序异常: {str(e)}"}
    finally:
        # 清理资源
        logging.info(" 正在清理资源...")
        await crawler.close()
        logging.info(" 资源清理完成")


async def main_batch(start_date: str, end_date: str):
    """
    批量爬取指定日期范围的数据
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    """
    from datetime import datetime, timedelta
    
    try:
        # 解析日期
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_dt > end_dt:
            print("Crawler Failed: Start date must be <= end date")
            logging.error("开始日期不能大于结束日期")
            return {"success": False, "message": "开始日期不能大于结束日期"}
        
        # 生成日期列表
        date_list = []
        current_dt = start_dt
        while current_dt <= end_dt:
            date_list.append(current_dt.strftime('%Y-%m-%d'))
            current_dt += timedelta(days=1)
        
        total_dates = len(date_list)
        total_records = 0
        success_count = 0
        failed_dates = []
        
        print(f"Crawler Batch Started: Processing {total_dates} dates from {start_date} to {end_date}")
        logging.info(f"开始批量爬取，共{total_dates}个日期：从{start_date}到{end_date}")
        
        # 逐个处理每个日期
        for i, date_str in enumerate(date_list, 1):
            print(f"Processing date {i}/{total_dates}: {date_str}")
            logging.info(f"正在处理第{i}/{total_dates}个日期：{date_str}")
            logging.info(f"传入main函数的日期参数：{date_str}")
            
            try:
                # 调用单日期爬取函数
                result = await main(date_str)
                
                if result and result.get('success', False):
                    success_count += 1
                    date_records = result.get('total', 0)
                    total_records += date_records
                    print(f"Date {date_str} completed: {date_records} records")
                    logging.info(f"日期{date_str}完成：{date_records}条记录")
                else:
                    failed_dates.append(date_str)
                    print(f"Date {date_str} failed: {result.get('message', 'Unknown error') if result else 'No result'}")
                    logging.error(f"日期{date_str}失败：{result.get('message', '未知错误') if result else '无结果'}")
                
            except Exception as e:
                failed_dates.append(date_str)
                print(f"Date {date_str} error: {str(e)}")
                logging.error(f"日期{date_str}异常：{str(e)}")
            
            # 在日期之间稍作休息，避免过于频繁
            if i < total_dates:
                await asyncio.sleep(2)
        
        # 输出最终结果
        print(f"Batch Completed: {success_count}/{total_dates} dates successful")
        print(f"Total Records: {total_records}")
        
        if failed_dates:
            print(f"Failed Dates: {', '.join(failed_dates)}")
            logging.warning(f"失败的日期：{', '.join(failed_dates)}")
        
        logging.info(f"批量爬取完成：{success_count}/{total_dates}个日期成功，共{total_records}条记录")
        
        return {
            "success": True,
            "message": f"批量爬取完成：{success_count}/{total_dates}个日期成功",
            "total": total_records,
            "success_count": success_count,
            "failed_count": len(failed_dates),
            "failed_dates": failed_dates
        }
        
    except ValueError as e:
        print(f"Crawler Failed: Invalid date format: {str(e)}")
        logging.error(f"日期格式错误：{str(e)}")
        return {"success": False, "message": f"日期格式错误：{str(e)}"}
    except Exception as e:
        print(f"Crawler Failed: Batch processing error: {str(e)}")
        logging.error(f"批量处理异常：{str(e)}")
        return {"success": False, "message": f"批量处理异常：{str(e)}"}


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='KSX数据爬虫')
    parser.add_argument('--date', type=str, help='指定要爬取的日期 (YYYY-MM-DD)')
    parser.add_argument('--start-date', type=str, help='指定开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='指定结束日期 (YYYY-MM-DD)')
    args = parser.parse_args()
    
    # 设置基本日志配置
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('api_extraction.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 处理参数并运行主函数
    if args.start_date or args.end_date:
        # 使用日期范围模式
        start_date = args.start_date
        end_date = args.end_date
        
        # 确保至少有开始日期
        if not start_date:
            if end_date:
                # 如果只有结束日期，将结束日期作为开始日期
                start_date = end_date
                end_date = None
            else:
                # 如果都没有，报错
                print("Crawler Failed: Must provide at least start_date")
                sys.exit(1)
        
        # 使用新的日期范围处理函数（一次浏览器会话）
        asyncio.run(main_range(start_date, end_date))
    else:
        # 使用单日期模式
        asyncio.run(main(args.date))
