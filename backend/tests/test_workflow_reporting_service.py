"""Tests for workflow_user_service and workflow_reporting_service."""
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.workflow_user_service import format_user_dict, build_external_workflow_issues
from services.workflow_reporting_service import build_staff_workload_report


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_user(**kwargs):
    u = MagicMock()
    u.id = kwargs.get("id", 1)
    u.username = kwargs.get("username", "jdoe")
    u.email = kwargs.get("email", "jdoe@example.com")
    role = MagicMock()
    role.value = kwargs.get("role", "staff")
    u.role = role if kwargs.get("role") is not False else None
    u.full_name = kwargs.get("full_name", "John Doe")
    u.title = kwargs.get("title", "Mr.")
    u.division = kwargs.get("division", "IT")
    u.unit = kwargs.get("unit", "Ops")
    u.dept_code = kwargs.get("dept_code", "IT01")
    u.mobile = kwargs.get("mobile", "0811111111")
    u.ext = kwargs.get("ext", "123")
    u.employee_id = kwargs.get("employee_id", 42)
    u.is_active = kwargs.get("is_active", True)
    return u


def _make_exam(exam_id, *, supervisions=None, invigilators_needed=1, title=None, date="2026-01-01", time="09:00"):
    e = MagicMock()
    e.id = exam_id
    e.supervisions = supervisions if supervisions is not None else []
    e.invigilators_needed = invigilators_needed
    e.title = title
    e.exam_date = date
    e.exam_time = time
    return e


def _make_period(period_id=1, **kwargs):
    p = MagicMock()
    p.id = period_id
    p.semester = kwargs.get("semester", 1)
    p.academic_year = kwargs.get("academic_year", 2026)
    p.exam_type = kwargs.get("exam_type", "midterm")
    p.label = kwargs.get("label", "Midterm 2026/1")
    return p


# ── format_user_dict ──────────────────────────────────────────────────────────

def test_format_user_dict_returns_all_keys():
    u = _make_user()
    result = format_user_dict(u)
    expected_keys = {
        "id", "username", "email", "role", "full_name", "title",
        "division", "unit", "dept_code", "mobile", "ext", "employee_id", "is_active",
    }
    assert expected_keys == set(result.keys())


def test_format_user_dict_values_match():
    u = _make_user(username="alice", email="alice@test.com", role="admin")
    result = format_user_dict(u)
    assert result["username"] == "alice"
    assert result["email"] == "alice@test.com"
    assert result["role"] == "admin"


def test_format_user_dict_none_role():
    u = _make_user(role=False)
    u.role = None
    result = format_user_dict(u)
    assert result["role"] is None


def test_format_user_dict_is_active_propagated():
    u = _make_user(is_active=False)
    assert format_user_dict(u)["is_active"] is False


# ── build_external_workflow_issues ────────────────────────────────────────────

def test_build_issues_no_period_returns_empty():
    db = MagicMock()
    assert build_external_workflow_issues(db, None) == []
    assert build_external_workflow_issues(db, 0) == []


def test_build_issues_no_exams_returns_empty():
    db = MagicMock()
    db.query.return_value.options.return_value.filter.return_value.order_by.return_value.all.return_value = []
    assert build_external_workflow_issues(db, 1) == []


def test_build_issues_no_invigilator_assigned():
    db = MagicMock()
    exam = _make_exam(10, supervisions=[], invigilators_needed=2, title="Finals")
    db.query.return_value.options.return_value.filter.return_value.order_by.return_value.all.return_value = [exam]
    issues = build_external_workflow_issues(db, 1)
    assert len(issues) == 1
    assert issues[0]["type"] == "no_invigilator_assigned"
    assert issues[0]["severity"] == "error"
    assert issues[0]["id"] == "external-none-10"


def test_build_issues_staff_shortage():
    db = MagicMock()
    exam = _make_exam(11, supervisions=[MagicMock()], invigilators_needed=3, title="Midterm")
    db.query.return_value.options.return_value.filter.return_value.order_by.return_value.all.return_value = [exam]
    issues = build_external_workflow_issues(db, 1)
    assert len(issues) == 1
    assert issues[0]["type"] == "external_staff_shortage"
    assert issues[0]["severity"] == "warning"
    assert issues[0]["id"] == "external-short-11"


def test_build_issues_fully_staffed_no_issue():
    db = MagicMock()
    exam = _make_exam(12, supervisions=[MagicMock(), MagicMock()], invigilators_needed=2)
    db.query.return_value.options.return_value.filter.return_value.order_by.return_value.all.return_value = [exam]
    assert build_external_workflow_issues(db, 1) == []


def test_build_issues_zero_invigilators_needed_no_issue():
    db = MagicMock()
    exam = _make_exam(13, supervisions=[], invigilators_needed=0)
    db.query.return_value.options.return_value.filter.return_value.order_by.return_value.all.return_value = [exam]
    assert build_external_workflow_issues(db, 1) == []


def test_build_issues_title_fallback():
    db = MagicMock()
    exam = _make_exam(14, supervisions=[], invigilators_needed=1, title=None)
    db.query.return_value.options.return_value.filter.return_value.order_by.return_value.all.return_value = [exam]
    issues = build_external_workflow_issues(db, 1)
    assert "External exam #14" in issues[0]["reference"]


# ── build_staff_workload_report ───────────────────────────────────────────────

def test_build_staff_workload_report_includes_period_key():
    db = MagicMock()
    period = _make_period(5, label="Final 2026/2")
    with patch("services.workflow_reporting_service.get_period_workload_snapshot", return_value={"staff": []}):
        result = build_staff_workload_report(db, period, "admin")
    assert "period" in result
    assert result["period"]["id"] == 5
    assert result["period"]["label"] == "Final 2026/2"


def test_build_staff_workload_report_includes_viewer_role():
    db = MagicMock()
    period = _make_period()
    with patch("services.workflow_reporting_service.get_period_workload_snapshot", return_value={}):
        result = build_staff_workload_report(db, period, "staff")
    assert result["viewer_role"] == "staff"


def test_build_staff_workload_report_none_viewer_role():
    db = MagicMock()
    period = _make_period()
    with patch("services.workflow_reporting_service.get_period_workload_snapshot", return_value={}):
        result = build_staff_workload_report(db, period, None)
    assert result["viewer_role"] is None


def test_build_staff_workload_report_preserves_snapshot_data():
    db = MagicMock()
    period = _make_period()
    snapshot_data = {"staff": [{"id": 1}], "total_assignments": 10}
    with patch("services.workflow_reporting_service.get_period_workload_snapshot", return_value=snapshot_data):
        result = build_staff_workload_report(db, period, "admin")
    assert result["staff"] == [{"id": 1}]
    assert result["total_assignments"] == 10
