from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ImpactItem:
    name: str
    reason: str
    detail: str = ""

    def as_dict(self) -> dict[str, str]:
        data = {"name": self.name, "reason": self.reason}
        if self.detail:
            data["detail"] = self.detail
        return data


CHANGE_TYPES: dict[str, tuple[str, tuple[str, ...]]] = {
    "filter_control": (
        "筛选/控件变更",
        ("筛选", "查询条件", "条件", "参数", "控件", "下拉", "联动", "选择", "日期", "班级", "年级", "课程", "地区", "region"),
    ),
    "data_logic": (
        "数据口径/取数逻辑变更",
        ("数据", "数据集", "取数", "来源", "sql", "where", "join", "字段", "口径", "表", "明细", "范围"),
    ),
    "display": (
        "展示字段/布局变更",
        ("展示", "显示", "列", "单元格", "表头", "标题", "布局", "样式", "隐藏", "新增列", "字段"),
    ),
    "formula": (
        "公式/指标计算变更",
        ("公式", "计算", "合计", "汇总", "平均", "比率", "比例", "率", "指标", "口径"),
    ),
    "writeback": (
        "填报/写回变更",
        ("填报", "写回", "提交", "保存", "主键", "映射"),
    ),
}


def analyze_change_impact(
    parsed: dict[str, Any],
    analysis: dict[str, Any] | None,
    change_request: str,
    lineage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return deterministic impact analysis for a requested report change."""
    parsed = parsed if isinstance(parsed, dict) else {}
    analysis = analysis if isinstance(analysis, dict) else {}
    lineage = lineage if isinstance(lineage, dict) else {}
    request = (change_request or "").strip()
    request_l = request.lower()

    change_type_keys = _detect_change_types(request_l)
    if not change_type_keys:
        change_type_keys = _infer_change_types_from_entities(parsed, analysis, request_l)
    if not change_type_keys:
        change_type_keys = ["data_logic", "display"]

    datasets = _impacted_datasets(parsed, request_l, change_type_keys)
    widgets = _impacted_widgets(parsed, request_l, change_type_keys)
    fields = _impacted_fields(parsed, analysis, request_l, change_type_keys, datasets)
    cells = _impacted_cells(parsed, fields, datasets, change_type_keys)
    formulas = _impacted_formulas(parsed, analysis, request_l, change_type_keys)
    sql = _impacted_sql(parsed, datasets, widgets, change_type_keys)
    writeback = _impacted_writeback(parsed, change_type_keys)

    affected = {
        "datasets": [item.as_dict() for item in datasets],
        "widgets": [item.as_dict() for item in widgets],
        "fields": [item.as_dict() for item in fields],
        "cells": [item.as_dict() for item in cells],
        "formulas": [item.as_dict() for item in formulas],
        "sql": [item.as_dict() for item in sql],
        "writeback": [item.as_dict() for item in writeback],
    }

    review_points = _review_points(parsed, analysis, lineage, change_type_keys, affected)

    return {
        "change_request": request,
        "change_types": [CHANGE_TYPES[key][0] for key in change_type_keys],
        "summary": _summary(change_type_keys, affected),
        "confidence": _confidence(affected, review_points),
        "affected": affected,
        "suggested_steps": _suggested_steps(affected),
        "evidence": _evidence(parsed, analysis, affected),
        "review_points": review_points,
    }


def _detect_change_types(request_l: str) -> list[str]:
    result: list[str] = []
    for key, (_label, words) in CHANGE_TYPES.items():
        if any(word.lower() in request_l for word in words):
            result.append(key)
    return result


def _infer_change_types_from_entities(parsed: dict[str, Any], analysis: dict[str, Any], request_l: str) -> list[str]:
    result: list[str] = []
    if any(_contains(request_l, widget.get("name")) for widget in _dicts(parsed.get("widgets"))):
        result.append("filter_control")
    if any(_contains(request_l, dataset.get("name")) for dataset in _dicts(parsed.get("datasets"))):
        result.append("data_logic")
    if any(_contains(request_l, cell.get("column")) for cell in _dicts(parsed.get("cell_bindings"))):
        result.extend(["data_logic", "display"])
    if any(_contains(request_l, item.get("indicator_name")) for item in _dicts(analysis.get("indicator_dict"))):
        result.append("formula")
    return _unique(result)


def _impacted_datasets(parsed: dict[str, Any], request_l: str, change_types: list[str]) -> list[ImpactItem]:
    datasets = _dicts(parsed.get("datasets"))
    selected: list[ImpactItem] = []
    for dataset in datasets:
        name = dataset.get("name", "")
        if _contains(request_l, name):
            selected.append(ImpactItem(name, "需求文本直接命中数据集名称", _dataset_detail(dataset)))

    if not selected and any(key in change_types for key in ("data_logic", "filter_control", "formula")):
        sql_datasets = [dataset for dataset in datasets if dataset.get("sql")]
        for dataset in (sql_datasets or datasets)[:5]:
            selected.append(ImpactItem(dataset.get("name", ""), "变更可能影响取数、字段口径或参数过滤", _dataset_detail(dataset)))
    return _dedupe_items(selected)


def _impacted_widgets(parsed: dict[str, Any], request_l: str, change_types: list[str]) -> list[ImpactItem]:
    widgets = _dicts(parsed.get("widgets"))
    selected: list[ImpactItem] = []
    for widget in widgets:
        name = widget.get("name", "")
        display = widget.get("display_column", "")
        key = widget.get("key_column", "")
        if _contains(request_l, name) or _contains(request_l, display) or _contains(request_l, key):
            selected.append(ImpactItem(name, "需求文本命中控件或控件字段", _widget_detail(widget)))

    if not selected and "filter_control" in change_types:
        for widget in widgets[:6]:
            selected.append(ImpactItem(widget.get("name", ""), "筛选或联动变更通常需要检查参数控件", _widget_detail(widget)))
    return _dedupe_items(selected)


def _impacted_fields(
    parsed: dict[str, Any],
    analysis: dict[str, Any],
    request_l: str,
    change_types: list[str],
    datasets: list[ImpactItem],
) -> list[ImpactItem]:
    selected: list[ImpactItem] = []
    dataset_names = {item.name for item in datasets}
    for cell in _dicts(parsed.get("cell_bindings")):
        column = cell.get("column")
        dataset = cell.get("dataset")
        if not column:
            continue
        if _contains(request_l, column) or dataset in dataset_names:
            selected.append(ImpactItem(f"{dataset}.{column}", "字段与变更需求或受影响数据集相关", f"展示单元格：{cell.get('pos', '-')}"))

    for indicator in _dicts(analysis.get("indicator_dict")):
        name = indicator.get("indicator_name")
        source = indicator.get("source_field")
        if _contains(request_l, name) or _contains(request_l, source):
            selected.append(ImpactItem(source or name or "未知指标", "需求命中 AI 指标字典", indicator.get("description", "")))

    if not selected and any(key in change_types for key in ("display", "formula", "data_logic")):
        for cell in _dicts(parsed.get("cell_bindings"))[:8]:
            if cell.get("dataset") and cell.get("column"):
                selected.append(ImpactItem(f"{cell.get('dataset')}.{cell.get('column')}", "可作为修改展示或口径时的优先检查字段", f"展示单元格：{cell.get('pos', '-')}"))
    return _dedupe_items(selected)


def _impacted_cells(parsed: dict[str, Any], fields: list[ImpactItem], datasets: list[ImpactItem], change_types: list[str]) -> list[ImpactItem]:
    field_names = {item.name.split(".", 1)[-1] for item in fields}
    dataset_names = {item.name for item in datasets}
    selected: list[ImpactItem] = []
    for cell in _dicts(parsed.get("cell_bindings")):
        if cell.get("column") in field_names or cell.get("dataset") in dataset_names:
            selected.append(ImpactItem(cell.get("pos", ""), "单元格绑定了受影响字段或数据集", f"{cell.get('dataset', '-')}.{cell.get('column', '-')}"))

    if not selected and "display" in change_types:
        for cell in _dicts(parsed.get("cell_bindings"))[:8]:
            selected.append(ImpactItem(cell.get("pos", ""), "展示变更需要检查单元格绑定", f"{cell.get('dataset', '-')}.{cell.get('column', '-')}"))
    return _dedupe_items(selected)


def _impacted_formulas(parsed: dict[str, Any], analysis: dict[str, Any], request_l: str, change_types: list[str]) -> list[ImpactItem]:
    selected: list[ImpactItem] = []
    formula_meanings = {item.get("pos"): item.get("meaning", "") for item in _dicts(analysis.get("formula_explanations"))}
    for formula in _dicts(parsed.get("formula_cells")):
        pos = formula.get("pos", "")
        formula_text = formula.get("formula", "")
        if "formula" in change_types or _contains(request_l, pos) or _contains(request_l, formula_text):
            detail = f"{formula_text} {formula_meanings.get(pos, '')}".strip()
            selected.append(ImpactItem(pos, "计算或指标变更需要检查公式", detail))
    return _dedupe_items(selected)


def _impacted_sql(parsed: dict[str, Any], datasets: list[ImpactItem], widgets: list[ImpactItem], change_types: list[str]) -> list[ImpactItem]:
    if not any(key in change_types for key in ("data_logic", "filter_control", "formula")):
        return []

    dataset_names = {item.name for item in datasets}
    widget_names = {item.name for item in widgets}
    selected: list[ImpactItem] = []
    for dataset in _dicts(parsed.get("datasets")):
        if not dataset.get("sql"):
            continue
        params = set(_scalars(dataset.get("sql_params")))
        if dataset.get("name") in dataset_names or params.intersection(widget_names) or "filter_control" in change_types:
            selected.append(
                ImpactItem(
                    dataset.get("name", ""),
                    "SQL 可能需要调整 SELECT、WHERE、参数条件或字段口径",
                    f"参数：{', '.join(_scalars(dataset.get('sql_params'))) or '无'}",
                )
            )
    return _dedupe_items(selected)


def _impacted_writeback(parsed: dict[str, Any], change_types: list[str]) -> list[ImpactItem]:
    config = parsed.get("writeback_config")
    if not isinstance(config, dict) or "writeback" not in change_types:
        return []
    return [
        ImpactItem(
            config.get("table") or "填报配置",
            "填报/写回变更需要检查目标表、主键和字段映射",
            f"连接：{config.get('db_connection') or '-'}；主键：{', '.join(_scalars(config.get('key_columns'))) or '-'}",
        )
    ]


def _suggested_steps(affected: dict[str, list[dict[str, str]]]) -> list[str]:
    steps = ["先确认业务口径变化是只影响当前报表，还是会影响共用数据集或字段。"]
    if affected["datasets"]:
        steps.append("检查受影响数据集，确认是否需要新增字段、替换数据源或调整数据集关系。")
    if affected["sql"]:
        steps.append("修改 SQL 的 SELECT / WHERE / 参数条件，并用典型参数验证结果行数和字段值。")
    if affected["widgets"]:
        steps.append("调整参数控件的数据来源、key/display 字段、默认值或联动关系。")
    if affected["fields"] or affected["cells"]:
        steps.append("同步检查展示字段和单元格绑定，确保新口径能显示在正确位置。")
    if affected["formulas"]:
        steps.append("复核公式引用范围和计算口径，避免新增字段后公式仍引用旧单元格。")
    if affected["writeback"]:
        steps.append("复核填报写回表、主键和字段映射，避免提交到错误字段。")
    steps.append("最后用真实参数预览报表，对比变更前后关键结果并记录人工复核结论。")
    return steps


def _evidence(parsed: dict[str, Any], analysis: dict[str, Any], affected: dict[str, list[dict[str, str]]]) -> list[str]:
    evidence = [
        f"报表文件：{parsed.get('file_name', '-')}",
        f"数据集 {len(_dicts(parsed.get('datasets')))} 个，控件 {len(_dicts(parsed.get('widgets')))} 个，单元格绑定 {len(_dicts(parsed.get('cell_bindings')))} 个。",
    ]
    if analysis.get("purpose"):
        evidence.append(f"AI 业务目的：{analysis['purpose']}")
    if affected["datasets"]:
        evidence.append("受影响数据集：" + "、".join(item["name"] for item in affected["datasets"][:5]))
    if affected["widgets"]:
        evidence.append("受影响控件：" + "、".join(item["name"] for item in affected["widgets"][:5]))
    return evidence


def _review_points(
    parsed: dict[str, Any],
    analysis: dict[str, Any],
    lineage: dict[str, Any],
    change_types: list[str],
    affected: dict[str, list[dict[str, str]]],
) -> list[str]:
    points: list[str] = []
    unmatched = lineage.get("unmatched_widget_names") or []
    if unmatched and "filter_control" in change_types:
        points.append(f"{len(unmatched)} 个控件未匹配到直接 SQL 链路，需要人工确认是否通过单元格过滤、JS 或其他配置生效。")
    if "data_logic" in change_types and not affected["sql"]:
        points.append("未定位到 SQL 原文，可能是内置数据集或非 DB 数据源，需要在 FineReport 设计器中复核数据来源。")
    if "formula" in change_types and not affected["formulas"]:
        points.append("未定位到相关公式单元格；若需求涉及计算口径，需要人工检查隐藏公式或父子格计算。")
    if parsed.get("writeback_config") and "writeback" not in change_types:
        points.append("该报表包含填报配置；即使本次需求未直接提到写回，也建议确认变更不会影响提交字段。")
    for risk in _scalars(analysis.get("notes_or_risks"))[:3]:
        points.append(f"既有风险提示：{risk}")
    return points or ["未发现明显阻断点；仍建议用真实参数预览并对账。"]


def _summary(change_types: list[str], affected: dict[str, list[dict[str, str]]]) -> str:
    labels = [CHANGE_TYPES[key][0] for key in change_types]
    touched = []
    for key, label in (
        ("datasets", "数据集"),
        ("sql", "SQL"),
        ("widgets", "控件"),
        ("fields", "字段"),
        ("cells", "单元格"),
        ("formulas", "公式"),
        ("writeback", "填报"),
    ):
        if affected[key]:
            touched.append(f"{label}{len(affected[key])}项")
    scope = "、".join(touched) if touched else "少量直接证据"
    return f"该变更主要属于{'、'.join(labels)}，当前定位到{scope}。"


def _confidence(affected: dict[str, list[dict[str, str]]], review_points: list[str]) -> str:
    count = sum(len(items) for items in affected.values())
    if count >= 6 and len(review_points) <= 2:
        return "高"
    if count >= 2:
        return "中"
    return "低"


def _dataset_detail(dataset: dict[str, Any]) -> str:
    params = _scalars(dataset.get("sql_params"))
    columns = dataset.get("columns") if isinstance(dataset.get("columns"), list) else []
    return f"类型：{dataset.get('type', '-')}；字段数：{len(columns)}；SQL参数：{', '.join(params) or '无'}"


def _widget_detail(widget: dict[str, Any]) -> str:
    parts = [f"类型：{widget.get('widget_type', '-')}"]
    if widget.get("bound_dataset"):
        parts.append(f"选项数据集：{widget['bound_dataset']}")
    if widget.get("key_column"):
        parts.append(f"key：{widget['key_column']}")
    if widget.get("display_column"):
        parts.append(f"display：{widget['display_column']}")
    return "；".join(parts)


def _contains(haystack: str, needle: Any) -> bool:
    value = str(needle or "").strip().lower()
    return bool(value) and value in haystack


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _scalars(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item is not None and not isinstance(item, (dict, list))]


def _unique(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def _dedupe_items(items: list[ImpactItem]) -> list[ImpactItem]:
    result: list[ImpactItem] = []
    seen: set[str] = set()
    for item in items:
        if not item.name or item.name in seen:
            continue
        seen.add(item.name)
        result.append(item)
    return result
