# API Contract

版本：P0 React + FastAPI v2 主线

## 当前接口

| Method | Path | 用途 | 输入 | 输出 |
| --- | --- | --- | --- | --- |
| POST | `/api/parse` | 上传并解析 CPT | multipart file `.cpt` | `ParsedReport` |
| POST | `/api/fr-connections` | 读取 FR 连接配置 | `{ fr_webinf_dir }` | connections map |
| POST | `/api/enrich` | 数据库字段增强 | `{ parsed, fr_webinf_dir, passwords }` | `{ parsed, report }` |
| POST | `/api/analyze` | LLM 分析 | `{ parsed }` | SSE progress / done / error |
| POST | `/api/chat` | 报表问答 | `{ parsed, analysis, question, history }` | SSE token / error / done |
| POST | `/api/export/markdown` | 导出 Markdown | `{ parsed, analysis }` | text/markdown |
| POST | `/api/export/html` | 导出 HTML | `{ parsed, analysis }` | text/html |
| POST | `/api/lineage` | 生成血缘图 | `{ parsed }` | `LineageResult` |

## Schema 真相源

- 后端请求模型：`api/main.py`
- 前端类型：`web/src/types.ts`
- 前端客户端：`web/src/api.ts`

## Contract 规则

- `ParsedReport` 字段变化必须同步后端、前端 types、导出文档和验收样例。
- `AnalysisResult` 字段变化必须同步 LLM prompt、前端 tabs、Markdown/HTML 生成器。
- SSE event 必须至少支持 `progress`、`done`、`error`。
- 数据库密码不得进入导出文档或日志。

## 最小请求与响应样例

### `POST /api/parse`

请求：

```text
multipart/form-data
file: report.cpt
```

成功响应：

```json
{
  "file_name": "report.cpt",
  "fr_version": "11.0",
  "sheet_count": 1,
  "report_type": "query",
  "datasets": [],
  "widgets": [],
  "cell_bindings": [],
  "formula_cells": [],
  "highlight_rules_summary": [],
  "db_connections": []
}
```

错误：

- 非 `.cpt` 文件返回 `400`。
- Parser 异常应返回可读错误，不应让前端只看到空白失败。

### `POST /api/fr-connections`

请求：

```json
{
  "fr_webinf_dir": "D:/FineReport/webapps/webroot/WEB-INF"
}
```

成功响应：

```json
{
  "conn_name": {
    "host": "127.0.0.1",
    "port": 3306,
    "database": "demo"
  }
}
```

约束：

- 路径为空或不存在时返回 `{}`。
- 不返回数据库密码。

### `POST /api/enrich`

请求：

```json
{
  "parsed": {},
  "fr_webinf_dir": "D:/FineReport/webapps/webroot/WEB-INF",
  "passwords": {
    "conn_name": "password"
  }
}
```

成功响应：

```json
{
  "parsed": {},
  "report": {
    "success": [],
    "failed": [],
    "skipped": []
  }
}
```

约束：

- 数据库增强失败不能污染原始 `parsed`。
- 密码不能写入日志、导出文档或响应体。

### `POST /api/analyze`

请求：

```json
{
  "parsed": {}
}
```

SSE 响应：

```text
data: {"type":"progress","step":1,"message":"正在整理报表结构信息..."}

data: {"type":"done","data":{"purpose":"...","indicator_dict":[]}}
```

错误事件：

```text
data: {"type":"error","message":"..."}
```

### `POST /api/chat`

请求：

```json
{
  "parsed": {},
  "analysis": {},
  "question": "这个报表的筛选条件是什么？",
  "history": []
}
```

SSE 响应：

```text
data: {"type":"token","text":"..."}

data: {"type":"done"}
```

### `POST /api/export/markdown`

请求：

```json
{
  "parsed": {},
  "analysis": {}
}
```

响应：

```text
# 报表交接文档
...
```

媒体类型：`text/markdown; charset=utf-8`

### `POST /api/export/html`

请求：

```json
{
  "parsed": {},
  "analysis": {}
}
```

响应：

```html
<!doctype html>
<html lang="zh-CN">
...
</html>
```

媒体类型：`text/html`

### `POST /api/lineage`

请求：

```json
{
  "parsed": {}
}
```

成功响应：

```json
{
  "mermaid": "graph TD",
  "mermaid_raw": "graph TD",
  "dot": "digraph G {}",
  "sql_driving_widget_names": [],
  "option_driving_widget_names": [],
  "unmatched_widget_names": []
}
```

## 错误约定

- 同步接口使用 HTTP 状态码表达请求失败。
- SSE 接口使用 `type: "error"` 表达业务或 LLM 失败。
- 前端必须展示可读错误，不能只停留在 loading。
- 数据库增强、LLM 分析和导出失败应能独立定位。

## P0 状态

- 已补最小请求/响应示例。
- 已明确 SSE 最小事件格式。
- TODO(CONFIRM): 是否将 FastAPI OpenAPI schema 作为 P1 平台化前置 contract。
