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
from datetime import datetime
from .crawler import KSXCrawler


async def main(target_date: str = None):
    """主函数 - 执行基于API的数据提取"""
    if target_date:
        logging.info(f"开始基于API的KSX数据提取，目标日期: {target_date}")
    else:
        logging.info("开始基于API的KSX数据提取...")
    
    # 创建爬虫实例（使用配置文件中的设置）
    try:
        from config import get_config
        config = get_config()
        crawler = KSXCrawler(headless=config['browser']['headless'], timeout=30000)
    except ImportError as e:
        logging.error(f"配置导入失败，使用默认设置: {e}")
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
            # 返回完整的结果，以便后端能够正确解析
            return extraction_result
        else:
            error_msg = extraction_result.get('message', '数据提取失败')
            if '没有业务数据' in error_msg or '没有数据' in error_msg:
                logging.info(f" {error_msg}")
                logging.info("INFO_TYPE: NO_DATA_FOR_DATE")
            else:
                logging.error(f" {error_msg}")
                logging.error("ERROR_TYPE: DATA_EXTRACTION_FAILED")
            # 返回失败结果
            return extraction_result
        
        # 自动关闭，无需用户确认
        logging.info(" 程序执行完成，正在自动关闭...")
        
    except KeyboardInterrupt:
        logging.error("\n 用户中断操作")
        logging.error("ERROR_TYPE: USER_INTERRUPTED")
        return {"success": False, "message": "用户中断操作"}
    except Exception as e:
        logging.error(f" 程序异常: {e}")
        logging.error("ERROR_TYPE: UNKNOWN_ERROR")
        logging.error(f"程序异常: {e}", exc_info=True)
        return {"success": False, "message": f"程序异常: {str(e)}"}
    finally:
        # 清理资源
        logging.info(" 正在清理资源...")
        await crawler.close()
        logging.info(" 资源清理完成")


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='KSX数据爬虫')
    parser.add_argument('--date', type=str, help='指定要爬取的日期 (YYYY-MM-DD)')
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
    
    # 运行主函数
    asyncio.run(main(args.date))
