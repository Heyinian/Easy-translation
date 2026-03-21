# 贡献指南

感谢您对本项目的关注！我们欢迎各种形式的贡献。

## 提交规范

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/) 规范：

### 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- **feat**: 新功能
- **fix**: 修复bug
- **docs**: 文档更新
- **style**: 代码格式调整（不改变代码逻辑）
- **refactor**: 代码重构
- **perf**: 性能优化
- **test**: 测试相关
- **chore**: 构建/工具/依赖更新
- **ci**: CI/CD配置更改

### 示例

```
feat(ocr): add screenshot translation feature

- Implement screenshot capture
- Add OCR processing pipeline
- Support multiple OCR engines

Closes #123
```

```
fix(translator): handle empty input correctly
```

```
docs: update README with installation instructions
```

## 提交前检查清单

- [ ] 代码符合项目风格
- [ ] 添加或更新了相关文档
- [ ] 提交信息清晰描述了变化
- [ ] 本地测试通过
- [ ] 没有增加不必要的依赖

## 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/Heyinian/Easy-translation.git
cd Easy-translation

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 开发模式运行
python app.py
```

## 分支策略

- `main`: 稳定发布版本
- `develop`: 开发分支（如果存在）
- `feature/*`: 功能分支
- `fix/*`: 修复分支

建议为新功能创建分支：
```bash
git checkout -b feature/your-feature-name
```

## 提交流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat(scope): Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 代码质量

- 遵循 PEP 8 风格指南
- 添加适当的注释和文档字符串
- 编写单元测试（如适用）

## 问题反馈

- 使用 GitHub Issues 报告bug
- 在标题中清晰描述问题
- 提供复现步骤和环境信息

感谢您的贡献！
