"""
services/exceptions.py — EMS domain exception hierarchy.

Services raise these; routers translate them to HTTPException.
No HTTP status codes here — that belongs in the transport layer.

Usage in a router:
    from services.exceptions import EMSNotFoundError, EMSPermissionError
    from fastapi import HTTPException

    try:
        result = submission_service.get(db, submission_id, user)
    except EMSNotFoundError as e:
        raise HTTPException(404, e.message)
    except EMSPermissionError as e:
        raise HTTPException(403, e.message)
"""
from __future__ import annotations


class EMSDomainError(Exception):
    """Base for all EMS business-logic errors."""

    def __init__(self, message: str, error_code: str = "EMS_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __repr__(self) -> str:
        return f"{type(self).__name__}(code={self.error_code!r}, message={self.message!r})"


class EMSValidationError(EMSDomainError):
    """Input data failed domain-level validation (not Pydantic schema validation)."""

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message, error_code="EMS_VALIDATION_ERROR")
        self.field = field


class EMSPermissionError(EMSDomainError):
    """Caller does not have the required permission for this operation."""

    def __init__(self, message: str = "ไม่มีสิทธิ์ดำเนินการนี้") -> None:
        super().__init__(message, error_code="EMS_PERMISSION_DENIED")


class EMSNotFoundError(EMSDomainError):
    """Requested resource does not exist."""

    def __init__(self, resource: str = "Resource", resource_id: int | str | None = None) -> None:
        detail = f"ไม่พบ {resource}"
        if resource_id is not None:
            detail += f" (id={resource_id})"
        super().__init__(detail, error_code="EMS_NOT_FOUND")
        self.resource = resource
        self.resource_id = resource_id


class EMSConflictError(EMSDomainError):
    """Operation conflicts with existing state (duplicate, locked, etc.)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="EMS_CONFLICT")


class EMSTermLockedError(EMSConflictError):
    """Operation rejected because the exam period is locked."""

    def __init__(self, period_label: str = "รอบสอบ") -> None:
        super().__init__(f"{period_label} ถูกล็อคแล้ว — ไม่สามารถแก้ไขได้")
        self.error_code = "EMS_TERM_LOCKED"


class EMSStateTransitionError(EMSDomainError):
    """State machine rejected the requested transition."""

    def __init__(self, from_state: str, to_state: str, reason: str = "") -> None:
        msg = f"ไม่สามารถเปลี่ยนสถานะจาก '{from_state}' เป็น '{to_state}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg, error_code="EMS_INVALID_TRANSITION")
        self.from_state = from_state
        self.to_state = to_state
