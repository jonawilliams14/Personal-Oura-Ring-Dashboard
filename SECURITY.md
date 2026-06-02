# Security Policy

## Sensitive Data

This project may process health-adjacent personal data from Oura exports or the Oura API. Treat the following as sensitive:

- Oura CSV exports.
- API access tokens.
- OAuth refresh tokens.
- Streamlit secrets.
- Screenshots that reveal personal health trends.

## Reporting Issues

If you find a security or privacy issue, avoid posting real tokens or health data in a public issue. Open a minimal report describing the behavior and use synthetic examples.

## Current Security Posture

- `.env`, Streamlit secrets, and `data/` are ignored by Git.
- The MVP is local-first.
- OAuth support is deferred until credential storage is designed.
