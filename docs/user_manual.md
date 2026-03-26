# User Manual

## Purpose

为当前 `Easy-translation` 仓库提供一份项目拥有态的协作与维护手册。

## Who Should Read This

适合以下角色：

- 接手当前仓库的人类开发者
- 需要继续工作的 AI 协作者
- 负责发布、验证或仓库治理的人

## Repository Mode

当前仓库已经处于 `project-owned` 状态：

- 业务代码已经存在
- `config/project/current_project.json` 已声明 `bootstrap_finalized: true`
- 不应再把上游模板初始化器当作当前仓库的日常操作

## Core Documents

优先阅读这些文件：

- `docs/START_HERE.md`
- `docs/current_status.md`
- `docs/backlog.md`
- `docs/roadmap.md`
- `docs/versioning_policy.md`
- `docs/developer_guide.md`
- `docs/app_developer_guide.md`

## Quick Start

第一次接手当前仓库时，按以下顺序：

1. 阅读 `docs/START_HERE.md`
2. 阅读 `docs/current_status.md`
3. 阅读 `docs/backlog.md`
4. 阅读 `docs/roadmap.md`
5. 若任务涉及业务实现，再阅读 `docs/app_developer_guide.md` 与 `docs/PROJECT_STATUS.md`
6. 运行 `scripts/run_repo_hygiene_checks.ps1` 以确认骨架状态
7. 按实际任务进入开发、验证或文档更新

## Daily Workflow

建议的日常节奏：

1. 从 `docs/current_status.md` 和 `docs/backlog.md` 确认当前主线
2. 做增量改动，不重写骨架
3. 若已验证事实变化，更新 `docs/current_status.md`
4. 若任务状态变化，更新 `docs/backlog.md`
5. 在有意义的检查点补写当日日志
6. 涉及仓库边界时运行 repo hygiene 检查

## Working With Remote AI Contributors

使用 `docs/prompt_templates/` 下的模板。

推荐要求：

1. AI 先读 `docs/START_HERE.md`
2. 再读 `docs/current_status.md`、`docs/backlog.md` 和 `docs/roadmap.md`
3. 需要改业务代码时，再读 `docs/app_developer_guide.md`
4. 只做增量变更
5. repo-boundary 改动必须补做 hygiene 检查

## Repo Hygiene Workflow

本地统一入口：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_repo_hygiene_checks.ps1
```

它会运行：

- `scripts/check_repo_guard.ps1`
- `scripts/check_gitignore_hygiene.ps1`

适用场景：

- 新增或修改 canonical docs
- 修改脚本、CI、配置样例或 `.gitignore`
- 引入新的本地缓存、构建产物或工件目录

## Initialization Workflow

当前仓库已经完成初始化，因此：

- 不要在本仓库重新执行 skeleton bootstrap
- 如需从头初始化一个新项目，请回到上游 `AIProjectSkeleton` 仓库执行
- 当前仓库只维护 project-owned 形态下的持续开发工作

## Handoff Workflow

交接前至少确认：

1. `docs/backlog.md` 已反映任务状态
2. `docs/current_status.md` 与已验证事实一致
3. 已补当天 `docs/daily/YYYY/MM/YYYY-MM-DD.md`
4. 已记录变更内容、验证结果、遗留问题和下一步建议
5. 如涉及仓库边界，已运行 repo hygiene 检查

## Troubleshooting

### Repo Guard 报缺少 canonical 文件

先确认以下路径是否存在：

- `docs/START_HERE.md`
- `docs/current_status.md`
- `docs/backlog.md`
- `docs/roadmap.md`
- `scripts/run_repo_hygiene_checks.ps1`
- `.github/workflows/repo-hygiene.yml`

### 不确定该更新哪份开发文档

- 更新骨架规则、任务状态、阶段规划：改 `docs/developer_guide.md`、`docs/current_status.md`、`docs/backlog.md`、`docs/roadmap.md`
- 更新模块职责、数据流、避坑点：改 `docs/app_developer_guide.md`

### 新增了本地文件但 hygiene 检查失败

说明 `.gitignore` 可能缺少规则。补齐规则后重新运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_repo_hygiene_checks.ps1
```
