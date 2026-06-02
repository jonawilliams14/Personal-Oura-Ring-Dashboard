from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RecoverySnapshot:
    day: str
    readiness_score: int | None
    sleep_score: int | None
    total_sleep_hours: float | None
    hrv_balance: int | None
    recommendation_level: str
    recommendation: str


def latest_recovery_snapshot(
    readiness_data: list[dict[str, Any]],
    sleep_data: list[dict[str, Any]],
) -> RecoverySnapshot:
    if not readiness_data:
        raise ValueError("readiness_data must contain at least one record")
    if not sleep_data:
        raise ValueError("sleep_data must contain at least one record")

    latest_readiness = sorted(readiness_data, key=lambda item: item["day"])[-1]
    sleep_by_day = {item.get("day"): item for item in sleep_data}
    latest_sleep = sleep_by_day.get(
        latest_readiness.get("day"), sorted(sleep_data, key=lambda item: item["day"])[-1]
    )

    total_sleep_seconds = (
        latest_sleep.get("contributors", {}).get("total_sleep")
        or latest_sleep.get("total_sleep_duration")
    )
    total_sleep_hours = (
        round(total_sleep_seconds / 3600, 2) if total_sleep_seconds else None
    )

    readiness_score = latest_readiness.get("score")
    sleep_score = latest_sleep.get("score")
    hrv_balance = latest_readiness.get("contributors", {}).get("hrv_balance")
    level, recommendation = running_recommendation(
        readiness_score=readiness_score,
        total_sleep_hours=total_sleep_hours,
    )

    return RecoverySnapshot(
        day=latest_readiness.get("day", "unknown"),
        readiness_score=readiness_score,
        sleep_score=sleep_score,
        total_sleep_hours=total_sleep_hours,
        hrv_balance=hrv_balance,
        recommendation_level=level,
        recommendation=recommendation,
    )


def running_recommendation(
    readiness_score: int | None,
    total_sleep_hours: float | None,
) -> tuple[str, str]:
    if readiness_score is None or total_sleep_hours is None:
        return (
            "unknown",
            "Not enough data for a training call. Keep the day flexible until Oura syncs.",
        )

    if readiness_score >= 85 and total_sleep_hours >= 7.5:
        return (
            "optimal",
            "Great day for a harder session if it matches your plan.",
        )

    if readiness_score >= 70 and total_sleep_hours >= 7.0:
        return (
            "moderate",
            "Proceed with the planned run, but keep pacing honest and avoid forcing intensity.",
        )

    return (
        "fatigue",
        "Bias toward recovery, mobility, walking, or an easy Zone 2 effort.",
    )
