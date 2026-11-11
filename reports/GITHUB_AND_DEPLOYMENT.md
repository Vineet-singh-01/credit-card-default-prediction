# GitHub and Streamlit deployment

Repository: https://github.com/Vineet-singh-01/credit-card-default-prediction

The source, notebooks, audit, metrics, reports, metadata and trained model artifact are now published on `main`. The raw workbook and customer-level CSV are intentionally excluded from the public repository.

## Verified model artifact
The latest GitHub Actions run completed successfully and generated `models/credit_default_pipeline.joblib`. It is approximately 19.4 MB. The workflow is reproducible from the official UCI source. Confirm the app can load it during deployment.

## Deploy
1. Open https://share.streamlit.io/ and sign in with GitHub.
2. In your workspace, choose **Create app** and select **Yup, I have an app**.
3. Repository: `Vineet-singh-01/credit-card-default-prediction`.
4. Branch: `main`.
5. Main file path: `app.py`.
6. Choose an optional memorable subdomain, then click **Deploy**.
7. Check build logs. Open the public app and test Business Overview, Data Insights, and a sample Prediction.
8. Add the live URL to README only after the public-browser test succeeds.

The application uses no secrets. Never commit tokens or credentials.

The Prediction result is an uncalibrated model score; it is not a validated probability of default and must not drive automated adverse action. See `reports/model_card.md`.
