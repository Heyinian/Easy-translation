# START_HERE

## Purpose

本文件是当前仓库的人类开发者与 AI 协作者统一入口。

先读这里，再按下面顺序继续：

1. `docs/current_status.md`
2. `docs/backlog.md`
3. `docs/roadmap.md`
4. `docs/versioning_policy.md`
5. `docs/execution_contract.md`
6. `docs/config_contract.md`
7. `docs/guard_profile_contract.md`
8. `docs/artifact_contract.md`
9. `docs/result_contract.md`
10. `docs/developer_guide.md`
11. `docs/app_developer_guide.md`
12. `docs/PROJECT_STATUS.md`
13. `docs/prompt_templates/README.md`
14. `docs/development_guidelines.md`
15. `docs/HANDOFF_PROTOCOL.md`
16. `docs/daily/` 下最新日期日志
17. `docs/archive/README.md`

## One-Line Project State

`Easy-translation` 当前处于 `Phase 2 - Pre-Release Stabilization`，工作版本为 `v0.5.9`。仓库已经以 `project-owned` 方式接入 `AIProjectSkeleton` 的治理骨架，同时保留原有桌面应用实现与产品级技术文档。

## Current Source Of Truth

这些文件是当前协作的第一真相来源：

- `docs/current_status.md`：当前经过验证的项目状态
- `docs/backlog.md`：当前任务、优先级、状态与验收标准
- `docs/roadmap.md`：当前阶段规划、阶段目标与退出版本
- `docs/versioning_policy.md`：版本策略与同步规则
- `docs/execution_contract.md`：主执行入口约定
- `docs/config_contract.md`：配置层边界约定
- `docs/guard_profile_contract.md`：仓库保护与结构变更约定
- `docs/artifact_contract.md`：构建产物与本地工件约定
- `docs/result_contract.md`：验证结果与输出摘要约定
- `docs/developer_guide.md`：当前仓库骨架和协作规则

这些文件作为产品级补充说明继续保留：

- `docs/app_developer_guide.md`：应用实现细节、模块职责、避坑说明
- `docs/PROJECT_STATUS.md`：现有产品状态、已知 Bug、功能规划
- `docs/DOCS_INDEX.md`：原有文档导航

辅助文档：

- `docs/prompt_templates/README.md`
- `docs/development_guidelines.md`
- `docs/HANDOFF_PROTOCOL.md`
- 最新的 `docs/daily/YYYY/MM/YYYY-MM-DD.md`
- `docs/archive/README.md`

当前仓库卫生检查入口：

- `scripts/run_repo_hygiene_checks.ps1`
- `scripts/check_repo_guard.ps1`
- `scripts/check_gitignore_hygiene.ps1`
- `docs/approvals/README.md`

## Documentation System

当前骨架职责拆分如下：

- `docs/START_HERE.md`：稳定入口
- `docs/current_status.md`：当前验证状态
- `docs/backlog.md`：活动任务与优先级
- `docs/roadmap.md`：阶段规划与退出条件
- `docs/versioning_policy.md`：版本规则
- `docs/development_guidelines.md`：协作与维护规则
- `docs/HANDOFF_PROTOCOL.md`：交接规则
- `docs/daily/YYYY/MM/YYYY-MM-DD.md`：按日追加的时间线
- `docs/archive/README.md`：归档解释规则

不要把 `docs/PROJECT_STATUS.md`、`docs/app_developer_guide.md` 当成这套骨架的替代品；它们是应用级补充，而不是当前协作主入口。

## Current Focus

当前重点是把已有的 Windows 桌面翻译工具继续推进到更稳定的预发布阶段，同时补齐仓库级协作与验证基线。

优先方向：

1. 建立最小自动化验证与回归入口
2. 处理当前已知的外部输入框回填与多显示器窗口定位问题
3. 为后续 `v1.0.0` 稳定版建立发布与验收门槛
