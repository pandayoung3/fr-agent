"""
数据血缘流向图构建器
从 summarize_to_dict() 的解析结果确定性地构建"控件 → 参数 → 数据集 → 展示字段"的血缘图

不调用 LLM，纯算法推导关系：
  1. widget.name ∈ dataset.sql_params  → 控件通过参数驱动 SQL 数据集
  2. widget.bound_dataset == dataset.name → 控件选项来源于某数据集
  3. cell_binding.dataset == dataset.name → 数据集字段展示在某单元格

输出格式：
  - mermaid: Mermaid flowchart LR（写入 Markdown，可直接渲染）
  - dot:     Graphviz DOT（传给 st.graphviz_chart）
"""
import re


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def _node_id(prefix: str, text: str) -> str:
    """将任意字符串转为合法的图节点 ID（保留字母数字下划线，截断到 40 字符）"""
    clean = re.sub(r"[^a-zA-Z0-9_]", "_", str(text))
    return f"{prefix}_{clean[:36]}"


def _trunc(text: str, max_len: int = 22) -> str:
    """截断过长的标签文字"""
    s = str(text)
    return s if len(s) <= max_len else s[:max_len - 1] + "…"


def _mermaid_label(text: str) -> str:
    """Mermaid 节点标签转义：替换双引号"""
    return str(text).replace('"', "'")


def _dot_label(text: str) -> str:
    """Graphviz DOT 标签转义：替换双引号、尖括号"""
    return str(text).replace('"', "'").replace("<", "\\<").replace(">", "\\>")


# ── 核心构建函数 ──────────────────────────────────────────────────────────────

def build_lineage(parsed: dict) -> dict:
    """
    构建数据血缘图。

    参数：
        parsed: summarize_to_dict() 的返回值

    返回：
        {
            "mermaid": str,                    # Mermaid flowchart 代码（含 ``` 包裹）
            "mermaid_raw": str,                # 不含 ``` 的纯 Mermaid 内容
            "dot": str,                        # Graphviz DOT 字符串
            "sql_driving_widget_names": list,  # 成功接入SQL的控件名
            "unmatched_widget_names": list,    # 未找到SQL参数的控件名
        }
    """
    datasets = parsed.get("datasets", [])
    widgets = [
        w for w in parsed.get("widgets", [])
        if w.get("widget_type") not in ("Label", "FreeButton", "FormSubmitButton")
    ]
    cell_bindings = [c for c in parsed.get("cell_bindings", []) if c.get("dataset")]

    # ── 关系映射 ──────────────────────────────────────────────────────────────

    # param_name → [SQL数据集名]（哪些SQL数据集用到了这个参数）
    param_to_sql_ds: dict = {}
    sql_ds_set = set()
    for ds in datasets:
        if ds.get("sql") and ds.get("sql_params"):
            sql_ds_set.add(ds["name"])
            for param in ds["sql_params"]:
                param_to_sql_ds.setdefault(param, []).append(ds["name"])

    # 控件数据集名 → [widget]（提供下拉选项的数据集 → 依赖它的控件）
    ctrl_ds_to_widgets: dict = {}
    for w in widgets:
        if w.get("bound_dataset"):
            ctrl_ds_to_widgets.setdefault(w["bound_dataset"], []).append(w)

    # SQL数据集名 → [cell_binding]
    sql_ds_to_cells: dict = {}
    for c in cell_bindings:
        ds_name = c.get("dataset", "")
        if ds_name in sql_ds_set:
            sql_ds_to_cells.setdefault(ds_name, []).append(c)

    # 分类控件
    sql_driving = [w for w in widgets if w["name"] in param_to_sql_ds]
    unmatched = [w for w in widgets if w["name"] not in param_to_sql_ds]

    # 控件数据集（为控件提供选项，自身不直接展示数据）
    ctrl_ds_names = set(ctrl_ds_to_widgets.keys()) - sql_ds_set

    mermaid_raw = _build_mermaid(
        widgets, datasets, sql_ds_set,
        param_to_sql_ds, ctrl_ds_to_widgets, sql_ds_to_cells, ctrl_ds_names,
    )
    dot = _build_dot(
        widgets, datasets, sql_ds_set,
        param_to_sql_ds, ctrl_ds_to_widgets, sql_ds_to_cells, ctrl_ds_names,
    )

    return {
        "mermaid": f"```mermaid\n{mermaid_raw}\n```",
        "mermaid_raw": mermaid_raw,
        "dot": dot,
        "sql_driving_widget_names": [w["name"] for w in sql_driving],
        "unmatched_widget_names": [w["name"] for w in unmatched],
    }


# ── Mermaid 生成 ──────────────────────────────────────────────────────────────

def _build_mermaid(widgets, datasets, sql_ds_set,
                   param_to_sql_ds, ctrl_ds_to_widgets, sql_ds_to_cells,
                   ctrl_ds_names) -> str:
    lines = [
        "flowchart LR",
        "    classDef ctrlDS  fill:#B0BEC5,color:#000,stroke:#78909C",
        "    classDef widget  fill:#1976D2,color:#fff,stroke:#0D47A1",
        "    classDef sqlDS   fill:#388E3C,color:#fff,stroke:#1B5E20",
        "    classDef cells   fill:#F57C00,color:#fff,stroke:#E65100",
        "",
    ]

    # 1. 控件数据集节点（灰）
    for ds in datasets:
        if ds["name"] not in ctrl_ds_names:
            continue
        nid = _node_id("CDS", ds["name"])
        label = _mermaid_label(_trunc(ds["name"]))
        lines.append(f'    {nid}["{label}\\n(控件数据集)"]:::ctrlDS')

    # 2. 参数控件节点（蓝）
    for w in widgets:
        nid = _node_id("W", w["name"])
        label = f'{_mermaid_label(_trunc(w["name"]))}\\n({w["widget_type"]})'
        lines.append(f'    {nid}["{label}"]:::widget')

    lines.append("")

    # 3. SQL 数据集节点（绿）
    for ds in datasets:
        if ds["name"] not in sql_ds_set:
            continue
        nid = _node_id("DS", ds["name"])
        label = _mermaid_label(_trunc(ds["name"], 24))
        lines.append(f'    {nid}[("数据集\\n{label}")]:::sqlDS')

    lines.append("")

    # 4. 展示字段节点（橙，按数据集分组）
    for ds_name, cells in sql_ds_to_cells.items():
        nid = _node_id("CELLS", ds_name)
        fields = [_mermaid_label(c["column"]) for c in cells[:6] if c.get("column")]
        if len(cells) > 6:
            fields.append(f"...共{len(cells)}列")
        label = "\\n".join(fields)
        lines.append(f'    {nid}["展示字段\\n{label}"]:::cells')

    lines.append("")

    # 5. 边：控件数据集 → 参数控件
    for ds_name, ws in ctrl_ds_to_widgets.items():
        if ds_name not in ctrl_ds_names:
            continue
        src = _node_id("CDS", ds_name)
        for w in ws:
            dst = _node_id("W", w["name"])
            lines.append(f'    {src} -->|"选项"| {dst}')

    # 6. 边：参数控件 → SQL 数据集（经由参数）
    for w in widgets:
        if w["name"] in param_to_sql_ds:
            src = _node_id("W", w["name"])
            for ds_name in param_to_sql_ds[w["name"]]:
                dst = _node_id("DS", ds_name)
                param = _mermaid_label(w["name"])
                lines.append(f'    {src} -->|"${param}"| {dst}')

    # 7. 边：SQL 数据集 → 展示字段
    for ds_name in sql_ds_to_cells:
        src = _node_id("DS", ds_name)
        dst = _node_id("CELLS", ds_name)
        lines.append(f"    {src} --> {dst}")

    return "\n".join(lines)


# ── Graphviz DOT 生成 ─────────────────────────────────────────────────────────

def _build_dot(widgets, datasets, sql_ds_set,
               param_to_sql_ds, ctrl_ds_to_widgets, sql_ds_to_cells,
               ctrl_ds_names) -> str:
    lines = [
        'digraph lineage {',
        '    rankdir=LR;',
        '    node [fontname="Arial", fontsize=9];',
        '    edge [fontname="Arial", fontsize=8];',
        '    graph [nodesep=0.4, ranksep=0.8];',
        '',
    ]

    # ── 控件数据集 cluster ────────────────────────────────────────────────────
    ctrl_ds_list = [ds for ds in datasets if ds["name"] in ctrl_ds_names]
    if ctrl_ds_list:
        lines += [
            '    subgraph cluster_ctrl_ds {',
            '        label="控件数据集"; style=filled; fillcolor="#ECEFF1"; color="#B0BEC5";',
        ]
        for ds in ctrl_ds_list:
            nid = _node_id("CDS", ds["name"])
            label = _dot_label(_trunc(ds["name"]))
            lines.append(
                f'        {nid} [label="{label}", shape=box, style=filled,'
                ' fillcolor="#B0BEC5", fontcolor="#212121"];'
            )
        lines.append('    }')
        lines.append('')

    # ── 参数控件 cluster ──────────────────────────────────────────────────────
    if widgets:
        lines += [
            '    subgraph cluster_widgets {',
            '        label="参数控件"; style=filled; fillcolor="#E3F2FD"; color="#1976D2";',
        ]
        for w in widgets:
            nid = _node_id("W", w["name"])
            label = f'{_dot_label(_trunc(w["name"]))}\\n{w["widget_type"]}'
            lines.append(
                f'        {nid} [label="{label}", shape=box, style=filled,'
                ' fillcolor="#1976D2", fontcolor=white];'
            )
        lines.append('    }')
        lines.append('')

    # ── SQL 数据集 cluster ────────────────────────────────────────────────────
    sql_ds_list = [ds for ds in datasets if ds["name"] in sql_ds_set]
    if sql_ds_list:
        lines += [
            '    subgraph cluster_sql_ds {',
            '        label="SQL 数据集"; style=filled; fillcolor="#E8F5E9"; color="#388E3C";',
        ]
        for ds in sql_ds_list:
            nid = _node_id("DS", ds["name"])
            label = _dot_label(_trunc(ds["name"], 24))
            lines.append(
                f'        {nid} [label="{label}", shape=cylinder, style=filled,'
                ' fillcolor="#388E3C", fontcolor=white];'
            )
        lines.append('    }')
        lines.append('')

    # ── 展示字段 cluster ──────────────────────────────────────────────────────
    if sql_ds_to_cells:
        lines += [
            '    subgraph cluster_cells {',
            '        label="展示字段"; style=filled; fillcolor="#FFF3E0"; color="#F57C00";',
        ]
        for ds_name, cells in sql_ds_to_cells.items():
            nid = _node_id("CELLS", ds_name)
            fields = [_dot_label(c["column"]) for c in cells[:6] if c.get("column")]
            if len(cells) > 6:
                fields.append(f"...{len(cells)}列")
            label = "\\n".join(fields)
            lines.append(
                f'        {nid} [label="{label}", shape=note, style=filled,'
                ' fillcolor="#F57C00", fontcolor=white];'
            )
        lines.append('    }')
        lines.append('')

    # ── 边 ────────────────────────────────────────────────────────────────────
    # 控件数据集 → 参数控件
    for ds_name, ws in ctrl_ds_to_widgets.items():
        if ds_name not in ctrl_ds_names:
            continue
        src = _node_id("CDS", ds_name)
        for w in ws:
            dst = _node_id("W", w["name"])
            lines.append(f'    {src} -> {dst} [label="选项", color="#78909C", style=dashed];')

    # 参数控件 → SQL 数据集
    for w in widgets:
        if w["name"] in param_to_sql_ds:
            src = _node_id("W", w["name"])
            for ds_name in param_to_sql_ds[w["name"]]:
                dst = _node_id("DS", ds_name)
                label = _dot_label(f"${w['name']}")
                lines.append(f'    {src} -> {dst} [label="{label}", color="#1565C0", fontcolor="#1565C0"];')

    # SQL 数据集 → 展示字段
    for ds_name in sql_ds_to_cells:
        src = _node_id("DS", ds_name)
        dst = _node_id("CELLS", ds_name)
        lines.append(f'    {src} -> {dst} [color="#2E7D32"];')

    lines.append('}')
    return "\n".join(lines)
