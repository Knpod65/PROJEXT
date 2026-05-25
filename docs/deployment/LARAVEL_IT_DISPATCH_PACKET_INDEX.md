# LARAVEL_IT_DISPATCH_PACKET_INDEX.md

**Date**: 2026-05-25  
**Purpose**: Exact index of what to send to Faculty IT / Laravel owner for auth contract verification.

## 1. Why This Packet Exists

The standalone EMS demo (98/100) has been successfully validated with real interactive browser testing. The single largest remaining blocker to any Faculty LAN pilot is the unverified Laravel / POLSCI OAuth / external auth contract.

This packet asks the precise questions that must be answered before any auth bridge code can be written (per AUTH_BRIDGE_IMPLEMENTATION_GATE.md).

## 2. What EMS Needs from IT / Laravel Owner

- Verified structure of the identity payload EMS will receive
- Verified callback / redirect behavior
- Verified session / token lifecycle
- Verified CMU email field mapping (for identity + PDPA)
- Verified EMS mount path / ServiceUrl policy
- Verified PostgreSQL target + ownership
- Verified strategy for non-CMU (print-shop) users
- Verified logout behavior

## 3. Documents to Send (in this order)

1. LARAVEL_IT_REQUEST_MESSAGE_READY_TO_SEND.md (Thai + English cover message)
2. LARAVEL_AUTH_CONTRACT_QUESTIONS.md (primary 203-line question set)
3. LARAVEL_AUTH_CONTRACT_CLOSURE_TRACKER.md (tracker for answers)
4. LARAVEL_OWNER_REQUEST_PACKAGE.md
5. LARAVEL_OWNER_HANDOFF_CHECKLIST.md
6. LARAVEL_AUTH_CONTRACT_COMPLETENESS_CHECKLIST.md
7. POLSCI_OAUTH_FLOW_ANALYSIS.md
8. FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md
9. HYBRID_AUTH_MODEL_CMU_AND_PRINT_SHOP.md

## 4. Questions That Must Be Answered

See LARAVEL_AUTH_CONTRACT_QUESTIONS.md sections:
- Routes & callbacks
- session("USS") payload
- cmu_at / token details
- CMU email field
- ServiceUrl / mount path
- PostgreSQL target
- Print-shop external lane
- Logout behavior

## 5. What NOT to Send

- Any real secrets, passwords, tokens, or .env files
- Production database credentials
- Internal network diagrams with sensitive details
- Raw source code of the current EMS implementation (send only the spec and questions)

## 6. What Happens After Answers Return

See LARAVEL_CONTRACT_RESPONSE_PROCESS.md

Auth bridge implementation may begin **only** after:
- All critical questions have verified answers
- Completeness checklist is passed
- Security / architecture reviewer accepts the design
- Leadership has chosen the bridge option

**Never start bridge code on assumptions.**

---
*Send this packet. Wait for real answers. Then decide.*
