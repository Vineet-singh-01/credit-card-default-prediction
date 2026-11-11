# Model artifact

The preliminary Random Forest pipeline `credit_default_pipeline.joblib` has been generated successfully by the GitHub Actions workflow and is present in this directory. It contains the fitted preprocessing and estimator. Metadata and held-out test metrics are recorded in `model_metadata.json` and `../reports/final_test_metrics.json`.

To reproduce the artifact, run `python src/prepare_data.py` and `python src/train_model.py` after obtaining the UCI workbook.

**Important limitations:** the score is not separately calibrated, and the 0.50 threshold is a technical default rather than a business-approved cutoff. The model is for academic demonstration and human-review support only.

Only load joblib artifacts from trusted sources because deserialisation can execute code.
