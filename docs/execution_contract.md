# Execution Contract

## Contract Status

Project-owned and active.

## Purpose

定义当前项目默认执行入口，避免开发者和 AI 依赖未文档化的命令。

## Primary Execution Entry

推荐源码启动入口：

```powershell
.\.venv312\Scripts\python.exe app.py
```

## Required Inputs

- Windows 环境
- Python `3.12`
- 已安装 `requirements.txt` 中依赖

## Optional Inputs

- 安装 Tesseract 以启用 OCR
- 配置翻译服务密钥或本地 Ollama 服务

## Primary Outputs

- 启动 PyQt6 主界面
- 在 `runtime/` 下生成本地用户设置、日志和截图目录

## Exit-Code Semantics

- 正常启动并正常退出时应返回 `0`
- 导入错误、配置错误或运行时致命异常通常表现为非 `0` 退出

## Stability Rule

在明确替换主入口前，`app.py` 应保持为稳定源码入口。
