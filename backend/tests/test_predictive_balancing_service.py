"""Tests for predictive_balancing_service."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.predictive_balancing_service import (
    compute_staff_load_profile,
    detect_fragile_staffing_days,
    detect_repeated_same_person_burden,
    detect_room_bottlenecks,
    recommend_rebalancing,
)


# ── Test helpers ──────────────────────────────────────────────────────────

def _entry(staff=None, date="2026-10-01", room_cap=30, students=20, **kw):
    return {
        "section_id": 1,
        "course_id": "POL101",
        "room": {"id": 1, "capacity": room_cap},
        "num_students": students,
        "assigned_staff": staff if staff is not None else [101, 102],
        "exam_date": date,
        "split_count": 1,
        **kw,
    }


# ── compute_staff_load_profile ────────────────────────────────────────────

def test_profile_empty_schedule():
    result = compute_staff_load_profile([])
    assert result["total_staff"] == 0
    assert result["profiles"] == []


def test_profile_counts_assignments():
    schedule = [_entry(staff=[101]), _entry(staff=[101, 102])]
    result = compute_staff_load_profile(schedule)
    staff_ids = {p["staff_id"] for p in result["profiles"]}
    assert 101 in staff_ids
    assert 102 in staff_ids
    staff_101 = next(p for p in result["profiles"] if p["staff_id"] == 101)
    assert staff_101["total_assignments"] == 2


def test_profile_classification_balanced():
    schedule = [_entry(staff=[101])]  # 1 assignment <= 3
    result = compute_staff_load_profile(schedule)
    assert result["profiles"][0]["classification"] == "balanced"
    assert not result["profiles"][0]["at_risk"]


def test_profile_classification_review():
    # 5 assignments (review_load = 5)
    schedule = [_entry(staff=[101]) for _ in range(5)]
    result = compute_staff_load_profile(schedule)
    staff_101 = next(p for p in result["profiles"] if p["staff_id"] == 101)
    assert staff_101["classification"] == "review"
    assert staff_101["at_risk"]


def test_profile_classification_high_risk():
    # 7 assignments (high_risk_load = 7)
    schedule = [_entry(staff=[101]) for _ in range(7)]
    result = compute_staff_load_profile(schedule)
    staff_101 = next(p for p in result["profiles"] if p["staff_id"] == 101)
    assert staff_101["classification"] == "high_risk"


def test_profile_high_risk_count():
    schedule = [_entry(staff=[101]) for _ in range(7)]
    result = compute_staff_load_profile(schedule)
    assert result["high_risk_count"] == 1


def test_profile_at_risk_count():
    schedule = (
        [_entry(staff=[101]) for _ in range(5)] +  # review
        [_entry(staff=[102])]                        # balanced
    )
    result = compute_staff_load_profile(schedule)
    assert result["at_risk_count"] == 1


def test_profile_max_single_day():
    schedule = [
        _entry(staff=[101], date="2026-10-01"),
        _entry(staff=[101], date="2026-10-01"),
        _entry(staff=[101], date="2026-10-02"),
    ]
    result = compute_staff_load_profile(schedule)
    staff_101 = next(p for p in result["profiles"] if p["staff_id"] == 101)
    assert staff_101["max_single_day"] == 2


def test_profile_ignores_none_staff():
    schedule = [_entry(staff=[None, 101])]
    result = compute_staff_load_profile(schedule)
    assert all(p["staff_id"] is not None for p in result["profiles"])


# ── detect_fragile_staffing_days ──────────────────────────────────────────

def test_fragile_day_single_invigilator():
    schedule = [_entry(staff=[101], date="2026-10-01")]
    fragile = detect_fragile_staffing_days(schedule, min_staff_threshold=2)
    assert len(fragile) == 1
    assert fragile[0]["exam_date"] == "2026-10-01"


def test_no_fragile_day_with_enough_staff():
    schedule = [_entry(staff=[101, 102], date="2026-10-01")]
    fragile = detect_fragile_staffing_days(schedule, min_staff_threshold=2)
    assert fragile == []


def test_fragile_day_unique_staff_counted():
    # Same person assigned twice — still only 1 unique invigilator
    schedule = [
        _entry(staff=[101], date="2026-10-01"),
        _entry(staff=[101], date="2026-10-01"),
    ]
    fragile = detect_fragile_staffing_days(schedule, min_staff_threshold=2)
    assert len(fragile) == 1
    assert fragile[0]["unique_staff_count"] == 1


# ── detect_room_bottlenecks ───────────────────────────────────────────────

def test_room_bottleneck_detected_at_95pct():
    schedule = [_entry(room_cap=30, students=29)]  # 97%
    bottlenecks = detect_room_bottlenecks(schedule, utilization_threshold=0.95)
    assert len(bottlenecks) == 1


def test_room_bottleneck_not_detected_below_threshold():
    schedule = [_entry(room_cap=30, students=20)]  # 67%
    bottlenecks = detect_room_bottlenecks(schedule, utilization_threshold=0.95)
    assert bottlenecks == []


def test_room_bottleneck_skips_no_capacity():
    schedule = [_entry(room_cap=0, students=20)]
    bottlenecks = detect_room_bottlenecks(schedule)
    assert bottlenecks == []


# ── detect_repeated_same_person_burden ────────────────────────────────────

def test_same_day_overload_detected():
    schedule = [
        _entry(staff=[101], date="2026-10-01"),
        _entry(staff=[101], date="2026-10-01"),
        _entry(staff=[101], date="2026-10-01"),  # 3 on same day, max=2
    ]
    overload = detect_repeated_same_person_burden(schedule, same_day_max=2)
    assert len(overload) == 1
    assert overload[0]["staff_id"] == 101
    assert overload[0]["same_day_count"] == 3


def test_no_overload_within_limit():
    schedule = [
        _entry(staff=[101], date="2026-10-01"),
        _entry(staff=[101], date="2026-10-01"),  # 2 = max_day exactly
    ]
    overload = detect_repeated_same_person_burden(schedule, same_day_max=2)
    assert overload == []


# ── recommend_rebalancing ─────────────────────────────────────────────────

def test_recommendations_for_high_risk():
    schedule = [_entry(staff=[101]) for _ in range(7)]
    recs = recommend_rebalancing(schedule)
    high_risk = [r for r in recs if r["severity"] == "HIGH_RISK"]
    assert len(high_risk) >= 1
    assert any(r["staff_id"] == 101 for r in high_risk)


def test_recommendations_for_review():
    schedule = [_entry(staff=[101]) for _ in range(5)]
    recs = recommend_rebalancing(schedule)
    warnings = [r for r in recs if r["severity"] == "WARNING" and r.get("staff_id") == 101]
    assert len(warnings) >= 1


def test_recommendations_for_fragile_day():
    schedule = [_entry(staff=[101], date="2026-10-01")]  # only 1 staff
    recs = recommend_rebalancing(schedule)
    fragile_recs = [r for r in recs if r.get("risk_type") == "FRAGILE_STAFFING_DAY"]
    assert len(fragile_recs) >= 1


def test_recommendations_for_balanced_schedule():
    # 2 staff across 2 days — balanced
    schedule = [
        _entry(staff=[101, 102], date="2026-10-01"),
        _entry(staff=[103, 104], date="2026-10-02"),
    ]
    recs = recommend_rebalancing(schedule)
    high_risk = [r for r in recs if r["severity"] == "HIGH_RISK"]
    assert high_risk == []


def test_recommendations_have_required_keys():
    schedule = [_entry(staff=[101]) for _ in range(7)]
    recs = recommend_rebalancing(schedule)
    for rec in recs:
        assert "severity" in rec
        assert "message" in rec
        assert "action" in rec
        assert "risk_type" in rec
