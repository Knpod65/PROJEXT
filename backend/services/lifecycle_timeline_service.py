"""Lifecycle timeline reconstruction service.

Normalizes events from mixed sources (EventEnvelope dicts, DomainEvent
asdict output, governance trace events, etc.) into a uniform timeline.

Pure logic. No DB, no ORM, no HTTP.
"""
from __future__ import annotations

from typing import Any

# Severity levels in ascending order for highest-severity computation.
_SEVERITY_RANK: dict[str, int] = {
    "INFO":      0,
    "WARNING":   1,
    "HIGH_RISK": 2,
    "HARD_FAIL": 3,
    "CRITICAL":  4,
}
_DEFAULT_SEVERITY = "INFO"


def build_lifecycle_timeline(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize a list of events from any source into a uniform timeline.

    Accepts any dict-based event format: EventEnvelope dicts,
    DomainEvent asdict, governance trace events, etc. Field extraction
    uses ordered fallbacks to tolerate format differences.

    Returns events sorted by timestamp (None timestamps sorted to end).
    """
    timeline = [_normalize_event(e) for e in events]
    return sorted(timeline, key=lambda item: (item["timestamp"] is None, item["timestamp"] or ""))


def summarize_lifecycle_timeline(timeline: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute an aggregate summary from an already-built timeline.

    Args:
        timeline: Output of build_lifecycle_timeline() (normalized items).

    Returns:
        Dict with event_count, first/last event timestamps, boolean flags
        for rollback/override/publication events, and highest_severity.
    """
    if not timeline:
        return {
            "event_count":     0,
            "first_event_at":  None,
            "last_event_at":   None,
            "has_rollback":    False,
            "has_override":    False,
            "has_publication": False,
            "highest_severity": _DEFAULT_SEVERITY,
        }

    timestamped = [item["timestamp"] for item in timeline if item["timestamp"] is not None]
    event_types = [item["event_type"] for item in timeline]
    severities = [item["severity"] for item in timeline]

    return {
        "event_count":     len(timeline),
        "first_event_at":  min(timestamped) if timestamped else None,
        "last_event_at":   max(timestamped) if timestamped else None,
        "has_rollback":    any("ROLL" in et for et in event_types),
        "has_override":    any("OVERRIDE" in et for et in event_types),
        "has_publication": any("PUBLISH" in et for et in event_types),
        "highest_severity": _highest_severity(severities),
    }


# ── Private helpers ───────────────────────────────────────────────────────────

def _normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    """Extract timeline item fields with ordered fallbacks per field."""
    return {
        "timestamp":      event.get("timestamp"),
        "event_type":     event.get("event_type") or event.get("type") or "UNKNOWN",
        "domain":         event.get("domain") or "unknown",
        "actor_id":       event.get("actor_id") or event.get("actor"),
        "actor_role":     event.get("actor_role"),
        "summary":        (
            event.get("details")
            or event.get("description")
            or event.get("summary")
            or event.get("event_type")
            or event.get("type")
            or "UNKNOWN"
        ),
        "severity":       event.get("severity") or _DEFAULT_SEVERITY,
        "aggregate_type": event.get("aggregate_type"),
        "aggregate_id":   event.get("aggregate_id"),
    }


def _highest_severity(severities: list[str]) -> str:
    """Return the highest severity level found in the list."""
    if not severities:
        return _DEFAULT_SEVERITY
    return max(severities, key=lambda s: _SEVERITY_RANK.get(s, 0))
