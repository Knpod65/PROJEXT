from __future__ import annotations

import sqlite3
from pathlib import Path


BACKEND_DB = Path(__file__).resolve().parent / "ems.db"


def main() -> None:
    if not BACKEND_DB.exists():
        raise SystemExit(f"Database not found: {BACKEND_DB}")

    conn = sqlite3.connect(BACKEND_DB)
    try:
        cursor = conn.cursor()
        dept_code_updates = cursor.execute(
            "UPDATE users SET dept_code = 'IA' WHERE dept_code = 'IR'"
        ).rowcount
        department_updates = cursor.execute(
            "UPDATE users SET department = 'IA' WHERE department = 'IR'"
        ).rowcount
        conn.commit()
        print(f"[migration] users.dept_code IR->IA rows={dept_code_updates}")
        print(f"[migration] users.department IR->IA rows={department_updates}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
