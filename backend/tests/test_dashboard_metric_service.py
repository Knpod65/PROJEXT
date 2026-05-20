"""Tests for dashboard_metric_service — OPS-DASH-s2."""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from services.dashboard_metric_service import DashboardMetricService
from contracts.dashboard_metric_contracts import build_minimal_metric


class TestBuildMetric:
    def test_all_fields(self):
        m = DashboardMetricService.build_metric(
            metric_code="test_001",
            title_i18n_key="dashboard.m.x",
            description_i18n_key="dashboard.m.x.d",
            value=42,
            unit="sections",
            trend="up",
            trend_label_i18n_key="dashboard.trendUp",
            severity="warning",
            why_it_matters_i18n_key="dashboard.m.x.wim",
            recommended_action_i18n_key="dashboard.m.x.ra",
            owner_role="admin",
            drilldown_route="/schedule",
            updated_at="2026-05-20T08:00:00Z",
            pdpa_level="internal",
        )
        assert m["metric_code"] == "test_001"
        assert m["value"] == 42
        assert m["unit"] == "sections"
        assert m["trend"] == "up"
        assert m["pdpa_level"] == "internal"

    def test_defaults(self):
        m = DashboardMetricService.build_metric(
            metric_code="d",
            title_i18n_key="t",
            description_i18n_key="d",
            value=0,
            unit="",
            trend="unknown",
            trend_label_i18n_key="t",
            severity="info",
            why_it_matters_i18n_key="w",
            recommended_action_i18n_key="a",
            owner_role="admin",
        )
        assert m["drilldown_route"] is None
        assert m["updated_at"] is None
        assert m["pdpa_level"] == "internal"


class TestBuildMetricGroup:
    def test_group_basic(self):
        metric = build_minimal_metric()
        g = DashboardMetricService.build_metric_group(
            group_code="examOperations",
            title_i18n_key="dashboard.admin.group.examOperations",
            description_i18n_key="dashboard.admin.group.examOperations.description",
            metrics=[metric],
            alerts=["alert!"],
            recommended_actions=["action!"],
        )
        assert g["group_code"] == "examOperations"
        assert len(g["metrics"]) == 1
        assert g["alerts"] == ["alert!"]
        assert g["recommended_actions"] == ["action!"]

    def test_group_defaults(self):
        g = DashboardMetricService.build_metric_group("g", "t", "d", [])
        assert g["alerts"] == []
        assert g["recommended_actions"] == []


class TestBuildAlert:
    def test_alert_shape(self):
        a = DashboardMetricService.build_alert(
            alert_code="X1",
            severity="critical",
            title_i18n_key="dashboard.alerts.X1",
            body_i18n_key="dashboard.alerts.X1.body",
            metric_codes=["m1"],
            pdpa_level="public",
        )
        assert a["alert_code"] == "X1"
        assert a["metric_codes"] == ["m1"]


class TestClassifyMetricSeverity:
    def test_critical(self):
        assert DashboardMetricService.classify_metric_severity(
            10.0, {"critical": 5.0, "warning": 3.0, "info": 1.0}) == "critical"

    def test_warning(self):
        assert DashboardMetricService.classify_metric_severity(
            3.5, {"critical": 5.0, "warning": 3.0, "info": 1.0}) == "warning"

    def test_info(self):
        # 1.5 >= info=1.0 but < warning=3.0
        assert DashboardMetricService.classify_metric_severity(
            1.5, {"critical": 5.0, "warning": 3.0, "info": 1.0}) == "info"

    def test_good_below_all(self):
        assert DashboardMetricService.classify_metric_severity(
            0.0, {"critical": 5.0, "warning": 3.0, "info": 1.0}) == "good"

    def test_unknown_for_non_numeric(self):
        assert DashboardMetricService.classify_metric_severity(
            "n/a", {"critical": 5.0}) == "unknown"

    def test_unknown_for_none(self):
        assert DashboardMetricService.classify_metric_severity(None, {}) == "unknown"

    def test_empty_thresholds_all_good(self):
        assert DashboardMetricService.classify_metric_severity(99.9, {}) == "good"


class TestFilterMetricsForRole:
    def make_metric(self, pdpa_level: str) -> dict:
        return build_minimal_metric({"pdpa_level": pdpa_level})

    def test_admin_sees_all(self):
        m_restricted = self.make_metric("restricted")
        assert DashboardMetricService.filter_metrics_for_role(
            [m_restricted], "admin") == [m_restricted]

    def test_dpo_sees_all(self):
        m_restricted = self.make_metric("restricted")
        assert DashboardMetricService.filter_metrics_for_role(
            [m_restricted], "dpo") == [m_restricted]

    def test_student_gets_only_public(self):
        m_public = self.make_metric("public")
        m_conf = self.make_metric("confidential")
        assert DashboardMetricService.filter_metrics_for_role(
            [m_public, m_conf], "student") == [m_public]

    def test_teacher_gets_public_and_internal(self):
        m_internal = self.make_metric("internal")
        m_conf = self.make_metric("confidential")
        assert DashboardMetricService.filter_metrics_for_role(
            [m_internal, m_conf], "teacher") == [m_internal]

    def test_case_insensitive(self):
        m_restricted = self.make_metric("restricted")
        assert DashboardMetricService.filter_metrics_for_role(
            [m_restricted], "Admin") == [m_restricted]


class TestSafeEmptyMetric:
    def test_returns_valid_metric(self):
        m = DashboardMetricService.safe_empty_metric("demo_metric")
        assert m["metric_code"] == "demo_metric"
        assert m["value"] == 0
        assert m["severity"] == "info"
        assert m["pdpa_level"] == "internal"


class TestOpsHealthGroups:
    def test_returns_list(self):
        result = DashboardMetricService.build_ops_health_groups({})
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["group_code"] == "systemOperations"

    def test_metric_count(self):
        health = {}
        result = DashboardMetricService.build_ops_health_groups(health)
        assert len(result[0]["metrics"]) == 3  # api + db + storage

    def test_real_values(self):
        health = {"api_uptime_pct": 99.9, "db_ok": True, "storage_usage_pct": 34.5}
        result = DashboardMetricService.build_ops_health_groups(health)
        metric_values = {m["metric_code"]: m["value"] for m in result[0]["metrics"]}
        assert metric_values["api_uptime_pct"] == 99.9
        assert metric_values["db_ok"] == 1.0
        assert metric_values["storage_usage_pct"] == 34.5

    def test_bad_values_default_to_zero(self):
        health = {"api_uptime_pct": "not_a_number", "db_ok": None}
        result = DashboardMetricService.build_ops_health_groups(health)
        metric_values = {m["metric_code"]: m["value"] for m in result[0]["metrics"]}
        assert metric_values["api_uptime_pct"] == 0.0
        assert metric_values["db_ok"] == 0.0


class TestPdpaHealthGroups:
    def test_empty_alerts_get_zero_count(self):
        result = DashboardMetricService.build_pdpa_health_groups([])
        assert len(result) == 1
        metric = result[0]["metrics"][0]
        assert metric["value"] == 0

    def test_alerts_count(self):
        result = DashboardMetricService.build_pdpa_health_groups(
            [{"id": 1}, {"id": 2}, {"id": 3}]
        )
        assert result[0]["metrics"][0]["value"] == 3

    def test_pdpa_level_restricted(self):
        result = DashboardMetricService.build_pdpa_health_groups([])
        assert result[0]["metrics"][0]["pdpa_level"] == "restricted"
