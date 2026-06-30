# 架构说明

## 当前主线

```text
React + TypeScript + Vite
-> web/src/api.ts
-> FastAPI api/main.py
-> Python core modules
   -> parser/cpt_parser.py
   -> agent/db_connector.py
   -> agent/lineage_builder.py
   -> agent/llm_analyzer.py
   -> agent/doc_generator.py
   -> agent/html_generator.py
```

## 技术栈

| 层 | 技术 | 状态 |
| --- | --- | --- |
| 前端 | React 19 + TypeScript + Vite | 主线 |
| 样式 | Tailwind CSS v4 + custom CSS | 主线 |
| 后端 | FastAPI | 主线 |
| LLM | OpenAI SDK 兼容接口 | 主线 |
| 数据库元数据 | PyMySQL + information_schema | 当前支持 MySQL / MariaDB |
| 旧 UI | Streamlit | 历史入口，计划下线 |

## 数据流

```text
CPT file
-> /api/parse
-> parsed
-> optional /api/enrich
-> /api/analyze
-> analysis
-> /api/lineage
-> /api/export/markdown or /api/export/html
```

## 架构边界

- React 只负责展示、状态和用户交互。
- FastAPI 负责文件、接口、SSE 和导出响应。
- Python core 不依赖 React。
- Parser 不调用 LLM。
- LLM 分析不读取数据库密码。
- DB connector 只读元数据，不读业务数据。

## 当前架构风险

- Streamlit 和 React 并存会增加维护分叉风险。
- 固定样例 CPT 尚未确认是否可以入仓，验收仍依赖人工样例。
- API contract 已文档化，但尚未自动从 OpenAPI 校验。
