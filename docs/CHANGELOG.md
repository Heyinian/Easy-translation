# 变更记录

本文档记录当前项目的重要功能演进和结构调整，便于后续开发者快速回溯历史脉络。

## 版本说明

- 当前版本：v0.5.9
- 版本策略：当前采用轻量语义化版本记录文档与功能阶段，不严格绑定发布包。

---

## v0.5.9 - 2026-03-26

### 新增功能
- 无

### Bug 修复
- 无

### 文档与工程
- **AI 翻译规划入库**：新增 `docs/ai_translation_profile_plan.md`，把 AI 场景翻译 profile、`BYOK` 兼容 provider 与可选候选词悬浮窗的方案、边界和 token 成本约束收敛为正式设计文档
- **任务体系扩展**：`docs/backlog.md` 与 `docs/PROJECT_STATUS.md` 新增 `ET-FEAT-002`、`ET-FEAT-003`、`ET-FEAT-004` 及对应规划项，覆盖 AI profile、`BYOK` provider 和候选词悬浮窗
- **发布检查点刷新**：同步 `README.md`、`docs/current_status.md`、`docs/RELEASE_NOTES.md`、`docs/RELEASE_DRAFT.md`、`config/project/current_project.json` 等版本落点，并重新生成 Windows release 包

### 遗留问题
- B-002：`_clear_external_selection` Right 键在富文本编辑器中移动光标
- B-003：多显示器下窗口居中基于主屏而非鼠标所在屏

---

## v0.5.8 - 2026-03-26

### 新增功能
- 无

### Bug 修复
- 无

### 文档与工程
- **开发骨架接入**：以 `project-owned` 方式接入 `AIProjectSkeleton` 的 canonical 文档、repo hygiene 脚本、CI 工作流、配置样例和 prompt 模板，形成稳定的协作入口，文件：`docs/START_HERE.md`、`docs/current_status.md`、`docs/backlog.md`、`docs/roadmap.md`、`scripts/*.ps1`、`.github/workflows/repo-hygiene.yml`
- **最小自动化冒烟测试**：新增 `tests/test_smoke_baseline.py` 与 `scripts/run_smoke_tests.ps1`，覆盖入口路径注入、配置加载、runtime 隔离与翻译核心基础无网络行为
- **测试隔离能力**：`src/config.py` 与 `src/settings_manager.py` 新增 `EASY_TRANSLATION_RUNTIME_DIR` 环境变量支持，使自动化测试可在临时 runtime 目录中运行而不污染本地数据
- **文档体系调整**：原业务实现深度文档保留并迁移为 `docs/app_developer_guide.md`，README、测试与归档提示同步改到新路径

### 遗留问题
- B-002：`_clear_external_selection` Right 键在富文本编辑器中移动光标
- B-003：多显示器下窗口居中基于主屏而非鼠标所在屏

---

## v0.5.7 - 2026-03-23

### 新增功能
- 无

### Bug 修复
- **三击空格在绝大多数应用文本框中失效**：`_foreground_has_text_input()` 依赖 Win32 caret API 检测文本焦点，但现代应用框架（WPF、Qt、UWP、Electron 等）均不使用 Win32 caret，导致约 95% 的应用被误判为"非文本窗口"而跳过 Ctrl+A 步骤 → 改用窗口句柄对比策略：记录触发时的前台窗口句柄，只要发送 Ctrl+C 后窗口未切换就进行 Ctrl+A，彻底解决现代应用兼容性问题，同时保留焦点漂移保护（防止误全选背景应用），文件：`src/main_window.py`

### 文档与工程
- 无

### 遗留问题
- B-002：`_clear_external_selection` Right 键在富文本编辑器中移动光标
- B-003：多显示器下窗口居中基于主屏而非鼠标所在屏

---

## v0.5.6 - 2026-03-23

### 新增功能
- 无

### Bug 修复
- **外部应用三击空格被误判为主窗口内部触发**：pynput 在驱动层拦截按键速度快于 Windows 向 Qt 发送 WM_KILLFOCUS，存在竞态导致 `hasFocus()` 返回旧值（True），误判客户在主窗口输入框。修复：新增 `_is_our_app_foreground()` 同时用 Win32 `GetForegroundWindow()` + `GetWindowThreadProcessId()` 查询系统级进程 ID，与 `hasFocus()` 做双重验证 → 彝彻规避竞态，文件：`src/main_window.py`

### 文档与工程
- 无

### 遗留问题
- B-001：Electron/浏览器类应用三击空格抓取成功率低
- B-002：`_clear_external_selection` Right 键在富文本编辑器中移动光标
- B-003：多显示器下窗口居中基于主屏而非鼠标所在屏

---

## v0.5.5 - 2026-03-23

### 新增功能
- 无

### Bug 修复
- **PyInstaller 打包后任务栏/托盘图标丢失**：`config.py` 中 `Path(__file__).parent.parent` 在 onefile 模式下指向系统临时目录，导致 assets 路径错误 → 检测 `sys.frozen` 标志，冻结环境下改用 `Path(sys._MEIPASS) / 'assets'`，文件：`src/config.py`
- **PyInstaller 打包后关闭窗口无法后台运行**：托盘图标因 assets 路径错误无法设置图标，`QSystemTrayIcon.show()` 静默失败，关闭窗口后应用消失 → 同上修复 assets 路径后托盘图标恢复正常，文件：`src/config.py`
- **PyInstaller 打包后三击空格翻译失效**：`pynput.keyboard._win32` 和 `pynput.mouse._win32` 未被自动识别并打入包，pynput 无法初始化键盘监听器 → 在 spec 中添加 `hiddenimports=['pynput.keyboard._win32', 'pynput.mouse._win32']`，文件：`Easy-translation.spec`
- **运行时目录位置错误**：`settings_manager.py` 的路径计算与 `config.py` 相同问题 → 检测冻结环境，改用 `Path(sys.executable).parent / 'runtime'` 作为运行时目录，文件：`src/settings_manager.py`

### 文档与工程
- 无

### 遗留问题
- B-001：Electron/浏览器类应用三击空格抓取成功率低
- B-002：`_clear_external_selection` Right 键在富文本编辑器中移动光标
- B-003：多显示器下窗口居中基于主屏而非鼠标所在屏

---

## v0.5.4 - 2026-03-23

### 新增功能
- 无

### Bug 修复
- 无

### 文档与工程
- **项目结构重组**：将全部源码模块（7 个 `.py` 文件）从根目录迁入 `src/` 包，`app.py` 保留在根目录作为唯一入口并通过 `sys.path` 注入 `src/`
- **运行时数据统一**：新建 `runtime/` 目录，将 `logs/`、`screenshots/`、`user_settings.json`、`.settings.key` 统一迁入，`.gitignore` 改为整体排除 `runtime/`
- **路径配置更新**：`src/config.py` 中 `PROJECT_ROOT = Path(__file__).parent.parent`，新增 `RUNTIME_DIR = PROJECT_ROOT / 'runtime'`；`src/settings_manager.py` 同步更新路径
- **PyInstaller 配置更新**：`Easy-translation.spec` 中 `pathex` 新增 `'src'`，确保打包时正确解析模块
- **归档规则文件**：`.github/copilot-instructions.md` 新增项目目录约定章节，明确 `src/`、`runtime/` 的使用规范

### 遗留问题
- B-001：浏览器/Electron 类应用三击空格成功率低
- B-002：_clear_external_selection 在富文本编辑器中可能移动光标
- B-003：多显示器环境下窗口居中仅基于 primaryScreen

---

## v0.5.3 - 2026-03-23

### Bug 修复

#### 三击空格在非文本窗口误触发全选

- **问题**：在打开非文本窗口（游戏、媒体播放器等）后三击空格，`capture_text_from_active_input` 无条件发送 `Ctrl+A`，导致后台有文本输入框的应用被全选，界面出现蓝色高亮覆盖
- **修复**：新增 `_foreground_has_text_input()` 方法，通过 Windows API `GetGUIThreadInfo` 检测前台窗口是否存在活跃文本光标（Win32 caret），同时通过窗口类名识别 Chrome / Edge / Firefox 等自绘光标的浏览器；仅在检测到文本输入焦点时才发送 `Ctrl+A`
- **文件**：`main_window.py`
- **抓取策略调整**：先发 `Ctrl+C`（无副作用），无结果且有文本光标才升级为 `Ctrl+A + Ctrl+C`；`_clear_external_selection` 的 Right 键也改为仅在执行了 `Ctrl+A` 时才发送

#### 主窗口启动不在屏幕中央

- **问题**：`init_ui` 中使用硬编码坐标 `setGeometry(100, 100, ...)` 定位窗口，无论屏幕分辨率如何，窗口总是出现在左上角附近
- **修复**：改为 `resize()` 设置尺寸后，通过 `QApplication.primaryScreen().geometry()` 动态计算居中坐标
- **文件**：`main_window.py`

#### PyQt6 版本锁定导致 DLL 加载失败

- **问题**：`requirements.txt` 将 PyQt6 锁定为 `==6.6.1`，但 pip 自动安装的 `PyQt6-Qt6==6.10.x` 与之不兼容，导致启动时报 `DLL load failed while importing QtCore`
- **修复**：放宽版本约束为 `PyQt6>=6.7.0`，`pip` 会自动解析匹配版本
- **文件**：`requirements.txt`

### 文档体系重构

- 新增 `docs/PROJECT_STATUS.md`：AI 开发者快速接入文档，包含当前版本状态、已知 Bug 列表、架构图、避坑清单
- `CHANGELOG.md` 改为以版本块归档，追加增量，不覆盖历史
- `DEVELOPER_GUIDE.md` 重写，强化模块职责说明和跨模块数据流

---

## v0.5.2 - 2026-03-21

### 三击空格稳定性修复

- 为三击空格链路增加 `logs/triple_space.log` 调试日志，覆盖计数、重置、抓取、替换和失败提示
- 忽略程序内部发出的 `Backspace`、`Ctrl+A/C/V`、`Right` 等按键，避免干扰三击空格计数
- 抓取外部输入框文本时增加剪贴板哨兵值、自动重试和“仅复制选中文本”回退路径
- 取消触发后预先向外部输入框发送 3 次 `Backspace` 的行为，改为只在内存中裁掉尾部触发空格
- 修复三击空格触发外部输入框翻译时可能误唤醒主窗口、误删文档或覆盖整段文本的问题

## v0.5.1 - 2026-03-21

### 品牌与资源统一

- 应用名称统一为 Easy-translation
- 新增应用图标资源，并接入主窗口、托盘和 PyInstaller 打包

### 后台托盘运行

- 关闭主窗口时自动切换到后台运行并保留托盘图标
- 最小化主窗口时也会自动切换到托盘后台运行
- 托盘菜单增加“翻译当前剪贴板”快捷入口
- 托盘右键菜单支持打开主界面、打开设置、退出应用

### 单实例保护

- 增加应用单实例存在检查，避免重复启动多个相同任务
- 第二次启动时会通知已运行实例显示主窗口并立即退出自身

### 功能收敛

- 移除候选译文功能，翻译结果统一为单结果输出

### OCR 配置调整

- Tesseract 改为可选配置，未安装时不再阻塞设置保存
- OCR 初始化会依次尝试手动路径、系统 PATH 和 Windows 常见默认安装路径

## v0.4.0 - 2026-03-21

### 文档体系整理

- 新增文档索引 DOCS_INDEX.md
- 为 README、QUICKSTART、DEVELOPER_GUIDE、DEPLOYMENT 增加文档导航
- 将变更记录切换为版本号格式维护

## v0.3.0 - 2026-03-21

### 文档归档完善

- 新增开发者归档文档 DEVELOPER_GUIDE.md
- 新增部署文档 DEPLOYMENT.md
- 新增 Markdown 版快速上手文档 QUICKSTART.md
- README.md 补充已完成功能归档与版本演进记录
- 删除旧的 QUICKSTART.py 伪文档脚本

### 输入窗口翻译机制完善

- 输入窗口翻译支持 triple_space 与组合键双模式
- 默认触发方式恢复为 triple_space
- 新增 translate_input_time_window 配置项
- 三击空格窗口期支持在设置页调整
- 组合键模式支持 ctrl/alt/shift + 字母数字、space、enter、tab、esc、backspace、F1-F12

### 运行时问题修复

- 修复点击翻译按钮时 clicked 信号传入 bool 导致 do_translation 报错的问题
- 修复旧三击空格逻辑残留导致外部输入框可能误删空格的问题
- 修复输入窗口翻译配置与运行时状态不同步导致的误判

### 外部输入框翻译能力

- 支持抓取当前外部输入框文本
- 支持翻译完成后回填至原输入框
- 支持在回填流程后恢复用户原始剪贴板内容

### 翻译核心增强

- Google 翻译结果解析修正
- 新增百度翻译支持
- 新增腾讯翻译支持
- 新增 Ollama 本地 AI 翻译支持
- 新增智能中英双向默认模式
- translate_result() 现在返回结构化主结果

### 设置系统与配置管理

- 新增 settings_manager.py
- 支持本地设置持久化
- 支持 API 密钥加密存储
- 支持运行时配置重载
- 设置页支持翻译源、OCR、热键、Tesseract、Ollama 等配置

### 环境与打包

- 推荐运行环境切换到 Python 3.12 / .venv312
- 处理 Windows 下 PyQt6 Qt DLL 路径问题
- 验证源码版启动链路
- 验证 PyInstaller 打包输出 exe

## v0.2.0 - 2026-03-21

### 设置与运行时配置

- 引入 settings_manager.py 管理本地设置和加密密钥
- 支持运行时配置重载
- 设置页支持翻译源、OCR、热键、Tesseract、Ollama 等配置

### 翻译能力扩展

- 修正 Google 翻译结果解析
- 增加百度翻译与腾讯翻译支持
- 增加智能中英双向默认模式

## v0.1.0 - 2026-03-21

### 初始可运行版本

- 建立 PyQt6 桌面翻译工具基础结构
- 支持主窗口文本翻译
- 支持剪贴板翻译
- 支持截图 OCR 翻译基础流程
- 支持系统托盘和基础热键
