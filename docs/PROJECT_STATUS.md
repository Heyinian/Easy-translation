# 项目当前状态（AI 开发快速接入文档）

> **本文档是异地 AI 开发者接入的第一入口。** 阅读本文后，应能在 5 分钟内了解项目全貌、当前可用状态、待处理问题和开发约定，无需再翻其他文件即可开始工作。

---

## 1. 项目一句话定位

**Easy-translation** 是一个 Windows 桌面翻译工具，基于 PyQt6 实现，支持多翻译源、全局热键触发、外部输入框翻译回填、截图 OCR 翻译，并可常驻系统托盘后台运行。

---

## 2. 当前版本与状态

| 项目 | 值 |
|------|-----|
| 当前版本 | **v0.5.8** |
| 最后归档日期 | 2026-03-26 |
| 运行平台 | Windows（仅支持） |
| 推荐 Python | 3.12（.venv312） |
| 整体状态 | ✅ 可正常启动并完成核心功能 |

---

## 3. 已实现功能清单

| 功能 | 状态 | 触发方式 |
|------|------|----------|
| 主窗口手动翻译 | ✅ 稳定 | 界面按钮 |
| 剪贴板自动监听翻译 | ✅ 稳定 | 自动 / Alt+Shift+C |
| 外部输入框翻译回填 | ✅ 稳定 | 三击空格 / 组合键 |
| 截图 OCR 翻译 | ✅ 稳定（需 Tesseract） | Alt+Shift+S |
| 系统托盘后台运行 | ✅ 稳定 | 关闭/最小化主窗口 |
| 单实例保护 | ✅ 稳定 | 自动（重复启动时唤醒） |
| Google 翻译 | ✅ 稳定 | 无需配置 |
| 百度翻译 | ✅ 稳定 | 需要 API 密钥 |
| 腾讯翻译 | ✅ 稳定 | 需要 API 密钥 |
| Ollama 本地 AI 翻译 | ✅ 稳定 | 需本地 Ollama 服务 |
| 智能中英方向检测 | ✅ 稳定 | 自动 |
| API 密钥本地加密存储 | ✅ 稳定 | 自动 |
| 设置界面 | ✅ 稳定 | 界面按钮 / 托盘菜单 |
| 最小 automated smoke baseline | ✅ 已接入 | `scripts/run_smoke_tests.ps1` |

---

## 4. 当前已知 Bug 与待处理事项

### 4.1 已修复（v0.5.3，2026-03-23）

| Bug | 修复方式 |
|-----|----------|
| 三击空格在非文本窗口（游戏、媒体播放器等）触发 Ctrl+A，导致应用内容全选变成蓝色高亮 | 新增 `_foreground_has_text_input()` 检测前台窗口文本光标，无光标时跳过 Ctrl+A |
| 软件启动时窗口固定在 (100, 100)，不在屏幕中央 | 改为根据主屏幕分辨率动态计算居中坐标 |
| PyQt6==6.6.1 与自动安装的 PyQt6-Qt6==6.10.x 版本不兼容，启动时报 DLL load failed | requirements.txt 改为 `PyQt6>=6.7.0` |

### 4.2 待处理 Bug（已知，未修复）

> 如有新 Bug 发现，追加到此表，格式保持一致。

| ID | 描述 | 严重程度 | 相关文件 | 备注 |
|----|------|----------|----------|------|
| B-002 | 外部输入框翻译回填后，`_clear_external_selection` 发送的 Right 键在某些富文本编辑器中会移动光标位置 | 低 | `src/main_window.py` → `_clear_external_selection` | 可考虑改为发送 Escape 或什么都不做 |
| B-003 | 多显示器环境下，窗口居中计算仅基于 `primaryScreen`，窗口会出现在主屏而非用户当前使用的屏幕 | 低 | `src/main_window.py` → `init_ui` | 可改为根据当前鼠标所在屏幕居中 |

### 4.3 待开发功能（规划中）

| ID | 描述 | 优先级 |
|----|------|--------|
| F-001 | 设置页增加"录制热键"功能，支持通过按键方式设置快捷键，代替手动输入字符串 | 中 |
| F-002 | 增加开机自启选项（注册 Windows 启动项） | 低 |
| F-003 | 翻译历史记录（最近 N 条） | 低 |
| F-004 | 为外部输入框抓取增加失败原因分类提示（区分"无焦点"、"无文本"、"剪贴板未变化"） | 中 |
| F-005 | 三击空格触发后增加视觉反馈（托盘图标短暂变化 / 气泡提示） | 低 |

---

## 5. 架构快速参考

```
app.py                    # 程序入口，仅调用 main_window.main()
main_window.py            # ★ 核心控制器，最复杂最常改的文件（~1200 行）
  ├── MainWindow           # 主窗口 + 托盘 + 热键接线 + 翻译流程编排
  ├── SettingsDialog       # 设置对话框
  ├── TranslationWorker    # 后台翻译线程（QThread）
  └── SingleInstanceManager # 单实例 QLocalServer 保护
translator_core.py        # 翻译引擎适配层（Google/百度/腾讯/Ollama + 缓存）
settings_manager.py       # 设置持久化 + Fernet 加密 API 密钥
config.py                 # 运行时配置常量 + reload_config()
hotkey_manager.py
  ├── HotkeyManager        # 组合键全局热键（pynput Listener）
  └── TripleClickDetector  # 三击空格检测（带抑制计数器）
clipboard_monitor.py      # 剪贴板轮询监听线程
ocr_handler.py            # Tesseract 封装 + 截图处理
assets/                   # 图标资源（.ico / .png）
```

### 数据流图（外部输入框翻译路径）

```
用户三击空格
  → TripleClickDetector.callback
  → translate_input_requested.emit()          # 跨线程信号
  → MainWindow.on_global_translate_triggered()
      ├─ 判断焦点是否在主窗口输入框
      │   └─ 是 → 直接翻译主输入框内容
      └─ 否 → capture_text_from_active_input()
              ├─ _foreground_has_text_input()  # 检测前台窗口文本光标
              ├─ Ctrl+C（先尝试复制当前选中）
              ├─ 若无结果 + 有文本光标 → Ctrl+A + Ctrl+C
              └─ 返回抓取到的原文
          → do_translation(text, replace_active_input=True)
          → on_translation_result()
          → replace_text_in_active_input()
              ├─ 复制译文到剪贴板
              ├─ Ctrl+A + Ctrl+V 回填
              ├─ _clear_external_selection() → Right 键消除全选
              └─ 恢复用户原始剪贴板
```

---

## 6. 关键实现细节（避坑清单）

### 6.1 三击空格检测抑制机制

`TripleClickDetector` 有一个引用计数式抑制器（`_suppression_count`），所有内部模拟按键操作（Ctrl+A/C/V、Right）**必须**在 `suppress_detection()` 上下文中执行，否则内部按键会污染三击计数。

```python
# 正确用法
with self._suppress_triple_space_detection('my_reason'):
    self._press_key_sequence(Key.ctrl, 'a')
```

### 6.2 前台窗口文本光标检测

`_foreground_has_text_input()` 通过 `GetGUIThreadInfo` 检测 Win32 caret，并额外识别以下浏览器渲染类（自绘光标，不走 Win32 caret API）：
- `Chrome_RenderWidgetHostHWND`（Chrome / Edge / Electron）
- `MozillaWindowClass`（Firefox）

如需支持更多应用，在此方法的 `web_render_classes` 集合中追加类名。

### 6.3 剪贴板哨兵值

抓取前会设置唯一哨兵值到剪贴板，通过检测剪贴板是否从哨兵值变化来判断 Ctrl+C 是否成功，避免误读历史剪贴板内容。

### 6.4 PyQt6 Qt DLL 路径问题

`main_window.py` 顶部的 `_configure_qt_dll_path()` 函数会在 import PyQt6 之前将 Qt6/bin 注入 `os.add_dll_directory`，解决 Windows 下 DLL 找不到的问题。**不要删除这段代码。**

### 6.5 设置生效时序

修改设置后，必须按顺序执行：
1. `settings_manager.save_settings(settings)`
2. `config.reload_config()`
3. `self.apply_runtime_settings_to_ui()`
4. `self.restart_hotkeys()`

### 6.6 翻译结果结构

所有翻译源统一返回：
```python
{'primary': '译文', 'source_lang': 'zh', 'target_lang': 'en'}
```
外部回填使用 `result['primary']`。

---

## 7. 本地环境快速启动

```powershell
# 进入项目目录
cd G:\GitHub\Easy-translation

# 创建虚拟环境（使用 uv 管理的 Python 3.12）
& "C:\Users\wuyuli\AppData\Roaming\uv\python\cpython-3.12.11-windows-x86_64-none\python.exe" -m venv .venv312
# 或 py -3.12 -m venv .venv312（如果系统 py launcher 能找到 3.12）

# 安装依赖
.\.venv312\Scripts\pip install -r requirements.txt

# 启动
.\.venv312\Scripts\python.exe app.py
```

> **注意**：requirements.txt 中 PyQt6 版本约束为 `>=6.7.0`，pip 会自动安装与 PyQt6-Qt6 匹配的最新版本，无需手动处理。> `runtime/` 目录在第一次启动时自动创建，全部内容已被 `.gitignore` 排除。
---

## 8. 调试入口

| 问题 | 调试入口 |
|------|----------|
| 三击空格不触发 / 误触发 | `runtime/logs/triple_space.log` |
| 翻译 API 异常 | `src/translator_core.py` → `last_error` 属性 |
| 设置未生效 | `runtime/user_settings.json` 和 `config.reload_config()` 返回值 |
| 截图 OCR 失败 | 设置页 Tesseract 路径 / `src/ocr_handler.py` → `configure_tesseract()` |

---

## 9. 文档体系导航

| 文档 | 面向对象 | 核心内容 |
|------|----------|----------|
| **PROJECT_STATUS.md**（本文） | AI 开发者 / 接手者 | 项目状态、Bug 列表、架构速查 |
| [app_developer_guide.md](app_developer_guide.md) | 深度开发者 | 模块详解、扩展建议、交接清单 |
| [CHANGELOG.md](CHANGELOG.md) | 所有开发者 | 版本演进与功能归档 |
| [TESTING.md](TESTING.md) | 测试 / QA | 功能测试清单与回归重点 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | 部署 / 实施 | 安装、打包、分发说明 |
| [QUICKSTART.md](QUICKSTART.md) | 新手 | 5 步内启动项目 |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | 用户 / 维护者 | 用户可见版本变化 |
