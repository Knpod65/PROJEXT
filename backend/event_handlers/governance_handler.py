"""Governance domain event handlers."""
from events.domain_event import DomainEvent
from events.governance_events import GovernanceEventType
from services.event_dispatcher_service import dispatcher


@dispatcher.on(GovernanceEventType.OVERRIDE_REQUESTED.value)
def on_override_requested(event: DomainEvent) -> None:
    pass


@dispatcher.on(GovernanceEventType.OVERRIDE_APPROVED.value)
def on_override_approved(event: DomainEvent) -> None:
    pass


@dispatcher.on(GovernanceEventType.OVERRIDE_REJECTED.value)
def on_override_rejected(event: DomainEvent) -> None:
    pass


@dispatcher.on(GovernanceEventType.AUTO_APPROVED.value)
def on_auto_approved(event: DomainEvent) -> None:
    pass


@dispatcher.on(GovernanceEventType.GOVERNANCE_ESCALATED.value)
def on_governance_escalated(event: DomainEvent) -> None:
    pass


@dispatcher.on(GovernanceEventType.AUTO_APPROVAL_BLOCKED.value)
def on_auto_approval_blocked(event: DomainEvent) -> None:
    pass
