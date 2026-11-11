"""Validation-based model comparison and one untouched test evaluation."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
from joblib import dump
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/"data"/"credit_card_default_clean.csv"
TARGET = "default payment next month"
CAT = ["SEX","EDUCATION","MARRIAGE"]

def main():
    if not DATA.exists():
        raise FileNotFoundError("Run python src/prepare_data.py first.")
    df = pd.read_csv(DATA)
    Xdf = df.drop(columns=["ID",TARGET]).copy()
    y = df[TARGET].astype(int).to_numpy()
    names = Xdf.columns.tolist()
    for c in CAT:
        Xdf[c] = Xdf[c].astype(int).astype(str)
    X = Xdf.to_numpy(dtype=object)
    ci = [names.index(c) for c in CAT]
    ni = [i for i,c in enumerate(names) if c not in CAT]
    Xdev,Xtest,ydev,ytest = train_test_split(X,y,test_size=.20,random_state=42,stratify=y)
    Xtrain,Xval,ytrain,yval = train_test_split(Xdev,ydev,test_size=.10,random_state=42,stratify=ydev)

    def prep(scale=False):
        num = Pipeline([("impute",SimpleImputer(strategy="median"))]+([("scale",StandardScaler())] if scale else []))
        cat = Pipeline([("impute",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))])
        return ColumnTransformer([("num",num,ni),("cat",cat,ci)])
    candidates = {
        "Logistic Regression":Pipeline([("prep",prep(True)),("model",LogisticRegression(max_iter=3000))]),
        "Decision Tree":Pipeline([("prep",prep()),("model",DecisionTreeClassifier(max_depth=7,min_samples_leaf=50,class_weight="balanced",random_state=42))]),
        "Random Forest":Pipeline([("prep",prep()),("model",RandomForestClassifier(n_estimators=300,min_samples_leaf=8,max_features="sqrt",class_weight="balanced_subsample",random_state=42,n_jobs=-1))])
    }
    results=[]
    for name,model in candidates.items():
        model.fit(Xtrain,ytrain)
        p=model.predict_proba(Xval)[:,1]; pred=(p>=.5).astype(int)
        results.append({"model":name,"accuracy":float(accuracy_score(yval,pred)),"precision_default":float(precision_score(yval,pred,zero_division=0)),"recall_default":float(recall_score(yval,pred,zero_division=0)),"f1_default":float(f1_score(yval,pred,zero_division=0)),"roc_auc":float(roc_auc_score(yval,p)),"average_precision":float(average_precision_score(yval,p))})
    selected=max(results,key=lambda r:(r["f1_default"],r["roc_auc"]))["model"]
    final_model=candidates[selected].fit(Xdev,ydev)
    p=final_model.predict_proba(Xtest)[:,1]; pred=(p>=.5).astype(int)
    cm=confusion_matrix(ytest,pred,labels=[0,1])
    final={"model":selected,"threshold":.5,"accuracy":float(accuracy_score(ytest,pred)),"precision_default":float(precision_score(ytest,pred,zero_division=0)),"recall_default":float(recall_score(ytest,pred,zero_division=0)),"f1_default":float(f1_score(ytest,pred,zero_division=0)),"roc_auc":float(roc_auc_score(ytest,p)),"average_precision":float(average_precision_score(ytest,p)),"brier_score":float(brier_score_loss(ytest,p)),"tn":int(cm[0,0]),"fp":int(cm[0,1]),"fn":int(cm[1,0]),"tp":int(cm[1,1])}
    (ROOT/"models").mkdir(exist_ok=True); (ROOT/"reports").mkdir(exist_ok=True)
    dump(final_model,ROOT/"models"/"credit_default_pipeline.joblib",compress=3)
    meta={"model_name":selected,"target":TARGET,"feature_names":names,"categorical_features":CAT,"numeric_features":[names[i] for i in ni],"threshold":.5,"probability_calibration":"Not separately calibrated; call this a model score, not a calibrated probability.","final_test_metrics":final}
    (ROOT/"models"/"model_metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    (ROOT/"reports"/"validation_model_comparison.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    (ROOT/"reports"/"final_test_metrics.json").write_text(json.dumps(final,indent=2),encoding="utf-8")
    print(json.dumps({"validation":results,"test":final},indent=2))

if __name__ == "__main__":
    main()
