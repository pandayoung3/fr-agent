import unittest

from agent.formula_validator import validate_formulas
from tests.helpers import minimal_parsed


class FormulaValidatorTest(unittest.TestCase):
    def test_validate_formulas_flags_missing_reference(self):
        result = validate_formulas(minimal_parsed())

        self.assertEqual(result["total"], 2)
        self.assertEqual(result["issue_count"], 1)
        missing = [item for item in result["items"] if item["pos"] == "D1"][0]
        self.assertEqual(missing["status"], "review")
        self.assertEqual(missing["missing_references"], ["Z99"])


if __name__ == "__main__":
    unittest.main()
