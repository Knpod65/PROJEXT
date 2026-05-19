"""
governance_validator.py — validation for governance operations.

Owns:
- session ID validation
- target state validation
"""
from typing import Optional
from fastapi import HTTPException


class GovernanceValidator:
    """Validation for governance operations."""

    VALID_STATES = {"draft", "swap_open", "swap_confirming", "confirmed", "locked"}

    @staticmethod
    def validate_session_id(session_id: int) -> int:
        if not isinstance(session_id, int) or session_id <= 0:
            raise HTTPException(400, "session_id ต้องเป็น integer บวก")
        return session_id

    @staticmethod
    def validate_target_state(target_state: str) -> str:
        if target_state not in GovernanceValidator.VALID_STATES:
            raise HTTPException(400, f"target_state ไม่ถูกต้อง ต้องเป็นหนึ่งใน: {GovernanceValidator.VALID_STATES}")
        return target_state
