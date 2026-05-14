"""Constraint trace service for optimization recheck output.

Builds structured ConstraintTrace objects from recheck issues. Each recheck
issue maps to one constraint trace: which constraint fired, whether it blocked,
severity, and stage. All data is read from recheck output — post-hoc, additive,
read-only. No solver changes.

Data source: `issues` list in the output of `build_recheck_report()` from
optimization_recheck_service.py.
"""
from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from events.optimization_events import OPTIMIZATION_DOMAIN, STAGE_RECHECK


@dataclass(frozen=True)
class ConstraintTrace:
    """Structured record of a single constraint evaluation outcome."""

    trace_id: str
    constraint_name: str
    triggered: bool               # True = constraint fired (violation detected)
    severity: str                 # "HARD_FAIL" | "WARNING" | "INFO" | "SUGGESTION"
    optimization_stage: str       # which optimizer stage this applies to
    message: str
    category: str | None          # from recheck issue category
    blocking: bool                # True = this constraint blocks publish/approve
    domain: str
    audit_metadata: dict
    timestamp: str                # ISO 8601 UTC


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _trace_id() -> str:
    return str(uuid.uuid4())


_SEVERITY_BLOCKING: dict[str, bool] = {
    "HARD_FAIL": True,
    "WARNING": False,
    "INFO": False,
    "SUGGESTION": False,
}

_SEVERITY_NORMALIZED: dict[str, str] = {
    "HARD_FAIL": "HARD_FAIL",
    "hard_fail": "HARD_FAIL",
    "ERROR": "HARD_FAIL",
    "error": "HARD_FAIL",
    "WARNING": "WARNING",
    "warning": "WARNING",
    "WARN": "WARNING",
    "INFO": "INFO",
    "info": "INFO",
    "SUGGESTION": "SUGGESTION",
    "suggestion": "SUGGESTION",
    "SUGGEST": "SUGGESTION",
}


def _normalize_severity(raw: str | None) -> str:
    if not raw:
        return "INFO"
    return _SEVERITY_NORMALIZED.get(raw, raw.upper())


def build_constraint_traces(
    recheck_issues: list[dict[str, Any]],
    *,
    optimization_stage: str = STAGE_RECHECK,
) -> list[ConstraintTrace]:
    """Build one ConstraintTrace per recheck issue.

    Args:
        recheck_issues: list of issue dicts from build_recheck_report().
                        Each dict typically has: code, severity, category,
                        message, blocking, section_id.
        optimization_stage: override the stage label (defaults to RECHECK).

    Returns:
        List of ConstraintTrace — one per issue.
    """
    traces: list[ConstraintTrace] = []
    timestamp = _now_iso()

    for issue in recheck_issues:
        if not isinstance(issue, dict):
            continue
        code = issue.get("code") or issue.get("constraint_code") or "UNKNOWN_CONSTRAINT"
        raw_severity = issue.get("severity")
        severity = _normalize_severity(raw_severity)
        blocking = bool(issue.get("blocking")) or _SEVERITY_BLOCKING.get(severity, False)
        message = issue.get("message") or ""
        category = issue.get("category")

        audit_metadata: dict[str, Any] = {}
        if issue.get("section_id") is not None:
            audit_metadata["section_id"] = issue["section_id"]
        if issue.get("course_id") is not None:
            audit_metadata["course_id"] = issue["course_id"]

        traces.append(ConstraintTrace(
            trace_id=_trace_id(),
            constraint_name=code,
            triggered=True,           # recheck only reports triggered constraints
            severity=severity,
            optimization_stage=optimization_stage,
            message=message,
            category=category,
            blocking=blocking,
            domain=OPTIMIZATION_DOMAIN,
            audit_metadata=audit_metadata,
            timestamp=timestamp,
        ))

    return traces


def build_constraint_summary(
    traces: list[ConstraintTrace],
) -> dict[str, Any]:
    """Summarize constraint traces into aggregate counts."""
    total = len(traces)
    hard_fails = sum(1 for t in traces if t.severity == "HARD_FAIL")
    warnings = sum(1 for t in traces if t.severity == "WARNING")
    blocking = sum(1 for t in traces if t.blocking)

    return {
        "total_constraints_triggered": total,
        "hard_fail_count": hard_fails,
        "warning_count": warnings,
        "blocking_count": blocking,
        "all_pass": total == 0,
    }


def constraint_traces_to_dicts(traces: list[ConstraintTrace]) -> list[dict[str, Any]]:
    """Serialize ConstraintTrace objects to plain dicts."""
    return [asdict(t) for t in traces]
