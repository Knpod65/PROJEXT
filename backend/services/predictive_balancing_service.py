"""Predictive workload balancing service.

Analyzes an already-generated schedule to detect workload imbalance RISK
before the recheck runs. Outputs structured recommendations without invoking
the solver.

All heuristics are deterministic — no randomness, no ML, no training data.
Thresholds are read from policies.optimization_policy.STAFFING_RISK_THRESHOLDS
(never duplicated here).
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable


def _staffing_thresholds() -> dict[str, int]:
    from policies.optimization_policy import STAFFING_RISK_THRESHOLDS
    return STAFFING_RISK_THRESHOLDS


# ── Staff load profile ────────────────────────────────────────────────────

def compute_staff_load_profile(
    schedule: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compute per-staff assignment counts and load classification.

    Returns:
      {
        "profiles": [
          {
            "staff_id": X,
            "total_assignments": N,
            "max_single_day": M,   # max assignments on any single exam_date
            "classification": "balanced"|"review"|"high_risk",
            "at_risk": bool,
          },
          ...
        ],
        "at_risk_count": int,
        "high_risk_count": int,
        "total_staff": int,
      }
    """
    thresholds = _staffing_thresholds()
    balanced_load = thresholds.get("balanced_load", 3)
    review_load = thresholds.get("review_load", 5)
    high_risk_load = thresholds.get("high_risk_load", 7)

    counts: dict[Any, int] = defaultdict(int)
    by_day: dict[Any, dict[str | None, int]] = defaultdict(lambda: defaultdict(int))

    for entry in schedule:
        exam_date = entry.get("exam_date")
        for sid in entry.get("assigned_staff", []):
            if sid is not None:
                counts[sid] += 1
                by_day[sid][exam_date] += 1

    profiles: list[dict[str, Any]] = []
    for sid, total in sorted(counts.items(), key=lambda x: -x[1]):
        daily = by_day[sid]
        max_day = max(daily.values()) if daily else 0

        if total >= high_risk_load:
            classification = "high_risk"
        elif total >= review_load:
            classification = "review"
        else:
            classification = "balanced"

        profiles.append({
            "staff_id": sid,
            "total_assignments": total,
            "max_single_day": max_day,
            "classification": classification,
            "at_risk": classification != "balanced",
        })

    return {
        "profiles": profiles,
        "at_risk_count": sum(1 for p in profiles if p["at_risk"]),
        "high_risk_count": sum(1 for p in profiles if p["classification"] == "high_risk"),
        "total_staff": len(profiles),
    }


# ── Fragile staffing day detection ────────────────────────────────────────

def detect_fragile_staffing_days(
    schedule: list[dict[str, Any]],
    *,
    min_staff_threshold: int = 2,
) -> list[dict[str, Any]]:
    """Detect exam dates with fewer than min_staff_threshold unique invigilators.

    A day with only 1 invigilator is fragile — any absence causes coverage failure.
    """
    day_staff: dict[str | None, set] = defaultdict(set)
    day_exam_count: dict[str | None, int] = defaultdict(int)

    for entry in schedule:
        exam_date = entry.get("exam_date")
        day_exam_count[exam_date] += 1
        for sid in entry.get("assigned_staff", []):
            if sid is not None:
                day_staff[exam_date].add(sid)

    fragile: list[dict[str, Any]] = []
    for date, staff_set in sorted(day_staff.items(), key=lambda x: str(x[0])):
        if len(staff_set) < min_staff_threshold:
            fragile.append({
                "exam_date": date,
                "unique_staff_count": len(staff_set),
                "exam_count": day_exam_count[date],
                "risk": "FRAGILE_STAFFING",
                "message": (
                    f"Only {len(staff_set)} unique invigilator(s) on {date} "
                    f"covering {day_exam_count[date]} exam(s)."
                ),
            })
    return fragile


# ── Room bottleneck detection ─────────────────────────────────────────────

def detect_room_bottlenecks(
    schedule: list[dict[str, Any]],
    *,
    utilization_threshold: float = 0.95,
) -> list[dict[str, Any]]:
    """Detect rooms booked at or above utilization_threshold capacity.

    Near-full rooms leave no margin for last-minute enrollment changes.
    """
    bottlenecks: list[dict[str, Any]] = []
    for entry in schedule:
        room = entry.get("room") or {}
        capacity = room.get("capacity") or 0
        students = entry.get("num_students") or 0
        if capacity <= 0:
            continue
        utilization = students / capacity
        if utilization >= utilization_threshold:
            bottlenecks.append({
                "room_id": room.get("id"),
                "course_id": entry.get("course_id"),
                "section_id": entry.get("section_id"),
                "utilization": round(utilization, 3),
                "students": students,
                "capacity": capacity,
                "risk": "ROOM_BOTTLENECK",
                "message": (
                    f"Room {room.get('id')} at {utilization:.0%} capacity "
                    f"({students}/{capacity})."
                ),
            })
    return bottlenecks


# ── Repeated-burden detection ─────────────────────────────────────────────

def detect_repeated_same_person_burden(
    schedule: list[dict[str, Any]],
    *,
    same_day_max: int = 2,
) -> list[dict[str, Any]]:
    """Detect staff assigned more than same_day_max times on the same date."""
    by_day: dict[str, dict[Any, int]] = defaultdict(lambda: defaultdict(int))
    for entry in schedule:
        exam_date = str(entry.get("exam_date") or "unknown")
        for sid in entry.get("assigned_staff", []):
            if sid is not None:
                by_day[exam_date][sid] += 1

    overburden: list[dict[str, Any]] = []
    for date, staff_counts in sorted(by_day.items()):
        for sid, count in staff_counts.items():
            if count > same_day_max:
                overburden.append({
                    "staff_id": sid,
                    "exam_date": date,
                    "same_day_count": count,
                    "risk": "SAME_DAY_OVERLOAD",
                    "message": (
                        f"Staff {sid} is assigned {count} times on {date} "
                        f"(max allowed: {same_day_max})."
                    ),
                })
    return overburden


# ── Recommendations ───────────────────────────────────────────────────────

def recommend_rebalancing(
    schedule: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return prioritized rebalancing recommendations.

    Each recommendation is a plain dict with severity, message, and action.
    Deterministic only — no solver call, no randomness.
    """
    thresholds = _staffing_thresholds()
    profile = compute_staff_load_profile(schedule)
    recommendations: list[dict[str, Any]] = []

    for p in profile["profiles"]:
        if p["classification"] == "high_risk":
            recommendations.append({
                "staff_id": p["staff_id"],
                "severity": "HIGH_RISK",
                "risk_type": "WORKLOAD_IMBALANCE",
                "message": (
                    f"Staff {p['staff_id']} has {p['total_assignments']} assignments "
                    f"(high-risk threshold: {thresholds.get('high_risk_load', 7)}). "
                    "Redistribute to lower-loaded staff."
                ),
                "action": "REDISTRIBUTE",
            })
        elif p["classification"] == "review":
            recommendations.append({
                "staff_id": p["staff_id"],
                "severity": "WARNING",
                "risk_type": "WORKLOAD_IMBALANCE",
                "message": (
                    f"Staff {p['staff_id']} has {p['total_assignments']} assignments "
                    f"(review threshold: {thresholds.get('review_load', 5)})."
                ),
                "action": "MONITOR",
            })

    # Fragile days
    for fragile in detect_fragile_staffing_days(schedule):
        recommendations.append({
            "staff_id": None,
            "severity": "WARNING",
            "risk_type": "FRAGILE_STAFFING_DAY",
            "message": fragile["message"],
            "action": "ADD_BACKUP_STAFF",
        })

    # Same-day overload
    for overload in detect_repeated_same_person_burden(schedule):
        recommendations.append({
            "staff_id": overload["staff_id"],
            "severity": "WARNING",
            "risk_type": "SAME_DAY_OVERLOAD",
            "message": overload["message"],
            "action": "REDISTRIBUTE",
        })

    return recommendations
