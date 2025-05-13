import os
from pathlib import Path
from datetime import datetime
import json
import re

def get_heading_tag(line):
    """获取标题级别和内容"""
    level = len(line) - len(line.lstrip('#'))
    content = line.lstrip('#').strip()
    return f"{'#' * level}{content}" if content else None

class MarkdownParser:
    def __init__(self):
        self.items = []
        self.current_content = None
        self.current_tags = ["命令"]  # 默认标签
        self.heading_tags = []  # 标题标签栈
        self.in_code_block = False
        self.code_block_content = []
        self.pending_code_block = None
        self.processed_files = set()  # 用于跟踪已处理的文件，避免循环引用

    def _handle_empty_line(self):
        """处理空行"""
        if self.current_content and not self.in_code_block:
            self.items.append((self.current_content, ','.join(self.current_tags)))
            self.current_content = None

    def _handle_code_block(self, line):
        """处理代码块"""
        if line.strip().startswith('```'):
            if not self.in_code_block:
                # 开始代码块
                self.in_code_block = True
                self._handle_empty_line()  # 处理之前的内容
                self.code_block_content = []
            else:
                # 结束代码块
                self.in_code_block = False
                if self.code_block_content:
                    # 存储代码块内容，等待下一个标签行
                    self.pending_code_block = '\n'.join(self.code_block_content)
                self.code_block_content = []
            return True
        
        if self.in_code_block:
            self.code_block_content.append(line)
            return True
            
        return False

    def _handle_file_reference(self, line):
        """处理文件引用语法 [[文件路径]]"""
        matches = re.findall(r'\[\[(.*?)\]\]', line)
        if matches:
            for file_path in matches:
                if file_path in self.processed_files:
                    print(f"警告: 检测到循环引用 {file_path}")
                    continue
                    
                self.processed_files.add(file_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        referenced_content = f.read()
                        # 递归解析引用的文件内容
                        referenced_items = self.parse(referenced_content)
                        self.items.extend(referenced_items)
                except FileNotFoundError:
                    print(f"错误: 找不到引用的文件 {file_path}")
                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {str(e)}")
            return True
        return False

    def _handle_tag_line(self, line):
        """处理标签行（以>开头）"""
        if line.startswith('>'):
            tags = line[1:].strip()
            tag_list = [tags] if tags else ["命令"]
            
            # 将标题标签添加到当前标签中
            combined_tags = tag_list + self.heading_tags
            
            # 如果有待处理的代码块，将其与组合标签关联
            if self.pending_code_block is not None:
                self.items.append((self.pending_code_block, ','.join(combined_tags)))
                self.pending_code_block = None
            elif self.current_content:
                self.items.append((self.current_content, ','.join(combined_tags)))
                self.current_content = None
                
            self.current_tags = combined_tags
            return True
        return False

    def _update_heading_stack(self, heading_tag):
        """更新标题标签栈"""
        level = len(heading_tag) - len(heading_tag.lstrip('#'))
        # 移除同级或更低级别的标题
        while self.heading_tags and (len(self.heading_tags[0]) - len(self.heading_tags[0].lstrip('#'))) >= level:
            self.heading_tags.pop(0)
        self.heading_tags.insert(0, heading_tag)
        self.current_tags = ["命令"] + self.heading_tags

    def _handle_heading(self, line):
        """处理Markdown标题"""
        if line.lstrip().startswith('#'):
            if self.current_content:
                self.items.append((self.current_content, ','.join(self.current_tags)))
                self.current_content = None
            elif self.pending_code_block:
                self.items.append((self.pending_code_block, ','.join(self.current_tags)))
                self.pending_code_block = None
            
            heading_tag = get_heading_tag(line)
            if heading_tag:
                self._update_heading_stack(heading_tag)
            return True
        return False

    def _handle_inline_tag(self, line):
        """处理行内标签"""
        if ' #' in line and not line.lstrip().startswith('#'):
            parts = line.split(' #', 1)
            content = parts[0].strip()
            tag = parts[1].strip()
            if content:
                tags = [tag] + self.heading_tags if tag else self.heading_tags
                self.items.append((content, ','.join(tags)))
            return True
        return False

    def _handle_normal_content(self, line):
        """处理普通内容"""
        if line.strip():
            if self.current_content:
                self.items.append((self.current_content, ','.join(self.current_tags)))
            self.current_content = line.strip()

    def parse(self, md_content):
        """解析markdown内容"""
        for line in md_content.split('\n'):
            if not line.strip() and not self.in_code_block:
                self._handle_empty_line()
                continue
                
            if self._handle_code_block(line):
                continue
                
            if not self.in_code_block:
                if self._handle_file_reference(line):
                    continue
                    
                if self._handle_tag_line(line):
                    continue
                    
                if self._handle_heading(line):
                    continue
                    
                if self._handle_inline_tag(line):
                    continue
                    
                self._handle_normal_content(line)
        
        if self.current_content and not self.in_code_block:
            self.items.append((self.current_content, ','.join(self.current_tags)))
        elif self.pending_code_block:
            self.items.append((self.pending_code_block, ','.join(self.current_tags)))
        
        return self.items

def parse_md_content(md_content):
    """解析markdown内容，提取命令及其标签"""
    md_content = md_content.replace('\\', '\\\\')
    parser = MarkdownParser()
    return parser.parse(md_content)

def create_command_store(items, store_path):
    """创建命令存储JSON文件"""
    commands = []
    existing_commands = set()
    
    # 如果文件已存在，读取现有命令
    if os.path.exists(store_path):
        with open(store_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            for cmd in existing_data:
                existing_commands.add(cmd['command'])
            commands.extend(existing_data)
    
    # 添加新命令
    new_count = 0
    for content, tags in items:
        if content not in existing_commands:
            command_data = {
                "command": content,
                "tags": tags.split(','),
                "created_at": datetime.now().isoformat(),
                "last_exported": None
            }
            commands.append(command_data)
            existing_commands.add(content)
            new_count += 1
            print(f"添加新命令: {content}")
            print(f"标签: {tags}")
            print("-" * 50)
    
    # 保存到文件
    with open(store_path, 'w', encoding='utf-8') as f:
        json.dump(commands, f, ensure_ascii=False, indent=2)
    
    return new_count

def main():
    current_dir = Path(__file__).parent
    md_path = current_dir / '命令管理.md'
    store_path = current_dir / 'commands_store.json'
    
    # 读取并解析markdown文件
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    items = parse_md_content(md_content)
    new_items_count = create_command_store(items, store_path)
    
    if new_items_count == 0:
        print("没有新的命令需要添加")
    else:
        print(f"共添加 {new_items_count} 条新命令")

if __name__ == "__main__":
    main() 