# Test Root

当前目录用于放置 `Easy-translation` 的自动化测试。

当前已接入的最小 smoke baseline 覆盖：

- `app.py` 入口路径注入
- `config.py` / `settings_manager.py` 的基础加载
- runtime 目录覆盖能力
- 翻译核心的基础无网络行为

本地运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_smoke_tests.ps1
```

或直接运行：

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```
