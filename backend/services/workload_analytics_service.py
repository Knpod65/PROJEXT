"""Workload analytics service.

Pure logic. No DB. No ORM. No HTTP.  All inputs are plain dicts / lists of dicts.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _fairness_band(std_dev: float, avg: float) -> str:
    if avg <= 0:
        return "green"
    ratio = std_dev / avg
    if ratio < 0.15:
        return "green"
    if ratio < 0.30:
        return "amber"
    return "red"


# ── Public API ────────────────────────────────────────────────────────────────

def build_workload_summary_dict(workload_map: dict | None) -> dict:
    """Build a JSON-safe workload summary from a pre-computed workload map."""
    if not workload_map:
        return {
            "total_assignments": 0,
            "average_load":      0.0,
            "max_load":          0,
            "imbalance_score":   0.0,
            "overloaded_staff_count": 0,
            "fairness_band":     "green",
        }
    return {
        "total_assignments":      _safe_int(workload_map.get("total_assignments")),
        "average_load":           _safe_float(workload_map.get("average_load")),
        "max_load":               _safe_int(workload_map.get("max_load")),
        "imbalance_score":        _safe_float(workload_map.get("imbalance_score")),
        "overloaded_staff_count": _safe_int(workload_map.get("overloaded_staff_count")),
        "fairness_band":          str(workload_map.get("fairness_band", "green")),
    }


def compute_workload_analytics(
    staff_loads: list[dict],
    duty_detail: list[dict],
    period_info: dict | None = None,
) -> dict:
    """Compute workload analytics from pre-computed data.

    Args:
        staff_loads:  [{user_id, staff_name, department, total_load}]
        duty_detail:  [{user_id, duty_type, date, workload_count}]
        period_info:  Optional {academic_year, semester, exam_type}

    Returns:
        WorkloadAnalyticsSummary-shaped dict.
    """
    loads = [_safe_float(l.get("total_load", 0)) for l in staff_loads]

    total_assignments = int(sum(loads))
    average_load = round(sum(loads) / len(loads), 2) if loads else 0.0
    max_load = int(max(loads)) if loads else 0

    if loads:
        mean_val = average_load
        variance = sum((l - mean_val) ** 2 for l in loads) / len(loads)
        std_dev = variance ** 0.5
        if mean_val > 0:
            imbalance_score = round(min(1.0, std_dev / (mean_val * 1.5)), 4)
        else:
            imbalance_score = 0.0
        overloaded_count = sum(1 for l in loads if l >= mean_val * 1.5)
    else:
        std_dev = 0.0
        imbalance_score = 0.0
        overloaded_count = 0

    fairness_band = _fairness_band(std_dev, average_load if average_load > 0 else 1.0)

    # Per-role summary
    per_role: dict[str, dict] = defaultdict(
        lambda: {"count": 0, "total_workload": 0.0}
    )
    for row in duty_detail:
        role = row.get("duty_type", "UNKNOWN")
        per_role[role]["count"] += 1
        per_role[role]["total_workload"] += _safe_float(row.get("workload_count", 0))
    per_role_summary = {k: dict(v) for k, v in per_role.items()}

    # Per-department summary
    per_dept: dict[str, dict] = defaultdict(
        lambda: {"count": 0, "total_workload": 0.0}
    )
    for row in staff_loads:
        dept = row.get("department", "UNKNOWN")
        per_dept[dept]["count"] += 1
        per_dept[dept]["total_workload"] += _safe_float(row.get("total_load", 0))
    per_dept_summary = {k: dict(v) for k, v in per_dept.items()}

    # Repeated burden: same user_id + same date counted once flagged
    burden_map: dict[tuple, int] = defaultdict(int)
    for row in duty_detail:
        uid = row.get("user_id")
        date = row.get("date")
        if uid is not None and date:
            burden_map[(int(uid), str(date))] += 1
    repeated_burden = [
        {"user_id": uid, "date": date, "assignment_count": cnt}
        for (uid, date), cnt in burden_map.items()
        if cnt > 1
    ]

    # Top overload risks
    avg_threshold = round(float(average_load * 1.5), 2) if average_load > 0 else 0.0
    top_overload_risks = [
        {
            "user_id":     int(row.get("user_id", 0)),
            "staff_name":  str(row.get("staff_name", "")),
            "department":  str(row.get("department", "")),
            "current_load": int(row.get("total_load", 0)),
            "overload_pct": round(
                (_safe_float(row.get("total_load", 0)) - avg_threshold) / avg_threshold * 100, 1
            ) if avg_threshold > 0 else 0.0,
        }
        for row in staff_loads
        if _safe_float(row.get("total_load", 0)) >= float(avg_threshold)
    ]

    return {
        "total_assignments":         total_assignments,
        "average_load":              round(float(average_load), 2),
        "max_load":                  int(max_load),
        "imbalance_score":           float(imbalance_score),
        "overloaded_staff_count":    int(overloaded_count),
        "fairness_band":             fairness_band,
        "top_overload_risks":        top_overload_risks[:10],
        "per_role_summary":          per_role_summary,
        "per_department_summary":    per_dept_summary,
        "repeated_burden_detection": repeated_burden,
        "period_info":               period_info or {},
    }
