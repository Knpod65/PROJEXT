"""In-system inspection checklist routes for draft payment documents."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import schemas
from auth_utils import get_current_user
from database import get_db
from services.payment_document_review_checklist_service import (
    get_payment_document_review_checklist,
    update_payment_document_review_checklist_item,
)

router = APIRouter()


@router.get("/{document_id}", response_model=schemas.PaymentDocumentReviewChecklistResponse)
def get_checklist(
    document_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_payment_document_review_checklist(
        db,
        current_user=current_user,
        document_id=document_id,
    )


@router.put("/{document_id}/items/{item_key}", response_model=schemas.PaymentDocumentReviewChecklistResponse)
def update_checklist_item(
    document_id: str,
    item_key: str,
    payload: schemas.PaymentDocumentReviewChecklistUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return update_payment_document_review_checklist_item(
        db,
        current_user=current_user,
        document_id=document_id,
        item_key=item_key,
        payload=payload,
    )
