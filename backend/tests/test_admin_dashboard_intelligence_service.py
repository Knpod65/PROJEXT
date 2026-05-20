"""Tests for admin_dashboard_intelligence_service — OPS-DASH-s3."""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from services.admin_dashboard_intelligence_service import AdminDashboardIntelligenceService
from contracts.dashboard_metric_contracts import AdminIntelligenceDashboard, DashboardMetricGroup

_PANDAS_MINIMAL_STATS = {
    "total_sections": 100,
    "scheduled_sections": 95,
    "unscheduled_sections": 5,
    "total_students": 3000,
    "total_sheets": 5000,
    "total_teachers": 20,
    "rooms_in_use": 10,
}


class TestBuildAdminIntelligenceDashboard:
    def test_returns_admin_intelligence_dashboard_type(self):
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
            db=None,
            user=None,
        )
        assert isinstance(result, dict)
        assert "groups" in result
        assert "role" in result

    def test_all_10_groups_present(self):
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(db=None, user=None)
        codes = {g["group_code"] for g in result["groups"]}
        expected = {
            "examOperations", "optimizationQuality", "governanceApproval",
            "staffWorkload", "roomCapacity", "teacherSubmission",
            "printExport", "qrPickup", "pdpaSecurity", "systemOperations",
        }
        assert codes == expected, f"Missing groups: {expected - codes}"

    def test_every_metric_has_i18n_keys(self):
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(db=None, user=None)
        for group in result["groups"]:
            for metric in group["metrics"]:
                assert metric["metric_code"], "metric_code must be non-empty"
                assert metric["title_i18n_key"], f"title_i18n_key missing in {metric['metric_code']}"
                assert metric["description_i18n_key"], f"description_i18n_key missing in {metric['metric_code']}"
                assert metric["why_it_matters_i18n_key"], f"why_it_matters_i18n_key missing in {metric['metric_code']}"
                assert metric["recommended_action_i18n_key"], f"recommended_action_i18n_key missing in {metric['metric_code']}"

    def test_no_raw_pii_in_values(self):
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(db=None, user=None)
        _PII_FIELDS = {"student_name", "teacher_name", "employee_id", "student_id", "pdf_filepath"}
        for group in result["groups"]:
            for metric in group["metrics"]:
                val_str = str(metric.get("value", ""))
                assert "student_name" not in val_str.lower(), f"PII in value: {val_str}"
                assert "teacher_name" not in val_str.lower(), f"PII in value: {val_str}"

    def test_safe_fallback_with_no_data(self):
        """When all data sources are absent, returns 10 groups with fallback metrics."""
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
            db=None, user=None,
            dashboard_stats=None, analytics=None, executive_summary=None,
            governance_analytics=None, workload_analytics=None,
            room_analytics=None, pdpa_alerts=[], health=None,
        )
        assert len(result["groups"]) == 10
        # Each group must have a well-formed metric list (zero or more)
        for group in result["groups"]:
            assert "metrics" in group
            assert isinstance(group["metrics"], list)

    def test_overall_health_score_admin_summary(self):
        exec_summary = {"overall_health_score": 72.5, "risk_band": "amber"}
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
            db=None, user=None, executive_summary=exec_summary
        )
        assert result["overall_health_score"] == 72.5
        assert result["overall_risk_band"] == "amber"

    def test_overall_health_default_green(self):
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
            db=None, user=None, executive_summary={}
        )
        assert result["overall_risk_band"] == "green"

    def test_pdpa_security_group_uses_pdpa_alerts_count(self):
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
            db=None, user=None, pdpa_alerts=[{"id": 1}, {"id": 2}, {"id": 3}]
        )
        pdpa_group = next(g for g in result["groups"] if g["group_code"] == "pdpaSecurity")
        assert pdpa_group["metrics"][0]["value"] == 3
        assert pdpa_group["metrics"][0]["pdpa_level"] == "restricted"

    def test_exam_ops_group_uses_dashboard_stats(self):
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
            db=None, user=None, dashboard_stats=_PANDAS_MINIMAL_STATS
        )
        exam_group = next(g for g in result["groups"] if g["group_code"] == "examOperations")
        metric_codes = {m["metric_code"] for m in exam_group["metrics"]}
        assert "unscheduled_sections" in metric_codes
        unscheduled = next(m for m in exam_group["metrics"] if m["metric_code"] == "unscheduled_sections")
        assert unscheduled["value"] == 5
        assert unscheduled["unit"] == "sections"
        assert unscheduled["pdpa_level"] == "internal"

    def test_all_group_codes_unique(self):
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(db=None, user=None)
        codes = [g["group_code"] for g in result["groups"]]
        assert len(codes) == len(set(codes)), "Duplicate group codes detected"

    def test_last_computed_at_is_iso(self):
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(db=None, user=None)
        assert result["last_computed_at"] is not None
        assert "T" in result["last_computed_at"]  # ISO-8601

    def test_groups_order(self):
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(db=None, user=None)
        expected_order = [
            "examOperations", "optimizationQuality", "governanceApproval",
            "staffWorkload", "roomCapacity", "teacherSubmission",
            "printExport", "qrPickup", "pdpaSecurity", "systemOperations",
        ]
        actual = [g["group_code"] for g in result["groups"]]
        assert actual == expected_order
