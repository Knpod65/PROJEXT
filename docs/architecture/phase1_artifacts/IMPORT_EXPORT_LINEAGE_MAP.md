# Import and Export Lineage Map
## Phase 1 Concrete Artifact

Source of truth:
- docs/architecture/IMPORT_EXPORT_GOVERNANCE.md
- docs/architecture/EMS_ARCHITECTURE_MAP.md

This map tracks lineage from ingestion, through storage, to downstream exports and operational consumers.

## Import Lineage

| Import Type | Ingest Endpoint | Pipeline Path | Primary Tables Written | Downstream Consumers |
|---|---|---|---|---|
| OpenCourse sections | POST /api/import/v2/start -> validate -> commit | parsers -> validators -> normalizers -> importer | courses, sections | scheduling, submissions, exports, workflow optimizer |
| Enrollment | POST /api/import/v2/start -> validate -> commit | parsers -> validators -> normalizers -> importer | enrollment_records, sections.num_students | scheduling capacity checks, submission prep, analytics |
| Personnel | POST /api/import/v2/start -> validate -> commit | parsers -> validators -> normalizers -> importer | users | workflow assignment, dashboard, exports |
| Room capacity | POST /api/import/v2/start -> validate -> commit | parsers -> validators -> normalizers -> importer | rooms | scheduling and optimizer feasibility |
| Historical schedule | Historical import path | specialized importer path | historical_schedule_batches, historical_schedule_entries, related historical tables | historical comparison dashboards and analytics |

## Export Lineage

| Export Surface | Endpoint | Upstream Data Sources | Output Format | Audit Expectation |
|---|---|---|---|---|
| Exam schedule | GET /api/exports/schedule | exam_schedules, sections, rooms, users | PDF | EXPORT_SCHEDULE_PDF |
| Workload summary | GET /api/exports/workload-summary-pdf | supervisions, users, schedules | PDF | EXPORT_WORKLOAD_PDF |
| Workload spreadsheet | GET /api/exports/schedule-excel | supervisions, users, schedules | XLSX | EXPORT_WORKLOAD_EXCEL |
| Submission summary | GET /api/exports/submissions-excel | exam_submissions, sections, users | XLSX | Export audit required |
| Exam document generation | POST /api/documents/generate/{id} | exam_submissions, templates, related metadata | PDF | GENERATE_EXAM_PDF |
| Tokenized exam file download | GET /api/pdf/download/{token} | exam_access_tokens, uploaded files | PDF binary | Access log + audit trail |

## Lineage Integrity Checks

1. Every committed import row must be traceable via import_session_id.
2. Every export endpoint involving PII or operational records must emit an audit action.
3. Period resolution for export must be canonicalized in a single resolver (Phase 2 task).
