"""Typed event type constants for the governance domain.

These enums define every event type that governance-related services
emit through the InMemoryEventBus. Use as the `event_type` argument
to `event_service.emit()` or `transaction_audit_service.execute_with_audit()`.

Source authority: this file owns the governance event type vocabulary.
"""
from __future__ import annotations

from enum import Enum

from events.base_event import EventDomain

GOVERNANCE_DOMAIN = EventDomain.GOVERNANCE.value


class GovernanceEventType(str, Enum):
    """All event types emitted in the governance domain."""

    # Decision lifecycle
    GOVERNANCE_DECISION_CREATED = "GOVERNANCE_DECISION_CREATED"
    GOVERNANCE_DECISION_UPDATED = "GOVERNANCE_DECISION_UPDATED"

    # Override lifecycle
    OVERRIDE_REQUESTED = "OVERRIDE_REQUESTED"
    OVERRIDE_APPROVED = "OVERRIDE_APPROVED"
    OVERRIDE_REJECTED = "OVERRIDE_REJECTED"

    # Escalation
    GOVERNANCE_ESCALATED = "GOVERNANCE_ESCALATED"
    ESCALATION_RESOLVED = "ESCALATION_RESOLVED"

    # Review
    REVIEW_ASSIGNED = "REVIEW_ASSIGNED"
    REVIEW_COMPLETED = "REVIEW_COMPLETED"

    # Auto-approval
    AUTO_APPROVED = "AUTO_APPROVED"
    AUTO_APPROVAL_BLOCKED = "AUTO_APPROVAL_BLOCKED"
