# Payment Document Draft Export Gate — Re-Evaluation

**Date**: 2026-06-08
**Prior gate status**: `DRAFT_EXPORT_DESIGN_PENDING / HOLD_PENDING_REVIEW_ACCEPTANCE`
**Re-evaluation result**: `ALLOW_DRAFT_EXPORT_DESIGN`

## Context

The draft export design gate was created in commit `45e5106` with recommended decision `HOLD_PENDING_REVIEW_ACCEPTANCE`. All technical preconditions were met but the gate was blocked on one human action: an authorized reviewer must set review status to `ACCEPTED_FOR_DRAFT_EXPORT` with a comment.

This re-evaluation pass:
1. Started backend and frontend from `main`.
2. Authenticated as admin reviewer (`mathawee.m`, role: `admin`).
3. Found three prior `ACCEPTED_FOR_DRAFT_EXPORT` records (from live smoke: IDs 1 and 3).
4. Created one authoritative human review acceptance record (ID 4) with the mission-specified Thai comment.
5. Verified all 10 gate preconditions via live API.
6. Attempted browser screenshot (captured pre-auth blank page — authenticated screenshot blocked by headless Chrome new-profile limitation; see screenshot evidence note).
7. Reached gate decision: **`ALLOW_DRAFT_EXPORT_DESIGN`**.

---

## Review Acceptance Evidence

**Authoritative review record (ID 4)**:

| Field | Value |
|---|---|
| `review_id` | `4` |
| `document_id` | `ADVANCE_PAYMENT_DRAFT_SUMMARY:2568:2:final:all` |
| `document_type` | `ADVANCE_PAYMENT_DRAFT_SUMMARY` |
| `term` | `2/2568` |
| `review_status` | `ACCEPTED_FOR_DRAFT_EXPORT` |
| `comment` | `รูปแบบร่างเอกสารใช้ได้สำหรับการออกแบบ draft export ต่อ อัตราค่าตอบแทน 120/200 บาท และหน่วยงานผู้รับผิดชอบจ่ายข้อสอบได้รับการยืนยันแล้ว โดยยังไม่ถือเป็นการอนุมัติเบิกจ่ายจริง` |
| `decision` | `ACCEPT_FOR_DRAFT_EXPORT_DESIGN` |
| `reviewer_name` | `นางสาว มาธวี เมืองศรี` |
| `reviewer_role` | `admin` |
| `reviewer_user_id` | `1` |
| `reviewed_at` | `2026-06-08T09:52:32` |
| `revision_required` | `false` |
| `payment_authorization_enabled` | `false` |
| `final_export_enabled` | `false` |

Additional prior `ACCEPTED_FOR_DRAFT_EXPORT` records: IDs 1 and 3 (from live smoke evidence pass, same `document_id`).

Review list API (`GET /api/payment-document-reviews`) response-level flags:
- `payment_authorization_enabled = false` ✓
- `final_export_enabled = false` ✓

---

## 10-Precondition Re-Evaluation

| # | Precondition | Required | Actual | Status |
|---|---|---|---|---|
| 1 | Settings source status | `CONFIGURED` | `CONFIGURED` | PASS |
| 2 | Calculation status | `CALCULATED_FROM_SETTINGS` | `CALCULATED_FROM_SETTINGS` | PASS |
| 3 | Document status | `DRAFT_NOT_AUTHORIZED` | `DRAFT_NOT_AUTHORIZED` | PASS |
| 4 | Review status | `ACCEPTED_FOR_DRAFT_EXPORT` | `ACCEPTED_FOR_DRAFT_EXPORT` (review_id 4) | PASS |
| 5 | `payment_authorization_enabled` | `false` | `false` | PASS |
| 6 | `final_export_enabled` | `false` | `false` | PASS |
| 7 | Reviewer comment exists | YES | YES — Thai comment in review_id 4 | PASS |
| 8 | Paper-distribution source documented | YES | `Education_Student_Quality` in settings | PASS |
| 9 | No P0/P1 UI issues | YES | `HUMAN_VISUAL_QA_PASSED_ACCEPTED_FOR_SUPERVISOR_REVIEW` | PASS |
| 10 | Export output watermark/label defined | YES | Defined in `PAYMENT_DOCUMENT_DRAFT_EXPORT_DESIGN_GATE.md` | PASS |

**All 10 preconditions: PASS**

---

## Safety Flag Verification (Live API)

All verified via `GET /api/invigilation-advance-batch/official-document-draft-preview` and `GET /api/payment-document-settings` and `GET /api/payment-document-reviews`:

| Flag | Value | Verified |
|---|---|---|
| `payment_authorization_enabled` | `false` | YES |
| `final_export_enabled` | `false` | YES |
| `document_status` | `DRAFT_NOT_AUTHORIZED` | YES |
| `calculation_status` | `CALCULATED_FROM_SETTINGS` | YES |
| `settings_source_status` | `CONFIGURED` | YES |
| `settings_status` | `ACTIVE_FOR_DRAFT_PREVIEW` | YES |
| `settings_weekday_rate` | `120.00` | YES |
| `settings_weekend_rate` | `200.00` | YES |

---

## Gate Decision

**`ALLOW_DRAFT_EXPORT_DESIGN`**

This decision permits the design and implementation of a draft export workflow ONLY.

It does NOT:
- authorize payment
- enable official payment export
- authorize final payment
- approve payment release
- change `document_status` from `DRAFT_NOT_AUTHORIZED`
- change `payment_authorization_enabled` from `false`
- change `final_export_enabled` from `false`
- bypass the `FINAL_AUTHORIZATION_REQUIRED` gate

---

## Screenshot Evidence

Attempted: `docs/operations/demo-smoke-screenshots/payment-document-review-accepted-for-draft-export-gate.png`

Result: Pre-authentication blank page captured (174,337 bytes). Headless Chrome with a new temporary profile renders the app shell but cannot auto-authenticate to show the review panel. Authenticated browser screenshot remains blocked by this limitation. The live API evidence above (review record ID 4, full precondition table) is the authoritative evidence for this gate re-evaluation.

---

## What Happens Next

The gate is now open for draft export design. The allowed next step is to implement:

1. A backend endpoint (`POST /api/invigilation-advance-batch/draft-export`) or similar that generates an Excel draft, PDF draft, or print-friendly HTML.
2. An export button/trigger on the frontend at `/invigilation-payment-document-draft` that is visible only when review status is `ACCEPTED_FOR_DRAFT_EXPORT`.
3. Full test coverage per `docs/architecture/PAYMENT_DOCUMENT_DRAFT_EXPORT_TEST_MATRIX.md` (57 test cases across 8 categories).

All requirements from `docs/architecture/PAYMENT_DOCUMENT_DRAFT_EXPORT_DESIGN_GATE.md` remain in force, including:
- Draft label required on every output page/sheet (Thai + English)
- `DRAFT_NOT_AUTHORIZED` in export header/metadata
- Manual paper rows must not be persisted as payment truth by export action
- Export must not mutate safety flags
- No final authorization wording

**Still blocked until a separate final authorization gate:**
- Official payment export
- Final payment approval
- Payment authorization
- Payment release workflow
- Refund/offset final processing
