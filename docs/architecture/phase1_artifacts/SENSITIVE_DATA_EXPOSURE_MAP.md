# Sensitive Data Exposure Map
## Phase 1 Concrete Artifact

Source of truth:
- docs/architecture/POLICY_AND_PDPA_ENFORCEMENT.md
- docs/architecture/IMPORT_EXPORT_GOVERNANCE.md

Classification labels used here:
- High: Student identifiers, enrollment records, exam files
- Medium: Staff names, workload and compensation outputs
- Low: Aggregated operational metadata without direct identity data

| Data Surface | Sensitivity | Entry Endpoint(s) | Storage Surface | Exposure Endpoint(s) | Primary Guard |
|---|---|---|---|---|---|
| Enrollment records (student_id, full_name) | High | POST /api/import/v2/validate, POST /api/import/v2/commit | enrollment_records, import_row_logs | Admin data management and derived exports | Admin-only route dependency |
| Exam submissions and attached PDFs | High | Submission step endpoints + upload endpoints | exam_submissions, exam_submission_versions, uploads/exam_files | Tokenized PDF access and document generation | Ownership checks + token lifecycle |
| Exam access tokens and access logs | High | POST /api/pdf/token/{submission_id} | exam_access_tokens, exam_access_logs | GET /api/pdf/download/{token} | print_shop role + token validation |
| Workload and compensation exports | Medium | N/A (generated from operational records) | No new base table; derived output | /api/exports/workload-summary-pdf, /api/exports/schedule-excel, compensation export | Role-based export checks + audit logs |
| Print queue and copy counts | Medium | Print queue creation from approved/released submissions | print_queue_jobs | Print endpoints and UI surfaces | Role checks (backend + UI split today) |
| Audit records (hashed network metadata, actor IDs) | Medium | log_action writes from mutation routes | audit_logs | Admin audit export and dashboards | Admin-only read path |
| Public schedule lookup | Low to Medium | GET /api/public/schedule | Derived from schedule data | Public schedule response | Response payload minimization |

## Immediate Control Notes

1. Public schedule endpoint intentionally avoids broad identity leakage.
2. Copy-count visibility needs backend hard enforcement to match UI policy.
3. All new high-sensitivity endpoints must be added to this map before merge.
