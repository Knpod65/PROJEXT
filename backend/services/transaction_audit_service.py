"""Transaction audit coupling service.

Provides execute_with_audit() — a single call that:
1. Runs a mutation inside a DB transaction
2. Writes an audit row inside the SAME transaction (commit together)
3. Emits a domain event AFTER commit (best-effort, never crashes caller)

This prevents the bad states where:
- mutation succeeds but audit row fails silently
- audit row is written but business write rolls back

Usage:
    result = execute_with_audit(
        db,
        mutation_fn=lambda db: some_service.create_thing(db),
        actor=current_user,
        audit_action="THING_CREATED",
        audit_table_name="things",
        audit_record_id=new_thing.id,
        event_type="THING_CREATED",
        event_domain="governance",
        event_payload={"thing_id": new_thing.id},
    )

Initial integration targets (opt-in — existing callers unaffected):
- Optimization governance override actions
- Submission rollback
- Sensitive lock operations
"""
from __future__ import annotations

from typing import Any, Callable

from sqlalchemy.orm import Session


def execute_with_audit(
    db: Session,
    *,
    mutation_fn: Callable[[Session], Any],
    actor: Any,
    audit_action: str,
    audit_table_name: str,
    audit_record_id: int | None = None,
    audit_old_values: dict[str, Any] | None = None,
    audit_new_values: dict[str, Any] | None = None,
    event_type: str,
    event_domain: str,
    event_payload: dict[str, Any] | None = None,
    session_id: str | None = None,
    correlation_id: str | None = None,
    request: Any = None,
) -> Any:
    """Run mutation_fn(db) + audit write atomically; emit event post-commit.

    Transaction semantics:
    - mutation_fn and audit_mutation share one DB transaction
    - db.commit() is called only once, after both succeed
    - db.rollback() is called on any exception; exception re-raised
    - Domain event is emitted AFTER commit (best-effort; errors swallowed)

    Args:
        db:               SQLAlchemy Session (caller owns lifecycle)
        mutation_fn:      Business mutation — receives `db`, must NOT commit
        actor:            User object for the audit row
        audit_action:     Action string (e.g. "OVERRIDE_APPLIED")
        audit_table_name: Table being mutated (e.g. "schedule_sessions")
        audit_record_id:  PK of the mutated record (optional)
        audit_old_values: Pre-mutation snapshot (no PII)
        audit_new_values: Post-mutation snapshot (no PII)
        event_type:       Domain event type (from typed event enum)
        event_domain:     Event domain (e.g. "governance")
        event_payload:    Event payload (no PII)
        session_id:       User session correlation ID
        correlation_id:   Cross-service correlation ID
        request:          FastAPI Request for IP/UA capture (optional)

    Returns:
        The return value of mutation_fn(db).

    Raises:
        Re-raises any exception from mutation_fn or audit_mutation.
    """
    from services.audit_service import audit_mutation
    from services.event_service import emit

    try:
        result = mutation_fn(db)

        audit_mutation(
            db,
            actor,
            audit_action,
            table_name=audit_table_name,
            record_id=audit_record_id,
            old_values=audit_old_values,
            new_values=audit_new_values,
            request=request,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    # Post-commit: emit domain event (best-effort, never crashes caller)
    actor_id: int | None = getattr(actor, "id", None)
    try:
        emit(
            event_type,
            event_domain,
            actor_id=actor_id,
            session_id=session_id,
            correlation_id=correlation_id,
            payload=event_payload or {},
        )
    except Exception:
        pass

    return result


def execute_readonly_with_event(
    *,
    event_type: str,
    event_domain: str,
    actor_id: int | None = None,
    session_id: str | None = None,
    correlation_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    """Emit a domain event without any DB transaction.

    Use for read-only operations that still need to be observable (e.g.
    report exports, schedule views by auditors).
    """
    from services.event_service import emit
    try:
        emit(
            event_type,
            event_domain,
            actor_id=actor_id,
            session_id=session_id,
            correlation_id=correlation_id,
            payload=payload or {},
        )
    except Exception:
        pass
