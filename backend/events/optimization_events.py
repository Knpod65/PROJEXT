"""Typed event type constants for the optimization domain.

These enums define every event type that can be emitted through the
InMemoryEventBus (event_service.py) by optimization-related services.
Use these constants as the `event_type` argument to `event_service.emit()`.

Source authority: this file owns the optimization event type vocabulary.
Do not define optimization event strings inline elsewhere.
"""
from __future__ import annotations

from enum import Enum


class OptimizationEventType(str, Enum):
    """All event types emitted in the optimization domain."""

    OPTIMIZATION_STARTED = "OPTIMIZATION_STARTED"
    OPTIMIZATION_FINISHED = "OPTIMIZATION_FINISHED"

    # Candidate selection events
    ROOM_CANDIDATE_REJECTED = "ROOM_CANDIDATE_REJECTED"
    ROOM_CANDIDATE_ACCEPTED = "ROOM_CANDIDATE_ACCEPTED"
    INVIGILATOR_REJECTED = "INVIGILATOR_REJECTED"
    INVIGILATOR_ACCEPTED = "INVIGILATOR_ACCEPTED"
    TIMESLOT_REJECTED = "TIMESLOT_REJECTED"
    TIMESLOT_ACCEPTED = "TIMESLOT_ACCEPTED"

    # Constraint events
    CONSTRAINT_TRIGGERED = "CONSTRAINT_TRIGGERED"
    HARD_CONSTRAINT_FAILED = "HARD_CONSTRAINT_FAILED"
    SOFT_CONSTRAINT_PENALIZED = "SOFT_CONSTRAINT_PENALIZED"

    # Quality events
    QUALITY_SCORE_ADJUSTED = "QUALITY_SCORE_ADJUSTED"

    # Structural events
    ROOM_SPLIT_APPLIED = "ROOM_SPLIT_APPLIED"

    # Governance events
    GOVERNANCE_ESCALATED = "GOVERNANCE_ESCALATED"
    RECHECK_WARNING_GENERATED = "RECHECK_WARNING_GENERATED"


# Domain identifier — use as `domain` argument to event_service.emit()
OPTIMIZATION_DOMAIN = "optimization"

# Optimization stage identifiers
STAGE_CANDIDATE_GENERATION = "CANDIDATE_GENERATION"
STAGE_CONSTRAINT_EVALUATION = "CONSTRAINT_EVALUATION"
STAGE_SCORING = "SCORING"
STAGE_SELECTION = "SELECTION"
STAGE_RECHECK = "RECHECK"
STAGE_GOVERNANCE = "GOVERNANCE"
STAGE_UNKNOWN = "UNKNOWN"
