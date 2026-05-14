"""Tests for event_handlers package."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import handlers to trigger registration
import event_handlers.optimization_handler  # noqa: F401
import event_handlers.governance_handler    # noqa: F401
import event_handlers.publication_handler   # noqa: F401
import event_handlers.audit_handler         # noqa: F401

from services.event_dispatcher_service import dispatcher
from events.domain_event import DomainEvent
from events.optimization_events import OptimizationEventType
from events.governance_events import GovernanceEventType
from events.audit_events import AuditEventType
import uuid
from datetime import datetime, timezone


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_event(event_type: str) -> DomainEvent:
    return DomainEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        domain="test",
        actor_id=1,
        session_id="test-session",
        correlation_id=str(uuid.uuid4()),
        payload={},
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# ── Registration tests ────────────────────────────────────────────────────────

def test_optimization_governance_escalated_registered():
    assert dispatcher.handler_count(OptimizationEventType.GOVERNANCE_ESCALATED.value) >= 1


def test_optimization_hard_constraint_failed_registered():
    assert dispatcher.handler_count(OptimizationEventType.HARD_CONSTRAINT_FAILED.value) >= 1


def test_optimization_recheck_warning_registered():
    assert dispatcher.handler_count(OptimizationEventType.RECHECK_WARNING_GENERATED.value) >= 1


def test_governance_override_requested_registered():
    assert dispatcher.handler_count(GovernanceEventType.OVERRIDE_REQUESTED.value) >= 1


def test_governance_auto_approved_registered():
    assert dispatcher.handler_count(GovernanceEventType.AUTO_APPROVED.value) >= 1


def test_governance_escalated_registered():
    assert dispatcher.handler_count(GovernanceEventType.GOVERNANCE_ESCALATED.value) >= 1


def test_publication_published_registered():
    assert dispatcher.handler_count("SCHEDULE_PUBLISHED") >= 1


def test_publication_rolled_back_registered():
    assert dispatcher.handler_count("SCHEDULE_ROLLED_BACK") >= 1


def test_audit_mutation_committed_registered():
    assert dispatcher.handler_count(AuditEventType.MUTATION_COMMITTED.value) >= 1


def test_audit_unauthorized_access_registered():
    assert dispatcher.handler_count(AuditEventType.UNAUTHORIZED_ACCESS_ATTEMPT.value) >= 1


# ── Dispatch tests — handlers must not raise ──────────────────────────────────

def test_dispatch_optimization_event_does_not_raise():
    event = _make_event(OptimizationEventType.GOVERNANCE_ESCALATED.value)
    dispatcher.dispatch(event)  # should not raise


def test_dispatch_governance_event_does_not_raise():
    event = _make_event(GovernanceEventType.OVERRIDE_REQUESTED.value)
    dispatcher.dispatch(event)


def test_dispatch_publication_event_does_not_raise():
    event = _make_event("SCHEDULE_PUBLISHED")
    dispatcher.dispatch(event)


def test_dispatch_audit_event_does_not_raise():
    event = _make_event(AuditEventType.MUTATION_COMMITTED.value)
    dispatcher.dispatch(event)


def test_dispatch_unknown_event_does_not_raise():
    event = _make_event("COMPLETELY_UNKNOWN_EVENT_TYPE")
    dispatcher.dispatch(event)  # no handler, should still not raise


# ── Handler exception isolation ───────────────────────────────────────────────

def test_handler_exception_does_not_crash_dispatcher():
    """A faulty handler must not propagate exceptions to the caller."""
    def bad_handler(event: DomainEvent) -> None:
        raise RuntimeError("handler exploded")

    dispatcher.register("TEST_CRASH_EVENT", bad_handler)
    event = _make_event("TEST_CRASH_EVENT")
    dispatcher.dispatch(event)  # must not raise RuntimeError


# ── registered_event_types sanity ────────────────────────────────────────────

def test_registered_event_types_includes_known_types():
    registered = dispatcher.registered_event_types()
    assert "SCHEDULE_PUBLISHED" in registered
    assert AuditEventType.MUTATION_COMMITTED.value in registered
    assert GovernanceEventType.AUTO_APPROVED.value in registered
