"""Tests for optimization_trace_service and optimization_trace_policy."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime

from policies.optimization_trace_policy import (
    TraceEventType,
    TraceSource,
    TraceSeverity,
    is_safe_metadata,
    strip_pii,
)
from services.optimization_trace_service import (
    build_trace_event,
    trace_from_explanation_factors,
    trace_from_observer_payload,
    trace_from_recheck_issues,
    trace_governance_decision,
)


# ── strip_pii ──────────────────────────────────────────────────────────────

def test_strip_pii_removes_student_id():
    result = strip_pii({"room_id": 5, "student_id": "630110123"})
    assert "student_id" not in result
    assert "room_id" in result


def test_strip_pii_removes_all_blocked_keys():
    blocked = {
        "student_id": "x",
        "student_ids": ["x"],
        "student_name": "Alice",
        "student_names": ["Alice"],
        "teacher_name": "Bob",
        "email": "a@b.com",
        "mobile": "0812345678",
    }
    result = strip_pii(blocked)
    assert result == {}


def test_strip_pii_preserves_safe_keys():
    data = {"room_id": 10, "course_id": "POL101", "split_count": 1}
    assert strip_pii(data) == data


def test_strip_pii_empty_input():
    assert strip_pii({}) == {}


def test_is_safe_metadata_true_when_no_pii():
    assert is_safe_metadata({"room_id": 1}) is True


def test_is_safe_metadata_false_when_pii_present():
    assert is_safe_metadata({"student_id": "abc"}) is False


# ── build_trace_event ──────────────────────────────────────────────────────

def test_build_trace_event_basic_shape():
    evt = build_trace_event(TraceEventType.OPTIMIZATION_STARTED)
    assert evt["event_type"] == TraceEventType.OPTIMIZATION_STARTED
    assert "timestamp" in evt
    assert "metadata" in evt
    assert "severity" in evt
    assert "source" in evt


def test_build_trace_event_strips_pii_from_metadata():
    evt = build_trace_event(
        TraceEventType.ROOM_SELECTED,
        metadata={"room_id": 5, "student_id": "630110123"},
    )
    assert "student_id" not in evt["metadata"]
    assert evt["metadata"]["room_id"] == 5


def test_build_trace_event_timestamp_is_valid_iso():
    evt = build_trace_event(TraceEventType.STAFF_SELECTED)
    datetime.fromisoformat(evt["timestamp"])


def test_build_trace_event_defaults():
    evt = build_trace_event(TraceEventType.FALLBACK_USED)
    assert evt["source"] == TraceSource.POST_HOC_TRACE
    assert evt["severity"] == TraceSeverity.INFO
    assert evt["entity_type"] is None
    assert evt["entity_id"] is None
    assert evt["constraint_code"] is None
    assert evt["score_delta"] is None


def test_build_trace_event_all_fields():
    evt = build_trace_event(
        TraceEventType.CONSTRAINT_APPLIED,
        entity_type="schedule_entry",
        entity_id=42,
        constraint_code="ROOM_CAPACITY",
        reason_code="OVER_CAPACITY",
        score_delta=-5.0,
        severity=TraceSeverity.WARNING,
        source=TraceSource.POLICY_RULE,
        metadata={"room_id": 10},
    )
    assert evt["entity_type"] == "schedule_entry"
    assert evt["entity_id"] == 42
    assert evt["constraint_code"] == "ROOM_CAPACITY"
    assert evt["score_delta"] == -5.0
    assert evt["severity"] == TraceSeverity.WARNING
    assert evt["source"] == TraceSource.POLICY_RULE


# ── trace_from_recheck_issues ───────────────────────────────────────────────

def _make_issue(**kw):
    base = {
        "severity": "WARNING",
        "category": "ROOM",
        "code": "LOW_UTILIZATION",
        "message": "Room underutilized",
        "course_id": "POL101",
        "section": "01",
        "exam_date": "2026-10-01",
        "room_id": 5,
        "blocking": False,
        "can_override": True,
        "source": "recheck_engine",
    }
    base.update(kw)
    return base


def test_trace_from_recheck_issues_wraps_started_and_completed():
    events = trace_from_recheck_issues([_make_issue()])
    types = [e["event_type"] for e in events]
    assert TraceEventType.RECHECK_STARTED in types
    assert TraceEventType.RECHECK_COMPLETED in types


def test_trace_from_recheck_issues_issue_count_in_completed():
    events = trace_from_recheck_issues([_make_issue(), _make_issue()])
    completed = next(e for e in events if e["event_type"] == TraceEventType.RECHECK_COMPLETED)
    assert completed["metadata"]["total_issues"] == 2


def test_trace_from_recheck_issues_no_pii_in_metadata():
    issue = _make_issue()
    issue["metadata"] = {"student_id": "x", "room_id": 5}
    events = trace_from_recheck_issues([issue])
    for evt in events:
        assert "student_id" not in evt.get("metadata", {})


def test_trace_from_recheck_issues_hard_fail_becomes_high_risk():
    events = trace_from_recheck_issues([_make_issue(severity="HARD_FAIL", blocking=True)])
    constraint_events = [e for e in events if e["event_type"] == TraceEventType.CONSTRAINT_APPLIED]
    assert any(e["severity"] == TraceSeverity.HIGH_RISK for e in constraint_events)


def test_trace_from_recheck_issues_empty():
    events = trace_from_recheck_issues([])
    assert any(e["event_type"] == TraceEventType.RECHECK_STARTED for e in events)
    assert any(e["event_type"] == TraceEventType.RECHECK_COMPLETED for e in events)


# ── trace_from_observer_payload ─────────────────────────────────────────────

def _make_observer_payload():
    return {
        "period_id": 1,
        "summary": {"checked_schedule_count": 10},
        "quality_report": {"overall_score": 88, "quality_band": "GOOD"},
        "schedule_entries": [
            {
                "section_id": 101,
                "course_id": "POL101",
                "exam_date": "2026-10-01",
                "exam_time": "09:00",
                "room": {"id": 5, "capacity": 30},
                "staff_load": 2,
                "split_count": 1,
            },
        ],
    }


def test_trace_from_observer_payload_starts_with_optimization_started():
    events = trace_from_observer_payload(_make_observer_payload())
    assert events[0]["event_type"] == TraceEventType.OPTIMIZATION_STARTED


def test_trace_from_observer_payload_entry_produces_final_selection():
    events = trace_from_observer_payload(_make_observer_payload())
    types = [e["event_type"] for e in events]
    assert TraceEventType.FINAL_SELECTION_ACCEPTED in types


def test_trace_from_observer_payload_no_pii():
    payload = _make_observer_payload()
    payload["schedule_entries"][0]["student_ids"] = ["630110001"]
    events = trace_from_observer_payload(payload)
    for evt in events:
        assert "student_ids" not in evt.get("metadata", {})


def test_trace_from_observer_payload_empty_entries():
    payload = _make_observer_payload()
    payload["schedule_entries"] = []
    events = trace_from_observer_payload(payload)
    assert events[0]["event_type"] == TraceEventType.OPTIMIZATION_STARTED
    assert len(events) == 1


# ── trace_from_explanation_factors ─────────────────────────────────────────

def _make_factor(category="ROOM_SELECTION", source="POST_HOC_HEURISTIC"):
    return {
        "category": category,
        "explanation_type": "CAPACITY_FIT",
        "source": source,
        "summary": "Room fits all students",
    }


def test_trace_from_explanation_factors_room_selection():
    entries = [{"section_id": 5, "factors": [_make_factor("ROOM_SELECTION")]}]
    events = trace_from_explanation_factors(entries)
    assert any(e["event_type"] == TraceEventType.ROOM_SELECTED for e in events)


def test_trace_from_explanation_factors_staff_assignment():
    entries = [{"section_id": 5, "factors": [_make_factor("STAFF_ASSIGNMENT")]}]
    events = trace_from_explanation_factors(entries)
    assert any(e["event_type"] == TraceEventType.STAFF_SELECTED for e in events)


def test_trace_from_explanation_factors_empty():
    assert trace_from_explanation_factors([]) == []


def test_trace_from_explanation_factors_no_pii():
    factor = _make_factor()
    entries = [{"section_id": 5, "factors": [factor], "student_name": "Alice"}]
    events = trace_from_explanation_factors(entries)
    for evt in events:
        assert "student_name" not in evt.get("metadata", {})


# ── trace_governance_decision ──────────────────────────────────────────────

def _make_governance(state="AUTO_APPROVED"):
    return {
        "governance_state": state,
        "review_priority": "LOW",
        "quality_snapshot": {"overall_score": 88, "quality_band": "GOOD", "risk_level": "LOW"},
    }


def test_trace_governance_decision_event_type():
    evt = trace_governance_decision(_make_governance())
    assert evt["event_type"] == TraceEventType.GOVERNANCE_DECISION_CREATED


def test_trace_governance_decision_blocked_is_high_risk():
    evt = trace_governance_decision(_make_governance("BLOCKED"))
    assert evt["severity"] == TraceSeverity.HIGH_RISK


def test_trace_governance_decision_auto_approved_is_info():
    evt = trace_governance_decision(_make_governance("AUTO_APPROVED"))
    assert evt["severity"] == TraceSeverity.INFO


def test_trace_governance_decision_source_is_policy_rule():
    evt = trace_governance_decision(_make_governance())
    assert evt["source"] == TraceSource.POLICY_RULE


def test_trace_governance_decision_state_in_metadata():
    evt = trace_governance_decision(_make_governance("ESCALATION_REQUIRED"))
    assert evt["metadata"]["governance_state"] == "ESCALATION_REQUIRED"
