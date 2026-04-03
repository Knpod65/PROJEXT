"""
import_data.py — นำเข้าข้อมูลจริงเข้า EMS Database
วางไฟล์นี้ไว้ใน ems_system/backend/
วาง Excel/CSV ทั้ง 4 ไฟล์ไว้ใน ems_system/backend/data/

รัน: python import_data.py
"""

import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from sqlalchemy.orm import Session
from database import engine, Base
from models import (
    User, UserRole, Course, Section, ExamSchedule, ExamType,
    ScheduleStatus, Room
)
from auth_utils import hash_password

# ── Config ────────────────────────────────────────────────────
DATA_DIR        = os.path.join(os.path.dirname(__file__), "data")
ADMIN_EMAIL     = "atikant.s@cmu.ac.th"   # ← email ของ admin
DEFAULT_PASSWORD = "cmu2025!"              # ← รหัสผ่านเริ่มต้นสำหรับทุกคน

EMPLOYEE_FILE   = os.path.join(DATA_DIR, "Employee190226.csv")
PERSONNEL_FILE  = os.path.join(DATA_DIR, "Personnel_120226.xlsx")
OPENCOURSE_FILE = os.path.join(DATA_DIR, "opencourse.xls")
BOOK1_FILE      = os.path.join(DATA_DIR, "Book1.xls")

# ─────────────────────────────────────────────────────────────

def clean(val):
    if pd.isna(val): return None
    return str(val).strip()

def make_username(email: str) -> str:
    """ใช้ส่วนหน้า @ เป็น username"""
    return email.split("@")[0].lower().strip()


def import_users(db: Session):
    print("\n📥 นำเข้า Users (Employee + Personnel)...")

    # ── Employee (Staff) ─────────────────────────────────────
    df_emp = pd.read_csv(EMPLOYEE_FILE, encoding="utf-8-sig")
    staff_count = 0
    for _, row in df_emp.iterrows():
        email = clean(row.get("cmu_mail", ""))
        if not email:
            continue

        # ตรวจสอบว่ามีแล้วหรือยัง
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            continue

        is_admin = (email == ADMIN_EMAIL)
        username = make_username(email)

        # ถ้า username ซ้ำ ให้เติม employee_id ต่อท้าย
        if db.query(User).filter(User.username == username).first():
            username = f"{username}_{int(row.get('employee_id', 0))}"

        full_name = f"{clean(row.get('title',''))} {clean(row.get('name',''))} {clean(row.get('surname',''))}".strip()

        user = User(
            username     = username,
            email        = email,
            password_hash= hash_password(DEFAULT_PASSWORD),
            role         = UserRole.admin if is_admin else UserRole.staff,
            full_name    = full_name,
            department   = clean(row.get("division")),
            is_active    = True,
        )
        db.add(user)
        staff_count += 1
        if is_admin:
            print(f"   ⭐ ADMIN: {full_name} ({email})")

    db.flush()
    print(f"   ✅ Staff: {staff_count} คน")

    # ── Personnel (Teacher) ───────────────────────────────────
    df_per = pd.read_excel(PERSONNEL_FILE)
    teacher_count = 0
    for _, row in df_per.iterrows():
        email = clean(row.get("cmu_mail", ""))
        if not email:
            continue

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            # ถ้ามีแล้วแต่เป็น staff → upgrade เป็น teacher
            if existing.role == UserRole.staff:
                existing.role = UserRole.teacher
            continue

        is_admin = (email == ADMIN_EMAIL)
        username = make_username(email)
        if db.query(User).filter(User.username == username).first():
            username = f"{username}_{int(row.get('teacher_id', 0))}"

        title   = clean(row.get("title", ""))
        name    = clean(row.get("name", ""))
        surname = clean(row.get("surname", ""))
        full_name = f"{title}{name} {surname}".strip()

        dept_map = {"GOV": "รัฐศาสตร์", "PA": "รัฐประศาสนศาสตร์", "IR": "ความสัมพันธ์ระหว่างประเทศ"}
        dept_code = clean(row.get("department", ""))
        dept = dept_map.get(dept_code, dept_code)

        user = User(
            username     = username,
            email        = email,
            password_hash= hash_password(DEFAULT_PASSWORD),
            role         = UserRole.admin if is_admin else UserRole.teacher,
            full_name    = full_name,
            department   = dept,
            is_active    = True,
        )
        db.add(user)
        teacher_count += 1

    db.flush()
    print(f"   ✅ Teacher: {teacher_count} คน")

    db.commit()


def import_courses_and_sections(db: Session):
    print("\n📥 นำเข้า Courses + Sections จาก opencourse.xls...")

    df = pd.read_html(OPENCOURSE_FILE)[0]

    # สร้าง lookup: full_name → user_id สำหรับ match อาจารย์
    teachers = db.query(User).filter(User.role == UserRole.teacher).all()
    # map ทั้ง "ชื่อ นามสกุล" และ "นามสกุล ชื่อ" เพื่อเพิ่มโอกาส match
    name_map = {}
    for t in teachers:
        if t.full_name:
            # ตัด title prefix (รศ.ดร. ผศ.ดร. อ.ดร. ฯลฯ) ออก
            bare = re.sub(r'^(รศ\.|ผศ\.|อ\.|ดร\.|ศ\.)+\.?\s*', '', t.full_name).strip()
            name_map[bare] = t.id
            name_map[t.full_name] = t.id

    course_count  = 0
    section_count = 0
    unmatched_lecturers = set()

    for _, row in df.iterrows():
        course_no = str(clean(row["COURESNO"]))
        title     = clean(row["TITLE"])
        seclec    = int(row["SECLEC"]) if pd.notna(row["SECLEC"]) else 0
        crelec    = float(row["CRELEC"]) if pd.notna(row["CRELEC"]) else 3.0
        regist    = int(row["REGIST"]) if pd.notna(row["REGIST"]) else 0
        max_std   = int(row["MAX"]) if pd.notna(row["MAX"]) else 0
        lecturer  = clean(row["LECTURER"])
        semester  = str(int(row["SEMESTER"])) if pd.notna(row["SEMESTER"]) else "2"
        year      = str(int(row["YEAR"])) if pd.notna(row["YEAR"]) else "2568"

        # สอบ final
        fin_day  = clean(row.get("FIN_DAY"))
        fin_time = clean(row.get("FIN_TIME"))
        mid_day  = clean(row.get("MID_DAY"))
        mid_time = clean(row.get("MID_TIME"))

        # ── Course ──
        course = db.query(Course).filter(Course.course_id == course_no).first()
        if not course:
            course = Course(
                course_id     = course_no,
                course_name_th= title,
                course_name_en= title,
                credits       = int(crelec),
                department    = "คณะรัฐศาสตร์ฯ",
            )
            db.add(course)
            db.flush()
            course_count += 1

        # ── Teacher match ──
        teacher_id = None
        if lecturer:
            # ลอง direct match ก่อน
            teacher_id = name_map.get(lecturer)
            if not teacher_id:
                # ลอง partial match (เอาแค่ชื่อ)
                for name_key, tid in name_map.items():
                    if lecturer in name_key or name_key in lecturer:
                        teacher_id = tid
                        break
            if not teacher_id and lecturer not in ("คณาจารย์",):
                unmatched_lecturers.add(lecturer)

        # ── Section ──
        exists = db.query(Section).join(Course).filter(
            Course.course_id == course_no,
            Section.section_no == str(seclec),
            Section.semester == semester,
            Section.academic_year == year,
        ).first()
        if exists:
            continue

        section = Section(
            course_id    = course.id,
            section_no   = str(seclec),
            teacher_id   = teacher_id,
            num_students = regist,
            semester     = semester,
            academic_year= year,
            is_co_exam   = False,
        )
        db.add(section)
        db.flush()
        section_count += 1

        # ── ExamSchedule (Final) ──
        if fin_day and fin_time:
            exam_date = _parse_date(fin_day)
            if exam_date:
                # หาห้อง
                room_name = clean(row.get("ROOM", ""))
                room = _get_or_create_room(db, room_name) if room_name else None

                sch = ExamSchedule(
                    section_id       = section.id,
                    room_id          = room.id if room else None,
                    exam_date        = exam_date,
                    exam_time        = fin_time,
                    exam_type        = ExamType.final,
                    status           = ScheduleStatus.published,
                    num_pages        = 1,
                    total_sheets     = regist * 1,
                )
                db.add(sch)

    db.flush()
    db.commit()
    print(f"   ✅ Courses: {course_count}  |  Sections: {section_count}")
    if unmatched_lecturers:
        print(f"   ⚠️  Lecturer ที่ match ไม่ได้: {unmatched_lecturers}")


def _parse_date(date_str: str) -> str | None:
    """แปลง '23 MAR 2026' → '2569-03-23' (ปี พ.ศ.)"""
    if not date_str:
        return None
    month_map = {
        "JAN":"01","FEB":"02","MAR":"03","APR":"04",
        "MAY":"05","JUN":"06","JUL":"07","AUG":"08",
        "SEP":"09","OCT":"10","NOV":"11","DEC":"12"
    }
    parts = date_str.strip().split()
    if len(parts) == 3:
        day, mon, year_ce = parts
        month = month_map.get(mon.upper(), "01")
        year_be = int(year_ce) + 543
        return f"{year_be}-{month}-{int(day):02d}"
    return None


def _get_or_create_room(db: Session, room_name: str) -> Room:
    room = db.query(Room).filter(Room.room_name == room_name).first()
    if not room:
        # ประมาณ capacity จากชื่อห้อง
        cap = 200 if "Auditorium" in room_name or "aud" in room_name.lower() else 60
        room = Room(room_name=room_name, capacity=cap, is_active=True)
        db.add(room)
        db.flush()
    return room


def import_students(db: Session):
    """
    นำเข้านักศึกษา + การลงทะเบียน
    Book1: ID, NAME, SNAME, COURSENO, SECLEC, SEMESTER, YEAR
    → สร้าง User (role=student) + Enrollment
    """
    print("\n📥 นำเข้านักศึกษาจาก Book1.xls...")

    # Import Student + Enrollment models
    from models import Student, Enrollment

    df = pd.read_excel(BOOK1_FILE, engine="xlrd")

    # กรองเฉพาะวิชาของคณะ (รหัสขึ้นต้นด้วย 12x, 13x)
    df_fac = df[df["COURSENO"].astype(str).str.match(r'^1[23]\d{4}$')]
    print(f"   วิชาของคณะ: {len(df_fac)} แถว จาก {len(df)} ทั้งหมด")

    student_count    = 0
    enrollment_count = 0
    skipped          = 0

    # Build section lookup: (courseno, seclec, semester, year) → section_id
    sections = db.query(Section).join(Course).all()
    sec_map = {}
    for s in sections:
        key = (s.course.course_id, str(int(s.section_no) if s.section_no.isdigit() else s.section_no),
               s.semester, s.academic_year)
        sec_map[key] = s.id

    seen_students = set()

    for _, row in df_fac.iterrows():
        student_id = str(int(row["ID"])) if pd.notna(row["ID"]) else None
        if not student_id:
            continue

        course_no = str(int(row["COURSENO"])) if pd.notna(row["COURSENO"]) else None
        sec_no    = str(int(row["SECLEC"])) if pd.notna(row["SECLEC"]) else "1"
        semester  = str(int(row["SEMESTER"])) if pd.notna(row["SEMESTER"]) else "2"
        year      = str(int(row["YEAR"])) if pd.notna(row["YEAR"]) else "2568"

        # ── Student (สร้างแค่ครั้งเดียวต่อ student_id) ──
        if student_id not in seen_students:
            existing = db.query(Student).filter(Student.student_id == student_id).first()
            if not existing:
                name    = clean(row.get("NAME", ""))
                surname = clean(row.get("SNAME", ""))
                major   = clean(row.get("MAJOR", ""))
                fac     = clean(row.get("FAC_NAME", ""))
                student = Student(
                    student_id = student_id,
                    full_name  = f"{name} {surname}".strip() if name else student_id,
                    major      = major,
                    faculty    = fac,
                )
                db.add(student)
                student_count += 1
            seen_students.add(student_id)

        # ── Enrollment ──
        sec_key = (course_no, sec_no, semester, year)
        section_id = sec_map.get(sec_key)
        if not section_id:
            skipped += 1
            continue

        existing_enroll = db.query(Enrollment).filter(
            Enrollment.student_id == student_id,
            Enrollment.section_id == section_id,
        ).first()
        if existing_enroll:
            continue

        db.add(Enrollment(student_id=student_id, section_id=section_id))
        enrollment_count += 1

        if enrollment_count % 500 == 0:
            db.flush()

    db.flush()
    db.commit()
    print(f"   ✅ Students: {student_count}  |  Enrollments: {enrollment_count}  |  Skipped: {skipped}")


def main():
    print("=" * 55)
    print("  EMS Data Import — คณะรัฐศาสตร์ฯ มช.")
    print("=" * 55)

    # สร้าง tables ถ้ายังไม่มี
    Base.metadata.create_all(bind=engine)

    db = Session(engine)
    try:
        import_users(db)
        import_courses_and_sections(db)
        import_students(db)

        # สรุป
        print("\n" + "=" * 55)
        print("  สรุปข้อมูลใน Database")
        print("=" * 55)
        from models import Student, Enrollment
        print(f"  Users (admin+staff+teacher): {db.query(User).count()}")
        print(f"  Courses:     {db.query(Course).count()}")
        print(f"  Sections:    {db.query(Section).count()}")
        print(f"  Schedules:   {db.query(ExamSchedule).count()}")
        print(f"  Students:    {db.query(Student).count()}")
        print(f"  Enrollments: {db.query(Enrollment).count()}")
        print(f"\n  🔑 Login: atikant.s@cmu.ac.th / {DEFAULT_PASSWORD}")
        print("=" * 55)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
