# HYBRID_AUTH_MODEL_CMU_AND_PRINT_SHOP.md

**Date**: 2026-05-25
**Purpose**: Define the target authentication model for both verified CMU/POLSCI users and external print-shop users without requiring implementation before the contract is verified.

---

## 1. Design Goal

EMS must support two distinct access lanes:

- Lane A: internal CMU / POLSCI authenticated users
- Lane B: external print-shop / partner users without CMU email

The two lanes must not be collapsed into one identity model.

---

## 2. Lane A - CMU / POLSCI Authenticated Users

Applies to:

- admin
- staff
- secretary
- esq_head / executive
- dept_supervisor
- teacher
- student if student integration is later enabled

Identity model:

- Auth source: POLSCI OAuth / CMU Account / MS Entra ID
- Faculty-side callback validates the auth result
- EMS mapping key: verified CMU email

Authority model:

- `cmu_email -> EMS user`
- `EMS user -> EMS role`
- `EMS role -> backend permissions`

Rules:

- Backend role enforcement is authoritative
- Frontend role state is display/navigation only
- No client-provided email is trusted
- No raw OAuth token is exposed to frontend
- EMS keeps its own session after server-side identity verification

---

## 3. Lane B - External Print Shop / Partner Users

Applies to:

- print shop
- copy center
- controlled document handling partner

Identity model:

- `partner_account_id`
- `external_username`
- `partner_org`
- optional contact email
- CMU email is optional and not required

Current code context:

- EMS already has a `print_shop` role
- EMS already has a print queue UI and backend printing endpoints
- Current code does not yet define whether the external identity source is EMS-owned or Laravel-owned

---

## 4. Allowed Permissions for Lane B

Allowed:

- view assigned print queue only
- view assigned print packages or jobs only
- update print workflow status
- acknowledge pickup, dispatch, or delivery

Forbidden:

- admin dashboards
- personnel management
- teacher dashboards
- student-facing dashboards
- governance cockpit
- broad exports
- general audit explorer access

---

## 5. Audit and PDPA Requirements

Audit events required:

- every login
- every file view or download
- every print-job state transition
- every acknowledgement event

Recommended captured context:

- EMS user or partner account ID
- route or action
- timestamp
- IP if available through the trusted server path
- user agent if available

PDPA rules:

- minimize visible personal data
- show only metadata required for print fulfillment
- prefer time-limited access for external partners
- do not give external users broad search access across student or staff data

---

## 6. Non-Negotiable Safety Rules

- Print-shop users must not be modeled as fake CMU students.
- Print-shop users must not be modeled as fake staff.
- Role mapping must remain database-authoritative.
- Frontend permission state is never authoritative.
- No raw CMU or POLSCI token reaches the browser for EMS use.

---

## 7. Implementation Gate

Do not implement Lane A until:

- callback payload is verified
- CMU email field is verified
- token lifecycle is verified
- session payload is verified

Do not implement Lane B until:

- identity owner is selected
- account source is selected
- permission matrix is approved
- audit requirements are approved

---

**End of HYBRID_AUTH_MODEL_CMU_AND_PRINT_SHOP.md**
