"""Pure adapters for native selection and final acceptance trace events."""
from __future__ import annotations

from typing import Any

from services.optimization_candidate_trace_adapter import (
    CANDIDATE_TYPE_ROOM,
    CANDIDATE_TYPE_SPLIT,
    CANDIDATE_TYPE_STAFF,
)
from services.optimization_trace_context import (
    OptimizationTraceContext,
    TRACE_SOURCE_SOLVER,
)

CANDIDATE_TYPE_DISTRIBUTOR = "DISTRIBUTOR"
CANDIDATE_TYPE_SCHEDULE = "SCHEDULE"


def _selection_metadata(
    *,
    selected_candidate: Any,
    accepted_reason: str | None,
    tradeoffs_accepted: list[str] | tuple[str, ...] | None = None,
    contributing_constraints: list[str] | tuple[str, ...] | None = None,
    quality_impact: dict[str, Any] | None = None,
    governance_relevance: str | None = None,
    confidence_level: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(metadata or {})
    payload.update({
        "selected_candidate": selected_candidate,
        "accepted_reason": accepted_reason,
        "tradeoffs_accepted": list(tradeoffs_accepted or []),
        "contributing_constraints": list(contributing_constraints or []),
        "quality_impact": dict(quality_impact or {}),
        "governance_relevance": governance_relevance,
        "confidence_level": confidence_level,
    })
    return payload


def _selection_message(
    *,
    candidate_type: str,
    accepted_reason: str | None,
    message: str | None = None,
) -> str:
    if message:
        return message
    if accepted_reason:
        return f"{candidate_type} selection accepted because {accepted_reason}."
    return f"{candidate_type} selection accepted."


def _trace_selection(
    context: OptimizationTraceContext,
    *,
    candidate_type: str,
    entity_type: str,
    entity_id: Any,
    candidate_id: Any,
    selected_candidate: Any,
    accepted_reason: str | None = None,
    tradeoffs_accepted: list[str] | tuple[str, ...] | None = None,
    contributing_constraints: list[str] | tuple[str, ...] | None = None,
    quality_impact: dict[str, Any] | None = None,
    governance_relevance: str | None = None,
    confidence_level: str | None = None,
    source: str = TRACE_SOURCE_SOLVER,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return context.add_candidate_accepted(
        entity_type=entity_type,
        entity_id=entity_id,
        candidate_type=candidate_type,
        candidate_id=candidate_id,
        reason_code=accepted_reason,
        source=source,
        message=_selection_message(
            candidate_type=candidate_type,
            accepted_reason=accepted_reason,
            message=message,
        ),
        metadata=_selection_metadata(
            selected_candidate=selected_candidate,
            accepted_reason=accepted_reason,
            tradeoffs_accepted=tradeoffs_accepted,
            contributing_constraints=contributing_constraints,
            quality_impact=quality_impact,
            governance_relevance=governance_relevance,
            confidence_level=confidence_level,
            metadata=metadata,
        ),
    )


def trace_room_selection(
    context: OptimizationTraceContext,
    *,
    entity_type: str,
    entity_id: Any,
    candidate_id: Any,
    selected_candidate: Any,
    accepted_reason: str | None = None,
    tradeoffs_accepted: list[str] | tuple[str, ...] | None = None,
    contributing_constraints: list[str] | tuple[str, ...] | None = None,
    quality_impact: dict[str, Any] | None = None,
    governance_relevance: str | None = None,
    confidence_level: str | None = None,
    source: str = TRACE_SOURCE_SOLVER,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _trace_selection(
        context,
        candidate_type=CANDIDATE_TYPE_ROOM,
        entity_type=entity_type,
        entity_id=entity_id,
        candidate_id=candidate_id,
        selected_candidate=selected_candidate,
        accepted_reason=accepted_reason,
        tradeoffs_accepted=tradeoffs_accepted,
        contributing_constraints=contributing_constraints,
        quality_impact=quality_impact,
        governance_relevance=governance_relevance,
        confidence_level=confidence_level,
        source=source,
        message=message,
        metadata=metadata,
    )


def trace_staff_selection(
    context: OptimizationTraceContext,
    *,
    entity_type: str,
    entity_id: Any,
    candidate_id: Any,
    selected_candidate: Any,
    accepted_reason: str | None = None,
    tradeoffs_accepted: list[str] | tuple[str, ...] | None = None,
    contributing_constraints: list[str] | tuple[str, ...] | None = None,
    quality_impact: dict[str, Any] | None = None,
    governance_relevance: str | None = None,
    confidence_level: str | None = None,
    source: str = TRACE_SOURCE_SOLVER,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _trace_selection(
        context,
        candidate_type=CANDIDATE_TYPE_STAFF,
        entity_type=entity_type,
        entity_id=entity_id,
        candidate_id=candidate_id,
        selected_candidate=selected_candidate,
        accepted_reason=accepted_reason,
        tradeoffs_accepted=tradeoffs_accepted,
        contributing_constraints=contributing_constraints,
        quality_impact=quality_impact,
        governance_relevance=governance_relevance,
        confidence_level=confidence_level,
        source=source,
        message=message,
        metadata=metadata,
    )


def trace_distribution_selection(
    context: OptimizationTraceContext,
    *,
    entity_type: str,
    entity_id: Any,
    candidate_id: Any,
    selected_candidate: Any,
    accepted_reason: str | None = None,
    tradeoffs_accepted: list[str] | tuple[str, ...] | None = None,
    contributing_constraints: list[str] | tuple[str, ...] | None = None,
    quality_impact: dict[str, Any] | None = None,
    governance_relevance: str | None = None,
    confidence_level: str | None = None,
    source: str = TRACE_SOURCE_SOLVER,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _trace_selection(
        context,
        candidate_type=CANDIDATE_TYPE_DISTRIBUTOR,
        entity_type=entity_type,
        entity_id=entity_id,
        candidate_id=candidate_id,
        selected_candidate=selected_candidate,
        accepted_reason=accepted_reason,
        tradeoffs_accepted=tradeoffs_accepted,
        contributing_constraints=contributing_constraints,
        quality_impact=quality_impact,
        governance_relevance=governance_relevance,
        confidence_level=confidence_level,
        source=source,
        message=message,
        metadata=metadata,
    )


def trace_split_selection(
    context: OptimizationTraceContext,
    *,
    entity_type: str,
    entity_id: Any,
    candidate_id: Any,
    selected_candidate: Any,
    accepted_reason: str | None = None,
    tradeoffs_accepted: list[str] | tuple[str, ...] | None = None,
    contributing_constraints: list[str] | tuple[str, ...] | None = None,
    quality_impact: dict[str, Any] | None = None,
    governance_relevance: str | None = None,
    confidence_level: str | None = None,
    source: str = TRACE_SOURCE_SOLVER,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _trace_selection(
        context,
        candidate_type=CANDIDATE_TYPE_SPLIT,
        entity_type=entity_type,
        entity_id=entity_id,
        candidate_id=candidate_id,
        selected_candidate=selected_candidate,
        accepted_reason=accepted_reason,
        tradeoffs_accepted=tradeoffs_accepted,
        contributing_constraints=contributing_constraints,
        quality_impact=quality_impact,
        governance_relevance=governance_relevance,
        confidence_level=confidence_level,
        source=source,
        message=message,
        metadata=metadata,
    )


def trace_final_schedule_selection(
    context: OptimizationTraceContext,
    *,
    entity_type: str,
    entity_id: Any,
    candidate_id: Any,
    selected_candidate: Any,
    accepted_reason: str | None = None,
    tradeoffs_accepted: list[str] | tuple[str, ...] | None = None,
    contributing_constraints: list[str] | tuple[str, ...] | None = None,
    quality_impact: dict[str, Any] | None = None,
    governance_relevance: str | None = None,
    confidence_level: str | None = None,
    source: str = TRACE_SOURCE_SOLVER,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return context.add_final_selection(
        entity_type=entity_type,
        entity_id=entity_id,
        candidate_type=CANDIDATE_TYPE_SCHEDULE,
        candidate_id=candidate_id,
        reason_code=accepted_reason,
        source=source,
        message=_selection_message(
            candidate_type=CANDIDATE_TYPE_SCHEDULE,
            accepted_reason=accepted_reason,
            message=message,
        ),
        metadata=_selection_metadata(
            selected_candidate=selected_candidate,
            accepted_reason=accepted_reason,
            tradeoffs_accepted=tradeoffs_accepted,
            contributing_constraints=contributing_constraints,
            quality_impact=quality_impact,
            governance_relevance=governance_relevance,
            confidence_level=confidence_level,
            metadata=metadata,
        ),
    )
