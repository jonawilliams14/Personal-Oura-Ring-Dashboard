from oura_dashboard.analysis import latest_recovery_snapshot, running_recommendation


def test_running_recommendation_optimal():
    level, recommendation = running_recommendation(90, 8.0)

    assert level == "optimal"
    assert "harder session" in recommendation


def test_running_recommendation_moderate_requires_both_signals():
    level, _ = running_recommendation(75, 7.1)

    assert level == "moderate"


def test_running_recommendation_fatigue_when_sleep_is_low():
    level, _ = running_recommendation(75, 6.5)

    assert level == "fatigue"


def test_latest_recovery_snapshot_matches_sleep_by_day():
    snapshot = latest_recovery_snapshot(
        readiness_data=[
            {"day": "2026-05-31", "score": 70, "contributors": {}},
            {"day": "2026-06-01", "score": 88, "contributors": {"hrv_balance": 82}},
        ],
        sleep_data=[
            {
                "day": "2026-05-31",
                "score": 72,
                "contributors": {"total_sleep": 6 * 3600},
            },
            {
                "day": "2026-06-01",
                "score": 91,
                "contributors": {"total_sleep": 8 * 3600},
            },
        ],
    )

    assert snapshot.day == "2026-06-01"
    assert snapshot.sleep_score == 91
    assert snapshot.total_sleep_hours == 8
    assert snapshot.recommendation_level == "optimal"
