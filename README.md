# Oura Personalization Dashboard

A small starter app for turning Oura Ring data into a personal recovery and training dashboard.

The first version focuses on a local-first workflow:

- Import manually exported Oura CSV data.
- Summarize the latest recovery metrics.
- Generate a simple running recommendation.
- View trends in a Streamlit dashboard.

## Why CSV First?

Oura's current API docs say personal access tokens were deprecated in December 2025 and are no longer available for use. That makes manual export the simplest MVP path while OAuth support is designed properly.

CSV import also keeps the project private by default: your health data can stay on your machine, outside of any hosted database.

## Where the API Fits Later

[`turing-complet/python-ouraring`](https://github.com/turing-complet/python-ouraring) is the natural starting point for Python Oura work. Its README notes that v2 API support exists, but the maintainer is looking for help and the v2 DataFrame/OAuth support is less mature. This repo keeps the API wrapper thin so it can be replaced with `oura.v2.OuraClientV2` later if that becomes the better fit.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dashboard,dev]"
Copy-Item .env.example .env
```

Edit `.env` only if you are experimenting with API access. For CSV-only usage, no token is required.

## Import Oura CSV Data

Export your data from the Oura Membership Hub, then place CSV files under `data/raw/`. The `data/` folder is ignored by Git so personal exports do not get committed.

## Run the CLI

```powershell
oura-dashboard
```

## Run the Dashboard

```powershell
streamlit run src/oura_dashboard/app.py
```

## Privacy Notes

Oura data is health-adjacent personal data. This starter keeps everything local and ignores `.env`, Streamlit secrets, and `data/` so tokens and exports do not get committed by accident.

## Current Scope

This is intentionally an MVP:

- CSV import first.
- OAuth/API support later.
- No database yet.
- No medical claims.
- Recommendation rules are simple and transparent.
