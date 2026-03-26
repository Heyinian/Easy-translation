# Easy-translation 工作区全局开发规则

本文件对所有 AI 开发会话强制生效。所有规则均为**阻塞性约束**，违反即视为会话未完成。

---

## 自动运行规则（BLOCKING）

**每次完成任何源代码修改并完成归档后，必须自动执行以下步骤启动最新源码版进行验证：**

1. 关闭当前所有正在运行的源码版进程（若存在）
2. 在终端运行命令：`.\.venv312\Scripts\python.exe app.py`（后台模式）
3. 等待 3-5 秒后检查日志文件 `runtime/logs/triple_space.log` 末尾，确认 `TripleClickDetector started` 出现即为启动成功

> 不需要等待用户开口请求"载入测试"——每次代码修改后直接自动启动。

---

## 核心约束：开发归档（BLOCKING）

**每次完成任何源代码修改后，在结束会话之前，必须完整执行以下归档步骤，缺一不可。**

> 判定标准：只要本次会话中有代码文件（`.py`）被修改、新增或删除，就必须归档。
> 仅修改文档（`.md`）或配置注释时，可只更新 CHANGELOG 和 PROJECT_STATUS，不需要版本号递增。

---

### 归档步骤（强制，不可跳过）

#### 步骤 1：确定版本号

遵循本项目版本策略（轻量语义化）：
- **路径 A（有代码修改）**：取 `docs/PROJECT_STATUS.md` 中当前版本号，递增最后一位（patch）。例：v0.5.3 → v0.5.4
- **路径 B（仅文档修改）**：版本号不变，仅记录"文档更新"条目

#### 步骤 2：更新 `docs/PROJECT_STATUS.md`

必须更新的字段：
- `当前版本` → 新版本号
- `最后归档日期` → 今日日期（YYYY-MM-DD）
- `已知 Bug 追踪表`：
  - 本次修复的 Bug → 从表中删除（移入 CHANGELOG 的"已修复"节）
  - 本次发现的新 Bug → 追加新行，分配自增 ID（`B-NNN`）
- `待开发功能规划表`：
  - 本次实现的功能 → 从表中删除（移入 CHANGELOG 的"新增功能"节）
  - 本次新增的规划 → 追加新行，分配自增 ID（`F-NNN`）

#### 步骤 3：在 `docs/CHANGELOG.md` 顶部新增版本块

版本块格式（**必须严格遵守**，追加在 `## 版本说明` 块之后，已有版本块之前）：

```markdown
## v{版本号} - {YYYY-MM-DD}

### 新增功能
- （若无则写"无"）

### Bug 修复
- **{问题简要标题}**：{一句话描述问题根因} → {一句话描述修复方式}，文件：`{文件名}.py`

### 文档与工程
- （若无则写"无"）

### 遗留问题
- （列出本次未解决但已知的 Bug，引用 B-NNN ID；若无则写"无"）

---
```

禁止：
- ❌ 修改已有版本块的任何内容
- ❌ 删除历史版本块
- ❌ 合并多个版本的改动到一个版本块

#### 步骤 4：按需更新 `docs/app_developer_guide.md`

**触发条件（满足任一即需更新）：**
- 新增或删除了模块/类/关键方法
- 修改了跨模块数据流
- 新增了需要后续开发者注意的"避坑点"
- 修改了关键实现细节（如抑制机制、哨兵值逻辑、设置时序等）

**不需要更新的情况：**
- 仅为已有方法修复 Bug，模块职责和接口不变
- 仅修改 UI 文案或样式

#### 步骤 5：确认归档完整性

归档完成后，必须输出以下确认清单，不得省略任何一项：

```
✅ 归档确认清单
- 版本号：v{新版本号}（{变更前版本} → {变更后版本}）
- PROJECT_STATUS.md 已更新：版本号 / 日期 / Bug 表 / 功能表
- CHANGELOG.md 已新增：v{新版本号} 版本块（{N} 条修复 / {M} 条新增）
- app_developer_guide.md：{已更新 | 本次无需更新（原因）}
- 本次遗留 Bug：{B-NNN 列表 | 无}
```

---

## 代码规范约束

### Python 代码

- 使用 Python 3.12 语法，不使用 3.14+ 专有特性
- 内部模拟按键（Ctrl+A/C/V/Right 等）**必须**在 `suppress_detection()` 上下文中执行
- 所有跨线程信号传递使用 Qt signal，不直接在 pynput 回调线程中操作 Qt 对象
- 翻译结果统一使用结构化 dict：`{'primary': str, 'source_lang': str, 'target_lang': str}`
- 修改设置后必须按顺序调用：`save_settings → reload_config → apply_runtime_settings_to_ui → restart_hotkeys`

### 文档格式

- CHANGELOG.md：仅追加，不修改历史块
- PROJECT_STATUS.md：Bug 表和功能表使用自增 ID（`B-NNN` / `F-NNN`）
- 所有文档使用中文，代码注释、技术标识符保持英文

---

## 文档体系说明

| 文档 | 定位 |
|------|------|
| `docs/PROJECT_STATUS.md` | 当前状态快照（AI 接入首选入口） |
| `docs/CHANGELOG.md` | 版本历史（只追加） |
| `docs/app_developer_guide.md` | 模块详解 + 避坑清单 |
| `docs/TESTING.md` | 测试清单 |
| `docs/DEPLOYMENT.md` | 部署说明 |

详见 [docs/DOCS_INDEX.md](../docs/DOCS_INDEX.md)。

---

## 项目目录约定

```
Easy-translation/
├── app.py                # 入口（保持在根，将 src/ 注入 sys.path）
├── src/                  # 源码包（所有业务模块）
│   ├── __init__.py
│   ├── main_window.py
│   ├── translator_core.py
│   ├── settings_manager.py
│   ├── config.py
│   ├── hotkey_manager.py
│   ├── clipboard_monitor.py
│   └── ocr_handler.py
├── assets/               # 图标资源
├── docs/                 # 文档
├── runtime/              # 运行时自动生成，全部被 .gitignore 排除
│   ├── user_settings.json
│   ├── .settings.key
│   ├── logs/
│   └── screenshots/
├── .github/              # Copilot 规则、Prompt、Issue 模板
├── requirements.txt
├── Easy-translation.spec # PyInstaller 打包配置
└── .gitignore
```

**关键约定：**
- 新增源码模块一律放入 `src/`
- `runtime/` 目录下的所有内容都属于运行时生成，不得提交到仓库
- `src/config.py` 中 `PROJECT_ROOT = Path(__file__).parent.parent`，`RUNTIME_DIR = PROJECT_ROOT / 'runtime'`
