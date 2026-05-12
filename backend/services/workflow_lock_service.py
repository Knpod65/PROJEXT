"""
services/workflow_lock_service.py

Service-layer lock lifecycle for optimize workflow editing.
Routers should translate EMSDomainError subclasses into HTTPException.
"""
from __future__ import annotations

from datetime import datetime, timezone

from config.policy import WORKFLOW_LOCK_TTL_SECONDS
from services.exceptions import EMSConflictError, EMSPermissionError, EMSValidationError
from auth_utils import is_signer


def is_lock_expired(session, now: datetime | None = None) -> bool:
    lock_at = getattr(session, "edit_lock_at", None)
    if not lock_at:
        return True
    current = now or datetime.now(timezone.utc)
    elapsed = (current - lock_at).total_seconds()
    return elapsed > WORKFLOW_LOCK_TTL_SECONDS


def remaining_lock_seconds(session, now: datetime | None = None) -> int:
    lock_at = getattr(session, "edit_lock_at", None)
    if not lock_at:
        return 0
    current = now or datetime.now(timezone.utc)
    elapsed = (current - lock_at).total_seconds()
    return max(0, int(WORKFLOW_LOCK_TTL_SECONDS - elapsed))


def assert_session_editable_for_lock(session, current_user) -> None:
    if session is None:
        raise EMSValidationError("ยังไม่มี optimize session")

    if session.status not in ("draft",):
        raise EMSConflictError(
            f"ไม่สามารถแก้ไขได้ — session status='{session.status}' (ต้องอยู่ใน draft เท่านั้น)"
        )

    if not is_signer(current_user):
        raise EMSPermissionError("เฉพาะผู้มีสิทธิ์ลงนามเท่านั้น (admin / esq_head / secretary)")

    holder_id = getattr(session, "edit_lock_user_id", None)
    if holder_id and holder_id != current_user.id and not is_lock_expired(session):
        holder = getattr(session, "edit_lock_user", None)
        name = holder.full_name if holder else f"user#{holder_id}"
        remaining = remaining_lock_seconds(session)
        raise EMSConflictError(f"กำลังถูกแก้ไขโดย {name} (หมดอายุใน {remaining} วินาที)")


def acquire_lock(session, user, now: datetime | None = None) -> None:
    session.edit_lock_user_id = user.id
    session.edit_lock_at = now or datetime.now(timezone.utc)


def release_lock(session, user) -> bool:
    if getattr(session, "edit_lock_user_id", None) != user.id:
        return False
    session.edit_lock_user_id = None
    session.edit_lock_at = None
    return True


def heartbeat_lock(session, user, now: datetime | None = None) -> bool:
    if getattr(session, "edit_lock_user_id", None) != user.id:
        return False
    session.edit_lock_at = now or datetime.now(timezone.utc)
    return True
