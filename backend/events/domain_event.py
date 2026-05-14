"""Domain event envelope model.

DomainEvent is the canonical wire format for all EMS domain events.
It is immutable (frozen dataclass) and contains no PII by design.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class DomainEvent:
    event_id: str
    event_type: str
    domain: str
    actor_id: int | None
    session_id: str | None
    correlation_id: str | None
    payload: dict[str, Any]
    timestamp: str


def make_domain_event(
    event_type: str,
    domain: str,
    *,
    actor_id: int | None = None,
    session_id: str | None = None,
    correlation_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> DomainEvent:
    """Factory that stamps event_id and timestamp automatically."""
    return DomainEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        domain=domain,
        actor_id=actor_id,
        session_id=session_id,
        correlation_id=correlation_id,
        payload=payload or {},
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
