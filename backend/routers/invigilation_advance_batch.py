"""Preview-only advance invigilation batch roster routes."""
from __future__ import annotations

import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

import schemas
from auth_utils import require_staff_or_admin, require_view_all
from database import get_db
from services.invigilation_advance_batch_preview_service import build_advance_batch_preview
from services.official_payment_document_draft_service import build_official_payment_document_draft_preview
from services.payment_document_draft_export_service import build_payment_document_draft_export

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


@router.post("/official-document-draft-export")
def export_official_payment_document_draft(
    payload: schemas.OfficialPaymentDocumentDraftRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(require_view_all),
):
    wb, filename = build_payment_document_draft_export(db, payload.model_dump())
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
