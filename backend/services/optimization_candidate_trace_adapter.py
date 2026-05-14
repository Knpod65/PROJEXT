"""Pure adapters that project candidate decisions into native trace events."""
from __future__ import annotations

from typing import Any

from events.optimization_events import STAGE_SELECTION
from services.optimization_trace_context import (
    OptimizationTraceContext,
    TRACE_SOURCE_SOLVER,
)

CANDIDATE_TYPE_ROOM = "ROOM"
CANDIDATE_TYPE_STAFF = "STAFF"
CANDIDATE_TYPE_TIMESLOT = "TIMESLOT"
CANDIDATE_TYPE_SPLIT = "SPLIT"

REASON_CODE_CAPACITY_TOO_LOW = "CAPACITY_TOO_LOW"
REASON_CODE_ROOM_UNAVAILABLE = "ROOM_UNAVAILABLE"
REASON_CODE_ROOM_ALREADY_ASSIGNED = "ROOM_ALREADY_ASSIGNED"
REASON_CODE_WALKING_DISTANCE_PENALTY = "WALKING_DISTANCE_PENALTY"
REASON_CODE_BUILDING_SPREAD_PENALTY = "BUILDING_SPREAD_PENALTY"
REASON_CODE_STAFF_OVERLOAD = "STAFF_OVERLOAD"
REASON_CODE_STAFF_UNAVAILABLE = "STAFF_UNAVAILABLE"
REASON_CODE_STAFF_ALREADY_ASSIGNED = "STAFF_ALREADY_ASSIGNED"
REASON_CODE_TIMESLOT_CONFLICT = "TIMESLOT_CONFLICT"
REASON_CODE_SPLIT_REQUIRED = "SPLIT_REQUIRED"
REASON_CODE_SPLIT_TOO_MANY_ROOMS = "SPLIT_TOO_MANY_ROOMS"
REASON_CODE_FAIRNESS_PENALTY = "FAIRNESS_PENALTY"
REASON_CODE_FALLBACK_USED = "FALLBACK_USED"


def _base_candidate_metadata(
    *,
    metadata: dict[str, Any] | None = None,
    capacity: int | None = None,
    assigned_count: int | None = None,
    utilization_ratio: float | None = None,
    building: str | None = None,
    floor: str | int | None = None,
    room_type: str | None = None,
    staff_current_load: int | None = None,
    staff_role: str | None = None,
    time_slot: str | None = None,
    reason_code: str | None = None,
) -> dict[str, Any]:
    candidate_metadata = dict(metadata or {})
    if capacity is not None:
        candidate_metadata["capacity"] = capacity
    if assigned_count is not None:
        candidate_metadata["assigned_count"] = assigned_count
    if utilization_ratio is None and capacity and assigned_count is not None:
        utilization_ratio = round(assigned_count / capacity, 4)
    if utilization_ratio is not None:
        candidate_metadata["utilization_ratio"] = float(utilization_ratio)
    if building is not None:
        candidate_metadata["building"] = building
    if floor is not None:
        candidate_metadata["floor"] = floor
    if room_type is not None:
        candidate_metadata["room_type"] = room_type
    if staff_current_load is not None:
        candidate_metadata["staff_current_load"] = staff_current_load
    if staff_role is not None:
        candidate_metadata["staff_role"] = staff_role
    if time_slot is not None:
        candidate_metadata["time_slot"] = time_slot
    if reason_code is not None:
        candidate_metadata["reason_code"] = reason_code
    return candidate_metadata


def _trace_generated_candidate(
    context: OptimizationTraceContext,
    *,
    candidate_type: str,
    entity_type: str,
    entity_id: Any,
    candidate_id: Any,
    reason_code: str | None = None,
    source: str = TRACE_SOURCE_SOLVER,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
    capacity: int | None = None,
    assigned_count: int | None = None,
    utilization_ratio: float | None = None,
    building: str | None = None,
    floor: str | int | None = None,
    room_type: str | None = None,
    staff_current_load: int | None = None,
    staff_role: str | None = None,
    time_slot: str | None = None,
) -> dict[str, Any]:
    return context.add_candidate_generated(
        entity_type=entity_type,
        entity_id=entity_id,
        candidate_type=candidate_type,
        candidate_id=candidate_id,
        reason_code=reason_code,
        source=source,
        message=message,
        metadata=_base_candidate_metadata(
            metadata=metadata,
            capacity=capacity,
            assigned_count=assigned_count,
            utilization_ratio=utilization_ratio,
            building=building,
            floor=floor,
            room_type=room_type,
            staff_current_load=staff_current_load,
            staff_role=staff_role,
            time_slot=time_slot,
            reason_code=reason_code,
        ),
    )


def trace_room_candidate(
    context: OptimizationTraceContext,
    *,
    entity_type: str,
    entity_id: Any,
    candidate_id: Any,
    reason_code: str | None = None,
    source: str = TRACE_SOURCE_SOLVER,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
    capacity: int | None = None,
    assigned_count: int | None = None,
    utilization_ratio: float | None = None,
    building: str | None = None,
    floor: str | int | None = None,
    room_type: str | None = None,
) -> dict[str, Any]:
    return _trace_generated_candidate(
        context,
        candidate_type=CANDIDATE_TYPE_ROOM,
        entity_type=entity_type,
        entity_id=entity_id,
        candidate_id=candidate_id,
        reason_code=reason_code,
        source=source,
        message=message,
        metadata=metadata,
        capacity=capacity,
        assigned_count=assigned_count,
        utilization_ratio=utilization_ratio,
        building=building,
        floor=floor,
        room_type=room_type,
    )


def trace_staff_candidate(
    context: OptimizationTraceContext,
    *,
    entity_type: str,
    entity_id: Any,
    candidate_id: Any,
    reason_code: str | None = None,
    source: str = TRACE_SOURCE_SOLVER,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
    staff_current_load: int | None = None,
    staff_role: str | None = None,
    assigned_count: int | None = None,
    time_slot: str | None = None,
) -> dict[str, Any]:
    return _trace_generated_candidate(
        context,
        candidate_type=CANDIDATE_TYPE_STAFF,
        entity_type=entity_type,
        entity_id=entity_id,
        candidate_id=candidate_id,
        reason_code=reason_code,
        source=source,
        message=message,
        metadata=metadata,
        assigned_count=assigned_count,
        staff_current_load=staff_current_load,
        staff_role=staff_role,
        time_slot=time_slot,
    )


def trace_timeslot_candidate(
    context: OptimizationTraceContext,
    *,
    entity_type: str,
    entity_id: Any,
    candidate_id: Any,
    reason_code: str | None = None,
    source: str = TRACE_SOURCE_SOLVER,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
    time_slot: str | None = None,
    assigned_count: int | None = None,
) -> dict[str, Any]:
    return _trace_generated_candidate(
        context,
        candidate_type=CANDIDATE_TYPE_TIMESLOT,
        entity_type=entity_type,
        entity_id=entity_id,
        candidate_id=candidate_id,
        reason_code=reason_code,
        source=source,
        message=message,
        metadata=metadata,
        assigned_count=assigned_count,
        time_slot=time_slot or str(candidate_id),
    )


def trace_split_candidate(
    context: OptimizationTraceContext,
    *,
    entity_type: str,
    entity_id: Any,
    candidate_id: Any,
    reason_code: str | None = None,
    source: str = TRACE_SOURCE_SOLVER,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
    assigned_count: int | None = None,
) -> dict[str, Any]:
    return _trace_generated_candidate(
        context,
        candidate_type=CANDIDATE_TYPE_SPLIT,
        entity_type=entity_type,
        entity_id=entity_id,
        candidate_id=candidate_id,
        reason_code=reason_code,
        source=source,
        message=message,
        metadata=metadata,
        assigned_count=assigned_count,
    )


def trace_rejected_candidate(
    context: OptimizationTraceContext,
    *,
    entity_type: str,
    entity_id: Any,
    candidate_type: str,
    candidate_id: Any,
    reason_code: str,
    severity: str = "WARNING",
    constraint_code: str | None = None,
    source: str = TRACE_SOURCE_SOLVER,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
    capacity: int | None = None,
    assigned_count: int | None = None,
    utilization_ratio: float | None = None,
    building: str | None = None,
    floor: str | int | None = None,
    room_type: str | None = None,
    staff_current_load: int | None = None,
    staff_role: str | None = None,
    time_slot: str | None = None,
) -> dict[str, Any]:
    return context.add_candidate_rejected(
        entity_type=entity_type,
        entity_id=entity_id,
        candidate_type=candidate_type,
        candidate_id=candidate_id,
        constraint_code=constraint_code,
        reason_code=reason_code,
        severity=severity,
        source=source,
        message=message,
        metadata=_base_candidate_metadata(
            metadata=metadata,
            capacity=capacity,
            assigned_count=assigned_count,
            utilization_ratio=utilization_ratio,
            building=building,
            floor=floor,
            room_type=room_type,
            staff_current_load=staff_current_load,
            staff_role=staff_role,
            time_slot=time_slot,
            reason_code=reason_code,
        ),
    )


def trace_accepted_candidate(
    context: OptimizationTraceContext,
    *,
    entity_type: str,
    entity_id: Any,
    candidate_type: str,
    candidate_id: Any,
    reason_code: str | None = None,
    source: str = TRACE_SOURCE_SOLVER,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
    capacity: int | None = None,
    assigned_count: int | None = None,
    utilization_ratio: float | None = None,
    building: str | None = None,
    floor: str | int | None = None,
    room_type: str | None = None,
    staff_current_load: int | None = None,
    staff_role: str | None = None,
    time_slot: str | None = None,
    stage: str = STAGE_SELECTION,
) -> dict[str, Any]:
    return context.add_candidate_accepted(
        entity_type=entity_type,
        entity_id=entity_id,
        candidate_type=candidate_type,
        candidate_id=candidate_id,
        reason_code=reason_code,
        source=source,
        message=message,
        stage=stage,
        metadata=_base_candidate_metadata(
            metadata=metadata,
            capacity=capacity,
            assigned_count=assigned_count,
            utilization_ratio=utilization_ratio,
            building=building,
            floor=floor,
            room_type=room_type,
            staff_current_load=staff_current_load,
            staff_role=staff_role,
            time_slot=time_slot,
            reason_code=reason_code,
        ),
    )
