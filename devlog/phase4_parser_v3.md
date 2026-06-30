# Phase 4 报告：解析器 v3 深度增强

> 日期：2026-05-22 | 状态：✅ 完成

---

## 一、本阶段背景

Phase 3 生成的文档已包含完整交互链路和开发步骤，但对 CPT 文件的解析深度仍不足：
- **单元格格式类型**未提取（常规/数字/百分比/日期），新人无法判断字段展示格式
- **数据展示模式**未识别（分组展开 vs 全量列表 vs 汇总），无法复现列表报表的行扩展逻辑
- **父子格关系**未解析，子格过滤逻辑完全缺失，新人不知道数据为何按批次/维度分组
- **公式内容**解析 Bug：Formula 类型单元格内容存于 `<Attributes>` 而非 `o.text`，v2 解析器静默丢弃所有公式
- **条件高亮规则**未提取，业务状态可视化规则完全不可见
- **JS 联动事件**未提取，单元格推参控件的交互不可见
- **填报提交配置**未提取，客服报表（填报报表）的写入目标表和字段映射无法展示

---

## 二、改动清单

### 2.1 解析器 v3（`parser/cpt_parser.py`）

#### 新增数据结构

**`WritebackConfig` dataclass**

| 字段 | 含义 |
|------|------|
| `db_connection` | 填报目标数据库连接名 |
| `table_schema` | Schema 名（如 public）|
| `table_name` | 目标表名 |
| `key_columns` | 主键字段列表 |
| `column_mappings` | 列表：{db_column, param, is_key} |

**`CellBinding` 新增字段**

| 字段 | 来源 XML | 含义 |
|------|---------|------|
| `formula` | `<O class="Formula"><Attributes>` | 单元格公式内容 |
| `cell_format` | StyleList `s` 属性 → CoreDecimalFormat / FineDateFormat | 原始格式 pattern |
| `format_type` | 由 pattern 分类 | 常规/数字/百分比/日期/整数 |
| `data_mode` | `RG divideMode` + class | 分组展开/全量列表/汇总 |
| `cell_filter` | `<Condition>` 节点 | 单元格级过滤条件（中文描述）|
| `parent_left` | `<Expand left="B4">` | 左父格坐标 |
| `parent_up` | `<Expand up="A3">` | 上父格坐标 |
| `js_events` | `<JavaScript><Content>` | JS 联动目标控件列表 |
| `highlight_rules` | `<HighlightList>` | 单元格条件高亮规则列表 |

#### 新增辅助函数

```
_parse_style_map(root)         → 从 StyleList 构建 {s_index: {pattern, type}}
_classify_format(cls, pattern) → "percent"/"date"/"integer"/"decimal"/"general"
_parse_data_mode(o)            → "list_group"/"list_all"/"aggregate"
_parse_cell_filter(o)          → 中文描述的过滤条件字符串
_extract_js_events(c)          → getWidgetByName("xxx") 提取控件名列表
_extract_highlight_rules(c)    → [{name, condition, action, color_hex}]
_deduplicate_highlight_rules() → 按规则名合并，收集 affected_columns
_parse_writeback_config(root)  → WritebackConfig（仅填报报表）
```

#### 关键 Bug 修复

**公式内容读取**（v2 静默丢弃）

```python
# v2（错误）
cb.formula = o.text  # Formula 节点 text 为 None

# v3（正确）
elif "Formula" in o_class:
    attrs = o.find("Attributes")
    if attrs is not None and attrs.text and attrs.text.strip():
        cb.formula = attrs.text.strip()
```

**FineColor 整数转十六进制**

```python
# FineColor 是有符号 32-bit ARGB，取低 24 位 RGB
color_hex = f"#{color_int & 0xFFFFFF:06X}"
# 示例：-2297857 → #DCB5FF
```

#### `summarize_to_dict()` 新增输出字段

| 字段 | 内容 |
|------|------|
| `formula_cells` | 仅含公式的单元格列表（pos + formula）|
| `highlight_rules_summary` | 去重后的条件高亮规则（含 affected_columns）|
| `writeback_config` | 填报提交配置（None 表示查询报表）|

### 2.2 LLM 分析器 v3（`agent/llm_analyzer.py`）

**System Prompt 增强**：新增对 formula_cells_sample、highlight_rules_summary、writeback_config 字段的说明；新增 `data_mode`、`parent_left/up`、`cell_filter` 字段语义解释。

**新增输出 JSON 字段**：

| 字段 | 内容 |
|------|------|
| `formula_explanations` | `[{pos, formula, meaning}]` — 结合业务上下文解释公式含义 |
| `display_rules` | 条件高亮规则业务含义（触发条件代表的业务状态、颜色含义）|

**动态 max_tokens 策略**（修复客服报表输出截断）：

| 输入字符数 | max_tokens |
|-----------|-----------|
| > 12,000 | 5,000（同时触发二次压缩）|
| > 8,000 | 4,500 |
| ≤ 8,000 | 3,500 |

**新增 `_slim_aggressive()`**：超大报表二次压缩 — 单元格→30条，公式→12条，数据集列→15列。

### 2.3 交接文档生成器 v3（`agent/doc_generator.py`）

**章节结构调整（8章 → 10章）**：

| 章节 | 新增/变更内容 |
|------|-------------|
| 五、单元格展示 | 5.2 表格新增：格式类型/数据模式/左父格/过滤条件列 |
| 五、单元格展示 | **新增 5.3 公式单元格**：含 LLM 含义解释 |
| 七、条件高亮规则 | **新增章节**：规则表格（触发条件/颜色/影响字段）+ AI 业务解释 |
| 八、填报配置 | **新增章节**：目标表/主键/字段映射表（仅填报报表显示）|
| 九、风险点 | 原七章 → 九章 |
| 十、交接确认 | 原八章 → 十章 |

---

## 三、生成文档效果对比

| 报表 | v2 文档 | v3 文档 |
|------|---------|---------|
| 习题8 | 基本字段列表 | 6个表单配对 + 公式解释 + 格式类型列 |
| 制单报表 | 5条交互链路 | 5条链路 + **父子格关系** + **5级高亮规则 + AI业务解释** |
| 出货汇总 | 1条链路 + 步骤 | 1条链路 + **10个公式解释**（月均/增长率/条件判断）|
| 客服报表 | 11条链路（曾截断）| 11条链路 + **12个公式解释** + **填报配置**（写入表/主键/字段映射）|

---

## 四、卡点记录

| 卡点 | 现象 | 解决 |
|------|------|------|
| 公式全部丢失 | v2 读 `o.text` 为 None → 公式单元格静默跳过 | 读 `<Attributes>` 节点的 text |
| 客服报表 finish_reason=length | 固定 max_tokens=3000 不足 | 动态 max_tokens（最高 5000）+ 二次压缩 |
| FineColor 颜色值为负整数 | 直接输出 -2297857 无法理解 | `color_int & 0xFFFFFF` 转 6 位 hex |
| 超链接不存在 | 调查发现 `click` 节点是 hover 背景色，非跳转链接 | 改用 JS 事件作为单元格交互代理 |

---

## 五、v3 测试验证

```bash
cd fr-agent && source .venv/bin/activate
python -c "
from parser.cpt_parser import parse_cpt, summarize_to_dict
d = summarize_to_dict(parse_cpt('sample_cptes/制单报表.cpt'))
print('formula_cells:', len(d.get('formula_cells', [])))
print('highlight_rules:', len(d.get('highlight_rules_summary', [])))
print('writeback:', d.get('writeback_config'))
"
```

输出示例：
- 制单报表：formula_cells=8, highlight_rules=5, writeback=None
- 客服报表：formula_cells=212, highlight_rules=0, writeback=WritebackConfig(table='fr_amz_ad_product_link_follow', key_columns=['sid','date','spu_id'])

---

## 六、当前 Demo 访问方式

```bash
cd fr-agent && source .venv/bin/activate
streamlit run ui/app.py
# http://localhost:8501
```

上传 .cpt → 解析（含公式/高亮/父子格）→ 生成 LLM 分析（含公式解释/高亮业务含义）→ 下载 10 章交接文档

---

## 七、下一步方向

- **批量导入**：支持目录级批量解析 + 一键批量生成交接文档
- **HTML 开发过程展示**：整合所有 devlog，生成完整的开发记录展示页面（最终收尾）

---

*由 FR 交接 Agent 开发日志系统自动记录 | Phase 4*
