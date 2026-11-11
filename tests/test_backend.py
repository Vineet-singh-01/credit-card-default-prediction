import unittest
from unittest.mock import patch

import numpy as np

from backend import main


class DummyPipeline:
    classes_ = np.array([0, 1])

    def predict_proba(self, values):
        assert values.shape == (1, 23)
        return np.array([[0.81, 0.19]])


class BackendCoreTests(unittest.TestCase):
    def test_input_order_and_categorical_conversion_match_metadata(self):
        features = ["SEX", "LIMIT_BAL", "EDUCATION", "PAY_0"]
        values = {"SEX": 2, "LIMIT_BAL": 250000, "EDUCATION": 1, "PAY_0": -1}
        payload = main.build_model_input(
            values,
            {"feature_names": features, "categorical_features": ["SEX", "EDUCATION"]},
        )
        self.assertEqual(payload.tolist()[0], ["2", 250000.0, "1", -1.0])

    def test_score_bands_are_exhaustive_and_ordered(self):
        self.assertEqual(main.score_category(0.05)[0], "Lower score band")
        self.assertEqual(main.score_category(0.20)[0], "Watchlist score band")
        self.assertEqual(main.score_category(0.35)[0], "Elevated score band")
        self.assertEqual(main.score_category(0.50)[0], "High review-priority band")

    def test_grouped_audit_supports_count_and_n_schemas(self):
        audit = {"groups": {
            "0": {"count": 100, "defaults": 12, "rate_pct": 12.0},
            "1": {"n": 200, "defaults": 50, "rate_pct": 25.0},
        }}
        rows = main.grouped_rate(audit, "groups")
        self.assertEqual([row["customers"] for row in rows], [100, 200])

    def test_profile_diagnostics_are_descriptive(self):
        from backend.main import CreditProfile
        sample = {
            "LIMIT_BAL": 100000, "SEX": 2, "EDUCATION": 2, "MARRIAGE": 2, "AGE": 35,
            "PAY_0": 2, "PAY_2": 0, "PAY_3": -1, "PAY_4": 1, "PAY_5": 0, "PAY_6": -1,
            "BILL_AMT1": 50000, "BILL_AMT2": 45000, "BILL_AMT3": 40000,
            "BILL_AMT4": 35000, "BILL_AMT5": 30000, "BILL_AMT6": 25000,
            "PAY_AMT1": 10000, "PAY_AMT2": 8000, "PAY_AMT3": 7000,
            "PAY_AMT4": 6000, "PAY_AMT5": 5000, "PAY_AMT6": 4000,
        }
        validated = CreditProfile.model_validate(sample).model_dump()
        diagnostics = main.profile_diagnostics(validated)
        self.assertEqual(diagnostics["months_with_delay_code"], 2)
        self.assertEqual(diagnostics["credit_limit_utilisation_pct"], 50.0)
        self.assertEqual(diagnostics["latest_payment_to_bill_pct"], 20.0)

    def test_prediction_uses_class_one_score_and_saved_threshold(self):
        from backend.main import CreditProfile
        sample = {
            "LIMIT_BAL": 100000, "SEX": 2, "EDUCATION": 2, "MARRIAGE": 2, "AGE": 35,
            "PAY_0": 0, "PAY_2": 0, "PAY_3": 0, "PAY_4": 0, "PAY_5": 0, "PAY_6": 0,
            "BILL_AMT1": 50000, "BILL_AMT2": 45000, "BILL_AMT3": 40000,
            "BILL_AMT4": 35000, "BILL_AMT5": 30000, "BILL_AMT6": 25000,
            "PAY_AMT1": 10000, "PAY_AMT2": 8000, "PAY_AMT3": 7000,
            "PAY_AMT4": 6000, "PAY_AMT5": 5000, "PAY_AMT6": 4000,
        }
        profile = CreditProfile.model_validate(sample).model_dump()
        metadata = {
            "feature_names": list(sample.keys()),
            "categorical_features": ["SEX", "EDUCATION", "MARRIAGE"],
            "threshold": 0.5,
            "model_name": "Test pipeline",
        }
        with patch.object(main, "load_metadata", return_value=metadata), patch.object(main, "load_model", return_value=DummyPipeline()):
            result = main.predict_profile(profile)
        self.assertAlmostEqual(result["score"], 0.19)
        self.assertFalse(result["technical_prediction"])
        self.assertEqual(result["model_name"], "Test pipeline")


if __name__ == "__main__":
    unittest.main()


def test_prediction_api_persists_real_response_and_history(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    sample = {
        "LIMIT_BAL": 100000, "SEX": 2, "EDUCATION": 2, "MARRIAGE": 2, "AGE": 35,
        "PAY_0": 0, "PAY_2": 0, "PAY_3": 0, "PAY_4": 0, "PAY_5": 0, "PAY_6": 0,
        "BILL_AMT1": 50000, "BILL_AMT2": 45000, "BILL_AMT3": 40000,
        "BILL_AMT4": 35000, "BILL_AMT5": 30000, "BILL_AMT6": 25000,
        "PAY_AMT1": 10000, "PAY_AMT2": 8000, "PAY_AMT3": 7000,
        "PAY_AMT4": 6000, "PAY_AMT5": 5000, "PAY_AMT6": 4000,
    }
    metadata = {
        "feature_names": list(sample.keys()),
        "categorical_features": ["SEX", "EDUCATION", "MARRIAGE"],
        "threshold": 0.5,
        "model_name": "Test pipeline",
    }
    monkeypatch.setattr(main, "HISTORY_DIR", tmp_path)
    monkeypatch.setattr(main, "HISTORY_DB", tmp_path / "history.sqlite3")
    monkeypatch.setattr(main, "load_metadata", lambda: metadata)
    monkeypatch.setattr(main, "load_model", lambda: DummyPipeline())

    with TestClient(main.app) as client:
        response = client.post("/api/predictions", json=sample)
        assert response.status_code == 200, response.text
        created = response.json()
        assert created["score"] == 0.19
        assert created["technical_prediction"] is False
        assert created["inputs"]["EDUCATION"] == 2

        history = client.get("/api/predictions/history")
        assert history.status_code == 200
        assert history.json()["total"] == 1
        assert history.json()["items"][0]["id"] == created["id"]

        detail = client.get(f"/api/predictions/{created['id']}")
        assert detail.status_code == 200
        assert detail.json()["inputs"]["MARRIAGE"] == 2

        cleared = client.delete("/api/predictions/history")
        assert cleared.status_code == 200
        assert client.get("/api/predictions/history").json()["total"] == 0
