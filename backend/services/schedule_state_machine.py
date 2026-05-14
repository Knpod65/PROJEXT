"""Schedule lifecycle state machine.

Manages the lifecycle of a generated exam schedule from creation through
publication, locking, and archival. This is distinct from the signing
workflow (OptimizeSession.status = draft/confirming/confirmed/...) which
tracks WHO has approved. This state machine tracks WHAT state the
SCHEDULE ITSELF is in.

States: DRAFT → OPTIMIZED → RECHECKED → (GOVERNANCE_REVIEW →) APPROVED
        → PUBLISHED → LOCKED → ARCHIVED
        Any non-terminal → ROLLED_BACK → DRAFT (recovery)

All transitions are pure logic — no DB calls. Callers own persistence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ScheduleState(str, Enum):
    DRAFT             = "DRAFT"
    OPTIMIZED         = "OPTIMIZED"
    RECHECKED         = "RECHECKED"
    GOVERNANCE_REVIEW = "GOVERNANCE_REVIEW"
    APPROVED          = "APPROVED"
    PUBLISHED         = "PUBLISHED"
    LOCKED            = "LOCKED"
    ARCHIVED          = "ARCHIVED"
    ROLLED_BACK       = "ROLLED_BACK"


# ScheduleState → set of reachable next states
_VALID_TRANSITIONS: dict[ScheduleState, set[ScheduleState]] = {
    ScheduleState.DRAFT:             {ScheduleState.OPTIMIZED},
    ScheduleState.OPTIMIZED:         {ScheduleState.RECHECKED, ScheduleState.DRAFT},
    ScheduleState.RECHECKED:         {
        ScheduleState.GOVERNANCE_REVIEW,
        ScheduleState.APPROVED,
        ScheduleState.ROLLED_BACK,
    },
    ScheduleState.GOVERNANCE_REVIEW: {ScheduleState.APPROVED, ScheduleState.ROLLED_BACK},
    ScheduleState.APPROVED:          {ScheduleState.PUBLISHED, ScheduleState.ROLLED_BACK},
    ScheduleState.PUBLISHED:         {ScheduleState.LOCKED, ScheduleState.ROLLED_BACK},
    ScheduleState.LOCKED:            {ScheduleState.ARCHIVED},
    ScheduleState.ARCHIVED:          set(),                     # terminal
    ScheduleState.ROLLED_BACK:       {ScheduleState.DRAFT},     # recovery path
}

_TERMINAL_STATES: frozenset[ScheduleState] = frozenset({ScheduleState.ARCHIVED})

# Maps OptimizeSession.status → ScheduleState without touching the DB.
# PUBLISHED / ARCHIVED / ROLLED_BACK are not derivable until SchedulePublicationState table exists.
_SESSION_STATUS_TO_SCHEDULE_STATE: dict[str, str] = {
    "draft":           "OPTIMIZED",         # CP-SAT ran; session under review
    "confirming":      "GOVERNANCE_REVIEW", # Round-1 signing in progress
    "confirmed":       "APPROVED",          # Round-1 complete; baseline_saved=True
    "swap_open":       "APPROVED",          # Swap window open; approval holds
    "swap_confirming": "GOVERNANCE_REVIEW", # Round-2 signing in progress
    "locked":          "APPROVED",          # All signatures; maximally approved
}


def derive_schedule_state(session_status: str, governance_state: str = "") -> str:
    """Map OptimizeSession.status to a ScheduleState string — pure logic, no DB.

    PUBLISHED / ARCHIVED / ROLLED_BACK are not derivable from session.status alone;
    they require a future SchedulePublicationState table.

    Governance override: if governance_state is BLOCKED and the derived state would
    be APPROVED, downgrade to GOVERNANCE_REVIEW — a blocked governance gate prevents
    publication regardless of signing completion.
    """
    derived = _SESSION_STATUS_TO_SCHEDULE_STATE.get(session_status, "OPTIMIZED")
    if derived == "APPROVED" and governance_state == "BLOCKED":
        return "GOVERNANCE_REVIEW"
    return derived


class ScheduleTransitionError(ValueError):
    """Raised when a transition violates the state machine rules."""


@dataclass(frozen=True)
class ScheduleTransitionResult:
    success: bool
    from_state: str
    to_state: str
    actor_id: int | None
    reason: str | None
    audit_metadata: dict
    timestamp: str


class ScheduleStateMachine:
    """Pure state-transition logic for the schedule lifecycle.

    No DB calls. All methods are deterministic given the same input.
    """

    def can_transition(self, from_state: str, to_state: str) -> bool:
        """Return True if the raw transition edge is defined (ignoring guards)."""
        try:
            src = ScheduleState(from_state)
            dst = ScheduleState(to_state)
        except ValueError:
            return False
        return dst in _VALID_TRANSITIONS.get(src, set())

    def valid_next_states(self, from_state: str) -> list[str]:
        """Return the list of states reachable from from_state (ignoring guards)."""
        try:
            src = ScheduleState(from_state)
        except ValueError:
            return []
        return [s.value for s in _VALID_TRANSITIONS.get(src, set())]

    def is_terminal(self, state: str) -> bool:
        """Return True if state is terminal (no valid outgoing transitions)."""
        try:
            return ScheduleState(state) in _TERMINAL_STATES
        except ValueError:
            return False

    def transition(
        self,
        from_state: str,
        to_state: str,
        *,
        actor_id: int | None,
        reason: str | None = None,
        hard_fail_count: int = 0,
        governance_state: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ScheduleTransitionResult:
        """Attempt the transition from_state → to_state with guard evaluation.

        Raises ScheduleTransitionError on any violation.
        Returns a ScheduleTransitionResult on success.
        """
        # 1. Parse states
        try:
            src = ScheduleState(from_state)
        except ValueError:
            raise ScheduleTransitionError(f"Unknown from_state: {from_state!r}")
        try:
            dst = ScheduleState(to_state)
        except ValueError:
            raise ScheduleTransitionError(f"Unknown to_state: {to_state!r}")

        # 2. Check transition edge
        if dst not in _VALID_TRANSITIONS.get(src, set()):
            raise ScheduleTransitionError(
                f"Invalid transition: {from_state} → {to_state}. "
                f"Valid next states from {from_state}: {self.valid_next_states(from_state)}"
            )

        # 3. Guard: rollback always requires a reason
        if dst == ScheduleState.ROLLED_BACK:
            if not reason or not reason.strip():
                raise ScheduleTransitionError(
                    "Transition to ROLLED_BACK requires a non-empty rollback_reason."
                )

        # 4. Guard: RECHECKED → APPROVED blocked when hard fails present
        if src == ScheduleState.RECHECKED and dst == ScheduleState.APPROVED:
            if hard_fail_count > 0:
                raise ScheduleTransitionError(
                    f"Cannot transition RECHECKED → APPROVED: "
                    f"{hard_fail_count} hard fail(s) are still present."
                )

        # 5. Guard: APPROVED → PUBLISHED blocked when governance is BLOCKED
        if src == ScheduleState.APPROVED and dst == ScheduleState.PUBLISHED:
            if governance_state == "BLOCKED":
                raise ScheduleTransitionError(
                    "Cannot transition APPROVED → PUBLISHED: governance_state is BLOCKED."
                )

        # 6. Guard: LOCKED → ARCHIVED requires an actor
        if src == ScheduleState.LOCKED and dst == ScheduleState.ARCHIVED:
            if actor_id is None:
                raise ScheduleTransitionError(
                    "Transition LOCKED → ARCHIVED requires an actor_id."
                )

        ts = datetime.now(timezone.utc).isoformat()
        audit = {
            "from_state": from_state,
            "to_state": to_state,
            "actor_id": actor_id,
            "reason": reason,
            "hard_fail_count": hard_fail_count,
            "governance_state": governance_state,
            "timestamp": ts,
            **(metadata or {}),
        }

        return ScheduleTransitionResult(
            success=True,
            from_state=from_state,
            to_state=to_state,
            actor_id=actor_id,
            reason=reason,
            audit_metadata=audit,
            timestamp=ts,
        )


# Module-level singleton for convenience
schedule_state_machine = ScheduleStateMachine()
