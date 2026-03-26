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
| `ET-FEAT-002` | AI translation profiles | `P1` | `Todo` | `Phase 3` |
| `ET-FEAT-003` | BYOK AI providers with token budget controls | `P1` | `Todo` | `Phase 3` |
| `ET-FEAT-004` | Optional floating translation candidate window | `P1` | `Todo` | `Phase 3` |
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

## ET-FEAT-002 AI Translation Profiles

- Type: `Feature`
- Priority: `P1`
- Status: `Todo`
- Milestone: `Phase 3`
- Summary: 为 AI 翻译源增加“场景翻译 profile”层，支持预置场景与自定义场景，并让每次 AI 翻译自动套用当前激活 profile
- Acceptance:
  - 设置层支持持久化 `active_profile`
  - 至少提供 `通用翻译` 与 `虚幻引擎开发翻译` 两个预置 profile
  - 支持一个可编辑的自定义场景 profile
  - AI provider 每次翻译请求都会自动应用当前 profile
  - 非 AI provider 的降级行为清晰且一致
  - profile 编译与回退逻辑有测试覆盖
- Current Reality:
  - `src/translator_core.py` 当前只有按 provider 分支的翻译逻辑，还没有 provider / profile 分离层
  - `ollama` 的 prompt 仍是硬编码在 provider 方法内部
  - 方案评估已整理到 `docs/ai_translation_profile_plan.md`

## ET-FEAT-003 BYOK AI Providers With Token Budget Controls

- Type: `Feature`
- Priority: `P1`
- Status: `Todo`
- Milestone: `Phase 3`
- Summary: 接入用户自填 `API key` 的 AI provider 能力，首期以 `OpenAI-compatible` 协议为主，并以内置低 token 成本策略支持 AI 场景翻译
- Acceptance:
  - 代码层有统一的 `OpenAI-compatible` adapter，可服务于 `OpenAI`、`DeepSeek` 以及自定义兼容端点
  - 设置层可安全存储用户自填的 `api_key`、`base_url`、`model` 与 `timeout`
  - 测试阶段不要求必须使用 `OpenAI`，可使用任一兼容 provider preset 或自定义兼容端点
  - 请求采用单轮翻译模式，不发送聊天历史
  - 默认输出只包含最终译文，不包含解释或多候选结果
  - prompt 编译、输出上限和缓存键都纳入 token 成本控制
  - 文档明确首期不支持直接复用 ChatGPT / DeepSeek 网页或 App 登录态
  - 至少有一组针对请求构造和设置读写的自动化验证
- Current Reality:
  - `src/settings_manager.py` 已支持本地加密存储 API 密钥
  - `src/translator_core.py` 当前只支持 `google` / `baidu` / `tencent` / `ollama`
  - 当前项目还没有统一的 `OpenAI-compatible` / `BYOK` 抽象，也没有 token 成本保护栏
  - 方案评估已整理到 `docs/ai_translation_profile_plan.md`

## ET-FEAT-004 Optional Floating Translation Candidate Window

- Type: `Feature`
- Priority: `P1`
- Status: `Todo`
- Milestone: `Phase 3`
- Summary: 为外部输入框翻译增加“输入法候选词式”悬浮窗模式，在回填前展示少量候选译文，允许用户快速确认、切换或取消
- Acceptance:
  - 该能力作为设置项开关，默认关闭
  - 仅对支持 AI profile 的 provider 生效，非 AI provider 有清晰回退行为
  - 外部输入框翻译在候选窗模式开启时，不再在首个结果返回后立刻回填
  - 候选窗默认选中第 `1` 个候选，支持 `1` / `2` / `3` 快速切换
  - 支持使用 `Space` 或 `Enter` 提交当前候选
  - 支持使用 `Backspace` 或 `Esc` 取消本次翻译，不修改目标输入框
  - 候选数首版限制为最多 `3` 个，并附带简短说明标签，例如词性或术语说明
  - 候选窗不能因为抢焦点而导致目标输入框丢失回填上下文
  - 长文本或不适合候选模式的场景会自动回退到单结果直接翻译
  - 有针对候选确认、取消、焦点保持和回退逻辑的验证记录
- Current Reality:
  - `src/main_window.py` 当前在 `on_translation_result()` 中收到结果后，会直接进入 `replace_text_in_active_input()`
  - 当前仓库还没有不抢焦点的候选悬浮窗，也没有候选交互状态机
  - 该能力依赖 `ET-FEAT-002` 的 profile 层和 `ET-FEAT-003` 的 AI provider 能力
  - 方案评估已整理到 `docs/ai_translation_profile_plan.md`

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
