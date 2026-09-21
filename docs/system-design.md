# 系统设计（已归档）

这里原本是 2026-09-13 的第一版系统设计：目录里写着 `database.py`、`schemas/`、`models/`、
`routers/`、`prompts/`，与实际实现并不一致。

当前设计与代码结构见 [architecture.md](architecture.md)：

- 后端分层：`db → repositories → services → api`；
- 数据模型：不可变分析版本 + 审核审计 + 提交证据快照；
- 前端：无构建步骤的 ES 模块（`app/static/js/`）；
- 接口约定与错误码：见 architecture.md 第四节。

历史文本不再保留，避免和实际代码互相矛盾；如需追溯，请看 git 历史与
`docs/superpowers/plans/` 下的历史计划文件。
