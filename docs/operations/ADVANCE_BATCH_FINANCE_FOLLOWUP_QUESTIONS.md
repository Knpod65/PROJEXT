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
| ABF-007 | Current rate selection | Which rate should EMS use for the current operational preview: historical `120/200`, user-stated draft `150/200`, active local `300/500`, or another approved rate? | Three conflicting rate candidates now exist | 120/200; 150/200; 300/500; term-specific; other | Finance/Admin | CRITICAL | YES |  | OPEN |
| ABF-008 | Term-specific rates | Are weekday/weekend rates term-specific or globally effective? | Determines rate selection and historical reproducibility | term-specific; global; effective-date based; other | Finance/Admin | CRITICAL | YES |  | OPEN |
| ABF-009 | Category rate sharing | Does paper-distribution committee use the same weekday/weekend rate as invigilation committee? | Historical sample appears shared, but no current approved rule exists | same rate; separate rate; not payable; other | Finance/Admin | CRITICAL | YES |  | OPEN |
| ABF-010 | Paper-distribution source | Which source should EMS use for payable paper-distribution committee counts? | Current assignments, schedule distributors, historical slots, and pickup evidence differ | current assignment table; historical slot; schedule distributor; approved import; other | Finance/Admin / Exam Office | CRITICAL | YES |  | OPEN |
| ABF-011 | Manual distribution fallback | Should paper-distribution committee counts be entered manually when no approved roster exists? | Needed if operational sources are incomplete or not authoritative | manual entry allowed; new source required; exclude; other | Finance/Admin / Exam Office | HIGH | YES |  | OPEN |
| ABF-012 | Official grouping | Should the future official-style output group exactly by exam date and time slot as in the 2/2568 transcription? | Defines official document aggregation shape | exact date/time grouping; daily only; period summary; other | Finance/Admin | HIGH | YES |  | OPEN |
| ABF-013 | 2/2568 sample rate | Should EMS use `120/200` for 2/2568? | The historical sample uses `120/200`, but active local EMS currently uses `300/500` and the prior user draft stated `150/200` | yes for 2/2568; no; term-specific; hold | Finance/Admin | CRITICAL | YES |  | OPEN |
| ABF-014 | Active demo rate handling | Should current active `300/500` be treated as demo/test only? | Prevents accidental use of demo configuration as official 2/2568 payment rate | demo/test only; official active rate; replace after confirmation; hold | Finance/Admin / System Owner | CRITICAL | YES |  | OPEN |
| ABF-015 | Final document reviewer | Who reviews the final document draft before use? | Official-style output needs a reviewer/signatory chain before it can leave draft status | finance reviewer; supervisor; joint review; other | Finance/Admin / Exam Office | CRITICAL | YES |  | OPEN |

## 2/2568 Rate And Paper-Distribution Decision Coverage

The following requested questions remain open. Existing rows cover several items; the added rows above capture the missing explicit decisions.

| Required question | Register row | status |
|---|---|---|
| Should EMS use `120/200` for 2/2568? | `ABF-013` | `OPEN` |
| Should rates be term-specific? | `ABF-008` | `OPEN` |
| Should current active `300/500` be treated as demo/test only? | `ABF-014` | `OPEN` |
| What is the authoritative source for paper-distribution committee counts? | `ABF-010` | `OPEN` |
| Should paper-distribution committee use the same weekday/weekend rates? | `ABF-009` | `OPEN` |
| Should official output group by date/time slot exactly like the sample? | `ABF-012` | `OPEN` |
| Should staff be allowed to enter paper-distribution counts manually? | `ABF-011` | `OPEN` |
| Who reviews the final document draft before use? | `ABF-015` | `OPEN` |

## Register Rules

- Only an authorized owner may mark an answer `ANSWERED_APPROVED`.
- Attach or cite the approval source for approved answers.
- Open blocking questions keep approval-workflow design blocked.
- Answers do not themselves authorize payment or enable official export.
