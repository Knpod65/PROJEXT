"""Event outbox service.

In-memory implementation of the transactional outbox pattern.
Provides staging, dispatch tracking, and query over a thread-safe
in-memory list. No DB writes — the outbox record shape documents
the future persistent outbox table schema.

Pure logic. No DB, no ORM, no HTTP.

Future DB outbox table (when approved by DBA):
    CREATE TABLE event_outbox (
        event_id       VARCHAR(36) PRIMARY KEY,
        event_type     VARCHAR(128) NOT NULL,
        domain         VARCHAR(64)  NOT NULL,
        aggregate_type VARCHAR(128),
        aggregate_id   VARCHAR(128),
        payload_json   TEXT         NOT NULL,
        metadata_json  TEXT         NOT NULL,
        status         VARCHAR(16)  NOT NULL DEFAULT 'STAGED',
        created_at     TIMESTAMPTZ  NOT NULL,
        dispatched_at  TIMESTAMPTZ
    );
"""
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from typing import Any

from events.event_envelope import EventEnvelope

# ── Outbox status constants ───────────────────────────────────────────────────

STATUS_STAGED = "STAGED"
STATUS_DISPATCHED = "DISPATCHED"
STATUS_FAILED = "FAILED"

# ── Module-level singleton ────────────────────────────────────────────────────

_outbox: list[dict[str, Any]] = []
_lock = threading.Lock()


# ── Public API ────────────────────────────────────────────────────────────────

def build_outbox_record(envelope: EventEnvelope) -> dict[str, Any]:
    """Serialize an EventEnvelope into an outbox record dict.

    Raises:
        ValueError: If payload or metadata are not JSON-serializable.
    """
    try:
        payload_json = json.dumps(envelope.payload, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Envelope payload is not JSON-serializable: {exc}") from exc

    try:
        metadata_json = json.dumps(envelope.metadata, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Envelope metadata is not JSON-serializable: {exc}") from exc

    return {
        "event_id":      envelope.event_id,
        "event_type":    envelope.event_type,
        "domain":        envelope.domain,
        "aggregate_type": envelope.aggregate_type,
        "aggregate_id":  envelope.aggregate_id,
        "payload_json":  payload_json,
        "metadata_json": metadata_json,
        "status":        STATUS_STAGED,
        "created_at":    datetime.now(timezone.utc).isoformat(),
        "dispatched_at": None,
    }


def stage_event(envelope: EventEnvelope) -> dict[str, Any]:
    """Build an outbox record from envelope and add it to the staging list.

    Returns the outbox record. The record stored internally is a copy;
    mutations of the returned dict do not affect the staged record.
    """
    record = build_outbox_record(envelope)
    with _lock:
        _outbox.append(dict(record))
    return record


def list_staged_events() -> list[dict[str, Any]]:
    """Return a shallow copy of all staged outbox records."""
    with _lock:
        return [dict(r) for r in _outbox]


def clear_staged_events() -> None:
    """Remove all records from the staging list."""
    with _lock:
        _outbox.clear()


def mark_event_dispatched(event_id: str) -> bool:
    """Set status=DISPATCHED and dispatched_at=now for the given event_id.

    Returns:
        True if the record was found and updated, False if not found.
    """
    dispatched_at = datetime.now(timezone.utc).isoformat()
    with _lock:
        for record in _outbox:
            if record["event_id"] == event_id:
                record["status"] = STATUS_DISPATCHED
                record["dispatched_at"] = dispatched_at
                return True
    return False


def get_staged_event(event_id: str) -> dict[str, Any] | None:
    """Return the outbox record for event_id, or None if not found."""
    with _lock:
        for record in _outbox:
            if record["event_id"] == event_id:
                return dict(record)
    return None
