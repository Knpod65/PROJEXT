"""
Import Data V2 schema migration.

Run directly:
    python migrate_v2_import.py

This migration is intentionally small and idempotent:
- add sections.is_thesis
- create import_row_logs
- create lecturer_name_map
- ensure the required indexes exist
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


def index_exists(inspector, table_name: str, index_name: str) -> bool:
    if not table_exists(inspector, table_name):
        return False
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def run() -> None:
    print("=" * 60)
    print("Import Data V2 migration starting")
    print("=" * 60)

    with engine.begin() as conn:
        inspector = inspect(conn)

        if not column_exists(inspector, "sections", "is_thesis"):
            conn.execute(text(
                "ALTER TABLE sections ADD COLUMN is_thesis BOOLEAN DEFAULT FALSE"
            ))
            print("  + sections.is_thesis added")
        else:
            print("  = sections.is_thesis already exists")

        if not table_exists(inspector, "import_row_logs"):
            models.ImportRowLog.__table__.create(bind=conn, checkfirst=True)
            print("  + import_row_logs created")
            inspector = inspect(conn)
        else:
            print("  = import_row_logs already exists")

        if not index_exists(inspector, "import_row_logs", "idx_import_row_logs_session"):
            conn.execute(text(
                "CREATE INDEX idx_import_row_logs_session ON import_row_logs(session_id)"
            ))
            print("  + idx_import_row_logs_session created")
        else:
            print("  = idx_import_row_logs_session already exists")

        if not table_exists(inspector, "lecturer_name_map"):
            models.LecturerNameMap.__table__.create(bind=conn, checkfirst=True)
            print("  + lecturer_name_map created")
            inspector = inspect(conn)
        else:
            print("  = lecturer_name_map already exists")

        if not index_exists(inspector, "lecturer_name_map", "idx_lecturer_name_map_raw_name"):
            conn.execute(text(
                "CREATE UNIQUE INDEX idx_lecturer_name_map_raw_name "
                "ON lecturer_name_map(raw_name)"
            ))
            print("  + lecturer_name_map raw_name unique index created")
        else:
            print("  = lecturer_name_map raw_name unique index already exists")

    print("\nImport Data V2 migration completed")


if __name__ == "__main__":
    run()
