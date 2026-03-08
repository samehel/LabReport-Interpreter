"""
Summary router. Re-triggers ML pipeline and generates PDF reports.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import io

from app.database import get_db
from app.models.user import User
from app.models.report import Report
from app.services.ml_service import process_lab_values
from app.utils.security import get_current_user
from app.utils.pdf_generator import generate_report_pdf
from fastapi import HTTPException, status

router = APIRouter(prefix="/summary", tags=["Summary & PDF"])


@router.post("/{report_id}")
async def regenerate_summary(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Re-trigger the ML pipeline to regenerate the summary for a report."""
    result = await db.execute(
        select(Report)
        .where(Report.id == report_id, Report.user_id == current_user.id)
        .options(selectinload(Report.lab_values))
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    # Re-run ML pipeline
    lab_value_dicts = [
        {"test_name": lv.test_name, "value": lv.value, "unit": lv.unit}
        for lv in report.lab_values
    ]

    ml_results = process_lab_values(lab_value_dicts)

    # Update summary
    report.summary_text = ml_results["summary_text"]
    await db.flush()

    return {
        "message": "Summary regenerated successfully.",
        "summary_text": ml_results["summary_text"],
        "predicted_conditions": ml_results["predicted_conditions"],
        "correlation_hints": ml_results["correlation_hints"],
    }


@router.get("/{report_id}/pdf")
async def download_pdf(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download a formatted PDF summary of a lab report."""
    result = await db.execute(
        select(Report)
        .where(Report.id == report_id, Report.user_id == current_user.id)
        .options(selectinload(Report.lab_values))
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    # Prepare lab values for PDF
    lab_values = [
        {
            "test_name": lv.test_name,
            "value": lv.value,
            "unit": lv.unit,
            "ref_low": lv.ref_low,
            "ref_high": lv.ref_high,
            "status": lv.status,
        }
        for lv in report.lab_values
    ]

    # Get ML predictions
    from app.ml.condition_predictor import predict_conditions
    from app.ml.correlations import detect_correlations

    lv_dicts = [
        {"test_name": lv.test_name, "value": lv.value, "unit": lv.unit, "status": lv.status}
        for lv in report.lab_values
    ]

    predicted = predict_conditions(lv_dicts)
    predicted_conditions = [c["condition"] for c in predicted if c.get("probability", 0) > 0.2]
    correlation_hints = detect_correlations(lv_dicts)

    # Generate PDF
    pdf_bytes = generate_report_pdf(
        patient_name=current_user.name,
        report_date=str(report.report_date),
        lab_values=lab_values,
        summary_text=report.summary_text or "",
        predicted_conditions=predicted_conditions,
        correlation_hints=correlation_hints,
    )

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=lab_report_{report_id}.pdf"
        }
    )
