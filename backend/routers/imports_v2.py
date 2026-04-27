from collections import Counter
from typing import Literal, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
import schemas as app_schemas
from auth_utils import require_admin, log_action
from database import get_db
from import_v2.file_cache import get_file, store_file
from import_v2.importer import ImportExecutionBlocked, execute_import
from import_v2.parsers import read_file_by_type
from import_v2.validators import (
    SUPPORTED_IMPORT_TYPES,
    validate_enrollment_db,
    validate_room_capacity_db,
    validate_rows,
)
from term_lifecycle import require_period_editable_for_values


router = APIRouter()


class ValidatePreviewRequest(BaseModel):
    file_token: str
    import_type: Literal["opencourse", "personnel", "employee", "enrollment", "room_capacity"]
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    exam_type: Optional[str] = None


class PrepareOverrideItem(BaseModel):
    row: int
    reason: str


class PrepareImportRequest(BaseModel):
    file_token: str
    import_type: Literal["opencourse", "personnel", "employee", "enrollment", "room_capacity"]
    academic_year: str
    semester: str
    exam_type: Optional[str] = None
    selected_rows: list[int] = []
    overrides: list[PrepareOverrideItem] = []


def _build_issue_summary(rows: list[dict], codes_key: str, messages_key: str) -> list[dict]:
    summary_counter: Counter = Counter()
    for row in rows:
        codes = row.get(codes_key, [])
        messages = row.get(messages_key, [])
        for code, message in zip(codes, messages):
            summary_counter[(code, message)] += 1

    summary = [
        {"code": code, "message": message, "count": count}
        for (code, message), count in summary_counter.items()
    ]
    summary.sort(key=lambda item: (-item["count"], item["code"]))
    return summary


def _build_term_context(
    academic_year: Optional[str],
    semester: Optional[str],
    exam_type: Optional[str],
) -> dict:
    return {
        "academic_year": academic_year,
        "semester": semester,
        "exam_type": exam_type,
    }


def _build_session_plan(
    import_type: str,
    academic_year: str,
    semester: str,
    exam_type: Optional[str],
    historical_mode: bool,
    source_filename: Optional[str],
    confirmed_by: int,
    dry_run: bool,
) -> dict:
    return {
        "import_type": import_type,
        "academic_year": academic_year,
        "semester": semester,
        "exam_type": exam_type,
        "historical_mode": historical_mode,
        "source_filename": source_filename,
        "confirmed_by": confirmed_by,
        "dry_run": dry_run,
    }


def _summarize_issue_pairs(issue_pairs: list[tuple[str, str]]) -> list[dict]:
    counter: Counter = Counter(issue_pairs)
    summary = [
        {"code": code, "message": message, "count": count}
        for (code, message), count in counter.items()
    ]
    summary.sort(key=lambda item: (-item["count"], item["code"]))
    return summary


def _enrich_validated_rows(
    validated_rows: list[dict],
    import_type: str,
    db: Session,
    academic_year: Optional[str],
    semester: Optional[str],
) -> list[dict]:
    if import_type == "room_capacity":
        return validate_room_capacity_db(validated_rows, db)

    if import_type == "enrollment" and academic_year and semester:
        return validate_enrollment_db(validated_rows, db, academic_year, semester)

    return validated_rows


def _decorate_rows_for_selection(
    rows: list[dict],
    academic_year: Optional[str],
    semester: Optional[str],
    exam_type: Optional[str],
    historical_mode: bool,
    selected_rows: Optional[set[int]] = None,
    overrides: Optional[dict[int, str]] = None,
) -> list[dict]:
    term_context = _build_term_context(academic_year, semester, exam_type)
    decorated_rows: list[dict] = []

    for row in rows:
        row_number = row.get("_row")
        default_selected = row.get("status") != "error"
        wants_selected = default_selected if selected_rows is None else row_number in selected_rows
        override_reason = overrides.get(row_number) if overrides else None
        has_override = bool(override_reason)
        can_override = row.get("can_override", False)
        override_policy = row.get("override_policy", "allowed")

        if row.get("status") == "error":
            selected = wants_selected and has_override and can_override
            override_required = wants_selected or has_override
        else:
            selected = wants_selected
            override_required = has_override

        decorated_rows.append({
            **row,
            "selected": selected,
            "override_required": override_required,
            "override_reason": override_reason,
            "historical_mode": historical_mode,
            "import_term_context": term_context,
        })

    return decorated_rows


def _build_confirm_plan(
    payload: app_schemas.ImportConfirmRequest,
    cached_file: dict,
    db: Optional[Session] = None,
) -> dict:
    overrides_by_row: dict[int, str] = {}
    for override in payload.overrides:
        reason = override.reason.strip()
        if not reason:
            raise HTTPException(status_code=400, detail="Override reason is required")
        overrides_by_row[override.row] = reason

    validated_rows = validate_rows(cached_file["rows"], payload.import_type)
    if db is not None:
        _enrich_validated_rows(
            validated_rows,
            payload.import_type,
            db,
            payload.academic_year,
            payload.semester,
        )
    selected_rows_set = set(payload.selected_rows)

    for row in validated_rows:
        row_number = row.get("_row")
        if row_number not in overrides_by_row:
            continue

        if row.get("override_policy") == "requires_mapping":
            raise HTTPException(
                status_code=400,
                detail=f"Row {row_number} requires mapping and cannot be overridden",
            )
        if not row.get("can_override", False):
            raise HTTPException(
                status_code=400,
                detail=f"Row {row_number} cannot be overridden safely",
            )

    prepared_rows = _decorate_rows_for_selection(
        validated_rows,
        academic_year=payload.academic_year,
        semester=payload.semester,
        exam_type=payload.exam_type,
        historical_mode=True,
        selected_rows=selected_rows_set,
        overrides=overrides_by_row,
    )

    selected_count = sum(1 for row in prepared_rows if row["selected"])
    override_count = sum(1 for row in prepared_rows if row["override_reason"])
    blocked_count = 0
    importable_count = 0
    blocking_pairs: list[tuple[str, str]] = []

    for row in prepared_rows:
        row_requested = row.get("_row") in selected_rows_set
        if not row_requested:
            continue

        if row.get("override_policy") == "requires_mapping":
            blocked_count += 1
            blocking_pairs.append(("mapping_required", "Selected row requires mapping before import"))
            continue

        if row.get("status") == "error":
            if row.get("can_override") and row.get("override_reason"):
                importable_count += 1
            elif row.get("can_override"):
                blocked_count += 1
                blocking_pairs.append((
                    "override_reason_required",
                    "Override reason required for selected error row",
                ))
            else:
                blocked_count += 1
                for code, message in zip(row.get("error_codes", []), row.get("errors", [])):
                    blocking_pairs.append((code, message))
        else:
            importable_count += 1

    return {
        "prepared_rows": prepared_rows,
        "selected_count": selected_count,
        "override_count": override_count,
        "blocked_count": blocked_count,
        "importable_count": importable_count,
        "non_importable_count": len(prepared_rows) - importable_count,
        "blocking_reasons": _summarize_issue_pairs(blocking_pairs),
        "ready_for_execution": blocked_count == 0 and importable_count > 0,
    }


@router.post("/preview")
async def import_v2_preview(
    file: UploadFile = File(...),
    academic_year: str = Form(...),
    semester: str = Form(...),
    exam_type: str = Form(...),
    _: models.User = Depends(require_admin),
):
    rows = read_file_by_type(file)
    file_token = store_file(rows=rows, filename=file.filename or "upload")

    return {
        "file_token": file_token,
        "file_name": file.filename or "upload",
        "academic_year": academic_year,
        "semester": semester,
        "exam_type": exam_type,
        "total_rows": len(rows),
        "sample_rows": rows[:20],
    }


@router.post("/validate")
async def import_v2_validate(
    payload: ValidatePreviewRequest,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    if payload.import_type not in SUPPORTED_IMPORT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported import_type")

    cached_file = get_file(payload.file_token)
    if not cached_file:
        raise HTTPException(status_code=404, detail="Preview data not found or expired")

    validated_rows = validate_rows(cached_file["rows"], payload.import_type)
    _enrich_validated_rows(
        validated_rows,
        payload.import_type,
        db,
        payload.academic_year,
        payload.semester,
    )
    historical_mode = bool(payload.academic_year and payload.semester)
    response_rows = _decorate_rows_for_selection(
        validated_rows,
        academic_year=payload.academic_year,
        semester=payload.semester,
        exam_type=payload.exam_type,
        historical_mode=historical_mode,
    )

    return {
        "total_rows": len(response_rows),
        "valid_count": sum(1 for row in response_rows if row["status"] == "valid"),
        "warning_count": sum(1 for row in response_rows if row["status"] == "warning"),
        "error_count": sum(1 for row in response_rows if row["status"] == "error"),
        "error_summary": _build_issue_summary(response_rows, "error_codes", "errors"),
        "warning_summary": _build_issue_summary(response_rows, "warning_codes", "warnings"),
        "rows": response_rows[:50],
    }


@router.post("/prepare")
async def import_v2_prepare(
    payload: PrepareImportRequest,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    if payload.import_type not in SUPPORTED_IMPORT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported import_type")

    cached_file = get_file(payload.file_token)
    if not cached_file:
        raise HTTPException(status_code=404, detail="Preview data not found or expired")

    overrides_by_row: dict[int, str] = {}
    for override in payload.overrides:
        reason = override.reason.strip()
        if not reason:
            raise HTTPException(status_code=400, detail="Override reason is required")
        overrides_by_row[override.row] = reason

    validated_rows = validate_rows(cached_file["rows"], payload.import_type)
    _enrich_validated_rows(
        validated_rows,
        payload.import_type,
        db,
        payload.academic_year,
        payload.semester,
    )
    prepared_rows = _decorate_rows_for_selection(
        validated_rows,
        academic_year=payload.academic_year,
        semester=payload.semester,
        exam_type=payload.exam_type,
        historical_mode=True,
        selected_rows=set(payload.selected_rows),
        overrides=overrides_by_row,
    )

    selected_count = sum(1 for row in prepared_rows if row["selected"])
    override_count = sum(1 for row in prepared_rows if row["override_reason"])
    error_blocking_count = sum(
        1 for row in prepared_rows
        if row["status"] == "error" and not row["selected"]
    )

    return {
        "import_type": payload.import_type,
        "academic_year": payload.academic_year,
        "semester": payload.semester,
        "exam_type": payload.exam_type,
        "historical_mode": True,
        "total_rows": len(prepared_rows),
        "selected_count": selected_count,
        "skipped_count": len(prepared_rows) - selected_count,
        "override_count": override_count,
        "error_blocking_count": error_blocking_count,
        "rows_preview": prepared_rows[:50],
    }


@router.post("/confirm-check", response_model=app_schemas.ImportConfirmResponse)
async def import_v2_confirm_check(
    payload: app_schemas.ImportConfirmRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    if payload.import_type not in SUPPORTED_IMPORT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported import_type")
    if payload.confirmed_by != current_user.id:
        raise HTTPException(status_code=400, detail="confirmed_by does not match current user")
    if payload.import_type != "room_capacity":
        require_period_editable_for_values(
            db,
            payload.academic_year,
            payload.semester,
            payload.exam_type,
        )

    cached_file = get_file(payload.file_token)
    if not cached_file:
        raise HTTPException(status_code=404, detail="Preview data not found or expired")

    plan = _build_confirm_plan(payload, cached_file, db=db)

    return {
        "total_rows": len(plan["prepared_rows"]),
        "selected_count": plan["selected_count"],
        "blocked_count": plan["blocked_count"],
        "override_count": plan["override_count"],
        "importable_count": plan["importable_count"],
        "non_importable_count": plan["non_importable_count"],
        "blocking_reasons": plan["blocking_reasons"],
        "ready_for_execution": plan["ready_for_execution"],
        "session_plan": _build_session_plan(
            import_type=payload.import_type,
            academic_year=payload.academic_year,
            semester=payload.semester,
            exam_type=payload.exam_type,
            historical_mode=True,
            source_filename=cached_file.get("filename"),
            confirmed_by=payload.confirmed_by,
            dry_run=payload.dry_run,
        ),
    }


@router.post("/confirm", response_model=app_schemas.ImportExecuteResponse)
async def import_v2_confirm(
    payload: app_schemas.ImportConfirmRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
    request: Request = None,
):
    if payload.import_type not in SUPPORTED_IMPORT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported import_type")
    if payload.confirmed_by != current_user.id:
        raise HTTPException(status_code=400, detail="confirmed_by does not match current user")
    if payload.import_type != "room_capacity" and not payload.exam_type:
        raise HTTPException(status_code=400, detail="exam_type is required for import execution")

    if payload.import_type != "room_capacity":
        require_period_editable_for_values(
            db,
            payload.academic_year,
            payload.semester,
            payload.exam_type,
        )

    cached_file = get_file(payload.file_token)
    if not cached_file:
        raise HTTPException(status_code=404, detail="Preview data not found or expired")

    plan = _build_confirm_plan(payload, cached_file, db=db)
    if not plan["ready_for_execution"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Import batch is not ready for execution.",
                "blocking_reasons": plan["blocking_reasons"],
            },
        )

    try:
        result = execute_import(
            db,
            import_type=payload.import_type,
            academic_year=payload.academic_year,
            semester=payload.semester,
            exam_type=payload.exam_type,
            prepared_rows=plan["prepared_rows"],
            confirmed_by=payload.confirmed_by,
            source_filename=cached_file.get("filename"),
        )
        db.commit()
        try:
            log_action(db, current_user, "IMPORT_CONFIRM_V2", "import_sessions",
                       new_values={"import_type": payload.import_type,
                                   "academic_year": payload.academic_year,
                                   "semester": payload.semester,
                                   "exam_type": payload.exam_type,
                                   "source_filename": cached_file.get("filename"),
                                   "imported_rows": getattr(result, "imported_rows", None),
                                   "dry_run": getattr(payload, "dry_run", False)},
                       request=request)
        except Exception:
            pass
        return result
    except ImportExecutionBlocked as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "message": exc.message,
                "blocking_reasons": exc.blocking_reasons,
            },
        ) from exc
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Import execution failed. No changes were committed.",
        ) from exc
