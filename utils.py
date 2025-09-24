import sys
import os
import subprocess
from pathlib import Path

from config import DATA_DIR, MARKDOWN_FILE

def restart_program():
    """重启当前程序"""
    python = sys.executable
    os.execl(python, python, *sys.argv)

def open_project_folder():
    """打开项目根目录"""
    folder_path = str(Path(__file__).parent.resolve())
    open_folder(folder_path)

def open_markdown_file():
    """用默认编辑器打开Markdown文件"""
    file_path = str((Path(__file__).parent / DATA_DIR / MARKDOWN_FILE).resolve())
    if sys.platform == "win32":
        os.startfile(file_path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", file_path])
    else:
        subprocess.Popen(["xdg-open", file_path])

def open_folder(path):
    """跨平台打开文件夹"""
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path]) 