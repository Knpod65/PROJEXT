"""Executive dashboard projection service.

Aggregates pre-computed dicts from existing EMS services into a single
executive-facing health summary. Pure logic. No DB, no ORM, no HTTP.
All inputs and outputs are JSON-safe plain dicts/lists.
"""
from __future__ import annotations

from typing import Any

from services.analytics_metric_registry_service import list_metrics
from services.analytics_projection_service import (
    project_governance_trend,
    project_quality_trend,
    project_room_utilization_trend,
    project_invigilator_overload_trend,
)
from contracts.analytics_contracts import ExecutiveDashboardSummary, WorkloadAnalyticsSummary


_DEFAULT_DASHBOARD: ExecutiveDashboardSummary = {
    "overall_health_score": 0.0,
    "risk_band": "red",
    "optimization_quality_avg": 0.0,
    "governance_blocker_count": 0,
    "publication_ready_count": 0,
    "workload_balance_score": 0.0,
    "room_utilization_score": 0.0,
    "pdpa_alert_count": 0,
    "top_risks": [],
    "recommended_actions": [],
}


def build_workload_summary_dict(
    workload_map: dict[str, Any] | None,
) -> dict[str, Any]:
    """Convert a pre-computed workload map into a JSON-safe workload summary.

    Args:
        workload_map: A pre-computed workload map from workload analytics.

    Returns:
        JSON-safe workload summary dict. Returns zeroed defaults if input is empty.
    """
    if not workload_map:
        return {
            "total_assignments": 0,
            "average_load": 0.0,
            "max_load": 0,
            "imbalance_score": 0.0,
            "overloaded_staff_count": 0,
            "fairness_band": "green",
            "top_overload_risks": [],
        }

    loads = workload_map.get("per_staff_load", [])
    if not loads:
        return {
            "total_assignments": 0,
            "average_load": 0.0,
            "max_load": 0,
            "imbalance_score": 0.0,
            "overloaded_staff_count": 0,
            "fairness_band": "green",
            "top_overload_risks": [],
        }

    load_values = [float(s.get("total_load", 0)) for s in loads]
    avg = sum(load_values) / len(load_values) if load_values else 0.0
    threshold = avg * 1.5
    overloaded = [s for s in loads if float(s.get("total_load", 0)) > threshold]
    variance = sum((v - avg) ** 2 for v in load_values) / len(load_values) if load_values else 0.0
    std_dev = variance ** 0.5

    fairness_band = _fairness_band(std_dev, avg)
    imbalance_score = round(std_dev / avg, 4) if avg > 0 else 0.0

    top_overload_risks = [
        {
            "user_id": int(s.get("user_id", 0)),
            "staff_name": str(s.get("staff_name", "")),
            "department": str(s.get("department", "")),
            "current_load": int(s.get("total_load", 0)),
            "overload_pct": round(
                (float(s.get("total_load", 0)) - avg) / avg * 100.0, 1
            ) if avg > 0 else 0.0,
        }
        for s in overloaded[:5]
    ]

    return {
        "total_assignments": int(sum(load_values)),
        "average_load": round(avg, 2),
        "max_load": int(max(load_values)) if load_values else 0,
        "imbalance_score": round(imbalance_score, 4),
        "overloaded_staff_count": len(overloaded),
        "fairness_band": fairness_band,
        "top_overload_risks": top_overload_risks,
    }


def compute_room_summary_dict(
    schedules: list[dict[str, Any]] | None,
    rooms: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """Compute a per-room utilization summary from schedules and room data.

    Args:
        schedules: List of schedule dicts with room_name, exam_date, exam_time,
                   sections_count, students_count (optional).
        rooms:      List of room dicts with room_name, building, capacity.

    Returns:
        Dict keyed by room_name with per-room utilization data.
    """
    result: dict[str, Any] = {}
    room_capacities: dict[str, int] = {}
    room_buildings: dict[str, str] = {}

    if rooms:
        for r in rooms:
            name = r.get("room_name", "")
            room_capacities[name] = int(r.get("capacity", 0))
            room_buildings[name] = str(r.get("building", ""))

    if schedules:
        for sched in schedules:
            rname = str(sched.get("room_name", ""))
            entry = result.setdefault(rname, {
                "room_name": rname,
                "building": room_buildings.get(rname, ""),
                "capacity": room_capacities.get(rname, 0),
                "slot_count": 0,
                "students_sum": 0,
            })
            entry["slot_count"] += 1
            entry["students_sum"] += int(sched.get("students_count", 0))

    for rname, entry in result.items():
        cap = entry["capacity"]
        slots = entry["slot_count"]
        students = entry["students_sum"]
        if cap > 0 and slots > 0:
            entry["avg_utilization"] = round(students / (cap * slots), 4)
        else:
            entry["avg_utilization"] = 0.0

    return result


# ── Scenario detection ─────────────────────────────────────────────────────────

def _detect_scenario(
    workload_map: dict | None,
    room_schedules: list | None,
    rooms: list | None,
    governance_snapshots: list | None,
    audit_logs_recent: list | None = None,
) -> str:
    has_w = workload_map is not None and bool(workload_map)
    has_rooms = (room_schedules is not None and bool(room_schedules)
                 and rooms is not None and bool(rooms))
    has_g = governance_snapshots is not None and bool(governance_snapshots)
    has_audit = audit_logs_recent is not None and bool(audit_logs_recent)
    if not has_g and not has_rooms and not has_w and not has_audit:
        return "empty"
    if has_g and not has_rooms and not has_w and not has_audit:
        return "governance_only"
    if has_rooms and not has_g and not has_w and not has_audit:
        return "rooms_only"
    if has_w and not has_g and not has_rooms and not has_audit:
        return "workload_only"
    if has_audit and not has_g and not has_rooms and not has_w:
        return "audit_only"
    return "mixed"


def project_executive_dashboard(
    workload_map: dict[str, Any] | None = None,
    room_schedules: list[dict[str, Any]] | None = None,
    rooms: list[dict[str, Any]] | None = None,
    governance_snapshots: list[dict[str, Any]] | None = None,
    audit_logs_recent: list[dict[str, Any]] | None = None,
    optimization_quality: dict[str, Any] | None = None,
    recent_import_sessions: list[dict[str, Any]] | None = None,
) -> ExecutiveDashboardSummary:
    """Build the full executive analytics dashboard.

    Args:
        workload_map:            Pre-computed workload map (D4.4 output).
        room_schedules:          List of raw room schedule dicts.
        rooms:                   List of room dicts.
        governance_snapshots:    List of governance state snapshots.
        audit_logs_recent:       Recent audit log entries.
        optimization_quality:    Quality report dict from optimization.
        recent_import_sessions:  Recent import session summaries.

    Returns:
        ExecutiveDashboardSummary with health score, risk band, top risks,
        and recommended actions. PII-free.
    """
    scenario = _detect_scenario(
        workload_map, room_schedules, rooms,
        governance_snapshots, audit_logs_recent,
    )

    # "empty" means caller called with no meaningful input — return safe defaults.
    if scenario == "empty":
        return _DEFAULT_DASHBOARD

    # ── Individual projections ─────────────────────────────────────────────────
    quality_snapshots = [optimization_quality] if optimization_quality else []
    quality_proj = project_quality_trend(quality_snapshots)
    gov_proj = project_governance_trend(
        governance_snapshots if governance_snapshots is not None else []
    )
    room_proj = project_room_utilization_trend(
        [{"room_efficiency_score": r.get("avg_utilization", 0) * 100}
         for r in (compute_room_summary_dict(room_schedules, rooms) or {}).values()]
        if (room_schedules is not None and room_schedules)
           and (rooms is not None and rooms)
        else []
    )

    workload_summary = build_workload_summary_dict(workload_map)

    # ── Health score ───────────────────────────────────────────────────────────
    has_governance = scenario not in ("empty", "rooms_only", "workload_only", "audit_only")
    has_rooms = scenario not in ("empty", "governance_only", "workload_only", "audit_only")
    has_workload = scenario in ("workload_only", "mixed")
    has_quality = bool(optimization_quality)

    quality_score = _safe_float(quality_proj.get("average_score")) if has_quality else 0.0
    governance_health_score = (
        _safe_float(gov_proj.get("escalation_rate")) * 100.0 if has_governance else 0.0
    )
    governance_health_contrib = (100.0 - governance_health_score) if has_governance else 0.0
    utilization_score = (
        _safe_float(room_proj.get("average_utilization")) * 100.0 if has_rooms else 0.0
    )
    workload_balance = (
        round(_safe_float(workload_summary.get("average_load")), 2) if has_workload else 0.0
    )

    overall_health = _score_to_percent(
        quality_score * 0.35
        + governance_health_contrib * 0.25
        + utilization_score * 0.20
        + workload_balance * 0.20,
    )
    risk_band = _risk_band(overall_health)

    # ── PDPA / publication counts ──────────────────────────────────────────────
    publication_ready = int(
        optimization_quality.get("publishability_score", 0)
        if optimization_quality
        else 0
    )
    if publication_ready > 100:
        publication_ready = int(publication_ready / 100.0)

    pdpa_alert_count = 0
    if audit_logs_recent:
        pdpa_alert_count = sum(
            1 for log in audit_logs_recent
            if any(
                kw in str(log.get("action", "")).lower()
                for kw in ("pdpa", "pii", "redact", "sensitive")
            )
        )

    blocker_count = int(gov_proj.get("state_distribution", {}).get("BLOCKED", 0))

    # ── Top risks & recommended actions ────────────────────────────────────────
    risks = _build_top_risks(
        quality_proj, gov_proj, workload_summary,
        optimization_quality, audit_logs_recent,
    )
    actions = _build_recommended_actions(
        risk_band, blocker_count, pdpa_alert_count,
        quality_proj, workload_summary,
    )

    return {
        "overall_health_score": overall_health,
        "risk_band": risk_band,
        "optimization_quality_avg": quality_score,
        "governance_blocker_count": blocker_count,
        "publication_ready_count": publication_ready,
        "workload_balance_score": round(workload_balance, 2),
        "overloaded_staff_count": int(workload_summary.get("overloaded_staff_count", 0)),
        "room_utilization_score": round(utilization_score, 2),
        "pdpa_alert_count": pdpa_alert_count,
        "top_risks": risks[:5],
        "recommended_actions": actions[:5],
    }


# ── Private helpers ─────────────────────────────────────────────────────────────

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _score_to_percent(value: float) -> float:
    return round(max(0.0, min(100.0, _safe_float(value))), 2)


def _fairness_band(std_dev: float, avg: float) -> str:
    if avg <= 0:
        return "green"
    if std_dev < avg * 0.15:
        return "green"
    if std_dev < avg * 0.30:
        return "amber"
    return "red"


def _risk_band(health: float) -> str:
    if health >= 75.0:
        return "green"
    if health >= 50.0:
        return "amber"
    return "red"


_RISK_ALERT_MESSAGE = "[REDACTED]"


# ── Public class wrapper ─────────────────────────────────────────────────────────

class ExecutiveDashboardProjectionService:
    """Namespace class providing a stable class-based API for OPS-DASH consumers.

    The underlying logic lives in the module-level ``project_executive_dashboard``
    function. This class simply delegates to it so that imports of the form
    ``ExecutiveDashboardProjectionService.build_executive_dashboard_summary(...)``
    resolve consistently across analytics and dashboard-intelligence routers.
    """

    @staticmethod
    def build_executive_dashboard_summary(
        workload: dict | None = None,
        governance: dict | None = None,
        room: dict | None = None,
        pdpa: list | None = None,
    ) -> dict:
        """Return an ``ExecutiveDashboardSummary``-shaped dict.

        Maps dashboard-intelligence kwargs to the underlying ``project_executive_dashboard``
        call which expects ``(workload_map, room_schedules, rooms, governance_snapshots,
        audit_logs_recent, optimization_quality, recent_import_sessions)``.

        All missing inputs fall back to empty/default values; the underlying function
        returns safe defaults rather than raising.
        """
        return project_executive_dashboard(
            workload_map=workload or {},
            room_schedules=room.get("rooms", []) if isinstance(room, dict) else [],
            rooms=room.get("rooms", []) if isinstance(room, dict) else [],
            governance_snapshots=governance.get("governance_decisions", []) if isinstance(governance, dict) else [],
            audit_logs_recent=pdpa if pdpa else [],
            optimization_quality=None,
            recent_import_sessions=None,
        )


def _build_top_risks(
    quality_proj: dict,
    gov_proj: dict,
    workload_summary: dict,
    optimization_quality: dict | None,
    audit_logs_recent: list | None,
) -> list[dict[str, str]]:
    risks: list[dict[str, str]] = []

    q_score = _safe_float(quality_proj.get("average_score"))
    if q_score < 40.0:
        risks.append({
            "risk": f"Optimization quality degraded ({round(q_score, 1)}/100)",
            "severity": "high",
            "category": "optimization",
        })

    for state, count in (gov_proj.get("state_distribution") or {}).items():
        if state == "BLOCKED" and count > 0:
            risks.append({
                "risk": f"{count} governance blocker(s) active",
                "severity": "critical",
                "category": "governance",
            })
        if state == "ESCALATION_REQUIRED" and count > 0:
            risks.append({
                "risk": f"{count} escalation(s) pending governance review",
                "severity": "high",
                "category": "governance",
            })

    overloaded = workload_summary.get("overloaded_staff_count", 0)
    if overloaded > 0:
        risks.append({
            "risk": f"{overloaded} staff member(s) overloaded",
            "severity": "medium",
            "category": "workload",
        })

    if audit_logs_recent and len(audit_logs_recent) > 10:
        risks.append({
            "risk": "High volume PDPA events in recent audit logs",
            "severity": "high",
            "category": "pdpa",
        })

    return risks


def _build_recommended_actions(
    risk_band: str,
    blocker_count: int,
    pdpa_alert_count: int,
    quality_proj: dict,
    workload_summary: dict,
) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []

    if risk_band == "red":
        actions.append({
            "action": "Immediate executive review required — health score below threshold",
            "owner": "admin",
            "priority": "critical",
        })

    if blocker_count > 0:
        actions.append({
            "action": f"Resolve {blocker_count} active governance blocker(s)",
            "owner": "esq_head",
            "priority": "high",
        })

    q_score = _safe_float(quality_proj.get("average_score"))
    if q_score < 50.0:
        actions.append({
            "action": "Re-run optimization cycle — quality score below acceptable range",
            "owner": "admin",
            "priority": "high",
        })

    if pdpa_alert_count > 0:
        actions.append({
            "action": "Review and triage PDPA alert events with data protection officer",
            "owner": "esq_head",
            "priority": "high",
        })

    overloaded = workload_summary.get("overloaded_staff_count", 0)
    if overloaded > 0:
        actions.append({
            "action": f"Re-balance workload across {overloaded} overloaded staff",
            "owner": "admin",
            "priority": "medium",
        })

    fb = workload_summary.get("fairness_band", "green")
    if fb == "red":
        actions.append({
            "action": "Investigate workload imbalance — fairness score critical",
            "owner": "admin",
            "priority": "medium",
        })

    return actions
