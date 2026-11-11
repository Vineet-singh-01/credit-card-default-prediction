# CreditRisk Analytics — React + FastAPI upgrade

This folder is an **upgrade overlay** for the existing `Vineet-singh-01/credit-card-default-prediction` repository. It adds a React dashboard and a REST API around the existing trained Random Forest pipeline.

> **Do not remove or retrain the existing model.** Keep the original `models/credit_default_pipeline.joblib`, `models/model_metadata.json`, `reports/`, `src/`, root Streamlit `app.py`, and existing `.gitignore`. Copy the `backend/`, `frontend/`, and `tests/` folders from this package into the existing repository. Append the entries in `GITIGNORE_ADDITIONS.txt` to the existing root `.gitignore` rather than replacing it. The root Streamlit app remains available as a legacy interface.

## 1. Existing ML integration

The API loads these existing project assets from the repository root:

- `models/credit_default_pipeline.joblib`
- `models/model_metadata.json`
- `reports/dataset_audit.json`
- `reports/final_test_metrics.json`
- `reports/validation_model_comparison.json`
- `reports/threshold_tradeoff_validation.csv`

Prediction requests are validated against the original 23 predictor fields. The API reads `feature_names` and `categorical_features` from model metadata, orders the fields exactly as trained, converts `SEX`, `EDUCATION`, and `MARRIAGE` to string category codes, and sends the resulting object array to the saved pipeline. It does not change the model, preprocessing, or model weights.

No image-upload feature is included because this is a tabular customer-risk project. The frontend uses the 23 structured profile fields expected by the existing classifier.

## 2. Project structure after merging

```text
credit-card-default-prediction/
├── app.py                              # existing Streamlit interface; retained
├── backend/
│   ├── __init__.py
│   ├── main.py                          # FastAPI REST API
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   └── src/
│       ├── components/
│       ├── layouts/
│       ├── pages/
│       ├── services/
│       ├── App.jsx
│       ├── main.jsx
│       └── index.css
├── models/                              # existing saved model + metadata
├── reports/                             # existing audit, evaluation and CSV files
├── src/                                 # existing data prep / training scripts
└── tests/
    └── test_backend.py
```

## 3. Requirements

- Python 3.11 recommended, matching the original model-build workflow.
- Node.js 20.19+ or 22.12+ for Vite 8.
- npm 10+.
- The existing committed `models/credit_default_pipeline.joblib` must be present at the project root before a real prediction can run.

The frontend package uses React 19, Vite 8, React Router DOM 7, Recharts 3, Lucide React, Motion for React, and Tailwind CSS 4. The corresponding package versions are declared in `frontend/package.json`.

## 4. Run locally (two terminals)

### Terminal A — Python API

From the repository root:

**Windows PowerShell**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**macOS / Linux**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

API health: <http://127.0.0.1:8000/api/health>  
Interactive API docs: <http://127.0.0.1:8000/docs>

### Terminal B — React frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` calls to `http://127.0.0.1:8000` during local development.

### Optional separate API URL

If the API is hosted on a different origin, copy `frontend/.env.example` to `frontend/.env` and set:

```env
VITE_API_URL=https://your-api-host.example.com
```

Set the backend environment variable `CORS_ORIGINS` to the exact frontend origin(s), comma-separated. Never use wildcard origins with credentials or expose a backend URL that stores real customer data without authentication and access controls.

## 5. Run tests and build

From the repository root, install the test-only dependencies once:

```bash
pip install -r backend/requirements-dev.txt
python -m pytest -q
```

For runtime-only deployment, `backend/requirements.txt` is sufficient.

Build the frontend:

```bash
cd frontend
npm run build
npm run preview
```

The backend tests verify feature ordering and categorical-code conversion, audit schema compatibility (`n` and `count`), diagnostic calculations, score-band boundaries, class-1 score handling, and the prediction/history API lifecycle using a test double. They do **not** replace a real-model integration test. The live prediction check must be run against the existing saved `.joblib` artifact after merging.

## 6. API routes

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API, model, metadata and report availability |
| GET | `/api/config` | Human-readable category and month labels |
| GET | `/api/overview` | Project KPIs and recent real assessments |
| GET | `/api/insights` | Actual grouped dataset-audit summaries |
| GET | `/api/performance` | Held-out metrics, validation comparisons and threshold trade-off data |
| POST | `/api/predictions` | Validate profile, run saved model, and save result |
| GET | `/api/predictions/history` | List actual predictions saved by this API instance |
| GET | `/api/predictions/{id}` | Retrieve one saved assessment and its inputs |
| DELETE | `/api/predictions/history` | Clear local prediction history |
| GET | `/api/metadata` | Safe model metadata summary (no model binary) |

Prediction history is stored in `backend/data/prediction_history.sqlite3`. It records input profiles and model scores locally so the Results and History pages can be revisited. It does not collect names, email addresses, account numbers, or other customer identifiers. The local SQLite file is ignored by Git.

## 7. Frontend pages

1. **Overview** — audited dataset KPIs, test metrics, class distribution and recent API-generated assessments.
2. **Risk assessment** — all 23 original model inputs, readable dropdown labels, synthetic input presets and a live model request.
3. **Assessment results** — uncalibrated model score, illustrative score band, technical threshold flag, profile diagnostics and CSV export.
4. **Data insights** — observed repayment, credit-limit, age and education patterns plus validation permutation importance.
5. **Model performance** — real held-out metrics, confusion matrix, validation candidate comparison and threshold trade-off.
6. **Prediction history** — searchable and filterable records created by actual prediction requests.
7. **About the project** — dataset, methodology, model workflow and limitations.

There is a responsive sidebar, mobile navigation drawer, light/dark theme toggle, loading/error/empty states, page transitions, chart tooltips and CSV exports.

## 8. Data integrity and interpretation

- The application does not generate sample predictions in the browser. Demo buttons only populate synthetic input values; a real API request is still required to run the saved model.
- Total prediction count and history come from the local SQLite database and begin at zero on a clean installation.
- Data-insight charts use the existing `reports/dataset_audit.json`; evaluation charts use the existing metric/validation reports. Missing files or sections are shown as unavailable, not filled with fabricated values.
- Confusion-matrix cells are read from `final_test_metrics.json` (TN, FP, FN, TP).
- The API returns the saved model's class-1 output as an **uncalibrated model score**, not a verified probability of default.
- Illustrative score bands are interface aids only. The saved technical threshold is distinct and is not an approved banking policy.
- Group charts are descriptive associations, not causal explanations. Profile indicators are calculations from inputs, not feature attribution.

## 9. Deployment guidance

A common split deployment is:

- **Frontend:** Vercel, Netlify, or another static hosting provider. Set `VITE_API_URL` to the deployed API URL before building.
- **Backend:** Render, Railway, or another Python host. Install `backend/requirements.txt`, start with `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`, and ensure the root model and reports directories are included in the deployment image.

SQLite data is ephemeral on many application hosts unless a persistent disk is configured. For multi-user or production deployment, use a managed database, authentication, role-based access control, audit/retention policy, secret management, TLS, rate limiting, and monitoring. Do not store real customer financial information in this academic prototype.

## 10. Legacy Streamlit interface

The original Streamlit application is not overwritten. From the repository root, it can still be run with:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The React + FastAPI application is a separate frontend/backend path. This avoids disrupting the existing Streamlit deployment while the new experience is tested.

## 11. Existing model limitations

The underlying dataset describes Taiwanese credit-card clients in 2005. It is not validated for current Indian credit portfolios. The saved Random Forest contains demographic attributes, scores are not separately calibrated, and the 0.50 cutoff is technical rather than business-approved. The model card and existing project documentation should be consulted before interpreting metrics. This project is an academic prototype and must not make automated approval, rejection, pricing, collections, or other adverse decisions.


## React + FastAPI application (new interface)

A separate React dashboard and FastAPI service are available alongside the legacy Streamlit app. This upgrade wraps the existing saved model; it does not retrain or replace it.

### Architecture

- **Frontend:** React 19, Vite, React Router, Tailwind CSS 4, Recharts, Lucide React, and Motion.
- **API:** FastAPI REST service in `backend/main.py`.
- **Model:** Existing `models/credit_default_pipeline.joblib` and `models/model_metadata.json`.
- **Reports:** Existing audit, held-out metrics, validation comparison, and threshold trade-off files under `reports/`.
- **History:** Local SQLite database at `backend/data/prediction_history.sqlite3`.

### Run the API (Terminal 1)

Use Python 3.11 to match the model-build environment. From the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

On macOS/Linux, create and activate the environment with `python3.11 -m venv .venv` and `source .venv/bin/activate` instead. API health is available at `http://127.0.0.1:8000/api/health`; interactive docs are at `http://127.0.0.1:8000/docs`.

### Run the React frontend (Terminal 2)

Requires Node.js 20.19+ or 22.12+ and npm. From the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` requests to the local FastAPI service on port 8000. To use a separately hosted API, copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_URL` to its base URL; configure `CORS_ORIGINS` on the backend to allow the exact frontend origin.

### Test and build

From the repository root, install the development test dependencies and run the backend/API checks:

```bash
pip install -r backend/requirements-dev.txt
python -m pytest -q
```

Build the frontend:

```bash
cd frontend
npm install
npm run build
```

The GitHub Actions workflow `.github/workflows/react-app-check.yml` runs the backend tests including real saved-model smoke tests, and builds the React production bundle. Real-model tests are skipped in source-only workspaces where the committed `.joblib` artifact is unavailable; in the repository CI, the artifact is required.

### New React pages

1. **Overview:** dataset KPIs, test metrics, outcome distribution, and recent real assessments.
2. **Risk assessment:** all 23 original model inputs with readable categorical descriptions and synthetic form presets.
3. **Assessment results:** saved model score, illustrative score band, separate technical threshold flag, profile diagnostics, and CSV export.
4. **Data insights:** historical repayment, credit-limit, age, and education breakdowns plus validation permutation importance.
5. **Model performance:** held-out metrics, confusion matrix, validation model comparison, and threshold trade-offs.
6. **Prediction history:** local history of real API-generated requests with search, filters, detail view, and export.
7. **About:** data, model workflow, architecture, and responsible-use limitations.

### Data integrity and responsible use

The frontend does not generate fake prediction results. Demo profiles only populate the form; a prediction is saved only after the API calls the committed model. Metrics and group-level charts read the existing reports. The API preserves the model metadata feature order and converts `SEX`, `EDUCATION`, and `MARRIAGE` into the string categories used by the original training pipeline.

Prediction scores are uncalibrated model outputs, not verified probabilities of default. Score bands are illustrative UI labels. The technical 0.50 cutoff is not approved banking policy. Data are from Taiwanese customers in 2005 and are not validated for current Indian credit portfolios. Do not use this academic prototype for automated approval, rejection, pricing, collection, or other adverse customer decisions. The local history database stores submitted numeric profiles; do not submit real customer data without authentication, access controls, encryption, retention rules, and appropriate governance.

The original root-level `app.py` and Streamlit workflow remain available and unchanged.
