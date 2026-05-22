# LARAVEL_OWNER_REQUEST_PACKAGE.md

**Date**: 2026-05-22  
**Purpose**: Copy-paste ready request package for the IT team and Laravel code owner — to speed up the Laravel/CMU auth contract verification.

---

## 1. Why This Request Exists

EMS (Exam Management System) is preparing for a controlled pilot on the Faculty LAN Server. The faculty's primary web system uses PHP/Laravel with CMU email authentication. EMS must integrate safely with that auth system without assuming any contract details.

We need your answers to the contract questions before any integration code is written.

---

## 2. What EMS Must Not Assume

EMS must NOT assume:
- The exact callback route name or HTTP method
- The exact session key (`session("USS")` is preliminary)
- The exact structure of `cmu_at`
- The exact CMU email field name
- The EMS mount path on the Faculty LAN
- Cookie domain or SameSite policy
- How logout is coordinated between systems

**All of the above must be verified from the real Laravel codebase before we proceed.**

---

## 3. Required Answers (12 Contract Questions)

Please fill in the attached `LARAVEL_AUTH_CONTRACT_QUESTIONS.md` and return it to the EMS team. Each question has a "TBD" placeholder that must be replaced with a real answer supported by code evidence.

If any answer cannot be determined from the current codebase, say so explicitly — do not guess.

---

## 4. Requested Files / Snippets from Laravel Owner

Please provide (wherever possible):

1. **routes/web.php** — relevant auth routes (callback route prefix, logout route, any EMS-mount path)
2. **AuthMiddleware** behavior summary — how it guards routes and what it checks
3. **AuthenController callback summary** — what happens at `/callback/authen/` (or equivalent)
4. **Session structure** — exact key (`USS` or equivalent) and fields stored
5. **CMU token handling** — what `cmu_at` is, how it is created, validated, and expired
6. **CMU email field** — exact column/field name in the user model or CMU API response
7. **Logout route and behavior** — how session is cleared, whether EMS must also clear its own session
8. **Cookie/session configuration** — domain, SameSite, Secure flag, session driver
9. **PostgreSQL target** — host, port, database name, EMS schema ownership
10. **EMS route mount path** — should EMS be under `/ems`, `/exam`, a subdomain, or integrated differently?

---

## 5. Requested Meeting Agenda (30–45 min)

1. Review the 12+ contract questions together
2. Confirm EMS mount path on the faculty server
3. Agree on PostgreSQL database ownership for EMS
4. Agree on auth bridge option (Option B preferred: short-lived server-side bridge code)
5. Assign IT owner and timeline
6. Confirm DPO review path for CMU identity data

---

## 6. Deadline Placeholder

Please return the completed contract answers by: **TBD**  
(This should be set by faculty IT lead based on pilot timeline.)

---

## 7. Security Note

- **Do not send secrets, tokens, or passwords** in plain text.
- Snippets of route definitions, session config, and controller structure are sufficient.
- Any credential-related configuration should be discussed verbally in a live session, not via unencrypted message.

---

**End of LARAVEL_OWNER_REQUEST_PACKAGE.md**  
Attach this package and `LARAVEL_AUTH_CONTRACT_QUESTIONS.md` to the same request. Send to Faculty IT and Laravel code owner.