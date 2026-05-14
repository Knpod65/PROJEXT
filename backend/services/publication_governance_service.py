"""Publication governance service.

Assesses whether a schedule is safe to publish, evaluates rollback risk,
and builds audit payloads for publication actions.

All functions are pure logic — no DB calls, no HTTP, no ORM.
Callers supply pre-loaded report dicts and receive structured results.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PublicationBlocker:
    code: str
    severity: str       # "HARD_FAIL" | "WARNING"
    message: str
    can_override: bool


@dataclass(frozen=True)
class PublicationReadiness:
    can_publish: bool
    risk_score: float   # 0–100, lower = safer to publish
    blockers: tuple     # tuple of dicts (serialisable)
    warnings: tuple     # tuple of strings
    approval_metadata: dict
    governance_state: str


@dataclass(frozen=True)
class RollbackAssessment:
    can_rollback: bool
    rollback_risks: tuple       # tuple of strings
    data_loss_risk: bool
    recommendation: str         # "SAFE" | "CAUTION" | "HIGH_RISK"


# ── Private helpers ───────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _compute_risk_score(
    governance_state: str,
    hard_fail_count: int,
    overall_score: float | None,
    schedule_state: str,
) -> float:
    """Compute publish risk 0–100 (lower = safer).

    Deductions bring the base of 100 down:
    -40 if governance is AUTO_APPROVED
    -20 if no hard failures
    -10 if overall quality score >= 80
    -10 if schedule is in APPROVED state
    """
    risk = 100.0
    if governance_state == "AUTO_APPROVED":
        risk -= 40.0
    if hard_fail_count == 0:
        risk -= 20.0
    if isinstance(overall_score, (int, float)) and overall_score >= 80:
        risk -= 10.0
    if schedule_state == "APPROVED":
        risk -= 10.0
    return _clamp(risk)


def _collect_blockers(
    governance_state: str,
    hard_fail_count: int,
    schedule_state: str,
) -> list[PublicationBlocker]:
    blockers: list[PublicationBlocker] = []

    if governance_state == "BLOCKED":
        blockers.append(PublicationBlocker(
            code="GOVERNANCE_BLOCKED",
            severity="HARD_FAIL",
            message="Governance has blocked this schedule. Hard failures must be resolved before publication.",
            can_override=False,
        ))

    if hard_fail_count > 0:
        blockers.append(PublicationBlocker(
            code="HARD_FAILURES_PRESENT",
            severity="HARD_FAIL",
            message=f"{hard_fail_count} hard failure(s) remain unresolved in the recheck report.",
            can_override=False,
        ))

    if governance_state == "ESCALATION_REQUIRED":
        blockers.append(PublicationBlocker(
            code="ESCALATION_REQUIRED",
            severity="WARNING",
            message="This schedule requires escalation review before publication.",
            can_override=True,
        ))

    if schedule_state not in ("APPROVED", "GOVERNANCE_REVIEW", "RECHECKED"):
        if schedule_state not in ("PUBLISHED", "LOCKED"):  # already past this gate
            blockers.append(PublicationBlocker(
                code="SCHEDULE_NOT_APPROVED",
                severity="WARNING",
                message=f"Schedule is in state '{schedule_state}', not APPROVED. Governance approval is required first.",
                can_override=True,
            ))

    return blockers


def _collect_warnings(
    governance_state: str,
    overall_score: float | None,
    warning_count: int,
) -> list[str]:
    warnings: list[str] = []
    if governance_state == "MANUAL_REVIEW_REQUIRED":
        warnings.append("Manual governance review is required before publication.")
    if governance_state == "APPROVAL_REQUIRED":
        warnings.append("Explicit approval is required — the schedule carries unresolved warnings.")
    if isinstance(overall_score, (int, float)) and overall_score < 70:
        warnings.append(f"Quality score {overall_score} is below the 70-point review threshold.")
    if warning_count > 0:
        warnings.append(f"{warning_count} warning(s) remain in the recheck report.")
    return warnings


# ── Public API ────────────────────────────────────────────────────────────────

def assess_publication_readiness(
    quality_report: dict[str, Any],
    governance: dict[str, Any],
    recheck_summary: dict[str, Any],
    schedule_state: str,
) -> PublicationReadiness:
    """Determine whether a schedule can be published and at what risk level.

    Args:
        quality_report:  Output of compute_quality_report() or quality_breakdown key.
        governance:      Output of determine_governance_state().
        recheck_summary: The recheck_summary / severity_summary dict.
        schedule_state:  Current ScheduleState string of the schedule.

    Returns:
        PublicationReadiness with can_publish flag, risk_score, blockers, warnings.
    """
    governance_state = governance.get("governance_state", "")
    hard_fail_count = int(
        recheck_summary.get("hard_fail_count", recheck_summary.get("hard_error_count", 0))
    )
    warning_count = int(recheck_summary.get("warning_count", 0))
    overall_score = quality_report.get("overall_score")

    risk_score = _compute_risk_score(governance_state, hard_fail_count, overall_score, schedule_state)
    blockers = _collect_blockers(governance_state, hard_fail_count, schedule_state)
    warnings = _collect_warnings(governance_state, overall_score, warning_count)

    has_hard_fail_blocker = any(b.severity == "HARD_FAIL" for b in blockers)
    can_publish = (risk_score < 60.0) and not has_hard_fail_blocker

    approval_metadata = {
        "governance_state": governance_state,
        "review_priority": governance.get("review_priority", ""),
        "hard_fail_count": hard_fail_count,
        "warning_count": warning_count,
        "overall_score": overall_score,
        "risk_score": round(risk_score, 2),
        "schedule_state": schedule_state,
        "assessed_at": _now_iso(),
    }

    return PublicationReadiness(
        can_publish=can_publish,
        risk_score=round(risk_score, 2),
        blockers=tuple(asdict(b) for b in blockers),
        warnings=tuple(warnings),
        approval_metadata=approval_metadata,
        governance_state=governance_state,
    )


def assess_rollback_safety(
    schedule_state: str,
    published_at: str | None,
    actor_id: int | None,
    rollback_reason: str | None,
) -> RollbackAssessment:
    """Evaluate whether rolling back a publication is safe.

    Args:
        schedule_state:  Current state of the schedule (PUBLISHED, LOCKED, etc.).
        published_at:    ISO timestamp when publication occurred (if applicable).
        actor_id:        ID of the actor requesting rollback.
        rollback_reason: Mandatory justification for rollback.

    Returns:
        RollbackAssessment with can_rollback, risks, and recommendation.
    """
    if not rollback_reason or not rollback_reason.strip():
        return RollbackAssessment(
            can_rollback=False,
            rollback_risks=("Rollback requires a non-empty reason.",),
            data_loss_risk=False,
            recommendation="HIGH_RISK",
        )

    risks: list[str] = []
    data_loss_risk = False

    if schedule_state == "LOCKED":
        risks.append("Schedule is LOCKED — rollback requires administrator authority and may violate signed commitments.")
        risks.append("Signed approval records may need to be invalidated.")
        data_loss_risk = True
        recommendation = "HIGH_RISK"
        can_rollback = False
    elif schedule_state == "PUBLISHED":
        risks.append("Publication recipients may have already received and acted on schedule data.")
        if published_at:
            risks.append(f"Schedule was published at {published_at} — any distributed copies remain in circulation.")
        recommendation = "CAUTION"
        can_rollback = True
    elif schedule_state == "APPROVED":
        risks.append("Rolling back from APPROVED discards governance approval decision.")
        recommendation = "CAUTION"
        can_rollback = True
    else:
        recommendation = "SAFE"
        can_rollback = True

    if actor_id is None:
        risks.append("No actor identified for rollback — all rollbacks require an accountable user.")
        can_rollback = False

    return RollbackAssessment(
        can_rollback=can_rollback,
        rollback_risks=tuple(risks),
        data_loss_risk=data_loss_risk,
        recommendation=recommendation,
    )


def build_publish_audit_payload(
    readiness: PublicationReadiness,
    actor_id: int | None,
    session_id: str | None,
) -> dict[str, Any]:
    """Build the structured audit metadata dict for a publish action.

    Args:
        readiness:  PublicationReadiness result from assess_publication_readiness().
        actor_id:   ID of the user performing the publish.
        session_id: Correlation ID for the workflow session.

    Returns:
        Dict suitable for passing as audit_metadata to execute_with_audit().
    """
    return {
        "action": "SCHEDULE_PUBLISHED",
        "actor_id": actor_id,
        "session_id": session_id,
        "published_at": _now_iso(),
        "governance_state": readiness.governance_state,
        "risk_score": readiness.risk_score,
        "can_publish": readiness.can_publish,
        "blocker_codes": [b["code"] for b in readiness.blockers],
        "warning_count": len(readiness.warnings),
        "approval_metadata": readiness.approval_metadata,
    }


def build_emergency_override_payload(
    actor_id: int | None,
    reason: str,
    blockers_overridden: list[str],
) -> dict[str, Any]:
    """Build the emergency override payload for bypassing publication blockers.

    Emergency overrides MUST include a non-empty reason and an actor.
    The payload is returned for audit logging — callers decide whether to proceed.

    Args:
        actor_id:            ID of the actor authorizing the override.
        reason:              Mandatory justification for overriding blockers.
        blockers_overridden: List of blocker codes being bypassed.

    Returns:
        Dict with override metadata, or raises ValueError if reason is empty.
    """
    if not reason or not reason.strip():
        raise ValueError("Emergency override requires a non-empty reason.")
    if not blockers_overridden:
        raise ValueError("Emergency override must name at least one blocker being overridden.")

    return {
        "action": "EMERGENCY_PUBLICATION_OVERRIDE",
        "actor_id": actor_id,
        "override_reason": reason.strip(),
        "blockers_overridden": list(blockers_overridden),
        "override_at": _now_iso(),
        "requires_post_incident_review": True,
    }
