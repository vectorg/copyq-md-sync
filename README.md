# CopyQ-MD-Sync

一个用于同步和管理命令的工具，支持将 Markdown 文件中的命令与 CopyQ 剪贴板管理器进行双向同步。

## 功能特点

- 📝 支持通过 Markdown 文件管理命令和代码片段
- 🔄 自动监控文件变化并同步到 CopyQ
- 🏷️ 支持通过标签对命令进行分类
- 📋 支持双向同步（CopyQ ↔ Markdown）
- 🔍 支持命令搜索和过滤
- 📚 支持多级分类和引用其他文件

## 系统要求

- Python 3.6+
- CopyQ 剪贴板管理器
- Windows 操作系统

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/copyq-md-sync.git
cd copyq-md-sync
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 启动监控服务

运行以下命令启动文件监控服务：
```bash
python watch_and_sync.py
```

这将开始监控 `命令管理.md` 文件的变化，并在文件发生更改时自动同步到 CopyQ。

### 2. 管理命令

在 `命令管理.md` 文件中，您可以：

- 使用 Markdown 格式编写命令
- 使用 `>` 添加标签
- 使用 `#` 添加命令标签
- 使用 `[[]]` 引用其他文件
- 使用代码块（```）来格式化命令

示例：
```markdown
### Git 命令
> git,开发

```bash
# 初始化仓库
git init
# 添加文件到暂存区
git add .
```
```

### 3. 导入命令

如果需要从 CopyQ 导入命令到 Markdown 文件：
```bash
python import_commands.py
```

## 文件说明

- `watch_and_sync.py`: 文件监控和同步服务
- `sync_commands.py`: 同步命令的核心逻辑
- `import_commands.py`: 从 CopyQ 导入命令
- `clipboard_manager.py`: CopyQ 剪贴板管理接口
- `命令管理.md`: 命令存储文件

## 注意事项

1. 确保 CopyQ 已经安装并正在运行
2. 保持 `命令管理.md` 文件的格式规范
3. 建议定期备份命令文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License 