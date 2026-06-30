# FR-Agent

FR-Agent 是一个 FineReport 报表交接工具。用户上传 `.cpt` 文件后，系统解析报表结构，结合可选数据库字段元数据和 LLM 语义分析，生成可核实、可交付的 Markdown / HTML 交接文档，并支持围绕报表上下文追问。

## 当前阶段

项目已从 Streamlit MVP 演进到 React + FastAPI v2。当前重点不是继续堆新功能，而是进入 P0 稳定化：

- 统一 React + FastAPI 主线文档。
- 补齐依赖和启动说明。
- 固化 API contract 和样例验收流程。
- 明确 Streamlit 下线策略。
- 为后续评分系统和 Agent 平台嫁接预留架构。

## 主线架构

```text
React + TypeScript + Vite
-> FastAPI
-> Python core modules
   -> parser/cpt_parser.py
   -> agent/db_connector.py
   -> agent/lineage_builder.py
   -> agent/llm_analyzer.py
   -> agent/doc_generator.py
   -> agent/html_generator.py
```

旧版 `ui/app.py` Streamlit 是历史 MVP 入口，后续不再作为主线新增能力。

## 已具备能力

- CPT 深度解析：数据集、SQL、参数控件、单元格绑定、公式、格式、父子格、条件高亮、填报配置。
- 数据库字段增强：读取 FineReport WEB-INF 连接配置，并查询 MySQL `information_schema` 字段元数据。
- 数据血缘：生成控件、SQL 参数、数据集、展示字段之间的链路图。
- LLM 分析：生成用途、布局、交互链路、字段语义、公式解释、指标字典、复现步骤和风险点。
- 报表问答：基于 parsed + analysis 做自然语言追问。
- 文档导出：生成 Markdown 和自包含 HTML 交接文档。

## 快速开始

### 1. 后端

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn api.main:app --reload --port 8000
```

> `requirements.txt` 已包含 FastAPI 主线依赖，并暂时保留 Streamlit 历史入口依赖。后续是否删除 Streamlit 依赖，按 P0 下线策略确认。

### 2. 前端

```bash
cd web
npm install
npm run dev
```

浏览器访问：

```text
http://localhost:5173
```

### 3. 环境变量

复制 `.env.example` 为 `.env`，填写 LLM 配置：

```env
SILICONFLOW_API_KEY=sk-your-key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=deepseek-ai/DeepSeek-V4-Flash
```

## 文档入口

- [操作文档](操作文档.md)
- [Agent 协作入口](AGENTS.md)
- [项目快速上下文](docs/project/AGENT_QUICK_CONTEXT.md)
- [项目进度](docs/project/PROJECT_STATUS.md)
- [PRD](docs/product/PRD.md)
- [需求池](docs/product/REQUIREMENTS_BACKLOG.md)
- [开发 SOP](docs/project/DEVELOPMENT_SOP.md)
- [P0 验收流程](docs/project/P0_VALIDATION.md)
- [Streamlit 下线策略](docs/project/STREAMLIT_DEPRECATION.md)
- [架构说明](docs/architecture/ARCHITECTURE.md)
- [API Contract](docs/architecture/API_CONTRACT.md)
- [多 Agent 架构](docs/agents/MULTI_AGENT_WRITING_ARCHITECTURE.md)
- [交接可用性评分标准](docs/product/SCORING_SYSTEM_DRAFT.md)
- [Handoff](docs/project/HANDOFF.md)

## 验证命令

```bash
git diff --check
python -m compileall api agent parser scripts
cd web
npm run build
npm run lint
```

如果本地缺依赖、样例文件或 API key，需要在 Handoff 中记录无法验证原因和替代检查。

## License

MIT
