# Easy-translation

一个基于 PyQt6 的 Windows 桌面翻译工具，支持截图翻译、剪贴板翻译、输入窗口翻译、可选 OCR 和多翻译源切换。

当前版本：v0.5.2

## 文档导航

- 项目总览：README.md
- 文档索引：docs/DOCS_INDEX.md
- 快速上手：docs/QUICKSTART.md
- 开发者归档：docs/DEVELOPER_GUIDE.md
- 部署说明：docs/DEPLOYMENT.md
- 测试说明：docs/TESTING.md
- 发布说明：docs/RELEASE_NOTES.md
- 变更记录：docs/CHANGELOG.md

## 当前功能

- 🖼️ 截图 OCR 翻译
- 📋 剪贴板翻译
- ⌨️ 输入窗口翻译
- 🌍 多语言翻译
- 🔁 智能中英方向判断
- 🤖 Ollama 本地 AI 翻译接入
- 🔐 本地加密设置与密钥存储
- 🎨 系统托盘后台运行
- 🧷 单实例保护，防止重复启动多个相同任务

## 已完成功能归档

- 已完成基础窗口翻译流程
- 已完成剪贴板翻译和自动监听接线
- 已完成截图 OCR 翻译
- 已完成百度与腾讯翻译接入
- 已完成 Ollama 本地 AI 翻译接入
- 已完成智能中英方向判断
- 已完成本地加密设置存储
- 已完成外部输入框抓取与回填
- 已完成输入窗口翻译双模式触发：triple_space / 组合键
- 已完成源码版启动任务与打包链路验证

## 版本演进记录

### Phase 0

- 项目用途梳理
- 初始开发计划确定

### Phase 1

- 设置系统接入
- 运行时配置重载
- API 密钥本地加密存储
- 设置对话框落地
- Google 返回结果修正
- 百度 / 腾讯翻译接入

### Phase 2

- Python 3.12 环境切换
- PyQt6 Windows DLL 启动修复
- 源码启动链路验证
- PyInstaller 打包验证

### Phase 3

- 外部输入框翻译回填流程实现
- 三击空格触发链路实现
- 可配置组合键触发支持
- 三击空格窗口期可配置

### Phase 4

- 智能默认翻译方向
- Ollama 配置项接入

### Phase 5

- 应用统一更名为 Easy-translation
- 新增应用图标与 PyInstaller 打包图标接入
- 关闭和最小化主窗口时切换到托盘后台运行
- 托盘菜单支持打开主界面、设置、剪贴板翻译与退出应用
- 增加单实例存在检查，重复启动时会唤醒已运行实例
- 候选译文功能移除，翻译结果统一为单结果输出
- Tesseract 改为可选配置，未安装时仍可保存设置

### Phase 6

- 三击空格外部输入框翻译稳定性修复
- 增加 `logs/triple_space.log` 调试日志
- 内部模拟按键不再干扰三击空格计数
- 抓取外部文本时增加重试与回退路径
- 不再通过预先回删 3 个空格修改外部文档内容

## 项目结构

```
Easy-translation/
├── app.py                  # 主程序入口
├── main_window.py          # PyQt6主窗口UI
├── config.py               # 运行时配置和常量
├── assets/                 # 应用图标资源
├── settings_manager.py     # 本地设置与密钥管理
├── translator_core.py      # 翻译核心引擎
├── ocr_handler.py          # OCR文字识别
├── hotkey_manager.py       # 全局快捷键管理
├── clipboard_monitor.py    # 剪贴板监听
├── docs/                   # 项目文档目录
│   ├── DOCS_INDEX.md       # 文档索引
│   ├── QUICKSTART.md       # 快速上手
│   ├── DEVELOPER_GUIDE.md  # 开发者归档
│   ├── DEPLOYMENT.md       # 部署说明
│   └── CHANGELOG.md        # 变更记录
└── requirements.txt        # 依赖列表
```

## 快速开始

### 1. 准备环境

当前推荐使用 Python 3.12。

```bash
# 安装依赖
pip install -r requirements.txt

# 安装 Tesseract OCR（可选，仅截图翻译需要）
```

Tesseract Windows 安装包：

- https://github.com/UB-Mannheim/tesseract/wiki

### 2. 运行应用

```bash
.\.venv312\Scripts\python.exe app.py
```

也可以在 VS Code 中直接运行任务：

- 运行源码版 Easy-translation

更简化的启动步骤见：

- docs/QUICKSTART.md

## 配置说明

应用启动后优先读取 user_settings.json 中的用户配置，而不是只依赖 config.py 中的默认值。

重要设置包括：

- 默认翻译源
- 当前翻译源
- 源语言 / 目标语言
- OCR 语言包
- Tesseract 路径（可留空）
- 剪贴板自动监听
- 输入窗口翻译触发方式
- 三击空格窗口期
- Ollama 地址 / 模型 / 超时

## 输入窗口翻译

输入窗口翻译支持两种触发方式：

- triple_space
- 组合键，例如 alt+shift+x

默认配置当前为：

- triple_space
- 窗口期 1.2 秒

如果触发方式是 triple_space，会启用三击空格检测。

如果触发方式是组合键，会注册全局热键。

## 翻译源

当前支持：

- Google
- 百度
- 腾讯
- Ollama

其中：

- Google 可直接使用
- 百度 / 腾讯 需要用户在设置页填入凭证
- Ollama 依赖本地服务

## 开发文档

开发交接和归档文档见：

- docs/DEVELOPER_GUIDE.md

部署说明见：

- docs/DEPLOYMENT.md

变更记录见：

- docs/CHANGELOG.md

## 开发指南

### 新增翻译源

优先修改 translator_core.py 中的 TranslatorCore，并保持 translate_result() 返回结构一致。

### 新增设置项

先在 settings_manager.py 的 DEFAULT_SETTINGS 中补默认值，再通过 config.reload_config() 接入运行时。

### 修改主界面行为

主窗口流程主要集中在 main_window.py。

### 扩展输入触发逻辑

输入窗口翻译涉及：

- hotkey_manager.py
- main_window.py
- clipboard_monitor.py

## 常见问题

### Q: 截图翻译无法识别文字？
A: 检查 Tesseract 是否已安装；如果未安装，也不会影响其他设置保存和普通翻译功能。

### Q: 翻译返回错误？
A: 检查网络连接和当前翻译源配置。百度、腾讯需要有效密钥，Ollama 需要本地服务。

### Q: 快捷键不生效？
A: 某些应用会拦截全局热键或阻止标准 Ctrl+A / Ctrl+C / Ctrl+V 行为，优先换个输入目标程序验证。

### Q: 三击空格不生效？
A: 先确认当前设置中的输入窗口翻译触发键是否为 triple_space，而不是组合键。
如果仍不稳定，可查看 `logs/triple_space.log`，确认是否已经累计到 3 次空格，以及抓取/回填是否成功。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

---

提示：首次运行后应用会常驻托盘。关闭或最小化主窗口时会切换到后台运行，可通过托盘图标或显示窗口热键恢复主界面。
如果重复启动应用，新实例会自动退出，并唤醒已在运行的主实例。
