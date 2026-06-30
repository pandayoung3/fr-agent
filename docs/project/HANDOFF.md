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

- TODO(CONFIRM): Streamlit 下线节奏。
- TODO(CONFIRM): 平台嫁接是否保持 P2。
- TODO(CONFIRM): 是否继续对 `MS填报-脱敏-llp.cpt` 跑 LLM + 前端全链路评分。
- TODO(CONFIRM): 是否开始准备本地 MySQL + FineReport 真实 DBTableData 样例。

## 建议下一步

P0 主线验证已闭环，100 分评分标准已定稿，首个样例 CPT 已完成静态初评。后续开发、测试、Bug 修复、Review 必须按 `docs/agents/MULTI_AGENT_WRITING_ARCHITECTURE.md` 启用对应 Codex subagent。建议下一步启动 FastAPI + React，对 `MS填报-脱敏-llp.cpt` 跑上传、AI 分析、问答和导出全链路评分。
