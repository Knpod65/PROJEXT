# Payment Document Draft Export — Test Matrix

**Date**: 2026-06-08
**Status**: test matrix defined for future implementation
**Export implemented**: NO
**Note**: These tests must exist and pass before any draft export is implemented and merged.

## Overview

This matrix defines the tests that must be written and pass before any draft export endpoint, button, or workflow is implemented. Tests are grouped by category. No test implementation is started in this pass.

---

## Category 1 — Export Blocked When Preconditions Not Met

| Test ID | Test Description | Expected Result |
|---|---|---|
| T-EXP-001 | Export endpoint returns error when review status is not `ACCEPTED_FOR_DRAFT_EXPORT` | HTTP 400 or 403; export file not generated |
| T-EXP-002 | Export endpoint returns error when settings source status is not `CONFIGURED` | HTTP 400; export file not generated |
| T-EXP-003 | Export endpoint returns error when settings status is not `ACTIVE_FOR_DRAFT_PREVIEW` | HTTP 400; export file not generated |
| T-EXP-004 | Export endpoint returns error when calculation status is not `CALCULATED_FROM_SETTINGS` | HTTP 400; export file not generated |
| T-EXP-005 | Export endpoint returns error when reviewer comment is missing | HTTP 400; export file not generated |
| T-EXP-006 | Export endpoint returns error when paper-distribution responsible group is blank and not intentionally documented as blank | HTTP 400; export file not generated |
| T-EXP-007 | Export blocked when `payment_authorization_enabled = true` (should never be true, but must be guarded) | HTTP 400; export file not generated |
| T-EXP-008 | Export blocked when `final_export_enabled = true` (should never be true, but must be guarded) | HTTP 400; export file not generated |

---

## Category 2 — Export Output Contains Required Draft Labels

| Test ID | Test Description | Expected Result |
|---|---|---|
| T-LBL-001 | Excel export contains Thai draft label on every sheet | Label `ร่างเอกสารเพื่อการตรวจทานเท่านั้น ยังไม่ใช่เอกสารอนุมัติเบิกจ่าย` present |
| T-LBL-002 | Excel export contains English draft label on every sheet | Label `Draft for review only. Not payment authorization.` present |
| T-LBL-003 | PDF export contains draft watermark on every page | Watermark is visible and prominent |
| T-LBL-004 | HTML export contains draft label in page header | Label appears in header section |
| T-LBL-005 | Export output header/metadata includes `document_status = DRAFT_NOT_AUTHORIZED` | Value present in header row or metadata |
| T-LBL-006 | Export filename follows convention `draft_payment_<term>_<timestamp>.<ext>` | Filename matches pattern |
| T-LBL-007 | Export output does not contain words implying final authorization (e.g., "อนุมัติ", "Authorized", "Final") anywhere except in the negative label | No unauthorized approval wording |
| T-LBL-008 | Export output does not contain words implying official payment release (e.g., "เบิกจ่าย Official", "Payment Released") | No unauthorized release wording |

---

## Category 3 — Export Output Contains Required Data

| Test ID | Test Description | Expected Result |
|---|---|---|
| T-DATA-001 | Export includes academic term label (Thai) | e.g., `ภาคการศึกษาที่ 2/2568` present |
| T-DATA-002 | Export includes weekday rate from settings | `120.00 THB` (or configured value) present |
| T-DATA-003 | Export includes weekend rate from settings | `200.00 THB` (or configured value) present |
| T-DATA-004 | Export includes paper-distribution responsible group from settings | Configured group name present |
| T-DATA-005 | Export includes invigilation committee counts grouped by date and time slot | Correct grouped rows present |
| T-DATA-006 | Export includes paper-distribution committee counts | Counts present, marked as draft/manual source |
| T-DATA-007 | Export includes compensation amounts calculated from settings rates | Correct calculated amounts present |
| T-DATA-008 | Export includes grand totals for invigilation, paper-distribution, and combined | Totals match per-row amounts |
| T-DATA-009 | Export includes review metadata (reviewer name, role, review status, reviewed_at) | All four fields present |
| T-DATA-010 | Export includes calculation status `CALCULATED_FROM_SETTINGS` | Status present |
| T-DATA-011 | Export includes document preparation timestamp | Timestamp present |
| T-DATA-012 | Export includes export generation timestamp | Timestamp present |
| T-DATA-013 | Export includes settings source reference (term, settings status) | Reference present |

---

## Category 4 — Export Does Not Include Prohibited Data

| Test ID | Test Description | Expected Result |
|---|---|---|
| T-PROH-001 | Export does not include final payment authorization reference | No authorization reference in output |
| T-PROH-002 | Export does not include official payment approval signature field | No signature field present |
| T-PROH-003 | Export does not include `payment_authorization_enabled = true` | Field absent or always false |
| T-PROH-004 | Export does not include `final_export_enabled = true` | Field absent or always false |
| T-PROH-005 | Export does not include teaching workload data of any kind | No teaching workload fields |
| T-PROH-006 | Export does not use active simple demo/test rates (e.g., 300/500) | Active demo rates not present in calculation |
| T-PROH-007 | Export does not persist manual paper-distribution rows as payment truth | No write/persistence call on export action |
| T-PROH-008 | Export action does not mutate `document_status` | Status unchanged after export |
| T-PROH-009 | Export action does not mutate `payment_authorization_enabled` | Field unchanged after export |
| T-PROH-010 | Export action does not mutate `final_export_enabled` | Field unchanged after export |

---

## Category 5 — Role Permission Tests

| Test ID | Test Description | Expected Result |
|---|---|---|
| T-ROLE-001 | Admin user can generate draft export when all preconditions met | HTTP 200; export file returned |
| T-ROLE-002 | ESQ head user can generate draft export when all preconditions met | HTTP 200; export file returned |
| T-ROLE-003 | Secretary user can generate draft export when all preconditions met | HTTP 200; export file returned |
| T-ROLE-004 | Staff user is blocked from generating draft export | HTTP 403 |
| T-ROLE-005 | Teacher user is blocked from generating draft export | HTTP 403 |
| T-ROLE-006 | Print shop user is blocked from generating draft export | HTTP 403 |
| T-ROLE-007 | Unauthenticated user is blocked from generating draft export | HTTP 401 |

---

## Category 6 — Thai Text Rendering Tests

| Test ID | Test Description | Expected Result |
|---|---|---|
| T-TH-001 | Excel export renders Thai characters without corruption | Thai text is readable in Excel |
| T-TH-002 | PDF export renders Thai characters without corruption | Thai text is readable in PDF |
| T-TH-003 | HTML export renders Thai characters without corruption | Thai text is readable in browser print view |
| T-TH-004 | Thai draft label is rendered at correct font size (not truncated) | Label is fully visible |
| T-TH-005 | Column headers use correct Thai labels from i18n keys | Headers match approved Thai terms |
| T-TH-006 | Day type labels use Thai (วันธรรมดา / วันหยุด) | Correct Thai labels |
| T-TH-007 | Academic term uses Thai Buddhist Era format | e.g., `ภาคการศึกษาที่ 2/2568` |

---

## Category 7 — Excel and PDF Formatting Tests

| Test ID | Test Description | Expected Result |
|---|---|---|
| T-FMT-001 | Excel columns are correctly sized for content | No truncated content in default view |
| T-FMT-002 | Excel draft label row is visually distinct (bold, background color, or banner) | Clearly distinguishable from data rows |
| T-FMT-003 | Excel totals row is visually distinct from data rows | Clear separation |
| T-FMT-004 | PDF page orientation is appropriate for table width (landscape if needed) | No horizontal overflow |
| T-FMT-005 | PDF footer on every page includes draft label and page number | Footer present and correct |
| T-FMT-006 | PDF header on every page includes document title and term | Header present and correct |
| T-FMT-007 | Amount columns use 2 decimal places | e.g., `120.00`, not `120` or `120.000` |
| T-FMT-008 | Count columns use integer format | No decimal places on count fields |

---

## Category 8 — Filename Convention Tests

| Test ID | Test Description | Expected Result |
|---|---|---|
| T-FILE-001 | Excel filename matches `draft_payment_<term>_<timestamp>.xlsx` | e.g., `draft_payment_2_2568_20260608_143022.xlsx` |
| T-FILE-002 | PDF filename matches `draft_payment_<term>_<timestamp>.pdf` | e.g., `draft_payment_2_2568_20260608_143022.pdf` |
| T-FILE-003 | Filename does not contain "official", "final", or "authorized" | No prohibited words in filename |
| T-FILE-004 | Filename term portion is URL-safe and filesystem-safe | No `/`, `:`, or special characters |
| T-FILE-005 | Content-Disposition header matches filename for browser download | Header and filename match |

---

## Pre-Implementation Acceptance Criteria

Before any draft export feature branch is merged, ALL of the following must be true:

1. All tests in Categories 1–8 above are written and passing.
2. All 10 preconditions in `PAYMENT_DOCUMENT_DRAFT_EXPORT_DESIGN_GATE.md` are met.
3. A human reviewer has explicitly set the review status to `ACCEPTED_FOR_DRAFT_EXPORT` on the target term.
4. Full backend test suite passes with export tests included (target: 1531+ tests passing after export tests added).
5. Frontend build passes after export button/UI is added.
6. EN/TH i18n parity maintained for all new export-related strings.
7. Live browser smoke confirms draft label is visible on generated output.
8. No code change touches `payment_authorization_enabled`, `final_export_enabled`, `document_status`, or payment calculation logic.
9. Git diff contains no changes to backend payment calculation services, review records, settings logic, or rate rules.
10. Final validation log is created documenting: file formats generated, safety flags confirmed, role blocks confirmed, Thai text rendering confirmed.
