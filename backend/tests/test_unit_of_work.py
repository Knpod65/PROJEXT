"""Tests for UnitOfWork and audit_event_service coupling."""
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.exceptions import EMSDomainError
from services.unit_of_work import UnitOfWork, atomic


# ── UnitOfWork ────────────────────────────────────────────────────────────

def test_commits_on_clean_exit():
    db = MagicMock()
    with UnitOfWork(db):
        pass
    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_rolls_back_on_ems_domain_error():
    db = MagicMock()
    try:
        with UnitOfWork(db):
            raise EMSDomainError("test error")
    except EMSDomainError:
        pass
    db.rollback.assert_called_once()
    db.commit.assert_not_called()


def test_rolls_back_on_generic_exception():
    db = MagicMock()
    try:
        with UnitOfWork(db):
            raise ValueError("unexpected")
    except ValueError:
        pass
    db.rollback.assert_called_once()
    db.commit.assert_not_called()


def test_re_raises_ems_domain_error():
    db = MagicMock()
    raised = False
    try:
        with UnitOfWork(db):
            raise EMSDomainError("should propagate")
    except EMSDomainError:
        raised = True
    assert raised


def test_re_raises_generic_exception():
    db = MagicMock()
    raised = False
    try:
        with UnitOfWork(db):
            raise RuntimeError("boom")
    except RuntimeError:
        raised = True
    assert raised


def test_uow_exposes_db():
    db = MagicMock()
    with UnitOfWork(db) as uow:
        assert uow.db is db


def test_nested_operations_commit_once():
    db = MagicMock()
    with UnitOfWork(db) as uow:
        uow.db.add(object())
        uow.db.flush()
    db.commit.assert_called_once()


# ── atomic() ─────────────────────────────────────────────────────────────

def test_atomic_commits_on_success():
    db = MagicMock()
    with atomic(db) as session:
        assert session is db
    db.commit.assert_called_once()


def test_atomic_rolls_back_on_ems_domain_error():
    db = MagicMock()
    try:
        with atomic(db):
            raise EMSDomainError("atomic fail")
    except EMSDomainError:
        pass
    db.rollback.assert_called_once()
    db.commit.assert_not_called()


def test_atomic_rolls_back_on_generic_exception():
    db = MagicMock()
    try:
        with atomic(db):
            raise TypeError("bad type")
    except TypeError:
        pass
    db.rollback.assert_called_once()


def test_atomic_re_raises():
    db = MagicMock()
    raised = False
    try:
        with atomic(db):
            raise EMSDomainError("re-raised")
    except EMSDomainError:
        raised = True
    assert raised


# ── audit_event_service ───────────────────────────────────────────────────

def _actor():
    return SimpleNamespace(id=42, username="admin")


def test_record_mutation_with_event_calls_audit_mutation():
    db = MagicMock()
    actor = _actor()
    # Lazy imports inside functions require patching at source module
    with (
        patch("services.audit_service.audit_mutation") as mock_audit,
        patch("services.event_service.emit"),
    ):
        from services.audit_event_service import record_mutation_with_event
        record_mutation_with_event(db, actor, "CREATE", "schedules", record_id=1)
    mock_audit.assert_called_once()
    args = mock_audit.call_args
    assert args[0][2] == "CREATE"   # action
    assert args[0][3] == "schedules"


def test_record_mutation_with_event_calls_emit():
    db = MagicMock()
    actor = _actor()
    with (
        patch("services.audit_service.audit_mutation"),
        patch("services.event_service.emit") as mock_emit,
    ):
        from services.audit_event_service import record_mutation_with_event
        record_mutation_with_event(
            db, actor, "DELETE", "users",
            record_id=5,
            session_id="sess-1",
            correlation_id="corr-1",
        )
    mock_emit.assert_called_once()
    kwargs = mock_emit.call_args[1]
    assert kwargs["actor_id"] == 42
    assert kwargs["session_id"] == "sess-1"
    assert kwargs["correlation_id"] == "corr-1"
    assert kwargs["payload"]["table_name"] == "users"


def test_record_mutation_swallows_emit_exception():
    db = MagicMock()
    actor = _actor()
    with (
        patch("services.audit_service.audit_mutation"),
        patch("services.event_service.emit", side_effect=RuntimeError("bus down")),
    ):
        from services.audit_event_service import record_mutation_with_event
        # must not raise even though emit fails
        record_mutation_with_event(db, actor, "UPDATE", "rooms")


def test_record_event_with_audit_calls_audit_event():
    db = MagicMock()
    actor = _actor()
    with (
        patch("services.audit_service.audit_event") as mock_audit,
        patch("services.event_service.emit"),
    ):
        from services.audit_event_service import record_event_with_audit
        record_event_with_audit(db, actor, "USER_LOGIN", "admin logged in")
    mock_audit.assert_called_once()


def test_record_event_with_audit_passes_domain():
    db = MagicMock()
    actor = _actor()
    with (
        patch("services.audit_service.audit_event"),
        patch("services.event_service.emit") as mock_emit,
    ):
        from services.audit_event_service import record_event_with_audit
        record_event_with_audit(
            db, actor, "EXPORT_PDF", "PDF exported",
            domain="export",
            payload={"period_id": 3},
        )
    mock_emit.assert_called_once()
    call_args = mock_emit.call_args
    # event_type is positional arg[0]; domain is keyword arg
    assert call_args[0][0] == "EXPORT_PDF"
    assert call_args[1]["domain"] == "export"
