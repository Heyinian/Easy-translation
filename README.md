# Easy-translation

基于 PyQt6 的 Windows 桌面翻译工具，支持截图 OCR、剪贴板翻译、外部输入框回填翻译、多翻译源切换，以及系统托盘后台运行。

当前版本：`v0.5.7`

## 功能概览

- 手动输入翻译
- 剪贴板自动监听翻译
- 截图 OCR 翻译
- 外部输入框翻译回填
- 多翻译源切换：Google、百度、腾讯、Ollama
- 中英智能默认目标语言
- 本地加密保存 API 凭证
- 系统托盘常驻与单实例保护

## 适用环境

- 操作系统：Windows
- Python：推荐 `3.12`
- GUI：PyQt6
- OCR：Tesseract（仅截图翻译需要，可选）

## 项目结构

```text
Easy-translation/
|-- app.py
|-- src/
|   |-- main_window.py
|   |-- translator_core.py
|   |-- settings_manager.py
|   |-- config.py
|   |-- hotkey_manager.py
|   |-- clipboard_monitor.py
|   `-- ocr_handler.py
|-- assets/
|-- docs/
|-- runtime/                  # 运行后自动生成，本地数据不入库
|-- Easy-translation.spec
`-- requirements.txt
```

说明：

- `app.py` 是唯一启动入口。
- `src/` 存放应用核心代码。
- `runtime/` 存放本地运行数据，如日志、截图、用户设置和加密密钥。

## 快速开始

### 1. 安装依赖

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\pip install -r requirements.txt
```

### 2. 启动应用

```powershell
.\.venv312\Scripts\python.exe app.py
```

### 3. 可选安装 OCR

如需使用截图翻译，请安装 Tesseract OCR，并在应用设置中填写 `tesseract.exe` 路径。

- Windows 安装包：https://github.com/UB-Mannheim/tesseract/wiki

## 默认热键

- `Alt+Shift+S`：截图翻译
- `Alt+Shift+C`：剪贴板翻译
- `Alt+Shift+T`：显示主窗口
- `triple_space`：翻译当前输入框内容或选中文本

输入框翻译触发键支持两种形式：

- `triple_space`
- 自定义组合键，例如 `alt+shift+x`

## 翻译源说明

### Google

- 默认可直接使用
- 无需填写密钥

### 百度

- 需要在设置中填写 `App ID` 和 `Secret Key`

### 腾讯

- 需要在设置中填写 `Secret ID`、`Secret Key` 和 `Region`

### Ollama

- 依赖本地 Ollama 服务
- 默认地址：`http://127.0.0.1:11434`

## 配置与数据

应用优先读取 `runtime/` 下的本地用户配置，而不是只使用代码默认值。

运行时常见文件：

- `runtime/user_settings.json`
- `runtime/.settings.key`
- `runtime/logs/`
- `runtime/screenshots/`

这些文件属于本地运行数据，不应提交到仓库。

## 文档导航

- [文档索引](docs/DOCS_INDEX.md)
- [项目状态](docs/PROJECT_STATUS.md)
- [快速上手](docs/QUICKSTART.md)
- [开发者指南](docs/DEVELOPER_GUIDE.md)
- [测试说明](docs/TESTING.md)
- [部署说明](docs/DEPLOYMENT.md)
- [发布说明](docs/RELEASE_NOTES.md)
- [变更记录](docs/CHANGELOG.md)

## 常见问题

### 截图翻译无法识别文字

优先检查是否已安装 Tesseract，以及设置中的 Tesseract 路径是否正确。

### 外部输入框翻译没有生效

先确认当前输入框翻译触发键配置是否为 `triple_space` 或自定义组合键，并检查目标应用是否允许复制和粘贴。

如需排查三击空格逻辑，可查看：

- `runtime/logs/triple_space.log`

### 启动后窗口没有留在桌面

应用默认支持最小化或关闭后驻留系统托盘，可通过托盘菜单或显示窗口热键恢复。

## 开发说明

- 入口文件：`app.py`
- 主界面与主要流程：`src/main_window.py`
- 翻译引擎：`src/translator_core.py`
- 设置与密钥存储：`src/settings_manager.py`
- 全局热键：`src/hotkey_manager.py`
- OCR：`src/ocr_handler.py`

更多开发细节见 [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)。

## License

MIT License
