# FR-Agent 开发 SOP

版本：0.1
来源：桌面 `开发SOP/AI协作开发SOP完整指南.md` 的项目化改写

## 1. 项目适配原则

FR-Agent 当前是已有 MVP 的稳定化项目，SOP 应重点保护：

- React + FastAPI 主线。
- CPT 解析 contract。
- LLM 输出 schema。
- Markdown / HTML 交接文档结构。
- 数据库元数据安全边界。
- Handoff 与 devlog 的连续性。

## 2. 标准任务流程

```text
Task Brief -> Subagent 分工 -> 定向读取 -> 计划 -> 实现 -> 验证 -> 审查 -> Handoff
```

### 2.1 Task Brief

每个任务开始前必须明确：

- 用户故事。
- 包含范围。
- 不包含范围。
- 影响模块。
- 验收标准。
- 验证命令。

模板见 `docs/templates/TASK_BRIEF.md`。

### 2.2 Subagent 分工

每个非简单任务必须判断是否启用 Codex subagent。以下场景默认启用：

- 涉及 Parser / API / UI / DB / LLM / Export 两个以上模块。
- 需要真实 CPT 样例评分。
- 需要 Bug 修复后独立回归。
- 需要 Review 检查风险或漏测。
- 需要同步 PRD、需求池、Handoff 等长期文档。

Subagent brief 必须明确：

- 角色。
- 目标。
- 必读文件。
- 允许修改的文件。
- 禁止事项。
- 验证命令。
- 输出格式。

模板见 `docs/templates/AGENT_BRIEF.md`。

### 2.3 定向读取

根据任务读取最少必要文件：

| 任务 | 必读 |
| --- | --- |
| Parser | `parser/cpt_parser.py`、相关 devlog、样例验收记录 |
| API | `api/main.py`、`web/src/api.ts`、`web/src/types.ts` |
| React UI | `web/src/App.tsx`、相关 component / tab |
| LLM | `agent/llm_analyzer.py`、PRD 输出 schema |
| 文档导出 | `agent/doc_generator.py`、`agent/html_generator.py` |
| 数据库增强 | `agent/db_connector.py`、安全边界文档 |
| SOP / PRD | `docs/product/PRD.md`、`docs/project/HANDOFF.md` |

### 2.4 实现规则

- 不绕过 FastAPI contract 直接让前端解释后端内部结构。
- 不改变 `analysis` schema，除非同步更新 types、API contract、导出文档和验收。
- 不读取真实业务数据，数据库增强只读元数据。
- LLM 输出必须允许失败和降级。
- 导出文档中的 AI 推断必须提示人工核实。
- Streamlit 不新增能力，除非用户明确恢复旧版主线。

## 3. 验证规则

最低验证：

```bash
git diff --check
git status --short --branch
```

Python：

```bash
python -m compileall api agent parser scripts
```

Web：

```bash
cd web
npm run build
npm run lint
```

接口任务需补充：

- parse 成功路径。
- analyze SSE 成功/失败路径。
- export Markdown / HTML。
- lineage 输出。

如果本地缺依赖、样例或 API key，必须记录替代检查。

## 4. Bug 修复规则

Bug 修复默认至少包含两个角色：

- Bugfix Subagent：负责最小修复。
- Test 或 Review Subagent：负责复现验证和回归检查。

严重 bug 必须补充：

- 复现路径。
- 根因说明。
- 最小修复范围。
- 回归命令。
- 是否影响评分标准。
- 是否需要更新需求池。

## 5. 完成定义

任务完成必须满足：

- 范围内事项已完成。
- 范围外事项未提前实现。
- 验证命令或人工验收路径已记录。
- 影响文档已同步。
- Subagent 结论已被主 Agent 审查并整合。
- `docs/project/HANDOFF.md` 已更新。
- 开放问题使用 `TODO(CONFIRM)` 标注。
