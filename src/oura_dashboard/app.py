from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from oura_dashboard.analysis import latest_recovery_snapshot
from oura_dashboard.client import OuraClient, OuraConfigurationError
from oura_dashboard.csv_import import load_oura_csv_records


def main() -> None:
    load_dotenv()
    st.set_page_config(page_title="Oura Dashboard", layout="wide")
    st.title("Oura Personalization Dashboard")

    source = st.sidebar.radio("Data source", ["CSV", "API"])
    if source == "CSV":
        data_dir = Path(st.sidebar.text_input("Data directory", "data/raw"))
        readiness = load_oura_csv_records(data_dir, "readiness")
        sleep = load_oura_csv_records(data_dir, "sleep")
    else:
        lookback_days = st.sidebar.slider("Lookback days", 3, 60, 14)
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days)

        try:
            client = OuraClient.from_env()
        except OuraConfigurationError as exc:
            st.error(str(exc))
            st.stop()

        with st.spinner("Fetching Oura data..."):
            readiness = client.fetch_collection("daily_readiness", start_date, end_date)
            sleep = client.fetch_collection("daily_sleep", start_date, end_date)

    if not readiness or not sleep:
        st.warning("Add Oura CSV exports under data/raw or switch to API mode.")
        st.stop()

    snapshot = latest_recovery_snapshot(readiness, sleep)
    metrics = st.columns(4)
    metrics[0].metric("Readiness", snapshot.readiness_score)
    metrics[1].metric("Sleep", snapshot.sleep_score)
    metrics[2].metric("Sleep Hours", snapshot.total_sleep_hours)
    metrics[3].metric("HRV Balance", snapshot.hrv_balance)

    st.subheader(snapshot.recommendation_level.title())
    st.write(snapshot.recommendation)

    readiness_df = pd.DataFrame(readiness)
    sleep_df = pd.DataFrame(sleep)

    chart_data = readiness_df[["day", "score"]].rename(
        columns={"score": "readiness_score"}
    )
    chart_data = chart_data.merge(
        sleep_df[["day", "score"]].rename(columns={"score": "sleep_score"}),
        on="day",
        how="outer",
    ).sort_values("day")

    st.plotly_chart(
        px.line(
            chart_data,
            x="day",
            y=["readiness_score", "sleep_score"],
            markers=True,
        ),
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
