"""PDPA event safety policy.

Provides classification, assertion, and masking for event payloads.
Supports nested dict/list traversal and case-insensitive key matching.

Pure logic. No DB, no ORM, no HTTP.
"""
from __future__ import annotations

import copy
from typing import Any

# PII key names — case-insensitive match against key name.
_PII_KEYS: frozenset[str] = frozenset({
    "name",
    "student_name",
    "student_id",
    "citizen_id",
    "national_id",
    "email",
    "phone",
    "mobile",
    "address",
    "token",
    "qr",
    "qr_payload",
    "qr_code",
    "password",
    "secret",
})

# Operational PII keys (token/QR related) — personal context but operational
_OPERATIONAL_PII_KEYS: frozenset[str] = frozenset({
    "token", "qr", "qr_payload", "qr_code", "password", "secret",
})

# Personal data keys — directly identify a person
_PERSONAL_DATA_KEYS: frozenset[str] = frozenset({
    "name", "student_name", "email", "phone", "mobile", "address",
})

# Restricted keys — high-sensitivity identifiers
_RESTRICTED_KEYS: frozenset[str] = frozenset({
    "citizen_id", "national_id", "student_id",
})


def classify_event_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Inspect payload for PII keys (nested support). Does NOT mutate input.

    Returns:
        {
            "contains_pii": bool,
            "pii_keys": list[str],          # sorted list of found PII keys
            "recommended_classification": str,  # public|internal|confidential|restricted
            "masking_required": bool,
        }
    """
    found = _find_pii_keys(payload)
    contains_pii = bool(found)
    pii_keys = sorted(found)

    return {
        "contains_pii":               contains_pii,
        "pii_keys":                   pii_keys,
        "recommended_classification": _recommend_classification(found),
        "masking_required":           contains_pii,
    }


def assert_event_payload_safe(
    payload: dict[str, Any],
    *,
    strict: bool = False,
) -> None:
    """Assert the payload contains no PII keys.

    Args:
        payload: Event payload dict to inspect.
        strict:  If True, raise ValueError when PII is found.
                 If False (default), silently pass even if PII found.

    Raises:
        ValueError: When strict=True and PII keys are present.
    """
    if not strict:
        return
    found = _find_pii_keys(payload)
    if found:
        raise ValueError(
            f"Event payload contains PII keys that must be masked before dispatch: "
            f"{sorted(found)}"
        )


def mask_event_payload(
    payload: dict[str, Any],
    *,
    mask_value: str = "[REDACTED]",
) -> dict[str, Any]:
    """Return a deep copy of payload with all PII key values replaced.

    Processes nested dicts and lists of dicts recursively.
    Does NOT mutate the input.
    """
    return _mask_recursive(copy.deepcopy(payload), mask_value)


# ── Private helpers ───────────────────────────────────────────────────────────

def _find_pii_keys(obj: Any, found: set[str] | None = None) -> set[str]:
    """Recursively find all PII key names present in obj."""
    if found is None:
        found = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() in _PII_KEYS:
                found.add(key.lower())
            _find_pii_keys(value, found)
    elif isinstance(obj, list):
        for item in obj:
            _find_pii_keys(item, found)
    return found


def _mask_recursive(obj: Any, mask_value: str) -> Any:
    """Recursively replace PII key values with mask_value."""
    if isinstance(obj, dict):
        return {
            key: mask_value if key.lower() in _PII_KEYS else _mask_recursive(value, mask_value)
            for key, value in obj.items()
        }
    if isinstance(obj, list):
        return [_mask_recursive(item, mask_value) for item in obj]
    return obj


def _recommend_classification(found_keys: set[str]) -> str:
    """Derive recommended PDPA classification from the set of found PII keys."""
    if not found_keys:
        return "public"
    normalized = {k.lower() for k in found_keys}
    if normalized & {k.lower() for k in _RESTRICTED_KEYS}:
        return "restricted"
    if normalized & {k.lower() for k in _PERSONAL_DATA_KEYS}:
        return "confidential"
    return "internal"
