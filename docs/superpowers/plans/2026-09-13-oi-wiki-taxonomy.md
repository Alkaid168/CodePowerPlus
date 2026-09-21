# OI-Wiki 风格知识体系 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 建立仅含 L1/L2/L3 的版本化竞赛算法知识体系，并接入分析、画像、推荐、审核、导入导出、实验和 UI。

**Architecture:** taxonomy.json 是唯一事实源；Taxonomy 服务负责校验和查询；分析、画像、推荐通过稳定 knowledge_id 交互；审核和导入导出保留版本与审计信息。

**Tech Stack:** Python 3.13、FastAPI、Pydantic、SQLite、JSON Schema、pytest、原生 HTML/CSS/JS。

**Spec:** docs/superpowers/specs/knowledge-taxonomy.md

## Global Constraints
- 只允许 L1/L2/L3，不创建 L4。
- 难度仅为入门、基础、进阶、高级。
- AI 只能返回 taxonomy 中存在的 L2/L3 ID。
- 所有关系必须可校验、可追溯、可版本化。
- 每一步都必须有自动化测试。

## Tasks
1. 正式规范与 JSON Schema；2. 扩展 L1/L2/L3 目录和内容；3. 分析标签校验与版本记录；4. 知识树查询接口；5. 图谱画像和推荐；6. 人工审核；7. 导入导出和迁移；8. 标注集与实验脚本；9. UI 知识树、证据和路径；10. 全量验证。
