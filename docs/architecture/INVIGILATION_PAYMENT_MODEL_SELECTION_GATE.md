# Invigilation Payment Model Selection Gate

**Date**: 2026-06-02  
**Status**: PREVIEW GATE REVIEW ONLY - NOT PAYMENT AUTHORIZATION

## Gate Decision

`READY_FOR_PREVIEW_IMPLEMENTATION = NO`

Final payment readiness: `NO`

## Recommended Preview Model

No preview model is selected.

The answer source does not confirm payment unit, rate source, role mapping, evidence requirement, approval owner, exception handling, payment period, or export format. Selecting Model A, B, C, or D would require assumptions, which are not allowed.

## Model Fit Review

| Model | Current fit | Why |
|---|---|---|
| Model A - Per Session | Not selected | Payment unit and session rate are not answered. |
| Model B - Per Hour | Not selected | Hourly unit, rounding, minimum duration, and hourly rate are not answered. |
| Model C - Role-Based | Not selected | Payable roles and role rates are not answered. |
| Model D - Hybrid | Not selected | All major rule families are missing; hybrid would multiply assumptions. |

## Fallback Candidate

Model A - Per Session may remain the simplest future fallback candidate for planning discussions only because EMS already has exam schedules and supervision records. It must not be implemented or treated as selected until finance/admin confirms that payment is per session and defines rates/evidence/approval rules.

## Required Inputs

- Payment unit
- Rate source and rate code
- Payable duty roles
- Evidence requirement
- Assignment, check-in, substitution, cancellation, and no-show statuses
- Payment period
- Approval owner and approval status
- Export format or explicit preview-export deferral

## Missing Inputs

All model-selecting policy inputs are missing. Current data can inventory assignments, but cannot authorize payment preview behavior.

## Rules Blocking Implementation

- Payment unit: missing
- Rate source: missing
- Duty roles: missing
- Evidence requirement: missing
- Approval owner: missing
- Exception rules: missing
- Payment period: missing
- Export format: missing
- Audit evidence requirement: missing

## Risks

- Existing `compensation` values may be mistaken as approved rates.
- `Supervision.confirmed` may be mistaken as attendance evidence without policy confirmation.
- QR pickup check-ins may be mistaken as invigilation attendance.
- Swap assignment mutation may obscure payment ownership without a confirmed substitution rule.
- Building any calculation now would encode unapproved assumptions.

## Gate Criteria Result

| Criteria | Required for YES | Current result |
|---|---|---|
| Payment unit answered | Yes | No |
| Rate source answered | Yes | No |
| Duty roles answered | Yes | No |
| Evidence requirement answered | Yes | No |
| Approval owner answered | Yes | No |
| Exception rules minimally answered | Yes | No |
| Payment period answered | Yes | No |
| Export format answered or preview-only export acceptable | Yes | No |

## Decision

Preview implementation is blocked. Continue with rule collection and data-readiness clarification only.

