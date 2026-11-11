# Credit Card Default Prediction Using Machine Learning

**MBA Business Analytics group project | Finance & Banking | Work in progress**

## Project overview

This project will develop a machine-learning decision-support prototype to estimate whether a credit-card customer is likely to default on the next month's payment. The work connects financial risk analysis, exploratory data analysis, supervised classification, model evaluation, and an interactive Streamlit application.

The system is intended to support credit-risk review. A model score is not, by itself, a credit approval, rejection, or collections decision; any operational decision would require human review and appropriate fairness, privacy, and governance controls.

## Dataset

We have selected the **Default of Credit Card Clients** dataset from the UCI Machine Learning Repository.

- **Official source:** https://archive.ics.uci.edu/dataset/350/default%2Bof%2Bcredit%2Bcard%2Bclients
- **Dataset DOI:** https://doi.org/10.24432/C55S3H
- **Source-reported records:** 30,000
- **Predictors:** 23 explanatory variables, plus a customer ID field
- **Target:** `default payment next month` (1 = default; 0 = no default)
- **Task:** Supervised binary classification
- **Context:** Historical credit-card data from Taiwan, covering 2005.

The dataset is historical and geographically specific. Results must not be presented as representative of current Indian borrowers or today's lending market. Refer to the UCI source for the dataset description, variable definitions, and licence terms. Attribution will be retained in project documentation.

## Project objectives

1. Understand the credit-risk business problem and dataset.
2. Inspect and prepare the data, documenting quality checks and leakage risks.
3. Explore repayment behaviour and customer-level patterns through EDA.
4. Establish an interpretable baseline and compare suitable classification models.
5. Evaluate model performance using metrics relevant to default detection and business error costs.
6. Save a reproducible preprocessing-and-model pipeline.
7. Build a three-page Streamlit application: Business Overview, Data Insights, and Prediction.
8. Document the work and deploy the application for demonstration.

## Planned workflow

Business problem → dataset verification → data preparation → EDA → feature engineering → model training → evaluation → business interpretation → model persistence → Streamlit → GitHub → cloud deployment.

## Repository structure

```text
credit-card-default-prediction/
├── data/                 # Dataset guidance; data files handled separately
├── notebooks/            # Data inspection, EDA, and model development
├── models/               # Evaluated model artefacts (added after training)
├── images/               # Project visualisations and application screenshots
├── app.py                # Streamlit application (to be developed)
├── requirements.txt      # Verified project dependencies (to be added)
├── README.md
└── .gitignore
```

## Current status

- [x] Business problem selected
- [x] UCI dataset selected
- [ ] Download and inspect the actual dataset
- [ ] Complete data-quality checks and cleaning
- [ ] Complete EDA and business interpretation
- [ ] Train and compare baseline and candidate models
- [ ] Evaluate model and select decision threshold
- [ ] Save and test the fitted pipeline
- [ ] Develop and test Streamlit pages
- [ ] Finalise dependencies and documentation
- [ ] Deploy and verify the live application

No model has been trained yet. No model-performance figures or dataset-specific business findings are claimed in this repository at this stage.

## Tools planned

Python, Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn, Joblib, and Streamlit. The final dependency list and versions will be recorded after the implementation environment is tested.

## Academic use and limitations

This is an educational prototype, not a production credit-scoring system. Model performance may be affected by historical context, population differences, class imbalance, data limitations, and changes in credit behaviour. Predictions should be interpreted alongside validation results, fairness assessment, and human judgement.

## Team

MBA Business Analytics group project (5 members). Team member names and individual contributions can be added by the group.

## Running the application

The application is not available yet. Instructions will be added after `app.py`, the evaluated model pipeline, and the dependency file have been developed and tested.
