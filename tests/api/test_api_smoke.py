import unittest

from fastapi.testclient import TestClient

from api.main import app
from tests.helpers import minimal_analysis, minimal_parsed


class ApiSmokeTest(unittest.TestCase):
    def test_llm_config_does_not_expose_secret(self):
        client = TestClient(app)
        response = client.get("/api/llm/config")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotIn("api_key", data)
        self.assertIn("api_key_hint", data)

    def test_score_and_formula_endpoints(self):
        client = TestClient(app)
        parsed = minimal_parsed()

        score_response = client.post(
            "/api/score",
            json={"parsed": parsed, "analysis": minimal_analysis(), "lineage": {"mermaid_raw": "flowchart LR"}},
        )
        formula_response = client.post("/api/validate/formulas", json={"parsed": parsed})

        self.assertEqual(score_response.status_code, 200)
        self.assertEqual(formula_response.status_code, 200)
        self.assertGreaterEqual(score_response.json()["score"], 70)
        self.assertEqual(formula_response.json()["issue_count"], 1)

    def test_change_impact_endpoint_locates_widget(self):
        client = TestClient(app)

        response = client.post(
            "/api/change-impact",
            json={
                "parsed": minimal_parsed(),
                "analysis": minimal_analysis(),
                "change_request": "新增按地区筛选",
                "lineage": {"unmatched_widget_names": []},
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("筛选/控件变更", data["change_types"])
        self.assertTrue(any(item["name"] == "region" for item in data["affected"]["widgets"]))
        self.assertGreater(len(data["suggested_steps"]), 0)
        self.assertGreater(len(data["review_points"]), 0)

    def test_change_impact_rejects_empty_request(self):
        client = TestClient(app)

        response = client.post(
            "/api/change-impact",
            json={"parsed": minimal_parsed(), "analysis": {}, "change_request": "   "},
        )

        self.assertEqual(response.status_code, 400)

    def test_change_impact_tolerates_malformed_analysis(self):
        client = TestClient(app)
        malformed_analysis = {
            "purpose": "销售分析",
            "indicator_dict": None,
            "formula_explanations": "bad-shape",
            "notes_or_risks": [None, {"bad": "shape"}, "需要人工确认口径"],
        }

        response = client.post(
            "/api/change-impact",
            json={
                "parsed": minimal_parsed(),
                "analysis": malformed_analysis,
                "change_request": "调整数据口径",
                "lineage": None,
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("数据口径/取数逻辑变更", data["change_types"])
        self.assertTrue(any("需要人工确认口径" in item for item in data["review_points"]))

    def test_change_impact_tolerates_null_analysis(self):
        client = TestClient(app)

        response = client.post(
            "/api/change-impact",
            json={
                "parsed": minimal_parsed(),
                "analysis": None,
                "change_request": "新增展示字段",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("展示字段/布局变更", response.json()["change_types"])

    def test_change_impact_covers_sql_formula_and_writeback(self):
        client = TestClient(app)
        parsed = minimal_parsed()
        parsed["datasets"][0]["type"] = "DBTableData"
        parsed["datasets"][0]["sql"] = "select region, amount from sales where region = ${region}"
        parsed["datasets"][0]["sql_params"] = ["region"]
        parsed["writeback_config"] = {
            "db_connection": "demo",
            "table": "sales_submit",
            "key_columns": ["id"],
            "column_mappings": [{"db_column": "amount", "param": "amount"}],
        }

        sql_response = client.post(
            "/api/change-impact",
            json={"parsed": parsed, "analysis": minimal_analysis(), "change_request": "调整 SQL where 取数范围"},
        )
        formula_response = client.post(
            "/api/change-impact",
            json={"parsed": parsed, "analysis": minimal_analysis(), "change_request": "调整合计公式"},
        )
        writeback_response = client.post(
            "/api/change-impact",
            json={"parsed": parsed, "analysis": minimal_analysis(), "change_request": "修改填报提交字段映射"},
        )

        self.assertEqual(sql_response.status_code, 200)
        self.assertEqual(formula_response.status_code, 200)
        self.assertEqual(writeback_response.status_code, 200)
        self.assertTrue(sql_response.json()["affected"]["sql"])
        self.assertTrue(formula_response.json()["affected"]["formulas"])
        self.assertTrue(writeback_response.json()["affected"]["writeback"])


if __name__ == "__main__":
    unittest.main()
