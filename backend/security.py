"""
security.py — Shared Security Utilities
=========================================
Centralizes all security-relevant functions:
  - Input sanitization
  - Cookie management
  - Secret validation
  - Token handling helpers
"""
from __future__ import annotations
import os
import re
import sys
import html
import uuid
import hashlib
from typing import Optional

from fastapi import Request, Response, HTTPException, Cookie, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.settings import settings

# ── HTML sanitization ─────────────────────────────────────────────────────────

def sanitize_text(value: Optional[str], max_len: int = 2000) -> Optional[str]:
    """
    Strip HTML, normalize whitespace, enforce max length.
    Use for all user-supplied text stored in DB and later displayed.
    """
    if value is None:
        return None
    # HTML-escape to prevent accidental rendering as markup
    cleaned = html.escape(str(value).strip())
    if len(cleaned) > max_len:
        raise HTTPException(400, f"ข้อความยาวเกิน {max_len} ตัวอักษร")
    return cleaned


def sanitize_id(value: str, pattern: str = r'^[a-zA-Z0-9_\-\.]{1,50}$') -> str:
    """Validate string IDs (student IDs, request IDs, etc.)."""
    if not re.match(pattern, value):
        raise HTTPException(400, "รูปแบบ ID ไม่ถูกต้อง")
    return value


def sanitize_request_id(raw: str) -> str:
    """
    Sanitize X-Request-ID header to prevent log injection.
    Only allow alphanumeric + hyphen, max 64 chars.
    """
    if raw and re.match(r'^[a-zA-Z0-9\-]{1,64}$', raw):
        return raw
    return str(uuid.uuid4())


# ── Secret validation ─────────────────────────────────────────────────────────

INSECURE_SECRET_VALUES = {
    "", "change-me", "secret", "password",
    "ems_dev_only_DO_NOT_USE_IN_PRODUCTION_2025_change_me",
}


def validate_production_secrets() -> None:
    """
    Crash the process early if dangerous defaults are detected in production.
    Call this in the lifespan startup hook.
    """
    env = os.getenv
    is_prod = env("ENV", "development").lower() in ("production", "prod")

    if not is_prod:
        return  # Dev mode: warn but don't crash

    errors = []

    secret_key = env("SECRET_KEY", "")
    if secret_key in INSECURE_SECRET_VALUES:
        errors.append("SECRET_KEY is unset or uses an insecure default")
    elif len(secret_key) < 32:
        errors.append("SECRET_KEY is too short (minimum 32 characters)")

    cron_secret = env("CRON_SECRET", "")
    if cron_secret in INSECURE_SECRET_VALUES:
        errors.append("CRON_SECRET is unset or uses an insecure default")

    pg_pass = env("POSTGRES_PASSWORD", "")
    if pg_pass in INSECURE_SECRET_VALUES:
        errors.append("POSTGRES_PASSWORD is unset or uses an insecure default")

    if errors:
        for err in errors:
            print(f"FATAL SECURITY: {err}", file=sys.stderr)
        sys.exit(1)


# ── Cookie management ─────────────────────────────────────────────────────────

COOKIE_NAME = "ems_session"
_IS_PRODUCTION = os.getenv("ENV", "development").lower() in ("production", "prod")
_COOKIE_MAX_AGE_SECONDS = settings.token_expire_hours * 3600


def set_auth_cookie(response: Response, token: str) -> None:
    """Set the session cookie with security flags."""
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,                          # JS cannot read
        secure=_IS_PRODUCTION,
        samesite="lax",                         # CSRF protection; lax allows same-site nav
        max_age=_COOKIE_MAX_AGE_SECONDS,
        path="/api",
    )


def clear_auth_cookie(response: Response) -> None:
    """Expire the session cookie on logout."""
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/api",
        httponly=True,
        secure=_IS_PRODUCTION,
        samesite="lax",
    )


def get_token_from_request(request: Request) -> Optional[str]:
    """
    Extract JWT from request — supports BOTH:
      1. HttpOnly cookie (ems_session) — preferred, secure
      2. Authorization: Bearer <token> — legacy / API clients

    Cookie takes priority. Bearer is kept for backward compatibility
    with the existing frontend and API scripts during migration.
    """
    # 1. Cookie (preferred)
    cookie_token = request.cookies.get(COOKIE_NAME)
    if cookie_token:
        return cookie_token

    # 2. Authorization header (legacy)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    return None


# ── IP extraction ─────────────────────────────────────────────────────────────

def get_real_ip(request: Request) -> str:
    """
    Get the real client IP from Nginx-proxied requests.
    Trusts X-Real-IP set by Nginx. Does NOT trust X-Forwarded-For
    from clients directly (can be spoofed).
    """
    real_ip = request.headers.get("X-Real-IP", "").strip()
    if real_ip:
        return real_ip
    # Fallback: first entry of X-Forwarded-For (set by Nginx)
    forwarded = request.headers.get("X-Forwarded-For", "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ── Hashing helpers ───────────────────────────────────────────────────────────

def hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
