"""Create canonical CSV/audit from the downloaded UCI .xls or .xlsx workbook."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SOURCES = [
    DATA_DIR / "default of credit card clients.xls",
    DATA_DIR / "default_of_credit_card_clients.xlsx",
]
OUTPUT = DATA_DIR / "credit_card_default_clean.csv"
TARGET = "default payment next month"

def main():
    source = next((p for p in SOURCES if p.exists()), None)
    if source is None:
        raise FileNotFoundError(
            "Download the UCI workbook and save it in data/ as "
            "'default of credit card clients.xls' or 'default_of_credit_card_clients.xlsx'."
        )
    df = pd.read_excel(source, sheet_name="Data", header=1)
    df.columns = df.columns.astype(str).str.strip()
    if TARGET not in df.columns or "ID" not in df.columns:
        raise ValueError(f"Required fields missing; actual columns: {df.columns.tolist()}")
    if df[TARGET].isna().any() or not set(df[TARGET].dropna().unique()).issubset({0, 1}):
        raise ValueError("Target must contain only 0/1 and no missing values.")
    df.to_csv(OUTPUT, index=False)
    audit = {
        "source_file": source.name, "sheet": "Data",
        "rows": int(len(df)), "columns": int(df.shape[1]),
        "predictor_count": int(df.shape[1] - 2),
        "missing_cells": int(df.isna().sum().sum()),
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "unique_ids": int(df["ID"].nunique()),
        "target": TARGET,
        "target_counts": {str(int(k)): int(v) for k, v in df[TARGET].value_counts().sort_index().items()},
        "target_pct": {str(int(k)): round(float(v * 100), 2) for k, v in df[TARGET].value_counts(normalize=True).sort_index().items()},
    }
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "dataset_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))
    print(f"Saved: {OUTPUT}")

if __name__ == "__main__":
    main()
