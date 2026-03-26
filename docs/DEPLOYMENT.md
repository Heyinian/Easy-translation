# 部署说明

本文档面向需要在本机运行、打包或分发本项目的开发者与实施人员。

## 文档导航

- 文档索引：DOCS_INDEX.md
- 项目总览：../README.md
- 快速上手：QUICKSTART.md
- 开发者归档：app_developer_guide.md
- 测试说明：TESTING.md
- 发布说明：RELEASE_NOTES.md
- 变更记录：CHANGELOG.md

## 1. 环境要求

- Windows
- Python 3.12
- 可联网环境（Google / 百度 / 腾讯翻译需要）
- Tesseract OCR（可选，仅截图翻译需要）

当前项目推荐使用本地虚拟环境：

- .venv312

## 2. 本地运行部署

### 2.1 安装依赖

```powershell
pip install -r requirements.txt
```

### 2.2 安装 Tesseract（可选）

下载地址：

- https://github.com/UB-Mannheim/tesseract/wiki

默认安装路径通常为：

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

如果路径不同，可在应用设置页中调整。未安装 Tesseract 不影响应用启动、设置保存和普通翻译功能。

### 2.3 启动源码版

```powershell
.\.venv312\Scripts\python.exe app.py
```

或者在 VS Code 中运行任务：

- 运行源码版 Easy-translation

## 3. 配置项部署说明

应用实际运行配置保存在：

- user_settings.json

敏感凭证加密密钥保存在：

- .settings.key

部署时需要注意：

1. 如果希望目标机器直接继承现有设置，需要同时带上 user_settings.json 和 .settings.key
2. 如果不希望继承本地密钥和设置，只分发程序文件即可，目标用户首次运行会自动生成新的设置文件和密钥文件

## 4. 翻译源部署建议

### 4.1 Google

- 默认可直接使用
- 适合无额外配置的轻量部署

### 4.2 百度 / 腾讯

- 需要用户自行填写 API 凭证
- 不建议将生产密钥直接写死进仓库

### 4.3 Ollama

如果要启用本地 AI 翻译：

1. 目标机器需安装并启动 Ollama
2. 目标机器需提前拉取模型
3. 应用设置页中配置 base_url、model、timeout

示例默认值：

```text
base_url = http://127.0.0.1:11434
model = qwen2.5:7b
timeout = 20
```

## 5. 打包为 exe

项目已包含：

- Easy-translation.spec

推荐打包命令：

```powershell
pyinstaller Easy-translation.spec
```

输出目录通常为：

- dist/

常见产物：

- dist/Easy-translation.exe

## 6. 分发建议

如果要分发给其他电脑使用，建议至少确认以下项：

1. 目标机器是否已安装 Tesseract，或者是否准备不使用截图 OCR 功能
2. 是否允许全局热键监听
3. 目标使用的软件是否支持标准 Ctrl+A / Ctrl+C / Ctrl+V，以便外部输入框翻译回填生效
4. 是否需要本地 Ollama 服务

## 7. 验收清单

部署完成后建议按顺序验证：

1. 应用是否能正常启动
2. 主窗口翻译是否正常
3. 剪贴板翻译是否正常
4. 输入窗口翻译是否正常
5. 三击空格或组合键是否正常触发
6. 截图 OCR 是否正常

## 8. 常见部署问题

### 8.1 启动时报 PyQt6 或 Qt DLL 错误

当前项目已在 main_window.py 中处理 Qt bin 路径注入。如果仍报错，优先检查：

1. 是否确实使用 .venv312 运行
2. PyQt6 是否完整安装

### 8.2 截图 OCR 不可用

优先检查：

1. Tesseract 是否安装
2. 设置页中的 Tesseract 路径是否正确
3. 是否希望依赖系统 PATH 或默认安装路径自动发现

### 8.3 三击空格不生效

优先检查：

1. 当前设置中的 hotkeys.translate_input 是否为 triple_space
2. translate_input_time_window 是否过短
3. 目标输入程序是否拦截按键

### 8.4 外部输入框未成功回填

优先检查：

1. 目标程序是否支持 Ctrl+A / Ctrl+C / Ctrl+V
2. 是否存在剪贴板访问限制
3. 目标控件是否是标准可编辑文本框
