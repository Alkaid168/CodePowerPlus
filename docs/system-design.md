# 码力加加系统设计（第一版）

## 第一个闭环

题目文本 → 题目分析服务 → DeepSeek → JSON 校验 → 保存分析结果 → API 查询。

第一版不接学校 OJ，题目通过 API 手工录入。

## 目录结构

```text
app/
  main.py
  config.py
  database.py
  schemas/
  models/
  services/llm.py
  services/problem_analyzer.py
  routers/
  prompts/
```

## 题目分析字段

`title`、`description`、`source`、`tags`、`difficulty`（1-5）、`difficulty_reason`、`prerequisites`、`solution_idea`、`target_level`、`confidence`、`model_name`、`prompt_version`。

## 数据库

初版包含 `problems` 和 `problem_analyses`；后续加入 `submissions`、`user_skill_states`。同一题允许多次分析，支持后期实验对比。

## API

- `GET /health`
- `POST /api/problems/analyze`
- `GET /api/problems/{id}`

## 可靠性

使用 Pydantic 校验模型输出；非法 JSON 有限重试；保存模型名、提示词版本和原始响应；API Key 只从环境变量读取。

## 后续

先建立规则能力画像 baseline，再比较 BKT 等知识追踪方法；推荐结果保留候选分数和推荐原因。
