# 简介

这是一个将 Markdown 文件中的命令同步到 CopyQ 剪贴板管理器的工具。

## 使用步骤

1.安装 CopyQ 剪贴板管理器 可以在 https://github.com/hluk/CopyQ/releases 页内搜索 setup.exe 下载

2.修改 config.py 中的配置参数：
   - `COPYQ_PATH`: 设置为实际的 CopyQ 安装位置
   - `DEFAULT_TAB`: 设置默认标签页
   - `DEFAULT_TAGS`: 设置默认标签
   - `DATA_DIR`: 设置数据目录
   - `MARKDOWN_FILE`: 设置要同步的Markdown文件名
   - `COMMAND_STORE_FILE`: 设置命令存储文件名

3.运行 sync_commands.py 一次性同步 Markdown 文件中新增的命令

或 运行 watch_and_sync.py 自动监控 Markdown 文件及其引用文件变化并同步到 CopyQ

说明：

1.目前命令存放在 CopyQ 的默认标签页中，可以在 config.py 中修改 DEFAULT_TAB 来更改。

2.导入一次后会产生 commands_store.json 文件，用于记录已经导入的命令，下次导入时将会跳过这些命令。

## 新增：托盘应用模式

为了提供更便捷的操作，项目现在包含一个图形化的托盘应用。

### 依赖安装

首先，需要安装 `PyQt5` 和 `watchdog`：
```bash
pip install -r requirements.txt
```

### 运行托盘应用

直接运行 `main_tray.py` 即可启动：
```bash
python main_tray.py
```
程序启动后，会在系统托盘区域显示一个绿色的 "S" 图标。右键点击图标会弹出菜单，提供以下功能：
- **手动同步一次**: 立即执行一次 Markdown 文件的同步。
- **开启/停止自动监控**: 启动或停止对 Markdown 文件及其引用文件的修改监控。
- **打开命令文件**: 使用系统默认编辑器打开 `MARKDOWN_FILE` 配置的文件。
- **打开项目目录**: 在文件浏览器中打开当前项目文件夹。
- **重启程序**: 重新启动托盘应用。
- **退出**: 关闭程序。

### 保留的命令行模式

原有的命令行操作方式**仍然可用**：
- **一次性同步**: `python sync_commands.py`
- **自动监控**: `python watch_and_sync.py`

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
