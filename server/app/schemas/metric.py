from pydantic import BaseModel
from datetime import date
from typing import Optional


class TrendDataPoint(BaseModel):
    """A single data point in a trend chart."""
    report_date: date
    value: float
    unit: str
    status: str
    ref_low: Optional[float] = None
    ref_high: Optional[float] = None


class TrendResponse(BaseModel):
    """Response for metric trend data."""
    test_name: str
    data_points: list[TrendDataPoint] = []
    ref_low: Optional[float] = None
    ref_high: Optional[float] = None
    unit: str = ""


class AvailableMetric(BaseModel):
    """A metric available for trending."""
    test_name: str
    count: int
    latest_value: float
    latest_unit: str
    latest_status: str
