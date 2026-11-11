# GitHub and Streamlit deployment

Repository: https://github.com/Vineet-singh-01/credit-card-default-prediction

The public repository includes updated Streamlit source, preprocessing/training scripts, dataset audit summaries, test metrics, notebooks, project report draft, and trained model artifact. The raw workbook and cleaned customer-level CSV remain excluded from the public repository.

## Updated application
The app uses the group's uploaded `app.py`. It includes human-readable dropdowns, synthetic demonstration profiles, reset, repayment history, bill/payment inputs, profile diagnostics, illustrative score bands, threshold exploration and downloadable assessment CSV. The Data Insights page handles the `n`/ `count` audit schema difference and displays grouped repayment/segment patterns plus validation feature diagnostics.

## Deploy
1. Open https://share.streamlit.io/ and sign in with GitHub.
2. Create an app from repository `Vineet-singh-01/credit-card-default-prediction`.
3. Branch: `main`.
4. Main file: `app.py`.
5. In Advanced settings, select Python 3.11 to match the model-build environment.
6. Deploy and check build logs.
7. Test Business Overview, every Data Insights tab, all three synthetic quick profiles, manual input changes, reset-all, threshold slider and CSV export.
8. Share the public URL only after the hosted app passes these checks.

No secrets are required. Never commit credentials.

## Limitations
The prediction score is not separately calibrated. The score categories are illustrative only; the 0.50 threshold is a technical cutoff, not bank policy. The historical Taiwan 2005 dataset is not validated for current Indian borrowers. Demographic features are present, so a no-demographics sensitivity model, fairness review, calibration and current external validation remain necessary before any operational use. Human review is required.
