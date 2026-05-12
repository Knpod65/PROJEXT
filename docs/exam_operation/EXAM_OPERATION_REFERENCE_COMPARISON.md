# Exam Operation Reference Comparison
## EMS vs CMU Faculty of Humanities Operational Manual (Pages 1–47)

**Date:** 2026-05-12  
**Reference:** Chapter 4 — เทคนิคการปฏิบัติงาน (Operational Techniques)  
**EMS State:** Phase 3 architecture renovation in progress (readiness 75/100)  
**Scope:** Pages 1–47 only. Pages 48–54 explicitly excluded.

---

## 1. Document Structure Summary

The reference document describes a **20-step manual exam scheduling process** used by CMU Faculty of Humanities' academic services unit. It covers:

- Monthly operation calendar across 3 semesters (Semester 1, 2, Summer)
- 20 discrete operational steps from schedule drafting through post-exam summary
- Data flows between CMU REG system, Excel files, e-humanities online system, and paper documents
- Invigilator assignment rules, co-supervisor formulas, room booking procedures
- Document generation: exam orders, OMR covers, attendance sheets, room notices

---

## 2. Architecture Level Comparison

| Dimension | Reference Manual | EMS Current State |
|-----------|-----------------|-------------------|
| **Primary data store** | REG system (external) + Excel files | PostgreSQL/SQLite via SQLAlchemy |
| **Workflow medium** | Paper circulation + email + phone | API-driven, role-gated, audited |
| **Scheduling logic** | Manual room/supervisor assignment | CP-SAT optimizer (OR-Tools) |
| **Import** | CSV from REG → manual XLS rename | Import V2: preview → validate → confirm |
| **Invigilator assignment** | Manual Excel counting + paper lists | Optimization engine + workload tracking |
| **Document generation** | System printout + paper attachment | gen_docs.py + operational_documents.py (PDF/DOCX) |
| **Audit trail** | None / paper records | Full audit_service.py + ImportRowLog |
| **Student data handling** | Uncontrolled Excel sheets | PDPA policy, role-gated exports |
| **QR / Check-in** | Not present in manual | checkins.py + exam_pickup.py with token system |
| **Term lifecycle** | Implicit (semester calendar) | Explicit: draft→active→archived→locked |
| **Access control** | Shared system login | JWT + role-based permissions.py |
| **Search** | Public web search at human.cmu.ac.th | Internal role-gated search only |

---

## 3. Step-by-Step Reference Process Mapping

### Step 1: Setting Central Exam Schedule (กำหนดตารางสอบกลาง/ปลายภาค)

**Reference process:**
- Midterm: set 3 weeks after semester open, reference CMU university-wide announcement
- Final: derived from class schedule using pattern table (MTh 0800 → TUE MAR 18, 1200-1500, etc.)
- Special Examination (ตารางสอบพิเศษ): for multi-section courses with different time slots
- Regular Examination (ตารางสอบปกติ): single time slot per class pattern
- Faculty checks and updates department courses with special exceptions

**EMS mapping:**
- Period management exists (`period.py`, `Period` model)
- No class-time → exam-time mapping table
- No Special/Regular exam type policy engine
- No university announcement import integration

**Classification:** `LEGACY_PROCESS_STILL_VALUABLE` — the scheduling rule table is a configurable policy that EMS optimizer should consume.

---

### Step 2: Data Preparation (การเตรียมข้อมูล)

**Reference process:**
- Download 3 files from REG system: (1) all open courses, (2) lecturer list, (3) enrolled students
- English Language department: Excel files with section-by-section breakdown
- Manual CSV → XLS rename (because REG exports CSV, system needs XLS)
- Student count updated after 3 weeks of semester start
- Data verification and cleanup before import

**EMS mapping:**
- Import V2 pipeline: `import_v2/{parsers, validators, normalizers, importer}.py`
- Supports preview-first, row-level selection, override with reason
- `ImportRowLog` audit trail

**Classification:** `EMS_ALREADY_BETTER` — EMS Import V2 replaces manual file conversion entirely. The CSV→XLS rename workaround is an artifact of legacy system limitations.

**Gap:** EMS does not yet have a REG-compatible adapter for automatic data fetch.

---

### Step 3: Profile Creation & System Import (การสร้างโปรไฟล์ฯ)

**Reference process:**
- Login to e-humanities system
- Create profile: set exam periods (midterm/final dates per semester)
- Set exam time windows per profile
- Upload course/lecturer/student files separately

**EMS mapping:**
- `period.py` manages exam periods with full lifecycle
- `imports_v2.py` handles multi-type imports with period scoping
- Settings V2 manages system-wide configuration

**Classification:** `EMS_ALREADY_BETTER` — EMS period management is more structured and auditable.

---

### Step 4: Setting Course Status/Conditions (การกำหนดเงื่อนไขของกระบวนวิชา)

**Reference process:**
- Check which courses have special exam conditions:
  - ไม่จัดสอบ (no exam)
  - สอบ ORAL (oral exam only)
  - สอบแยกห้อง (separate room)
  - ไม่สอบร่วมกับวิชาอื่น (no co-exam with other courses)
  - ห้องพิเศษ (special room required)
  - ห้อง Lab (lab room required)
- Cross-reference with university bulletin of non-examined courses
- Faculty-specific exceptions documented

**EMS mapping:**
- `ExamSubmission` model has `exam_type` (online/onsite/no_exam)
- No course-level exam condition flags beyond basic type
- No room requirement flags (oral, lab, special) on courses

**Classification:** `LEGACY_PROCESS_STILL_VALUABLE` — course condition flags are real operational data the optimizer needs.

**Gap:** EMS lacks `CourseExamCondition` model with flags: oral_only, no_co_exam, special_room, lab_required, no_exam.

---

### Step 5: Changing Exam Status in System (เปลี่ยนสถานะการสอบ)

**Reference process:**
- Change exam status per course in the scheduling system
- Requires reviewing draft status list first
- Faculty notifies academic services of non-examined courses

**EMS mapping:**
- `ExamSubmission.exam_type` handles this
- Workflow approval governs state transitions

**Classification:** `EMS_ALREADY_BETTER` — EMS has formalized workflow for status changes with approval chain.

---

### Step 6: Room Assignment in Documents (จัดห้องสอบในเอกสาร)

**Reference process:**
- Manual room assignment in Excel/paper
- Considerations: room capacity vs student count, special rooms, oral rooms, language labs
- Can't mix "no co-exam" courses in same room
- Cross-faculty room borrowing requires formal request
- Takes 5 days (full faculty), 3 days (English Language)
- Common problem: insufficient rooms → pre-request other faculty rooms

**EMS mapping:**
- Room management: `routers/schedule.py` + `RoomManagementV2.tsx`
- Room model has capacity, unavailability slots
- Optimizer assigns rooms respecting capacity constraints

**Classification:** `EMS_ALREADY_BETTER` — CP-SAT optimizer handles room assignment automatically. The 5-day manual process collapses to minutes.

**Operational knowledge to preserve:** Room condition rules (oral, lab, no-mixing) must become optimizer constraints.

---

### Step 7: Uploading Room Data to Online System (กรอกข้อมูลห้องสอบในระบบ)

**Reference process:**
- 4-step manual entry: select semester → select course section → select room → enter student count and save
- Entirely manual, repeated for every course section

**EMS mapping:**
- Fully automated via optimizer output + confirm flow
- Manual adjustment available after optimization

**Classification:** `LEGACY_PROCESS_SHOULD_NOT_BE_IMPORTED` — this is manual data entry that the optimizer eliminates entirely.

---

### Step 8: Requesting Leave Information (ขอข้อมูลการลา)

**Reference process:**
- Request leave data from academic registry
- Paper/email request process
- Data covers lecturers, civil servants, employees
- Used to determine invigilator availability

**EMS mapping:**
- `StaffUnavailability` model in database
- `staff_workloads.py`: `build_staff_unavailability_map()` + `is_staff_unavailable()`
- Unavailability considered during optimization

**Classification:** `EMS_ALREADY_BETTER` — EMS has structured unavailability data model. The paper request chain is replaced by direct data entry.

**Gap:** No integration with CMU HR system for leave data auto-sync.

---

### Step 9: Organizing Exam Supervisors (จัดกรรมการคุมสอบในเอกสาร)

**Reference process:**
- Two data sources: (1) English Language Excel, (2) REG website self-invigilation list
- Rules:
  - 2 per room (standard)
  - ≥80 students → 3 per room (can exceed)
  - Large room (mixed courses) → 3 per room
  - Faculty head/special professors → only supervise own department
  - No consecutive sessions (except when necessary)
  - Takes 5 days full-faculty, 7 days English Language

**EMS mapping:**
- Optimizer assigns invigilators respecting:
  - Teacher invigilates own course
  - Fair distribution
  - Unavailability blocks
- No explicit room-capacity-based ratio rule (2 per room / 3 if ≥80)
- No "same department only" constraint for senior staff

**Classification:** `LEGACY_PROCESS_STILL_VALUABLE` — the ratio rules and seniority constraints are real operational requirements the optimizer must implement as configurable policy.

---

### Step 10: Calculating Co-Supervisor Count (คำนวณจำนวนกรรมการคุมสอบร่วม)

**Reference process:**
- Formula: `(enrolled students from other faculties) / (total enrolled) × required invigilators`
- Download data from REG Report #42 (enrollment by faculty)
- Used to request invigilators from other faculties
- Results documented in formal table per department

**EMS mapping:**
- `co_exam.py` router for cross-faculty exam management
- No co-supervisor count calculation engine
- No integration with REG Report #42

**Classification:** `LEGACY_PROCESS_STILL_VALUABLE` — the calculation formula is important operational logic.

---

### Step 11: Uploading Supervisor List to System (กรอกรายชื่อกรรมการคุมสอบ)

**Reference process:**
- Manual entry: select profile → click date → select room → add supervisor name → save
- Repeated for every room, every date

**EMS mapping:**
- Automated via optimizer output

**Classification:** `LEGACY_PROCESS_SHOULD_NOT_BE_IMPORTED` — fully replaced by optimization.

---

### Step 12: Checking Supervisor Workload (ตรวจสอบภาระงานคุมสอบ)

**Reference process:**
- Print workload calendar per supervisor
- Verify even distribution across time slots
- Identify supervisors with too-heavy or too-light loads
- Manual balancing if needed

**EMS mapping:**
- Optimizer includes fairness objective
- `staff_workloads.py` tracks workload
- Dashboard shows optimization issues
- No supervisor workload calendar view

**Classification:** `LEGACY_PROCESS_STILL_VALUABLE` — the workload verification step is an important QA gate. EMS should expose a supervisor workload calendar view.

---

### Step 13–14: Co-Supervisor Management (จัดและกรอกกรรมการคุมสอบร่วม)

**Reference process:**
- Co-supervisors from other faculties assigned per formal policy
- Rules: assigned to same rooms as own-faculty supervisors, or nearby rooms
- Consideration for consecutive time slots
- Enter into online system

**EMS mapping:**
- `co_exam.py` for external exam coordination
- No formalized co-supervisor assignment flow integrated with optimizer

**Classification:** `LEGACY_PROCESS_STILL_VALUABLE` — co-supervisor integration is a gap.

---

### Step 15: Uploading Student Names (นำข้อมูลรายชื่อนักศึกษาเข้าระบบ)

**Reference process:**
- Upload enrollment file after room/supervisor setup complete
- Update after tuition payment period (enrollment stabilizes)
- Select by department/major
- Used for: seating arrangement, attendance sheets, exam envelope covers

**EMS mapping:**
- Import V2 handles student enrollment
- `student_repository.py` manages student data
- Import happens early in workflow, not after room setup

**Classification:** `EMS_ALREADY_BETTER` — EMS import pipeline handles this, but the timing constraint (wait for enrollment stabilization) is a workflow policy EMS should make configurable.

---

### Step 16–17: Draft Schedule Circulation (เวียนร่างตารางสอบ)

**Reference process:**
- Draft sent to all departments (email/paper)
- Departments review: course names, dates, times, rooms, supervisors
- Errors reported back to academic services
- Changes made in system
- No formal tracking of feedback rounds

**EMS mapping:**
- Workflow approval chain: Admin → ESQ → Secretary
- No "draft circulation" concept with department-level review
- No per-department feedback collection

**Classification:** `LEGACY_PROCESS_STILL_VALUABLE` — draft circulation is a critical QA step that EMS lacks. Should become a configurable review round in the workflow engine.

---

### Step 18: Document Generation (การออกรายงาน)

**Reference process:**
- 18.1 Exam Appointment Order (คำสั่งแต่งตั้งกรรมการคุมสอบ) — formal government order document
- 18.2 OMR Cover / Exam Envelope (ปกซองข้อสอบ) — course, section, date, room, supervisor signatures
- 18.3 Answer Paper Submission Form (แบบฟอร์มรับส่งข้อสอบ) — paper pickup/delivery record

**EMS mapping:**
- `gen_docs.py`: exam cover, OMR envelope, attendance sheet (DOCX/PDF)
- `operational_documents.py`: PDF generation with QR codes, Thai date formatting
- `routers/documents.py`: document endpoints

**Classification:** `EMS_ALREADY_BETTER` for core document types. 

**Gap:** Exam Appointment Order (formal government command) formatting needs validation against actual document format.

---

### Step 19: Public Search (การสืบค้น)

**Reference process:**
- Public website (human.cmu.ac.th) allows search by:
  - Student ID
  - Course code + section
  - Supervisor name

**EMS mapping:**
- `routers/public.py` exists
- Internal search only, no public-facing student search
- `StudentSearch.tsx` page exists

**Classification:** `LEGACY_PROCESS_STILL_VALUABLE` — public student exam lookup is a real user need currently missing from EMS as a proper public endpoint.

---

### Step 20: Post-Exam Summary (สรุปผลการดำเนินการสอบ)

**Reference process:**
- Supervisors report issues during exam
- QR code on OMR envelope → incident report form
- Faculty compiles issues for departmental meeting
- Issues presented at faculty committee meeting
- Results used for continuous improvement

**EMS mapping:**
- QR check-in system exists
- No post-exam issue reporting module
- No structured incident collection
- No post-exam summary generation

**Classification:** `LEGACY_PROCESS_STILL_VALUABLE` — structured post-exam review loop is a critical quality management process EMS lacks entirely.

---

## 4. Operation Calendar Comparison

The reference document (Table 4.1) defines a monthly activity calendar covering:

| Activity | Semester 1 | Semester 2 | Summer |
|----------|-----------|-----------|--------|
| Setting central exam schedule | Jun | Nov | Apr |
| Data preparation | Jun | Nov | Apr |
| Profile creation & import | Jul | Dec | Apr |
| Setting course conditions | Jul | Dec | Apr |
| Changing exam status | Jul → Aug | Dec → Jan | Apr |
| Room booking (documents) | Jul | Dec | Apr |
| Room booking (system) | Jul → Sep | Dec → Feb | Apr |
| Leave data request | Jun | Nov | Apr |
| Supervisor assignment (docs) | Jul | Dec | Apr |
| Supervisor count calculation | Jul | Dec | Apr |
| Upload supervisor list | Jul | Dec | Apr |
| Check supervisor workload | Jul | Dec | Apr |
| Co-supervisor management | Jul → Sep | Dec → Mar | Apr |
| Upload student names | Jul → Sep | Dec → Mar | Apr |
| Draft schedule circulation | Aug | Jan | May |
| Schedule revision | Aug | Jan | May |
| Document generation | Aug | Jan | May |
| Search | Aug+ | Jan+ | May+ |
| Post-exam summary | Oct | Mar | May |

**EMS Gap:** No system equivalent to this calendar exists. EMS has no configurable deadline/activity calendar engine.

---

## 5. Summary Classification Table

| Reference Step | Classification | EMS Action |
|---------------|---------------|------------|
| 1. Central exam schedule | LEGACY_STILL_VALUABLE | → ExamPolicyEngine (scheduling rules table) |
| 2. Data preparation | EMS_ALREADY_BETTER | Keep Import V2, add REG adapter |
| 3. Profile creation | EMS_ALREADY_BETTER | Keep period management |
| 4. Course conditions | LEGACY_STILL_VALUABLE | → CourseExamConditionService |
| 5. Change exam status | EMS_ALREADY_BETTER | Keep workflow |
| 6. Room assignment (docs) | LEGACY_SHOULD_NOT_IMPORT | Replaced by optimizer |
| 7. Room upload (system) | LEGACY_SHOULD_NOT_IMPORT | Replaced by optimizer |
| 8. Leave request | EMS_ALREADY_BETTER | Keep, add HR sync |
| 9. Supervisor assignment | LEGACY_STILL_VALUABLE | → InvigilationRuleSet in optimizer |
| 10. Co-supervisor count | LEGACY_STILL_VALUABLE | → CoSupervisorCalculationService |
| 11. Upload supervisors | LEGACY_SHOULD_NOT_IMPORT | Replaced by optimizer |
| 12. Workload check | LEGACY_STILL_VALUABLE | → WorkloadCalendarView |
| 13-14. Co-supervisors | LEGACY_STILL_VALUABLE | → CoExam integration |
| 15. Upload students | EMS_ALREADY_BETTER | Keep, add timing policy |
| 16-17. Draft circulation | LEGACY_STILL_VALUABLE | → DraftReviewWorkflow |
| 18. Document generation | EMS_ALREADY_BETTER | Keep, validate formats |
| 19. Public search | LEGACY_STILL_VALUABLE | → Public exam lookup API |
| 20. Post-exam summary | LEGACY_STILL_VALUABLE | → PostExamReviewCenter |
| Operation calendar | MISSING_FROM_EMS | → ExamOperationCalendar |

---

*Next document: LEGACY_PROCESS_VS_EMS_ANALYSIS.md*
