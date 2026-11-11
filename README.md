# Credit Card Default Prediction – CreditRisk Analytics

MBA Business Analytics project: estimate next-month credit-card default risk as a **human-review decision-support signal**, not an automated credit decision.

**Dataset:** UCI Default of Credit Card Clients · [UCI dataset page](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients) · DOI [10.24432/C55S3H](https://doi.org/10.24432/C55S3H) · CC BY 4.0.

## Verified dataset audit

The user-provided workbook was inspected. It contains 30,000 observations and 25 columns: ID, 23 predictors, and target `default payment next month`. The actual field names are on spreadsheet row 2; row 1 contains generic X1–X23/Y labels.

- Missing cells: **0**
- Exact duplicate rows: **0**
- Unique IDs: **30,000**
- No default (0): **23,364 (77.88%)**
- Default (1): **6,636 (22.12%)**
- ID is excluded from predictors.

## Preliminary held-out test results

Candidates were compared on a validation set. Random Forest was selected using default-class F1 (ROC-AUC tie-break), refitted on the 24,000-record development set, then evaluated once on a separate 6,000-record test set. Threshold: 0.50.

| Metric | Test result |
|---|---:|
| Accuracy | 79.32% |
| Precision – default | 53.17% |
| Recall – default | 54.41% |
| F1 – default | 0.538 |
| ROC-AUC | 0.774 |
| Average precision | 0.552 |
| Brier score | 0.156 |

Confusion matrix: TN=4,037, FP=636, FN=605, TP=722. The model misses 45.6% of actual defaulters at this cutoff. A bank should not use this threshold without a documented cost analysis.

## EDA findings (associations, not causation)

- The default class is 22.12% of the sample; accuracy alone is inadequate.
- PAY_0=2 has a 69.14% observed default rate (2,667 accounts); PAY_0=0 has 12.81% (14,737 accounts). Rare PAY_0 codes have small sample sizes.
- The <=50k credit-limit band has 31.79% observed default rate; the >300k band has 13.26%.
- These group differences do not establish causal relationships.

## Scope and limitations

The data represent Taiwan in 2005, not current Indian borrowers or modern lending portfolios. Demographic fields are present. Complete a no-demographics sensitivity model and fairness review before any real-world use. Model scores are not separately calibrated probabilities. The 0.50 threshold is technical, not business-approved. No production or external validation has been performed.

## Repository contents

```
app.py
requirements.txt
src/prepare_data.py
src/train_model.py
notebooks/
models/model_metadata.json
reports/
```

The original workbook, customer-level CSV and binary joblib model are not in this GitHub commit. This avoids publishing customer-level data or a large pickle through the text-file publishing route. Download the data from UCI and follow `data/README.md`. The Prediction page stays disabled until the trusted model artifact is added.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

1. Download the UCI Excel workbook; save as `data/default_of_credit_card_clients.xlsx`.
2. Run `python src/prepare_data.py`.
3. Run `python src/train_model.py`.
4. Copy the resulting `models/credit_default_pipeline.joblib` from your local project package (or regenerate it).
5. Run `streamlit run app.py`.

## Deployment

After the binary model artifact is present and locally tested, deploy from [Streamlit Community Cloud](https://share.streamlit.io/): repository `Vineet-singh-01/credit-card-default-prediction`, branch `main`, main file `app.py`. Do not claim deployment until the public app and prediction flow have been tested.

## Five-member work plan

| Member | Lead |
|---|---|
| 1 | Business problem and dataset source |
| 2 | Data audit and EDA |
| 3 | ML development and reproducibility |
| 4 | Evaluation, thresholds, fairness and business interpretation |
| 5 | Streamlit, GitHub, report coordination and deployment |

Every member must understand the complete workflow and be able to defend the decisions. This is an academic prototype, not an approved credit decision system.
