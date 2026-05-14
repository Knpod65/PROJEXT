"""Tests for services/lifecycle_timeline_service.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.lifecycle_timeline_service import (
    build_lifecycle_timeline,
    summarize_lifecycle_timeline,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _event(**kwargs):
    base = {
        "event_type": "TEST_EVENT",
        "domain": "test",
        "timestamp": "2026-05-01T08:00:00+00:00",
        "severity": "INFO",
    }
    base.update(kwargs)
    return base


# ── Empty input ───────────────────────────────────────────────────────────────

def test_empty_list_returns_empty_timeline():
    assert build_lifecycle_timeline([]) == []


def test_empty_timeline_summary_has_zero_count():
    s = summarize_lifecycle_timeline([])
    assert s["event_count"] == 0
    assert s["first_event_at"] is None
    assert s["last_event_at"] is None
    assert s["has_rollback"] is False
    assert s["has_override"] is False
    assert s["has_publication"] is False


# ── Timeline item shape ───────────────────────────────────────────────────────

def test_timeline_items_have_all_required_keys():
    timeline = build_lifecycle_timeline([_event()])
    item = timeline[0]
    for key in ("timestamp", "event_type", "domain", "actor_id", "actor_role",
                "summary", "severity", "aggregate_type", "aggregate_id"):
        assert key in item, f"Missing key: {key}"


# ── Sorting ───────────────────────────────────────────────────────────────────

def test_timeline_sorted_by_timestamp_ascending():
    events = [
        _event(timestamp="2026-05-03T10:00:00+00:00"),
        _event(timestamp="2026-05-01T08:00:00+00:00"),
        _event(timestamp="2026-05-02T09:00:00+00:00"),
    ]
    timeline = build_lifecycle_timeline(events)
    ts = [item["timestamp"] for item in timeline]
    assert ts == sorted(ts)


def test_none_timestamps_sorted_last():
    events = [
        _event(timestamp=None, event_type="NO_TS"),
        _event(timestamp="2026-05-01T08:00:00+00:00", event_type="HAS_TS"),
    ]
    timeline = build_lifecycle_timeline(events)
    assert timeline[0]["event_type"] == "HAS_TS"
    assert timeline[1]["event_type"] == "NO_TS"


# ── Field fallback extraction ─────────────────────────────────────────────────

def test_event_type_falls_back_to_type_key():
    e = {"type": "SESSION_CREATED", "timestamp": "2026-05-01T08:00:00+00:00"}
    timeline = build_lifecycle_timeline([e])
    assert timeline[0]["event_type"] == "SESSION_CREATED"


def test_summary_falls_back_to_details_key():
    e = _event(details="Session was locked by admin.")
    timeline = build_lifecycle_timeline([e])
    assert timeline[0]["summary"] == "Session was locked by admin."


def test_summary_falls_back_to_event_type_when_no_detail():
    e = {"event_type": "STATUS_TRANSITION", "timestamp": "2026-05-01T08:00:00+00:00"}
    timeline = build_lifecycle_timeline([e])
    assert timeline[0]["summary"] == "STATUS_TRANSITION"


def test_actor_id_falls_back_to_actor_key():
    e = _event(actor="99")
    e.pop("actor_id", None)
    timeline = build_lifecycle_timeline([e])
    assert timeline[0]["actor_id"] == "99"


# ── Summary flags ─────────────────────────────────────────────────────────────

def test_has_rollback_true_when_rolled_back_event():
    events = [_event(event_type="SCHEDULE_ROLLED_BACK")]
    timeline = build_lifecycle_timeline(events)
    s = summarize_lifecycle_timeline(timeline)
    assert s["has_rollback"] is True


def test_has_override_true_when_override_event():
    events = [_event(event_type="GOVERNANCE_OVERRIDE_APPLIED")]
    timeline = build_lifecycle_timeline(events)
    s = summarize_lifecycle_timeline(timeline)
    assert s["has_override"] is True


def test_has_publication_true_when_published_event():
    events = [_event(event_type="SCHEDULE_PUBLISHED")]
    timeline = build_lifecycle_timeline(events)
    s = summarize_lifecycle_timeline(timeline)
    assert s["has_publication"] is True


def test_flags_all_false_for_normal_events():
    events = [_event(event_type="SESSION_CREATED")]
    timeline = build_lifecycle_timeline(events)
    s = summarize_lifecycle_timeline(timeline)
    assert s["has_rollback"] is False
    assert s["has_override"] is False
    assert s["has_publication"] is False


# ── Highest severity ──────────────────────────────────────────────────────────

def test_highest_severity_escalates_to_hard_fail():
    events = [
        _event(severity="INFO"),
        _event(severity="HARD_FAIL"),
        _event(severity="WARNING"),
    ]
    timeline = build_lifecycle_timeline(events)
    s = summarize_lifecycle_timeline(timeline)
    assert s["highest_severity"] == "HARD_FAIL"


def test_highest_severity_defaults_to_info_on_empty():
    s = summarize_lifecycle_timeline([])
    assert s["highest_severity"] == "INFO"


# ── First/last event timestamps ───────────────────────────────────────────────

def test_first_and_last_event_timestamps():
    events = [
        _event(timestamp="2026-05-01T08:00:00+00:00"),
        _event(timestamp="2026-05-05T12:00:00+00:00"),
        _event(timestamp="2026-05-03T10:00:00+00:00"),
    ]
    timeline = build_lifecycle_timeline(events)
    s = summarize_lifecycle_timeline(timeline)
    assert s["first_event_at"] == "2026-05-01T08:00:00+00:00"
    assert s["last_event_at"] == "2026-05-05T12:00:00+00:00"


# ── Mixed source events ───────────────────────────────────────────────────────

def test_mixed_source_events_normalized():
    events = [
        # governance trace format
        {"type": "SESSION_CREATED", "timestamp": "2026-05-01T08:00:00+00:00",
         "actor": None, "details": "Session created.", "severity": "INFO"},
        # EventEnvelope dict format
        {"event_type": "SCHEDULE_PUBLISHED", "domain": "governance",
         "timestamp": "2026-05-05T12:00:00+00:00", "severity": "INFO",
         "actor_id": 1, "actor_role": "admin"},
    ]
    timeline = build_lifecycle_timeline(events)
    assert len(timeline) == 2
    types = [item["event_type"] for item in timeline]
    assert "SESSION_CREATED" in types
    assert "SCHEDULE_PUBLISHED" in types
