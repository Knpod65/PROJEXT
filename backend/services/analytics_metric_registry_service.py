"""Analytics metric registry service.

Canonical definitions for all institutional analytics metrics.
Pure logic. No DB. No ORM. No HTTP.

Each metric definition:
{
  "metric_code": str,
  "name": str,
  "category": str,
  "description": str,
  "unit": str,
  "aggregation": "count" | "sum" | "avg" | "ratio" | "score",
  "pdpa_level": "public" | "internal" | "confidential" | "restricted",
  "dimension_keys": list[str],
  "source_entities": list[str],
  "refresh_mode": "on_demand" | "scheduled" | "event_driven",
}
"""
from __future__ import annotations

from typing import Any

from policies.pdpa_policy import DataSensitivity


# ── Metric Definitions ────────────────────────────────────────────────────────

_METRICS: dict[str, dict[str, Any]] = {
    "opt_quality_score": {
        "metric_code": "opt_quality_score",
        "name": "Optimization Quality Score",
        "category": "optimization",
        "description": "Average optimization quality across active exam schedules.",
        "unit": "score",
        "aggregation": "avg",
        "pdpa_level": "internal",
        "dimension_keys": ["exam_period_id", "exam_type"],
        "source_entities": ["optimization_quality_report"],
        "refresh_mode": "on_demand",
    },
    "sched_coverage_pct": {
        "metric_code": "sched_coverage_pct",
        "name": "Schedule Coverage Rate",
        "category": "schedule",
        "description": "Percentage of exam sections that have a published schedule.",
        "unit": "ratio",
        "aggregation": "ratio",
        "pdpa_level": "public",
        "dimension_keys": ["academic_year", "semester", "exam_type"],
        "source_entities": ["exam_schedules", "sections"],
        "refresh_mode": "on_demand",
    },
    "wkl_invigilation_balance_score": {
        "metric_code": "wkl_invigilation_balance_score",
        "name": "Invigilation Load Balance Score",
        "category": "workload",
        "description": "Fairness score for invigilation load distribution across active supervisors.",
        "unit": "score",
        "aggregation": "score",
        "pdpa_level": "internal",
        "dimension_keys": ["academic_year", "semester", "exam_type"],
        "source_entities": ["supervisions", "users"],
        "refresh_mode": "on_demand",
    },
    "rms_avg_utilization_pct": {
        "metric_code": "rms_avg_utilization_pct",
        "name": "Room Utilization Rate",
        "category": "room_utilization",
        "description": "Average seat-fraction vs. declared capacity for all occupied time slots.",
        "unit": "ratio",
        "aggregation": "avg",
        "pdpa_level": "public",
        "dimension_keys": ["academic_year", "semester", "exam_type", "building"],
        "source_entities": ["exam_schedules", "rooms"],
        "refresh_mode": "on_demand",
    },
    "gov_health_score": {
        "metric_code": "gov_health_score",
        "name": "Governance Health Score",
        "category": "governance",
        "description": "Index measuring the health of the decision governance pipeline.",
        "unit": "score",
        "aggregation": "score",
        "pdpa_level": "internal",
        "dimension_keys": ["exam_period_id"],
        "source_entities": ["governance_decisions", "audit_logs"],
        "refresh_mode": "on_demand",
    },
    "pub_ready_count": {
        "metric_code": "pub_ready_count",
        "name": "Publication Ready Count",
        "category": "publication",
        "description": "Number of sections whose exam submission is approved and ready for publication.",
        "unit": "count",
        "aggregation": "count",
        "pdpa_level": "internal",
        "dimension_keys": ["academic_year", "semester", "exam_type"],
        "source_entities": ["exam_submissions"],
        "refresh_mode": "on_demand",
    },
    "prt_throughput_score": {
        "metric_code": "prt_throughput_score",
        "name": "Print Queue Throughput Score",
        "category": "print",
        "description": "Velocity of the print queue from queuing to completion.",
        "unit": "score",
        "aggregation": "score",
        "pdpa_level": "internal",
        "dimension_keys": ["academic_year", "semester", "exam_type"],
        "source_entities": ["print_queue_jobs"],
        "refresh_mode": "scheduled",
    },
    "qr_pickup_rate_pct": {
        "metric_code": "qr_pickup_rate_pct",
        "name": "QR Pickup Success Rate",
        "category": "pickup_qr",
        "description": "Ratio of successful QR token check-ins to total issued tokens.",
        "unit": "ratio",
        "aggregation": "ratio",
        "pdpa_level": "public",
        "dimension_keys": ["academic_year", "semester"],
        "source_entities": ["exam_pickup_qr_tokens", "exam_pickup_checkins"],
        "refresh_mode": "event_driven",
    },
    "stu_conflict_count": {
        "metric_code": "stu_conflict_count",
        "name": "Student Schedule Conflict Count",
        "category": "student_conflict",
        "description": "Count of detected student double-booking conflicts in exam schedules.",
        "unit": "count",
        "aggregation": "count",
        "pdpa_level": "restricted",
        "dimension_keys": ["academic_year", "semester", "exam_type"],
        "source_entities": ["enrollment_records", "exam_schedules"],
        "refresh_mode": "on_demand",
    },
    "fac_oper_score": {
        "metric_code": "fac_oper_score",
        "name": "Faculty Operations Score",
        "category": "faculty_operations",
        "description": "Per-faculty operational health summary covering submission, scheduling, and governance.",
        "unit": "score",
        "aggregation": "avg",
        "pdpa_level": "confidential",
        "dimension_keys": ["faculty_id", "academic_year", "semester"],
        "source_entities": ["sections", "exam_submissions", "exam_schedules"],
        "refresh_mode": "scheduled",
    },
    "pdpa_alert_count": {
        "metric_code": "pdpa_alert_count",
        "name": "PDPA Alert Count",
        "category": "pdpa_compliance",
        "description": "Count of audit events that triggered a PDPA-sensitive field classification warning.",
        "unit": "count",
        "aggregation": "count",
        "pdpa_level": "restricted",
        "dimension_keys": ["academic_year", "semester"],
        "source_entities": ["audit_logs", "exam_access_logs"],
        "refresh_mode": "on_demand",
    },
}

_METRIC_LIST = list(_METRICS.values())

_VALID_AGGREGATIONS = frozenset({"count", "sum", "avg", "ratio", "score"})
_VALID_PDPA_LEVELS = frozenset({"public", "internal", "confidential", "restricted"})


# ── Public API ────────────────────────────────────────────────────────────────

def list_metrics() -> list[dict[str, Any]]:
    """Return all metric definitions (shallow copies)."""
    return [dict(m) for m in _METRIC_LIST]


def get_metric(metric_code: str) -> dict[str, Any]:
    """Return a single metric definition or raise KeyError with a descriptive message."""
    if metric_code not in _METRICS:
        raise KeyError(
            f"Metric '{metric_code}' not found. "
            f"Valid codes: {sorted(_METRICS.keys())}."
        )
    return dict(_METRICS[metric_code])


def list_metrics_by_category(category: str) -> list[dict[str, Any]]:
    """Return all metric definitions belonging to the given category."""
    return [dict(m) for m in _METRIC_LIST if m["category"] == category]


def list_public_metrics() -> list[dict[str, Any]]:
    """Return all metric definitions whose pdpa_level is 'public'."""
    return [dict(m) for m in _METRIC_LIST if m["pdpa_level"] == "public"]


def classify_metric_pdpa(metric_code: str) -> DataSensitivity:
    """Translate the metric's pdpa_level string into a DataSensitivity enum value.

    Raises KeyError if metric_code is unknown.
    """
    definition = get_metric(metric_code)
    pdpa_level = definition.get("pdpa_level", "internal")

    mapping = {
        "public":        DataSensitivity.public,
        "internal":      DataSensitivity.role_restricted,
        "confidential":  DataSensitivity.sensitive,
        "restricted":    DataSensitivity.critical,
    }
    return mapping[pdpa_level]
