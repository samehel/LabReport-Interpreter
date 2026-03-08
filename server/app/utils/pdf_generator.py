"""
PDF Generator. Creates formatted PDF summaries of lab reports using ReportLab.
"""

import io
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# Color scheme matching the Flutter app
COLORS = {
    "primary": HexColor("#006D77"),
    "primary_dark": HexColor("#004F59"),
    "normal": HexColor("#2ECC71"),
    "warning": HexColor("#E29D3E"),
    "critical": HexColor("#C0392B"),
    "text": HexColor("#1A1A2E"),
    "text_secondary": HexColor("#6B7280"),
    "background": HexColor("#F4F7F9"),
    "white": HexColor("#FFFFFF"),
    "light_gray": HexColor("#E5E7EB"),
}

STATUS_COLORS = {
    "normal": COLORS["normal"],
    "low": COLORS["warning"],
    "high": COLORS["warning"],
    "critical_low": COLORS["critical"],
    "critical_high": COLORS["critical"],
    "unknown": COLORS["text_secondary"],
}


def generate_report_pdf(
    patient_name: str,
    report_date: str,
    lab_values: list[dict],
    summary_text: str,
    predicted_conditions: list[str] = None,
    correlation_hints: list[str] = None,
) -> bytes:
    """
    Generate a formatted PDF summary of a lab report.

    Args:
        patient_name: Patient's name.
        report_date: Date of the report.
        lab_values: List of lab value dicts.
        summary_text: Plain-language summary.
        predicted_conditions: Optional list of predicted conditions.
        correlation_hints: Optional list of correlation hints.

    Returns:
        PDF file content as bytes.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title="Lab Report Summary",
        author="LabReport Interpreter",
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=18,
        textColor=COLORS["primary"],
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=COLORS["text_secondary"],
        spaceAfter=15,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=COLORS["primary_dark"],
        spaceBefore=15,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=COLORS["text"],
        spaceAfter=8,
        leading=14,
    )

    elements = []

    # Header
    elements.append(Paragraph("Lab Report Summary", title_style))
    elements.append(Paragraph(
        f"Patient: {patient_name} &nbsp; | &nbsp; Date: {report_date} &nbsp; | &nbsp; "
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        subtitle_style
    ))

    # Lab Values Table
    elements.append(Paragraph("Test Results", heading_style))

    if lab_values:
        table_data = [["Test Name", "Value", "Unit", "Reference Range", "Status"]]

        for lv in lab_values:
            ref_range = _format_range(lv.get("ref_low"), lv.get("ref_high"))
            status_display = lv.get("status", "unknown").replace("_", " ").title()
            table_data.append([
                lv.get("test_name", ""),
                str(lv.get("value", "")),
                lv.get("unit", ""),
                ref_range,
                status_display,
            ])

        table = Table(table_data, colWidths=[120, 60, 60, 100, 80])

        # Style the table
        table_style_commands = [
            # Header row
            ("BACKGROUND", (0, 0), (-1, 0), COLORS["primary"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["white"]),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            # Body
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("ALIGN", (1, 1), (1, -1), "CENTER"),
            ("ALIGN", (3, 1), (3, -1), "CENTER"),
            ("ALIGN", (4, 1), (4, -1), "CENTER"),
            # Grid
            ("GRID", (0, 0), (-1, -1), 0.5, COLORS["light_gray"]),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLORS["white"], COLORS["background"]]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]

        # Color-code status cells
        for i, lv in enumerate(lab_values, start=1):
            status = lv.get("status", "unknown")
            if status in STATUS_COLORS:
                table_style_commands.append(
                    ("TEXTCOLOR", (4, i), (4, i), STATUS_COLORS[status])
                )
                table_style_commands.append(
                    ("FONTNAME", (4, i), (4, i), "Helvetica-Bold")
                )

        table.setStyle(TableStyle(table_style_commands))
        elements.append(table)

    # Summary
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Summary", heading_style))
    if summary_text:
        for paragraph in summary_text.split("\n\n"):
            if paragraph.strip():
                elements.append(Paragraph(paragraph.strip(), body_style))

    # Predicted Conditions
    if predicted_conditions:
        elements.append(Paragraph("Predicted Conditions", heading_style))
        for condition in predicted_conditions:
            elements.append(Paragraph(f"• {condition}", body_style))

    # Correlation Hints
    if correlation_hints:
        elements.append(Paragraph("Clinical Observations", heading_style))
        for hint in correlation_hints:
            elements.append(Paragraph(f"• {hint}", body_style))

    # Footer disclaimer
    elements.append(Spacer(1, 20))
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=7,
        textColor=COLORS["text_secondary"],
        alignment=TA_CENTER,
    )
    elements.append(Paragraph(
        "This report is generated by an automated system for educational purposes only. "
        "It is not a substitute for professional medical advice. "
        "Always consult your healthcare provider for interpretation of lab results.",
        disclaimer_style
    ))

    doc.build(elements)
    return buffer.getvalue()


def _format_range(ref_low: Optional[float], ref_high: Optional[float]) -> str:
    """Format reference range for display."""
    if ref_low is not None and ref_high is not None:
        return f"{ref_low} - {ref_high}"
    elif ref_low is not None:
        return f"> {ref_low}"
    elif ref_high is not None:
        return f"< {ref_high}"
    return "N/A"
