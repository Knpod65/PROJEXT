# Advance Batch Assignment Data Audit

**Date**: 2026-06-02  
**Status**: PREVIEW ONLY - INTERNAL INVIGILATION ASSIGNMENTS ONLY

| File / Path | Data Concept | Has Exam Session? | Has Room? | Has Assigned Person? | Has Role? | Has Assignment Status? | Has Approval Status? | Has Period/Semester? | Usable For Advance Roster? | Missing Fields | Recommendation |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `backend/models.py` `ExamSchedule` | Exam session, room, date/time, status | Yes | Partial | Via `supervisions` | Via `supervisions` | Schedule status only | No roster approval | Via section/period lookup | Yes | Explicit batch status | Use as primary schedule source. |
| `backend/models.py` `Supervision` | Invigilator assignment | Via schedule | Via schedule | Yes | Yes | `confirmed` exists but not payment approval | No | Via schedule | Yes | No advance batch fields | Use as one row per duty. |
| `backend/models.py` `User` | Person identity | No | No | Yes | Person role exists | No | No | No | Yes | Finance person type | Use identity only, not rate category. |
| `backend/models.py` `Room` | Room identity | No | Yes | No | No | No | No | No | Yes | None for roster preview | Use room name/id when present. |
| `backend/models.py` `Section` / `Course` | Course, section, term | Yes through schedule | No | Teacher only | No | No | No | Yes | Yes | None for internal roster preview | Use for course/section/period context. |
| `backend/models.py` `ExamPeriod` | Academic year, semester, exam type | No | No | No | No | Lifecycle only | No | Yes | Yes | May not equal payment period | Use candidate batch period only. |
| `backend/services/schedule_query_service.py` | Existing schedule serialization | Yes | Yes | Yes | Yes | Schedule/supervision flags | No | Yes via section | Yes | Payment-specific statuses | Reuse field semantics; do not reuse compensation values. |
| `backend/repositories/workload_duty_analytics_repository.py` | Normalized duty analytics | Yes | Limited | Yes | Partial | No | No | Yes | Candidate only | Loses schedule/supervision detail | Do not use as first source; query assignments directly. |
| `frontend/src/pages/WorkloadDutyAnalytics.tsx` | Duty workload UI | Aggregated | No | Aggregated | Grouped | No | No | Filtered | No backend source | Payment-specific columns | Do not change in this pass. |

## Decision

The current model is sufficient for a read-only backend preview service with no migration. It is not sufficient for final payment, final export, refund amounts, or official disbursement approval.

