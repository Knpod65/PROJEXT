"""
policy.py — Flat module-level constant re-exports from config.settings.

All existing `from config.policy import X` statements continue to work unchanged.
The canonical source of truth is now config.settings.Settings.
"""
from __future__ import annotations

from config.settings import settings

TOKEN_EXPIRE_HOURS = settings.token_expire_hours
LOGIN_RATE_MAX = settings.login_rate_max
LOGIN_RATE_WINDOW = settings.login_rate_window
ALLOWED_ORIGINS: list[str] = list(settings.allowed_origins)

PRINT_PRIORITY_HIGH_THRESHOLD = settings.print_priority_high_threshold
PRINT_PRIORITY_MEDIUM_THRESHOLD = settings.print_priority_medium_threshold
PRINT_PRIORITY_NORMAL_THRESHOLD = settings.print_priority_normal_threshold

PICKUP_QR_OPEN_MINUTES_BEFORE = settings.pickup_qr_open_minutes_before
EMS_LOCAL_TIMEZONE = settings.ems_local_timezone
QR_PICKUP_PREFIX = settings.qr_pickup_prefix
QR_REGULATION_PREFIX = settings.qr_regulation_prefix
PDF_TOKEN_EXPIRE_HOURS = settings.pdf_token_expire_hours

SIGN_ORDER_USERNAMES: list[str] = list(settings.sign_order_usernames)

PAPER_DISTRIBUTION_DIVISION = settings.paper_distribution_division
PAPER_DISTRIBUTION_EXCLUDED_USERNAMES: set[str] = set(settings.paper_distribution_excluded_usernames)
PAPER_DISTRIBUTION_EXCLUDED_NAME_SNIPPETS: tuple[str, ...] = settings.paper_distribution_excluded_name_snippets
