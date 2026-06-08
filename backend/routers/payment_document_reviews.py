"""Persistent draft payment document review routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import schemas
from auth_utils import get_current_user
from database import get_db
from services.payment_document_review_service import (
    create_payment_document_review,
    get_payment_document_reviews,
    list_payment_document_reviews,
    update_payment_document_review,
)

router = APIRouter()


@router.get("", response_model=schemas.PaymentDocumentReviewListResponse)
def list_reviews(
    document_id: str | None = Query(default=None),
    document_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return list_payment_document_reviews(
        db,
        current_user=current_user,
        document_id=document_id,
        document_type=document_type,
    )


@router.get("/{document_id}", response_model=schemas.PaymentDocumentReviewListResponse)
def get_reviews_for_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_payment_document_reviews(
        db,
        current_user=current_user,
        document_id=document_id,
    )


@router.post("", response_model=schemas.PaymentDocumentReviewOut)
def create_review(
    payload: schemas.PaymentDocumentReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_payment_document_review(
        db,
        current_user=current_user,
        payload=payload,
    )


@router.put("/{review_id}", response_model=schemas.PaymentDocumentReviewOut)
def update_review(
    review_id: int,
    payload: schemas.PaymentDocumentReviewUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return update_payment_document_review(
        db,
        current_user=current_user,
        review_id=review_id,
        payload=payload,
    )
