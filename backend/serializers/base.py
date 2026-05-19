"""
backend/serializers/base.py — pure serialization helpers.

All functions are:
- Pure (no side effects, no DB access, no auth)
- Safe (handle None gracefully)
- JSON-safe (output can be directly JSON serialized)
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional, TypeVar, Callable

T = TypeVar("T")


def serialize_datetime(value: Optional[datetime]) -> Optional[str]:
    """Convert datetime to ISO 8601 string or None."""
    if value is None:
        return None
    return value.isoformat()


def serialize_date(value: Optional[date]) -> Optional[str]:
    """Convert date to ISO string or None."""
    if value is None:
        return None
    return value.isoformat()


def serialize_enum(value: Optional[Enum]) -> Optional[str]:
    """Return .value of an Enum or None."""
    if value is None:
        return None
    return value.value


def serialize_decimal(value: Optional[Decimal], places: int = 2) -> Optional[float]:
    """Convert Decimal to float rounded to given places."""
    if value is None:
        return None
    return round(float(value), places)


def safe_getattr(obj: Any, attr: str, default: Any = None) -> Any:
    """Safely get attribute, return default if missing or None."""
    try:
        val = getattr(obj, attr, default)
        return val if val is not None else default
    except Exception:
        return default


def serialize_optional(value: Optional[T], transformer: Callable[[T], Any]) -> Any:
    """Apply transformer only if value is not None."""
    if value is None:
        return None
    return transformer(value)


def mask_sensitive_field(value: Optional[str], mask_char: str = "*") -> Optional[str]:
    """Mask a sensitive string (e.g. student_id, phone)."""
    if not value:
        return None
    if len(value) <= 4:
        return mask_char * len(value)
    return value[:2] + mask_char * (len(value) - 4) + value[-2:]


def serialize_collection(
    items: list[Any],
    transformer: Callable[[Any], dict[str, Any]]
) -> list[dict[str, Any]]:
    """Apply transformer to every item in a list."""
    return [transformer(item) for item in items]


def ensure_json_safe(value: Any) -> Any:
    """Recursively convert common non-JSON types to safe equivalents."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {k: ensure_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [ensure_json_safe(v) for v in value]
    return value
