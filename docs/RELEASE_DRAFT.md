# 发布草稿

本文档用于 GitHub Release 发布时直接粘贴，格式与现有发布说明保持一致。

## v0.5.9

发布时间：2026-03-26

### 本版本重点

- 新增 AI 翻译能力规划文档与正式 backlog 任务
- 明确 `BYOK` 云端 AI provider 接入方向，不把测试阶段锁定到 `OpenAI`
- 重新生成 Windows release 包，作为新的维护检查点

### 用户可见变化

1. 当前版本没有新增可直接操作的 UI 功能
2. 仓库已正式登记 AI profile、`BYOK` provider 和候选词悬浮窗三条后续功能线
3. Windows 发布包已按当前仓库状态重新打包，可直接用于本地部署与验证

### 下载文件

- `Easy-translation.exe`
- `Easy-translation-windows-x64.zip`

### 使用说明

1. 平台：Windows x64
2. 普通翻译功能无需安装 Tesseract
3. 截图 OCR 功能需要用户机器安装 Tesseract
4. 百度、腾讯、Ollama 仍需用户在设置页自行配置
5. 计划中的云端 AI provider 将采用用户自填 `API key` 的 `BYOK` 模式

### SHA256

- `Easy-translation.exe`: `44DE6EA2CFFA6AD639F9B0B841ADCAD411DEF7B2CB4D6C34DCB2C3E0BDBD5F2B`
- `Easy-translation-windows-x64.zip`: `77CB84E1E6195321761F312BEFD7F2A5F6BACBB484D14A7FF291611BD2E58E8C`
