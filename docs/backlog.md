# Backlog

## Usage Rules

- 在把需求视为正式计划工作之前，先登记到这里
- 仅使用这些状态：
  - `Todo`
  - `Ready`
  - `In Progress`
  - `Blocked`
  - `Done`
- `docs/current_status.md` 负责描述当前已验证事实
- 本文件负责描述当前任务优先级、状态与验收边界

## Priority Overview

| ID | Title | Priority | Status | Milestone |
|---|---|---|---|---|
| `ET-GOV-001` | Project-owned skeleton adoption | `P0` | `Done` | `Phase 2` |
| `ET-QA-001` | Minimal automated smoke baseline | `P0` | `Done` | `Phase 2` |
| `ET-QA-002` | Hosted smoke workflow | `P1` | `Todo` | `Phase 2` |
| `ET-BUG-001` | External input selection clear side effect | `P0` | `Ready` | `Phase 2` |
| `ET-BUG-002` | Multi-monitor window centering | `P1` | `Ready` | `Phase 2` |
| `ET-FEAT-001` | Hotkey recording UI | `P1` | `Todo` | `Phase 3` |
| `ET-REL-001` | Release gate and packaging checklist | `P1` | `Ready` | `Release` |

## Item Details

## ET-GOV-001 Project-Owned Skeleton Adoption

- Type: `Operations`
- Priority: `P0`
- Status: `Done`
- Milestone: `Phase 2`
- Summary: 在不破坏现有 PyQt6 桌面应用代码和产品级文档的前提下，把仓库接入 AIProjectSkeleton 的 project-owned 治理骨架
- Acceptance:
  - `docs/START_HERE.md`、`docs/current_status.md`、`docs/backlog.md`、`docs/roadmap.md` 已就位
  - repo hygiene 脚本和 CI 工作流已接入
  - `config/project/current_project.json` 已声明 project-owned 状态
  - 原有应用级开发文档被保留并重新挂接
- Current Reality:
  - 当前检查点已经完成骨架落地
  - 旧的应用实现说明保留在 `docs/app_developer_guide.md`

## ET-QA-001 Minimal Automated Smoke Baseline

- Type: `Quality`
- Priority: `P0`
- Status: `Done`
- Milestone: `Phase 2`
- Summary: 为当前仓库建立最小自动化验证入口，至少覆盖启动、配置、目录和脚本层面的回归风险
- Acceptance:
  - 至少有一个可重复执行的 smoke 检查入口
  - 可以在不依赖完整 GUI 手工操作的情况下验证关键导入和配置加载
  - 仓库脚本与验证文档保持一致
- Current Reality:
  - `tests/test_smoke_baseline.py` 已覆盖入口路径注入、配置加载、runtime 隔离和翻译核心的基础无网络行为
  - `scripts/run_smoke_tests.ps1` 已提供统一本地入口
  - `docs/TESTING.md` 与 `tests/README.md` 已同步说明运行方式

## ET-QA-002 Hosted Smoke Workflow

- Type: `Quality`
- Priority: `P1`
- Status: `Todo`
- Milestone: `Phase 2`
- Summary: 将当前最小 smoke baseline 接入 hosted CI，形成每次 push / pull request 的基础自动校验
- Acceptance:
  - smoke 测试可以在 Windows hosted runner 上执行
  - 不依赖真实 GUI 交互或手工剪贴板输入
  - workflow 失败时能提供可读的失败定位
- Current Reality:
  - 当前 smoke baseline 仅在本地脚本层面验证
  - 仓库当前只有 repo hygiene CI

## ET-BUG-001 External Input Selection Clear Side Effect

- Type: `Bug`
- Priority: `P0`
- Status: `Ready`
- Milestone: `Phase 2`
- Summary: 修复外部输入框回填后用于消除全选状态的按键动作在部分富文本编辑器中移动光标的问题
- Acceptance:
  - 常见文本编辑器回填后光标位置不再意外漂移
  - 不回归外部输入框回填成功率
  - 手工验证步骤被记录到 `docs/TESTING.md` 或后续自动化验证中
- Current Reality:
  - 该问题已记录在 `docs/PROJECT_STATUS.md`

## ET-BUG-002 Multi-Monitor Window Centering

- Type: `Bug`
- Priority: `P1`
- Status: `Ready`
- Milestone: `Phase 2`
- Summary: 将窗口初始定位从仅依赖主屏调整为基于当前使用屏幕或更合理的显示器策略
- Acceptance:
  - 多显示器环境下主窗口不会总是固定落在主屏
  - 单屏行为保持稳定
- Current Reality:
  - 该问题已记录在 `docs/PROJECT_STATUS.md`

## ET-FEAT-001 Hotkey Recording UI

- Type: `Feature`
- Priority: `P1`
- Status: `Todo`
- Milestone: `Phase 3`
- Summary: 在设置页增加热键录制能力，替代手工输入组合键字符串
- Acceptance:
  - 用户可直接录制组合键
  - 录制结果可落入现有设置结构
  - 不破坏 `triple_space` 触发模式
- Current Reality:
  - 当前需求已在旧产品规划文档中出现，但尚未实现

## ET-REL-001 Release Gate And Packaging Checklist

- Type: `Release`
- Priority: `P1`
- Status: `Ready`
- Milestone: `Release`
- Summary: 为首个稳定版建立发布门槛，覆盖环境、打包、核心回归场景和文档同步
- Acceptance:
  - 发布前最低验证集明确
  - PyInstaller 打包流程明确
  - 版本同步规则明确
- Current Reality:
  - 当前已有 `Easy-translation.spec` 和相关部署文档，但缺少统一 release gate
