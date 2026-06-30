# Agent 快速上下文

## 一句话状态

FR-Agent 是一个 FineReport 报表交接 Agent。当前远端代码已同步到本地 `main`，项目已有 MVP 能力和 React + FastAPI v2 主线，但文档、依赖、验收体系和后续 PRD 仍需统一。

## 当前目标

当前目标不是开发新功能，而是完成 P0 React + FastAPI 主线稳定化：

- 分析真实项目进度。
- 基于桌面开发 SOP 指南，重建适配当前项目的开发 SOP。
- 规范文档目录和交接方式。
- 梳理 PRD、需求池、迭代路线和评分标准位置。
- 设计多 Agent 写作/开发协作架构。
- 补齐依赖、API contract、验收流程和 Streamlit 下线策略。
- P0 最后再与用户讨论 100 分交接可用性评分标准。

## 关键事实

- GitHub remote：`https://github.com/pandayoung3/fr-agent.git`
- 当前主线：`main...origin/main`
- 现有产品形态：React + FastAPI v2，本地工具优先。
- 旧入口：`ui/app.py` Streamlit，计划下线或归档。
- 当前主线文档已统一到 React + FastAPI v2。
- `requirements.txt` 已体现 FastAPI 主线依赖，Streamlit 依赖暂时保留到下线策略确认。

## 接手提醒

- 先不要删除 Streamlit，除非有明确 Task Brief。
- 先不要实现评分系统；P0 最后只讨论并定稿评分标准。
- 先不要做 MCP / 插件；平台嫁接当前规划为 P2。
- 所有新需求先进入 `docs/product/REQUIREMENTS_BACKLOG.md`，再进入 Sprint。
