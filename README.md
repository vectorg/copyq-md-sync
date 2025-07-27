# 简介

这是一个将 Markdown 文件中的命令同步到 CopyQ 剪贴板管理器的工具。

## 使用步骤

1.安装 CopyQ 剪贴板管理器 可以在 https://github.com/hluk/CopyQ/releases 页内搜索 setup.exe 下载

2.将 clipboard_manager.py 的 COPYQ_PATH 中改为实际的 CopyQ 安装位置，根据需要修改 "data/命令管理.md" 文件

3.运行 sync_commands.py 一次性同步 "data/命令管理.md" 文件中新增的命令

或 运行 watch_and_sync.py 自动监控 "data/命令管理.md" 及其引用文件变化并同步到 CopyQ

说明：

1.目前命令存放在 CopyQ 的标签 "命令"中，可以通过修改 sync_commands.py 对 export_to_clipboard 函数的两处调用来修改。

2.导入一次后会产生文件 data/commands_store.json ，用于记录已经导入的命令，下次导入时将会跳过这些命令。

## "命令管理.md" 文件格式说明

- Markdown 格式的各级标题及单行文本
文本会被导入到 CopyQ ，并使用标题作为标签，如
```md
# 测试
## 测试前端
npm run dev
## 测试后端
ps aux | grep [p]ython
```
将被导入为两条：
```
npm run dev #测试 ##测试前端
ps aux | grep [p]ython #测试 ##测试后端
```

- 多行文本需要使用代码块（```）来导入

- 对于单行文本，可以使用 文本 # 标签 的方式添加标签

- 对于多行文本，可以在代码块的下一行用 > 标签 的方式添加标签

- 可以使用 `[[]]` 引用其他文件
