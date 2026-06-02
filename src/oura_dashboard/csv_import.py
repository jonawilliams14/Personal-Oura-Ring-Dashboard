from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def load_oura_csv_records(data_dir: Path, keyword: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(data_dir.glob(f"*{keyword}*.csv")):
        with path.open(newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                normalized = normalize_csv_row(row)
                if normalized.get("day"):
                    records.append(normalized)
    return records


def normalize_csv_row(row: dict[str, str]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in row.items():
        field = normalize_field_name(key)
        if field in {"date", "timestamp"}:
            field = "day"
        normalized[field] = parse_value(value)

    if "score" not in normalized:
        for candidate in ("readiness_score", "sleep_score"):
            if candidate in normalized:
                normalized["score"] = normalized[candidate]
                break

    if "contributors_total_sleep" in normalized:
        normalized.setdefault("contributors", {})["total_sleep"] = normalized[
            "contributors_total_sleep"
        ]

    if "hrv_balance" in normalized:
        normalized.setdefault("contributors", {})["hrv_balance"] = normalized[
            "hrv_balance"
        ]

    return normalized


def normalize_field_name(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(".", "_")
    )


def parse_value(value: str | None) -> Any:
    if value is None:
        return None

    stripped = value.strip()
    if not stripped:
        return None

    try:
        as_float = float(stripped)
    except ValueError:
        return stripped

    if as_float.is_integer():
        return int(as_float)
    return as_float
