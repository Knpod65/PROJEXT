"""Analytics read model contracts.

TypedDict-only file. Zero imports from other contracts:
  from __future__ import annotations
  from typing import ...
  from typing_extensions import TypedDict

Pure-Python validators: validate_analytics_dict() and sanitize_analytics_output().
"""
from __future__ import annotations

from typing import Any, List, Optional, Dict
from typing_extensions import TypedDict

_PDPA_LEVELS = frozenset({"public", "internal", "confidential", "restricted"})


# ── Core TypedDicts ────────────────────────────────────────────────────────────

class MetricDefinition(TypedDict):
    code: str
    name: str
    category: str
    description: str
    unit: str
    aggregation: str          # count | sum | avg | ratio | score
    pdpa_level: str           # public | internal | confidential | restricted


class MetricValue(TypedDict):
    metric_code: str
    value: float
    computed_at: str
    period_key: str
    scope: Optional[Dict[str, Any]]


class TimeSeriesPoint(TypedDict):
    period_key: str
    value: float
    trend_direction: str      # improving | degrading | stable


class FacultyAnalyticsScope(TypedDict):
    faculty_id: str
    faculty_name: str
    academic_year: str
    semester: str


class ExecutiveDashboardSummary(TypedDict):
    overall_health_score: float
    risk_band: str             # green | amber | red
    optimization_quality_avg: float
    governance_blocker_count: int
    publication_ready_count: int
    workload_balance_score: float
    room_utilization_score: float
    pdpa_alert_count: int
    top_risks: List[Dict[str, str]]
    recommended_actions: List[Dict[str, str]]


class WorkloadAnalyticsSummary(TypedDict):
    total_assignments: int
    average_load: float
    max_load: int
    imbalance_score: float
    overloaded_staff_count: int
    fairness_band: str         # green | amber | red
    top_overload_risks: List[Dict[str, Any]]


class RoomUtilizationSummary(TypedDict):
    average_utilization: float
    underutilized_count: int
    overcapacity_count: int
    room_conflict_count: int
    building_distribution: Dict[str, Any]
    floor_distribution: Dict[str, Any]
    room_risk_flags: List[Dict[str, str]]


class OptimizationTrendSummary(TypedDict):
    period_key: str
    quality_score: float
    fairness_score: float
    trend_vs_previous: str     # improving | degrading | stable


class GovernanceTrendSummary(TypedDict):
    period_key: str
    health_score: float
    blocker_count: int
    override_count: int


class PDPAAnalyticsBoundary(TypedDict):
    pdpa_level: str
    restricted_fields: List[str]
    allowed_output_aggregation: bool


# ── Validators ─────────────────────────────────────────────────────────────────

_PII_FIELD_NAMES = frozenset({
    "student_id", "student_name", "teacher_name", "staff_name",
    "uploaded_file", "pdf_file", "export_data", "qr_token",
})


def validate_analytics_dict(obj: Any, schema: Dict[str, type]) -> List[str]:
    """Validate a dict against a schema mapping of required key → expected type.

    Returns a list of human-readable error strings. Never raises.
    """
    errors: List[str] = []
    if not isinstance(obj, dict):
        errors.append("Expected object to be a dict.")
        return errors
    for key, expected_type in schema.items():
        if key not in obj:
            errors.append(f"Missing required key: {key}")
            continue
        if not isinstance(obj[key], expected_type):
            errors.append(
                f"Key '{key}' expected type {expected_type.__name__}, "
                f"got {type(obj[key]).__name__}."
            )
    return errors


def sanitize_analytics_output(
    obj: Any,
    pdpa_boundary: PDPAAnalyticsBoundary,
) -> Any:
    """Return a JSON-safe copy of *obj* with PII fields removed per boundary.

    Rules:
    - All restricted_fields keys are replaced with the string ``[REDACTED]``.
    - Dicts and lists are recursed into.
    - Scalar values are returned as-is unless they are listed restricted_fields.
    """
    restricted = set(pdpa_boundary.get("restricted_fields", []))

    if isinstance(obj, dict):
        safe: Dict[str, Any] = {}
        for k, v in obj.items():
            if k in restricted:
                safe[k] = "[REDACTED]"
            else:
                safe[k] = sanitize_analytics_output(v, pdpa_boundary)
        return safe

    if isinstance(obj, list):
        return [sanitize_analytics_output(item, pdpa_boundary) for item in obj]

    return obj
