"""In-memory domain event bus.

Provides a thread-safe ring buffer (deque) for domain events with subscriber
callbacks. No DB persistence in this phase — events are in-memory only.

Future consumers: audit integration, notification hooks, analytics, WebSocket
push, report builder. Consumers subscribe via event_bus.subscribe(fn).
"""
from __future__ import annotations

from collections import deque
from threading import Lock
from typing import Any, Callable, Deque, List

from events.domain_event import DomainEvent, make_domain_event

_MAX_BUFFER = 500


class InMemoryEventBus:
    """Thread-safe ring-buffer event bus.

    Oldest events are silently dropped when max_size is reached.
    Subscriber exceptions are swallowed — the bus never crashes the caller.
    """

    def __init__(self, max_size: int = _MAX_BUFFER) -> None:
        self._queue: Deque[DomainEvent] = deque(maxlen=max_size)
        self._subscribers: list[Callable[[DomainEvent], None]] = []
        self._lock = Lock()

    def publish(self, event: DomainEvent) -> None:
        with self._lock:
            self._queue.append(event)
        for fn in self._subscribers:
            try:
                fn(event)
            except Exception:
                pass  # subscribers must never crash the emitter

    def subscribe(self, fn: Callable[[DomainEvent], None]) -> None:
        self._subscribers.append(fn)

    def recent(self, n: int = 50) -> List[DomainEvent]:
        with self._lock:
            return list(self._queue)[-n:]

    def drain(self) -> List[DomainEvent]:
        """Return all buffered events and clear the buffer."""
        with self._lock:
            events = list(self._queue)
            self._queue.clear()
            return events

    def size(self) -> int:
        with self._lock:
            return len(self._queue)


# Module-level singleton — shared across all callers in this process.
# No DB, no migration required.
event_bus: InMemoryEventBus = InMemoryEventBus()


def emit(
    event_type: str,
    domain: str,
    *,
    actor_id: int | None = None,
    session_id: str | None = None,
    correlation_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> DomainEvent:
    """Create and publish a DomainEvent to the module-level bus.

    Returns the emitted event so callers can inspect event_id / timestamp.
    """
    event = make_domain_event(
        event_type=event_type,
        domain=domain,
        actor_id=actor_id,
        session_id=session_id,
        correlation_id=correlation_id,
        payload=payload,
    )
    event_bus.publish(event)
    return event
