# Dataset audit, EDA and preliminary modelling

## Dataset audit
- Workbook: `Untitled spreadsheet.xlsx`; sheet `Data`; 30,000 rows and 25 columns.
- Actual field names are on spreadsheet row 2; row 1 contains generic X1–X23/Y labels.
- 23 predictors, one ID (excluded), and target `default payment next month`.
- Missing cells: 0; exact duplicate rows: 0; unique IDs: 30,000.
- Target: 0=23,364 (77.88%); 1=6,636 (22.12%).

## Observed EDA
- PAY_0=2 group: 2,667 customers and 69.14% observed default rate.
- PAY_0=0 group: 14,737 customers and 12.81% observed default rate.
- Credit limit <=50k: 7,676 customers and 31.79% observed default rate; >300k: 4,563 and 13.26%.
- The PAY_0 codes 5–8 are rare; their rates should not be over-interpreted.
- These are descriptive associations, not causal findings.

## Validation comparison
| Model | Default precision | Default recall | Default F1 | ROC-AUC |
|---|---:|---:|---:|---:|
| Logistic Regression | 0.702 | 0.271 | 0.391 | 0.712 |
| Decision Tree | 0.467 | 0.554 | 0.507 | 0.757 |
| Random Forest | 0.523 | 0.550 | 0.536 | 0.785 |

Selected Random Forest using validation default-class F1, ROC-AUC tie-break.

## Held-out test – Random Forest, threshold 0.50
- Accuracy 0.793; default precision 0.532; default recall 0.544; default F1 0.538.
- ROC-AUC 0.774; average precision 0.552; Brier score 0.156.
- TN=4,037; FP=636; FN=605; TP=722.

## Limitations
The 0.50 cutoff is not business-approved. Probability calibration is incomplete. The data are from Taiwan in 2005 and should not be generalised to current Indian borrowers. Demographic attributes are present; no-demographics sensitivity modelling and fairness review remain required.
