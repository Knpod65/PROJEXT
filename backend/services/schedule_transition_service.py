"""Schedule transition service.

Coordinates governance policy + state machine into a single pre-flight
attempt_transition() check. Pure logic — callers decide what to persist.

Call order:
  1. schedule_governance_policy.get_transition_blockers() — role/governance pre-flight
  2. schedule_governance_policy.requires_audit_annotation()
  3. schedule_state_machine.transition()               — definitive enforcement

The state machine guards are NOT bypassed. If the policy pre-flight passes
but the state machine raises, the result is allowed=False with the guard error.
"""
from __future__ import annotations

from policies.schedule_governance_policy import (
    get_transition_blockers,
    requires_audit_annotation,
    requires_governance_review,
)
from services.schedule_state_machine import (
    ScheduleTransitionError,
    schedule_state_machine,
)


def attempt_transition(
    *,
    from_state: str,
    to_state: str,
    user_role: str,
    governance_state: str,
    hard_fail_count: int,
    reason: str | None = None,
    actor_id: int | None = None,
    metadata: dict | None = None,
) -> dict:
    """Pre-flight + state machine check for a proposed lifecycle transition.

    Does NOT mutate any state. Returns a structured result — callers decide
    whether to call schedule_state_machine.transition() for the real commit.

    Args:
        from_state:       Current derived_schedule_state.
        to_state:         Target ScheduleState string.
        user_role:        Effective role from get_effective_role().
        governance_state: From determine_governance_state().
        hard_fail_count:  From recheck_summary.
        reason:           Required for rollback transitions.
        actor_id:         Required for LOCKED → ARCHIVED.
        metadata:         Optional extra audit fields.

    Returns:
        Dict with allowed, target_state, transition_type, blockers, warnings,
        required_actions, audit_required, requires_emergency_override,
        state_machine_result.
    """
    policy_blockers = get_transition_blockers(
        from_state, to_state,
        user_role=user_role,
        governance_state=governance_state,
        hard_fail_count=hard_fail_count,
    )

    transition_type = _classify_transition(from_state, to_state)
    audit_required = requires_audit_annotation(from_state, to_state)
    requires_review = requires_governance_review(
        from_state, to_state,
        governance_state=governance_state,
        hard_fail_count=hard_fail_count,
    )

    warnings: list[str] = []
    required_actions: list[str] = []

    if requires_review:
        warnings.append(
            f"Transition {from_state} → {to_state} is recommended to route through "
            "GOVERNANCE_REVIEW first."
        )
        required_actions.append("complete_governance_review")

    # Pre-flight failed — return early without hitting state machine
    if policy_blockers:
        has_hard_fail = any(b["severity"] == "HARD_FAIL" for b in policy_blockers)
        return {
            "allowed": False,
            "target_state": to_state,
            "transition_type": transition_type,
            "blockers": policy_blockers,
            "warnings": warnings,
            "required_actions": required_actions,
            "audit_required": audit_required,
            "requires_emergency_override": has_hard_fail,
            "state_machine_result": None,
        }

    # Pre-flight passed — attempt the state machine transition
    try:
        result = schedule_state_machine.transition(
            from_state,
            to_state,
            actor_id=actor_id,
            reason=reason,
            hard_fail_count=hard_fail_count,
            governance_state=governance_state,
            metadata=metadata,
        )
        return {
            "allowed": True,
            "target_state": to_state,
            "transition_type": transition_type,
            "blockers": [],
            "warnings": warnings,
            "required_actions": required_actions,
            "audit_required": audit_required,
            "requires_emergency_override": False,
            "state_machine_result": result.audit_metadata,
        }
    except ScheduleTransitionError as exc:
        guard_blocker = {
            "code": "STATE_MACHINE_GUARD",
            "reason": str(exc),
            "severity": "HARD_FAIL",
            "can_override": False,
        }
        return {
            "allowed": False,
            "target_state": to_state,
            "transition_type": transition_type,
            "blockers": [guard_blocker],
            "warnings": warnings,
            "required_actions": required_actions,
            "audit_required": audit_required,
            "requires_emergency_override": True,
            "state_machine_result": None,
        }


def _classify_transition(from_state: str, to_state: str) -> str:
    if to_state == "ROLLED_BACK":
        return "rollback"
    if to_state == "PUBLISHED":
        return "publication"
    if to_state == "ARCHIVED":
        return "archival"
    return "normal"
