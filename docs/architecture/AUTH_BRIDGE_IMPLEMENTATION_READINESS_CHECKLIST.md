# AUTH_BRIDGE_IMPLEMENTATION_READINESS_CHECKLIST.md

**Date**: 2026-05-25
**Purpose**: Execution readiness checklist for any future EMS auth bridge implementation work.

---

## CMU / POLSCI Lane

- [ ] POLSCI callback contract verified
- [ ] Callback parameter names verified
- [ ] CMU email field verified
- [ ] `session("USS")` payload verified
- [ ] Token lifecycle verified
- [ ] EMS mount path verified
- [ ] Laravel-to-EMS bridge boundary selected

---

## External Print-Shop Lane

- [ ] External identity owner selected
- [ ] External account source selected
- [ ] Print-shop route family approved
- [ ] `print_shop` permission matrix approved
- [ ] Audit event list approved
- [ ] PDPA-minimized field set approved

---

## Shared Safety Checks

- [ ] No frontend token handling
- [ ] No client-trusted email
- [ ] No client-trusted role
- [ ] EMS role mapping remains DB-authoritative
- [ ] Logging plan excludes raw tokens and raw session payload
- [ ] Logout behavior agreed
- [ ] Test plan drafted before code work begins

---

## Readiness Rule

If any item above is still open, implementation must not begin.

---

**End of AUTH_BRIDGE_IMPLEMENTATION_READINESS_CHECKLIST.md**
