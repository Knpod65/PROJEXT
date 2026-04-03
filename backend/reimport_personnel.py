"""
reimport_personnel.py
นำเข้าข้อมูลจาก Personnel_120226.xlsx (sheet: staff + teacher)
และ opencourse.xls

วางไฟล์นี้ใน ems_system/backend/
วาง Excel ไว้ใน ems_system/backend/data/

รัน: python reimport_personnel.py
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import engine, Base
from models import (
    User, UserRole, Course, Section, ExamSchedule, ExamType,
    ScheduleStatus, Room, Student, Enrollment,
    SectionCoordinator
)
from auth_utils import hash_password

DATA_DIR         = os.path.join(os.path.dirname(__file__), "data")
PERSONNEL_FILE   = os.path.join(DATA_DIR, "Personnel_120226.xlsx")
OPENCOURSE_FILE  = os.path.join(DATA_DIR, "opencourse.xls")
BOOK1_FILE       = os.path.join(DATA_DIR, "Book1.xls")

ADMIN_EMAIL      = "atikant.s@cmu.ac.th"
DEFAULT_PASSWORD = "cmu2025!"

DEPT_TH = {
    "GOV": "ภาควิชารัฐศาสตร์",
    "PA":  "ภาควิชารัฐประศาสนศาสตร์",
    "IR":  "ภาควิชาความสัมพันธ์ระหว่างประเทศ",
    "STB": "ศูนย์ Thai-Burma Studies",
}


def clean(val):
    if pd.isna(val): return None
    return str(val).strip()


def make_username(email: str) -> str:
    return email.split("@")[0].lower().strip()


def unique_username(db, base: str) -> str:
    uname = base
    i = 1
    while db.query(User).filter(User.username == uname).first():
        uname = f"{base}_{i}"
        i += 1
    return uname


# ─────────────────────────────────────────────────────────────
def wipe_users(db: Session):
    """ลบ users ทั้งหมด (ยกเว้นจะสร้างใหม่หมด)"""
    print("🗑  ลบข้อมูล users เดิมทั้งหมด...")
    # ลบ dependents ก่อน
    db.execute(text("DELETE FROM audit_logs"))
    db.execute(text("DELETE FROM exam_access_logs"))
    db.execute(text("DELETE FROM exam_access_tokens"))
    db.execute(text("DELETE FROM exam_messages"))
    db.execute(text("DELETE FROM exam_submission_versions"))
    db.execute(text("DELETE FROM exam_submissions"))
    db.execute(text("DELETE FROM checkin_events"))
    db.execute(text("DELETE FROM swap_requests"))
    db.execute(text("DELETE FROM supervisions"))
    db.execute(text("DELETE FROM supervision_baselines"))
    db.execute(text("DELETE FROM section_coordinators"))
    db.execute(text("DELETE FROM pdf_tokens"))
    db.execute(text("DELETE FROM sections"))
    db.execute(text("DELETE FROM exam_schedules"))
    db.execute(text("DELETE FROM users"))
    db.commit()
    print("   ✅ ลบแล้ว")


# ─────────────────────────────────────────────────────────────
def import_staff(db: Session):
    print("\n📥 นำเข้า Staff (sheet: staff)...")
    df = pd.read_excel(PERSONNEL_FILE, sheet_name="staff")
    count = 0

    for _, row in df.iterrows():
        email  = clean(row.get("cmu_mail", ""))
        if not email:
            continue

        name    = clean(row.get("name", "")) or ""
        surname = clean(row.get("surname", "")) or ""
        title_v = clean(row.get("title", "")) or ""
        role_v  = clean(row.get("role", "")) or ""
        division= clean(row.get("division", "")) or ""
        unit    = clean(row.get("unit", "")) or ""
        mobile  = clean(row.get("mobile", ""))
        ext     = clean(row.get("ext", ""))
        emp_id  = int(row.get("employee_id", 0)) if pd.notna(row.get("employee_id")) else None

        full_name = f"{title_v}{name} {surname}".strip()
        is_name_head = "หัวหน้างาน" in surname or "หัวหน้างาน" in name

        # Determine role
        if email == ADMIN_EMAIL:
            user_role = UserRole.admin
        elif division == "Education_Student_Quality":
            if role_v == "Head_of_Unit" or is_name_head:
                user_role = UserRole.esq_head
            else:
                user_role = UserRole.esq_staff
        else:
            user_role = UserRole.staff

        username = unique_username(db, make_username(email))
        user = User(
            username    = username,
            email       = email,
            password_hash= hash_password(DEFAULT_PASSWORD),
            role        = user_role,
            full_name   = full_name,
            department  = division,
            division    = division,
            unit        = unit,
            title       = title_v,
            mobile      = mobile,
            ext         = ext,
            employee_id = emp_id,
            is_active   = True,
        )
        db.add(user)
        count += 1

        tag = ""
        if user_role == UserRole.admin:    tag = " ⭐ ADMIN"
        elif user_role == UserRole.esq_head:  tag = " 👁 ESQ_HEAD"
        elif user_role == UserRole.esq_staff: tag = " 📋 ESQ_STAFF"
        print(f"   {full_name} ({email}){tag}")

    db.flush()
    print(f"   ✅ Staff: {count} คน")
    return count


# ─────────────────────────────────────────────────────────────
def import_teachers(db: Session):
    print("\n📥 นำเข้า Teacher (sheet: teacher)...")
    df = pd.read_excel(PERSONNEL_FILE, sheet_name="teacher")
    count = 0
    dept_heads = {}  # dept_code → first teacher as dept coordinator

    for _, row in df.iterrows():
        email  = clean(row.get("cmu_mail", ""))
        if not email:
            continue

        name    = clean(row.get("name", "")) or ""
        surname = clean(row.get("surname", "")) or ""
        title_v = clean(row.get("title", "")) or ""
        dept    = clean(row.get("department", "")) or ""
        mobile  = clean(row.get("mobile", ""))
        ext     = clean(row.get("ext", ""))
        t_id    = int(row.get("teacher_id", 0)) if pd.notna(row.get("teacher_id")) else None

        full_name = f"{title_v}{name} {surname}".strip()
        dept_full = DEPT_TH.get(dept, dept)

        username = unique_username(db, make_username(email))
        user = User(
            username    = username,
            email       = email,
            password_hash= hash_password(DEFAULT_PASSWORD),
            role        = UserRole.teacher,
            full_name   = full_name,
            department  = dept_full,
            dept_code   = dept,
            title       = title_v,
            mobile      = mobile,
            ext         = ext,
            employee_id = t_id,
            is_active   = True,
        )
        db.add(user)
        count += 1
        print(f"   {full_name} ({email}) [{dept}]")

    db.flush()
    print(f"   ✅ Teacher: {count} คน")

    # สร้าง SectionCoordinator จาก ESQ staff (1 คนต่อ dept)
    # ตามที่ระบุว่า GOV/PA/IR/STB มี ESQ staff ดูแล
    print("\n📥 กำหนด Section Coordinators...")
    esq_staff = db.query(User).filter(
        User.role.in_([UserRole.esq_staff, UserRole.esq_head]),
        User.is_active == True,
    ).all()

    # Map dept → coordinator (ใช้ ESQ staff ที่ไม่ได้เป็น head)
    depts = ["GOV", "PA", "IR", "STB"]
    esq_members = [u for u in esq_staff if u.role == UserRole.esq_staff]
    for i, dept in enumerate(depts):
        if i < len(esq_members):
            coord = SectionCoordinator(
                user_id    = esq_members[i].id,
                department = dept,
            )
            db.add(coord)
            print(f"   {dept} → {esq_members[i].full_name}")

    db.flush()
    return count


# ─────────────────────────────────────────────────────────────
def import_courses_and_schedules(db: Session):
    """นำเข้า OpenCourse + สร้าง Schedule"""
    print("\n📥 นำเข้าวิชาจาก opencourse.xls...")
    if not os.path.exists(OPENCOURSE_FILE):
        print("   ⚠️  ไม่พบ opencourse.xls — ข้าม")
        return

    df = pd.read_html(OPENCOURSE_FILE)[0]

    # Build teacher name lookup: full_name → user
    teachers = db.query(User).filter(User.role == UserRole.teacher).all()
    name_map = {}
    for t in teachers:
        if t.full_name:
            bare = re.sub(r'^(รศ\.|ผศ\.|อ\.|ดร\.|ศ\.)+\.?\s*', '', t.full_name).strip()
            name_map[bare]       = t.id
            name_map[t.full_name]= t.id
            # Also map first name only
            parts = bare.split()
            if parts:
                name_map[parts[0]] = t.id

    # Clear courses/sections/schedules/rooms
    db.execute(text("DELETE FROM supervisions"))
    db.execute(text("DELETE FROM exam_schedules"))
    db.execute(text("DELETE FROM sections"))
    db.execute(text("DELETE FROM courses"))
    db.execute(text("DELETE FROM rooms"))
    db.commit()

    MONTH_MAP = {"JAN":"01","FEB":"02","MAR":"03","APR":"04","MAY":"05","JUN":"06",
                 "JUL":"07","AUG":"08","SEP":"09","OCT":"10","NOV":"11","DEC":"12"}

    def parse_date(s):
        if not s: return None
        parts = str(s).strip().split()
        if len(parts)==3:
            d,m,y = parts
            month = MONTH_MAP.get(m.upper(),"01")
            return f"{int(y)+543}-{month}-{int(d):02d}"
        return None

    def get_or_create_room(room_name):
        r = db.query(Room).filter(Room.room_name==room_name).first()
        if not r:
            cap = 200 if any(x in room_name.lower() for x in ["auditorium","aud"]) else 60
            r = Room(room_name=room_name, capacity=cap, is_active=True)
            db.add(r); db.flush()
        return r

    course_objs = {}
    section_count = 0
    unmatched = set()

    for _, row in df.iterrows():
        cno   = str(clean(row["COURESNO"]))
        title = clean(row["TITLE"])
        seclec= int(row["SECLEC"]) if pd.notna(row["SECLEC"]) else 0
        crelec= float(row["CRELEC"]) if pd.notna(row["CRELEC"]) else 3.0
        regist= int(row["REGIST"]) if pd.notna(row["REGIST"]) else 0
        lecturer = clean(row["LECTURER"])
        semester = str(int(row["SEMESTER"])) if pd.notna(row["SEMESTER"]) else "2"
        year = str(int(row["YEAR"])) if pd.notna(row["YEAR"]) else "2568"
        fin_day = clean(row.get("FIN_DAY"))
        fin_time= clean(row.get("FIN_TIME"))
        room_name = clean(row.get("ROOM",""))

        # Course
        if cno not in course_objs:
            c = Course(course_id=cno, course_name_th=title, course_name_en=title,
                       credits=int(crelec), department="คณะรัฐศาสตร์ฯ")
            db.add(c); db.flush()
            course_objs[cno] = c
        course = course_objs[cno]

        # Teacher match
        teacher_id = None
        if lecturer:
            teacher_id = name_map.get(lecturer)
            if not teacher_id:
                for nk,tid in name_map.items():
                    if lecturer in nk or nk in lecturer:
                        teacher_id = tid; break
            if not teacher_id and lecturer not in ("คณาจารย์",):
                unmatched.add(lecturer)

        section = Section(
            course_id=course.id, section_no=str(seclec),
            teacher_id=teacher_id, num_students=regist,
            semester=semester, academic_year=year,
        )
        db.add(section); db.flush()
        section_count += 1

        if fin_day and fin_time:
            exam_date = parse_date(fin_day)
            if exam_date:
                room = get_or_create_room(room_name) if room_name else None
                sch = ExamSchedule(
                    section_id=section.id,
                    room_id=room.id if room else None,
                    exam_date=exam_date, exam_time=fin_time,
                    exam_type=ExamType.final,
                    status=ScheduleStatus.published,
                    num_pages=1, total_sheets=regist,
                )
                db.add(sch)

    db.commit()
    print(f"   ✅ Courses: {len(course_objs)}  Sections: {section_count}")
    if unmatched:
        print(f"   ⚠️  Match ไม่ได้: {unmatched}")


# ─────────────────────────────────────────────────────────────
def import_students(db: Session):
    print("\n📥 นำเข้านักศึกษาจาก Book1.xls...")
    if not os.path.exists(BOOK1_FILE):
        print("   ⚠️  ไม่พบ Book1.xls — ข้าม")
        return

    # Clear students
    db.execute(text("DELETE FROM enrollments"))
    db.execute(text("DELETE FROM students"))
    db.commit()

    df = pd.read_excel(BOOK1_FILE, engine="xlrd")
    df_fac = df[df["COURSENO"].astype(str).str.match(r'^1[23]\d{4}$')]
    print(f"   วิชาคณะ: {len(df_fac)} แถว")

    sections = db.query(Section).join(Course).all()
    sec_map = {}
    for s in sections:
        key = (s.course.course_id, str(s.section_no), s.semester, s.academic_year)
        sec_map[key] = s.id

    seen = set()
    stu_count = 0
    enroll_count = 0

    for _, row in df_fac.iterrows():
        sid = str(int(row["ID"])) if pd.notna(row["ID"]) else None
        if not sid: continue

        cno = str(int(row["COURSENO"])) if pd.notna(row["COURSENO"]) else None
        sec = str(int(row["SECLEC"]))   if pd.notna(row["SECLEC"])   else "1"
        sem = str(int(row["SEMESTER"])) if pd.notna(row["SEMESTER"]) else "2"
        yr  = str(int(row["YEAR"]))     if pd.notna(row["YEAR"])     else "2568"

        if sid not in seen:
            name = clean(row.get("NAME","")) or ""
            sname= clean(row.get("SNAME","")) or ""
            db.add(Student(
                student_id=sid,
                full_name=f"{name} {sname}".strip(),
                major=clean(row.get("MAJOR","")),
                faculty=clean(row.get("FAC_NAME","")),
            ))
            stu_count += 1
            seen.add(sid)

        section_id = sec_map.get((cno, sec, sem, yr))
        if section_id:
            db.add(Enrollment(student_id=sid, section_id=section_id))
            enroll_count += 1

        if (stu_count + enroll_count) % 500 == 0:
            db.flush()

    db.commit()
    print(f"   ✅ Students: {stu_count}  Enrollments: {enroll_count}")


# ─────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  EMS Data Reimport — Personnel_120226.xlsx")
    print("=" * 60)

    Base.metadata.create_all(bind=engine)
    db = Session(engine)

    try:
        wipe_users(db)
        import_staff(db)
        import_teachers(db)
        import_courses_and_schedules(db)
        import_students(db)

        # สรุป
        print("\n" + "=" * 60)
        print("  สรุป")
        print("=" * 60)
        from sqlalchemy import func
        roles = db.execute(text(
            "SELECT role, COUNT(*) as n FROM users GROUP BY role ORDER BY n DESC"
        )).fetchall()
        for r in roles:
            print(f"  {r[0]:15s} : {r[1]} คน")
        print()
        print(f"  Courses      : {db.query(Course).count()}")
        print(f"  Sections     : {db.query(Section).count()}")
        print(f"  Schedules    : {db.query(ExamSchedule).count()}")
        print(f"  Students     : {db.query(Student).count()}")
        print(f"  Enrollments  : {db.query(Enrollment).count()}")
        print()
        print(f"  🔑 Login: atikant.s@cmu.ac.th  /  {DEFAULT_PASSWORD}")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        import traceback; traceback.print_exc()
        print(f"\n❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
