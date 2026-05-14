"""Optimization domain event handlers."""
from events.domain_event import DomainEvent
from events.optimization_events import OptimizationEventType
from services.event_dispatcher_service import dispatcher


@dispatcher.on(OptimizationEventType.GOVERNANCE_ESCALATED.value)
def on_governance_escalated(event: DomainEvent) -> None:
    pass  # Future: structured log, metric increment


@dispatcher.on(OptimizationEventType.HARD_CONSTRAINT_FAILED.value)
def on_hard_constraint_failed(event: DomainEvent) -> None:
    pass


@dispatcher.on(OptimizationEventType.RECHECK_WARNING_GENERATED.value)
def on_recheck_warning_generated(event: DomainEvent) -> None:
    pass


@dispatcher.on(OptimizationEventType.QUALITY_SCORE_ADJUSTED.value)
def on_quality_score_adjusted(event: DomainEvent) -> None:
    pass
