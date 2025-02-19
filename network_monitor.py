import os
import sys
import threading
import winreg
from queue import Queue

import psutil
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QToolTip, QWidget

data_queue = Queue(maxsize=2)


class NetworkMonitorTrayApp:
    def __init__(self):
        # 设置应用和窗口
        self.app = QApplication(sys.argv)

        # 创建一个 QWidget 作为透明的提示窗口，确保其永远在最顶层
        self.tooltip_window = QWidget()
        self.tooltip_window.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # self.tooltip_window.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        self.tooltip_window.setGeometry(0, 0, 300, 100)  # 设置一个合适的大小

        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon(r"icon.png"))  # 设置托盘图标
        self.tray_icon.setVisible(True)

        # 创建菜单
        self.menu = QMenu()
        self.exit_action = QAction("退出", self.menu)
        self.exit_action.triggered.connect(self.app.quit)
        self.menu.addAction(self.exit_action)
        self.tray_icon.setContextMenu(self.menu)

        # 初始化网络监控
        self.last_upload = psutil.net_io_counters().bytes_sent
        self.last_download = psutil.net_io_counters().bytes_recv
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_network_speed)
        self.timer.start(1000)  # 每秒更新一次

        #     开启一个线程
        threading.Thread(target=self.update_display, daemon=True).start()

    def update_display(self):
        while True:
            tooltip_text = data_queue.get()

    def update_network_speed(self):
        # 获取当前网络流量
        current_upload = psutil.net_io_counters().bytes_sent
        current_download = psutil.net_io_counters().bytes_recv

        # 计算上传和下载速率（KB/s）
        upload_speed = (current_upload - self.last_upload) / 1024
        download_speed = (current_download - self.last_download) / 1024

        # 更新上一次的网络流量
        self.last_upload = current_upload
        self.last_download = current_download
        # 更新托盘图标提示信息 # 一直显示
        tooltip_text = (f"上传: {upload_speed:.2f} KB/s\n"
                        f"下载: {download_speed:.2f} KB/s")
        data_queue.put_nowait(tooltip_text)
        # 获取托盘图标的几何信息，并计算显示位置
        tray_geometry = self.tray_icon.geometry()
        tray_position = tray_geometry.topRight()  # 获取托盘图标的右上角位置
        tray_position.setY(tray_position.y() - (tray_geometry.height() + 40))
        # 将提示框显示在托盘图标的位置
        self.tooltip_window.move(
            tray_position - QPoint(self.tooltip_window.width(), self.tooltip_window.height()))  # 调整位置
        self.tray_icon.setToolTip(tooltip_text)
        QToolTip.showText(tray_position, tooltip_text, self.tooltip_window)

    def run(self):
        sys.exit(self.app.exec_())


def add_to_startup(app_name, exe_path):
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(reg_key, app_name, 0, winreg.REG_SZ, exe_path)
    winreg.CloseKey(reg_key)


if __name__ == "__main__":
    app = NetworkMonitorTrayApp()
    exe_path = os.path.abspath("dist/network_monitor.exe")  # EXE 文件路径
    add_to_startup("NetworkMonitor", exe_path)
    app.run()
