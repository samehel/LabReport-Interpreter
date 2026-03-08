"""
Summarizer module for generating plain-language summaries of lab results.
Uses template-based generation driven by classification results and condition predictions.
"""

from typing import Optional


# System-specific grouping for clear summaries
SYSTEM_GROUPS = {
    "Blood Cells": ["RBC", "Hemoglobin", "Hematocrit", "MCV", "MCH", "MCHC", "RDW",
                     "WBC", "Neutrophils", "Lymphocytes", "Monocytes", "Eosinophils",
                     "Basophils", "Platelets", "MPV"],
    "Metabolic": ["Glucose", "BUN", "Creatinine", "GFR", "Sodium", "Potassium",
                   "Chloride", "CO2", "Calcium", "Total Protein", "Albumin",
                   "Anion Gap", "Osmolality"],
    "Liver": ["ALT", "AST", "ALP", "Total Bilirubin", "Direct Bilirubin", "GGT", "LDH"],
    "Cholesterol": ["Total Cholesterol", "LDL Cholesterol", "HDL Cholesterol",
                     "Triglycerides", "VLDL Cholesterol"],
    "Thyroid": ["TSH", "Free T4", "Free T3", "Total T4", "Total T3"],
    "Diabetes": ["HbA1c", "Fasting Insulin"],
    "Iron": ["Serum Iron", "Ferritin", "TIBC", "Transferrin Saturation"],
    "Coagulation": ["PT", "INR", "aPTT", "D-Dimer", "Fibrinogen"],
    "Inflammation": ["CRP", "ESR"],
    "Cardiac": ["Troponin I", "BNP", "CK-MB", "CK"],
    "Vitamins & Minerals": ["Vitamin D", "Vitamin B12", "Folate", "Magnesium", "Phosphorus"],
    "Kidney": ["BUN", "Creatinine", "GFR"],
}


def generate_summary(
    lab_values: list[dict],
    predicted_conditions: list[dict] = None,
    correlation_hints: list[str] = None
) -> str:
    """
    Generate a plain-language summary of lab results.

    Args:
        lab_values: List of dicts with test_name, value, unit, status, ref_low, ref_high.
        predicted_conditions: Optional list of condition predictions from the RF model.
        correlation_hints: Optional list of clinical correlation hints.

    Returns:
        Plain-language summary string.
    """
    if not lab_values:
        return "No lab values were provided for analysis."

    # Categorize values
    normal_values = [lv for lv in lab_values if lv.get("status") == "normal"]
    low_values = [lv for lv in lab_values if lv.get("status") == "low"]
    high_values = [lv for lv in lab_values if lv.get("status") == "high"]
    critical_low = [lv for lv in lab_values if lv.get("status") == "critical_low"]
    critical_high = [lv for lv in lab_values if lv.get("status") == "critical_high"]
    unknown_values = [lv for lv in lab_values if lv.get("status") == "unknown"]

    total = len(lab_values)
    abnormal_count = len(low_values) + len(high_values) + len(critical_low) + len(critical_high)

    sections = []

    # Opening statement
    if abnormal_count == 0:
        sections.append(
            f"Your lab report includes {total} test(s), and all results are within "
            f"normal reference ranges. This is a positive finding."
        )
    else:
        sections.append(
            f"Your lab report includes {total} test(s). "
            f"{len(normal_values)} result(s) are within normal range, "
            f"and {abnormal_count} result(s) require attention."
        )

    # Critical alerts (highest priority)
    if critical_low or critical_high:
        critical_items = []
        for lv in critical_low:
            critical_items.append(
                f"{lv['test_name']} is critically low at {lv['value']} {lv['unit']} "
                f"(normal range: {lv.get('ref_low', '?')}-{lv.get('ref_high', '?')} {lv['unit']})"
            )
        for lv in critical_high:
            critical_items.append(
                f"{lv['test_name']} is critically high at {lv['value']} {lv['unit']} "
                f"(normal range: {lv.get('ref_low', '?')}-{lv.get('ref_high', '?')} {lv['unit']})"
            )
        sections.append(
            "⚠️ CRITICAL VALUES DETECTED: " + "; ".join(critical_items) + ". "
            "These values are significantly outside the expected range and should be "
            "discussed with your healthcare provider promptly."
        )

    # Group abnormal values by body system
    abnormal_by_system = _group_by_system(low_values + high_values)
    for system_name, system_values in abnormal_by_system.items():
        descriptions = []
        for lv in system_values:
            direction = "below" if lv["status"] == "low" else "above"
            ref_range = _format_range(lv.get("ref_low"), lv.get("ref_high"), lv["unit"])
            descriptions.append(
                f"{lv['test_name']} is {direction} normal at {lv['value']} {lv['unit']} "
                f"(expected: {ref_range})"
            )
        sections.append(
            f"{system_name}: " + ". ".join(descriptions) + "."
        )

    # ML condition predictions
    if predicted_conditions:
        top_conditions = [
            c for c in predicted_conditions
            if c.get("probability", 0) > 0.2 and c.get("condition", "").lower() != "fit"
        ]
        if top_conditions:
            condition_strs = [
                f"{c['condition']} ({c['probability']*100:.0f}% likelihood)"
                for c in top_conditions[:3]
            ]
            sections.append(
                "Based on the pattern of your results, the analysis suggests possible: "
                + ", ".join(condition_strs) + ". "
                "Please note this is an automated assessment and should be confirmed by "
                "a qualified healthcare professional."
            )

    # Correlation hints
    if correlation_hints:
        sections.append(
            "Additional observations: " + " ".join(correlation_hints)
        )

    # Closing
    if abnormal_count > 0:
        sections.append(
            "It is recommended to discuss these results with your healthcare provider "
            "for proper interpretation in the context of your overall health."
        )

    return "\n\n".join(sections)


def _group_by_system(lab_values: list[dict]) -> dict[str, list[dict]]:
    """Group lab values by body system/category."""
    grouped: dict[str, list[dict]] = {}

    for lv in lab_values:
        test_name = lv.get("test_name", "")
        system = "Other"

        for system_name, tests in SYSTEM_GROUPS.items():
            if test_name in tests:
                system = system_name
                break

        if system not in grouped:
            grouped[system] = []
        grouped[system].append(lv)

    return grouped


def _format_range(ref_low: Optional[float], ref_high: Optional[float], unit: str) -> str:
    """Format a reference range for display."""
    if ref_low is not None and ref_high is not None:
        return f"{ref_low}-{ref_high} {unit}"
    elif ref_low is not None:
        return f">{ref_low} {unit}"
    elif ref_high is not None:
        return f"<{ref_high} {unit}"
    return "not available"
