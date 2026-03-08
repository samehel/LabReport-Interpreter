"""
Reports router. Handles CRUD operations for lab reports.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.report import ReportCreate, ReportListItem, ReportDetail, DashboardStats
from app.services.report_service import (
    create_report_from_upload,
    create_report_from_manual,
    get_user_reports,
    get_report_detail,
    delete_report,
    get_dashboard_stats,
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("", response_model=list[ReportListItem])
async def list_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all reports for the authenticated user, newest first."""
    reports = await get_user_reports(current_user, db)
    return reports


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard summary statistics (total reports, flagged values, last upload)."""
    return await get_dashboard_stats(current_user, db)


@router.post("/upload", response_model=ReportDetail, status_code=201)
async def upload_report(
    file: UploadFile = File(...),
    report_date: date = Form(...),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a PDF or image lab report.
    The file is processed through the OCR + ML pipeline to extract, classify,
    and summarize lab values automatically.
    """
    report = await create_report_from_upload(file, report_date, notes, current_user, db)
    return await get_report_detail(report.id, current_user, db)


@router.post("/manual", response_model=ReportDetail, status_code=201)
async def manual_report(
    data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit lab values manually.
    Values are classified against reference ranges and a summary is generated.
    """
    report = await create_report_from_manual(data, current_user, db)
    return await get_report_detail(report.id, current_user, db)


@router.get("/{report_id}", response_model=ReportDetail)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get full details of a specific report including lab values, summary, and predictions."""
    return await get_report_detail(report_id, current_user, db)


@router.delete("/{report_id}")
async def remove_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a report and its associated data."""
    await delete_report(report_id, current_user, db)
    return {"message": "Report deleted successfully."}
