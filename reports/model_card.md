# Model card – preliminary academic prototype

- Model: Random Forest with preprocessing pipeline.
- Dataset: UCI Default of Credit Card Clients (Taiwan, 2005).
- Rows: 30,000; predictors: 23; target: `default payment next month`.
- ID excluded. SEX, EDUCATION and MARRIAGE one-hot encoded; other fields handled as numeric in this initial version.
- Split: 21,600 training / 2,400 validation / 6,000 held-out test.
- Candidate selection: validation default-class F1, ROC-AUC tie-break.
- Threshold: 0.50 (technical default).
- Test accuracy: 0.793; default precision: 0.532; default recall: 0.544; default F1: 0.538; ROC-AUC: 0.774; average precision: 0.552.
- Confusion matrix TN/FP/FN/TP: 4037/636/605/722.

## Not approved for production
Scores are not separately calibrated. Threshold economics are not approved. Demographic features are present. A no-demographics sensitivity model, fairness assessment, current external validation and human oversight are required before any operational use.
