import sys
from PyQt5.QtWidgets import QApplication
from tray_manager import TrayManager

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 允许无窗口时程序继续运行
    app.setQuitOnLastWindowClosed(False)
    
    # 创建托盘管理器
    tray_manager = TrayManager(app)
    
    tray_manager.show_message("程序已启动", "CopyQ MD Sync 正在后台运行。")
    
    sys.exit(app.exec_()) 