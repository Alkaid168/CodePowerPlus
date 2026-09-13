# 可用 MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将当前接口骨架升级为可直接使用的单用户学习工作台。

**Architecture:** 保留 FastAPI + SQLite + DeepSeek，按 Repository、Service、Router 分层；前端改为带导航、状态反馈和完整流程的单页工作台。数据模型通过幂等迁移扩展，模型能力可选，规则能力在无 API Key 时仍可用。

**Tech Stack:** Python 3.12, FastAPI, Pydantic, SQLite, vanilla HTML/CSS/JS, pytest, Docker。

**Spec:** `docs/superpowers/specs/2026-09-13-usable-mvp-design.md`

## Global Constraints

- 不依赖学校 OJ 源码或特权数据。
- API Key 只从环境变量读取。
- 所有模型响应经过 Pydantic 校验。
- 每项功能先写失败测试，再实现，再运行全量测试。
- 前端必须提供加载、成功、失败和重试状态。
- 知识点必须使用版本化树，模型不得生成体系外标签。

### Task 0: 知识体系基线

**Files:** Create `data/knowledge_taxonomy.json`, `app/knowledge.py`, `tests/test_knowledge.py`.

- [ ] 按 OI-Wiki 组织方式建立 L1/L2/L3 初始节点和稳定 ID。
- [ ] 实现树结构加载、ID 校验、层级校验和版本号。
- [ ] 为题目分析输出增加主/辅知识点 ID、证据和置信度。
- [ ] 拒绝体系外 ID、重复节点、断裂父子关系和环。
- [ ] 运行全量测试并提交。

### Task 1: 数据层完善

**Files:** Modify `app/repositories.py`; Create `tests/test_repository_mvp.py`.

- [ ] 为题目增加来源、状态、时间字段并提供列表搜索。
- [ ] 为提交保存代码、语言、时间并校验题目存在。
- [ ] 新增辅导记录表和读写方法。
- [ ] 编写分页、搜索、详情和辅导记录测试。
- [ ] 运行 `python -m pytest -q` 并提交。

### Task 2: 服务层拆分与模型可靠性

**Files:** Create `app/services/problem_service.py`, `app/services/tutor_service.py`, `tests/test_services.py`.

- [ ] 将题目分析、辅导、画像和推荐逻辑移出 Router。
- [ ] 增加 DeepSeek 超时、有限重试、结构化解析和明确异常。
- [ ] 增加离线规则辅导和推荐降级路径。
- [ ] 编写服务层成功、失败、降级测试。
- [ ] 运行全量测试并提交。

### Task 3: API 完整化

**Files:** Modify `app/main.py`; Create `tests/test_api_mvp.py`.

- [ ] 增加题目列表筛选、提交历史、辅导记录接口。
- [ ] 统一 404、422、503 错误响应。
- [ ] 为接口定义响应模型，隐藏内部异常和敏感数据。
- [ ] 用 TestClient 覆盖完整学习流程。
- [ ] 运行全量测试并提交。

### Task 4: 工作台 UI

**Files:** Replace `app/static/index.html`; Create `app/static/app.css`, `app/static/app.js`.

- [ ] 实现左侧导航和六个功能视图。
- [ ] 实现题目搜索、分析表单、提交表单、画像卡片、推荐卡片和辅导面板。
- [ ] 加入空状态、加载状态、错误提示、重试按钮和移动端布局。
- [ ] 使用真实 API 完成浏览器流程验证。
- [ ] 运行全量测试并提交。

### Task 5: 数据与部署验收

**Files:** Modify `README.md`, `scripts/seed_demo.py`, `Dockerfile`; Create `tests/test_smoke.py`.

- [ ] 扩充示例题目和示例提交数据，使首次启动可体验完整流程。
- [ ] 增加启动、环境变量、Docker、数据备份说明。
- [ ] 运行应用级冒烟测试、全量 pytest 和 Docker 构建验证。
- [ ] 清理运行时文件，提交最终版本。
