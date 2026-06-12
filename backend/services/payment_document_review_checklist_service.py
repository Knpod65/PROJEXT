"""Persistent inspection checklist for draft payment-document review."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from auth_utils import get_effective_role

DOCUMENT_TYPE = "ADVANCE_PAYMENT_DRAFT_SUMMARY"
DECISION_GATE_STATUS = "HOLD_PENDING_ADDITIONAL_REVIEW"

DEFAULT_ITEMS = (
    "CHECK_PAYMENT_DOCUMENT_SETTINGS",
    "CHECK_OFFICIAL_PAYMENT_DOCUMENT_DRAFT",
    "CHECK_REVIEW_PANEL_STATUS",
    "CHECK_DRAFT_XLSX_FILE_LAYOUT",
    "CHECK_DRAFT_ONLY_LABEL",
    "CHECK_NOT_PAYMENT_AUTHORIZATION",
    "CHECK_FINAL_AUTHORIZATION_DISABLED",
)

ALLOWED_STATUSES = {
    "NOT_STARTED",
    "IN_PROGRESS",
    "CHECKED",
    "NEEDS_ATTENTION",
    "BLOCKED",
}

READ_ROLES = {
    models.UserRole.admin,
    models.UserRole.staff,
    models.UserRole.esq_head,
    models.UserRole.secretary,
}

UPDATE_ROLES = {
    models.UserRole.admin,
    models.UserRole.esq_head,
    models.UserRole.secretary,
}


def _role_value(role: object) -> str:
    return str(role.value) if hasattr(role, "value") else str(role)


def _display_name(user: models.User) -> str:
    return str(
        getattr(user, "full_name", None)
        or getattr(user, "username", None)
        or f"user-{getattr(user, 'id', 'unknown')}"
    )


def _ensure_read_access(user: models.User) -> models.UserRole:
    role = get_effective_role(user)
    if role not in READ_ROLES:
        raise HTTPException(status_code=403, detail="payment document checklist access requires staff or reviewer role")
    return role


def _ensure_update_access(user: models.User) -> models.UserRole:
    role = _ensure_read_access(user)
    if role not in UPDATE_ROLES:
        raise HTTPException(status_code=403, detail="payment document checklist updates require reviewer role")
    return role


def _validate_document_id(document_id: str) -> tuple[str, str | None]:
    normalized = document_id.strip()
    parts = normalized.split(":")
    if len(parts) != 5 or parts[0] != DOCUMENT_TYPE:
        raise HTTPException(status_code=400, detail="unknown payment document checklist document id")
    academic_year, semester = parts[1], parts[2]
    term = f"{semester}/{academic_year}" if academic_year != "unknown" and semester != "unknown" else None
    return normalized, term


def _validate_item_key(item_key: str) -> str:
    if item_key not in DEFAULT_ITEMS:
        raise HTTPException(status_code=400, detail="unknown payment document checklist item")
    return item_key


def _validate_status(item_status: str) -> str:
    if item_status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="unknown payment document checklist status")
    return item_status


def _item_out(
    *,
    document_id: str,
    term: str | None,
    item_key: str,
    item_order: int,
    record: models.PaymentDocumentReviewChecklistItem | None,
) -> schemas.PaymentDocumentReviewChecklistItemOut:
    return schemas.PaymentDocumentReviewChecklistItemOut(
        checklist_id=record.id if record else None,
        document_id=document_id,
        document_type=DOCUMENT_TYPE,
        term=term,
        item_key=item_key,
        item_order=item_order,
        item_status=record.item_status if record else "NOT_STARTED",
        reviewer_user_id=record.reviewer_user_id if record else None,
        reviewer_name=record.reviewer_name if record else None,
        reviewer_role=record.reviewer_role if record else None,
        comment=record.comment if record else None,
        checked_at=record.checked_at if record else None,
        created_at=record.created_at if record else None,
        updated_at=record.updated_at if record else None,
        payment_authorization_enabled=False,
        final_export_enabled=False,
    )


def get_payment_document_review_checklist(
    db: Session,
    *,
    current_user: models.User,
    document_id: str,
) -> schemas.PaymentDocumentReviewChecklistResponse:
    _ensure_read_access(current_user)
    normalized_id, term = _validate_document_id(document_id)
    records = db.query(models.PaymentDocumentReviewChecklistItem).filter(
        models.PaymentDocumentReviewChecklistItem.document_id == normalized_id
    ).all()
    records_by_key = {record.item_key: record for record in records}
    items = [
        _item_out(
            document_id=normalized_id,
            term=term,
            item_key=item_key,
            item_order=index,
            record=records_by_key.get(item_key),
        )
        for index, item_key in enumerate(DEFAULT_ITEMS, start=1)
    ]
    checked_items = sum(item.item_status == "CHECKED" for item in items)
    overall_status = "CHECKED" if checked_items == len(items) else (
        "NOT_STARTED" if all(item.item_status == "NOT_STARTED" for item in items) else "IN_PROGRESS"
    )
    return schemas.PaymentDocumentReviewChecklistResponse(
        document_id=normalized_id,
        document_type=DOCUMENT_TYPE,
        term=term,
        items=items,
        total_items=len(items),
        checked_items=checked_items,
        remaining_items=len(items) - checked_items,
        overall_status=overall_status,
        decision_gate_status=DECISION_GATE_STATUS,
        payment_authorization_enabled=False,
        final_export_enabled=False,
    )


def update_payment_document_review_checklist_item(
    db: Session,
    *,
    current_user: models.User,
    document_id: str,
    item_key: str,
    payload: schemas.PaymentDocumentReviewChecklistUpdate,
) -> schemas.PaymentDocumentReviewChecklistResponse:
    role = _ensure_update_access(current_user)
    normalized_id, term = _validate_document_id(document_id)
    normalized_key = _validate_item_key(item_key)
    item_status = _validate_status(str(payload.item_status))
    item_order = DEFAULT_ITEMS.index(normalized_key) + 1
    record = db.query(models.PaymentDocumentReviewChecklistItem).filter(
        models.PaymentDocumentReviewChecklistItem.document_id == normalized_id,
        models.PaymentDocumentReviewChecklistItem.item_key == normalized_key,
    ).first()
    if record is None:
        record = models.PaymentDocumentReviewChecklistItem(
            document_id=normalized_id,
            document_type=DOCUMENT_TYPE,
            term=term,
            item_key=normalized_key,
            item_order=item_order,
        )
        db.add(record)

    now = datetime.now(timezone.utc)
    record.item_order = item_order
    record.item_status = item_status
    record.reviewer_user_id = getattr(current_user, "id", None)
    record.reviewer_name = _display_name(current_user)
    record.reviewer_role = _role_value(role)
    record.comment = payload.comment
    record.checked_at = now if item_status == "CHECKED" else None
    record.payment_authorization_enabled = False
    record.final_export_enabled = False
    db.commit()
    return get_payment_document_review_checklist(db, current_user=current_user, document_id=normalized_id)
