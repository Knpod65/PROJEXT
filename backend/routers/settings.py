"""
Settings Router - system-wide configuration (admin only)
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth_utils import log_action, require_base_admin
from database import get_db
import models

router = APIRouter()

VALID_KEYS = {
    "exam_format_deadline": "Deadline for confirming exam format (ISO 8601)",
    "exam_submission_deadline": "Deadline for exam submission (ISO 8601)",
    "swap_request_deadline": "Deadline for swap requests (ISO 8601)",
    "swap_enabled": "Enable or disable swap workflow (true/false)",
    "current_semester": "Current semester",
    "current_academic_year": "Current academic year (BE)",
    "printshop_copies_buffer": "Extra printshop copy buffer percentage",
}


def get_setting(db: Session, key: str) -> str | None:
    row = db.query(models.SystemSetting).filter(
        models.SystemSetting.key == key
    ).first()
    return row.value if row else None


def is_past_deadline(db: Session, key: str) -> bool:
    value = get_setting(db, key)
    if not value:
        return False

    try:
        deadline = datetime.fromisoformat(value)
    except Exception:
        return False

    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)

    return datetime.now(timezone.utc) > deadline


@router.get("/")
def list_settings(
    db: Session = Depends(get_db),
    _=Depends(require_base_admin),
):
    rows = db.query(models.SystemSetting).all()
    result = {}
    for key, desc in VALID_KEYS.items():
        row = next((item for item in rows if item.key == key), None)
        result[key] = {
            "value": row.value if row else None,
            "description": desc,
            "updated_at": row.updated_at.isoformat() if row and row.updated_at else None,
        }
    return result


@router.put("/{key}")
def update_setting(
    key: str,
    value: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_base_admin),
):
    if key not in VALID_KEYS:
        raise HTTPException(400, f"key '{key}' not supported")

    row = db.query(models.SystemSetting).filter(
        models.SystemSetting.key == key
    ).first()
    old_value = row.value if row else None

    if row:
        row.value = value
        row.updated_by = current_user.id
    else:
        row = models.SystemSetting(
            key=key,
            value=value,
            description=VALID_KEYS[key],
            updated_by=current_user.id,
        )
        db.add(row)

    db.commit()
    log_action(
        db,
        current_user,
        f"SETTING_{key.upper()}",
        "system_settings",
        old_values={"value": old_value},
        new_values={"value": value},
        request=request,
    )
    return {"key": key, "value": value, "updated": True}


@router.get("/public/deadlines")
def public_deadlines(db: Session = Depends(get_db)):
    keys = [
        "exam_format_deadline",
        "exam_submission_deadline",
        "swap_request_deadline",
        "swap_enabled",
    ]
    return {key: get_setting(db, key) for key in keys}
