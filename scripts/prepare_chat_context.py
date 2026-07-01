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
from agent.llm_analyzer import analyze_report
from parser.cpt_parser import parse_cpt, summarize_to_dict


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


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def prepare_context(
    cpt_path: Path,
    out_dir: Path,
    fr_webinf_dir: str = "",
    passwords: dict[str, str] | None = None,
    run_analyze: bool = False,
) -> dict[str, Any]:
    summary = parse_cpt(str(cpt_path))
    parsed = summarize_to_dict(summary)
    parsed["file_name"] = cpt_path.name

    enrich_report: dict[str, Any] = {"success": [], "failed": [], "skipped": []}
    if fr_webinf_dir and Path(fr_webinf_dir).is_dir():
        fr_connections = parse_fr_connections(fr_webinf_dir)
        if passwords:
            parsed, enrich_report = enrich_parsed_datasets(parsed, fr_connections, passwords)

    analysis: dict[str, Any] = {}
    if run_analyze:
        analysis = analyze_report(parsed)

    parsed_path = out_dir / "parsed.json"
    analysis_path = out_dir / "analysis.json"
    _write_json(parsed_path, parsed)
    _write_json(analysis_path, analysis)

    return {
        "passed": True,
        "file_name": cpt_path.name,
        "parsed_json": str(parsed_path),
        "analysis_json": str(analysis_path),
        "analysis_mode": "llm" if run_analyze else "empty",
        "enrich_report": enrich_report,
        "next_chat_acceptance_command": (
            f'python scripts/run_chat_acceptance.py --parsed-json "{parsed_path}" '
            f'--analysis-json "{analysis_path}"'
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare parsed.json and analysis.json for P2 multi-turn chat acceptance.")
    parser.add_argument("cpt_path", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("tmp") / "p2_chat_context")
    parser.add_argument("--fr-webinf-dir", default="")
    parser.add_argument(
        "--passwords",
        default=os.environ.get("FR_AGENT_DB_PASSWORDS", ""),
        help='JSON object or JSON file path. Example: {"demo_mysql":"password"}',
    )
    parser.add_argument("--analyze", action="store_true", help="Call the configured LLM and write a real analysis.json.")
    args = parser.parse_args()

    if not args.cpt_path.exists():
        print(json.dumps({"passed": False, "error": f"CPT 文件不存在：{args.cpt_path}"}, ensure_ascii=False, indent=2))
        return 2

    try:
        result = prepare_context(
            args.cpt_path,
            args.out_dir,
            args.fr_webinf_dir,
            _load_passwords(args.passwords),
            args.analyze,
        )
    except Exception as exc:  # noqa: BLE001 - CLI should produce a readable validation error.
        print(json.dumps({"passed": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
