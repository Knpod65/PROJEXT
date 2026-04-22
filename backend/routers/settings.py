"""
Settings Router - system-wide configuration (admin only)
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth_utils import log_action, require_base_admin
from database import get_db
import models
import schemas
from term_lifecycle import (
    get_active_period,
    get_all_periods,
    get_latest_historical_term,
    get_latest_term,
    get_period_status,
    period_to_dict,
    resolve_preview_term,
)

router = APIRouter()

VALID_KEYS = {
    "exam_format_deadline": "Deadline for confirming exam format (ISO 8601)",
    "exam_submission_deadline": "Deadline for exam submission (ISO 8601)",
    "swap_request_deadline": "Deadline for swap requests (ISO 8601)",
    "swap_enabled": "Enable or disable swap workflow (true/false)",
    "current_semester": "Current semester",
    "current_academic_year": "Current academic year (BE)",
    "printshop_copies_buffer": "Extra printshop copy buffer percentage",
    "exam_file_retention_mode": "When exam files become eligible for retention review: semester_end, academic_year_end, years, or manual",
    "exam_file_retention_years": "Retention duration in years when retention mode is 'years'",
    "exam_file_destroy_requires_approval": "Whether exam file destruction requires explicit admin approval",
    "exam_file_archive_before_destroy": "Whether exam files must be archived before destruction is allowed",
    "retain_import_audit_logs_years": "How many years import audit logs are retained",
    "retain_import_raw_files": "Whether uploaded raw import files are retained after processing",
    "historical_term_data_retained_indefinitely": "Whether historical term data remains visible indefinitely for audit/reporting",
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


def _get_bool_setting(db: Session, key: str, default: bool) -> bool:
    value = get_setting(db, key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int_setting(db: Session, key: str, default: int | None = None) -> int | None:
    value = get_setting(db, key)
    if value in (None, ""):
        return default
    try:
        return int(value)
    except Exception:
        return default


def _upsert_setting(
    db: Session,
    key: str,
    value: str,
    updated_by: int,
) -> str | None:
    row = db.query(models.SystemSetting).filter(models.SystemSetting.key == key).first()
    old_value = row.value if row else None
    if row:
        row.value = value
        row.updated_by = updated_by
    else:
        db.add(
            models.SystemSetting(
                key=key,
                value=value,
                description=VALID_KEYS.get(key, key),
                updated_by=updated_by,
            )
        )
    return old_value


def _build_retention_policy_payload(db: Session) -> dict:
    retention_mode = get_setting(db, "exam_file_retention_mode") or "manual"
    retention_years = _get_int_setting(db, "exam_file_retention_years")
    destroy_requires_approval = _get_bool_setting(
        db,
        "exam_file_destroy_requires_approval",
        True,
    )
    archive_before_destroy = _get_bool_setting(
        db,
        "exam_file_archive_before_destroy",
        True,
    )
    retain_import_audit_logs_years = _get_int_setting(
        db,
        "retain_import_audit_logs_years",
        7,
    )
    retain_import_raw_files = _get_bool_setting(
        db,
        "retain_import_raw_files",
        True,
    )
    historical_visible = _get_bool_setting(
        db,
        "historical_term_data_retained_indefinitely",
        True,
    )

    if retention_mode == "years" and retention_years:
        retention_summary = f"Exam files are kept for {retention_years} year(s) before retention review."
    elif retention_mode == "semester_end":
        retention_summary = "Exam files are kept until the end of the semester before retention review."
    elif retention_mode == "academic_year_end":
        retention_summary = "Exam files are kept until the end of the academic year before retention review."
    else:
        retention_summary = "Exam files are kept until an admin starts a manual archival or destruction review."

    archive_summary = (
        "Exam files must be archived before any destruction action is allowed."
        if archive_before_destroy
        else "Exam files may be destroyed without a required archive step."
    )
    destruction_summary = (
        "Any destruction action requires explicit admin approval."
        if destroy_requires_approval
        else "Destruction may proceed without a separate approval checkpoint."
    )
    historical_visibility_summary = (
        "Historical term data remains visible for audit and reporting even if source files are later archived or destroyed."
        if historical_visible
        else "Historical term visibility policy is disabled."
    )

    return {
        "exam_file_retention_mode": retention_mode,
        "exam_file_retention_years": retention_years,
        "exam_file_destroy_requires_approval": destroy_requires_approval,
        "exam_file_archive_before_destroy": archive_before_destroy,
        "retain_import_audit_logs_years": retain_import_audit_logs_years,
        "retain_import_raw_files": retain_import_raw_files,
        "parsed_snapshot_storage": "Parsed preview snapshots stay in temporary in-memory cache for 10 minutes only.",
        "historical_term_data_retained_indefinitely": historical_visible,
        "plain_language": {
            "exam_file_retention_summary": retention_summary,
            "archive_summary": archive_summary,
            "destruction_summary": destruction_summary,
            "historical_visibility_summary": historical_visibility_summary,
        },
    }


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


@router.get("/retention-policy", response_model=schemas.ImportRetentionPolicyResponse)
def get_retention_policy(
    db: Session = Depends(get_db),
    _=Depends(require_base_admin),
):
    return _build_retention_policy_payload(db)


@router.put("/retention-policy", response_model=schemas.ImportRetentionPolicyResponse)
def update_retention_policy(
    payload: schemas.ImportRetentionPolicyUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_base_admin),
):
    if payload.exam_file_retention_mode == "years":
        if payload.exam_file_retention_years is None or payload.exam_file_retention_years <= 0:
            raise HTTPException(400, "exam_file_retention_years must be a positive integer when retention mode is 'years'")
    elif payload.exam_file_retention_years is not None:
        raise HTTPException(400, "exam_file_retention_years must be null unless retention mode is 'years'")

    if payload.retain_import_audit_logs_years <= 0:
        raise HTTPException(400, "retain_import_audit_logs_years must be a positive integer")

    if payload.historical_term_data_retained_indefinitely is not True:
        raise HTTPException(
            400,
            "historical_term_data_retained_indefinitely must remain true to preserve historical audit/reporting visibility",
        )

    updates = {
        "exam_file_retention_mode": payload.exam_file_retention_mode,
        "exam_file_retention_years": "" if payload.exam_file_retention_years is None else str(payload.exam_file_retention_years),
        "exam_file_destroy_requires_approval": "true" if payload.exam_file_destroy_requires_approval else "false",
        "exam_file_archive_before_destroy": "true" if payload.exam_file_archive_before_destroy else "false",
        "retain_import_audit_logs_years": str(payload.retain_import_audit_logs_years),
        "retain_import_raw_files": "true" if payload.retain_import_raw_files else "false",
        "historical_term_data_retained_indefinitely": "true",
    }

    old_values: dict[str, str | None] = {}
    for key, value in updates.items():
        old_values[key] = _upsert_setting(db, key, value, current_user.id)

    db.commit()

    log_action(
        db,
        current_user,
        "SETTING_RETENTION_POLICY_UPDATE",
        "system_settings",
        old_values=old_values,
        new_values=updates,
        request=request,
    )

    return _build_retention_policy_payload(db)


@router.get("/term-preview", response_model=schemas.TermSettingsPreviewResponse)
def get_term_preview(
    period_id: int | None = None,
    db: Session = Depends(get_db),
    _=Depends(require_base_admin),
):
    current_active_term = get_active_period(db)
    latest_term = get_latest_term(db)
    latest_historical_term = get_latest_historical_term(db)
    selected_term = resolve_preview_term(db, period_id)
    available_terms = [period_to_dict(period) for period in get_all_periods(db)]

    if not selected_term:
        return {
            "current_active_term": period_to_dict(current_active_term) if current_active_term else None,
            "latest_term": period_to_dict(latest_term) if latest_term else None,
            "latest_historical_term": period_to_dict(latest_historical_term) if latest_historical_term else None,
            "selected_term": None,
            "available_terms": available_terms,
            "default_preview_term_id": None,
            "selected_term_status": None,
            "selected_term_editable": False,
            "selected_term_read_only": False,
            "plain_language_summary": "No academic term is available yet. Create or activate a term to start using term preview.",
            "historical_visibility_summary": "Historical data remains visible for audit and reporting when a term exists.",
        }

    selected_term_data = period_to_dict(selected_term)
    return {
        "current_active_term": period_to_dict(current_active_term) if current_active_term else None,
        "latest_term": period_to_dict(latest_term) if latest_term else None,
        "latest_historical_term": period_to_dict(latest_historical_term) if latest_historical_term else None,
        "selected_term": selected_term_data,
        "available_terms": available_terms,
        "default_preview_term_id": selected_term.id,
        "selected_term_status": get_period_status(selected_term),
        "selected_term_editable": selected_term_data["is_editable"],
        "selected_term_read_only": selected_term_data["is_read_only"],
        "plain_language_summary": selected_term_data["status_summary"],
        "historical_visibility_summary": (
            "Historical data remains visible for audit and reporting even after a term is archived or locked."
        ),
    }
