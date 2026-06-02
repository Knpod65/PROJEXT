# Advance Batch Frontend Live Smoke Results

Date: 2026-06-02

## Page Result

- Route loaded: `/invigilation-advance-batch-preview`.
- Page title rendered: `Advance Batch Preview` / `รายชื่อเตรียมเบิกค่าคุมสอบ`.
- Warning banner rendered with preview-only and not payment authorization language.
- Summary cards showed the live endpoint values.
- The roster table rendered 23 rows.
- All amount fields stayed on `PENDING_RATE_RULE`.

## Control Check

- Approve button: not present.
- Final payment button: not present.
- Official export button: not present.
- Payment-calculation wording: not present.
- Check-in is described as post-duty reconciliation evidence, not a pre-payment gate.

## Role Access

- Admin: page accessible.
- Staff: page accessible.
- Teacher: access denied on direct route.
- Print shop: access denied on direct route.

## Screenshot Evidence

- `docs/operations/demo-smoke-screenshots/advance-batch-preview-admin.png`
- `docs/operations/demo-smoke-screenshots/advance-batch-preview-staff.png`
- `docs/operations/demo-smoke-screenshots/advance-batch-preview-warning-banner.png`
