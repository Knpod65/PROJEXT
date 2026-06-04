# แบบรับผลการตรวจสอบยอดตัวอย่างค่าคุมสอบจากฝ่ายการเงิน/ผู้ดูแลระบบ

**English title**: Advance Batch Finance Validation Response Intake
**สถานะปัจจุบัน**: `PENDING_FINANCE_ADMIN_REVIEW`
**คำเตือน**: แบบฟอร์มนี้ใช้ยืนยันตรรกะยอดตัวอย่างเท่านั้น ไม่ใช่การอนุมัติจ่ายเงินจริง ไม่ใช่การอนุมัติ batch และไม่ใช่เอกสารส่งออกอย่างเป็นทางการ

## 1. ข้อมูลผู้ตรวจสอบ / Reviewer Information

| Field | Response |
|---|---|
| reviewed_by |  |
| role |  |
| unit |  |
| reviewed_at |  |
| contact |  |

## 2. ผลการตรวจสอบ / Validation Decision

เลือกได้หนึ่งค่าโดยผู้มีอำนาจตรวจสอบ:

- [ ] `APPROVE_PREVIEW_LOGIC`
- [ ] `APPROVE_WITH_CORRECTIONS`
- [ ] `HOLD_PENDING_RULE_CLARIFICATION`
- [ ] `REJECT_PREVIEW_LOGIC`

| Field | Response |
|---|---|
| selected_decision |  |
| decision_reason |  |

## 3. การยืนยันสรุปผล / Summary Confirmation

Allowed answers: `YES`, `NO`, `NEEDS_REVIEW`

| Check | Response | Reviewer note |
|---|---|---|
| total roster rows confirmed |  |  |
| weekday count confirmed |  |  |
| weekend count confirmed |  |  |
| preview total confirmed |  |  |
| weekday rate confirmed |  |  |
| weekend rate confirmed |  |  |
| Buddhist Era year normalization accepted |  |  |

## 4. สรุปข้อแตกต่าง / Discrepancy Summary

| Field | Response |
|---|---|
| discrepancies_found (`YES` / `NO`) |  |
| discrepancy_register_completed (`YES` / `NO`) |  |
| number_of_discrepancies |  |
| highest_severity |  |
| discrepancy_register_reference | `docs/operations/ADVANCE_BATCH_PREVIEW_DISCREPANCY_REGISTER.md` |

## 5. การแก้ไขที่ต้องดำเนินการ / Required Correction

เลือกได้มากกว่าหนึ่งรายการ:

- [ ] `NONE`
- [ ] `RATE_CORRECTION`
- [ ] `DAY_TYPE_CORRECTION`
- [ ] `ROSTER_INCLUSION_CORRECTION`
- [ ] `MISSING_EXAM_DATE_CORRECTION`
- [ ] `DUPLICATE_DUTY_CORRECTION`
- [ ] `OTHER`

| Field | Response |
|---|---|
| correction_summary |  |
| correction_backlog_reference | `docs/operations/ADVANCE_BATCH_PREVIEW_CORRECTION_BACKLOG.md` |

## 6. ข้อเสนอแนะขั้นตอนถัดไป / Next-Step Recommendation

เลือกได้หนึ่งรายการ:

- [ ] `PROCEED_TO_APPROVAL_WORKFLOW_DESIGN`
- [ ] `FIX_PREVIEW_LOGIC_FIRST`
- [ ] `REQUEST_MORE_RULE_CLARIFICATION`
- [ ] `STOP_AND_REDESIGN`

| Field | Response |
|---|---|
| selected_recommendation |  |
| follow_up_questions_reference | `docs/operations/ADVANCE_BATCH_FINANCE_FOLLOWUP_QUESTIONS.md` |

## 7. การยืนยัน / Confirmation

| Field | Response |
|---|---|
| reviewer_name_or_signature |  |
| confirmation_date |  |
| notes |  |

## Submission Requirements

- Attach or complete the independent manual comparison.
- Record every mismatch in the discrepancy register.
- Create correction backlog entries or follow-up questions where required.
- Leave the gate at `PENDING_FINANCE_ADMIN_REVIEW` until this response is complete and signed.

## Safety Confirmation

- This response validates preview logic only.
- It does not authorize payment.
- It does not approve an advance batch.
- It does not enable final payment calculation or official export.
- Check-in remains post-duty reconciliation evidence, not an advance-payment gate.
