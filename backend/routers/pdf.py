"""
M3 — PDF Generator (stub — จะ implement เต็มใน phase ถัดไป)
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
import models
from auth_utils import get_current_user
from config.policy import PDF_TOKEN_EXPIRE_HOURS
from services.audit_service import audit_event
import uuid, secrets
from datetime import datetime, timedelta, timezone

router = APIRouter()

@router.post("/token/{section_id}")
def generate_pdf_token(
    section_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """สร้าง one-time token สำหรับ download PDF ข้อสอบ"""
    section = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not section:
        raise HTTPException(404, "ไม่พบ section")

    token_str = secrets.token_hex(32)
    token = models.PdfToken(
        token=token_str,
        section_id=section_id,
        created_by=current_user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=PDF_TOKEN_EXPIRE_HOURS),
    )
    db.add(token)
    db.commit()
    audit_event(
        db,
        current_user,
        action="PDF_TOKEN_ISSUED",
        table_name="pdf_tokens",
        record_id=token.id,
        metadata={"section_id": section_id, "expires_in_hours": PDF_TOKEN_EXPIRE_HOURS},
        request=request,
    )
    return {"token": token_str, "expires_in": f"{PDF_TOKEN_EXPIRE_HOURS} hour"}


@router.get("/download/{token}")
def download_pdf(token: str, db: Session = Depends(get_db)):
    """Download PDF ข้อสอบด้วย one-time token"""
    t = db.query(models.PdfToken).filter(
        models.PdfToken.token == token,
        models.PdfToken.used == False,
    ).first()
    if not t or (t.expires_at and t.expires_at < datetime.now(timezone.utc)):
        raise HTTPException(403, "Token ไม่ถูกต้องหรือหมดอายุ")

    t.used = True
    db.commit()

    # TODO: implement WeasyPrint PDF generation ใน M3 phase
    return {"message": "PDF generation จะถูก implement ใน M3", "section_id": t.section_id}
