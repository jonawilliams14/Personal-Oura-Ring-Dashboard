# Contributing

Thanks for improving the Oura Personalization Dashboard.

## Local Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dashboard,dev]"
pytest
```

## Guidelines

- Keep changes small and focused.
- Do not commit personal Oura exports, tokens, or screenshots containing private health data.
- Add or update tests when changing recommendation logic.
- Keep recommendations transparent and non-medical.

## Data Safety

Use synthetic or anonymized data in tests and documentation. Do not include real Oura exports in the repository.
