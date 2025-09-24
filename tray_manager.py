import threading
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from icon_creator import create_tray_icon
from utils import restart_program, open_project_folder, open_markdown_file
import sync_logic
from PyQt5.QtCore import QObject, QMetaObject, Qt, pyqtSlot

class TrayManager(QObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(create_tray_icon())
        self.tray_icon.setToolTip("CopyQ MD Sync")
        
        self.watcher_thread = None
        self.is_watching = False

        # --- 菜单 ---
        self.tray_menu = QMenu()
        
        self.sync_action = QAction("手动同步一次", self)
        self.watch_action = QAction("开启自动监控", self)
        self.watch_action.setCheckable(True)

        self.tray_menu.addAction(self.sync_action)
        self.tray_menu.addAction(self.watch_action)
        self.tray_menu.addSeparator()
        
        self.open_md_action = QAction("打开命令文件", self)
        self.open_folder_action = QAction("打开项目目录", self)
        self.tray_menu.addAction(self.open_md_action)
        self.tray_menu.addAction(self.open_folder_action)
        self.tray_menu.addSeparator()

        self.restart_action = QAction("重启程序", self)
        self.quit_action = QAction("退出", self)
        self.tray_menu.addAction(self.restart_action)
        self.tray_menu.addAction(self.quit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # --- 信号连接 ---
        self.sync_action.triggered.connect(self.run_sync_in_thread)
        self.watch_action.toggled.connect(self.toggle_watching)
        self.open_md_action.triggered.connect(open_markdown_file)
        self.open_folder_action.triggered.connect(open_project_folder)
        self.restart_action.triggered.connect(restart_program)
        self.quit_action.triggered.connect(self.quit_app)
        
        self.tray_icon.show()

    def show_message(self, title, message, mtype=QSystemTrayIcon.Information, timeout=3000):
        self.tray_icon.showMessage(title, message, mtype, timeout)

    def run_sync_in_thread(self):
        """在新线程中执行一次性同步，避免UI阻塞"""
        self.show_message("正在同步", "正在同步Markdown文件到CopyQ...")
        sync_thread = threading.Thread(target=self.sync_and_notify)
        sync_thread.start()

    def sync_and_notify(self):
        result = sync_logic.run_one_time_sync()
        if "error" in result:
            self.show_message("同步失败", result["error"], QSystemTrayIcon.Critical)
        else:
            msg = f"同步完成。\n新增 {result['new']} 条, 更新 {result['updated']} 条。"
            self.show_message("同步成功", msg)

    def toggle_watching(self, checked):
        if checked:
            self.start_watching()
        else:
            self.stop_watching()

    def start_watching(self):
        if self.is_watching:
            return
        self.is_watching = True
        self.show_message("监控已开启", "正在监控Markdown文件变化...")
        self.watch_action.setText("停止自动监控")
        
        # 在新线程中运行 watchdog observer
        self.watcher_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watcher_thread.start()

    def _watch_loop(self):
        # start_watching (blocking=True) will run until stop_watching is called from another thread.
        # It handles its own join.
        sync_logic.start_watching(blocking=True)
        
        # When the loop finishes, update UI. Needs to be thread-safe.
        # Using postEvent or signals would be better, but this direct call might work for simple cases.
        QMetaObject.invokeMethod(self, "on_watcher_stopped", Qt.QueuedConnection)

    @pyqtSlot()
    def on_watcher_stopped(self):
        """Callback to run in the main thread to update UI."""
        self.is_watching = False
        self.watch_action.setChecked(False)
        self.watch_action.setText("开启自动监控")
        self.show_message("监控已停止", "已停止自动监控文件变化。")

    def stop_watching(self):
        if not self.is_watching:
            return
        
        self.show_message("正在停止", "正在停止文件监控...")
        sync_logic.stop_watching()


    def quit_app(self):
        self.stop_watching()
        self.tray_icon.hide()
        QApplication.instance().quit() 