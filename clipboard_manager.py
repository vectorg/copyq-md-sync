import subprocess

# 定义常量
COPYQ_PATH = "D:\\Software\\copyq-9.1.0\\copyq.exe"

def check_content_exists(content, tab="test"):
    """
    检查内容是否已存在于指定标签页
    :param content: 要检查的内容
    :param tab: CopyQ的标签页
    :return: 是否存在
    """
    try:
        result = subprocess.run(
            [COPYQ_PATH, 'tab', tab, 'eval', 
             f'var content = "{content.replace(chr(34), chr(92)+chr(34))}"; '
             'var exists = false; '
             'for (var i = 0; i < size(); ++i) { '
             '    if (str(read(i)) === content) { '
             '        exists = true; '
             '        break; '
             '    } '
             '} '
             'print(exists);'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        return result.stdout.strip().lower() == 'true'
    except subprocess.CalledProcessError as e:
        print(f"检查内容是否存在时发生错误: {e}")
        return False

def export_to_clipboard(content, tab="test", tags="测试,test", need_check=False):
    """
    将内容导出到剪贴板，如果内容不存在才添加
    :param content: 要导出的完整内容
    :param tab: CopyQ的标签页，默认为"test"
    :param tags: 要添加的标签，默认为"测试,test"
    :param need_check: 是否需要检查内容是否存在，默认为False
    :return: 是否成功添加新内容
    """
    if need_check and check_content_exists(content, tab):
        return False
        
    command = [
        COPYQ_PATH, 'tab', tab,
        'write', 'text/plain', content,
        'application/x-copyq-tags', tags
    ]
    subprocess.run(command)
    return True

def import_from_clipboard():
    """
    从剪贴板导入内容
    :return: 返回剪贴板内容
    """
    try:

        result = subprocess.run(
            [COPYQ_PATH, 'read', '0'], 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"读取剪贴板失败: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    # 导出示例
    export_to_clipboard("Item with tag 'test'")  # 现在需要传递完整内容
    
    # 导入示例
    content = import_from_clipboard()
    print("从剪贴板导入的内容：", content)
