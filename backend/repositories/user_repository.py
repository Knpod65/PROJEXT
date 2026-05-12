"""User repository scaffolding for future router -> service -> repository flow."""
from __future__ import annotations

from typing import Iterable

from sqlalchemy.orm import Session

import models


def normalize_lookup_value(value: object) -> str | None:
    """Trim lookup input and collapse empty values to None."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def normalize_employee_id(value: object) -> int | None:
    """Convert employee-id shaped values into ints for ORM lookups."""
    text = normalize_lookup_value(value)
    if not text or not text.isdigit():
        return None
    return int(text)


class UserRepository:
    """Repository wrapper around common EMS user queries.

    This module is additive scaffolding only. Existing routers still query the
    ORM directly until the planned service extraction phases move them here.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> models.User | None:
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def get_by_username(self, username: object) -> models.User | None:
        normalized = normalize_lookup_value(username)
        if not normalized:
            return None
        return (
            self.db.query(models.User)
            .filter(models.User.username == normalized)
            .first()
        )

    def get_active_by_username(self, username: object) -> models.User | None:
        normalized = normalize_lookup_value(username)
        if not normalized:
            return None
        return (
            self.db.query(models.User)
            .filter(
                models.User.username == normalized,
                models.User.is_active.is_(True),
            )
            .first()
        )

    def get_by_email(self, email: object) -> models.User | None:
        normalized = normalize_lookup_value(email)
        if not normalized:
            return None
        return self.db.query(models.User).filter(models.User.email == normalized).first()

    def get_by_employee_id(self, employee_id: object) -> models.User | None:
        normalized = normalize_employee_id(employee_id)
        if normalized is None:
            return None
        return (
            self.db.query(models.User)
            .filter(models.User.employee_id == normalized)
            .first()
        )

    def get_first_matching_identity(
        self,
        candidates: Iterable[tuple[str, object]],
    ) -> models.User | None:
        """Resolve the first supported identity candidate.

        Supported keys intentionally mirror the current `users` table shape.
        Future schema extensions can add `student_id` / external-subject lookups
        here without changing router code.
        """
        for field_name, value in candidates:
            if field_name == "username":
                user = self.get_by_username(value)
            elif field_name == "email":
                user = self.get_by_email(value)
            elif field_name == "employee_id":
                user = self.get_by_employee_id(value)
            else:
                user = None
            if user:
                return user
        return None
