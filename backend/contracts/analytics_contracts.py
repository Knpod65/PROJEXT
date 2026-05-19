"""Analytics read model contracts — TypedDict payload shapes.

Pure type definitions. No runtime behaviour required except optional
pure-Python validators. No imports from other contract files to avoid circular
dependencies — use string annotations only.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

from typing_extensions import TypedDict as ExtTypedDict


# ── Metric Contracts ──────────────────────────────────────────────────────────

class MetricDefinition(ExtTypedDict):
    metric_code: str
    name: str
    category: str
    description: str
    unit: str
    aggregation: str            # count | sum | avg | ratio | score
    pdpa_level: str             # public | internal | confidential | restricted
    dimension_keys: List[str]
    source_entities: List[str]
    refresh_mode: str           # on_demand | scheduled | event_driven


class MetricValue(ExtTypedDict):
    metric_code: str
    value: float
    computed_at: str            # ISO 8601
    period_key: str             # e.g. "2026-2-final"
    scope: Optional[Dict[str, Any]]


class TimeSeriesPoint(ExtTypedDict):
    period_key: str             # e.g. "2026-1-midterm"
    value: float
    trend_direction: str        # improving | degrading | stable


# ── Executive Contracts ───────────────────────────────────────────────────────

class TopRiskItem(ExtTypedDict):
    risk: str
    severity: str               # low | medium | high
    category: str


class RecommendedActionItem(ExtTypedDict):
    action: str
    owner: str
    priority: str               # low | medium | high


class ExecutiveDashboardSummary(ExtTypedDict):
    overall_health_score: float      # 0.0 – 100.0
    risk_band: str                   # green | amber | red
    optimization_quality_avg: float  # 0.0 – 100.0
    governance_blocker_count: int
    publication_ready_count: int
    workload_balance_score: float    # 0.0 – 100.0
    room_utilization_score: float    # 0.0 – 100.0
    pdpa_alert_count: int
    top_risks: List[TopRiskItem]
    recommended_actions: List[RecommendedActionItem]


# ── Domain Contracts ──────────────────────────────────────────────────────────

class WorkloadAnalyticsSummary(ExtTypedDict):
    total_assignments: int
    average_load: float
    max_load: int
    imbalance_score: float          # 0.0 – 1.0
    overloaded_staff_count: int
    fairness_band: str              # green | amber | red
    top_overload_risks: List[Dict[str, Any]]


class RoomUtilizationSummary(ExtTypedDict):
    average_utilization: float      # 0.0 – 1.0
    underutilized_count: int
    overcapacity_count: int
    building_distribution: Dict[str, Any]
    floor_distribution: Dict[str, Any]
    room_risk_flags: List[Dict[str, Any]]


class OptimizationTrendSummary(ExtTypedDict):
    period_key: str
    quality_score: float            # 0.0 – 100.0
    fairness_score: float           # 0.0 – 100.0
    trend_vs_previous: str          # improving | degrading | stable


class GovernanceTrendSummary(ExtTypedDict):
    period_key: str
    health_score: float             # 0.0 – 100.0
    blocker_count: int
    override_count: int


class PDPAAnalyticsBoundary(ExtTypedDict):
    pdpa_level: str                 # public | internal | confidential | restricted
    restricted_fields: List[str]
    allowed_output_aggregation: bool  # True = output may contain aggregated values
                                       # False = output must be entirely suppressed


class FacultyAnalyticsScope(ExtTypedDict):
    faculty_id: Optional[int]
    faculty_name: Optional[str]
    academic_year: str
    semester: str


# ── Helper Validators ─────────────────────────────────────────────────────────

_VALID_PDPA = frozenset({"public", "internal", "confidential", "restricted"})
_VALID_TRENDS = frozenset({"improving", "degrading", "stable"})
_VALID_RISK_BANDS = frozenset({"green", "amber", "red"})
_VALID_FAIRNESS = frozenset({"green", "amber", "red"})


def validate_analytics_dict(obj: dict, schema_type: str) -> List[str]:
    """Return a list of validation error strings. Empty list = valid.

    Schema types recognized:
      - "executive_dashboard"
      - "workload_analytics"
      - "room_utilization"
      - "optimization_trend"
      - "governance_trend"
      - "pdpa_boundary"
    """
    errors: list[str] = []

    if schema_type == "executive_dashboard":
        if not isinstance(obj.get("overall_health_score"), (int, float)):
            errors.append("overall_health_score must be numeric")
        if obj.get("risk_band") not in _VALID_RISK_BANDS:
            errors.append(f"risk_band must be one of {_VALID_RISK_BANDS}")

    elif schema_type == "workload_analytics":
        if not isinstance(obj.get("total_assignments"), int):
            errors.append("total_assignments must be int")
        fb = obj.get("fairness_band")
        if fb not in _VALID_FAIRNESS:
            errors.append(f"fairness_band must be one of {_VALID_FAIRNESS}")

    elif schema_type == "room_utilization":
        if not isinstance(obj.get("average_utilization"), (int, float)):
            errors.append("average_utilization must be numeric")

    elif schema_type == "optimization_trend":
        td = obj.get("trend_vs_previous")
        if td not in _VALID_TRENDS:
            errors.append(f"trend_vs_previous must be one of {_VALID_TRENDS}")

    elif schema_type == "governance_trend":
        if not isinstance(obj.get("health_score"), (int, float)):
            errors.append("health_score must be numeric")

    elif schema_type == "pdpa_boundary":
        if not isinstance(obj.get("allowed_output_aggregation"), bool):
            errors.append("allowed_output_aggregation must be bool")
        if obj.get("pdpa_level") not in _VALID_PDPA:
            errors.append(f"pdpa_level must be one of {_VALID_PDPA}")

    else:
        errors.append(f"Unknown schema_type: {schema_type!r}")

    return errors


def sanitize_analytics_output(
    obj: dict,
    pdpa_boundary: PDPAAnalyticsBoundary,
) -> dict:
    """Return a JSON-safe copy of *obj* with PII fields removed per *pdpa_boundary*.

    If *pdpa_boundary["allowed_output_aggregation"]* is False, returns a
    plain {"suppressed": True} dict so no field is accidentally forwarded.
    Non-serialisable nested values are replaced with str().
    """
    if not pdpa_boundary.get("allowed_output_aggregation", True):
        return {"suppressed": True, "pdpa_level": pdpa_boundary.get("pdpa_level", "restricted")}

    restricted: set[str] = set(pdpa_boundary.get("restricted_fields", []))

    def _clean(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: _clean(v) for k, v in value.items()
                    if k not in restricted}
        if isinstance(value, list):
            return [_clean(v) for v in value]
        return value

    return _clean(obj)
