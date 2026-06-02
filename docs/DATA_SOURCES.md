# Data Sources

## Manual Oura Export

Use the Oura Membership Hub personal data export flow to download CSV data. Place exported CSV files under:

```text
data/raw/
```

The `data/` directory is ignored by Git.

## Oura API

The Oura API v2 base route is:

```text
https://api.ouraring.com/v2/usercollection/
```

Useful endpoints for this project include:

- `daily_sleep`
- `daily_readiness`
- `daily_activity`
- `workout`
- `tag`

Oura's current docs say personal access tokens were deprecated in December 2025. Any live API integration should use OAuth and should store credentials carefully.

## Privacy Rules

- Do not commit raw exports.
- Do not commit `.env` files or Streamlit secrets.
- Prefer local processing before adding a cloud database.
- Treat exported Oura files as sensitive personal data.
