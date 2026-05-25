# LARAVEL_AUTH_CONTRACT_COMPLETENESS_CHECKLIST.md

**Date**: 2026-05-25
**Purpose**: Gate checklist for deciding whether the Laravel/POLSCI auth contract is complete enough for EMS implementation work.

---

## Callback and Identity

- [ ] Callback path verified
- [ ] Callback method verified
- [ ] Callback parameter names verified
- [ ] Callback artifact type verified
- [ ] CMU email field name verified
- [ ] Additional identity fields verified

---

## Session and Token

- [ ] `session("USS")` key verified
- [ ] `session("USS")` field structure verified
- [ ] Token / `cmu_at` lifecycle verified
- [ ] Error callback behavior verified
- [ ] Logout behavior verified

---

## Route and Mount Strategy

- [ ] `ServiceUrl` strategy verified
- [ ] EMS callback ownership verified
- [ ] EMS mount path verified
- [ ] Separate print-shop route family approved

---

## External Print-Shop Lane

- [ ] External account owner selected
- [ ] External account storage location selected
- [ ] `print_shop` permission matrix approved
- [ ] Audit requirements approved
- [ ] PDPA-minimized visible field set approved

---

## Deployment and Database

- [ ] PostgreSQL target verified
- [ ] EMS DB ownership verified
- [ ] Reverse-proxy / Nginx ownership verified
- [ ] Session / cookie policy verified

---

## Decision Rule

If any critical item above is still open, auth bridge or external print-shop implementation must remain blocked.

---

**End of LARAVEL_AUTH_CONTRACT_COMPLETENESS_CHECKLIST.md**
