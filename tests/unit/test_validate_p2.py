from __future__ import annotations

import argparse
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.validate_p2 import _resolve_command, validate_p2


class ValidateP2Test(unittest.TestCase):
    def test_validate_p2_marks_optional_gates_skipped(self):
        args = argparse.Namespace(
            skip_frontend=True,
            real_db_cpt=None,
            fr_webinf_dir="",
            passwords="",
            chat=False,
            api_base="http://127.0.0.1:8000",
            parsed_json=None,
            analysis_json=None,
            questions_json=None,
            chat_out_dir=Path("tmp"),
            analyze=False,
            timeout=120,
        )

        with patch("scripts.validate_p2._run", return_value={"ok": True, "returncode": 0}):
            report = validate_p2(args)

        self.assertTrue(report["passed"])
        self.assertEqual(len(report["required_gates"]), 3)
        self.assertEqual(len(report["optional_gates"]), 2)
        self.assertTrue(all(gate["skipped"] for gate in report["optional_gates"]))

    def test_resolve_command_uses_npm_cmd_on_windows(self):
        with patch("scripts.validate_p2.os.name", "nt"):
            self.assertEqual(_resolve_command(["npm", "run", "build"]), ["npm.cmd", "run", "build"])


if __name__ == "__main__":
    unittest.main()
