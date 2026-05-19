"""Schedule filter request validator (example).

Use Pydantic models for request validation. Keep these classes in `backend/validators`
so routers can refer to them and keep validation consistent and testable.
"""
from pydantic import BaseModel, Field
from typing import Optional


class ScheduleFilterRequest(BaseModel):
    faculty_id: Optional[int] = Field(None, description="Faculty id to filter schedules")
    date_from: Optional[str] = Field(None, description="Start date (ISO) for filter")
    date_to: Optional[str] = Field(None, description="End date (ISO) for filter")
    include_archived: bool = Field(False, description="Include archived schedules")
    page: int = Field(1, ge=1)
    per_page: int = Field(50, ge=1, le=500)
