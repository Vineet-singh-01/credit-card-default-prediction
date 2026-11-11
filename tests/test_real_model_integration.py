"""Integration smoke test for the real repository model artifact.

This test is skipped in a source-only checkout that does not include the
large .joblib file. In the GitHub Actions workflow and merged repository, the
artifact is expected to exist and the test exercises the actual saved model.
"""

from __future__ import annotations

import pytest

from backend import main


pytestmark = pytest.mark.skipif(
    not main.MODEL_PATH.exists(),
    reason="Saved model artifact is not present in this source-only workspace.",
)


def _profile(**overrides):
    values = {
        "LIMIT_BAL": 200_000,
        "SEX": 2,
        "EDUCATION": 2,
        "MARRIAGE": 2,
        "AGE": 35,
        "PAY_0": 0,
        "PAY_2": 0,
        "PAY_3": 0,
        "PAY_4": 0,
        "PAY_5": 0,
        "PAY_6": 0,
        "BILL_AMT1": 50_000,
        "BILL_AMT2": 48_000,
        "BILL_AMT3": 45_000,
        "BILL_AMT4": 42_000,
        "BILL_AMT5": 40_000,
        "BILL_AMT6": 38_000,
        "PAY_AMT1": 5_000,
        "PAY_AMT2": 5_000,
        "PAY_AMT3": 4_500,
        "PAY_AMT4": 4_000,
        "PAY_AMT5": 4_000,
        "PAY_AMT6": 4_000,
    }
    values.update(overrides)
    return values


def test_real_saved_pipeline_scores_three_distinct_synthetic_profiles():
    # Clear cached values so the test validates the artifacts present in this
    # checkout rather than values cached by another test.
    main.load_metadata.cache_clear()
    main.load_model.cache_clear()

    profiles = [
        _profile(
            LIMIT_BAL=500_000, EDUCATION=1, AGE=38,
            PAY_0=-1, PAY_2=-1, PAY_3=-1, PAY_4=-1, PAY_5=-1, PAY_6=-1,
            BILL_AMT1=24_000, BILL_AMT2=22_000, BILL_AMT3=21_000,
            BILL_AMT4=20_000, BILL_AMT5=19_000, BILL_AMT6=18_000,
            PAY_AMT1=25_000, PAY_AMT2=23_000, PAY_AMT3=22_000,
            PAY_AMT4=20_000, PAY_AMT5=19_000, PAY_AMT6=18_000,
        ),
        _profile(
            LIMIT_BAL=50_000, SEX=1, EDUCATION=3, MARRIAGE=1, AGE=29,
            PAY_0=2, PAY_2=2, PAY_3=1, PAY_4=1, PAY_5=0, PAY_6=0,
            BILL_AMT1=48_000, BILL_AMT2=46_000, BILL_AMT3=44_000,
            BILL_AMT4=42_000, BILL_AMT5=40_000, BILL_AMT6=38_000,
            PAY_AMT1=1_000, PAY_AMT2=1_000, PAY_AMT3=1_000,
            PAY_AMT4=1_500, PAY_AMT5=2_000, PAY_AMT6=2_000,
        ),
        _profile(
            LIMIT_BAL=150_000, AGE=42, PAY_0=1, PAY_2=0, PAY_3=-1,
            PAY_4=0, PAY_5=-1, PAY_6=0,
            BILL_AMT1=82_000, BILL_AMT2=77_000, BILL_AMT3=74_000,
            BILL_AMT4=68_000, BILL_AMT5=63_000, BILL_AMT6=59_000,
            PAY_AMT1=6_000, PAY_AMT2=5_000, PAY_AMT3=7_000,
            PAY_AMT4=5_000, PAY_AMT5=4_000, PAY_AMT6=4_000,
        ),
    ]

    results = [main.predict_profile(profile) for profile in profiles]
    scores = [result["score"] for result in results]

    assert all(0.0 <= score <= 1.0 for score in scores)
    assert len({round(score, 8) for score in scores}) == 3
    assert all(result["model_name"] == "Random Forest" for result in results)
    assert all(result["score_note"].startswith("Uncalibrated") for result in results)
    assert all(result["diagnostics"]["months_reviewed"] == 6 for result in results)


def test_real_prediction_api_and_sqlite_history(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    main.load_metadata.cache_clear()
    main.load_model.cache_clear()
    monkeypatch.setattr(main, "HISTORY_DIR", tmp_path)
    monkeypatch.setattr(main, "HISTORY_DB", tmp_path / "real-model-history.sqlite3")

    with TestClient(main.app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["model_available"] is True

        response = client.post(
            "/api/predictions",
            json=_profile(PAY_0=2, PAY_2=1, BILL_AMT1=90_000),
        )
        assert response.status_code == 200, response.text
        result = response.json()
        assert 0.0 <= result["score"] <= 1.0
        assert result["model_name"] == "Random Forest"
        assert result["inputs"]["PAY_0"] == 2

        history = client.get("/api/predictions/history")
        assert history.status_code == 200
        assert history.json()["total"] == 1
        assert history.json()["items"][0]["id"] == result["id"]

        detail = client.get(f"/api/predictions/{result['id']}")
        assert detail.status_code == 200
        assert detail.json()["inputs"]["PAY_0"] == 2

    main.load_metadata.cache_clear()
    main.load_model.cache_clear()
