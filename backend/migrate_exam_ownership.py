from __future__ import annotations

import sqlite3
from pathlib import Path


BACKEND_DB = Path(__file__).resolve().parent / "ems.db"


def has_column(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    rows = cursor.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


def main() -> None:
    if not BACKEND_DB.exists():
        raise SystemExit(f"Database not found: {BACKEND_DB}")

    conn = sqlite3.connect(BACKEND_DB)
    try:
        cursor = conn.cursor()
        if not has_column(cursor, "section_exam_managers", "assignment_source"):
            cursor.execute(
                "ALTER TABLE section_exam_managers "
                "ADD COLUMN assignment_source TEXT NOT NULL DEFAULT 'manual'"
            )
            print("[migration] added section_exam_managers.assignment_source")
        else:
            print("[migration] section_exam_managers.assignment_source already exists")

        updated = cursor.execute(
            "UPDATE section_exam_managers "
            "SET assignment_source = 'manual' "
            "WHERE assignment_source IS NULL OR TRIM(assignment_source) = ''"
        ).rowcount
        conn.commit()
        print(f"[migration] normalized assignment_source rows={updated}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
