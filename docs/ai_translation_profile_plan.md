# AI Translation Profile Plan

## Purpose

把“AI 场景翻译 profile”与“官方 LLM provider 接入”从口头讨论收敛成可执行方案，并明确一个硬约束：

- 在 API key 模式下，单次翻译的 token 消耗要尽可能低

## Decision Summary

- 当前项目可以新增 `AI 场景翻译 profile`
- 该能力应建立在 `Provider` 与 `Profile` 分离的结构上
- 首批适配对象应为 LLM 类翻译源：
  - `ollama`
  - 后续新增的 `OpenAI-compatible` provider
- 传统翻译源（`google` / `baidu` / `tencent`）首期不做 profile 深度控制
- 官方 GPT / DeepSeek 的接入首期采用 `BYOK`（用户自填 `API key`）模式
- 测试阶段不限制为 `OpenAI`，可使用任一兼容 provider preset 或自定义兼容端点
- 不支持直接复用 ChatGPT / DeepSeek 网页或 App 登录态

## Expected User Experience

- 用户在设置页选择当前激活的翻译场景，例如：
  - `通用翻译`
  - `虚幻引擎开发翻译`
  - `自定义场景`
- 只要当前翻译源属于 AI provider，每次翻译请求都会自动套用当前 profile
- 用户切换 profile 后，后续请求立即按新 profile 生效
- 非 AI provider 的行为必须明确：
  - 要么忽略 profile 并在 UI 中说明
  - 要么禁止选择不支持的组合

## Architecture Direction

### 1. Provider 与 Profile 解耦

- `Provider` 负责模型调用
- `Profile` 负责场景约束
- `TranslatorCore` 不再直接把场景写死在某个 provider 的 prompt 里

建议结构：

```text
TranslatorCore
  ├─ resolve provider
  ├─ resolve active profile
  ├─ compile compact translation instruction
  └─ dispatch to provider adapter
```

### 2. Profile 数据模型

建议新增持久化结构：

```json
{
  "ai_translation": {
    "active_profile": "general",
    "custom_profiles": {
      "custom_1": {
        "name": "我的场景",
        "system_brief": "偏技术文档风格，保持术语一致。",
        "glossary": {
          "Blueprint": "蓝图",
          "Actor": "Actor"
        },
        "preserve_terms": [
          "C++",
          "UFUNCTION",
          "UPROPERTY"
        ]
      }
    }
  }
}
```

预置 profile 至少应包含：

- `general`
- `unreal_engine_dev`

### 3. Provider 接入方式

- UI 层可以暴露 provider preset：
  - `OpenAI`
  - `DeepSeek`
- UI 层还应允许配置自定义兼容端点
- 代码层建议抽象为统一的 `OpenAI-compatible` adapter
- 每个 provider 只保留自己的默认：
  - `base_url`
  - `model`
  - `timeout`
  - `api_key`
- 所有云端 AI provider 首期都按 `BYOK` 处理，而不是绑定单一测试厂商

## Token Cost Minimization Rules

这是本方案的核心约束。

### 1. 单轮请求

- 每次翻译只发一轮请求
- 不保留聊天历史
- 不发送上下文对话
- 不发送解释型追问

### 2. Profile 本地编译，不把整套配置原样发给模型

- 预置 profile 存在本地
- 每次请求前，将当前 profile 编译成一段紧凑指令
- 只发送“当前激活 profile”的最小必要文本
- 不发送所有 profile 列表

### 3. 默认不用 few-shot 示例

- few-shot 对翻译质量有帮助，但非常耗 token
- 首版默认关闭示例
- 只有在确实证明收益显著时，才考虑给个别 profile 增加可选示例

### 4. glossary 和 preserve_terms 要限长

- `system_brief` 设定长度上限
- `glossary` 限制条目数
- `preserve_terms` 限制数量
- 超出上限时在本地截断，而不是原样发给模型

建议首版限制：

- `system_brief` 不超过 `300` 字符
- `glossary` 不超过 `20` 条
- `preserve_terms` 不超过 `20` 条

### 5. 输出只要译文，不要解释

- 当前应用只消费最终译文
- `source_lang` / `target_lang` 已由本地逻辑掌握
- 因此不应要求模型返回解释、备注、置信度或多候选结果

首选输出约束：

- 只返回最终译文纯文本

保底方案：

- 若某 provider 稳定性不足，再退回极简 JSON，例如 `{"translation":"..."}`

### 6. 控制采样与输出上限

- `temperature` 保持低值
- 若 provider 支持 reasoning / verbosity 控制，应选择最低成本模式
- 为输出设置动态上限，不使用过高固定值

建议：

- 短文本默认较低输出上限
- 长文本按输入长度估算上限
- 严禁直接给出远高于场景需要的默认 `max_tokens`

### 7. 复用缓存

缓存键建议至少包含：

- provider
- model
- source_lang
- target_lang
- active_profile
- text

这样可以避免同一 profile 下重复扣费。

## Optional Candidate Window Mode

这是建立在 profile 和 AI provider 之上的可选增强模式，不作为首批基础翻译链路的一部分。

### Intended Interaction

- 用户开启“候选词悬浮窗模式”
- 在外部输入框中触发翻译
- 应用先抓取原文，再请求 AI 候选结果
- 结果返回后先显示候选窗，而不是立刻回填
- 默认高亮第 `1` 个候选
- 用户按 `1` / `2` / `3` 切换候选
- 用户按 `Space` 或 `Enter` 提交当前候选并执行回填
- 用户按 `Backspace` 或 `Esc` 取消本次翻译

### Design Constraints

- 该模式必须作为设置项开关，默认关闭
- 首版只对 AI provider 生效
- 候选数量限制为最多 `3` 个
- 候选说明只能是短标签，不做长篇词典释义
- 悬浮窗不能因为抢焦点破坏目标输入框回填
- 长文本、整段文本或不适合候选模式的请求必须自动回退到单结果直接翻译

### Focus And Positioning Risks

- 候选窗如果抢走焦点，后续回填可能打到错误窗口
- 因此应优先使用不抢焦点的顶层悬浮窗，或者至少保存目标窗口句柄并在提交前校验
- 候选窗位置优先跟随文本光标
- 当目标应用无法可靠暴露 caret 位置时，退回到鼠标附近或目标窗口可见区域

### Token Cost Rules For Candidate Mode

候选模式比单结果翻译更耗 token，因此必须额外收紧。

- 只在短文本场景下启用
- 候选数最多 `3` 个，不做更多枚举
- 说明字段只允许短标签，例如：
  - `术语`
  - `名词`
  - `动词`
  - `建议保留英文`
- 优先使用本地 glossary 生成说明，不要每次让模型返回完整解释
- 不返回完整词典释义、例句、同义词或用法分析

### Recommended Fallback Strategy

- provider 不支持时：直接走当前单结果翻译链路
- 文本过长时：直接走当前单结果翻译链路
- 候选窗初始化失败时：直接走当前单结果翻译链路
- 目标窗口上下文丢失时：取消回填并提示用户重新触发

## Scope Boundaries

### In Scope

- AI provider 的场景化翻译
- 预置 profile 与自定义 profile
- `BYOK` 的 `OpenAI-compatible` API provider
- API key 加密存储
- 低 token 成本约束

### Out Of Scope For First Phase

- 直接复用 ChatGPT / DeepSeek 网页登录态
- 多轮会话记忆式翻译
- 面向传统翻译源的 profile 精准控制
- token 级精确计费统计面板

## Proposed Implementation Sequence

### Stage A. Profile 基础层

- 新增 profile 数据结构
- 新增预置 profile
- 新增“紧凑指令编译器”
- 让 `ollama` 先接 profile 能力

### Stage B. 设置页与持久化

- 增加 active profile 选择
- 增加自定义 profile 编辑
- 增加长度限制和输入校验

### Stage C. BYOK OpenAI-Compatible Provider Layer

- 新增统一 adapter
- 接入 provider preset：`OpenAI` / `DeepSeek`
- 接入自定义兼容端点
- 接入用户自填 `api_key` / `base_url` / `model` / `timeout`
- 复用 profile 编译结果

### Stage D. 验证与文档

- 为 prompt 编译逻辑补单元测试
- 为设置读写补 smoke / isolated tests
- 明确哪些 provider 支持 profile
- 在文档中写清“不支持网页登录态”

### Stage E. Optional Candidate Window

- 增加候选窗设置项
- 增加不抢焦点的候选悬浮窗
- 增加候选确认 / 取消状态机
- 接入短文本候选请求与回退逻辑
- 补充人工验证步骤

## Recommended Backlog Split

- `ET-FEAT-002`: AI 场景翻译 profile 与自定义场景
- `ET-FEAT-003`: BYOK AI provider 接入与低 token 成本控制
- `ET-FEAT-004`: 可选的输入法式翻译候选窗

## Professional Assessment

- 这项能力和现有架构兼容，适合增量接入
- 最合理的第一步不是先接很多 provider，而是先把 `profile` 层抽出来
- 如果直接在每个 provider 内继续手写 prompt，会很快失控
- “不用 key 直接像官方聊天一样翻译”不适合作为当前桌面应用的首期实现路线
- 如果未来坚持免 key 体验，应单独规划自建中转服务，而不是污染当前本地直连架构
