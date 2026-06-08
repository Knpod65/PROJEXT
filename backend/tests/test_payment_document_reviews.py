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
from routers.invigilation_advance_batch import router as draft_router
from routers.payment_document_reviews import router as review_router


DOCUMENT_ID = "ADVANCE_PAYMENT_DRAFT_SUMMARY:2568:2:final:all"


@pytest.fixture()
def app_and_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    app = FastAPI()
    app.include_router(review_router, prefix="/api/payment-document-reviews")
    app.include_router(draft_router, prefix="/api/invigilation-advance-batch")
    app.dependency_overrides[get_db] = lambda: session

    try:
        yield app
    finally:
        session.close()


def _client_for_role(app: FastAPI, role: models.UserRole) -> TestClient:
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=1,
        username=f"{role.value}.user",
        full_name=f"{role.value.title()} User",
        role=role,
        view_as_role=None,
        _active_role=role,
    )
    return TestClient(app)


def _create_payload(**overrides):
    payload = {
        "document_id": DOCUMENT_ID,
        "document_type": "ADVANCE_PAYMENT_DRAFT_SUMMARY",
        "term": "2/2568",
        "review_status": "DRAFT_READY_FOR_REVIEW",
        "comment": "Prepared for supervisor review.",
        "prepared_by": "EMS staff",
    }
    payload.update(overrides)
    return payload


def test_list_reviews_empty(app_and_db):
    response = _client_for_role(app_and_db, models.UserRole.admin).get("/api/payment-document-reviews")
    assert response.status_code == 200
    payload = response.json()
    assert payload["records"] == []
    assert payload["payment_authorization_enabled"] is False
    assert payload["final_export_enabled"] is False


def test_create_review_comment_persists(app_and_db):
    client = _client_for_role(app_and_db, models.UserRole.admin)
    create_response = client.post("/api/payment-document-reviews", json=_create_payload())
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["review_id"] > 0
    assert created["comment"] == "Prepared for supervisor review."
    assert created["payment_authorization_enabled"] is False
    assert created["final_export_enabled"] is False

    list_response = client.get(f"/api/payment-document-reviews/{DOCUMENT_ID}")
    assert list_response.status_code == 200
    records = list_response.json()["records"]
    assert len(records) == 1
    assert records[0]["document_id"] == DOCUMENT_ID
    assert records[0]["comment"] == "Prepared for supervisor review."


@pytest.mark.parametrize(
    "status",
    ["UNDER_REVIEW", "REVISIONS_REQUESTED", "ACCEPTED_FOR_DRAFT_EXPORT"],
)
def test_admin_can_set_review_statuses_and_flags_stay_false(app_and_db, status):
    client = _client_for_role(app_and_db, models.UserRole.admin)
    create_response = client.post("/api/payment-document-reviews", json=_create_payload())
    review_id = create_response.json()["review_id"]

    response = client.put(
        f"/api/payment-document-reviews/{review_id}",
        json={"review_status": status, "comment": f"Status set to {status}."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["review_status"] == status
    assert payload["payment_authorization_enabled"] is False
    assert payload["final_export_enabled"] is False


def test_staff_can_comment_but_cannot_accept(app_and_db):
    staff_client = _client_for_role(app_and_db, models.UserRole.staff)
    create_response = staff_client.post("/api/payment-document-reviews", json=_create_payload(comment="Staff request review."))
    assert create_response.status_code == 200
    review_id = create_response.json()["review_id"]

    accept_response = staff_client.put(
        f"/api/payment-document-reviews/{review_id}",
        json={"review_status": "ACCEPTED_FOR_DRAFT_EXPORT", "comment": "Looks accepted."},
    )
    assert accept_response.status_code == 403


@pytest.mark.parametrize("role", [models.UserRole.teacher, models.UserRole.print_shop, models.UserRole.student])
def test_unrelated_roles_are_blocked(app_and_db, role):
    client = _client_for_role(app_and_db, role)
    assert client.get("/api/payment-document-reviews").status_code == 403
    assert client.post("/api/payment-document-reviews", json=_create_payload()).status_code == 403


def test_invalid_status_and_unknown_document_type_are_rejected(app_and_db):
    client = _client_for_role(app_and_db, models.UserRole.admin)
    invalid_status = client.post(
        "/api/payment-document-reviews",
        json=_create_payload(review_status="PAYMENT_AUTHORIZED"),
    )
    assert invalid_status.status_code in (400, 422)

    invalid_type = client.post(
        "/api/payment-document-reviews",
        json=_create_payload(document_type="FINAL_PAYMENT_AUTHORIZATION"),
    )
    assert invalid_type.status_code in (400, 422)


def test_review_records_do_not_modify_draft_calculation_or_persist_manual_paper_truth(app_and_db):
    client = _client_for_role(app_and_db, models.UserRole.admin)
    draft_payload = {
        "academic_year": "2568",
        "semester": "2",
        "exam_type": "final",
        "paper_distribution_rows": [
            {"exam_date": "2026-03-21", "exam_time": "09:00-12:00", "committee_count": 2}
        ],
    }
    before = client.post("/api/invigilation-advance-batch/official-document-draft-preview", json=draft_payload)
    assert before.status_code == 200

    review = client.post(
        "/api/payment-document-reviews",
        json=_create_payload(review_status="ACCEPTED_FOR_DRAFT_EXPORT", comment="Format accepted for draft export design."),
    )
    assert review.status_code == 200
    assert review.json()["payment_authorization_enabled"] is False
    assert review.json()["final_export_enabled"] is False

    after = client.post("/api/invigilation-advance-batch/official-document-draft-preview", json=draft_payload)
    assert after.status_code == 200
    assert after.json()["totals"] == before.json()["totals"]
    assert after.json()["rows"] == before.json()["rows"]

    without_manual_rows = client.post(
        "/api/invigilation-advance-batch/official-document-draft-preview",
        json={**draft_payload, "paper_distribution_rows": []},
    )
    assert without_manual_rows.status_code == 200
    assert without_manual_rows.json()["totals"]["paper_distribution_committee_count"] == 0
