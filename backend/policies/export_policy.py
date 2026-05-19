"""
export_policy.py — export permission and policy checks.

Owns:
- role-based export permissions
- scope validation
- audit requirement checks
"""
from typing import Optional
from fastapi import HTTPException
import models


class ExportPolicy:
    """Policy checks for export operations."""

    @staticmethod
    def can_export_schedule(user: models.User) -> bool:
        """Check if user can export schedule."""
        return user.role in (models.UserRole.admin, models.UserRole.staff, models.UserRole.teacher)

    @staticmethod
    def can_export_workload(user: models.User) -> bool:
        """Check if user can export workload."""
        return user.role in (models.UserRole.admin, models.UserRole.staff)

    @staticmethod
    def can_export_paper_distribution(user: models.User) -> bool:
        """Check if user can export paper distribution."""
        return user.role in (models.UserRole.admin, models.UserRole.staff)

    @staticmethod
    def can_export_submissions(user: models.User) -> bool:
        """Check if user can export submissions."""
        return user.role == models.UserRole.admin

    @staticmethod
    def can_export_compensation(user: models.User) -> bool:
        """Check if user can export compensation."""
        return user.role == models.UserRole.admin

    @staticmethod
    def require_export_permission(user: models.User, scope: str) -> None:
        """Raise if user lacks permission for scope."""
        permissions = {
            "schedule": ExportPolicy.can_export_schedule,
            "workload": ExportPolicy.can_export_workload,
            "paper_distribution": ExportPolicy.can_export_paper_distribution,
            "submissions": ExportPolicy.can_export_submissions,
            "compensation": ExportPolicy.can_export_compensation,
        }
        check = permissions.get(scope)
        if not check or not check(user):
            raise HTTPException(403, f"ไม่มีสิทธิ์ส่งออก {scope}")