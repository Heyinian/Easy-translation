# Development Guidelines

## Scope

这些规则适用于：

- 本地开发者
- 远程开发者
- 持续接手当前仓库的 AI 协作者

## Canonical Document Responsibilities

当前骨架使用这些文件承担固定职责：

- `docs/START_HERE.md`：稳定入口
- `docs/current_status.md`：当前已验证事实
- `docs/backlog.md`：活动任务与优先级
- `docs/roadmap.md`：阶段规划与退出条件
- `docs/versioning_policy.md`：版本规则
- `docs/HANDOFF_PROTOCOL.md`：交接纪律
- `docs/daily/YYYY/MM/YYYY-MM-DD.md`：按日追加的时间线
- `docs/archive/README.md`：归档解释规则

应用实现本身的深度说明继续放在：

- `docs/app_developer_guide.md`
- `docs/PROJECT_STATUS.md`

## Incremental Maintenance Rule

不要在每次交接时重写整套文档系统。

应该：

1. 保持主文档结构稳定
2. 只更新本轮工作真正影响的部分
3. 将时序性信息追加到 daily log
4. 保留旧资料，但不让旧资料覆盖当前真相

结构重写不是默认维护方式。

## Bootstrap One-Time Rule

当前仓库已经处于 `project-owned` 状态。

因此：

1. 不要把 skeleton bootstrap 当成日常维护命令再次执行
2. 不要重新引入一次性 bootstrap 资产，除非项目明确决定回到 template-linked 模式
3. 当前仓库更关注持续开发，而不是重新初始化

## New Requirement Intake

把一个请求当成正式计划工作前，应先：

1. 记录到 `docs/backlog.md`
2. 补齐 `ID`、`Priority`、`Status`、`Milestone`
3. 在开始实现前写明验收标准

## Version Discipline

有意义的检查点完成后：

1. 判断这是 patch 级检查点还是阶段完成检查点
2. 需要时同步更新版本信息
3. 保证 `docs/current_status.md`、相关产品文档和当日日志一致
4. 只有在确实需要保留历史边界时才写 archive

阶段完成时：

1. 更新 `docs/roadmap.md`
2. 需要时在 `docs/archive/legacy/YYYY/MM/` 留档
3. 只有退出条件满足后才把下一阶段任务推进为主线

## Repository Hygiene Rule

把 `.gitignore` 当作持续维护的仓库边界文件，而不是一次性初始化文件。

当引入新的工具链、本地缓存、构建产物、日志目录或本机配置时：

1. 评估 `.gitignore` 是否需要同步更新
2. 优先使用最窄、最明确的忽略规则
3. 不要用会掩盖 `src/`、`docs/`、配置样例或 schema 的过宽规则
4. 预期会持续存在的本地工件，应与对应的 `.gitignore` 变更在同一检查点落地

关闭重要的 repo-boundary、脚本、CI 或工具链检查点前，运行：

1. `scripts/run_repo_hygiene_checks.ps1`
2. 若发生已批准的结构重写，临时添加 `docs/approvals/ALLOW_DOC_STRUCTURE_CHANGE.json`
3. 结构变更落地后移除该 override 文件

## Collaboration Rule

不要把多个无关问题塞进同一个 backlog 项，避免降低并行度和交接清晰度。

优先拆成边界明确的任务节点，例如：

- 产品缺陷修复
- 测试与验证
- 文档维护
- 仓库治理与工具链
- 发布准备
