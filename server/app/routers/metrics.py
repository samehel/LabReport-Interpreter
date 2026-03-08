"""
Metrics router. Provides trend data for charting lab values over time.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models.user import User
from app.models.report import Report
from app.models.lab_value import LabValue
from app.schemas.metric import TrendResponse, TrendDataPoint, AvailableMetric
from app.utils.security import get_current_user

router = APIRouter(prefix="/metrics", tags=["Metrics & Trends"])


@router.get("/available", response_model=list[AvailableMetric])
async def list_available_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all unique test names across the user's reports.
    Useful for populating dropdowns in the Trends screen.
    """
    result = await db.execute(
        select(
            LabValue.test_name,
            func.count(LabValue.id).label("count"),
        )
        .join(Report, LabValue.report_id == Report.id)
        .where(Report.user_id == current_user.id)
        .group_by(LabValue.test_name)
        .order_by(desc(func.count(LabValue.id)))
    )
    rows = result.all()

    metrics = []
    for row in rows:
        # Get the latest value for this test
        latest = await db.execute(
            select(LabValue)
            .join(Report, LabValue.report_id == Report.id)
            .where(
                Report.user_id == current_user.id,
                LabValue.test_name == row.test_name
            )
            .order_by(desc(Report.report_date))
            .limit(1)
        )
        latest_lv = latest.scalar_one_or_none()

        if latest_lv:
            metrics.append(AvailableMetric(
                test_name=row.test_name,
                count=row.count,
                latest_value=latest_lv.value,
                latest_unit=latest_lv.unit,
                latest_status=latest_lv.status,
            ))

    return metrics


@router.get("/{test_name}/trend", response_model=TrendResponse)
async def get_trend(
    test_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the trend data for a specific test across all reports.
    Returns data points sorted by date for charting.
    """
    result = await db.execute(
        select(LabValue, Report.report_date)
        .join(Report, LabValue.report_id == Report.id)
        .where(
            Report.user_id == current_user.id,
            LabValue.test_name == test_name
        )
        .order_by(Report.report_date)
    )
    rows = result.all()

    data_points = []
    unit = ""
    ref_low = None
    ref_high = None

    for lv, report_date in rows:
        data_points.append(TrendDataPoint(
            report_date=report_date,
            value=lv.value,
            unit=lv.unit,
            status=lv.status,
            ref_low=lv.ref_low,
            ref_high=lv.ref_high,
        ))
        unit = lv.unit
        if lv.ref_low is not None:
            ref_low = lv.ref_low
        if lv.ref_high is not None:
            ref_high = lv.ref_high

    return TrendResponse(
        test_name=test_name,
        data_points=data_points,
        ref_low=ref_low,
        ref_high=ref_high,
        unit=unit,
    )
