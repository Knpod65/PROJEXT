"""Draft payment-document settings routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import schemas
from auth_utils import get_current_user
from database import get_db
from services.payment_document_settings_service import (
    get_payment_document_settings,
    list_payment_document_settings,
    save_payment_document_settings,
)

router = APIRouter()


@router.get("", response_model=schemas.PaymentDocumentSettingsListResponse)
def list_settings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return list_payment_document_settings(db, current_user=current_user)


@router.get("/{term:path}", response_model=schemas.PaymentDocumentSettingsOut)
def get_settings(
    term: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_payment_document_settings(db, current_user=current_user, term=term)


@router.put("/{term:path}", response_model=schemas.PaymentDocumentSettingsOut)
def put_settings(
    term: str,
    payload: schemas.PaymentDocumentSettingsUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return save_payment_document_settings(db, current_user=current_user, term=term, payload=payload)
