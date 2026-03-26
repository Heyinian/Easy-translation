# Current Status

Last updated: `2026-03-26`

## Current Phase

`Phase 2 - Pre-Release Stabilization`

## Current Working Version

- `v0.5.8`

## Verified Reality

- 当前仓库已经是一个有实现代码的 Windows 桌面翻译应用，而不是空模板仓库
- 主执行入口仍然是 `app.py`
- 应用实现位于 `src/`，核心模块包括：
  - `main_window.py`
  - `translator_core.py`
  - `settings_manager.py`
  - `config.py`
  - `hotkey_manager.py`
  - `clipboard_monitor.py`
  - `ocr_handler.py`
- 当前已经具备的主要能力包括：
  - 手动输入翻译
  - 剪贴板监听翻译
  - 截图 OCR 翻译
  - 外部输入框内容抓取与回填
  - Google / 百度 / 腾讯 / Ollama 多翻译源切换
  - 系统托盘常驻与单实例保护
- 运行时本地数据仍存放在 `runtime/`，不应提交到仓库
- 原有的产品级技术交接文档已经保留到 `docs/app_developer_guide.md`
- 原有的产品状态与 Bug/功能规划文档继续保留在 `docs/PROJECT_STATUS.md`
- 当前仓库已经接入 `AIProjectSkeleton` 的 project-owned 治理骨架：
  - `docs/START_HERE.md`
  - `docs/current_status.md`
  - `docs/backlog.md`
  - `docs/roadmap.md`
  - `docs/versioning_policy.md`
  - `scripts/run_repo_hygiene_checks.ps1`
  - `.github/workflows/repo-hygiene.yml`
  - `docs/prompt_templates/`
- `config/project/current_project.json` 已声明 `bootstrap_finalized: true`
- 当前已具备最小本地 automated smoke baseline：
  - `tests/test_smoke_baseline.py`
  - `scripts/run_smoke_tests.ps1`
  - `tests/README.md`
- 依据已有项目文档，当前仍需关注的产品问题包括：
  - 外部输入框回填后用于清除选中的方向键行为可能移动光标
  - 多显示器环境下窗口居中仍基于主屏而非当前使用屏幕

## Release Policy Summary

- 当前项目仍处于 `v1.0.0` 之前的预发布阶段
- 在活跃阶段内，优先使用 patch 版本记录有意义的检查点
- 阶段关闭时递增 minor 版本
- `v1.0.0` 仍保留给首个稳定发布

## Immediate Next Step

优先处理 `ET-BUG-001`：

- 评估 `_clear_external_selection()` 的方向键清选策略
- 在不回归外部输入框回填成功率的前提下消除光标漂移风险

## Known Gaps

- 当前 smoke baseline 仍未接入 hosted CI，也不覆盖 GUI 级交互回归
- 当前 backlog 仍需要把既有产品 Bug 与 skeleton 接入后的运维任务并行维护
- 合同文档目前已可用，但仍可继续结合项目实际收紧边界
