"""Tests for publication_governance_service.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.publication_governance_service import (
    assess_publication_readiness,
    assess_rollback_safety,
    build_publish_audit_payload,
    build_emergency_override_payload,
    PublicationReadiness,
    RollbackAssessment,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _clean_governance():
    return {"governance_state": "AUTO_APPROVED", "review_priority": "LOW"}


def _clean_recheck():
    return {"hard_fail_count": 0, "warning_count": 0}


def _clean_quality():
    return {"overall_score": 85}


def _blocked_governance():
    return {"governance_state": "BLOCKED", "review_priority": "CRITICAL"}


def _hard_fail_recheck():
    return {"hard_fail_count": 3, "warning_count": 1}


# ── assess_publication_readiness ──────────────────────────────────────────────

def test_clean_can_publish():
    r = assess_publication_readiness(
        quality_report=_clean_quality(),
        governance=_clean_governance(),
        recheck_summary=_clean_recheck(),
        schedule_state="APPROVED",
    )
    assert r.can_publish is True
    assert r.risk_score < 60.0


def test_blocked_governance_cannot_publish():
    r = assess_publication_readiness(
        quality_report=_clean_quality(),
        governance=_blocked_governance(),
        recheck_summary=_clean_recheck(),
        schedule_state="APPROVED",
    )
    assert r.can_publish is False
    codes = [b["code"] for b in r.blockers]
    assert "GOVERNANCE_BLOCKED" in codes


def test_hard_fail_blocks_publication():
    r = assess_publication_readiness(
        quality_report=_clean_quality(),
        governance=_clean_governance(),
        recheck_summary=_hard_fail_recheck(),
        schedule_state="APPROVED",
    )
    assert r.can_publish is False
    codes = [b["code"] for b in r.blockers]
    assert "HARD_FAILURES_PRESENT" in codes


def test_risk_score_maximum_with_blocked_state():
    r = assess_publication_readiness(
        quality_report={"overall_score": 50},
        governance={"governance_state": "BLOCKED", "review_priority": ""},
        recheck_summary={"hard_fail_count": 5, "warning_count": 3},
        schedule_state="DRAFT",
    )
    assert r.risk_score == 100.0


def test_risk_score_minimum_with_clean_state():
    r = assess_publication_readiness(
        quality_report=_clean_quality(),
        governance=_clean_governance(),
        recheck_summary=_clean_recheck(),
        schedule_state="APPROVED",
    )
    assert r.risk_score == 20.0


def test_schedule_not_approved_adds_warning_blocker():
    r = assess_publication_readiness(
        quality_report=_clean_quality(),
        governance=_clean_governance(),
        recheck_summary=_clean_recheck(),
        schedule_state="DRAFT",
    )
    codes = [b["code"] for b in r.blockers]
    assert "SCHEDULE_NOT_APPROVED" in codes


def test_escalation_required_adds_warning_blocker():
    r = assess_publication_readiness(
        quality_report=_clean_quality(),
        governance={"governance_state": "ESCALATION_REQUIRED", "review_priority": "HIGH"},
        recheck_summary=_clean_recheck(),
        schedule_state="APPROVED",
    )
    codes = [b["code"] for b in r.blockers]
    assert "ESCALATION_REQUIRED" in codes
    severities = [b["severity"] for b in r.blockers if b["code"] == "ESCALATION_REQUIRED"]
    assert severities[0] == "WARNING"


def test_low_quality_score_adds_warning():
    r = assess_publication_readiness(
        quality_report={"overall_score": 60},
        governance=_clean_governance(),
        recheck_summary=_clean_recheck(),
        schedule_state="APPROVED",
    )
    assert any("60" in w for w in r.warnings)


def test_empty_dicts_handled_gracefully():
    r = assess_publication_readiness(
        quality_report={},
        governance={},
        recheck_summary={},
        schedule_state="DRAFT",
    )
    assert isinstance(r, PublicationReadiness)
    assert isinstance(r.can_publish, bool)
    assert isinstance(r.risk_score, float)


def test_approval_metadata_has_required_keys():
    r = assess_publication_readiness(
        quality_report=_clean_quality(),
        governance=_clean_governance(),
        recheck_summary=_clean_recheck(),
        schedule_state="APPROVED",
    )
    for key in ("governance_state", "hard_fail_count", "risk_score", "assessed_at", "schedule_state"):
        assert key in r.approval_metadata


def test_published_state_skips_schedule_not_approved_blocker():
    r = assess_publication_readiness(
        quality_report=_clean_quality(),
        governance=_clean_governance(),
        recheck_summary=_clean_recheck(),
        schedule_state="PUBLISHED",
    )
    codes = [b["code"] for b in r.blockers]
    assert "SCHEDULE_NOT_APPROVED" not in codes


def test_hard_error_count_alias_supported():
    r = assess_publication_readiness(
        quality_report=_clean_quality(),
        governance=_clean_governance(),
        recheck_summary={"hard_error_count": 2, "warning_count": 0},
        schedule_state="APPROVED",
    )
    codes = [b["code"] for b in r.blockers]
    assert "HARD_FAILURES_PRESENT" in codes


# ── assess_rollback_safety ────────────────────────────────────────────────────

def test_rollback_from_published_is_safe():
    r = assess_rollback_safety(
        schedule_state="PUBLISHED",
        published_at="2026-05-10T12:00:00+00:00",
        actor_id=1,
        rollback_reason="critical data error",
    )
    assert r.can_rollback is True
    assert r.recommendation == "CAUTION"


def test_rollback_from_locked_high_risk():
    r = assess_rollback_safety(
        schedule_state="LOCKED",
        published_at="2026-05-01T08:00:00+00:00",
        actor_id=1,
        rollback_reason="emergency override",
    )
    assert r.can_rollback is False
    assert r.recommendation == "HIGH_RISK"
    assert r.data_loss_risk is True


def test_rollback_without_reason_cannot():
    r = assess_rollback_safety(
        schedule_state="PUBLISHED",
        published_at=None,
        actor_id=1,
        rollback_reason=None,
    )
    assert r.can_rollback is False


def test_rollback_with_empty_reason_cannot():
    r = assess_rollback_safety(
        schedule_state="PUBLISHED",
        published_at=None,
        actor_id=1,
        rollback_reason="   ",
    )
    assert r.can_rollback is False


def test_rollback_without_actor_cannot():
    r = assess_rollback_safety(
        schedule_state="PUBLISHED",
        published_at=None,
        actor_id=None,
        rollback_reason="valid reason",
    )
    assert r.can_rollback is False
    assert any("actor" in risk.lower() for risk in r.rollback_risks)


def test_rollback_from_approved_is_caution():
    r = assess_rollback_safety(
        schedule_state="APPROVED",
        published_at=None,
        actor_id=7,
        rollback_reason="governance decision reversed",
    )
    assert r.can_rollback is True
    assert r.recommendation == "CAUTION"


def test_rollback_from_draft_is_safe():
    r = assess_rollback_safety(
        schedule_state="DRAFT",
        published_at=None,
        actor_id=3,
        rollback_reason="reset",
    )
    assert r.can_rollback is True
    assert r.recommendation == "SAFE"


def test_rollback_result_is_frozen():
    r = assess_rollback_safety(
        schedule_state="DRAFT",
        published_at=None,
        actor_id=1,
        rollback_reason="test",
    )
    with pytest.raises(Exception):
        r.can_rollback = False  # type: ignore


# ── build_publish_audit_payload ───────────────────────────────────────────────

def test_audit_payload_has_required_keys():
    readiness = assess_publication_readiness(
        quality_report=_clean_quality(),
        governance=_clean_governance(),
        recheck_summary=_clean_recheck(),
        schedule_state="APPROVED",
    )
    payload = build_publish_audit_payload(readiness=readiness, actor_id=5, session_id="sess-123")
    for key in ("action", "actor_id", "session_id", "published_at", "governance_state", "risk_score", "can_publish"):
        assert key in payload


def test_audit_payload_action_is_correct():
    readiness = assess_publication_readiness(
        quality_report=_clean_quality(),
        governance=_clean_governance(),
        recheck_summary=_clean_recheck(),
        schedule_state="APPROVED",
    )
    payload = build_publish_audit_payload(readiness=readiness, actor_id=1, session_id=None)
    assert payload["action"] == "SCHEDULE_PUBLISHED"


def test_audit_payload_blocker_codes_is_list():
    readiness = assess_publication_readiness(
        quality_report=_clean_quality(),
        governance=_blocked_governance(),
        recheck_summary=_clean_recheck(),
        schedule_state="APPROVED",
    )
    payload = build_publish_audit_payload(readiness=readiness, actor_id=1, session_id=None)
    assert isinstance(payload["blocker_codes"], list)
    assert "GOVERNANCE_BLOCKED" in payload["blocker_codes"]


# ── build_emergency_override_payload ─────────────────────────────────────────

def test_emergency_override_requires_reason():
    with pytest.raises(ValueError, match="non-empty reason"):
        build_emergency_override_payload(actor_id=1, reason="", blockers_overridden=["GOVERNANCE_BLOCKED"])


def test_emergency_override_requires_blockers():
    with pytest.raises(ValueError, match="at least one blocker"):
        build_emergency_override_payload(actor_id=1, reason="emergency", blockers_overridden=[])


def test_emergency_override_payload_structure():
    payload = build_emergency_override_payload(
        actor_id=99,
        reason="  Emergency board decision  ",
        blockers_overridden=["GOVERNANCE_BLOCKED", "HARD_FAILURES_PRESENT"],
    )
    assert payload["action"] == "EMERGENCY_PUBLICATION_OVERRIDE"
    assert payload["actor_id"] == 99
    assert payload["override_reason"] == "Emergency board decision"
    assert payload["requires_post_incident_review"] is True
    assert len(payload["blockers_overridden"]) == 2


def test_emergency_override_strips_reason_whitespace():
    payload = build_emergency_override_payload(
        actor_id=1,
        reason="  padded reason  ",
        blockers_overridden=["GOVERNANCE_BLOCKED"],
    )
    assert payload["override_reason"] == "padded reason"
