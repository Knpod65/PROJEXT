"""
import_validator.py — validation for import operations.

Owns:
- exam_type validation
- semester validation  
- file validation
- import request validation
"""
from typing import Optional
from fastapi import HTTPException
import pandas as pd


class ImportValidator:
    """Validation for import operations."""

    @staticmethod
    def validate_exam_type(exam_type: str) -> str:
        """Validate exam_type is valid."""
        if exam_type not in ("midterm", "final"):
            raise HTTPException(400, "exam_type ต้องเป็น 'midterm' หรือ 'final'")
        return exam_type

    @staticmethod
    def validate_semester(semester: str) -> str:
        """Validate semester is valid."""
        if semester not in ("1", "2"):
            raise HTTPException(400, "semester ต้องเป็น '1' หรือ '2'")
        return semester

    @staticmethod
    def validate_opencourse_columns(df: pd.DataFrame) -> None:
        """Validate opencourse file has required columns."""
        required = {"COURESNO", "SECLEC", "LECTURER", "REGIST"}
        missing = required - set(df.columns)
        if missing:
            raise HTTPException(400, f"ไฟล์ขาด columns: {missing}")

    @staticmethod
    def validate_enrollment_columns(df: pd.DataFrame) -> None:
        """Validate enrollment file has required columns."""
        required = {"ID", "COURSENO", "SECLEC"}
        missing = required - set(df.columns)
        if missing:
            raise HTTPException(400, f"ไฟล์ขาด columns: {missing}")