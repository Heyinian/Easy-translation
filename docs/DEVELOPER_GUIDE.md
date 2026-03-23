# 开发者归档文档

> 新接手者请先阅读 [PROJECT_STATUS.md](PROJECT_STATUS.md)，5 分钟内了解当前版本状态、已知 Bug 和架构总览，再回到本文查阅模块细节。

---

## 文档导航

| 文档 | 用途 |
|------|------|
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | **首选入口** — 当前版本、Bug 列表、架构速查 |
| [CHANGELOG.md](CHANGELOG.md) | 版本演进与功能归档（增量追加） |
| [TESTING.md](TESTING.md) | 功能测试清单与回归重点 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | 安装、打包、分发 |
| [QUICKSTART.md](QUICKSTART.md) | 5 步内启动项目 |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | 用户可见版本变化 |
| [../README.md](../README.md) | 项目用户入口 |

---

## 1. 项目定位与技术栈

**Easy-translation** 是仅限 Windows 的桌面翻译工具，核心依赖如下：

| 依赖 | 版本约束 | 用途 |
|------|---------|------|
| PyQt6 | >=6.7.0 | GUI 框架 |
| pynput | 1.7.6 | 全局键盘监听 |
| pyperclip | 1.8.2 | 剪贴板读写 |
| cryptography | 44.0.2 | API 密钥加密（Fernet） |
| Pillow | 10.1.0 | 截图处理 |
| pytesseract | 0.3.10 | OCR 封装（需另装 Tesseract） |
| requests | 2.31.0 | HTTP 调用翻译 API |

推荐运行环境：Python 3.12，虚拟环境目录 `.venv312`。

---

## 2. 模块职责详解

### 2.1 app.py（入口）

唯一职责：将 `src/` 注入 `sys.path`，然后调用 `main_window.main()`。不包含任何业务逻辑。

> 所有业务模块均在 `src/` 目录下。`src/` 中的模块可通过模块名直接相互导入（如 `from config import ...`），无需相对导入。

### 2.2 main_window.py（核心控制器）⭐

**最核心、改动最频繁的文件（~1200 行）。** 包含四个主要类：

#### MainWindow

| 职责域 | 关键方法 |
|--------|----------|
| 初始化与 UI 构建 | `init_ui()`, `setup_tray()` |
| 热键接线 | `setup_hotkeys()`, `_restart_translate_input_detector()` |
| 翻译流程编排 | `do_translation()`, `on_translation_result()` |
| 外部输入框抓取 | `capture_text_from_active_input()`, `_foreground_has_text_input()` |
| 外部输入框回填 | `replace_text_in_active_input()`, `_clear_external_selection()` |
| 三击空格抑制 | `_suppress_triple_space_detection()` |
| 剪贴板协作 | `on_clipboard_change()`, `on_clipboard_translate()` |
| 单实例唤醒 | `show_window()` |
| 生命周期 | `quit_app()`, `closeEvent()`, `changeEvent()` |

#### SettingsDialog

完整设置 UI，所有设置修改都在此对话框内完成后再批量写入 `settings_manager`。

#### TranslationWorker

`QObject` + `QThread` 组合，避免翻译 I/O 阻塞 UI 线程。翻译完成通过 `result_ready` 信号传回主线程。

#### SingleInstanceManager

基于 `QLocalServer` / `QLocalSocket` 的单实例保护，首个实例监听命名管道，后续实例发 `SHOW` 消息后立即退出。

---

### 2.3 translator_core.py（翻译引擎）

`TranslatorCore` 类统一封装所有翻译源，对外只暴露两个入口：

- `translate(text, source, target) -> str | None`：返回字符串，兼容旧代码
- `translate_result(text, source, target) -> dict | None`：返回结构化结果，**推荐使用**

结构化结果格式：
```python
{'primary': '译文', 'source_lang': 'zh', 'target_lang': 'en'}
```

内部结构：
```
TranslatorCore
  ├── _resolve_translation_direction()  # 智能中英方向判断
  ├── _translate_google()               # Google 翻译（SimpleGoogleTranslate 辅助类）
  ├── _translate_baidu()                # 百度翻译
  ├── _translate_tencent()              # 腾讯翻译
  └── _translate_ollama_result()        # Ollama 本地 AI 翻译
```

**新增翻译源**：在 `config.py` → `TRANSLATION_APIS` 注册，在此类中增加对应 `_translate_xxx()` 方法，并在 `translate_result()` 的 dispatch 中接入即可。

---

### 2.4 settings_manager.py（设置管理）

- 设置文件：`runtime/user_settings.json`（明文 JSON，API 密鑰字段已加密）
- 密鑰文件：`runtime/.settings.key`（Fernet 密鑰，需与 `user_settings.json` 配套）
- 默认值：`DEFAULT_SETTINGS` 字典，所有读取操作都会 fallback 到此
- 对外接口：`get_all_settings()`, `save_settings()`, `update_setting()`, `get_provider_settings()`, `validate_*`
- 重要：修改设置后必须调用 `config.reload_config()` 才能让运行时配置同步

---

### 2.5 config.py（运行时配置）

不是静态常量文件。`reload_config()` 每次调用都会重新从 `settings_manager` 读取并合并默认值，更新模块级全局变量（`HOTKEYS`、`DEFAULT_API` 等）。

**修改设置后的正确调用顺序**（见 `open_settings_dialog`）：
```python
settings_manager.save_settings(settings)
config.reload_config()
self.apply_runtime_settings_to_ui()
self.restart_hotkeys()
```

---

### 2.6 hotkey_manager.py（热键与三击检测）

#### HotkeyManager

通过 `pynput.Listener` 监听全局按键，维护 `pressed_keys` 集合和 `active_hotkeys` 去重集合，避免组合键重复触发。

#### TripleClickDetector

- 维护 `click_times` 时间戳列表，在 `time_window` 秒内累计 3 次空格触发回调
- **抑制机制**：`_suppression_count` 引用计数器，内部模拟按键时必须通过 `suppress_detection()` 上下文管理器将其递增，防止内部按键污染计数
- 非空格且非修饰键会重置 `click_times`，修饰键（Ctrl/Alt/Shift 等）不重置
- 调试日志：`logs/triple_space.log`

---

### 2.7 clipboard_monitor.py（剪贴板监听）

后台线程轮询剪贴板，内容变化时触发回调。注意：`ClipboardMonitor.last_clipboard` 在抓取/回填流程中被主动维护，用于配合哨兵值机制，**不要轻易修改此字段的维护逻辑**。

---

### 2.8 ocr_handler.py（OCR）

- Tesseract 为**可选**依赖，未安装时不影响启动
- `configure_tesseract()` 依次尝试：手动配置路径 → 系统 PATH → Windows 常见默认路径
- `OCRHandler.recognize_text_from_image()` 封装 pytesseract 调用
- `ScreenshotHandler.take_screenshot()` 负责截图并保存到 `screenshots/` 目录

---

## 3. 关键数据流

### 3.1 三击空格 → 外部输入框翻译回填

```
TripleClickDetector 按键监听线程
  │  连续3次空格，在 time_window 内
  ↓
callback()  →  translate_input_requested.emit()   # Qt 信号，跨线程安全
  ↓
MainWindow.on_global_translate_triggered()         # 主线程
  │
  ├─ 焦点在主窗口输入框？
  │   └─ 是 → do_translation()（直接翻译）
  │
  └─ 否 → capture_text_from_active_input()
            ├─ 设置哨兵值到剪贴板
            ├─ _foreground_has_text_input()        # Win32 API 检测文本光标
            ├─ suppress_detection('capture')
            │   ├─ Ctrl+C（先尝试）
            │   └─ 若无结果 + 有文本光标 → Ctrl+A + Ctrl+C
            └─ 返回 captured_text
          → do_translation(captured_text, replace_active_input=True)
          → TranslationWorker.run()                # QThread
          → on_translation_result(result)
          → replace_text_in_active_input(translated_text)
              ├─ suppress_detection('replace')
              ├─ Ctrl+A + Ctrl+V
              ├─ _clear_external_selection()        # Right 键消除全选
              └─ 恢复原始剪贴板
```

### 3.2 设置修改流程

```
SettingsDialog.accept()
  → settings_manager.save_settings(new_settings)  # 写 JSON + 加密密钥
  → config.reload_config()                         # 更新模块全局变量
  → apply_runtime_settings_to_ui()                 # 更新 UI 控件状态
  → restart_hotkeys()                              # 重建 HotkeyManager + TripleClickDetector
```

---

## 4. 文件与目录约定

| 路径 | 类型 | 说明 |
|------|------|------|
| `runtime/user_settings.json` | 运行时生成 | 用户设置持久化，包含加密 API 密鑰 |
| `runtime/.settings.key` | 运行时生成 | Fernet 加密密鑰，需与 settings.json 配套 |
| `runtime/logs/triple_space.log` | 运行时生成 | 三击空格调试日志 |
| `runtime/screenshots/` | 运行时生成 | 截图临时文件 |
| `assets/easy-translation.ico` | 版本库 | Windows 应用图标 |
| `assets/easy-translation.png` | 版本库 | PNG 备用图标 |
| `Easy-translation.spec` | 版本库 | PyInstaller 打包配置 |

---

## 5. 已知注意事项

### 5.1 PyQt6 DLL 问题

`main_window.py` 顶部 `_configure_qt_dll_path()` 在 import PyQt6 之前将 Qt6/bin 注入 `os.add_dll_directory`。**不要删除或移动这段代码。**

### 5.2 三击空格在 Electron / 浏览器类应用中成功率

这类应用自绘光标，不走 Win32 caret API，`_foreground_has_text_input()` 通过类名白名单识别。如需扩展支持，在 `web_render_classes` 集合中追加窗口类名（可用 Spy++ 或 `GetClassName` 获取）。

### 5.3 多显示器居中

当前 `init_ui` 根据 `primaryScreen` 居中，多显示器下窗口会出现在主屏而非用户当前使用的屏幕（已记录为 B-003，待处理）。

### 5.4 ClipboardMonitor 与主流程的协同

抓取/回填过程中，`_clipboard_capture_in_progress` 标志会临时屏蔽 `on_clipboard_change` 的自动翻译逻辑，避免剪贴板内容被中间值误触发翻译。**新增剪贴板操作时，注意维护此标志。**

---

## 6. 推荐扩展方向

按优先级排序：

1. **F-001**：设置页"录制热键"功能（中优先级）
2. **F-004**：外部输入框抓取失败原因分类提示（中优先级）
3. **B-001**：扩展 `web_render_classes` 白名单支持更多 Electron 应用（中优先级）
4. **F-002**：开机自启选项（低优先级）
5. **F-003**：翻译历史记录（低优先级）

> 完整列表见 [PROJECT_STATUS.md](PROJECT_STATUS.md) → 第 4 节。

---

## 7. 接手验证清单

新开发者接手后，建议按顺序手动验证以下场景，确认当前构建可用：

- [ ] 应用可从 `app.py` 正常启动
- [ ] 主窗口出现在屏幕正中央
- [ ] 主输入框手动翻译正常
- [ ] 剪贴板翻译正常
- [ ] 三击空格在记事本中触发，原文被译文替换
- [ ] 三击空格在游戏/媒体播放器前台时**不**触发全选
- [ ] 关闭主窗口后应用仍可从托盘恢复
- [ ] 重复启动时不出现第二个实例
- [ ] 设置保存后热键立即生效
- [ ] 截图 OCR 正常（需 Tesseract）


## 1. 项目当前定位

本项目是一个 Windows 桌面翻译工具，基于 PyQt6 实现，当前已具备以下能力：

- 文本输入翻译
- 剪贴板翻译
- 截图 OCR 翻译
- 外部输入框翻译回填
- 多翻译源切换
- 本地加密设置存储
- Ollama 本地翻译接入
- 单实例存在检查

当前推荐运行环境是 Python 3.12，对应本地虚拟环境为 .venv312。

## 2. 当前可运行状态

截至当前归档版本，已验证以下事项：

- 源码版可从 app.py 正常启动
- .vscode/tasks.json 中已存在“运行源码版 Easy-translation”任务
- 默认输入窗口翻译触发方式为 triple_space
- 三击空格窗口期当前默认配置为 1.2 秒
- 如果将输入窗口触发方式改成组合键，组合键模式也可工作
- 重复启动时不会保留多个实例，后启动实例会唤醒主实例后退出
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
- 单实例激活请求接入

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

### 4.9 单实例机制

当前通过 QLocalServer / QLocalSocket 实现单实例保护：

- 首个实例启动后监听本地命名通道
- 后续实例启动时会向主实例发送 `SHOW` 请求
- 主实例收到请求后显示主窗口
- 后续实例立即退出，不会保留重复进程

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

### 8.4.1 三击空格稳定性

- 三击空格触发后不再预先向外部输入框发送 3 次 `Backspace`
- 当前改为先抓取文本，再在内存中裁掉尾部 3 个触发空格
- 内部模拟按键期间会临时抑制 `TripleClickDetector`，避免内部按键污染计数
- 抓取失败时会自动重试一次 `Ctrl+A + Ctrl+C`，再回退到“仅复制当前选中文本”
- 调试日志统一写入 `logs/triple_space.log`

### 8.5 Tesseract 可选配置

- 未安装 Tesseract 时，应用仍可正常启动和保存设置
- 只有截图 OCR 功能会受影响
- OCR 初始化会依次尝试：手动配置路径、系统 PATH、Windows 常见默认安装路径

### 8.6 单实例限制

- 单实例保护依赖本地命名通道
- 如果主实例异常崩溃，启动时会先清理残留 server 名称再重新监听
- 当前重复启动时只负责唤醒主窗口，不做参数透传

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
7. 重复启动时是否只保留一个实例并唤醒主窗口
