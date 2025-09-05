import sys
import os
import subprocess
import threading
import time
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QFrame, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QUrl, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings


class LocalServerThread(QThread):
    """本地HTTP服务器线程"""
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
        self.server_port = None
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("KSX门店管理系统")
        self.setGeometry(100, 100, 1400, 900)
        
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
        
        # 启用右键菜单
        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.web_view.customContextMenuRequested.connect(self.show_context_menu)
        
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
        toolbar.setStyleSheet("QFrame { background-color: #f0f2f5; border-radius: 8px; }")
        
        layout = QHBoxLayout(toolbar)
        
        # 标题
        title_label = QLabel("🚀 KSX门店管理系统")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #001529; padding: 10px;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 服务器状态标签
        self.server_status_label = QLabel("服务器: 未启动")
        self.server_status_label.setStyleSheet("color: #ff4d4f; font-weight: bold; padding: 8px;")
        layout.addWidget(self.server_status_label)
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_page)
        layout.addWidget(refresh_btn)
        
        # 开发者工具按钮
        dev_tools_btn = QPushButton("🔧 开发者工具")
        dev_tools_btn.setStyleSheet("""
            QPushButton {
                background-color: #52c41a;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #73d13d;
            }
        """)
        dev_tools_btn.clicked.connect(self.toggle_dev_tools)
        layout.addWidget(dev_tools_btn)
        
        # 打开文件夹按钮
        open_folder_btn = QPushButton("📁 打开文件夹")
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #722ed1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #9254de;
            }
        """)
        open_folder_btn.clicked.connect(self.open_build_folder)
        layout.addWidget(open_folder_btn)
        
        return toolbar
        
    def load_application(self):
        """加载应用"""
        try:
            # 检查dist文件夹是否存在
            dist_path = os.path.join(os.getcwd(), 'dist')
            index_path = os.path.join(dist_path, 'index.html')
            
            if os.path.exists(index_path):
                # 启动本地HTTP服务器
                self.start_local_server(dist_path)
            else:
                # 如果不存在构建文件，显示错误信息
                self.show_build_error(dist_path, index_path)
                
        except Exception as e:
            self.show_load_error(str(e))
    
    def start_local_server(self, dist_path):
        """启动本地HTTP服务器"""
        try:
            self.status_bar.showMessage("正在启动本地服务器...")
            self.server_status_label.setText("服务器: 启动中...")
            self.server_status_label.setStyleSheet("color: #faad14; font-weight: bold; padding: 8px;")
            
            # 创建服务器线程
            self.server_thread = LocalServerThread(dist_path)
            self.server_thread.server_started.connect(self.on_server_started)
            self.server_thread.server_error.connect(self.on_server_error)
            
            # 启动服务器
            self.server_thread.start()
            
        except Exception as e:
            self.show_load_error(f"启动服务器失败: {str(e)}")
    
    def on_server_started(self, port):
        """服务器启动成功"""
        self.server_port = port
        self.server_status_label.setText(f"服务器: 运行中 (端口 {port})")
        self.server_status_label.setStyleSheet("color: #52c41a; font-weight: bold; padding: 8px;")
        
        # 加载应用
        app_url = f"http://localhost:{port}/"
        self.web_view.load(QUrl(app_url))
        self.status_bar.showMessage(f"已加载应用: {app_url}")
    
    def on_server_error(self, error_msg):
        """服务器启动失败"""
        self.server_status_label.setText("服务器: 启动失败")
        self.server_status_label.setStyleSheet("color: #ff4d4f; font-weight: bold; padding: 8px;")
        self.show_load_error(f"服务器启动失败: {error_msg}")
    
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
                        <div class="code">npm run build</div>
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
            QMessageBox.warning(self, "警告", "服务器未启动，无法刷新页面")
            
    def toggle_dev_tools(self):
        """切换开发者工具"""
        if self.web_view:
            try:
                # 尝试使用WebInspector
                self.web_view.page().triggerAction(
                    self.web_view.page().WebAction.WebInspector
                )
            except AttributeError:
                try:
                    # 尝试使用InspectElement
                    self.web_view.page().triggerAction(
                        self.web_view.page().WebAction.InspectElement
                    )
                except AttributeError:
                    # 如果都不存在，显示提示信息
                    QMessageBox.information(
                        self, 
                        "开发者工具", 
                        "当前版本的PySide6不支持开发者工具功能。\n\n请使用右键菜单或F12键查看页面源码。"
                    )
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        from PySide6.QtWidgets import QMenu
        
        context_menu = QMenu(self)
        
        # 添加菜单项
        refresh_action = context_menu.addAction("🔄 刷新页面")
        reload_action = context_menu.addAction("🔄 重新加载")
        context_menu.addSeparator()
        
        # 尝试添加开发者工具菜单项
        try:
            dev_tools_action = context_menu.addAction("🔧 开发者工具")
            dev_tools_action.triggered.connect(self.toggle_dev_tools)
        except:
            pass
            
        context_menu.addSeparator()
        inspect_action = context_menu.addAction("🔍 检查元素")
        
        # 连接信号
        refresh_action.triggered.connect(self.refresh_page)
        reload_action.triggered.connect(self.reload_page)
        inspect_action.triggered.connect(self.inspect_element)
        
        # 显示菜单
        context_menu.exec(self.web_view.mapToGlobal(position))
    
    def reload_page(self):
        """重新加载页面"""
        if self.web_view and self.server_port:
            self.web_view.reload()
            self.status_bar.showMessage("页面已重新加载")
        else:
            QMessageBox.warning(self, "警告", "服务器未启动，无法重新加载页面")
    
    def inspect_element(self):
        """检查元素（备用方法）"""
        QMessageBox.information(
            self,
            "检查元素",
            "请使用以下方法之一：\n\n"
            "1. 按F12键打开开发者工具\n"
            "2. 右键点击页面元素选择'检查'\n"
            "3. 使用菜单栏的'开发者工具'按钮"
        )
    
    def open_build_folder(self):
        """打开构建文件夹"""
        dist_path = os.path.join(os.getcwd(), 'dist')
        
        if os.path.exists(dist_path):
            try:
                # 在文件管理器中打开文件夹
                if sys.platform == "win32":
                    os.startfile(dist_path)
                elif sys.platform == "darwin":  # macOS
                    subprocess.run(["open", dist_path])
                else:  # Linux
                    subprocess.run(["xdg-open", dist_path])
                    
                self.status_bar.showMessage("已打开构建文件夹")
            except Exception as e:
                QMessageBox.warning(
                    self, 
                    "警告", 
                    f"无法打开文件夹：{str(e)}\n\n请手动访问：{dist_path}"
                )
        else:
            QMessageBox.information(
                self, 
                "提示", 
                "构建文件夹不存在，请先构建Vue项目"
            )
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止服务器
        if self.server_thread and self.server_thread.isRunning():
            self.server_thread.stop_server()
            self.server_thread.quit()
            self.server_thread.wait(3000)  # 等待3秒
        
        event.accept()


def check_dependencies():
    """检查依赖"""
    try:
        import PySide6
        print("✓ PySide6已安装")
    except ImportError:
        print("✗ PySide6未安装，请运行: pip install PySide6")
        return False
        
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        print("✓ QtWebEngine已安装")
    except ImportError:
        print("✗ QtWebEngine未安装，请运行: pip install PySide6-WebEngine")
        return False
        
    return True


def main():
    """主函数"""
    print("KSX门店管理系统 - 桌面版")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n请先安装必要的依赖包")
        input("按回车键退出...")
        return
        
    # 检查dist文件夹
    if not os.path.exists('dist'):
        print("✗ 未找到dist文件夹，请先构建Vue项目")
        input("按回车键退出...")
        return
        
    if not os.path.exists(os.path.join('dist', 'index.html')):
        print("✗ dist文件夹中未找到index.html文件")
        input("按回车键退出...")
        return
    
    print("✓ 检测到构建文件")
    print("🚀 启动本地HTTP服务器...")
    
    # 创建Qt应用
    app = QApplication(sys.argv)
    app.setApplicationName("KSX门店管理系统")
    app.setApplicationVersion("1.0.0")
    
    # 创建主窗口
    window = KSXDesktopApp()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
