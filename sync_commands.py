from sync_logic import run_one_time_sync

def main():
    """命令行入口：执行一次性同步"""
    print("开始一次性同步...")
    result = run_one_time_sync()
    if "error" in result:
        print(f"发生错误: {result['error']}")
    else:
        print(f"同步完成。新增 {result['new']} 条，更新 {result['updated']} 条。")
        print("详细信息请查看日志。")

if __name__ == "__main__":
    main() 