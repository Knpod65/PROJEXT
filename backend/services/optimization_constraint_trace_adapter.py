"""Pure adapters that normalize constraint outcomes into trace events."""
from __future__ import annotations

from typing import Any

from services.optimization_trace_context import (
    OptimizationTraceContext,
    TRACE_SOURCE_INPUT,
    TRACE_SOURCE_POLICY,
)

CONSTRAINT_TYPE_HARD = "HARD"
CONSTRAINT_TYPE_SOFT = "SOFT"
CONSTRAINT_TYPE_GOVERNANCE = "GOVERNANCE"

SEVERITY_HARD_FAIL = "HARD_FAIL"
SEVERITY_WARNING = "WARNING"
SEVERITY_INFO = "INFO"
SEVERITY_SUGGESTION = "SUGGESTION"

CONSTRAINT_CODE_CAPACITY = "ROOM_CAPACITY"
CONSTRAINT_CODE_STAFFING = "STAFFING_AVAILABILITY"
CONSTRAINT_CODE_ROOM_CONFLICT = "ROOM_CONFLICT"
CONSTRAINT_CODE_STUDENT_CONFLICT = "STUDENT_CONFLICT"
CONSTRAINT_CODE_FAIRNESS = "FAIRNESS_BALANCE"
CONSTRAINT_CODE_DOCUMENT_READINESS = "DOCUMENT_READINESS"
CONSTRAINT_CODE_QR_READINESS = "QR_READINESS"


def _severity_for_constraint(
    *,
    constraint_type: str,
    passed: bool,
    severity: str | None = None,
) -> str:
    if passed:
        return severity or SEVERITY_INFO
    if constraint_type == CONSTRAINT_TYPE_HARD:
        return SEVERITY_HARD_FAIL
    return severity or SEVERITY_WARNING


def _constraint_metadata(
    *,
    constraint_code: str,
    constraint_type: str,
    passed: bool,
    severity: str,
    entity_type: str,
    entity_id: Any,
    reason_code: str | None = None,
    score_delta: float | int | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(metadata or {})
    payload.update({
        "constraint_code": constraint_code,
        "constraint_type": constraint_type,
        "passed": bool(passed),
        "severity": severity,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "reason_code": reason_code,
        "score_delta": float(score_delta) if score_delta is not None else None,
    })
    return payload


def _default_message(
    *,
    constraint_code: str,
    passed: bool,
    constraint_type: str,
) -> str:
    if passed:
        return f"{constraint_type} constraint {constraint_code} passed."
    return f"{constraint_type} constraint {constraint_code} failed."


def _trace_constraint(
    context: OptimizationTraceContext,
    *,
    constraint_code: str,
    constraint_type: str,
    passed: bool,
    entity_type: str,
    entity_id: Any,
    reason_code: str | None = None,
    score_delta: float | int | None = None,
    severity: str | None = None,
    source: str = TRACE_SOURCE_INPUT,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_severity = _severity_for_constraint(
        constraint_type=constraint_type,
        passed=passed,
        severity=severity,
    )
    return context.add_constraint_triggered(
        entity_type=entity_type,
        entity_id=entity_id,
        constraint_code=constraint_code,
        reason_code=reason_code,
        score_delta=score_delta,
        severity=resolved_severity,
        source=source,
        message=message or _default_message(
            constraint_code=constraint_code,
            passed=passed,
            constraint_type=constraint_type,
        ),
        metadata=_constraint_metadata(
            constraint_code=constraint_code,
            constraint_type=constraint_type,
            passed=passed,
            severity=resolved_severity,
            entity_type=entity_type,
            entity_id=entity_id,
            reason_code=reason_code,
            score_delta=score_delta,
            metadata=metadata,
        ),
    )


def trace_hard_constraint(
    context: OptimizationTraceContext,
    *,
    constraint_code: str,
    passed: bool,
    entity_type: str,
    entity_id: Any,
    reason_code: str | None = None,
    score_delta: float | int | None = None,
    severity: str | None = None,
    source: str = TRACE_SOURCE_INPUT,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _trace_constraint(
        context,
        constraint_code=constraint_code,
        constraint_type=CONSTRAINT_TYPE_HARD,
        passed=passed,
        entity_type=entity_type,
        entity_id=entity_id,
        reason_code=reason_code,
        score_delta=score_delta,
        severity=severity,
        source=source,
        message=message,
        metadata=metadata,
    )


def trace_soft_constraint(
    context: OptimizationTraceContext,
    *,
    constraint_code: str,
    passed: bool,
    entity_type: str,
    entity_id: Any,
    reason_code: str | None = None,
    score_delta: float | int | None = None,
    severity: str | None = None,
    source: str = TRACE_SOURCE_INPUT,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _trace_constraint(
        context,
        constraint_code=constraint_code,
        constraint_type=CONSTRAINT_TYPE_SOFT,
        passed=passed,
        entity_type=entity_type,
        entity_id=entity_id,
        reason_code=reason_code,
        score_delta=score_delta,
        severity=severity,
        source=source,
        message=message,
        metadata=metadata,
    )


def trace_capacity_constraint(
    context: OptimizationTraceContext,
    *,
    passed: bool,
    entity_type: str,
    entity_id: Any,
    reason_code: str | None = None,
    score_delta: float | int | None = None,
    severity: str | None = None,
    source: str = TRACE_SOURCE_INPUT,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return trace_hard_constraint(
        context,
        constraint_code=CONSTRAINT_CODE_CAPACITY,
        passed=passed,
        entity_type=entity_type,
        entity_id=entity_id,
        reason_code=reason_code,
        score_delta=score_delta,
        severity=severity,
        source=source,
        message=message,
        metadata=metadata,
    )


def trace_staffing_constraint(
    context: OptimizationTraceContext,
    *,
    passed: bool,
    entity_type: str,
    entity_id: Any,
    reason_code: str | None = None,
    score_delta: float | int | None = None,
    severity: str | None = None,
    source: str = TRACE_SOURCE_INPUT,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return trace_hard_constraint(
        context,
        constraint_code=CONSTRAINT_CODE_STAFFING,
        passed=passed,
        entity_type=entity_type,
        entity_id=entity_id,
        reason_code=reason_code,
        score_delta=score_delta,
        severity=severity,
        source=source,
        message=message,
        metadata=metadata,
    )


def trace_room_conflict_constraint(
    context: OptimizationTraceContext,
    *,
    passed: bool,
    entity_type: str,
    entity_id: Any,
    reason_code: str | None = None,
    score_delta: float | int | None = None,
    severity: str | None = None,
    source: str = TRACE_SOURCE_INPUT,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return trace_hard_constraint(
        context,
        constraint_code=CONSTRAINT_CODE_ROOM_CONFLICT,
        passed=passed,
        entity_type=entity_type,
        entity_id=entity_id,
        reason_code=reason_code,
        score_delta=score_delta,
        severity=severity,
        source=source,
        message=message,
        metadata=metadata,
    )


def trace_student_conflict_constraint(
    context: OptimizationTraceContext,
    *,
    passed: bool,
    entity_type: str,
    entity_id: Any,
    reason_code: str | None = None,
    score_delta: float | int | None = None,
    severity: str | None = None,
    source: str = TRACE_SOURCE_INPUT,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return trace_hard_constraint(
        context,
        constraint_code=CONSTRAINT_CODE_STUDENT_CONFLICT,
        passed=passed,
        entity_type=entity_type,
        entity_id=entity_id,
        reason_code=reason_code,
        score_delta=score_delta,
        severity=severity,
        source=source,
        message=message,
        metadata=metadata,
    )


def trace_fairness_constraint(
    context: OptimizationTraceContext,
    *,
    passed: bool,
    entity_type: str,
    entity_id: Any,
    reason_code: str | None = None,
    score_delta: float | int | None = None,
    severity: str | None = None,
    source: str = TRACE_SOURCE_INPUT,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return trace_soft_constraint(
        context,
        constraint_code=CONSTRAINT_CODE_FAIRNESS,
        passed=passed,
        entity_type=entity_type,
        entity_id=entity_id,
        reason_code=reason_code,
        score_delta=score_delta,
        severity=severity,
        source=source,
        message=message,
        metadata=metadata,
    )


def trace_document_readiness_constraint(
    context: OptimizationTraceContext,
    *,
    passed: bool,
    entity_type: str,
    entity_id: Any,
    reason_code: str | None = None,
    score_delta: float | int | None = None,
    severity: str | None = None,
    source: str = TRACE_SOURCE_POLICY,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _trace_constraint(
        context,
        constraint_code=CONSTRAINT_CODE_DOCUMENT_READINESS,
        constraint_type=CONSTRAINT_TYPE_GOVERNANCE,
        passed=passed,
        entity_type=entity_type,
        entity_id=entity_id,
        reason_code=reason_code,
        score_delta=score_delta,
        severity=severity,
        source=source,
        message=message,
        metadata=metadata,
    )


def trace_qr_readiness_constraint(
    context: OptimizationTraceContext,
    *,
    passed: bool,
    entity_type: str,
    entity_id: Any,
    reason_code: str | None = None,
    score_delta: float | int | None = None,
    severity: str | None = None,
    source: str = TRACE_SOURCE_POLICY,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _trace_constraint(
        context,
        constraint_code=CONSTRAINT_CODE_QR_READINESS,
        constraint_type=CONSTRAINT_TYPE_GOVERNANCE,
        passed=passed,
        entity_type=entity_type,
        entity_id=entity_id,
        reason_code=reason_code,
        score_delta=score_delta,
        severity=severity,
        source=source,
        message=message,
        metadata=metadata,
    )
