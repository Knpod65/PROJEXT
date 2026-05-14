"""Base event protocol and shared domain/severity enums.

Defines the common vocabulary shared across all domain event modules.
The `DomainEvent` frozen dataclass (in domain_event.py) conforms to
`BaseEventProtocol` — any code that receives typed events can type-hint
against the protocol instead of the concrete class.

Also provides `EventDomain` and `EventSeverity` enums used as values
for `domain` and payload severity fields across governance_events.py,
audit_events.py, and optimization_events.py.
"""
from __future__ import annotations

from enum import Enum
from typing import Any


class EventDomain(str, Enum):
    """Canonical domain identifiers for the event bus."""

    OPTIMIZATION = "optimization"
    GOVERNANCE = "governance"
    AUDIT = "audit"
    WORKFLOW = "workflow"
    SUBMISSION = "submission"
    SYSTEM = "system"


class EventSeverity(str, Enum):
    """Severity levels that can appear in event payloads."""

    INFO = "INFO"
    WARNING = "WARNING"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"


class BaseEventProtocol:
    """Structural protocol satisfied by DomainEvent and any typed event.

    Concrete classes do NOT need to inherit from this — it is used only
    for documentation and isinstance/type-hint purposes. `DomainEvent`
    already has all these fields.
    """
    event_id: str
    event_type: str
    domain: str
    actor_id: int | None
    session_id: str | None
    correlation_id: str | None
    payload: dict[str, Any]
    timestamp: str
