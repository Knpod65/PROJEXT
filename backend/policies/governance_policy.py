"""
governance_policy.py — governance permission and policy checks.

Owns:
- governance endpoint role checks
- publication readiness access controls
"""
from fastapi import HTTPException
import models


class GovernancePolicy:
    """Policy checks for governance operations."""

    @staticmethod
    def can_view_governance(user: models.User) -> bool:
        return user.role in (
            models.UserRole.admin,
            models.UserRole.staff,
            models.UserRole.esq_head,
            models.UserRole.secretary,
        )

    @staticmethod
    def can_run_recheck(user: models.User) -> bool:
        return user.role in (
            models.UserRole.admin,
            models.UserRole.staff,
            models.UserRole.esq_head,
            models.UserRole.secretary,
        )

    @staticmethod
    def require_governance_access(user: models.User) -> None:
        if not GovernancePolicy.can_view_governance(user):
            raise HTTPException(403, "ไม่มีสิทธิ์เข้าถึง governance data")

    @staticmethod
    def require_recheck_access(user: models.User) -> None:
        if not GovernancePolicy.can_run_recheck(user):
            raise HTTPException(403, "ไม่มีสิทธิ์เรียก recheck")

    @staticmethod
    def require_admin(user: models.User) -> None:
        if user.role != models.UserRole.admin:
            raise HTTPException(403, "ต้องเป็น admin")
