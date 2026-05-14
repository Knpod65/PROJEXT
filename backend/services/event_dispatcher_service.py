"""Event dispatcher service.

Provides type-based event routing on top of the existing InMemoryEventBus.
The `EventDispatcher` registers domain-specific handlers for specific event
types, then routes published events to the correct handlers.

Architecture:
- The existing `event_bus` (InMemoryEventBus) stores and delivers all events
- `EventDispatcher` subscribes ONE routing function to the bus
- When an event arrives, the dispatcher looks up handlers by `event.event_type`
- Zero or more handlers may be registered per event type
- Handler exceptions are ALWAYS swallowed — dispatcher never crashes the bus
- Unregistered event types are silently ignored

DO NOT implement:
- WebSocket infrastructure
- HTTP push/notification infrastructure
- DB persistence of dispatch outcomes
- Retry logic or dead-letter queues (future phases)

Usage:
    from services.event_dispatcher_service import dispatcher

    @dispatcher.on("GOVERNANCE_ESCALATED")
    def handle_escalation(event: DomainEvent) -> None:
        ...  # called after each matching event is published

    # or register programmatically:
    dispatcher.register("OVERRIDE_REQUESTED", my_handler)
"""
from __future__ import annotations

import threading
from collections import defaultdict
from typing import Callable, Iterable

from events.domain_event import DomainEvent
from services.event_service import InMemoryEventBus, event_bus


class EventDispatcher:
    """Type-based event router wrapping an InMemoryEventBus.

    Thread-safe: handler registration and dispatching use the same lock.
    """

    def __init__(self, bus: InMemoryEventBus) -> None:
        self._bus = bus
        self._handlers: dict[str, list[Callable[[DomainEvent], None]]] = defaultdict(list)
        self._lock = threading.Lock()
        # Subscribe a single routing callback to the bus
        self._bus.subscribe(self._route)

    def register(
        self,
        event_type: str,
        handler: Callable[[DomainEvent], None],
    ) -> None:
        """Register a handler for a specific event type string.

        Multiple handlers can be registered for the same event type.
        All are called in registration order when a matching event arrives.

        Args:
            event_type: Exact string match against DomainEvent.event_type
            handler:    Callable that receives the DomainEvent
        """
        with self._lock:
            self._handlers[event_type].append(handler)

    def on(
        self,
        event_type: str,
    ) -> Callable[[Callable[[DomainEvent], None]], Callable[[DomainEvent], None]]:
        """Decorator shorthand for register().

        Usage:
            @dispatcher.on("SOME_EVENT")
            def handle(event: DomainEvent) -> None: ...
        """
        def decorator(fn: Callable[[DomainEvent], None]) -> Callable[[DomainEvent], None]:
            self.register(event_type, fn)
            return fn
        return decorator

    def dispatch(self, event: DomainEvent) -> None:
        """Route a single event to all registered handlers.

        Does NOT publish to the bus — use `event_bus.publish()` or
        `event_service.emit()` to both publish AND dispatch.

        Handler exceptions are caught and silently swallowed.
        """
        self._route(event)

    def dispatch_many(self, events: Iterable[DomainEvent]) -> None:
        """Route a sequence of events, one at a time."""
        for event in events:
            self._route(event)

    def handler_count(self, event_type: str) -> int:
        """Return how many handlers are registered for event_type."""
        with self._lock:
            return len(self._handlers.get(event_type, []))

    def registered_event_types(self) -> list[str]:
        """Return all event types that have at least one handler."""
        with self._lock:
            return [k for k, v in self._handlers.items() if v]

    def _route(self, event: DomainEvent) -> None:
        with self._lock:
            handlers = list(self._handlers.get(event.event_type, []))
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                # Dispatcher exceptions must NEVER crash the event bus
                pass


# Module-level singleton — wraps the shared event_bus singleton
dispatcher = EventDispatcher(event_bus)
