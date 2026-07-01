from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.prepare_chat_context import prepare_context


class PrepareChatContextTest(unittest.TestCase):
    def test_prepare_context_writes_parsed_and_analysis_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            cpt_path = tmp_dir / "sample.cpt"
            cpt_path.write_bytes(b"fake-cpt")

            with (
                patch("scripts.prepare_chat_context.parse_cpt", return_value=object()),
                patch(
                    "scripts.prepare_chat_context.summarize_to_dict",
                    return_value={
                        "file_name": "",
                        "datasets": [],
                        "widgets": [],
                        "cell_bindings": [],
                        "formula_cells": [],
                    },
                ),
                patch("scripts.prepare_chat_context.analyze_report", return_value={"purpose": "测试报表"}),
            ):
                result = prepare_context(cpt_path, tmp_dir / "out", run_analyze=True)

            parsed = json.loads(Path(result["parsed_json"]).read_text(encoding="utf-8"))
            analysis = json.loads(Path(result["analysis_json"]).read_text(encoding="utf-8"))

        self.assertTrue(result["passed"])
        self.assertEqual(parsed["file_name"], "sample.cpt")
        self.assertEqual(analysis["purpose"], "测试报表")
        self.assertIn("run_chat_acceptance.py", result["next_chat_acceptance_command"])


if __name__ == "__main__":
    unittest.main()
