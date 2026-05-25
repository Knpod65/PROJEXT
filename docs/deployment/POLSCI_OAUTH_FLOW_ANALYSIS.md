# POLSCI_OAUTH_FLOW_ANALYSIS.md

**Date**: 2026-05-25
**Purpose**: Record the observed POLSCI OAuth login pattern and define what EMS may and may not assume before the Laravel/POLSCI callback contract is verified.

---

## 1. Raw URL

```text
https://account.pol.cmu.ac.th/oauth/login?ServiceUrl=https%3A%2F%2Fportal.mis.pol.cmu.ac.th%2Foauth%2Fcallback
```

---

## 2. Decoded URL

| Component | Value |
|---|---|
| Login endpoint | `https://account.pol.cmu.ac.th/oauth/login` |
| `ServiceUrl` callback | `https://portal.mis.pol.cmu.ac.th/oauth/callback` |

---

## 3. Endpoint Analysis

- The login page is hosted by the POLSCI account system, not by EMS.
- The observed `ServiceUrl` points back to the faculty portal callback, not to EMS.
- The login page wording indicates the actual human identity provider is CMU Account / MS Entra ID behind the POLSCI gateway.

---

## 4. ServiceUrl Explanation

`ServiceUrl` appears to be the browser return target after successful or failed login. Based on the observed URL, the faculty portal currently owns that callback path.

What this means for EMS:

- EMS should not assume it can parse the original OAuth callback directly.
- EMS should be designed to integrate after faculty-side server validation unless the Laravel owner confirms a different contract.

---

## 5. Expected Browser Redirect Sequence

1. User requests a protected faculty or EMS-related route.
2. Faculty-side auth redirects browser to `https://account.pol.cmu.ac.th/oauth/login`.
3. User signs in with CMU Account / MS Entra ID.
4. POLSCI OAuth redirects browser to the configured `ServiceUrl`.
5. Faculty portal callback receives the auth result.
6. Faculty-side server validates the auth result.
7. Faculty-side server creates or refreshes its own session.
8. EMS should receive only verified identity or a one-time bridge artifact from that point forward.

---

## 6. What Is Confirmed

- A POLSCI OAuth gateway exists.
- The observed user-facing login is CMU Account / MS Entra ID based.
- The observed callback target is a faculty portal callback.

---

## 7. What Is Still Unknown

- Callback payload shape
- Callback parameter names
- Whether the callback receives a `code`, token, ticket, `cmu_at`, or another artifact
- Session payload structure
- CMU email field name
- Token lifecycle
- Error callback format
- Logout behavior
- Role mapping behavior

---

## 8. Security Assumptions That Are NOT Allowed

- Do not assume callback parameter names.
- Do not assume `cmu_at` exists.
- Do not expose any OAuth token or callback artifact to the EMS frontend.
- Do not trust email from a query string.
- Do not trust role from the frontend.
- Do not assume `ServiceUrl` can be changed for EMS until the owner confirms it.

---

## 9. Required Questions for Laravel Owner

1. What exact fields arrive at the callback?
2. Is the callback GET or POST?
3. Is `ServiceUrl` allowlisted?
4. Can EMS use its own callback path, or must the faculty portal terminate the callback first?
5. What verified identity fields are available after callback validation?
6. What happens on login denial or expiry?
7. How is logout coordinated?

---

## 10. EMS Integration Implication

Safest current interpretation:

- Laravel or faculty-side server validates the POLSCI callback first.
- EMS consumes only a verified identity signal or one-time bridge artifact after that validation.
- EMS must keep role mapping DB-authoritative.
- No EMS bridge code should be written until the callback contract is verified.

---

**End of POLSCI_OAUTH_FLOW_ANALYSIS.md**
