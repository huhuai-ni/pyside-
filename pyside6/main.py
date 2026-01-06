from PySide6.QtWidgets import QApplication
import sys
from login_window import LoginWindow
from detection_window import DetectionWindow

class AppManager:
    def __init__(self):
        self.login_window = None
        self.detection_window = None
        
    def show_login(self):
        """显示登录窗口"""
        if self.login_window is None:
            self.login_window = LoginWindow(self)
        self.login_window.show()
        self.login_window.raise_()
        self.login_window.activateWindow()
        
    def show_detection(self, username):
        """显示检测窗口"""
        # 隐藏登录窗口
        if self.login_window:
            self.login_window.hide()
            
        # 创建或显示检测窗口
        if self.detection_window is None:
            self.detection_window = DetectionWindow(username, self)
        self.detection_window.show()
        self.detection_window.raise_()
        self.detection_window.activateWindow()
        
    def show_login_from_detection(self):
        """从检测窗口返回登录"""
        if self.detection_window:
            self.detection_window.close()
            self.detection_window = None
            
        if self.login_window:
            self.login_window.show()
        else:
            self.show_login()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 设置统一的样式
    
    manager = AppManager()
    manager.show_login()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()