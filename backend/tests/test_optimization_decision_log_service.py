"""Tests for optimization_decision_log_service."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_decision_log_service import (
    DecisionLogEntry,
    build_decision_log,
    decision_log_to_dicts,
)


# ── Test helpers ──────────────────────────────────────────────────────────

def _observer(schedules=None, governance_state="AUTO_APPROVED", **kw):
    return {
        "schedules": schedules or [],
        "governance": {"governance_state": governance_state},
        "explanation_summary": {},
        "status": "OK",
        **kw,
    }


def _schedule_entry(**kw):
    base = {
        "section_id": 1,
        "course_id": "POL101",
        "room": {"id": 10, "capacity": 30},
        "assigned_staff": [101, 102],
        "exam_date": "2026-10-01",
        "exam_time": "09:00",
        "split_count": 1,
        "paper_distributor": "dist-A",
        "num_students": 25,
        "avoided_conflicts": [],
        "split_reason": None,
        "course_preferred_building": None,
    }
    base.update(kw)
    return base


# ── Empty / none safety ───────────────────────────────────────────────────

def test_empty_observer_returns_empty_list():
    result = build_decision_log(_observer(schedules=[]))
    assert result == []


def test_missing_schedules_key_returns_empty():
    result = build_decision_log({})
    assert result == []


# ── Entry shape ───────────────────────────────────────────────────────────

def test_one_entry_per_schedule():
    entries = build_decision_log(_observer(schedules=[_schedule_entry(), _schedule_entry(section_id=2)]))
    assert len(entries) == 2


def test_entry_captures_section_id():
    entries = build_decision_log(_observer(schedules=[_schedule_entry(section_id=42)]))
    assert entries[0].section_id == 42


def test_entry_captures_course_id():
    entries = build_decision_log(_observer(schedules=[_schedule_entry(course_id="POL999")]))
    assert entries[0].course_id == "POL999"


def test_entry_captures_room_id():
    entries = build_decision_log(_observer(schedules=[_schedule_entry(room={"id": 77, "capacity": 40})]))
    assert entries[0].chosen_room_id == 77


def test_entry_captures_room_capacity():
    entries = build_decision_log(_observer(schedules=[_schedule_entry(room={"id": 5, "capacity": 50})]))
    assert entries[0].chosen_room_capacity == 50


def test_entry_captures_staff_ids():
    entries = build_decision_log(_observer(schedules=[_schedule_entry(assigned_staff=[101, 202])]))
    assert set(entries[0].chosen_staff_ids) == {101, 202}


def test_entry_filters_none_staff():
    entries = build_decision_log(_observer(schedules=[_schedule_entry(assigned_staff=[None, 101])]))
    assert None not in entries[0].chosen_staff_ids
    assert 101 in entries[0].chosen_staff_ids


def test_entry_captures_exam_date():
    entries = build_decision_log(_observer(schedules=[_schedule_entry(exam_date="2026-11-01")]))
    assert entries[0].exam_date == "2026-11-01"


def test_entry_captures_split_count():
    entries = build_decision_log(_observer(schedules=[_schedule_entry(split_count=3)]))
    assert entries[0].split_count == 3


# ── Decision factors ──────────────────────────────────────────────────────

def test_decision_factors_non_empty():
    entries = build_decision_log(_observer(schedules=[_schedule_entry()]))
    assert len(entries[0].decision_factors) > 0


def test_split_decision_factor_when_split():
    entry = _schedule_entry(split_count=2)
    entries = build_decision_log(_observer(schedules=[entry]))
    assert "SPLIT_DECISION" in entries[0].decision_factors


def test_conflict_avoidance_factor_when_conflicts():
    entry = _schedule_entry(avoided_conflicts=["conflict_1"])
    entries = build_decision_log(_observer(schedules=[entry]))
    assert "CONFLICT_AVOIDANCE" in entries[0].decision_factors


# ── Governance relevance ──────────────────────────────────────────────────

def test_governance_relevance_auto_approved():
    entries = build_decision_log(_observer(schedules=[_schedule_entry()], governance_state="AUTO_APPROVED"))
    assert entries[0].governance_relevance == "NONE"


def test_governance_relevance_blocked():
    entries = build_decision_log(_observer(schedules=[_schedule_entry()], governance_state="BLOCKED"))
    assert entries[0].governance_relevance == "BLOCKED"


def test_governance_relevance_approval_required():
    entries = build_decision_log(_observer(schedules=[_schedule_entry()], governance_state="APPROVAL_REQUIRED"))
    assert entries[0].governance_relevance == "REVIEW_REQUIRED"


# ── Required keys ─────────────────────────────────────────────────────────

def test_entry_has_required_fields():
    entries = build_decision_log(_observer(schedules=[_schedule_entry()]))
    e = entries[0]
    assert e.log_id
    assert e.timestamp
    assert e.confidence in ("HIGH", "MEDIUM", "LOW", "UNKNOWN")
    assert e.policy_source
    assert isinstance(e.audit_metadata, dict)


def test_entry_is_immutable():
    entries = build_decision_log(_observer(schedules=[_schedule_entry()]))
    e = entries[0]
    try:
        e.section_id = 999  # type: ignore[misc]
        assert False, "Should have raised FrozenInstanceError"
    except Exception:
        pass


# ── Serialization ─────────────────────────────────────────────────────────

def test_to_dicts_returns_list_of_dicts():
    entries = build_decision_log(_observer(schedules=[_schedule_entry()]))
    result = decision_log_to_dicts(entries)
    assert isinstance(result, list)
    assert isinstance(result[0], dict)


def test_to_dicts_staff_ids_are_list():
    entries = build_decision_log(_observer(schedules=[_schedule_entry(assigned_staff=[101, 102])]))
    result = decision_log_to_dicts(entries)
    assert isinstance(result[0]["chosen_staff_ids"], list)


def test_to_dicts_decision_factors_are_list():
    entries = build_decision_log(_observer(schedules=[_schedule_entry()]))
    result = decision_log_to_dicts(entries)
    assert isinstance(result[0]["decision_factors"], list)
