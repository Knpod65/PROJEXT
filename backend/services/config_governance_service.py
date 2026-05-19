"""Config governance service — immutable audit log for platform config changes.

All functions are pure (no DB, no HTTP). Module-level in-memory store,
thread-safe via threading.Lock. clear_config_history() for test isolation.
"""
from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class ConfigChangeRecord:
    record_id: str
    actor_id: int | None
    actor_role: str | None
    action: str           # "CREATE"|"UPDATE"|"DELETE"|"IMPORT"
    config_type: str
    faculty_id: int | None
    before_snapshot: dict[str, Any] | None
    after_snapshot: dict[str, Any] | None
    reason: str | None
    timestamp: str        # UTC ISO
    validation_report: dict[str, Any] | None


_lock = threading.Lock()
_history: list[ConfigChangeRecord] = []


def record_config_change(
    *,
    actor_id: int | None = None,
    actor_role: str | None = None,
    action: str,
    config_type: str,
    faculty_id: int | None = None,
    before_snapshot: dict[str, Any] | None = None,
    after_snapshot: dict[str, Any] | None = None,
    reason: str | None = None,
    validation_report: dict[str, Any] | None = None,
) -> ConfigChangeRecord:
    record = ConfigChangeRecord(
        record_id=str(uuid.uuid4()),
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        config_type=config_type,
        faculty_id=faculty_id,
        before_snapshot=dict(before_snapshot) if before_snapshot is not None else None,
        after_snapshot=dict(after_snapshot) if after_snapshot is not None else None,
        reason=reason,
        timestamp=datetime.now(timezone.utc).isoformat(),
        validation_report=dict(validation_report) if validation_report is not None else None,
    )
    with _lock:
        _history.append(record)
    return record


def get_config_history(
    config_type: str | None = None,
    faculty_id: int | None = None,
) -> list[ConfigChangeRecord]:
    """Return change records filtered by config_type and/or faculty_id, descending by timestamp."""
    with _lock:
        records = list(_history)

    if config_type is not None:
        records = [r for r in records if r.config_type == config_type]
    if faculty_id is not None:
        records = [r for r in records if r.faculty_id == faculty_id]

    return sorted(records, key=lambda r: r.timestamp, reverse=True)


def get_recent_changes(limit: int = 20) -> list[ConfigChangeRecord]:
    """Return the N most recent change records, descending by timestamp."""
    with _lock:
        records = list(_history)
    return sorted(records, key=lambda r: r.timestamp, reverse=True)[:limit]


def clear_config_history() -> None:
    """Reset audit log. Use in tests for isolation."""
    with _lock:
        _history.clear()
