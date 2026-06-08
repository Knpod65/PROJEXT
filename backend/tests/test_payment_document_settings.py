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
from routers.payment_document_settings import router as settings_router


TERM = "2/2568"
DOCUMENT_ID = "ADVANCE_PAYMENT_DRAFT_SUMMARY:2568:2:final:all"


@pytest.fixture()
def app_and_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    app = FastAPI()
    app.include_router(settings_router, prefix="/api/payment-document-settings")
    app.include_router(review_router, prefix="/api/payment-document-reviews")
    app.include_router(draft_router, prefix="/api/invigilation-advance-batch")
    app.dependency_overrides[get_db] = lambda: session

    try:
        yield app, session
    finally:
        session.close()


def _client_for_role(app: FastAPI, role: models.UserRole) -> TestClient:
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=10,
        username=f"{role.value}.user",
        full_name=f"{role.value.title()} User",
        role=role,
        view_as_role=None,
        _active_role=role,
    )
    return TestClient(app)


def _payload(**overrides):
    payload = {
        "term": TERM,
        "weekday_rate": 120,
        "weekend_rate": 200,
        "currency": "THB",
        "payment_unit": "PER_PERSON_SESSION",
        "paper_distribution_responsible_group": "Education_Student_Quality",
        "paper_distribution_responsible_person": None,
        "status": "ACTIVE_FOR_DRAFT_PREVIEW",
        "note": "Draft settings for document preparation only.",
    }
    payload.update(overrides)
    return payload


def test_get_missing_term_returns_pending_defaults(app_and_db):
    app, _session = app_and_db
    response = _client_for_role(app, models.UserRole.admin).get(f"/api/payment-document-settings/{TERM}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["term"] == TERM
    assert payload["configuration_status"] == "PENDING_CONFIGURATION"
    assert payload["weekday_rate"] is None
    assert payload["weekend_rate"] is None
    assert payload["paper_distribution_responsible_group"] == "Education_Student_Quality"
    assert payload["payment_authorization_enabled"] is False
    assert payload["final_export_enabled"] is False


@pytest.mark.parametrize("role", [models.UserRole.admin, models.UserRole.esq_head, models.UserRole.secretary])
def test_reviewer_roles_can_save_and_read_settings(app_and_db, role):
    app, _session = app_and_db
    client = _client_for_role(app, role)
    save = client.put(f"/api/payment-document-settings/{TERM}", json=_payload())
    assert save.status_code == 200
    saved = save.json()
    assert saved["weekday_rate"] == "120.00"
    assert saved["weekend_rate"] == "200.00"
    assert saved["paper_distribution_responsible_group"] == "Education_Student_Quality"
    assert saved["paper_distribution_responsible_person"] is None
    assert saved["configuration_status"] == "CONFIGURED"
    assert saved["status"] == "ACTIVE_FOR_DRAFT_PREVIEW"
    assert saved["updated_by"] == 10
    assert saved["updated_at"]
    assert saved["payment_authorization_enabled"] is False
    assert saved["final_export_enabled"] is False

    read = client.get(f"/api/payment-document-settings/{TERM}")
    assert read.status_code == 200
    assert read.json()["weekday_rate"] == "120.00"


def test_responsible_person_is_optional_and_persists_when_supplied(app_and_db):
    app, _session = app_and_db
    response = _client_for_role(app, models.UserRole.admin).put(
        f"/api/payment-document-settings/{TERM}",
        json=_payload(paper_distribution_responsible_person="Review Coordinator"),
    )
    assert response.status_code == 200
    assert response.json()["paper_distribution_responsible_person"] == "Review Coordinator"


def test_staff_can_read_but_cannot_write(app_and_db):
    app, _session = app_and_db
    staff = _client_for_role(app, models.UserRole.staff)
    assert staff.get(f"/api/payment-document-settings/{TERM}").status_code == 200
    assert staff.put(f"/api/payment-document-settings/{TERM}", json=_payload()).status_code == 403


@pytest.mark.parametrize("role", [models.UserRole.teacher, models.UserRole.print_shop, models.UserRole.student])
def test_unrelated_roles_are_blocked(app_and_db, role):
    app, _session = app_and_db
    client = _client_for_role(app, role)
    assert client.get("/api/payment-document-settings").status_code == 403
    assert client.get(f"/api/payment-document-settings/{TERM}").status_code == 403
    assert client.put(f"/api/payment-document-settings/{TERM}", json=_payload()).status_code == 403


@pytest.mark.parametrize(
    "overrides",
    [
        {"weekday_rate": 0},
        {"weekday_rate": -1},
        {"weekend_rate": 0},
        {"weekend_rate": -1},
        {"paper_distribution_responsible_group": " "},
        {"status": "PAYMENT_AUTHORIZED"},
        {"currency": "USD"},
        {"payment_unit": "PER_PAYMENT"},
    ],
)
def test_invalid_settings_are_rejected(app_and_db, overrides):
    app, _session = app_and_db
    response = _client_for_role(app, models.UserRole.admin).put(
        f"/api/payment-document-settings/{TERM}",
        json=_payload(**overrides),
    )
    assert response.status_code in (400, 422)


def test_path_and_payload_term_must_match(app_and_db):
    app, _session = app_and_db
    response = _client_for_role(app, models.UserRole.admin).put(
        "/api/payment-document-settings/1/2568",
        json=_payload(),
    )
    assert response.status_code == 400


def test_saving_settings_does_not_create_review_acceptance_or_export(app_and_db):
    app, session = app_and_db
    client = _client_for_role(app, models.UserRole.admin)
    response = client.put(f"/api/payment-document-settings/{TERM}", json=_payload())
    assert response.status_code == 200
    assert session.query(models.PaymentDocumentReviewRecord).count() == 0

    reviews = client.get(f"/api/payment-document-reviews/{DOCUMENT_ID}")
    assert reviews.status_code == 200
    assert reviews.json()["records"] == []
    assert response.json()["payment_authorization_enabled"] is False
    assert response.json()["final_export_enabled"] is False


def test_saving_settings_enables_draft_preview_amounts_without_persisting_manual_paper_truth(app_and_db):
    app, _session = app_and_db
    client = _client_for_role(app, models.UserRole.admin)
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
    assert before.json()["metadata"]["settings_source_status"] == "PENDING_SETTINGS"
    assert before.json()["totals"]["paper_distribution_committee_count"] == 2
    assert before.json()["totals"]["paper_distribution_compensation_amount"] is None
    assert before.json()["totals"]["grand_total_amount"] is None
    settings = client.put(f"/api/payment-document-settings/{TERM}", json=_payload())
    assert settings.status_code == 200
    after = client.post("/api/invigilation-advance-batch/official-document-draft-preview", json=draft_payload)
    assert after.status_code == 200
    assert after.json()["metadata"]["settings_source_status"] == "CONFIGURED"
    assert after.json()["metadata"]["calculation_status"] == "CALCULATED_FROM_SETTINGS"
    assert after.json()["totals"]["paper_distribution_committee_count"] == 2
    assert after.json()["totals"]["paper_distribution_compensation_amount"] == "400.00"
    assert after.json()["totals"]["grand_total_amount"] == "400.00"
    assert after.json()["payment_authorization_enabled"] is False
    assert after.json()["final_export_enabled"] is False

    without_manual_rows = client.post(
        "/api/invigilation-advance-batch/official-document-draft-preview",
        json={**draft_payload, "paper_distribution_rows": []},
    )
    assert without_manual_rows.status_code == 200
    assert without_manual_rows.json()["totals"]["paper_distribution_committee_count"] == 0


@pytest.mark.parametrize("status", ["DRAFT_CONFIG", "ARCHIVED"])
def test_non_active_settings_block_draft_calculation(app_and_db, status):
    app, _session = app_and_db
    client = _client_for_role(app, models.UserRole.admin)
    assert client.put(f"/api/payment-document-settings/{TERM}", json=_payload(status=status)).status_code == 200

    response = client.post(
        "/api/invigilation-advance-batch/official-document-draft-preview",
        json={
            "academic_year": "2568",
            "semester": "2",
            "exam_type": "final",
            "paper_distribution_rows": [
                {"exam_date": "2026-03-21", "exam_time": "09:00-12:00", "committee_count": 1}
            ],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["metadata"]["settings_source_status"] == "INCOMPLETE_SETTINGS"
    assert payload["metadata"]["calculation_status"] == "BLOCKED_INCOMPLETE_SETTINGS"
    assert payload["rows"][0]["rate_amount"] is None
    assert payload["totals"]["grand_total_amount"] is None
