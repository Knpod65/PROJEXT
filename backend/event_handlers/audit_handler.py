"""Audit domain event handlers."""
from events.domain_event import DomainEvent
from events.audit_events import AuditEventType
from services.event_dispatcher_service import dispatcher


@dispatcher.on(AuditEventType.MUTATION_COMMITTED.value)
def on_mutation_committed(event: DomainEvent) -> None:
    pass


@dispatcher.on(AuditEventType.MUTATION_ROLLED_BACK.value)
def on_mutation_rolled_back(event: DomainEvent) -> None:
    pass


@dispatcher.on(AuditEventType.UNAUTHORIZED_ACCESS_ATTEMPT.value)
def on_unauthorized_access(event: DomainEvent) -> None:
    pass


@dispatcher.on(AuditEventType.SENSITIVE_ACCESS.value)
def on_sensitive_access(event: DomainEvent) -> None:
    pass


@dispatcher.on(AuditEventType.EXPORT_INITIATED.value)
def on_export_initiated(event: DomainEvent) -> None:
    pass
