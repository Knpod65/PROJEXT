from __future__ import annotations

from pathlib import Path
import sqlite3


def main() -> int:
    db_path = Path(__file__).resolve().parent / "ems.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()
        columns = {
            row["name"]
            for row in cursor.execute("PRAGMA table_info(sections)").fetchall()
        }

        if "teaching_room_id" not in columns:
            cursor.execute("ALTER TABLE sections ADD COLUMN teaching_room_id INTEGER REFERENCES rooms(id)")
            print("[migration] added sections.teaching_room_id")
        else:
            print("[migration] sections.teaching_room_id already exists")

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS ix_sections_teaching_room_id ON sections(teaching_room_id)"
        )

        imported_default_count = cursor.execute(
            """
            SELECT COUNT(*)
            FROM exam_schedules
            WHERE room_id IS NOT NULL
              AND COALESCE(num_pages, 0) = 0
              AND status = 'draft'
            """
        ).fetchone()[0]

        cursor.execute(
            """
            WITH imported_defaults AS (
              SELECT section_id, MIN(room_id) AS room_id
              FROM exam_schedules
              WHERE room_id IS NOT NULL
                AND COALESCE(num_pages, 0) = 0
                AND status = 'draft'
              GROUP BY section_id
            )
            UPDATE sections
            SET teaching_room_id = (
              SELECT imported_defaults.room_id
              FROM imported_defaults
              WHERE imported_defaults.section_id = sections.id
            )
            WHERE id IN (SELECT section_id FROM imported_defaults)
              AND teaching_room_id IS NULL
            """
        )
        backfilled_sections = cursor.rowcount if cursor.rowcount != -1 else None

        cursor.execute(
            """
            UPDATE exam_schedules
            SET room_id = NULL
            WHERE room_id IS NOT NULL
              AND COALESCE(num_pages, 0) = 0
              AND status = 'draft'
            """
        )
        cleared_schedules = cursor.rowcount if cursor.rowcount != -1 else imported_default_count

        conn.commit()
        print(
            f"[migration] imported-default schedules checked={imported_default_count} "
            f"sections_backfilled={backfilled_sections if backfilled_sections is not None else 'unknown'} "
            f"schedules_cleared={cleared_schedules if cleared_schedules is not None else imported_default_count}"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
