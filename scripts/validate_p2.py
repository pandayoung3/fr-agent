from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.prepare_chat_context import prepare_context
from scripts.run_chat_acceptance import DEFAULT_QUESTIONS, run_acceptance
from scripts.validate_real_db_sample import _load_passwords, validate_real_db_sample


def _run(command: list[str], cwd: Path = ROOT) -> dict[str, Any]:
    resolved = _resolve_command(command)
    try:
        completed = subprocess.run(
            resolved,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        return {
            "command": " ".join(command),
            "ok": False,
            "returncode": 127,
            "stdout_tail": "",
            "stderr_tail": str(exc),
        }
    return {
        "command": " ".join(command),
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout_tail": (completed.stdout or "")[-2000:],
        "stderr_tail": (completed.stderr or "")[-2000:],
    }


def _resolve_command(command: list[str]) -> list[str]:
    if os.name == "nt" and command and command[0] == "npm":
        return ["npm.cmd", *command[1:]]
    return command


def _gate(name: str, result: dict[str, Any], required: bool = True) -> dict[str, Any]:
    return {"name": name, "required": required, **result}


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def validate_p2(args: argparse.Namespace) -> dict[str, Any]:
    gates: list[dict[str, Any]] = [
        _gate("git diff --check", _run(["git", "diff", "--check"])),
        _gate("python compileall", _run([sys.executable, "-m", "compileall", "-q", "api", "agent", "parser", "scripts", "tests"])),
        _gate("python unittest", _run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-p", "test_*.py", "-v"])),
    ]

    if not args.skip_frontend:
        gates.append(_gate("web lint", _run(["npm", "run", "lint"], ROOT / "web")))
        gates.append(_gate("web build", _run(["npm", "run", "build"], ROOT / "web")))

    real_db_result: dict[str, Any] | None = None
    if args.real_db_cpt:
        real_db_result = validate_real_db_sample(args.real_db_cpt, args.fr_webinf_dir, _load_passwords(args.passwords))
        gates.append(_gate("real DBTableData CPT validation", {"ok": bool(real_db_result.get("passed")), "detail": real_db_result}))
    else:
        gates.append(_gate("real DBTableData CPT validation", {"ok": False, "skipped": True, "reason": "未提供 --real-db-cpt"}, required=False))

    chat_result: dict[str, Any] | None = None
    if args.chat:
        if args.parsed_json and args.analysis_json:
            parsed = json.loads(args.parsed_json.read_text(encoding="utf-8"))
            analysis = json.loads(args.analysis_json.read_text(encoding="utf-8"))
        elif args.real_db_cpt:
            context = prepare_context(
                args.real_db_cpt,
                args.chat_out_dir,
                args.fr_webinf_dir,
                _load_passwords(args.passwords),
                args.analyze,
            )
            parsed = json.loads(Path(context["parsed_json"]).read_text(encoding="utf-8"))
            analysis = json.loads(Path(context["analysis_json"]).read_text(encoding="utf-8"))
        else:
            parsed = {}
            analysis = {}

        questions = DEFAULT_QUESTIONS
        if args.questions_json:
            questions = json.loads(args.questions_json.read_text(encoding="utf-8"))
        chat_result = run_acceptance(args.api_base, parsed, analysis, questions, args.timeout)
        gates.append(_gate("multi-turn chat acceptance", {"ok": bool(chat_result.get("passed")), "detail": chat_result}))
    else:
        gates.append(_gate("multi-turn chat acceptance", {"ok": False, "skipped": True, "reason": "未传入 --chat"}, required=False))

    passed = all(gate["ok"] for gate in gates if gate.get("required", True))
    return {
        "passed": passed,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "required_gates": [gate for gate in gates if gate.get("required", True)],
        "optional_gates": [gate for gate in gates if not gate.get("required", True)],
        "real_db_result": real_db_result,
        "chat_result": chat_result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the P2 validation gates and optionally real DB/chat acceptance.")
    parser.add_argument("--skip-frontend", action="store_true")
    parser.add_argument("--real-db-cpt", type=Path)
    parser.add_argument("--fr-webinf-dir", default="")
    parser.add_argument("--passwords", default=os.environ.get("FR_AGENT_DB_PASSWORDS", ""))
    parser.add_argument("--chat", action="store_true", help="Run multi-turn chat acceptance.")
    parser.add_argument("--api-base", default="http://127.0.0.1:8000")
    parser.add_argument("--parsed-json", type=Path)
    parser.add_argument("--analysis-json", type=Path)
    parser.add_argument("--questions-json", type=Path)
    parser.add_argument("--chat-out-dir", type=Path, default=Path("tmp") / "p2_chat_context")
    parser.add_argument("--analyze", action="store_true", help="When --chat uses --real-db-cpt, call LLM to create analysis.json.")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--report", type=Path, default=Path("tmp") / "p2_validation_report.json")
    args = parser.parse_args()

    if args.real_db_cpt and not args.real_db_cpt.exists():
        print(json.dumps({"passed": False, "error": f"CPT 文件不存在：{args.real_db_cpt}"}, ensure_ascii=False, indent=2))
        return 2
    if args.chat and not args.real_db_cpt and not (args.parsed_json and args.analysis_json):
        print(json.dumps({"passed": False, "error": "--chat 需要 --real-db-cpt 或 --parsed-json + --analysis-json"}, ensure_ascii=False, indent=2))
        return 2

    report = validate_p2(args)
    _write_report(args.report, report)
    print(json.dumps({"passed": report["passed"], "report": str(args.report)}, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
