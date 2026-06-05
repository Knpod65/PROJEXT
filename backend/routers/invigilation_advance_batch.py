"""Preview-only advance invigilation batch roster routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import schemas
from auth_utils import require_staff_or_admin
from database import get_db
from services.invigilation_advance_batch_preview_service import build_advance_batch_preview
from services.official_payment_document_draft_service import build_official_payment_document_draft_preview

router = APIRouter()


@router.get("/preview", response_model=schemas.AdvanceInvigilationBatchPreviewResponse)
def preview_advance_invigilation_batch(
    period_id: int | None = Query(default=None),
    academic_year: str | None = Query(default=None),
    semester: str | None = Query(default=None),
    exam_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _current_user=Depends(require_staff_or_admin),
):
    return build_advance_batch_preview(
        db,
        period_id=period_id,
        academic_year=academic_year,
        semester=semester,
        exam_type=exam_type,
    )


@router.post("/official-document-draft-preview", response_model=schemas.OfficialPaymentDocumentDraftResponse)
def preview_official_payment_document_draft(
    payload: schemas.OfficialPaymentDocumentDraftRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(require_staff_or_admin),
):
    return build_official_payment_document_draft_preview(
        db,
        payload.model_dump(),
    )
