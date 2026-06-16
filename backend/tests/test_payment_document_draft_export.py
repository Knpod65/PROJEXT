"""Tests for gated draft payment document export endpoint.

Categories covered:
  Category 1 — gate-block tests (exp_001..008): each precondition failure → 400
  Category 5 — role permission tests (role_001..007)
  Mutation / content checks (mut_001..006)
"""
from __future__ import annotations

import copy
import io
import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import openpyxl
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
from services.thai_export_service import XLSX_THAI_FONT, has_mojibake_marker

EXPORT_URL = "/api/invigilation-advance-batch/official-document-draft-export"
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

GOOD_REQUEST = {
    "academic_year": "2568",
    "semester": "2",
    "exam_type": "final",
    "period_id": None,
    "paper_distribution_rows": [],
}

GOOD_DRAFT = {
    "metadata": {
        "academic_year": "2568",
        "semester": "2",
        "exam_type": "final",
        "term_label": "2/2568",
        "document_status": "DRAFT_NOT_AUTHORIZED",
        "settings_source_status": "CONFIGURED",
        "settings_status": "ACTIVE_FOR_DRAFT_PREVIEW",
        "settings_term": "2/2568",
        "settings_id": 1,
        "calculation_status": "CALCULATED_FROM_SETTINGS",
        "weekday_rate": "120.00",
        "weekend_rate": "200.00",
        "settings_weekday_rate": "120.00",
        "settings_weekend_rate": "200.00",
        "currency": "THB",
        "payment_unit": "PER_PERSON_SESSION",
        "paper_distribution_responsible_group": "คณะพาณิชยศาสตร์และการบัญชี",
        "paper_distribution_responsible_person": None,
        "paper_distribution_source_status": "STAFF_CONFIRMED_MANUAL_DRAFT_INPUT",
        "rate_source": "PAYMENT_DOCUMENT_SETTINGS:1",
        "rate_scope": "TERM_SPECIFIC:2/2568",
        "settings_issues": [],
    },
    "rows": [
        {
            "exam_date": "2025-10-15",
            "normalized_exam_date": "2025-10-15",
            "time_slot": "09:00-12:00",
            "start_time": "09:00",
            "end_time": "12:00",
            "day_type": "WEEKDAY",
            "rate_amount": "120.00",
            "invigilation_committee_count": 3,
            "paper_distribution_committee_count": 2,
            "invigilation_compensation_amount": "360.00",
            "paper_distribution_compensation_amount": "240.00",
            "total_compensation_amount": "600.00",
            "source_notes": [],
            "warnings": [],
        }
    ],
    "totals": {
        "invigilation_committee_count": 3,
        "invigilation_compensation_amount": "360.00",
        "paper_distribution_committee_count": 2,
        "paper_distribution_compensation_amount": "240.00",
        "grand_total_amount": "600.00",
        "row_count": 1,
    },
    "warnings": [],
    "draft_only": True,
    "payment_authorization_enabled": False,
    "final_export_enabled": False,
    "supervisor_finance_review_required": True,
}

_PATCH_TARGET = (
    "services.payment_document_draft_export_service"
    ".build_official_payment_document_draft_preview"
)


@pytest.fixture()
def app_and_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    app = FastAPI()
    app.include_router(router, prefix="/api/invigilation-advance-batch")
    app.dependency_overrides[get_db] = lambda: session
    yield app, session
    session.close()


def _client(app: FastAPI, role: "models.UserRole") -> TestClient:
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=1,
        role=role,
        view_as_role=None,
        _active_role=role,
    )
    return TestClient(app)


def _seed_review(
    session,
    review_status: str = "ACCEPTED_FOR_DRAFT_EXPORT",
    comment: str = "ยืนยันรูปแบบร่างสำหรับการ export",
    document_id: str = "ADVANCE_PAYMENT_DRAFT_SUMMARY:2568:2:final:all",
) -> "models.PaymentDocumentReviewRecord":
    record = models.PaymentDocumentReviewRecord(
        document_id=document_id,
        document_type="ADVANCE_PAYMENT_DRAFT_SUMMARY",
        term="2/2568",
        review_status=review_status,
        comment=comment,
        reviewer_name="ผู้ทดสอบ",
        reviewer_role="admin",
        payment_authorization_enabled=False,
        final_export_enabled=False,
    )
    session.add(record)
    session.commit()
    return record


def _patched_good(app, session):
    _seed_review(session)
    client = _client(app, models.UserRole.admin)
    with patch(_PATCH_TARGET, return_value=copy.deepcopy(GOOD_DRAFT)):
        resp = client.post(EXPORT_URL, json=GOOD_REQUEST)
    return resp


# ---------------------------------------------------------------------------
# Category 1 — Gate-block tests
# ---------------------------------------------------------------------------


def test_exp_001_no_accepted_review(app_and_db):
    """Export blocked: no ACCEPTED_FOR_DRAFT_EXPORT review record."""
    app, session = app_and_db
    # Seed a review with a different status
    _seed_review(session, review_status="DRAFT_READY_FOR_REVIEW")
    with patch(_PATCH_TARGET, return_value=copy.deepcopy(GOOD_DRAFT)):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code == 400
    assert "ACCEPTED_FOR_DRAFT_EXPORT" in resp.json()["detail"]


def test_exp_002_empty_review_comment(app_and_db):
    """Export blocked: review accepted but comment is empty."""
    app, session = app_and_db
    _seed_review(session, comment="")
    with patch(_PATCH_TARGET, return_value=copy.deepcopy(GOOD_DRAFT)):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code == 400
    assert "comment" in resp.json()["detail"].lower()


def test_exp_003_settings_not_configured(app_and_db):
    """Export blocked: settings_source_status != CONFIGURED."""
    app, session = app_and_db
    _seed_review(session)
    bad_draft = copy.deepcopy(GOOD_DRAFT)
    bad_draft["metadata"]["settings_source_status"] = "PENDING_SETTINGS"
    with patch(_PATCH_TARGET, return_value=bad_draft):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code == 400
    assert "settings_source_status" in resp.json()["detail"]


def test_exp_004_settings_status_not_active(app_and_db):
    """Export blocked: settings_status != ACTIVE_FOR_DRAFT_PREVIEW."""
    app, session = app_and_db
    _seed_review(session)
    bad_draft = copy.deepcopy(GOOD_DRAFT)
    bad_draft["metadata"]["settings_status"] = "ARCHIVED"
    with patch(_PATCH_TARGET, return_value=bad_draft):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code == 400
    assert "settings_status" in resp.json()["detail"]


def test_exp_005_calculation_not_from_settings(app_and_db):
    """Export blocked: calculation_status != CALCULATED_FROM_SETTINGS."""
    app, session = app_and_db
    _seed_review(session)
    bad_draft = copy.deepcopy(GOOD_DRAFT)
    bad_draft["metadata"]["calculation_status"] = "BLOCKED_PENDING_SETTINGS"
    with patch(_PATCH_TARGET, return_value=bad_draft):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code == 400
    assert "calculation_status" in resp.json()["detail"]


def test_exp_006_paper_group_empty(app_and_db):
    """Export blocked: paper_distribution_responsible_group is empty."""
    app, session = app_and_db
    _seed_review(session)
    bad_draft = copy.deepcopy(GOOD_DRAFT)
    bad_draft["metadata"]["paper_distribution_responsible_group"] = ""
    with patch(_PATCH_TARGET, return_value=bad_draft):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code == 400
    assert "paper_distribution_responsible_group" in resp.json()["detail"]


def test_exp_007_payment_auth_enabled_true(app_and_db):
    """Export blocked: payment_authorization_enabled = True (must always be false)."""
    app, session = app_and_db
    _seed_review(session)
    bad_draft = copy.deepcopy(GOOD_DRAFT)
    bad_draft["payment_authorization_enabled"] = True
    with patch(_PATCH_TARGET, return_value=bad_draft):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code == 400
    assert "payment_authorization_enabled" in resp.json()["detail"]


def test_exp_008_final_export_enabled_true(app_and_db):
    """Export blocked: final_export_enabled = True (must always be false)."""
    app, session = app_and_db
    _seed_review(session)
    bad_draft = copy.deepcopy(GOOD_DRAFT)
    bad_draft["final_export_enabled"] = True
    with patch(_PATCH_TARGET, return_value=bad_draft):
        resp = _client(app, models.UserRole.admin).post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code == 400
    assert "final_export_enabled" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Category 5 — Role permission tests
# ---------------------------------------------------------------------------


def test_role_001_admin_allowed(app_and_db):
    """Admin: export allowed when all preconditions met."""
    app, session = app_and_db
    resp = _patched_good(app, session)
    assert resp.status_code == 200
    assert XLSX_MIME in resp.headers.get("content-type", "")


def test_role_002_esq_head_allowed(app_and_db):
    """ESQ head: export allowed."""
    app, session = app_and_db
    _seed_review(session)
    client = _client(app, models.UserRole.esq_head)
    with patch(_PATCH_TARGET, return_value=copy.deepcopy(GOOD_DRAFT)):
        resp = client.post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code == 200


def test_role_003_secretary_allowed(app_and_db):
    """Secretary: export allowed."""
    app, session = app_and_db
    _seed_review(session)
    client = _client(app, models.UserRole.secretary)
    with patch(_PATCH_TARGET, return_value=copy.deepcopy(GOOD_DRAFT)):
        resp = client.post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code == 200


def test_role_004_staff_blocked(app_and_db):
    """Staff: export blocked — 403."""
    app, session = app_and_db
    _seed_review(session)
    client = _client(app, models.UserRole.staff)
    with patch(_PATCH_TARGET, return_value=copy.deepcopy(GOOD_DRAFT)):
        resp = client.post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code == 403


def test_role_005_teacher_blocked(app_and_db):
    """Teacher: export blocked — 403."""
    app, session = app_and_db
    client = _client(app, models.UserRole.teacher)
    resp = client.post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code == 403


def test_role_006_print_shop_blocked(app_and_db):
    """Print shop: export blocked — 403."""
    app, session = app_and_db
    client = _client(app, models.UserRole.print_shop)
    resp = client.post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code == 403


def test_role_007_unauthenticated_blocked(app_and_db):
    """Unauthenticated: no user override — must not be 200."""
    app, _ = app_and_db
    # Remove any role override so the real auth dependency runs
    app.dependency_overrides.pop(get_current_user, None)
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post(EXPORT_URL, json=GOOD_REQUEST)
    assert resp.status_code in (401, 403, 422)


# ---------------------------------------------------------------------------
# Mutation / content checks
# ---------------------------------------------------------------------------


def test_mut_001_review_count_unchanged(app_and_db):
    """Export does not create or delete review records."""
    app, session = app_and_db
    _seed_review(session)
    count_before = session.query(models.PaymentDocumentReviewRecord).count()
    with patch(_PATCH_TARGET, return_value=copy.deepcopy(GOOD_DRAFT)):
        _client(app, models.UserRole.admin).post(EXPORT_URL, json=GOOD_REQUEST)
    count_after = session.query(models.PaymentDocumentReviewRecord).count()
    assert count_before == count_after


def test_mut_002_content_type_is_xlsx(app_and_db):
    """Response Content-Type is xlsx."""
    app, session = app_and_db
    resp = _patched_good(app, session)
    assert XLSX_MIME in resp.headers.get("content-type", "")


def test_mut_003_content_disposition_header(app_and_db):
    """Content-Disposition header is present and contains filename."""
    app, session = app_and_db
    resp = _patched_good(app, session)
    cd = resp.headers.get("content-disposition", "")
    assert "attachment" in cd
    assert "EMS_DRAFT_PAYMENT_DOCUMENT" in cd
    assert ".xlsx" in cd
    assert "filename*=UTF-8''" in cd


def test_mut_004_response_is_binary(app_and_db):
    """Response body is bytes (xlsx magic bytes PK\\x03\\x04)."""
    app, session = app_and_db
    resp = _patched_good(app, session)
    assert resp.status_code == 200
    assert resp.content[:4] == b"PK\x03\x04"


def test_mut_004b_workbook_preserves_thai_values_and_fonts(app_and_db):
    """Reopened workbook keeps exact Thai values and Thai-capable font names."""
    app, session = app_and_db
    resp = _patched_good(app, session)
    workbook = openpyxl.load_workbook(io.BytesIO(resp.content), data_only=False)
    draft = workbook["ร่างเอกสาร"]
    review = workbook["การตรวจร่าง"]

    assert draft["A1"].value == "ร่างเอกสารเพื่อการตรวจทานเท่านั้น ยังไม่ใช่เอกสารอนุมัติเบิกจ่าย"
    assert draft["A6"].value == "ภาคการศึกษา: 2/2568"
    assert draft["A9"].value == "วันที่สอบ"
    assert review["A11"].value == "สถานะเอกสาร (Document Status)"
    assert draft["A1"].font.name == XLSX_THAI_FONT
    assert draft["A9"].font.name == XLSX_THAI_FONT
    assert review["A1"].font.name == XLSX_THAI_FONT
    for sheet in workbook.worksheets:
        assert not has_mojibake_marker(sheet.title)
        for row in sheet.iter_rows():
            for cell in row:
                assert not has_mojibake_marker(cell.value)


def test_mut_005_filename_contains_draft(app_and_db):
    """Filename includes DRAFT — not 'final', 'official', or 'authorized'."""
    app, session = app_and_db
    resp = _patched_good(app, session)
    cd = resp.headers.get("content-disposition", "").lower()
    assert "draft" in cd
    assert "final" not in cd
    assert "authorized" not in cd
    assert "official" not in cd


def test_mut_006_payment_auth_never_true_in_review(app_and_db):
    """Review records in DB never have payment_authorization_enabled=True after export."""
    app, session = app_and_db
    _seed_review(session)
    with patch(_PATCH_TARGET, return_value=copy.deepcopy(GOOD_DRAFT)):
        _client(app, models.UserRole.admin).post(EXPORT_URL, json=GOOD_REQUEST)
    records = session.query(models.PaymentDocumentReviewRecord).all()
    for rec in records:
        assert rec.payment_authorization_enabled is False or rec.payment_authorization_enabled == 0
