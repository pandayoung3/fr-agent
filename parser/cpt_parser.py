"""
CPT 文件解析器 v3
支持 FineReport 11.x 原始 XML 格式

v3 新增：
- 父子格关系（左父格 / 上父格）
- 单元格公式（修复 Formula 类型提取 bug）
- 数据展示模式（列表/分组展开/汇总）
- 单元格数字格式（百分比/日期/整数/小数/常规）
- 单元格过滤条件（父子联动过滤/公式条件）
- 填报提交配置（写入表、主键、字段映射）
- 条件高亮规则（颜色分级业务规则）
- JavaScript 单元格联动事件（隐式控件交互）
"""
import xml.etree.ElementTree as ET
import os
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict


# ── 数据类 ────────────────────────────────────────────────────────────────────

@dataclass
class Dataset:
    name: str
    type: str                           # DBTableData / EmbeddedTableData
    sql: Optional[str] = None
    sql_params: List[str] = field(default_factory=list)
    db_connection: Optional[str] = None
    columns: List[str] = field(default_factory=list)


@dataclass
class WidgetBinding:
    """参数控件（参数面板中）"""
    name: str
    widget_type: str
    bound_dataset: Optional[str] = None
    key_column: Optional[str] = None
    display_column: Optional[str] = None
    custom_options: List[Dict] = field(default_factory=list)


@dataclass
class CellBinding:
    """单元格完整描述"""
    row: int
    col: int
    # 内容类型
    label: Optional[str] = None         # 静态文字
    formula: Optional[str] = None       # FR 公式，如 =SUM(AA4)、=SEQ()
    dataset: Optional[str] = None       # 绑定的数据集名
    column: Optional[str] = None        # 绑定的字段名
    # 格式
    cell_format: Optional[str] = None   # 格式 pattern，如 "#0.00%"、"yyyy-MM-dd"
    format_type: Optional[str] = None   # percent / date / integer / decimal / general
    # 数据展示模式（DSColumn 专属）
    data_mode: Optional[str] = None     # list_group / list_all / aggregate
    # 单元格过滤条件
    cell_filter: Optional[str] = None   # 过滤条件描述
    # 父子格关系
    expand_dir: Optional[str] = None    # "row" / "col"
    parent_left: Optional[str] = None   # 左父格坐标，如 "B4"
    parent_up: Optional[str] = None     # 上父格坐标，如 "A3"
    # 控件
    widget_type: Optional[str] = None
    colspan: int = 1
    rowspan: int = 1
    # JS 联动事件目标控件
    js_events: List[str] = field(default_factory=list)
    # 条件高亮规则
    highlight_rules: List[Dict] = field(default_factory=list)
    # 自定义选项（填报下拉）
    custom_options: List[Dict] = field(default_factory=list)


@dataclass
class LabelDataPair:
    """标签-数据配对：描述一个表单字段的展示结构"""
    label_text: str
    label_pos: str
    data_pos: str
    dataset: Optional[str]
    column: Optional[str]
    widget_type: Optional[str]


@dataclass
class WritebackConfig:
    """填报提交配置"""
    db_connection: Optional[str] = None
    table_schema: Optional[str] = None
    table_name: Optional[str] = None
    key_columns: List[str] = field(default_factory=list)
    column_mappings: List[Dict] = field(default_factory=list)  # [{db_column, param, is_key}]


@dataclass
class ReportSummary:
    file_name: str
    file_size_kb: float
    fr_version: str
    xml_version: str
    report_type: str = "query"
    datasets: List[Dataset] = field(default_factory=list)
    widgets: List[WidgetBinding] = field(default_factory=list)
    cell_bindings: List[CellBinding] = field(default_factory=list)
    label_data_pairs: List[LabelDataPair] = field(default_factory=list)
    dataset_shared_keys: List[Dict] = field(default_factory=list)
    highlight_rules_summary: List[Dict] = field(default_factory=list)  # 去重后的高亮规则
    writeback_config: Optional[WritebackConfig] = None
    db_connections: List[str] = field(default_factory=list)
    sheet_count: int = 0
    errors: List[str] = field(default_factory=list)


# ── 主解析入口 ────────────────────────────────────────────────────────────────

def parse_cpt(file_path: str) -> ReportSummary:
    fname = os.path.basename(file_path)
    size_kb = os.path.getsize(file_path) / 1024

    summary = ReportSummary(
        file_name=fname,
        file_size_kb=round(size_kb, 1),
        fr_version="unknown",
        xml_version="unknown",
    )

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        summary.errors.append(f"XML 解析失败: {e}")
        return summary

    summary.fr_version = root.attrib.get("releaseVersion", "unknown")
    summary.xml_version = root.attrib.get("xmlVersion", "unknown")
    summary.sheet_count = len(root.findall("Report"))
    summary.datasets = _parse_datasets(root)
    summary.db_connections = _parse_connections(root)
    summary.widgets = _parse_widgets(root)

    style_map = _parse_style_map(root)
    summary.cell_bindings = _parse_cells(root, style_map)
    summary.label_data_pairs = _extract_label_data_pairs(summary.cell_bindings)
    summary.dataset_shared_keys = _find_shared_keys(summary.datasets)
    summary.writeback_config = _parse_writeback_config(root)
    summary.highlight_rules_summary = _deduplicate_highlight_rules(summary.cell_bindings)
    summary.report_type = _detect_report_type(root, summary.writeback_config)

    return summary


# ── 数据集 ────────────────────────────────────────────────────────────────────

def _parse_datasets(root: ET.Element) -> List[Dataset]:
    datasets = []
    tdm = root.find("TableDataMap")
    if tdm is None:
        return datasets

    for td in tdm.findall("TableData"):
        name = td.attrib.get("name", "")
        cls = td.attrib.get("class", "")
        ds = Dataset(name=name, type=cls.split(".")[-1])

        query = td.find("Query")
        if query is not None and query.text and query.text.strip():
            ds.sql = query.text.strip()
            ds.sql_params = _extract_sql_params(ds.sql)

        conn = td.find("Connection")
        if conn is not None:
            for sub in conn:
                if sub.text and sub.text.strip():
                    ds.db_connection = sub.text.strip()
                    break

        col_node = td.find("ColumnNames")
        if col_node is not None and col_node.text:
            ds.columns = [c.strip() for c in col_node.text.strip().split(",,.,,") if c.strip()]

        datasets.append(ds)
    return datasets


def _extract_sql_params(sql: str) -> List[str]:
    params = set()
    params.update(re.findall(r'len\((\w+)\)', sql))
    params.update(re.findall(r"'\s*\+\s*(\w+)\s*\+\s*'", sql))
    params.update(re.findall(r'\$\{(\w+)\}', sql))
    return sorted(params)


# ── 数据库连接 ─────────────────────────────────────────────────────────────────

def _parse_connections(root: ET.Element) -> List[str]:
    conn_set = set()
    for conn in root.iter("Connection"):
        for sub in conn:
            v = (sub.text or "").strip()
            if v and len(v) < 100:
                conn_set.add(v)
    return sorted(conn_set)


# ── 参数控件 ──────────────────────────────────────────────────────────────────

def _parse_widgets(root: ET.Element) -> List[WidgetBinding]:
    seen = set()
    widgets = []

    for w in root.iter("InnerWidget"):
        cls = w.attrib.get("class", "")
        name_node = w.find("WidgetName")
        name = name_node.attrib.get("name", "") if name_node is not None else ""
        if not name or not cls or (name, cls) in seen:
            continue
        seen.add((name, cls))

        wb = WidgetBinding(name=name, widget_type=cls.split(".")[-1])

        name_tag = w.find(".//Dictionary//Name")
        if name_tag is not None and name_tag.text:
            wb.bound_dataset = name_tag.text.strip()
            fda = w.find(".//FormulaDictAttr")
            if fda is not None:
                wb.key_column = fda.attrib.get("kiName")
                wb.display_column = fda.attrib.get("viName")

        for d in w.findall(".//CustomDictionary//Dict"):
            k = d.attrib.get("key", "")
            v = d.attrib.get("value", "")
            if k or v:
                wb.custom_options.append({"key": k, "value": v})

        widgets.append(wb)
    return widgets


# ── 样式映射 ──────────────────────────────────────────────────────────────────

def _parse_style_map(root: ET.Element) -> Dict[int, Dict]:
    """构建 style 索引 → 格式信息的映射表（跨所有 Report 节点）"""
    style_map: Dict[int, Dict] = {}
    for style_list in root.iter("StyleList"):
        for i, style in enumerate(style_list):
            fmt = style.find(".//Format")
            if fmt is not None:
                cls = fmt.attrib.get("class", "")
                pattern = (fmt.text or "").strip()
                style_map[i] = {
                    "pattern": pattern,
                    "type": _classify_format(cls, pattern),
                }
    return style_map


def _classify_format(cls: str, pattern: str) -> str:
    """将 FR Format class + pattern 归类为可读类型"""
    if "Date" in cls:
        return "date"
    if "Decimal" in cls or "CoreDecimal" in cls:
        if "%" in pattern:
            return "percent"
        if "." in pattern:
            return "decimal"
        return "integer"
    return "general"


# ── 单元格解析（核心）────────────────────────────────────────────────────────

def _parse_cells(root: ET.Element, style_map: Dict[int, Dict]) -> List[CellBinding]:
    cells = []
    for report in root.findall("Report"):
        cell_list = report.find("CellElementList")
        if cell_list is None:
            continue
        for c in cell_list.findall("C"):
            cb = CellBinding(
                row=int(c.attrib.get("r", 0)),
                col=int(c.attrib.get("c", 0)),
                colspan=int(c.attrib.get("cs", 1)),
                rowspan=int(c.attrib.get("rs", 1)),
            )

            # ── 格式（来自样式表）──────────────────────────────────────────
            s_idx = c.attrib.get("s")
            if s_idx is not None:
                fmt_info = style_map.get(int(s_idx))
                if fmt_info:
                    cb.cell_format = fmt_info["pattern"]
                    cb.format_type = fmt_info["type"]

            # ── 内容解析（O 节点）─────────────────────────────────────────
            o = c.find("O")
            if o is not None:
                o_type = o.attrib.get("t", "")
                o_class = o.attrib.get("class", "")

                if o_type == "DSColumn":
                    # 数据集字段绑定
                    attrs = o.find("Attributes")
                    if attrs is not None:
                        cb.dataset = attrs.attrib.get("dsName")
                        cb.column = attrs.attrib.get("columnName")

                    # 数据展示模式
                    cb.data_mode = _parse_data_mode(o)

                    # 单元格过滤条件
                    cb.cell_filter = _parse_cell_filter(o)

                elif "Formula" in o_class:
                    # 公式单元格（修复：内容在 <Attributes> 的 .text，不在 o.text）
                    attrs = o.find("Attributes")
                    if attrs is not None and attrs.text and attrs.text.strip():
                        cb.formula = attrs.text.strip()

                else:
                    # 静态文字标签
                    if o.text and o.text.strip():
                        cb.label = o.text.strip()

            # ── 内嵌控件 ──────────────────────────────────────────────────
            w_node = c.find("Widget")
            if w_node is not None:
                cb.widget_type = w_node.attrib.get("class", "").split(".")[-1]
                for d in w_node.findall(".//CustomDictionary//Dict"):
                    cb.custom_options.append({
                        "key": d.attrib.get("key", ""),
                        "value": d.attrib.get("value", ""),
                    })

            # ── 扩展方向 + 父子格 ─────────────────────────────────────────
            expand = c.find("Expand")
            if expand is not None:
                d = expand.attrib.get("dir", "0")
                if d == "1":
                    cb.expand_dir = "row"
                elif d == "2":
                    cb.expand_dir = "col"
                left = expand.attrib.get("left", "")
                up = expand.attrib.get("up", "")
                if left:
                    cb.parent_left = left
                if up:
                    cb.parent_up = up

            # ── JS 联动事件 ───────────────────────────────────────────────
            cb.js_events = _extract_js_events(c)

            # ── 条件高亮规则 ──────────────────────────────────────────────
            cb.highlight_rules = _extract_highlight_rules(c)

            # 只保留有实质内容的单元格
            if cb.label or cb.dataset or cb.widget_type or cb.formula:
                cells.append(cb)

    return sorted(cells, key=lambda x: (x.row, x.col))


def _parse_data_mode(o: ET.Element) -> Optional[str]:
    """解析 DSColumn 单元格的数据展示模式"""
    rg = o.find("RG")
    if rg is None:
        return None
    rg_class = rg.attrib.get("class", "")
    attr = rg.find("Attr")
    divide_mode = attr.attrib.get("divideMode", "0") if attr is not None else "0"

    if "SumFunctionGrouper" in rg_class or "AvgFunctionGrouper" in rg_class:
        func = rg_class.split(".")[-1].replace("FunctionGrouper", "").lower()
        return f"aggregate_{func}" if func else "aggregate"
    elif divide_mode == "1":
        return "list_group"   # 分组展开，不重复（按该字段值分组）
    else:
        return "list_all"     # 全量列表展示


def _parse_cell_filter(o: ET.Element) -> Optional[str]:
    """解析 DSColumn 单元格的过滤条件"""
    cond = o.find("Condition")
    if cond is None:
        return None
    cond_class = cond.attrib.get("class", "")

    # 空 ListCondition = 无过滤
    if "ListCondition" in cond_class and len(list(cond)) == 0:
        return None

    if "CommonCondition" in cond_class:
        cname = cond.find("CNAME")
        compare_col = cond.find(".//SimpleDSColumn")
        if cname is not None and compare_col is not None:
            field_name = (cname.text or "").strip()
            ref_ds = compare_col.attrib.get("dsName", "")
            ref_col = compare_col.attrib.get("columnName", "")
            return f"关联过滤: 按 {field_name} 匹配 {ref_ds}.{ref_col}"
        return "关联过滤（详见XML）"

    if "FormulaCondition" in cond_class:
        f_node = cond.find("Formula")
        if f_node is not None and f_node.text:
            return f"公式条件: {f_node.text.strip()}"

    # ListCondition 含嵌套 JoinCondition（复合条件）
    formulas = []
    for jc in cond.findall("JoinCondition"):
        for fc in jc.findall("Condition"):
            if "FormulaCondition" in fc.attrib.get("class", ""):
                f_node = fc.find("Formula")
                if f_node is not None and f_node.text:
                    formulas.append(f_node.text.strip())
    if formulas:
        return "复合条件: " + " AND ".join(formulas)

    return None


def _extract_js_events(c: ET.Element) -> List[str]:
    """提取单元格 JavaScript 事件中联动的目标控件名"""
    targets = []
    for js in c.findall(".//JavaScript"):
        content = js.find("Content")
        if content is not None and content.text:
            names = re.findall(r'getWidgetByName\s*\(\s*["\'](\w+)["\']\s*\)', content.text)
            targets.extend(names)
    return sorted(set(targets))


def _extract_highlight_rules(c: ET.Element) -> List[Dict]:
    """提取单元格条件高亮规则"""
    rules = []
    hl_list = c.find("HighlightList")
    if hl_list is None:
        return rules

    for hl in hl_list.findall("Highlight"):
        rule: Dict = {}

        name_node = hl.find("Name")
        rule["name"] = (name_node.text or "").strip() if name_node is not None else ""

        # 条件
        cond = hl.find("Condition")
        if cond is not None:
            cond_class = cond.attrib.get("class", "")
            if "FormulaCondition" in cond_class:
                f_node = cond.find("Formula")
                rule["condition"] = (f_node.text or "").strip() if f_node is not None else ""
            else:
                # 嵌套 JoinCondition 列表
                formulas = []
                for jc in cond.findall("JoinCondition"):
                    for fc in jc.findall("Condition"):
                        if "FormulaCondition" in fc.attrib.get("class", ""):
                            f_node = fc.find("Formula")
                            if f_node is not None and f_node.text:
                                formulas.append(f_node.text.strip())
                rule["condition"] = " AND ".join(formulas)

        # 动作（背景色/字体色）
        action = hl.find("HighlightAction")
        if action is not None:
            action_class = action.attrib.get("class", "")
            if "Background" in action_class:
                rule["action"] = "background_color"
                color_node = action.find(".//FineColor")
                if color_node is not None:
                    try:
                        color_int = int(color_node.attrib.get("color", "0"))
                        rgb = color_int & 0xFFFFFF
                        rule["color"] = f"#{rgb:06X}"
                    except (ValueError, OverflowError):
                        pass
            elif "Font" in action_class:
                rule["action"] = "font_color"
            else:
                rule["action"] = action_class.split(".")[-1]

        if rule.get("name") or rule.get("condition"):
            rules.append(rule)

    return rules


# ── 高亮规则去重 ──────────────────────────────────────────────────────────────

def _deduplicate_highlight_rules(cells: List[CellBinding]) -> List[Dict]:
    """
    将分散在各单元格的高亮规则去重合并：
    相同名称的规则只保留一条，记录影响了哪些字段。
    """
    rule_map: Dict[str, Dict] = {}
    for cell in cells:
        for rule in cell.highlight_rules:
            name = rule.get("name", "")
            if not name:
                continue
            if name not in rule_map:
                rule_map[name] = {
                    "name": name,
                    "condition": rule.get("condition", ""),
                    "action": rule.get("action", ""),
                    "color": rule.get("color", ""),
                    "affected_columns": [],
                }
            if cell.column and cell.column not in rule_map[name]["affected_columns"]:
                rule_map[name]["affected_columns"].append(cell.column)

    return list(rule_map.values())


# ── 报表类型识别 ───────────────────────────────────────────────────────────────

def _detect_report_type(root: ET.Element, writeback_config: Optional[WritebackConfig] = None) -> str:
    if writeback_config is not None:
        return "writeback"

    if root.find(".//ReportWriteAttr") is not None:
        return "writeback"

    for elem in root.iter("Widget"):
        cls = elem.attrib.get("class", "")
        if "AppendRowButton" in cls or "DeleteRowButton" in cls:
            return "writeback"
    return "query"


# ── 填报提交配置 ───────────────────────────────────────────────────────────────

def _parse_writeback_config(root: ET.Element) -> Optional[WritebackConfig]:
    """解析填报报表的数据提交配置（写入哪张表、主键、字段映射）"""
    for report in root.findall("Report"):
        write_attr = report.find("ReportWriteAttr")
        if write_attr is None:
            continue
        visitor = write_attr.find(".//SubmitVisitor")
        if visitor is None:
            continue

        cfg = WritebackConfig()
        db_attrs = visitor.find("Attributes")
        if db_attrs is not None:
            cfg.db_connection = db_attrs.attrib.get("dsName")

        dml = visitor.find("DMLConfig")
        if dml is not None:
            table = dml.find("Table")
            if table is not None:
                cfg.table_schema = table.attrib.get("schema")
                cfg.table_name = table.attrib.get("name")

            for col_cfg in dml.findall("ColumnConfig"):
                col_name = col_cfg.attrib.get("name", "")
                is_key = col_cfg.attrib.get("isKey") == "true"
                param_attrs = col_cfg.find(".//Parameter/Attributes")
                param_name = param_attrs.attrib.get("name") if param_attrs is not None else None

                if col_name:
                    if is_key:
                        cfg.key_columns.append(col_name)
                    cfg.column_mappings.append({
                        "db_column": col_name,
                        "param": param_name,
                        "is_key": is_key,
                    })

        return cfg
    return None


# ── 标签-数据配对 ─────────────────────────────────────────────────────────────

def _extract_label_data_pairs(cells: List[CellBinding]) -> List[LabelDataPair]:
    cell_map = {(c.row, c.col): c for c in cells}
    pairs = []
    for c in cells:
        if not c.label:
            continue
        for offset in [1, 2, c.colspan]:
            neighbor = cell_map.get((c.row, c.col + offset))
            if neighbor and neighbor.dataset:
                pairs.append(LabelDataPair(
                    label_text=c.label,
                    label_pos=f"({c.row},{c.col})",
                    data_pos=f"({neighbor.row},{neighbor.col})",
                    dataset=neighbor.dataset,
                    column=neighbor.column,
                    widget_type=neighbor.widget_type,
                ))
                break
    return pairs


# ── 跨数据集共享字段识别 ───────────────────────────────────────────────────────

def _find_shared_keys(datasets: List[Dataset]) -> List[Dict]:
    if len(datasets) < 2:
        return []
    from collections import defaultdict
    field_to_datasets: Dict[str, List[str]] = defaultdict(list)
    for ds in datasets:
        for col in ds.columns:
            field_to_datasets[col].append(ds.name)
    shared = []
    for field, ds_names in field_to_datasets.items():
        if len(ds_names) >= 2:
            shared.append({"field": field, "shared_by": ds_names, "likely_join_key": True})
    return shared


# ── 序列化输出 ────────────────────────────────────────────────────────────────

_DATA_MODE_ZH = {
    "list_group": "分组展开（不重复）",
    "list_all":   "全量列表",
    "aggregate":  "汇总",
}

_FORMAT_TYPE_ZH = {
    "percent": "百分比",
    "date":    "日期",
    "integer": "整数",
    "decimal": "小数",
    "general": "常规",
}


def summarize_to_dict(summary: ReportSummary) -> dict:
    # 分离公式单元格和数据绑定单元格
    formula_cells = [cb for cb in summary.cell_bindings if cb.formula]
    bound_cells = [cb for cb in summary.cell_bindings if cb.dataset]

    wb_cfg = None
    if summary.writeback_config:
        cfg = summary.writeback_config
        full_table = f"{cfg.table_schema}.{cfg.table_name}" if cfg.table_schema else cfg.table_name
        wb_cfg = {
            "db_connection": cfg.db_connection,
            "table": full_table,
            "key_columns": cfg.key_columns,
            "column_mappings": cfg.column_mappings,
        }

    return {
        "file_name": summary.file_name,
        "file_size_kb": summary.file_size_kb,
        "fr_version": summary.fr_version,
        "report_type": summary.report_type,
        "sheet_count": summary.sheet_count,
        "db_connections": summary.db_connections,
        "datasets": [
            {
                "name": d.name,
                "type": d.type,
                "db_connection": d.db_connection,
                "sql": d.sql,
                "sql_params": d.sql_params,
                "columns": d.columns,
            }
            for d in summary.datasets
        ],
        "widgets": [
            {
                "name": w.name,
                "widget_type": w.widget_type,
                "bound_dataset": w.bound_dataset,
                "key_column": w.key_column,
                "display_column": w.display_column,
                "custom_options": w.custom_options,
            }
            for w in summary.widgets
            if w.widget_type not in ("Label", "FreeButton", "FormSubmitButton")
        ],
        "cell_bindings": [
            {k: v for k, v in {
                "pos": f"({cb.row},{cb.col})",
                "label": cb.label,
                "dataset": cb.dataset,
                "column": cb.column,
                "data_mode": _DATA_MODE_ZH.get(cb.data_mode, cb.data_mode) if cb.data_mode else None,
                "cell_format": cb.cell_format,
                "format_type": _FORMAT_TYPE_ZH.get(cb.format_type, cb.format_type) if cb.format_type else None,
                "cell_filter": cb.cell_filter,
                "parent_left": cb.parent_left,
                "parent_up": cb.parent_up,
                "widget_type": cb.widget_type,
                "expand_dir": cb.expand_dir,
                "colspan": cb.colspan if cb.colspan > 1 else None,
                "rowspan": cb.rowspan if cb.rowspan > 1 else None,
                "js_events": cb.js_events if cb.js_events else None,
                "custom_options": cb.custom_options if cb.custom_options else None,
            }.items() if v is not None}
            for cb in summary.cell_bindings
        ],
        "formula_cells": [
            {
                "pos": f"({cb.row},{cb.col})",
                "formula": cb.formula,
                "widget_type": cb.widget_type,
                "js_events": cb.js_events if cb.js_events else None,
            }
            for cb in formula_cells
        ],
        "label_data_pairs": [
            {
                "label_text": p.label_text,
                "label_pos": p.label_pos,
                "data_pos": p.data_pos,
                "dataset": p.dataset,
                "column": p.column,
                "widget_type": p.widget_type,
            }
            for p in summary.label_data_pairs
        ],
        "dataset_shared_keys": summary.dataset_shared_keys,
        "highlight_rules_summary": summary.highlight_rules_summary,
        "writeback_config": wb_cfg,
        "errors": summary.errors,
    }
