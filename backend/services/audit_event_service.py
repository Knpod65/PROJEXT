"""Coupled audit log + domain event emission.

When a mutation is recorded, this module writes the audit log entry via
audit_service AND emits the corresponding DomainEvent to the in-memory bus
(Phase 1B event_service). Both happen in the same function call so the
audit trail and the event stream stay consistent.

ADDITIVE ONLY — existing callers of audit_service.audit_mutation() are
unaffected. This service is opt-in for code that wants coupled behaviour.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy.orm import Session

if TYPE_CHECKING:
    import models


def record_mutation_with_event(
    db: Session,
    actor: "models.User",
    action: str,
    table_name: str,
    *,
    record_id: Optional[int] = None,
    old_values: Optional[dict[str, Any]] = None,
    new_values: Optional[dict[str, Any]] = None,
    request: Any = None,
    session_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> None:
    """Write an audit log entry and emit a matching DomainEvent.

    Step 1: audit_service.audit_mutation() — DB write (existing pattern).
    Step 2: event_service.emit() — in-memory event bus publish.

    If the DB write fails, the event is never emitted (correct ordering).
    If the event emit fails, the exception is swallowed so the DB write
    is not rolled back (event bus is best-effort in Phase 1B).
    """
    from services.audit_service import audit_mutation
    from services.event_service import emit

    audit_mutation(
        db,
        actor,
        action,
        table_name,
        record_id=record_id,
        old_values=old_values,
        new_values=new_values,
        request=request,
    )

    try:
        emit(
            action,
            domain="audit",
            actor_id=getattr(actor, "id", None),
            session_id=session_id,
            correlation_id=correlation_id,
            payload={
                "table_name": table_name,
                "record_id": record_id,
                "action": action,
            },
        )
    except Exception:
        pass  # event bus is best-effort; never roll back an audit write


def record_event_with_audit(
    db: Session,
    actor: "models.User",
    event_type: str,
    description: str,
    *,
    domain: str = "audit",
    session_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    payload: Optional[dict[str, Any]] = None,
) -> None:
    """Write a named audit event and emit a matching DomainEvent.

    Mirrors record_mutation_with_event() but for non-mutation audit events
    (logins, exports, custom events).
    """
    from services.audit_service import audit_event
    from services.event_service import emit

    audit_event(db, actor, event_type, description)

    try:
        emit(
            event_type,
            domain=domain,
            actor_id=getattr(actor, "id", None),
            session_id=session_id,
            correlation_id=correlation_id,
            payload=payload or {"description": description},
        )
    except Exception:
        pass
