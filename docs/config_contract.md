# Config Contract

## Contract Status

Project-owned and active.

## Runtime Config

运行时配置和本地秘密主要位于：

- `runtime/user_settings.json`
- `runtime/.settings.key`

这些文件属于本机状态，不应提交到仓库。

## Project Config

仓库级配置样例和项目身份位于：

- `config/runtime/default.example.json`
- `config/project/current_project.json`
- `config/profiles/default_guard.example.json`

## Guard Profile

仓库治理边界由以下内容共同约束：

- `.gitignore`
- `scripts/check_repo_guard.ps1`
- `scripts/check_gitignore_hygiene.ps1`
- `docs/approvals/ALLOW_DOC_STRUCTURE_CHANGE.example.json`

## Contract Rule

真实秘密留在 `runtime/`，示例配置留在 `config/`，不要把本机配置或凭据写回示例文件。
