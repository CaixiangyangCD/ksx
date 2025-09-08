import sys
import os
import subprocess
import time
import socket
import signal
import atexit
from http.server import HTTPServer, SimpleHTTPRequestHandler
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QFrame, QPushButton, QMessageBox, QProgressDialog
from PySide6.QtCore import Qt, QUrl, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings


# PyInstaller支持
def get_project_root():
    """获取项目根目录，支持PyInstaller打包"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的情况
        return sys._MEIPASS
    else:
        # 开发环境
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class StartupCheckThread(QThread):
    """启动检查线程"""
    check_progress = Signal(str)  # 发送检查进度
    check_completed = Signal(bool)  # 发送检查结果
    
    def __init__(self):
        super().__init__()
        self.project_root = get_project_root()
    
    def run(self):
        """执行启动检查"""
        try:
            # 在打包后的应用中，跳过复杂的启动检查
            if getattr(sys, 'frozen', False):
                self.check_progress.emit("运行在打包环境中，跳过启动检查...")
                self.check_progress.emit("设置环境变量...")
                self.setup_environment()
                self.check_progress.emit("启动检查完成")
                self.check_completed.emit(True)
                return
            
            # 开发环境中的完整检查
            self.check_progress.emit("检查Python环境...")
            if not self.check_python_environment():
                self.check_completed.emit(False)
                return
            
            self.check_progress.emit("检查Playwright...")
            if not self.check_and_install_playwright():
                self.check_completed.emit(False)
                return
            
            self.check_progress.emit("检查浏览器...")
            if not self.check_and_install_browsers():
                self.check_completed.emit(False)
                return
            
            self.check_progress.emit("设置环境变量...")
            self.setup_environment()
            
            self.check_progress.emit("启动检查完成")
            self.check_completed.emit(True)
            
        except Exception as e:
            self.check_progress.emit(f"启动检查失败: {str(e)}")
            self.check_completed.emit(False)
    
    def check_python_environment(self):
        """检查Python环境"""
        python_version = sys.version_info
        return python_version >= (3, 8)
    
    def check_and_install_playwright(self):
        """检查并安装Playwright"""
        try:
            import playwright
            return True
        except ImportError:
            try:
                result = subprocess.run([
                    sys.executable, "-m", "uv", "add", "playwright"
                ], capture_output=True, text=True, cwd=self.project_root)
                return result.returncode == 0
            except:
                return False
    
    def check_and_install_browsers(self):
        """检查并安装浏览器"""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                try:
                    browser = p.chromium.launch(headless=True)
                    browser.close()
                    return True
                except:
                    result = subprocess.run([
                        sys.executable, "-m", "playwright", "install", "chromium"
                    ], capture_output=True, text=True, cwd=self.project_root)
                    return result.returncode == 0
        except:
            return False
    
    def setup_environment(self):
        """设置环境变量"""
        if getattr(sys, 'frozen', False):
            # 打包后的应用，使用应用内部目录
            app_dir = os.path.dirname(sys.executable)
            browser_path = os.path.join(app_dir, "playwright-browsers")
            
            # 检查并安装Playwright浏览器
            self.install_playwright_browsers(browser_path)
        else:
            # 开发环境
            browser_path = os.path.join(self.project_root, "playwright-browsers")
        
        os.makedirs(browser_path, exist_ok=True)
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browser_path
        print(f"设置Playwright浏览器路径: {browser_path}")
    
    def install_playwright_browsers(self, browser_path):
        """安装Playwright浏览器"""
        try:
            # 检查是否已经安装了浏览器
            chromium_path = os.path.join(browser_path, "chromium-1091", "chrome-mac", "Chromium.app")
            if os.path.exists(chromium_path):
                print("Playwright浏览器已存在，跳过安装")
                return
            
            print("正在安装Playwright浏览器...")
            import subprocess
            
            # 设置环境变量
            env = os.environ.copy()
            env["PLAYWRIGHT_BROWSERS_PATH"] = browser_path
            
            # 安装Chromium浏览器
            result = subprocess.run([
                sys.executable, "-m", "playwright", "install", "chromium"
            ], env=env, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("Playwright浏览器安装成功")
            else:
                print(f"Playwright浏览器安装失败: {result.stderr}")
                
        except Exception as e:
            print(f"安装Playwright浏览器时出错: {e}")


class FastAPIThread(QThread):
    """后端服务器线程"""
    api_started = Signal(int)  # 发送端口号
    api_error = Signal(str)    # 发送错误信息
    
    def __init__(self):
        super().__init__()
        self.api_process = None
        self.api_port = 18888  # 默认使用18888端口
        self.port_range = [18888, 18889, 18890, 18891, 18892]  # 备用端口列表
        
    def run(self):
        try:
            # 尝试找到可用端口
            available_port = self.find_available_port()
            if available_port is None:
                self.api_error.emit("无法找到可用端口，请检查端口占用情况")
                return
            
            self.api_port = available_port
            
            # 启动后端服务
            self.start_fastapi_server()
            
        except Exception as e:
            self.api_error.emit(str(e))
    
    def is_port_in_use(self, port):
        """检查端口是否被占用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('127.0.0.1', port))
                return result == 0
        except:
            return False
    
    def cleanup_port(self, port):
        """清理指定端口的占用"""
        try:
            current_pid = os.getpid()
            print(f"正在清理端口 {port} 的占用... (当前进程PID: {current_pid})")
            
            # 使用lsof查找占用端口的进程
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid.strip() and pid.strip() != str(current_pid):
                        try:
                            print(f"强制杀死进程 {pid} (占用端口 {port})")
                            subprocess.run(['kill', '-9', pid], timeout=3)
                        except Exception as e:
                            print(f"杀死进程 {pid} 失败: {e}")
                            return False
                
                # 等待端口释放
                time.sleep(1)
                
                # 再次检查端口是否已释放
                if not self.is_port_in_use(port):
                    print(f"端口 {port} 已成功释放")
                    return True
                else:
                    print(f"端口 {port} 仍然被占用")
                    return False
            else:
                print(f"端口 {port} 未被占用")
                return True
                
        except Exception as e:
            print(f"清理端口 {port} 失败: {e}")
            return False
    
    def find_available_port(self):
        """查找可用端口"""
        for port in self.port_range:
            if not self.is_port_in_use(port):
                print(f"找到可用端口: {port}")
                return port
            else:
                print(f"端口 {port} 被占用，尝试清理...")
                if self.cleanup_port(port):
                    print(f"端口 {port} 清理成功")
                    return port
                else:
                    print(f"端口 {port} 清理失败，尝试下一个端口")
        
        return None
    
    def start_fastapi_server(self):
        """启动后端服务器"""
        try:
            # 获取项目根目录（desktop目录的父目录）
            project_root = get_project_root()
            
            if getattr(sys, 'frozen', False):
                # 打包后的应用，使用内置的FastAPI服务器
                self.start_internal_server()
            else:
                # 开发环境，使用uv运行
                self.api_process = subprocess.Popen(
                    ['uv', 'run', 'python', 'backend/app.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=project_root
                )
                
                # 等待服务启动
                time.sleep(3)
                
                # 检查服务是否启动成功
                if self.api_process.poll() is None:
                    self.api_started.emit(self.api_port)
                else:
                    stdout, stderr = self.api_process.communicate()
                    self.api_error.emit(f"后端启动失败: {stderr}")
                
        except Exception as e:
            self.api_error.emit(f"启动后端失败: {str(e)}")
    
    def start_internal_server(self):
        """启动内置的FastAPI服务器（用于打包后的应用）"""
        try:
            import uvicorn
            from backend.app import app
            
            # 在单独的线程中启动服务器
            def run_server():
                uvicorn.run(app, host="127.0.0.1", port=self.api_port, log_level="warning")
            
            import threading
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # 等待服务启动
            time.sleep(2)
            self.api_started.emit(self.api_port)
            
        except Exception as e:
            self.api_error.emit(f"启动内置服务器失败: {str(e)}")
    
    def stop_api_server(self):
        """停止后端服务器"""
        if self.api_process and self.api_process.poll() is None:
            try:
                print("正在停止后端服务...")
                # 发送终止信号
                self.api_process.terminate()
                # 等待进程结束
                self.api_process.wait(timeout=3)
                print("后端服务已正常停止")
            except subprocess.TimeoutExpired:
                print("后端服务未响应终止信号，强制杀死...")
                # 如果进程没有正常结束，强制杀死
                self.api_process.kill()
                self.api_process.wait()
                print("后端服务已强制停止")
            except Exception as e:
                print(f"停止后端服务时出错: {e}")
                # 尝试强制杀死
                try:
                    self.api_process.kill()
                    self.api_process.wait()
                except:
                    pass


class LocalServerThread(QThread):
    """本地HTTP服务器线程（用于前端静态文件）"""
    server_started = Signal(int)  # 发送端口号
    server_error = Signal(str)    # 发送错误信息
    
    def __init__(self, dist_path):
        super().__init__()
        self.dist_path = dist_path
        self.server = None
        self.port = None
        
    def run(self):
        try:
            # 查找可用端口
            self.port = self.find_free_port()
            
            # 切换到dist目录
            os.chdir(self.dist_path)
            
            # 创建HTTP服务器
            self.server = HTTPServer(('localhost', self.port), SimpleHTTPRequestHandler)
            
            # 发送成功信号
            self.server_started.emit(self.port)
            
            # 启动服务器
            self.server.serve_forever()
            
        except Exception as e:
            self.server_error.emit(str(e))
    
    def find_free_port(self):
        """查找可用端口"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def stop_server(self):
        """停止服务器"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()


class KSXDesktopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.web_view = None
        self.server_thread = None
        self.api_thread = None
        self.server_port = None
        self.api_port = 18888
        self.startup_check_thread = None
        self.progress_dialog = None
        self.init_ui()
        
        # 执行启动检查
        self.perform_startup_check()
    
    def perform_startup_check(self):
        """执行启动检查"""
        # 简化启动检查，直接启动服务
        print("跳过复杂的启动检查，直接启动服务...")
        
        # 检查Playwright环境
        self.check_playwright_environment()
        
        # 简单清理端口
        self.cleanup_startup_ports()
        
        # 直接启动后端和前端服务
        self.start_fastapi_server()
        project_root = get_project_root()
        dist_path = os.path.join(project_root, 'frontend', 'dist')
        self.start_frontend_server(dist_path)
    
    def check_playwright_environment(self):
        """检查Playwright环境"""
        try:
            print("🔍 检查Playwright环境...")
            
            # 尝试导入Playwright
            try:
                import playwright
                print("✓ Playwright模块已安装")
            except ImportError:
                print("⚠️ Playwright模块未安装，将在需要时自动安装")
                return
            
            # 设置浏览器路径
            project_root = get_project_root()
            browser_path = os.path.join(project_root, "playwright-browsers")
            os.makedirs(browser_path, exist_ok=True)
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browser_path
            
            # 检查浏览器是否已安装
            chromium_path = os.path.join(browser_path, "chromium-1091", "chrome-mac", "Chromium.app")
            if not os.path.exists(chromium_path):
                print("⚠️ Playwright浏览器未安装，将在首次使用时自动安装")
            else:
                print("✓ Playwright浏览器已安装")
                
        except Exception as e:
            print(f"⚠️ Playwright环境检查失败: {e}")
            print("将在首次使用时自动处理")
    
    def cleanup_startup_ports(self):
        """启动时清理可能被占用的端口"""
        try:
            print("正在清理启动时的端口占用...")
            
            # 只清理必要的端口，避免过度清理
            ports_to_check = [18888, 18889, 18890, 18891, 18892]
            for port in ports_to_check:
                if self.is_port_in_use(port):
                    print(f"检测到端口 {port} 被占用，尝试清理...")
                    self.cleanup_single_port(port)
                    
            print("启动端口清理完成")
        except Exception as e:
            print(f"启动端口清理失败: {e}")
    
    def cleanup_single_port(self, port):
        """清理单个端口"""
        try:
            current_pid = os.getpid()
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid.strip() and pid.strip() != str(current_pid):
                        try:
                            print(f"清理端口 {port} 的进程 {pid}")
                            subprocess.run(['kill', '-9', pid], timeout=2)
                        except Exception as e:
                            print(f"清理进程 {pid} 失败: {e}")
        except Exception as e:
            print(f"清理端口 {port} 失败: {e}")
    
    def is_port_in_use(self, port):
        """检查端口是否被占用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('127.0.0.1', port))
                return result == 0
        except:
            return False
    
    def on_check_progress(self, message):
        """更新检查进度（已弃用，保留兼容性）"""
        # 这个方法已经不再使用，因为启动检查已经简化
        print(f"检查进度: {message}")
    
    def on_check_completed(self, success):
        """检查完成回调（已弃用，保留兼容性）"""
        # 这个方法已经不再使用，因为启动检查已经简化
        pass
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("KSX门店管理系统")
        self.setGeometry(100, 100, 1400, 900)
        
        # 不设置应用图标，保持简洁
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建顶部工具栏
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # 创建Web视图
        self.web_view = QWebEngineView()
        
        # 配置Web引擎设置
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptEnabled, True
        )
        
        # 禁用右键菜单
        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        
        main_layout.addWidget(self.web_view)
        
        # 创建状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("准备就绪")
        
        # 加载应用
        self.load_application()
        
    def create_toolbar(self):
        """创建顶部工具栏"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.StyledPanel)
        toolbar.setMaximumHeight(60)
        toolbar.setStyleSheet("""
            QFrame { 
                background-color: #ffffff;
                border-bottom: 1px solid #e8e8e8;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("KSX门店管理系统")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #262626; padding: 5px;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 后端状态标签
        self.api_status_label = QLabel("后端: 未启动")
        self.api_status_label.setStyleSheet("""
            color: #ff4d4f; 
            font-weight: 500; 
            padding: 6px 12px;
            background-color: #fff2f0;
            border: 1px solid #ffccc7;
            border-radius: 4px;
            font-size: 13px;
        """)
        layout.addWidget(self.api_status_label)
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:pressed {
                background-color: #096dd9;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_page)
        layout.addWidget(refresh_btn)
        
        return toolbar
        
    def load_application(self):
        """加载应用"""
        try:
            # 检查dist文件夹是否存在
            # 获取项目根目录（desktop目录的父目录）
            project_root = get_project_root()
            dist_path = os.path.join(project_root, 'frontend', 'dist')
            index_path = os.path.join(dist_path, 'index.html')
            
            if os.path.exists(index_path):
                # 直接启动后端服务
                self.start_fastapi_server()
            else:
                # 如果不存在构建文件，显示错误信息
                self.show_build_error(dist_path, index_path)
                
        except Exception as e:
            self.show_load_error(str(e))
    
    def start_fastapi_server(self):
        """启动后端服务器"""
        try:
            self.status_bar.showMessage("正在启动后端服务...")
            self.api_status_label.setText("后端: 启动中...")
            self.api_status_label.setStyleSheet("""
                color: #faad14; 
                font-weight: 500; 
                padding: 6px 12px;
                background-color: #fffbe6;
                border: 1px solid #ffe58f;
                border-radius: 4px;
                font-size: 13px;
            """)
            
            # 创建后端服务器线程
            self.api_thread = FastAPIThread()
            self.api_thread.api_started.connect(self.on_api_started)
            self.api_thread.api_error.connect(self.on_api_error)
            
            # 启动后端服务器
            self.api_thread.start()
            
        except Exception as e:
            self.show_load_error(f"启动后端服务失败: {str(e)}")
    
    def start_frontend_server(self, dist_path):
        """启动桌面应用"""
        try:
            self.status_bar.showMessage("正在启动桌面应用...")
            
            # 创建桌面应用服务器线程
            self.server_thread = LocalServerThread(dist_path)
            self.server_thread.server_started.connect(self.on_frontend_started)
            self.server_thread.server_error.connect(self.on_frontend_error)
            
            # 启动桌面应用
            self.server_thread.start()
            
        except Exception as e:
            self.show_load_error(f"启动桌面应用失败: {str(e)}")
    
    def on_api_started(self, port):
        """后端服务器启动成功"""
        self.api_port = port
        self.api_status_label.setText(f"后端: 运行中 (端口 {port})")
        self.api_status_label.setStyleSheet("""
            color: #52c41a; 
            font-weight: 500; 
            padding: 6px 12px;
            background-color: #f6ffed;
            border: 1px solid #b7eb8f;
            border-radius: 4px;
            font-size: 13px;
        """)
        self.status_bar.showMessage("后端服务已启动")
        
        # 后端启动成功后，启动桌面应用
        # 获取项目根目录（desktop目录的父目录）
        project_root = get_project_root()
        dist_path = os.path.join(project_root, 'frontend', 'dist')
        self.start_frontend_server(dist_path)
    
    def on_api_error(self, error_msg):
        """后端服务器启动失败"""
        self.api_status_label.setText("后端: 启动失败")
        self.api_status_label.setStyleSheet("""
            color: #ff4d4f; 
            font-weight: 500; 
            padding: 6px 12px;
            background-color: #fff2f0;
            border: 1px solid #ffccc7;
            border-radius: 4px;
            font-size: 13px;
        """)
        self.show_load_error(f"后端服务启动失败: {error_msg}")
    
    def on_frontend_started(self, port):
        """桌面应用启动成功"""
        self.server_port = port
        
        # 加载应用
        app_url = f"http://localhost:{port}/"
        self.web_view.load(QUrl(app_url))
        self.status_bar.showMessage(f"应用已加载: {app_url}")
    
    def on_frontend_error(self, error_msg):
        """桌面应用启动失败"""
        self.show_load_error(f"桌面应用启动失败: {error_msg}")
    
    def show_build_error(self, dist_path, index_path):
        """显示构建错误"""
        self.web_view.setHtml(f"""
            <html>
            <head>
                <title>KSX门店管理系统</title>
                <style>
                    body {{ 
                        font-family: 'Microsoft YaHei', Arial, sans-serif; 
                        text-align: center; 
                        padding: 50px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }}
                    .container {{
                        background: rgba(255,255,255,0.1);
                        padding: 40px;
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                    }}
                    h1 {{ font-size: 2.5em; margin-bottom: 20px; }}
                    p {{ font-size: 1.2em; margin-bottom: 15px; }}
                    .error {{
                        background: rgba(255,0,0,0.2);
                        padding: 20px;
                        border-radius: 10px;
                        border: 2px solid rgba(255,0,0,0.5);
                    }}
                    .btn {{
                        background: #4CAF50;
                        color: white;
                        padding: 15px 30px;
                        border: none;
                        border-radius: 25px;
                        font-size: 1.1em;
                        cursor: pointer;
                        margin: 10px;
                        text-decoration: none;
                        display: inline-block;
                    }}
                    .btn:hover {{ background: #45a049; }}
                    .code {{
                        background: rgba(0,0,0,0.3);
                        padding: 10px;
                        border-radius: 5px;
                        font-family: monospace;
                        margin: 10px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>❌ 未找到构建文件</h1>
                    <div class="error">
                        <p><strong>请先构建Vue项目！</strong></p>
                        <p>在项目根目录运行:</p>
                        <div class="code">cd frontend && npm run build</div>
                    </div>
                    <p><strong>当前路径:</strong> {os.getcwd()}</p>
                    <p><strong>期望文件:</strong> {index_path}</p>
                    <br>
                    <a href="#" class="btn" onclick="window.location.reload()">🔄 重新加载</a>
                </div>
            </body>
            </html>
        """)
        self.status_bar.showMessage("错误: 未找到构建文件")
    
    def show_load_error(self, error_msg):
        """显示加载错误"""
        self.web_view.setHtml(f"""
            <html>
            <head>
                <title>KSX门店管理系统 - 加载错误</title>
                <style>
                    body {{ 
                        font-family: 'Microsoft YaHei', Arial, sans-serif; 
                        text-align: center; 
                        padding: 50px;
                        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                        color: white;
                    }}
                    .container {{
                        background: rgba(255,255,255,0.1);
                        padding: 40px;
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                    }}
                    h1 {{ font-size: 2.5em; margin-bottom: 20px; }}
                    p {{ font-size: 1.2em; margin-bottom: 15px; }}
                    .error {{
                        background: rgba(0,0,0,0.3);
                        padding: 10px;
                        border-radius: 5px;
                        font-family: monospace;
                        margin: 10px 0;
                        word-break: break-all;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>💥 加载异常</h1>
                    <p><strong>应用加载过程中出现错误:</strong></p>
                    <div class="error">{error_msg}</div>
                    <p>请检查构建文件或联系技术支持</p>
                </div>
            </body>
            </html>
        """)
        self.status_bar.showMessage(f"加载异常: {error_msg}")
            
    def refresh_page(self):
        """刷新页面"""
        if self.web_view and self.server_port:
            self.web_view.reload()
            self.status_bar.showMessage("页面已刷新")
        else:
            QMessageBox.warning(self, "警告", "桌面应用未启动，无法刷新页面")
    
    def stop_all_services(self):
        """停止所有服务"""
        print("开始停止所有服务...")
        
        # 停止桌面应用
        if self.server_thread and self.server_thread.isRunning():
            print("正在停止前端服务...")
            self.server_thread.stop_server()
            self.server_thread.quit()
            self.server_thread.wait(3000)
            print("前端服务已停止")
        
        # 停止后端服务
        if self.api_thread and self.api_thread.isRunning():
            print("正在停止后端服务...")
            self.api_thread.stop_api_server()
            self.api_thread.quit()
            self.api_thread.wait(3000)
            print("后端服务已停止")
        
        # 强制清理端口占用 - 简单粗暴的方法
        print("正在清理端口占用...")
        self.force_cleanup_ports()
        
        print("所有服务已停止")
    
    def force_cleanup_ports(self):
        """强制清理端口占用 - 简化版本"""
        try:
            current_pid = os.getpid()
            print(f"当前进程PID: {current_pid}")
            
            # 只清理必要的端口，避免过度清理
            ports_to_clean = [18888, 18889, 18890, 18891, 18892]
            
            for port in ports_to_clean:
                self.cleanup_single_port(port)
                            
            print("端口清理完成")
        except Exception as e:
            print(f"端口清理失败: {e}")
    
    def closeEvent(self, event):
        """关闭事件"""
        print("应用正在关闭...")
        # 停止所有服务
        self.stop_all_services()
        print("应用关闭完成")
        event.accept()


def check_dependencies():
    """检查依赖"""
    # 在打包后的应用中，所有依赖都已经包含，不需要检查外部工具
    if getattr(sys, 'frozen', False):
        # 打包后的应用，跳过依赖检查
        print("✓ 运行在打包环境中，跳过依赖检查")
        return True
    
    # 开发环境中的依赖检查
    try:
        import PySide6  # noqa: F401
        print("✓ PySide6已安装")
    except ImportError:
        print("✗ PySide6未安装，请运行: pip install PySide6")
        return False
        
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
        print("✓ QtWebEngine已安装")
    except ImportError:
        print("✗ QtWebEngine未安装，请运行: pip install PySide6-WebEngine")
        return False
        
    # 检查uv是否安装（仅在开发环境中）
    try:
        subprocess.run(['uv', '--version'], capture_output=True, check=True)
        print("✓ uv已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ uv未安装，请运行: pip install uv")
        return False
        
    return True


# 全局变量用于存储主窗口实例
main_window = None

def force_cleanup_ports_standalone():
    """独立的端口清理函数 - 简化版本"""
    try:
        current_pid = os.getpid()
        print(f"正在强制清理端口占用... (当前进程PID: {current_pid})")
        
        # 只清理必要的端口
        ports_to_clean = [18888, 18889, 18890, 18891, 18892]
        
        for port in ports_to_clean:
            try:
                result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid.strip() and pid.strip() != str(current_pid):
                            try:
                                print(f"清理端口 {port} 的进程 {pid}")
                                subprocess.run(['kill', '-9', pid], timeout=2)
                            except Exception as e:
                                print(f"清理进程 {pid} 失败: {e}")
            except Exception as e:
                print(f"清理端口 {port} 失败: {e}")
                        
        print("端口清理完成")
    except Exception as e:
        print(f"端口清理失败: {e}")

def cleanup_services():
    """清理服务函数"""
    global main_window
    if main_window:
        print("正在清理服务...")
        main_window.stop_all_services()
    else:
        # 如果主窗口不存在，直接清理端口
        print("主窗口不存在，直接清理端口...")
        force_cleanup_ports_standalone()

def signal_handler(signum, frame):
    """信号处理函数"""
    print(f"收到信号 {signum}，正在关闭应用...")
    cleanup_services()
    sys.exit(0)

def main():
    """主函数"""
    global main_window
    
    print("KSX门店管理系统 - 桌面版 (简化版)")
    print("=" * 60)
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 注册退出时清理函数
    atexit.register(cleanup_services)
    
    # 设置环境变量以避免图形问题
    os.environ["QT_MAC_WANTS_LAYER"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    # 检查依赖
    if not check_dependencies():
        print("\n请先安装必要的依赖包")
        input("按回车键退出...")
        return
        
    # 检查dist文件夹
    # 获取项目根目录（desktop目录的父目录）
    project_root = get_project_root()
    dist_path = os.path.join(project_root, 'frontend', 'dist')
    index_path = os.path.join(dist_path, 'index.html')
    
    if not os.path.exists(dist_path):
        print("✗ 未找到frontend/dist文件夹，请先构建Vue项目")
        print("运行命令: cd frontend && npm run build")
        input("按回车键退出...")
        return
        
    if not os.path.exists(index_path):
        print("✗ frontend/dist文件夹中未找到index.html文件")
        print("请确保Vue项目构建成功")
        input("按回车键退出...")
        return
    
    print("✓ 检测到构建文件")
    print("🚀 启动桌面应用...")
    
    # 创建Qt应用
    app = QApplication(sys.argv)
    app.setApplicationName("KSX门店管理系统")
    app.setApplicationVersion("1.0.0")
    
    # 创建主窗口
    main_window = KSXDesktopApp()
    main_window.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()