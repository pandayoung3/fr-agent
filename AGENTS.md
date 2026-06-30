# AGENTS.md

本文件是 FR-Agent 仓库的 AI Agent 协作入口。

## 项目判断

FR-Agent 当前不是空仓起步项目，而是已有 MVP 和 React + FastAPI v2 演进线的 FineReport 报表交接工具。后续开发默认围绕真实代码主线展开：

```text
React + TypeScript + Vite
-> FastAPI
-> Python core modules
   -> parser
   -> db metadata connector
   -> LLM analyzer
   -> lineage builder
   -> Markdown / HTML generator
```

旧版 `ui/app.py` Streamlit 是历史 MVP 入口。PRD 当前倾向为尽快下线，不再作为主线新增能力。

## 必读顺序

1. `docs/project/AGENT_QUICK_CONTEXT.md`
2. `docs/project/PROJECT_STATUS.md`
3. `docs/product/PRD.md`
4. `docs/product/REQUIREMENTS_BACKLOG.md`
5. `docs/project/DEVELOPMENT_SOP.md`
6. `docs/architecture/ARCHITECTURE.md`
7. `docs/agents/MULTI_AGENT_WRITING_ARCHITECTURE.md`
8. `docs/product/SCORING_SYSTEM_DRAFT.md`
9. `docs/templates/SCORING_REVIEW.md`
10. `docs/project/SPRINT_PLAN.md`
11. `docs/project/P0_VALIDATION.md`
12. `docs/project/STREAMLIT_DEPRECATION.md`
13. `docs/project/HANDOFF.md`

## 工作原则

- 先写 Task Brief，再改代码。
- 非简单任务默认评估是否启用 Codex subagent；开发、测试、Bug 修复、Review、Handoff 都有对应 subagent 角色。
- 只读当前任务相关文件，避免把旧结论误当事实。
- 不跨 Sprint 提前实现能力。
- 不把 AI 推断写成事实；未确认内容使用 `TODO(CONFIRM)`。
- 高风险变更必须更新 `docs/project/HANDOFF.md`。
- React + FastAPI 为主线；Streamlit 只读参考，除非用户明确要求。

## Subagent 默认角色

| 场景 | 默认 subagent |
| --- | --- |
| Parser / CPT 样例 | Parser Subagent + Test Subagent |
| API / SSE / contract | API Subagent + Review Subagent |
| React 前端 | UI Subagent + Test Subagent |
| 数据库增强 | DB Subagent + Test Subagent |
| LLM 分析 | LLM Subagent + Review Subagent |
| 导出文档 | Export Subagent + Review Subagent |
| Bug 修复 | Bugfix Subagent + Test Subagent |
| 需求 / SOP / Handoff | Product Subagent + Context Steward |

## 默认验证

文档任务：

```bash
git diff --check
git status --short --branch
```

Python 任务：

```bash
python -m compileall api agent parser scripts
```

Web 任务：

```bash
cd web
npm run build
npm run lint
```

如果本地缺依赖或 API key，记录阻断原因和替代静态检查。
