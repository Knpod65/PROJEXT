"""Tests for role_dashboard_service — OPS-DASH-s4."""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from services.role_dashboard_service import RoleDashboardService
from contracts.dashboard_metric_contracts import RoleDashboardPayload, DashboardRoleSummary


_PANDAS_STATS = {
    "total_sections": 50, "scheduled_sections": 45,
    "unscheduled_sections": 5, "total_teachers": 5, "rooms_in_use": 3,
}


class TestRoleDashboardServiceDispatch:
    def _pay(self, role: str, ctx: dict | None = None) -> RoleDashboardPayload:
        return RoleDashboardService.build_role_dashboard(role, ctx)

    @pytest.mark.parametrize("role", [
        "admin", "staff", "teacher", "student",
        "print_shop", "dept_supervisor",
        "esq_head", "secretary", "it", "dpo", "executive",
    ])
    def test_known_roles_return_payload(self, role):
        p = self._pay(role)
        assert isinstance(p, dict)
        assert p["role"] == role
        assert "summary" in p
        assert "groups" in p
        assert p["unauthorized"] is False

    def test_unknown_role_unauthorized(self):
        p = self._pay("wizard")
        assert p["unauthorized"] is True
        assert p["groups"] == []
        assert p["summary"]["key_metrics"] == []

    def test_case_insensitive(self):
        p = self._pay("STAFF")
        assert p["unauthorized"] is False
        assert p["role"] == "staff"


class TestStaffDashboard:
    def test_staff_groups_present(self):
        p = RoleDashboardService.build_role_dashboard("staff")
        assert len(p["groups"]) >= 1

    def test_staff_no_student_pii(self):
        p = RoleDashboardService.build_role_dashboard("staff")
        pii = {"student_name", "teacher_name", "student_id"}
        for g in p["groups"]:
            for m in g["metrics"]:
                val = str(m.get("value", ""))
                for field in pii:
                    assert field not in val.lower(), f"PII {field} in staff metric: {m['metric_code']}"


class TestTeacherDashboard:
    def test_teacher_groups_present(self):
        p = RoleDashboardService.build_role_dashboard("teacher")
        assert len(p["groups"]) >= 1

    def test_teacher_no_cross_teacher_leakage(self):
        p = RoleDashboardService.build_role_dashboard("teacher")
        for g in p["groups"]:
            for m in g["metrics"]:
                assert "teacher_name" not in str(m.get("value", "")).lower()
                assert m.get("owner_role") in ("teacher", "admin"), \
                    f"Unexpected owner_role: {m.get('owner_role')} in {m['metric_code']}"


class TestStudentDashboard:
    def test_student_has_groups(self):
        p = RoleDashboardService.build_role_dashboard("student")
        assert len(p["groups"]) >= 1

    def test_student_no_other_student_data(self):
        p = RoleDashboardService.build_role_dashboard("student")
        for g in p["groups"]:
            for m in g["metrics"]:
                val = str(m.get("value", ""))
                assert "student_name" not in val.lower()
                assert "teacher_name" not in val.lower()

    def test_student_metrics_pdpa_safe(self):
        p = RoleDashboardService.build_role_dashboard("student")
        pii = {"student_name", "teacher_name", "employee_id"}
        for g in p["groups"]:
            for m in g["metrics"]:
                val = str(m.get("value", ""))
                for field in pii:
                    assert field not in val.lower()


class TestPrintShopDashboard:
    def test_print_shop_has_groups(self):
        p = RoleDashboardService.build_role_dashboard("print_shop")
        assert len(p["groups"]) >= 1

    def test_print_shop_metrics(self):
        p = RoleDashboardService.build_role_dashboard("print_shop")
        all_codes = []
        for g in p["groups"]:
            for m in g["metrics"]:
                all_codes.append(m["metric_code"])
        assert any("queue" in c for c in all_codes), \
            f"Expected queue metric in print_shop: {all_codes}"


class TestDeptSupervisorDashboard:
    def test_dept_supervisor_has_groups(self):
        p = RoleDashboardService.build_role_dashboard("dept_supervisor")
        assert len(p["groups"]) >= 1

    def test_dept_supervisor_context(self):
        ctx = {"dashboard_stats": _PANDAS_STATS}
        p = RoleDashboardService.build_role_dashboard("dept_supervisor", ctx)
        assert p["unauthorized"] is False

    def test_dept_supervisor_no_cross_dept_leakage(self):
        ctx = {"dashboard_stats": _PANDAS_STATS}
        p = RoleDashboardService.build_role_dashboard("dept_supervisor", ctx)
        for g in p["groups"]:
            for m in g["metrics"]:
                assert m.get("owner_role") in (
                    "dept_supervisor", "admin"
                ) or m["metric_code"] != "unscheduled_sections"


class TestEsqSecretaryDashboard:
    def test_esq_head_has_groups(self):
        p = RoleDashboardService.build_role_dashboard("esq_head")
        assert len(p["groups"]) >= 1

    def test_secretary_has_groups(self):
        p = RoleDashboardService.build_role_dashboard("secretary")
        assert len(p["groups"]) >= 1

    def test_esq_no_cross_dept_student_files(self):
        p = RoleDashboardService.build_role_dashboard("esq_head")
        for g in p["groups"]:
            for m in g["metrics"]:
                val = str(m.get("value", ""))
                assert "student_name" not in val.lower()


class TestITDashboard:
    def test_it_has_groups(self):
        p = RoleDashboardService.build_role_dashboard("it")
        assert len(p["groups"]) >= 1

    def test_it_no_academic_pii(self):
        p = RoleDashboardService.build_role_dashboard("it")
        pii = {"student_name", "teacher_name"}
        for g in p["groups"]:
            for m in g["metrics"]:
                val = str(m.get("value", ""))
                for field in pii:
                    assert field not in val.lower()

    def test_it_with_health_context(self):
        health = {"api_uptime_pct": 99.9, "db_ok": True, "storage_usage_pct": 34.5}
        p = RoleDashboardService.build_role_dashboard("it", {"health": health})
        assert p["unauthorized"] is False
        # Should include metrics populated from health context
        all_metrics = []
        for g in p["groups"]:
            all_metrics.extend(g["metrics"])
        assert len(all_metrics) > 0


class TestDPODashboard:
    def test_dpo_has_pdpa_group(self):
        p = RoleDashboardService.build_role_dashboard("dpo")
        assert len(p["groups"]) >= 1
        grp_codes = [g["group_code"] for g in p["groups"]]
        assert "pdpaSecurity" in grp_codes

    def test_dpo_no_raw_student_info(self):
        p = RoleDashboardService.build_role_dashboard("dpo")
        for g in p["groups"]:
            for m in g["metrics"]:
                val = str(m.get("value", ""))
                assert "student_name" not in val.lower()

    def test_dpo_metrics_are_aggregates(self):
        p = RoleDashboardService.build_role_dashboard("dpo")
        for g in p["groups"]:
            for m in g["metrics"]:
                # Values should be numbers or simple strings, never PII identifiers
                assert isinstance(m["value"], (int, float, str, type(None)))


class TestExecutiveDashboard:
    def test_executive_has_groups(self):
        p = RoleDashboardService.build_role_dashboard("executive")
        assert len(p["groups"]) >= 1

    def test_executive_with_summary(self):
        exec_summary = {
            "overall_health_score": 78.3,
            "risk_band": "amber",
            "top_risks": [{"risk": "low_stock"}],
        }
        p = RoleDashboardService.build_role_dashboard("executive", {"executive_summary": exec_summary})
        assert p["summary"]["health_score"] == 78.3
        assert p["summary"]["risk_band"] == "amber"
        top_risks_metric = next(
            (m for m in p["summary"]["key_metrics"] if m["metric_code"] == "top_risks"),
            None,
        )
        assert top_risks_metric is not None
        assert top_risks_metric["value"] == 1

    def test_executive_no_pii(self):
        p = RoleDashboardService.build_role_dashboard("executive")
        for g in p["groups"]:
            for m in g["metrics"]:
                val = str(m.get("value", ""))
                assert "student_name" not in val.lower()
                assert "teacher_full" not in val.lower()
