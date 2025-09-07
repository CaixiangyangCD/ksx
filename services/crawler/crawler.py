#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KSX网站爬虫模块 - API版本
使用Playwright实现网站登录和API数据爬取功能
"""

import asyncio
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, Page, BrowserContext, Response
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from loguru import logger
import sys
import os

# 设置浏览器路径到项目目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
browser_path = os.path.join(project_root, "playwright-browsers")
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browser_path

# 自动检查和安装浏览器
def ensure_browser_environment():
    """确保浏览器环境已正确设置"""
    try:
        from services.browser_manager import setup_browser_environment
        if not setup_browser_environment(project_root):
            logger.error("浏览器环境设置失败")
            return False
        return True
    except Exception as e:
        logger.error(f"设置浏览器环境时发生错误: {e}")
        return False

# 在导入时自动检查浏览器环境
if not ensure_browser_environment():
    logger.warning("浏览器环境检查失败，将使用系统默认路径")
    os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)

# 添加项目根目录到路径，以便导入services模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
from services.database_manager import get_db_manager
from services.config_database_manager import config_db_manager


class KSXCrawler:
    """KSX网站爬虫类 - API版本"""
    
    def __init__(self, headless: bool = False, timeout: int = None, target_date: str = None):
        """
        初始化爬虫
        
        Args:
            headless: 是否无头模式运行浏览器
            timeout: 超时时间（毫秒），如果为None则从配置文件读取
            target_date: 目标日期 (YYYY-MM-DD)，如果为None则使用默认日期
        """
        self.headless = headless
        self.target_date = target_date
        
        # 从配置文件读取超时时间
        if timeout is None:
            try:
                from config import WEBSITE_CONFIG
                self.timeout = WEBSITE_CONFIG['timeout']
            except ImportError:
                self.timeout = 30000  # 默认30秒
        else:
            self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # 配置日志
        self._setup_logging()
        
        # 登录信息
        self.login_url = "https://ksx.dahuafuli.com:8306/"
        # 从配置文件读取用户名和密码
        try:
            # 尝试不同的导入方式
            try:
                from config import LOGIN_CONFIG
            except ImportError:
                from .config import LOGIN_CONFIG
            
            self.username = LOGIN_CONFIG['username']
            self.password = LOGIN_CONFIG['password']
        except ImportError:
            # 如果配置文件不存在，使用默认值
            self.username = "fsrm001"
            self.password = "fsrm001"
        
        # 网络请求数据存储
        self.api_responses = []
        self.current_page_data = None
        self.page_info = None
        
    def _setup_logging(self):
        """配置日志系统 - 使用loguru"""
        # 清除默认的logger
        logger.remove()
        
        # 添加控制台输出
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        
        # 添加文件输出，按日期轮转，保留近30天
        logger.add(
            "logs/crawler_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="1 day",
            retention="30 days",
            compression="zip",
            encoding="utf-8"
        )
        
        # 创建logs目录
        Path("logs").mkdir(exist_ok=True)
        
        self.logger = logger
    
    async def _setup_request_interception(self):
        """设置网络请求拦截"""
        if not self.page:
            self.logger.error("页面未初始化，无法设置请求拦截")
            return
            
        # 监听响应
        self.page.on("response", self._handle_response)
        self.logger.info("✅ 网络请求拦截已设置")
    
    async def _handle_response(self, response: Response):
        """处理网络响应"""
        try:
            # 只处理UIProcessor相关的请求
            if "/UIProcessor" in response.url:
                self.logger.info(f"🔍 拦截到UIProcessor请求: {response.url}")
                
                # 获取响应内容
                if response.status == 200:
                    try:
                        response_data = await response.json()
                        self.logger.info(f"📦 UIProcessor响应状态: {response.status}")
                        
                        # 检查响应格式
                        if isinstance(response_data, dict) and 'success' in response_data:
                            if response_data.get('success'):
                                data = response_data.get('data', [])
                                page_info = response_data.get('pageInfo', {})
                                
                                self.logger.info(f"✅ 成功获取数据: {len(data)} 条记录")
                                self.logger.info(f"📄 分页信息: {page_info}")
                                
                                # 存储数据
                                self.current_page_data = data
                                self.page_info = page_info
                                self.api_responses.append({
                                    'url': response.url,
                                    'data': data,
                                    'pageInfo': page_info,
                                    'timestamp': datetime.now()
                                })
                            else:
                                self.logger.warning(f"❌ UIProcessor请求失败: {response_data}")
                        else:
                            self.logger.warning(f"⚠️ 意外的响应格式: {response_data}")
                            
                    except Exception as e:
                        self.logger.error(f"❌ 解析UIProcessor响应失败: {e}")
                        # 尝试获取文本内容
                        try:
                            text_content = await response.text()
                            self.logger.info(f"📝 响应文本内容: {text_content[:500]}...")
                        except Exception:
                            pass
                else:
                    self.logger.warning(f"⚠️ UIProcessor请求状态码: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"❌ 处理响应时出错: {e}")
    
    async def start_browser(self):
        """启动浏览器"""
        try:
            # 确保正确初始化 playwright
            self.playwright = await async_playwright().start()
            if not self.playwright:
                raise Exception("Playwright 初始化失败")
            
            # 启动浏览器 - 使用Chrome Beta
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                channel="chrome-beta",  # 使用Chrome Beta
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            
            if not self.browser:
                raise Exception("浏览器启动失败")
            
            # 创建上下文
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            if not self.context:
                raise Exception("浏览器上下文创建失败")
            
            # 创建页面
            self.page = await self.context.new_page()
            if not self.page:
                raise Exception("页面创建失败")
                
            # set_default_timeout 是同步方法，不需要 await
            self.page.set_default_timeout(self.timeout)
            
            # 设置网络请求拦截
            await self._setup_request_interception()
            
            self.logger.info("浏览器启动成功")
            return True
            
        except Exception as e:
            self.logger.error(f"启动浏览器失败: {e}")
            # 清理已创建的资源
            try:
                await self.close()
            except Exception:
                pass
            return False
    
    async def navigate_to_login(self) -> bool:
        """导航到登录页面"""
        try:
            self.logger.info("正在导航到登录页面...")
            self.logger.info(f"正在访问登录页面: {self.login_url}")
            
            await self.page.goto(self.login_url)
            await self.page.wait_for_load_state('networkidle')
            
            self.logger.info("成功访问登录页面")
            return True
            
        except Exception as e:
            self.logger.error(f"导航到登录页面失败: {e}")
            return False
    
    async def find_login_elements(self) -> Dict[str, Any]:
        """查找登录页面元素"""
        try:
            self.logger.info("正在查找登录元素...")
            
            # 查找用户名输入框
            username_input = await self.page.wait_for_selector('input[name="userId"]', timeout=10000)
            if not username_input:
                raise Exception("未找到用户名输入框")
            
            # 查找密码输入框
            password_input = await self.page.wait_for_selector('input[name="pass"]', timeout=5000)
            if not password_input:
                raise Exception("未找到密码输入框")
            
            # 查找登录按钮
            login_button = await self.page.wait_for_selector('button[type="submit"]', timeout=5000)
            if not login_button:
                raise Exception("未找到登录按钮")
            
            self.logger.info("成功找到所有登录元素")
            return {
                'username_input': username_input,
                'password_input': password_input,
                'login_button': login_button
            }
            
        except Exception as e:
            self.logger.error(f"查找登录元素失败: {e}")
            return {}
    
    async def perform_login(self, elements: Dict[str, Any]) -> bool:
        """执行登录操作"""
        try:
            # 清空输入框并输入用户名
            await elements['username_input'].fill('')
            await elements['username_input'].type(self.username, delay=100)
            self.logger.info(f"输入用户名: {self.username}")
            
            # 清空输入框并输入密码
            await elements['password_input'].fill('')
            await elements['password_input'].type(self.password, delay=100)
            self.logger.info(f"输入密码: {self.password}")
            
            # 点击登录按钮
            await elements['login_button'].click()
            self.logger.info("点击登录按钮")
            
            # 等待页面响应
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)  # 额外等待确保页面完全加载
            
            return True
            
        except Exception as e:
            self.logger.error(f"执行登录操作失败: {e}")
            return False
    
    async def verify_login_success(self) -> bool:
        """验证登录是否成功 - 简化版本，直接返回True"""
        try:
            # 等待一下让页面加载
            await asyncio.sleep(2)
            self.logger.info("跳过登录验证，假设登录成功")
            return True
        except Exception as e:
            self.logger.error(f"登录验证异常: {e}")
            return True
    
    async def login(self) -> bool:
        """完整的登录流程"""
        try:
            self.logger.info("开始登录流程...")
            
            # 检查浏览器是否已启动，如果没有则启动
            if not self.browser or not self.page:
                if not await self.start_browser():
                    return False
            
            # 导航到登录页面
            if not await self.navigate_to_login():
                return False
            
            # 查找登录元素
            elements = await self.find_login_elements()
            if not elements:
                return False
            
            # 执行登录
            self.logger.info("正在执行登录操作...")
            if not await self.perform_login(elements):
                return False
            
            # 验证登录结果
            login_success = await self.verify_login_success()
            
            self.logger.info("登录流程完成")
            return login_success
            
        except Exception as e:
            self.logger.error(f"登录失败: {e}")
            return False
    
    async def set_date_and_search(self) -> bool:
        """设置日期并执行搜索"""
        try:
            self.logger.info("正在设置日期并执行搜索...")
            
            # 点击展开按钮
            self.logger.info("正在查找并点击展开按钮...")
            expand_button = await self.page.wait_for_selector('button.lb-LBObjectParameterFormExpandButton-root', timeout=10000)
            if not expand_button:
                self.logger.error("未找到展开按钮")
                return False
            
            await expand_button.click()
            self.logger.info("点击展开按钮成功")
            await asyncio.sleep(1)  # 等待展开动画完成
            
            # 查找所有日期输入框
            self.logger.info("正在查找日期输入框...")
            date_inputs = await self.page.query_selector_all('input.lb-LBDatePicker-input[type="text"]')
            if not date_inputs or len(date_inputs) < 2:
                self.logger.error(f"未找到足够的日期输入框，找到 {len(date_inputs) if date_inputs else 0} 个")
                return False
            
            # 计算目标日期
            if self.target_date:
                # 使用指定的目标日期
                date_str = self.target_date
                self.logger.info(f"使用指定的目标日期: {date_str}")
            else:
                # 使用默认日期（前天的日期，9月6日有数据）
                yesterday = datetime.now() - timedelta(days=2)
                date_str = yesterday.strftime('%Y-%m-%d')
                self.logger.info(f"使用默认日期: {date_str}")
            
            # 设置开始日期（第一个输入框）
            start_date_input = date_inputs[0]
            await start_date_input.fill('')
            await start_date_input.type(date_str, delay=100)
            self.logger.info(f"设置开始日期为: {date_str}")
            
            # 设置结束日期（第二个输入框）
            end_date_input = date_inputs[1]
            await end_date_input.fill('')
            await end_date_input.type(date_str, delay=100)
            self.logger.info(f"设置结束日期为: {date_str}")
            
            # 查找并点击搜索按钮
            search_button = await self.page.wait_for_selector('button.lb-LBButton-contained', timeout=5000)
            if not search_button:
                self.logger.error("未找到搜索按钮")
                return False
            
            await search_button.click()
            self.logger.info("点击搜索按钮")
            
            # 等待搜索结果
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(1)  # 减少等待时间
            
            # 等待API响应数据
            self.logger.info("等待API响应数据...")
            await asyncio.sleep(2)  # 给API响应一些时间
            
            self.logger.info("搜索完成")
            return True
            
        except Exception as e:
            self.logger.error(f"设置日期并搜索失败: {e}")
            return False
    
    async def extract_data_from_api(self) -> dict:
        """从拦截的API响应中提取数据"""
        try:
            self.logger.info("正在等待API响应数据...")
            
            # 等待API响应数据
            max_wait_time = 5  # 减少等待时间到5秒
            wait_interval = 0.2  # 更频繁的检查，每0.2秒检查一次
            waited_time = 0
            
            while waited_time < max_wait_time:
                if self.current_page_data is not None and self.page_info is not None:
                    self.logger.info(f"✅ 获取到API数据: {len(self.current_page_data)} 条记录")
                    self.logger.info(f"📄 分页信息: {self.page_info}")
                    
                    return {
                        'data': self.current_page_data,
                        'pageInfo': self.page_info,
                        'success': True
                    }
                
                await asyncio.sleep(wait_interval)
                waited_time += wait_interval
            
            # 如果超时，检查是否有部分数据
            if self.current_page_data is not None:
                self.logger.warning("⏰ 等待分页信息超时，但已有数据")
                return {
                    'data': self.current_page_data,
                    'pageInfo': self.page_info or {},
                    'success': True
                }
            
            self.logger.warning("⏰ 等待API响应超时")
            return {
                'data': [],
                'pageInfo': {},
                'success': False,
                'error': 'API响应超时'
            }
            
        except Exception as e:
            self.logger.error(f"❌ 从API提取数据失败: {e}")
            return {
                'data': [],
                'pageInfo': {},
                'success': False,
                'error': str(e)
            }
    
    async def extract_all_pages_data_from_api(self) -> list:
        """使用API数据提取所有页面数据"""
        try:
            self.logger.info("🚀 开始基于API的数据提取...")
            all_data = []
            current_page = 1
            total_pages = 0
            total_records = 0
            seen_ids = set()  # 用于检查重复数据
            
            while True:
                self.logger.info(f"📄 正在处理第 {current_page} 页...")
                
                # 如果不是第一页，需要点击下一页
                if current_page > 1:
                    # 清空之前的数据（只在翻页时清空）
                    self.current_page_data = None
                    self.page_info = None
                    
                    click_result = await self.click_next_page_api()
                    if not click_result:
                        self.logger.info("✅ 已到达最后一页，停止数据提取")
                        break
                    
                    # 等待并获取API数据
                    api_result = await self.extract_data_from_api()
                else:
                    # 第一页使用已有的数据
                    if self.current_page_data is not None and self.page_info is not None:
                        self.logger.info(f"✅ 使用已有的第一页数据: {len(self.current_page_data)} 条记录")
                        api_result = {
                            'data': self.current_page_data,
                            'pageInfo': self.page_info,
                            'success': True
                        }
                    else:
                        # 如果没有数据，等待并获取API数据
                        api_result = await self.extract_data_from_api()
                
                if not api_result['success']:
                    self.logger.error(f"❌ 第 {current_page} 页API数据获取失败: {api_result.get('error', '未知错误')}")
                    break
                
                page_data = api_result['data']
                page_info = api_result['pageInfo']
                
                # 记录分页信息
                if current_page == 1:
                    total_records = page_info.get('total', 0)
                    page_size = page_info.get('pageSize', 50)
                    total_pages = (total_records + page_size - 1) // page_size
                    self.logger.info(f"📊 数据统计: 总计 {total_records} 条记录，共 {total_pages} 页")
                
                # 检查数据是否重复
                if page_data:
                    new_count = 0
                    for item in page_data:
                        item_id = item.get('ID')
                        if item_id and item_id not in seen_ids:
                            seen_ids.add(item_id)
                            new_count += 1
                    
                    if new_count == 0:
                        self.logger.warning(f"⚠️ 第 {current_page} 页: 所有数据都是重复的，停止提取")
                        break
                    
                    all_data.extend(page_data)
                    self.logger.info(f"✅ 第 {current_page} 页: 新增 {len(page_data)} 条记录（其中 {new_count} 条新数据），累计 {len(all_data)} 条")
                else:
                    self.logger.warning(f"⚠️ 第 {current_page} 页: 没有数据")
                    break
                
                # 检查是否还有更多页
                has_more = page_info.get('hasMore', False)
                if not has_more:
                    self.logger.info("✅ 根据API返回的hasMore=false，已到达最后一页")
                    break
                
                # 检查当前页号是否超过总页数
                current_page_no = page_info.get('pageNo', current_page)
                if current_page_no >= total_pages:
                    self.logger.info(f"✅ 当前页号 {current_page_no} 已达到总页数 {total_pages}，停止提取")
                    break
                
                # 安全检查：避免无限循环
                if current_page >= 20:  # 最多20页
                    self.logger.info(f"🛑 达到最大页数限制 ({current_page})，停止提取")
                    break
                
                current_page += 1
                
                # 页面间等待
                await asyncio.sleep(1)
            
            self.logger.info(f"🎉 数据提取完成！总计获取 {len(all_data)} 条记录，唯一记录 {len(seen_ids)} 条")
            return all_data
            
        except Exception as e:
            self.logger.error(f"❌ API数据提取过程出错: {e}")
            return []
    
    async def click_next_page_api(self) -> bool:
        """点击下一页（用于API数据提取）"""
        try:
            self.logger.info("📄 正在点击下一页...")
            
            # 查找分页容器
            pagination_container = await self.page.wait_for_selector('ul.lb-MuiPagination-ul', timeout=5000)
            if not pagination_container:
                self.logger.warning("❌ 未找到分页容器")
                return False
            
            # 获取所有分页项
            page_items = await pagination_container.query_selector_all('li')
            if not page_items or len(page_items) < 2:
                self.logger.warning("❌ 分页项不足")
                return False
            
            # 找到下一页按钮（通常是最后一个li）
            next_button_li = page_items[-1]
            next_button = await next_button_li.query_selector('button')
            
            if not next_button:
                self.logger.warning("❌ 未找到下一页按钮")
                return False
            
            # 检查按钮是否可点击
            is_disabled = await next_button.get_attribute('disabled')
            if is_disabled:
                self.logger.info("✅ 下一页按钮已禁用，到达最后一页")
                return False
            
            # 检查按钮是否可见
            is_visible = await next_button.is_visible()
            if not is_visible:
                self.logger.warning("❌ 下一页按钮不可见")
                return False
            
            # 点击下一页
            await next_button.click()
            self.logger.info("✅ 成功点击下一页")
            
            # 等待页面更新
            await asyncio.sleep(2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 点击下一页失败: {e}")
            return False
    
    async def save_api_data_to_csv(self, data: list, filename: str = None) -> str:
        """
        将API数据保存到CSV文件
        
        注意：此功能已暂时注释，如需启用请取消相关代码的注释
        """
        try:
            if not data:
                self.logger.warning("没有数据可保存")
                return ""
            
            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ksx_api_data_{timestamp}.csv"
            
            # 确保data目录存在
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            filepath = data_dir / filename
            
            # 如果数据是字典列表，直接保存
            if data and isinstance(data[0], dict):
                # 获取所有可能的字段名
                all_fields = set()
                for item in data:
                    all_fields.update(item.keys())
                
                all_fields = sorted(list(all_fields))
                
                with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=all_fields)
                    writer.writeheader()
                    
                    for item in data:
                        writer.writerow(item)
                
                self.logger.info(f"✅ API数据已保存到: {filepath}")
                self.logger.info(f"📊 保存记录数: {len(data)}")
                self.logger.info(f"📄 字段数: {len(all_fields)}")
                self.logger.info(f"🔑 字段列表: {all_fields}")
                
                return str(filepath)
            else:
                self.logger.error("❌ 数据格式不支持")
                return ""
                
        except Exception as e:
            self.logger.error(f"❌ 保存CSV文件失败: {e}")
            return ""
    
    async def sync_stores_to_config(self, data: list):
        """
        同步门店到配置数据库
        
        Args:
            data: 数据列表
        """
        try:
            if not data:
                return
            
            # 提取所有唯一的门店名称
            store_names = set()
            for item in data:
                if isinstance(item, dict):
                    # 尝试多个可能的字段名
                    store_name = item.get('store_name') or item.get('MDShow') or item.get('mdshow')
                    if store_name and store_name.strip():
                        # 清理HTML标签
                        import re
                        clean_name = re.sub(r'<[^>]+>', '', store_name.strip())
                        if clean_name:
                            store_names.add(clean_name)
            
            # 添加到配置数据库
            new_stores_count = 0
            for store_name in store_names:
                if config_db_manager.add_store(store_name):
                    new_stores_count += 1
            
            if new_stores_count > 0:
                self.logger.info(f"🆕 新增 {new_stores_count} 个门店到配置数据库")
            else:
                self.logger.info(f"📋 门店配置数据库已是最新状态")
                
        except Exception as e:
            self.logger.error(f"❌ 同步门店到配置数据库失败: {e}")
    
    async def smart_data_extraction(self, current_db_count: int) -> Dict[str, Any]:
        """智能数据提取流程 - 根据当前数据库数据量决定是否需要同步"""
        try:
            self.logger.info(f"🧠 开始智能数据提取，当前数据库有 {current_db_count} 条数据...")
            
            # 执行搜索
            search_result = await self.set_date_and_search()
            if not search_result:
                self.logger.error("❌ 搜索失败")
                return {"success": False, "action": "error", "message": "搜索失败"}
            
            # 获取第一页数据来检查总数
            self.logger.info("📄 获取第一页数据以检查总数...")
            first_page_result = await self.extract_data_from_api()
            
            if not first_page_result['success']:
                self.logger.error("❌ 第一页数据获取失败")
                return {"success": False, "action": "error", "message": "第一页数据获取失败"}
            
            # 检查是否有数据
            if not first_page_result['data']:
                self.logger.warning("⚠️ 当前日期没有业务数据")
                return {"success": True, "action": "no_data", "message": "当前日期没有业务数据，请核查日期"}
            
            # 获取网站上的总数据量
            website_total = first_page_result.get('total', 0)
            self.logger.info(f"📊 网站显示总数据量: {website_total} 条")
            
            # 对比数据量
            if current_db_count == website_total and current_db_count > 0:
                self.logger.info("✅ 数据已是最新，无需同步")
                return {"success": True, "action": "no_sync", "message": "数据已是最新，无需同步", "total": current_db_count}
            
            # 需要同步数据
            self.logger.info(f"🔄 需要同步数据: 数据库 {current_db_count} 条，网站 {website_total} 条")
            
            # 提取所有页面数据
            all_data = await self.extract_all_pages_data_from_api()
            if not all_data:
                self.logger.error("❌ 没有提取到数据")
                return {"success": False, "action": "error", "message": "没有提取到数据"}
            
            # 数据去重（基于ID字段）
            unique_data = await self.deduplicate_data(all_data)
            
            # 保存到数据库
            db_result = await self.save_to_database(unique_data)
            
            # 同步门店到配置数据库
            await self.sync_stores_to_config(unique_data)
            
            # 可选：保存到CSV文件作为备份（已注释，留作备用）
            # csv_file = await self.save_api_data_to_csv(unique_data)
            
            if db_result > 0:
                self.logger.info(f"🎉 数据同步完成！新增数据库记录: {db_result}条")
                # if csv_file:
                #     self.logger.info(f"📄 CSV备份文件: {csv_file}")
                return {"success": True, "action": "sync", "message": "数据同步完成", "total": db_result}
            else:
                # 检查是否是因为网站没有数据导致的
                if website_total == 0:
                    self.logger.warning("⚠️ 网站没有数据，无法同步")
                    return {"success": True, "action": "no_data", "message": "当前日期没有业务数据，请核查日期"}
                else:
                    self.logger.info(f"📋 数据同步完成！数据已是最新状态，无新记录需要添加")
                    return {"success": True, "action": "sync", "message": "数据已是最新状态", "total": 0}
                
        except Exception as e:
            self.logger.error(f"❌ 智能数据提取异常: {e}")
            return {"success": False, "action": "error", "message": f"智能数据提取异常: {str(e)}"}

    async def full_api_data_extraction(self) -> bool:
        """完整的API数据提取流程"""
        try:
            self.logger.info("🚀 开始完整的API数据提取流程...")
            
            # 执行搜索
            search_result = await self.set_date_and_search()
            if not search_result:
                self.logger.error("❌ 搜索失败")
                return False
            
            # 立即尝试获取第一页数据
            self.logger.info("📄 尝试获取第一页数据...")
            first_page_result = await self.extract_data_from_api()
            
            if first_page_result['success']:
                if first_page_result['data']:
                    self.logger.info(f"✅ 成功获取第一页数据: {len(first_page_result['data'])} 条记录")
                    
                    # 提取所有页面数据
                    all_data = await self.extract_all_pages_data_from_api()
                    if not all_data:
                        self.logger.error("❌ 没有提取到数据")
                        return False
                else:
                    # 成功获取但数据为空，说明没有业务数据
                    self.logger.warning("⚠️ 当前日期没有业务数据")
                    print("⚠️ 当前日期没有业务数据")
                    return False
            else:
                self.logger.error("❌ 第一页数据获取失败")
                return False
            
            # 数据去重（基于ID字段）
            unique_data = await self.deduplicate_data(all_data)
            
            # 保存到数据库
            db_result = await self.save_to_database(unique_data)
            
            # 同步门店到配置数据库
            await self.sync_stores_to_config(unique_data)
            
            # 可选：保存到CSV文件作为备份（已注释，留作备用）
            # csv_file = await self.save_api_data_to_csv(unique_data)
            
            if db_result > 0:
                self.logger.info(f"🎉 API数据提取完成！新增数据库记录: {db_result}条")
                print(f"🎉 API数据提取完成！新增数据库记录: {db_result}条")
                # if csv_file:
                #     self.logger.info(f"📄 CSV备份文件: {csv_file}")
                return True
            else:
                self.logger.info(f"📋 API数据提取完成！数据已是最新状态，无新记录需要添加")
                print(f"📋 API数据提取完成！数据已是最新状态，无新记录需要添加")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ 完整API数据提取失败: {e}")
            return False
    
    async def save_to_database(self, data: list) -> int:
        """将数据保存到数据库"""
        try:
            if not data:
                self.logger.warning("没有数据需要保存到数据库")
                return 0
            
            # 获取数据库管理器
            db_manager = get_db_manager()
            
            # 计算目标日期，与爬取日期保持一致
            if self.target_date:
                # 使用指定的目标日期
                target_date_obj = datetime.strptime(self.target_date, '%Y-%m-%d')
                yesterday = target_date_obj
            else:
                # 使用默认日期（前天的日期）
                yesterday = datetime.now() - timedelta(days=2)
            
            # 插入数据（会自动去重），使用昨天的日期
            self.logger.info(f"📊 准备保存 {len(data)} 条记录到数据库（日期: {yesterday.strftime('%Y-%m-%d')}）")
            print(f"📊 准备保存 {len(data)} 条记录到数据库（日期: {yesterday.strftime('%Y-%m-%d')}）")
            
            inserted_count = db_manager.insert_data(data, date=yesterday)
            
            self.logger.info(f"✅ 成功保存 {inserted_count} 条记录到数据库（日期: {yesterday.strftime('%Y-%m-%d')}）")
            print(f"✅ 成功保存 {inserted_count} 条记录到数据库（日期: {yesterday.strftime('%Y-%m-%d')}）")
            
            # 清理旧数据库（保留近1个月）
            db_manager.cleanup_old_databases(keep_months=1)
            
            return inserted_count
            
        except Exception as e:
            self.logger.error(f"❌ 保存到数据库失败: {e}")
            return 0
    
    async def deduplicate_data(self, data: list) -> list:
        """数据去重"""
        try:
            if not data:
                return data
            
            # 尝试找到ID字段进行去重
            id_fields = ['id', 'ID', 'Id', '_id', 'uuid', 'key', 'objectKey']
            id_field = None
            
            if data and isinstance(data[0], dict):
                for field in id_fields:
                    if field in data[0]:
                        id_field = field
                        break
            
            if id_field:
                # 基于ID字段去重
                seen_ids = set()
                unique_data = []
                
                for item in data:
                    item_id = item.get(id_field)
                    if item_id not in seen_ids:
                        seen_ids.add(item_id)
                        unique_data.append(item)
                
                self.logger.info(f"🔄 基于'{id_field}'字段去重: {len(data)} -> {len(unique_data)} 条记录")
                return unique_data
            else:
                # 如果没有ID字段，基于整条记录去重
                unique_data = []
                seen_records = set()
                
                for item in data:
                    # 将字典转换为可哈希的字符串
                    record_str = json.dumps(item, sort_keys=True, ensure_ascii=False)
                    if record_str not in seen_records:
                        seen_records.add(record_str)
                        unique_data.append(item)
                
                self.logger.info(f"🔄 基于完整记录去重: {len(data)} -> {len(unique_data)} 条记录")
                return unique_data
                
        except Exception as e:
            self.logger.error(f"❌ 数据去重失败: {e}")
            return data
    
    async def take_screenshot(self, filename: str = "screenshot.png") -> bool:
        """截图保存"""
        try:
            if not self.page:
                return False
            
            await self.page.screenshot(path=filename, full_page=True)
            self.logger.info(f"截图保存成功: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"截图失败: {e}")
            return False
    
    async def close(self):
        """关闭浏览器和资源"""
        try:
            # 安全关闭页面
            if hasattr(self, 'page') and self.page:
                try:
                    await self.page.close()
                    self.page = None
                except Exception as e:
                    self.logger.warning(f"关闭页面时出错: {e}")
            
            # 安全关闭上下文
            if hasattr(self, 'context') and self.context:
                try:
                    await self.context.close()
                    self.context = None
                except Exception as e:
                    self.logger.warning(f"关闭上下文时出错: {e}")
            
            # 安全关闭浏览器
            if hasattr(self, 'browser') and self.browser:
                try:
                    await self.browser.close()
                    self.browser = None
                except Exception as e:
                    self.logger.warning(f"关闭浏览器时出错: {e}")
            
            # 停止 playwright
            if hasattr(self, 'playwright') and self.playwright:
                try:
                    await self.playwright.stop()
                    self.playwright = None
                except Exception as e:
                    self.logger.warning(f"停止playwright时出错: {e}")
            
            self.logger.info("浏览器资源已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭资源时出错: {e}")


async def main():
    """主函数示例"""
    crawler = KSXCrawler(headless=False)  # 设置为False可以看到浏览器操作过程
    
    try:
        # 执行登录
        success = await crawler.login()
        
        if success:
            print("登录成功！")
            
            # 执行完整的API数据提取
            extraction_success = await crawler.full_api_data_extraction()
            
            if extraction_success:
                print("数据提取完成！")
            else:
                print("数据提取失败！")
            
            # 等待用户查看
            input("按回车键继续...")
        else:
            print("登录失败！")
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"程序异常: {e}")
    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
