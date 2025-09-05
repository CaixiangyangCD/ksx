#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于API网络请求的数据提取脚本
使用Playwright拦截/UIProcessor请求获取数据
"""

import asyncio
import logging
from datetime import datetime
from crawler import KSXCrawler


async def main():
    """主函数 - 执行基于API的数据提取"""
    print("🚀 开始基于API的KSX数据提取...")
    
    # 创建爬虫实例（显示浏览器方便调试）
    crawler = KSXCrawler(headless=False, timeout=30000)
    
    try:
        # 启动浏览器
        print("📱 正在启动浏览器...")
        browser_success = await crawler.start_browser()
        if not browser_success:
            print("❌ 浏览器启动失败")
            return
        
        print("✅ 浏览器启动成功")
        
        # 执行登录
        print("🔐 正在登录...")
        login_success = await crawler.login()
        if not login_success:
            print("❌ 登录失败")
            return
        
        print("✅ 登录成功")
        
        # 执行完整的API数据提取流程
        print("📊 开始API数据提取...")
        extraction_success = await crawler.full_api_data_extraction()
        
        if extraction_success:
            print("🎉 API数据提取完成！")
        else:
            print("❌ API数据提取失败")
        
        # 等待用户确认
        input("\n按回车键关闭浏览器...")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        logging.error(f"程序异常: {e}", exc_info=True)
    finally:
        # 清理资源
        print("🔄 正在清理资源...")
        await crawler.close()
        print("✅ 资源清理完成")


if __name__ == "__main__":
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
    asyncio.run(main())
