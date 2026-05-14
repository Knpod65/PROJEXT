"""Tests for optimization_constraint_trace_adapter.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_constraint_trace_adapter import (
    CONSTRAINT_CODE_CAPACITY,
    CONSTRAINT_CODE_DOCUMENT_READINESS,
    CONSTRAINT_CODE_FAIRNESS,
    CONSTRAINT_CODE_QR_READINESS,
    CONSTRAINT_CODE_ROOM_CONFLICT,
    CONSTRAINT_CODE_STAFFING,
    CONSTRAINT_CODE_STUDENT_CONFLICT,
    CONSTRAINT_TYPE_GOVERNANCE,
    CONSTRAINT_TYPE_HARD,
    CONSTRAINT_TYPE_SOFT,
    SEVERITY_HARD_FAIL,
    SEVERITY_INFO,
    SEVERITY_SUGGESTION,
    SEVERITY_WARNING,
    trace_capacity_constraint,
    trace_document_readiness_constraint,
    trace_fairness_constraint,
    trace_hard_constraint,
    trace_qr_readiness_constraint,
    trace_room_conflict_constraint,
    trace_soft_constraint,
    trace_staffing_constraint,
    trace_student_conflict_constraint,
)
from services.optimization_trace_context import OptimizationTraceContext, TRACE_SOURCE_INPUT, TRACE_SOURCE_POLICY


def test_trace_hard_constraint_failed_is_hard_fail():
    context = OptimizationTraceContext()

    event = trace_hard_constraint(
        context,
        constraint_code="ROOM_CAPACITY",
        passed=False,
        entity_type="section",
        entity_id=1,
        reason_code="CAPACITY_TOO_LOW",
    )

    assert event["event_type"] == "CONSTRAINT_TRIGGERED"
    assert event["severity"] == SEVERITY_HARD_FAIL
    assert event["metadata"]["constraint_type"] == CONSTRAINT_TYPE_HARD
    assert event["metadata"]["passed"] is False


def test_trace_hard_constraint_passed_defaults_to_info():
    context = OptimizationTraceContext()

    event = trace_hard_constraint(
        context,
        constraint_code="ROOM_CAPACITY",
        passed=True,
        entity_type="section",
        entity_id=2,
    )

    assert event["severity"] == SEVERITY_INFO
    assert event["metadata"]["passed"] is True


def test_trace_soft_constraint_failed_defaults_to_warning():
    context = OptimizationTraceContext()

    event = trace_soft_constraint(
        context,
        constraint_code="FAIRNESS_BALANCE",
        passed=False,
        entity_type="section",
        entity_id=3,
        score_delta=-4,
    )

    assert event["severity"] == SEVERITY_WARNING
    assert event["score_delta"] == -4.0
    assert event["metadata"]["constraint_type"] == CONSTRAINT_TYPE_SOFT


def test_trace_soft_constraint_can_use_suggestion_severity():
    context = OptimizationTraceContext()

    event = trace_soft_constraint(
        context,
        constraint_code="FAIRNESS_BALANCE",
        passed=False,
        entity_type="section",
        entity_id=4,
        severity=SEVERITY_SUGGESTION,
    )

    assert event["severity"] == SEVERITY_SUGGESTION


def test_trace_capacity_constraint_uses_capacity_code_and_input_source():
    context = OptimizationTraceContext()

    event = trace_capacity_constraint(
        context,
        passed=False,
        entity_type="section",
        entity_id=5,
    )

    assert event["constraint_code"] == CONSTRAINT_CODE_CAPACITY
    assert event["source"] == TRACE_SOURCE_INPUT


def test_trace_staffing_constraint_uses_staffing_code():
    context = OptimizationTraceContext()

    event = trace_staffing_constraint(
        context,
        passed=False,
        entity_type="section",
        entity_id=6,
        reason_code="STAFF_UNAVAILABLE",
    )

    assert event["constraint_code"] == CONSTRAINT_CODE_STAFFING
    assert event["reason_code"] == "STAFF_UNAVAILABLE"


def test_trace_room_conflict_constraint_uses_room_conflict_code():
    context = OptimizationTraceContext()

    event = trace_room_conflict_constraint(
        context,
        passed=False,
        entity_type="section",
        entity_id=7,
    )

    assert event["constraint_code"] == CONSTRAINT_CODE_ROOM_CONFLICT


def test_trace_student_conflict_constraint_uses_student_conflict_code():
    context = OptimizationTraceContext()

    event = trace_student_conflict_constraint(
        context,
        passed=False,
        entity_type="section",
        entity_id=8,
    )

    assert event["constraint_code"] == CONSTRAINT_CODE_STUDENT_CONFLICT


def test_trace_fairness_constraint_uses_soft_constraint_profile():
    context = OptimizationTraceContext()

    event = trace_fairness_constraint(
        context,
        passed=False,
        entity_type="section",
        entity_id=9,
        score_delta=-2.5,
    )

    assert event["constraint_code"] == CONSTRAINT_CODE_FAIRNESS
    assert event["severity"] == SEVERITY_WARNING
    assert event["metadata"]["constraint_type"] == CONSTRAINT_TYPE_SOFT
    assert event["metadata"]["score_delta"] == -2.5


def test_trace_document_readiness_constraint_uses_governance_profile():
    context = OptimizationTraceContext()

    event = trace_document_readiness_constraint(
        context,
        passed=False,
        entity_type="section",
        entity_id=10,
    )

    assert event["constraint_code"] == CONSTRAINT_CODE_DOCUMENT_READINESS
    assert event["source"] == TRACE_SOURCE_POLICY
    assert event["metadata"]["constraint_type"] == CONSTRAINT_TYPE_GOVERNANCE


def test_trace_qr_readiness_constraint_uses_governance_profile():
    context = OptimizationTraceContext()

    event = trace_qr_readiness_constraint(
        context,
        passed=False,
        entity_type="section",
        entity_id=11,
    )

    assert event["constraint_code"] == CONSTRAINT_CODE_QR_READINESS
    assert event["source"] == TRACE_SOURCE_POLICY
    assert event["metadata"]["constraint_type"] == CONSTRAINT_TYPE_GOVERNANCE


def test_constraint_adapter_uses_context_sanitization():
    context = OptimizationTraceContext()

    event = trace_document_readiness_constraint(
        context,
        passed=False,
        entity_type="section",
        entity_id=12,
        metadata={
            "candidate_name": "Alice Student",
            "safe_total": 3,
        },
    )

    assert event["metadata"]["candidate_name"] == "[REDACTED]"
    assert event["metadata"]["safe_total"] == 3


def test_constraint_adapter_appends_events_to_context():
    context = OptimizationTraceContext()

    trace_capacity_constraint(context, passed=False, entity_type="section", entity_id=13)
    trace_fairness_constraint(context, passed=False, entity_type="section", entity_id=13)
    trace_document_readiness_constraint(context, passed=True, entity_type="section", entity_id=13)

    assert len(context.events) == 3
