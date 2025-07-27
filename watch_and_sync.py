from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time
import os
import re
from pathlib import Path
from config import DATA_DIR, MARKDOWN_FILE, COMMAND_STORE_FILE

def extract_referenced_files(md_file_path):
    """提取Markdown文件中引用的其他文件路径"""
    referenced_files = set()
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 查找[[文件路径]]格式的引用
            matches = re.findall(r'\[\[(.*?)\]\]', content)
            for file_path in matches:
                # 转换为绝对路径
                if os.path.isabs(file_path):
                    abs_path = file_path
                else:
                    abs_path = os.path.join(os.path.dirname(md_file_path), file_path)
                
                if os.path.exists(abs_path):
                    referenced_files.add(abs_path)
                    # 递归查找引用文件中的引用
                    nested_refs = extract_referenced_files(abs_path)
                    referenced_files.update(nested_refs)
                else:
                    print(f"警告: 引用的文件不存在: {file_path}")
    except Exception as e:
        print(f"提取引用文件时出错: {str(e)}")
    
    return referenced_files

class CommandFileHandler(FileSystemEventHandler):
    def __init__(self, main_file_path, sync_script_path):
        self.main_file_path = main_file_path
        self.sync_script_path = sync_script_path
        self.watched_files = set([main_file_path])
        self.update_watched_files()
        
    def update_watched_files(self):
        """更新监控的文件列表"""
        new_files = extract_referenced_files(self.main_file_path)
        added_files = new_files - self.watched_files
        if added_files:
            print(f"添加监控以下引用的文件:")
            for file in added_files:
                print(f"  - {file}")
        self.watched_files.update(new_files)
        return new_files
        
    def on_modified(self, event):
        file_path = event.src_path
        if file_path in self.watched_files:
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f"[{time_str}] 检测到文件变化: {file_path}")
            # 如果主文件发生变化，可能有新的引用
            if file_path == self.main_file_path:
                self.update_watched_files()
            # 运行同步脚本
            subprocess.run(['python', self.sync_script_path])

def start_watching(command_file_path, sync_script_path):
    # 获取命令文件的绝对路径
    abs_command_file = os.path.abspath(command_file_path)
    
    # 创建处理器
    event_handler = CommandFileHandler(abs_command_file, sync_script_path)
    
    # 创建观察者
    observer = Observer()
    
    # 添加主文件所在目录的监控
    main_dir = os.path.dirname(abs_command_file)
    observer.schedule(event_handler, main_dir, recursive=False)
    
    # 添加所有引用文件所在目录的监控
    watched_dirs = set([main_dir])
    for file_path in event_handler.watched_files:
        dir_path = os.path.dirname(file_path)
        if dir_path not in watched_dirs:
            observer.schedule(event_handler, dir_path, recursive=False)
            watched_dirs.add(dir_path)
    
    # 启动时立即执行一次同步命令
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{time_str}] 启动时执行初始同步...")
    subprocess.run(['python', sync_script_path])
    
    # 开始监控
    observer.start()
    print(f"开始监控文件: {abs_command_file}")
    print(f"以及引用的文件: {len(event_handler.watched_files) - 1} 个")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n停止监控")
    
    observer.join()

if __name__ == "__main__":
    # 获取当前文件的目录
    current_dir = Path(__file__).parent
    # 指定命令管理文件路径
    command_file = current_dir / DATA_DIR / MARKDOWN_FILE
    # 指定同步脚本路径
    sync_script = current_dir / 'sync_commands.py'

    # 设置脚本目录为当前目录
    os.chdir(current_dir)

    # 开始监控
    start_watching(command_file, sync_script)
