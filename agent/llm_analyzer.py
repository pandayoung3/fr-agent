"""
LLM 语义分析模块 v3
调用 DeepSeek（硅基流动）对 CPT 解析结果做业务语义推断

v3 新增输入字段：
- formula_cells：公式单元格（LLM 解释含义）
- highlight_rules_summary：条件高亮规则（LLM 解释业务规则）
- writeback_config：填报提交配置
- cell_bindings 新增：format_type、data_mode、parent_left、cell_filter
"""
import os
import json
import re
from openai import OpenAI
from typing import Optional

def get_client() -> OpenAI:
    """每次调用都从环境变量重新读取配置，避免 .env 更新后需要重启进程。"""
    api_key  = os.environ.get("SILICONFLOW_API_KEY", "")
    base_url = os.environ.get("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    proxy    = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    kwargs: dict = {"api_key": api_key, "base_url": base_url}
    if proxy:
        import httpx
        kwargs["http_client"] = httpx.Client(proxy=proxy)
        print(f"[LLM] 使用代理: {proxy}")
    print(f"[LLM] base_url={base_url} model={os.environ.get('LLM_MODEL','(未设置)')}")
    return OpenAI(**kwargs)


def _get_model() -> str:
    return os.environ.get("LLM_MODEL", "deepseek-ai/DeepSeek-V4-Flash")

SYSTEM_PROMPT = """你是一个 FineReport（帆软报表）专家，目标是帮助新接手报表的开发人员快速理解报表完整逻辑，能从零复现这张报表。

你会收到一个 JSON 格式的报表解析结果，包含以下关键字段：
- datasets：数据集（SQL、字段列表、数据库连接）
- widgets：参数控件（控件名、类型、绑定的数据集和字段）
- cell_bindings_sample：关键单元格（含 dataset/column/data_mode/format_type/parent_left/cell_filter）
- formula_cells_sample：公式单元格（含公式文本，需解释含义）
- label_data_pairs：标签与数据单元格的配对（揭示字段业务名称）
- dataset_shared_keys：多数据集共有字段（推断 JOIN Key）
- highlight_rules_summary：条件高亮规则（含触发条件和颜色）
- writeback_config：填报报表的提交配置（写入哪张表、主键、字段映射）

字段说明：
- data_mode = "分组展开（不重复）" 表示该字段作为分组 key 驱动行扩展；"全量列表" 表示显示所有行
- parent_left / parent_up 是父格坐标，子格数据随父格当前值自动过滤
- cell_filter 是单元格级别的额外过滤条件（独立于 SQL WHERE）

请用中文分析并严格输出以下固定 key 名的 JSON：

{
  "purpose": "一句话描述该报表的业务用途和使用场景",

  "interaction_chains": [
    {
      "widget_name": "控件名称（若无参数则写'无参数'）",
      "widget_type": "控件类型",
      "param_role": "该控件在筛选/驱动数据中的作用",
      "sql_impact": "该控件如何影响 SQL 查询（参数变量、动态条件）",
      "data_displayed": "最终哪些单元格/字段展示了来自该数据集的数据",
      "why_this_design": "为什么这样设计（从业务角度解释）"
    }
  ],

  "dataset_relationships": "解释各数据集关系：哪个是主数据集、哪个是辅助/参数数据集、通过哪些字段关联、parent_left/cell_filter 揭示了什么数据分组逻辑",

  "field_semantics": "解释关键字段的业务含义，结合 label_data_pairs 说明表单字段名称，说明百分比/日期类型字段代表什么",

  "layout_description": "描述报表布局：表单型还是列表型、哪行是表头/数据行/合计行、data_mode=分组展开 的字段如何驱动行扩展",

  "formula_explanations": [
    {
      "pos": "单元格位置",
      "formula": "原始公式",
      "meaning": "这个公式的作用（结合报表上下文解释，说明用到了什么 FR 函数、业务含义是什么）"
    }
  ],

  "display_rules": "解释条件高亮规则的业务含义：触发条件代表什么业务状态，各颜色含义，这套规则的设计目的是什么",

  "development_steps": [
    "步骤1：...",
    "步骤2：...",
    "按实际开发顺序列出，让新人能从零复现这张报表，需包含：建数据集→配参数控件→设计报表布局→配置填报属性（如有）"
  ],

  "indicator_dict": [
    {
      "indicator_name": "指标/字段业务名称（优先从 label_data_pairs 取，否则推断）",
      "source_field": "对应字段名，公式指标填单元格坐标如(2,26)",
      "dataset": "所属数据集名，公式计算型填 null",
      "type": "维度 或 度量",
      "unit": "单位（件/元/% 等），无单位填 null",
      "formula": "公式内容，字段型填 null",
      "description": "业务含义与计算口径（一句话）"
    }
  ],

  "notes_or_risks": ["风险点或注意事项1", "风险点或注意事项2"]
}

重要原则：
1. interaction_chains 讲清楚"控件→参数→SQL→数据→展示"的完整流向
2. formula_explanations 只对有业务意义的公式解释（跳过简单的 =SEQ()，但 =SUM()、计算比率、条件公式都要解释）
3. display_rules 若无高亮规则则写"无条件高亮规则"
4. 有 writeback_config 时 development_steps 须包含填报属性配置步骤
5. 所有内容用中文，notes_or_risks 为字符串数组
6. indicator_dict 只列有业务意义的指标，最多 20 条，优先列度量字段和带格式类型的字段；formula_explanations 中已解释的公式同步汇总到此处作为【公式型度量】"""


def analyze_report(parsed_dict: dict) -> dict:
    """对解析结果做语义分析，返回结构化分析结论"""
    client = get_client()
    slim = _slim_for_llm(parsed_dict)
    prompt_body = json.dumps(slim, ensure_ascii=False, indent=2)

    # 根据输入大小动态调整 max_tokens（避免截断）
    input_chars = len(prompt_body) + len(SYSTEM_PROMPT)
    if input_chars > 12000:
        # 超大报表：进一步压缩，保证输出空间足够
        slim = _slim_aggressive(slim)
        prompt_body = json.dumps(slim, ensure_ascii=False, indent=2)
        max_out = 5500
    elif input_chars > 8000:
        max_out = 5000
    else:
        max_out = 4000

    prompt = "请分析以下 FineReport 报表解析数据，还原其完整交互逻辑和业务含义：\n\n" + prompt_body

    print(f"[LLM] 发送请求 model={_get_model()} max_tokens={max_out} input_chars={input_chars}")
    response = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_out,
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    print(f"[LLM] 收到响应 tokens={response.usage.total_tokens} finish_reason={response.choices[0].finish_reason}")

    raw = response.choices[0].message.content
    tokens = response.usage.total_tokens

    if not raw:
        print("[LLM] content 为空")
        return {"_tokens_used": tokens, "_parse_error": "模型返回内容为空（content=None）"}

    print(f"[LLM] content 长度={len(raw)} 前100字符: {raw[:100]}")
    try:
        result = json.loads(raw)
        print(f"[LLM] JSON 解析成功，顶层 keys={list(result.keys())}")
    except (json.JSONDecodeError, TypeError) as e:
        print(f"[LLM] JSON 解析失败: {e}，尝试修复...")
        result = _repair_truncated_json(raw)

    result["_tokens_used"] = tokens
    return _normalize_keys(result)


def answer_question(parsed_dict: dict, analysis: dict, question: str) -> str:
    """基于解析结果和已有分析，回答用户对报表的具体问题"""
    client = get_client()
    slim = _slim_for_llm(parsed_dict)
    context = (
        f"报表解析数据：\n{json.dumps(slim, ensure_ascii=False, indent=2)}\n\n"
        f"已有分析结论：\n{json.dumps(analysis, ensure_ascii=False, indent=2)}"
    )

    response = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {"role": "system", "content": "你是 FineReport 报表专家，根据报表解析数据和已有分析回答问题，重点说明交互链路、公式含义和业务逻辑。"},
            {"role": "user", "content": f"{context}\n\n问题：{question}"},
        ],
        max_tokens=600,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def _slim_for_llm(d: dict) -> dict:
    """精简解析结果，保留语义关键信息，控制 token 用量"""

    # ── 数据集：优先实时查询，最多15个 ────────────────────────────────────────
    all_ds = d.get("datasets", [])
    db_ds = [ds for ds in all_ds if ds.get("type") == "DBTableData" or ds.get("sql")]
    embed_ds = [ds for ds in all_ds if ds not in db_ds]
    datasets = []
    for ds in (db_ds + embed_ds)[:15]:
        slim_ds = {k: v for k, v in ds.items() if v is not None and v != "" and v != []}
        if len(slim_ds.get("columns", [])) > 20:
            slim_ds["columns"] = slim_ds["columns"][:20] + [f"...共{len(ds['columns'])}列"]
        # column_details：每张表的字段类型+注释，最多保留 3 张表 × 25 列
        if slim_ds.get("column_details"):
            trimmed = {}
            for tbl, cols in list(slim_ds["column_details"].items())[:3]:
                trimmed[tbl] = [
                    {k: v for k, v in c.items() if k in ("column", "type", "comment", "key")}
                    for c in cols[:25]
                ]
            slim_ds["column_details"] = trimmed
        datasets.append(slim_ds)
    if len(all_ds) > 15:
        datasets.append({"_note": f"另有 {len(all_ds) - 15} 个辅助数据集未展示"})

    # ── 参数控件 ───────────────────────────────────────────────────────────────
    widgets = [
        w for w in d.get("widgets", [])
        if w.get("widget_type") not in ("Label", "FreeButton", "FormSubmitButton")
    ]

    # ── 单元格绑定：保留关键字段，最多 45 条 ────────────────────────────────
    cell_keys = {"pos", "dataset", "column", "data_mode", "format_type",
                 "cell_filter", "parent_left", "parent_up", "widget_type", "js_events"}
    cells = [
        {k: v for k, v in c.items() if k in cell_keys and v is not None}
        for c in d.get("cell_bindings", [])
        if c.get("dataset")
    ][:45]

    # ── 公式单元格：有业务意义的，最多 20 条 ────────────────────────────────
    skip_trivial = {"=SEQ()", "=$"}  # 跳过序号、简单参数引用
    formula_cells = [
        {"pos": f["pos"], "formula": f["formula"]}
        for f in d.get("formula_cells", [])
        if f.get("formula") and not any(f["formula"].startswith(p) for p in skip_trivial)
    ][:20]

    # ── 共享字段：只保留高价值的（≥3 个数据集共享）最多 10 条 ──────────────
    shared_keys = sorted(
        d.get("dataset_shared_keys", []),
        key=lambda x: -len(x.get("shared_by", [])),
    )
    significant_keys = [sk for sk in shared_keys if len(sk.get("shared_by", [])) >= 3][:10]
    if not significant_keys:
        significant_keys = shared_keys[:5]

    result = {
        "file_name": d.get("file_name"),
        "report_type": d.get("report_type"),
        "sheet_count": d.get("sheet_count"),
        "db_connections": d.get("db_connections"),
        "datasets": datasets,
        "widgets": widgets,
        "cell_bindings_sample": cells,
        "formula_cells_sample": formula_cells,
        "label_data_pairs": d.get("label_data_pairs", []),
        "dataset_shared_keys": significant_keys,
        "highlight_rules_summary": d.get("highlight_rules_summary", []),
    }

    # 填报配置（仅填报报表有）
    if d.get("writeback_config"):
        result["writeback_config"] = d["writeback_config"]

    return result


def _slim_aggressive(slim: dict) -> dict:
    """对超大报表进行二次压缩，减少 LLM 输入 token"""
    result = dict(slim)
    # 单元格绑定减少到 30 条
    result["cell_bindings_sample"] = slim.get("cell_bindings_sample", [])[:30]
    # 公式单元格减少到 12 条
    result["formula_cells_sample"] = slim.get("formula_cells_sample", [])[:12]
    # 数据集列名压缩到 15 个
    compressed_ds = []
    for ds in slim.get("datasets", []):
        ds2 = dict(ds)
        if len(ds2.get("columns", [])) > 15:
            ds2["columns"] = ds2["columns"][:15] + [f"...共{len(ds['columns'])}列"]
        compressed_ds.append(ds2)
    result["datasets"] = compressed_ds
    # 共享字段减到 6 条
    result["dataset_shared_keys"] = slim.get("dataset_shared_keys", [])[:6]
    return result


def _repair_truncated_json(raw: str) -> dict:
    """尝试修复因 token 截断导致的不完整 JSON"""
    for end in range(len(raw) - 1, 0, -1):
        candidate = raw[:end].rstrip()
        open_braces = candidate.count('{') - candidate.count('}')
        open_brackets = candidate.count('[') - candidate.count(']')
        candidate = re.sub(r',\s*$', '', candidate)
        candidate = re.sub(r'"\w*$', '', candidate)
        candidate = re.sub(r',\s*$', '', candidate)
        suffix = ']' * max(0, open_brackets) + '}' * max(0, open_braces)
        try:
            return json.loads(candidate + suffix)
        except json.JSONDecodeError:
            continue
    return {"raw_response": raw, "_parse_error": "JSON 截断且无法修复"}


# ── Key 归一化：兼容模型未严格遵循 schema 时的别名映射 ─────────────────────────
_KEY_ALIASES: dict[str, list[str]] = {
    "purpose":               ["report_purpose", "business_purpose", "用途", "报表用途"],
    "layout_description":    ["display_content_description", "layout", "布局", "展示内容说明",
                              "report_layout", "layout_structure"],
    "dataset_relationships": ["data_source_analysis", "dataset_relationship", "数据集关系",
                              "data_relationship", "datasource_analysis"],
    "field_semantics":       ["field_semantic", "字段含义", "field_description", "field_meanings"],
    "interaction_chains":    ["parameter_filter_logic", "interaction_chain", "参数链路",
                              "widget_interactions", "filter_logic"],
    "formula_explanations":  ["formula_explanation", "公式说明", "formulas"],
    "display_rules":         ["highlight_rules", "conditional_rules", "条件规则", "display_rule"],
    "development_steps":     ["development_step", "开发步骤", "dev_steps", "steps"],
    "indicator_dict":        ["indicator_dictionary", "indicators", "指标字典", "metric_dict",
                              "indicator_list"],
    "notes_or_risks":        ["notes", "risks", "风险", "注意事项", "risk_notes", "notes_risks"],
}


def _normalize_keys(result: dict) -> dict:
    """将模型返回的别名 key 统一映射为代码期望的标准 key。"""
    for canonical, aliases in _KEY_ALIASES.items():
        if canonical in result:
            continue  # 已有标准 key，跳过
        for alias in aliases:
            if alias in result:
                result[canonical] = result.pop(alias)
                print(f"[LLM] key 归一化: '{alias}' → '{canonical}'")
                break
    # interaction_chains 若为字符串（模型把它当普通文本返回），包一层
    chains = result.get("interaction_chains")
    if isinstance(chains, str):
        result["interaction_chains"] = [{"widget_name": "（AI汇总）", "param_role": chains}]
    return result
