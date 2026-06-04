# Invigilation Simple Rate Manual Browser Smoke Checklist

**Date**: 2026-06-04  
**Target**: `http://127.0.0.1:3000/invigilation-rate-rules`  
**Scope**: Weekday/weekend configuration only

The prior generic draft/activate/archive lifecycle checklist is superseded by this checklist.

## Preconditions

- [ ] Current EMS `main` is clean and current.
- [ ] Backend and frontend are running from the EMS repository.
- [ ] Use local demo accounts only.

## Admin

- [ ] Page loads with the preview/configuration-only warning.
- [ ] Exactly two amount inputs are visible.
- [ ] Inputs are Monday-Friday and Saturday-Sunday.
- [ ] Fixed labels show `THB`, `PER_SESSION`, and baht per session.
- [ ] Old generic name/scope/date/lifecycle controls are absent.
- [ ] Missing, zero, negative, and nonnumeric values are visibly rejected.
- [ ] Save valid weekday/weekend values.
- [ ] Refresh and confirm both values persist.
- [ ] No payment calculation, approval, final payment, or official export action appears.

## Staff

- [ ] Staff can access the page.
- [ ] Both values are visible in selectable read-only inputs.
- [ ] Read-only mode is clearly labelled.
- [ ] Save controls are absent.

## Teacher And Print Shop

- [ ] Navigation item is absent.
- [ ] Direct route access shows access denied.

## Safety

- [ ] Advance Batch remains disconnected and `PENDING_RATE_RULE`.
- [ ] No teaching workload, Work H, `opencourse`, or `coinstruc` logic is present.
- [ ] Do not claim payment or production readiness from this configuration smoke.

