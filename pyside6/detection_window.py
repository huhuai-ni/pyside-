from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QTimer, QDateTime, Signal, QObject
from PySide6.QtGui import QPixmap, QImage
import cv2
import numpy as np
import os
import time
from threading import Thread, Lock

# 设置YOLO不输出调试信息
os.environ['YOLO_VERBOSE'] = 'False'

# 定义一个信号类用于线程间通信
class DetectionSignals(QObject):
    update_treated_image = Signal(QImage)  # 更新检测后图像
    update_result_text = Signal(str)        # 更新检测结果文本
    update_status_text = Signal(str)        # 更新状态文本
    update_info_text = Signal(str)          # 更新信息文本

class DetectionWindow(QMainWindow):
    def __init__(self, username, app_manager):
        super().__init__()
        self.username = username
        self.app_manager = app_manager
        self.camera = None
        self.is_camera_open = False
        self.is_detecting = False
        
        # YOLO相关
        self.frameToAnalyze = []
        self.detection_results = []
        self.model = None
        self.lock = Lock()  # 线程锁
        
        # 创建信号对象
        self.signals = DetectionSignals()
        
        self.initUI()
        
        # 连接信号到槽函数
        self.signals.update_treated_image.connect(self.update_treated_image)
        self.signals.update_result_text.connect(self.update_result_text)
        self.signals.update_status_text.connect(self.update_status_text)
        self.signals.update_info_text.connect(self.update_info_text)
        
        # 启动YOLO处理线程（在后台加载模型）
        Thread(target=self.load_yolo_model, daemon=True).start()
        
    def initUI(self):
        self.setWindowTitle(f'AI视觉检测系统 - 欢迎 {self.username}')
        self.setGeometry(100, 50, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题栏
        title_layout = QHBoxLayout()
        title_label = QLabel('AI视觉检测系统 - YOLO目标检测')
        title_label.setStyleSheet('font-size: 24px; font-weight: bold; color: #2196F3;')
        
        user_label = QLabel(f'用户: {self.username}')
        user_label.setStyleSheet('font-size: 14px; color: #666;')
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(user_label)
        
        # 视频显示区域（双画面）
        video_layout = QHBoxLayout()
        
        # 原视频画面
        self.label_ori_video = QLabel()
        self.label_ori_video.setMinimumSize(520, 400)
        self.label_ori_video.setStyleSheet('border: 2px solid #ccc; background-color: #000;')
        self.label_ori_video.setAlignment(Qt.AlignCenter)
        self.label_ori_video.setText("原视频画面")
        
        # 检测后画面
        self.label_treated = QLabel()
        self.label_treated.setMinimumSize(520, 400)
        self.label_treated.setStyleSheet('border: 2px solid #ccc; background-color: #000;')
        self.label_treated.setAlignment(Qt.AlignCenter)
        self.label_treated.setText("YOLO检测画面")
        
        video_layout.addWidget(self.label_ori_video)
        video_layout.addWidget(self.label_treated)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.camera_btn = QPushButton('📹 开启摄像头')
        self.camera_btn.clicked.connect(self.toggle_camera)
        self.camera_btn.setFixedHeight(40)
        self.camera_btn.setStyleSheet('''
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        ''')
        
        self.detect_btn = QPushButton('🎯 开始检测')
        self.detect_btn.clicked.connect(self.toggle_detection)
        self.detect_btn.setFixedHeight(40)
        self.detect_btn.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        ''')
        
        logout_btn = QPushButton('🚪 退出登录')
        logout_btn.clicked.connect(self.logout)
        logout_btn.setFixedHeight(40)
        logout_btn.setStyleSheet('''
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        ''')
        
        button_layout.addWidget(self.camera_btn)
        button_layout.addWidget(self.detect_btn)
        button_layout.addStretch()
        button_layout.addWidget(logout_btn)
        
        # 信息面板
        info_group = QGroupBox("系统信息")
        info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(100)
        self.update_info_text_signal("系统状态: 就绪")
        
        info_layout.addWidget(self.info_text)
        info_group.setLayout(info_layout)
        
        # 检测结果面板
        result_group = QGroupBox("检测结果")
        result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(100)
        self.result_text.setText("等待检测结果...")
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        
        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet('color: #666; font-size: 12px;')
        
        # 组装所有布局
        main_layout.addLayout(title_layout)
        main_layout.addLayout(video_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(info_group)
        main_layout.addWidget(result_group)
        main_layout.addWidget(self.status_label)
        
        central_widget.setLayout(main_layout)
        
        # 定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
    def load_yolo_model(self):
        """加载YOLO模型（在独立线程中）"""
        try:
            from ultralytics import YOLO
            self.update_status_text_signal("正在加载YOLO模型，请稍候...")
            self.model = YOLO('yolov8n.pt')
            self.update_status_text_signal("YOLO模型加载完成")
            self.update_info_text_signal("YOLO模型已加载")
            
            # 启动处理线程
            Thread(target=self.frame_analyze_thread_func, daemon=True).start()
            
        except Exception as e:
            self.update_status_text_signal(f"YOLO模型加载失败: {str(e)}")
            self.update_info_text_signal(f"YOLO模型加载失败: {str(e)}")
            
    def update_info_text_signal(self, message):
        """通过信号更新信息面板"""
        current_time = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')
        full_message = f"用户: {self.username}\n时间: {current_time}\n{message}"
        self.signals.update_info_text.emit(full_message)
        
    def update_info_text(self, message):
        """槽函数：更新信息面板"""
        self.info_text.setText(message)
        
    def update_status_text_signal(self, message):
        """通过信号更新状态文本"""
        self.signals.update_status_text.emit(message)
        
    def update_status_text(self, message):
        """槽函数：更新状态文本"""
        self.status_label.setText(message)
        
    def toggle_camera(self):
        """切换摄像头"""
        if not self.is_camera_open:
            # 在Windows上使用CAP_DSHOW提高打开速度
            self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if self.camera.isOpened():
                self.is_camera_open = True
                self.camera_btn.setText('📹 关闭摄像头')
                self.timer.start(50)  # 50ms更新一次（约20fps）
                self.update_info_text_signal("摄像头已开启")
                self.update_status_text_signal("摄像头已开启")
            else:
                QMessageBox.warning(self, '错误', '无法打开摄像头！')
                self.update_status_text_signal("摄像头打开失败")
        else:
            self.timer.stop()
            if self.camera:
                self.camera.release()
            self.is_camera_open = False
            self.camera_btn.setText('📹 开启摄像头')
            self.label_ori_video.setText("摄像头已关闭")
            self.label_treated.setText("摄像头已关闭")
            self.label_ori_video.setPixmap(QPixmap())
            self.label_treated.setPixmap(QPixmap())
            self.update_info_text_signal("摄像头已关闭")
            self.update_status_text_signal("摄像头已关闭")
            
    def update_frame(self):
        """更新视频帧"""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # 调整帧大小
                frame = cv2.resize(frame, (520, 400))
                
                # 显示原视频画面
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                qt_image = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0],
                                frame_rgb.shape[2] * frame_rgb.shape[1], QImage.Format_RGB888)
                self.label_ori_video.setPixmap(QPixmap.fromImage(qt_image))
                
                # 如果正在进行检测且模型已加载，将帧加入处理队列
                if self.is_detecting and self.model:
                    with self.lock:
                        if len(self.frameToAnalyze) == 0:
                            self.frameToAnalyze.append(frame_rgb)
                    
    def frame_analyze_thread_func(self):
        """YOLO处理线程"""
        while True:
            frame = None
            with self.lock:
                if self.frameToAnalyze:
                    frame = self.frameToAnalyze.pop(0)
            
            if frame is None:
                time.sleep(0.01)
                continue
                
            try:
                # 进行YOLO检测
                results = self.model(frame)[0]
                
                # 获取检测结果
                detected_objects = []
                if hasattr(results, 'boxes'):
                    for box in results.boxes:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        label = results.names[cls_id]
                        detected_objects.append(f"{label}: {conf:.2f}")
                
                # 绘制检测结果
                img = results.plot(line_width=1)
                
                # 更新检测结果文本
                if detected_objects:
                    result_text = "检测到对象:\n" + "\n".join(detected_objects[:5])  # 只显示前5个
                    if len(detected_objects) > 5:
                        result_text += f"\n...还有{len(detected_objects)-5}个对象"
                else:
                    result_text = "未检测到对象"
                    
                # 通过信号更新UI
                self.signals.update_result_text.emit(result_text)
                
                # 显示检测后的画面
                h, w, ch = img.shape
                bytes_per_line = ch * w
                qImage = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.signals.update_treated_image.emit(qImage)
                
            except Exception as e:
                print(f"YOLO检测错误: {e}")
                # 通过信号更新错误信息
                self.signals.update_result_text.emit(f"检测错误: {str(e)}")
                
            time.sleep(0.1)  # 控制处理频率
            
    def update_treated_image(self, qImage):
        """槽函数：更新处理后的图像"""
        self.label_treated.setPixmap(QPixmap.fromImage(qImage))
        
    def update_result_text(self, text):
        """槽函数：更新结果文本"""
        self.result_text.setText(text)
        
    def toggle_detection(self):
        """切换检测状态"""
        if not self.is_camera_open:
            QMessageBox.warning(self, '警告', '请先开启摄像头！')
            self.update_status_text_signal("请先开启摄像头")
            return
            
        if self.model is None:
            QMessageBox.warning(self, '警告', 'YOLO模型正在加载中，请稍候...')
            self.update_status_text_signal("YOLO模型加载中")
            return
            
        self.is_detecting = not self.is_detecting
        if self.is_detecting:
            self.detect_btn.setText('⏸️ 停止检测')
            self.update_info_text_signal("YOLO检测进行中")
            self.update_status_text_signal("YOLO检测进行中")
            QMessageBox.information(self, '检测', '开始YOLO目标检测...')
        else:
            self.detect_btn.setText('🎯 开始检测')
            self.update_info_text_signal("检测已停止")
            self.update_status_text_signal("检测已停止")
            self.result_text.setText("检测已停止")
            
    def logout(self):
        """退出登录"""
        reply = QMessageBox.question(self, '确认退出',
            '确定要退出登录吗？',
            QMessageBox.Yes | QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            # 关闭摄像头
            if self.is_camera_open:
                self.timer.stop()
                if self.camera:
                    self.camera.release()
                    
            # 调用app_manager的show_login方法
            if self.app_manager:
                self.app_manager.show_login_from_detection()
                
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 释放摄像头资源
        if self.is_camera_open:
            self.timer.stop()
            if self.camera:
                self.camera.release()
        event.accept()