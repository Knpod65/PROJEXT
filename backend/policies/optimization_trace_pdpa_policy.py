"""PDPA safety policy for optimization trace payloads."""
from __future__ import annotations

import copy
from typing import Any

_MASK_VALUE = "[REDACTED]"

_RESTRICTED_KEYS: frozenset[str] = frozenset({
    "student_id",
    "student_ids",
    "token",
    "qr",
    "qr_payload",
    "qr_code",
    "secret",
    "password",
})

_CONFIDENTIAL_KEYS: frozenset[str] = frozenset({
    "student_name",
    "student_names",
    "candidate_name",
    "full_name",
    "display_name",
    "email",
    "phone",
    "mobile",
    "attachment_path",
    "pdf_original_path",
    "pdf_stripped_path",
})

_ALL_SENSITIVE_KEYS: frozenset[str] = _RESTRICTED_KEYS | _CONFIDENTIAL_KEYS


def _is_masked(value: Any) -> bool:
    return value in (None, _MASK_VALUE)


def _classify_keys(keys: set[str]) -> str:
    if not keys:
        return "internal"
    normalized = {key.lower() for key in keys}
    if normalized & _RESTRICTED_KEYS:
        return "restricted"
    if normalized & _CONFIDENTIAL_KEYS:
        return "confidential"
    return "internal"


def _collect_trace_flags(obj: Any, *, raw: set[str], masked: set[str]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            normalized = str(key).lower()
            if normalized in _ALL_SENSITIVE_KEYS:
                if _is_masked(value):
                    masked.add(normalized)
                else:
                    raw.add(normalized)
            _collect_trace_flags(value, raw=raw, masked=masked)
    elif isinstance(obj, list):
        for item in obj:
            _collect_trace_flags(item, raw=raw, masked=masked)


def _mask_recursive(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            key: _MASK_VALUE if str(key).lower() in _ALL_SENSITIVE_KEYS else _mask_recursive(value)
            for key, value in obj.items()
        }
    if isinstance(obj, list):
        return [_mask_recursive(item) for item in obj]
    return obj


def classify_trace_event(event: dict[str, Any]) -> dict[str, Any]:
    """Classify one trace event for PDPA safety."""
    raw_keys: set[str] = set()
    masked_keys: set[str] = set()
    _collect_trace_flags(event, raw=raw_keys, masked=masked_keys)
    all_keys = raw_keys | masked_keys

    return {
        "contains_sensitive_data": bool(raw_keys),
        "sensitive_keys": sorted(raw_keys),
        "masked_keys": sorted(masked_keys),
        "recommended_classification": _classify_keys(all_keys),
        "safe": not raw_keys,
    }


def mask_trace_event(event: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy of event with sensitive trace fields redacted."""
    return _mask_recursive(copy.deepcopy(event))


def assert_trace_event_safe(event: dict[str, Any]) -> None:
    """Raise when a trace event still contains raw sensitive fields."""
    classification = classify_trace_event(event)
    if classification["contains_sensitive_data"]:
        raise ValueError(
            "Optimization trace event contains raw sensitive fields: "
            f"{classification['sensitive_keys']}"
        )


def classify_trace_batch(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify a batch of trace events for PDPA safety."""
    unsafe_keys: set[str] = set()
    masked_keys: set[str] = set()
    unsafe_event_count = 0

    for event in events:
        classification = classify_trace_event(event)
        if classification["contains_sensitive_data"]:
            unsafe_event_count += 1
            unsafe_keys.update(classification["sensitive_keys"])
        masked_keys.update(classification["masked_keys"])

    return {
        "total_events": len(events),
        "unsafe_event_count": unsafe_event_count,
        "safe_event_count": len(events) - unsafe_event_count,
        "sensitive_keys": sorted(unsafe_keys),
        "masked_keys": sorted(masked_keys),
        "recommended_classification": _classify_keys(unsafe_keys | masked_keys),
    }
