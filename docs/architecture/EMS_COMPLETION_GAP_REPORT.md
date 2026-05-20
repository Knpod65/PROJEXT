# EMS_COMPLETION_GAP_REPORT

## Known Gaps After U1 Completion

### Frontend
- **Legacy pages:** Checkins, MyExam, Optimizer, RoomManagementV2, WorkflowV2, External may still contain inline orchestration
- **Raw string scanner:** ~100 candidates (pre-existing patterns, scanner remains noisy)
- **Presenter overlap:** Some presenters may duplicate logic in legacy `utils/format.ts`
- **Presenter adoption:** Minor adoption needed in remaining hooks
- **Workload Duty Analytics:** Core page, i18n cleanup, empty states, and supporting docs are complete; remaining work is QA evidence and future performance hardening only

### i18n
- Raw string scanner remains noisy (false positives)
- Backend message_key adoption is partial
- Some legacy pages may contain raw strings

### Backend
- Some routers still need service/repository/policy extraction (L2.3+)

### P1 Pilot Readiness
- **UAT pending** - test script created, pilot users needed
- **IT handoff pending** - docs created, operational setup needed
- **PDPA sign-off pending** - review package created, DPO approval needed
- **Workload Duty Analytics browser verification pending** - checklist and smoke-plan docs exist; live browser evidence still needs capture

---

**Frontend ViewModel (U1):** COMPLETE  
**Authorization Alignment (L5):** COMPLETE  
**OPS-DASH Workload Duty Analytics:** COMPLETE for controlled pilot  
**Pilot Readiness (P1):** COMPLETE (docs ready, operational handoff pending)

---

*See FRONTEND_VIEWMODEL_COMPLETION_REPORT.md for full U1 status.*
