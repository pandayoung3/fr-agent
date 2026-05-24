"""
交接文档生成器 v4
将解析结果 + LLM 分析合并为标准化 Markdown 交接文档

v4 新增区块：
- 数据血缘流向图（Mermaid，控件→参数→SQL数据集→展示字段）
- 指标字典（LLM 推断，含指标名/类型/单位/公式/业务含义）
"""
from datetime import datetime
from agent.lineage_builder import build_lineage


def generate_handover_doc(parsed: dict, analysis: dict, author: str = "") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    fname = parsed.get("file_name", "未知文件")
    report_type_zh = "填报报表" if parsed.get("report_type") == "writeback" else "查询报表"

    lines = []

    # ── 标题 ──────────────────────────────────────────────────────────────────
    lines += [
        f"# 报表交接文档：{fname}",
        "",
        f"> 生成时间：{now}　|　FR 版本：{parsed.get('fr_version', '?')}　|　"
        f"报表类型：{report_type_zh}　|　文件大小：{parsed.get('file_size_kb', '?')} KB",
        "",
        "> ⚠️ 本文档由 AI 自动推断生成，请交接双方核实确认后使用。",
        "",
        "---",
        "",
    ]

    # ── 一、报表概述 ───────────────────────────────────────────────────────────
    lines += [
        "## 一、报表概述",
        "",
        "**业务用途**",
        "",
        analysis.get("purpose", "（AI 未能推断）"),
        "",
    ]
    if analysis.get("layout_description"):
        lines += ["**布局结构**", "", analysis["layout_description"], ""]

    # ── 二、基本信息 ──────────────────────────────────────────────────────────
    lines += [
        "## 二、基本信息",
        "",
        "| 属性 | 值 |",
        "|------|---|",
        f"| 文件名 | `{fname}` |",
        f"| FineReport 版本 | {parsed.get('fr_version', '?')} |",
        f"| 报表类型 | {report_type_zh} |",
        f"| Sheet 数量 | {parsed.get('sheet_count', '?')} |",
        f"| 文件大小 | {parsed.get('file_size_kb', '?')} KB |",
    ]
    if author:
        lines.append(f"| 交接人 | {author} |")
    lines.append("")

    # ── 三、数据来源与字段关系 ────────────────────────────────────────────────
    lines += ["## 三、数据来源与字段关系", ""]

    # 数据血缘流向图（确定性生成，不依赖 LLM）
    lineage = build_lineage(parsed)
    lines += [
        "### 数据血缘流向图",
        "",
        "> 蓝色 = 参数控件　绿色 = SQL 数据集　橙色 = 展示字段　灰色 = 控件选项数据集",
        "",
        lineage["mermaid"],
        "",
    ]
    unmatched = lineage.get("unmatched_widget_names", [])
    if unmatched:
        unmatched_str = "、".join(f"`{n}`" for n in unmatched[:10])
        if len(unmatched) > 10:
            unmatched_str += f" 等共 {len(unmatched)} 个"
        lines += [
            f"> ⚠️ **未找到 SQL 参数连接的控件**（{len(unmatched)} 个）：{unmatched_str}",
            "> 这些控件可能通过单元格过滤条件（cell_filter）或前端 JS 实现筛选，需人工核实。",
            "",
        ]

    db_conns = parsed.get("db_connections", [])
    if db_conns:
        lines += [
            "### 3.1 数据库连接",
            "",
            "| 连接名 | 说明 |",
            "|--------|------|",
        ]
        for c in db_conns:
            lines.append(f"| `{c}` | （请补充数据库类型和用途） |")
        lines.append("")

    datasets = parsed.get("datasets", [])
    if datasets:
        lines += ["### 3.2 数据集清单", ""]
        for ds in datasets:
            type_zh = "实时DB查询" if ds.get("type") == "DBTableData" else "内嵌静态数据"
            conn = ds.get("db_connection") or "—"
            cols = ds.get("columns", [])
            lines += [
                f"#### {ds.get('name', '未命名')}",
                "",
                "| 属性 | 值 |",
                "|------|---|",
                f"| 类型 | {type_zh} |",
                f"| 数据库连接 | `{conn}` |",
                f"| 字段数量 | {len(cols)} |",
                "",
            ]
            if cols:
                lines += ["**字段列表**", "", "| 字段名 | 业务含义 |", "|--------|---------|"]
                for col in cols:
                    lines.append(f"| `{col}` | — |")
                lines.append("")
            if ds.get("sql"):
                lines += ["**SQL 语句**", "", "```sql", ds["sql"], "```", ""]
                if ds.get("sql_params"):
                    params_str = "、".join(f"`{p}`" for p in ds["sql_params"])
                    lines += [f"**动态参数**：{params_str}（由参数控件传入）", ""]

    if analysis.get("dataset_relationships"):
        lines += [
            "### 3.3 数据集关系与数据流向（AI 推断）",
            "",
            analysis["dataset_relationships"],
            "",
        ]

    shared_keys = parsed.get("dataset_shared_keys", [])
    if shared_keys:
        lines += [
            "### 3.4 跨数据集共享字段（推断 JOIN Key）",
            "",
            "| 字段名 | 共享于数据集 |",
            "|--------|------------|",
        ]
        for sk in shared_keys:
            ds_names = "、".join(sk.get("shared_by", []))
            lines.append(f"| `{sk.get('field', '')}` | {ds_names} |")
        lines.append("")

    if analysis.get("field_semantics"):
        lines += ["### 3.5 关键字段业务含义（AI 推断）", "", analysis["field_semantics"], ""]

    # 3.6 指标字典
    indicator_dict = analysis.get("indicator_dict", [])
    if indicator_dict:
        lines += [
            "### 3.6 指标字典（AI 推断）",
            "",
            "| 指标名 | 来源字段 | 数据集 | 类型 | 单位 | 公式 | 业务含义 |",
            "|--------|---------|-------|------|------|------|---------|",
        ]
        for ind in indicator_dict:
            formula_val = f"`{ind.get('formula')}`" if ind.get("formula") else "—"
            dataset_val = ind.get("dataset") or "—"
            unit_val = ind.get("unit") or "—"
            lines.append(
                f"| {ind.get('indicator_name', '')} "
                f"| `{ind.get('source_field', '')}` "
                f"| {dataset_val} "
                f"| {ind.get('type', '')} "
                f"| {unit_val} "
                f"| {formula_val} "
                f"| {ind.get('description', '')} |"
            )
        lines.append("")

    # ── 四、控件交互链路 ──────────────────────────────────────────────────────
    chains = analysis.get("interaction_chains", [])
    lines += [
        "## 四、控件 → 参数 → 数据 → 展示：交互链路",
        "",
        "本节描述每个参数控件如何驱动数据查询并影响展示内容。",
        "",
    ]
    if chains:
        for i, chain in enumerate(chains, 1):
            w_name = chain.get("widget_name", f"链路{i}")
            w_type = chain.get("widget_type", "")
            lines += [f"### 链路 {i}：{w_name}" + (f"（{w_type}）" if w_type else ""), ""]
            if chain.get("param_role"):
                lines += [f"**控件作用**：{chain['param_role']}", ""]
            if chain.get("sql_impact"):
                lines += [f"**SQL 影响**：{chain['sql_impact']}", ""]
            if chain.get("data_displayed"):
                lines += [f"**数据展示**：{chain['data_displayed']}", ""]
            if chain.get("why_this_design"):
                lines += [f"**设计原因**：{chain['why_this_design']}", ""]
    else:
        lines += ["（AI 未能推断交互链路，请人工补充）", ""]

    widgets = parsed.get("widgets", [])
    if widgets:
        lines += [
            "### 参数控件汇总",
            "",
            "| 控件名 | 类型 | 数据来源 | key 字段 | 显示字段 | 固定选项 |",
            "|--------|------|---------|---------|---------|---------|",
        ]
        for w in widgets:
            opts = " / ".join(f"{o['key']}={o['value']}" for o in w.get("custom_options", []))
            lines.append(
                f"| `{w.get('name', '')}` | {w.get('widget_type', '')} "
                f"| {w.get('bound_dataset') or '直接输入'} "
                f"| {w.get('key_column') or '—'} "
                f"| {w.get('display_column') or '—'} "
                f"| {opts or '—'} |"
            )
        lines.append("")

    # ── 五、单元格展示与字段对照 ─────────────────────────────────────────────
    lines += ["## 五、单元格展示与字段对照", ""]

    # 5.1 表单字段对照（标签-数据配对）
    label_pairs = parsed.get("label_data_pairs", [])
    if label_pairs:
        lines += [
            "### 5.1 表单字段对照（标签 → 数据绑定）",
            "",
            "| 标签文字 | 标签位置 | 数据位置 | 数据集 | 字段 | 控件类型 |",
            "|---------|---------|---------|------|------|---------|",
        ]
        for p in label_pairs:
            lines.append(
                f"| {p.get('label_text', '')} | {p.get('label_pos', '')} "
                f"| {p.get('data_pos', '')} | {p.get('dataset', '—')} "
                f"| `{p.get('column', '—')}` | {p.get('widget_type') or '—'} |"
            )
        lines.append("")

    # 5.2 数据绑定单元格明细（含格式、数据模式、父子格）
    bound_cells = [c for c in parsed.get("cell_bindings", []) if c.get("dataset")]
    if bound_cells:
        lines += [
            "### 5.2 数据绑定单元格明细",
            "",
            "| 位置 | 绑定数据集 | 绑定字段 | 格式类型 | 数据模式 | 左父格 | 过滤条件 | 控件 |",
            "|------|-----------|---------|---------|---------|------|---------|------|",
        ]
        for c in bound_cells:
            expand_arrow = {"row": "↓", "col": "→"}.get(c.get("expand_dir", ""), "")
            lines.append(
                f"| `{c.get('pos', '')}` "
                f"| {c.get('dataset', '')} "
                f"| `{c.get('column', '')}` "
                f"| {c.get('format_type') or '常规'} "
                f"| {c.get('data_mode') or '—'} {expand_arrow} "
                f"| {c.get('parent_left') or '—'} "
                f"| {c.get('cell_filter') or '—'} "
                f"| {c.get('widget_type') or '—'} |"
            )
        lines.append("")

    # 5.3 公式单元格（含 LLM 解释）
    formula_cells = parsed.get("formula_cells", [])
    if formula_cells:
        # 构建 LLM 解释的快速查找表
        llm_explanations = {
            e.get("pos"): e.get("meaning", "")
            for e in analysis.get("formula_explanations", [])
            if e.get("pos")
        }
        lines += [
            "### 5.3 公式单元格",
            "",
            "| 位置 | 公式 | 含义（AI 推断）| JS 联动目标 |",
            "|------|------|-------------|-----------|",
        ]
        for f in formula_cells:
            pos = f.get("pos", "")
            formula = f.get("formula", "")
            meaning = llm_explanations.get(pos, "—")
            js_targets = "、".join(f.get("js_events") or []) or "—"
            # 公式文字截断避免表格撑开
            formula_short = formula[:60] + "..." if len(formula) > 60 else formula
            lines.append(f"| `{pos}` | `{formula_short}` | {meaning} | {js_targets} |")
        lines.append("")

    # ── 六、从零复现开发步骤 ──────────────────────────────────────────────────
    steps = analysis.get("development_steps", [])
    lines += [
        "## 六、从零复现该报表的开发步骤（AI 推断）",
        "",
        "> 以下步骤由 AI 根据报表结构推断，供新开发人员参考。",
        "",
    ]
    if steps:
        for step in steps:
            lines.append(f"- {step}")
        lines.append("")
    else:
        lines += ["（AI 未能推断，请人工补充）", ""]

    # ── 七、条件高亮规则（业务规则可视化）────────────────────────────────────
    hl_rules = parsed.get("highlight_rules_summary", [])
    display_rules_text = analysis.get("display_rules", "")
    if hl_rules or display_rules_text:
        lines += ["## 七、条件高亮规则（业务规则）", ""]
        if display_rules_text and display_rules_text != "无条件高亮规则":
            lines += [f"> {display_rules_text}", ""]
        if hl_rules:
            lines += [
                "| 规则名称 | 触发条件 | 效果 | 颜色 | 影响字段 |",
                "|---------|---------|------|------|---------|",
            ]
            for rule in hl_rules:
                affected = "、".join(rule.get("affected_columns", [])) or "—"
                color = rule.get("color", "—")
                color_cell = f"`{color}`" if color != "—" else "—"
                lines.append(
                    f"| {rule.get('name', '')} "
                    f"| `{rule.get('condition', '')}` "
                    f"| {rule.get('action', '')} "
                    f"| {color_cell} "
                    f"| {affected} |"
                )
            lines.append("")

    # ── 八、填报配置（仅填报报表）────────────────────────────────────────────
    wb_cfg = parsed.get("writeback_config")
    if wb_cfg:
        lines += [
            "## 八、填报提交配置",
            "",
            f"| 属性 | 值 |",
            f"|------|---|",
            f"| 数据库连接 | `{wb_cfg.get('db_connection') or '—'}` |",
            f"| 目标表 | `{wb_cfg.get('table') or '—'}` |",
            f"| 主键字段 | {', '.join(f'`{k}`' for k in wb_cfg.get('key_columns', []))} |",
            "",
        ]
        if wb_cfg.get("column_mappings"):
            lines += [
                "**字段映射关系**",
                "",
                "| 数据库字段 | 来源参数 | 是否主键 |",
                "|-----------|---------|---------|",
            ]
            for m in wb_cfg["column_mappings"]:
                is_key = "✓" if m.get("is_key") else ""
                param = m.get("param") or "（来自单元格）"
                lines.append(f"| `{m.get('db_column', '')}` | `{param}` | {is_key} |")
            lines.append("")

    # ── 九、注意事项与风险点 ──────────────────────────────────────────────────
    risks = analysis.get("notes_or_risks", [])
    if risks:
        lines += [
            "## 九、注意事项与风险点",
            "",
            "> 以下风险点由 AI 识别，请人工复核。",
            "",
        ]
        for i, r in enumerate(risks, 1):
            lines.append(f"{i}. {r}")
        lines.append("")

    # ── 十、交接确认 ──────────────────────────────────────────────────────────
    lines += [
        "## 十、交接确认",
        "",
        "| 项目 | 交接方 | 接收方 |",
        "|------|--------|--------|",
        "| 确认人 | | |",
        "| 确认时间 | | |",
        "| 补充说明 | | |",
        "",
        "---",
        "",
        f"*本文档由 FR 交接 Agent 自动生成 v4 | 模型：DeepSeek-V4-Flash | {now}*",
    ]

    return "\n".join(lines)
