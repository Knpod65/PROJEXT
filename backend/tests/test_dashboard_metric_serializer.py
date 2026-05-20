"""Tests for dashboard_metric_serializer — OPS-DASH-s2."""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from contracts.dashboard_metric_contracts import (
    build_minimal_metric,
    build_minimal_group,
    build_minimal_dashboard,
    build_minimal_payload,
    DashboardMetricGroup,
)
from serializers.dashboard_metric_serializer import (
    DashboardMetricSerializer,
    _clearance_set,
    _redacted_metric,
)


class TestSerializeDashboardMetric:
    def test_admin_sees_restricted_value(self):
        m = build_minimal_metric({"pdpa_level": "restricted", "value": 999})
        out = DashboardMetricSerializer.serialize_dashboard_metric(m, "admin")
        assert out["value"] == 999

    def test_student_gets_restricted_redacted(self):
        m = build_minimal_metric({"pdpa_level": "restricted", "value": 999})
        out = DashboardMetricSerializer.serialize_dashboard_metric(m, "student")
        assert out["value"] == "[RESTRICTED]"
        assert out["trend"] == "unknown"
        assert out["severity"] == "info"
        assert out["drilldown_route"] is None

    def test_public_passes_through_for_all_roles(self):
        m = build_minimal_metric({"pdpa_level": "public", "value": 5})
        for role in ("student", "teacher", "admin"):
            out = DashboardMetricSerializer.serialize_dashboard_metric(m, role)
            assert out["value"] == 5

    def test_confidential_hidden_from_student(self):
        m = build_minimal_metric({"pdpa_level": "confidential", "value": 7})
        out = DashboardMetricSerializer.serialize_dashboard_metric(m, "student")
        assert out["value"] == "[RESTRICTED]"

    def test_no_role_no_filtering(self):
        m = build_minimal_metric({"pdpa_level": "restricted"})
        out = DashboardMetricSerializer.serialize_dashboard_metric(m, None)
        assert out["value"] != "[RESTRICTED]"


class TestSerializeMetricGroup:
    def test_all_metrics_passthrough_for_admin(self):
        m_public = build_minimal_metric({"pdpa_level": "public"})
        m_conf = build_minimal_metric({"pdpa_level": "confidential"})
        group: DashboardMetricGroup = build_minimal_group(
            {"metrics": [m_public, m_conf]}
        )
        out = DashboardMetricSerializer.serialize_metric_group(group, "admin")
        assert len(out["metrics"]) == 2

    def test_student_sees_only_public(self):
        m_public = build_minimal_metric({"pdpa_level": "public", "value": 1})
        m_conf = build_minimal_metric({"pdpa_level": "confidential", "value": 2})
        group = build_minimal_group({"metrics": [m_public, m_conf]})
        out = DashboardMetricSerializer.serialize_metric_group(group, "student")
        # Serializer keeps the metric but redacts the value — preserves structural
        # visibility so frontend still knows public vs restricted rows exist.
        assert len(out["metrics"]) == 2
        assert out["metrics"][0]["value"] == 1
        assert out["metrics"][1]["value"] == "[RESTRICTED]"
        # Conf metric fields preserved but value redacted
        assert out["metrics"][1]["metric_code"] == "minimal"

    def test_alerts_and_actions_passthrough(self):
        group = build_minimal_group({
            "alerts": ["a1"],
            "recommended_actions": ["r1"],
        })
        out = DashboardMetricSerializer.serialize_metric_group(group, "admin")
        assert out["alerts"] == ["a1"]
        assert out["recommended_actions"] == ["r1"]


class TestSerializeAdminIntelligence:
    def test_shape(self):
        d = build_minimal_dashboard()
        out = DashboardMetricSerializer.serialize_admin_intelligence(d)
        assert out["role"] == "admin"
        assert "groups" in out
        assert len(out["groups"]) == 10

    def test_student_gets_redacted_metrics(self):
        d = build_minimal_dashboard()
        out = DashboardMetricSerializer.serialize_admin_intelligence(d)
        # Admin serializer always uses admin role, so all metrics visible
        # Redaction only happens through serialize_dashboard_metric with role arg


class TestSerializeRolePayload:
    def test_shape(self):
        payload = build_minimal_payload("teacher")
        out = DashboardMetricSerializer.serialize_role_payload(payload, "teacher")
        assert out["role"] == "teacher"
        assert "summary" in out
        assert "groups" in out
        assert out["unauthorized"] is False

    def test_unauthorized_passthrough(self):
        payload = build_minimal_payload(override={"unauthorized": True})
        out = DashboardMetricSerializer.serialize_role_payload(payload)
        assert out["unauthorized"] is True


class TestClearanceSet:
    def test_admin(self):
        assert _clearance_set("admin") == {"public", "internal", "confidential", "restricted"}

    def test_dpo(self):
        assert _clearance_set("dpo") == {"public", "internal", "confidential", "restricted"}

    def test_staff(self):
        assert _clearance_set("staff") == {"public", "internal"}

    def test_student(self):
        assert _clearance_set("student") == {"public"}

    def test_teacher(self):
        assert _clearance_set("teacher") == {"public", "internal"}

    def test_unknown_defaults_to_public(self):
        assert _clearance_set("wizard") == {"public"}


class TestRedactedMetric:
    def test_value_redacted(self):
        m = build_minimal_metric({"value": 42})
        r = _redacted_metric(m)
        assert r["value"] == "[RESTRICTED]"

    def test_route_replaced(self):
        m = build_minimal_metric({"drilldown_route": "/schedule"})
        r = _redacted_metric(m)
        assert r["drilldown_route"] is None

    def test_other_fields_preserved(self):
        m = build_minimal_metric({"metric_code": "X1", "pdpa_level": "restricted"})
        r = _redacted_metric(m)
        assert r["metric_code"] == "X1"
        assert r["pdpa_level"] == "restricted"
        assert r["severity"] == "info"
        assert r["trend"] == "unknown"
