"""Tests for transaction_audit_service."""
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.transaction_audit_service import (
    execute_with_audit,
    execute_readonly_with_event,
)


# ── Test helpers ──────────────────────────────────────────────────────────

def _db():
    db = MagicMock()
    db.commit = MagicMock()
    db.rollback = MagicMock()
    return db


def _actor(user_id=42):
    return SimpleNamespace(id=user_id, username="test_user")


def _call(**kw):
    defaults = dict(
        mutation_fn=lambda db: "result",
        actor=_actor(),
        audit_action="TEST_ACTION",
        audit_table_name="test_table",
        event_type="TEST_EVENT",
        event_domain="test",
    )
    defaults.update(kw)
    return defaults


# ── Success path ──────────────────────────────────────────────────────────

def test_returns_mutation_result():
    with patch("services.audit_service.audit_mutation"), \
         patch("services.event_service.emit"):
        result = execute_with_audit(_db(), **_call(mutation_fn=lambda db: 99))
    assert result == 99


def test_mutation_fn_receives_db():
    received = []
    db = _db()

    def capture(session):
        received.append(session)
        return None

    with patch("services.audit_service.audit_mutation"), \
         patch("services.event_service.emit"):
        execute_with_audit(db, **_call(mutation_fn=capture))

    assert received[0] is db


def test_commit_called_on_success():
    db = _db()
    with patch("services.audit_service.audit_mutation"), \
         patch("services.event_service.emit"):
        execute_with_audit(db, **_call())
    db.commit.assert_called_once()


def test_rollback_not_called_on_success():
    db = _db()
    with patch("services.audit_service.audit_mutation"), \
         patch("services.event_service.emit"):
        execute_with_audit(db, **_call())
    db.rollback.assert_not_called()


def test_audit_mutation_called():
    db = _db()
    with patch("services.audit_service.audit_mutation") as mock_audit, \
         patch("services.event_service.emit"):
        execute_with_audit(db, **_call(audit_action="CREATED"))
    mock_audit.assert_called_once()
    _, call_args, call_kwargs = mock_audit.mock_calls[0]
    assert call_kwargs.get("action") == "CREATED" or call_args[2] == "CREATED"


def test_event_emitted_after_commit():
    db = _db()
    call_order = []
    db.commit.side_effect = lambda: call_order.append("commit")

    with patch("services.audit_service.audit_mutation"), \
         patch("services.event_service.emit", side_effect=lambda *a, **kw: call_order.append("emit")):
        execute_with_audit(db, **_call(event_type="TEST_EVT", event_domain="test"))

    assert call_order.index("commit") < call_order.index("emit")


def test_event_payload_passed_to_emit():
    db = _db()
    with patch("services.audit_service.audit_mutation"), \
         patch("services.event_service.emit") as mock_emit:
        execute_with_audit(db, **_call(event_payload={"key": "value"}))
    _, _, emit_kw = mock_emit.mock_calls[0]
    assert emit_kw.get("payload", {}).get("key") == "value"


def test_actor_id_extracted_from_actor():
    db = _db()
    with patch("services.audit_service.audit_mutation"), \
         patch("services.event_service.emit") as mock_emit:
        execute_with_audit(db, **_call(actor=_actor(user_id=77)))
    _, _, emit_kw = mock_emit.mock_calls[0]
    assert emit_kw.get("actor_id") == 77


# ── Rollback on failure ───────────────────────────────────────────────────

def test_rollback_called_on_mutation_failure():
    db = _db()

    def failing(session):
        raise ValueError("mutation error")

    with patch("services.audit_service.audit_mutation"), \
         patch("services.event_service.emit"):
        try:
            execute_with_audit(db, **_call(mutation_fn=failing))
        except ValueError:
            pass

    db.rollback.assert_called_once()
    db.commit.assert_not_called()


def test_exception_re_raised_on_mutation_failure():
    db = _db()

    def failing(session):
        raise ValueError("specific error")

    with patch("services.audit_service.audit_mutation"), \
         patch("services.event_service.emit"):
        try:
            execute_with_audit(db, **_call(mutation_fn=failing))
            assert False, "Should have raised"
        except ValueError as exc:
            assert "specific error" in str(exc)


def test_rollback_called_on_audit_failure():
    db = _db()
    with patch("services.audit_service.audit_mutation", side_effect=RuntimeError("audit fail")), \
         patch("services.event_service.emit"):
        try:
            execute_with_audit(db, **_call())
        except RuntimeError:
            pass
    db.rollback.assert_called_once()
    db.commit.assert_not_called()


def test_event_not_emitted_on_rollback():
    db = _db()

    def failing(session):
        raise ValueError()

    with patch("services.audit_service.audit_mutation"), \
         patch("services.event_service.emit") as mock_emit:
        try:
            execute_with_audit(db, **_call(mutation_fn=failing))
        except ValueError:
            pass
    mock_emit.assert_not_called()


# ── Event emission failure isolation ─────────────────────────────────────

def test_emit_failure_does_not_propagate():
    db = _db()
    with patch("services.audit_service.audit_mutation"), \
         patch("services.event_service.emit", side_effect=RuntimeError("bus down")):
        # Should NOT raise despite emit failure
        result = execute_with_audit(db, **_call(mutation_fn=lambda db: "ok"))
    assert result == "ok"


# ── execute_readonly_with_event ───────────────────────────────────────────

def test_readonly_event_emits_without_db():
    with patch("services.event_service.emit") as mock_emit:
        execute_readonly_with_event(
            event_type="REPORT_VIEWED",
            event_domain="audit",
            actor_id=5,
            payload={"report": "governance"},
        )
    mock_emit.assert_called_once()


def test_readonly_event_failure_swallowed():
    with patch("services.event_service.emit", side_effect=RuntimeError("bus down")):
        # Must not raise
        execute_readonly_with_event(event_type="EVT", event_domain="test")
