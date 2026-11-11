from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

ROOT=Path(__file__).resolve().parent
def read_json(p):
    try: return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except (OSError,json.JSONDecodeError): return {}
audit=read_json(ROOT/"reports/dataset_audit.json")
metrics=read_json(ROOT/"reports/final_test_metrics.json")
meta=read_json(ROOT/"models/model_metadata.json")
MODEL=ROOT/"models/credit_default_pipeline.joblib"

st.set_page_config(page_title="CreditRisk Analytics",page_icon="📊",layout="wide")
st.markdown("""
<style>
.stApp{background:linear-gradient(180deg,#F2F6F9,#FAFCFD)}
[data-testid="stSidebar"]{background:#10243A}
[data-testid="stSidebar"] *{color:#F5FAFC!important}
.hero{background:linear-gradient(115deg,#10243A,#145568);color:white;padding:1.5rem 1.8rem;border-radius:18px;margin-bottom:1.2rem}
.hero h1{color:white;margin:0}.hero p{color:#D7E8EE;margin:.4rem 0 0}
div[data-testid="stMetric"]{background:white;border:1px solid #E2E8F0;padding:14px;border-radius:14px}
div.stButton>button,div.stFormSubmitButton>button{border-radius:10px;font-weight:650;min-height:2.6rem}
div[data-testid="stExpander"]{background:white;border-radius:12px}
</style>""",unsafe_allow_html=True)

EDU={0:"Not specified / unknown",1:"Graduate school",2:"University",3:"High school",4:"Other",5:"Not specified (code 5)",6:"Not specified (code 6)"}
MARR={0:"Not specified / unknown",1:"Married",2:"Single / unmarried",3:"Other"}
SEX={1:"Male",2:"Female"}
PAY={-2:"No consumption recorded",-1:"Paid duly",0:"Revolving credit status",1:"Delayed by 1 month",2:"Delayed by 2 months",3:"Delayed by 3 months",4:"Delayed by 4 months",5:"Delayed by 5 months",6:"Delayed by 6 months",7:"Delayed by 7 months",8:"Delayed by 8 months"}
def pick(label,opts,default):
    codes=list(opts)
    return int(st.selectbox(label,codes,index=codes.index(default),format_func=lambda x:opts[x]))
def make_chart_rows(key,label):
    groups=audit.get(key,{})
    if not isinstance(groups,dict) or not groups:return None
    rows=[{label:str(k),"Default rate (%)":v["rate_pct"],"Customers":v.get("count",0)} for k,v in groups.items() if isinstance(v,dict) and "rate_pct" in v]
    return pd.DataFrame(rows) if rows else None

with st.sidebar:
    st.markdown("## ◈ CREDITRISK")
    st.caption("BUSINESS ANALYTICS · DECISION SUPPORT")
    page=st.radio("WORKSPACE",["Business Overview","Data Insights","Prediction"])
    st.divider()
    st.caption("UCI historical dataset · Taiwan · 2005")
    st.caption("Academic prototype · Human review only")

st.markdown('<div class="hero"><h1>CreditRisk Analytics</h1><p>Credit-card default intelligence · Next-month risk screening · Decision-support workspace</p></div>',unsafe_allow_html=True)

if page=="Business Overview":
    st.subheader("Business Overview")
    st.write("An interactive analytics prototype estimating next-month credit-card default risk from repayment history, credit limits, bill amounts and previous payments.")
    if audit and metrics:
        a,b,c,d=st.columns(4)
        a.metric("Customer records",f'{audit.get("rows",0):,}')
        b.metric("Predictor variables",str(audit.get("predictor_count",23)))
        c.metric("Observed default rate",f'{audit.get("target_pct",{}).get("1",0):.2f}%')
        d.metric("Held-out test ROC-AUC",f'{metrics.get("roc_auc",0):.3f}')
    st.markdown("### How business teams could use this")
    x,y,z=st.columns(3)
    x.markdown("#### 01 · Identify");x.write("Prioritise accounts with stronger model risk signals for qualified review.")
    y.markdown("#### 02 · Understand");y.write("Review repayment history, balances and payment patterns.")
    z.markdown("#### 03 · Support");z.write("Consider suitable customer outreach after authorised human review.")
    with st.expander("Dataset and model details"):
        st.write("30,000 historical Taiwanese credit-card customer records from 2005.")
        st.write(f'Selected model: {meta.get("model_name","Random Forest")}')
    st.info("Not validated for current Indian credit portfolios. Not an automated lending, collections or adverse-action system.")

elif page=="Data Insights":
    st.subheader("Data Insights")
    st.caption("Explore portfolio patterns and held-out model evaluation.")
    if not audit or not metrics:
        st.error("Audit or model metrics are missing. Check the reports folder in GitHub.")
    else:
        a,b,c,d=st.columns(4)
        a.metric("Total records",f'{audit.get("rows",0):,}')
        b.metric("Default accounts",f'{audit.get("target_counts",{}).get("1",0):,}',f'{audit.get("target_pct",{}).get("1",0):.2f}%')
        c.metric("Non-default accounts",f'{audit.get("target_counts",{}).get("0",0):,}',f'{audit.get("target_pct",{}).get("0",0):.2f}%')
        d.metric("Missing cells",f'{audit.get("missing_cells",0):,}')
        st.caption(f'{audit.get("columns",25)} columns · {audit.get("exact_duplicate_rows",0)} duplicate rows · {audit.get("unique_ids",0):,} unique IDs')
        st.markdown("### Portfolio patterns")
        pay=make_chart_rows("default_rate_by_PAY_0","Repayment status")
        lim=make_chart_rows("default_rate_by_limit_band","Credit-limit band")
        age=make_chart_rows("default_rate_by_age_band","Age band")
        left,right=st.columns(2)
        with left:
            st.markdown("#### Observed default rate by latest repayment status")
            if pay is not None:
                st.bar_chart(pay.set_index("Repayment status")["Default rate (%)"])
                st.dataframe(pay,hide_index=True,use_container_width=True)
            else: st.info("This breakdown is not in the current audit. Run the updated model-build workflow once to regenerate it.")
            st.markdown("#### Default rate by credit-limit band")
            if lim is not None: st.bar_chart(lim.set_index("Credit-limit band")["Default rate (%)"])
            else: st.info("Credit-limit breakdown will appear after the updated audit is generated.")
        with right:
            st.markdown("#### Default rate by age band")
            if age is not None: st.bar_chart(age.set_index("Age band")["Default rate (%)"])
            else: st.info("Age breakdown will appear after the updated audit is generated.")
            comp=read_json(ROOT/"reports/validation_model_comparison.json")
            if isinstance(comp,list) and comp:
                st.markdown("#### Validation model comparison")
                st.dataframe(pd.DataFrame(comp).set_index("model").style.format(precision=3),use_container_width=True)
        st.markdown("### Held-out test performance")
        x,y,z,w=st.columns(4)
        x.metric("Default precision",f'{metrics.get("precision_default",0):.1%}')
        y.metric("Default recall",f'{metrics.get("recall_default",0):.1%}')
        z.metric("Default F1",f'{metrics.get("f1_default",0):.3f}')
        w.metric("ROC-AUC",f'{metrics.get("roc_auc",0):.3f}')
        with st.expander("Understand the errors"):
            st.write(f'False negatives: {metrics.get("fn",0):,} · False positives: {metrics.get("fp",0):,}')
            st.write("Precision measures the reliability of a default flag; recall measures the share of actual defaults identified.")
        st.warning("These are descriptive associations, not causes. Demographic attributes are included; fairness and calibration reviews remain necessary.")

else:
    st.subheader("Customer Risk Assessment")
    st.caption("Enter a customer profile to generate a model score and illustrative review category.")
    st.warning("Academic use only. This uncalibrated score is not a verified probability and must not drive automated decisions.")
    if not MODEL.exists() or not meta:
        st.error("The trained model or model metadata is missing from the models folder.")
    else:
        import joblib
        @st.cache_resource
        def load_model(): return joblib.load(MODEL)
        try: model=load_model()
        except Exception:
            st.error("The model could not be loaded. Check Python, scikit-learn and joblib version compatibility.")
            st.stop()
        features=meta.get("feature_names",[])
        cats=set(meta.get("categorical_features",[]))
        if not features: st.error("Model feature metadata is incomplete.");st.stop()
        values={}
        with st.form("risk_assessment",clear_on_submit=False):
            st.markdown("### 1 · Customer and credit profile")
            p1,p2,p3=st.columns(3)
            with p1:
                values["LIMIT_BAL"]=st.number_input("Credit limit (NT$)",10000,2000000,200000,10000)
                values["SEX"]=pick("Gender category",SEX,2)
            with p2:
                values["EDUCATION"]=pick("Education level",EDU,2)
                values["MARRIAGE"]=pick("Marital status",MARR,2)
            with p3: values["AGE"]=st.number_input("Age (years)",18,100,35)
            st.markdown("### 2 · Repayment history")
            st.caption("Select the status recorded for each historical month.")
            cols=st.columns(3)
            for i,f in enumerate(["PAY_0","PAY_2","PAY_3","PAY_4","PAY_5","PAY_6"]):
                with cols[i%3]: values[f]=pick(f"{f} · repayment status",PAY,0)
            st.markdown("### 3 · Bill amounts")
            st.caption("All amounts are in New Taiwan dollars (NT$).")
            cols=st.columns(3)
            for i,f in enumerate([f"BILL_AMT{k}" for k in range(1,7)]):
                with cols[i%3]: values[f]=st.number_input(f"Bill amount · month {i+1}",-1000000,5000000,50000 if i==0 else 40000,1000,key=f"field_{f}")
            st.markdown("### 4 · Previous payment amounts")
            cols=st.columns(3)
            for i,f in enumerate([f"PAY_AMT{k}" for k in range(1,7)]):
                with cols[i%3]: values[f]=st.number_input(f"Payment amount · month {i+1}",0,5000000,4000,500,key=f"field_{f}")
            submitted=st.form_submit_button("Assess customer risk",type="primary",use_container_width=True)
        if submitted:
            try:
                row=[str(int(values[f])) if f in cats else float(values[f]) for f in features]
                score=float(model.predict_proba(pd.DataFrame([row],columns=features))[0,1])
                threshold=float(meta.get("threshold",.5))
                if score<.20:
                    band="Lower model-score band";msg="Continue normal monitoring. This score alone is not a reason to change account treatment.";kind="success"
                elif score<.35:
                    band="Watchlist band";msg="Consider a routine account review and check recent repayment activity.";kind="info"
                elif score<threshold:
                    band="Elevated review band";msg="Prioritise qualified manual review of repayment history and customer context.";kind="warning"
                else:
                    band="High review-priority band";msg="Prioritise timely review by an authorised team member. Verify account information before any supportive outreach.";kind="error"
                st.divider()
                st.markdown("## Assessment result")
                x,y,z=st.columns(3)
                x.metric("Uncalibrated model score",f"{score:.1%}",help="Raw model score; not a calibrated default probability.")
                y.metric("Illustrative score category",band)
                y.metric("Class at technical threshold","Default flag" if score>=threshold else "No default flag")
                st.progress(min(max(score,0),1),text="Relative model score (not a calibrated probability)")
                if kind=="success":st.success(msg)
                elif kind=="info":st.info(msg)
                elif kind=="warning":st.warning(msg)
                else:st.error(msg)
                st.markdown("### Result explanation")
                st.write(f"The score is {score:.1%}; the technical classification threshold is {threshold:.0%}. The score is {'above' if score>=threshold else 'below'} that threshold.")
                st.caption("Score bands are illustrative interface categories only, not validated risk grades or approved banking cutoffs.")
                with st.expander("Review submitted customer profile"):
                    summary={"Credit limit":f'NT$ {values["LIMIT_BAL"]:,.0f}',"Age":f'{values["AGE"]} years',"Gender":SEX[values["SEX"]],"Education":EDU[values["EDUCATION"]],"Marital status":MARR[values["MARRIAGE"]],"Latest repayment status":PAY[values["PAY_0"]]}
                    st.dataframe(pd.DataFrame(summary.items(),columns=["Input","Selected value"]),hide_index=True,use_container_width=True)
                report=pd.DataFrame([{"uncalibrated_model_score":score,"illustrative_category":band,"technical_threshold":threshold,"predicted_class":int(score>=threshold),"management_guidance":msg}])
                st.download_button("Download assessment summary",report.to_csv(index=False),"credit_risk_assessment.csv","text/csv")
            except (KeyError,ValueError,TypeError) as exc: st.error(f"Unable to score this profile. Check input values and model features: {exc}")
