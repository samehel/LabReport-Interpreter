from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional


class LabValueCreate(BaseModel):
    """Schema for creating a lab value (manual entry)."""
    test_name: str
    value: float
    unit: str

    @field_validator("test_name")
    @classmethod
    def test_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Test name cannot be empty")
        return v.strip()


class LabValueResponse(BaseModel):
    """Schema for lab value in responses."""
    id: int
    test_name: str
    value: float
    unit: str
    ref_low: Optional[float] = None
    ref_high: Optional[float] = None
    status: str

    class Config:
        from_attributes = True


class ReportCreate(BaseModel):
    """Schema for creating a report via manual entry."""
    report_date: date
    notes: Optional[str] = None
    lab_values: list[LabValueCreate]

    @field_validator("lab_values")
    @classmethod
    def at_least_one_value(cls, v: list) -> list:
        if len(v) == 0:
            raise ValueError("At least one lab value is required")
        return v


class ReportListItem(BaseModel):
    """Schema for report in list views."""
    id: int
    report_date: date
    uploaded_at: datetime
    source: str
    notes: Optional[str] = None
    flagged_count: int = 0
    total_values: int = 0

    class Config:
        from_attributes = True


class ReportDetail(BaseModel):
    """Schema for full report detail."""
    id: int
    report_date: date
    uploaded_at: datetime
    source: str
    notes: Optional[str] = None
    summary_text: Optional[str] = None
    lab_values: list[LabValueResponse] = []
    predicted_conditions: list[str] = []
    correlation_hints: list[str] = []

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """Schema for dashboard summary cards."""
    total_reports: int
    flagged_values: int
    last_upload_date: Optional[datetime] = None
