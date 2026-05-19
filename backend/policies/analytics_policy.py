"""
analytics_policy.py — analytics permission and policy checks.

Owns:
- role-based analytics permissions
- sensitive analytics scope checks
"""
from fastapi import HTTPException
import models


class AnalyticsPolicy:
    """Policy checks for analytics operations."""

    SENSITIVE_SCOPES = {"executive-summary", "integration-contracts", "optimization-trace"}

    @staticmethod
    def can_view_analytics(user: models.User) -> bool:
        return user.role in (
            models.UserRole.admin,
            models.UserRole.staff,
            models.UserRole.esq_head,
            models.UserRole.secretary,
        )

    @staticmethod
    def can_view_sensitive_analytics(user: models.User) -> bool:
        return user.role in (models.UserRole.admin, models.UserRole.staff)

    @staticmethod
    def require_analytics_access(user: models.User, scope: str = "") -> None:
        if scope in AnalyticsPolicy.SENSITIVE_SCOPES:
            if not AnalyticsPolicy.can_view_sensitive_analytics(user):
                raise HTTPException(403, f"ไม่มีสิทธิ์เข้าถึง analytics scope: {scope}")
        else:
            if not AnalyticsPolicy.can_view_analytics(user):
                raise HTTPException(403, "ไม่มีสิทธิ์เข้าถึง analytics")
