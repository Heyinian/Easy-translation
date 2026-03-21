# 发布草稿

本文档用于 GitHub Release 发布时直接粘贴，格式与现有发布说明保持一致。

## v0.5.1

发布时间：2026-03-21

### 本版本重点

- 应用统一更名为 Easy-translation
- 新增应用图标，并接入主窗口、托盘与 PyInstaller 打包
- 托盘后台运行体验完善，更接近常见常驻应用
- 增加单实例保护，避免重复启动多个相同任务
- 候选译文功能移除，翻译结果统一为单结果
- Tesseract 改为可选配置，未安装时不再阻塞设置保存

### 用户可见变化

1. 主窗口关闭或最小化后会自动切换到托盘后台运行
2. 托盘菜单支持打开主界面、打开设置、翻译当前剪贴板和退出应用
3. 重复启动时不会保留多个实例，后启动实例会唤醒主实例后退出
4. 应用显示名称和打包产物统一为 Easy-translation
5. 设置页不再显示 Ollama 候选数，翻译结果区只保留单结果
6. 未安装 Tesseract 时仍可正常保存设置和使用非 OCR 功能

### 下载文件

- `Easy-translation.exe`
- `Easy-translation-windows-x64.zip`

### 使用说明

1. 平台：Windows x64
2. 普通翻译功能无需安装 Tesseract
3. 截图 OCR 功能需要用户机器安装 Tesseract
4. 百度、腾讯、Ollama 仍需用户在设置页自行配置

### SHA256

- `Easy-translation.exe`: `051A737A9EB48E403725944DFC36CBFA5F20A875DE549E4AAC8D0E215C071FDA`
