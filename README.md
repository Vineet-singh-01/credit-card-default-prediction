# Credit Card Default Prediction – CreditRisk Analytics

MBA Business Analytics project: estimate next-month credit-card default risk as a **human-review decision-support signal**, not an automated credit decision.

**Dataset:** UCI Default of Credit Card Clients · [UCI dataset page](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients) · DOI [10.24432/C55S3H](https://doi.org/10.24432/C55S3H) · CC BY 4.0.

## Verified dataset audit

The user-provided workbook was inspected. It contains 30,000 observations and 25 columns: ID, 23 predictors and target `default payment next month`. Actual field names are on spreadsheet row 2; row 1 contains generic X1–X23/Y labels.

- Missing cells: **0**
- Exact duplicate rows: **0**
- Unique IDs: **30,000**
- No default (0): **23,364 (77.88%)**
- Default (1): **6,636 (22.12%)**
- ID excluded from predictors.

## Preliminary held-out test results

Candidates were compared on a validation set. Random Forest was selected using default-class F1 (ROC-AUC tie-break), refitted on the 24,000-record development set, and evaluated once on a separate 6,000-record test set. Threshold: 0.50.

| Metric | Test result |
|---|---:|
| Accuracy | 79.32% |
| Precision – default | 53.17% |
| Recall – default | 54.41% |
| F1 – default | 0.538 |
| ROC-AUC | 0.774 |
| Average precision | 0.552 |
| Brier score | 0.156 |

Confusion matrix: TN=4,037, FP=636, FN=605, TP=722. At this cutoff, the model misses 45.6% of actual defaulters. A financial institution must not use this cutoff without an explicit cost analysis.

## EDA observations (association, not causation)

- Default class is 22.12%; accuracy alone is inadequate.
- PAY_0=2 has 69.14% observed default rate (2,667 accounts); PAY_0=0 has 12.81% (14,737 accounts). Rare codes have small samples.
- The <=50k credit-limit band has 31.79% observed default rate; >300k has 13.26%.
- These associations do not establish causal effects.

## Limitations and responsible use

The data represent Taiwan in 2005, not current Indian borrowers. Demographic fields are present. Complete a no-demographics sensitivity model and fairness review before any real use. Scores are not separately calibrated probabilities. The 0.50 threshold is technical, not business-approved. No production or recent external validation has been performed.

## Repository contents

```
app.py
requirements.txt
src/prepare_data.py
src/train_model.py
notebooks/
models/model_metadata.json
reports/
.github/workflows/build-model.yml
```

The raw workbook, customer-level CSV and binary joblib model are not in this public text commit. The model-build workflow can reproduce the artifact from the official UCI source. Do not publish the customer-level dataset. The Prediction page remains disabled until the trusted model artifact is added.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

1. Download the UCI workbook to `data/` (either `default of credit card clients.xls` or `default_of_credit_card_clients.xlsx`).
2. Run `python src/prepare_data.py`.
3. Run `python src/train_model.py`.
4. Run `streamlit run app.py`.

## Generate the model in GitHub Actions

The workflow `.github/workflows/build-model.yml` is manually triggered. In GitHub, open **Actions → Build and publish credit-risk model → Run workflow** on the `main` branch. It downloads the official UCI workbook, recreates the CSV and model, then commits the model artifact and updated metadata. Check that the run succeeds before deploying.

## Streamlit deployment

After the model artifact is present on `main`, deploy on [Streamlit Community Cloud](https://share.streamlit.io/): repository `Vineet-singh-01/credit-card-default-prediction`, branch `main`, main file `app.py`. Test all three pages and a sample prediction. Add the live URL only after successful public-browser testing.

## Five-member work plan

| Member | Lead |
|---|---|
| 1 | Business case and data source |
| 2 | Data audit and EDA |
| 3 | ML development |
| 4 | Evaluation, threshold, fairness and business interpretation |
| 5 | Streamlit, GitHub and deployment |

All members should understand the full workflow and defend each decision. This is an academic prototype, not an approved credit decision system.
