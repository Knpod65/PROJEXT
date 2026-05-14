"""Schedule governance policy.

Centralizes transition permission rules as declarative data.
This is a richer pre-flight check layer — it does NOT replace the
guards inside ScheduleStateMachine (those remain as definitive enforcement).

All functions are pure logic. No DB calls, no ORM, no HTTP.
"""
from __future__ import annotations

# ── Role requirements per transition edge ─────────────────────────────────────
# Key format: "FROM_STATE→TO_STATE" or "ANY→TO_STATE" for universal rules.

_TRANSITION_ROLE_REQUIREMENTS: dict[str, frozenset[str]] = {
    "OPTIMIZED→RECHECKED":          frozenset({"admin"}),
    "RECHECKED→GOVERNANCE_REVIEW":  frozenset({"admin", "esq_head", "secretary"}),
    "RECHECKED→APPROVED":           frozenset({"admin"}),
    "RECHECKED→ROLLED_BACK":        frozenset({"admin"}),
    "GOVERNANCE_REVIEW→APPROVED":   frozenset({"admin", "esq_head", "secretary"}),
    "GOVERNANCE_REVIEW→ROLLED_BACK":frozenset({"admin"}),
    "APPROVED→PUBLISHED":           frozenset({"admin"}),
    "APPROVED→ROLLED_BACK":         frozenset({"admin"}),
    "PUBLISHED→LOCKED":             frozenset({"admin"}),
    "PUBLISHED→ROLLED_BACK":        frozenset({"admin"}),
    "LOCKED→ARCHIVED":              frozenset({"admin"}),
    "ROLLED_BACK→DRAFT":            frozenset({"admin"}),
    "OPTIMIZED→DRAFT":              frozenset({"admin"}),
}

# Transitions that always require an audit annotation in the log
_AUDIT_REQUIRED: frozenset[str] = frozenset({
    "APPROVED→PUBLISHED",
    "PUBLISHED→LOCKED",
    "LOCKED→ARCHIVED",
    "RECHECKED→ROLLED_BACK",
    "GOVERNANCE_REVIEW→ROLLED_BACK",
    "APPROVED→ROLLED_BACK",
    "PUBLISHED→ROLLED_BACK",
})


def _transition_key(from_state: str, to_state: str) -> str:
    return f"{from_state}→{to_state}"


def is_transition_allowed(
    from_state: str,
    to_state: str,
    *,
    user_role: str,
    governance_state: str = "",
    hard_fail_count: int = 0,
) -> bool:
    """Return True if the transition is allowed for this role and current conditions.

    Does not validate the state machine edge itself (ScheduleStateMachine does that).
    This is a pre-flight permission + governance check.
    """
    return len(get_transition_blockers(
        from_state, to_state,
        user_role=user_role,
        governance_state=governance_state,
        hard_fail_count=hard_fail_count,
    )) == 0


def get_transition_blockers(
    from_state: str,
    to_state: str,
    *,
    user_role: str,
    governance_state: str = "",
    hard_fail_count: int = 0,
) -> list[dict]:
    """Return list of blocker dicts for a proposed transition.

    Each blocker dict has: {code, reason, severity, can_override}.
    Empty list means transition is allowed.
    """
    blockers: list[dict] = []
    key = _transition_key(from_state, to_state)
    required = _TRANSITION_ROLE_REQUIREMENTS.get(key)

    # Unknown edge — not in the permission table
    if required is None:
        blockers.append({
            "code": "INVALID_TRANSITION_EDGE",
            "reason": f"Transition {from_state} → {to_state} is not defined in the governance policy.",
            "severity": "HARD_FAIL",
            "can_override": False,
        })
        return blockers

    # Role check
    if user_role not in required:
        blockers.append({
            "code": "ROLE_INSUFFICIENT",
            "reason": (
                f"Role '{user_role}' cannot trigger {from_state} → {to_state}. "
                f"Required: {sorted(required)}."
            ),
            "severity": "HARD_FAIL",
            "can_override": False,
        })

    # Governance block
    if to_state == "PUBLISHED" and governance_state == "BLOCKED":
        blockers.append({
            "code": "GOVERNANCE_BLOCKED",
            "reason": "Governance is BLOCKED — publication cannot proceed until resolved.",
            "severity": "HARD_FAIL",
            "can_override": False,
        })

    # Hard fails block RECHECKED → APPROVED
    if from_state == "RECHECKED" and to_state == "APPROVED" and hard_fail_count > 0:
        blockers.append({
            "code": "HARD_FAILS_PRESENT",
            "reason": f"{hard_fail_count} hard failure(s) must be resolved before approval.",
            "severity": "HARD_FAIL",
            "can_override": False,
        })

    # Rollback always requires admin (covered by role check above, but make explicit)
    if to_state == "ROLLED_BACK" and user_role != "admin":
        if not any(b["code"] == "ROLE_INSUFFICIENT" for b in blockers):
            blockers.append({
                "code": "ROLLBACK_REQUIRES_ADMIN",
                "reason": "Only admin can initiate a rollback.",
                "severity": "HARD_FAIL",
                "can_override": False,
            })

    return blockers


def get_required_roles(from_state: str, to_state: str) -> list[str]:
    """Return the sorted list of roles that may trigger this transition.

    Returns an empty list if the edge is unknown.
    """
    key = _transition_key(from_state, to_state)
    required = _TRANSITION_ROLE_REQUIREMENTS.get(key, frozenset())
    return sorted(required)


def requires_governance_review(
    from_state: str,
    to_state: str,
    *,
    governance_state: str,
    hard_fail_count: int,
) -> bool:
    """Return True if this transition should route through GOVERNANCE_REVIEW first.

    Used to recommend an intermediate step rather than a direct transition.
    """
    if to_state == "APPROVED":
        if governance_state in ("ESCALATION_REQUIRED", "MANUAL_REVIEW_REQUIRED"):
            return True
        if hard_fail_count > 0:
            return True
    if to_state == "PUBLISHED" and governance_state in ("ESCALATION_REQUIRED",):
        return True
    return False


def requires_audit_annotation(from_state: str, to_state: str) -> bool:
    """Return True if this transition must be accompanied by an audit log annotation."""
    return _transition_key(from_state, to_state) in _AUDIT_REQUIRED
