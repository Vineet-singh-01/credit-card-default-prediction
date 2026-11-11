from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
AUDIT_PATH = ROOT / "reports" / "dataset_audit.json"
METRICS_PATH = ROOT / "reports" / "final_test_metrics.json"
MODEL_PATH = ROOT / "models" / "credit_default_pipeline.joblib"
METADATA_PATH = ROOT / "models" / "model_metadata.json"

st.set_page_config(page_title="CreditRisk Analytics", page_icon="📊", layout="wide")
st.markdown("""
<style>
.stApp{background:#F4F7FA}
[data-testid="stSidebar"]{background:#10243A}
[data-testid="stSidebar"] *{color:#F4F7FA !important}
.hero{background:linear-gradient(110deg,#10243A,#174B5A);color:white;padding:1.4rem 1.6rem;border-radius:16px;margin-bottom:1rem}
.hero h1{color:white;margin:0}.hero p{color:#D8E7EC;margin:.4rem 0 0}
div[data-testid="stMetric"]{background:white;border:1px solid #E2E8F0;padding:12px;border-radius:12px}
</style>
""", unsafe_allow_html=True)

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

audit = read_json(AUDIT_PATH)
metrics = read_json(METRICS_PATH)

with st.sidebar:
    st.markdown("## CREDITRISK")
    st.caption("Business analytics decision support")
    page = st.radio("NAVIGATION", ["Business Overview", "Data Insights", "Prediction"])
    st.divider()
    st.caption("UCI historical data · Taiwan · 2005")

st.markdown('<div class="hero"><h1>CreditRisk Analytics</h1><p>Next-month credit-card default risk · Machine-learning decision support</p></div>', unsafe_allow_html=True)

if page == "Business Overview":
    st.subheader("Business Overview")
    st.write("This academic prototype estimates whether an existing credit-card customer may default on the next month's payment using historical credit-limit, repayment, bill and payment information.")
    if audit and metrics:
        a,b,c,d = st.columns(4)
        a.metric("Customer records", f"{audit['rows']:,}")
        b.metric("Predictor variables", str(audit["predictor_count"]))
        c.metric("Observed default rate", f"{audit['target_pct']['1']:.2f}%")
        d.metric("Held-out test accuracy", f"{metrics['accuracy']:.1%}")
    st.markdown("### Decision supported")
    st.write("Prioritise accounts for qualified human review and suitable customer outreach. A prediction is an early-warning signal, not an automatic credit approval, rejection, collection action or adverse decision.")
    st.info("The source data describe Taiwanese credit-card customers in 2005. Results are not validated for current Indian credit portfolios.")

elif page == "Data Insights":
    st.subheader("Data Insights")
    if not audit or not metrics:
        st.warning("Dataset audit or test-metric files are missing.")
    else:
        a,b,c = st.columns(3)
        a.metric("No default", f"{audit['target_counts']['0']:,}", f"{audit['target_pct']['0']:.2f}%")
        b.metric("Default", f"{audit['target_counts']['1']:,}", f"{audit['target_pct']['1']:.2f}%")
        c.metric("Missing cells", f"{audit['missing_cells']:,}")
        st.caption(f"{audit['rows']:,} records · {audit['columns']} original columns · {audit['exact_duplicate_rows']} duplicate rows · {audit['unique_ids']:,} unique IDs")
        left,right = st.columns(2)
        with left:
            st.markdown("#### Observed default rate by PAY_0")
            pay = pd.DataFrame([{"PAY_0":int(k),"Default rate (%)":v["rate_pct"]} for k,v in audit["default_rate_by_PAY_0"].items()]).sort_values("PAY_0").set_index("PAY_0")
            st.bar_chart(pay)
            st.markdown("#### Default rate by credit-limit band")
            lim = pd.DataFrame.from_dict(audit["default_rate_by_limit_band"], orient="index")
            st.bar_chart(lim["rate_pct"].rename("Default rate (%)"))
        with right:
            st.markdown("#### Default rate by age band")
            age = pd.DataFrame.from_dict(audit["default_rate_by_age_band"], orient="index")
            st.bar_chart(age["rate_pct"].rename("Default rate (%)"))
            comp = read_json(ROOT / "reports" / "validation_model_comparison.json")
            if comp:
                st.markdown("#### Validation model comparison")
                st.dataframe(pd.DataFrame(comp).set_index("model"), use_container_width=True)
        st.markdown("### Held-out test metrics")
        x,y,z,w = st.columns(4)
        x.metric("Precision – default", f"{metrics['precision_default']:.1%}")
        y.metric("Recall – default", f"{metrics['recall_default']:.1%}")
        z.metric("F1 – default", f"{metrics['f1_default']:.3f}")
        w.metric("ROC-AUC", f"{metrics['roc_auc']:.3f}")
        st.warning("Observed patterns are associations, not causes. Demographic features are present; fairness review and probability calibration remain incomplete.")

else:
    st.subheader("Customer Risk Assessment")
    st.warning("Academic demonstration only. The model score is not separately calibrated and must not drive automated decisions.")
    if not MODEL_PATH.exists() or not METADATA_PATH.exists():
        st.info("Prediction is disabled in this GitHub version. Add the trusted models/credit_default_pipeline.joblib artifact from the locally generated project package, then test it before enabling prediction.")
    else:
        import joblib
        metadata = read_json(METADATA_PATH)
        @st.cache_resource
        def load_model():
            return joblib.load(MODEL_PATH)
        model = load_model()
        categorical = set(metadata["categorical_features"])
        pay_codes = [-2,-1,0,1,2,3,4,5,6,7,8]
        values = {}
        with st.form("customer_risk_form"):
            st.markdown("#### Customer and credit profile")
            c1,c2,c3 = st.columns(3)
            with c1:
                values["LIMIT_BAL"] = st.number_input("Credit limit (NT$)", min_value=0, max_value=2_000_000, value=200_000, step=10_000)
                values["SEX"] = st.selectbox("SEX code", [1,2], index=1)
            with c2:
                values["EDUCATION"] = st.selectbox("EDUCATION code", [0,1,2,3,4,5,6], index=2)
                values["MARRIAGE"] = st.selectbox("MARRIAGE code", [0,1,2,3], index=2)
            with c3:
                values["AGE"] = st.number_input("Age (years)", min_value=18, max_value=100, value=35)
            st.markdown("#### Repayment status codes")
            cols = st.columns(3)
            for i,col in enumerate(["PAY_0","PAY_2","PAY_3","PAY_4","PAY_5","PAY_6"]):
                with cols[i%3]:
                    values[col] = st.selectbox(col, pay_codes, index=2)
            st.markdown("#### Bill amounts (NT$)")
            cols = st.columns(3)
            for i,col in enumerate([f"BILL_AMT{k}" for k in range(1,7)]):
                with cols[i%3]:
                    values[col] = st.number_input(col, value=50000 if i == 0 else 40000, step=1000)
            st.markdown("#### Previous payment amounts (NT$)")
            cols = st.columns(3)
            for i,col in enumerate([f"PAY_AMT{k}" for k in range(1,7)]):
                with cols[i%3]:
                    values[col] = st.number_input(col, min_value=0, value=4000, step=500)
            submitted = st.form_submit_button("Estimate model score", type="primary", use_container_width=True)
        if submitted:
            ordered = [str(int(values[f])) if f in categorical else float(values[f]) for f in metadata["feature_names"]]
            score = float(model.predict_proba(np.asarray([ordered], dtype=object))[0,1])
            predicted = int(score >= float(metadata["threshold"]))
            x,y = st.columns(2)
            x.metric("Uncalibrated model score", f"{score:.1%}")
            y.metric("Predicted class at current threshold", "Default flag" if predicted else "No default flag")
            if predicted:
                st.error("Flag for qualified human review and suitable customer outreach.")
            else:
                st.success("No default flag at the current threshold. This is not a guarantee of repayment.")
            st.caption("The 0.50 cutoff is a technical default, not a bank-approved business cutoff.")
