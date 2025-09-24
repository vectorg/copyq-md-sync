import os
from pathlib import Path
from datetime import datetime
import json
import logging
import re
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from clipboard_manager import export_to_clipboard
from import_commands import parse_md_content
from config import DATA_DIR, MARKDOWN_FILE, COMMAND_STORE_FILE, DEFAULT_TAB

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_command_store(store_path):
    """加载已存储的命令"""
    if os.path.exists(store_path):
        with open(store_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_command_store(commands, store_path):
    """保存命令到存储文件"""
    with open(store_path, 'w', encoding='utf-8') as f:
        json.dump(commands, f, ensure_ascii=False, indent=2)

def run_one_time_sync():
    """
    执行一次性同步命令。
    从md文件解析，更新json存储，导出到剪贴板。
    返回一个包含新命令和更新命令数量的字典。
    """
    current_dir = Path(__file__).parent
    md_path = current_dir / DATA_DIR / MARKDOWN_FILE
    store_path = current_dir / DATA_DIR / COMMAND_STORE_FILE

    logger.info(f"开始同步文件: {md_path}")
    
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        logger.error(f"Markdown 文件未找到: {md_path}")
        return {"new": 0, "updated": 0, "error": "Markdown file not found."}

    parsed_items = parse_md_content(md_content, base_path=md_path)
    stored_commands = load_command_store(store_path)
    command_map = {cmd['command']: cmd for cmd in stored_commands}
    
    new_count = 0
    update_count = 0
    start_time = datetime.now()
    
    for content, tags in parsed_items:
        tags_list = tags.split(',')
        if content not in command_map:
            command_data = {
                "command": content,
                "tags": tags_list,
                "created_at": datetime.now().isoformat(),
                "last_exported": None
            }
            
            if export_to_clipboard(content, tab=DEFAULT_TAB, tags=tags):
                command_data["last_exported"] = datetime.now().isoformat()
                logger.info(f"导出新命令: {content} | 标签: {tags}")
            
            stored_commands.append(command_data)
            command_map[content] = command_data
            new_count += 1
        else:
            existing_cmd = command_map[content]
            existing_tags = set(existing_cmd['tags'])
            new_tags = set(tags_list)
            
            if not new_tags.issubset(existing_tags):
                missing_tags = new_tags - existing_tags
                existing_cmd['tags'] = list(existing_tags | missing_tags)
                
                if export_to_clipboard(content, tab=DEFAULT_TAB, tags=','.join(existing_cmd['tags'])):
                    existing_cmd["last_exported"] = datetime.now().isoformat()
                    logger.info(f"更新命令标签: {content} | 新增标签: {','.join(missing_tags)}")
                update_count += 1
    
    if new_count > 0 or update_count > 0:
        save_command_store(stored_commands, store_path)
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"同步完成。新增 {new_count} 条，更新 {update_count} 条。用时 {elapsed_time:.1f} 秒。")
    else:
        logger.info("同步完成。没有发现新命令或需要更新的标签。")
        
    return {"new": new_count, "updated": update_count}

# --- Watchdog Logic ---

def extract_referenced_files(md_file_path):
    """提取Markdown文件中引用的其他文件路径"""
    referenced_files = set()
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = re.findall(r'\[\[(.*?)\]\]', content)
            for file_path in matches:
                if os.path.isabs(file_path):
                    abs_path = file_path
                else:
                    abs_path = os.path.join(os.path.dirname(md_file_path), file_path)
                
                if os.path.exists(abs_path):
                    referenced_files.add(abs_path)
                    nested_refs = extract_referenced_files(abs_path)
                    referenced_files.update(nested_refs)
                else:
                    logger.warning(f"引用的文件不存在: {file_path}")
    except Exception as e:
        logger.error(f"提取引用文件时出错: {str(e)}")
    
    return referenced_files

class SyncEventHandler(FileSystemEventHandler):
    def __init__(self, main_file_path):
        self.main_file_path = main_file_path
        self.watched_files = {main_file_path}
        self.update_watched_files()
        
    def update_watched_files(self):
        """更新监控的文件列表"""
        new_files = extract_referenced_files(self.main_file_path)
        new_files.add(self.main_file_path) # 确保主文件始终在监控列表
        added_files = new_files - self.watched_files
        if added_files:
            logger.info(f"添加监控以下文件: {added_files}")
        self.watched_files = new_files
        
    def on_modified(self, event):
        file_path = event.src_path
        if file_path in self.watched_files:
            logger.info(f"检测到文件变化: {file_path}, 触发同步...")
            if file_path == self.main_file_path:
                self.update_watched_files()
            run_one_time_sync()

_observer = None

def start_watching(blocking=True):
    """启动文件监控"""
    global _observer
    if _observer and _observer.is_alive():
        logger.warning("监控已在运行中。")
        return

    current_dir = Path(__file__).parent
    md_path = current_dir / DATA_DIR / MARKDOWN_FILE
    abs_md_path = str(md_path.resolve())

    logger.info("执行初始同步...")
    run_one_time_sync()

    event_handler = SyncEventHandler(abs_md_path)
    
    _observer = Observer()
    
    watched_dirs = {os.path.dirname(p) for p in event_handler.watched_files}
    for path in watched_dirs:
        _observer.schedule(event_handler, path, recursive=False)
        logger.info(f"正在监控目录: {path}")

    _observer.start()
    logger.info(f"已启动对 {abs_md_path} 及其引用的文件监控。")

    if blocking:
        # 用于命令行版本阻塞
        try:
            while _observer.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("检测到中断信号，正在停止监控...")
        finally:
            if _observer.is_alive():
                _observer.stop()
            _observer.join()

def stop_watching():
    """停止文件监控"""
    global _observer
    if _observer and _observer.is_alive():
        _observer.stop()
        logger.info("文件监控停止信号已发送。")
        return True
    else:
        logger.info("文件监控未在运行。")
        return False 