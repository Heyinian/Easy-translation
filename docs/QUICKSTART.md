# 快速上手

这是一份面向新开发者和测试人员的最短启动指南。

## 文档导航

- 文档索引：DOCS_INDEX.md
- 项目总览：../README.md
- 开发者归档：DEVELOPER_GUIDE.md
- 部署说明：DEPLOYMENT.md
- 测试说明：TESTING.md
- 发布说明：RELEASE_NOTES.md
- 变更记录：CHANGELOG.md

## 1. 进入项目目录

```powershell
cd <项目目录>\Easy-translation
```

## 2. 使用推荐环境启动

```powershell
.\.venv312\Scripts\python.exe app.py
```

## 3. 如果依赖未安装

```powershell
pip install -r requirements.txt
```

## 4. 如果要使用截图 OCR（可选）

安装 Tesseract：

- https://github.com/UB-Mannheim/tesseract/wiki

默认路径通常为：

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

未安装 Tesseract 不影响应用启动、设置保存和普通翻译功能。

## 5. 启动后优先验证

1. 输入框手动翻译
2. 剪贴板翻译
3. 输入窗口翻译
4. 关闭或最小化后是否能从托盘恢复
5. 三击空格触发
6. 截图 OCR 翻译（如需）

## 6. 当前默认触发方式

- 截图翻译：alt+shift+s
- 剪贴板翻译：alt+shift+c
- 显示窗口：alt+shift+t
- 输入窗口翻译：triple_space
- 三击空格窗口期：1.2 秒

## 7. 需要看更完整资料时

- 用户入口说明：README.md
- 用户入口说明：../README.md
- 开发者归档：DEVELOPER_GUIDE.md
- 部署说明：DEPLOYMENT.md
- 测试说明：TESTING.md
- 发布说明：RELEASE_NOTES.md
- 变更记录：CHANGELOG.md
