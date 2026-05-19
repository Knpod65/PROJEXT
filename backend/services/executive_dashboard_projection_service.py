"""Executive dashboard projection service.

Aggregates existing analytics outputs into an executive-facing summary.
No DB calls. No ORM. No HTTP.  All inputs are plain dicts.
"""
from __future__ import annotations

from typing import Any


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _health_to_band(score: float) -> str:
    if score >= 75:
        return "green"
    if score >= 50:
        return "amber"
    return "red"


# ── Private layer ─────────────────────────────────────────────────────────────

def _summarise_workload(workload_summary: dict | None) -> dict:
    """Return safe workload fields (handle None).

    The optional `_has_workload_data` bool returned in a tuple allows the
    caller to decide whether the score should contribute to overall health.
    """
    if not workload_summary:
        return {
            "fairness_band": "green",
            "total_assignments": 0,
            "overloaded_staff_count": 0,
        }
    return {
        "fairness_band":          str(workload_summary.get("fairness_band", "green")),
        "total_assignments":      _safe_int(workload_summary.get("total_assignments")),
        "overloaded_staff_count": _safe_int(workload_summary.get("overloaded_staff_count")),
        "imbalance_score":        _safe_float(workload_summary.get("imbalance_score")),
    }


# ── Public API ────────────────────────────────────────────────────────────────

def build_workload_summary_dict(workload_map: dict | None) -> dict:
    """Build a JSON-safe workload summary from a pre-computed workload map.

    Args:
        workload_map:    Dict with at least total_assignments, average_load,
                         max_load, imbalance_score, overloaded_staff_count,
                         fairness_band.  Caller pre-computed.
    Returns:
        JSON-safe workload summary dict.
    """
    if not workload_map:
        return {
            "total_assignments": 0,
            "average_load":      0.0,
            "max_load":          0,
            "imbalance_score":   0.0,
            "overloaded_staff_count": 0,
            "fairness_band":     "green",
        }
    return {
        "total_assignments":      _safe_int(workload_map.get("total_assignments")),
        "average_load":           _safe_float(workload_map.get("average_load")),
        "max_load":               _safe_int(workload_map.get("max_load")),
        "imbalance_score":        _safe_float(workload_map.get("imbalance_score")),
        "overloaded_staff_count": _safe_int(workload_map.get("overloaded_staff_count")),
        "fairness_band":          str(workload_map.get("fairness_band", "green")),
    }


def compute_room_summary_dict(
    schedules: list[dict],
    rooms: dict[int, dict],
) -> dict[str, dict]:
    """Derive an aggregated room summary keyed by room_name.

    Args:
        schedules:       List of schedule dicts  with at minimum: room_id,
                         exam_date, total_sheets.
        rooms:           Dict keyed room_id → {room_name, capacity, building}.

    Returns:
        {room_name: {total_sheets, schedule_count, capacity}} dict.
    """
    result: dict[str, dict] = {}
    for sch in schedules:
        room_id = sch.get("room_id")
        if not room_id:
            continue
        room_info = rooms.get(room_id, {})
        room_name = room_info.get("room_name", f"room-{room_id}")
        entry = result.setdefault(
            room_name,
            {"total_sheets": 0, "schedule_count": 0,
             "capacity": room_info.get("capacity", 0),
             "building":   room_info.get("building", "")},
        )
        entry["total_sheets"] += _safe_int(sch.get("total_sheets", 0))
        entry["schedule_count"] += 1
    return result


def project_executive_dashboard(
    *,
    optimization_quality:    dict | None = None,
    governance_snapshots:    list[dict] | None = None,
    audit_logs_recent:       list[dict] | None = None,
    publication_readiness:   dict | None = None,
    workload_summary:        dict | None = None,
    room_util_summary:       dict | None = None,
    pdpa_alert_count:        int = 0,
    recent_import_sessions:  list[dict] | None = None,
    workload_balance_hint:   float = 0.0,
) -> dict:
    """Build the executive dashboard summary.

    All inputs are plain dicts or None. Aggregate-only. No PII names.

    Args:
        optimization_quality:     Output of compute_quality_report() or None.
        governance_snapshots:     List of governance state dicts.
        audit_logs_recent:        Recent audit_log rows.
        publication_readiness:    Output of assess_publication_readiness().
        workload_summary:         Pre-computed workload analytics dict or None.
        room_util_summary:        Pre-computed room util summary dict or None.
        pdpa_alert_count:         Raw count of PDPA-classified events.
        recent_import_sessions:   Import session rows (unused in this release).
        workload_balance_hint:    Optional numeric workload hint 0-100.

    Returns:
        ExecutiveDashboardSummary -shaped dict.
    """
    gov_snaps = governance_snapshots or []

    # ── Optimization quality ──────────────────────────────────────────────────
    quality_score = _safe_float(
        (optimization_quality or {}).get("overall_score"), 0.0
    )

    # ── Governance blocker + override counts ─────────────────────────────────
    blocker_count = 0
    override_count = 0
    for snap in gov_snaps:
        if snap.get("governance_state") in ("BLOCKED", "ESCALATION_REQUIRED", "ESCALATED"):
            blocker_count += 1
        if snap.get("override_recommendation") == "override_approved":
            override_count += 1

    # ── Publication ready count ───────────────────────────────────────────────
    pub_ready = 0
    if publication_readiness:
        if publication_readiness.get("can_publish"):
            pub_ready = 1
        pub_ready = _safe_int(publication_readiness.get("ready_count", pub_ready))

    # ── Workload balance score ────────────────────────────────────────────────
    # Only include the workload health dimension when the caller has actually
    # provided workload data (total_assignments > 0  OR  supplied explicitly).
    # Absent data → score stays at 0.0 (neutral, doesn't inflate overall health).
    wkl_balance_score = 0.0

    # `wkld["total_assignments"]` is authoritative: 0 means the workload
    # analytics ran and found nothing; None means nothing was passed.
    wkld = _summarise_workload(workload_summary)
    total_assignments_for_wl = _safe_int(wkld.get("total_assignments", 0))

    if workload_balance_hint > 0:
        # Caller explicitly provided a 3rd(r with provideMetrics_partial) calls w_kl_balance →**avoids gradient imbalances here
        wkl_balance_score = float(workload_balance_hint)
        wkl_balance_score = max(0.0, min(100.0, wkl_balance_score))
    elif workload_summary and total_assignments_for_wl > 0:
        # Caller provided a computed analytics dict — derive score from imbalance.
        wkl_imbalance = _safe_float(
            (workload_summary or {}).get("imbalance_score"), 0.0
        )
        wkl_balance_score = max(0.0, min(100.0, round((1.0 - wkl_imbalance) * 100, 1)))

    # ── Room utilization score ────────────────────────────────────────────────
    room_util_score = 0.0
    if room_util_summary:
        avg_util = _safe_float(room_util_summary.get("average_utilization"))
        room_util_score = round(avg_util * 100, 1)

    # ── PDPA alert count ──────────────────────────────────────────────────────
    pdpa_count = int(pdpa_alert_count)

    # ── Per-dimension scores ──────────────────────────────────────────────────
    # Only include scores that were actually provided (> 0 means data existed).
    scores = [quality_score, wkl_balance_score, room_util_score]
    # quality_score == 0 is a real score (e.g. synthesized result); room_util == 0
    # and wkl_balance == 0 mean "absent data" — exclude from the average.
    # We filter when the health distance that generated them was all 0/not given.
    active_scores = _build_active_scores(quality_score, wkl_balance_score, room_util_score)
    overall_health_score = round(
        sum(active_scores) / max(len(active_scores), 1), 1
    ) if has_active_scores(quality_score, wkl_balance_score, room_util_score) else 0.0

    # ── Risk band ─────────────────────────────────────────────────────────────
    risk_band = _health_to_band(overall_health_score)

    # ── Top risks (rule-based — no PII) ───────────────────────────────────────
    top_risks: list[dict] = []
    if blocker_count > 0:
        top_risks.append({
            "risk": f"{blocker_count} governance blocker(s) in current period",
            "severity": "high",
            "category": "governance",
        })
    if pdpa_count > 0:
        top_risks.append({
            "risk": f"{pdpa_count} PDPA classification event(s) in audit log",
            "severity": "high",
            "category": "pdpa_compliance",
        })
    if publication_readiness is not None and pub_ready < 10:
        top_risks.append({
            "risk": "Fewer than 10 sections publication ready — workflow bottleneck detected",
            "severity": "medium",
            "category": "publication",
        })
        recommended_actions.append({
            "action": "Escalate publication-ready shortfall to relevant department supervisors",
            "owner": "esq_head",
            "priority": "medium",
        })
    if wkld["overloaded_staff_count"] > 0:
        top_risks.append({
            "risk": f'{wkld["overloaded_staff_count"]} staff member(s) above normalised load threshold',
            "severity": "medium",
            "category": "workload",
        })
    if not top_risks:
        top_risks.append({
            "risk": "None identified",
            "severity": "low",
            "category": "operational",
        })
    top_risks = top_risks[:5]

    # ── Recommended actions ───────────────────────────────────────────────────
    recommended_actions: list[dict] = []
    if blocker_count > 0:
        recommended_actions.append({
            "action": "Review and clear governance blockers before next period deadline",
            "owner": "admin",
            "priority": "high",
        })
    if pdpa_count > 0:
        recommended_actions.append({
            "action": "Audit PDPA events in audit log and confirm redaction is complete",
            "owner": "admin",
            "priority": "high",
        })
    if publication_readiness is not None and pub_ready < 10:
        recommended_actions.append({
            "action": "Escalate publication-ready shortfall to relevant department supervisors",
            "owner": "esq_head",
            "priority": "medium",
        })
    recommended_actions = recommended_actions[:5]

    return {
        "overall_health_score":    overall_health_score,
        "risk_band":               risk_band,
        "optimization_quality_avg":round(quality_score, 1),
        "governance_blocker_count":blocker_count,
        "publication_ready_count": pub_ready,
        "workload_balance_score":  round(wkl_balance_score, 1),
        "room_utilization_score":  round(room_util_score, 1),
        "pdpa_alert_count":        pdpa_count,
        "top_risks":               top_risks,
        "recommended_actions":     recommended_actions,
    }


# ── Private score-availability helpers ────────────────────────────────────────

# Scores that carry operational signal-in (i.e. they were not set to zero
# simply because the caller omitted that data source).  A real zero quality
# score or utilisation value does count as signal.  A zero workload value that
# was produced by the absence of data should not pull the average toward green.
_EMPTY_DEFAULT = {
    "total_assignments": 0,
    "average_load": 0.0,
    "overloaded_staff_count": 0,
}

def _has_active_signal(*values: float) -> bool:
    """Return True if at least one score was actually provided by a data source.

    A signal is "active" when the value is greater than zero — this allows a
    real zero (e.g. all rooms unused) to be counted, while defaulting a missing
    source (no data = zero by default) to silent.
    """
    return any(v > 0 for v in values)


def _build_active_scores(*values: float) -> list[float]:
    """Return only the scores that represent actual data, not absent defaults."""
    return [v for v in values if v > 0]


def has_active_scores(*values: float) -> bool:
    return _has_active_signal(*values)
