"""FacultyConfigRepository — protocol + in-memory implementation.

All methods return copies so callers cannot mutate internal state.
The in-memory implementation is thread-safe via threading.Lock.
"""
from __future__ import annotations

import threading
from typing import Protocol, runtime_checkable

from config_models.faculty_config import FacultyConfig


@runtime_checkable
class FacultyConfigRepository(Protocol):
    def save(self, config: FacultyConfig) -> FacultyConfig: ...
    def get_by_id(self, faculty_id: int) -> FacultyConfig | None: ...
    def get_by_code(self, code: str) -> FacultyConfig | None: ...
    def list_all(self) -> list[FacultyConfig]: ...
    def list_active(self) -> list[FacultyConfig]: ...
    def delete(self, faculty_id: int) -> bool: ...


class InMemoryFacultyConfigRepository:
    """Thread-safe in-memory implementation of FacultyConfigRepository."""

    def __init__(self) -> None:
        self._store: dict[int, FacultyConfig] = {}
        self._lock = threading.Lock()

    def save(self, config: FacultyConfig) -> FacultyConfig:
        with self._lock:
            self._store[config.faculty_id] = config
        return config

    def get_by_id(self, faculty_id: int) -> FacultyConfig | None:
        with self._lock:
            return self._store.get(faculty_id)

    def get_by_code(self, code: str) -> FacultyConfig | None:
        normalized = code.strip().upper()
        with self._lock:
            for config in self._store.values():
                if config.code.strip().upper() == normalized:
                    return config
        return None

    def list_all(self) -> list[FacultyConfig]:
        with self._lock:
            return list(self._store.values())

    def list_active(self) -> list[FacultyConfig]:
        with self._lock:
            return [c for c in self._store.values() if c.is_active]

    def delete(self, faculty_id: int) -> bool:
        with self._lock:
            if faculty_id in self._store:
                del self._store[faculty_id]
                return True
        return False
