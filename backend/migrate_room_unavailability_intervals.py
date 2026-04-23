from __future__ import annotations

import sqlite3
from pathlib import Path

from time_ranges import parse_time_range


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

        if not has_column(cursor, "room_unavailability", "start_time"):
            cursor.execute(
                "ALTER TABLE room_unavailability ADD COLUMN start_time TEXT NULL"
            )
            print("[migration] added room_unavailability.start_time")
        else:
            print("[migration] room_unavailability.start_time already exists")

        if not has_column(cursor, "room_unavailability", "end_time"):
            cursor.execute(
                "ALTER TABLE room_unavailability ADD COLUMN end_time TEXT NULL"
            )
            print("[migration] added room_unavailability.end_time")
        else:
            print("[migration] room_unavailability.end_time already exists")

        updated = 0
        rows = cursor.execute(
            """
            SELECT id, block_time
            FROM room_unavailability
            WHERE block_time IS NOT NULL
              AND (start_time IS NULL OR end_time IS NULL)
            """
        ).fetchall()
        for row_id, block_time in rows:
            parsed = parse_time_range(block_time)
            if not parsed:
                continue
            cursor.execute(
                """
                UPDATE room_unavailability
                SET start_time = ?, end_time = ?
                WHERE id = ?
                """,
                (parsed[0], parsed[1], row_id),
            )
            updated += 1

        conn.commit()
        print(f"[migration] room_unavailability intervals backfilled rows={updated}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
