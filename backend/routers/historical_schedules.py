from __future__ import annotations

import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from auth_utils import get_current_user, log_action, require_admin
from database import get_db
from historical_schedule_import import (
    build_difference_rows,
    build_distribution_rows,
    build_schedule_rows,
    build_workload_rows,
    build_workload_summary,
    get_latest_batch,
    get_room_opening_candidates,
    get_room_opening_start_username,
    serialize_batch_summary,
    set_room_opening_start_username,
)
import models


router = APIRouter()


def _parse_version_kind(value: str) -> models.HistoricalScheduleVersion:
    try:
        return models.HistoricalScheduleVersion(value)
    except ValueError as exc:
        raise HTTPException(400, f"Unknown version_kind: {value}") from exc


def _latest_required(
    db: Session,
    version_kind: models.HistoricalScheduleVersion,
    semester: str,
    academic_year: str,
    exam_type: str,
) -> models.HistoricalScheduleBatch:
    batch = get_latest_batch(db, version_kind, semester=semester, academic_year=academic_year, exam_type=exam_type)
    if not batch:
        raise HTTPException(404, f"No historical schedule batch found for {version_kind.value}")
    return db.query(models.HistoricalScheduleBatch).options(
        joinedload(models.HistoricalScheduleBatch.entries).joinedload(models.HistoricalScheduleEntry.invigilators),
        joinedload(models.HistoricalScheduleBatch.distribution_slots),
    ).filter(models.HistoricalScheduleBatch.id == batch.id).first()


@router.get("/overview")
def get_historical_schedule_overview(
    semester: str = "2",
    academic_year: str = "2568",
    exam_type: str = "final",
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    final_batch = get_latest_batch(db, models.HistoricalScheduleVersion.final_adjusted, semester=semester, academic_year=academic_year, exam_type=exam_type)
    baseline_batch = get_latest_batch(db, models.HistoricalScheduleVersion.optimized_baseline, semester=semester, academic_year=academic_year, exam_type=exam_type)
    comparison_count = 0
    if final_batch and baseline_batch:
        final_loaded = _latest_required(db, models.HistoricalScheduleVersion.final_adjusted, semester, academic_year, exam_type)
        baseline_loaded = _latest_required(db, models.HistoricalScheduleVersion.optimized_baseline, semester, academic_year, exam_type)
        comparison_count = len(build_difference_rows(baseline_loaded, final_loaded))
    return {
        "term": {
            "semester": semester,
            "academic_year": academic_year,
            "exam_type": exam_type,
        },
        "room_opening_start_username": get_room_opening_start_username(db),
        "room_opening_candidates": [
            {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
            }
            for user in get_room_opening_candidates(db)
        ],
        "final_adjusted_batch": serialize_batch_summary(final_batch),
        "optimized_baseline_batch": serialize_batch_summary(baseline_batch),
        "comparison_count": comparison_count,
    }


@router.get("/rows")
def get_historical_schedule_rows(
    version_kind: str,
    semester: str = "2",
    academic_year: str = "2568",
    exam_type: str = "final",
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    batch = _latest_required(db, _parse_version_kind(version_kind), semester, academic_year, exam_type)
    return {
        "batch": serialize_batch_summary(batch),
        "rows": build_schedule_rows(batch),
    }


@router.get("/distribution")
def get_historical_distribution_rows(
    version_kind: str,
    semester: str = "2",
    academic_year: str = "2568",
    exam_type: str = "final",
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    batch = _latest_required(db, _parse_version_kind(version_kind), semester, academic_year, exam_type)
    return {
        "batch": serialize_batch_summary(batch),
        "rows": build_distribution_rows(batch),
    }


@router.get("/workload")
def get_historical_workload_rows(
    version_kind: str,
    semester: str = "2",
    academic_year: str = "2568",
    exam_type: str = "final",
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    batch = _latest_required(db, _parse_version_kind(version_kind), semester, academic_year, exam_type)
    return {
        "batch": serialize_batch_summary(batch),
        "summary": build_workload_summary(batch),
        "rows": build_workload_rows(batch),
    }


@router.get("/comparison")
def get_historical_comparison(
    semester: str = "2",
    academic_year: str = "2568",
    exam_type: str = "final",
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    baseline_batch = _latest_required(db, models.HistoricalScheduleVersion.optimized_baseline, semester, academic_year, exam_type)
    final_batch = _latest_required(db, models.HistoricalScheduleVersion.final_adjusted, semester, academic_year, exam_type)
    rows = build_difference_rows(baseline_batch, final_batch)
    return {
        "baseline_batch": serialize_batch_summary(baseline_batch),
        "final_batch": serialize_batch_summary(final_batch),
        "count": len(rows),
        "rows": rows,
    }

@router.put("/room-opening-start")
def update_room_opening_start(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    username = str(payload.get("username") or "").strip()
    if not username:
        raise HTTPException(400, "username is required")
    try:
        saved = set_room_opening_start_username(db, username, actor_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    db.commit()
    log_action(
        db,
        current_user,
        "UPDATE_ROOM_OPENING_START",
        "system_settings",
        new_values={"username": saved},
        request=request,
    )
    return {"username": saved}


def _csv_response(filename: str, header: list[str], rows: list[list[object]]) -> StreamingResponse:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    byte_buffer = io.BytesIO(buffer.getvalue().encode("utf-8-sig"))
    return StreamingResponse(
        byte_buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/comparison-csv")
def export_historical_comparison_csv(
    semester: str = "2",
    academic_year: str = "2568",
    exam_type: str = "final",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
    request: Request = None,
):
    baseline_batch = _latest_required(db, models.HistoricalScheduleVersion.optimized_baseline, semester, academic_year, exam_type)
    final_batch = _latest_required(db, models.HistoricalScheduleVersion.final_adjusted, semester, academic_year, exam_type)
    rows = build_difference_rows(baseline_batch, final_batch)
    csv_rows = []
    for row in rows:
        csv_rows.append(
            [
                row["course_code"],
                row["section_no"],
                row["exam_date"],
                row["exam_time"],
                row["status"],
                ", ".join(row["changes"]),
                (row["baseline"] or {}).get("room_name"),
                (row["final"] or {}).get("room_name"),
                (row["baseline"] or {}).get("invigilators_raw"),
                (row["final"] or {}).get("invigilators_raw"),
                (row["baseline"] or {}).get("paper_distribution_staff_name"),
                (row["final"] or {}).get("paper_distribution_staff_name"),
                (row["baseline"] or {}).get("room_opening_staff_name"),
                (row["final"] or {}).get("room_opening_staff_name"),
            ]
        )
    try:
        log_action(db, current_user, "export_historical_comparison_csv",
                   table_name="historical_schedule_batches",
                   new_values={"file_type": "csv", "export_scope": "historical_snapshot",
                               "row_count": len(csv_rows),
                               "semester": semester,
                               "academic_year": academic_year,
                               "exam_type": exam_type},
                   http_status=200, request=request)
    except Exception:
        pass
    return _csv_response(
        f"historical_schedule_comparison_{semester}_{academic_year}_{exam_type}.csv",
        [
            "course_code",
            "section_no",
            "exam_date",
            "exam_time",
            "status",
            "changes",
            "baseline_room",
            "final_room",
            "baseline_invigilators",
            "final_invigilators",
            "baseline_paper_distribution",
            "final_paper_distribution",
            "baseline_room_opening",
            "final_room_opening",
        ],
        csv_rows,
    )


@router.get("/export/workload-csv")
def export_historical_workload_csv(
    version_kind: str,
    semester: str = "2",
    academic_year: str = "2568",
    exam_type: str = "final",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
    request: Request = None,
):
    batch = _latest_required(db, _parse_version_kind(version_kind), semester, academic_year, exam_type)
    rows = build_workload_rows(batch)
    csv_rows = [
        [
            row["person_name"],
            row["duty_type"],
            row["date"],
            row["time_slot"],
            "; ".join(row["courses_covered"]),
            "; ".join(row["rooms"]),
            row["workload_count"],
            row["counted_or_not_counted"],
            row["source_file"],
            row["version_kind"],
        ]
        for row in rows
    ]
    try:
        log_action(db, current_user, "export_historical_workload_csv",
                   table_name="historical_schedule_batches",
                   new_values={"file_type": "csv", "export_scope": "historical_snapshot",
                               "row_count": len(csv_rows),
                               "version_kind": version_kind,
                               "semester": semester,
                               "academic_year": academic_year,
                               "exam_type": exam_type},
                   http_status=200, request=request)
    except Exception:
        pass
    return _csv_response(
        f"historical_schedule_workload_{version_kind}_{semester}_{academic_year}_{exam_type}.csv",
        [
            "person_name",
            "duty_type",
            "date",
            "time_slot",
            "courses_covered",
            "rooms",
            "workload_count",
            "counted_or_not_counted",
            "source_file",
            "version_kind",
        ],
        csv_rows,
    )
