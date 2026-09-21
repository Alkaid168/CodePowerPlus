# 知识体系完整建设 Implementation Plan

> 历史记录：本文是 2026-09-13 第一版知识体系（带讲解、难度与前置 DAG）的施工计划。当天晚些时候知识体系已改为纯标签词表（见 `docs/knowledge-standard.md` 的 2026.09.6），因此涉及节点内容字段、前置关系与内容状态的条目不再适用。

> **For agentic workers:** 使用 subagent-driven-development 分工实现，父代理负责接口与整体验收；所有修改留在当前功能分支，不自行提交或推送。

**Goal:** 完成用户要求的知识规范、目录内容、校验、分析、查询、画像推荐、审核、工具、实验和 UI 十一步。

**Architecture:** 版本化 JSON 定义知识树和前置 DAG，SQLite 保存不可变分析与审核审计，业务服务贯通提交证据和学习推荐。接口契约固定在设计文档，各子任务只修改归属文件。

**Tech Stack:** Python 3.12+、FastAPI、Pydantic、jsonschema、SQLite、原生 JavaScript、pytest。

**Spec:** `docs/superpowers/specs/2026-09-13-knowledge-system-design.md`

## Global Constraints

- 本轮用户已授权执行全部十一项；完成前持续工作。
- 原有 19 个知识 ID 不复用；版本有独立快照。
- 保留现有未提交改动与数据库；测试数据库隔离。
- 人工审核与机器样例区分，不宣称样例实验验证教学有效性。
- 中文讲解关键决策，不要求用户手写代码。

## 任务与文件归属

### Task A 知识规范、目录与工具（步骤 1—4、9）
- 文件：app/knowledge.py、data/knowledge_taxonomy*.json、data/taxonomy_versions/、scripts/taxonomy_tool.py、docs/knowledge-standard.md、tests/test_taxonomy_system.py、tests/test_taxonomy_tools.py。
- 先写坏引用、环、Schema、标签约束与往返导入迁移测试并观察失败。
- 实现设计中的 Taxonomy 契约和至少十个领域完整目录基线，原有知识内容改为具体自编内容。
- 核心知识点必须包含适用条件、复杂度、典型错误、学习目标、示例和出处；无专家审核声明。
- 实现无损 JSON/CSV、显式映射迁移和失败保护，运行所属测试。

### Task B 数据与业务闭环（步骤 5—8）
- 文件：app/repositories.py、app/schemas.py、app/services/llm.py、app/services/analysis.py、app/profile.py、app/recommend.py、app/main.py、tests/conftest.py、tests/test_learning_flow.py。
- 先写录入→手工分析→审核→提交→画像→推荐→路径的失败集成测试；另写未知 ID、陈旧审核与历史不可变测试。
- 先实现事务化分析与审核，后统一知识证据和图感知推荐，最后接 HTTP。
- 为既有数据保留 legacy 状态，不猜测历史自由标签。

### Task C 标注与实验（步骤 10）
- 文件：app/evaluation.py、data/evaluation/、scripts/evaluate.py、tests/test_evaluation.py、docs/evaluation.md。
- 先用手算小样本测试 F1、MAE、MRR、候选覆盖和前置违例率。
- 提供至少 12 道自编样例及模拟历史，所有 provenance 明示；提供外部预测输入与可重复的 baseline/graph 比较。
- 程序命令成功输出带版本/样本量/局限的 JSON 和 Markdown；不能将 golden labels 冒充模型预测。

### Task D 前端（步骤 11）
- 文件：app/static/index.html、app/static/app.js、app/static/app.css。
- 使用统一 HTTP 契约实现知识树浏览和搜索、内容详情、手工标签解释、人工审核入口、画像与个人路径。
- 保留现有学习功能并使无 API Key 可通过手工标注使用；用户文本转义；响应错误、加载、空状态和移动端导航可用。
- 所有 UI 文案说明待审核/待评估状态。浏览器验证主路径。

### Task E 集成、部署与文档
- 文件：README.md、requirements.txt、requirements-dev.txt、Dockerfile、scripts/seed_demo.py、docs/learning-notes.md、docs/acceptance-knowledge-system.md、项目记忆文件。
- 运行隔离全量 pytest、CLI 往返和迁移、实验、浏览器主流程。
- 审查跨任务的版本/审核/证据契约并修复问题。
- 输出十一项验收映射、真实验证结果和剩余边界。

## 接口交叉审查

| 任务对 | 共同契约 | 裁定 |
|---|---|---|
| A/B | Taxonomy 方法、原有 ID、版本 | A 保留原 ID；B 从 Taxonomy 取版本，禁止硬编码新版本 |
| A/C | 样例知识 ID | C 优先使用保留的原 ID，新增 ID 向 A 协调 |
| B/C | recommend(problems, mastery, solved_ids, limit=10, taxonomy=None) | C 用带 approved 分析的题目；只用历史计算 mastery，标签正确答案不当预测 |
| B/D | HTTP JSON 契约 | 以设计文档为唯一契约，兼容新增字段 |
| A/D | 节点内容字段 | UI 容忍非核心例子为空，正确显示 content_status |
| A 内部 | 原规范允许 L4、现要求 L1-L3 | 以本次用户明确 L1-L3 为准，更新规范 |
| B 内部 | 旧自由 tags 与稳定 ID | 老数据保留为 legacy；新提交只用 approved 分析产生证据 |
| C 内部 | 示例数据与效果结论 | 输出明确 synthetic fixture 局限，真实教学效果等待未来试用 |
| D 内部 | 新知识功能与既有六视图 | 保留六视图并补齐知识/审核/路径入口 |
