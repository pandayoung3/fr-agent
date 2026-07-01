from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.db_connector import enrich_parsed_datasets, parse_fr_connections
from agent.lineage_builder import build_lineage
from agent.scoring_engine import score_report
from parser.cpt_parser import parse_cpt, summarize_to_dict


def _status(ok: bool, message: str, detail: Any = None) -> dict[str, Any]:
    data: dict[str, Any] = {"ok": ok, "message": message}
    if detail is not None:
        data["detail"] = detail
    return data


def validate_real_db_sample(cpt_path: Path, fr_webinf_dir: str = "", passwords: dict[str, str] | None = None) -> dict[str, Any]:
    summary = parse_cpt(str(cpt_path))
    parsed = summarize_to_dict(summary)
    parsed["file_name"] = cpt_path.name

    fr_connections = parse_fr_connections(fr_webinf_dir) if fr_webinf_dir and Path(fr_webinf_dir).is_dir() else {}
    enrich_report: dict[str, Any] = {"success": [], "failed": [], "skipped": []}
    if fr_connections and passwords:
        parsed, enrich_report = enrich_parsed_datasets(parsed, fr_connections, passwords)

    datasets = [dataset for dataset in parsed.get("datasets", []) if isinstance(dataset, dict)]
    db_datasets = [dataset for dataset in datasets if dataset.get("type") == "DBTableData"]
    sql_datasets = [dataset for dataset in db_datasets if dataset.get("sql")]
    param_datasets = [dataset for dataset in sql_datasets if dataset.get("sql_params")]
    connected_datasets = [dataset for dataset in db_datasets if dataset.get("db_connection")]
    enriched_datasets = [dataset for dataset in db_datasets if dataset.get("column_details")]
    lineage = build_lineage(parsed)
    score = score_report(parsed, {}, lineage)

    checks = {
        "has_dbtabledata": _status(bool(db_datasets), "至少识别到一个 DBTableData 数据集", [d.get("name") for d in db_datasets]),
        "has_db_connection": _status(bool(connected_datasets), "DBTableData 带有 FineReport 连接名", [d.get("db_connection") for d in connected_datasets]),
        "has_sql": _status(bool(sql_datasets), "DBTableData 提取到 SQL 原文", [d.get("name") for d in sql_datasets]),
        "has_sql_params": _status(bool(param_datasets), "SQL 参数可识别", {d.get("name"): d.get("sql_params") for d in param_datasets}),
        "fr_connections_read": _status(bool(fr_connections), "可读取 FineReport WEB-INF 连接配置", sorted(fr_connections.keys())),
        "metadata_enriched": _status(bool(enriched_datasets), "MySQL 字段元数据已增强", [d.get("name") for d in enriched_datasets]),
        "lineage_available": _status(bool(lineage.get("mermaid_raw")), "可生成数据血缘图"),
        "score_available": _status(score.get("score", 0) > 0, "可生成交接可用性评分", {"score": score.get("score"), "grade": score.get("grade")}),
    }

    required_keys = ["has_dbtabledata", "has_db_connection", "has_sql", "lineage_available", "score_available"]
    optional_keys = ["has_sql_params", "fr_connections_read", "metadata_enriched"]

    return {
        "file_name": cpt_path.name,
        "passed": all(checks[key]["ok"] for key in required_keys),
        "required_checks": {key: checks[key] for key in required_keys},
        "optional_checks": {key: checks[key] for key in optional_keys},
        "enrich_report": enrich_report,
        "summary": {
            "datasets": len(datasets),
            "db_datasets": len(db_datasets),
            "widgets": len(parsed.get("widgets", []) or []),
            "cell_bindings": len(parsed.get("cell_bindings", []) or []),
            "formula_cells": len(parsed.get("formula_cells", []) or []),
        },
    }


def _load_passwords(raw: str) -> dict[str, str]:
    if not raw:
        return {}
    if raw.strip().startswith("{"):
        data = json.loads(raw)
        return {str(key): str(value) for key, value in data.items()}
    path = Path(raw)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return {str(key): str(value) for key, value in data.items()}
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a real MySQL + FineReport DBTableData CPT sample.")
    parser.add_argument("cpt_path", type=Path)
    parser.add_argument("--fr-webinf-dir", default="")
    parser.add_argument(
        "--passwords",
        default=os.environ.get("FR_AGENT_DB_PASSWORDS", ""),
        help='JSON object or JSON file path. Example: {"demo_mysql":"password"}',
    )
    args = parser.parse_args()

    if not args.cpt_path.exists():
        print(json.dumps({"passed": False, "error": f"CPT 文件不存在：{args.cpt_path}"}, ensure_ascii=False, indent=2))
        return 2

    result = validate_real_db_sample(args.cpt_path, args.fr_webinf_dir, _load_passwords(args.passwords))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
