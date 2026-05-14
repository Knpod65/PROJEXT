"""Publication domain event handlers."""
from events.domain_event import DomainEvent
from services.event_dispatcher_service import dispatcher


@dispatcher.on("SCHEDULE_PUBLISHED")
def on_schedule_published(event: DomainEvent) -> None:
    pass


@dispatcher.on("SCHEDULE_ROLLED_BACK")
def on_schedule_rolled_back(event: DomainEvent) -> None:
    pass


@dispatcher.on("EMERGENCY_PUBLICATION_OVERRIDE")
def on_emergency_override(event: DomainEvent) -> None:
    pass


@dispatcher.on("SCHEDULE_LOCKED")
def on_schedule_locked(event: DomainEvent) -> None:
    pass
