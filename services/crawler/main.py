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
from crawler import KSXCrawler


async def main(target_date: str = None):
    """主函数 - 执行基于API的数据提取"""
    if target_date:
        print(f"🚀 开始基于API的KSX数据提取，目标日期: {target_date}")
    else:
        print("🚀 开始基于API的KSX数据提取...")
    
    # 创建爬虫实例（使用配置文件中的设置）
    from config import get_config
    config = get_config()
    crawler = KSXCrawler(headless=config['browser']['headless'], timeout=30000)
    
    # 如果指定了日期，设置爬虫的目标日期
    if target_date:
        crawler.target_date = target_date
    
    try:
        # 启动浏览器
        print("📱 正在启动浏览器...")
        browser_success = await crawler.start_browser()
        if not browser_success:
            print("❌ 浏览器启动失败")
            print("ERROR_TYPE: BROWSER_START_FAILED")
            return
        
        print("✅ 浏览器启动成功")
        
        # 执行登录
        print("🔐 正在登录...")
        login_success = await crawler.login()
        if not login_success:
            print("❌ 登录失败")
            print("ERROR_TYPE: LOGIN_FAILED")
            return
        
        print("✅ 登录成功")
        
        # 执行完整的API数据提取流程
        print("📊 开始API数据提取...")
        extraction_success = await crawler.full_api_data_extraction()
        
        if extraction_success:
            print("🎉 API数据提取完成！")
        else:
            print("❌ API数据提取失败")
            print("ERROR_TYPE: DATA_EXTRACTION_FAILED")
        
        # 自动关闭，无需用户确认
        print("🔄 程序执行完成，正在自动关闭...")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        print("ERROR_TYPE: USER_INTERRUPTED")
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        print("ERROR_TYPE: UNKNOWN_ERROR")
        logging.error(f"程序异常: {e}", exc_info=True)
    finally:
        # 清理资源
        print("🔄 正在清理资源...")
        await crawler.close()
        print("✅ 资源清理完成")


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
