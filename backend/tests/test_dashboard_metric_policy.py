"""Tests for dashboard_metric_policy — OPS-DASH-s2."""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from policies.dashboard_metric_policy import DashboardMetricPolicy


class TestCanViewAdminIntelligence:
    def test_admin_allowed(self):
        assert DashboardMetricPolicy.can_view_admin_intelligence("admin") is True

    def test_non_admin_denied(self):
        for role in ("staff", "teacher", "student", "esq_head", "dpo"):
            assert DashboardMetricPolicy.can_view_admin_intelligence(role) is False

    def test_case_insensitive(self):
        assert DashboardMetricPolicy.can_view_admin_intelligence("Admin") is True


class TestCanViewRoleSummary:
    def test_same_role_allowed(self):
        assert DashboardMetricPolicy.can_view_role_summary("staff", "staff") is True

    def test_admin_can_view_any(self):
        for target in ("staff", "teacher", "student", "print_shop"):
            assert DashboardMetricPolicy.can_view_role_summary("admin", target) is True

    def test_esq_can_view_any(self):
        assert DashboardMetricPolicy.can_view_role_summary("esq_head", "teacher") is True

    def test_teacher_not_staff(self):
        assert not DashboardMetricPolicy.can_view_role_summary("teacher", "staff")

    def test_student_not_teacher(self):
        assert not DashboardMetricPolicy.can_view_role_summary("student", "teacher")


class TestCanViewPdpaHealth:
    def test_admin_allowed(self):
        assert DashboardMetricPolicy.can_view_pdpa_health("admin") is True

    def test_esq_secretary_allowed(self):
        assert DashboardMetricPolicy.can_view_pdpa_health("esq_head") is True
        assert DashboardMetricPolicy.can_view_pdpa_health("secretary") is True

    def test_dpo_allowed(self):
        assert DashboardMetricPolicy.can_view_pdpa_health("dpo") is True

    def test_student_denied(self):
        assert not DashboardMetricPolicy.can_view_pdpa_health("student")

    def test_teacher_denied(self):
        assert not DashboardMetricPolicy.can_view_pdpa_health("teacher")


class TestCanViewExecutiveSummary:
    def test_admin_allowed(self):
        assert DashboardMetricPolicy.can_view_executive_summary("admin") is True

    def test_esq_head_allowed(self):
        assert DashboardMetricPolicy.can_view_executive_summary("esq_head") is True

    def test_student_denied(self):
        assert not DashboardMetricPolicy.can_view_executive_summary("student")


class TestAuthorizeRoleDashboardAccess:
    def test_known_roles(self):
        for role in ("admin", "staff", "teacher", "student", "print_shop",
                     "dept_supervisor", "esq_head", "secretary", "it", "dpo", "executive"):
            DashboardMetricPolicy.authorize_role_dashboard_access(role)  # no error

    def test_unknown_role_raises(self):
        with pytest.raises(ValueError):
            DashboardMetricPolicy.authorize_role_dashboard_access("zombie")

    def test_case_insensitive(self):
        DashboardMetricPolicy.authorize_role_dashboard_access("Staff")  # no error
