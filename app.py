from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import streamlit as st


# -----------------------------------------------------------------------------
# Paths and application configuration
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "credit_default_pipeline.joblib"
METADATA_PATH = ROOT / "models" / "model_metadata.json"
AUDIT_PATH = ROOT / "reports" / "dataset_audit.json"
METRICS_PATH = ROOT / "reports" / "final_test_metrics.json"

st.set_page_config(
    page_title="CreditRisk Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#10243A"
NAVY_2 = "#173B52"
TEAL = "#0F8B8D"
BG = "#F4F7FA"
TEXT = "#183044"
MUTED = "#64748B"


# -----------------------------------------------------------------------------
# Dataset labels
# The labels are for the interface only. The original numeric codes are sent
# to the saved pipeline so the model receives the same representation as it
# received during training.
# -----------------------------------------------------------------------------
SEX_OPTIONS = {
    1: "Male",
    2: "Female",
}

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

MONTH_LABELS = {
    1: "September 2005",
    2: "August 2005",
    3: "July 2005",
    4: "June 2005",
    5: "May 2005",
    6: "April 2005",
}

CATEGORICAL_OPTIONS = {
    "SEX": SEX_OPTIONS,
    "EDUCATION": EDUCATION_OPTIONS,
    "MARRIAGE": MARRIAGE_OPTIONS,
}

DEFAULT_VALUES: dict[str, int | float] = {
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


# Synthetic sample profiles are provided only to demonstrate that changing
# the customer inputs changes the model's assessment. They are not real people
# or recommended customer profiles.
PROFILE_PRESETS: dict[str, dict[str, int | float]] = {
    "On-time payment example": {
        "LIMIT_BAL": 500_000,
        "SEX": 2,
        "EDUCATION": 1,
        "MARRIAGE": 2,
        "AGE": 38,
        "PAY_0": -1,
        "PAY_2": -1,
        "PAY_3": -1,
        "PAY_4": -1,
        "PAY_5": -1,
        "PAY_6": -1,
        "BILL_AMT1": 24_000,
        "BILL_AMT2": 22_000,
        "BILL_AMT3": 21_000,
        "BILL_AMT4": 20_000,
        "BILL_AMT5": 19_000,
        "BILL_AMT6": 18_000,
        "PAY_AMT1": 25_000,
        "PAY_AMT2": 23_000,
        "PAY_AMT3": 22_000,
        "PAY_AMT4": 20_000,
        "PAY_AMT5": 19_000,
        "PAY_AMT6": 18_000,
    },
    "Recent delay example": {
        "LIMIT_BAL": 50_000,
        "SEX": 1,
        "EDUCATION": 3,
        "MARRIAGE": 1,
        "AGE": 29,
        "PAY_0": 2,
        "PAY_2": 2,
        "PAY_3": 1,
        "PAY_4": 1,
        "PAY_5": 0,
        "PAY_6": 0,
        "BILL_AMT1": 48_000,
        "BILL_AMT2": 46_000,
        "BILL_AMT3": 44_000,
        "BILL_AMT4": 42_000,
        "BILL_AMT5": 40_000,
        "BILL_AMT6": 38_000,
        "PAY_AMT1": 1_000,
        "PAY_AMT2": 1_000,
        "PAY_AMT3": 1_000,
        "PAY_AMT4": 1_500,
        "PAY_AMT5": 2_000,
        "PAY_AMT6": 2_000,
    },
    "Mixed history example": {
        "LIMIT_BAL": 150_000,
        "SEX": 2,
        "EDUCATION": 2,
        "MARRIAGE": 2,
        "AGE": 42,
        "PAY_0": 1,
        "PAY_2": 0,
        "PAY_3": -1,
        "PAY_4": 0,
        "PAY_5": -1,
        "PAY_6": 0,
        "BILL_AMT1": 82_000,
        "BILL_AMT2": 77_000,
        "BILL_AMT3": 74_000,
        "BILL_AMT4": 68_000,
        "BILL_AMT5": 63_000,
        "BILL_AMT6": 59_000,
        "PAY_AMT1": 6_000,
        "PAY_AMT2": 5_000,
        "PAY_AMT3": 7_000,
        "PAY_AMT4": 5_000,
        "PAY_AMT5": 4_000,
        "PAY_AMT6": 4_000,
    },
}


# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
      .stApp {{ background: {BG}; color: {TEXT}; }}
      [data-testid="stHeader"] {{ background: rgba(244,247,250,.92); }}
      [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {NAVY}, #17364D);
        border-right: 1px solid rgba(255,255,255,.08);
      }}
      [data-testid="stSidebar"] * {{ color: #F3F7FA !important; }}
      [data-testid="stSidebar"] [data-testid="stRadio"] label {{
        padding: .32rem .15rem;
        font-weight: 600;
      }}
      .hero {{
        background: linear-gradient(112deg, {NAVY} 0%, {NAVY_2} 65%, #176B70 100%);
        color: white;
        border-radius: 18px;
        padding: 1.55rem 1.8rem;
        margin: .2rem 0 1.2rem 0;
        box-shadow: 0 12px 28px rgba(16,36,58,.12);
      }}
      .hero h1 {{ color: white; margin: 0; font-size: 2rem; letter-spacing: -.03em; }}
      .hero p {{ color: #D7E8EC; margin: .45rem 0 0 0; font-size: 1rem; }}
      .eyebrow {{ color: #A8DADC; text-transform: uppercase; letter-spacing: .12em;
                  font-size: .72rem; font-weight: 750; margin-bottom: .45rem; }}
      .section-intro {{ color: {MUTED}; margin-top: -.35rem; }}
      .note-card {{ background: #EAF4F5; border: 1px solid #CDE4E5;
                    border-left: 4px solid {TEAL}; border-radius: 10px;
                    padding: .8rem 1rem; color: #1D3B45; }}
      div[data-testid="stMetric"] {{
        background: white; border: 1px solid #E2E8F0; border-radius: 13px;
        padding: 14px 16px; box-shadow: 0 2px 7px rgba(15,23,42,.035);
      }}
      div[data-testid="stMetricLabel"] {{ color: {MUTED}; }}
      div[data-testid="stExpander"] {{
        background: white; border: 1px solid #E2E8F0; border-radius: 12px;
      }}
      div.stButton > button, div.stFormSubmitButton > button,
      div[data-testid="stDownloadButton"] > button {{
        border-radius: 10px; font-weight: 650; min-height: 2.55rem;
        border: 1px solid #D6E0E8;
      }}
      div.stFormSubmitButton > button[kind="primary"] {{
        background: {TEAL}; border-color: {TEAL}; color: white;
      }}
      div[data-testid="stTabs"] button {{ font-weight: 650; }}
      .small-muted {{ color: {MUTED}; font-size: .85rem; }}
      .footer {{ color: #718096; font-size: .78rem; padding: 1.5rem 0 .4rem; }}
      @media (max-width: 700px) {{ .hero {{ padding: 1.2rem; }} .hero h1 {{ font-size: 1.55rem; }} }}
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Data and model helpers
# -----------------------------------------------------------------------------
def read_json(path: Path) -> dict[str, Any]:
    """Read a JSON asset safely; a missing/invalid file becomes an empty dict."""
    try:
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        pass
    return {}


@st.cache_resource(show_spinner="Loading trained model…")
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Trained model not found: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def safe_number(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
        return number if np.isfinite(number) else default
    except (TypeError, ValueError):
        return default


def make_chart_rows(
    audit: dict[str, Any], key: str, label: str, *, code_labels: dict[int, str] | None = None
) -> pd.DataFrame | None:
    """Build chart data without assuming an audit section exists or is valid."""
    groups = audit.get(key, {}) if isinstance(audit, dict) else {}
    if not isinstance(groups, dict) or not groups:
        return None

    rows: list[dict[str, Any]] = []
    for raw_key, details in groups.items():
        if not isinstance(details, dict) or "rate_pct" not in details:
            continue
        display_key = str(raw_key)
        if code_labels is not None:
            try:
                code = int(raw_key)
                display_key = code_labels.get(code, f"Other / code {code}")
            except (TypeError, ValueError):
                display_key = str(raw_key)
        rows.append(
            {
                label: display_key,
                "Default rate (%)": safe_number(details.get("rate_pct")),
                "Customers": int(safe_number(details.get("count", details.get("n")))),
                "Defaults": int(safe_number(details.get("defaults"))),
            }
        )

    if not rows:
        return None
    frame = pd.DataFrame(rows)
    # JSON object insertion order is retained, so the source-code order in the
    # audit (normally -2, -1, 0, 1, …) is preserved in the table and chart.
    return frame


def code_label(options: dict[int, str], value: Any) -> str:
    try:
        code = int(value)
        return options.get(code, f"Other / code {code}")
    except (TypeError, ValueError):
        return str(value)


def build_model_frame(
    values: dict[str, int | float], feature_names: list[str], categorical_features: set[str]
) -> pd.DataFrame:
    """Restore the feature order and category dtypes expected by the pipeline."""
    missing = [feature for feature in feature_names if feature not in values]
    if missing:
        raise ValueError(f"Input values are missing model features: {', '.join(missing)}")

    row: dict[str, Any] = {}
    for feature in feature_names:
        value = values[feature]
        if feature in categorical_features:
            row[feature] = str(int(value))
        else:
            row[feature] = float(value)
    return pd.DataFrame([row], columns=feature_names)


def get_default_score(model: Any, frame: pd.DataFrame) -> float:
    """Return the probability column for class 1, with a safe class-order check."""
    if not hasattr(model, "predict_proba"):
        raise TypeError("The saved model does not provide predict_proba().")
    probabilities = np.asarray(model.predict_proba(frame.to_numpy(dtype=object)))[0]
    classes = list(getattr(model, "classes_", [0, 1]))
    try:
        positive_index = classes.index(1)
    except ValueError:
        positive_index = 1 if len(probabilities) > 1 else 0
    if positive_index >= len(probabilities):
        raise ValueError("The model output does not contain a probability for class 1.")
    return float(np.clip(probabilities[positive_index], 0.0, 1.0))


def score_band(score: float) -> tuple[str, str, str]:
    """Illustrative score bands; these are not validated bank risk grades."""
    if score < 0.20:
        return "Lower score band", "Routine monitoring", "success"
    if score < 0.35:
        return "Watchlist score band", "Routine account review", "info"
    if score < 0.50:
        return "Elevated score band", "Prioritised manual review", "warning"
    return "High review-priority band", "Timely authorised review", "error"


def profile_diagnostics(values: dict[str, int | float]) -> dict[str, str]:
    pay_codes = [int(values[f"PAY_{suffix}"]) for suffix in ("0", "2", "3", "4", "5", "6")]
    delayed_months = sum(code >= 1 for code in pay_codes)
    latest_bill = float(values["BILL_AMT1"])
    latest_payment = float(values["PAY_AMT1"])
    credit_limit = float(values["LIMIT_BAL"])

    if credit_limit > 0:
        utilisation = latest_bill / credit_limit * 100
        utilisation_text = f"{utilisation:.1f}%" if np.isfinite(utilisation) else "Not available"
    else:
        utilisation_text = "Not available (zero credit limit)"

    if latest_bill > 0:
        payment_ratio = latest_payment / latest_bill * 100
        payment_text = f"{payment_ratio:.1f}%" if np.isfinite(payment_ratio) else "Not available"
    else:
        payment_text = "Not meaningful for a zero / credit bill"

    return {
        "Months with a delay code": f"{delayed_months} of 6",
        "Latest bill / credit limit": utilisation_text,
        "Latest payment / latest bill": payment_text,
        "Latest repayment status": code_label(PAY_OPTIONS, values["PAY_0"]),
    }


def set_profile_values(profile: dict[str, int | float]) -> None:
    for field, value in profile.items():
        st.session_state[f"input_{field}"] = value
    st.session_state.pop("assessment_result", None)


def reset_profile_values() -> None:
    for field in DEFAULT_VALUES:
        st.session_state.pop(f"input_{field}", None)
    st.session_state.pop("assessment_result", None)
    st.session_state.pop("review_threshold", None)


def csv_download(values: dict[str, int | float], result: dict[str, Any]) -> str:
    record: dict[str, Any] = {f"input_{key}": value for key, value in values.items()}
    record.update(
        {
            "uncalibrated_model_score": result["score"],
            "illustrative_score_band": result["band"],
            "technical_threshold": result["threshold"],
            "technical_prediction": result["prediction"],
        }
    )
    return pd.DataFrame([record]).to_csv(index=False)


# -----------------------------------------------------------------------------
# Load lightweight project assets
# -----------------------------------------------------------------------------
audit = read_json(AUDIT_PATH)
metrics = read_json(METRICS_PATH)
metadata = read_json(METADATA_PATH)


# -----------------------------------------------------------------------------
# Sidebar and page header
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ◈ CREDITRISK")
    st.caption("BUSINESS ANALYTICS · DECISION SUPPORT")
    st.divider()
    page = st.radio(
        "WORKSPACE",
        ["Business Overview", "Data Insights", "Prediction"],
        format_func=lambda item: {
            "Business Overview": "🏠  Business Overview",
            "Data Insights": "📈  Data Insights",
            "Prediction": "🧭  Risk Assessment",
        }[item],
        label_visibility="visible",
    )
    st.divider()
    st.caption("SOURCE DATA")
    st.caption("UCI Taiwan credit-card clients · 2005")
    st.caption("Academic prototype · Human review only")
    st.markdown("---")
    st.caption("Model output is not a calibrated probability or a lending decision.")

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Credit portfolio intelligence</div>
      <h1>CreditRisk Analytics</h1>
      <p>Explore portfolio patterns, assess sample customer profiles, and support informed human review.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Business Overview
# -----------------------------------------------------------------------------
if page == "Business Overview":
    st.subheader("Business Overview")
    st.markdown(
        '<p class="section-intro">A machine-learning prototype for exploring next-month credit-card default signals.</p>',
        unsafe_allow_html=True,
    )
    st.write(
        "The application analyses historical credit limits, repayment status, bill statements, "
        "previous payments, and customer-profile fields to estimate a model score for possible "
        "next-month default. It is designed as an academic decision-support demonstration."
    )

    if audit:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Customer records", f"{int(safe_number(audit.get('rows'))):,}")
        c2.metric("Predictor variables", f"{int(safe_number(audit.get('predictor_count'))):,}")
        c3.metric(
            "Observed default rate",
            f"{safe_number(audit.get('target_pct', {}).get('1')):.2f}%",
        )
        c4.metric(
            "Test ROC-AUC",
            f"{safe_number(metrics.get('roc_auc')):.3f}" if metrics else "Not available",
        )
    else:
        st.info("Dataset audit metrics are not available. Check reports/dataset_audit.json.")

    st.markdown("### How a business team could use the prototype")
    one, two, three = st.columns(3)
    with one:
        st.markdown("#### 01 · Identify")
        st.write("Use model scores as one signal to prioritise accounts for qualified review.")
    with two:
        st.markdown("#### 02 · Understand")
        st.write("Review repayment patterns, recent bills, payments, and the wider customer context.")
    with three:
        st.markdown("#### 03 · Respond")
        st.write("Consider suitable customer support or outreach only after authorised human review.")

    with st.expander("Dataset and model details", expanded=False):
        d1, d2 = st.columns(2)
        d1.write(f"**Dataset records:** {int(safe_number(audit.get('rows'))):,}" if audit else "**Dataset records:** Not available")
        d1.write(f"**Original columns:** {int(safe_number(audit.get('columns'))):,}" if audit else "**Original columns:** Not available")
        d2.write(f"**Selected model:** {metadata.get('model_name', 'Not specified')}")
        d2.write(f"**Decision target:** {metadata.get('target', 'Default payment next month')}")
        st.caption("The source dataset represents Taiwanese credit-card customers and historical records from 2005.")

    st.markdown(
        '<div class="note-card"><strong>Important scope limitation:</strong> '
        "The dataset is historical and based on Taiwanese customers in 2005. The model has not been validated "
        "for current Indian credit portfolios. It must not make automatic approval, rejection, collection, "
        "pricing, or other adverse customer decisions.</div>",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Data Insights
# -----------------------------------------------------------------------------
elif page == "Data Insights":
    st.subheader("Portfolio Data Insights")
    st.markdown(
        '<p class="section-intro">Explore observed customer outcomes, repayment patterns, and model evaluation results.</p>',
        unsafe_allow_html=True,
    )

    if not audit:
        st.error("The dataset audit could not be read. Check reports/dataset_audit.json in the project repository.")
    else:
        target_counts = audit.get("target_counts", {}) if isinstance(audit.get("target_counts"), dict) else {}
        target_pct = audit.get("target_pct", {}) if isinstance(audit.get("target_pct"), dict) else {}
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total records", f"{int(safe_number(audit.get('rows'))):,}")
        c2.metric(
            "Observed defaults",
            f"{int(safe_number(target_counts.get('1'))):,}",
            f"{safe_number(target_pct.get('1')):.2f}% of records",
        )
        c3.metric(
            "Non-defaults",
            f"{int(safe_number(target_counts.get('0'))):,}",
            f"{safe_number(target_pct.get('0')):.2f}% of records",
        )
        c4.metric("Missing cells", f"{int(safe_number(audit.get('missing_cells'))):,}")
        st.caption(
            f"{int(safe_number(audit.get('columns'))):,} original columns · "
            f"{int(safe_number(audit.get('exact_duplicate_rows'))):,} exact duplicate rows · "
            f"{int(safe_number(audit.get('unique_ids'))):,} unique IDs"
        )

        tab_repayment, tab_segments, tab_signals, tab_performance = st.tabs(
            ["Repayment behaviour", "Customer segments", "Model signals", "Model performance"]
        )

        with tab_repayment:
            st.markdown("### Observed default rate by latest repayment status")
            pay_labels = {
                -2: "No consumption",
                -1: "Paid duly",
                0: "Revolving credit",
                1: "1 month late",
                2: "2 months late",
                3: "3 months late",
                4: "4 months late",
                5: "5 months late",
                6: "6 months late",
                7: "7 months late",
                8: "8 months late",
            }
            pay = make_chart_rows(
                audit,
                "default_rate_by_PAY_0",
                "Latest repayment status",
                code_labels=pay_labels,
            )
            if pay is not None:
                st.bar_chart(pay.set_index("Latest repayment status")["Default rate (%)"])
                st.dataframe(
                    pay[["Latest repayment status", "Customers", "Defaults", "Default rate (%)"]],
                    hide_index=True,
                    use_container_width=True,
                    column_config={"Default rate (%)": st.column_config.NumberColumn(format="%.2f%%")},
                )
            else:
                st.info(
                    "The audit file does not contain a valid 'default_rate_by_PAY_0' section. "
                    "The rest of Data Insights remains available. Regenerate the dataset audit to add this breakdown."
                )

        with tab_segments:
            left, right = st.columns(2)
            limit_data = make_chart_rows(audit, "default_rate_by_limit_band", "Credit-limit band")
            age_data = make_chart_rows(audit, "default_rate_by_age_band", "Age band")
            education_data = make_chart_rows(
                audit, "default_rate_by_education", "Education level", code_labels=EDUCATION_OPTIONS
            )
            with left:
                st.markdown("### Default rate by credit-limit band")
                if limit_data is not None:
                    st.bar_chart(limit_data.set_index("Credit-limit band")["Default rate (%)"])
                    st.dataframe(limit_data, hide_index=True, use_container_width=True)
                else:
                    st.info("Credit-limit breakdown is not present in the current audit file.")
            with right:
                st.markdown("### Default rate by age band")
                if age_data is not None:
                    st.bar_chart(age_data.set_index("Age band")["Default rate (%)"])
                    st.dataframe(age_data, hide_index=True, use_container_width=True)
                else:
                    st.info("Age breakdown is not present in the current audit file.")
            st.markdown("#### Observed default rate by education group")
            if education_data is not None:
                st.bar_chart(education_data.set_index("Education level")["Default rate (%)"])
                st.dataframe(education_data, hide_index=True, use_container_width=True)
            else:
                st.info("Education-group breakdown is not present in the current audit file.")

        with tab_signals:
            st.markdown("### Validation permutation importance")
            st.caption("Importance is measured as the reduction in validation average precision when one feature is shuffled. It is a predictive diagnostic, not a causal effect.")
            importance = audit.get("permutation_importance_validation", [])
            if isinstance(importance, list) and importance:
                importance_df = pd.DataFrame(importance)
                required_cols = {"feature", "mean_ap_drop"}
                if required_cols.issubset(importance_df.columns):
                    importance_df = importance_df.sort_values("mean_ap_drop", ascending=False).head(12)
                    st.bar_chart(importance_df.set_index("feature")["mean_ap_drop"])
                    st.dataframe(importance_df, hide_index=True, use_container_width=True)
                else:
                    st.info("Permutation-importance data has an unexpected schema.")
            else:
                st.info("Validation permutation-importance results are not present in the audit file.")
            st.warning("Feature importance does not establish cause, fairness, or a valid reason to take adverse action against an individual customer.")

        with tab_performance:
            st.markdown("### Held-out test performance")
            if metrics:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Accuracy", f"{safe_number(metrics.get('accuracy')):.1%}")
                m2.metric("Default precision", f"{safe_number(metrics.get('precision_default')):.1%}")
                m3.metric("Default recall", f"{safe_number(metrics.get('recall_default')):.1%}")
                m4.metric("ROC-AUC", f"{safe_number(metrics.get('roc_auc')):.3f}")

                cm_values = [
                    [int(safe_number(metrics.get("tn"))), int(safe_number(metrics.get("fp")))],
                    [int(safe_number(metrics.get("fn"))), int(safe_number(metrics.get("tp")))],
                ]
                cm = pd.DataFrame(
                    cm_values,
                    index=["Actual: No default", "Actual: Default"],
                    columns=["Predicted: No default", "Predicted: Default"],
                )
                st.markdown("#### Confusion matrix")
                st.dataframe(cm, use_container_width=True)
                with st.expander("How to read these metrics"):
                    st.write(
                        "**Precision** indicates how often a predicted default flag was correct. "
                        "**Recall** indicates how many actual defaults were identified. "
                        "**ROC-AUC** measures how well the model ranks positive cases above negative cases across thresholds."
                    )
            else:
                st.info("Final test metrics are not available. Check reports/final_test_metrics.json.")

        st.warning(
            "These are historical associations, not causes. The current model includes demographic attributes; "
            "a formal fairness, calibration, and suitability review is still required."
        )

        st.download_button(
            "Download dataset audit (JSON)",
            data=json.dumps(audit, indent=2),
            file_name="dataset_audit.json",
            mime="application/json",
            use_container_width=False,
        )


# -----------------------------------------------------------------------------
# Prediction / risk assessment
# -----------------------------------------------------------------------------
else:
    st.subheader("Customer Risk Assessment")
    st.markdown(
        '<p class="section-intro">Build a customer profile, run the trained model, and review an illustrative score category.</p>',
        unsafe_allow_html=True,
    )
    st.info(
        "Academic demonstration only. The model score is not separately calibrated and must not be interpreted "
        "as a verified probability of default or used to make an automated decision about an individual."
    )

    if not MODEL_PATH.exists():
        st.error("The trained model is missing. Confirm that models/credit_default_pipeline.joblib is committed to the repository.")
    elif not metadata or not metadata.get("feature_names"):
        st.error("Model metadata is missing or incomplete. Confirm models/model_metadata.json.")
    else:
        feature_names = list(metadata["feature_names"])
        categorical_features = set(metadata.get("categorical_features", []))
        model_threshold = float(metadata.get("threshold", 0.50))

        # Quick-fill buttons support interactive demonstrations without changing
        # the saved model or its feature definitions.
        st.markdown("### Quick demo profiles")
        st.caption("Load a synthetic example, then select **Assess customer profile** to run the model.")
        preset_cols = st.columns(4)
        for column, preset_name in zip(preset_cols[:3], PROFILE_PRESETS):
            with column:
                st.button(
                    preset_name,
                    key=f"preset_{preset_name}",
                    use_container_width=True,
                    on_click=set_profile_values,
                    args=(PROFILE_PRESETS[preset_name],),
                )
        with preset_cols[3]:
            st.button(
                "↺ Reset all fields",
                key="reset_profile",
                use_container_width=True,
                on_click=reset_profile_values,
            )
        st.caption("Example profiles are synthetic test inputs. They do not represent real customers or recommended credit decisions.")

        # Initialise widget state once. Preset/reset callbacks update these keys,
        # and the widgets then render the selected values without stale defaults.
        for field, default_value in DEFAULT_VALUES.items():
            state_key = f"input_{field}"
            if state_key not in st.session_state:
                st.session_state[state_key] = default_value

        values: dict[str, int | float] = {}
        with st.form("risk_assessment_form", clear_on_submit=False):
            with st.container(border=True):
                st.markdown("#### 1 · Customer and credit profile")
                st.caption("The labels below are user-friendly descriptions; the model receives the original dataset codes.")
                a, b, c = st.columns(3)
                with a:
                    values["LIMIT_BAL"] = st.number_input(
                        "Credit limit (NT$)", min_value=0, max_value=2_000_000,
                        step=10_000, key="input_LIMIT_BAL",
                        help="Credit limit recorded in New Taiwan dollars in the source dataset.",
                    )
                    values["SEX"] = st.selectbox(
                        "Gender", options=list(SEX_OPTIONS), format_func=lambda x: SEX_OPTIONS[x],
                        key="input_SEX",
                    )
                with b:
                    values["EDUCATION"] = st.selectbox(
                        "Education level", options=list(EDUCATION_OPTIONS),
                        format_func=lambda x: EDUCATION_OPTIONS[x], key="input_EDUCATION",
                    )
                    values["MARRIAGE"] = st.selectbox(
                        "Marital status", options=list(MARRIAGE_OPTIONS),
                        format_func=lambda x: MARRIAGE_OPTIONS[x], key="input_MARRIAGE",
                    )
                with c:
                    values["AGE"] = st.number_input(
                        "Age (years)", min_value=18, max_value=100, step=1,
                        key="input_AGE",
                    )

            with st.container(border=True):
                st.markdown("#### 2 · Historical repayment behaviour")
                st.caption("Choose the recorded repayment status for each month. The dropdown displays descriptions, not raw codes.")
                pay_fields = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
                pay_cols = st.columns(3)
                for index, field in enumerate(pay_fields):
                    with pay_cols[index % 3]:
                        month_no = 1 if field == "PAY_0" else int(field.split("_")[1])
                        values[field] = st.selectbox(
                            f"{MONTH_LABELS[month_no]} · repayment status",
                            options=list(PAY_OPTIONS),
                            format_func=lambda x: PAY_OPTIONS[x],
                            key=f"input_{field}",
                        )

            with st.container(border=True):
                st.markdown("#### 3 · Historical bill statements")
                st.caption("Amounts are in New Taiwan dollars (NT$). Negative statement values are allowed because credits or adjustments can occur in the source data.")
                bill_cols = st.columns(3)
                for index in range(1, 7):
                    field = f"BILL_AMT{index}"
                    with bill_cols[(index - 1) % 3]:
                        values[field] = st.number_input(
                            f"{MONTH_LABELS[index]} · bill amount (NT$)",
                            min_value=-1_000_000, max_value=5_000_000, step=1_000,
                            key=f"input_{field}",
                        )

            with st.container(border=True):
                st.markdown("#### 4 · Previous payment amounts")
                st.caption("Enter the amount paid in each historical month, in NT$.")
                payment_cols = st.columns(3)
                for index in range(1, 7):
                    field = f"PAY_AMT{index}"
                    with payment_cols[(index - 1) % 3]:
                        values[field] = st.number_input(
                            f"{MONTH_LABELS[index]} · payment amount (NT$)",
                            min_value=0, max_value=5_000_000, step=500,
                            key=f"input_{field}",
                        )

            submitted = st.form_submit_button(
                "🧭  Assess customer profile",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            try:
                with st.spinner("Running the trained model…"):
                    model = load_model()
                    sample = build_model_frame(values, feature_names, categorical_features)
                    score = get_default_score(model, sample)
                    band, guidance, message_type = score_band(score)
                    prediction = int(score >= model_threshold)
                    st.session_state["assessment_result"] = {
                        "score": score,
                        "band": band,
                        "guidance": guidance,
                        "message_type": message_type,
                        "threshold": model_threshold,
                        "prediction": prediction,
                        "values": values.copy(),
                    }
            except Exception as exc:
                st.error(f"The assessment could not be completed: {exc}")
                st.caption("Check that the model file, metadata feature order, and installed scikit-learn/joblib versions match the training environment.")
                st.stop()

        result = st.session_state.get("assessment_result")
        if result:
            st.divider()
            st.markdown("## Assessment result")
            score = float(result["score"])
            band, guidance = result["band"], result["guidance"]
            result_values = result["values"]

            score_col, band_col, class_col = st.columns(3)
            score_col.metric(
                "Uncalibrated model score",
                f"{score:.1%}",
                help="Raw model output for class 1. It has not been separately calibrated and is not a verified default probability.",
            )
            band_col.metric("Illustrative score category", band)
            class_col.metric(
                "Class at model threshold",
                "Default flag" if int(result["prediction"]) else "No default flag",
                help=f"Technical model threshold: {float(result['threshold']):.0%}. This is not a bank-approved business cutoff.",
            )

            st.progress(score, text="Relative model-score scale · 0% to 100% (not a calibrated probability)")
            st.caption("Illustrative bands: below 20% = lower; 20–34.99% = watchlist; 35–49.99% = elevated review; 50% or above = high review-priority. These bands are for interface demonstration only.")

            message = (
                f"**Suggested review posture: {guidance}.** "
                "Use the score only as one input to an authorised human review."
            )
            if result["message_type"] == "success":
                st.success(message)
            elif result["message_type"] == "info":
                st.info(message)
            elif result["message_type"] == "warning":
                st.warning(message)
            else:
                st.error(message)

            st.markdown("### Profile indicators")
            st.caption("These are descriptive calculations from the entered values, not explanations of model causality or feature-level attribution.")
            diagnostics = profile_diagnostics(result_values)
            diag_cols = st.columns(4)
            for column, (label, value) in zip(diag_cols, diagnostics.items()):
                column.metric(label, value)

            st.markdown("### Assessment details")
            left, right = st.columns([1, 1])
            with left:
                st.markdown("#### Customer profile")
                profile_summary = [
                    ("Credit limit", f"NT$ {float(result_values['LIMIT_BAL']):,.0f}"),
                    ("Age", f"{int(result_values['AGE'])} years"),
                    ("Gender", code_label(SEX_OPTIONS, result_values["SEX"])),
                    ("Education", code_label(EDUCATION_OPTIONS, result_values["EDUCATION"])),
                    ("Marital status", code_label(MARRIAGE_OPTIONS, result_values["MARRIAGE"])),
                    ("Latest repayment status", code_label(PAY_OPTIONS, result_values["PAY_0"])),
                ]
                st.dataframe(
                    pd.DataFrame(profile_summary, columns=["Input", "Selected value"]),
                    hide_index=True,
                    use_container_width=True,
                )
            with right:
                st.markdown("#### Explore the technical threshold")
                st.caption("Move the slider to see how the technical class changes. This does not retrain the model or change its score.")
                selected_threshold = st.slider(
                    "Classification threshold",
                    min_value=0.05,
                    max_value=0.95,
                    value=float(result["threshold"]),
                    step=0.01,
                    key="review_threshold",
                    format="%.2f",
                )
                threshold_flag = score >= selected_threshold
                st.metric(
                    "Class at selected threshold",
                    "Default flag" if threshold_flag else "No default flag",
                    delta=f"Threshold {selected_threshold:.0%}",
                )
                st.caption("Threshold exploration is for learning and discussion only. It is not an approved policy setting.")

            st.download_button(
                "⬇ Download assessment summary (CSV)",
                data=csv_download(result_values, result),
                file_name="credit_risk_assessment.csv",
                mime="text/csv",
                use_container_width=True,
            )

            st.markdown(
                '<div class="note-card"><strong>Decision safeguard:</strong> '
                "A lower model score does not guarantee repayment, and a higher score does not prove that a customer will default. "
                "Verify the underlying information and follow approved, fair, and lawful review procedures.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="note-card"><strong>Ready for assessment.</strong> '
                "Complete the profile or load one of the synthetic examples, then select <em>Assess customer profile</em>. "
                "The result will include a model score category, a threshold-based class, and descriptive profile indicators.</div>",
                unsafe_allow_html=True,
            )


st.markdown(
    '<div class="footer">CreditRisk Analytics · Academic business analytics prototype · Human review required</div>',
    unsafe_allow_html=True,
)