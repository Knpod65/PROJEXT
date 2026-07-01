"""
dashboard_policy.py — dashboard permission and policy checks.

Owns:
- role-based dashboard permissions
- visibility filtering by role/faculty
"""
from fastapi import HTTPException
import models


class DashboardPolicy:
    """Policy checks for dashboard operations."""

    @staticmethod
    def can_view_dashboard(user: models.User) -> bool:
        return user.role in (
            models.UserRole.admin,
            models.UserRole.dept_supervisor,
            models.UserRole.staff,
            models.UserRole.teacher,
            models.UserRole.esq_head,
            models.UserRole.secretary,
        )

    @staticmethod
    def can_view_analytics(user: models.User) -> bool:
        return user.role == models.UserRole.admin

    @staticmethod
    def can_view_recent_logs(user: models.User) -> bool:
        return user.role == models.UserRole.admin

    @staticmethod
    def require_dashboard_access(user: models.User) -> None:
        if not DashboardPolicy.can_view_dashboard(user):
            raise HTTPException(403, "ไม่มีสิทธิ์เข้าถึง dashboard")

    @staticmethod
    def require_analytics_access(user: models.User) -> None:
        if not DashboardPolicy.can_view_analytics(user):
            raise HTTPException(403, "ไม่มีสิทธิ์เข้าถึง analytics")
