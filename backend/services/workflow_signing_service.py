"""
services/workflow_signing_service.py

Workflow signing state machine helpers for optimize_workflow.
Routers remain responsible for DB commits and transport-layer HTTP mapping.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import models
from auth_utils import get_effective_role, is_signer
from policies.workflow_policy import (
    WORKFLOW_SIGN_ORDER,
    get_round_allowed_statuses,
    is_backward_transition,
)
from services.exceptions import EMSConflictError, EMSPermissionError, EMSValidationError


@dataclass(frozen=True)
class WorkflowSignatureResult:
    round_no: int
    slot: int
    status: str
    completed: bool
    baseline_ready: bool


def _signature_field_names(round_no: int, slot: int) -> tuple[str, str]:
    suffix = "" if round_no == 1 else "r2"
    return f"sig{slot}{suffix}_user_id", f"sig{slot}{suffix}_at"


def _signature_snapshot(session: models.OptimizeSession, round_no: int) -> list[dict[str, object]]:
    suffix = "" if round_no == 1 else "r2"
    signatures = []
    for index, username in enumerate(WORKFLOW_SIGN_ORDER, start=1):
        user_id = getattr(session, f"sig{index}{suffix}_user_id")
        signed_at = getattr(session, f"sig{index}{suffix}_at")
        signatures.append(
            {
                "order": index,
                "username": username,
                "user_id": user_id,
                "signed_at": signed_at.isoformat() if signed_at else None,
            }
        )
    return signatures


def get_or_create_session(db, period_id: int) -> models.OptimizeSession:
    sess = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.exam_period_id == period_id
    ).first()
    if not sess:
        sess = models.OptimizeSession(exam_period_id=period_id, status="draft")
        db.add(sess)
        db.flush()
    return sess


def build_session_payload(session: models.OptimizeSession) -> dict:
    sigs_r1 = _signature_snapshot(session, 1)
    sigs_r2 = _signature_snapshot(session, 2)
    r1_done = sum(1 for signature in sigs_r1 if signature["signed_at"])
    r2_done = sum(1 for signature in sigs_r2 if signature["signed_at"])
    return {
        "id": session.id,
        "exam_period_id": session.exam_period_id,
        "status": session.status,
        "baseline_saved": session.baseline_saved,
        "round1": {
            "signatures": sigs_r1,
            "done": r1_done,
            "total": 4,
            "complete": r1_done == 4,
        },
        "round2": {
            "signatures": sigs_r2,
            "done": r2_done,
            "total": 4,
            "complete": r2_done == 4,
        },
        "next_signer_r1": WORKFLOW_SIGN_ORDER[r1_done] if r1_done < 4 else None,
        "next_signer_r2": WORKFLOW_SIGN_ORDER[r2_done] if r2_done < 4 else None,
    }


def get_signer_list(current_user: models.User) -> list[dict[str, object]]:
    return [
        {
            "order": index,
            "username": username,
            "is_me": current_user.username == username,
        }
        for index, username in enumerate(WORKFLOW_SIGN_ORDER, start=1)
    ]


def get_expected_signer_username(session: models.OptimizeSession, round_no: int) -> Optional[str]:
    allowed_statuses = get_round_allowed_statuses(round_no)
    if session.status not in allowed_statuses:
        return None
    signatures = _signature_snapshot(session, round_no)
    completed_count = sum(1 for signature in signatures if signature["signed_at"])
    if completed_count >= len(WORKFLOW_SIGN_ORDER):
        return None
    return WORKFLOW_SIGN_ORDER[completed_count]


def get_current_signer_slot(session: models.OptimizeSession, round_no: int) -> Optional[int]:
    expected_username = get_expected_signer_username(session, round_no)
    if expected_username is None:
        return None
    signatures = _signature_snapshot(session, round_no)
    for signature in signatures:
        if signature["username"] == expected_username:
            return int(signature["order"])
    return None


def validate_signer_for_round(session: models.OptimizeSession, current_user: models.User, round_no: int) -> int:
    if session is None:
        raise EMSValidationError("ยังไม่มี optimize session")

    allowed_statuses = get_round_allowed_statuses(round_no)
    if session.status not in allowed_statuses:
        raise EMSConflictError(
            f"ไม่อยู่ใน state ที่ sign round {round_no} ได้ (status={session.status})"
        )

    if not is_signer(current_user):
        raise EMSPermissionError("เฉพาะผู้มีสิทธิ์ลงนามเท่านั้น (admin / esq_head / secretary)")

    slot = get_current_signer_slot(session, round_no)
    if slot is None:
        raise EMSConflictError("ลายเซ็นครบแล้ว")

    expected_username = WORKFLOW_SIGN_ORDER[slot - 1]
    if current_user.username != expected_username:
        raise EMSPermissionError(
            f"ลำดับที่ {slot} ต้องเป็น {expected_username} เท่านั้น (คุณคือ {current_user.username})"
        )

    return slot


def apply_signature(
    session: models.OptimizeSession,
    current_user: models.User,
    round_no: int,
    *,
    now: datetime | None = None,
) -> WorkflowSignatureResult:
    slot = validate_signer_for_round(session, current_user, round_no)
    user_field, signed_at_field = _signature_field_names(round_no, slot)
    setattr(session, user_field, current_user.id)
    setattr(session, signed_at_field, now or datetime.now(timezone.utc))

    signatures = _signature_snapshot(session, round_no)
    done = sum(1 for signature in signatures if signature["signed_at"])
    complete = done == len(WORKFLOW_SIGN_ORDER)

    if round_no == 1:
        session.status = "confirmed" if complete else "confirming"
    else:
        session.status = "locked" if complete else "swap_confirming"

    return WorkflowSignatureResult(
        round_no=round_no,
        slot=slot,
        status=session.status,
        completed=complete,
        baseline_ready=round_no == 1 and complete,
    )


def open_swap_transition(session: models.OptimizeSession) -> None:
    if session is None:
        raise EMSValidationError("ยังไม่มี optimize session")
    if session.status != "confirmed":
        raise EMSConflictError("ต้อง confirm round 1 ครบก่อน (4 ลายเซ็น)")
    session.status = "swap_open"


def ensure_forward_transition(
    session: models.OptimizeSession,
    target_status: str,
    *,
    allow_rollback: bool = False,
) -> None:
    if session is None:
        raise EMSValidationError("ยังไม่มี optimize session")
    if target_status == session.status:
        return
    if is_backward_transition(session.status, target_status) and not allow_rollback:
        raise EMSConflictError(
            f"ไม่สามารถถอยสถานะจาก '{session.status}' ไป '{target_status}' ได้โดยตรง"
        )
    session.status = target_status


def reject_transition(
    session: models.OptimizeSession,
    *,
    round_no: int,
    allow_rollback: bool = False,
) -> str:
    if round_no not in (1, 2):
        raise EMSValidationError("round ต้องเป็น 1 หรือ 2")
    target_status = "draft" if round_no == 1 else "swap_open"
    ensure_forward_transition(session, target_status, allow_rollback=allow_rollback)
    return session.status


def approve_transition(
    session: models.OptimizeSession,
    *,
    round_no: int,
) -> str:
    if round_no not in (1, 2):
        raise EMSValidationError("round ต้องเป็น 1 หรือ 2")
    target_status = "confirmed" if round_no == 1 else "locked"
    ensure_forward_transition(session, target_status)
    return session.status


def audit_action_for_signature(round_no: int, slot: int) -> str:
    return f"SIGN_R{round_no}_SLOT{slot}"
