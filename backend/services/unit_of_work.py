"""Unit of Work pattern for EMS service layer.

Centralizes commit/rollback ownership so service functions can use db.flush()
(visible within the transaction) while the UoW context manager owns the final
commit or rollback boundary.

Pattern:
    with UnitOfWork(db) as uow:
        service.create_something(uow.db)
        # commit happens automatically on __exit__ if no exception

Or the functional shorthand:
    with atomic(db) as session:
        session.add(record)

ADDITIVE ONLY — existing routers that call db.commit() directly continue to
work unchanged. The UoW is opt-in for new service code.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from services.exceptions import EMSDomainError


class UnitOfWork:
    """Context manager that owns the commit/rollback boundary for a session.

    On clean exit: db.commit()
    On any exception: db.rollback(), then re-raises (never swallows)
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            self.db.commit()
        else:
            self.db.rollback()
        return False  # always re-raise; never suppress exceptions


@contextmanager
def atomic(db: Session) -> Generator[Session, None, None]:
    """Functional shorthand for UnitOfWork.

    Usage:
        with atomic(db) as session:
            session.add(record)
        # commit executed automatically; rollback on any exception
    """
    try:
        yield db
        db.commit()
    except EMSDomainError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
