"""Policy registry service — layered resolution of faculty/period policy values.

Resolution chain (highest priority first):
  1. Period override  (faculty_id + period_id + key)
  2. Faculty override (faculty_id + key)
  3. Global default   (key)
  4. Runtime fallback (fallback argument, if provided)
  5. KeyError         (if no match and no fallback)

All internal state is module-level and thread-safe via threading.Lock.
Use clear_all_policies() in tests for isolation.
"""
from __future__ import annotations

import threading
from typing import Any

_SENTINEL = object()

_lock = threading.Lock()
_global: dict[str, Any] = {}
_faculty: dict[int, dict[str, Any]] = {}
_period: dict[tuple[int, int], dict[str, Any]] = {}


def set_global_policy(key: str, value: Any) -> None:
    with _lock:
        _global[key] = value


def set_faculty_policy(faculty_id: int, key: str, value: Any) -> None:
    with _lock:
        if faculty_id not in _faculty:
            _faculty[faculty_id] = {}
        _faculty[faculty_id][key] = value


def set_period_policy(faculty_id: int, period_id: int, key: str, value: Any) -> None:
    with _lock:
        k = (faculty_id, period_id)
        if k not in _period:
            _period[k] = {}
        _period[k][key] = value


def get_policy_value(
    key: str,
    *,
    faculty_id: int | None = None,
    period_id: int | None = None,
    fallback: Any = _SENTINEL,
) -> Any:
    """Resolve policy value via the layered resolution chain.

    Raises KeyError if no match found and no fallback provided.
    Note: fallback=None is a valid explicit fallback — pass _SENTINEL (no kwarg) to
    distinguish "no fallback given" from "fallback is None".
    """
    with _lock:
        # 1. Period override
        if faculty_id is not None and period_id is not None:
            period_map = _period.get((faculty_id, period_id), {})
            if key in period_map:
                return period_map[key]

        # 2. Faculty override
        if faculty_id is not None:
            faculty_map = _faculty.get(faculty_id, {})
            if key in faculty_map:
                return faculty_map[key]

        # 3. Global default
        if key in _global:
            return _global[key]

    # 4. Runtime fallback
    if fallback is not _SENTINEL:
        return fallback

    raise KeyError(f"No policy value found for key={key!r}")


def clear_faculty_policies(faculty_id: int) -> None:
    with _lock:
        _faculty.pop(faculty_id, None)
        keys_to_remove = [k for k in _period if k[0] == faculty_id]
        for k in keys_to_remove:
            del _period[k]


def clear_period_policies(faculty_id: int, period_id: int) -> None:
    with _lock:
        _period.pop((faculty_id, period_id), None)


def clear_all_policies() -> None:
    with _lock:
        _global.clear()
        _faculty.clear()
        _period.clear()


def list_policy_keys(
    *,
    faculty_id: int | None = None,
    period_id: int | None = None,
) -> list[str]:
    """Return sorted list of registered policy keys at the given scope."""
    with _lock:
        if faculty_id is not None and period_id is not None:
            return sorted(_period.get((faculty_id, period_id), {}).keys())
        if faculty_id is not None:
            return sorted(_faculty.get(faculty_id, {}).keys())
        return sorted(_global.keys())


def has_faculty_override(faculty_id: int, key: str) -> bool:
    with _lock:
        return key in _faculty.get(faculty_id, {})


def has_period_override(faculty_id: int, period_id: int, key: str) -> bool:
    with _lock:
        return key in _period.get((faculty_id, period_id), {})
