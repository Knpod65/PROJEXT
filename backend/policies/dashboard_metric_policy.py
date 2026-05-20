"""dashboard_metric_policy.py — Policy checks for role-based dashboard metrics.

Rules:
- Pure functions. Zero DB, zero ORM, zero FastAPI imports (except None list).
- Returns booleans. Never raises HTTPException from this file — callers handle 403.
"""


class DashboardMetricPolicy:
    """Policy checks for the role-based dashboard intelligence layer."""

    @staticmethod
    def can_view_admin_intelligence(role: str) -> bool:
        """Admin intelligence dashboard — admin only."""
        return role.lower() == "admin"

    @staticmethod
    def can_view_role_summary(requesting_role: str, target_role: str) -> bool:
        """A user with *requesting_role* may view the role summary of *target_role*.

        Same-role users may always see their own summary.
        Admin / esq_head / secretary may view any role summary.
        Everyone else sees only their own.
        """
        req = requesting_role.lower()
        tgt = target_role.lower()
        if req == tgt:
            return True
        if req in ("admin", "esq_head", "secretary"):
            return True
        return False

    @staticmethod
    def can_view_pdpa_health(role: str) -> bool:
        """PDPA health feed is visible to admin, esq_head, secretary, and DPO."""
        return role.lower() in ("admin", "esq_head", "secretary", "dpo")

    @staticmethod
    def can_view_executive_summary(role: str) -> bool:
        """Executive summary is visible to admin, esq_head, and secretary."""
        return role.lower() in ("admin", "esq_head", "secretary")

    @staticmethod
    def authorize_role_dashboard_access(role: str) -> None:
        """Raise ValueError if *role* is not a recognised EMS role."""
        allowed = frozenset({
            "admin", "staff", "teacher", "student", "print_shop",
            "dept_supervisor", "esq_head", "secretary", "it", "dpo", "executive",
        })
        if role.lower() not in allowed:
            raise ValueError(f"Unknown role: {role!r}")
