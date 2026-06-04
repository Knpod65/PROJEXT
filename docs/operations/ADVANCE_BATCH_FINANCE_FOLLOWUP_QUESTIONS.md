# Advance Batch Finance Follow-Up Questions

**Status**: Open question register
**Current gate**: `PENDING_FINANCE_ADMIN_REVIEW`
**Purpose**: Capture finance/admin rule clarifications needed before approval-workflow design.

Allowed `status` values:

- `OPEN`
- `ANSWERED_DRAFT`
- `ANSWERED_APPROVED`
- `DEFERRED`
- `NOT_APPLICABLE`

| question_id | topic | question | why_needed | options | owner | urgency | blocks_approval_workflow_design | answer | status |
|---|---|---|---|---|---|---|---|---|---|
| ABF-001 | Rounding | Should preview totals be rounded or exact? | Defines expected amount comparison and later workflow design | exact; round per row; round total; other | Finance/Admin | HIGH | YES |  | OPEN |
| ABF-002 | Advance roster inclusion | Should all assigned roster rows be included before reconciliation? | Confirms advance roster inclusion policy | all assigned; approved assignments only; exceptions; other | Finance/Admin / Exam Office | CRITICAL | YES |  | OPEN |
| ABF-003 | Cancelled exams | How should cancelled exams before disbursement be handled? | Defines whether cancelled duties enter preview or remain blocked | exclude; include; manual review; other | Finance/Admin / Exam Office | HIGH | YES |  | OPEN |
| ABF-004 | Duplicate duties | How should duplicate same-person same-slot duties be handled? | Defines duplicate resolution and audit expectations | block; merge; manual review; other | Finance/Admin / Exam Office | HIGH | YES |  | OPEN |
| ABF-005 | Validation sign-off | What document is required for preview logic sign-off? | Establishes acceptable evidence and approval authority | signed intake; official memo; meeting record; other | Finance/Admin | CRITICAL | YES |  | OPEN |
| ABF-006 | Workflow ownership | Who owns final approval workflow design? | Identifies the responsible owner for the next design stage | finance; exam office; joint owner; other | Faculty Leadership / Finance/Admin | CRITICAL | YES |  | OPEN |

## Register Rules

- Only an authorized owner may mark an answer `ANSWERED_APPROVED`.
- Attach or cite the approval source for approved answers.
- Open blocking questions keep approval-workflow design blocked.
- Answers do not themselves authorize payment or enable official export.
