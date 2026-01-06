首先安装 pip install pyside6
         pip install ultralytics
1.应用程序入口 (main.py)
核心功能：
应用程序启动入口和管理器
管理登录窗口和检测窗口之间的切换
主要类：
python
class AppManager:
    def show_login(self)              # 显示登录窗口
    def show_detection(self, username) # 显示检测窗口
    def show_login_from_detection(self) # 从检测窗口返回登录
设置应用程序的样式为 'Fusion'
'Fusion' 是 Qt 的一种现代化样式，具有以下特点：
跨平台外观一致
现代扁平化设计
支持主题颜色定制
比系统原生样式更美观










    
2.用户验证逻辑
登录验证：
检查用户名是否存在
验证密码是否正确
成功后跳转到检测窗口
注册验证：
用户名长度≥3字符
密码长度≥6字符
两次密码输入一致
用户名唯一性检查







3.密码储存文件   users
4.检测界面
