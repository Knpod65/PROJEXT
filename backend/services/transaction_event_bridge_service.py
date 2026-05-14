"""Transaction audit event bridge service.

Pure helper that composes EventEnvelope + immutable audit event + outbox record
into a single bundle. Does NOT change any existing service behavior — callers
can use the bundle to inspect, log, or stage events without modifying the
execute_with_audit() call chain.

Pure logic. No DB, no ORM, no HTTP.
"""
from __future__ import annotations

from typing import Any

from events.event_envelope import EventEnvelope, create_event_envelope
from services.event_outbox_service import build_outbox_record, stage_event
from services.immutable_audit_service import build_immutable_audit_event


def build_transaction_event_bundle(
    *,
    # Event envelope fields
    event_type: str,
    domain: str,
    actor_id: int | None = None,
    actor_role: str | None = None,
    session_id: str | None = None,
    correlation_id: str | None = None,
    causation_id: str | None = None,
    aggregate_type: str | None = None,
    aggregate_id: str | None = None,
    event_payload: dict[str, Any] | None = None,
    # Audit event fields
    audit_action: str,
    resource_type: str,
    resource_id: str | int | None = None,
    before_snapshot: dict[str, Any] | None = None,
    after_snapshot: dict[str, Any] | None = None,
    reason: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a structured event bundle from envelope + audit event + outbox record.

    Pure — no DB writes, no bus emission, no outbox staging. Callers
    decide whether to stage, dispatch, or discard the bundle.

    The mutation_event and audit_event share the same correlation_id
    to allow cross-linking in future analytics or audit logs.

    Returns:
        Dict with keys:
          - mutation_event: EventEnvelope
          - audit_event:    dict (build_immutable_audit_event result)
          - outbox_record:  dict (build_outbox_record result, status=STAGED)
    """
    mutation_event = create_event_envelope(
        event_type,
        domain,
        actor_id=actor_id,
        actor_role=actor_role,
        session_id=session_id,
        correlation_id=correlation_id,
        causation_id=causation_id,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload=event_payload or {},
    )

    audit_event = build_immutable_audit_event(
        action=audit_action,
        actor_id=actor_id,
        actor_role=actor_role,
        resource_type=resource_type,
        resource_id=resource_id,
        before_snapshot=before_snapshot,
        after_snapshot=after_snapshot,
        reason=reason,
        metadata=dict(metadata) if metadata else {"correlation_id": correlation_id},
    )

    outbox_record = build_outbox_record(mutation_event)

    return {
        "mutation_event": mutation_event,
        "audit_event":    audit_event,
        "outbox_record":  outbox_record,
    }


def stage_transaction_events(bundle: dict[str, Any]) -> dict[str, Any]:
    """Stage the mutation_event from the bundle to the in-memory outbox.

    Args:
        bundle: Dict returned by build_transaction_event_bundle().

    Returns:
        The outbox record that was staged.
    """
    mutation_event: EventEnvelope = bundle["mutation_event"]
    return stage_event(mutation_event)
