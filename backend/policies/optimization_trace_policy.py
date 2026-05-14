"""Policy definitions for optimization trace events.

Defines the canonical set of trace event types, source labels, severity levels,
and a PII-stripping guard that must be applied to all trace metadata before
the event is serialized or transmitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TraceEventType(str, Enum):
    OPTIMIZATION_STARTED = "OPTIMIZATION_STARTED"
    CANDIDATE_GENERATED = "CANDIDATE_GENERATED"
    CANDIDATE_REJECTED = "CANDIDATE_REJECTED"
    CANDIDATE_SCORED = "CANDIDATE_SCORED"
    CONSTRAINT_APPLIED = "CONSTRAINT_APPLIED"
    PENALTY_APPLIED = "PENALTY_APPLIED"
    ROOM_SELECTED = "ROOM_SELECTED"
    STAFF_SELECTED = "STAFF_SELECTED"
    DISTRIBUTOR_SELECTED = "DISTRIBUTOR_SELECTED"
    SPLIT_DECISION_MADE = "SPLIT_DECISION_MADE"
    FALLBACK_USED = "FALLBACK_USED"
    FINAL_SELECTION_ACCEPTED = "FINAL_SELECTION_ACCEPTED"
    RECHECK_STARTED = "RECHECK_STARTED"
    RECHECK_COMPLETED = "RECHECK_COMPLETED"
    GOVERNANCE_DECISION_CREATED = "GOVERNANCE_DECISION_CREATED"


class TraceSource(str, Enum):
    POST_HOC_TRACE = "POST_HOC_TRACE"   # wrapped from existing service output
    POLICY_RULE = "POLICY_RULE"          # produced by a named policy rule
    SOLVER_TRACE = "SOLVER_TRACE"        # reserved for native CP-SAT instrumentation


class TraceSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH_RISK = "HIGH_RISK"


# Keys forbidden from appearing in any trace metadata payload.
_PII_BLOCKED_KEYS: frozenset[str] = frozenset({
    "student_id",
    "student_ids",
    "student_name",
    "student_names",
    "teacher_name",
    "email",
    "mobile",
})


@dataclass(frozen=True)
class TraceEvent:
    event_type: str
    entity_type: str | None
    entity_id: Any
    constraint_code: str | None
    reason_code: str | None
    score_delta: float | None
    severity: str
    source: str
    metadata: dict[str, Any]
    timestamp: str


def strip_pii(metadata: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of metadata with all PII-sensitive keys removed."""
    return {k: v for k, v in metadata.items() if k not in _PII_BLOCKED_KEYS}


def is_safe_metadata(metadata: dict[str, Any]) -> bool:
    """Return True only if metadata contains no PII-blocked keys."""
    return not (_PII_BLOCKED_KEYS & metadata.keys())
