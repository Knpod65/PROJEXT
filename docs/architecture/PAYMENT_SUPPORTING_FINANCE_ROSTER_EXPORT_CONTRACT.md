# Payment Supporting Finance Roster Export — API Contract

**Date**: 2026-06-12
**Export name**: `DRAFT_FINANCE_INVIGILATION_ROSTER_XLSX`
**Status**: DESIGN — not yet implemented
**Implementation gate**: `HOLD_PENDING_OPTIMIZE_ROSTER_SOURCE_CONFIRMATION`

---

## Purpose

This export supports finance counting, signature/payment form checking, and bridges the optimized
invigilation assignment and the reimbursement announcement forms. It is **not** a final payment
approval document.

It accompanies the accepted RC1 draft XLSX summary (`DRAFT_FINANCE_INVIGILATION_ROSTER_XLSX`
complements, does not replace, the existing summary export).

---

## Draft Labels (Required on Every Sheet)

**Thai (primary)**:
`ร่างเอกสารประกอบการตรวจนับค่าตอบแทน ยังไม่ใช่เอกสารอนุมัติเบิกจ่าย`

**English (secondary)**:
`Draft supporting roster for payment checking only. Not payment authorization.`

These labels must appear on every sheet as a prominent banner row. They must not be footnotes.

---

## Endpoint (Future Implementation)

```
POST /api/invigilation-advance-batch/finance-support-roster-export
```

**Auth**: `require_view_all` — admin/esq_head/secretary pass; staff/teacher/print_shop → 403

---

## Request Schema

```json
{
  "academic_year": "string",
  "semester": "string",
  "exam_type": "string",
  "period_id": "int | null",
  "export_format": "XLSX_DRAFT",
  "include_trace_detail": true,
  "include_signature_check_sheet": true
}
```

`export_format` must be `XLSX_DRAFT`. No other format is permitted in this pass.

---

## Response

- `StreamingResponse` with `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `Content-Disposition: attachment; filename="<filename>"`
- No JSON body; blob only

**Response metadata embedded in Sheet 2**:
```
export_status: DRAFT_SUPPORTING_EXPORT_ONLY
payment_authorization_enabled: false
final_export_enabled: false
document_status: DRAFT_NOT_AUTHORIZED
```

---

## Filename Convention

```
EMS_DRAFT_FINANCE_ROSTER_{semester}-{academic_year}_{YYYYMMDD_HHMM}.xlsx
```

Example: `EMS_DRAFT_FINANCE_ROSTER_2-2568_20260612_1430.xlsx`

---

## Export Gate (Preconditions)

All of the following must be true before any xlsx bytes are generated:

| # | Condition | Required value |
|---|---|---|
| 1 | Review status | `ACCEPTED_FOR_DRAFT_EXPORT` with non-empty comment |
| 2 | Settings source status | `CONFIGURED` |
| 3 | Settings status | `ACTIVE_FOR_DRAFT_PREVIEW` |
| 4 | Calculation status | `CALCULATED_FROM_SETTINGS` |
| 5 | Paper distribution responsible group | Non-empty |
| 6 | `payment_authorization_enabled` | `false` |
| 7 | `final_export_enabled` | `false` |
| 8 | Optimization assignments present | At least one `Supervision` row for the scope |

Any failure → HTTP 400 with a specific error message. Do not generate partial xlsx on gate failure.

---

## Workbook Structure

### Sheet 1 — `สรุปตามวันและช่วงเวลา`

**One row per `exam_date + time_slot`.** Do not break out by room/course/section in this sheet.

Banner rows 1–3: draft label (TH, EN, `DRAFT_NOT_AUTHORIZED`) — highlighted yellow.

| Column | Thai label | Notes |
|--------|-----------|-------|
| A | วันที่สอบ | ISO date |
| B | วันในสัปดาห์ | Mon–Sun (Thai) |
| C | ประเภทวัน | วันทำการ / วันหยุด |
| D | ช่วงเวลา | e.g. 09:00–12:00 |
| E | จำนวนห้องสอบ | Physical room count in slot |
| F | จำนวนวิชา/section | Distinct ExamSchedule rows |
| G | จำนวน นศ. รวม | Sum of Section.num_students |
| H | จำนวนกรรมการคุมสอบ/เปิดห้อง | Distinct Supervision persons (pending duplicate-count policy) |
| I | จำนวนกรรมการจ่ายข้อสอบที่ผูกห้อง | Paper-dist persons with room binding |
| J | จำนวนหัวรวมสำหรับตรวจเบิก | H + I |
| K | อัตรา | weekday/weekend rate from settings |
| L | รวมเงินคุมสอบ/เปิดห้อง | H × rate |
| M | รวมเงินจ่ายข้อสอบที่ผูกห้อง | I × rate |
| N | รวมเงินทั้งช่วงเวลา | L + M |
| O | หมายเหตุ | Flags: online-excluded, room-count-insufficient, extra-paper-dist |

Footer row after data: `ร่างเพื่อการตรวจทาน ไม่ใช่เอกสารอนุมัติเบิกจ่าย` — highlighted yellow.

---

### Sheet 2 — `รายชื่อประกอบการเบิก`

**One row per person per `exam_date + time_slot`.**

Banner rows 1–3: draft label.

| Column | Thai label | Notes |
|--------|-----------|-------|
| A | วันที่สอบ | |
| B | วันในสัปดาห์ | |
| C | ประเภทวัน | |
| D | ช่วงเวลา | |
| E | ชื่อ-นามสกุล | From User record |
| F | บทบาทในช่วงเวลานี้ | กรรมการคุมสอบ / ผู้เปิดห้อง / กรรมการจ่ายข้อสอบที่ผูกห้อง |
| G | ห้องที่เกี่ยวข้อง | Room code(s); multiple rooms joined with ", " |
| H | วิชา/section ย่อ | Abbreviated for readability; full detail in Sheet 4 |
| I | จำนวนครั้งที่นับเบิก | 1 (pending duplicate-count policy confirmation) |
| J | อัตรา | From payment settings |
| K | จำนวนเงิน | I × J |
| L | แหล่งที่มา | Supervision / PaperDistributionAssignment / manual |
| M | หมายเหตุ | Override flags |
| N | ช่องตรวจลายเซ็น | Blank — for human signature checking |

---

### Sheet 3 — `การผูกคนจ่ายข้อสอบกับห้อง`

**One row per paper-distribution-to-room assignment.**

Banner rows 1–3: draft label.

| Column | Thai label | Notes |
|--------|-----------|-------|
| A | วันที่สอบ | |
| B | ช่วงเวลา | |
| C | ลำดับห้องตามจำนวน นศ. | 1 = largest, 2 = second largest |
| D | รหัสห้อง | Room.code |
| E | จำนวน นศ. ในห้อง | Section.num_students for this room |
| F | วิชา/section ในห้อง | Course + section codes |
| G | ชื่อกรรมการจ่ายข้อสอบ | Assigned paper-dist person name |
| H | เหตุผลการผูกห้อง | top-1-by-student-count / top-2-by-student-count / tie-break-room-code-asc / only-eligible-room |
| I | หมายเหตุ | insufficient-rooms / extra-persons / no-eligible-rooms-online-only |

**Paper-to-room assignment rule** (algorithm Step D):
1. Rank physical rooms in slot by `Section.num_students DESC`
2. Tie-break: room code ASC → course code ASC → section ASC
3. Assign paper-dist person 1 → rank 1 room; person 2 → rank 2 room
4. If only 1 room: assign 1 person; flag "insufficient physical rooms"
5. If 0 rooms: flag "no eligible rooms"
6. If >2 persons: flag extra persons for review

---

### Sheet 4 — `รายละเอียดอ้างอิง`

**One row per source ExamSchedule row (room/course/section).**

Banner rows 1–3: draft label.

| Column | Thai label | Notes |
|--------|-----------|-------|
| A | วันที่สอบ | |
| B | ช่วงเวลา | |
| C | กระบวนวิชา | Course code |
| D | section | Section identifier |
| E | อาจารย์ผู้สอน | Instructor name if available |
| F | จำนวน นศ. | Section.num_students |
| G | ห้อง | Room.code |
| H | กรรมการคุมสอบจากแหล่งข้อมูล | Supervision.user names for this schedule |
| I | กรรมการจ่ายข้อสอบจากแหล่งข้อมูล | PaperDistributionAssignment.user name (if available) |
| J | source schedule id | ExamSchedule.id |
| K | สถานะ | ExamSchedule.status |
| L | หมายเหตุ | excluded-online / external-exam / no-invigilation-assigned |

---

## Safety Invariants

| Flag | Required value | Enforcement |
|------|---------------|-------------|
| `payment_authorization_enabled` | `false` | Hard-coded in export service; gate rejects if True |
| `final_export_enabled` | `false` | Hard-coded in export service; gate rejects if True |
| `document_status` | `DRAFT_NOT_AUTHORIZED` | Banner row on every sheet |
| `export_status` | `DRAFT_SUPPORTING_EXPORT_ONLY` | Embedded in Sheet 2 metadata block |

---

## Role Access Table

| Role | Access |
|------|--------|
| admin | Allowed — HTTP 200 + xlsx |
| esq_head | Allowed — HTTP 200 + xlsx |
| secretary | Allowed — HTTP 200 + xlsx |
| staff | Blocked — HTTP 403 |
| teacher | Blocked — HTTP 403 |
| print_shop | Blocked — HTTP 403 |
| unauthenticated | HTTP 401/422 |

---

## Blocked Items (Not Part of This Export)

| Item | Status |
|------|--------|
| Final payment approval | BLOCKED |
| Official final export | BLOCKED |
| Payment authorization | BLOCKED |
| Payment release workflow | BLOCKED |
| Final payment truth record | BLOCKED |
| Export that bypasses `DRAFT_NOT_AUTHORIZED` | Permanently prohibited |
| Teaching workload / Work H / opencourse / coinstruc | Out of scope |

---

## Related Documents

- `PAYMENT_SUPPORTING_FINANCE_ROSTER_SOURCE_REVIEW.md` — confirmed source tables and gaps
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_ALGORITHM.md` — step-by-step algorithm
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_IMPLEMENTATION_GATE.md` — implementation gate and open items
- `PAYMENT_DOCUMENT_DRAFT_EXPORT_API_CONTRACT.md` — existing summary XLSX contract
