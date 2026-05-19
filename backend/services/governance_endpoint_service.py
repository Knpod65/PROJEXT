"""
governance_endpoint_service.py — orchestration for governance endpoints.

Owns:
- governance overview shaping
- lifecycle timeline shaping
- publication readiness response shaping
- blocker summary shaping
- capability response shaping
"""
from typing import Any, Optional
from sqlalchemy.orm import Session, joinedload
import models
from services.optimization_report_builder import build_optimization_report
from services.schedule_state_machine import derive_schedule_state, schedule_state_machine
from services.publication_governance_service import assess_publication_readiness
from services.schedule_capability_service import compute_schedule_capabilities
from services.executive_risk_service import compute_executive_risk_report
from services.schedule_transition_service import attempt_transition


class GovernanceEndpointService:
    """Orchestration for governance endpoints."""

    @staticmethod
    def _load_session_and_period(db: Session, session_id: int):
        session = db.query(models.OptimizeSession).filter(
            models.OptimizeSession.id == session_id
        ).first()
        if not session:
            from fastapi import HTTPException
            raise HTTPException(404, "Session not found")
        return session, session.period

    @staticmethod
    def _load_schedules(db: Session, period) -> list:
        return (
            db.query(models.ExamSchedule)
            .join(models.Section)
            .filter(
                models.Section.academic_year == period.academic_year,
                models.Section.semester == period.semester,
                models.ExamSchedule.exam_type == period.exam_type,
            )
            .options(
                joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
                joinedload(models.ExamSchedule.room),
                joinedload(models.ExamSchedule.supervisions),
            )
            .all()
        )

    @staticmethod
    def _build_report(db: Session, session_id: int) -> tuple:
        session, period = GovernanceEndpointService._load_session_and_period(db, session_id)
        schedules = GovernanceEndpointService._load_schedules(db, period)
        report = build_optimization_report(period=period, schedules=schedules)
        governance_state = report.get("governance", {}).get("governance_state", "")
        derived_state = derive_schedule_state(session.status, governance_state)
        return report, session, period, derived_state

    @staticmethod
    def get_governance_report(db: Session, session_id: int) -> dict[str, Any]:
        report, session, period, derived_state = GovernanceEndpointService._build_report(db, session_id)
        report["derived_schedule_state"] = derived_state
        report["valid_next_states"] = schedule_state_machine.valid_next_states(derived_state)
        report["session_status"] = session.status
        return report

    @staticmethod
    def get_publication_readiness(db: Session, session_id: int) -> dict[str, Any]:
        from dataclasses import asdict
        report, session, period, derived_state = GovernanceEndpointService._build_report(db, session_id)
        readiness = assess_publication_readiness(
            quality_report=report.get("quality_breakdown", {}),
            governance=report.get("governance", {}),
            recheck_summary=report.get("severity_summary", {}),
            schedule_state=derived_state,
        )
        result = asdict(readiness)
        result["derived_schedule_state"] = derived_state
        result["valid_next_states"] = schedule_state_machine.valid_next_states(derived_state)
        result["session_status"] = session.status
        return result

    @staticmethod
    def get_session_capabilities(
        db: Session,
        session_id: int,
        user_role: str,
    ) -> dict[str, Any]:
        from dataclasses import asdict
        report, session, period, derived_state = GovernanceEndpointService._build_report(db, session_id)
        recheck_summary = report.get("severity_summary", {})
        hard_fail_count = int(recheck_summary.get("hard_fail_count", recheck_summary.get("hard_error_count", 0)))

        readiness = assess_publication_readiness(
            quality_report=report.get("quality_breakdown", {}),
            governance=report.get("governance", {}),
            recheck_summary=recheck_summary,
            schedule_state=derived_state,
        )
        blocker_codes = [
            b.get("code", "") for b in (readiness.blockers or []) if isinstance(b, dict)
        ]

        return compute_schedule_capabilities(
            derived_schedule_state=derived_state,
            governance_state=report.get("governance", {}).get("governance_state", ""),
            session_status=session.status,
            user_role=user_role,
            can_publish=readiness.can_publish,
            risk_score=readiness.risk_score,
            hard_fail_count=hard_fail_count,
            blocker_codes=blocker_codes,
        )

    @staticmethod
    def get_transition_check(
        db: Session,
        session_id: int,
        target_state: str,
        user_role: str,
        actor_id: int,
    ) -> dict[str, Any]:
        report, session, period, derived_state = GovernanceEndpointService._build_report(db, session_id)
        governance_state = report.get("governance", {}).get("governance_state", "")
        recheck_summary = report.get("severity_summary", {})
        hard_fail_count = int(recheck_summary.get("hard_fail_count", recheck_summary.get("hard_error_count", 0)))

        return attempt_transition(
            from_state=derived_state,
            to_state=target_state,
            user_role=user_role,
            governance_state=governance_state,
            hard_fail_count=hard_fail_count,
            actor_id=actor_id,
        )

    @staticmethod
    def get_executive_risk(db: Session, session_id: int) -> dict[str, Any]:
        from dataclasses import asdict
        report, session, period, derived_state = GovernanceEndpointService._build_report(db, session_id)
        readiness = assess_publication_readiness(
            quality_report=report.get("quality_breakdown", {}),
            governance=report.get("governance", {}),
            recheck_summary=report.get("severity_summary", {}),
            schedule_state=derived_state,
        )
        return compute_executive_risk_report(
            quality_report=report.get("quality_breakdown", {}),
            governance=report.get("governance", {}),
            recheck_summary=report.get("severity_summary", {}),
            readiness_dict=asdict(readiness),
        )
