import os
from pathlib import Path
from datetime import datetime
import json
from clipboard_manager import export_to_clipboard
from import_commands import parse_md_content

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

def sync_commands(md_path, store_path):
    """同步命令：从md文件解析，更新json存储，导出到剪贴板"""
    # 读取markdown文件
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 解析markdown内容，传递文件路径以正确处理相对引用
    parsed_items = parse_md_content(md_content, base_path=md_path)
    
    # 加载现有命令存储
    stored_commands = load_command_store(store_path)
    # 创建命令到存储数据的映射
    command_map = {cmd['command']: cmd for cmd in stored_commands}
    
    # 处理新命令和更新标签
    new_count = 0
    update_count = 0
    start_time = datetime.now()
    
    for content, tags in parsed_items:
        tags_list = tags.split(',')
        if content not in command_map:
            # 创建新命令数据
            command_data = {
                "command": content,
                "tags": tags_list,
                "created_at": datetime.now().isoformat(),
                "last_exported": None
            }
            
            # 导出到剪贴板
            if export_to_clipboard(content, tab='命令', tags=tags):
                command_data["last_exported"] = datetime.now().isoformat()
                print(f"已导出新命令到剪贴板: {content}")
                print(f"标签: {tags}")
                print("-" * 50)
            
            # 添加到存储
            stored_commands.append(command_data)
            command_map[content] = command_data
            new_count += 1
        else:
            # 检查是否有新标签需要添加
            existing_cmd = command_map[content]
            existing_tags = set(existing_cmd['tags'])
            new_tags = set(tags_list)
            
            if not new_tags.issubset(existing_tags):
                # 有新标签需要添加
                missing_tags = new_tags - existing_tags
                existing_cmd['tags'] = list(existing_tags | missing_tags) #保留已存在命令的所有历史标签，同时添加新的标签，导致旧标签删除重新加上时剪贴板不更新
                # existing_cmd['tags'] = tags_list #完全使用新的标签替换旧标签，导致命令重复时多次更新
                
                # 重新导出到剪贴板
                if export_to_clipboard(content, tab='命令', tags=','.join(existing_cmd['tags'])):
                    existing_cmd["last_exported"] = datetime.now().isoformat()
                    print(f"更新命令标签并重新导出: {content}")
                    print(f"新增标签: {','.join(missing_tags)}")
                    print(f"完整标签: {','.join(existing_cmd['tags'])}")
                    print("-" * 50)
                update_count += 1
    
    # 保存更新后的命令存储
    if new_count > 0 or update_count > 0:
        save_command_store(stored_commands, store_path)
        elapsed_time = (datetime.now() - start_time).total_seconds()
        print(f"共处理 {new_count} 条新命令，更新 {update_count} 条已存在命令的标签，用时 {elapsed_time:.1f} 秒")
    else:
        print("没有新的命令或标签需要处理")

def main():
    current_dir = Path(__file__).parent
    md_path = current_dir / 'data' / '命令管理.md'
    store_path = current_dir / 'data' / 'commands_store.json'
    
    sync_commands(md_path, store_path)

if __name__ == "__main__":
    main() 