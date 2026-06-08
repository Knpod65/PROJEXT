"""Persistent review records for draft payment documents."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from auth_utils import get_effective_role

ALLOWED_DOCUMENT_TYPES = {
    "ADVANCE_PAYMENT_DRAFT_SUMMARY",
    "PAYMENT_RECONCILIATION_DRAFT",
    "ABSENCE_EXPLANATION_REQUEST",
    "REFUND_OFFSET_TRACKING_DRAFT",
}

ALLOWED_REVIEW_STATUSES = {
    "DRAFT_NOT_AUTHORIZED",
    "DRAFT_READY_FOR_REVIEW",
    "UNDER_REVIEW",
    "REVISIONS_REQUESTED",
    "ACCEPTED_FOR_DRAFT_EXPORT",
    "REJECTED_REDESIGN_REQUIRED",
    "FINAL_AUTHORIZATION_REQUIRED",
}

COMMENT_ROLES = {
    models.UserRole.admin,
    models.UserRole.staff,
    models.UserRole.esq_head,
    models.UserRole.secretary,
}

REVIEW_DECISION_ROLES = {
    models.UserRole.admin,
    models.UserRole.esq_head,
    models.UserRole.secretary,
}

STAFF_ALLOWED_STATUSES = {
    "DRAFT_READY_FOR_REVIEW",
}


def _role_value(role: object) -> str:
    if hasattr(role, "value"):
        return str(role.value)
    return str(role)


def _display_name(user: models.User) -> str:
    full_name = getattr(user, "full_name", None)
    username = getattr(user, "username", None)
    if full_name:
        return str(full_name)
    if username:
        return str(username)
    user_id = getattr(user, "id", None)
    return f"user-{user_id}" if user_id is not None else "unknown"


def _ensure_comment_access(user: models.User) -> models.UserRole:
    role = get_effective_role(user)
    if role not in COMMENT_ROLES:
        raise HTTPException(status_code=403, detail="payment document review access requires staff or reviewer role")
    return role


def _validate_document_type(document_type: str) -> None:
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail="unknown payment document type")


def _validate_status(review_status: str) -> None:
    if review_status not in ALLOWED_REVIEW_STATUSES:
        raise HTTPException(status_code=400, detail="unknown payment document review status")


def _ensure_status_access(role: models.UserRole, review_status: str) -> None:
    _validate_status(review_status)
    if role in REVIEW_DECISION_ROLES:
        return
    if role == models.UserRole.staff and review_status in STAFF_ALLOWED_STATUSES:
        return
    raise HTTPException(status_code=403, detail="review decision status requires reviewer role")


def _to_out(record: models.PaymentDocumentReviewRecord) -> schemas.PaymentDocumentReviewOut:
    return schemas.PaymentDocumentReviewOut(
        review_id=record.id,
        document_id=record.document_id,
        document_type=record.document_type,
        term=record.term,
        review_status=record.review_status,
        comment=record.comment,
        decision=record.decision,
        reviewer_name=record.reviewer_name,
        reviewer_role=record.reviewer_role,
        reviewer_user_id=record.reviewer_user_id,
        prepared_by=record.prepared_by,
        created_at=record.created_at,
        updated_at=record.updated_at,
        reviewed_at=record.reviewed_at,
        revision_required=bool(record.revision_required),
        note=record.note,
        payment_authorization_enabled=False,
        final_export_enabled=False,
    )


def _list_response(records: Iterable[models.PaymentDocumentReviewRecord]) -> schemas.PaymentDocumentReviewListResponse:
    return schemas.PaymentDocumentReviewListResponse(
        records=[_to_out(record) for record in records],
        payment_authorization_enabled=False,
        final_export_enabled=False,
    )


def list_payment_document_reviews(
    db: Session,
    *,
    current_user: models.User,
    document_id: str | None = None,
    document_type: str | None = None,
) -> schemas.PaymentDocumentReviewListResponse:
    _ensure_comment_access(current_user)
    if document_type:
        _validate_document_type(document_type)

    query = db.query(models.PaymentDocumentReviewRecord)
    if document_id:
        query = query.filter(models.PaymentDocumentReviewRecord.document_id == document_id)
    if document_type:
        query = query.filter(models.PaymentDocumentReviewRecord.document_type == document_type)

    records = query.order_by(models.PaymentDocumentReviewRecord.created_at.desc(), models.PaymentDocumentReviewRecord.id.desc()).all()
    return _list_response(records)


def get_payment_document_reviews(
    db: Session,
    *,
    current_user: models.User,
    document_id: str,
) -> schemas.PaymentDocumentReviewListResponse:
    return list_payment_document_reviews(db, current_user=current_user, document_id=document_id)


def create_payment_document_review(
    db: Session,
    *,
    current_user: models.User,
    payload: schemas.PaymentDocumentReviewCreate,
) -> schemas.PaymentDocumentReviewOut:
    role = _ensure_comment_access(current_user)
    document_type = str(payload.document_type)
    review_status = str(payload.review_status)
    _validate_document_type(document_type)
    _ensure_status_access(role, review_status)

    now = datetime.now(timezone.utc)
    record = models.PaymentDocumentReviewRecord(
        document_id=payload.document_id.strip(),
        document_type=document_type,
        term=payload.term,
        review_status=review_status,
        comment=payload.comment,
        decision=payload.decision,
        reviewer_name=_display_name(current_user),
        reviewer_role=_role_value(role),
        reviewer_user_id=getattr(current_user, "id", None),
        prepared_by=payload.prepared_by,
        reviewed_at=now,
        revision_required=bool(payload.revision_required),
        note=payload.note,
        payment_authorization_enabled=False,
        final_export_enabled=False,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _to_out(record)


def update_payment_document_review(
    db: Session,
    *,
    current_user: models.User,
    review_id: int,
    payload: schemas.PaymentDocumentReviewUpdate,
) -> schemas.PaymentDocumentReviewOut:
    role = _ensure_comment_access(current_user)
    record = db.query(models.PaymentDocumentReviewRecord).filter(
        models.PaymentDocumentReviewRecord.id == review_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="payment document review record not found")

    if payload.review_status is not None:
        review_status = str(payload.review_status)
        _ensure_status_access(role, review_status)
        record.review_status = review_status

    if payload.comment is not None:
        record.comment = payload.comment
    if payload.decision is not None:
        record.decision = payload.decision
    if payload.revision_required is not None:
        record.revision_required = bool(payload.revision_required)
    if payload.note is not None:
        record.note = payload.note

    record.reviewer_name = _display_name(current_user)
    record.reviewer_role = _role_value(role)
    record.reviewer_user_id = getattr(current_user, "id", None)
    record.reviewed_at = datetime.now(timezone.utc)
    record.payment_authorization_enabled = False
    record.final_export_enabled = False

    db.commit()
    db.refresh(record)
    return _to_out(record)
