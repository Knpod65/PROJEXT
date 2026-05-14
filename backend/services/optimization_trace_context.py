"""In-memory native trace collector for optimization decisions.

This collector is additive and side-effect free. It captures native trace
events as plain dicts, keeps them JSON-safe, and can project them into
EventEnvelope objects for downstream audit/outbox workflows when needed.
"""
from __future__ import annotations

import copy
import json
import uuid
from datetime import date, datetime, time, timezone
from enum import Enum
from typing import Any

from events.event_envelope import EventEnvelope, create_event_envelope
from events.optimization_events import (
    OPTIMIZATION_DOMAIN,
    STAGE_CANDIDATE_GENERATION,
    STAGE_CONSTRAINT_EVALUATION,
    STAGE_SCORING,
    STAGE_SELECTION,
)
from policies.event_pdpa_policy import classify_event_payload, mask_event_payload

TRACE_EVENT_CANDIDATE_GENERATED = "CANDIDATE_GENERATED"
TRACE_EVENT_CANDIDATE_REJECTED = "CANDIDATE_REJECTED"
TRACE_EVENT_CANDIDATE_ACCEPTED = "CANDIDATE_ACCEPTED"
TRACE_EVENT_CONSTRAINT_TRIGGERED = "CONSTRAINT_TRIGGERED"
TRACE_EVENT_PENALTY_APPLIED = "PENALTY_APPLIED"
TRACE_EVENT_TRADEOFF_CHOSEN = "TRADEOFF_CHOSEN"
TRACE_EVENT_FINAL_SELECTION = "FINAL_SELECTION_ACCEPTED"

TRACE_SOURCE_SOLVER = "SOLVER_TRACE"
TRACE_SOURCE_POLICY = "POLICY_RULE"
TRACE_SOURCE_INPUT = "INPUT_CONSTRAINT"
TRACE_SOURCE_POST_HOC = "POST_HOC_TRACE"
TRACE_SOURCE_FALLBACK = "FALLBACK_HEURISTIC"

ALLOWED_TRACE_SOURCES: frozenset[str] = frozenset({
    TRACE_SOURCE_SOLVER,
    TRACE_SOURCE_POLICY,
    TRACE_SOURCE_INPUT,
    TRACE_SOURCE_POST_HOC,
    TRACE_SOURCE_FALLBACK,
})

_TRACE_SENSITIVE_KEYS: frozenset[str] = frozenset({
    "student_id",
    "student_ids",
    "student_name",
    "student_names",
    "candidate_name",
    "full_name",
    "display_name",
    "email",
    "phone",
    "mobile",
    "token",
    "qr",
    "qr_payload",
    "qr_code",
    "password",
    "secret",
    "attachment_path",
    "pdf_original_path",
})


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


def _json_safe(value: Any) -> Any:
    """Return a deterministic, JSON-safe representation of value."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, (date, time)):
        return value.isoformat()
    if isinstance(value, Enum):
        return _json_safe(value.value)
    if isinstance(value, dict):
        return {
            str(key): _json_safe(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, set):
        normalized = [_json_safe(item) for item in value]
        return sorted(normalized, key=lambda item: json.dumps(item, sort_keys=True, default=str))
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "__dict__"):
        return _json_safe(vars(value))
    return str(value)


def _mask_trace_payload(obj: Any, *, mask_value: str = "[REDACTED]") -> Any:
    """Recursively redact trace-specific sensitive keys from payload fragments."""
    if isinstance(obj, dict):
        return {
            key: mask_value if str(key).lower() in _TRACE_SENSITIVE_KEYS else _mask_trace_payload(value, mask_value=mask_value)
            for key, value in obj.items()
        }
    if isinstance(obj, list):
        return [_mask_trace_payload(item, mask_value=mask_value) for item in obj]
    return obj


def _sanitize_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    safe_metadata = _json_safe(metadata or {})
    if not isinstance(safe_metadata, dict):
        safe_metadata = {"value": safe_metadata}
    masked = mask_event_payload(copy.deepcopy(safe_metadata))
    trace_masked = _mask_trace_payload(masked)
    if not isinstance(trace_masked, dict):
        return {"value": trace_masked}
    return trace_masked


class OptimizationTraceContext:
    """Collect native optimization trace events in memory."""

    def __init__(
        self,
        *,
        session_id: str | None = None,
        trace_id: str | None = None,
    ) -> None:
        self.trace_id = trace_id or _new_id()
        self.session_id = session_id
        self.events: list[dict[str, Any]] = []

    def add_event(
        self,
        *,
        event_type: str,
        stage: str,
        entity_type: str | None = None,
        entity_id: Any = None,
        candidate_type: str | None = None,
        candidate_id: Any = None,
        constraint_code: str | None = None,
        reason_code: str | None = None,
        severity: str = "INFO",
        score_delta: float | int | None = None,
        source: str = TRACE_SOURCE_SOLVER,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
        timestamp: str | None = None,
    ) -> dict[str, Any]:
        if source not in ALLOWED_TRACE_SOURCES:
            allowed = ", ".join(sorted(ALLOWED_TRACE_SOURCES))
            raise ValueError(f"Unsupported trace source '{source}'. Allowed sources: {allowed}")

        event = {
            "trace_event_id": _new_id(),
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "event_type": str(event_type),
            "stage": str(stage),
            "entity_type": entity_type,
            "entity_id": _json_safe(entity_id),
            "candidate_type": candidate_type,
            "candidate_id": _json_safe(candidate_id),
            "constraint_code": constraint_code,
            "reason_code": reason_code,
            "severity": str(severity),
            "score_delta": float(score_delta) if score_delta is not None else None,
            "source": source,
            "message": str(message) if message is not None else None,
            "metadata": _sanitize_metadata(metadata),
            "timestamp": timestamp or _now_iso(),
        }
        self.events.append(event)
        return dict(event)

    def add_candidate_generated(self, **kwargs: Any) -> dict[str, Any]:
        return self.add_event(
            event_type=TRACE_EVENT_CANDIDATE_GENERATED,
            stage=kwargs.pop("stage", STAGE_CANDIDATE_GENERATION),
            source=kwargs.pop("source", TRACE_SOURCE_SOLVER),
            **kwargs,
        )

    def add_candidate_rejected(self, **kwargs: Any) -> dict[str, Any]:
        return self.add_event(
            event_type=TRACE_EVENT_CANDIDATE_REJECTED,
            stage=kwargs.pop("stage", STAGE_CONSTRAINT_EVALUATION),
            source=kwargs.pop("source", TRACE_SOURCE_SOLVER),
            severity=kwargs.pop("severity", "WARNING"),
            **kwargs,
        )

    def add_candidate_accepted(self, **kwargs: Any) -> dict[str, Any]:
        return self.add_event(
            event_type=TRACE_EVENT_CANDIDATE_ACCEPTED,
            stage=kwargs.pop("stage", STAGE_SELECTION),
            source=kwargs.pop("source", TRACE_SOURCE_SOLVER),
            **kwargs,
        )

    def add_constraint_triggered(self, **kwargs: Any) -> dict[str, Any]:
        return self.add_event(
            event_type=TRACE_EVENT_CONSTRAINT_TRIGGERED,
            stage=kwargs.pop("stage", STAGE_CONSTRAINT_EVALUATION),
            source=kwargs.pop("source", TRACE_SOURCE_INPUT),
            severity=kwargs.pop("severity", "INFO"),
            **kwargs,
        )

    def add_penalty_applied(self, **kwargs: Any) -> dict[str, Any]:
        return self.add_event(
            event_type=TRACE_EVENT_PENALTY_APPLIED,
            stage=kwargs.pop("stage", STAGE_SCORING),
            source=kwargs.pop("source", TRACE_SOURCE_SOLVER),
            severity=kwargs.pop("severity", "INFO"),
            **kwargs,
        )

    def add_tradeoff_chosen(self, **kwargs: Any) -> dict[str, Any]:
        return self.add_event(
            event_type=TRACE_EVENT_TRADEOFF_CHOSEN,
            stage=kwargs.pop("stage", STAGE_SELECTION),
            source=kwargs.pop("source", TRACE_SOURCE_SOLVER),
            severity=kwargs.pop("severity", "INFO"),
            **kwargs,
        )

    def add_final_selection(self, **kwargs: Any) -> dict[str, Any]:
        return self.add_event(
            event_type=TRACE_EVENT_FINAL_SELECTION,
            stage=kwargs.pop("stage", STAGE_SELECTION),
            source=kwargs.pop("source", TRACE_SOURCE_SOLVER),
            severity=kwargs.pop("severity", "INFO"),
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "event_count": len(self.events),
            "events": [dict(event) for event in self.events],
        }

    def to_event_envelopes(self) -> list[EventEnvelope]:
        envelopes: list[EventEnvelope] = []
        for event in self.events:
            payload = {
                "trace_event_id": event["trace_event_id"],
                "trace_id": event["trace_id"],
                "stage": event["stage"],
                "entity_type": event["entity_type"],
                "entity_id": event["entity_id"],
                "candidate_type": event["candidate_type"],
                "candidate_id": event["candidate_id"],
                "constraint_code": event["constraint_code"],
                "reason_code": event["reason_code"],
                "score_delta": event["score_delta"],
                "message": event["message"],
                "metadata": event["metadata"],
                "timestamp": event["timestamp"],
            }
            classification = classify_event_payload(payload)
            envelopes.append(
                create_event_envelope(
                    event["event_type"],
                    OPTIMIZATION_DOMAIN,
                    severity=event["severity"],
                    session_id=self.session_id,
                    correlation_id=self.trace_id,
                    causation_id=event["trace_event_id"],
                    aggregate_type=event["entity_type"],
                    aggregate_id=str(event["entity_id"]) if event["entity_id"] is not None else None,
                    payload=payload,
                    metadata={
                        "trace_id": self.trace_id,
                        "trace_event_id": event["trace_event_id"],
                        "stage": event["stage"],
                        "source": event["source"],
                        "candidate_type": event["candidate_type"],
                    },
                    pdpa_classification=str(classification.get("recommended_classification", "internal")),
                    contains_pii=bool(classification.get("contains_pii", False)),
                    retention_hint="optimization_trace",
                )
            )
        return envelopes
