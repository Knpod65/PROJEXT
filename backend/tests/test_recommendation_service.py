"""Tests for recommendation_service."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.recommendation_service import (
    generate_recommendations,
    CATEGORY_GOVERNANCE,
    CATEGORY_QUALITY,
    CATEGORY_WORKLOAD,
    CATEGORY_STAFFING,
    SOURCE_GOVERNANCE_STATE,
    SOURCE_QUALITY_SCORE,
    SOURCE_PREDICTIVE_HEURISTIC,
)


# ── Test helpers ──────────────────────────────────────────────────────────

def _gov(state="AUTO_APPROVED", priority="LOW"):
    return {"governance_state": state, "review_priority": priority}


def _quality(overall=80.0, **kw):
    base = {
        "overall_score": overall,
        "quality_band": "GOOD",
        "fairness_score": 75.0,
        "room_efficiency_score": 82.0,
        "invigilator_balance_score": 78.0,
    }
    base.update(kw)
    return base


def _entry(staff=None, date="2026-10-01", room_cap=30, students=20):
    return {
        "section_id": 1,
        "course_id": "POL101",
        "room": {"id": 1, "capacity": room_cap},
        "num_students": students,
        "assigned_staff": staff if staff is not None else [101, 102],
        "exam_date": date,
        "split_count": 1,
    }


def _recs(gov=None, quality=None, schedule=None):
    return generate_recommendations(
        quality or _quality(),
        gov or _gov(),
        schedule or [_entry()],
    )


# ── Return shape ──────────────────────────────────────────────────────────

def test_returns_list():
    assert isinstance(_recs(), list)


def test_required_keys_present():
    recs = generate_recommendations(_quality(), _gov("BLOCKED"), [_entry()])
    for r in recs:
        assert "priority" in r
        assert "category" in r
        assert "action" in r
        assert "message" in r
        assert "source" in r
        assert "rule" in r
        assert "reason" in r


def test_sorted_by_priority_ascending():
    recs = generate_recommendations(
        _quality(overall=50.0),
        _gov("BLOCKED"),
        [_entry(staff=[101]) for _ in range(7)],
    )
    priorities = [r["priority"] for r in recs]
    assert priorities == sorted(priorities)


# ── Governance — BLOCKED ──────────────────────────────────────────────────

def test_blocked_generates_governance_rec():
    recs = _recs(gov=_gov("BLOCKED"))
    gov_recs = [r for r in recs if r["category"] == CATEGORY_GOVERNANCE]
    assert len(gov_recs) >= 1


def test_blocked_rec_has_priority_1():
    recs = _recs(gov=_gov("BLOCKED"))
    gov_recs = [r for r in recs if r["category"] == CATEGORY_GOVERNANCE]
    assert any(r["priority"] == 1 for r in gov_recs)


def test_blocked_rec_source_is_governance():
    recs = _recs(gov=_gov("BLOCKED"))
    gov_recs = [r for r in recs if r["category"] == CATEGORY_GOVERNANCE]
    assert all(r["source"] == SOURCE_GOVERNANCE_STATE for r in gov_recs)


def test_escalation_required_generates_rec():
    recs = _recs(gov=_gov("ESCALATION_REQUIRED"))
    gov_recs = [r for r in recs if r["category"] == CATEGORY_GOVERNANCE]
    assert any(r["action"] == "ESCALATE_TO_AUTHORITY" for r in gov_recs)


def test_manual_review_required_generates_rec():
    recs = _recs(gov=_gov("MANUAL_REVIEW_REQUIRED"))
    gov_recs = [r for r in recs if r["category"] == CATEGORY_GOVERNANCE]
    assert any(r["action"] == "REQUEST_MANUAL_REVIEW" for r in gov_recs)


def test_approval_required_generates_rec():
    recs = _recs(gov=_gov("APPROVAL_REQUIRED"))
    gov_recs = [r for r in recs if r["category"] == CATEGORY_GOVERNANCE]
    assert any(r["action"] == "OBTAIN_APPROVAL" for r in gov_recs)


def test_auto_approved_no_governance_rec():
    recs = _recs(gov=_gov("AUTO_APPROVED"))
    gov_recs = [r for r in recs if r["category"] == CATEGORY_GOVERNANCE]
    assert gov_recs == []


# ── Quality thresholds ────────────────────────────────────────────────────

def test_score_below_55_triggers_reoptimization_rec():
    recs = _recs(quality=_quality(overall=45.0))
    q_recs = [r for r in recs if r["category"] == CATEGORY_QUALITY]
    assert any(r["action"] == "TRIGGER_REOPTIMIZATION" for r in q_recs)


def test_score_between_55_and_70_triggers_review_rec():
    recs = _recs(quality=_quality(overall=65.0))
    q_recs = [r for r in recs if r["category"] == CATEGORY_QUALITY]
    assert any(r["action"] == "REVIEW_LOW_SCORING_DIMENSIONS" for r in q_recs)


def test_score_above_70_no_quality_rec():
    recs = _recs(quality=_quality(overall=80.0))
    q_recs = [r for r in recs if r["category"] == CATEGORY_QUALITY and
              r["action"] in ("TRIGGER_REOPTIMIZATION", "REVIEW_LOW_SCORING_DIMENSIONS")]
    assert q_recs == []


def test_quality_missing_overall_score_no_crash():
    recs = generate_recommendations({}, _gov(), [_entry()])
    assert isinstance(recs, list)


def test_low_room_efficiency_score_generates_rec():
    recs = _recs(quality=_quality(room_efficiency_score=50.0))
    dim_recs = [r for r in recs if r.get("rule") == "ROOM_EFFICIENCY_LOW"]
    assert len(dim_recs) >= 1


def test_low_invigilator_balance_score_generates_rec():
    recs = _recs(quality=_quality(invigilator_balance_score=55.0))
    dim_recs = [r for r in recs if r.get("rule") == "INVIGILATOR_BALANCE_LOW"]
    assert len(dim_recs) >= 1


# ── Predictive balancing integration ─────────────────────────────────────

def test_high_risk_staff_generates_predictive_rec():
    schedule = [_entry(staff=[101]) for _ in range(7)]
    recs = generate_recommendations(_quality(), _gov(), schedule)
    pred_recs = [r for r in recs if r["source"] == SOURCE_PREDICTIVE_HEURISTIC]
    assert len(pred_recs) >= 1


def test_high_risk_predictive_rec_has_low_priority_number():
    schedule = [_entry(staff=[101]) for _ in range(7)]
    recs = generate_recommendations(_quality(), _gov(), schedule)
    pred_recs = [r for r in recs if r["source"] == SOURCE_PREDICTIVE_HEURISTIC]
    # HIGH_RISK maps to priority 2
    assert any(r["priority"] == 2 for r in pred_recs)


def test_fragile_day_generates_staffing_category_rec():
    schedule = [_entry(staff=[101], date="2026-10-01")]  # only 1 unique staff
    recs = generate_recommendations(_quality(), _gov(), schedule)
    staffing_recs = [r for r in recs if r["category"] == CATEGORY_STAFFING]
    assert len(staffing_recs) >= 1


def test_empty_schedule_no_crash():
    recs = generate_recommendations(_quality(), _gov(), [])
    assert isinstance(recs, list)


# ── Context parameter ─────────────────────────────────────────────────────

def test_context_does_not_affect_output():
    recs_no_ctx = generate_recommendations(_quality(), _gov("BLOCKED"), [_entry()])
    recs_with_ctx = generate_recommendations(
        _quality(), _gov("BLOCKED"), [_entry()],
        context={"session_id": "abc", "actor_id": 42},
    )
    # Context is metadata only — output logic must not change
    assert len(recs_no_ctx) == len(recs_with_ctx)
