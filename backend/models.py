"""
Models — 16 tables ตาม ERD
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, Date, Numeric,
    ForeignKey, Enum, JSON, UniqueConstraint, Index, event, select
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
from academic_groups import academic_group_label, get_academic_group_code_from_course_id


class UserRole(str, enum.Enum):
    admin            = "admin"            # full access + edit + ลงนามทุก round
    esq_head         = "esq_head"         # นภาภรณ์ — view all, read-only + ลงนาม + ข้อเสนอแนะ
    secretary        = "secretary"        # ปวีณา — view all, read-only + ลงนาม + ข้อเสนอแนะ
    dept_supervisor  = "dept_supervisor"  # ภูษณิศา/พรชนก/รุ่งทิวา/ชนิกานต์ — view+edit แค่แผนกตัวเอง
    staff            = "staff"            # เจ้าหน้าที่ทั่วไป — คุมสอบ/swap/check-in
    teacher          = "teacher"          # อาจารย์ — จัดการข้อสอบของตัวเอง
    print_shop       = "print_shop"       # dedicated print-queue and dispatch workflow
    student          = "student"          # นักศึกษา — ค้นหาตารางสอบ (no login)


class ExamType(str, enum.Enum):
    midterm  = "midterm"
    final    = "final"


class QuestionType(str, enum.Enum):
    mcq      = "mcq"       # Multiple Choice
    essay    = "essay"     # อัตนัย


class ScheduleStatus(str, enum.Enum):
    draft     = "draft"
    published = "published"
    locked    = "locked"


# ─── Users ───────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(100), unique=True, nullable=False, index=True)
    email         = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role          = Column(Enum(UserRole), default=UserRole.staff, nullable=False)
    full_name     = Column(String(200))
    department    = Column(String(200))
    is_active     = Column(Boolean, default=True)
    view_as_role  = Column(Enum(UserRole), nullable=True)   # admin impersonation
    division      = Column(String(100))     # แผนก (staff)
    unit          = Column(String(100))     # หน่วยงาน
    dept_code     = Column(String(10))      # GOV/PA/IR/STB (teacher)
    title         = Column(String(50))      # คำนำหน้า เช่น ผศ.ดร.
    mobile        = Column(String(30))
    ext           = Column(String(20))
    employee_id   = Column(Integer)         # id จาก original file
    special_role  = Column(String(30))      # room_keeper | esq_staff | None
    # room_keeper: ธีราภัณฑ์ + ชนะชล — เปิด/ปิดห้อง ไม่คุม/ไม่กระจาย
    # esq_staff: อารยา + สัพพัญญู — ESQ staff อยู่ใน optimizer แต่ remind
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

    sections      = relationship("Section", back_populates="teacher", foreign_keys="[Section.teacher_id]")
    supervisions  = relationship("Supervision", foreign_keys="[Supervision.user_id]", back_populates="user")
    audit_logs    = relationship("AuditLog", back_populates="actor")
    submissions   = relationship("ExamSubmission", foreign_keys="[ExamSubmission.submitted_by]", back_populates="submitter")


# ─── Courses & Sections ──────────────────────────────────────
class Course(Base):
    __tablename__ = "courses"
    id            = Column(Integer, primary_key=True, index=True)
    course_id     = Column(String(20), nullable=False, index=True)   # เช่น 126101
    course_name_th= Column(String(300))
    course_name_en= Column(String(300))
    credits       = Column(Integer, default=3)
    department    = Column(String(200))
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    sections      = relationship("Section", back_populates="course")

    __table_args__ = (
        UniqueConstraint("course_id", name="uq_course_id"),
        Index("ix_course_course_id", "course_id"),  # ใช้ cast(course_id, Integer) ตอน order_by
    )


    @property
    def academic_group(self) -> str | None:
        return get_academic_group_code_from_course_id(self.course_id)

    @property
    def academic_group_label(self) -> str | None:
        return academic_group_label(self.academic_group)


class Section(Base):
    __tablename__ = "sections"
    id            = Column(Integer, primary_key=True, index=True)
    course_id     = Column(Integer, ForeignKey("courses.id"), nullable=False)
    section_no    = Column(String(10), nullable=False)   # "1", "801", "701"
    teacher_id    = Column(Integer, ForeignKey("users.id"))
    teaching_room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    num_students  = Column(Integer, default=0)
    is_thesis     = Column(Boolean, default=False)
    is_co_exam    = Column(Boolean, default=False)       # co=0 หลายตอนสอบด้วยกัน
    co_group_id   = Column(String(50))                   # group key สำหรับ co-exam
    semester      = Column(String(10), default="2")
    academic_year     = Column(String(10), default="2568")
    import_session_id = Column(Integer, ForeignKey("import_sessions.id"), nullable=True)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())

    course        = relationship("Course", back_populates="sections")
    teacher       = relationship("User", back_populates="sections")
    teaching_room = relationship("Room", back_populates="teaching_sections", foreign_keys=[teaching_room_id])
    schedules     = relationship("ExamSchedule", back_populates="section",
                                  cascade="all, delete-orphan")  # midterm + final
    questions     = relationship("Question", back_populates="section")

    __table_args__ = (
        UniqueConstraint("course_id", "section_no", "semester", "academic_year",
                         name="uq_section"),
        Index("ix_section_period", "semester", "academic_year"),
        Index("ix_section_teaching_room", "teaching_room_id"),
    )


# ─── Rooms ───────────────────────────────────────────────────
    @property
    def academic_group(self) -> str | None:
        if self.course:
            return self.course.academic_group
        return None

    @property
    def academic_group_label(self) -> str | None:
        return academic_group_label(self.academic_group)


class Room(Base):
    __tablename__ = "rooms"
    id            = Column(Integer, primary_key=True, index=True)
    room_name     = Column(String(100), unique=True, nullable=False)
    building      = Column(String(100))
    capacity      = Column(Integer, default=30)
    e_room_code   = Column(String(50))    # รหัสสำหรับ e-room API ของ มช.
    is_active     = Column(Boolean, default=True)

    schedules     = relationship("ExamSchedule", back_populates="room")
    teaching_sections = relationship("Section", back_populates="teaching_room", foreign_keys="[Section.teaching_room_id]")


# ─── Exam Schedule (output ของ Optimizer) ────────────────────
class ExamSchedule(Base):
    __tablename__ = "exam_schedules"
    id            = Column(Integer, primary_key=True, index=True)
    section_id    = Column(Integer, ForeignKey("sections.id"), nullable=False)
    # NOTE: ไม่ unique เพราะ 1 section มีได้ทั้ง midterm + final
    room_id       = Column(Integer, ForeignKey("rooms.id"))
    exam_date     = Column(Date)           # DATE type — sort/query ถูกต้อง
    exam_time     = Column(String(20))    # "09.00-12.00" (เก็บ string เพื่อ backward compat)
    exam_time_start = Column(String(8))   # "09:00" normalized HH:MM
    exam_time_end   = Column(String(8))   # "12:00" normalized HH:MM
    exam_type     = Column(Enum(ExamType), default=ExamType.final)
    status        = Column(Enum(ScheduleStatus), default=ScheduleStatus.draft)
    num_pages     = Column(Integer, default=1)
    total_sheets  = Column(Integer, default=0)  # num_students × num_pages
    paper_distributor = Column(String(200))
    notes         = Column(Text)
    # exam_type_label removed — use exam_type.value instead
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

    section       = relationship("Section", back_populates="schedules")
    room          = relationship("Room", back_populates="schedules")
    supervisions  = relationship("Supervision", back_populates="schedule")

    @property
    def computed_sheets(self) -> int:
        """total_sheets คำนวณจาก section.num_students × num_pages (single source of truth)"""
        n = self.section.num_students if self.section else 0
        return (n or 0) * max(self.num_pages or 1, 1)

    __table_args__ = (
        UniqueConstraint("section_id", "exam_type", name="uq_schedule_section_examtype"),
        Index("ix_schedule_date",          "exam_date"),
        Index("ix_schedule_section",       "section_id"),
        Index("ix_schedule_room_slot",     "room_id", "exam_date", "exam_time"),  # conflict detection
        Index("ix_schedule_date_time",     "exam_date", "exam_time"),             # slot queries
        Index("ix_schedule_status_period", "status", "exam_date"),
    )


# ─── Supervision (กรรมการคุมสอบ) ─────────────────────────────
class Supervision(Base):
    __tablename__ = "supervisions"
    id            = Column(Integer, primary_key=True, index=True)
    schedule_id   = Column(Integer, ForeignKey("exam_schedules.id"), nullable=False)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_in_exam       = Column(String(50), default="supervisor")  # supervisor / chief / distributor
    slot_order         = Column(Integer, default=1)    # 1 = หลัก, 2 = รอง
    compensation       = Column(Numeric(10, 2), default=0.00)  # ค่าตอบแทน (Numeric ป้องกัน float error)
    confirmed          = Column(Boolean, default=False)
    swap_requested     = Column(Boolean, default=False)
    swap_with_id       = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_swapped         = Column(Boolean, default=False)    # True = ถูก swap แล้ว
    baseline_user_id   = Column(Integer, ForeignKey("users.id"), nullable=True)  # original ก่อน swap
    is_emergency_sub   = Column(Boolean, default=False)    # True = คนแทนฉุกเฉิน

    schedule      = relationship("ExamSchedule", back_populates="supervisions")
    user          = relationship("User", foreign_keys="[Supervision.user_id]", back_populates="supervisions")
    swap_with     = relationship("User", foreign_keys="[Supervision.swap_with_id]")
    baseline_user = relationship("User", foreign_keys="[Supervision.baseline_user_id]")

    __table_args__ = (
        UniqueConstraint("schedule_id", "user_id", name="uq_supervision"),
        Index("ix_sup_user", "user_id"),
        Index("ix_sup_schedule", "schedule_id"),
    )


# ─── Exam Builder (M1) ───────────────────────────────────────
class Question(Base):
    __tablename__ = "questions"
    id            = Column(Integer, primary_key=True, index=True)
    section_id    = Column(Integer, ForeignKey("sections.id"), nullable=False)
    q_type        = Column(Enum(QuestionType), nullable=False)
    q_number      = Column(Integer)
    q_text        = Column(Text)
    image_path    = Column(String(500))
    points        = Column(Float, default=1.0)
    answer_lines  = Column(Integer, default=5)    # สำหรับ essay
    options       = Column(JSON)                  # [{label:"A", text:"..."}, ...]
    correct_option= Column(String(5))             # "A","B","C","D"
    page_number   = Column(Integer, default=1)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

    section       = relationship("Section", back_populates="questions")


# ─── PDF Tokens (M3) ─────────────────────────────────────────
class PdfToken(Base):
    __tablename__ = "pdf_tokens"
    id            = Column(Integer, primary_key=True, index=True)
    token         = Column(String(64), unique=True, nullable=False, index=True)
    section_id    = Column(Integer, ForeignKey("sections.id"))
    created_by    = Column(Integer, ForeignKey("users.id"))
    used          = Column(Boolean, default=False)
    expires_at    = Column(DateTime(timezone=True))
    created_at    = Column(DateTime(timezone=True), server_default=func.now())


# ─── Audit Log ───────────────────────────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id              = Column(Integer, primary_key=True, index=True)
    actor_id        = Column(Integer, ForeignKey("users.id"))
    action          = Column(String(100), nullable=False)
    table_name      = Column(String(100))
    record_id       = Column(Integer)
    old_values      = Column(JSON)
    new_values      = Column(JSON)
    ip_hash         = Column(String(64))
    user_agent_hash = Column(String(64))      # hash ของ User-Agent ตรวจ bot/browser
    request_id      = Column(String(36))      # correlation UUID ติดตามทุก log ของ request เดียว
    duration_ms     = Column(Integer)         # response time (ms) ตรวจ slow endpoints
    http_status     = Column(Integer)         # HTTP status code
    timestamp       = Column(DateTime(timezone=True), server_default=func.now())

    actor           = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_timestamp",    "timestamp"),
        Index("ix_audit_actor",        "actor_id"),
        Index("ix_audit_table_record", "table_name", "record_id"),   # history of record
        Index("ix_audit_action",       "action"),
        Index("ix_audit_request",      "request_id"),
    )


# ─── Email Digest Log (M5) ────────────────────────────────────
class EmailDigest(Base):
    __tablename__ = "email_digests"
    id            = Column(Integer, primary_key=True, index=True)
    week_number   = Column(Integer)
    sent_at       = Column(DateTime(timezone=True), server_default=func.now())
    recipient_count = Column(Integer, default=0)
    status        = Column(String(50))
    error_msg     = Column(Text)


# ─── Student (ไม่ต้อง Login) ─────────────────────────────────
# NOTE: Student/Enrollment เป็น legacy — ใช้ EnrollmentRecord แทนสำหรับ import จากทะเบียน
class Student(Base):
    __tablename__ = "students"
    id         = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20), unique=True, nullable=False, index=True)
    full_name  = Column(String(200))
    major      = Column(String(200))
    faculty    = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    enrollments = relationship("Enrollment", back_populates="student")


# ─── Enrollment (นศ. ลงวิชาไหน) ──────────────────────────────
class Enrollment(Base):
    __tablename__ = "enrollments"
    id         = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20), ForeignKey("students.student_id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="enrollments")
    section = relationship("Section")

    __table_args__ = (
        UniqueConstraint("student_id", "section_id", name="uq_enrollment"),
        Index("ix_enrollment_student", "student_id"),
    )

# ─── Exam Type Choice (Teacher Workflow) ─────────────────────
class ExamTypeChoice(str, enum.Enum):
    no_exam       = "no_exam"
    online        = "online"
    onsite        = "onsite"
    outside_sched = "outside_sched"
    in_class      = "in_class"

class AnswerFormat(str, enum.Enum):
    on_paper    = "on_paper"    # เขียนบนกระดาษข้อสอบ
    mcq_omr     = "mcq_omr"    # OMR / optical
    a4_sheets   = "a4_sheets"  # กระดาษ A4 แยก
    booklet     = "booklet"    # สมุดคำตอบ
    hybrid      = "hybrid"     # ผสม

class SubmissionStatus(str, enum.Enum):
    draft     = "draft"
    submitted = "submitted"
    approved  = "approved"
    rejected  = "rejected"
    released  = "released"     # release ให้ printshop แล้ว


class PrintJobStatus(str, enum.Enum):
    queued     = "queued"
    processing = "processing"
    completed  = "completed"
    dispatched = "dispatched"
    delivered  = "delivered"

class SwapStatus(str, enum.Enum):
    pending  = "pending"
    accepted = "accepted"
    rejected = "rejected"
    cancelled= "cancelled"

class CheckinType(str, enum.Enum):
    receive_papers = "receive_papers"   # รับข้อสอบ
    at_room        = "at_room"          # check-in ที่ห้อง


# ─── System Settings ─────────────────────────────────────────
class SystemSetting(Base):
    __tablename__ = "system_settings"
    id          = Column(Integer, primary_key=True, index=True)
    key         = Column(String(100), unique=True, nullable=False)
    value       = Column(Text)
    description = Column(Text)
    updated_by  = Column(Integer, ForeignKey("users.id"))
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now(),
                         server_default=func.now())
    # Keys ที่ใช้:
    # exam_submission_deadline  → "2025-04-01T17:00:00"
    # swap_request_deadline     → "2025-03-20T17:00:00"
    # swap_enabled              → "true" / "false"
    # current_semester          → "2"
    # current_academic_year     → "2568"


# ─── Exam Submission (Teacher Workflow) ──────────────────────
class ExamSubmission(Base):
    __tablename__ = "exam_submissions"
    id                = Column(Integer, primary_key=True, index=True)
    section_id        = Column(Integer, ForeignKey("sections.id"), nullable=False)
    submitted_by      = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Step 0 — exam format (กรอกได้ก่อนกำหนดวัน)
    exam_format_confirmed   = Column(Boolean, default=False)
    exam_format_confirmed_at= Column(DateTime(timezone=True))
    # exam_type_choice + material request กรอกพร้อมกันใน step 0

    # Step 1 — ยืนยันวันสอบ (หลัง admin กำหนดวัน)
    date_confirmed    = Column(Boolean, default=False)
    date_confirmed_at = Column(DateTime(timezone=True))

    # Step 2 — exam type
    exam_type_choice  = Column(Enum(ExamTypeChoice))
    answer_formats    = Column(JSON)   # list[AnswerFormat]
    a4_pages_count    = Column(Integer, default=0)

    # Step 3 — file
    has_uploaded_pdf  = Column(Boolean, default=False)
    pdf_original_path = Column(String(500))   # raw storage path (never exposed)
    pdf_stripped_path = Column(String(500))   # metadata-stripped version
    no_cover_page_confirmed = Column(Boolean, default=False)

    # Step 4 — Print Specifications (อาจารย์กำหนด)
    print_duplex      = Column(Boolean, default=False)   # True = หน้า-หลัง, False = หน้าเดียว
    print_staple      = Column(String(30))               # none | corner_left | side_left | custom
    print_staple_page = Column(Integer, nullable=True)   # ถ้า staple แยกชุด: เย็บที่หน้าที่เท่าไหร่
    print_note        = Column(Text)                     # หมายเหตุเพิ่มเติมสำหรับร้านถ่าย
    print_spec_confirmed = Column(Boolean, default=False)  # อาจารย์ยืนยัน spec แล้ว

    # Shared across sections
    is_shared_exam    = Column(Boolean, default=False)
    shared_with_sections = Column(JSON)  # list[section_id]

    # Workflow
    status            = Column(Enum(SubmissionStatus), default=SubmissionStatus.draft)
    submitted_at      = Column(DateTime(timezone=True))
    approved_by       = Column(Integer, ForeignKey("users.id"))
    approved_at       = Column(DateTime(timezone=True))
    rejected_reason   = Column(Text)
    admin_note        = Column(Text)

    # Version
    version           = Column(Integer, default=1)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())
    updated_at        = Column(DateTime(timezone=True), onupdate=func.now())

    section    = relationship("Section")
    submitter  = relationship("User", foreign_keys="[ExamSubmission.submitted_by]", back_populates="submissions")
    approver   = relationship("User", foreign_keys="[ExamSubmission.approved_by]")
    material_request = relationship("ExamMaterialRequest",
                                     back_populates="submission",
                                     uselist=False,
                                     cascade="all, delete-orphan")
    versions   = relationship("ExamSubmissionVersion",
                              back_populates="submission",
                              order_by="ExamSubmissionVersion.version")
    tokens     = relationship("ExamAccessToken", back_populates="submission")
    print_jobs = relationship("PrintQueueJob", back_populates="submission")

    __table_args__ = (
        UniqueConstraint("section_id", name="uq_submission_section"),
    )


# ─── Exam Submission Version (full history) ──────────────────
class ExamSubmissionVersion(Base):
    __tablename__ = "exam_submission_versions"
    id            = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("exam_submissions.id"), nullable=False)
    version       = Column(Integer, nullable=False)
    snapshot      = Column(JSON, nullable=False)   # full dict of submission at that point
    changed_by    = Column(Integer, ForeignKey("users.id"))
    change_reason = Column(Text)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    submission = relationship("ExamSubmission", back_populates="versions")
    changer    = relationship("User", foreign_keys="[ExamSubmissionVersion.changed_by]")

    __table_args__ = (
        UniqueConstraint("submission_id", "version", name="uq_submission_version"),
        Index("ix_subver_submission", "submission_id"),
    )


# ─── Exam Access Token (time-limited, one-time-ish) ──────────
class TokenPurpose(str, enum.Enum):
    view      = "view"       # Edu-SQ / view only
    print     = "print"      # Printshop
    download  = "download"   # Teacher / Admin only

class ExamAccessToken(Base):
    __tablename__ = "exam_access_tokens"
    id            = Column(Integer, primary_key=True, index=True)
    token         = Column(String(64), unique=True, nullable=False, index=True)
    submission_id = Column(Integer, ForeignKey("exam_submissions.id"), nullable=False)
    issued_to     = Column(Integer, ForeignKey("users.id"), nullable=False)
    purpose       = Column(Enum(TokenPurpose), nullable=False)
    max_uses      = Column(Integer, default=1)   # printshop = 1, view = 5
    use_count     = Column(Integer, default=0)
    ip_hash       = Column(String(64))
    expires_at    = Column(DateTime(timezone=True), nullable=False)
    revoked       = Column(Boolean, default=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    submission    = relationship("ExamSubmission", back_populates="tokens")
    issued_user   = relationship("User", foreign_keys="[ExamAccessToken.issued_to]")
    access_logs   = relationship("ExamAccessLog", back_populates="token")


# ─── Exam Access Log (immutable — append-only) ───────────────
class ExamAccessLog(Base):
    __tablename__ = "exam_access_logs"
    id            = Column(Integer, primary_key=True, index=True)
    token_id      = Column(Integer, ForeignKey("exam_access_tokens.id"), nullable=False)
    user_id       = Column(Integer, ForeignKey("users.id"))
    action        = Column(String(50))   # "viewed", "printed", "downloaded", "denied"
    page_number   = Column(Integer)
    ip_hash       = Column(String(64))
    user_agent_hash = Column(String(64))
    watermark_text  = Column(String(200))   # บันทึก watermark ที่แสดง
    timestamp     = Column(DateTime(timezone=True), server_default=func.now())

    token = relationship("ExamAccessToken", back_populates="access_logs")

    __table_args__ = (
        Index("ix_examlog_token",     "token_id"),
        Index("ix_examlog_user",      "user_id"),
        Index("ix_examlog_timestamp", "timestamp"),
    )


# ─── Swap Request ─────────────────────────────────────────────
class PrintQueueJob(Base):
    __tablename__ = "print_queue_jobs"
    id            = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("exam_submissions.id"), nullable=False)
    created_by    = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to   = Column(Integer, ForeignKey("users.id"))
    status        = Column(Enum(PrintJobStatus), default=PrintJobStatus.queued, nullable=False)
    priority      = Column(String(20), default="standard", nullable=False)
    release_token = Column(String(64), unique=True)
    notes         = Column(Text)
    delivery_note = Column(Text)
    started_at    = Column(DateTime(timezone=True))
    completed_at  = Column(DateTime(timezone=True))
    dispatched_at = Column(DateTime(timezone=True))
    delivered_at  = Column(DateTime(timezone=True))
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

    submission    = relationship("ExamSubmission", back_populates="print_jobs")
    creator       = relationship("User", foreign_keys=[created_by])
    assignee      = relationship("User", foreign_keys=[assigned_to])

    __table_args__ = (
        UniqueConstraint("submission_id", name="uq_print_queue_submission"),
        Index("ix_print_queue_status", "status"),
    )


class SwapRequest(Base):
    __tablename__ = "swap_requests"
    id             = Column(Integer, primary_key=True, index=True)
    requester_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    requester_sup_id = Column(Integer, ForeignKey("supervisions.id"), nullable=False)
    target_sup_id  = Column(Integer, ForeignKey("supervisions.id"), nullable=False)
    message        = Column(Text)
    status         = Column(Enum(SwapStatus), default=SwapStatus.pending)
    responded_at   = Column(DateTime(timezone=True))
    reject_reason  = Column(Text)
    admin_override = Column(Boolean, default=False)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    requester      = relationship("User", foreign_keys="[SwapRequest.requester_id]")
    target         = relationship("User", foreign_keys="[SwapRequest.target_id]")
    requester_sup  = relationship("Supervision",
                                  foreign_keys="[SwapRequest.requester_sup_id]")
    target_sup     = relationship("Supervision",
                                  foreign_keys="[SwapRequest.target_sup_id]")


# ─── Checkin Event ────────────────────────────────────────────
class CheckinEvent(Base):
    __tablename__ = "checkin_events"
    id                = Column(Integer, primary_key=True, index=True)
    schedule_id       = Column(Integer, ForeignKey("exam_schedules.id"), nullable=False)
    user_id           = Column(Integer, ForeignKey("users.id"), nullable=False)
    checkin_type      = Column(Enum(CheckinType), nullable=False)
    checked_in_at     = Column(DateTime(timezone=True), server_default=func.now())

    # ที่ห้องสอบ
    students_present  = Column(Integer)
    late_count        = Column(Integer, default=0)
    absent_student_ids= Column(JSON)    # list[student_id]
    notes             = Column(Text)

    # Multi-party confirmation
    confirmed         = Column(Boolean, default=False)
    confirmed_by_all  = Column(Boolean, default=False)  # true เมื่อทุกคนกด confirm
    confirmations     = Column(JSON)    # {user_id: timestamp, ...}

    schedule = relationship("ExamSchedule")
    user     = relationship("User", foreign_keys="[CheckinEvent.user_id]")

    __table_args__ = (
        UniqueConstraint("schedule_id", "user_id", "checkin_type",
                         name="uq_checkin"),
        Index("ix_checkin_schedule", "schedule_id"),
    )


# ─── Teacher-Admin Message ────────────────────────────────────
class ExamMessage(Base):
    __tablename__ = "exam_messages"
    id            = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("exam_submissions.id"), nullable=False)
    sender_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    message       = Column(Text, nullable=False)
    is_read       = Column(Boolean, default=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    sender     = relationship("User", foreign_keys="[ExamMessage.sender_id]")
    __table_args__ = (Index("ix_msg_submission", "submission_id"),)



# ─── Supervision Baseline Stats (เก็บสถิติ original ก่อน swap) ──
class SupervisionBaseline(Base):
    """เก็บ snapshot ของ optimization ครั้งแรกที่ Admin confirm
       ใช้สำหรับสถิติระยะยาว ไม่เปลี่ยนแม้จะมี swap"""
    __tablename__ = "supervision_baselines"
    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    schedule_id  = Column(Integer, ForeignKey("exam_schedules.id"), nullable=False)
    slot_order   = Column(Integer, default=1)
    role_in_exam = Column(String(50), default="supervisor")
    confirmed_at = Column(DateTime(timezone=True), server_default=func.now())

    user     = relationship("User", foreign_keys=[user_id])
    schedule = relationship("ExamSchedule")

    __table_args__ = (
        UniqueConstraint("user_id", "schedule_id", name="uq_baseline"),
        Index("ix_baseline_user", "user_id"),
    )


# ─── Section Coordinator (4 คน ดูแลอาจารย์ตามสาขา) ──────────
class SectionCoordinator(Base):
    """4 staff ที่ดูแลอาจารย์ตามสาขา — เห็นข้อสอบอาจารย์ได้"""
    __tablename__ = "section_coordinators"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    department = Column(String(100))  # GOV / PA / IR / etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint("user_id", "department", name="uq_coordinator"),
    )


# ─── Printshop Access ──────────────────────────────────────────
class PrintshopUser(Base):
    """ร้านถ่ายเอกสาร — login ด้วย token แยก ไม่มี CMU account"""
    __tablename__ = "printshop_users"
    id         = Column(Integer, primary_key=True, index=True)
    shop_name  = Column(String(200))
    token_hash = Column(String(256), unique=True, nullable=False)  # bcrypt hash
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())






# ─── Room Unavailability (ก่อน optimize) ─────────────────────
class RoomUnavailability(Base):
    """
    Admin กำหนดว่าห้องนี้ไม่ว่างวัน/เวลาไหน
    optimizer จะ skip ห้องนี้ใน slot นั้น
    """
    __tablename__ = "room_unavailability"
    id            = Column(Integer, primary_key=True, index=True)
    room_id       = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    exam_period_id= Column(Integer, ForeignKey("exam_periods.id"), nullable=False)
    block_date    = Column(String(20), nullable=False)   # "2026-03-23"
    block_time    = Column(String(20), nullable=True)    # "09.00-12.00" | NULL=ทั้งวัน
    start_time    = Column(String(8), nullable=True)
    end_time      = Column(String(8), nullable=True)
    reason        = Column(String(300))
    created_by    = Column(Integer, ForeignKey("users.id"))
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    room          = relationship("Room")
    period        = relationship("ExamPeriod")

    __table_args__ = (
        UniqueConstraint("room_id", "exam_period_id", "block_date", "block_time",
                         name="uq_room_unavail"),
        Index("ix_room_unavail_period", "room_id", "exam_period_id"),
        Index("ix_room_unavail_date",   "block_date"),
    )



# ─── Section Exam Manager (ผู้รับผิดชอบสอบต่อ section) ───────
class SectionExamManager(Base):
    """
    กำหนดว่าใครเป็น "exam manager" ของ section นี้
    สำหรับกรณีอาจารย์สอนร่วม — ต้องตกลงกันก่อนว่าใครรับผิดชอบ
    มีต่อ (section, exam_type) เช่น midterm ใครรับ, final ใครรับ อาจต่างกันได้

    workflow:
      1. อาจารย์คนใดคนหนึ่งเสนอตัว (proposed_by)
      2. อาจารย์อีกคน confirm หรือ admin assign
    """
    __tablename__ = "section_exam_managers"
    id              = Column(Integer, primary_key=True, index=True)
    section_id      = Column(Integer, ForeignKey("sections.id"), nullable=False)
    exam_type       = Column(String(10), nullable=False)   # "midterm" | "final"
    manager_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    proposed_by     = Column(Integer, ForeignKey("users.id"), nullable=False)
    confirmed       = Column(Boolean, default=False)       # อีกฝ่าย confirm แล้ว
    confirmed_by    = Column(Integer, ForeignKey("users.id"), nullable=True)
    confirmed_at    = Column(DateTime(timezone=True), nullable=True)
    assignment_source = Column(String(20), default="manual", nullable=False)
    note            = Column(Text)                         # หมายเหตุการมอบหมาย
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    section      = relationship("Section")
    manager      = relationship("User", foreign_keys=[manager_id])
    proposer     = relationship("User", foreign_keys=[proposed_by])
    confirmer    = relationship("User", foreign_keys=[confirmed_by])

    __table_args__ = (
        UniqueConstraint("section_id", "exam_type", name="uq_exam_manager"),
        Index("ix_exam_manager_user", "manager_id"),
        Index("ix_exam_manager_section", "section_id"),
    )


# ─── Exam Material Request (สิ่งที่ต้องการเพิ่มเติม) ─────────
class ExamMaterialRequest(Base):
    """
    สิ่งที่อาจารย์ต้องการนอกจากกระดาษคำถาม
    กรอกได้ตั้งแต่ step 1 ก่อนมีวันสอบ
    ใช้ในการคำนวณ order ที่ร้านถ่าย/คลังพัสดุ
    """
    __tablename__ = "exam_material_requests"
    id              = Column(Integer, primary_key=True, index=True)
    submission_id   = Column(Integer, ForeignKey("exam_submissions.id"),
                             nullable=False, unique=True)

    # กระดาษเขียนตอบ (lined paper)
    answer_paper_sheets = Column(Integer, default=0)   # จำนวนแผ่น/คน
    answer_paper_staple = Column(Boolean, default=False)  # เย็บเป็นชุดไหม

    # สมุดคำตอบ (blue book / booklet)
    answer_booklet_count = Column(Integer, default=0)  # จำนวนเล่ม/คน

    # กระดาษ OMR (optical mark recognition)
    omr_sheet_count = Column(Integer, default=0)       # จำนวนชุด/คน
    omr_form_code   = Column(String(50))               # รหัสแบบฟอร์ม OMR ถ้ามี

    # กระดาษทด (scratch paper)
    scratch_paper_sheets = Column(Integer, default=0)  # จำนวนแผ่น/คน

    # หมายเหตุพิเศษสำหรับร้านถ่าย/ฝ่ายจัดสอบ
    special_note    = Column(Text)     # เช่น "ต้องการกระดาษ 100g", "แยกถุงตามห้อง"

    # สถานะ
    confirmed       = Column(Boolean, default=False)   # อาจารย์ยืนยันแล้ว
    confirmed_at    = Column(DateTime(timezone=True), nullable=True)

    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())

    submission      = relationship("ExamSubmission", back_populates="material_request")

# ─── Revoked Tokens (token blacklist) ────────────────────────
class RevokedToken(Base):
    """JWT blacklist — เก็บ hash ของ token ที่ถูก revoke (logout)
    cleanup ด้วย cron: DELETE WHERE created_at < now() - 13 hours"""
    __tablename__ = "revoked_tokens"
    id          = Column(Integer, primary_key=True, index=True)
    token_hash  = Column(String(64), unique=True, nullable=False, index=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_revoked_created", "created_at"),
    )

# ─── Staff Unavailability (ก่อน optimize) ────────────────────
class StaffUnavailability(Base):
    """
    Admin กำหนดว่า staff คนนี้ไม่ว่างวัน/เวลาไหน
    ก่อน optimize — optimizer จะ skip คนนี้ใน slot นั้น
    """
    __tablename__ = "staff_unavailability"
    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_period_id= Column(Integer, ForeignKey("exam_periods.id"), nullable=False)
    block_date    = Column(String(20), nullable=False)   # "2026-03-23"
    block_time    = Column(String(20), nullable=True)    # "09.00-12.00" | NULL=ทั้งวัน
    reason        = Column(String(300))
    created_by    = Column(Integer, ForeignKey("users.id"))
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    user          = relationship("User", foreign_keys=[user_id])
    period        = relationship("ExamPeriod")

    __table_args__ = (
        Index("ix_unavail_user_period", "user_id", "exam_period_id"),
        Index("ix_unavail_date", "block_date"),
    )


# ─── Optimize Session (workflow confirmation) ─────────────────
class OptimizeSession(Base):
    """
    ติดตาม state ของ optimization ใน 1 period
    status:
      draft      → optimize แล้ว รอ admin ตรวจ + manual adjust
      confirming → กำลังรอลายเซ็น 4 คน (Round 1)
      confirmed  → ครบ 4 คน → baseline stats ถูกบันทึก
      swap_open  → เปิด swap ได้
      swap_confirming → รอลายเซ็น 4 คน (Round 2)
      locked     → เสร็จสมบูรณ์
    """
    __tablename__ = "optimize_sessions"
    id             = Column(Integer, primary_key=True, index=True)
    exam_period_id = Column(Integer, ForeignKey("exam_periods.id"), nullable=False, unique=True)
    status         = Column(String(20), default="draft", nullable=False)
    # Round 1 signatures (ลำดับ: atikant → mathawee → napaporn → paweena)
    sig1_user_id   = Column(Integer, ForeignKey("users.id"), nullable=True)
    sig1_at        = Column(DateTime(timezone=True), nullable=True)
    sig2_user_id   = Column(Integer, ForeignKey("users.id"), nullable=True)
    sig2_at        = Column(DateTime(timezone=True), nullable=True)
    sig3_user_id   = Column(Integer, ForeignKey("users.id"), nullable=True)
    sig3_at        = Column(DateTime(timezone=True), nullable=True)
    sig4_user_id   = Column(Integer, ForeignKey("users.id"), nullable=True)
    sig4_at        = Column(DateTime(timezone=True), nullable=True)
    # Round 2 signatures (หลัง swap)
    sig1r2_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sig1r2_at      = Column(DateTime(timezone=True), nullable=True)
    sig2r2_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sig2r2_at      = Column(DateTime(timezone=True), nullable=True)
    sig3r2_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sig3r2_at      = Column(DateTime(timezone=True), nullable=True)
    sig4r2_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sig4r2_at      = Column(DateTime(timezone=True), nullable=True)
    # Edit lock — ป้องกัน admin สองคนแก้พร้อมกัน
    edit_lock_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    edit_lock_at      = Column(DateTime(timezone=True), nullable=True)
    # expire หลัง 5 นาทีไม่มีกิจกรรม (ตรวจใน backend)

    # meta
    baseline_saved = Column(Boolean, default=False)  # True = บันทึก stat แล้ว
    notes          = Column(Text)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())
    updated_at     = Column(DateTime(timezone=True), onupdate=func.now())

    period          = relationship("ExamPeriod")
    edit_lock_user  = relationship("User", foreign_keys=[edit_lock_user_id])
    sig1_user = relationship("User", foreign_keys=[sig1_user_id])
    sig2_user = relationship("User", foreign_keys=[sig2_user_id])
    sig3_user = relationship("User", foreign_keys=[sig3_user_id])
    sig4_user = relationship("User", foreign_keys=[sig4_user_id])

    __table_args__ = (
        Index("ix_optsess_period", "exam_period_id"),
        Index("ix_optsess_status", "status"),
    )


# ─── Co-Exam Group (วิชาที่สอบร่วมกัน) ───────────────────────
class CoExamGroup(Base):
    """
    กลุ่มวิชาที่สอบร่วมห้องเดียวกัน เพื่อลดจำนวนกรรมการ
    
    Case 1: วิชาเดียวกัน คนละตอน (126101 sec1+sec2+sec5)
    Case 2: ต่างวิชา อาจารย์คนเดียวกัน สอบพร้อมกัน
    
    ผลลัพธ์: optimizer จะ assign ห้องให้ sections ในกลุ่ม
    แบ่งตามความจุห้อง ลำดับนักศึกษาต่อเนื่องกัน
    กรรมการคุมสอบ = 1 ชุด (ไม่ duplicate)
    """
    __tablename__ = "co_exam_groups"
    id             = Column(Integer, primary_key=True, index=True)
    exam_period_id = Column(Integer, ForeignKey("exam_periods.id"), nullable=False)
    group_key      = Column(String(100), nullable=False)  # "126101_2568_2_final" หรือ custom
    label          = Column(String(300))                  # แสดงใน UI
    exam_date      = Column(String(20))                   # วันสอบ (ทุก section ในกลุ่มต้องตรงกัน)
    exam_time      = Column(String(20))                   # เวลาสอบ
    exam_type      = Column(String(20), default="final")
    total_students = Column(Integer, default=0)           # คำนวณอัตโนมัติ
    created_by     = Column(Integer, ForeignKey("users.id"))
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    period   = relationship("ExamPeriod")
    members  = relationship("CoExamMember", back_populates="group",
                            cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("exam_period_id", "group_key", name="uq_co_exam_group"),
        Index("ix_co_exam_period", "exam_period_id"),
    )



class CoExamMember(Base):
    """Section ที่อยู่ใน Co-Exam Group"""
    __tablename__ = "co_exam_members"
    id         = Column(Integer, primary_key=True, index=True)
    group_id   = Column(Integer, ForeignKey("co_exam_groups.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group   = relationship("CoExamGroup", back_populates="members")
    section = relationship("Section")

    __table_args__ = (
        UniqueConstraint("group_id", "section_id", name="uq_co_exam_member"),
        Index("ix_co_member_section", "section_id"),
    )

# ─── External Exam (สอบภาษาอังกฤษกลาง มช. / สอบพิเศษ) ────────
class ExternalExam(Base):
    """
    การสอบที่มาจากภายนอกคณะ เช่น สอบภาษาอังกฤษกลาง มช.
    ไม่มี section / course ในระบบ — Admin กรอกข้อมูลเอง
    """
    __tablename__ = "external_exams"
    id            = Column(Integer, primary_key=True, index=True)
    exam_period_id= Column(Integer, ForeignKey("exam_periods.id"), nullable=False)
    title         = Column(String(300), nullable=False)   # "สอบ CMU-eTEGS ภาษาอังกฤษ"
    organizer     = Column(String(200))                   # "สำนักทะเบียนและประมวลผล มช."
    exam_date     = Column(String(20), nullable=False)    # "2026-03-15"
    exam_time     = Column(String(20), nullable=False)    # "09.00-12.00"
    room_name     = Column(String(200))                   # "PSB 1101, PSB 1204"
    num_students  = Column(Integer, default=0)
    invigilators_needed = Column(Integer, default=1)      # จำนวนกรรมการที่ต้องการ
    notes         = Column(Text)
    status        = Column(String(20), default="draft")   # draft | confirmed | done
    created_by    = Column(Integer, ForeignKey("users.id"))
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

    period        = relationship("ExamPeriod")
    supervisions  = relationship("ExternalSupervision", back_populates="external_exam",
                                 cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_external_period", "exam_period_id"),
        Index("ix_external_date",   "exam_date"),
    )


class ExternalSupervision(Base):
    """กรรมการคุมสอบ External Exam"""
    __tablename__ = "external_supervisions"
    id               = Column(Integer, primary_key=True, index=True)
    external_exam_id = Column(Integer, ForeignKey("external_exams.id"), nullable=False)
    user_id          = Column(Integer, ForeignKey("users.id"), nullable=False)
    slot_order       = Column(Integer, default=1)
    compensation     = Column(Numeric(10, 2), default=0.00)  # ใช้ Numeric ป้องกัน float error
    confirmed        = Column(Boolean, default=False)
    assigned_by      = Column(String(20), default="auto")  # "auto" | "manual"
    created_at       = Column(DateTime(timezone=True), server_default=func.now())

    external_exam = relationship("ExternalExam", back_populates="supervisions")
    user          = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint("external_exam_id", "user_id", name="uq_ext_supervision"),
        Index("ix_ext_sup_user", "user_id"),
    )

# ─── Exam Period (รอบสอบ) ────────────────────────────────────
class ExamPeriod(Base):
    """
    แต่ละรอบสอบ — 1 ปีมีได้ 4-5 รอบ
    (midterm 1, final 1, midterm 2, final 2, summer)
    is_active=True = รอบที่กำลังใช้งานอยู่ (มีได้แค่ 1)
    """
    __tablename__ = "exam_periods"
    id            = Column(Integer, primary_key=True, index=True)
    academic_year = Column(String(10), nullable=False)   # "2568"
    semester      = Column(String(10), nullable=False)   # "1" | "2" | "summer"
    exam_type     = Column(String(20), nullable=False)   # "midterm" | "final"
    label         = Column(String(100))                  # "ปลายภาค 2/2568"
    is_active     = Column(Boolean, default=False, nullable=False)
    lifecycle_status = Column(String(20), default="draft", nullable=False)
    archived_at   = Column(DateTime(timezone=True))
    locked_at     = Column(DateTime(timezone=True))
    created_by    = Column(Integer, ForeignKey("users.id"))
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("academic_year", "semester", "exam_type",
                         name="uq_exam_period"),
        Index("ix_period_active", "is_active"),
    )

# ─── Import Session ────────────────────────────────────────────
class ImportSession(Base):
    """
    ติดตามการ import แต่ละครั้ง
    key: (academic_year, semester, exam_type) — unique per exam period
    """
    __tablename__ = "import_sessions"
    id               = Column(Integer, primary_key=True, index=True)
    academic_year    = Column(String(10), nullable=False)   # เช่น "2568"
    semester         = Column(String(5),  nullable=False)   # "1" หรือ "2"
    exam_type        = Column(String(20), nullable=False)   # "midterm" | "final"
    opencourse_rows  = Column(Integer, default=0)           # rows จาก opencourse
    enrollment_rows  = Column(Integer, default=0)           # rows จาก Book1
    created_by       = Column(Integer, ForeignKey("users.id"))
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    last_updated     = Column(DateTime(timezone=True), onupdate=func.now())

    enrollments = relationship("EnrollmentRecord", back_populates="session")
    row_logs = relationship("ImportRowLog", back_populates="session",
                            cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("academic_year", "semester", "exam_type",
                         name="uq_import_session"),
    )


# ─── Enrollment Record ─────────────────────────────────────────
class EnrollmentRecord(Base):
    """รายชื่อนักศึกษาที่ลงทะเบียนแต่ละวิชา (จาก Book1.xls)"""
    __tablename__ = "enrollment_records"
    id                = Column(Integer, primary_key=True, index=True)
    import_session_id = Column(Integer, ForeignKey("import_sessions.id"), nullable=False)
    section_id        = Column(Integer, ForeignKey("sections.id"),        nullable=False)
    student_id        = Column(String(20), nullable=False, index=True)   # รหัสนักศึกษา
    student_name      = Column(String(300))
    major             = Column(String(300))
    faculty_name      = Column(String(300))
    type_regist       = Column(String(5))    # K, P, I, S, ...

    session = relationship("ImportSession", back_populates="enrollments")
    section = relationship("Section")

    __table_args__ = (
        Index("ix_enroll_session_section", "import_session_id", "section_id"),
    )


# ══════════════════════════════════════════════════════════════
# SQLAlchemy Events — ต้องอยู่หลัง class definitions ทั้งหมด
# ══════════════════════════════════════════════════════════════

class ImportRowLog(Base):
    __tablename__ = "import_row_logs"
    id              = Column(Integer, primary_key=True, index=True)
    session_id      = Column(Integer, ForeignKey("import_sessions.id"), nullable=False)
    row_number      = Column(Integer, nullable=False)
    raw_data        = Column(JSON, nullable=False)
    status          = Column(String(20), nullable=False)
    error_code      = Column(String(20))
    error_message   = Column(Text)
    was_selected    = Column(Boolean)
    was_imported    = Column(Boolean)
    override_reason = Column(Text)
    override_by     = Column(Integer, ForeignKey("users.id"))
    override_at     = Column(DateTime(timezone=True))
    # room_capacity audit fields — null for all other import types
    change_type       = Column(String(20))   # "create" | "update" | "skip" | "blocked"
    previous_capacity = Column(Integer)
    new_capacity      = Column(Integer)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ImportSession", back_populates="row_logs")
    override_user = relationship("User", foreign_keys=[override_by])

    __table_args__ = (
        Index("idx_import_row_logs_session", "session_id"),
    )


class LecturerNameMap(Base):
    __tablename__ = "lecturer_name_map"
    id           = Column(Integer, primary_key=True, index=True)
    raw_name     = Column(String(300), unique=True, nullable=False)
    teacher_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    confirmed_by = Column(Integer, ForeignKey("users.id"))
    confirmed_at = Column(DateTime(timezone=True))

    teacher = relationship("User", foreign_keys=[teacher_id])
    confirmer = relationship("User", foreign_keys=[confirmed_by])


@event.listens_for(CoExamMember, "after_insert")
@event.listens_for(CoExamMember, "after_delete")
def _recalc_co_exam_total(mapper, connection, target):
    """Auto-recalculate CoExamGroup.total_students เมื่อ add/remove member"""
    connection.execute(
        CoExamGroup.__table__.update()
        .where(CoExamGroup.__table__.c.id == target.group_id)
        .values(total_students=(
            select(func.coalesce(func.sum(Section.__table__.c.num_students), 0))
            .select_from(
                CoExamMember.__table__.join(
                    Section.__table__,
                    CoExamMember.__table__.c.section_id == Section.__table__.c.id
                )
            )
            .where(CoExamMember.__table__.c.group_id == target.group_id)
            .scalar_subquery()
        ))
    )
