# Audit and Event Coverage Table
## Phase 1 Concrete Artifact

Source of truth:
- docs/architecture/AUDIT_AND_EVENT_MODEL.md
- docs/architecture/POLICY_AND_PDPA_ENFORCEMENT.md

Legend:
- Covered: explicit log action path confirmed
- Gap: known missing or partial coverage

| Domain Area | Endpoint/Operation | Expected Audit Action | Current State | Priority |
|---|---|---|---|---|
| Identity | Login | LOGIN | Covered | High |
| Identity | Logout | LOGOUT | Covered | High |
| Identity | Create user | CREATE_USER | Covered | High |
| Identity | Update user | UPDATE_USER | Covered | High |
| Identity | Deactivate user | DEACTIVATE_USER | Gap | High |
| Term lifecycle | Create period | CREATE_PERIOD | Gap | High |
| Term lifecycle | Archive period | ARCHIVE_PERIOD | Gap | High |
| Term lifecycle | Lock period | LOCK_PERIOD | Gap | High |
| Term lifecycle | Update settings | UPDATE_SETTINGS | Gap | High |
| Submissions | Submit exam | SUBMIT_EXAM | Covered/partial by flow | High |
| Submissions | Approve submission | APPROVE_SUBMISSION | Covered | High |
| Submissions | Reject submission | REJECT_SUBMISSION | Covered | High |
| Workflow | Sign workflow | SIGN_WORKFLOW | Covered | High |
| Workflow | Unlock swap window | UNLOCK_SWAP_WINDOW | Covered | High |
| Swaps | Confirm swap | CONFIRM_SWAP | Covered/partial | Medium |
| Swaps | Reject swap | REJECT_SWAP | Gap in legacy path | Medium |
| Scheduling | Delete schedule | DELETE_SCHEDULE | Gap | High |
| Co-exam | Create co-exam group | CREATE_CO_EXAM_GROUP | Gap | Medium |
| Co-exam | Update co-exam group | UPDATE_CO_EXAM_GROUP | Gap | Medium |
| External exams | Delete external exam | DELETE_EXTERNAL_EXAM | Gap | Medium |
| Import pipeline | Import commit | IMPORT_COMMIT | Covered | High |
| Export center | Export schedule/workload | EXPORT_* | Covered | Medium |
| Pickup | Generate QR | GENERATE_QR | Covered | Medium |
| Pickup | Confirm pickup | CONFIRM_PICKUP | Covered | Medium |

## Implementation Usage

1. Treat this table as the review checklist for any route mutation PR.
2. Phase 3 audit_service rollout should encode this table as actionable test assertions.
3. Gaps marked High should be prioritized before broad feature expansion.
