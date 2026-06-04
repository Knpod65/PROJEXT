# Advance Batch Finance Validation Decision Gate

**Date**: 2026-06-04
**Current status**: `PENDING_FINANCE_ADMIN_REVIEW`
**Scope**: Preview-logic validation only

## Gate Status Values

- `PENDING_FINANCE_ADMIN_REVIEW`
- `APPROVED_FOR_APPROVAL_WORKFLOW_DESIGN`
- `APPROVED_WITH_CORRECTIONS_PENDING`
- `HOLD_PENDING_RULE_CLARIFICATION`
- `REJECTED_REDESIGN_REQUIRED`

## Transition Requirements

A gate transition requires all of the following:

- A completed and signed `ADVANCE_BATCH_FINANCE_VALIDATION_RESPONSE_INTAKE.md`.
- A completed independent comparison summary.
- A completed discrepancy register when mismatches exist.
- Correction backlog or follow-up questions when required by the selected decision.

Without that evidence, the status remains `PENDING_FINANCE_ADMIN_REVIEW`.

## Decision Mapping

| Finance/Admin Decision | Gate Outcome | Required Next Action | Approval/Export Allowed? |
|---|---|---|---|
| `APPROVE_PREVIEW_LOGIC` | `APPROVED_FOR_APPROVAL_WORKFLOW_DESIGN` | Begin a separate approval-workflow design pass | No |
| `APPROVE_WITH_CORRECTIONS` | `APPROVED_WITH_CORRECTIONS_PENDING` | Create correction backlog, fix discrepancies, and rerun validation | No |
| `HOLD_PENDING_RULE_CLARIFICATION` | `HOLD_PENDING_RULE_CLARIFICATION` | Complete finance/admin follow-up questions | No |
| `REJECT_PREVIEW_LOGIC` | `REJECTED_REDESIGN_REQUIRED` | Stop approval/export path and redesign the preview model | No |

## Outcome Rules

### `APPROVED_FOR_APPROVAL_WORKFLOW_DESIGN`

- Preview logic is accepted for planning purposes.
- A later pass may design an approval workflow.
- Payment remains unauthorized and official export remains unimplemented.

### `APPROVED_WITH_CORRECTIONS_PENDING`

- Every required correction must be tracked.
- Preview logic must be fixed and independently revalidated.
- Approval/export design remains blocked.

### `HOLD_PENDING_RULE_CLARIFICATION`

- Follow-up questions must be assigned and answered.
- The preview model remains unchanged while clarification is pending.
- Approval/export design remains blocked.

### `REJECTED_REDESIGN_REQUIRED`

- Stop the approval/export path.
- Preserve evidence and discrepancy history.
- Redesign and revalidate the preview model before reopening this gate.

## Safety Boundary

No gate outcome authorizes payment, approves a batch, creates an official payment report, or changes post-duty reconciliation. The current status is and must remain `PENDING_FINANCE_ADMIN_REVIEW` until an actual signed response is received.
