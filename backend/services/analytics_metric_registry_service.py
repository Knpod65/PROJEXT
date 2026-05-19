"""Analytics metric registry service.

Central registry of 11 institutional KPIs for the EMS analytics platform.
Pure logic. No DB. No ORM. All functions return JSON-safe dicts.
"""
from __future__ import annotations

from typing import Any

from policies.pdpa_policy import DataSensitivity

_PDPA_LEVELS = {"public", "internal", "confidential", "restricted"}

_METRICS: dict[str, dict[str, Any]] = {
    "opt_quality_score": {
        "metric_code": "opt_quality_score",
        "name": "Optimization Quality Score",
        "category": "optimization",
        "description": "Average optimization quality score across all exam schedules.",
        "unit": "score",
        "aggregation": "avg",
        "pdpa_level": "public",
        "dimension_keys": ["faculty_id", "academic_year", "semester"],
        "source_entities": ["exam_schedules", "optimization_sessions"],
        "refresh_mode": "on_demand",
    },
    "sched_coverage_pct": {
        "metric_code": "sched_coverage_pct",
        "name": "Schedule Coverage",
        "category": "schedule",
        "description": "Percentage of exam sections with a published exam schedule.",
        "unit": "percent",
        "aggregation": "ratio",
        "pdpa_level": "public",
        "dimension_keys": ["faculty_id", "academic_year", "semester"],
        "source_entities": ["exam_schedules", "sections"],
        "refresh_mode": "on_demand",
    },
    "wkl_invigilation_balance_score": {
        "metric_code": "wkl_invigilation_balance_score",
        "name": "Invigilation Balance Score",
        "category": "workload",
        "description": "Fairness score reflecting how evenly invigilation duties are distributed.",
        "unit": "score",
        "aggregation": "score",
        "pdpa_level": "internal",
        "dimension_keys": ["user_id", "department"],
        "source_entities": ["supervisions", "paper_distribution_assignments"],
        "refresh_mode": "on_demand",
    },
    "rms_avg_utilization_pct": {
        "metric_code": "rms_avg_utilization_pct",
        "name": "Room Utilization Rate",
        "category": "room_utilization",
        "description": "Average seat-fraction of allocated rooms vs. declared room capacity.",
        "unit": "percent",
        "aggregation": "avg",
        "pdpa_level": "public",
        "dimension_keys": ["room_name", "building", "exam_date"],
        "source_entities": ["exam_schedules", "rooms"],
        "refresh_mode": "on_demand",
    },
    "gov_health_score": {
        "metric_code": "gov_health_score",
        "name": "Governance Health Score",
        "category": "governance",
        "description": "Decision pipeline health index based on approval cycles and blocker rates.",
        "unit": "score",
        "aggregation": "score",
        "pdpa_level": "internal",
        "dimension_keys": ["academic_year", "semester"],
        "source_entities": ["governance_decisions", "audit_logs"],
        "refresh_mode": "on_demand",
    },
    "pub_ready_count": {
        "metric_code": "pub_ready_count",
        "name": "Publish-Ready Section Count",
        "category": "publication",
        "description": "Number of sections ready for exam publication.",
        "unit": "count",
        "aggregation": "count",
        "pdpa_level": "internal",
        "dimension_keys": ["faculty_id", "academic_year", "semester"],
        "source_entities": ["exam_submissions", "sections"],
        "refresh_mode": "on_demand",
    },
    "prt_throughput_score": {
        "metric_code": "prt_throughput_score",
        "name": "Print Queue Throughput",
        "category": "print",
        "description": "Print queue velocity index measuring queue processing efficiency.",
        "unit": "score",
        "aggregation": "score",
        "pdpa_level": "internal",
        "dimension_keys": ["exam_date"],
        "source_entities": ["print_queue_jobs"],
        "refresh_mode": "on_demand",
    },
    "qr_pickup_rate_pct": {
        "metric_code": "qr_pickup_rate_pct",
        "name": "QR Pickup Rate",
        "category": "pickup_qr",
        "description": "Percentage of QR-coded exam pickups that were successfully checked in.",
        "unit": "percent",
        "aggregation": "ratio",
        "pdpa_level": "public",
        "dimension_keys": ["exam_date", "room_name"],
        "source_entities": ["exam_pickup_checkins", "exam_access_logs"],
        "refresh_mode": "on_demand",
    },
    "stu_conflict_count": {
        "metric_code": "stu_conflict_count",
        "name": "Student Schedule Conflicts",
        "category": "student_conflict",
        "description": "Count of detected student exam schedule conflicts (PII never surfaced).",
        "unit": "count",
        "aggregation": "count",
        "pdpa_level": "restricted",
        "dimension_keys": ["academic_year", "semester"],
        "source_entities": ["exam_schedules"],
        "refresh_mode": "on_demand",
    },
    "fac_oper_score": {
        "metric_code": "fac_oper_score",
        "name": "Faculty Operations Health",
        "category": "faculty_operations",
        "description": "Per-faculty operational health summary across all exam KPIs.",
        "unit": "score",
        "aggregation": "score",
        "pdpa_level": "internal",
        "dimension_keys": ["faculty_id", "academic_year", "semester"],
        "source_entities": ["exam_schedules", "supervisions", "audit_logs"],
        "refresh_mode": "on_demand",
    },
    "pdpa_alert_count": {
        "metric_code": "pdpa_alert_count",
        "name": "PDPA Alert Count",
        "category": "pdpa_compliance",
        "description": "Count of PDPA-classified warning events detected during the period.",
        "unit": "count",
        "aggregation": "count",
        "pdpa_level": "internal",
        "dimension_keys": ["academic_year", "semester"],
        "source_entities": ["audit_logs", "import_row_logs"],
        "refresh_mode": "on_demand",
    },
}


def list_metrics() -> list[dict[str, Any]]:
    """Return all metric definitions as plain dicts."""
    return [dict(m) for m in _METRICS.values()]


def get_metric(metric_code: str) -> dict[str, Any]:
    """Return a single metric definition or raise KeyError."""
    if metric_code not in _METRICS:
        raise KeyError(f"Metric '{metric_code}' not found in registry.")
    return dict(_METRICS[metric_code])


def list_metrics_by_category(category: str) -> list[dict[str, Any]]:
    """Return metrics filtered by category string."""
    return [dict(m) for m in _METRICS.values() if m["category"] == category]


def list_public_metrics() -> list[dict[str, Any]]:
    """Return metrics whose PDPA level is 'public' only."""
    return [dict(m) for m in _METRICS.values() if m["pdpa_level"] == "public"]


def classify_metric_pdpa(metric_code: str) -> DataSensitivity:
    """Map a metric's pdpa_level string to a DataSensitivity enum value."""
    m = get_metric(metric_code)
    level = m["pdpa_level"]
    _PDPA_TO_POLICY: dict[str, str] = {
        "public":        DataSensitivity.public.value,
        "internal":      DataSensitivity.authenticated.value,
        "confidential":  DataSensitivity.role_restricted.value,
        "restricted":    DataSensitivity.sensitive.value,
    }
    mapped = _PDPA_TO_POLICY.get(level, level)
    return DataSensitivity(mapped)
