"""Tests for optimizer_trace_aggregator_service.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimizer_trace_aggregator_service import aggregate_optimization_traces


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _entry(**overrides):
    base = {
        "section_id": 101,
        "course_id": "POL101",
        "exam_date": "2026-10-01",
        "exam_time": "09:00",
        "room": {"id": 5, "capacity": 30},
        "staff_ids": [10, 11],
        "staff_load": 2,
        "split_count": 1,
        "rejected_room_candidates": [],
        "rejected_staff_candidates": [],
    }
    base.update(overrides)
    return base


def _payload(entries=None):
    return {
        "period_id": 1,
        "summary": {"checked_schedule_count": 5},
        "quality_report": {"overall_score": 88, "quality_band": "GOOD"},
        "schedule_entries": entries if entries is not None else [_entry()],
    }


def _issue(severity="WARNING", code="STAFF_OVERLOAD", blocking=False):
    return {"severity": severity, "code": code, "message": "Test issue.", "blocking": blocking}


# ── All keys present ──────────────────────────────────────────────────────────

def test_all_keys_present():
    result = aggregate_optimization_traces(
        observer_payload=_payload(),
        recheck_issues=[],
    )
    for key in (
        "candidate_traces", "constraint_traces", "decision_log",
        "trace_events", "constraint_summary", "rejection_breakdown",
    ):
        assert key in result, f"Missing key: {key}"


def test_constraint_summary_keys():
    result = aggregate_optimization_traces(
        observer_payload=_payload(),
        recheck_issues=[_issue()],
    )
    cs = result["constraint_summary"]
    for key in ("total_constraints_triggered", "hard_fail_count", "warning_count", "blocking_count", "all_pass"):
        assert key in cs, f"Missing constraint_summary key: {key}"


def test_rejection_breakdown_keys():
    result = aggregate_optimization_traces(
        observer_payload=_payload(),
        recheck_issues=[],
    )
    rb = result["rejection_breakdown"]
    for key in ("room_rejections", "staff_rejections", "timeslot_rejections", "total_rejections"):
        assert key in rb, f"Missing rejection_breakdown key: {key}"


# ── Empty inputs ──────────────────────────────────────────────────────────────

def test_empty_entries_and_issues():
    result = aggregate_optimization_traces(
        observer_payload=_payload(entries=[]),
        recheck_issues=[],
    )
    assert result["candidate_traces"] == []
    assert result["constraint_traces"] == []
    assert result["rejection_breakdown"]["total_rejections"] == 0
    assert result["constraint_summary"]["all_pass"] is True


def test_empty_payload_does_not_raise():
    result = aggregate_optimization_traces(
        observer_payload={},
        recheck_issues=[],
    )
    assert isinstance(result["candidate_traces"], list)
    assert isinstance(result["trace_events"], list)


# ── Constraint traces passthrough ─────────────────────────────────────────────

def test_constraint_traces_produced_from_issues():
    result = aggregate_optimization_traces(
        observer_payload=_payload(),
        recheck_issues=[_issue("HARD_FAIL", "ROOM_CONFLICT"), _issue("WARNING", "STAFF_OVERLOAD")],
    )
    assert len(result["constraint_traces"]) == 2


def test_constraint_summary_counts_hard_fails():
    result = aggregate_optimization_traces(
        observer_payload=_payload(),
        recheck_issues=[_issue("HARD_FAIL"), _issue("HARD_FAIL"), _issue("WARNING")],
    )
    cs = result["constraint_summary"]
    assert cs["hard_fail_count"] == 2
    assert cs["warning_count"] == 1
    assert cs["all_pass"] is False


# ── Rejection breakdown ───────────────────────────────────────────────────────

def test_rejection_breakdown_counts_room_rejections():
    entry = _entry(
        rejected_room_candidates=[
            {"room_id": 99, "reason": "CAPACITY_INSUFFICIENT", "severity": "WARNING"},
            {"room_id": 88, "reason": "UNAVAILABLE", "severity": "WARNING"},
        ]
    )
    result = aggregate_optimization_traces(
        observer_payload=_payload(entries=[entry]),
        recheck_issues=[],
    )
    rb = result["rejection_breakdown"]
    assert rb["room_rejections"] == 2
    assert rb["staff_rejections"] == 0
    assert rb["total_rejections"] == 2


def test_rejection_breakdown_counts_staff_rejections():
    entry = _entry(
        rejected_staff_candidates=[
            {"staff_id": 999, "reason": "UNAVAILABLE", "severity": "WARNING"},
        ]
    )
    result = aggregate_optimization_traces(
        observer_payload=_payload(entries=[entry]),
        recheck_issues=[],
    )
    rb = result["rejection_breakdown"]
    assert rb["staff_rejections"] == 1
    assert rb["room_rejections"] == 0


# ── Trace events ──────────────────────────────────────────────────────────────

def test_trace_events_include_optimization_started():
    result = aggregate_optimization_traces(
        observer_payload=_payload(),
        recheck_issues=[],
    )
    event_types = [e["event_type"] for e in result["trace_events"]]
    assert "OPTIMIZATION_STARTED" in event_types


def test_trace_events_include_recheck_events_when_issues_present():
    result = aggregate_optimization_traces(
        observer_payload=_payload(),
        recheck_issues=[_issue()],
    )
    assert len(result["trace_events"]) > 1


# ── Session ID passthrough ────────────────────────────────────────────────────

def test_session_id_passed_to_trace_events():
    result = aggregate_optimization_traces(
        observer_payload=_payload(),
        recheck_issues=[],
        session_id="sess-42",
    )
    started = next(e for e in result["trace_events"] if e["event_type"] == "OPTIMIZATION_STARTED")
    assert started["metadata"]["session_id"] == "sess-42"
