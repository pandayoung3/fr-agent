import unittest

from agent.lineage_builder import build_lineage
from tests.helpers import minimal_parsed


class LineageBuilderTest(unittest.TestCase):
    def test_build_lineage_returns_graph_payload(self):
        result = build_lineage(minimal_parsed())

        self.assertIn("flowchart LR", result["mermaid_raw"])
        self.assertIn("digraph lineage", result["dot"])
        self.assertIn("region", result["option_driving_widget_names"])


if __name__ == "__main__":
    unittest.main()
