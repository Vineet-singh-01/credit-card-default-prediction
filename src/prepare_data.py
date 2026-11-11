"""Create canonical CSV and enriched audit summaries from the UCI workbook."""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA_DIR=ROOT/"data"
SOURCES=[DATA_DIR/"default of credit card clients.xls",DATA_DIR/"default_of_credit_card_clients.xlsx"]
OUTPUT=DATA_DIR/"credit_card_default_clean.csv"
TARGET="default payment next month"

def rate_summary(frame,group_col):
    grouped=frame.groupby(group_col,observed=False)[TARGET].agg(["count","sum","mean"])
    out={}
    for key,row in grouped.iterrows():
        if pd.isna(key) or int(row["count"])==0: continue
        out[str(key)]={"count":int(row["count"]),"defaults":int(row["sum"]),"rate_pct":round(float(row["mean"]*100),2)}
    return out

def main():
    source=next((p for p in SOURCES if p.exists()),None)
    if source is None: raise FileNotFoundError("Place the UCI workbook in data/ using one of the documented filenames.")
    df=pd.read_excel(source,sheet_name="Data",header=1)
    df.columns=df.columns.astype(str).str.strip()
    if TARGET not in df.columns or "ID" not in df.columns: raise ValueError(f"Required fields missing: {df.columns.tolist()}")
    if df[TARGET].isna().any() or not set(df[TARGET].dropna().unique()).issubset({0,1}): raise ValueError("Target must contain only 0/1 and no missing values.")
    df.to_csv(OUTPUT,index=False)
    df["credit_limit_band"]=pd.cut(df["LIMIT_BAL"],[-1,50000,100000,200000,300000,float("inf")],labels=["<=50k","50k–100k","100k–200k","200k–300k",">300k"],include_lowest=True)
    df["age_band"]=pd.cut(df["AGE"],[0,25,35,45,55,100],labels=["18–25","26–35","36–45","46–55","56+"],include_lowest=True)
    audit={
      "source_file":source.name,"sheet":"Data","rows":int(len(df)),"columns":int(df.shape[1]-4),"predictor_count":int(df.shape[1]-4),
      "missing_cells":int(df.iloc[:,:-2].isna().sum().sum()),"exact_duplicate_rows":int(df.duplicated(subset=df.columns[:25]).sum()),
      "unique_ids":int(df["ID"].nunique()),"target":TARGET,
      "target_counts":{str(int(k)):int(v) for k,v in df[TARGET].value_counts().sort_index().items()},
      "target_pct":{str(int(k)):round(float(v*100),2) for k,v in df[TARGET].value_counts(normalize=True).sort_index().items()},
      "default_rate_by_PAY_0":rate_summary(df,"PAY_0"),
      "default_rate_by_limit_band":rate_summary(df.dropna(subset=["credit_limit_band"]),"credit_limit_band"),
      "default_rate_by_age_band":rate_summary(df.dropna(subset=["age_band"]),"age_band")
    }
    reports=ROOT/"reports";reports.mkdir(exist_ok=True)
    (reports/"dataset_audit.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False));print(f"Saved: {OUTPUT}")

if __name__=="__main__":main()
