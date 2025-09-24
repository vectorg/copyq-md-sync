from sync_logic import start_watching, stop_watching
import os
from pathlib import Path

def main():
    """命令行入口：启动文件监控"""
    print("启动自动监控... (按 Ctrl+C 停止)")
    os.chdir(Path(__file__).parent)
    # start_watching from sync_logic handles the KeyboardInterrupt and stopping.
    start_watching(blocking=True)
    print("监控已停止。")

if __name__ == "__main__":
    main()
