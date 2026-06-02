from pathlib import Path

from oura_dashboard.csv_import import load_oura_csv_records, normalize_csv_row


def test_normalize_csv_row_maps_common_score_fields():
    row = normalize_csv_row(
        {
            "Date": "2026-06-01",
            "Readiness Score": "88",
            "HRV Balance": "82",
        }
    )

    assert row["day"] == "2026-06-01"
    assert row["score"] == 88
    assert row["contributors"]["hrv_balance"] == 82


def test_load_oura_csv_records_filters_by_keyword(tmp_path: Path):
    csv_path = tmp_path / "oura_readiness.csv"
    csv_path.write_text(
        "Date,Readiness Score,HRV Balance\n2026-06-01,88,82\n",
        encoding="utf-8",
    )

    records = load_oura_csv_records(tmp_path, "readiness")

    assert records == [
        {
            "day": "2026-06-01",
            "readiness_score": 88,
            "hrv_balance": 82,
            "score": 88,
            "contributors": {"hrv_balance": 82},
        }
    ]
