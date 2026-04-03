"""
Schemas — Pydantic v2 request/response models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime, date
from models import UserRole, ExamType, QuestionType, ScheduleStatus


# ─── Auth ─────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserMe"

class UserMe(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    view_as_role: Optional[UserRole]
    effective_role: UserRole   # role หลังจาก impersonate

    class Config:
        from_attributes = True


# ─── Users ────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole = UserRole.staff
    full_name: Optional[str] = None
    department: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    department: Optional[str]
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class ViewAsRequest(BaseModel):
    role: Optional[UserRole] = None   # None = reset to own role


# ─── Courses ──────────────────────────────────────────────────
class CourseOut(BaseModel):
    id: int
    course_id: str
    course_name_th: Optional[str]
    course_name_en: Optional[str]
    credits: int
    department: Optional[str]

    class Config:
        from_attributes = True

class SectionCreate(BaseModel):
    course_id: int
    section_no: str
    teacher_id: Optional[int] = None
    num_students: int = 0
    is_co_exam: bool = False
    co_group_id: Optional[str] = None
    semester: str = "2"
    academic_year: str = "2568"

class SectionUpdate(BaseModel):
    teacher_id: Optional[int] = None
    num_students: Optional[int] = None
    is_co_exam: Optional[bool] = None
    co_group_id: Optional[str] = None

class SectionOut(BaseModel):
    id: int
    section_no: str
    num_students: int
    is_co_exam: bool
    co_group_id: Optional[str]
    semester: str
    academic_year: str
    course: Optional[CourseOut]
    teacher: Optional[UserOut]
    schedules: List["ScheduleOut"] = []  # midterm + final
    # helper: schedule = schedules[0] if schedules else None

    class Config:
        from_attributes = True


# ─── Rooms ────────────────────────────────────────────────────
class RoomOut(BaseModel):
    id: int
    room_name: str
    building: Optional[str]
    capacity: int
    e_room_code: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class RoomCreate(BaseModel):
    room_name: str
    building: Optional[str] = None
    capacity: int = 30
    e_room_code: Optional[str] = None


# ─── Schedule ─────────────────────────────────────────────────
class ScheduleCreate(BaseModel):
    section_id: int
    room_id: int
    exam_date: str
    exam_time: str
    exam_type: ExamType = ExamType.final
    num_pages: int = 1
    paper_distributor: Optional[str] = None
    notes: Optional[str] = None

class ScheduleUpdate(BaseModel):
    room_id: Optional[int] = None
    exam_date: Optional[str] = None
    exam_time: Optional[str] = None
    num_pages: Optional[int] = None
    paper_distributor: Optional[str] = None
    status: Optional[ScheduleStatus] = None
    notes: Optional[str] = None

class SupervisionOut(BaseModel):
    id: int
    user: Optional[UserOut]
    role_in_exam: str
    slot_order: int
    compensation: float
    confirmed: bool
    is_swapped: bool = False
    is_emergency_sub: bool = False
    swap_requested: bool = False

    class Config:
        from_attributes = True

class ScheduleOut(BaseModel):
    id: int
    exam_date: date
    exam_time: str
    exam_type: ExamType
    status: ScheduleStatus
    num_pages: int
    total_sheets: int
    paper_distributor: Optional[str]
    notes: Optional[str]
    room: Optional[RoomOut]
    supervisions: List[SupervisionOut] = []

    class Config:
        from_attributes = True

class ScheduleWithSection(ScheduleOut):
    section: Optional[SectionOut] = None

    class Config:
        from_attributes = True

# ── Optimizer Input ───────────────────────────────────────────
class OptimizerRequest(BaseModel):
    semester: str = "2"
    academic_year: str = "2568"
    exam_type: ExamType = ExamType.final

class OptimizerResult(BaseModel):
    success: bool
    sections_assigned: int
    sections_total: int
    fairness_score: float
    violations: List[str] = []
    details: List[dict] = []


# ─── Questions (M1) ───────────────────────────────────────────
class OptionSchema(BaseModel):
    label: str
    text: str

class QuestionCreate(BaseModel):
    section_id: int
    q_type: QuestionType
    q_number: Optional[int] = None
    q_text: str
    points: float = 1.0
    answer_lines: int = 5
    options: Optional[List[OptionSchema]] = None
    correct_option: Optional[str] = None

class QuestionOut(BaseModel):
    id: int
    q_type: QuestionType
    q_number: Optional[int]
    q_text: str
    points: float
    answer_lines: int
    options: Optional[Any]
    correct_option: Optional[str]
    image_path: Optional[str]
    page_number: int

    class Config:
        from_attributes = True


# ─── Dashboard ────────────────────────────────────────────────
class DashboardStats(BaseModel):
    total_sections: int
    total_students: int
    total_sheets: int
    total_teachers: int
    scheduled_sections: int
    unscheduled_sections: int
    rooms_in_use: int
    copy_cost: float
    recent_logs: List[dict] = []


# ─── Audit ────────────────────────────────────────────────────
class AuditOut(BaseModel):
    id: int
    action: str
    table_name: Optional[str]
    record_id: Optional[int]
    timestamp: datetime
    actor: Optional[UserOut]

    class Config:
        from_attributes = True


SectionOut.model_rebuild()
