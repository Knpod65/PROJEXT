# Workflow State Machine
## EMS — Formal State Machine Specification for All Stateful Workflows

> **Audience:** Engineers implementing workflow changes, QA writing test cases
> **Scope:** Implementation-level state machine spec — states, transitions, guards, side effects
> **NOT the user-facing workflow narrative** — that is in `docs/WORKFLOW.md`
> **Reference files:** `backend/term_lifecycle.py`, `backend/routers/submissions.py`, `backend/routers/optimize_workflow.py`, `backend/routers/swaps_v2.py`, `backend/models.py`

---

## State Machine Index

| # | Machine | Model | Current Location |
|---|---------|-------|-----------------|
| 1 | ExamPeriod Lifecycle | `ExamPeriod.lifecycle_status` | `term_lifecycle.py` — exemplary |
| 2 | ExamSubmission Status | `ExamSubmission.status` | `routers/submissions.py` — needs service extraction |
| 3 | WorkflowSession Signing | `OptimizeSession.status` | `routers/optimize_workflow.py` — mixed with unrelated code |
| 4 | PrintQueueJob Status | `PrintQueueJob.status` | `routers/printing.py` |
| 5 | SwapRequest Status | `SwapRequest.status` | `routers/swaps_v2.py` |

---

## 1. ExamPeriod Lifecycle

**State enum values** (`ExamPeriod.lifecycle_status` string field):
- `draft` — created, not yet active; editable
- `active` — current operating period; editable
- `archived` — historical; still visible; no mutations
- `locked` — fully closed; read-only forever

### Transition Table

| From | To | Trigger | Guard | Side Effect | Function |
|------|----|---------|-------|-------------|----------|
| `draft` | `active` | Admin activates period | Only one `active` period allowed at a time | `is_active=True`, `archived_at=None`, `locked_at=None` | `mark_period_active()` |
| `active` | `archived` | Admin archives period | Period must not be locked | `is_active=False`, `archived_at=UTC now` | `mark_period_archived()` |
| `archived` | `active` | Admin re-activates | Only one `active` at a time | `is_active=True`, `archived_at=None` | `mark_period_active()` |
| `active` | `locked` | Admin closes term | Period in `CLOSEABLE_STATUSES` (`active` or `archived`) | `is_active=False`, `locked_at=UTC now`, `archived_at=UTC now` | `mark_period_locked()` |
| `archived` | `locked` | Admin closes historical term | Period in `CLOSEABLE_STATUSES` | `is_active=False`, `locked_at=UTC now` | `mark_period_locked()` |
| `locked` | _any_ | ❌ **FORBIDDEN** | No transition out of locked | — | — |

### State Capability Sets
```python
EDITABLE_STATUSES   = {"draft", "active", "archived"}  # mutations allowed
CLOSEABLE_STATUSES  = {"active", "archived"}            # can be locked
```

### Cross-Domain Impact of Locked Status
When a period is locked, ALL other domains must refuse mutations to data scoped to that period:
- `ExamSchedule` records for that period → read-only
- `ExamSubmission` records for that period → read-only
- `Supervision` assignments for that period → read-only
- `SwapRequest` records for that period → read-only
- `ImportSession` for that period → blocked (imports rejected)

**Enforcement:** All mutation route handlers must call `ensure_period_record_editable(period)`
before any write. The function raises `HTTPException(409)` if period is locked.

### Current Implementation Notes
`term_lifecycle.py` is the gold standard for this machine. All functions are pure, UTC-correct,
and follow the rule that getters don't mutate. The `get_period_status()` function has a fallback
to `is_active` for legacy rows that predate the `lifecycle_status` column.

---

## 2. ExamSubmission Status

**State field:** `ExamSubmission.status` (string, maps to `SubmissionStatus` enum)
**State values:** `draft`, `submitted`, `approved`, `rejected`, `released`

### Transition Table

| From | To | Trigger | Who Can Trigger | Guard | Side Effect |
|------|----|---------|-----------------|-------|-------------|
| _(none)_ | `draft` | Section created or teacher opens submission | System / Teacher | Period must be `active`; teacher owns section | `ExamSubmission` record created |
| `draft` | `draft` | Teacher updates Step1/Step2/Step3 | Teacher | Teacher owns submission; period not locked | Metadata updated; `ExamSubmissionVersion` snapshot saved |
| `draft` | `submitted` | Teacher submits | Teacher | All required fields complete; PDF uploaded (if onsite); period not locked | `submitted_at` set; notification may send |
| `submitted` | `approved` | Admin approves | Admin only | Submission is in `submitted` status | `approved_by`, `approved_at` set; `ExamSubmissionVersion` snapshot; print queue job upserted |
| `submitted` | `rejected` | Admin rejects | Admin only | Submission is in `submitted` status | `rejected_at` set; rejection reason stored; notification to teacher |
| `rejected` | `draft` | Teacher re-opens after rejection | Teacher | Submission is in `rejected` status; period not locked | Status reset to `draft` |
| `approved` | `released` | Admin releases to print | Admin only | Submission is in `approved` status | Print queue job status set to `queued` |
| `approved` | `rejected` | Admin un-approves | Admin only | Unusual but possible | `approved_at` cleared; reason stored |

### 4-Step Wizard (Steps are Sub-states within `draft`)

The 4-step wizard does not change `status` — it only updates fields on the submission.
The submission remains `draft` until the teacher explicitly submits.

| Step | API Endpoint | Fields Written | Guard |
|------|-------------|----------------|-------|
| Step 1 | `PUT /api/submissions/{id}/step1` | `exam_date`, `start_time`, `end_time` | Teacher owns section |
| Step 2 | `PUT /api/submissions/{id}/step2` | `exam_type_choice`, `answer_formats` | Teacher owns section |
| Step 3 | `PUT /api/submissions/{id}/step3` | `a4_pages_count`, `duplex`, `staple`, `extra_copies` | Teacher owns section; exam_type = onsite |
| Upload | `POST /api/submissions/{id}/upload` | `file_path`, `original_filename` | Teacher owns section; exam_type = onsite |
| Submit | `PUT /api/submissions/{id}/submit` | `status = submitted`, `submitted_at` | All required steps complete |

### Version Snapshots
Every transition from `submitted` → `approved` or `approved` → `rejected` creates an
`ExamSubmissionVersion` record. This preserves a full audit trail of the submission state
at each approval decision point. The snapshot includes all printable metadata fields.

---

## 3. WorkflowSession Signing

**State field:** `OptimizeSession.status` (string)
**State values:** `draft`, `round1_signing`, `round1_complete`, `swap_open`, `round2_signing`, `complete`, `cancelled`

### Signing Order
`SIGN_ORDER_USERNAMES = ["atikant.s", "mathawee.m", "napaporn.ph", "paweena.t"]` (from `auth_utils.py`)
These users sign in order. Each user must sign before the next can.

### Transition Table

| From | To | Trigger | Who | Guard |
|------|----|---------|-----|-------|
| _(none)_ | `draft` | Admin runs optimizer | Admin | Period is `active`; no existing `draft` session |
| `draft` | `round1_signing` | Admin initiates signing | Admin | Optimizer result confirmed (not just preview) |
| `round1_signing` | `round1_signing` | Next signer in order signs | Signer (per SIGN_ORDER) | Signer's turn in sequence; not already signed |
| `round1_signing` | `round1_complete` | Final Round 1 signer signs | Final signer | All Round 1 signers have signed |
| `round1_complete` | `swap_open` | Admin opens swap window | Admin | Session is `round1_complete` |
| `swap_open` | `round2_signing` | Admin closes swap window and initiates Round 2 | Admin | Session is `swap_open` |
| `round2_signing` | `round2_signing` | Next signer signs | Signer (per SIGN_ORDER) | Signer's turn; not already signed in Round 2 |
| `round2_signing` | `complete` | Final Round 2 signer signs | Final signer | All Round 2 signers have signed |
| _any_ | `cancelled` | Admin cancels | Admin | Session not `complete` |
| `cancelled` | `draft` | Admin re-runs optimizer | Admin | Creates new session; old one stays `cancelled` |

### Swap Window Rules (during `swap_open` status)
- Staff may submit new `SwapRequest` records
- Each time slot allows a maximum of 1 approved swap
- Approving a swap for slot X auto-rejects all other pending swaps for slot X
- After swap window closes, all pending (unapproved) swaps are auto-rejected

### Cross-State Machine Dependency
ExamPeriod must be in `active` status for a WorkflowSession to be created.
If the period transitions to `archived` while a session is in `round1_signing`, the session
can continue but new optimizer runs are blocked.
If the period becomes `locked`, the session is effectively frozen — no further signing.

---

## 4. PrintQueueJob Status

**State field:** `PrintQueueJob.status` (maps to `PrintJobStatus` enum)
**State values:** `queued`, `printing`, `printed`, `dispatched`, `delivered`

### Transition Table

| From | To | Trigger | Who | Guard |
|------|----|---------|-----|-------|
| _(none)_ | `queued` | Admin releases submission to print | Admin | `ExamSubmission.status == "released"` |
| `queued` | `printing` | Print shop starts printing | `print_shop` role | Job is in `queued` status |
| `printing` | `printed` | Print shop marks complete | `print_shop` role | Job is in `printing` status |
| `printed` | `dispatched` | Print shop dispatches to collection point | `print_shop` role | Job is in `printed` status |
| `dispatched` | `delivered` | Recipient confirms receipt | `print_shop` or `admin` | Job is in `dispatched` status |
| _any_ | `queued` | Admin re-queues on error | Admin | Not in `delivered` status |

### Copy Count Visibility
Copy count is a field on `PrintQueueJob` (or the linked `ExamSubmission`). Visibility rules:
- `admin`, `esq_head`, `secretary`: can see copy counts
- `staff`, `teacher`: copy count is HIDDEN (PDPA — per-section print volumes are sensitive)
- `print_shop`: can see copy counts (needed for print operations)

**Current gap:** Enforcement is UI-only. Backend does not filter the field by role. Phase 4 fix required.

---

## 5. SwapRequest Status

**State field:** `SwapRequest.status` (maps to `SwapStatus` enum)
**State values:** `pending`, `approved`, `rejected`, `applied`, `cancelled`

### Transition Table

| From | To | Trigger | Who | Guard |
|------|----|---------|-----|-------|
| _(none)_ | `pending` | Staff submits swap request | Staff | WorkflowSession is in `swap_open` status; no conflicting swap exists for same slot |
| `pending` | `approved` | Admin approves | Admin | Swap is `pending`; no other `approved` swap for same slot |
| `pending` | `rejected` | Admin rejects | Admin | Swap is `pending` |
| `approved` | `applied` | Admin closes swap window | Admin | WorkflowSession transitions from `swap_open` → `round2_signing` |
| `applied` | _(terminal)_ | — | — | Applied swaps are immutable |
| _pending/approved_ | `cancelled` | Staff withdraws request | Staff (own request) | Not yet `applied` |

### Slot Conflict Rule (Invariant)
Only 1 `approved` swap is permitted per `(schedule_id, exam_date, time_slot)` combination.
When a swap is approved for slot S:
- All other `pending` swaps for slot S are automatically set to `rejected`
- The auto-rejection sends a notification to the requester

### Relationship with WorkflowSession
Swaps can only be submitted during `swap_open` status of the active `OptimizeSession`.
Attempting to create a swap outside the swap window returns HTTP 409.

---

## 6. Cross-State Machine Dependencies

```
ExamPeriod (active)
    ↓ required for
WorkflowSession (can be created/progressed)
    ↓ swap_open required for
SwapRequest (can be submitted)

ExamPeriod (active)
    ↓ required for
ExamSubmission (can be created/submitted)
    ↓ released required for
PrintQueueJob (can be created)

ExamPeriod (locked)
    ↓ blocks ALL mutations in all machines
```

---

## 7. Violation Catalog

Known locations where state machine guards are missing or incomplete:

| Violation | File | Risk |
|-----------|------|------|
| `approve_submission` does not check `period.lifecycle_status` | `submissions.py` | Approvals possible on locked period |
| Swap creation does not verify `OptimizeSession.status == swap_open` in all code paths | `swaps_v2.py` | Swaps created outside swap window |
| `PrintQueueJob` creation does not verify `ExamSubmission.status == released` | `printing.py` | Print jobs for unapproved submissions |
| WorkflowSession `complete` status allows further signature calls | `optimize_workflow.py` | Double-signing possible |
| `draft` → `round1_signing` transition missing explicit guard preventing duplicate sessions | `optimize_workflow.py` | Two active sessions for one period |
