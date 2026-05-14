"""Schedule lifecycle event builders.

Produces structured event payload dicts for lifecycle transitions.
These are domain event payloads (not audit rows) — callers decide
whether to emit via event_service.emit() or store elsewhere.

All functions are pure logic. No DB, no bus, no ORM.
"""
from __future__ import annotations

from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base_payload(
    event_type: str,
    actor_id: int | None,
    session_id: int | None,
    derived_schedule_state: str,
    governance_state: str,
    reason: str | None,
    risk_snapshot: dict | None,
    quality_snapshot: dict | None,
) -> dict:
    return {
        "event_type": event_type,
        "actor_id": actor_id,
        "session_id": session_id,
        "derived_schedule_state": derived_schedule_state,
        "governance_state": governance_state,
        "timestamp": _now_iso(),
        "reason": reason,
        "risk_snapshot": risk_snapshot or {},
        "quality_snapshot": quality_snapshot or {},
    }


def build_publication_event(
    *,
    actor_id: int | None,
    session_id: int | None,
    derived_schedule_state: str,
    governance_state: str,
    risk_score: float,
    quality_snapshot: dict | None = None,
) -> dict:
    """Build a SCHEDULE_PUBLISHED lifecycle event payload."""
    return _base_payload(
        event_type="SCHEDULE_PUBLISHED",
        actor_id=actor_id,
        session_id=session_id,
        derived_schedule_state=derived_schedule_state,
        governance_state=governance_state,
        reason=None,
        risk_snapshot={"risk_score": risk_score, "governance_state": governance_state},
        quality_snapshot=quality_snapshot,
    )


def build_rollback_event(
    *,
    actor_id: int | None,
    session_id: int | None,
    derived_schedule_state: str,
    reason: str,
    risk_snapshot: dict | None = None,
) -> dict:
    """Build a SCHEDULE_ROLLED_BACK lifecycle event payload.

    Raises ValueError if reason is empty.
    """
    if not reason or not reason.strip():
        raise ValueError("Rollback event requires a non-empty reason.")
    return _base_payload(
        event_type="SCHEDULE_ROLLED_BACK",
        actor_id=actor_id,
        session_id=session_id,
        derived_schedule_state=derived_schedule_state,
        governance_state="",
        reason=reason.strip(),
        risk_snapshot=risk_snapshot,
        quality_snapshot=None,
    )


def build_archive_event(
    *,
    actor_id: int | None,
    session_id: int | None,
    derived_schedule_state: str,
) -> dict:
    """Build a SCHEDULE_ARCHIVED lifecycle event payload."""
    return _base_payload(
        event_type="SCHEDULE_ARCHIVED",
        actor_id=actor_id,
        session_id=session_id,
        derived_schedule_state=derived_schedule_state,
        governance_state="",
        reason=None,
        risk_snapshot=None,
        quality_snapshot=None,
    )


def build_reopen_event(
    *,
    actor_id: int | None,
    session_id: int | None,
    derived_schedule_state: str,
    reason: str,
) -> dict:
    """Build a SCHEDULE_REOPENED lifecycle event payload.

    Raises ValueError if reason is empty.
    """
    if not reason or not reason.strip():
        raise ValueError("Reopen event requires a non-empty reason.")
    return _base_payload(
        event_type="SCHEDULE_REOPENED",
        actor_id=actor_id,
        session_id=session_id,
        derived_schedule_state=derived_schedule_state,
        governance_state="",
        reason=reason.strip(),
        risk_snapshot=None,
        quality_snapshot=None,
    )


def build_governance_override_event(
    *,
    actor_id: int | None,
    session_id: int | None,
    blockers_overridden: list[str],
    reason: str,
    governance_state: str,
) -> dict:
    """Build a GOVERNANCE_OVERRIDE_APPLIED lifecycle event payload.

    Raises ValueError if reason is empty or blockers_overridden is empty.
    """
    if not reason or not reason.strip():
        raise ValueError("Governance override event requires a non-empty reason.")
    if not blockers_overridden:
        raise ValueError("Governance override event must name at least one blocker.")
    payload = _base_payload(
        event_type="GOVERNANCE_OVERRIDE_APPLIED",
        actor_id=actor_id,
        session_id=session_id,
        derived_schedule_state="",
        governance_state=governance_state,
        reason=reason.strip(),
        risk_snapshot=None,
        quality_snapshot=None,
    )
    payload["blockers_overridden"] = list(blockers_overridden)
    return payload
