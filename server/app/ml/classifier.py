"""
Classifier module for determining the status of lab values
based on the reference range database.
"""

from typing import Optional
from app.data.reference_ranges import classify_value, get_reference_range


def classify_lab_value(
    test_name: str,
    value: float,
    gender: Optional[str] = None
) -> dict:
    """
    Classify a single lab value against reference ranges.

    Args:
        test_name: Name of the lab test.
        value: The numeric result.
        gender: Optional patient gender for gender-specific ranges.

    Returns:
        Dictionary with status, ref_low, ref_high, and severity info.
    """
    status, ref_low, ref_high = classify_value(test_name, value, gender)

    # Determine severity level (for UI display)
    severity_map = {
        "normal": "normal",
        "low": "warning",
        "high": "warning",
        "critical_low": "critical",
        "critical_high": "critical",
        "unknown": "unknown",
    }

    return {
        "status": status,
        "ref_low": ref_low,
        "ref_high": ref_high,
        "severity": severity_map.get(status, "unknown"),
    }


def classify_all(
    lab_values: list[dict],
    gender: Optional[str] = None
) -> list[dict]:
    """
    Classify a list of lab values.

    Args:
        lab_values: List of dicts with 'test_name', 'value', and 'unit' keys.
        gender: Optional patient gender.

    Returns:
        List of dicts with classification results added.
    """
    results = []
    for lv in lab_values:
        classification = classify_lab_value(
            lv["test_name"],
            lv["value"],
            gender
        )
        results.append({
            **lv,
            "status": classification["status"],
            "ref_low": classification["ref_low"],
            "ref_high": classification["ref_high"],
            "severity": classification["severity"],
        })
    return results
