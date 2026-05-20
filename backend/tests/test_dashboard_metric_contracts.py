"""Tests for dashboard_metric_contracts — OPS-DASH-s1."""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from contracts.dashboard_metric_contracts import (
    validate_metric,
    validate_pdpa_level,
    build_minimal_metric,
    build_minimal_group,
    build_minimal_dashboard,
    build_minimal_payload,
    _PDPA_LEVELS,
)


class TestValidatePdpaLevel:
    def test_all_levels_valid(self):
        for level in ("public", "internal", "confidential", "restricted"):
            assert validate_pdpa_level(level) is True

    def test_invalid_level(self):
        assert validate_pdpa_level("super_secret") is False
        assert validate_pdpa_level("") is False


class TestValidateMetric:
    def test_minimal_metric_is_valid(self):
        m = build_minimal_metric()
        errors = validate_metric(m)
        assert errors == [], errors

    def test_missing_key_reports_error(self):
        m = build_minimal_metric()
        del m["unit"]  # type: ignore[misc]
        errors = validate_metric(m)
        assert any("unit" in e for e in errors)

    def test_invalid_pdpa_level_reports_error(self):
        m = build_minimal_metric({"pdpa_level": "invalid"})
        errors = validate_metric(m)
        assert any("pdpa_level" in e for e in errors)

    def test_wrong_type_reports_error(self):
        # pdpa_level must be str; pass None to trigger type error
        m = build_minimal_metric({"pdpa_level": None})
        errors = validate_metric(m)
        # pdpa_level key is present but wrong type — validate_metric also
        # separately rejects invalid enum values; either path produces an error
        assert errors, "expected at least one validation error for None pdpa_level"
        assert any("pdpa_level" in e for e in errors)


class TestBuildMinimalMetric:
    def test_default_fields(self):
        m = build_minimal_metric()
        assert m["metric_code"] == "minimal"
        assert m["pdpa_level"] == "internal"
        assert m["severity"] == "info"
        assert m["drilldown_route"] is None
        assert m["updated_at"] is None

    def test_override(self):
        m = build_minimal_metric({"value": 42, "pdpa_level": "restricted"})
        assert m["value"] == 42
        assert m["pdpa_level"] == "restricted"


class TestBuildMinimalGroup:
    def test_default_fields(self):
        g = build_minimal_group()
        assert g["group_code"] == "default"
        assert len(g["metrics"]) == 1
        assert g["alerts"] == []
        assert g["recommended_actions"] == []


class TestBuildMinimalDashboard:
    def test_returns_10_groups(self):
        d = build_minimal_dashboard()
        assert len(d["groups"]) == 10

    def test_group_codes(self):
        expected = {
            "examOperations", "optimizationQuality", "governanceApproval",
            "staffWorkload", "roomCapacity", "teacherSubmission",
            "printExport", "qrPickup", "pdpaSecurity", "systemOperations",
        }
        d = build_minimal_dashboard()
        actual = {g["group_code"] for g in d["groups"]}
        assert actual == expected

    def test_role_is_admin(self):
        d = build_minimal_dashboard()
        assert d["role"] == "admin"

    def test_health_score_present(self):
        d = build_minimal_dashboard()
        assert isinstance(d["overall_health_score"], float)


class TestBuildMinimalPayload:
    def test_default_role(self):
        p = build_minimal_payload()
        assert p["role"] == "admin"
        assert p["unauthorized"] is False

    def test_custom_role(self):
        p = build_minimal_payload("teacher")
        assert p["role"] == "teacher"
        assert "teacher" in p["role_label_i18n_key"]

    def test_unauthorized(self):
        p = build_minimal_payload(override={"unauthorized": True})
        assert p["unauthorized"] is True

    def test_has_summary_and_groups(self):
        p = build_minimal_payload()
        assert "summary" in p
        assert "groups" in p
        assert isinstance(p["summary"]["key_metrics"], list)
        assert isinstance(p["groups"], list)
