# LAN_TO_FACULTY_WEB_PORTAL_TERMINOLOGY_AUDIT.md

**Date**: 2026-05-25  
**Pass**: EMS FACULTY WEB PORTAL DEPLOYMENT + SYSTEM COMPLETION PASS

## Summary of Findings

A broad search across docs/ for "Faculty LAN", "LAN Server", "LAN pilot", "LAN-only", "Faculty LAN Server" returned 211+ matches across ~40+ files.

The language is pervasive in:
- Readiness scorecards and summaries
- Post-demo decision/tracker docs
- Deployment and auth specs
- Demo limitation and stakeholder materials
- Design handoff sources
- Historical pilot/UAT docs

## Document-by-Document Assessment (High-Impact Files)

**Must Update Now (core current-state documents):**

1. EMS_100_PERCENT_READINESS_EXECUTIVE_SUMMARY.md
   - Current: "Controlled Faculty LAN Pilot 100%"
   - Action: Reframe to "Faculty Web Portal Integration Pilot 100%"
   - Keep historical note for prior LAN planning

2. EMS_100_PERCENT_MASTER_SCORECARD.md
   - Current: "Laravel / Faculty LAN" column
   - Action: Rename column to "Laravel / Faculty Web Portal Integration"

3. LARAVEL_FACULTY_LAN_100_PERCENT_READINESS_SCORE.md (entire file)
   - Current: Title and all content use "Faculty LAN"
   - Action: Rename file to LARAVEL_FACULTY_WEB_PORTAL_100_PERCENT_READINESS_SCORE.md (or keep old as historical and create new reframed version). Update all table entries.

4. PILOT_100_PERCENT_READINESS_SCORE.md
   - Definition uses "Controlled Faculty LAN Pilot"
   - Action: Update definition and title references to Faculty Web Portal.

5. POST_DEMO_* docs (DECISION_MATRIX, NEXT_PHASE_OPTIONS, 48_HOUR_TRACKER, SOURCE_REVIEW, DECISION_CAPTURE)
   - Multiple "Faculty LAN pilot", "Faculty LAN server"
   - Action: Replace with "Faculty Web Portal integration/pilot/deployment" where referring to future target.

6. DEMO_LIMITATIONS_AND_DISCLOSURE.md, EMS_STAKEHOLDER_DEMO_ONE_PAGER.md, STAKEHOLDER_DEMO_SCRIPT.md, DEMO_DAY_RUNBOOK.md, etc.
   - "Faculty LAN" used in limitations and Q&A
   - Action: Update to "Faculty Web Portal" + note that previous planning used LAN terminology.

7. Deployment specs:
   - FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md
   - PILOT_ROUTE_AND_AUTH_MAPPING.md
   - LARAVEL_OWNER_REQUEST_MEMO_TH_EN.md
   - LARAVEL_IT_DISPATCH_PACKET_INDEX.md
   - LARAVEL_IT_REQUEST_MESSAGE_READY_TO_SEND.md (Thai/English)
   - Action: Replace "Faculty LAN Server" / "Faculty LAN" with "Faculty Web Portal / Faculty web hosting environment". Keep the actual technical questions intact.

8. Auth bridge docs:
   - EMS_AUTH_BRIDGE_DESIGN.md
   - AUTH_BRIDGE_IMPLEMENTATION_GATE.md
   - HYBRID_AUTH_MODEL_CMU_AND_PRINT_SHOP.md
   - Action: Update framing from "Faculty LAN Server" to "Faculty Web Portal".

**Keep as Historical (with note):**

- Older design handoff sources (CLAUDE_DESIGN_*, EMS_DESIGN_* in design/ and sources/)
- UAT_GO_NO_GO_REPORT.md, PILOT_BLOCKER_DASHBOARD.md (pre-pivot planning)
- DEMO_AUTH_AND_PRINT_SHOP_SCOPE.md
- SYSTEM_100_PERCENT_READINESS_SOURCE_REVIEW.md and older audits

Add a standard note at top of historical files:
"Note (2026-05-25): Target environment pivoted from Faculty LAN Server to Faculty Web Portal integration. This document reflects planning at the time of writing."

**Low-Impact / Already Mostly Abstract:**

- Pure code audits (backend/frontend compatibility) — mostly use "web portal" or neutral terms already in recent files.
- Some performance and security scores have isolated references.

## Risks if Left Unchanged

- Confusion for new readers / IT recipients: "Is this still a LAN-only app?"
- Stakeholder materials may accidentally imply old topology.
- Future maintainers may copy outdated mount path / proxy assumptions.
- Design handoff package may mislead redesign team about deployment context.

## Recommended Replacement Wording (Consistent Glossary)

- Old: Faculty LAN Server / Faculty LAN
- New: Faculty Web Portal / Faculty web hosting environment / Faculty Web Portal deployment target

- Old: LAN pilot / Faculty LAN pilot
- New: Faculty Web Portal integration pilot

- Old: LAN-only access
- New: Controlled faculty web access (with external partner lane for print shop)

- Old: Faculty server
- New: Faculty web hosting environment

## Action Plan for This Pass

1. Update all high-impact operational/deployment/auth docs (this pass)
2. Rename/reframe the main LAN score file
3. Add historical notes to design sources and old pilot docs
4. Update readiness scorecards and executive summary
5. Ensure new docs created in this pass (deployment architecture, checklist, roadmap, etc.) use only the new terminology

No mass string replace — manual review per file for context.

---
*Terminology pivot is cosmetic in the short term but critical for clarity when handing materials to IT/Laravel owners and future maintainers.*
