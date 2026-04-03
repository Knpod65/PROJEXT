"""
migrate_v2.py — Full migration script
คณะรัฐศาสตร์และรัฐประศาสนศาสตร์ มหาวิทยาลัยเชียงใหม่

รัน: python migrate_v2.py
รองรับ PostgreSQL — idempotent (รันซ้ำได้ปลอดภัย)

Changes จาก schema เดิม:
  [users]
    + division, unit, dept_code, title, mobile, ext, employee_id

  [sections]
    + import_session_id  FK → import_sessions(id)

  [exam_schedules]
    - UNIQUE(section_id)          ← ลบทิ้ง (1 section มี midterm+final ได้)
    + UNIQUE(section_id, exam_type)
    + INDEX ix_schedule_date
    + INDEX ix_schedule_section

  [supervisions]
    - role_in_exam column ซ้ำ     ← ตรวจสอบ (PG ไม่มีปัญหา duplicate col)

  [exam_submissions]
    + print_duplex
    + print_staple
    + print_staple_page
    + print_note
    + print_spec_confirmed

  [courses]
    + INDEX ix_course_course_id

  NEW TABLES (สร้างถ้ายังไม่มี):
    import_sessions
    enrollment_records
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text, inspect as sa_inspect
from database import engine
import models


# ── helpers ───────────────────────────────────────────────────
def col_exists(conn, table: str, column: str) -> bool:
    r = conn.execute(text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name=:t AND column_name=:c"
    ), {"t": table, "c": column})
    return r.fetchone() is not None


def constraint_exists(conn, table: str, constraint: str) -> bool:
    r = conn.execute(text(
        "SELECT 1 FROM information_schema.table_constraints "
        "WHERE table_name=:t AND constraint_name=:c"
    ), {"t": table, "c": constraint})
    return r.fetchone() is not None


def index_exists(conn, index: str) -> bool:
    r = conn.execute(text(
        "SELECT 1 FROM pg_indexes WHERE indexname=:i"
    ), {"i": index})
    return r.fetchone() is not None


def safe_exec(conn, sql: str, ok_msg: str, skip_msg: str = None, params: dict = None):
    try:
        conn.execute(text(sql), params or {})
        conn.commit()
        print(f"  ✅ {ok_msg}")
    except Exception as e:
        conn.rollback()
        msg = str(e).lower()
        if any(k in msg for k in ["already exists", "duplicate", "does not exist", "no such"]):
            print(f"  ⏭  {skip_msg or ok_msg} (already done)")
        else:
            print(f"  ⚠  {ok_msg}: {e}")


def add_column(conn, table: str, column: str, definition: str):
    if col_exists(conn, table, column):
        print(f"  ⏭  {table}.{column} already exists")
        return
    safe_exec(
        conn,
        f"ALTER TABLE {table} ADD COLUMN {column} {definition}",
        f"{table}.{column} added",
    )


# ── main ──────────────────────────────────────────────────────
def run():
    print("=" * 60)
    print("EMS Migration v2 — starting")
    print("=" * 60)

    with engine.connect() as conn:

        # ════════════════════════════════════════════════════
        # STEP 0: สร้าง tables ใหม่ทั้งหมดที่ยังไม่มี
        # ════════════════════════════════════════════════════
        print("\n[0] Create new tables (if not exist)")
        models.Base.metadata.create_all(bind=engine)
        print("  ✅ All tables verified / created")

        # ════════════════════════════════════════════════════
        # STEP 1: users — เพิ่ม columns ที่ขาด
        # ════════════════════════════════════════════════════
        print("\n[1] users — add new columns")
        user_cols = [
            ("division",    "VARCHAR(100)"),
            ("unit",        "VARCHAR(100)"),
            ("dept_code",   "VARCHAR(10)"),
            ("title",       "VARCHAR(50)"),
            ("mobile",      "VARCHAR(30)"),
            ("ext",         "VARCHAR(20)"),
            ("employee_id", "INTEGER"),
            ("updated_at",  "TIMESTAMPTZ"),
        ]
        for col, defn in user_cols:
            add_column(conn, "users", col, defn)

        # ════════════════════════════════════════════════════
        # STEP 2: sections — เพิ่ม import_session_id
        # ════════════════════════════════════════════════════
        print("\n[2] sections — add import_session_id")
        if not col_exists(conn, "sections", "import_session_id"):
            safe_exec(
                conn,
                "ALTER TABLE sections ADD COLUMN import_session_id INTEGER "
                "REFERENCES import_sessions(id) ON DELETE SET NULL",
                "sections.import_session_id added with FK",
            )
        else:
            # ตรวจว่า FK มีหรือยัง — ถ้าไม่มีให้เพิ่ม
            fk = conn.execute(text(
                "SELECT 1 FROM information_schema.referential_constraints rc "
                "JOIN information_schema.key_column_usage kcu "
                "  ON rc.constraint_name = kcu.constraint_name "
                "WHERE kcu.table_name='sections' AND kcu.column_name='import_session_id'"
            )).fetchone()
            if not fk:
                safe_exec(
                    conn,
                    "ALTER TABLE sections ADD CONSTRAINT fk_sections_import_session "
                    "FOREIGN KEY (import_session_id) REFERENCES import_sessions(id) ON DELETE SET NULL",
                    "sections.import_session_id FK added",
                )
            else:
                print("  ⏭  sections.import_session_id already exists with FK")

        # ════════════════════════════════════════════════════
        # STEP 3: exam_schedules — fix unique constraint
        # ════════════════════════════════════════════════════
        print("\n[3] exam_schedules — fix unique constraint")

        # ลบ constraint เดิมที่ unique เฉพาะ section_id
        old_constraints = [
            "exam_schedules_section_id_key",  # default PG name
            "uq_exam_schedule_section",
        ]
        for c in old_constraints:
            if constraint_exists(conn, "exam_schedules", c):
                safe_exec(
                    conn,
                    f"ALTER TABLE exam_schedules DROP CONSTRAINT {c}",
                    f"dropped old constraint {c}",
                )

        # เพิ่ม constraint ใหม่ (section_id, exam_type)
        if not constraint_exists(conn, "exam_schedules", "uq_schedule_section_examtype"):
            safe_exec(
                conn,
                "ALTER TABLE exam_schedules ADD CONSTRAINT uq_schedule_section_examtype "
                "UNIQUE (section_id, exam_type)",
                "uq_schedule_section_examtype added",
            )
        else:
            print("  ⏭  uq_schedule_section_examtype already exists")

        # ════════════════════════════════════════════════════
        # STEP 4: exam_submissions — print spec columns
        # ════════════════════════════════════════════════════
        print("\n[4] exam_submissions — add print spec columns")
        sub_cols = [
            ("print_duplex",          "BOOLEAN DEFAULT FALSE"),
            ("print_staple",          "VARCHAR(30)"),
            ("print_staple_page",     "INTEGER"),
            ("print_note",            "TEXT"),
            ("print_spec_confirmed",  "BOOLEAN DEFAULT FALSE"),
        ]
        for col, defn in sub_cols:
            add_column(conn, "exam_submissions", col, defn)

        # ════════════════════════════════════════════════════
        # STEP 5: indexes
        # ════════════════════════════════════════════════════
        print("\n[5] Create indexes")
        indexes = [
            ("ix_schedule_date",      "CREATE INDEX IF NOT EXISTS ix_schedule_date ON exam_schedules(exam_date)"),
            ("ix_schedule_section",   "CREATE INDEX IF NOT EXISTS ix_schedule_section ON exam_schedules(section_id)"),
            ("ix_course_course_id",   "CREATE INDEX IF NOT EXISTS ix_course_course_id ON courses(course_id)"),
            ("ix_enroll_student",     "CREATE INDEX IF NOT EXISTS ix_enroll_student ON enrollment_records(student_id)"),
            ("ix_enroll_session_sec", "CREATE INDEX IF NOT EXISTS ix_enroll_session_sec ON enrollment_records(import_session_id, section_id)"),
            ("ix_audit_timestamp",    "CREATE INDEX IF NOT EXISTS ix_audit_timestamp ON audit_logs(timestamp)"),
            ("ix_audit_actor",        "CREATE INDEX IF NOT EXISTS ix_audit_actor ON audit_logs(actor_id)"),
            ("ix_sup_user",           "CREATE INDEX IF NOT EXISTS ix_sup_user ON supervisions(user_id)"),
            ("ix_sup_schedule",       "CREATE INDEX IF NOT EXISTS ix_sup_schedule ON supervisions(schedule_id)"),
        ]
        for name, sql in indexes:
            safe_exec(conn, sql, f"index {name}")

        # ════════════════════════════════════════════════════
        # STEP 6: UserRole enum — เพิ่ม dept_supervisor
        # ════════════════════════════════════════════════════
        print("\n[6] UserRole enum — add dept_supervisor")
        try:
            conn.execute(text(
                "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'dept_supervisor'"
            ))
            conn.commit()
            print("  ✅ UserRole.dept_supervisor added")
        except Exception as e:
            conn.rollback()
            if "already exists" in str(e).lower() or "does not exist" in str(e).lower():
                print("  ⏭  UserRole.dept_supervisor (already exists or not enum type)")
            else:
                print(f"  ⚠  UserRole enum: {e}")

        # ════════════════════════════════════════════════════
        # STEP 7: ตรวจสอบ integrity
        # ════════════════════════════════════════════════════
        print("\n[7] Integrity check")

        checks = [
            ("users",             "division"),
            ("users",             "dept_code"),
            ("users",             "employee_id"),
            ("sections",          "import_session_id"),
            ("exam_submissions",  "print_duplex"),
            ("exam_submissions",  "print_staple"),
            ("exam_submissions",  "print_spec_confirmed"),
        ]
        all_ok = True
        for table, col in checks:
            exists = col_exists(conn, table, col)
            status = "✅" if exists else "❌"
            print(f"  {status} {table}.{col}")
            if not exists:
                all_ok = False

        # ตรวจ tables ใหม่
        new_tables = ["import_sessions", "enrollment_records", "exam_periods", "external_exams", "external_supervisions", "staff_unavailability", "room_unavailability", "optimize_sessions", "co_exam_groups", "co_exam_members", "revoked_tokens", "section_exam_managers", "exam_material_requests"]
        for t in new_tables:
            r = conn.execute(text(
                "SELECT 1 FROM information_schema.tables WHERE table_name=:t"
            ), {"t": t}).fetchone()
            status = "✅" if r else "❌"
            print(f"  {status} table {t}")
            if not r:
                all_ok = False



        # ════════════════════════════════════════════════════
        # STEP 7c: external_exams + external_supervisions
        # ════════════════════════════════════════════════════
        print("\n[7c] external_exams + external_supervisions tables")
        # สร้างโดย create_all ใน STEP 0 แล้ว — ตรวจสอบ indexes
        ext_indexes = [
            "CREATE INDEX IF NOT EXISTS ix_external_period ON external_exams(exam_period_id)",
            "CREATE INDEX IF NOT EXISTS ix_external_date   ON external_exams(exam_date)",
            "CREATE INDEX IF NOT EXISTS ix_ext_sup_user    ON external_supervisions(user_id)",
        ]
        for sql in ext_indexes:
            safe_exec(conn, sql, sql.split("ix_")[1].split(" ")[0])


        # ════════════════════════════════════════════════════
        # STEP 7d: revoked_tokens + co_exam tables
        # ════════════════════════════════════════════════════
        print("\n[7d] revoked_tokens + co_exam + optimize_sessions lock fields")
        add_column(conn, "optimize_sessions", "edit_lock_user_id", "INTEGER REFERENCES users(id)")
        add_column(conn, "optimize_sessions", "edit_lock_at",      "TIMESTAMPTZ")
        safe_exec(conn,
            "CREATE INDEX IF NOT EXISTS ix_revoked_created ON revoked_tokens(created_at)",
            "ix_revoked_created")
        safe_exec(conn,
            "CREATE INDEX IF NOT EXISTS ix_co_exam_period ON co_exam_groups(exam_period_id)",
            "ix_co_exam_period")
        safe_exec(conn,
            "CREATE INDEX IF NOT EXISTS ix_co_member_section ON co_exam_members(section_id)",
            "ix_co_member_section")

        # ════════════════════════════════════════════════════
        # STEP 7b: exam_periods table + seed active period
        # ════════════════════════════════════════════════════
        print("\n[7b] exam_periods — create + seed active period")

        # table จะถูกสร้างใน STEP 0 แล้ว แต่ seed ถ้ายังว่าง
        try:
            r = conn.execute(text("SELECT COUNT(*) FROM exam_periods"))
            count = r.scalar()
            if count == 0:
                # อ่าน active period จาก system_settings
                yr_row = conn.execute(text(
                    "SELECT value FROM system_settings WHERE key='current_academic_year'"
                )).fetchone()
                sem_row = conn.execute(text(
                    "SELECT value FROM system_settings WHERE key='current_semester'"
                )).fetchone()
                yr  = yr_row[0]  if yr_row  else "2568"
                sem = sem_row[0] if sem_row else "2"
                label = f"ปลายภาค {sem}/{yr}"
                conn.execute(text(
                    "INSERT INTO exam_periods (academic_year, semester, exam_type, label, is_active) "
                    "VALUES (:yr, :sem, 'final', :label, TRUE)"
                ), {"yr": yr, "sem": sem, "label": label})
                conn.commit()
                print(f"  ✅ Seeded active period: {label}")
            else:
                print(f"  ⏭  exam_periods already has {count} rows")
        except Exception as e:
            conn.rollback()
            print(f"  ⚠  exam_periods seed: {e}")

        # ════════════════════════════════════════════════════
        # STEP 8: สรุป
        # ════════════════════════════════════════════════════
        # ════════════════════════════════════════════════════
        # STEP 8: exam_date String → Date type migration
        # ════════════════════════════════════════════════════
        print("\n[8] exam_schedules — migrate exam_date String → Date")
        try:
            # ตรวจ type ปัจจุบัน
            r = conn.execute(text(
                "SELECT data_type FROM information_schema.columns "
                "WHERE table_name='exam_schedules' AND column_name='exam_date'"
            )).fetchone()
            current_type = r[0] if r else None

            if current_type and 'character' in current_type.lower():
                # แปลง string → date (format: YYYY-MM-DD)
                # ก่อน ALTER ต้องแก้ค่า NULL ก่อน
                conn.execute(text(
                    "UPDATE exam_schedules SET exam_date = NULL WHERE exam_date = '' OR exam_date IS NULL"
                ))
                conn.execute(text(
                    "ALTER TABLE exam_schedules "
                    "ALTER COLUMN exam_date TYPE DATE USING exam_date::DATE"
                ))
                conn.commit()
                print("  ✅ exam_date migrated String → DATE")
            elif current_type and 'date' in current_type.lower():
                print("  ⏭  exam_date already DATE type")
            else:
                print(f"  ⚠  exam_date type: {current_type}")
        except Exception as e:
            conn.rollback()
            print(f"  ⚠  exam_date migration: {e}")

        print("\n[8b] AuditLog — add new columns")
        audit_new_cols = [
            ("user_agent_hash", "VARCHAR(64)"),
            ("request_id",      "VARCHAR(36)"),
            ("duration_ms",     "INTEGER"),
            ("http_status",     "INTEGER"),
        ]
        for col, defn in audit_new_cols:
            add_column(conn, "audit_logs", col, defn)

        print("\n[8c] ExamSchedule — add normalized time columns")
        add_column(conn, "exam_schedules", "exam_time_start", "VARCHAR(8)")
        add_column(conn, "exam_schedules", "exam_time_end",   "VARCHAR(8)")

        # backfill exam_time_start/end จาก exam_time string
        try:
            conn.execute(text("""
                UPDATE exam_schedules
                SET exam_time_start = SPLIT_PART(exam_time, '-', 1),
                    exam_time_end   = SPLIT_PART(exam_time, '-', 2)
                WHERE exam_time IS NOT NULL
                  AND exam_time LIKE '%-%'
                  AND exam_time_start IS NULL
            """))
            conn.commit()
            print("  ✅ exam_time_start/end backfilled")
        except Exception as e:
            conn.rollback()
            print(f"  ⚠  backfill: {e}")

        print("\n[8d] Section — sync num_students from enrollment_records")
        try:
            conn.execute(text("""
                UPDATE sections s
                SET num_students = (
                    SELECT COUNT(*)
                    FROM enrollment_records er
                    WHERE er.section_id = s.id
                )
                WHERE EXISTS (
                    SELECT 1 FROM enrollment_records er WHERE er.section_id = s.id
                )
            """))
            conn.commit()
            print("  ✅ Section.num_students synced")
        except Exception as e:
            conn.rollback()
            print(f"  ⚠  num_students sync: {e}")

        print("\n[8e] Supervision.compensation — Float → Numeric")
        try:
            r = conn.execute(text(
                "SELECT data_type FROM information_schema.columns "
                "WHERE table_name='supervisions' AND column_name='compensation'"
            )).fetchone()
            if r and 'double' in (r[0] or '').lower():
                conn.execute(text(
                    "ALTER TABLE supervisions ALTER COLUMN compensation TYPE NUMERIC(10,2)"
                ))
                conn.execute(text(
                    "ALTER TABLE external_supervisions ALTER COLUMN compensation TYPE NUMERIC(10,2)"
                ))
                conn.commit()
                print("  ✅ compensation migrated Float → NUMERIC(10,2)")
            else:
                print(f"  ⏭  compensation already {r[0] if r else 'unknown'}")
        except Exception as e:
            conn.rollback()
            print(f"  ⚠  compensation migration: {e}")

        print("\n[8f] Missing composite indexes")
        new_indexes = [
            "CREATE INDEX IF NOT EXISTS ix_schedule_room_slot ON exam_schedules(room_id, exam_date, exam_time)",
            "CREATE INDEX IF NOT EXISTS ix_schedule_date_time ON exam_schedules(exam_date, exam_time)",
            "CREATE INDEX IF NOT EXISTS ix_schedule_status_period ON exam_schedules(status, exam_date)",
            "CREATE INDEX IF NOT EXISTS ix_section_period ON sections(semester, academic_year)",
            "CREATE INDEX IF NOT EXISTS ix_audit_table_record ON audit_logs(table_name, record_id)",
            "CREATE INDEX IF NOT EXISTS ix_audit_action ON audit_logs(action)",
            "CREATE INDEX IF NOT EXISTS ix_audit_request ON audit_logs(request_id)",
            "CREATE INDEX IF NOT EXISTS ix_er_student ON enrollment_records(student_id)",
        ]
        for sql in new_indexes:
            safe_exec(conn, sql, sql.split("ix_")[1].split(" ")[0])


        # ════════════════════════════════════════════════════
        # STEP 9b: users.special_role
        # ════════════════════════════════════════════════════
        print("\n[9b] users.special_role")
        add_column(conn, "users", "special_role", "VARCHAR(30)")
        # backfill room_keepers
        try:
            conn.execute(text("""
                UPDATE users SET special_role = 'room_keeper'
                WHERE username IN ('chanachon.th', 'thiraphan.y')
            """))
            conn.execute(text("""
                UPDATE users SET special_role = 'esq_staff'
                WHERE username IN ('araya.fa', 'sapanyu.wong')
            """))
            conn.commit()
            print("  ✅ special_role backfilled")
        except Exception as e:
            conn.rollback()
            print(f"  ⚠  {e}")

        # ════════════════════════════════════════════════════
        # STEP 9: schema cleanup
        # ════════════════════════════════════════════════════
        print("\n[9] Schema cleanup")

        # 9a: drop exam_type_label (redundant with exam_type enum)
        try:
            result = conn.execute(text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name='exam_schedules' AND column_name='exam_type_label'"
            )).fetchone()
            if result:
                conn.execute(text(
                    "ALTER TABLE exam_schedules DROP COLUMN exam_type_label"
                ))
                conn.commit()
                print("  ✅ exam_type_label column dropped")
            else:
                print("  ⏭  exam_type_label already removed")
        except Exception as e:
            conn.rollback()
            print(f"  ⚠  drop exam_type_label: {e}")

        # 9b: add cascade on exam_schedules (FK)
        # Note: SQLAlchemy handles cascade in ORM layer; DB-level handled via FK
        # เพิ่ม ON DELETE CASCADE ถ้า section ถูกลบ
        try:
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.referential_constraints
                        WHERE constraint_name = 'exam_schedules_section_id_fkey_cascade'
                    ) THEN
                        ALTER TABLE exam_schedules
                            DROP CONSTRAINT IF EXISTS exam_schedules_section_id_fkey;
                        ALTER TABLE exam_schedules
                            ADD CONSTRAINT exam_schedules_section_id_fkey
                            FOREIGN KEY (section_id) REFERENCES sections(id)
                            ON DELETE CASCADE;
                    END IF;
                END $$;
            """))
            conn.commit()
            print("  ✅ exam_schedules.section_id FK updated to ON DELETE CASCADE")
        except Exception as e:
            conn.rollback()
            print(f"  ⚠  cascade FK: {e}")

        # 9c: add exam_time_start/end computed values
        print("\n[9c] Normalize exam_time → start/end")
        add_column(conn, "exam_schedules", "exam_time_start", "VARCHAR(8)")
        add_column(conn, "exam_schedules", "exam_time_end",   "VARCHAR(8)")
        try:
            conn.execute(text("""
                UPDATE exam_schedules
                SET exam_time_start = TRIM(SPLIT_PART(exam_time::text, '-', 1)),
                    exam_time_end   = TRIM(SPLIT_PART(exam_time::text, '-', 2))
                WHERE exam_time IS NOT NULL
                  AND exam_time::text LIKE '%-%'
                  AND exam_time_start IS NULL
            """))
            conn.commit()
            print("  ✅ exam_time_start/end backfilled")
        except Exception as e:
            conn.rollback()
            print(f"  ⚠  time normalize: {e}")

        # 9d: unique constraint on enrollment_records (section_id, student_id)
        print("\n[9d] EnrollmentRecord unique constraint")
        if not constraint_exists(conn, "enrollment_records", "uq_enrollment_section_student"):
            safe_exec(
                conn,
                "ALTER TABLE enrollment_records ADD CONSTRAINT uq_enrollment_section_student "
                "UNIQUE (section_id, student_id)",
                "uq_enrollment_section_student added",
            )
        else:
            print("  ⏭  uq_enrollment_section_student already exists")


        # ════════════════════════════════════════════════════
        # STEP 10: exam_manager tables + exam_format_confirmed
        # ════════════════════════════════════════════════════
        print("\n[10] exam_manager + material request")
        add_column(conn, "exam_submissions", "exam_format_confirmed",    "BOOLEAN DEFAULT FALSE")
        add_column(conn, "exam_submissions", "exam_format_confirmed_at", "TIMESTAMPTZ")
        safe_exec(conn,
            "CREATE INDEX IF NOT EXISTS ix_exam_manager_user ON section_exam_managers(manager_id)",
            "ix_exam_manager_user")
        safe_exec(conn,
            "CREATE INDEX IF NOT EXISTS ix_exam_manager_section ON section_exam_managers(section_id)",
            "ix_exam_manager_section")


        print("\n" + "=" * 60)
        if all_ok:
            print("✅ Migration v2 COMPLETE — all checks passed")
        else:
            print("⚠  Migration v2 DONE with warnings — check ❌ items above")
        print("=" * 60)


if __name__ == "__main__":
    run()
