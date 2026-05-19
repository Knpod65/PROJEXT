"""Document authorization policy helpers.

This keeps document access semantics in one place and mirrors the Laravel-style
policy layer used elsewhere in the platform.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException

import models
from auth_utils import get_current_user, get_effective_role


def can_manage_documents(user: models.User) -> bool:
    return get_effective_role(user) in (models.UserRole.admin, models.UserRole.staff)


def require_document_manager(user: models.User = Depends(get_current_user)) -> models.User:
    if not can_manage_documents(user):
        raise HTTPException(status_code=403, detail="ต้องการสิทธิ์ staff หรือ admin")
    return user
