# Project Plan

## Goal

Build a local-first Oura Ring personalization dashboard that helps review recovery, sleep, and training readiness without sending health data to a hosted service.

## MVP

1. Import Oura CSV exports from `data/raw/`.
2. Normalize sleep and readiness records into a predictable internal format.
3. Show daily sleep, readiness, and recovery trends in Streamlit.
4. Generate transparent, non-medical training suggestions.
5. Keep all user health data out of Git.

## Later

- Add OAuth-based Oura API sync.
- Add local SQLite caching.
- Add user-configurable goals such as running, strength, sleep consistency, or recovery.
- Add annotations for workouts, illness, alcohol, travel, and stress.
- Add exports for weekly coaching summaries.

## Non-Goals

- Medical diagnosis or treatment guidance.
- Hosted multi-user service.
- Automatic data sharing.
- Background sync before privacy and OAuth storage are designed.

## Success Criteria

- A user can export Oura CSV data, drop it into `data/raw/`, and view a dashboard.
- The app runs locally with a short setup path.
- The recommendation logic is unit-tested.
- The repo clearly explains data privacy boundaries.
