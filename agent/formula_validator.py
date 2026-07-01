"""Formula coordinate validation for parsed FineReport cells."""

from __future__ import annotations

import re
from typing import Any


CELL_REF_RE = re.compile(r"(?<![A-Za-z0-9_])\$?([A-Z]{1,3})\$?([1-9][0-9]{0,5})(?![A-Za-z0-9_])")
RANGE_RE = re.compile(
    r"\$?([A-Z]{1,3})\$?([1-9][0-9]{0,5})\s*:\s*\$?([A-Z]{1,3})\$?([1-9][0-9]{0,5})"
)
RISKY_FUNCTIONS = {"SQL", "EVAL", "EXEC", "JAVA", "SCRIPT"}


def validate_formulas(parsed: dict[str, Any]) -> dict[str, Any]:
    """Validate formula cell references against parsed cell coordinates."""
    cell_index = _build_cell_index(parsed)
    items = []
    issue_count = 0

    for formula_cell in parsed.get("formula_cells") or []:
        if not isinstance(formula_cell, dict):
            continue

        pos = str(formula_cell.get("pos") or "")
        formula = str(formula_cell.get("formula") or "")
        refs = _extract_refs(formula)
        ranges = _extract_ranges(formula)
        missing = sorted(ref for ref in refs if ref not in cell_index)
        risky = _detect_risky_functions(formula)
        status = "ok"
        messages: list[str] = []

        if missing:
            status = "review"
            messages.append("部分引用坐标未在解析出的单元格中出现，可能是空单元格、跨 Sheet 引用或解析遗漏。")
        if risky:
            status = "review"
            messages.append("公式包含高风险函数或脚本类函数，需要人工确认执行语义。")
        if not refs and not ranges:
            status = "review"
            messages.append("未识别到标准单元格坐标，可能是纯函数、参数函数或 FineReport 专有表达式。")

        if status != "ok":
            issue_count += 1

        items.append(
            {
                "pos": pos,
                "formula": formula,
                "references": sorted(refs),
                "ranges": ranges,
                "missing_references": missing,
                "risky_functions": risky,
                "status": status,
                "messages": messages,
            }
        )

    return {
        "total": len(items),
        "issue_count": issue_count,
        "items": items,
    }


def _build_cell_index(parsed: dict[str, Any]) -> set[str]:
    cells = set()
    for key in ("cell_bindings", "formula_cells"):
        for item in parsed.get(key) or []:
            if isinstance(item, dict) and item.get("pos"):
                cells.add(_normalize_ref(str(item["pos"])))
    return cells


def _extract_refs(formula: str) -> set[str]:
    return {_normalize_ref(f"{col}{row}") for col, row in CELL_REF_RE.findall(formula.upper())}


def _extract_ranges(formula: str) -> list[str]:
    return [
        f"{_normalize_ref(start_col + start_row)}:{_normalize_ref(end_col + end_row)}"
        for start_col, start_row, end_col, end_row in RANGE_RE.findall(formula.upper())
    ]


def _detect_risky_functions(formula: str) -> list[str]:
    upper = formula.upper()
    found = []
    for name in sorted(RISKY_FUNCTIONS):
        if re.search(rf"\b{name}\s*\(", upper):
            found.append(name)
    return found


def _normalize_ref(ref: str) -> str:
    return ref.replace("$", "").upper()
