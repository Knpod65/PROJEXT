"""Tests for optimization_constraint_trace_service."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_constraint_trace_service import (
    ConstraintTrace,
    build_constraint_summary,
    build_constraint_traces,
    constraint_traces_to_dicts,
)


# ── Test helpers ──────────────────────────────────────────────────────────

def _issue(code="ROOM_CAPACITY", severity="WARNING", message="Room near capacity",
           blocking=False, **kw):
    return {"code": code, "severity": severity, "message": message, "blocking": blocking, **kw}


# ── Empty / None safety ───────────────────────────────────────────────────

def test_empty_issues_returns_empty_list():
    assert build_constraint_traces([]) == []


def test_non_dict_issues_skipped():
    traces = build_constraint_traces(["invalid", None, 42])
    assert traces == []


# ── One trace per issue ───────────────────────────────────────────────────

def test_one_trace_per_issue():
    issues = [_issue("A"), _issue("B"), _issue("C")]
    traces = build_constraint_traces(issues)
    assert len(traces) == 3


# ── HARD_FAIL mapping ─────────────────────────────────────────────────────

def test_hard_fail_severity_normalized():
    traces = build_constraint_traces([_issue(severity="HARD_FAIL")])
    assert traces[0].severity == "HARD_FAIL"


def test_hard_fail_lowercase_normalized():
    traces = build_constraint_traces([_issue(severity="hard_fail")])
    assert traces[0].severity == "HARD_FAIL"


def test_error_normalized_to_hard_fail():
    traces = build_constraint_traces([_issue(severity="ERROR")])
    assert traces[0].severity == "HARD_FAIL"


def test_hard_fail_is_blocking():
    traces = build_constraint_traces([_issue(severity="HARD_FAIL", blocking=False)])
    # HARD_FAIL is always blocking regardless of the issue's blocking flag
    assert traces[0].blocking is True


# ── WARNING mapping ───────────────────────────────────────────────────────

def test_warning_severity_normalized():
    traces = build_constraint_traces([_issue(severity="WARNING")])
    assert traces[0].severity == "WARNING"


def test_warning_lowercase_normalized():
    traces = build_constraint_traces([_issue(severity="warning")])
    assert traces[0].severity == "WARNING"


def test_warning_not_blocking_by_default():
    traces = build_constraint_traces([_issue(severity="WARNING", blocking=False)])
    assert traces[0].blocking is False


def test_warning_with_explicit_blocking_flag():
    traces = build_constraint_traces([_issue(severity="WARNING", blocking=True)])
    assert traces[0].blocking is True


# ── INFO + SUGGESTION mapping ─────────────────────────────────────────────

def test_info_severity_mapped():
    traces = build_constraint_traces([_issue(severity="INFO")])
    assert traces[0].severity == "INFO"


def test_suggestion_severity_mapped():
    traces = build_constraint_traces([_issue(severity="SUGGESTION")])
    assert traces[0].severity == "SUGGESTION"


# ── All issues are triggered=True ─────────────────────────────────────────

def test_all_traces_are_triggered():
    issues = [_issue(severity="WARNING"), _issue(severity="INFO")]
    traces = build_constraint_traces(issues)
    assert all(t.triggered for t in traces)


# ── Constraint name ───────────────────────────────────────────────────────

def test_constraint_name_from_code():
    traces = build_constraint_traces([_issue(code="INVIGILATOR_CONFLICT")])
    assert traces[0].constraint_name == "INVIGILATOR_CONFLICT"


def test_missing_code_defaults_to_unknown():
    traces = build_constraint_traces([{"severity": "INFO", "message": "test"}])
    assert traces[0].constraint_name == "UNKNOWN_CONSTRAINT"


# ── Required fields ───────────────────────────────────────────────────────

def test_trace_has_required_fields():
    traces = build_constraint_traces([_issue()])
    t = traces[0]
    assert t.trace_id
    assert t.timestamp
    assert t.domain == "optimization"
    assert t.optimization_stage
    assert isinstance(t.audit_metadata, dict)


def test_trace_is_immutable():
    traces = build_constraint_traces([_issue()])
    t = traces[0]
    try:
        t.severity = "MUTATED"  # type: ignore[misc]
        assert False, "Should have raised FrozenInstanceError"
    except Exception:
        pass


def test_category_captured():
    traces = build_constraint_traces([_issue(category="ROOM_CONSTRAINT")])
    assert traces[0].category == "ROOM_CONSTRAINT"


def test_section_id_in_audit_metadata():
    traces = build_constraint_traces([_issue(section_id=42)])
    assert traces[0].audit_metadata.get("section_id") == 42


# ── build_constraint_summary ──────────────────────────────────────────────

def test_summary_empty_issues():
    summary = build_constraint_summary([])
    assert summary["total_constraints_triggered"] == 0
    assert summary["all_pass"] is True


def test_summary_hard_fail_count():
    traces = build_constraint_traces([_issue(severity="HARD_FAIL"), _issue(severity="WARNING")])
    summary = build_constraint_summary(traces)
    assert summary["hard_fail_count"] == 1
    assert summary["warning_count"] == 1


def test_summary_blocking_count():
    issues = [
        _issue(severity="HARD_FAIL", blocking=False),  # blocking via severity
        _issue(severity="WARNING", blocking=True),
        _issue(severity="INFO", blocking=False),
    ]
    traces = build_constraint_traces(issues)
    summary = build_constraint_summary(traces)
    assert summary["blocking_count"] == 2


# ── Serialization ─────────────────────────────────────────────────────────

def test_to_dicts_returns_list_of_dicts():
    traces = build_constraint_traces([_issue()])
    result = constraint_traces_to_dicts(traces)
    assert isinstance(result, list)
    assert isinstance(result[0], dict)


def test_to_dicts_round_trip_trace_id():
    traces = build_constraint_traces([_issue()])
    result = constraint_traces_to_dicts(traces)
    assert result[0]["trace_id"] == traces[0].trace_id
