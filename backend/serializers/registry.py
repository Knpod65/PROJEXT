"""
backend/serializers/registry.py — central registry of all serializers.

Allows services and routers to request a serializer by domain.
"""
from typing import Any, Callable, Dict

from serializers.base import (
    serialize_datetime,
    serialize_date,
    serialize_enum,
    serialize_decimal,
    safe_getattr,
    serialize_optional,
    mask_sensitive_field,
    serialize_collection,
    ensure_json_safe,
)

# Domain → serializer function registry
_SERIALIZERS: Dict[str, Callable] = {
    "datetime": serialize_datetime,
    "date": serialize_date,
    "enum": serialize_enum,
    "decimal": serialize_decimal,
    "safe_getattr": safe_getattr,
    "optional": serialize_optional,
    "mask": mask_sensitive_field,
    "collection": serialize_collection,
    "json_safe": ensure_json_safe,
}


def get_serializer(name: str) -> Callable:
    """Retrieve a serializer function by name."""
    if name not in _SERIALIZERS:
        raise KeyError(f"Serializer '{name}' not registered")
    return _SERIALIZERS[name]


def register_serializer(name: str, func: Callable) -> None:
    """Register a new serializer (for extension in tests or future modules)."""
    _SERIALIZERS[name] = func


def serialize(value: Any, serializer_name: str) -> Any:
    """Convenience wrapper."""
    return get_serializer(serializer_name)(value)
