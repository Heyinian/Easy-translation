# Versioning Policy

## Base Rule

- 该代码库早于 skeleton 接入而存在，当前纳入治理的工作版本为 `v0.5.9`
- 当前仍处于首个稳定版之前
- `v1.0.0` 保留给首个稳定发布

## Pre-Release Phase Version Rule

- 在当前阶段内，针对有意义的实现、文档、工具链或验证检查点递增 patch 版本
- 阶段完成时递增 minor 版本并将 patch 归零
- 影响产品对外认知的版本变化，需要同步更新产品级文档

## Post-Release Version Rule

After `v1.0.0`:

- 向后兼容的修复、文档澄清、验证加固，使用 patch 版本
- 向后兼容的能力扩展或较大功能块，使用 minor 版本
- 只有在稳定版边界被破坏时才使用 major 版本

## Examples

- 当前 skeleton 接入后的治理基线：`v0.5.8`
- `Phase 2` 内一个新的发布与维护检查点：`v0.5.9`
- `Phase 2` 完成：`v0.6.0`
- 发布准备阶段完成：`v0.9.0`
- 首个稳定发布：`v1.0.0`

## Patch Increment Use

以下情况适合递增 patch：

- 修复了一个明确的产品问题
- 完成了一次有意义的验证或交接检查点
- 收紧了配置、文档或仓库治理边界
- 增加了新的可重复执行的测试或 smoke 验证

纯编辑噪声不应触发版本号变化。

## Required Sync Points

当版本变化时，至少检查这些文件是否需要同步：

- `README.md`
- `docs/current_status.md`
- `docs/roadmap.md`
- `docs/PROJECT_STATUS.md`
- 当前日期对应的 `docs/daily/YYYY/MM/YYYY-MM-DD.md`
- `docs/CHANGELOG.md` 与 `docs/RELEASE_NOTES.md`（若本次变化需要对外说明）

## Current Applied Version

- 当前工作版本是 `v0.5.9`
- 当前阶段是 `Phase 2 - Pre-Release Stabilization`
