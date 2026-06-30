# Handoff

更新日期：2026-06-30

## 当前目标

基于已同步的真实 GitHub 项目，完成 React + FastAPI v2 主线 P0 稳定化准备：统一文档、依赖、API contract、验收流程、Streamlit 下线策略，并把 100 分评分标准列为 P0 最后讨论项。

## 已完成

- 确认当前本地 `main` 跟踪 `origin/main`。
- 确认真实项目已有 React + FastAPI v2、Python core、旧 Streamlit、devlog、操作文档。
- 读取桌面 `开发SOP/AI协作开发SOP完整指南.md`。
- 新增项目级 `AGENTS.md`。
- 新增 `docs/` 文档体系。
- 改写根 `README.md` 为项目入口。
- 改写 `操作文档.md` 为 React + FastAPI v2 操作指南。
- 删除无业务价值的 Vite 模板文档 `web/README.md`。
- 补齐 `requirements.txt` 中 FastAPI 主线运行依赖。
- 补全 API contract 最小请求/响应样例。
- 新增 P0 验收流程。
- 新增 Streamlit 下线策略。
- 将 100 分交接可用性评分标准定稿为 P0 初版，自动评分实现放到 P1。
- 新增 `docs/templates/SCORING_REVIEW.md`，用于样例 CPT 初评。
- 使用 `MS填报-脱敏-llp.cpt` 完成 Parser + 血缘 + 导出静态初评，并修复填报类型识别与 EmbeddedTableData 血缘问题，记录在 `docs/project/SCORING_REVIEW_MS_WRITEBACK_LLP.md`。
- 新增 `docs/project/REAL_DB_VALIDATION_PLAN.md`，明确需要真实 MySQL + FineReport DBTableData 样例验证客户场景。
- 实际启用 Codex subagent 参与 SOP 设计审查：
  - Development Subagent：开发角色、ownership、冲突规则。
  - Test/Validation Subagent：验证命令、API smoke、评分记录证据格式。
  - Bugfix/Review Subagent：缺陷分级、修复流转、回归验证。
- 经用户许可，修复 `web/src/components/tabs/LineageTab.tsx` 的 React lint 问题。
- 将平台嫁接定位为 P2 MCP / 插件方向。

## 关键决策

- React + FastAPI 是后续主线。
- 本地工具是 P0 交付形态。
- Streamlit 不再新增能力。
- P0 先稳定化，不做新功能。
- P0 评分标准已定稿，不实现自动评分。
- AI 输出不可替代人工验收。

## 修改文件

- `README.md`
- `操作文档.md`
- `AGENTS.md`
- `requirements.txt`
- `web/src/components/tabs/LineageTab.tsx`
- `docs/README.md`
- `docs/project/AGENT_QUICK_CONTEXT.md`
- `docs/project/PROJECT_STATUS.md`
- `docs/project/DEVELOPMENT_SOP.md`
- `docs/project/DOCUMENTATION_STANDARD.md`
- `docs/project/SPRINT_PLAN.md`
- `docs/project/HANDOFF.md`
- `docs/project/DOCUMENT_CLEANUP.md`
- `docs/project/P0_VALIDATION.md`
- `docs/project/REAL_DB_VALIDATION_PLAN.md`
- `docs/project/SCORING_REVIEW_MS_WRITEBACK_LLP.md`
- `docs/project/STREAMLIT_DEPRECATION.md`
- `docs/product/PRD.md`
- `docs/product/REQUIREMENTS_BACKLOG.md`
- `docs/product/SCORING_SYSTEM_DRAFT.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/API_CONTRACT.md`
- `docs/agents/MULTI_AGENT_WRITING_ARCHITECTURE.md`
- `docs/templates/TASK_BRIEF.md`
- `docs/templates/AGENT_BRIEF.md`
- `docs/templates/REVIEW_REPORT.md`
- `docs/templates/SCORING_REVIEW.md`

## 删除文件

- `web/README.md`

## 验证结果

- 已通过：`git diff --check`
- 已通过：`rg -n " +$" AGENTS.md docs README.md 操作文档.md requirements.txt web\src\components\tabs\LineageTab.tsx` 无输出。
- 已通过：`python -m compileall -q api agent parser scripts`，使用 `PYTHONDONTWRITEBYTECODE=1`，未产生 Git 变更。
- 已通过：`cd web && npm install`。
- 已通过：`cd web && npm run build`。
- 已通过：`cd web && npm run lint`。
- 已通过：`MS填报-脱敏-llp.cpt` Parser + API smoke 静态初评，无解析错误；修复后得分 `70 / 100`，记录见 `docs/project/SCORING_REVIEW_MS_WRITEBACK_LLP.md`。
- 注意：`npm run build` 仍提示部分 chunks 大于 500 kB，这是 Vite 构建优化提醒，不阻断 P0。
- 已确认：`git status --short --branch` 显示文档、`requirements.txt` 变更和 `web/README.md` 删除。
- 已确认：`git diff --name-status` 未显示 `api/`、`agent/`、`parser/`、`scripts/` 改动；`web/src/components/tabs/LineageTab.tsx` 为经用户许可的最小 lint 修复。
- 注意：`npm install` 报告 3 个 moderate severity vulnerabilities，尚未运行 `npm audit fix`，避免自动改动依赖树。

## 开放问题

- Streamlit 下线节奏仍待确认。
- 平台嫁接保持 P2，优先考虑 MCP / 插件方向。
- P0 全链路评分已改用 `习题 8.cpt` 完成，记录见 `docs/project/SCORING_REVIEW_P0_CLOSURE.md`。
- 本地 MySQL + FineReport 真实 DBTableData 样例进入 P1，用户确认不阻塞 P0。

## 建议下一步

P0 主线验证已闭环，100 分评分标准已定稿，并已形成 `86 / 100` 的全链路收口基线。下一步进入 P1：优先准备真实 MySQL + FineReport DBTableData CPT、API smoke 自动化、公式坐标校验、多轮问答验收和评分系统 MVP。后续开发、测试、Bug 修复、Review 按 `docs/agents/MULTI_AGENT_WRITING_ARCHITECTURE.md` 默认启用对应 Codex subagent。

## P0 收口基线（2026-06-30）

P0 已收口为 React + FastAPI 本地工具基线。用户已确认真实 MySQL + FineReport DBTableData CPT 开发需要时间，因此该全链路验证移入 P1，不阻塞 P0。

最新 P0 全链路评分记录见 `docs/project/SCORING_REVIEW_P0_CLOSURE.md`：

- 样例：`习题 8.cpt`。
- 范围：上传、解析、AI 分析、问答、数据血缘、Markdown / HTML 导出预览。
- 结果：`86 / 100`，B 级。
- 结论：P0 可收口，进入 P1。

P0 收口后剩余关键 P1 任务：

- 准备真实 MySQL + FineReport DBTableData CPT，并验证客户场景。
- 建立 API smoke 自动化测试。
- 增强公式坐标和字段位置校验。
- 系统验证多轮问答。
- 基于 P0 评分标准实现评分系统 MVP。

Subagent 引入时机：

- P0 收口阶段仅轻量启用 Review/Test Subagent 做文档和验收复核。
- P1 起默认启用 subagent 协作；跨 Parser / API / UI / DB / LLM / Export 任意两个以上模块的任务，必须显式分配对应 subagent。
