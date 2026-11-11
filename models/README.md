# Model artifact

The selected preliminary Random Forest pipeline is generated locally as `credit_default_pipeline.joblib`; it includes preprocessing and estimator. Recreate it using `python src/train_model.py` after preparing the data.

The binary artifact is not included in this GitHub text commit. The app keeps Prediction disabled until the trusted artifact and metadata are present. Do not deploy the Prediction page before loading and testing the model.

The score is not separately calibrated. Joblib/pickle should only load trusted files because deserialisation can execute code.
