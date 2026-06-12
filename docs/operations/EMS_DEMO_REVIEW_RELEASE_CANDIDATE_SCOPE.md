# EMS Demo/Review Release Candidate Scope

**Release candidate**: `EMS_DEMO_REVIEW_RC_1`  
**Freeze date**: 2026-06-12  
**Baseline commit**: `170dfa2`

## Release Candidate Statement

`EMS_DEMO_REVIEW_RC_1` is ready for a supervised demo and review within the documented constraints. It is not production-final, does not authorize finance payment, and does not provide an official-final payment export.

## Included

- Exam schedule and operational workspaces.
- Staff availability, rooms, periods, swaps, submissions, print review, and external-exam pages.
- Invigilation advance preview.
- Term-specific payment-document settings.
- Persistent payment-document review workflow.
- Settings-backed official payment-document draft preview.
- Review-gated draft XLSX export.
- Role-based visibility and access evidence.
- Full UI regression closure evidence.

## Excluded And Blocked

- Final payment approval.
- Final payment authorization.
- Official-final payment export.
- Production finance release workflow.
- Payment release and post-duty reconciliation finalization.
- Production deployment or production-auth readiness claim.
- Workload-route presentation polish.
- Teaching workload, Work H, opencourse, and coinstruc logic.

## Required Demo Language

- Demo/review ready within documented constraints.
- Payment document remains `DRAFT_NOT_AUTHORIZED`.
- Draft XLSX is for review only and is not official-final output.
- Production readiness and finance authorization are not claimed.

## Freeze Rules

- No new features or UI redesign.
- No backend, API, permission, payment, export, review/settings, rate, or production configuration changes.
- No workload-domain changes.
- Only a true release-candidate blocker may justify a separately validated and separately committed fix.

## Post-Demo Decision Status (2026-06-12)

- Human decision on the produced RC1 draft XLSX format: `NOT_PROVIDED`.
- Current format gate: `HOLD_PENDING_ADDITIONAL_REVIEW`.
- Existing `ACCEPTED_FOR_DRAFT_EXPORT` remains a draft-generation gate only.
- Final-authorization design remains blocked.
- RC1 scope, safety boundaries, and readiness claims remain unchanged.
