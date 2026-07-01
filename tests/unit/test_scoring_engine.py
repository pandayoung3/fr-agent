import unittest

from agent.scoring_engine import score_report
from tests.helpers import minimal_analysis, minimal_parsed


class ScoringEngineTest(unittest.TestCase):
    def test_score_report_returns_dimension_breakdown(self):
        result = score_report(minimal_parsed(), minimal_analysis(), {"mermaid_raw": "flowchart LR"})

        self.assertGreaterEqual(result["score"], 70)
        self.assertIn(result["grade"], {"A", "B", "C"})
        self.assertEqual(
            {item["key"] for item in result["dimensions"]},
            {"parser", "lineage", "analysis", "delivery"},
        )
        self.assertTrue(result["recommendations"])


if __name__ == "__main__":
    unittest.main()
