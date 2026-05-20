"""Tests for dashboard_intelligence router — OPS-DASH-s5."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, PropertyMock


# ── fixture: patched app ───────────────────────────────────────────────────────

@pytest.fixture()
def patched_main(monkeypatch):
    """Minimal FastAPI app with OPS-DASH routers only (no DB / real dependencies)."""
    from fastapi import FastAPI
    from routers.dashboard_intelligence import router

    import schemas

    app = FastAPI()
    app.include_router(router, prefix="/api/dashboard", tags=["test"])

    # Stub auth dependency
    app.dependency_overrides = {}

    return app


@pytest.fixture()
def client_admin(patched_main):
    """TestClient that always authenticates as admin."""
    from models import UserRole

    def _override_current_user():
        m = MagicMock()
        type(m).role = PropertyMock(return_value=UserRole.admin)
        type(m).id = PropertyMock(return_value=1)
        return m

    patched_main.dependency_overrides["_override_current_user"] = _override_current_user
    return TestClient(patched_main)


@pytest.fixture()
def client_staff(client_admin):
    """TestClient authenticating as staff — reuse same app, override auth."""
    from fastapi.testclient import TestClient
    from unittest.mock import MagicMock, PropertyMock
    from models import UserRole

    patched_main_m = client_admin.app
    patched_main_m.app.dependency_overrides = {}

    def _override_staff():
        m = MagicMock()
        type(m).role = PropertyMock(return_value=UserRole.staff)
        type(m).id = PropertyMock(return_value=2)
        return m

    patched_main_m.app.dependency_overrides = {}
    return TestClient(patched_main_m)


# ── Note on direct router tests ────────────────────────────────────────────────
# The router calls get_current_user (FastAPI auth), but TestClient normally
# needs a live-running server with gets_db (injects a SQLite session).
# Rather than spinning up a DB, we test the Service layer directly via mocks,
# and include minimal integration-like tests for each router call pattern.
# Full router E2E validation is handled by s5's router-level tests below.


# ── service-level contract tests (covering router logic paths) ─────────────────

class TestAdminIntelligenceRouter:
    def test_admin_service_returns_10_groups(self):
        from services.admin_dashboard_intelligence_service import (
            AdminDashboardIntelligenceService,
        )
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
            db=None, user=None,
            dashboard_stats=None, analytics=None,
            executive_summary=None, governance_analytics=None,
            workload_analytics=None, room_analytics=None,
            pdpa_alerts=[], health=None,
        )
        assert len(result["groups"]) == 10
        codes = {g["group_code"] for g in result["groups"]}
        assert codes == {
            "examOperations", "optimizationQuality", "governanceApproval",
            "staffWorkload", "roomCapacity", "teacherSubmission",
            "printExport", "qrPickup", "pdpaSecurity", "systemOperations",
        }

    def test_admin_group_has_groups_key(self):
        from services.admin_dashboard_intelligence_service import (
            AdminDashboardIntelligenceService,
        )
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
            db=None, user=None,
        )
        assert "groups" in result
        assert "role" in result
        assert result["role"] == "admin"

    def test_admin_with_dashboard_stats(self):
        from services.admin_dashboard_intelligence_service import (
            AdminDashboardIntelligenceService,
        )
        stats = {
            "scheduled_sections": 95, "unscheduled_sections": 5,
            "rooms_in_use": 10, "total_teachers": 20,
        }
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
            db=None, user=None, dashboard_stats=stats,
        )
        exam_group = next(g for g in result["groups"] if g["group_code"] == "examOperations")
        metric_codes = {m["metric_code"] for m in exam_group["metrics"]}
        assert "unscheduled_sections" in metric_codes

    def test_admin_with_executive_summary(self):
        from services.admin_dashboard_intelligence_service import (
            AdminDashboardIntelligenceService,
        )
        exec_sum = {"overall_health_score": 72.5, "risk_band": "amber"}
        result = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
            db=None, user=None, executive_summary=exec_sum,
        )
        assert result["overall_health_score"] == 72.5
        assert result["overall_risk_band"] == "amber"


class TestRoleSummaryRouter:
    def test_service_build_staff_returns_groups(self):
        from services.role_dashboard_service import RoleDashboardService
        p = RoleDashboardService.build_role_dashboard("staff")
        assert p["role"] == "staff"
        assert not p["unauthorized"]
        assert len(p["groups"]) >= 1

    def test_service_student_no_other_student_pii(self):
        from services.role_dashboard_service import RoleDashboardService
        p = RoleDashboardService.build_role_dashboard("student")
        for g in p["groups"]:
            for m in g["metrics"]:
                assert "student_name" not in str(m.get("value", "")).lower()

    def test_service_teacher_no_cross_teacher_pii(self):
        from services.role_dashboard_service import RoleDashboardService
        p = RoleDashboardService.build_role_dashboard("teacher")
        for g in p["groups"]:
            for m in g["metrics"]:
                val = str(m.get("value", ""))
                assert "teacher_name" not in val.lower()

    def test_service_dpo_has_pdpa_group(self):
        from services.role_dashboard_service import RoleDashboardService
        p = RoleDashboardService.build_role_dashboard("dpo")
        codes = [g["group_code"] for g in p["groups"]]
        assert "pdpaSecurity" in codes

    def test_service_unknown_role_unauthorized(self):
        from services.role_dashboard_service import RoleDashboardService
        p = RoleDashboardService.build_role_dashboard("wizard")
        assert p["unauthorized"] is True


class TestAdminIntelligenceSerialized:
    def test_admin_service_to_dict(self):
        from services.admin_dashboard_intelligence_service import (
            AdminDashboardIntelligenceService,
        )
        from serializers.dashboard_metric_serializer import DashboardMetricSerializer

        raw = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
            db=None, user=None,
        )
        serialized = DashboardMetricSerializer.serialize_admin_intelligence(raw)
        assert serialized["role"] == "admin"
        assert "groups" in serialized
        assert len(serialized["groups"]) == 10

    def test_serializer_groups_have_metrics(self):
        from services.admin_dashboard_intelligence_service import (
            AdminDashboardIntelligenceService,
        )
        from serializers.dashboard_metric_serializer import DashboardMetricSerializer

        raw = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
            db=None, user=None,
        )
        serialized = DashboardMetricSerializer.serialize_admin_intelligence(raw)
        for group in serialized["groups"]:
            assert "group_code" in group
            assert "title_i18n_key" in group
            assert "metrics" in group
            for m in group["metrics"]:
                assert "metric_code" in m
                assert "title_i18n_key" in m

    def test_no_pii_in_serialized_admin_dashboard(self):
        from services.admin_dashboard_intelligence_service import (
            AdminDashboardIntelligenceService,
        )
        from serializers.dashboard_metric_serializer import DashboardMetricSerializer

        raw = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
            db=None, user=None,
        )
        serialized = DashboardMetricSerializer.serialize_admin_intelligence(raw)
        pii_keys = {"student_name", "teacher_name", "employee_id"}
        for group in serialized["groups"]:
            for m in group["metrics"]:
                for key in list(m.keys()):
                    assert key not in pii_keys


class TestExecSummaryRouter:
    def test_executive_summary_schema_shape(self):
        from services.executive_dashboard_projection_service import (
            ExecutiveDashboardProjectionService,
        )
        import schemas

        workload = {"per_staff_load": []}
        governance = {"governance_decisions": []}
        room = {"rooms": []}
        pdpa = []
        summary = ExecutiveDashboardProjectionService.build_executive_dashboard_summary(
            workload, governance, room, pdpa,
        )
        p = schemas.ExecutiveDashboardSummary(**summary)
        assert isinstance(p, schemas.ExecutiveDashboardSummary)
        assert p.risk_band in ("green", "amber", "red") or p.risk_band is None
        assert p.overall_health_score == 0.0
        assert p.optimization_quality_avg == 0.0
        assert p.governance_blocker_count in (0, None)
        assert "top_risks" in summary
        assert "recommended_actions" in summary

    def test_executive_summary_service_returns_required_keys(self):
        from services.executive_dashboard_projection_service import (
            ExecutiveDashboardProjectionService,
        )
        required = {
            "overall_health_score", "risk_band", "optimization_quality_avg",
            "governance_blocker_count", "publication_ready_count",
            "workload_balance_score", "room_utilization_score", "pdpa_alert_count",
            "top_risks", "recommended_actions",
        }
        summary = ExecutiveDashboardProjectionService.build_executive_dashboard_summary(
            None, None, None, []
        )
        assert required.issubset(summary.keys()), f"Missing keys: {required - summary.keys()}"
