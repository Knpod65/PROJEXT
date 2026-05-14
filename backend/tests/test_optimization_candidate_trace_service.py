"""Tests for optimization_candidate_trace_service."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_candidate_trace_service import (
    CandidateTrace,
    build_candidate_traces,
    candidate_traces_to_dicts,
)


# ── Test helpers ──────────────────────────────────────────────────────────

def _entry(**kw):
    base = {
        "section_id": 1,
        "course_id": "POL101",
        "room": {"id": 10, "capacity": 30},
        "assigned_staff": [101, 102],
        "exam_date": "2026-10-01",
        "rejected_room_candidates": [],
        "rejected_staff_candidates": [],
        "split_count": 1,
    }
    base.update(kw)
    return base


def _rejected_room(room_id=99, reason="CAPACITY_INSUFFICIENT", severity="WARNING"):
    return {"room_id": room_id, "reason": reason, "severity": severity}


def _rejected_staff(staff_id=999, reason="UNAVAILABLE", severity="WARNING"):
    return {"staff_id": staff_id, "reason": reason, "severity": severity}


# ── Empty / None safety ───────────────────────────────────────────────────

def test_empty_schedule_returns_empty_list():
    assert build_candidate_traces([]) == []


def test_no_rejections_returns_accepted_traces_only():
    traces = build_candidate_traces([_entry()])
    assert len(traces) > 0
    decisions = {t.decision for t in traces}
    assert decisions == {"ACCEPTED"}


# ── Accepted traces ───────────────────────────────────────────────────────

def test_accepted_room_trace_created():
    traces = build_candidate_traces([_entry()])
    room_traces = [t for t in traces if t.candidate_type == "ROOM" and t.decision == "ACCEPTED"]
    assert len(room_traces) == 1
    assert room_traces[0].candidate_id == 10


def test_accepted_staff_traces_created():
    traces = build_candidate_traces([_entry(assigned_staff=[101, 102])])
    staff_traces = [t for t in traces if t.candidate_type == "STAFF" and t.decision == "ACCEPTED"]
    assert len(staff_traces) == 2
    ids = {t.candidate_id for t in staff_traces}
    assert ids == {101, 102}


def test_no_accepted_room_if_room_missing():
    traces = build_candidate_traces([_entry(room={})])
    room_accepted = [t for t in traces if t.candidate_type == "ROOM" and t.decision == "ACCEPTED"]
    assert room_accepted == []


def test_none_staff_skipped():
    traces = build_candidate_traces([_entry(assigned_staff=[None, 101])])
    staff_ids = [t.candidate_id for t in traces if t.candidate_type == "STAFF" and t.decision == "ACCEPTED"]
    assert None not in staff_ids
    assert 101 in staff_ids


# ── Rejected room candidates ──────────────────────────────────────────────

def test_rejected_room_candidate_parsed():
    entry = _entry(rejected_room_candidates=[_rejected_room(room_id=55)])
    traces = build_candidate_traces([entry])
    rejected = [t for t in traces if t.candidate_type == "ROOM" and t.decision == "REJECTED"]
    assert len(rejected) == 1
    assert rejected[0].candidate_id == 55


def test_rejected_room_reason_captured():
    entry = _entry(rejected_room_candidates=[_rejected_room(reason="CAPACITY_INSUFFICIENT")])
    traces = build_candidate_traces([entry])
    rejected = [t for t in traces if t.decision == "REJECTED" and t.candidate_type == "ROOM"]
    assert rejected[0].reason == "CAPACITY_INSUFFICIENT"


def test_multiple_rejected_rooms():
    entry = _entry(rejected_room_candidates=[
        _rejected_room(room_id=1),
        _rejected_room(room_id=2),
        _rejected_room(room_id=3),
    ])
    traces = build_candidate_traces([entry])
    rejected_rooms = [t for t in traces if t.candidate_type == "ROOM" and t.decision == "REJECTED"]
    assert len(rejected_rooms) == 3


# ── Rejected staff candidates ─────────────────────────────────────────────

def test_rejected_staff_candidate_parsed():
    entry = _entry(rejected_staff_candidates=[_rejected_staff(staff_id=777)])
    traces = build_candidate_traces([entry])
    rejected = [t for t in traces if t.candidate_type == "STAFF" and t.decision == "REJECTED"]
    assert len(rejected) == 1
    assert rejected[0].candidate_id == 777


def test_non_dict_candidates_skipped():
    entry = _entry(rejected_room_candidates=["invalid", None, 42])
    traces = build_candidate_traces([entry])
    rejected = [t for t in traces if t.decision == "REJECTED"]
    assert rejected == []


# ── CandidateTrace fields ─────────────────────────────────────────────────

def test_trace_has_required_fields():
    traces = build_candidate_traces([_entry()])
    for t in traces:
        assert isinstance(t, CandidateTrace)
        assert t.trace_id
        assert t.decision in ("ACCEPTED", "REJECTED")
        assert t.candidate_type in ("ROOM", "STAFF", "TIMESLOT")
        assert t.timestamp
        assert t.domain == "optimization"


def test_trace_is_immutable():
    traces = build_candidate_traces([_entry()])
    t = traces[0]
    try:
        t.decision = "MUTATED"  # type: ignore[misc]
        assert False, "Should have raised FrozenInstanceError"
    except Exception:
        pass


# ── Serialization ─────────────────────────────────────────────────────────

def test_to_dicts_returns_list_of_dicts():
    traces = build_candidate_traces([_entry()])
    result = candidate_traces_to_dicts(traces)
    assert isinstance(result, list)
    assert all(isinstance(d, dict) for d in result)


def test_to_dicts_round_trip():
    traces = build_candidate_traces([_entry()])
    dicts = candidate_traces_to_dicts(traces)
    assert dicts[0]["trace_id"] == traces[0].trace_id
