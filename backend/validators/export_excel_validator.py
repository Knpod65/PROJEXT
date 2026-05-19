"""
export_excel_validator.py — validation for Excel export operations.

Owns:
- workbook type validation
- sheet metadata validation
- export scope validation
"""
from typing import Optional
from fastapi import HTTPException


class ExportExcelValidator:
    """Validation for Excel export operations."""

    @staticmethod
    def validate_workbook_type(wb_type: str) -> str:
        """Validate workbook type is supported."""
        valid_types = ("compensation", "schedule", "submissions", "workload", "paper_distribution")
        if wb_type not in valid_types:
            raise HTTPException(400, f"workbook_type ต้องเป็นหนึ่งใน: {valid_types}")
        return wb_type

    @staticmethod
    def validate_sheet_metadata(sheet_name: str, headers: list) -> bool:
        """Validate sheet metadata is valid."""
        if not sheet_name or not isinstance(sheet_name, str):
            raise HTTPException(400, "ชื่อ sheet ต้องเป็น string")
        if not headers or not isinstance(headers, list):
            raise HTTPException(400, "headers ต้องเป็น list")
        return True

    @staticmethod
    def validate_export_scope(scope: Optional[str] = None) -> str:
        """Validate export scope."""
        valid_scopes = ("schedule", "workload", "paper_distribution", "submissions", "compensation")
        if scope and scope not in valid_scopes:
            raise HTTPException(400, f"export_scope ต้องเป็นหนึ่งใน: {valid_scopes}")
        return scope or "schedule"