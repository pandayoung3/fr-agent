# P0 验收流程

## 目标

P0 验收不是证明产品已经完美，而是证明 React + FastAPI v2 主线可以被稳定启动、验证和交接。

## 验收前置

- 本地分支基于 `main...origin/main`。
- 已安装 Python 依赖：`pip install -r requirements.txt`。
- 已安装前端依赖：`cd web && npm install`。
- 已复制 `.env.example` 为 `.env`，并填写可用 LLM 配置。
- 如需数据库增强，准备 FineReport `WEB-INF` 路径和只读测试数据库密码。

## 最小验证命令

```bash
git diff --check
python -m compileall api agent parser scripts
cd web
npm run build
npm run lint
```

如果本地未安装依赖或没有网络，必须在 `docs/project/HANDOFF.md` 记录阻断原因。

## 主线启动验收

### 后端

```bash
python -m uvicorn api.main:app --reload --port 8000
```

验收点：

- FastAPI 可在 `http://127.0.0.1:8000` 启动。
- OpenAPI 可访问 `http://127.0.0.1:8000/docs`。
- 后端启动不依赖 Streamlit。

### 前端

```bash
cd web
npm run dev
```

验收点：

- React 可在 `http://localhost:5173` 启动。
- 前端请求统一走 `/api`。
- 上传、分析、问答、导出入口在 React 主线完成，不跳转到 Streamlit。

## 样例 CPT 人工验收

当前仓库尚未确认是否允许提交脱敏样例 CPT，因此 P0 先采用人工样例验收。

建议至少准备三类样例：

| 样例 | 目的 | 必须覆盖 |
| --- | --- | --- |
| Query CPT | 查询型报表 | 数据集、SQL、参数控件、展示字段 |
| Writeback CPT | 填报型报表 | 填报配置、主键、字段映射 |
| Complex CPT | 复杂逻辑报表 | 公式、父子格、条件高亮、交互链路 |

## 功能链路验收

| 步骤 | 验收标准 |
| --- | --- |
| 上传 CPT | `/api/parse` 返回 `ParsedReport`，无未解释崩溃 |
| 结构解析 | 能看到数据集、控件、单元格绑定、公式和高亮信息 |
| 数据库增强 | 成功时补字段类型/注释，失败时不阻塞后续分析 |
| AI 分析 | `/api/analyze` SSE 返回 progress 和 done，失败时返回 error |
| 数据血缘 | `/api/lineage` 返回 mermaid / dot 结构 |
| 问答 | `/api/chat` 回答基于当前 parsed + analysis |
| 导出 | Markdown / HTML 均可生成，并提示人工核实 |
| 前端体验 | 用户能看清当前阶段、错误原因和下一步动作 |

## Test/Validation Subagent 协作

P0 后的样例验证默认启用 Test/Validation Subagent。该 subagent 不直接改业务代码，负责收集证据和填写评分记录。

| 角色 | 职责 | 输出 |
| --- | --- | --- |
| Validation Lead | 确认样例、范围、`.env`、LLM key、DB 条件 | 验收范围和阻断项 |
| Parser Sample Validator | 验证 Query / Writeback / Complex CPT | Parser 摘要和异常 |
| API Smoke Validator | 验证 parse、lineage、export、analyze、chat | 接口状态码和核心字段 |
| Web Validator | 验证 build/lint 和 React 主流程 | 命令结果和交互观察 |
| LLM/Chat Validator | 验证 SSE 分析、问答上下文和 AI 边界 | 分析/问答证据 |
| Scoring Recorder | 按评分模板打分 | `SCORING_REVIEW_*.md` |

验证证据必须包含：

- 分支 / commit 或工作区状态。
- 样例 CPT 路径和类型。
- 是否使用 DB 增强。
- 是否使用 LLM。
- 已运行命令。
- 未运行命令和阻断原因。
- API smoke 结果。
- 扣分原因和 P1 问题。

## P0 最后一步：评分标准

在以上链路跑通后，进入评分标准讨论。评分标准应模拟真实交接 Agent 从复现 CPT 报表的角度评估输出是否可用，同时纳入前端交互质量。

评分标准先定稿文档，不在 P0 内实现自动评分功能。
