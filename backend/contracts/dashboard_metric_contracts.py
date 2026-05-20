"""dashboard_metric_contracts.py — TypedDict contracts for role-based dashboard metrics.

Rules:
- Pure contracts only — zero DB, zero ORM, zero FastAPI.
- All fields JSON-safe.
- Importable without importing the backend package.
"""
from __future__ import annotations

from typing import Any, Literal, Optional

from typing_extensions import TypedDict

_PDPA_LEVELS = frozenset({"public", "internal", "confidential", "restricted"})


# ── Metric and Group ───────────────────────────────────────────────────────────

class DashboardMetric(TypedDict):
    metric_code: str
    title_i18n_key: str
    description_i18n_key: str
    value: int | float | str
    unit: str
    trend: str                          # "up" | "down" | "flat" | "unknown"
    trend_label_i18n_key: str
    severity: str                       # "good" | "info" | "warning" | "critical"
    why_it_matters_i18n_key: str
    recommended_action_i18n_key: str
    owner_role: str
    drilldown_route: Optional[str]
    updated_at: Optional[str]           # ISO-8601 or None
    pdpa_level: str                     # "public" | "internal" | "confidential" | "restricted"


class DashboardMetricGroup(TypedDict):
    group_code: str
    title_i18n_key: str
    description_i18n_key: str
    metrics: list[DashboardMetric]
    alerts: list[str]
    recommended_actions: list[str]


# ── Alert / Action ─────────────────────────────────────────────────────────────

class DashboardAction(TypedDict):
    action_code: str
    label_i18n_key: str
    route: str
    requires_roles: list[str]


class DashboardAlert(TypedDict):
    alert_code: str
    severity: str
    title_i18n_key: str
    body_i18n_key: str
    metric_codes: list[str]
    pdpa_level: str


# ── Summary / Payload ──────────────────────────────────────────────────────────

class DashboardRoleSummary(TypedDict):
    role: str
    role_label_i18n_key: str
    health_score: Optional[float]
    risk_band: Optional[str]            # "green" | "amber" | "red" | "unknown"
    key_metrics: list[DashboardMetric]
    alerts: list[DashboardAlert]
    recommended_actions: list[DashboardAction]
    last_updated: Optional[str]


class AdminIntelligenceDashboard(TypedDict):
    role: str                           # always "admin"
    overall_health_score: Optional[float]
    overall_risk_band: Optional[str]
    last_computed_at: Optional[str]
    groups: list[DashboardMetricGroup]


class RoleDashboardPayload(TypedDict):
    role: str
    role_label_i18n_key: str
    summary: DashboardRoleSummary
    groups: list[DashboardMetricGroup]
    unauthorized: bool


# ── Validators ─────────────────────────────────────────────────────────────────


def validate_pdpa_level(value: str) -> bool:
    return value in _PDPA_LEVELS


def validate_metric(m: dict) -> list[str]:
    """Return a list of validation errors (never raises)."""
    errors: list[str] = []
    required = {
        "metric_code": str,
        "title_i18n_key": str,
        "description_i18n_key": str,
        "value": (int, float, str),
        "unit": str,
        "trend": str,
        "trend_label_i18n_key": str,
        "severity": str,
        "why_it_matters_i18n_key": str,
        "recommended_action_i18n_key": str,
        "owner_role": str,
        "pdpa_level": str,
    }
    for key, expected in required.items():
        if key not in m:
            errors.append(f"Missing required key: {key}")
        elif not isinstance(m[key], expected):
            errors.append(
                f"Key '{key}' expected type {expected}, got {type(m[key]).__name__}."
            )
    if "pdpa_level" in m and not validate_pdpa_level(m["pdpa_level"]):
        errors.append(f"Invalid pdpa_level: {m['pdpa_level']!r}")
    return errors


def build_minimal_metric(override: Optional[dict] = None) -> DashboardMetric:
    base: DashboardMetric = {
        "metric_code": "minimal",
        "title_i18n_key": "k",
        "description_i18n_key": "k",
        "value": 0,
        "unit": "",
        "trend": "unknown",
        "trend_label_i18n_key": "k",
        "severity": "info",
        "why_it_matters_i18n_key": "k",
        "recommended_action_i18n_key": "k",
        "owner_role": "admin",
        "drilldown_route": None,
        "updated_at": None,
        "pdpa_level": "internal",
    }
    if override:
        base.update(override)  # type: ignore[typeddict-item]
    return base


def build_minimal_group(override: Optional[dict] = None) -> DashboardMetricGroup:
    group: DashboardMetricGroup = {
        "group_code": "default",
        "title_i18n_key": "k",
        "description_i18n_key": "k",
        "metrics": [build_minimal_metric()],
        "alerts": [],
        "recommended_actions": [],
    }
    if override:
        group.update(override)  # type: ignore[typeddict-item]
    return group


def build_minimal_dashboard(override: Optional[dict] = None) -> AdminIntelligenceDashboard:
    _GROUPS = ["examOperations", "optimizationQuality", "governanceApproval",
               "staffWorkload", "roomCapacity", "teacherSubmission",
               "printExport", "qrPickup", "pdpaSecurity", "systemOperations"]
    dashboard: AdminIntelligenceDashboard = {
        "role": "admin",
        "overall_health_score": 0.0,
        "overall_risk_band": "green",
        "last_computed_at": None,
        "groups": [build_minimal_group({"group_code": g}) for g in _GROUPS],
    }
    if override:
        dashboard.update(override)  # type: ignore[typeddict-item]
    return dashboard


def build_minimal_payload(
    role: str = "admin",
    override: Optional[dict] = None,
) -> RoleDashboardPayload:
    payload: RoleDashboardPayload = {
        "role": role,
        "role_label_i18n_key": f"dashboard.role.{role}",
        "summary": {
            "role": role,
            "role_label_i18n_key": f"dashboard.role.{role}",
            "health_score": 0.0,
            "risk_band": "green",
            "key_metrics": [],
            "alerts": [],
            "recommended_actions": [],
            "last_updated": None,
        },
        "groups": [],
        "unauthorized": False,
    }
    if override:
        extra = dict(payload)
        extra.update(override)
        payload = extra  # type: ignore[assignment]
    return payload
