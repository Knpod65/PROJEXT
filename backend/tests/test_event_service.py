"""Tests for the in-memory event bus and domain event model."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime

from events.domain_event import DomainEvent, make_domain_event
from services.event_service import InMemoryEventBus, emit, event_bus


# ── make_domain_event ─────────────────────────────────────────────────────

def test_make_domain_event_assigns_uuid():
    evt = make_domain_event("TEST", "optimization")
    assert len(evt.event_id) == 36  # UUID4 string length


def test_make_domain_event_timestamp_is_iso():
    evt = make_domain_event("TEST", "optimization")
    datetime.fromisoformat(evt.timestamp)


def test_make_domain_event_defaults():
    evt = make_domain_event("X", "audit")
    assert evt.actor_id is None
    assert evt.session_id is None
    assert evt.correlation_id is None
    assert evt.payload == {}


def test_make_domain_event_all_fields():
    evt = make_domain_event(
        "OPTIMIZATION_STARTED",
        "optimization",
        actor_id=7,
        session_id="sess-abc",
        correlation_id="corr-123",
        payload={"period_id": 1},
    )
    assert evt.event_type == "OPTIMIZATION_STARTED"
    assert evt.domain == "optimization"
    assert evt.actor_id == 7
    assert evt.session_id == "sess-abc"
    assert evt.correlation_id == "corr-123"
    assert evt.payload == {"period_id": 1}


def test_domain_event_is_immutable():
    evt = make_domain_event("X", "test")
    try:
        evt.event_type = "Y"  # type: ignore[misc]
        assert False, "Should have raised FrozenInstanceError"
    except Exception:
        pass


# ── InMemoryEventBus ──────────────────────────────────────────────────────

def _make_evt(suffix=""):
    return make_domain_event(f"E{suffix}", "test")


def test_publish_and_recent():
    bus = InMemoryEventBus(max_size=10)
    evt = _make_evt()
    bus.publish(evt)
    assert bus.recent(1)[0].event_id == evt.event_id


def test_recent_returns_last_n():
    bus = InMemoryEventBus(max_size=20)
    evts = [_make_evt(str(i)) for i in range(10)]
    for e in evts:
        bus.publish(e)
    last3 = bus.recent(3)
    assert len(last3) == 3
    assert last3[-1].event_id == evts[-1].event_id


def test_max_size_evicts_oldest():
    bus = InMemoryEventBus(max_size=3)
    ids = []
    for i in range(5):
        e = _make_evt(str(i))
        ids.append(e.event_id)
        bus.publish(e)
    buffered = bus.recent(10)
    assert len(buffered) == 3
    assert buffered[0].event_id == ids[2]  # oldest surviving


def test_drain_clears_queue():
    bus = InMemoryEventBus()
    bus.publish(_make_evt())
    bus.publish(_make_evt())
    drained = bus.drain()
    assert len(drained) == 2
    assert bus.size() == 0


def test_drain_returns_in_order():
    bus = InMemoryEventBus()
    evts = [_make_evt(str(i)) for i in range(4)]
    for e in evts:
        bus.publish(e)
    drained = bus.drain()
    assert [e.event_id for e in drained] == [e.event_id for e in evts]


def test_size_reflects_published_count():
    bus = InMemoryEventBus(max_size=10)
    assert bus.size() == 0
    bus.publish(_make_evt())
    bus.publish(_make_evt())
    assert bus.size() == 2


def test_subscriber_called_on_publish():
    bus = InMemoryEventBus()
    received = []
    bus.subscribe(received.append)
    evt = _make_evt()
    bus.publish(evt)
    assert received[0].event_id == evt.event_id


def test_subscriber_exception_does_not_crash_publisher():
    bus = InMemoryEventBus()

    def bad_subscriber(e):
        raise RuntimeError("subscriber failure")

    bus.subscribe(bad_subscriber)
    bus.publish(_make_evt())  # must not raise
    assert bus.size() == 1


def test_multiple_subscribers():
    bus = InMemoryEventBus()
    calls_a, calls_b = [], []
    bus.subscribe(calls_a.append)
    bus.subscribe(calls_b.append)
    bus.publish(_make_evt())
    assert len(calls_a) == 1
    assert len(calls_b) == 1


# ── emit() module function ────────────────────────────────────────────────

def test_emit_returns_domain_event():
    evt = emit("GOVERNANCE_DECISION_CREATED", "optimization", actor_id=42)
    assert isinstance(evt, DomainEvent)
    assert evt.event_type == "GOVERNANCE_DECISION_CREATED"
    assert evt.actor_id == 42


def test_emit_publishes_to_module_bus():
    before = event_bus.size()
    emit("TEST_EMIT", "audit", payload={"x": 1})
    assert event_bus.size() == before + 1


def test_emit_with_all_params():
    evt = emit(
        "RECHECK_COMPLETED",
        "optimization",
        actor_id=1,
        session_id="s1",
        correlation_id="c1",
        payload={"issues": 3},
    )
    assert evt.session_id == "s1"
    assert evt.correlation_id == "c1"
    assert evt.payload == {"issues": 3}
