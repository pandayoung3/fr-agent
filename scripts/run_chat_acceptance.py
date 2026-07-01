from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_QUESTIONS = [
    "这张报表主要解决什么业务问题？",
    "用户通过哪些控件影响查询或展示结果？",
    "如果我要新增一个筛选条件，应优先检查哪些数据集、SQL 或单元格？",
]


def _post_sse(url: str, payload: dict[str, Any], timeout: int) -> tuple[bool, str]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    text_parts: list[str] = []
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line.startswith("data: "):
                    continue
                event = json.loads(line[6:])
                if event.get("type") == "token":
                    text_parts.append(str(event.get("text", "")))
                if event.get("type") == "error":
                    return False, str(event.get("message", "unknown error"))
                if event.get("type") == "done":
                    return True, "".join(text_parts).strip()
    except urllib.error.HTTPError as exc:
        return False, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001 - CLI should report any connectivity failure clearly.
        return False, str(exc)
    return bool(text_parts), "".join(text_parts).strip()


def run_acceptance(api_base: str, parsed: dict[str, Any], analysis: dict[str, Any], questions: list[str], timeout: int) -> dict[str, Any]:
    history: list[dict[str, str]] = []
    turns = []
    for question in questions:
        ok, answer = _post_sse(
            f"{api_base.rstrip('/')}/api/chat",
            {"parsed": parsed, "analysis": analysis, "question": question, "history": history},
            timeout,
        )
        turns.append({"question": question, "ok": ok, "answer_preview": answer[:300]})
        if not ok:
            return {"passed": False, "turns": turns}
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})
    return {"passed": True, "turns": turns}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a multi-turn chat acceptance check against a local FR-Agent backend.")
    parser.add_argument("--api-base", default="http://127.0.0.1:8000")
    parser.add_argument("--parsed-json", type=Path, required=True)
    parser.add_argument("--analysis-json", type=Path, required=True)
    parser.add_argument("--questions-json", type=Path)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    parsed = json.loads(args.parsed_json.read_text(encoding="utf-8"))
    analysis = json.loads(args.analysis_json.read_text(encoding="utf-8"))
    questions = DEFAULT_QUESTIONS
    if args.questions_json:
        questions = json.loads(args.questions_json.read_text(encoding="utf-8"))

    result = run_acceptance(args.api_base, parsed, analysis, questions, args.timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
