"""
ML Service. Orchestrates the full ML pipeline:
OCR → Parse → Classify → Predict Conditions → Detect Correlations → Summarize
"""

from typing import Optional

from app.ml.classifier import classify_all
from app.ml.condition_predictor import predict_conditions
from app.ml.correlations import detect_correlations
from app.ml.summarizer import generate_summary
from app.ml.parser import parse_lab_values, normalize_test_name


def process_raw_text(raw_text: str, gender: Optional[str] = None) -> dict:
    """
    Process raw OCR text through the full ML pipeline.

    Args:
        raw_text: Raw text extracted from a lab report.
        gender: Optional patient gender for gender-specific ranges.

    Returns:
        Dict with lab_values, predicted_conditions, correlation_hints, and summary_text.
    """
    # Step 1: Parse lab values from text
    parsed_values = parse_lab_values(raw_text)

    if not parsed_values:
        return {
            "lab_values": [],
            "predicted_conditions": [],
            "correlation_hints": [],
            "summary_text": "No lab values could be extracted from the provided document."
        }

    # Normalize test names
    lab_value_dicts = []
    for pv in parsed_values:
        normalized_name = normalize_test_name(pv.test_name)
        lab_value_dicts.append({
            "test_name": normalized_name,
            "value": pv.value,
            "unit": pv.unit,
        })

    return process_lab_values(lab_value_dicts, gender)


def process_lab_values(lab_values: list[dict], gender: Optional[str] = None) -> dict:
    """
    Process structured lab values through the ML pipeline.

    Args:
        lab_values: List of dicts with test_name, value, and unit.
        gender: Optional patient gender.

    Returns:
        Dict with classified lab_values, predicted_conditions, correlation_hints, and summary_text.
    """
    # Step 2: Classify each value against reference ranges
    classified_values = classify_all(lab_values, gender)

    # Step 3: Predict conditions using the trained RF model
    predicted_conditions = predict_conditions(classified_values)

    # Step 4: Detect clinical correlations
    correlation_hints = detect_correlations(classified_values)

    # Step 5: Generate plain-language summary
    summary_text = generate_summary(
        classified_values,
        predicted_conditions,
        correlation_hints
    )

    return {
        "lab_values": classified_values,
        "predicted_conditions": predicted_conditions,
        "correlation_hints": correlation_hints,
        "summary_text": summary_text,
    }
