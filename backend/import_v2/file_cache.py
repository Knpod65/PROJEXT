from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import secrets


TTL_SECONDS = 10 * 60
_CACHE: Dict[str, Dict[str, Any]] = {}


def _purge_expired() -> None:
    now = datetime.now(timezone.utc)
    expired_tokens = [
        token
        for token, payload in _CACHE.items()
        if now - payload["upload_time"] > timedelta(seconds=TTL_SECONDS)
    ]
    for token in expired_tokens:
        _CACHE.pop(token, None)


def store_file(rows: List[Dict[str, Any]], filename: str) -> str:
    _purge_expired()
    file_token = secrets.token_urlsafe(24)
    _CACHE[file_token] = {
        "rows": rows,
        "filename": filename,
        "upload_time": datetime.now(timezone.utc),
    }
    return file_token


def get_file(file_token: str) -> Optional[Dict[str, Any]]:
    _purge_expired()
    return _CACHE.get(file_token)


def clear_file(file_token: str) -> None:
    _CACHE.pop(file_token, None)
