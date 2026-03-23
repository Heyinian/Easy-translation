# 文档索引

本文档用于帮助不同角色快速找到合适的项目资料入口。

## 按角色查阅

### 0. AI 开发者 / 异地接手者（首选）

- [PROJECT_STATUS.md](PROJECT_STATUS.md) — 当前版本、Bug 列表、架构速查、避坑清单

### 1. 首次查看项目

- [README.md](../README.md)

### 2. 新开发者快速启动

- [QUICKSTART.md](QUICKSTART.md)

### 3. 接手代码实现与架构

- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

### 4. 部署、打包、分发

- [DEPLOYMENT.md](DEPLOYMENT.md)

### 5. 测试与验收

- [TESTING.md](TESTING.md)

### 6. 查看发布说明

- [RELEASE_NOTES.md](RELEASE_NOTES.md)

### 7. 查看阶段性改动历史

- [CHANGELOG.md](CHANGELOG.md)

---

## 按目的查阅

### 想快速了解当前项目状态和待处理 Bug

- [PROJECT_STATUS.md](PROJECT_STATUS.md)

### 想知道项目现在能做什么

- [README.md](../README.md)

### 想在本机最快跑起来

- [QUICKSTART.md](QUICKSTART.md)

### 想了解设置、热键、三击空格、翻译链路

- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

### 想知道如何打包成 exe

- [DEPLOYMENT.md](DEPLOYMENT.md)

### 想做功能验证或回归测试

- [TESTING.md](TESTING.md)

### 想快速了解每个版本对使用者的影响

- [RELEASE_NOTES.md](RELEASE_NOTES.md)

### 想回溯某次变更是在哪个版本引入的

- [CHANGELOG.md](CHANGELOG.md)

---

## 文档体系说明

| 文档 | 更新频率 | 维护责任 |
|------|----------|----------|
| PROJECT_STATUS.md | 每次改动后更新当前版本号 / Bug 状态 | 每次发版必须同步 |
| CHANGELOG.md | 每个版本追加一个版本块，**不覆盖历史** | 每次发版必须同步 |
| DEVELOPER_GUIDE.md | 架构或模块职责发生变化时更新 | 按需 |
| TESTING.md | 新增功能或回归重点变化时更新 | 按需 |
| DEPLOYMENT.md | 依赖或部署流程变化时更新 | 按需 |
| RELEASE_NOTES.md | 每个版本追加用户可见变化 | 每次发版 |
| QUICKSTART.md | 启动命令或环境要求变化时更新 | 按需 |

---

## 强制归档规则

开发规范文件：[.github/copilot-instructions.md](../.github/copilot-instructions.md)

每次修改源代码（`.py`）后，AI 开发者必须在结束会话前执行增量归档，步骤如下：

1. 递增 patch 版本号（`PROJECT_STATUS.md` → `当前版本`）
2. 在 `CHANGELOG.md` 顶部新增版本块（不修改历史块）
3. 更新 `PROJECT_STATUS.md` 的 Bug 表和功能规划表
4. 按需更新 `DEVELOPER_GUIDE.md`
5. 输出"归档确认清单"

**快速触发**：在 Copilot Chat 中输入 `/archive-dev-session` 可一键执行完整归档流程。


### 想知道最近改了什么

- [CHANGELOG.md](CHANGELOG.md)

## 当前文档关系

1. README.md 是总入口
2. QUICKSTART.md 是最短启动路径
3. DEVELOPER_GUIDE.md 是开发交接文档
4. DEPLOYMENT.md 是部署与分发说明
5. TESTING.md 是测试与验收文档
6. RELEASE_NOTES.md 是面向使用者的版本说明
7. CHANGELOG.md 是版本演进记录