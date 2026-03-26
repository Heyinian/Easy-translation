# Roadmap

## Purpose

本文件定义当前仓库的阶段性目标、阶段退出条件和目标版本。

说明：较早期版本历史早于 skeleton 接入，下面的阶段划分是基于当前仓库状态建立的治理基线，不是对所有旧版本的逐条审计回放。

## Versioning Rule

- 当前项目仍处于 `v1.0.0` 之前
- 阶段内的有意义检查点使用 patch 版本递增
- 阶段完成时递增 minor 版本并将 patch 归零
- 首个稳定发布保留为 `v1.0.0`

## Phase Overview

| Phase | Status | Goal | Exit Version |
|---|---|---|---|
| `Phase 0` | `Done` | 完成核心桌面翻译流程与基础运行形态 | `v0.3.0` |
| `Phase 1` | `Done` | 补齐多翻译源、设置持久化、OCR 和单实例等主要能力 | `v0.5.0` |
| `Phase 2 - Pre-Release Stabilization` | `In Progress` | 提升稳定性、接入治理骨架并建立最小验证基线 | `v0.6.0` |
| `Phase 3 - Release Preparation` | `Todo` | 打磨发布门槛、回归验证与打包流程 | `v0.9.0` |
| `Release` | `Todo` | 首个稳定版发布 | `v1.0.0` |

## Phase 2 - Pre-Release Stabilization

### Goal

- 维持现有功能可用
- 接入统一开发骨架与仓库卫生规则
- 补上最小自动化验证与回归入口
- 处理当前高优先级稳定性问题

### Exit Criteria

- skeleton 文档和 repo hygiene 流程稳定运行
- 至少有一套最小 smoke 验证入口
- 关键已知问题有明确处理结果或风险说明
- 当前结果目标：推进到 `v0.6.0`

## Phase 3 - Release Preparation

### Goal

- 明确发布门槛
- 固化打包和分发流程
- 清理影响首个稳定版的剩余高优问题

### Exit Criteria

- 发布清单明确
- 验证清单明确
- 用户可见文档与内部文档版本同步

## Release

### Goal

交付首个稳定版 `Easy-translation`

### Exit Criteria

- 功能与稳定性门槛满足
- 打包产物验证通过
- 版本、发布说明、部署与测试文档同步完成
