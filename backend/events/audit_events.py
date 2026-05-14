"""Typed event type constants for the audit domain.

These enums define every event type that audit-related services emit
through the InMemoryEventBus. Use as the `event_type` argument to
`event_service.emit()` or `transaction_audit_service.execute_with_audit()`.

Source authority: this file owns the audit event type vocabulary.
"""
from __future__ import annotations

from enum import Enum

from events.base_event import EventDomain

AUDIT_DOMAIN = EventDomain.AUDIT.value


class AuditEventType(str, Enum):
    """All event types emitted in the audit domain."""

    # Transaction events
    MUTATION_COMMITTED = "MUTATION_COMMITTED"
    MUTATION_ROLLED_BACK = "MUTATION_ROLLED_BACK"

    # Access events
    SENSITIVE_ACCESS = "SENSITIVE_ACCESS"
    UNAUTHORIZED_ACCESS_ATTEMPT = "UNAUTHORIZED_ACCESS_ATTEMPT"

    # Document/export events
    EXPORT_INITIATED = "EXPORT_INITIATED"
    EXPORT_COMPLETED = "EXPORT_COMPLETED"

    # Token events
    TOKEN_ISSUED = "TOKEN_ISSUED"
    TOKEN_REVOKED = "TOKEN_REVOKED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"

    # Session events
    SESSION_STARTED = "SESSION_STARTED"
    SESSION_ENDED = "SESSION_ENDED"
    SESSION_EXPIRED = "SESSION_EXPIRED"

    # Retention events
    RETENTION_CLEANUP_INITIATED = "RETENTION_CLEANUP_INITIATED"
    RETENTION_CLEANUP_COMPLETED = "RETENTION_CLEANUP_COMPLETED"
