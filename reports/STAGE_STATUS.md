# Project stage tracker

| Stage | Status | Notes |
|---|---|---|
| 1. Project selection | Complete | Credit-card default prediction |
| 2. Dataset verification | Complete | User-provided workbook inspected |
| 3. Business problem | Draft complete | Early-warning human-review decision support |
| 4. Data audit | Complete | 30,000 rows; 0 missing; 0 duplicate rows |
| 5. EDA | Initial complete | Class balance, PAY_0, credit-limit, age patterns |
| 6. Model development | Initial complete | Logistic Regression, Decision Tree, Random Forest |
| 7. Model evaluation | Initial complete | Random Forest evaluated on held-out 6,000 records |
| 8. Model saving | Local artifact prepared | Joblib available in local project archive; not published to GitHub |
| 9. Streamlit | Source published | Prediction requires binary model artifact |
| 10. GitHub | Source and reports published | Raw workbook/CSV and model binary excluded |
| 11. Documentation | Drafts published | Group review and final writing needed |
| 12. Cloud deployment | Pending | Add model artifact, then deploy and smoke test |
| 13. Viva | Prep pack included | All members should rehearse all stages |

## Required extensions
1. Test alternative thresholds on validation data using a documented cost matrix.
2. Compare a model excluding demographic features.
3. Evaluate probability calibration.
4. Review subgroup error metrics and discuss limitations.
5. Do not tune against the held-out test set.
