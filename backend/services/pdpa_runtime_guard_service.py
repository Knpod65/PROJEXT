"""
PDPA Runtime Guard Service

Provides runtime validation for PII exposure prevention in responses.
Pure-dict validation with no ORM requirements.
"""
from __future__ import annotations

import os
from typing import Any


RESTRICTED_FIELDS = {
    "student_name",
    "full_name",
    "email",
    "phone",
    "address",
    "national_id",
    "passport_id",
    "religion",
    "birthdate",
    "blood_type",
}

CONFIDENTIAL_FIELDS = {
    "gpa",
    "grade",
    "advisor_notes",
    "financial_aid_amount",
    "scholarship_details",
}


def validate_analytics_not_exposing_pii(data: dict[str, Any]) -> bool:
    """Validate analytics payload does not contain restricted fields."""
    if not isinstance(data, dict):
        return True
    for key in RESTRICTED_FIELDS | CONFIDENTIAL_FIELDS:
        if key in data:
            return False
    return True


def validate_export_payload(data: dict[str, Any]) -> bool:
    """Validate export payload for safe fields only."""
    if not isinstance(data, dict):
        return True
    for key in RESTRICTED_FIELDS:
        if key in data:
            return False
    return True


def validate_config_for_secrets(data: dict[str, Any]) -> bool:
    """Validate config does not leak secrets."""
    if not isinstance(data, dict):
        return True
    secret_keys = {"secret", "password", "api_key", "token", "private_key"}
    for key in data:
        if any(sk in key.lower() for sk in secret_keys):
            if data.get(key):
                return False
    return True


def validate_trace_for_unsafe_fields(data: dict[str, Any]) -> bool:
    """Validate optimization trace has no unsafe fields."""
    return validate_analytics_not_exposing_pii(data)


def is_production_environment() -> bool:
    """Detect if running in production mode."""
    env = os.getenv("ENV", os.getenv("ENVIRONMENT", "")).lower()
    return env in {"prod", "production", "live"}


def assert_production_secrets() -> None:
    """Runtime assert that production secrets are configured correctly."""
    if is_production_environment():
        secret = os.getenv("SECRET_KEY", "")
        if not secret or len(secret) < 32 or secret == "dev-secret-key-change-me":
            raise RuntimeError("SECRET_KEY must be set to a random 32+ char string in production")