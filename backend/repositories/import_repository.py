"""
import_repository.py — repository for import session operations.

Owns:
- ImportSession CRUD
- ImportRowLog queries
- Session stats aggregation
"""
from sqlalchemy.orm import Session, and_, func, joinedload
from typing import Optional
import models
from datetime import datetime, timezone


class ImportRepository:
    """Repository for import session and row log operations."""

    @staticmethod
    def get_or_create_session(
        db: Session,
        academic_year: str,
        semester: str,
        exam_type: str,
        current_user_id: int,
    ) -> models.ImportSession:
        """หา ImportSession ที่ตรงกัน หรือสร้างใหม่"""
        sess = db.query(models.ImportSession).filter(
            and_(
                models.ImportSession.academic_year == academic_year,
                models.ImportSession.semester == semester,
                models.ImportSession.exam_type == exam_type,
            )
        ).first()
        if not sess:
            sess = models.ImportSession(
                academic_year=academic_year,
                semester=semester,
                exam_type=exam_type,
                created_by=current_user_id,
            )
            db.add(sess)
            db.flush()
        return sess

    @staticmethod
    def get_session_with_counts(db: Session, session_id: int) -> Optional[dict]:
        """Get session with aggregated counts."""
        sess = db.query(models.ImportSession).filter(
            models.ImportSession.id == session_id
        ).first()
        if not sess:
            return None

        creator_ids = [sess.created_by] if sess.created_by else []
        user_lookup = {}
        if creator_ids:
            users = db.query(models.User).filter(models.User.id.in_(creator_ids)).all()
            user_lookup = {u.id: (u.full_name or u.username or "unknown") for u in users}

        return {
            "session": sess,
            "user_lookup": user_lookup,
        }

    @staticmethod
    def get_session_list(db: Session) -> list:
        """Get all import sessions with aggregated stats."""
        sessions = db.query(models.ImportSession).order_by(
            models.ImportSession.created_at.desc()
        ).all()

        if not sessions:
            return []

        session_ids = [s.id for s in sessions]
        creator_ids = list({s.created_by for s in sessions if s.created_by is not None})

        user_lookup = {}
        if creator_ids:
            users = db.query(models.User).filter(models.User.id.in_(creator_ids)).all()
            user_lookup = {u.id: (u.full_name or u.username or "unknown") for u in users}

        grouped_rows = db.query(
            models.ImportRowLog.session_id,
            models.ImportRowLog.status,
            func.count(models.ImportRowLog.id),
        ).filter(
            models.ImportRowLog.session_id.in_(session_ids)
        ).group_by(
            models.ImportRowLog.session_id,
            models.ImportRowLog.status,
        ).all()

        grouped_imported = db.query(
            models.ImportRowLog.session_id,
            func.sum(case((models.ImportRowLog.was_imported == True, 1), else_=0)),
            func.sum(case((models.ImportRowLog.was_imported == False, 1), else_=0)),
        ).filter(
            models.ImportRowLog.session_id.in_(session_ids)
        ).group_by(
            models.ImportRowLog.session_id,
        ).all()

        count_map = {sid: {
            "total_rows": 0, "valid_rows": 0, "warning_rows": 0,
            "error_rows": 0, "imported_rows": 0, "skipped_rows": 0,
        } for sid in session_ids}

        for session_id, status, count in grouped_rows:
            stats = count_map.setdefault(session_id, count_map[session_ids[0]])
            stats["total_rows"] += int(count or 0)
            if status == "valid":
                stats["valid_rows"] += int(count or 0)
            elif status == "warning":
                stats["warning_rows"] += int(count or 0)
            elif status == "error":
                stats["error_rows"] += int(count or 0)

        for session_id, imported_count, skipped_count in grouped_imported:
            stats = count_map.setdefault(session_id, count_map[session_ids[0]])
            stats["imported_rows"] = int(imported_count or 0)
            stats["skipped_rows"] = int(skipped_count or 0)

        return {"sessions": sessions, "user_lookup": user_lookup, "count_map": count_map}

    @staticmethod
    def get_row_logs(db: Session, session_id: int, status: Optional[str] = None,
                     error_code: Optional[str] = None, q: Optional[str] = None):
        """Get row logs for a session with filtering."""
        query = db.query(models.ImportRowLog).filter(
            models.ImportRowLog.session_id == session_id
        )

        if status:
            query = query.filter(models.ImportRowLog.status == status)
        if error_code:
            query = query.filter(models.ImportRowLog.error_code == error_code)

        row_logs = query.order_by(models.ImportRowLog.row_number.asc()).all()

        keyword = (q or "").strip().lower()
        rows = []
        for row in row_logs:
            raw_data = row.raw_data or {}
            raw_values_text = " ".join(str(value) for value in raw_data.values()).lower() \
                if isinstance(raw_data, dict) else str(raw_data).lower()

            if keyword:
                searchable = " ".join([
                    str(row.row_number),
                    str(row.error_code or ""),
                    str(row.error_message or ""),
                    raw_values_text,
                ]).lower()
                if keyword not in searchable:
                    continue

            rows.append({
                "id": row.id,
                "row_number": row.row_number,
                "status": row.status,
                "error_code": row.error_code,
                "error_message": row.error_message,
                "was_selected": bool(row.was_selected),
                "was_imported": bool(row.was_imported),
                "override_reason": row.override_reason,
                "raw_data": raw_data,
                "raw_data_preview": raw_values_text[:280],
                "created_at": row.created_at.isoformat() if row.created_at else None,
            })

        return {"session_id": session_id, "total_rows": len(rows), "rows": rows}

    @staticmethod
    def get_issue_summary(db: Session, session_id: int) -> list:
        """Get issue summary for a session."""
        issue_rows = db.query(
            models.ImportRowLog.error_code,
            models.ImportRowLog.error_message,
            func.count(models.ImportRowLog.id),
        ).filter(
            models.ImportRowLog.session_id == session_id,
            models.ImportRowLog.error_code.isnot(None),
        ).group_by(
            models.ImportRowLog.error_code,
            models.ImportRowLog.error_message,
        ).order_by(
            func.count(models.ImportRowLog.id).desc(),
            models.ImportRowLog.error_code.asc(),
        ).all()

        return [{
            "code": code,
            "message": message,
            "count": int(count or 0),
        } for code, message, count in issue_rows]

    @staticmethod
    def update_session_stats(db: Session, session_id: int, stats: dict):
        """Update session with final stats."""
        sess = db.query(models.ImportSession).filter(
            models.ImportSession.id == session_id
        ).first()
        if sess:
            sess.opencourse_rows = stats.get("opencourse_rows", 0)
            sess.enrollment_rows = stats.get("enrollment_rows", 0)
            sess.last_updated = datetime.now(timezone.utc)
            db.commit()