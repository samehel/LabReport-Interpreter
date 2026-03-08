"""
Parser module for extracting structured lab values from raw text.
Uses regex patterns to identify (test_name, value, unit) tuples from OCR output.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedLabValue:
    """A parsed lab value extracted from raw text."""
    test_name: str
    value: float
    unit: str
    ref_low: Optional[float] = None
    ref_high: Optional[float] = None


# Common lab test names to look for (case-insensitive matching)
KNOWN_TEST_NAMES = [
    # CBC
    "RBC", "Red Blood Cell", "Hemoglobin", "Hb", "Hgb", "HGB",
    "Hematocrit", "Hct", "HCT", "MCV", "MCH", "MCHC", "RDW",
    "WBC", "White Blood Cell", "Platelets", "PLT", "MPV",
    "Neutrophils", "Lymphocytes", "Monocytes", "Eosinophils", "Basophils",
    # CMP
    "Glucose", "Blood Sugar", "BUN", "Blood Urea Nitrogen", "Creatinine",
    "Sodium", "Na", "Potassium", "Chloride", "CO2", "Bicarbonate",
    "Calcium", "Total Protein", "Albumin", "GFR", "eGFR",
    # LFT
    "ALT", "SGPT", "AST", "SGOT", "ALP", "Alkaline Phosphatase",
    "Total Bilirubin", "Direct Bilirubin", "GGT", "LDH",
    # Lipids
    "Total Cholesterol", "Cholesterol", "LDL", "HDL", "Triglycerides", "VLDL",
    # Thyroid
    "TSH", "Free T4", "FT4", "Free T3", "FT3", "T4", "T3",
    # Diabetes
    "HbA1c", "A1C", "Fasting Insulin",
    # Iron
    "Serum Iron", "Iron", "Ferritin", "TIBC", "Transferrin Saturation",
    # Coagulation
    "PT", "INR", "aPTT", "PTT", "D-Dimer", "Fibrinogen",
    # Inflammation
    "CRP", "C-Reactive Protein", "ESR",
    # Vitamins
    "Vitamin D", "Vitamin B12", "B12", "Folate", "Folic Acid",
    # Minerals
    "Magnesium", "Phosphorus",
    # Pancreatic
    "Amylase", "Lipase",
    # Uric Acid
    "Uric Acid",
    # Cardiac
    "Troponin", "Troponin I", "BNP", "CK-MB", "CK", "CPK",
    # Urinalysis
    "Urine pH", "Specific Gravity", "Urobilinogen",
    # Prostate
    "PSA",
    # Electrolytes
    "Anion Gap", "Osmolality",
]

# Common units pattern
UNIT_PATTERN = (
    r"(?:g/dL|mg/dL|mg/L|ng/mL|ng/dL|pg/mL|µg/dL|µU/mL|mIU/L|mEq/L|"
    r"mmol/L|U/L|IU/L|%|fL|pg|seconds|sec|ratio|×10[³⁶]/µL|10\^[36]/[uµ]L|"
    r"mL/min|mm/hr|mOsm/kg|/hpf|cells/[uµ]L|K/[uµ]L|M/[uµ]L)"
)

# Pattern: TestName [separators] NumericValue [space] Unit
# Handles formats like:
#   "Hemoglobin: 14.5 g/dL"
#   "Hemoglobin    14.5 g/dL"
#   "Hemoglobin    14.5    g/dL    12.0 - 16.0"
VALUE_PATTERN = re.compile(
    r"([A-Za-z][A-Za-z0-9\s\-\(\)/\.]+?)"  # Test name (group 1)
    r"[\s:|\t]+"                             # Separator
    r"(\d+\.?\d*)"                           # Numeric value (group 2)
    r"\s*"
    r"(" + UNIT_PATTERN + r")?"              # Unit (group 3, optional)
    r"(?:\s+(\d+\.?\d*)\s*-\s*(\d+\.?\d*))?" # Reference range (groups 4-5, optional)
)

# Alternate pattern for table-style formats
TABLE_PATTERN = re.compile(
    r"^(.+?)\s{2,}(\d+\.?\d*)\s+(" + UNIT_PATTERN + r")"
    r"(?:\s+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*))?",
    re.MULTILINE
)


def parse_lab_values(raw_text: str) -> list[ParsedLabValue]:
    """
    Extract lab values from raw OCR text.

    Uses multiple regex strategies to handle various lab report formats.

    Args:
        raw_text: Raw text extracted from a lab report.

    Returns:
        List of parsed lab values.
    """
    results: list[ParsedLabValue] = []
    seen_tests: set[str] = set()

    # Strategy 1: Match known test names directly
    for test_name in KNOWN_TEST_NAMES:
        pattern = re.compile(
            re.escape(test_name)
            + r"[\s:|\t]+(\d+\.?\d*)"
            + r"\s*(" + UNIT_PATTERN + r")?"
            + r"(?:\s+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*))?",
            re.IGNORECASE
        )

        for match in pattern.finditer(raw_text):
            value_str = match.group(1)
            unit = match.group(2) or ""
            ref_low_str = match.group(3)
            ref_high_str = match.group(4)

            try:
                value = float(value_str)
            except ValueError:
                continue

            ref_low = float(ref_low_str) if ref_low_str else None
            ref_high = float(ref_high_str) if ref_high_str else None

            # Avoid duplicates
            name_key = test_name.lower()
            if name_key not in seen_tests:
                seen_tests.add(name_key)
                results.append(ParsedLabValue(
                    test_name=test_name,
                    value=value,
                    unit=unit.strip(),
                    ref_low=ref_low,
                    ref_high=ref_high
                ))

    # Strategy 2: General pattern matching for any remaining values
    for match in TABLE_PATTERN.finditer(raw_text):
        test_name = match.group(1).strip()
        value_str = match.group(2)
        unit = match.group(3) or ""
        ref_low_str = match.group(4)
        ref_high_str = match.group(5)

        # Skip if already found
        name_key = test_name.lower()
        if name_key in seen_tests:
            continue

        try:
            value = float(value_str)
        except ValueError:
            continue

        ref_low = float(ref_low_str) if ref_low_str else None
        ref_high = float(ref_high_str) if ref_high_str else None

        # Basic validation: test name should look reasonable
        if len(test_name) < 2 or len(test_name) > 60:
            continue
        if test_name[0].isdigit():
            continue

        seen_tests.add(name_key)
        results.append(ParsedLabValue(
            test_name=test_name,
            value=value,
            unit=unit.strip(),
            ref_low=ref_low,
            ref_high=ref_high
        ))

    return results


def normalize_test_name(name: str) -> str:
    """
    Normalize a test name for consistent matching.

    Args:
        name: Raw test name from parsed text.

    Returns:
        Normalized test name.
    """
    # Strip whitespace and normalize case
    name = name.strip()

    # Common substitutions
    substitutions = {
        "hb": "Hemoglobin",
        "hgb": "Hemoglobin",
        "hct": "Hematocrit",
        "plt": "Platelets",
        "wbc": "WBC",
        "rbc": "RBC",
        "sgpt": "ALT",
        "sgot": "AST",
        "alk phos": "ALP",
        "t. bili": "Total Bilirubin",
        "d. bili": "Direct Bilirubin",
        "na": "Sodium",
        "k": "Potassium",
        "cl": "Chloride",
        "ca": "Calcium",
        "mg": "Magnesium",
        "fe": "Serum Iron",
        "fbs": "Glucose",
        "blood sugar": "Glucose",
        "a1c": "HbA1c",
        "tsh": "TSH",
        "ft4": "Free T4",
        "ft3": "Free T3",
        "chol": "Total Cholesterol",
        "tg": "Triglycerides",
        "cpk": "CK",
        "egfr": "GFR",
        "sed rate": "ESR",
        "ptt": "aPTT",
        "vit d": "Vitamin D",
        "b12": "Vitamin B12",
        "psa": "PSA",
    }

    name_lower = name.lower()
    if name_lower in substitutions:
        return substitutions[name_lower]

    return name
