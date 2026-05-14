"""Pure helpers for replaying optimization trace events into decision lineage."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from services.optimization_trace_context import (
    TRACE_EVENT_CANDIDATE_ACCEPTED,
    TRACE_EVENT_CANDIDATE_GENERATED,
    TRACE_EVENT_CANDIDATE_REJECTED,
    TRACE_EVENT_CONSTRAINT_TRIGGERED,
    TRACE_EVENT_FINAL_SELECTION,
    TRACE_EVENT_PENALTY_APPLIED,
)

_SENSITIVE_KEYS: frozenset[str] = frozenset({
    "student_id",
    "student_ids",
    "student_name",
    "student_names",
    "candidate_name",
    "full_name",
    "email",
    "phone",
    "mobile",
    "token",
    "qr",
    "qr_payload",
    "qr_code",
})

_SEVERITY_ORDER: dict[str, int] = {
    "INFO": 0,
    "SUGGESTION": 1,
    "WARNING": 2,
    "HIGH_RISK": 3,
    "HARD_FAIL": 4,
}


def _sanitize_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _sanitize_metadata(item)
            for key, item in value.items()
            if str(key).lower() not in _SENSITIVE_KEYS
        }
    if isinstance(value, list):
        return [_sanitize_metadata(item) for item in value]
    return value


def _iso_key(value: str | None) -> tuple[int, str]:
    if not value:
        return (1, "")
    try:
        return (0, datetime.fromisoformat(value).isoformat())
    except ValueError:
        return (1, value)


def _normalize_trace_event(event: dict[str, Any]) -> dict[str, Any]:
    """Normalize either a trace event dict or an EventEnvelope dict."""
    if not isinstance(event, dict):
        return {}

    payload = event.get("payload") if isinstance(event.get("payload"), dict) else None
    metadata = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}

    if payload is not None and "event_type" in event:
        normalized = {
            "trace_event_id": payload.get("trace_event_id") or metadata.get("trace_event_id") or event.get("event_id"),
            "trace_id": payload.get("trace_id") or metadata.get("trace_id") or event.get("correlation_id"),
            "session_id": event.get("session_id"),
            "event_type": event.get("event_type"),
            "stage": payload.get("stage") or metadata.get("stage"),
            "entity_type": payload.get("entity_type") or event.get("aggregate_type"),
            "entity_id": payload.get("entity_id") or event.get("aggregate_id"),
            "candidate_type": payload.get("candidate_type") or metadata.get("candidate_type"),
            "candidate_id": payload.get("candidate_id"),
            "constraint_code": payload.get("constraint_code"),
            "reason_code": payload.get("reason_code"),
            "severity": event.get("severity"),
            "score_delta": payload.get("score_delta"),
            "source": metadata.get("source") or payload.get("source"),
            "message": payload.get("message"),
            "metadata": _sanitize_metadata(payload.get("metadata") or {}),
            "timestamp": payload.get("timestamp") or event.get("timestamp"),
        }
        return normalized

    normalized = {
        "trace_event_id": event.get("trace_event_id"),
        "trace_id": event.get("trace_id"),
        "session_id": event.get("session_id"),
        "event_type": event.get("event_type"),
        "stage": event.get("stage"),
        "entity_type": event.get("entity_type"),
        "entity_id": event.get("entity_id"),
        "candidate_type": event.get("candidate_type"),
        "candidate_id": event.get("candidate_id"),
        "constraint_code": event.get("constraint_code"),
        "reason_code": event.get("reason_code"),
        "severity": event.get("severity"),
        "score_delta": event.get("score_delta"),
        "source": event.get("source"),
        "message": event.get("message"),
        "metadata": _sanitize_metadata(event.get("metadata") or {}),
        "timestamp": event.get("timestamp"),
    }
    return normalized


def build_trace_timeline(trace_events) -> list[dict[str, Any]]:
    """Return normalized trace events sorted by timestamp."""
    normalized = [
        _normalize_trace_event(event)
        for event in trace_events or []
        if isinstance(event, dict)
    ]
    normalized = [event for event in normalized if event.get("event_type")]
    return sorted(normalized, key=lambda event: (_iso_key(event.get("timestamp")), str(event.get("trace_event_id") or "")))


def group_trace_events_by_entity(trace_events) -> dict[str, list[dict[str, Any]]]:
    """Group normalized events by entity_type/entity_id pair."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for event in build_trace_timeline(trace_events):
        entity_type = event.get("entity_type") or "unknown"
        entity_id = event.get("entity_id")
        key = f"{entity_type}:{entity_id}"
        grouped.setdefault(key, []).append(event)
    return grouped


def find_rejected_alternatives(trace_events, entity_id=None) -> list[dict[str, Any]]:
    """Return rejected candidate events, optionally scoped to one entity id."""
    rejected = []
    for event in build_trace_timeline(trace_events):
        if event.get("event_type") != TRACE_EVENT_CANDIDATE_REJECTED:
            continue
        if entity_id is not None and event.get("entity_id") != entity_id:
            continue
        rejected.append(event)
    return rejected


def summarize_decision_lineage(trace_events) -> dict[str, Any]:
    """Summarize key counts and severity/source distribution for a trace stream."""
    timeline = build_trace_timeline(trace_events)
    source_breakdown: dict[str, int] = {}
    highest_severity = None

    for event in timeline:
        source = str(event.get("source") or "UNKNOWN")
        source_breakdown[source] = source_breakdown.get(source, 0) + 1
        severity = str(event.get("severity") or "INFO")
        if highest_severity is None or _SEVERITY_ORDER.get(severity, 0) > _SEVERITY_ORDER.get(highest_severity, 0):
            highest_severity = severity

    candidate_generated_count = sum(1 for event in timeline if event.get("event_type") == TRACE_EVENT_CANDIDATE_GENERATED)
    candidate_rejected_count = sum(1 for event in timeline if event.get("event_type") == TRACE_EVENT_CANDIDATE_REJECTED)
    candidate_accepted_count = sum(1 for event in timeline if event.get("event_type") == TRACE_EVENT_CANDIDATE_ACCEPTED)
    constraint_triggered_count = sum(1 for event in timeline if event.get("event_type") == TRACE_EVENT_CONSTRAINT_TRIGGERED)
    penalty_count = sum(1 for event in timeline if event.get("event_type") == TRACE_EVENT_PENALTY_APPLIED)
    selection_count = sum(
        1
        for event in timeline
        if event.get("event_type") in {TRACE_EVENT_CANDIDATE_ACCEPTED, TRACE_EVENT_FINAL_SELECTION}
    )

    return {
        "candidate_generated_count": candidate_generated_count,
        "candidate_rejected_count": candidate_rejected_count,
        "candidate_accepted_count": candidate_accepted_count,
        "constraint_triggered_count": constraint_triggered_count,
        "penalty_count": penalty_count,
        "selection_count": selection_count,
        "highest_severity": highest_severity,
        "trace_source_breakdown": source_breakdown,
    }


def build_decision_lineage(trace_events) -> dict[str, Any]:
    """Build entity-centric decision lineage from trace events."""
    grouped = group_trace_events_by_entity(trace_events)
    lineage = []

    for entity_key, events in grouped.items():
        final_selection = next(
            (event for event in reversed(events) if event.get("event_type") == TRACE_EVENT_FINAL_SELECTION),
            None,
        )
        lineage.append({
            "entity_key": entity_key,
            "entity_type": events[0].get("entity_type"),
            "entity_id": events[0].get("entity_id"),
            "events": events,
            "rejected_alternatives": [event for event in events if event.get("event_type") == TRACE_EVENT_CANDIDATE_REJECTED],
            "final_selection": final_selection,
        })

    lineage.sort(key=lambda item: str(item.get("entity_key") or ""))
    return {
        "lineage": lineage,
        "summary": summarize_decision_lineage(trace_events),
    }
