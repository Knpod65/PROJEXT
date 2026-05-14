"""Enterprise event envelope.

EventEnvelope is the canonical enterprise-grade event format. It extends
the concepts in DomainEvent with audit, PDPA, and traceability fields
required for enterprise event infrastructure.

DomainEvent (events/domain_event.py) remains unchanged as the existing
wire format. EventEnvelope is additive — new services use it; existing
services continue using DomainEvent.

Pure logic. No DB, no ORM, no HTTP.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# PII key names that must be redacted from event payloads.
# Matching is case-insensitive against the key name.
_PII_KEYS: frozenset[str] = frozenset({
    "student_name",
    "student_id",
    "citizen_id",
    "national_id",
    "email",
    "phone",
    "token",
    "qr_payload",
    "qr_code",
    "password",
    "secret",
})


@dataclass(frozen=True)
class EventEnvelope:
    """Canonical enterprise event envelope.

    All fields are immutable after creation. Use create_event_envelope()
    to build an instance — it auto-generates event_id and timestamp.
    """
    event_id: str
    event_type: str
    domain: str
    severity: str
    actor_id: int | None
    actor_role: str | None
    session_id: str | None
    correlation_id: str | None
    causation_id: str | None
    aggregate_type: str | None
    aggregate_id: str | None
    timestamp: str
    payload: dict[str, Any]
    metadata: dict[str, Any]
    pdpa_classification: str
    contains_pii: bool
    retention_hint: str | None
    schema_version: str


def create_event_envelope(
    event_type: str,
    domain: str,
    *,
    severity: str = "INFO",
    actor_id: int | None = None,
    actor_role: str | None = None,
    session_id: str | None = None,
    correlation_id: str | None = None,
    causation_id: str | None = None,
    aggregate_type: str | None = None,
    aggregate_id: str | None = None,
    payload: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    pdpa_classification: str = "internal",
    contains_pii: bool = False,
    retention_hint: str | None = None,
    schema_version: str = "1.0",
) -> EventEnvelope:
    """Factory that auto-generates event_id (UUID4) and timestamp (UTC ISO).

    payload and metadata are sanitized (PII keys replaced with [REDACTED])
    before being stored in the envelope.
    """
    return EventEnvelope(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        domain=domain,
        severity=severity,
        actor_id=actor_id,
        actor_role=actor_role,
        session_id=session_id,
        correlation_id=correlation_id,
        causation_id=causation_id,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        payload=sanitize_event_payload(payload or {}),
        metadata=sanitize_event_payload(metadata or {}),
        pdpa_classification=pdpa_classification,
        contains_pii=contains_pii,
        retention_hint=retention_hint,
        schema_version=schema_version,
    )


def event_envelope_to_dict(envelope: EventEnvelope) -> dict[str, Any]:
    """Serialize EventEnvelope to a JSON-safe dict (all fields included)."""
    return {
        "event_id":            envelope.event_id,
        "event_type":          envelope.event_type,
        "domain":              envelope.domain,
        "severity":            envelope.severity,
        "actor_id":            envelope.actor_id,
        "actor_role":          envelope.actor_role,
        "session_id":          envelope.session_id,
        "correlation_id":      envelope.correlation_id,
        "causation_id":        envelope.causation_id,
        "aggregate_type":      envelope.aggregate_type,
        "aggregate_id":        envelope.aggregate_id,
        "timestamp":           envelope.timestamp,
        "payload":             dict(envelope.payload),
        "metadata":            dict(envelope.metadata),
        "pdpa_classification": envelope.pdpa_classification,
        "contains_pii":        envelope.contains_pii,
        "retention_hint":      envelope.retention_hint,
        "schema_version":      envelope.schema_version,
    }


def sanitize_event_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow copy of payload with known PII keys redacted.

    Matching is case-insensitive against the key name. Does NOT mutate
    the input dict. Does NOT recurse into nested dicts — for deep
    sanitization use event_pdpa_policy.mask_event_payload().
    """
    result: dict[str, Any] = {}
    for key, value in payload.items():
        if key.lower() in _PII_KEYS:
            result[key] = "[REDACTED]"
        else:
            result[key] = value
    return result
