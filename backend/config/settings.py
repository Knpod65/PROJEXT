"""
settings.py — Canonical typed configuration for EMS.

All runtime configuration lives here. Values are read from environment variables
at import time via the module-level `settings` singleton. The `get_settings()`
function is FastAPI Depends-compatible for future DI wiring.

Existing code continues to import from config.policy (which now re-exports
from this module), so no migration of call sites is required.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from zoneinfo import ZoneInfo


def _csv_tuple(env_name: str, default: str) -> tuple[str, ...]:
    value = os.getenv(env_name, default)
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    # --- Authentication ---
    token_expire_hours: int = field(
        default_factory=lambda: int(os.getenv("TOKEN_EXPIRE_HOURS", "12"))
    )

    # --- Rate limiting ---
    login_rate_max: int = field(
        default_factory=lambda: int(os.getenv("LOGIN_RATE_MAX", "10"))
    )
    login_rate_window: int = field(
        default_factory=lambda: int(os.getenv("LOGIN_RATE_WINDOW", "300"))
    )

    # --- CORS ---
    allowed_origins: tuple[str, ...] = field(
        default_factory=lambda: _csv_tuple(
            "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000"
        )
    )

    # --- Print priority thresholds ---
    print_priority_high_threshold: int = field(
        default_factory=lambda: int(os.getenv("PRINT_PRIORITY_HIGH_THRESHOLD", "120"))
    )
    print_priority_medium_threshold: int = field(
        default_factory=lambda: int(os.getenv("PRINT_PRIORITY_MEDIUM_THRESHOLD", "70"))
    )
    print_priority_normal_threshold: int = field(
        default_factory=lambda: int(os.getenv("PRINT_PRIORITY_NORMAL_THRESHOLD", "15"))
    )

    # --- QR and timing ---
    pickup_qr_open_minutes_before: int = field(
        default_factory=lambda: int(os.getenv("PICKUP_QR_OPEN_MINUTES_BEFORE", "120"))
    )
    ems_local_timezone: ZoneInfo = field(
        default_factory=lambda: ZoneInfo(os.getenv("EMS_LOCAL_TIMEZONE", "Asia/Bangkok"))
    )
    qr_pickup_prefix: str = "EMS-PICKUP:"
    qr_regulation_prefix: str = "EMS-REGULATION:"
    pdf_token_expire_hours: int = field(
        default_factory=lambda: int(os.getenv("PDF_TOKEN_EXPIRE_HOURS", "1"))
    )
    printshop_token_expire_hours: int = field(
        default_factory=lambda: int(os.getenv("PRINTSHOP_TOKEN_HOURS", "72"))
    )
    submission_access_token_expire_hours: int = field(
        default_factory=lambda: int(os.getenv("SUBMISSION_ACCESS_TOKEN_HOURS", "2"))
    )
    workflow_lock_ttl_seconds: int = field(
        default_factory=lambda: int(os.getenv("WORKFLOW_LOCK_TTL_SECONDS", "300"))
    )

    # --- Workflow signing order (override via comma-separated env var) ---
    sign_order_usernames: tuple[str, ...] = field(
        default_factory=lambda: _csv_tuple(
            "SIGN_ORDER_USERNAMES",
            "atikant.s,mathawee.m,napaporn.ph,paweena.t",
        )
    )

    # --- Paper distribution exclusions (per-faculty; Phase 6 will DB-back these) ---
    paper_distribution_division: str = field(
        default_factory=lambda: os.getenv(
            "PAPER_DISTRIBUTION_DIVISION", "Education_Student_Quality"
        )
    )
    paper_distribution_excluded_usernames: frozenset[str] = field(
        default_factory=lambda: frozenset(
            _csv_tuple("PAPER_DISTRIBUTION_EXCLUDED_USERNAMES", "araya.fa,sapanyu.wong")
        )
    )
    paper_distribution_excluded_name_snippets: tuple[str, ...] = field(
        default_factory=lambda: _csv_tuple(
            "PAPER_DISTRIBUTION_EXCLUDED_NAME_SNIPPETS", "อารยา,สัพพัญญู"
        )
    )

    # --- Feature flags ---
    multi_faculty_enabled: bool = field(
        default_factory=lambda: os.getenv("MULTI_FACULTY_ENABLED", "false").lower() == "true"
    )
    retention_cleanup_enabled: bool = field(
        default_factory=lambda: os.getenv("RETENTION_CLEANUP_ENABLED", "false").lower() == "true"
    )

    # --- Security ---
    secret_key: str = field(default_factory=lambda: _get_secret_key())


def _get_secret_key() -> str:
    """Enforce strong SECRET_KEY in production, allow dev fallback with warning."""
    key = os.getenv("SECRET_KEY", "").strip()
    env = os.getenv("ENVIRONMENT", "development").lower()

    if env == "production":
        if not key:
            raise RuntimeError("SECRET_KEY must be set in production environment")
        if len(key) < 50:
            raise RuntimeError("SECRET_KEY must be at least 50 characters in production")
        return key

    # Non-production
    if not key:
        import warnings
        warnings.warn(
            "SECRET_KEY not set — using insecure development fallback. "
            "Never use this in production.",
            stacklevel=2
        )
        return "ems_dev_only_DO_NOT_USE_IN_PRODUCTION_2025_change_me_very_insecure"

    return key


# Module-level singleton — instantiated once at import time.
settings: Settings = Settings()


def get_settings() -> Settings:
    """FastAPI Depends-compatible getter. Returns the module-level singleton."""
    return settings
