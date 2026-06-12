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
from routers.payment_document_review_checklist import router

DOCUMENT_ID = "ADVANCE_PAYMENT_DRAFT_SUMMARY:2568:2:final:all"
BASE_URL = f"/api/payment-document-review-checklist/{DOCUMENT_ID}"


@pytest.fixture()
def app_and_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    app = FastAPI()
    app.include_router(router, prefix="/api/payment-document-review-checklist")
    app.dependency_overrides[get_db] = lambda: session
    try:
        yield app, session
    finally:
        session.close()


def _client(app: FastAPI, role: models.UserRole) -> TestClient:
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=1,
        username=f"{role.value}.user",
        full_name=f"{role.value.title()} User",
        role=role,
        view_as_role=None,
        _active_role=role,
    )
    return TestClient(app)


def test_default_checklist_is_ordered_and_not_persisted(app_and_db):
    app, session = app_and_db
    response = _client(app, models.UserRole.admin).get(BASE_URL)
    assert response.status_code == 200
    payload = response.json()
    assert [item["item_order"] for item in payload["items"]] == list(range(1, 8))
    assert all(item["item_status"] == "NOT_STARTED" for item in payload["items"])
    assert payload["decision_gate_status"] == "HOLD_PENDING_ADDITIONAL_REVIEW"
    assert payload["payment_authorization_enabled"] is False
    assert payload["final_export_enabled"] is False
    assert session.query(models.PaymentDocumentReviewChecklistItem).count() == 0


@pytest.mark.parametrize("role", [models.UserRole.admin, models.UserRole.esq_head, models.UserRole.secretary])
def test_reviewer_roles_can_update_and_persist_item(app_and_db, role):
    app, session = app_and_db
    client = _client(app, role)
    response = client.put(
        f"{BASE_URL}/items/CHECK_DRAFT_XLSX_FILE_LAYOUT",
        json={"item_status": "CHECKED", "comment": "Reviewed the generated workbook layout."},
    )
    assert response.status_code == 200
    item = response.json()["items"][3]
    assert item["item_status"] == "CHECKED"
    assert item["checked_at"] is not None
    assert item["payment_authorization_enabled"] is False
    assert item["final_export_enabled"] is False
    assert session.query(models.PaymentDocumentReviewChecklistItem).count() == 1

    persisted = client.get(BASE_URL).json()["items"][3]
    assert persisted["comment"] == "Reviewed the generated workbook layout."


def test_moving_away_from_checked_clears_checked_at(app_and_db):
    app, _ = app_and_db
    client = _client(app, models.UserRole.admin)
    item_url = f"{BASE_URL}/items/CHECK_DRAFT_ONLY_LABEL"
    assert client.put(item_url, json={"item_status": "CHECKED"}).json()["items"][4]["checked_at"]
    updated = client.put(item_url, json={"item_status": "NEEDS_ATTENTION"}).json()["items"][4]
    assert updated["checked_at"] is None


def test_staff_is_read_only(app_and_db):
    app, _ = app_and_db
    client = _client(app, models.UserRole.staff)
    assert client.get(BASE_URL).status_code == 200
    assert client.put(
        f"{BASE_URL}/items/CHECK_PAYMENT_DOCUMENT_SETTINGS",
        json={"item_status": "CHECKED"},
    ).status_code == 403


@pytest.mark.parametrize("role", [models.UserRole.teacher, models.UserRole.print_shop, models.UserRole.student])
def test_unrelated_roles_are_blocked(app_and_db, role):
    app, _ = app_and_db
    client = _client(app, role)
    assert client.get(BASE_URL).status_code == 403
    assert client.put(
        f"{BASE_URL}/items/CHECK_PAYMENT_DOCUMENT_SETTINGS",
        json={"item_status": "CHECKED"},
    ).status_code == 403


def test_unknown_item_status_and_document_are_rejected(app_and_db):
    app, _ = app_and_db
    client = _client(app, models.UserRole.admin)
    assert client.put(f"{BASE_URL}/items/UNKNOWN_ITEM", json={"item_status": "CHECKED"}).status_code == 400
    assert client.put(
        f"{BASE_URL}/items/CHECK_PAYMENT_DOCUMENT_SETTINGS",
        json={"item_status": "PAYMENT_AUTHORIZED"},
    ).status_code == 422
    assert client.get("/api/payment-document-review-checklist/FINAL_PAYMENT:2568:2:final:all").status_code == 400


def test_checklist_completion_does_not_change_review_or_authorization(app_and_db):
    app, session = app_and_db
    review = models.PaymentDocumentReviewRecord(
        document_id=DOCUMENT_ID,
        document_type="ADVANCE_PAYMENT_DRAFT_SUMMARY",
        term="2/2568",
        review_status="ACCEPTED_FOR_DRAFT_EXPORT",
        comment="Existing export gate only.",
        payment_authorization_enabled=False,
        final_export_enabled=False,
    )
    session.add(review)
    session.commit()
    client = _client(app, models.UserRole.admin)
    for key in (
        "CHECK_PAYMENT_DOCUMENT_SETTINGS",
        "CHECK_OFFICIAL_PAYMENT_DOCUMENT_DRAFT",
        "CHECK_REVIEW_PANEL_STATUS",
        "CHECK_DRAFT_XLSX_FILE_LAYOUT",
        "CHECK_DRAFT_ONLY_LABEL",
        "CHECK_NOT_PAYMENT_AUTHORIZATION",
        "CHECK_FINAL_AUTHORIZATION_DISABLED",
    ):
        response = client.put(f"{BASE_URL}/items/{key}", json={"item_status": "CHECKED"})
        assert response.status_code == 200

    payload = response.json()
    assert payload["overall_status"] == "CHECKED"
    assert payload["decision_gate_status"] == "HOLD_PENDING_ADDITIONAL_REVIEW"
    assert payload["payment_authorization_enabled"] is False
    assert payload["final_export_enabled"] is False
    session.refresh(review)
    assert review.review_status == "ACCEPTED_FOR_DRAFT_EXPORT"
    assert review.payment_authorization_enabled is False
    assert review.final_export_enabled is False
