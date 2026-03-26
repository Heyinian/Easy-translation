# Developer Guide

## Purpose

说明当前 `Easy-translation` 仓库如何使用接入后的 AIProjectSkeleton 骨架开展协作，并明确它与应用级技术文档的分工关系。

## Entry Workflow

建议按此顺序进入当前仓库：

1. `docs/START_HERE.md`
2. `docs/current_status.md`
3. `docs/backlog.md`
4. `docs/roadmap.md`
5. `docs/versioning_policy.md`
6. `docs/development_guidelines.md`
7. `docs/HANDOFF_PROTOCOL.md`
8. `docs/app_developer_guide.md`
9. `docs/PROJECT_STATUS.md`

## Repository Roles

这份 `docs/developer_guide.md` 负责：

- 说明开发骨架怎么用
- 约束 current status / backlog / roadmap / daily log 的维护方式
- 约束 repo hygiene、结构变更和远程 AI 协作边界

这份 `docs/app_developer_guide.md` 负责：

- 解释应用实现细节
- 解释模块职责、数据流和避坑点
- 服务于深入改动业务代码时的技术接手

不要把这两类文档混在一起维护。

## Operating Rules

- 保持 canonical 文档职责稳定
- 保证 `docs/current_status.md`、`docs/backlog.md`、`docs/roadmap.md` 和当日日志与已验证事实一致
- 仅在检查点值得记录版本时才更新版本信息
- 影响仓库边界的改动完成后运行 `scripts/run_repo_hygiene_checks.ps1`
- skeleton 接入已经完成，不再把 bootstrap 当成日常操作

## Working With Remote AI Contributors

使用 `docs/prompt_templates/` 下的提示词模板。

推荐流程：

1. 让 AI 先读 `docs/START_HERE.md`
2. 再读 `docs/current_status.md`、`docs/backlog.md` 和 `docs/roadmap.md`
3. 如果任务会改业务代码，再补读 `docs/app_developer_guide.md`
4. 要求 AI 只做增量改动
5. 对 repo-boundary 改动要求补齐 hygiene 检查

## Checkpoint Discipline

在关闭一个有意义的检查点前：

1. 确认 `docs/backlog.md` 反映了当前任务状态
2. 如验证事实变化，更新 `docs/current_status.md`
3. 补当天的 `docs/daily/YYYY/MM/YYYY-MM-DD.md`
4. 只有阶段计划变化时才更新 `docs/roadmap.md`
5. 如有必要，更新版本信息和相关产品文档
6. 需要时再做 archive，而不是默认做 archive
7. 运行 `scripts/run_repo_hygiene_checks.ps1`

## Structural Rewrite Rule

不要为了图省事而替换 canonical 文档集或顶层骨架。

如果确实需要结构重写：

1. 先在 `docs/backlog.md` 记录原因和范围
2. 再在当前日期日志里记录背景
3. 使用 `docs/approvals/ALLOW_DOC_STRUCTURE_CHANGE.example.json` 生成 `docs/approvals/ALLOW_DOC_STRUCTURE_CHANGE.json`
4. 在获批范围内实施结构改动
5. 改动完成后移除 override 文件
