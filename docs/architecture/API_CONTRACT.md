# API Contract

版本：P1.5 React + FastAPI v2 主线

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
| POST | `/api/score` | 生成交接可用性评分 | `{ parsed, analysis, lineage }` | `ScoreResult` |
| POST | `/api/validate/formulas` | 校验公式引用与风险函数 | `{ parsed }` | `FormulaValidationResult` |
| POST | `/api/change-impact` | 变更定位与修改建议 | `{ parsed, analysis, change_request, lineage }` | `ChangeImpactResult` |
| GET | `/api/llm/config` | 读取本地 LLM 配置状态 | - | `{ configured, provider, base_url, model, api_key_hint }` |
| POST | `/api/llm/test` | 测试本地 LLM 配置 | `{ prompt }` | `{ ok, model, message }` |

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

### `POST /api/score`

请求：

```json
{
  "parsed": {},
  "analysis": {},
  "lineage": {
    "mermaid_raw": "flowchart LR"
  }
}
```

成功响应：

```json
{
  "score": 86,
  "grade": "B",
  "dimensions": [],
  "top_findings": [],
  "recommendations": []
}
```

### `POST /api/validate/formulas`

请求：

```json
{
  "parsed": {}
}
```

成功响应：

```json
{
  "total": 2,
  "issue_count": 1,
  "items": [
    {
      "pos": "D1",
      "formula": "=SUM(Z99)",
      "references": ["Z99"],
      "ranges": [],
      "missing_references": ["Z99"],
      "risky_functions": [],
      "status": "review",
      "messages": []
    }
  ]
}
```

### `POST /api/change-impact`

请求：

```json
{
  "parsed": {},
  "analysis": {},
  "change_request": "新增按地区筛选",
  "lineage": {
    "unmatched_widget_names": []
  }
}
```

成功响应：

```json
{
  "change_request": "新增按地区筛选",
  "change_types": ["筛选/控件变更"],
  "summary": "该变更主要属于筛选/控件变更，当前定位到数据集1项、控件1项、字段2项、单元格2项。",
  "confidence": "中",
  "affected": {
    "datasets": [{ "name": "ds_sales", "reason": "变更可能影响取数、字段口径或参数过滤" }],
    "widgets": [{ "name": "region", "reason": "需求文本命中控件或控件字段" }],
    "fields": [],
    "cells": [],
    "formulas": [],
    "sql": [],
    "writeback": []
  },
  "suggested_steps": [],
  "evidence": [],
  "review_points": []
}
```

约束：

- `change_request` 为空或全空格时返回 `400`。
- 该接口不调用 LLM，基于 `parsed`、`analysis`、`lineage` 做确定性定位。
- `analysis` 可为 `null`，内部数组字段也可能为 `null` 或不规整结构；接口应降级处理，不应返回 500。
- 输出是修改建议和复核清单，不代表系统已经自动修改 CPT 或 FineReport 设计器。

### `GET /api/llm/config`

成功响应：

```json
{
  "configured": true,
  "provider": "siliconflow",
  "base_url": "https://api.siliconflow.cn/v1",
  "model": "Qwen/Qwen2.5-72B-Instruct",
  "api_key_hint": "***1234"
}
```

约束：

- 不返回完整 API Key。
- `api_key_hint` 最多只暴露尾部掩码信息。

### `POST /api/llm/test`

请求：

```json
{
  "prompt": "请用一句话回复 FR-Agent LLM 配置已可用。"
}
```

成功响应：

```json
{
  "ok": true,
  "model": "Qwen/Qwen2.5-72B-Instruct",
  "message": "FR-Agent LLM 配置已可用。"
}
```

错误：

- 未配置 `SILICONFLOW_API_KEY` 时返回 `400`。
- 上游模型调用失败时返回 `502`。

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

## P1.5 状态

- 已补最小请求/响应示例。
- 已明确 SSE 最小事件格式。
- 已补评分、公式校验、LLM 配置检测和变更定位接口。
- TODO(CONFIRM): 是否将 FastAPI OpenAPI schema 作为 P1 平台化前置 contract。
