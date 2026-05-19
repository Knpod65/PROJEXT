"""Tests for D3.8 — config validation service."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config_models.academic_group_config import make_academic_group_config
from config_models.faculty_config import make_faculty_config
from config_models.governance_flow import make_governance_flow_config
from config_models.workload_policy import make_workload_policy
from services.config_validation_service import (
    ConfigValidationReport,
    ValidationResult,
    ValidationSeverity,
    has_hard_failures,
    summarize_validation,
    validate_academic_group_config,
    validate_faculty_config,
    validate_governance_flow,
    validate_workload_policy,
)


# ── validate_faculty_config ───────────────────────────────────────────────────

def test_valid_faculty_config_produces_valid_report():
    cfg = make_faculty_config(1, "POL", "คณะรัฐศาสตร์", "Political Science",
                              email_domain="polsci.cmu.ac.th", metadata={"k": "v"})
    report = validate_faculty_config(cfg)
    assert report.valid is True
    assert report.config_type == "FacultyConfig"


def test_faculty_config_hard_fail_on_faculty_id_zero():
    cfg = make_faculty_config(0, "POL", "A", "B", email_domain="x.com")
    report = validate_faculty_config(cfg)
    assert report.valid is False
    codes = [r.code for r in report.results]
    assert "INVALID_FACULTY_ID" in codes


def test_faculty_config_hard_fail_on_empty_code():
    cfg = make_faculty_config(1, "   ", "A", "B", email_domain="x.com")
    report = validate_faculty_config(cfg)
    codes = [r.code for r in report.results]
    assert "MISSING_FACULTY_CODE" in codes


def test_faculty_config_hard_fail_on_empty_name_th():
    cfg = make_faculty_config(1, "POL", "", "B", email_domain="x.com")
    report = validate_faculty_config(cfg)
    codes = [r.code for r in report.results]
    assert "MISSING_FACULTY_NAME_TH" in codes


def test_faculty_config_hard_fail_on_empty_name_en():
    cfg = make_faculty_config(1, "POL", "A", "", email_domain="x.com")
    report = validate_faculty_config(cfg)
    codes = [r.code for r in report.results]
    assert "MISSING_FACULTY_NAME_EN" in codes


def test_faculty_config_warning_on_empty_email_domain():
    cfg = make_faculty_config(1, "POL", "A", "B", email_domain="")
    report = validate_faculty_config(cfg)
    severities = [r.severity for r in report.results]
    assert ValidationSeverity.WARNING in severities


def test_faculty_config_info_on_empty_metadata():
    cfg = make_faculty_config(1, "POL", "A", "B", email_domain="x.com")
    report = validate_faculty_config(cfg)
    codes = [r.code for r in report.results]
    assert "EMPTY_METADATA" in codes


def test_validated_at_is_utc_iso():
    cfg = make_faculty_config(1, "POL", "A", "B", email_domain="x.com")
    report = validate_faculty_config(cfg)
    assert "T" in report.validated_at


# ── validate_workload_policy ──────────────────────────────────────────────────

def test_workload_policy_hard_fail_on_negative_sessions():
    policy = make_workload_policy(max_supervision_sessions=-1)
    report = validate_workload_policy(policy)
    assert report.valid is False
    codes = [r.code for r in report.results]
    assert "NEGATIVE_SUPERVISION_SESSIONS" in codes


def test_workload_policy_warning_on_empty_excluded_usernames():
    policy = make_workload_policy(excluded_usernames=frozenset())
    report = validate_workload_policy(policy)
    severities = [r.severity for r in report.results]
    assert ValidationSeverity.WARNING in severities


def test_workload_policy_info_on_cross_department():
    policy = make_workload_policy(allow_cross_department=True, excluded_usernames=frozenset({"x"}))
    report = validate_workload_policy(policy)
    codes = [r.code for r in report.results]
    assert "CROSS_DEPARTMENT_ENABLED" in codes


# ── validate_governance_flow ──────────────────────────────────────────────────

def test_governance_flow_hard_fail_on_no_signers():
    flow = make_governance_flow_config("test", [], [])
    report = validate_governance_flow(flow)
    assert report.valid is False
    codes = [r.code for r in report.results]
    assert "NO_ROUND1_SIGNERS" in codes


def test_governance_flow_hard_fail_when_quorum_exceeds_slots():
    flow = make_governance_flow_config(
        "test",
        [{"position": 1, "role": "admin", "username_hint": None, "required": True}],
        [],
        approval_quorum=5,
    )
    report = validate_governance_flow(flow)
    assert report.valid is False
    codes = [r.code for r in report.results]
    assert "QUORUM_EXCEEDS_SLOTS" in codes


def test_governance_flow_warning_on_empty_round2():
    flow = make_governance_flow_config(
        "test",
        [{"position": 1, "role": "admin", "username_hint": None, "required": True}],
        [],
    )
    report = validate_governance_flow(flow)
    codes = [r.code for r in report.results]
    assert "EMPTY_ROUND2_SIGNERS" in codes


# ── validate_academic_group_config ────────────────────────────────────────────

def test_academic_group_hard_fail_on_empty_course_prefixes():
    grp = make_academic_group_config(1, "IA", "A", "B", ())
    report = validate_academic_group_config(grp)
    assert report.valid is False
    codes = [r.code for r in report.results]
    assert "EMPTY_COURSE_PREFIXES" in codes


def test_academic_group_warning_on_empty_label_th():
    grp = make_academic_group_config(1, "IA", "", "English", ("126",))
    report = validate_academic_group_config(grp)
    severities = [r.severity for r in report.results]
    assert ValidationSeverity.WARNING in severities


# ── has_hard_failures / summarize_validation ─────────────────────────────────

def test_has_hard_failures_true_for_invalid():
    cfg = make_faculty_config(0, "", "", "")
    report = validate_faculty_config(cfg)
    assert has_hard_failures([report]) is True


def test_has_hard_failures_false_for_valid():
    cfg = make_faculty_config(1, "POL", "A", "B", email_domain="x.com")
    report = validate_faculty_config(cfg)
    assert has_hard_failures([report]) is False


def test_summarize_validation_counts_severities():
    cfg = make_faculty_config(0, "", "", "")
    report = validate_faculty_config(cfg)
    summary = summarize_validation([report])
    assert summary["hard_fail_count"] >= 3  # id, code, name_th, name_en
    assert "warning_count" in summary
    assert summary["all_valid"] is False


def test_all_validation_result_fields_present():
    cfg = make_faculty_config(0, "X", "A", "B")
    report = validate_faculty_config(cfg)
    result = next(r for r in report.results if r.severity == ValidationSeverity.HARD_FAIL)
    assert result.code
    assert result.message
    assert isinstance(result.context, dict)
