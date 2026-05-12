"""Quality scoring for optimized schedules.

This service remains read-only and additive. It does not change optimizer
behavior; it only analyzes already-generated allocations.
"""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Dict, Iterable, List


DEFAULT_QUALITY_WEIGHTS: dict[str, float] = {
    "fairness_score": 0.12,
    "room_efficiency_score": 0.12,
    "invigilator_balance_score": 0.11,
    "distribution_balance_score": 0.08,
    "conflict_risk_score": 0.14,
    "operational_complexity_score": 0.10,
    "student_experience_score": 0.10,
    "document_readiness_score": 0.08,
    "accessibility_score": 0.07,
    "continuity_score": 0.08,
}


def _clamp(score: float) -> float:
    return max(0.0, min(100.0, score))


def _normalize_weights(weights: dict[str, float] | None) -> dict[str, float]:
    merged = dict(DEFAULT_QUALITY_WEIGHTS)
    merged.update(weights or {})
    total = sum(value for value in merged.values() if value > 0) or 1.0
    return {key: value / total for key, value in merged.items()}


def _variance_penalty(values: List[int]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    stddev = math.sqrt(variance)
    return (stddev / (mean + 1e-6)) * 25.0


def _room_efficiency_score(schedule: List[Dict[str, Any]]) -> float:
    if not schedule:
        return 100.0
    target = 0.8
    scores = []
    for entry in schedule:
        room = entry.get("room") or {}
        capacity = room.get("capacity") or 0
        students = entry.get("num_students", 0) or 0
        if capacity <= 0:
            scores.append(25.0)
            continue
        utilization = students / capacity
        if utilization > 1.0:
            scores.append(0.0)
            continue
        deviation = abs(utilization - target)
        scores.append(_clamp(100.0 - (deviation * 125.0)))
    return sum(scores) / len(scores)


def _assignment_counts(schedule: List[Dict[str, Any]]) -> dict[Any, int]:
    counts: dict[Any, int] = {}
    for entry in schedule:
        for staff in entry.get("assigned_staff", []) or []:
            counts[staff] = counts.get(staff, 0) + 1
    return counts


def _fairness_score(schedule: List[Dict[str, Any]]) -> float:
    counts = _assignment_counts(schedule)
    if not counts:
        return 100.0
    return _clamp(100.0 - _variance_penalty(list(counts.values())))


def _invigilator_balance_score(schedule: List[Dict[str, Any]]) -> float:
    counts = _assignment_counts(schedule)
    if not counts:
        return 100.0
    max_count = max(counts.values())
    min_count = min(counts.values())
    spread_penalty = (max_count - min_count) * 12.0
    return _clamp(100.0 - spread_penalty - _variance_penalty(list(counts.values())) * 0.5)


def _distribution_balance_score(schedule: List[Dict[str, Any]]) -> float:
    counts: dict[Any, int] = {}
    missing = 0
    for entry in schedule:
        distributor = entry.get("paper_distributor")
        if not distributor:
            missing += 1
            continue
        counts[distributor] = counts.get(distributor, 0) + 1
    if not schedule:
        return 100.0
    if not counts:
        return 20.0
    missing_penalty = (missing / len(schedule)) * 60.0
    balance_penalty = _variance_penalty(list(counts.values())) * 0.6
    return _clamp(100.0 - missing_penalty - balance_penalty)


def _slot_key(entry: Dict[str, Any]) -> tuple[str | None, str | None]:
    return entry.get("exam_date"), entry.get("exam_time")


def _student_conflict_score(schedule: List[Dict[str, Any]]) -> float:
    slot_map: dict[tuple[str | None, str | None], set[str]] = defaultdict(set)
    collisions = 0
    total_students = 0
    for entry in schedule:
        slot = _slot_key(entry)
        student_ids = set(entry.get("student_ids", []) or [])
        total_students += len(student_ids)
        for student_id in student_ids:
            if student_id in slot_map[slot]:
                collisions += 1
            slot_map[slot].add(student_id)
    if total_students == 0:
        return 100.0
    reduction = min(100.0, (collisions / total_students) * 100.0)
    return _clamp(100.0 - reduction)


def _conflict_risk_score(schedule: List[Dict[str, Any]]) -> float:
    student_score = _student_conflict_score(schedule)
    room_conflicts = 0
    staff_conflicts = 0
    room_seen: dict[tuple[str | None, str | None], set[Any]] = defaultdict(set)
    staff_seen: dict[tuple[str | None, str | None], set[Any]] = defaultdict(set)
    total_slots = max(1, len(schedule))

    for entry in schedule:
        slot = _slot_key(entry)
        room_id = (entry.get("room") or {}).get("id")
        if room_id is not None:
            if room_id in room_seen[slot]:
                room_conflicts += 1
            room_seen[slot].add(room_id)
        for staff_id in entry.get("assigned_staff", []) or []:
            if staff_id in staff_seen[slot]:
                staff_conflicts += 1
            staff_seen[slot].add(staff_id)

    risk_penalty = min(100.0, (room_conflicts + staff_conflicts) * 18.0 / total_slots)
    return _clamp((student_score * 0.5) + ((100.0 - risk_penalty) * 0.5))


def _operational_complexity_score(schedule: List[Dict[str, Any]]) -> float:
    if not schedule:
        return 100.0
    penalty = 0.0
    for entry in schedule:
        split_count = entry.get("split_count", 1) or 1
        if split_count > 1:
            penalty += min(30.0, (split_count - 1) * 10.0)
        if not entry.get("paper_distributor"):
            penalty += 10.0
        if entry.get("timeslot_compromise"):
            penalty += 8.0
    return _clamp(100.0 - (penalty / len(schedule)))


def _student_experience_score(schedule: List[Dict[str, Any]]) -> float:
    conflict_score = _student_conflict_score(schedule)
    split_penalty = 0.0
    capacity_penalty = 0.0
    for entry in schedule:
        split_count = entry.get("split_count", 1) or 1
        if split_count > 1:
            split_penalty += min(20.0, (split_count - 1) * 6.0)
        room = entry.get("room") or {}
        capacity = room.get("capacity") or 0
        students = entry.get("num_students", 0) or 0
        if capacity and students > capacity:
            capacity_penalty += 25.0
    average_penalty = (split_penalty + capacity_penalty) / max(1, len(schedule))
    return _clamp(conflict_score - average_penalty * 0.8)


def _document_readiness_score(schedule: List[Dict[str, Any]]) -> float:
    if not schedule:
        return 100.0
    score = 100.0
    missing_qr = 0
    page_mismatch = 0
    for entry in schedule:
        if not entry.get("pickup_qr_ready"):
            missing_qr += 1
        submission_pages = entry.get("submission_page_count")
        schedule_pages = entry.get("schedule_page_count")
        if submission_pages and schedule_pages and submission_pages != schedule_pages:
            page_mismatch += 1
        if not entry.get("document_ready"):
            score -= 8.0
    score -= (missing_qr / len(schedule)) * 35.0
    score -= (page_mismatch / len(schedule)) * 15.0
    return _clamp(score)


def _accessibility_score(schedule: List[Dict[str, Any]]) -> float:
    if not schedule:
        return 100.0
    known = 0
    accessible = 0
    for entry in schedule:
        value = entry.get("accessibility_ready")
        if value is None:
            continue
        known += 1
        if value:
            accessible += 1
    if known == 0:
        return 85.0
    return _clamp((accessible / known) * 100.0)


def _continuity_score(schedule: List[Dict[str, Any]]) -> float:
    if not schedule:
        return 100.0
    groups: dict[Any, int] = defaultdict(int)
    penalty = 0.0
    for entry in schedule:
        group = entry.get("continuity_group")
        if group:
            groups[group] += 1
        if entry.get("timeslot_compromise"):
            penalty += 6.0
    if groups:
        penalty += sum(max(0, count - 1) * 3.0 for count in groups.values())
    return _clamp(95.0 - (penalty / len(schedule)))


def _quality_band(overall_score: float, scores: dict[str, float]) -> str:
    if (
        scores["conflict_risk_score"] < 55
        or scores["document_readiness_score"] < 50
        or scores["invigilator_balance_score"] < 45
        or scores["operational_complexity_score"] < 45
        or overall_score < 55
    ):
        return "HIGH_RISK"
    if overall_score >= 90:
        return "EXCELLENT"
    if overall_score >= 80:
        return "GOOD"
    if overall_score >= 70:
        return "ACCEPTABLE"
    if overall_score >= 55:
        return "NEEDS_REVIEW"
    return "HIGH_RISK"


def _risk_level_from_band(band: str) -> str:
    if band in {"EXCELLENT", "GOOD"}:
        return "LOW"
    if band == "ACCEPTABLE":
        return "MEDIUM"
    return "HIGH"


def _dominant_components(scores: dict[str, float], *, reverse: bool) -> List[dict[str, Any]]:
    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=reverse)
    return [{"metric": key, "score": int(round(value))} for key, value in ordered[:3]]


def _build_quality_recommendations(scores: dict[str, float]) -> List[str]:
    recommendations = []
    if scores["conflict_risk_score"] < 80:
        recommendations.append("Review overlapping room, staff, and student-slot assignments before sign-off.")
    if scores["document_readiness_score"] < 85:
        recommendations.append("Complete QR/document readiness checks before approval.")
    if scores["invigilator_balance_score"] < 75:
        recommendations.append("Rebalance invigilator workload across available staff.")
    if scores["room_efficiency_score"] < 75:
        recommendations.append("Review room sizing to reduce underuse and over-capacity allocations.")
    if scores["operational_complexity_score"] < 70:
        recommendations.append("Reduce split or handoff complexity for manual execution safety.")
    return recommendations


def _build_quality_risks(schedule: List[Dict[str, Any]], scores: dict[str, float]) -> dict[str, List[str] | str]:
    staffing_fragility = []
    overloaded_days = []
    fairness_instability = []
    room_dependency = []

    assignments_by_day: dict[str, int] = defaultdict(int)
    room_usage: dict[Any, int] = defaultdict(int)
    for entry in schedule:
        day = entry.get("exam_date")
        if day:
            assignments_by_day[day] += len(entry.get("assigned_staff", []) or [])
        room_id = (entry.get("room") or {}).get("id")
        if room_id is not None:
            room_usage[room_id] += 1

    if scores["invigilator_balance_score"] < 70:
        staffing_fragility.append("Invigilator allocation is concentrated and may fail under staff absence.")
    if scores["distribution_balance_score"] < 70:
        staffing_fragility.append("Distribution coverage depends on too few staff members.")
    for day, count in assignments_by_day.items():
        if count > 6:
            overloaded_days.append(f"{day} has elevated staffing density and may be operationally brittle.")
    if scores["fairness_score"] < 75:
        fairness_instability.append("Workload distribution is uneven enough to trigger fairness complaints.")
    for room_id, count in room_usage.items():
        if count > 2:
            room_dependency.append(f"Room {room_id} is a repeated dependency across the generated schedule.")

    risk_summary = "Quality profile is stable."
    if scores["conflict_risk_score"] < 80 or scores["document_readiness_score"] < 85:
        risk_summary = "Quality profile needs operational review before governance approval."
    if scores["conflict_risk_score"] < 60:
        risk_summary = "Quality profile is high risk and should not progress without manual intervention."

    future_operational_risks = staffing_fragility + overloaded_days + fairness_instability + room_dependency

    return {
        "risk_summary": risk_summary,
        "future_operational_risks": future_operational_risks,
        "staffing_fragility_warnings": staffing_fragility,
        "overloaded_day_warnings": overloaded_days,
        "fairness_instability_warnings": fairness_instability,
        "room_dependency_warnings": room_dependency,
    }


def _trend_preparation(scores: dict[str, float], weights: dict[str, float], band: str) -> dict[str, Any]:
    return {
        "normalized_metrics": {key: round(value / 100.0, 4) for key, value in scores.items()},
        "comparison_keys": sorted(scores.keys()),
        "quality_band": band,
        "weights_used": weights,
    }


def compute_quality_report(
    schedule: List[Dict[str, Any]],
    *,
    weights: dict[str, float] | None = None,
) -> Dict[str, Any]:
    normalized_weights = _normalize_weights(weights)

    scores = {
        "fairness_score": _fairness_score(schedule),
        "room_efficiency_score": _room_efficiency_score(schedule),
        "invigilator_balance_score": _invigilator_balance_score(schedule),
        "distribution_balance_score": _distribution_balance_score(schedule),
        "conflict_risk_score": _conflict_risk_score(schedule),
        "operational_complexity_score": _operational_complexity_score(schedule),
        "student_experience_score": _student_experience_score(schedule),
        "document_readiness_score": _document_readiness_score(schedule),
        "accessibility_score": _accessibility_score(schedule),
        "continuity_score": _continuity_score(schedule),
    }

    overall_score = round(
        sum(scores[metric] * normalized_weights.get(metric, 0.0) for metric in normalized_weights),
        2,
    )
    band = _quality_band(overall_score, scores)
    risk_level = _risk_level_from_band(band)
    recommendations = _build_quality_recommendations(scores)
    risk_details = _build_quality_risks(schedule, scores)
    strengths = _dominant_components(scores, reverse=True)
    weaknesses = _dominant_components(scores, reverse=False)

    warnings = [item for item in recommendations if "Review" in item or "Complete" in item]
    critical_issues = [item for item in risk_details["future_operational_risks"] if "high risk" in item.lower()]

    student_conflict_score = _student_conflict_score(schedule)

    return {
        "overall_score": int(round(overall_score)),
        "quality_band": band,
        "risk_level": risk_level,
        "fairness_score": int(round(scores["fairness_score"])),
        "room_efficiency_score": int(round(scores["room_efficiency_score"])),
        "invigilator_balance_score": int(round(scores["invigilator_balance_score"])),
        "distribution_balance_score": int(round(scores["distribution_balance_score"])),
        "conflict_risk_score": int(round(scores["conflict_risk_score"])),
        "operational_complexity_score": int(round(scores["operational_complexity_score"])),
        "student_experience_score": int(round(scores["student_experience_score"])),
        "document_readiness_score": int(round(scores["document_readiness_score"])),
        "accessibility_score": int(round(scores["accessibility_score"])),
        "continuity_score": int(round(scores["continuity_score"])),
        # Compatibility field retained from the earlier report shape.
        "student_conflict_score": int(round(student_conflict_score)),
        "weights_used": normalized_weights,
        "breakdown": {key: int(round(value)) for key, value in scores.items()},
        "dominant_strengths": strengths,
        "dominant_weaknesses": weaknesses,
        "recommended_actions": recommendations,
        "warnings": warnings,
        "critical_issues": critical_issues,
        **risk_details,
        "trend_preparation": _trend_preparation(scores, normalized_weights, band),
    }
