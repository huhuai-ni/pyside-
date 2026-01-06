from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
import json
import os

class LoginWindow(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.user_data_file = 'users.json'
        self.initUI()
        self.load_user_data()
        
    def initUI(self):
        self.setWindowTitle('AI视觉检测系统 - 登录/注册')
        self.setFixedSize(450, 400)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title_label = QLabel('AI视觉检测系统')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('''
            font-size: 24px;
            font-weight: bold;
            color: #2196F3;
            margin-bottom: 20px;
        ''')
        
        # 模式选择（登录/注册）
        self.mode_tabs = QTabWidget()
        
        # 登录选项卡
        login_tab = QWidget()
        self.setup_login_tab(login_tab)
        self.mode_tabs.addTab(login_tab, "登录")
        
        # 注册选项卡
        register_tab = QWidget()
        self.setup_register_tab(register_tab)
        self.mode_tabs.addTab(register_tab, "注册")
        
        # 添加到主布局
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.mode_tabs)
        self.setLayout(main_layout)
        self.center()
        
    def setup_login_tab(self, tab):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel('用户名:')
        username_label.setFixedWidth(60)
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText('请输入用户名')
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.login_username)
        
        # 密码
        password_layout = QHBoxLayout()
        password_label = QLabel('密 码:')
        password_label.setFixedWidth(60)
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText('请输入密码')
        self.login_password.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.login_password)
        
        # 记住密码
        self.remember_me = QCheckBox('记住密码')
        
        # 登录按钮
        login_btn = QPushButton('登录')
        login_btn.clicked.connect(self.login)
        login_btn.setFixedHeight(40)
        login_btn.setStyleSheet('''
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        ''')
        
        # 忘记密码链接
        forgot_link = QPushButton('忘记密码?')
        forgot_link.setStyleSheet('''
            QPushButton {
                border: none;
                color: #666;
                text-align: left;
                padding: 0;
            }
            QPushButton:hover {
                color: #2196F3;
                text-decoration: underline;
            }
        ''')
        forgot_link.setCursor(Qt.PointingHandCursor)
        forgot_link.clicked.connect(self.forgot_password)
        
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)
        layout.addWidget(self.remember_me)
        layout.addWidget(login_btn)
        layout.addWidget(forgot_link)
        layout.addStretch(1)
        tab.setLayout(layout)
        
    def setup_register_tab(self, tab):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 用户名
        reg_username_layout = QHBoxLayout()
        reg_username_label = QLabel('用户名:')
        reg_username_label.setFixedWidth(60)
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText('请输入用户名')
        reg_username_layout.addWidget(reg_username_label)
        reg_username_layout.addWidget(self.reg_username)
        
        # 密码
        reg_password_layout = QHBoxLayout()
        reg_password_label = QLabel('密 码:')
        reg_password_label.setFixedWidth(60)
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText('请输入密码')
        self.reg_password.setEchoMode(QLineEdit.Password)
        reg_password_layout.addWidget(reg_password_label)
        reg_password_layout.addWidget(self.reg_password)
        
        # 确认密码
        confirm_password_layout = QHBoxLayout()
        confirm_password_label = QLabel('确认密码:')
        confirm_password_label.setFixedWidth(60)
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText('请再次输入密码')
        self.confirm_password.setEchoMode(QLineEdit.Password)
        confirm_password_layout.addWidget(confirm_password_label)
        confirm_password_layout.addWidget(self.confirm_password)
        
        # 邮箱（可选）
        email_layout = QHBoxLayout()
        email_label = QLabel('邮 箱:')
        email_label.setFixedWidth(60)
        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText('请输入邮箱（可选）')
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.reg_email)
        
        # 注册按钮
        register_btn = QPushButton('注册')
        register_btn.clicked.connect(self.register)
        register_btn.setFixedHeight(40)
        register_btn.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #2E7D32;
            }
        ''')
        
        layout.addLayout(reg_username_layout)
        layout.addLayout(reg_password_layout)
        layout.addLayout(confirm_password_layout)
        layout.addLayout(email_layout)
        layout.addWidget(register_btn)
        layout.addStretch(1)
        tab.setLayout(layout)
        
    def load_user_data(self):
        """加载用户数据"""
        try:
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            else:
                self.users = {}
                
            # 创建初始管理员账户（如果不存在）
            if 'admin' not in self.users:
                self.users['admin'] = {
                    'password': 'admin123',
                    'email': 'admin@example.com',
                    'role': 'admin'
                }
                self.save_user_data()
                
        except Exception as e:
            self.users = {}
            QMessageBox.warning(self, '错误', f'加载用户数据失败: {str(e)}')
            
    def save_user_data(self):
        """保存用户数据"""
        try:
            with open(self.user_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self, '错误', f'保存用户数据失败: {str(e)}')
            
    def login(self):
        """登录功能"""
        username = self.login_username.text().strip()
        password = self.login_password.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, '警告', '请输入用户名和密码！')
            return
            
        if username in self.users:
            if self.users[username]['password'] == password:
                QMessageBox.information(self, '成功', 
                    f'登录成功！\n欢迎回来，{username}')
                
                # 调用app_manager的show_detection方法
                if self.app_manager:
                    self.app_manager.show_detection(username)
                else:
                    QMessageBox.warning(self, '错误', '应用管理器未正确初始化')
            else:
                QMessageBox.warning(self, '错误', '密码错误！')
        else:
            QMessageBox.warning(self, '错误', 
                '用户不存在！\n请先注册或使用管理员账户登录')
                
    def register(self):
        """注册功能"""
        username = self.reg_username.text().strip()
        password = self.reg_password.text().strip()
        confirm_password = self.confirm_password.text().strip()
        email = self.reg_email.text().strip()
        
        # 验证输入
        if not username or not password:
            QMessageBox.warning(self, '警告', '用户名和密码不能为空！')
            return
            
        if len(username) < 3:
            QMessageBox.warning(self, '警告', '用户名至少需要3个字符！')
            return
            
        if len(password) < 6:
            QMessageBox.warning(self, '警告', '密码至少需要6个字符！')
            return
            
        if password != confirm_password:
            QMessageBox.warning(self, '错误', '两次输入的密码不一致！')
            return
            
        if username in self.users:
            QMessageBox.warning(self, '错误', '用户名已存在！')
            return
            
        # 注册新用户
        self.users[username] = {
            'password': password,
            'email': email if email else '',
            'role': 'user'
        }
        
        self.save_user_data()
        QMessageBox.information(self, '成功', 
            '注册成功！\n现在可以使用新账户登录。')
            
        # 清空注册表单
        self.reg_username.clear()
        self.reg_password.clear()
        self.confirm_password.clear()
        self.reg_email.clear()
        
        # 切换到登录选项卡并预填充用户名
        self.mode_tabs.setCurrentIndex(0)
        self.login_username.setText(username)
        
    def forgot_password(self):
        """忘记密码功能"""
        username, ok = QInputDialog.getText(self, '找回密码', 
            '请输入用户名:')
            
        if ok and username:
            if username in self.users:
                email = self.users[username].get('email', '')
                if email:
                    QMessageBox.information(self, '找回密码',
                        f'密码已发送到注册邮箱：\n{email}\n\n请查收邮件并重置密码。')
                else:
                    QMessageBox.warning(self, '找回密码',
                        '该用户未绑定邮箱，请联系管理员重置密码。')
            else:
                QMessageBox.warning(self, '错误', '用户不存在！')
                
    def center(self):
        """窗口居中"""
        frame_geometry = self.frameGeometry()
        center_point = QApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(self, '确认退出',
            '确定要退出程序吗？',
            QMessageBox.Yes | QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()