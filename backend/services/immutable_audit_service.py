"""Immutable audit event model.

Builds audit event payloads with hashed snapshots for tamper detection.
The `immutable: True` flag signals to callers and future storage layers
that this record must not be altered once written.

Pure logic. No DB, no ORM, no HTTP.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

# PII key names to sanitize from snapshots before hashing and storage.
# Defined independently from event_envelope to avoid circular imports.
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


def build_immutable_audit_event(
    *,
    action: str,
    actor_id: int | None,
    actor_role: str | None,
    resource_type: str,
    resource_id: str | int | None,
    before_snapshot: dict[str, Any] | None = None,
    after_snapshot: dict[str, Any] | None = None,
    reason: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an immutable audit event with hashed snapshots.

    Snapshots are sanitized (PII keys replaced) before hashing and
    storage. Input dicts are never mutated.

    Returns:
        Dict with audit_event_id, action, actor_id, actor_role,
        resource_type, resource_id, before_hash, after_hash,
        before_snapshot, after_snapshot, reason, metadata, timestamp,
        immutable, schema_version.
    """
    sanitized_before = _sanitize_snapshot(before_snapshot) if before_snapshot is not None else None
    sanitized_after = _sanitize_snapshot(after_snapshot) if after_snapshot is not None else None

    return {
        "audit_event_id":  str(uuid.uuid4()),
        "action":          action,
        "actor_id":        actor_id,
        "actor_role":      actor_role,
        "resource_type":   resource_type,
        "resource_id":     str(resource_id) if resource_id is not None else "unknown",
        "before_hash":     _hash_snapshot(sanitized_before) if sanitized_before is not None else None,
        "after_hash":      _hash_snapshot(sanitized_after) if sanitized_after is not None else None,
        "before_snapshot": sanitized_before,
        "after_snapshot":  sanitized_after,
        "reason":          reason,
        "metadata":        dict(metadata) if metadata else {},
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "immutable":       True,
        "schema_version":  "1.0",
    }


# ── Private helpers ───────────────────────────────────────────────────────────

def _sanitize_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow copy with known PII keys replaced by [REDACTED]."""
    return {
        key: "[REDACTED]" if key.lower() in _PII_KEYS else value
        for key, value in snapshot.items()
    }


def _hash_snapshot(snapshot: dict[str, Any]) -> str:
    """Return SHA-256 hex digest of the JSON-serialized snapshot.

    Serialization uses sort_keys=True for deterministic output.
    """
    canonical = json.dumps(snapshot, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
