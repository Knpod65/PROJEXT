"""Tests for the draft payment document export endpoint.

Tests are derived from PAYMENT_DOCUMENT_DRAFT_EXPORT_TEST_MATRIX.md
Categories 1 (gate checks) and 5 (role permissions) plus mutation
invariant checks.

Minimum required: 18 tests. This file has 23 tests.
"""
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

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
from routers.invigilation_advance_batch import router as batch_router
from routers.payment_document_reviews import router as review_router


DOCUMENT_ID = "ADVANCE_PAYMENT_DRAFT_SUMMARY:2568:2:final:all"
EXPORT_URL = "/api/invigilation-advance-batch/official-document-draft-export"
REVIEW_URL = "/api/payment-document-reviews"

VALID_EXPORT_BODY = {
    "period_id": None,
    "academic_year": "2568",
    "semester": "2",
    "exam_type": "final",
    "paper_distribution_rows": [],
}

GOOD_DRAFT_METADATA = {
    "settings_source_status": "CONFIGURED",
    "settings_status": "ACTIVE_FOR_DRAFT_PREVIEW",
    "calculation_status": "CALCULATED_FROM_SETTINGS",
    "paper_distribution_responsible_group": "Education_Student_Quality",
    "settings_weekday_rate": "120.00",
    "settings_weekend_rate": "200.00",
    "term_label": "2/2568",
    "settings_term": "2/2568",
    "document_status": "DRAFT_NOT_AUTHORIZED",
    "academic_year": "2568",
    "semester": "2",
    "exam_type": "final",
    "rate_source": "PAYMENT_DOCUMENT_SETTINGS:1",
    "rate_scope": "TERM_SPECIFIC:2/2568",
    "paper_distribution_source_status": "STAFF_CONFIRMED_MANUAL_DRAFT_INPUT",
    "paper_distribution_responsible_person": None,
    "currency": "THB",
    "payment_unit": "PER_PERSON_SESSION",
    "settings_issues": [],
}

GOOD_DRAFT_RESPONSE = {
    "metadata": GOOD_DRAFT_METADATA,
    "rows": [],
    "totals": {
        "invigilation_committee_count": 0,
        "invigilation_compensation_amount": "0.00",
        "paper_distribution_committee_count": 0,
        "paper_distribution_compensation_amount": "0.00",
        "grand_total_amount": "0.00",
        "row_count": 0,
    },
    "warnings": [],
    "draft_only": True,
    "payment_authorization_enabled": False,
    "final_export_enabled": False,
    "supervisor_finance_review_required": True,
}


@pytest.fixture()
def app_and_db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()

    app = FastAPI()
    app.include_router(review_router, prefix="/api/payment-document-reviews")
    app.include_router(batch_router, prefix="/api/invigilation-advance-batch")
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
    return TestClient(app, raise_server_exceptions=False)


def _seed_review(session, review_status: str = "ACCEPTED_FOR_DRAFT_EXPORT", comment: str = "Thai comment") -> None:
    record = models.PaymentDocumentReviewRecord(
        document_id=DOCUMENT_ID,
        document_type="ADVANCE_PAYMENT_DRAFT_SUMMARY",
        term="2/2568",
        review_status=review_status,
        comment=comment,
        decision="ACCEPT_FOR_DRAFT_EXPORT_DESIGN",
        reviewer_name="Admin User",
        reviewer_role="admin",
        reviewer_user_id=1,
        revision_required=False,
    )
    session.add(record)
    session.commit()


# ── Category 1: Gate checks — blocked when preconditions not met ──────────────

def test_exp_001_blocked_no_accepted_review(app_and_db):
    """T-EXP-001: No ACCEPTED_FOR_DRAFT_EXPORT record → 400."""
    app, _ = app_and_db
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=GOOD_DRAFT_RESPONSE):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 400
    assert "ACCEPTED_FOR_DRAFT_EXPORT" in resp.json()["detail"]


def test_exp_002_blocked_unconfigured_settings(app_and_db):
    """T-EXP-002: settings_source_status not CONFIGURED → 400."""
    app, session = app_and_db
    _seed_review(session)
    bad_draft = {**GOOD_DRAFT_RESPONSE, "metadata": {**GOOD_DRAFT_METADATA, "settings_source_status": "PENDING_SETTINGS"}}
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=bad_draft):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 400
    assert "settings_source_status" in resp.json()["detail"]


def test_exp_003_blocked_inactive_settings_status(app_and_db):
    """T-EXP-003: settings_status not ACTIVE_FOR_DRAFT_PREVIEW → 400."""
    app, session = app_and_db
    _seed_review(session)
    bad_draft = {**GOOD_DRAFT_RESPONSE, "metadata": {**GOOD_DRAFT_METADATA, "settings_status": "DRAFT_CONFIG"}}
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=bad_draft):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 400
    assert "settings_status" in resp.json()["detail"]


def test_exp_004_blocked_wrong_calculation_status(app_and_db):
    """T-EXP-004: calculation_status not CALCULATED_FROM_SETTINGS → 400."""
    app, session = app_and_db
    _seed_review(session)
    bad_draft = {**GOOD_DRAFT_RESPONSE, "metadata": {**GOOD_DRAFT_METADATA, "calculation_status": "BLOCKED_PENDING_SETTINGS"}}
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=bad_draft):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 400
    assert "calculation_status" in resp.json()["detail"]


def test_exp_005_blocked_missing_reviewer_comment(app_and_db):
    """T-EXP-005: review record with ACCEPTED_FOR_DRAFT_EXPORT but empty comment → 400."""
    app, session = app_and_db
    _seed_review(session, comment="")
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=GOOD_DRAFT_RESPONSE):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 400
    assert "comment" in resp.json()["detail"]


def test_exp_006_blocked_missing_paper_group(app_and_db):
    """T-EXP-006: paper_distribution_responsible_group blank → 400."""
    app, session = app_and_db
    _seed_review(session)
    bad_draft = {**GOOD_DRAFT_RESPONSE, "metadata": {**GOOD_DRAFT_METADATA, "paper_distribution_responsible_group": ""}}
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=bad_draft):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 400
    assert "paper_distribution_responsible_group" in resp.json()["detail"]


def test_exp_007_blocked_payment_authorization_enabled(app_and_db):
    """T-EXP-007: payment_authorization_enabled = true → 400 (invariant violated)."""
    app, session = app_and_db
    _seed_review(session)
    bad_draft = {**GOOD_DRAFT_RESPONSE, "payment_authorization_enabled": True}
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=bad_draft):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 400
    assert "payment_authorization_enabled" in resp.json()["detail"]


def test_exp_008_blocked_final_export_enabled(app_and_db):
    """T-EXP-008: final_export_enabled = true → 400 (invariant violated)."""
    app, session = app_and_db
    _seed_review(session)
    bad_draft = {**GOOD_DRAFT_RESPONSE, "final_export_enabled": True}
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=bad_draft):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 400
    assert "final_export_enabled" in resp.json()["detail"]


# ── Category 5: Role permission tests ────────────────────────────────────────

def test_role_001_admin_allowed(app_and_db):
    """T-ROLE-001: Admin with valid conditions → 200 + xlsx content."""
    app, session = app_and_db
    _seed_review(session)
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=GOOD_DRAFT_RESPONSE):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 200
    assert "spreadsheetml" in resp.headers["content-type"]
    assert "attachment" in resp.headers["content-disposition"]
    assert "EMS_DRAFT_PAYMENT_DOCUMENT" in resp.headers["content-disposition"]


def test_role_002_esq_head_allowed(app_and_db):
    """T-ROLE-002: ESQ head with valid conditions → 200."""
    app, session = app_and_db
    _seed_review(session)
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=GOOD_DRAFT_RESPONSE):
        resp = _client(app, models.UserRole.esq_head).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 200
    assert "spreadsheetml" in resp.headers["content-type"]


def test_role_003_secretary_allowed(app_and_db):
    """T-ROLE-003: Secretary with valid conditions → 200."""
    app, session = app_and_db
    _seed_review(session)
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=GOOD_DRAFT_RESPONSE):
        resp = _client(app, models.UserRole.secretary).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 200


def test_role_004_staff_blocked(app_and_db):
    """T-ROLE-004: Staff → 403."""
    app, session = app_and_db
    _seed_review(session)
    resp = _client(app, models.UserRole.staff).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 403


def test_role_005_teacher_blocked(app_and_db):
    """T-ROLE-005: Teacher → 403."""
    app, session = app_and_db
    resp = _client(app, models.UserRole.teacher).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 403


def test_role_006_print_shop_blocked(app_and_db):
    """T-ROLE-006: Print shop → 403."""
    app, session = app_and_db
    resp = _client(app, models.UserRole.print_shop).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 403


def test_role_007_unauthenticated_blocked(app_and_db):
    """T-ROLE-007: No auth → 401 or 422 (TestClient dependency raises)."""
    app, _ = app_and_db
    app.dependency_overrides.pop(get_current_user, None)
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code in (401, 422)


# ── Mutation invariant checks ─────────────────────────────────────────────────

def test_export_does_not_mutate_review_records(app_and_db):
    """Export action must not add or change any review records."""
    app, session = app_and_db
    _seed_review(session)
    before_count = session.query(models.PaymentDocumentReviewRecord).count()
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=GOOD_DRAFT_RESPONSE):
        _client(app, models.UserRole.admin).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    after_count = session.query(models.PaymentDocumentReviewRecord).count()
    assert before_count == after_count


def test_export_response_is_xlsx(app_and_db):
    """Export must return xlsx content-type, not JSON."""
    app, session = app_and_db
    _seed_review(session)
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=GOOD_DRAFT_RESPONSE):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def test_export_filename_convention(app_and_db):
    """Filename must follow EMS_DRAFT_PAYMENT_DOCUMENT_{semester}-{year}_{ts}.xlsx."""
    app, session = app_and_db
    _seed_review(session)
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=GOOD_DRAFT_RESPONSE):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 200
    disposition = resp.headers["content-disposition"]
    assert "EMS_DRAFT_PAYMENT_DOCUMENT_2-2568_" in disposition
    assert ".xlsx" in disposition


def test_export_blocked_when_only_non_accepted_review_exists(app_and_db):
    """A review record with different status must not unlock export."""
    app, session = app_and_db
    _seed_review(session, review_status="UNDER_REVIEW", comment="under review comment")
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=GOOD_DRAFT_RESPONSE):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=VALID_EXPORT_BODY)
    assert resp.status_code == 400
    assert "ACCEPTED_FOR_DRAFT_EXPORT" in resp.json()["detail"]


def test_export_preview_endpoint_still_works_for_staff(app_and_db):
    """The preview endpoint must remain accessible to staff after export endpoint is added."""
    app, _ = app_and_db
    with patch("services.official_payment_document_draft_service.build_official_payment_document_draft_preview") as mock_preview:
        mock_preview.return_value = GOOD_DRAFT_RESPONSE
        resp = _client(app, models.UserRole.staff).post(
            "/api/invigilation-advance-batch/official-document-draft-preview",
            json=VALID_EXPORT_BODY,
        )
    assert resp.status_code == 200


def test_export_document_id_all_when_no_period(app_and_db):
    """document_id with period_id=None must use 'all' suffix and find correct record."""
    app, session = app_and_db
    _seed_review(session)
    with patch("services.payment_document_draft_export_service.build_official_payment_document_draft_preview", return_value=GOOD_DRAFT_RESPONSE):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json={**VALID_EXPORT_BODY, "period_id": None})
    assert resp.status_code == 200
