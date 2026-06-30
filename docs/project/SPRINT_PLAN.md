# Sprint 计划

## 当前 Sprint：P0 React + FastAPI 主线稳定化

目标：把 React + FastAPI v2 主线统一为可启动、可验证、可交接的项目基线；评分标准放在 P0 最后一步讨论定稿。

## 范围

包含：

- 当前项目进度分析。
- 开发 SOP。
- PRD 与需求池。
- React + FastAPI v2 主线文档统一。
- 后端依赖补齐。
- API contract。
- 固定样例验收流程。
- Streamlit 下线策略。
- P0 最后一步：100 分交接可用性评分标准讨论稿。
- 文档规范。
- 多 Agent 写作和开发架构。
- Handoff。

不包含：

- 新功能开发。
- 直接删除 Streamlit。
- 修改 React / FastAPI 业务代码。
- 实现评分系统。
- 实现 MCP / 插件。

## 任务清单

- [x] 确认本地已同步 GitHub 真实 `main`。
- [x] 读取桌面开发 SOP 指南。
- [x] 分析当前能力和主要缺口。
- [x] 建立 SOP、PRD、需求池、评分标准。
- [x] 建立多 Agent 写作架构。
- [x] 统一 README 与 `操作文档.md` 到 React + FastAPI v2。
- [x] 补齐 FastAPI 主线运行依赖。
- [x] 固化 API contract 最小请求/响应样例。
- [x] 建立 P0 验收流程。
- [x] 建立 Streamlit 下线策略。
- [x] 运行可用验证命令并记录阻断项。
- [x] 修复 `LineageTab` lint 问题并完成 P0 验证闭环。
- [x] 建立 100 分评分标准和样例评分记录模板。
- [x] 与用户讨论并定稿 100 分评分标准权重。
- [x] 根据评分标准对 `MS填报-脱敏-llp.cpt` 做 Parser 静态初评。
- [ ] 根据评分标准对 `MS填报-脱敏-llp.cpt` 做 LLM + 前端全链路评分。
- [ ] 准备真实 MySQL + FineReport DBTableData 样例，验证客户场景可用性。

## 开放问题

- TODO(CONFIRM): Streamlit 是直接删除还是先 deprecated。
- TODO(CONFIRM): 是否允许脱敏样例 CPT 入仓。
