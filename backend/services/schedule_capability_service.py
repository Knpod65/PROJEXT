"""Schedule capability service.

Computes what the current role can do right now, given lifecycle state,
governance state, and publication readiness. All inputs are pre-computed
by callers — no DB calls, no HTTP, no ORM.

Frontend MUST use this output instead of inferring capabilities from state.
"""
from __future__ import annotations

# ── Roles ─────────────────────────────────────────────────────────────────────

_ADMIN_ONLY: frozenset[str] = frozenset({"admin"})
_SIGNER_ROLES: frozenset[str] = frozenset({"admin", "esq_head", "secretary"})
_EDIT_ROLES: frozenset[str] = frozenset({"admin", "dept_supervisor", "teacher"})

# OptimizeSession.status values that mean "signing is active"
_SIGNING_STATUSES: frozenset[str] = frozenset({"confirming", "swap_confirming"})


# ── Public API ────────────────────────────────────────────────────────────────

def compute_schedule_capabilities(
    *,
    derived_schedule_state: str,
    governance_state: str,
    session_status: str,
    user_role: str,
    can_publish: bool,
    risk_score: float,
    hard_fail_count: int,
    blocker_codes: list[str],
) -> dict:
    """Compute what this role can do given the current lifecycle + governance.

    Args:
        derived_schedule_state: ScheduleState string from derive_schedule_state().
        governance_state:        From determine_governance_state().
        session_status:          Raw OptimizeSession.status ("draft", "locked", etc.).
        user_role:               Effective role string from get_effective_role().
        can_publish:             From PublicationReadiness.can_publish.
        risk_score:              From PublicationReadiness.risk_score (0–100, lower = safer).
        hard_fail_count:         From recheck_summary.
        blocker_codes:           From PublicationReadiness.blockers[*]["code"].

    Returns:
        Dict with boolean capabilities, blocking_reasons, warnings, required_actions.
    """
    blocking_reasons: list[str] = []
    warnings: list[str] = []
    required_actions: list[str] = []

    is_admin = user_role in _ADMIN_ONLY
    is_signer = user_role in _SIGNER_ROLES
    is_editor = user_role in _EDIT_ROLES

    state = derived_schedule_state
    is_locked_or_archived = state in ("LOCKED", "ARCHIVED")
    is_terminal = state == "ARCHIVED"

    # ── can_publish ───────────────────────────────────────────────────────────
    publish_blocked = not can_publish
    if is_admin and state == "APPROVED" and not publish_blocked:
        _can_publish = True
    else:
        _can_publish = False
        if not is_admin:
            blocking_reasons.append("Only admin can publish a schedule.")
        if state != "APPROVED":
            blocking_reasons.append(
                f"Schedule must be in APPROVED state to publish (current: {state})."
            )
        if publish_blocked:
            if hard_fail_count > 0:
                blocking_reasons.append(
                    f"{hard_fail_count} hard failure(s) must be resolved before publication."
                )
                required_actions.append("resolve_hard_failures")
            if "GOVERNANCE_BLOCKED" in blocker_codes:
                blocking_reasons.append("Governance is BLOCKED — resolve before publishing.")
                required_actions.append("resolve_governance_block")
            if risk_score >= 60:
                warnings.append(f"Risk score {risk_score:.0f} is above the publication threshold (60).")

    # ── can_unpublish ─────────────────────────────────────────────────────────
    _can_unpublish = is_admin and state == "PUBLISHED"

    # ── can_archive ───────────────────────────────────────────────────────────
    _can_archive = is_admin and state in ("APPROVED", "LOCKED")

    # ── can_reopen ────────────────────────────────────────────────────────────
    _can_reopen = is_admin and state == "LOCKED"

    # ── can_rollback ──────────────────────────────────────────────────────────
    _can_rollback = is_admin and not is_terminal and state not in ("DRAFT", "OPTIMIZED")
    if not _can_rollback and not is_admin:
        blocking_reasons.append("Only admin can initiate a rollback.")

    # ── can_edit ──────────────────────────────────────────────────────────────
    # dept_supervisor and teacher can edit (own scope, enforced at query layer)
    _can_edit = is_editor and not is_locked_or_archived
    if not _can_edit and is_locked_or_archived:
        warnings.append(f"Schedule is {state} — editing is not permitted.")

    # ── can_regenerate ────────────────────────────────────────────────────────
    _can_regenerate = is_admin and state in ("DRAFT", "OPTIMIZED")

    # ── can_open_swap_window ──────────────────────────────────────────────────
    _can_open_swap_window = is_admin and session_status == "confirmed"

    # ── can_finalize ─────────────────────────────────────────────────────────
    _can_finalize = is_signer and session_status in _SIGNING_STATUSES

    # ── warnings for governance state ─────────────────────────────────────────
    if governance_state == "ESCALATION_REQUIRED":
        warnings.append("Escalation review is required before publication can proceed.")
        required_actions.append("complete_escalation_review")
    elif governance_state == "MANUAL_REVIEW_REQUIRED":
        warnings.append("Manual governance review is required.")
        required_actions.append("complete_manual_review")

    return {
        "can_publish":          _can_publish,
        "can_unpublish":        _can_unpublish,
        "can_archive":          _can_archive,
        "can_reopen":           _can_reopen,
        "can_rollback":         _can_rollback,
        "can_edit":             _can_edit,
        "can_regenerate":       _can_regenerate,
        "can_open_swap_window": _can_open_swap_window,
        "can_finalize":         _can_finalize,
        "blocking_reasons":     list(dict.fromkeys(blocking_reasons)),  # deduplicate
        "warnings":             warnings,
        "required_actions":     list(dict.fromkeys(required_actions)),
    }
