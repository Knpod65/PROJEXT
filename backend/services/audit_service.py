"""
services/audit_service.py — Thin, semantic wrapper around log_action().

Provides named functions for the three main audit event categories so
callers don't need to know the action-name strings or parameter order.
Backward compatible: all existing log_action() calls in routers continue
to work unchanged. This layer is additive.

Rules:
  - No FastAPI imports, no Depends(), no HTTPException.
  - Accepts db: Session + actor: User + optional request object.
  - Never logs secrets or raw PII (student_id in new_values is OK as a
    reference key; full student names are not).
"""
from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    import models


def audit_mutation(
    db: Session,
    actor: "models.User",
    action: str,
    table_name: str,
    record_id: Optional[int] = None,
    old_values: Optional[dict[str, Any]] = None,
    new_values: Optional[dict[str, Any]] = None,
    request=None,
) -> None:
    """Record a CREATE / UPDATE / DELETE mutation event."""
    from auth_utils import log_action
    log_action(
        db,
        actor,
        action,
        table_name=table_name,
        record_id=record_id,
        old_values=old_values,
        new_values=new_values,
        request=request,
    )


def audit_export(
    db: Session,
    actor: "models.User",
    export_type: str,
    period_id: Optional[int] = None,
    record_count: Optional[int] = None,
    request=None,
) -> None:
    """Record an export action (PDF, Excel, QR sheet, etc.)."""
    from auth_utils import log_action
    new_values: dict[str, Any] = {"export_type": export_type}
    if period_id is not None:
        new_values["period_id"] = period_id
    if record_count is not None:
        new_values["record_count"] = record_count
    log_action(
        db,
        actor,
        "EXPORT",
        table_name="exports",
        new_values=new_values,
        request=request,
    )


def audit_event(
    db: Session,
    actor: "models.User",
    action: str,
    table_name: Optional[str] = None,
    record_id: Optional[int] = None,
    metadata: Optional[dict[str, Any]] = None,
    request=None,
) -> None:
    """Generic audit event for anything that doesn't fit mutation or export."""
    from auth_utils import log_action
    log_action(
        db,
        actor,
        action,
        table_name=table_name,
        record_id=record_id,
        new_values=metadata,
        request=request,
    )


def audit_login(
    db: Session,
    actor: "models.User",
    success: bool,
    request=None,
) -> None:
    """Record a login attempt."""
    from auth_utils import log_action
    log_action(
        db,
        actor,
        "LOGIN_SUCCESS" if success else "LOGIN_FAILURE",
        table_name="users",
        record_id=actor.id,
        request=request,
    )


def audit_permission_denied(
    db: Session,
    actor: "models.User",
    attempted_action: str,
    resource: Optional[str] = None,
    request=None,
) -> None:
    """Record a permission denial for security audit trail."""
    from auth_utils import log_action
    new_values: dict[str, Any] = {"attempted_action": attempted_action}
    if resource:
        new_values["resource"] = resource
    log_action(
        db,
        actor,
        "PERMISSION_DENIED",
        table_name=resource,
        new_values=new_values,
        request=request,
    )
