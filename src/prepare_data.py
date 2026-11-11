"""Create the canonical CSV and audit from the UCI workbook."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "default_of_credit_card_clients.xlsx"
OUTPUT = ROOT / "data" / "credit_card_default_clean.csv"
TARGET = "default payment next month"

def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Save the UCI workbook as {SOURCE.name} in {SOURCE.parent}")
    df = pd.read_excel(SOURCE, sheet_name=0, header=1)
    df.columns = df.columns.astype(str).str.strip()
    if TARGET not in df.columns or "ID" not in df.columns:
        raise ValueError(f"Required fields not found. Actual columns: {df.columns.tolist()}")
    if df[TARGET].isna().any() or not set(df[TARGET].dropna().unique()).issubset({0,1}):
        raise ValueError("Target must contain only 0/1 and no missing values.")
    df.to_csv(OUTPUT, index=False)
    audit = {
        "rows": int(len(df)), "columns": int(df.shape[1]),
        "predictor_count": int(df.shape[1]-2),
        "missing_cells": int(df.isna().sum().sum()),
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "unique_ids": int(df.ID.nunique()),
        "target_counts": {str(int(k)):int(v) for k,v in df[TARGET].value_counts().sort_index().items()},
        "target_pct": {str(int(k)):round(float(v*100),2) for k,v in df[TARGET].value_counts(normalize=True).sort_index().items()}
    }
    (ROOT/"reports").mkdir(exist_ok=True)
    (ROOT/"reports"/"dataset_audit.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
    print(json.dumps(audit,indent=2))
    print(f"Saved: {OUTPUT}")

if __name__ == "__main__":
    main()
