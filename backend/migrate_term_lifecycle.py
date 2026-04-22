"""
Term lifecycle schema migration.

Run directly:
    python migrate_term_lifecycle.py

This migration is intentionally small and idempotent:
- add exam_periods.lifecycle_status
- add exam_periods.archived_at
- add exam_periods.locked_at
- backfill lifecycle_status for existing rows
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import inspect, text

from database import engine
import models  # noqa: F401 - register models


def table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def column_exists(inspector, table_name: str, column_name: str) -> bool:
    if not table_exists(inspector, table_name):
        return False
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def run() -> None:
    print("=" * 60)
    print("Term lifecycle migration starting")
    print("=" * 60)

    with engine.begin() as conn:
        inspector = inspect(conn)

        if not column_exists(inspector, "exam_periods", "lifecycle_status"):
            conn.execute(text(
                "ALTER TABLE exam_periods "
                "ADD COLUMN lifecycle_status VARCHAR(20) DEFAULT 'draft'"
            ))
            print("  + exam_periods.lifecycle_status added")
            inspector = inspect(conn)
        else:
            print("  = exam_periods.lifecycle_status already exists")

        if not column_exists(inspector, "exam_periods", "archived_at"):
            conn.execute(text(
                "ALTER TABLE exam_periods ADD COLUMN archived_at TIMESTAMP NULL"
            ))
            print("  + exam_periods.archived_at added")
            inspector = inspect(conn)
        else:
            print("  = exam_periods.archived_at already exists")

        if not column_exists(inspector, "exam_periods", "locked_at"):
            conn.execute(text(
                "ALTER TABLE exam_periods ADD COLUMN locked_at TIMESTAMP NULL"
            ))
            print("  + exam_periods.locked_at added")
        else:
            print("  = exam_periods.locked_at already exists")

        conn.execute(text(
            "UPDATE exam_periods "
            "SET lifecycle_status = 'active' "
            "WHERE is_active = TRUE"
        ))
        conn.execute(text(
            "UPDATE exam_periods "
            "SET lifecycle_status = 'archived' "
            "WHERE COALESCE(is_active, FALSE) = FALSE "
            "AND (lifecycle_status IS NULL OR lifecycle_status = 'draft')"
        ))
        print("  + lifecycle_status backfilled for existing periods")

    print("\nTerm lifecycle migration completed")


if __name__ == "__main__":
    run()
