from __future__ import annotations

import csv
import json
import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "credit_default_pipeline.joblib"
METADATA_PATH = ROOT / "models" / "model_metadata.json"
AUDIT_PATH = ROOT / "reports" / "dataset_audit.json"
METRICS_PATH = ROOT / "reports" / "final_test_metrics.json"
VALIDATION_PATH = ROOT / "reports" / "validation_model_comparison.json"
THRESHOLD_PATH = ROOT / "reports" / "threshold_tradeoff_validation.csv"
HISTORY_DIR = ROOT / "backend" / "data"
HISTORY_DB = HISTORY_DIR / "prediction_history.sqlite3"

SEX_OPTIONS = {1: "Male", 2: "Female"}
EDUCATION_OPTIONS = {
    0: "Not reported / unknown",
    1: "Graduate school",
    2: "University",
    3: "High school",
    4: "Other",
    5: "Unknown (source code 5)",
    6: "Unknown (source code 6)",
}
MARRIAGE_OPTIONS = {
    0: "Not reported / unknown",
    1: "Married",
    2: "Single / unmarried",
    3: "Other",
}
PAY_OPTIONS = {
    -2: "No consumption recorded",
    -1: "Paid duly / on time",
    0: "Revolving credit (no recorded delay)",
    1: "Payment delayed by 1 month",
    2: "Payment delayed by 2 months",
    3: "Payment delayed by 3 months",
    4: "Payment delayed by 4 months",
    5: "Payment delayed by 5 months",
    6: "Payment delayed by 6 months",
    7: "Payment delayed by 7 months",
    8: "Payment delayed by 8 months",
}
MONTHS = {
    1: "September 2005", 2: "August 2005", 3: "July 2005",
    4: "June 2005", 5: "May 2005", 6: "April 2005",
}

class CreditProfile(BaseModel):
    """Validated single-customer input; field names mirror model metadata."""
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    LIMIT_BAL: float = Field(ge=0, le=2_000_000)
    SEX: int = Field(ge=1, le=2)
    EDUCATION: int = Field(ge=0, le=6)
    MARRIAGE: int = Field(ge=0, le=3)
    AGE: int = Field(ge=18, le=100)
    PAY_0: int = Field(ge=-2, le=8)
    PAY_2: int = Field(ge=-2, le=8)
    PAY_3: int = Field(ge=-2, le=8)
    PAY_4: int = Field(ge=-2, le=8)
    PAY_5: int = Field(ge=-2, le=8)
    PAY_6: int = Field(ge=-2, le=8)
    BILL_AMT1: float = Field(ge=-1_000_000, le=5_000_000)
    BILL_AMT2: float = Field(ge=-1_000_000, le=5_000_000)
    BILL_AMT3: float = Field(ge=-1_000_000, le=5_000_000)
    BILL_AMT4: float = Field(ge=-1_000_000, le=5_000_000)
    BILL_AMT5: float = Field(ge=-1_000_000, le=5_000_000)
    BILL_AMT6: float = Field(ge=-1_000_000, le=5_000_000)
    PAY_AMT1: float = Field(ge=0, le=5_000_000)
    PAY_AMT2: float = Field(ge=0, le=5_000_000)
    PAY_AMT3: float = Field(ge=0, le=5_000_000)
    PAY_AMT4: float = Field(ge=0, le=5_000_000)
    PAY_AMT5: float = Field(ge=0, le=5_000_000)
    PAY_AMT6: float = Field(ge=0, le=5_000_000)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {} if default is None else default


def read_csv_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        clean: list[dict[str, Any]] = []
        for row in rows:
            item: dict[str, Any] = {}
            for key, value in row.items():
                if value is None:
                    continue
                try:
                    item[key] = float(value)
                except (TypeError, ValueError):
                    item[key] = value
            clean.append(item)
        return clean
    except OSError:
        return []


@lru_cache(maxsize=1)
def load_metadata() -> dict[str, Any]:
    payload = read_json(METADATA_PATH)
    return payload if isinstance(payload, dict) else {}

@lru_cache(maxsize=1)
def load_audit() -> dict[str, Any]:
    payload = read_json(AUDIT_PATH)
    return payload if isinstance(payload, dict) else {}

@lru_cache(maxsize=1)
def load_metrics() -> dict[str, Any]:
    payload = read_json(METRICS_PATH)
    return payload if isinstance(payload, dict) else {}

@lru_cache(maxsize=1)
def load_model() -> Any:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Trained model not found at models/credit_default_pipeline.joblib. "
            "Copy the existing model artifact from the original repository; do not retrain for this UI upgrade."
        )
    return joblib.load(MODEL_PATH)


@contextmanager
def db_connection() -> Iterator[sqlite3.Connection]:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(HISTORY_DB, timeout=15)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_history_db() -> None:
    with db_connection() as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                score REAL NOT NULL,
                category TEXT NOT NULL,
                technical_prediction INTEGER NOT NULL,
                threshold REAL NOT NULL,
                inputs_json TEXT NOT NULL,
                diagnostics_json TEXT NOT NULL
            )"""
        )


def count_predictions() -> int:
    init_history_db()
    with db_connection() as connection:
        return int(connection.execute("SELECT COUNT(*) FROM predictions").fetchone()[0])


def serialize_history_row(row: sqlite3.Row, include_inputs: bool = False) -> dict[str, Any]:
    result = {
        "id": row["id"],
        "created_at": row["created_at"],
        "score": row["score"],
        "category": row["category"],
        "technical_prediction": bool(row["technical_prediction"]),
        "threshold": row["threshold"],
        "diagnostics": json.loads(row["diagnostics_json"]),
    }
    if include_inputs:
        result["inputs"] = json.loads(row["inputs_json"])
    return result


def score_category(score: float) -> tuple[str, str, str]:
    # Interface-only bands; not validated banking grades or calibrated PD bands.
    if score < 0.20:
        return "Lower score band", "Routine monitoring", "low"
    if score < 0.35:
        return "Watchlist score band", "Routine account review", "watch"
    if score < 0.50:
        return "Elevated score band", "Prioritised manual review", "elevated"
    return "High review-priority band", "Timely authorised review", "high"


def profile_diagnostics(values: dict[str, int | float]) -> dict[str, Any]:
    pay_codes = [int(values[f"PAY_{suffix}"]) for suffix in ("0", "2", "3", "4", "5", "6")]
    delayed_months = sum(code >= 1 for code in pay_codes)
    limit = float(values["LIMIT_BAL"])
    bill = float(values["BILL_AMT1"])
    payment = float(values["PAY_AMT1"])
    utilisation = (bill / limit * 100) if limit > 0 else None
    payment_ratio = (payment / bill * 100) if bill > 0 else None
    return {
        "months_with_delay_code": delayed_months,
        "months_reviewed": 6,
        "latest_repayment_status": PAY_OPTIONS.get(int(values["PAY_0"]), "Other / unknown"),
        "credit_limit_utilisation_pct": round(utilisation, 1) if utilisation is not None else None,
        "latest_payment_to_bill_pct": round(payment_ratio, 1) if payment_ratio is not None else None,
    }


def build_model_input(values: dict[str, int | float], metadata: dict[str, Any]) -> np.ndarray:
    feature_names = metadata.get("feature_names")
    categorical_features = set(metadata.get("categorical_features", []))
    if not isinstance(feature_names, list) or not feature_names:
        raise ValueError("models/model_metadata.json has no feature_names list")
    missing = [feature for feature in feature_names if feature not in values]
    if missing:
        raise ValueError(f"Missing model inputs: {', '.join(missing)}")
    ordered: list[Any] = []
    for feature in feature_names:
        value = values[feature]
        ordered.append(str(int(value)) if feature in categorical_features else float(value))
    return np.asarray([ordered], dtype=object)


def predict_profile(values: dict[str, int | float]) -> dict[str, Any]:
    metadata = load_metadata()
    if not metadata:
        raise FileNotFoundError("Model metadata is missing at models/model_metadata.json")
    model = load_model()
    model_input = build_model_input(values, metadata)
    if not hasattr(model, "predict_proba"):
        raise TypeError("The saved pipeline does not expose predict_proba().")
    probabilities = np.asarray(model.predict_proba(model_input))[0]
    classes = list(getattr(model, "classes_", [0, 1]))
    try:
        positive_index = classes.index(1)
    except ValueError as exc:
        raise ValueError("Model classes do not contain target class 1") from exc
    if positive_index >= len(probabilities):
        raise ValueError("Model did not return a class-1 score")
    score = float(np.clip(probabilities[positive_index], 0.0, 1.0))
    threshold = float(metadata.get("threshold", 0.50))
    category, guidance, category_key = score_category(score)
    diagnostics = profile_diagnostics(values)
    return {
        "score": score,
        "category": category,
        "category_key": category_key,
        "guidance": guidance,
        "technical_threshold": threshold,
        "technical_prediction": bool(score >= threshold),
        "diagnostics": diagnostics,
        "model_name": metadata.get("model_name", "Saved model"),
        "score_note": "Uncalibrated model score; not a verified probability of default.",
        "threshold_note": "The threshold is the technical cutoff stored with the model, not an approved business policy.",
    }


def grouped_rate(audit: dict[str, Any], key: str, label_map: dict[int, str] | None = None) -> list[dict[str, Any]]:
    groups = audit.get(key, {}) if isinstance(audit, dict) else {}
    if not isinstance(groups, dict):
        return []
    output: list[dict[str, Any]] = []
    for raw_key, details in groups.items():
        if not isinstance(details, dict) or "rate_pct" not in details:
            continue
        display = str(raw_key)
        if label_map is not None:
            try:
                display = label_map.get(int(raw_key), f"Other / code {raw_key}")
            except (TypeError, ValueError):
                pass
        output.append({
            "label": display,
            "code": str(raw_key),
            "default_rate_pct": float(details.get("rate_pct", 0)),
            "customers": int(details.get("count", details.get("n", 0))),
            "defaults": int(details.get("defaults", 0)),
        })
    return output


def build_insights_payload() -> dict[str, Any]:
    audit = load_audit()
    importance = audit.get("permutation_importance_validation", [])
    return {
        "dataset": {
            "rows": audit.get("rows"),
            "columns": audit.get("columns"),
            "predictor_count": audit.get("predictor_count"),
            "missing_cells": audit.get("missing_cells"),
            "duplicate_rows": audit.get("exact_duplicate_rows"),
            "unique_ids": audit.get("unique_ids"),
            "target_counts": audit.get("target_counts", {}),
            "target_pct": audit.get("target_pct", {}),
        },
        "repayment": grouped_rate(audit, "default_rate_by_PAY_0", PAY_OPTIONS),
        "credit_limit": grouped_rate(audit, "default_rate_by_limit_band"),
        "age": grouped_rate(audit, "default_rate_by_age_band"),
        "education": grouped_rate(audit, "default_rate_by_education", EDUCATION_OPTIONS),
        "permutation_importance": [
            {"feature": row.get("feature"), "mean_ap_drop": row.get("mean_ap_drop"), "std": row.get("std")}
            for row in importance if isinstance(row, dict)
        ] if isinstance(importance, list) else [],
    }


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_history_db()
    yield


app = FastAPI(
    title="CreditRisk Analytics API",
    description="REST API for the existing CreditRisk Analytics Random Forest model.",
    version="1.0.0",
    lifespan=lifespan,
)
allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:4173").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)

@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok" if MODEL_PATH.exists() and METADATA_PATH.exists() else "degraded",
        "model_available": MODEL_PATH.exists(),
        "metadata_available": METADATA_PATH.exists(),
        "dataset_audit_available": AUDIT_PATH.exists(),
        "metrics_available": METRICS_PATH.exists(),
        "model_name": load_metadata().get("model_name", "Not loaded"),
    }

@app.get("/api/config")
def config() -> dict[str, Any]:
    return {
        "categories": {
            "gender": [{"value": k, "label": v} for k, v in SEX_OPTIONS.items()],
            "education": [{"value": k, "label": v} for k, v in EDUCATION_OPTIONS.items()],
            "marital_status": [{"value": k, "label": v} for k, v in MARRIAGE_OPTIONS.items()],
            "repayment_status": [{"value": k, "label": v} for k, v in PAY_OPTIONS.items()],
        },
        "months": MONTHS,
    }

@app.get("/api/overview")
def overview() -> dict[str, Any]:
    audit, metrics = load_audit(), load_metrics()
    init_history_db()
    with db_connection() as connection:
        total = int(connection.execute("SELECT COUNT(*) FROM predictions").fetchone()[0])
        recent_rows = connection.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 6").fetchall()
    return {
        "project": "CreditRisk Analytics",
        "description": "Next-month credit-card default risk as human-review decision support.",
        "dataset": {
            "rows": audit.get("rows"),
            "predictors": audit.get("predictor_count"),
            "observed_default_rate": (audit.get("target_pct") or {}).get("1"),
            "no_default_count": (audit.get("target_counts") or {}).get("0"),
            "default_count": (audit.get("target_counts") or {}).get("1"),
        },
        "metrics": {
            "accuracy": metrics.get("accuracy"),
            "precision_default": metrics.get("precision_default"),
            "recall_default": metrics.get("recall_default"),
            "f1_default": metrics.get("f1_default"),
            "roc_auc": metrics.get("roc_auc"),
        },
        "model_name": load_metadata().get("model_name", "Not specified"),
        "predictions_performed": total,
        "recent_predictions": [serialize_history_row(row) for row in recent_rows],
    }

@app.get("/api/insights")
def insights() -> dict[str, Any]:
    return build_insights_payload()

@app.get("/api/performance")
def performance() -> dict[str, Any]:
    metrics = load_metrics()
    comparisons = read_json(VALIDATION_PATH, default=[])
    threshold_rows = read_csv_records(THRESHOLD_PATH)
    if not metrics:
        raise HTTPException(status_code=503, detail="Held-out test metrics are missing from reports/final_test_metrics.json")
    tn, fp = int(metrics.get("tn", 0)), int(metrics.get("fp", 0))
    fn, tp = int(metrics.get("fn", 0)), int(metrics.get("tp", 0))
    return {
        "metrics": metrics,
        "confusion_matrix": {"labels": ["No default", "Default"], "rows": [[tn, fp], [fn, tp]]},
        "validation_comparison": comparisons if isinstance(comparisons, list) else [],
        "threshold_tradeoff": threshold_rows,
        "metric_explanations": {
            "accuracy": "Share of all test records classified correctly. It can hide missed defaults when classes are imbalanced.",
            "precision_default": "Among accounts flagged as default, the share that actually defaulted in the held-out test set.",
            "recall_default": "Among actual defaults in the held-out test set, the share the model identified.",
            "f1_default": "Harmonic mean of default precision and recall; balances the two.",
            "roc_auc": "How well the model ranks default cases above non-default cases across possible thresholds.",
            "average_precision": "Summarises the precision-recall curve; useful when the positive class is less common.",
            "brier_score": "Mean squared error of the model's probability-like scores against the binary outcome. Lower is better, but this is not a calibration certificate.",
        },
    }

@app.post("/api/predictions")
def create_prediction(profile: CreditProfile) -> dict[str, Any]:
    values = profile.model_dump()
    try:
        result = predict_profile(values)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (ValueError, TypeError, OSError) as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with db_connection() as connection:
            cursor = connection.execute(
                """INSERT INTO predictions
                   (created_at, score, category, technical_prediction, threshold, inputs_json, diagnostics_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    created_at,
                    result["score"],
                    result["category"],
                    int(result["technical_prediction"]),
                    result["technical_threshold"],
                    json.dumps(values, separators=(",", ":")),
                    json.dumps(result["diagnostics"], separators=(",", ":")),
                ),
            )
            prediction_id = int(cursor.lastrowid)
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="The prediction was calculated but could not be saved to history.") from exc
    return {"id": prediction_id, "created_at": created_at, **result, "inputs": values}

@app.get("/api/predictions/history")
def prediction_history(limit: int = Query(default=100, ge=1, le=500)) -> dict[str, Any]:
    init_history_db()
    with db_connection() as connection:
        rows = connection.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        total = int(connection.execute("SELECT COUNT(*) FROM predictions").fetchone()[0])
    return {"total": total, "items": [serialize_history_row(row) for row in rows]}

@app.get("/api/predictions/{prediction_id}")
def get_prediction(prediction_id: int) -> dict[str, Any]:
    init_history_db()
    with db_connection() as connection:
        row = connection.execute("SELECT * FROM predictions WHERE id = ?", (prediction_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Prediction was not found in this application's local history.")
    return serialize_history_row(row, include_inputs=True)

@app.delete("/api/predictions/history")
def clear_prediction_history() -> dict[str, Any]:
    init_history_db()
    with db_connection() as connection:
        connection.execute("DELETE FROM predictions")
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'predictions'")
    return {"deleted": True, "message": "Local prediction history cleared."}

@app.get("/api/metadata")
def metadata() -> dict[str, Any]:
    source = load_metadata()
    return {
        "model_name": source.get("model_name"),
        "target": source.get("target"),
        "feature_count": len(source.get("feature_names", [])),
        "feature_names": source.get("feature_names", []),
        "categorical_features": source.get("categorical_features", []),
        "threshold": source.get("threshold", 0.5),
        "probability_calibration": source.get("probability_calibration"),
    }
