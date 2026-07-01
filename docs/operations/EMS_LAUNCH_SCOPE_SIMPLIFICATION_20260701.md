# EMS Launch-Scope Simplification Record

**Date:** 2026-07-01  
**Pass type:** Launch-scope simplification — wording + minimal UI addition  
**Follows:** Pilot readiness final smoke (commit `26a99b7`)

---

## Product Decision

The EMS is being reduced to the safest, simplest launch scope:

- **Finance** = evidence/supporting document review only. Not final payment approval. Not final authorization.
- **Paper pickup** = simple one-click confirmation per assigned exam slot. No mandatory QR scanning for launch.
- **Room arrival** = existing duty check-in surface is sufficient. No new real-time room check-in module.

---

## What Was Already Safe (No Change Needed)

| Surface | Finding |
|---------|---------|
| `payment_authorization_enabled` | Hardcoded `False` in all payment service responses. No endpoint sets it to `True`. |
| `final_export_enabled` | Hardcoded `False` in all payment service responses. |
| Draft export gate | Requires `ACCEPTED_FOR_DRAFT_EXPORT` review status before XLSX generation. |
| Export watermarks | Backend embeds "Draft for review only. Not payment authorization." in all generated files. |
| Checklist item `CHECK_FINAL_AUTHORIZATION_DISABLED` | Requires reviewer to confirm final auth is NOT enabled. |
| Payment draft warning banners | EN and TH both include explicit negations on every payment-related page. |
| `paymentDraft.warning.title` | "Draft only - not payment authorization." |

All safety architecture is intact. This pass makes no logic changes to the payment system.

---

## Changes Made

### A. Finance Evidence Status Label (i18n only)

**Problem**: Status `FINAL_AUTHORIZATION_REQUIRED` appeared as a red/crimson badge and read:
- EN (before): `"Final authorization still required"`
- TH (before): `"ยังต้องมีการอนุมัติขั้นสุดท้าย"`

This sounded like the system was waiting to grant final payment approval.

**Change**: Display strings renamed. Backend enum value `FINAL_AUTHORIZATION_REQUIRED` unchanged (DB data preserved):
- EN (after): `"Requires additional review before any authorization"`
- TH (after): `"ต้องผ่านการตรวจเพิ่มเติมก่อนการอนุมัติใด ๆ"`

File: `frontend/src/i18n/en.ts` — key `paymentDraft.status.FINAL_AUTHORIZATION_REQUIRED`  
File: `frontend/src/i18n/th.ts` — same key

### B. Finance Roster Explanation (i18n only)

**Problem**: EN explanation had only one negation ("does not authorize payment"). TH was clearer but EN could be stronger.

**Change** (EN): `"This file is for supporting evidence, headcount, and signature verification only. It is not a payment authorization and not a final authorization document."`

**Change** (TH): `"ไฟล์นี้ใช้เป็นหลักฐานประกอบการตรวจ ตรวจรายชื่อ จำนวนหัว และลายเซ็นเท่านั้น ไม่ใช่การอนุมัติเบิกจ่าย และไม่ใช่เอกสารอนุมัติขั้นสุดท้าย"`

File: `frontend/src/i18n/en.ts` — key `paymentDraft.financeRoster.explanation`  
File: `frontend/src/i18n/th.ts` — same key

### C. Simple Paper Pickup Confirmation (frontend only)

**Problem**: The QR Pickup tab showed only an empty state for non-manager users (staff, teachers). The only pickup path required `BarcodeDetector` API + camera.

**Change**: For non-manager users who have assigned schedules on the selected date:
- Show a simple list of exam slots with a "มารับข้อสอบแล้ว / Picked up exam papers" button per slot
- Button calls existing `POST /api/checkins` with `checkin_type: "receive_papers"` (already in backend)
- On success: button replaced by green "Confirmed / ยืนยันแล้ว" badge (session-state only)
- If no schedules for that date: original empty state shown (unchanged)

No GPS required. No camera. No QR required. No new backend endpoint.

File: `frontend/src/pages/Checkins.tsx`  
New i18n keys:
- `checkins.pickup.simpleConfirmButton` → "Picked up exam papers" / "มารับข้อสอบแล้ว"
- `checkins.pickup.alreadyConfirmed` → "Confirmed" / "ยืนยันแล้ว"
- `checkins.pickup.simpleConfirmNote` → "Record that you have received the exam papers for your assigned slots." / "บันทึกว่าท่านได้รับข้อสอบสำหรับช่วงเวลาที่ได้รับมอบหมาย"

### D. Room Duty Check-In (no change)

**Finding**: The "Room Operations" tab already handles `at_room` check-ins with:
- Students present count
- Late count
- Notes
- Multi-party confirmation

This IS the room duty report. No new module needed. No wording change was required — the existing labels are clear enough for launch.

---

## What Was Intentionally Skipped

| Item | Decision | Reason |
|------|----------|--------|
| QR pickup regeneration/simplification | SKIP | QR scanner already works for those who use it; simple confirm added as alternative |
| Edit/clear for check-ins | SKIP | Backend is append-only by design (audit-first); unique constraint `(schedule_id, user_id, checkin_type)` prevents duplicates; corrections require admin |
| Room arrival as separate surface | SKIP | Existing `at_room` check-in already serves this purpose |
| New duty reporting module | SKIP | Not in existing codebase; would be a new large feature |
| Admin View As | NOT TOUCHED | Remains invalid; not used for role review |
| Real-time geolocation check-in | SKIP | GPS already captured optionally in notes; no new location system |
| Print queue handoff workflow | SKIP | Already works; no change needed |
| Complex QR camera flow | UNCHANGED | Still available for those who prefer it; simple confirm is an additional path |

---

## Role Responsibilities at Launch

| Role | Finance evidence review | Paper pickup confirm | Room duty report |
|------|------------------------|----------------------|-----------------|
| Admin | View + record review | Can manage pickup QR + monitor | Full access |
| ESQ Head / Secretary | View + record review decision | Monitor only | View |
| Dept Supervisor | View only | Monitor only | View |
| Staff | View + flag for review | Simple confirm button | Record at_room check-in |
| Teacher | View only | Simple confirm button | Record at_room check-in |
| Print Shop | Not applicable | Not applicable | Not applicable |

---

## Safety Boundaries (Unchanged)

- Final payment approval: NOT IMPLEMENTED. `payment_authorization_enabled` remains hardcoded `False`.
- Final authorization: NOT IMPLEMENTED. `final_export_enabled` remains hardcoded `False`.
- Payment logic: UNCHANGED.
- Export gates: UNCHANGED.
- Route guards: UNCHANGED.
- Permissions: UNCHANGED.
- Scheduling/workload logic: UNCHANGED.

---

## Known Launch Limitations

1. **Paper pickup correction**: If a pickup was confirmed incorrectly, there is no self-service undo. The `CheckinEvent` record is permanent once created. Admin must handle corrections directly.

2. **Pickup confirmation is session-state only**: The "Confirmed" badge on the simple pickup confirm card resets on page reload. The underlying `CheckinEvent` record is preserved in the database; the UI just doesn't reload it after page refresh.

3. **Secretary demo credential**: Not in the RUNBOOK quick-start table. A secretary account exists in `seed.py` but was not tested in the role smoke.

4. **Thai export/font pass**: Pending. If Thai official document exports (PDF/Excel with Thai fonts) are required before pilot, this must be completed separately.

5. **Finance review of supporting roster**: Pending acceptance by Finance stakeholder.

6. **Admin View As**: Not valid for role review. Must not be used.
