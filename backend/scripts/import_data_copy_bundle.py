from __future__ import annotations

from pathlib import Path
import sys


SCRIPT_PATH = Path(__file__).resolve()
BACKEND_ROOT = SCRIPT_PATH.parents[1]
PROJECT_ROOT = next((parent for parent in SCRIPT_PATH.parents if (parent / "data_Copy").exists()), SCRIPT_PATH.parents[4])
DATA_COPY_DIR = PROJECT_ROOT / "data_Copy"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from database import SessionLocal  # noqa: E402
from import_v2.importer import execute_import  # noqa: E402
from import_v2.parsers import read_path_by_type  # noqa: E402
from import_v2.validators import (  # noqa: E402
    validate_enrollment_db,
    validate_room_capacity_db,
    validate_rows,
)
import models  # noqa: E402


ACADEMIC_YEAR = "2568"
SEMESTER = "2"
IMPORT_EXAM_TYPE = "final"


def ensure_period(
    db,
    *,
    academic_year: str,
    semester: str,
    exam_type: str,
    created_by: int,
) -> tuple[models.ExamPeriod, bool]:
    period = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.academic_year == academic_year,
        models.ExamPeriod.semester == semester,
        models.ExamPeriod.exam_type == exam_type,
    ).first()
    if period:
        return period, False

    label_prefix = "กลางภาค" if exam_type == "midterm" else "ปลายภาค"
    period = models.ExamPeriod(
        academic_year=academic_year,
        semester=semester,
        exam_type=exam_type,
        label=f"{label_prefix} {semester}/{academic_year}",
        is_active=False,
        lifecycle_status="draft",
        created_by=created_by,
    )
    db.add(period)
    db.flush()
    return period, True


def resolve_operator_id(db) -> int:
    admin_user = db.query(models.User).filter(
        models.User.role == models.UserRole.admin,
        models.User.is_active == True,
    ).order_by(models.User.id.asc()).first()
    if admin_user:
        return admin_user.id

    any_user = db.query(models.User).order_by(models.User.id.asc()).first()
    if any_user:
        return any_user.id

    raise RuntimeError("No user account exists in the backend database to own the import session.")

def prepare_rows(
    db,
    *,
    rows,
    import_type: str,
    academic_year: str,
    semester: str,
    exam_type: str,
) -> list[dict]:
    validated_rows = validate_rows(rows, import_type)
    if import_type == "room_capacity":
        validate_room_capacity_db(validated_rows, db)
    elif import_type == "enrollment":
        validate_enrollment_db(validated_rows, db, academic_year, semester)

    return [
        {
            **row,
            "selected": row.get("status") != "error",
            "override_required": False,
            "override_reason": None,
            "historical_mode": True,
            "import_term_context": {
                "academic_year": academic_year,
                "semester": semester,
                "exam_type": exam_type,
            },
        }
        for row in validated_rows
    ]


def run_bundle_step(
    db,
    *,
    file_name: str,
    import_type: str,
    exam_type: str,
    confirmed_by: int,
    sheet_name: str | None = None,
) -> dict:
    path = DATA_COPY_DIR / file_name
    if not path.exists():
        raise FileNotFoundError(f"Expected data file was not found: {path}")

    rows = read_path_by_type(path, sheet_name=sheet_name)
    prepared_rows = prepare_rows(
        db,
        rows=rows,
        import_type=import_type,
        academic_year=ACADEMIC_YEAR,
        semester=SEMESTER,
        exam_type=exam_type,
    )

    result = execute_import(
        db,
        import_type=import_type,
        academic_year=ACADEMIC_YEAR,
        semester=SEMESTER,
        exam_type=exam_type,
        prepared_rows=prepared_rows,
        confirmed_by=confirmed_by,
        source_filename=file_name,
    )
    db.commit()
    return result


def main() -> int:
    if not DATA_COPY_DIR.exists():
        raise FileNotFoundError(f"data_Copy directory was not found at {DATA_COPY_DIR}")

    db = SessionLocal()
    try:
        operator_id = resolve_operator_id(db)
        active_period = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()
        active_period_id = active_period.id if active_period else None

        for exam_type in ("midterm", "final"):
            period, created = ensure_period(
                db,
                academic_year=ACADEMIC_YEAR,
                semester=SEMESTER,
                exam_type=exam_type,
                created_by=operator_id,
            )
            print(
                f"[period] {exam_type}: id={period.id} "
                f"{'created' if created else 'exists'} active={period.is_active}"
            )
        db.commit()

        steps = [
            {
                "file_name": "Personnel_120226.xlsx",
                "import_type": "personnel",
                "exam_type": IMPORT_EXAM_TYPE,
                "sheet_name": "teacher",
            },
            {
                "file_name": "Employee190226.csv",
                "import_type": "employee",
                "exam_type": IMPORT_EXAM_TYPE,
                "sheet_name": None,
            },
            {
                "file_name": "room_cap.xlsx",
                "import_type": "room_capacity",
                "exam_type": IMPORT_EXAM_TYPE,
                "sheet_name": None,
            },
            {
                "file_name": "opencourse.xls",
                "import_type": "opencourse",
                "exam_type": "midterm",
                "sheet_name": None,
            },
            {
                "file_name": "opencourse.xls",
                "import_type": "opencourse",
                "exam_type": "final",
                "sheet_name": None,
            },
            {
                "file_name": "Book1.xls",
                "import_type": "enrollment",
                "exam_type": "final",
                "sheet_name": None,
            },
        ]

        for step in steps:
            result = run_bundle_step(
                db,
                file_name=step["file_name"],
                import_type=step["import_type"],
                exam_type=step["exam_type"],
                confirmed_by=operator_id,
                sheet_name=step["sheet_name"],
            )
            print(
                f"[import] {step['file_name']} ({step['import_type']}:{step['exam_type']}) "
                f"imported={result['imported_count']} skipped={result['skipped_count']} "
                f"summary={result['summary']['business_writes']}"
            )

        current_active = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()
        current_active_id = current_active.id if current_active else None
        print(
            f"[active-period] preserved={current_active_id == active_period_id} "
            f"before={active_period_id} after={current_active_id}"
        )
        return 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
