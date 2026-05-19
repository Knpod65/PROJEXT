"""Tests for contracts/analytics_contracts.py"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from contracts.analytics_contracts import (
    MetricDefinition,
    MetricValue,
    TimeSeriesPoint,
    FacultyAnalyticsScope,
    ExecutiveDashboardSummary,
    WorkloadAnalyticsSummary,
    RoomUtilizationSummary,
    OptimizationTrendSummary,
    GovernanceTrendSummary,
    PDPAAnalyticsBoundary,
    validate_analytics_dict,
    sanitize_analytics_output,
)


# ── TypedDict construction smoke tests ────────────────────────────────────────

def _md(**kw):
    base: MetricDefinition = {
        "code": "opt_quality_score",
        "name": "Quality Score",
        "category": "optimization",
        "description": "...",
        "unit": "score",
        "aggregation": "avg",
        "pdpa_level": "public",
    }
    base.update(kw)
    return base


def _mv(**kw):
    base: MetricValue = {
        "metric_code": "opt_quality_score",
        "value": 75.0,
        "computed_at": "2026-01-01T00:00:00Z",
        "period_key": "2026-01",
        "scope": None,
    }
    base.update(kw)
    return base


def test_metric_definition_typeddict_fields():
    m = _md()
    assert m["code"] == "opt_quality_score"
    assert m["name"] == "Quality Score"
    assert m["aggregation"] == "avg"
    assert m["pdpa_level"] == "public"


def test_metric_value_typeddict_fields():
    v = _mv()
    assert v["metric_code"] == "opt_quality_score"
    assert v["value"] == 75.0
    assert v["period_key"] == "2026-01"


def test_time_series_point_typeddict():
    tsp: TimeSeriesPoint = {
        "period_key": "2026-01",
        "value": 70.0,
        "trend_direction": "improving",
    }
    assert tsp["trend_direction"] == "improving"


def test_faculty_analytics_scope_typeddict():
    scope: FacultyAnalyticsScope = {
        "faculty_id": "F01",
        "faculty_name": "Political Science",
        "academic_year": "2026",
        "semester": "1",
    }
    assert scope["faculty_id"] == "F01"


def test_executive_dashboard_summary_typeddict():
    dash: ExecutiveDashboardSummary = {
        "overall_health_score": 80.0,
        "risk_band": "green",
        "optimization_quality_avg": 85.0,
        "governance_blocker_count": 0,
        "publication_ready_count": 42,
        "workload_balance_score": 78.0,
        "room_utilization_score": 72.0,
        "pdpa_alert_count": 0,
        "top_risks": [{"risk": "none", "severity": "low", "category": "scheduling"}],
        "recommended_actions": [{"action": "n/a", "owner": "admin", "priority": "low"}],
    }
    assert dash["pdpa_alert_count"] == 0
    assert dash["risk_band"] == "green"


def test_workload_analytics_summary_typeddict():
    w: WorkloadAnalyticsSummary = {
        "total_assignments": 120,
        "average_load": 6.0,
        "max_load": 15,
        "imbalance_score": 0.3,
        "overloaded_staff_count": 3,
        "fairness_band": "amber",
        "top_overload_risks": [],
    }
    assert w["fairness_band"] == "amber"


def test_room_utilization_summary_typeddict():
    r: RoomUtilizationSummary = {
        "average_utilization": 0.55,
        "underutilized_count": 2,
        "overcapacity_count": 0,
        "room_conflict_count": 0,
        "building_distribution": {},
        "floor_distribution": {},
        "room_risk_flags": [],
    }
    assert r["average_utilization"] == 0.55


def test_pdpa_analytics_boundary_typeddict():
    b: PDPAAnalyticsBoundary = {
        "pdpa_level": "restricted",
        "restricted_fields": ["student_id", "student_name"],
        "allowed_output_aggregation": False,
    }
    assert b["pdpa_level"] == "restricted"


# ── validate_analytics_dict ────────────────────────────────────────────────────

_EMP_SCHEMA = {
    "overall_health_score": float,
    "risk_band": str,
    "pdpa_alert_count": int,
}


def test_validate_valid_dict_returns_empty():
    errors = validate_analytics_dict(
        {"overall_health_score": 80.0, "risk_band": "green", "pdpa_alert_count": 0},
        _EMP_SCHEMA,
    )
    assert errors == []


def test_validate_missing_key():
    errors = validate_analytics_dict(
        {"overall_health_score": 80.0, "risk_band": "green"},
        _EMP_SCHEMA,
    )
    assert any("pdpa_alert_count" in e for e in errors)


def test_validate_wrong_type():
    errors = validate_analytics_dict(
        {"overall_health_score": "high", "risk_band": "green", "pdpa_alert_count": 0},
        _EMP_SCHEMA,
    )
    assert any("overall_health_score" in e and "str" in e for e in errors)


def test_validate_non_dict_input():
    errors = validate_analytics_dict([1, 2, 3], _EMP_SCHEMA)
    assert len(errors) == 1
    assert "dict" in errors[0]


def test_validate_extra_keys_are_ignored():
    obj = {"overall_health_score": 80.0, "risk_band": "green",
            "pdpa_alert_count": 0, "extra_key": 42}
    errors = validate_analytics_dict(obj, _EMP_SCHEMA)
    assert errors == []


# ── sanitize_analytics_output ──────────────────────────────────────────────────

def test_sanitize_redacts_restricted_fields():
    boundary: PDPAAnalyticsBoundary = {
        "pdpa_level": "restricted",
        "restricted_fields": ["student_id", "student_name"],
        "allowed_output_aggregation": False,
    }
    obj = {"risk_band": "green", "student_id": "12345678", "student_name": "John Doe"}
    result = sanitize_analytics_output(obj, boundary)
    assert result["student_id"] == "[REDACTED]"
    assert result["student_name"] == "[REDACTED]"
    assert result["risk_band"] == "green"


def test_sanitize_leaves_non_restricted_fields_intact():
    boundary: PDPAAnalyticsBoundary = {
        "pdpa_level": "public",
        "restricted_fields": [],
        "allowed_output_aggregation": True,
    }
    obj = {"pdpa_alert_count": 5, "risk_band": "green"}
    result = sanitize_analytics_output(obj, boundary)
    assert result == obj


def test_sanitize_no_restricted_fields():
    boundary: PDPAAnalyticsBoundary = {
        "pdpa_level": "internal",
        "restricted_fields": [],
        "allowed_output_aggregation": True,
    }
    obj = {"pdpa_alert_count": 0}
    result = sanitize_analytics_output(obj, boundary)
    assert result == obj


def test_sanitize_nested_dict():
    boundary: PDPAAnalyticsBoundary = {
        "pdpa_level": "restricted",
        "restricted_fields": ["student_name"],
        "allowed_output_aggregation": False,
    }
    obj = {"top_risks": [{"risk": "foo", "student_name": "bar"}]}
    result = sanitize_analytics_output(obj, boundary)
    assert result["top_risks"][0]["student_name"] == "[REDACTED]"
    assert result["top_risks"][0]["risk"] == "foo"


def test_sanitize_scalar_passthrough():
    boundary: PDPAAnalyticsBoundary = {
        "pdpa_level": "public",
        "restricted_fields": [],
        "allowed_output_aggregation": True,
    }
    assert sanitize_analytics_output(42, boundary) == 42
    assert sanitize_analytics_output("hello", boundary) == "hello"
    assert sanitize_analytics_output(None, boundary) is None


def test_sanitize_list():
    boundary: PDPAAnalyticsBoundary = {
        "pdpa_level": "internal",
        "restricted_fields": ["staff_name"],
        "allowed_output_aggregation": True,
    }
    items = [{"staff_name": "Alice"}, {"staff_name": "Bob"}]
    result = sanitize_analytics_output(items, boundary)
    assert result[0]["staff_name"] == "[REDACTED]"
    assert result[1]["staff_name"] == "[REDACTED]"
