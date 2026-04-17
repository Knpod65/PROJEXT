"""
migrate.py — Alembic-free migration script
รันตรงได้เลย: python migrate.py
ใช้สำหรับ DB ที่มีอยู่แล้ว (ไม่ต้อง drop-recreate)
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text, inspect
from database import engine, Base
import models  # noqa: F401 — register all models

def column_exists(conn, table, column):
    result = conn.execute(text(
        f"SELECT 1 FROM information_schema.columns "
        f"WHERE table_name='{table}' AND column_name='{column}'"
    ))
    return result.fetchone() is not None

def constraint_exists(conn, table, constraint):
    result = conn.execute(text(
        f"SELECT 1 FROM information_schema.table_constraints "
        f"WHERE table_name='{table}' AND constraint_name='{constraint}'"
    ))
    return result.fetchone() is not None

def index_exists(conn, index_name):
    result = conn.execute(text(
        f"SELECT 1 FROM pg_indexes WHERE indexname='{index_name}'"
    ))
    return result.fetchone() is not None

def run():
    print("🔧 EMS Migration Script")
    Base.metadata.create_all(bind=engine)  # สร้างตารางใหม่ที่ยังไม่มี
    print("  ✅ New tables created (if any)")

    with engine.begin() as conn:

        # ── 1. Section: เพิ่ม import_session_id ──────────────────
        if not column_exists(conn, 'sections', 'import_session_id'):
            conn.execute(text(
                "ALTER TABLE sections "
                "ADD COLUMN import_session_id INTEGER "
                "REFERENCES import_sessions(id) ON DELETE SET NULL"
            ))
            print("  ✅ sections.import_session_id added")
        else:
            # ตรวจ FK จริงๆ
            fk = conn.execute(text(
                "SELECT 1 FROM information_schema.referential_constraints rc "
                "JOIN information_schema.key_column_usage kcu "
                "ON rc.constraint_name = kcu.constraint_name "
                "WHERE kcu.table_name='sections' AND kcu.column_name='import_session_id'"
            )).fetchone()
            if not fk:
                conn.execute(text(
                    "ALTER TABLE sections "
                    "ADD CONSTRAINT fk_sections_import_session "
                    "FOREIGN KEY (import_session_id) REFERENCES import_sessions(id)"
                ))
                print("  ✅ sections.import_session_id FK added")
            else:
                print("  ⏭  sections.import_session_id already OK")

        # ── 2. ExamSchedule: drop unique(section_id) ─────────────
        # เช็คว่ามี unique constraint เฉพาะ section_id อยู่ไหม
        old_uniq = conn.execute(text(
            "SELECT tc.constraint_name "
            "FROM information_schema.table_constraints tc "
            "JOIN information_schema.key_column_usage kcu "
            "ON tc.constraint_name = kcu.constraint_name "
            "WHERE tc.table_name='exam_schedules' "
            "AND tc.constraint_type='UNIQUE' "
            "AND kcu.column_name='section_id' "
            "AND tc.constraint_name != 'uq_schedule_section_examtype'"
        )).fetchall()
        for row in old_uniq:
            conn.execute(text(
                f"ALTER TABLE exam_schedules DROP CONSTRAINT \"{row[0]}\""
            ))
            print(f"  ✅ Dropped old unique constraint: {row[0]}")

        # ── 3. ExamSchedule: เพิ่ม uq(section_id, exam_type) ────
        if not constraint_exists(conn, 'exam_schedules', 'uq_schedule_section_examtype'):
            conn.execute(text(
                "ALTER TABLE exam_schedules "
                "ADD CONSTRAINT uq_schedule_section_examtype "
                "UNIQUE (section_id, exam_type)"
            ))
            print("  ✅ uq_schedule_section_examtype added")
        else:
            print("  ⏭  uq_schedule_section_examtype already exists")

        # ── 4. ExamSchedule: เพิ่ม indexes ───────────────────────
        for idx_name, idx_sql in [
            ("ix_schedule_date",    "CREATE INDEX IF NOT EXISTS ix_schedule_date ON exam_schedules(exam_date)"),
            ("ix_schedule_section", "CREATE INDEX IF NOT EXISTS ix_schedule_section ON exam_schedules(section_id)"),
        ]:
            conn.execute(text(idx_sql))
        print("  ✅ ExamSchedule indexes ensured")

        # ── 5. Supervision: ลบ duplicate role_in_exam (ถ้าเกิด) ──
        # PostgreSQL ไม่ให้มี duplicate column จริงๆ แต่ตรวจ logic ไว้
        sup_cols = conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='supervisions' ORDER BY ordinal_position"
        )).fetchall()
        sup_col_names = [r[0] for r in sup_cols]
        print(f"  ℹ  Supervision columns: {sup_col_names}")

        # ── 6. users: เพิ่ม dept_code ถ้ายังไม่มี ────────────────
        if not column_exists(conn, 'users', 'dept_code'):
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN dept_code VARCHAR(10)"
            ))
            print("  ✅ users.dept_code added")
        else:
            print("  ⏭  users.dept_code already exists")

        # ── 7. users: เพิ่ม dept_supervisor role (Enum) ──────────
        try:
            conn.execute(text(
                "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'dept_supervisor'"
            ))
            print("  ✅ userrole enum: dept_supervisor added")
        except Exception as e:
            print(f"  ⏭  userrole enum: {e}")

        try:
            conn.execute(text(
                "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'print_shop'"
            ))
            print("  ✅ userrole enum: print_shop added")
        except Exception as e:
            print(f"  ⏭  userrole enum (print_shop): {e}")

        # ── 8. Course: เพิ่ม index ix_course_course_id ───────────
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_course_course_id ON courses(course_id)"
        ))
        print("  ✅ ix_course_course_id ensured")

        # ── 9. EnrollmentRecord: ตรวจ index ──────────────────────
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_enroll_session_section "
            "ON enrollment_records(import_session_id, section_id)"
        ))
        print("  ✅ ix_enroll_session_section ensured")

    print("\n✅ Migration completed successfully")

if __name__ == "__main__":
    run()
