"""Rule-based report quality scoring for the P1 baseline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DimensionScore:
    key: str
    label: str
    score: int
    max_score: int
    findings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "score": self.score,
            "max_score": self.max_score,
            "findings": self.findings,
        }


def _count(items: Any) -> int:
    return len(items) if isinstance(items, list) else 0


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _clamp(value: int, max_score: int) -> int:
    return max(0, min(max_score, value))


def score_report(
    parsed: dict[str, Any],
    analysis: dict[str, Any] | None = None,
    lineage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a deterministic P1 score from parser, AI, and lineage outputs."""
    analysis = analysis or {}
    lineage = lineage or {}

    dimensions = [
        _score_parser(parsed),
        _score_lineage(parsed, lineage),
        _score_ai_analysis(parsed, analysis),
        _score_delivery(parsed, analysis, lineage),
    ]

    total = sum(item.score for item in dimensions)
    max_total = sum(item.max_score for item in dimensions)
    normalized = round(total / max_total * 100) if max_total else 0

    if normalized >= 90:
        grade = "A"
    elif normalized >= 75:
        grade = "B"
    elif normalized >= 60:
        grade = "C"
    else:
        grade = "D"

    recommendations = _recommend(parsed, analysis, lineage, dimensions)
    top_findings = [finding for item in dimensions for finding in item.findings[:2]][:6]

    return {
        "score": normalized,
        "grade": grade,
        "dimensions": [item.to_dict() for item in dimensions],
        "top_findings": top_findings,
        "recommendations": recommendations,
    }


def _score_parser(parsed: dict[str, Any]) -> DimensionScore:
    score = 0
    findings: list[str] = []

    if _count(parsed.get("datasets")):
        score += 8
    else:
        findings.append("未识别到数据集，后续血缘和字段解释会受限。")

    if _count(parsed.get("cell_bindings")):
        score += 8
    else:
        findings.append("未识别到单元格字段绑定，无法稳定说明展示字段。")

    if _count(parsed.get("widgets")):
        score += 5

    if _count(parsed.get("formula_cells")):
        score += 3

    if not parsed.get("errors"):
        score += 6
    else:
        findings.append("解析结果包含错误，需要先复核 CPT 结构或解析器覆盖范围。")

    return DimensionScore("parser", "解析完整度", _clamp(score, 30), 30, findings)


def _score_lineage(parsed: dict[str, Any], lineage: dict[str, Any]) -> DimensionScore:
    score = 0
    findings: list[str] = []

    if lineage.get("mermaid_raw") or lineage.get("dot"):
        score += 7
    else:
        findings.append("尚未生成血缘图，无法快速浏览控件、数据集和字段关系。")

    if _count(lineage.get("sql_driving_widget_names")):
        score += 5
    if _count(lineage.get("option_driving_widget_names")):
        score += 5

    datasets = parsed.get("datasets") or []
    cell_bindings = parsed.get("cell_bindings") or []
    displayed_datasets = {
        cell.get("dataset")
        for cell in cell_bindings
        if isinstance(cell, dict) and cell.get("dataset")
    }
    if datasets and len(displayed_datasets) >= min(len(datasets), 1):
        score += 5

    unmatched = lineage.get("unmatched_widget_names") or []
    if unmatched:
        findings.append(f"仍有 {len(unmatched)} 个控件未匹配到参数或选项链路。")
    else:
        score += 3

    return DimensionScore("lineage", "血缘清晰度", _clamp(score, 25), 25, findings)


def _score_ai_analysis(parsed: dict[str, Any], analysis: dict[str, Any]) -> DimensionScore:
    score = 0
    findings: list[str] = []

    for key in ("purpose", "layout_description", "dataset_relationships", "field_semantics"):
        if _has_text(analysis.get(key)):
            score += 3

    if _count(analysis.get("interaction_chains")):
        score += 5
    else:
        findings.append("AI 结果缺少交互链路解释，客户难以理解筛选控件影响。")

    indicator_count = _count(analysis.get("indicator_dict"))
    if indicator_count:
        score += 4
    elif _count(parsed.get("cell_bindings")):
        findings.append("尚未形成指标字典，字段交付仍偏技术解析。")

    formula_count = _count(parsed.get("formula_cells"))
    explained_formula_count = _count(analysis.get("formula_explanations"))
    if formula_count == 0 or explained_formula_count:
        score += 4
    else:
        findings.append("存在公式单元格，但 AI 未给出公式含义解释。")

    return DimensionScore("analysis", "AI 解释质量", _clamp(score, 25), 25, findings)


def _score_delivery(
    parsed: dict[str, Any],
    analysis: dict[str, Any],
    lineage: dict[str, Any],
) -> DimensionScore:
    score = 0
    findings: list[str] = []

    if parsed.get("report_type") in {"query", "writeback"}:
        score += 4

    if parsed.get("writeback_config"):
        findings.append("该报表包含填报写回配置，上线交付前需要重点复核主键和字段映射。")
    else:
        score += 3

    if _count(analysis.get("notes_or_risks")):
        score += 4
    else:
        findings.append("风险提示较少，建议在交付文档中补充人工复核项。")

    if lineage.get("mermaid_raw"):
        score += 3

    if parsed.get("db_connections"):
        findings.append("检测到数据库连接名；真实 DBTableData 全链路验证已移至 P2。")
    else:
        score += 3

    if _count(analysis.get("development_steps")):
        score += 3

    return DimensionScore("delivery", "交付就绪度", _clamp(score, 20), 20, findings)


def _recommend(
    parsed: dict[str, Any],
    analysis: dict[str, Any],
    lineage: dict[str, Any],
    dimensions: list[DimensionScore],
) -> list[str]:
    recommendations: list[str] = []

    if not lineage.get("mermaid_raw"):
        recommendations.append("先生成血缘图，再从工作台检查控件、数据集、字段的可解释链路。")
    if not _count(analysis.get("indicator_dict")):
        recommendations.append("补充指标字典，让业务用户直接看到字段含义、口径和单位。")
    if _count(parsed.get("formula_cells")) and not _count(analysis.get("formula_explanations")):
        recommendations.append("对公式单元格做人工抽检，确认引用坐标、计算口径和展示影响。")
    if parsed.get("writeback_config"):
        recommendations.append("填报报表需要复核写回表、主键列和字段映射，避免误写生产数据。")

    weakest = min(dimensions, key=lambda item: item.score / item.max_score)
    recommendations.append(f"下一轮优先提升「{weakest.label}」。")

    return recommendations[:5]
