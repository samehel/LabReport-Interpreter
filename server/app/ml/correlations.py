"""
Correlations module for detecting clinically meaningful patterns
between lab values within a single report.
"""

from typing import Optional


# Pre-defined clinical correlation rules
CORRELATION_RULES = [
    {
        "name": "Iron Deficiency Anemia Pattern",
        "required_low": ["Hemoglobin", "MCV", "Serum Iron"],
        "required_high": ["TIBC"],
        "optional_low": ["Ferritin", "Hematocrit", "MCH", "MCHC"],
        "hint": "Low hemoglobin combined with low MCV and low iron levels suggests "
                "a pattern consistent with iron deficiency anemia. Consider iron studies "
                "and dietary assessment."
    },
    {
        "name": "Diabetes Indicator Pattern",
        "required_high": ["Glucose", "HbA1c"],
        "hint": "Elevated glucose and HbA1c together suggest poor blood sugar control. "
                "HbA1c reflects average blood sugar over the past 2-3 months."
    },
    {
        "name": "Kidney Dysfunction Pattern",
        "required_high": ["BUN", "Creatinine"],
        "required_low": ["GFR"],
        "hint": "Elevated BUN and creatinine with reduced GFR indicate impaired kidney function. "
                "Further assessment of kidney health may be warranted."
    },
    {
        "name": "Liver Stress Pattern",
        "required_high": ["ALT", "AST"],
        "optional_high": ["Total Bilirubin", "GGT", "ALP"],
        "hint": "Elevated liver enzymes (ALT and AST) suggest liver stress or inflammation. "
                "The pattern and ratio of these enzymes can help identify the cause."
    },
    {
        "name": "Hyperthyroid Pattern",
        "required_low": ["TSH"],
        "required_high": ["Free T4"],
        "optional_high": ["Free T3"],
        "hint": "Low TSH with elevated thyroid hormones suggests an overactive thyroid. "
                "This pattern warrants further thyroid evaluation."
    },
    {
        "name": "Hypothyroid Pattern",
        "required_high": ["TSH"],
        "required_low": ["Free T4"],
        "optional_low": ["Free T3"],
        "hint": "High TSH with low thyroid hormones suggests an underactive thyroid. "
                "This is the most common thyroid disorder."
    },
    {
        "name": "Cardiovascular Risk Pattern",
        "required_high": ["Total Cholesterol", "LDL Cholesterol", "Triglycerides"],
        "optional_low": ["HDL Cholesterol"],
        "hint": "Elevated LDL cholesterol and triglycerides with potentially low HDL "
                "indicate increased cardiovascular risk. Lifestyle modifications and "
                "follow-up lipid monitoring may be recommended."
    },
    {
        "name": "Infection/Inflammation Pattern",
        "required_high": ["WBC", "CRP"],
        "optional_high": ["ESR", "Neutrophils"],
        "hint": "Elevated white blood cells and CRP suggest an active infection or "
                "inflammatory process in the body."
    },
    {
        "name": "Vitamin Deficiency Pattern",
        "required_low": ["Vitamin B12", "Folate"],
        "optional_high": ["MCV"],
        "hint": "Low vitamin B12 and folate can cause macrocytic anemia (large red blood cells). "
                "Supplementation and dietary changes may be recommended."
    },
    {
        "name": "Dehydration Pattern",
        "required_high": ["BUN", "Sodium", "Hematocrit"],
        "optional_high": ["Osmolality"],
        "hint": "Elevated BUN, sodium, and hematocrit together may suggest dehydration. "
                "Adequate fluid intake is important."
    },
    {
        "name": "Cardiac Event Risk",
        "required_high": ["Troponin I"],
        "optional_high": ["CK-MB", "CK", "BNP"],
        "hint": "Elevated troponin is a marker of heart muscle damage. This finding, "
                "especially combined with elevated CK-MB, requires urgent medical attention."
    },
    {
        "name": "Gout/Hyperuricemia Pattern",
        "required_high": ["Uric Acid"],
        "optional_high": ["CRP", "ESR"],
        "hint": "Elevated uric acid levels may increase the risk of gout and kidney stones. "
                "Dietary modifications may be recommended."
    },
    {
        "name": "Pancreatitis Indicator",
        "required_high": ["Amylase", "Lipase"],
        "hint": "Elevated amylase and lipase together suggest pancreatic inflammation. "
                "Lipase is more specific to the pancreas than amylase."
    },
]


def detect_correlations(lab_values: list[dict]) -> list[str]:
    """
    Detect clinically meaningful correlations in a set of lab values.

    Args:
        lab_values: List of dicts with 'test_name' and 'status' keys.

    Returns:
        List of correlation hint strings.
    """
    if not lab_values:
        return []

    # Build status lookup
    status_map = {}
    for lv in lab_values:
        name = lv.get("test_name", "")
        status = lv.get("status", "")
        status_map[name] = status

    hints = []

    for rule in CORRELATION_RULES:
        if _check_rule(rule, status_map):
            hints.append(rule["hint"])

    return hints


def _check_rule(rule: dict, status_map: dict[str, str]) -> bool:
    """
    Check if a correlation rule matches the current lab values.

    A rule matches if ALL required conditions are met and at least some
    of the tests are present in the report.
    """
    # Check required_low tests
    required_low = rule.get("required_low", [])
    for test in required_low:
        status = status_map.get(test)
        if status not in ("low", "critical_low"):
            return False

    # Check required_high tests
    required_high = rule.get("required_high", [])
    for test in required_high:
        status = status_map.get(test)
        if status not in ("high", "critical_high"):
            return False

    # At least some required tests must be present
    all_required = required_low + required_high
    if not all_required:
        return False

    # Check that we have enough of the required tests present
    present_count = sum(1 for t in all_required if t in status_map)
    if present_count < len(all_required):
        return False

    return True
