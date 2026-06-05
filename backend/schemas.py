"""
Schemas — Pydantic v2 request/response models
"""
from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, List, Any, Dict, Literal
from datetime import datetime, date
from decimal import Decimal
from models import UserRole, ExamType, QuestionType, ScheduleStatus


# ─── Auth ─────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str
    selected_role: str

    @model_validator(mode="before")
    @classmethod
    def _normalize_selected_role(cls, value: Any):
        # Backward-compat: legacy clients may send `role` instead of `selected_role`.
        if isinstance(value, dict):
            selected_role = value.get("selected_role")
            if selected_role in (None, "") and value.get("role") not in (None, ""):
                value = {**value, "selected_role": value.get("role")}
        return value

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
    active_role: UserRole
    view_as_role: Optional[UserRole]
    effective_role: UserRole   # role หลังจาก impersonate
    available_roles: List[UserRole] = []

    class Config:
        from_attributes = True


# ─── Users ────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.staff
    full_name: Optional[str] = None
    department: Optional[str] = None
    is_active: bool = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    department: Optional[str]
    dept_code: Optional[str] = None
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
    academic_group: Optional[str] = None
    academic_group_label: Optional[str] = None

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
    academic_group: Optional[str] = None
    academic_group_label: Optional[str] = None
    course: Optional[CourseOut]
    teacher: Optional[UserOut]
    teaching_room: Optional["RoomOut"] = None
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


class RoomUpdate(BaseModel):
    room_name: Optional[str] = None
    building: Optional[str] = None
    capacity: Optional[int] = None
    e_room_code: Optional[str] = None
    is_active: Optional[bool] = None


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
    paper_distribution_assigned: int = 0
    paper_distribution_slots: int = 0
    paper_distribution_unfilled: int = 0
    paper_distribution_warnings: List[str] = []
    esq_staff_excluded: List[dict] = []
    esq_in_stat: List[dict] = []
    room_keepers_assigned: List[dict] = []
    reminder: Optional[str] = None
    native_trace_summary: Dict[str, Any] = {}
    native_trace_events: List[Dict[str, Any]] = []
    traceability_completeness_score: float = 0.0
    trace_source_breakdown: Dict[str, int] = {}


# ─── Questions (M1) ───────────────────────────────────────────
class ImportColumnWarning(BaseModel):
    original: str
    rename_to: str
    reason: str


class ImportPreviewResponse(BaseModel):
    import_type: str
    file_name: str
    file_format: str
    encoding: str
    total_rows: int
    columns_detected: List[str] = []
    column_warnings: List[ImportColumnWarning] = []
    preview_rows: List[Dict[str, Any]] = []


class ImportSuggestedTeacherMatch(BaseModel):
    teacher_id: int
    full_name: str
    cmu_mail: str
    department: Optional[str] = None


class ImportTermContext(BaseModel):
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    exam_type: Optional[str] = None


class ImportIssueSummaryItem(BaseModel):
    code: str
    message: str
    count: int


class ImportValidationRow(BaseModel):
    row_number: int = Field(alias="_row")
    status: str
    errors: List[str] = []
    warnings: List[str] = []
    error_codes: List[str] = []
    warning_codes: List[str] = []
    can_override: bool = False
    override_policy: Literal["allowed", "disallowed", "requires_mapping"] = "allowed"
    selected: bool = False
    override_required: bool = False
    override_reason: Optional[str] = None
    historical_mode: bool = False
    import_term_context: ImportTermContext = ImportTermContext()
    data: Dict[str, Any] = {}

    model_config = {"populate_by_name": True}


class ImportValidationResponse(BaseModel):
    total_rows: int
    valid_count: int
    warning_count: int
    error_count: int
    error_summary: List[ImportIssueSummaryItem] = []
    warning_summary: List[ImportIssueSummaryItem] = []
    rows: List[ImportValidationRow] = []
    lecturer_unresolved: List[ImportUnresolvedLecturer] = []
    conflict_map: List[ImportConflictItem] = []


class ImportOverrideRequestItem(BaseModel):
    row: int
    reason: str


class ImportSessionPlan(BaseModel):
    import_type: str
    academic_year: str
    semester: str
    exam_type: Optional[str] = None
    historical_mode: bool = True
    source_filename: Optional[str] = None
    confirmed_by: int
    dry_run: bool = True


class ImportConfirmRequest(BaseModel):
    file_token: str
    import_type: Literal["opencourse", "personnel", "employee", "enrollment", "room_capacity"]
    academic_year: str
    semester: str
    exam_type: Optional[str] = None
    selected_rows: List[int] = []
    overrides: List[ImportOverrideRequestItem] = []
    confirmed_by: int
    dry_run: bool = True


class ImportConfirmResponse(BaseModel):
    total_rows: int
    selected_count: int
    blocked_count: int
    override_count: int
    importable_count: int
    non_importable_count: int
    blocking_reasons: List[ImportIssueSummaryItem] = []
    ready_for_execution: bool
    session_plan: Optional[ImportSessionPlan] = None


class ImportExecuteResponse(BaseModel):
    success: bool
    total_rows: int
    imported_count: int
    skipped_count: int
    override_count: int
    import_session_id: int
    summary: Dict[str, Any] = {}


class ImportRetentionPlainLanguage(BaseModel):
    exam_file_retention_summary: str
    archive_summary: str
    destruction_summary: str
    historical_visibility_summary: str


class ImportRetentionPolicyResponse(BaseModel):
    exam_file_retention_mode: Literal["semester_end", "academic_year_end", "years", "manual"]
    exam_file_retention_years: Optional[int] = None
    exam_file_destroy_requires_approval: bool
    exam_file_archive_before_destroy: bool
    retain_import_audit_logs_years: Optional[int] = None
    retain_import_raw_files: bool
    parsed_snapshot_storage: str
    historical_term_data_retained_indefinitely: bool
    plain_language: ImportRetentionPlainLanguage


class ImportRetentionPolicyUpdateRequest(BaseModel):
    exam_file_retention_mode: Literal["semester_end", "academic_year_end", "years", "manual"]
    exam_file_retention_years: Optional[int] = None
    exam_file_destroy_requires_approval: bool
    exam_file_archive_before_destroy: bool
    retain_import_audit_logs_years: int = Field(default=7)
    retain_import_raw_files: bool
    historical_term_data_retained_indefinitely: bool = True


class TermLifecyclePreviewItem(BaseModel):
    id: int
    academic_year: str
    semester: str
    exam_type: str
    label: Optional[str] = None
    is_active: bool
    lifecycle_status: Literal["draft", "active", "archived", "locked"]
    is_historical: bool
    is_editable: bool
    is_read_only: bool
    status_summary: str
    preview_summary: str
    archived_at: Optional[str] = None
    locked_at: Optional[str] = None
    created_at: Optional[str] = None


class TermSettingsPreviewResponse(BaseModel):
    current_active_term: Optional[TermLifecyclePreviewItem] = None
    latest_term: Optional[TermLifecyclePreviewItem] = None
    latest_historical_term: Optional[TermLifecyclePreviewItem] = None
    selected_term: Optional[TermLifecyclePreviewItem] = None
    available_terms: List[TermLifecyclePreviewItem] = []
    default_preview_term_id: Optional[int] = None
    selected_term_status: Optional[Literal["draft", "active", "archived", "locked"]] = None
    selected_term_editable: bool
    selected_term_read_only: bool
    plain_language_summary: str
    historical_visibility_summary: str


class PeriodCloseResponse(BaseModel):
    success: bool
    period_id: int
    previous_lifecycle_status: Optional[Literal["draft", "active", "archived", "locked"]] = None
    new_lifecycle_status: Optional[Literal["draft", "active", "archived", "locked"]] = None
    locked_at: Optional[str] = None
    plain_language_summary: str
    blocking_reasons: List[str] = []


# Questions (M1)
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


# ─── Dashboard Intelligence (OPS-DASH) ─────────────────────────

class AdminIntelligenceDashboard(BaseModel):
    role: str
    overall_health_score: Optional[float] = None
    overall_risk_band: Optional[str] = None
    last_computed_at: Optional[str] = None
    groups: list[dict]                          # list[DashboardMetricGroup] as plain dict
    model_config = {"arbitrary_types_allowed": True}


class ExecutiveDashboardSummary(BaseModel):
    overall_health_score: float
    risk_band: str
    optimization_quality_avg: float
    governance_blocker_count: int
    publication_ready_count: int
    workload_balance_score: float
    room_utilization_score: float
    pdpa_alert_count: int
    top_risks: List[dict[str, str]] = []
    recommended_actions: List[dict[str, str]] = []


class RoleDashboardPayload(BaseModel):
    role: str
    role_label_i18n_key: str
    summary: dict          # DashboardRoleSummary as plain dict
    groups: list[dict]     # list[DashboardMetricGroup] as plain dict
    unauthorized: bool


class WorkloadDutyAnalyticsFilters(BaseModel):
    semester: Optional[str] = None
    academic_year: Optional[str] = None
    period_id: Optional[int] = None
    exam_type: Optional[str] = None
    role_group: str = "all"
    person_id: Optional[str] = None
    duty_type: str = "all"


class WorkloadDutyAnalyticsPerson(BaseModel):
    person_id: str
    display_name: str
    role_group: str
    invigilation_count: int
    distribution_count: int
    combined_count: int


class WorkloadDutyAnalyticsDailyPoint(BaseModel):
    date: str
    invigilation_count: int
    distribution_count: int
    combined_count: int
    cumulative_invigilation: int
    cumulative_distribution: int
    cumulative_combined: int


class WorkloadDutyAnalyticsTimeSlotPoint(BaseModel):
    time_slot: str
    invigilation_count: int
    distribution_count: int
    combined_count: int


class WorkloadDutyAnalyticsSummary(BaseModel):
    total_people: int
    total_invigilation_duties: int
    total_distribution_duties: int
    total_combined_duties: int
    average_duties_per_person: float
    max_duties: int
    imbalance_score: float


class WorkloadDutyAnalyticsFairness(BaseModel):
    imbalance_score: float
    overloaded_people: list[WorkloadDutyAnalyticsPerson] = []
    underloaded_people: list[WorkloadDutyAnalyticsPerson] = []
    risk_band: str


class WorkloadDutyAnalyticsPayload(BaseModel):
    filters: WorkloadDutyAnalyticsFilters
    summary: WorkloadDutyAnalyticsSummary
    by_person: list[WorkloadDutyAnalyticsPerson]
    daily_series: list[WorkloadDutyAnalyticsDailyPoint]
    time_slot_series: list[WorkloadDutyAnalyticsTimeSlotPoint]
    fairness: WorkloadDutyAnalyticsFairness


class AdvanceInvigilationBatchPreviewSummary(BaseModel):
    preview_only: bool
    amount_calculation: str
    amount_calculation_enabled: bool = False
    amount_status: str
    preview_amount_enabled: bool = False
    preview_total_amount: Decimal = Decimal("0")
    preview_weekday_count: int = 0
    preview_weekend_count: int = 0
    total_rows: int
    total_assignments: int
    ready_for_batch_review: int
    included_in_advance_batch: int = 0
    blocked_missing_assignment_data: int = 0
    blocked_duplicate_duty: int = 0
    blocked_rule_gap: int = 0
    blocked_rows: int
    pending_rate_rule_count: int
    missing_exam_date_count: int = 0
    invalid_exam_date_count: int = 0
    blocked_roster_amount_count: int = 0
    warning_count: int
    payment_authorization_enabled: bool = False
    final_export_enabled: bool = False


class AdvanceInvigilationBatchRosterRow(BaseModel):
    advance_batch_id: Optional[str] = None
    batch_period: Optional[str] = None
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    exam_period: Optional[str] = None
    batch_status: str
    prepared_by: Optional[str] = None
    prepared_at: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    duty_id: Optional[int] = None
    exam_id: Optional[int] = None
    schedule_id: Optional[int] = None
    course_code: Optional[str] = None
    course_title: Optional[str] = None
    section: Optional[str] = None
    exam_date: Optional[str] = None
    exam_date_calendar: Optional[str] = None
    normalized_exam_date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room_id: Optional[int] = None
    room_name: Optional[str] = None
    person_id: Optional[str] = None
    person_name: Optional[str] = None
    person_type: Optional[str] = None
    department: Optional[str] = None
    duty_role: str
    advance_inclusion_status: str
    inclusion_reason: Optional[str] = None
    blocked_reason: Optional[str] = None
    rate_rule_status: str
    amount_status: str
    amount_preview: Optional[Decimal] = None
    rate_day_type: str = "UNKNOWN"
    rate_source: Optional[str] = None
    payment_authorization_status: str = "NOT_AUTHORIZED_PREVIEW_ONLY"
    reconciliation_status: str
    post_duty_evidence_status: str
    absence_explanation_status: str
    refund_offset_status: str
    source_record_ref: str
    audit_note: str
    warnings: list[str] = Field(default_factory=list)


class AdvanceInvigilationBatchPreviewResponse(BaseModel):
    summary: AdvanceInvigilationBatchPreviewSummary
    roster_rows: list[AdvanceInvigilationBatchRosterRow]
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    rule_gaps: list[str] = Field(default_factory=list)


class OfficialPaymentDocumentDraftManualPaperRow(BaseModel):
    exam_date: str
    exam_time: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    committee_count: int = Field(ge=0)
    notes: Optional[str] = None


class OfficialPaymentDocumentDraftRequest(BaseModel):
    period_id: Optional[int] = None
    academic_year: Optional[str] = "2568"
    semester: Optional[str] = "2"
    exam_type: Optional[str] = "final"
    paper_distribution_rows: list[OfficialPaymentDocumentDraftManualPaperRow] = Field(default_factory=list)


class OfficialPaymentDocumentDraftMetadata(BaseModel):
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    exam_type: Optional[str] = None
    term_label: str
    document_status: str = "DRAFT_NOT_AUTHORIZED"
    rate_source: str
    weekday_rate: Decimal
    weekend_rate: Decimal
    rate_scope: str
    paper_distribution_source_status: str


class OfficialPaymentDocumentDraftRow(BaseModel):
    exam_date: str
    normalized_exam_date: Optional[str] = None
    time_slot: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    day_type: str
    rate_amount: Decimal
    invigilation_committee_count: int = 0
    invigilation_compensation_amount: Decimal = Decimal("0")
    paper_distribution_committee_count: int = 0
    paper_distribution_compensation_amount: Decimal = Decimal("0")
    total_compensation_amount: Decimal = Decimal("0")
    source_notes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class OfficialPaymentDocumentDraftTotals(BaseModel):
    invigilation_committee_count: int = 0
    invigilation_compensation_amount: Decimal = Decimal("0")
    paper_distribution_committee_count: int = 0
    paper_distribution_compensation_amount: Decimal = Decimal("0")
    grand_total_amount: Decimal = Decimal("0")
    row_count: int = 0


class OfficialPaymentDocumentDraftResponse(BaseModel):
    metadata: OfficialPaymentDocumentDraftMetadata
    rows: list[OfficialPaymentDocumentDraftRow]
    totals: OfficialPaymentDocumentDraftTotals
    warnings: list[str] = Field(default_factory=list)
    draft_only: bool = True
    payment_authorization_enabled: bool = False
    final_export_enabled: bool = False
    supervisor_finance_review_required: bool = True


class InvigilationRateRuleCreate(BaseModel):
    rate_name: str
    payment_unit: str = "PER_SESSION"
    rate_amount: Optional[Decimal] = None
    currency: str = "THB"
    role_scope: str = "ALL"
    person_type_scope: str = "ALL"
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    note: Optional[str] = None


class InvigilationRateRuleUpdate(BaseModel):
    rate_name: Optional[str] = None
    payment_unit: Optional[str] = None
    rate_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    role_scope: Optional[str] = None
    person_type_scope: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    note: Optional[str] = None


class InvigilationRateRuleOut(BaseModel):
    rate_rule_id: int
    rate_name: str
    payment_unit: str
    rate_amount: Decimal
    currency: str
    role_scope: str
    person_type_scope: str
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    status: str
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    activated_by: Optional[int] = None
    activated_at: Optional[datetime] = None
    archived_by: Optional[int] = None
    archived_at: Optional[datetime] = None
    note: Optional[str] = None
    preview_only: bool = True
    payment_authorization_enabled: bool = False
    final_export_enabled: bool = False


class InvigilationRateRuleListResponse(BaseModel):
    rate_rules: list[InvigilationRateRuleOut]
    preview_only: bool = True
    payment_authorization_enabled: bool = False
    final_export_enabled: bool = False


class InvigilationRateRuleMutationResponse(BaseModel):
    rate_rule: InvigilationRateRuleOut
    preview_only: bool = True
    payment_authorization_enabled: bool = False
    final_export_enabled: bool = False


class InvigilationSimpleRateUpdate(BaseModel):
    weekday_amount: Decimal
    weekend_amount: Decimal


class InvigilationSimpleRateOut(BaseModel):
    day_scope: str
    amount: Optional[Decimal] = None
    amount_status: str
    rate_rule_id: Optional[int] = None
    saved_at: Optional[datetime] = None


class InvigilationSimpleRatesResponse(BaseModel):
    currency: str = "THB"
    payment_unit: str = "PER_SESSION"
    configuration_status: str
    weekday_rate: InvigilationSimpleRateOut
    weekend_rate: InvigilationSimpleRateOut
    preview_only: bool = True
    payment_authorization_enabled: bool = False
    final_export_enabled: bool = False



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
