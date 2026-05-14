"""Tests for event_dispatcher_service."""
import os
import sys
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from events.domain_event import make_domain_event
from services.event_dispatcher_service import EventDispatcher
from services.event_service import InMemoryEventBus


# ── Test helpers ──────────────────────────────────────────────────────────

def _bus():
    return InMemoryEventBus(max_size=100)


def _dispatcher(bus=None):
    return EventDispatcher(bus or _bus())


def _event(event_type="TEST_EVENT", domain="test", **kw):
    return make_domain_event(event_type=event_type, domain=domain, payload=kw)


# ── Handler registration ──────────────────────────────────────────────────

def test_register_adds_handler():
    d = _dispatcher()
    d.register("EVT_A", lambda e: None)
    assert d.handler_count("EVT_A") == 1


def test_register_multiple_handlers_same_type():
    d = _dispatcher()
    d.register("EVT", lambda e: None)
    d.register("EVT", lambda e: None)
    assert d.handler_count("EVT") == 2


def test_unregistered_event_type_has_zero_handlers():
    d = _dispatcher()
    assert d.handler_count("NEVER_REGISTERED") == 0


def test_registered_event_types_lists_all():
    d = _dispatcher()
    d.register("EVT_X", lambda e: None)
    d.register("EVT_Y", lambda e: None)
    types = d.registered_event_types()
    assert "EVT_X" in types
    assert "EVT_Y" in types


# ── Dispatch routing ──────────────────────────────────────────────────────

def test_dispatch_calls_registered_handler():
    d = _dispatcher()
    received = []
    d.register("MY_EVENT", received.append)
    d.dispatch(_event("MY_EVENT"))
    assert len(received) == 1


def test_dispatch_passes_correct_event():
    d = _dispatcher()
    received = []
    d.register("MY_EVENT", received.append)
    evt = _event("MY_EVENT")
    d.dispatch(evt)
    assert received[0].event_id == evt.event_id


def test_dispatch_calls_all_handlers_for_type():
    d = _dispatcher()
    counter = [0]
    d.register("EVT", lambda e: counter.__setitem__(0, counter[0] + 1))
    d.register("EVT", lambda e: counter.__setitem__(0, counter[0] + 1))
    d.dispatch(_event("EVT"))
    assert counter[0] == 2


def test_dispatch_unmatched_type_is_noop():
    d = _dispatcher()
    received = []
    d.register("OTHER", received.append)
    d.dispatch(_event("DIFFERENT"))
    assert received == []


def test_dispatch_many_routes_each_event():
    d = _dispatcher()
    received = []
    d.register("BATCH", received.append)
    events = [_event("BATCH"), _event("BATCH"), _event("BATCH")]
    d.dispatch_many(events)
    assert len(received) == 3


def test_dispatch_many_mixed_types():
    d = _dispatcher()
    a_received = []
    b_received = []
    d.register("A", a_received.append)
    d.register("B", b_received.append)
    d.dispatch_many([_event("A"), _event("B"), _event("A")])
    assert len(a_received) == 2
    assert len(b_received) == 1


# ── Error isolation ───────────────────────────────────────────────────────

def test_handler_exception_is_swallowed():
    d = _dispatcher()

    def bad_handler(event):
        raise RuntimeError("handler exploded")

    d.register("EVT", bad_handler)
    # Must not raise
    d.dispatch(_event("EVT"))


def test_other_handlers_called_after_failing_handler():
    d = _dispatcher()
    received = []

    def bad(event):
        raise RuntimeError()

    d.register("EVT", bad)
    d.register("EVT", received.append)
    d.dispatch(_event("EVT"))
    assert len(received) == 1


# ── Bus integration (via publish) ─────────────────────────────────────────

def test_bus_publish_triggers_dispatcher():
    bus = _bus()
    d = EventDispatcher(bus)
    received = []
    d.register("BUS_EVT", received.append)
    evt = _event("BUS_EVT")
    bus.publish(evt)
    assert len(received) == 1


# ── @on decorator ─────────────────────────────────────────────────────────

def test_on_decorator_registers_handler():
    d = _dispatcher()
    received = []

    @d.on("DECORATOR_EVT")
    def handle(event):
        received.append(event)

    d.dispatch(_event("DECORATOR_EVT"))
    assert len(received) == 1


def test_on_decorator_returns_original_function():
    d = _dispatcher()

    @d.on("EVT")
    def handle(event):
        return "original"

    assert handle(_event("EVT")) == "original"


# ── Thread safety ─────────────────────────────────────────────────────────

def test_concurrent_registration_is_safe():
    d = _dispatcher()
    errors = []

    def register_many():
        try:
            for _ in range(20):
                d.register("CONCURRENT", lambda e: None)
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=register_many) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    assert d.handler_count("CONCURRENT") == 100
