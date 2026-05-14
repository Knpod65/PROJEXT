"""Governance trace service.

Builds a chronological governance timeline from pre-loaded session data.
Pure logic — no DB calls, no ORM, no HTTP.

The timeline is built from OptimizeSession signature timestamps and the
output of determine_governance_state(). It provides executive-grade
explainability for how the schedule reached its current state.
"""
from __future__ import annotations

from typing import Any


def build_governance_trace(
    *,
    session_dict: dict[str, Any],
    governance_decision: dict[str, Any],
    recheck_issues: list[dict[str, Any]] | None = None,
    quality_snapshot: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build a chronological governance trace from session and governance data.

    Args:
        session_dict:       Serialized OptimizeSession fields (created_at, updated_at,
                            sig1_at…sig4_at, sig1r2_at…sig4r2_at, status, etc.).
        governance_decision: Output of determine_governance_state().
        recheck_issues:     List of recheck issue dicts with 'severity' field.
        quality_snapshot:   Dict with at least 'overall_score' and 'quality_band'.

    Returns:
        List of trace event dicts sorted by timestamp (Nones sorted to end),
        each with: type, timestamp, actor, details, severity.
    """
    events: list[dict[str, Any]] = []

    # Session creation
    created_at = _ts(session_dict.get("created_at"))
    events.append(_event(
        "SESSION_CREATED",
        timestamp=created_at,
        actor=None,
        details="Optimization session created — schedule allocations generated.",
        severity="INFO",
    ))

    # Round-1 signatures (sig1_at … sig4_at)
    _add_signature_events(events, session_dict, round_num=1)

    # Round-2 signatures (sig1r2_at … sig4r2_at)
    _add_signature_events(events, session_dict, round_num=2)

    # Status transition (derived from current status + updated_at)
    status = session_dict.get("status", "")
    updated_at = _ts(session_dict.get("updated_at"))
    if status:
        events.append(_event(
            "STATUS_TRANSITION",
            timestamp=updated_at,
            actor=None,
            details=f"Session status transitioned to '{status}'.",
            severity="INFO",
        ))

    # Governance decision
    gov_state = governance_decision.get("governance_state", "")
    review_priority = governance_decision.get("review_priority", "")
    gov_severity = "HARD_FAIL" if gov_state == "BLOCKED" else "WARNING" if gov_state in (
        "ESCALATION_REQUIRED", "MANUAL_REVIEW_REQUIRED",
    ) else "INFO"
    events.append(_event(
        "GOVERNANCE_DECISION",
        timestamp=None,
        actor=None,
        details=(
            f"Governance state: {gov_state}. "
            f"Review priority: {review_priority}. "
            f"{governance_decision.get('approval_reasoning', '')}".strip()
        ),
        severity=gov_severity,
    ))

    # Recheck HARD_FAIL issues
    for issue in (recheck_issues or []):
        if str(issue.get("severity", "")).upper() == "HARD_FAIL":
            events.append(_event(
                "RECHECK_BLOCKER",
                timestamp=None,
                actor=None,
                details=(
                    f"Hard failure: [{issue.get('code', 'UNKNOWN')}] "
                    f"{issue.get('message', '')}".strip()
                ),
                severity="HARD_FAIL",
            ))

    # Quality snapshot
    if quality_snapshot:
        score = quality_snapshot.get("overall_score", "")
        band = quality_snapshot.get("quality_band", "")
        events.append(_event(
            "QUALITY_ASSESSED",
            timestamp=None,
            actor=None,
            details=f"Quality score: {score}. Band: {band}.",
            severity="INFO",
        ))

    return _sort_events(events)


# ── Private helpers ───────────────────────────────────────────────────────────

def _event(
    event_type: str,
    *,
    timestamp: str | None,
    actor: str | None,
    details: str,
    severity: str,
) -> dict[str, Any]:
    return {
        "type": event_type,
        "timestamp": timestamp,
        "actor": actor,
        "details": details,
        "severity": severity,
    }


def _ts(value: Any) -> str | None:
    """Convert datetime / string timestamp to ISO string or None."""
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _add_signature_events(
    events: list[dict], session_dict: dict, round_num: int
) -> None:
    prefix = "" if round_num == 1 else "r2"
    suffix = f"r{round_num}" if round_num == 2 else ""
    for signer_num in range(1, 5):
        field = f"sig{signer_num}{suffix}_at" if round_num == 2 else f"sig{signer_num}_at"
        actor_field = f"sig{signer_num}{suffix}_user_id" if round_num == 2 else f"sig{signer_num}_user_id"
        ts = _ts(session_dict.get(field))
        if ts is not None:
            actor_id = session_dict.get(actor_field)
            events.append(_event(
                f"SIG_ROUND{round_num}_SIGNER{signer_num}",
                timestamp=ts,
                actor=str(actor_id) if actor_id is not None else None,
                details=f"Round {round_num} signature {signer_num} recorded.",
                severity="INFO",
            ))


def _sort_events(events: list[dict]) -> list[dict]:
    """Sort events by timestamp, Nones sorted to end."""
    return sorted(events, key=lambda e: (e["timestamp"] is None, e["timestamp"] or ""))
