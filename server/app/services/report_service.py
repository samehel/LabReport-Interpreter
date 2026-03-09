"""
Report service. Handles CRUD operations for reports and lab values.
"""

import os
import uuid
from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, UploadFile, status

from app.config import settings
from app.models.report import Report
from app.models.lab_value import LabValue
from app.models.user import User
from app.schemas.report import ReportCreate, LabValueCreate
from app.services.ml_service import process_lab_values, process_raw_text
from app.ml.ocr import extract_text
from app.utils.email_service import send_email_background
from app.utils.email_templates import report_ready_email, critical_values_alert_email


async def create_report_from_upload(
    file: UploadFile,
    report_date: date,
    notes: Optional[str],
    user: User,
    db: AsyncSession
) -> Report:
    """
    Create a report from an uploaded file (PDF or image).
    Runs OCR → ML pipeline on the file.

    Args:
        file: Uploaded file.
        report_date: Date of the lab report.
        notes: Optional notes.
        user: Authenticated user.
        db: Database session.

    Returns:
        Created Report object with lab values.
    """
    # Validate file type
    allowed_types = ["application/pdf", "image/png", "image/jpeg", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file.content_type}' is not supported. "
                   f"Allowed types: PDF, PNG, JPEG."
        )

    # Validate file size
    content = await file.read()
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the {settings.MAX_FILE_SIZE_MB}MB limit."
        )

    # Save file to disk
    file_ext = os.path.splitext(file.filename)[1] or ".pdf"
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(content)

    # Run OCR to extract text
    try:
        raw_text = extract_text(file_path)
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not process file: {str(e)}"
        )

    # Run ML pipeline
    ml_results = process_raw_text(raw_text)

    # Create report
    report = Report(
        user_id=user.id,
        report_date=report_date,
        source="file",
        notes=notes,
        file_path=file_path,
        summary_text=ml_results["summary_text"],
    )
    db.add(report)
    await db.flush()

    # Create lab values
    for lv_data in ml_results["lab_values"]:
        lab_value = LabValue(
            report_id=report.id,
            test_name=lv_data["test_name"],
            value=lv_data["value"],
            unit=lv_data["unit"],
            ref_low=lv_data.get("ref_low"),
            ref_high=lv_data.get("ref_high"),
            status=lv_data["status"],
        )
        db.add(lab_value)

    await db.flush()
    await db.refresh(report)

    # Send report-ready email
    _send_report_emails(user, report, ml_results["lab_values"])

    return report


async def create_report_from_manual(
    data: ReportCreate,
    user: User,
    db: AsyncSession
) -> Report:
    """
    Create a report from manually entered lab values.
    Runs classification pipeline on the values.

    Args:
        data: Report creation data with lab values.
        user: Authenticated user.
        db: Database session.

    Returns:
        Created Report object.
    """
    # Prepare lab values for ML pipeline
    lab_value_dicts = [
        {"test_name": lv.test_name, "value": lv.value, "unit": lv.unit}
        for lv in data.lab_values
    ]

    # Run ML pipeline (classify, predict conditions, summarize)
    ml_results = process_lab_values(lab_value_dicts)

    # Create report
    report = Report(
        user_id=user.id,
        report_date=data.report_date,
        source="manual",
        notes=data.notes,
        summary_text=ml_results["summary_text"],
    )
    db.add(report)
    await db.flush()

    # Create lab values
    for lv_data in ml_results["lab_values"]:
        lab_value = LabValue(
            report_id=report.id,
            test_name=lv_data["test_name"],
            value=lv_data["value"],
            unit=lv_data["unit"],
            ref_low=lv_data.get("ref_low"),
            ref_high=lv_data.get("ref_high"),
            status=lv_data["status"],
        )
        db.add(lab_value)

    await db.flush()
    await db.refresh(report)

    # Send report-ready email
    _send_report_emails(user, report, ml_results["lab_values"])

    return report


async def get_user_reports(user: User, db: AsyncSession) -> list[dict]:
    """
    Get all reports for a user with summary info.

    Returns:
        List of report dicts with flagged_count and total_values.
    """
    result = await db.execute(
        select(Report)
        .where(Report.user_id == user.id)
        .options(selectinload(Report.lab_values))
        .order_by(desc(Report.uploaded_at))
    )
    reports = result.scalars().all()

    report_list = []
    for report in reports:
        flagged = sum(
            1 for lv in report.lab_values
            if lv.status in ("low", "high", "critical_low", "critical_high")
        )
        report_list.append({
            "id": report.id,
            "report_date": report.report_date,
            "uploaded_at": report.uploaded_at,
            "source": report.source,
            "notes": report.notes,
            "flagged_count": flagged,
            "total_values": len(report.lab_values),
        })

    return report_list


async def get_report_detail(report_id: int, user: User, db: AsyncSession) -> dict:
    """
    Get full report details including lab values, summary, and predictions.

    Returns:
        Report detail dict with lab values, summary, conditions, and correlations.
    """
    result = await db.execute(
        select(Report)
        .where(Report.id == report_id, Report.user_id == user.id)
        .options(selectinload(Report.lab_values))
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found."
        )

    # Get condition predictions and correlations from current lab values
    from app.ml.condition_predictor import predict_conditions
    from app.ml.correlations import detect_correlations

    lv_dicts = [
        {"test_name": lv.test_name, "value": lv.value, "unit": lv.unit, "status": lv.status}
        for lv in report.lab_values
    ]
    predicted_conditions = predict_conditions(lv_dicts)
    correlation_hints = detect_correlations(lv_dicts)

    return {
        "id": report.id,
        "report_date": report.report_date,
        "uploaded_at": report.uploaded_at,
        "source": report.source,
        "notes": report.notes,
        "summary_text": report.summary_text,
        "lab_values": [
            {
                "id": lv.id,
                "test_name": lv.test_name,
                "value": lv.value,
                "unit": lv.unit,
                "ref_low": lv.ref_low,
                "ref_high": lv.ref_high,
                "status": lv.status,
            }
            for lv in report.lab_values
        ],
        "predicted_conditions": [c["condition"] for c in predicted_conditions if c.get("probability", 0) > 0.2],
        "correlation_hints": correlation_hints,
    }


async def delete_report(report_id: int, user: User, db: AsyncSession) -> bool:
    """
    Delete a report owned by the user.

    Returns:
        True if deleted.
    """
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == user.id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found."
        )

    # Delete the uploaded file if it exists
    if report.file_path and os.path.exists(report.file_path):
        try:
            os.remove(report.file_path)
        except OSError:
            pass

    await db.delete(report)
    await db.flush()
    return True


async def get_dashboard_stats(user: User, db: AsyncSession) -> dict:
    """Get dashboard summary statistics for a user."""
    # Total reports
    total_result = await db.execute(
        select(func.count(Report.id)).where(Report.user_id == user.id)
    )
    total_reports = total_result.scalar() or 0

    # Total flagged values across all reports
    flagged_result = await db.execute(
        select(func.count(LabValue.id))
        .join(Report, LabValue.report_id == Report.id)
        .where(
            Report.user_id == user.id,
            LabValue.status.in_(["low", "high", "critical_low", "critical_high"])
        )
    )
    flagged_values = flagged_result.scalar() or 0

    # Last upload date
    last_upload_result = await db.execute(
        select(func.max(Report.uploaded_at)).where(Report.user_id == user.id)
    )
    last_upload_date = last_upload_result.scalar()

    return {
        "total_reports": total_reports,
        "flagged_values": flagged_values,
        "last_upload_date": last_upload_date,
    }


def _send_report_emails(user: User, report: Report, lab_values: list[dict]):
    """
    Send report-ready email and critical-value alert if applicable.
    All emails are fire-and-forget (non-blocking).
    """
    # Count flagged values
    flagged = sum(
        1 for lv in lab_values
        if lv.get("status") in ("low", "high", "critical_low", "critical_high")
    )

    # Send report-ready email
    subject, html_body = report_ready_email(
        name=user.name,
        report_date=str(report.report_date),
        total_tests=len(lab_values),
        flagged_count=flagged,
        report_id=report.id,
    )
    send_email_background(user.email, subject, html_body)

    # If any critical values, send a separate urgent alert
    critical_values = [
        lv for lv in lab_values
        if lv.get("status") in ("critical_low", "critical_high")
    ]

    if critical_values:
        alert_subject, alert_html = critical_values_alert_email(
            name=user.name,
            critical_values=critical_values,
            report_date=str(report.report_date),
        )
        send_email_background(user.email, alert_subject, alert_html)

