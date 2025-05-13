from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time
import os
from pathlib import Path

class CommandFileHandler(FileSystemEventHandler):
    def __init__(self, sync_script_path):
        self.sync_script_path = sync_script_path
        
    def on_modified(self, event):
        if event.src_path.endswith('命令管理.md'):
            print(f"检测到文件变化: {event.src_path}")
            # 运行同步脚本
            subprocess.run(['python', self.sync_script_path])

def start_watching(command_file_path, sync_script_path):
    # 获取要监控的目录路径
    watch_path = os.path.dirname(command_file_path)
    
    # 创建观察者和处理器
    event_handler = CommandFileHandler(sync_script_path)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=False)
    
    # 开始监控
    observer.start()
    print(f"开始监控文件: {command_file_path}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n停止监控")
    
    observer.join()

if __name__ == "__main__":
    current_dir = Path(__file__).parent
    command_file = current_dir / '命令管理.md'
    sync_script = current_dir / 'sync_commands.py'

    start_watching(command_file, sync_script)
