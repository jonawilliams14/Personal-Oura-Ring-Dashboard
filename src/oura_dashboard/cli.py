from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

from oura_dashboard.analysis import latest_recovery_snapshot
from oura_dashboard.client import OuraClient
from oura_dashboard.csv_import import load_oura_csv_records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["csv", "api"], default="csv")
    parser.add_argument("--data-dir", default="data/raw")
    args = parser.parse_args()

    load_dotenv()

    if args.source == "csv":
        data_dir = Path(args.data_dir)
        readiness = load_oura_csv_records(data_dir, "readiness")
        sleep = load_oura_csv_records(data_dir, "sleep")
    else:
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        client = OuraClient.from_env()
        readiness = client.fetch_collection("daily_readiness", start_date, end_date)
        sleep = client.fetch_collection("daily_sleep", start_date, end_date)

    snapshot = latest_recovery_snapshot(readiness, sleep)

    print(f"Latest Oura metrics for {snapshot.day}")
    print(f"Readiness: {snapshot.readiness_score}")
    print(f"Sleep: {snapshot.sleep_score}")
    print(f"Total sleep hours: {snapshot.total_sleep_hours}")
    print(f"HRV balance: {snapshot.hrv_balance}")
    print(f"Recommendation: {snapshot.recommendation_level}")
    print(snapshot.recommendation)


if __name__ == "__main__":
    main()
