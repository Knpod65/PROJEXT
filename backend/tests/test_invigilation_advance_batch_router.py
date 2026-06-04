import os
import sys
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import models
from auth_utils import get_current_user
from database import Base, get_db
from routers.invigilation_advance_batch import router


@pytest.fixture()
def app_and_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    app = FastAPI()
    app.include_router(router, prefix="/api/invigilation-advance-batch")
    app.dependency_overrides[get_db] = lambda: session

    try:
        yield app
    finally:
        session.close()


def _client_for_role(app: FastAPI, role: models.UserRole) -> TestClient:
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=1,
        role=role,
        view_as_role=None,
        _active_role=role,
    )
    return TestClient(app)


@pytest.mark.parametrize(
    "role,expected_status",
    [
        (models.UserRole.admin, 200),
        (models.UserRole.staff, 200),
        (models.UserRole.teacher, 403),
        (models.UserRole.print_shop, 403),
    ],
)
def test_advance_batch_preview_role_permissions(app_and_db, role, expected_status):
    response = _client_for_role(app_and_db, role).get("/api/invigilation-advance-batch/preview")
    assert response.status_code == expected_status
    if response.status_code == 200:
        payload = response.json()
        assert payload["summary"]["payment_authorization_enabled"] is False
        assert payload["summary"]["final_export_enabled"] is False
