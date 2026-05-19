"""Tests for analytics_contracts.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from contracts.analytics_contracts import (
    MetricDefinition,
    MetricValue,
    TimeSeriesPoint,
    ExecutiveDashboardSummary,
    WorkloadAnalyticsSummary,
    RoomUtilizationSummary,
    OptimizationTrendSummary,
    GovernanceTrendSummary,
    PDPAAnalyticsBoundary,
    FacultyAnalyticsScope,
    validate_analytics_dict,
    sanitize_analytics_output,
)


# ── TypedDict construction ────────────────────────────────────────────────────

def test_metric_definition_can_be_constructed():
    md: MetricDefinition = {
        "metric_code": "opt_quality_score",
        "name": "Optimization Quality Score",
        "category": "optimization",
        "description": "desc",
        "unit": "score",
        "aggregation": "avg",
        "pdpa_level": "internal",
        "dimension_keys": ["exam_period_id"],
        "source_entities": ["exam_schedules"],
        "refresh_mode": "on_demand",
    }
    assert md["metric_code"] == "opt_quality_score"


def test_executive_dashboard_summary_can_be_constructed():
    ds: ExecutiveDashboardSummary = {
        "overall_health_score": 82.5,
        "risk_band": "amber",
        "optimization_quality_avg": 78.0,
        "governance_blocker_count": 3,
        "publication_ready_count": 40,
        "workload_balance_score": 65.0,
        "room_utilization_score": 70.0,
        "pdpa_alert_count": 2,
        "top_risks": [{"risk": "low invig coverage", "severity": "medium", "category": "workload"}],
        "recommended_actions": [{"action": "rebalance", "owner": "admin", "priority": "high"}],
    }
    assert ds["risk_band"] == "amber"


def test_workload_analytics_summary_can_be_constructed():
    ws: WorkloadAnalyticsSummary = {
        "total_assignments": 120,
        "average_load": 4.0,
        "max_load": 12,
        "imbalance_score": 0.35,
        "overloaded_staff_count": 3,
        "fairness_band": "amber",
        "top_overload_risks": [],
    }
    assert ws["imbalance_score"] == 0.35


def test_room_utilization_summary_can_be_constructed():
    rs: RoomUtilizationSummary = {
        "average_utilization": 0.62,
        "underutilized_count": 5,
        "overcapacity_count": 1,
        "building_distribution": {},
        "floor_distribution": {},
        "room_risk_flags": [],
    }
    assert rs["average_utilization"] == 0.62


def test_optimization_trend_summary_can_be_constructed():
    ts: OptimizationTrendSummary = {
        "period_key": "2026-2-final",
        "quality_score": 85.0,
        "fairness_score": 78.0,
        "trend_vs_previous": "improving",
    }
    assert ts["trend_vs_previous"] == "improving"


def test_governance_trend_summary_can_be_constructed():
    gt: GovernanceTrendSummary = {
        "period_key": "2026-2-final",
        "health_score": 92.0,
        "blocker_count": 1,
        "override_count": 0,
    }
    assert gt["health_score"] == 92.0


def test_pdpa_analytics_boundary_can_be_constructed():
    pb: PDPAAnalyticsBoundary = {
        "pdpa_level": "restricted",
        "restricted_fields": ["student_name", "student_id"],
        "allowed_output_aggregation": False,
    }
    assert pb["pdpa_level"] == "restricted"


def test_faculty_analytics_scope_can_be_constructed():
    fs: FacultyAnalyticsScope = {
        "faculty_id": 1,
        "faculty_name": "Political Science",
        "academic_year": "2568",
        "semester": "2",
    }
    assert fs["faculty_name"] == "Political Science"


# ── validate_analytics_dict ───────────────────────────────────────────────────

def test_validate_executive_dashboard_valid():
    d = {
        "overall_health_score": 80.0,
        "risk_band": "amber",
        "optimization_quality_avg": 75.0,
        "governance_blocker_count": 2,
        "publication_ready_count": 30,
        "workload_balance_score": 70.0,
        "room_utilization_score": 65.0,
        "pdpa_alert_count": 1,
        "top_risks": [],
        "recommended_actions": [],
    }
    assert validate_analytics_dict(d, "executive_dashboard") == []


def test_validate_executive_dashboard_invalid_band():
    d = {"overall_health_score": 80.0, "risk_band": "purple"}
    errors = validate_analytics_dict(d, "executive_dashboard")
    assert any("risk_band" in e for e in errors)


def test_validate_executive_dashboard_invalid_score_type():
    d = {"overall_health_score": "eighty", "risk_band": "green"}
    errors = validate_analytics_dict(d, "executive_dashboard")
    assert any("overall_health_score" in e for e in errors)


def test_validate_workload_valid():
    d = {"total_assignments": 100, "fairness_band": "green"}
    assert validate_analytics_dict(d, "workload_analytics") == []


def test_validate_workload_invalid_fairness():
    d = {"total_assignments": 100, "fairness_band": "blue"}
    errors = validate_analytics_dict(d, "workload_analytics")
    assert any("fairness_band" in e for e in errors)


def test_validate_room_utilization_valid():
    d = {"average_utilization": 0.7}
    assert validate_analytics_dict(d, "room_utilization") == []


def test_validate_room_utilization_invalid():
    d = {"average_utilization": "high"}
    errors = validate_analytics_dict(d, "room_utilization")
    assert len(errors) > 0


def test_validate_optimization_trend_valid():
    d = {"trend_vs_previous": "improving"}
    assert validate_analytics_dict(d, "optimization_trend") == []


def test_validate_optimization_trend_invalid():
    d = {"trend_vs_previous": "sideways"}
    errors = validate_analytics_dict(d, "optimization_trend")
    assert any("trend_vs_previous" in e for e in errors)


def test_validate_governance_trend_valid():
    d = {"health_score": 90.0}
    assert validate_analytics_dict(d, "governance_trend") == []


def test_validate_governance_trend_invalid():
    d = {"health_score": "excellent"}
    errors = validate_analytics_dict(d, "governance_trend")
    assert any("health_score" in e for e in errors)


def test_validate_pdpa_boundary_valid():
    d = {"pdpa_level": "restricted", "allowed_output_aggregation": False}
    assert validate_analytics_dict(d, "pdpa_boundary") == []


def test_validate_pdpa_boundary_invalid_pdpa_level():
    d = {"pdpa_level": "topsecret", "allowed_output_aggregation": True}
    errors = validate_analytics_dict(d, "pdpa_boundary")
    assert any("pdpa_level" in e for e in errors)


def test_validate_unknown_schema_type():
    errors = validate_analytics_dict({}, "nonexistent_type")
    assert any("Unknown schema_type" in e for e in errors)


# ── sanitize_analytics_output ─────────────────────────────────────────────────

def test_sanitize_allowed_output_passthrough():
    boundary: PDPAAnalyticsBoundary = {
        "pdpa_level": "internal",
        "restricted_fields": ["student_name"],
        "allowed_output_aggregation": True,
    }
    obj = {"score": 82, "detail": {"room": "A-101", "count": 5}}
    result = sanitize_analytics_output(obj, boundary)
    assert result["score"] == 82
    assert result["detail"]["room"] == "A-101"


def test_sanitize_restricted_fields_removed():
    boundary: PDPAAnalyticsBoundary = {
        "pdpa_level": "restricted",
        "restricted_fields": ["student_name", "student_id"],
        "allowed_output_aggregation": True,
    }
    obj = {
        "score": 82,
        "detail": {
            "student_name": "สมุทร",
            "student_id": "12345678",
            "room": "A-101",
        },
    }
    result = sanitize_analytics_output(obj, boundary)
    assert "student_name" not in result["detail"]
    assert "student_id" not in result["detail"]
    assert result["detail"]["room"] == "A-101"


def test_sanitize_aggregation_not_allowed_suppresses_all():
    boundary: PDPAAnalyticsBoundary = {
        "pdpa_level": "restricted",
        "restricted_fields": ["student_name"],
        "allowed_output_aggregation": False,
    }
    obj = {"score": 100, "detail": "everything"}
    result = sanitize_analytics_output(obj, boundary)
    assert "suppressed" in result
    assert result["suppressed"] is True
    assert "detail" not in result


def test_sanitize_non_serialisable_value_replaced():
    boundary: PDPAAnalyticsBoundary = {
        "pdpa_level": "internal",
        "restricted_fields": [],
        "allowed_output_aggregation": True,
    }
    obj = {"ts": "2026-01-01"}
    result = sanitize_analytics_output(obj, boundary)
    assert isinstance(result, dict)


def test_sanitize_preserves_pdpa_level_in_suppressed_output():
    boundary: PDPAAnalyticsBoundary = {
        "pdpa_level": "restricted",
        "restricted_fields": ["sensitive"],
        "allowed_output_aggregation": False,
    }
    result = sanitize_analytics_output({"anything": "goes"}, boundary)
    assert result["pdpa_level"] == "restricted"
    assert result["suppressed"] is True
