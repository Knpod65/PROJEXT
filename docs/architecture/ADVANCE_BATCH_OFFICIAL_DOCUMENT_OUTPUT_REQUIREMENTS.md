# Advance Batch Official-Style Document Output Requirements

**Date**: 2026-06-04
**Status**: DOCUMENT DRAFT REQUIREMENTS - NOT OFFICIAL EXPORT
**Finance validation gate**: `PENDING_FINANCE_ADMIN_REVIEW`

## Document Identity

- Thai title: `สรุปจำนวนกรรมการและค่าตอบแทน รายวัน/ช่วงเวลา`
- Term label example: `ภาคการศึกษาที่ 2/2568`
- Primary language: Thai
- Intended layout: print-friendly summary table

This specification aligns EMS terminology and data requirements with a user-transcribed historical official-style sample. It does not implement or authorize an official export.

## Output Columns

| Field | Thai label |
|---|---|
| `exam_date` | วันที่สอบ |
| `time_slot` | ช่วงเวลา |
| `day_type` | ประเภทวัน |
| `invigilation_committee_count` | จำนวนกรรมการคุมสอบ |
| `invigilation_compensation_amount` | ค่าตอบแทนคุมสอบ (บาท) |
| `paper_distribution_committee_count` | จำนวนกรรมการจ่ายข้อสอบ |
| `paper_distribution_compensation_amount` | ค่าตอบแทนจ่ายข้อสอบ (บาท) |
| `total_compensation_amount` | รวมค่าตอบแทน (บาท) |

## Grouping And Calculation Shape

- Group by exam date and normalized time slot.
- Classify weekday/weekend from normalized exam date.
- Sum invigilation committee count per date/time slot.
- Sum paper-distribution committee count per date/time slot.
- Calculate each category subtotal only from finance-confirmed rates and units.
- Calculate row total as the sum of both category subtotals.
- Calculate grand totals for both categories and the combined amount.

## Required Header And Footer Metadata

- Academic term and exam type
- Approved rate statement and effective period
- Document preparation date
- Source/provenance statement
- Reviewer and signatory fields
- Official memo/document number when required
- Preview/document-draft watermark until official approval/export rules exist

## Source And Reconciliation Boundaries

- Invigilation and paper-distribution categories must retain separate source lineage.
- Current Advance Batch preview cannot be treated as the complete source because it covers invigilation only.
- Paper-distribution source selection remains pending finance/admin confirmation.
- Check-in, pickup scans, absence, and no-show evidence remain reconciliation/audit inputs unless finance/admin approves another rule.

## Future Output Formats

- Excel-style summary output: later, after rule and source confirmation
- PDF/document output: later, after signatory and official metadata rules
- Official finance export: blocked

No Excel, PDF, payment report, approval action, or official export is implemented by this document.

## 2026-06-05 Draft Preview Decision

- The next implementation is an in-app official-style draft preview for term `2/2568`.
- Use fixed term-specific rates: weekday `120 THB`, weekend `200 THB`.
- Treat active local `300/500` as demo/test data only; the draft preview must not read it.
- Include both `INVIGILATION_COMMITTEE` and `PAPER_DISTRIBUTION_COMMITTEE`.
- Paper-distribution committee counts may be staff-entered/manual-confirmed for draft purposes only and must not be persisted by this pass.
- Keep `draft_only`, no final payment approval, no payment authorization, no official export, and supervisor/finance review required.
- Do not touch teaching workload, Work H, opencourse, or coinstruc logic.
