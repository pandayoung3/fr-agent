# FR 交接 Agent

> 上传 FineReport `.cpt` 文件，自动解析报表结构 + 接入真实数据库 + AI 语义推断，60 秒生成可交付的 HTML / Markdown 交接文档。

---

## 目录

- [背景与动机](#背景与动机)
- [核心功能](#核心功能)
- [技术架构](#技术架构)
- [模块说明](#模块说明)
- [数据流](#数据流)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [交接文档结构](#交接文档结构)
- [开发历程](#开发历程)

---

## 背景与动机

FineReport 报表在团队交接时，接手方通常需要逐行阅读 `.cpt` 文件的 XML 结构，人工还原业务逻辑、数据流向和交互链路，耗时数小时甚至数天。

FR 交接 Agent 解决这个问题：

| 之前 | 之后 |
|------|------|
| 手动读 XML，猜字段含义 | AI 自动推断业务语义 |
| 不知道控件如何驱动 SQL | 交互链路图自动生成 |
| 字段含义靠经验猜测 | 连接真实数据库获取字段类型和注释 |
| 交接文档靠手写 | 结构化 HTML / Markdown 一键导出 |

---

## 核心功能

- **CPT 深度解析**：解析 `.cpt` 文件（ZIP + XML），提取数据集 SQL、参数控件绑定、单元格公式、条件高亮规则、填报提交配置、父子格关系
- **真实数据库接入**：自动读取 FineReport 连接配置（host / port / 库名 / 用户名），查询 `information_schema` 补全字段结构，不读取真实业务数据
- **数据血缘流向图**：确定性算法生成「控件 → 参数 → 数据集 → 展示字段」完整链路，输出 Mermaid 和 Graphviz DOT 两种格式
- **LLM 语义分析**：调用 DeepSeek / 任意 OpenAI 兼容模型，推断报表业务用途、交互链路、公式含义、指标字典、从零复现步骤、风险点
- **Markdown 交接文档**：10 章节结构化文档，含血缘图、指标字典、开发步骤、填报配置、交接确认表
- **HTML 交接文档**：自包含单文件 HTML，黏性目录、折叠章节、Mermaid 渲染、`@media print` 支持打印导出 PDF
- **报表问答**：基于解析结果和 LLM 分析，支持自然语言追问

---

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (ui/app.py)               │
│  文件上传  │  解析结构展示  │  DB接入  │  LLM分析  │  导出  │
└──────┬─────────────┬──────────────┬──────────────┬───────┘
       │             │              │              │
       ▼             ▼              ▼              ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│ cpt_parser  │ │ lineage  │ │    db    │ │ llm_analyzer │
│   (解析层)   │ │ _builder │ │_connector│ │   (分析层)    │
│             │ │ (血缘图) │ │ (DB接入) │ │              │
└──────┬──────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘
       │             │            │               │
       └─────────────┴────────────┘               │
                     │                            │
                     ▼                            ▼
              parsed: dict              analysis: dict
                     │                            │
                     └──────────┬─────────────────┘
                                ▼
                    ┌─────────────────────┐
                    │   doc_generator     │  →  Markdown
                    │   html_generator    │  →  HTML
                    └─────────────────────┘
```

### 技术栈

| 层次 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **前端** | Streamlit | 1.50.0 | Web UI，文件上传，结果展示 |
| **LLM** | OpenAI SDK | 2.37.0 | 统一调用接口，兼容 SiliconFlow / DeepSeek / OpenAI |
| **HTTP** | httpx | 0.28.1 | 支持代理的 HTTP 客户端（LLM API 访问） |
| **数据库** | PyMySQL | 1.2.0 | 连接 MySQL，查询 information_schema |
| **数据处理** | pandas | 2.3.3 | UI 中指标字典表格渲染 |
| **图形化** | Mermaid.js (CDN) | 10.x | HTML 中血缘流向图渲染 |
| **图形化** | Graphviz (DOT) | — | Streamlit 内嵌血缘图 |
| **解析** | Python 标准库 | — | zipfile（CPT 解压）、xml.etree（XML 解析）、re（SQL 参数提取） |
| **运行时** | Python | 3.9.6 | 主语言 |

### LLM 模型

默认使用 `deepseek-ai/DeepSeek-V4-Flash`（通过 SiliconFlow 接口）。

由于使用标准 OpenAI SDK 格式，可通过修改 `.env` 切换至任意兼容端点：
- 本地 Ollama（`http://localhost:11434/v1`）
- Azure OpenAI
- Anthropic Claude（通过代理层）
- 其他私有部署模型

---

## 模块说明

### `parser/cpt_parser.py`（719 行）

CPT 文件解析核心，FineReport 11.x 兼容。

**输入**：`.cpt` 文件路径

**主要数据类**：

```python
Dataset        # 数据集：name / type / sql / sql_params / db_connection / columns
WidgetBinding  # 参数控件：name / widget_type / bound_dataset / key_column / display_column
CellBinding    # 单元格：pos / label / formula / dataset / column / data_mode /
               #         format_type / parent_left / parent_up / cell_filter / js_events
LabelDataPair  # 标签-数据配对（表单字段名还原）
WritebackConfig# 填报配置：db_connection / table / key_columns / column_mappings
ReportSummary  # 汇总：以上所有 + fr_version / sheet_count / highlight_rules_summary
```

**主要函数**：

| 函数 | 作用 |
|------|------|
| `parse_cpt(path)` | 主入口，返回 `ReportSummary` |
| `summarize_to_dict(summary)` | 转为纯 dict，供 LLM 和 UI 使用 |
| `_parse_datasets()` | 提取数据集（SQL / 字段 / 连接名）|
| `_parse_widgets()` | 提取参数控件及其数据源绑定 |
| `_parse_cells()` | 提取单元格绑定、公式、格式、过滤条件、JS事件 |
| `_parse_writeback_config()` | 提取填报提交配置 |
| `_extract_highlight_rules()` | 提取条件高亮规则 |
| `_extract_label_data_pairs()` | 匹配标签单元格与数据单元格 |
| `_find_shared_keys()` | 推断多数据集间的 JOIN Key |

---

### `agent/llm_analyzer.py`（334 行）

LLM 语义分析层，通过 OpenAI SDK 调用 DeepSeek。

**主要函数**：

| 函数 | 作用 |
|------|------|
| `analyze_report(parsed_dict)` | 主分析入口，返回结构化 JSON |
| `answer_question(parsed, analysis, question)` | 基于上下文回答追问 |
| `_slim_for_llm(d)` | 精简 parsed dict，控制 token 用量（最多15个数据集、45个单元格绑定、20个公式）|
| `_normalize_keys(result)` | 模型输出别名 key 映射为标准 key（兼容 DeepSeek 不严格遵循 schema）|
| `_repair_truncated_json(raw)` | 修复因 token 截断导致的不完整 JSON |

**LLM 输出 schema（10个标准字段）**：

```
purpose              报表一句话业务用途
interaction_chains   控件→参数→SQL→数据→展示的完整链路（数组）
dataset_relationships 各数据集主辅关系与 JOIN 逻辑
field_semantics      关键字段业务含义
layout_description   报表布局（表单型/列表型/分组）
formula_explanations  公式含义解释（数组）
display_rules        条件高亮规则业务含义
development_steps    从零复现的开发步骤（数组）
indicator_dict       指标字典，含类型/单位/公式/业务含义（数组，最多20条）
notes_or_risks       风险点与注意事项（字符串数组）
```

**动态 max_tokens**：根据输入大小自动调整（4000 / 5000 / 5500），防止截断。

---

### `agent/lineage_builder.py`（302 行）

纯确定性算法，不调用 LLM，构建数据血缘图。

**核心逻辑**：
1. `datasets[].sql_params` → 找出被 SQL 参数引用的控件名
2. `widgets[].bound_dataset` → 找出控件的选项数据集
3. `cell_bindings[].dataset` → 找出数据集的展示字段

**输出**：

```python
{
  "mermaid": "flowchart LR\n...",          # 写入 Markdown
  "dot": "digraph {\n...",                 # 传给 st.graphviz_chart
  "sql_driving_widget_names": [...],       # 接入 SQL 的控件
  "unmatched_widget_names": [...]          # 未找到 SQL 参数连接的控件
}
```

**节点颜色**：灰 = 控件选项数据集，蓝 = 参数控件，绿 = SQL 数据集，橙 = 展示字段

---

### `agent/db_connector.py`（333 行）

从 FineReport 配置读取连接元数据，连接数据库补全字段结构。

**主要函数**：

| 函数 | 作用 |
|------|------|
| `parse_fr_connections(fr_webinf_dir)` | 读 `config_entity.properties`，提取所有连接的 host/port/db/user/driver（不含加密密码）|
| `extract_table_names(sql)` | 正则提取 SQL 中 FROM / JOIN 后的表名 |
| `fetch_schema(conn_meta, password, tables)` | 连接 DB，查 `information_schema.COLUMNS`，返回字段类型和注释 |
| `enrich_parsed_datasets(parsed, conn_meta_map, passwords)` | 主入口：回填 `columns` + `column_details` 到 parsed 数据集 |

**设计说明**：
- FR 的密码用 RSA 加密存储，无法自动解密，由用户在 UI 中手动输入
- 只查元数据（字段名/类型/注释），不读取任何业务数据
- 支持 MySQL / MariaDB，其他数据库（Oracle / SQL Server / PostgreSQL）预留接口

---

### `agent/doc_generator.py`（378 行）

将 `parsed` + `analysis` 合并为结构化 Markdown 交接文档。

**10 个章节**：

```
一、报表概述          业务用途 + 布局结构
二、基本信息          文件名 / FR版本 / Sheet数 / 文件大小
三、数据来源与字段关系  血缘图 + 数据集清单 + SQL + 指标字典
四、交互链路          控件→参数→数据→展示详情 + 控件汇总表
五、单元格展示        标签-数据配对 + 单元格绑定明细 + 公式列表
六、从零复现步骤       AI 推断的开发步骤
七、条件高亮规则       业务规则可视化
八、填报配置          写入表 / 主键 / 字段映射（仅填报报表）
九、注意事项与风险点   AI 识别的风险
十、交接确认          确认签字表格
```

---

### `agent/html_generator.py`（790 行）

程序化生成自包含 HTML 交接文档（最大输出模块）。

**特性**：
- 全部 CSS 内嵌，无外部样式表依赖
- Mermaid.js 通过 CDN 渲染血缘图（`cdn.jsdelivr.net/npm/mermaid@10`）
- 黏性顶部导航栏（报表元数据 + 打印按钮）
- 左侧悬浮目录，滚动自动高亮当前章节
- 所有章节可折叠展开（纯 JS，无框架依赖）
- 指标字典带度量（橙色）/ 维度（蓝色）色标
- `@media print` CSS，点击"🖨️ 打印"直接导出 PDF

---

### `ui/app.py`（426 行）

Streamlit 前端，整合所有模块。

**页面结构**：

```
顶部：5个指标卡（FR版本 / Sheet数 / 数据集数 / 文件大小 / 报表类型）
├── 左栏（解析结构）
│   ├── 📦 数据集（SQL / 字段 / DB连接）
│   ├── 🎛️ 参数控件
│   ├── 🔗 单元格-数据集绑定
│   ├── 🔌 数据库连接（输入密码 → 获取真实字段）
│   └── 🗺️ 数据血缘流向图（Graphviz）
└── 右栏（业务分析）
    ├── 🤖 生成 LLM 分析（按钮）
    ├── 报表用途 / 布局 / 数据集关系
    ├── 交互链路（折叠卡片）
    ├── 📋 指标字典（DataFrame 表格）
    ├── ⚠️ 注意事项
    ├── 导出区
    │   ├── 👁️ 预览 Markdown / ⬇️ 下载 Markdown
    │   └── 🌐 生成 HTML / ⬇️ 下载 HTML（iframe 内嵌预览）
    └── 💬 报表问答（chat input）
```

**关键工程细节**：
- 用 `uploaded_filename` 追踪上传文件名，避免 `st.rerun()` 时误清空 analysis
- `.env` 文件每次启动强制读取（`os.environ[k] = v`，非 `setdefault`）
- LLM 分析错误存入 `{"_parse_error": str(e)}`，不中断页面渲染

---

## 数据流

```
.cpt 文件（ZIP + XML）
    │
    ▼ parse_cpt() + summarize_to_dict()
    │
parsed: dict {
  file_name, fr_version, report_type, sheet_count,
  db_connections: [str],
  datasets: [{name, type, sql, sql_params, db_connection, columns}],
  widgets: [{name, widget_type, bound_dataset, key_column}],
  cell_bindings: [{pos, dataset, column, data_mode, formula, parent_left, ...}],
  formula_cells, label_data_pairs, dataset_shared_keys,
  highlight_rules_summary, writeback_config
}
    │
    ├─► build_lineage(parsed) → {mermaid, dot, sql_driving_widget_names, ...}
    │
    ├─► enrich_parsed_datasets(parsed, fr_conns, passwords)
    │       └─► 回填 datasets[].columns + datasets[].column_details
    │
    └─► analyze_report(parsed) → analysis: dict {
            purpose, interaction_chains, dataset_relationships,
            field_semantics, layout_description, formula_explanations,
            display_rules, development_steps, indicator_dict, notes_or_risks
        }
            │
            ├─► generate_handover_doc(parsed, analysis) → Markdown str
            └─► generate_handover_html(parsed, analysis) → HTML str
```

---

## 快速开始

### 环境要求

- Python 3.9+
- MySQL 客户端（可选，用于数据库接入功能）
- FineReport 11.x（可选，用于读取连接配置）

### 安装

```bash
git clone https://github.com/pandayoung3/fr-agent.git
cd fr-agent

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 配置

```bash
cp .env.example .env
```

编辑 `.env`：

```env
SILICONFLOW_API_KEY=sk-你的密钥
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=deepseek-ai/DeepSeek-V4-Flash

# 如需通过本地代理访问（可选）
# HTTPS_PROXY=http://127.0.0.1:7890
```

### 启动

```bash
streamlit run ui/app.py
```

浏览器打开 `http://localhost:8501`

### 命令行批量生成（可选）

```bash
python scripts/gen_v4.py
```

---

## 配置说明

| 环境变量 | 必填 | 说明 |
|----------|------|------|
| `SILICONFLOW_API_KEY` | ✅ | LLM API 密钥 |
| `SILICONFLOW_BASE_URL` | ✅ | API Endpoint（支持任意 OpenAI 兼容地址）|
| `LLM_MODEL` | ✅ | 模型名称 |
| `HTTPS_PROXY` | — | HTTP 代理（国内访问海外 API 时使用）|

### 切换其他 LLM

只需修改 `.env` 中的三个变量，代码无需改动：

```env
# 本地 Ollama
SILICONFLOW_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5:14b
SILICONFLOW_API_KEY=ollama

# OpenAI
SILICONFLOW_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o
SILICONFLOW_API_KEY=sk-...
```

---

## 交接文档结构

生成的交接文档包含 10 个标准章节：

```
一、报表概述          业务用途 + 布局描述
二、基本信息          版本 / 类型 / Sheet数 / 大小
三、数据来源与字段关系  血缘图 + 数据集清单 + SQL + 指标字典
四、交互链路          控件→参数→SQL→展示全链路
五、单元格展示        字段对照 + 绑定明细 + 公式解释
六、从零复现步骤       AI 推断的开发步骤
七、条件高亮规则       业务规则（颜色 / 触发条件）
八、填报配置          写入表 / 主键 / 字段映射
九、注意事项与风险点   AI 识别的潜在问题
十、交接确认          签字确认表格
```

---

## 开发历程

本项目从 2026-05-21 开始，历经约 4 天完成 MVP 到真实数据接入的完整验证。

| 日期 | 阶段 | 关键成果 |
|------|------|---------|
| 05-21 | Phase 0 | CPT 文件底层结构验证，确认 ZIP+XML 解析路径可行 |
| 05-21 | Phase 1 | 解析器 v1，支持数据集、控件、单元格基础提取 |
| 05-22 | Phase 2 | LLM 接入 + Markdown 文档生成，完整 v1 流程跑通 |
| 05-22 | Phase 3 | 解析器 v3，新增公式、父子格、条件高亮、填报配置 |
| 05-22 | Phase 4 | 血缘图（lineage_builder）+ 指标字典（indicator_dict）|
| 05-22 | Phase 5 | HTML 交接文档生成器（html_generator）|
| 05-23 | Phase 6 | Streamlit UI 完整实现，修复关键 Bug（rerun 清空 analysis）|
| 05-23 | Phase 7 | **真实数据库接入**（db_connector），习题8.cpt + MySQL 全链路验证 |

**核心 Bug 记录**：

- `st.file_uploader` 每次 `st.rerun()` 都触发，导致 analysis 被清空 → 用 `uploaded_filename` 追踪解决
- DeepSeek 不严格遵循 schema key 名 → `_normalize_keys()` 别名映射兜底
- SiliconFlow API 被 VPN 拦截 → `HTTPS_PROXY` 走本地代理
- FR 密码 RSA 加密无法自动解密 → 设计为用户手动输入，符合安全实践

---

## 项目结构

```
fr-agent/
├── parser/
│   └── cpt_parser.py        # CPT 解析器 v3（719 行）
├── agent/
│   ├── llm_analyzer.py      # LLM 语义分析（334 行）
│   ├── doc_generator.py     # Markdown 文档生成（378 行）
│   ├── html_generator.py    # HTML 文档生成（790 行）
│   ├── lineage_builder.py   # 数据血缘图（302 行）
│   └── db_connector.py      # 数据库字段接入（333 行）
├── ui/
│   └── app.py               # Streamlit 前端（426 行）
├── scripts/
│   └── gen_v4.py            # 命令行批量生成脚本
├── devlog/                  # 各阶段开发日志（7篇）
├── .env.example             # 环境变量模板
├── .gitignore
└── README.md
```

**代码总量**：3,355 行（不含 .venv 和测试数据）

---

## License

MIT
