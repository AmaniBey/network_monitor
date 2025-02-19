import sys
import win32gui
import win32con
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

class TrayInfoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('系统托盘信息')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        self.label = QLabel('系统托盘应用信息：')
        layout.addWidget(self.label)

        self.setLayout(layout)

        self.get_tray_info()

    def get_tray_info(self):
        # 获取系统托盘窗口句柄
        tray_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
        if tray_hwnd:
            # 获取托盘工具栏句柄
            toolbar_hwnd = win32gui.FindWindowEx(tray_hwnd, 0, "ToolbarWindow32", None)
            if toolbar_hwnd:
                # 获取托盘图标数量
                count = win32gui.SendMessage(toolbar_hwnd, win32con.TB_BUTTONCOUNT, 0, 0)
                self.label.setText(f"系统托盘应用数量: {count}\n")

                # 遍历每个托盘图标
                for i in range(count):
                    # 获取图标信息
                    info = win32gui.SendMessage(toolbar_hwnd, win32con.TB_GETBUTTON, i, 0)
                    if info:
                        # 解析图标信息
                        buffer = win32gui.PyMakeBuffer(win32gui.SendMessage(toolbar_hwnd, win32con.TB_GETBUTTONTEXT, i, 0))
                        text = buffer.decode('utf-16', errors='ignore').strip()
                        self.label.setText(self.label.text() + f"图标 {i + 1}: {text}\n")
            else:
                self.label.setText("未找到托盘工具栏")
        else:
            self.label.setText("未找到系统托盘窗口")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TrayInfoApp()
    ex.show()
    sys.exit(app.exec_())