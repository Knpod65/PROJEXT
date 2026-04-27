from __future__ import annotations

from pathlib import Path
import sys

from database import SessionLocal
from historical_schedule_import import import_historical_schedule_snapshot
import models


def _find_single(pattern: str) -> Path:
    matches = sorted(Path.home().joinpath("Desktop").glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No file found for pattern: {pattern}")
    return matches[0]


def main() -> None:
    final_path = _find_single("3.*ตารางสอบปลายภาค*.pdf")
    baseline_path = _find_single("countworkloadonthis_*.pdf")

    db = SessionLocal()
    try:
        final_batch = import_historical_schedule_snapshot(
            db,
            pdf_path=final_path,
            version_kind=models.HistoricalScheduleVersion.final_adjusted,
            source_label="final_adjusted_result",
            semester="2",
            academic_year="2568",
            exam_type="final",
        )
        baseline_batch = import_historical_schedule_snapshot(
            db,
            pdf_path=baseline_path,
            version_kind=models.HistoricalScheduleVersion.optimized_baseline,
            source_label="optimized_original_result",
            semester="2",
            academic_year="2568",
            exam_type="final",
        )
        db.commit()
        print("Imported final_adjusted_result:", final_batch.id, final_batch.source_filename, final_batch.row_count, final_batch.manual_review_count)
        print("Imported optimized_original_result:", baseline_batch.id, baseline_batch.source_filename, baseline_batch.row_count, baseline_batch.manual_review_count)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"IMPORT FAILED: {exc}", file=sys.stderr)
        raise
