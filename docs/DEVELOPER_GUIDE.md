# 开发者归档文档

本文档用于帮助后续开发者快速接手当前项目，重点记录当前可运行状态、核心模块职责、配置落点、已实现功能、已知限制和推荐扩展方向。

## 文档导航

- 文档索引：DOCS_INDEX.md
- 项目总览：../README.md
- 快速上手：QUICKSTART.md
- 部署说明：DEPLOYMENT.md
- 测试说明：TESTING.md
- 发布说明：RELEASE_NOTES.md
- 变更记录：CHANGELOG.md

## 1. 项目当前定位

本项目是一个 Windows 桌面翻译工具，基于 PyQt6 实现，当前已具备以下能力：

- 文本输入翻译
- 剪贴板翻译
- 截图 OCR 翻译
- 外部输入框翻译回填
- 多翻译源切换
- 本地加密设置存储
- Ollama 本地翻译接入

当前推荐运行环境是 Python 3.12，对应本地虚拟环境为 .venv312。

## 2. 当前可运行状态

截至当前归档版本，已验证以下事项：

- 源码版可从 app.py 正常启动
- .vscode/tasks.json 中已存在“运行源码版 Easy-translation”任务
- 默认输入窗口翻译触发方式为 triple_space
- 三击空格窗口期当前默认配置为 1.2 秒
- 如果将输入窗口触发方式改成组合键，组合键模式也可工作
- PyInstaller 可构建 dist/Easy-translation.exe

## 3. 启动方式

### 3.1 源码启动

推荐命令：

```powershell
.\.venv312\Scripts\python.exe app.py
```

### 3.2 VS Code 任务启动

使用 .vscode/tasks.json 中的任务：

- 运行源码版 Easy-translation

### 3.3 打包启动

仓库已有 PyInstaller 配置文件 Easy-translation.spec，可用于构建 exe。

### 3.4 相关文档入口

- 快速上手：QUICKSTART.md
- 部署说明：DEPLOYMENT.md
- 测试说明：TESTING.md
- 发布说明：RELEASE_NOTES.md
- 用户入口：../README.md
- 变更记录：CHANGELOG.md

## 4. 核心模块职责

### 4.1 app.py

程序入口，仅负责注入项目根目录并调用主窗口 main。

### 4.2 main_window.py

主窗口和主工作流控制器，负责：

- 设置对话框
- 全局热键注册
- 三击空格检测接线
- 剪贴板监听接线
- 截图 OCR 翻译流程
- 外部输入框文本抓取与回填
- 后台翻译线程

这是当前最核心、改动最多的文件。

### 4.3 translator_core.py

翻译核心，负责：

- 统一翻译入口
- 智能中英方向判断
- Google / 百度 / 腾讯 / Ollama 调用
- 主结果结构化输出
- 简单内存缓存

当前建议优先通过 translate_result() 扩展新能力，而不是继续只围绕 translate() 做单字符串处理。

### 4.4 settings_manager.py

负责本地设置持久化和 API 密钥加密存储。

关键点：

- 设置文件为 user_settings.json
- 密钥文件为 .settings.key
- API 密钥通过 cryptography.fernet 加密
- 默认值通过 DEFAULT_SETTINGS 管理
- Tesseract 路径默认允许为空

### 4.5 config.py

负责运行时配置常量和设置合并。

注意：

- 运行时配置来源不是单纯写死在文件里的常量
- 真正生效值来自 settings_manager.reload_settings() 与默认配置的合并结果
- 修改设置后需要调用 reload_config() 重新同步

### 4.6 hotkey_manager.py

负责两类输入触发：

- HotkeyManager：组合键热键
- TripleClickDetector：三击空格检测

当前输入窗口翻译模式支持：

- triple_space
- ctrl/alt/shift + 字母数字
- ctrl/alt/shift + F1-F12
- ctrl/alt/shift + space / enter / tab / esc / backspace

### 4.7 clipboard_monitor.py

轮询剪贴板变化，并在内容变化时回调主窗口。

### 4.8 ocr_handler.py

负责截图 OCR 和 Tesseract 路径接入。

当前行为：

- Tesseract 是可选配置
- 优先使用设置页中的路径
- 如果未手填路径，会继续尝试系统 PATH 和 Windows 常见默认安装路径

## 5. 设置结构说明

当前重要设置项如下：

```json
{
  "default_api": "google",
  "current_api": "google",
  "source_lang": "auto",
  "target_lang": "__smart__ 或具体语言",
  "ocr_language": "chi_sim+eng",
  "tesseract_path": "...",
  "auto_clipboard_monitor": true,
  "translate_input_time_window": 1.2,
  "hotkeys": {
    "screenshot": "alt+shift+s",
    "clipboard": "alt+shift+c",
    "show_window": "alt+shift+t",
    "translate_input": "triple_space 或组合键"
  },
  "provider_settings": {
    "ollama": {
      "base_url": "http://127.0.0.1:11434",
      "model": "qwen2.5:7b",
      "timeout": 20
    }
  }
}
```

## 6. 输入窗口翻译机制

这是项目里最容易回归出问题的一段，建议后续开发重点关注。

### 6.1 默认模式

默认值是：

- hotkeys.translate_input = triple_space

此时会启用 TripleClickDetector，在配置窗口期内连续按 3 次空格后触发翻译。

### 6.2 组合键模式

如果将 hotkeys.translate_input 改成组合键字符串，则：

- 不再启用 TripleClickDetector
- 改由 HotkeyManager 注册全局热键

### 6.3 外部输入框翻译流程

当焦点不在应用主输入框中时，触发输入窗口翻译会执行：

1. 向当前活动输入框发送 Ctrl+A
2. 发送 Ctrl+C
3. 从剪贴板读取抓取到的原文
4. 调用翻译线程
5. 翻译完成后将译文放入剪贴板
6. 对原输入框发送 Ctrl+A、Ctrl+V 完成回填
7. 恢复用户原始剪贴板内容

这一段强依赖目标程序是否支持标准文本快捷键。

## 7. 翻译结果机制

当前翻译结果统一走结构化格式：

```python
{
    'primary': '主译文',
    'source_lang': 'zh',
    'target_lang': 'en',
}
```

说明：

- 所有翻译源当前都统一返回单结果
- 外部输入框回填使用主结果

## 8. 已知注意事项

### 8.1 PyQt6 DLL 问题

Windows 上为避免 PyQt6 Qt DLL 加载失败，main_window.py 启动时会提前配置 Qt6/bin 路径。

### 8.2 Python 版本建议

当前推荐 Python 3.12。项目曾处理过 Python 3.14 下 pytesseract 兼容性问题，但当前已不作为主要运行目标。

### 8.3 托盘图标提示

当前已设置应用图标资源，主窗口、托盘和打包 exe 会统一使用 Easy-translation 图标。

### 8.4 全局热键冲突

某些软件会拦截系统热键，或阻止标准 Ctrl+A / Ctrl+C / Ctrl+V 行为，这会影响外部输入框翻译成功率。

### 8.5 Tesseract 可选配置

- 未安装 Tesseract 时，应用仍可正常启动和保存设置
- 只有截图 OCR 功能会受影响
- OCR 初始化会依次尝试：手动配置路径、系统 PATH、Windows 常见默认安装路径

## 9. 推荐扩展方向

建议后续开发优先级如下：

1. 为输入窗口翻译增加录制热键功能
2. 为三击空格增加更明确的运行日志或调试开关
3. 增加开机自启或托盘常驻相关设置项
4. 将翻译线程管理进一步封装，减少 main_window.py 复杂度
5. 为外部输入抓取流程增加失败原因分类

## 10. 交接建议

如果新开发者要继续迭代，建议先读以下文件：

1. main_window.py
2. translator_core.py
3. settings_manager.py
4. hotkey_manager.py
5. README.md

然后优先手动验证以下场景：

1. 输入框直接翻译
2. 三击空格触发外部输入框翻译
3. 组合键触发外部输入框翻译
4. 剪贴板翻译
5. 截图 OCR 翻译
6. Ollama 翻译结果返回
