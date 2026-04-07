"""
migrate_local.py — SQLite schema migration for local dev
=========================================================
Fixes schema drift between the existing ems.db and the current models.py.
Run ONCE before starting the server if you have an existing ems.db.

Usage:
    python migrate_local.py

Safe to re-run (all operations check before altering).
"""
import sqlite3
import sys
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ems.db")


def column_exists(cur: sqlite3.Cursor, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def table_exists(cur: sqlite3.Cursor, table: str) -> bool:
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    )
    return cur.fetchone() is not None


def add_column_if_missing(cur, table, column, col_type, default=None):
    if not column_exists(cur, table, column):
        default_clause = f" DEFAULT {default}" if default is not None else ""
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}{default_clause}")
        print(f"  [+] Added {table}.{column}")
    else:
        print(f"  [ok] {table}.{column} already exists")


def run_migrations():
    if not os.path.exists(DB_PATH):
        print("No ems.db found — will be created fresh on first server start.")
        return

    print(f"Migrating: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys=OFF")
    cur.execute("PRAGMA journal_mode=WAL")

    # ── users ──────────────────────────────────────────────────
    print("\n[users]")
    add_column_if_missing(cur, "users", "special_role", "VARCHAR(30)")

    # ── audit_logs ─────────────────────────────────────────────
    print("\n[audit_logs]")
    add_column_if_missing(cur, "audit_logs", "user_agent_hash", "VARCHAR(64)")
    add_column_if_missing(cur, "audit_logs", "request_id",      "VARCHAR(64)")
    add_column_if_missing(cur, "audit_logs", "duration_ms",     "INTEGER")
    add_column_if_missing(cur, "audit_logs", "http_status",     "INTEGER")

    # ── sections ───────────────────────────────────────────────
    print("\n[sections]")
    add_column_if_missing(cur, "sections", "import_session_id", "INTEGER")

    # ── exam_schedules ─────────────────────────────────────────
    print("\n[exam_schedules]")
    add_column_if_missing(cur, "exam_schedules", "exam_time_start", "VARCHAR(8)")
    add_column_if_missing(cur, "exam_schedules", "exam_time_end",   "VARCHAR(8)")
    # Note: old 'exam_type_label' column is harmless — SQLite keeps it, SQLAlchemy ignores it

    # ── exam_submissions ───────────────────────────────────────
    print("\n[exam_submissions]")
    add_column_if_missing(cur, "exam_submissions", "exam_format_confirmed",    "BOOLEAN", "0")
    add_column_if_missing(cur, "exam_submissions", "exam_format_confirmed_at", "DATETIME")
    add_column_if_missing(cur, "exam_submissions", "print_duplex",             "BOOLEAN", "0")
    add_column_if_missing(cur, "exam_submissions", "print_staple",             "VARCHAR(30)", "'none'")
    add_column_if_missing(cur, "exam_submissions", "print_staple_page",        "INTEGER")
    add_column_if_missing(cur, "exam_submissions", "print_note",               "TEXT")
    add_column_if_missing(cur, "exam_submissions", "print_spec_confirmed",     "BOOLEAN", "0")

    conn.commit()
    conn.close()

    # Verify by re-running the drift check
    print("\nVerifying...")
    conn2 = sqlite3.connect(DB_PATH)
    cur2 = conn2.cursor()

    checks = [
        ("users",           "special_role"),
        ("audit_logs",      "user_agent_hash"),
        ("audit_logs",      "request_id"),
        ("exam_schedules",  "exam_time_start"),
        ("exam_schedules",  "exam_time_end"),
        ("exam_submissions","print_spec_confirmed"),
        ("exam_submissions","exam_format_confirmed"),
        ("sections",        "import_session_id"),
    ]

    all_ok = True
    for table, col in checks:
        ok = column_exists(cur2, table, col)
        status = "[OK]" if ok else "[FAIL]"
        print(f"  {status} {table}.{col}")
        if not ok:
            all_ok = False

    conn2.close()

    if all_ok:
        print("\n[DONE] Migration complete - ready to run!")
    else:
        print("\n[FAIL] Some columns still missing - check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    run_migrations()
