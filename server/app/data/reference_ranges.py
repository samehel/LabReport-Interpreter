"""
Complete reference range database for common medical lab tests.
Each entry includes normal range, critical thresholds, unit, category, and gender specificity.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class ReferenceRange:
    """A single reference range entry."""
    test_name: str
    unit: str
    ref_low: Optional[float]
    ref_high: Optional[float]
    critical_low: Optional[float]
    critical_high: Optional[float]
    category: str
    gender: Optional[str] = None  # None = both, "male", "female"
    aliases: tuple = ()  # Alternative names for the same test


# ============================================================
# COMPLETE REFERENCE RANGE DATABASE
# ============================================================

REFERENCE_RANGES: list[ReferenceRange] = [

    # --------------------------------------------------------
    # COMPLETE BLOOD COUNT (CBC)
    # --------------------------------------------------------
    ReferenceRange("RBC", "×10⁶/µL", 4.35, 5.65, 3.0, 7.0, "CBC", "male",
                   ("Red Blood Cell Count", "Red Blood Cells", "Erythrocytes")),
    ReferenceRange("RBC", "×10⁶/µL", 3.92, 5.13, 3.0, 6.5, "CBC", "female",
                   ("Red Blood Cell Count", "Red Blood Cells", "Erythrocytes")),
    ReferenceRange("Hemoglobin", "g/dL", 13.5, 17.5, 7.0, 20.0, "CBC", "male",
                   ("Hb", "Hgb", "HGB")),
    ReferenceRange("Hemoglobin", "g/dL", 12.0, 16.0, 7.0, 18.0, "CBC", "female",
                   ("Hb", "Hgb", "HGB")),
    ReferenceRange("Hematocrit", "%", 41.0, 53.0, 25.0, 60.0, "CBC", "male",
                   ("Hct", "HCT", "PCV", "Packed Cell Volume")),
    ReferenceRange("Hematocrit", "%", 36.0, 46.0, 25.0, 55.0, "CBC", "female",
                   ("Hct", "HCT", "PCV", "Packed Cell Volume")),
    ReferenceRange("MCV", "fL", 80.0, 100.0, 60.0, 120.0, "CBC", None,
                   ("Mean Corpuscular Volume",)),
    ReferenceRange("MCH", "pg", 27.0, 33.0, 20.0, 40.0, "CBC", None,
                   ("Mean Corpuscular Hemoglobin",)),
    ReferenceRange("MCHC", "g/dL", 32.0, 36.0, 28.0, 40.0, "CBC", None,
                   ("Mean Corpuscular Hemoglobin Concentration",)),
    ReferenceRange("RDW", "%", 11.0, 14.5, 8.0, 20.0, "CBC", None,
                   ("Red Cell Distribution Width", "RDW-CV")),
    ReferenceRange("WBC", "×10³/µL", 4.5, 11.0, 2.0, 30.0, "CBC", None,
                   ("White Blood Cell Count", "White Blood Cells", "Leukocytes")),
    ReferenceRange("Neutrophils", "%", 40.0, 70.0, 10.0, 90.0, "CBC", None,
                   ("Neutrophil %", "Neut %", "Segs")),
    ReferenceRange("Lymphocytes", "%", 20.0, 40.0, 5.0, 70.0, "CBC", None,
                   ("Lymphocyte %", "Lymph %")),
    ReferenceRange("Monocytes", "%", 2.0, 8.0, 0.0, 15.0, "CBC", None,
                   ("Monocyte %", "Mono %")),
    ReferenceRange("Eosinophils", "%", 1.0, 4.0, 0.0, 10.0, "CBC", None,
                   ("Eosinophil %", "Eos %")),
    ReferenceRange("Basophils", "%", 0.0, 1.0, None, 5.0, "CBC", None,
                   ("Basophil %", "Baso %")),
    ReferenceRange("Platelets", "×10³/µL", 150.0, 400.0, 50.0, 1000.0, "CBC", None,
                   ("Platelet Count", "PLT", "Thrombocytes")),
    ReferenceRange("MPV", "fL", 7.5, 11.5, 5.0, 15.0, "CBC", None,
                   ("Mean Platelet Volume",)),

    # --------------------------------------------------------
    # COMPREHENSIVE METABOLIC PANEL (CMP)
    # --------------------------------------------------------
    ReferenceRange("Glucose", "mg/dL", 70.0, 100.0, 40.0, 500.0, "CMP", None,
                   ("Fasting Glucose", "Blood Sugar", "FBS", "Fasting Blood Sugar", "Blood Glucose")),
    ReferenceRange("BUN", "mg/dL", 7.0, 20.0, 2.0, 100.0, "CMP", None,
                   ("Blood Urea Nitrogen", "Urea Nitrogen", "Urea")),
    ReferenceRange("Creatinine", "mg/dL", 0.7, 1.3, 0.4, 10.0, "CMP", "male",
                   ("Cr", "Serum Creatinine")),
    ReferenceRange("Creatinine", "mg/dL", 0.6, 1.1, 0.4, 10.0, "CMP", "female",
                   ("Cr", "Serum Creatinine")),
    ReferenceRange("Sodium", "mEq/L", 136.0, 145.0, 120.0, 160.0, "CMP", None,
                   ("Na", "Na+", "Serum Sodium")),
    ReferenceRange("Potassium", "mEq/L", 3.5, 5.0, 2.5, 6.5, "CMP", None,
                   ("K", "K+", "Serum Potassium")),
    ReferenceRange("Chloride", "mEq/L", 98.0, 106.0, 80.0, 120.0, "CMP", None,
                   ("Cl", "Cl-", "Serum Chloride")),
    ReferenceRange("CO2", "mEq/L", 23.0, 29.0, 10.0, 40.0, "CMP", None,
                   ("Bicarbonate", "HCO3", "Carbon Dioxide", "TCO2")),
    ReferenceRange("Calcium", "mg/dL", 8.5, 10.5, 6.0, 13.0, "CMP", None,
                   ("Ca", "Ca2+", "Serum Calcium", "Total Calcium")),
    ReferenceRange("Total Protein", "g/dL", 6.0, 8.3, 4.0, 12.0, "CMP", None,
                   ("TP", "Serum Protein")),
    ReferenceRange("Albumin", "g/dL", 3.5, 5.5, 2.0, 7.0, "CMP", None,
                   ("Alb", "Serum Albumin")),
    ReferenceRange("GFR", "mL/min", 90.0, 120.0, 15.0, None, "CMP", None,
                   ("eGFR", "Glomerular Filtration Rate", "Estimated GFR")),

    # --------------------------------------------------------
    # LIVER FUNCTION TESTS (LFT)
    # --------------------------------------------------------
    ReferenceRange("ALT", "U/L", 7.0, 56.0, None, 1000.0, "LFT", None,
                   ("SGPT", "Alanine Aminotransferase", "Alanine Transaminase")),
    ReferenceRange("AST", "U/L", 10.0, 40.0, None, 1000.0, "LFT", None,
                   ("SGOT", "Aspartate Aminotransferase", "Aspartate Transaminase")),
    ReferenceRange("ALP", "U/L", 44.0, 147.0, None, 500.0, "LFT", None,
                   ("Alkaline Phosphatase", "Alk Phos")),
    ReferenceRange("Total Bilirubin", "mg/dL", 0.1, 1.2, None, 15.0, "LFT", None,
                   ("T. Bili", "Bilirubin Total", "TBIL")),
    ReferenceRange("Direct Bilirubin", "mg/dL", 0.0, 0.3, None, 10.0, "LFT", None,
                   ("D. Bili", "Conjugated Bilirubin", "DBIL")),
    ReferenceRange("GGT", "U/L", 9.0, 48.0, None, 500.0, "LFT", None,
                   ("Gamma-GT", "Gamma-Glutamyl Transferase", "GGTP")),
    ReferenceRange("LDH", "U/L", 140.0, 280.0, None, 1000.0, "LFT", None,
                   ("Lactate Dehydrogenase", "LD")),

    # --------------------------------------------------------
    # LIPID / CHOLESTEROL PANEL
    # --------------------------------------------------------
    ReferenceRange("Total Cholesterol", "mg/dL", None, 200.0, None, 300.0, "Lipids", None,
                   ("Cholesterol", "TC", "Chol")),
    ReferenceRange("LDL Cholesterol", "mg/dL", None, 100.0, None, 190.0, "Lipids", None,
                   ("LDL", "LDL-C", "Bad Cholesterol")),
    ReferenceRange("HDL Cholesterol", "mg/dL", 40.0, None, 20.0, None, "Lipids", "male",
                   ("HDL", "HDL-C", "Good Cholesterol")),
    ReferenceRange("HDL Cholesterol", "mg/dL", 50.0, None, 20.0, None, "Lipids", "female",
                   ("HDL", "HDL-C", "Good Cholesterol")),
    ReferenceRange("Triglycerides", "mg/dL", None, 150.0, None, 500.0, "Lipids", None,
                   ("TG", "Trig", "Trigs")),
    ReferenceRange("VLDL Cholesterol", "mg/dL", 5.0, 40.0, None, 100.0, "Lipids", None,
                   ("VLDL", "VLDL-C")),

    # --------------------------------------------------------
    # THYROID PANEL
    # --------------------------------------------------------
    ReferenceRange("TSH", "mIU/L", 0.4, 4.0, 0.01, 20.0, "Thyroid", None,
                   ("Thyroid Stimulating Hormone", "Thyrotropin")),
    ReferenceRange("Free T4", "ng/dL", 0.8, 1.8, 0.3, 5.0, "Thyroid", None,
                   ("FT4", "Free Thyroxine")),
    ReferenceRange("Free T3", "pg/mL", 2.3, 4.2, 1.0, 8.0, "Thyroid", None,
                   ("FT3", "Free Triiodothyronine")),
    ReferenceRange("Total T4", "µg/dL", 5.0, 12.0, 2.0, 20.0, "Thyroid", None,
                   ("T4", "Thyroxine")),
    ReferenceRange("Total T3", "ng/dL", 80.0, 200.0, 40.0, 400.0, "Thyroid", None,
                   ("T3", "Triiodothyronine")),

    # --------------------------------------------------------
    # DIABETES MARKERS
    # --------------------------------------------------------
    ReferenceRange("HbA1c", "%", 4.0, 5.6, 3.0, 15.0, "Diabetes", None,
                   ("Hemoglobin A1c", "A1C", "Glycated Hemoglobin", "Glycosylated Hemoglobin")),
    ReferenceRange("Fasting Insulin", "µU/mL", 2.6, 24.9, None, 100.0, "Diabetes", None,
                   ("Insulin", "Serum Insulin")),

    # --------------------------------------------------------
    # IRON STUDIES
    # --------------------------------------------------------
    ReferenceRange("Serum Iron", "µg/dL", 65.0, 175.0, 30.0, 300.0, "Iron Studies", "male",
                   ("Iron", "Fe", "Iron Level")),
    ReferenceRange("Serum Iron", "µg/dL", 50.0, 170.0, 30.0, 300.0, "Iron Studies", "female",
                   ("Iron", "Fe", "Iron Level")),
    ReferenceRange("Ferritin", "ng/mL", 24.0, 336.0, 10.0, 1000.0, "Iron Studies", "male",
                   ("Serum Ferritin",)),
    ReferenceRange("Ferritin", "ng/mL", 11.0, 307.0, 5.0, 1000.0, "Iron Studies", "female",
                   ("Serum Ferritin",)),
    ReferenceRange("TIBC", "µg/dL", 250.0, 450.0, 100.0, 600.0, "Iron Studies", None,
                   ("Total Iron-Binding Capacity", "Total Iron Binding Capacity")),
    ReferenceRange("Transferrin Saturation", "%", 20.0, 50.0, 10.0, 80.0, "Iron Studies", None,
                   ("TSAT", "Iron Saturation", "Transferrin Sat")),

    # --------------------------------------------------------
    # COAGULATION
    # --------------------------------------------------------
    ReferenceRange("PT", "seconds", 11.0, 13.5, 8.0, 30.0, "Coagulation", None,
                   ("Prothrombin Time", "Pro Time")),
    ReferenceRange("INR", "ratio", 0.8, 1.1, None, 4.5, "Coagulation", None,
                   ("International Normalized Ratio",)),
    ReferenceRange("aPTT", "seconds", 25.0, 35.0, 15.0, 60.0, "Coagulation", None,
                   ("Activated Partial Thromboplastin Time", "PTT", "Partial Thromboplastin Time")),
    ReferenceRange("D-Dimer", "µg/mL", 0.0, 0.5, None, 5.0, "Coagulation", None,
                   ("D Dimer", "DDimer")),
    ReferenceRange("Fibrinogen", "mg/dL", 200.0, 400.0, 100.0, 700.0, "Coagulation", None,
                   ("Factor I",)),

    # --------------------------------------------------------
    # INFLAMMATION MARKERS
    # --------------------------------------------------------
    ReferenceRange("CRP", "mg/L", 0.0, 3.0, None, 100.0, "Inflammation", None,
                   ("C-Reactive Protein", "C Reactive Protein", "hs-CRP")),
    ReferenceRange("ESR", "mm/hr", 0.0, 15.0, None, 100.0, "Inflammation", "male",
                   ("Erythrocyte Sedimentation Rate", "Sed Rate")),
    ReferenceRange("ESR", "mm/hr", 0.0, 20.0, None, 100.0, "Inflammation", "female",
                   ("Erythrocyte Sedimentation Rate", "Sed Rate")),

    # --------------------------------------------------------
    # VITAMINS & MINERALS
    # --------------------------------------------------------
    ReferenceRange("Vitamin D", "ng/mL", 30.0, 100.0, 10.0, 150.0, "Vitamins", None,
                   ("25-OH Vitamin D", "25-Hydroxyvitamin D", "Vit D", "Vitamin D3")),
    ReferenceRange("Vitamin B12", "pg/mL", 200.0, 900.0, 100.0, None, "Vitamins", None,
                   ("B12", "Cobalamin", "Cyanocobalamin")),
    ReferenceRange("Folate", "ng/mL", 3.0, 17.0, 1.0, None, "Vitamins", None,
                   ("Folic Acid", "Serum Folate", "Vitamin B9")),
    ReferenceRange("Magnesium", "mg/dL", 1.7, 2.2, 1.0, 4.0, "Minerals", None,
                   ("Mg", "Mg2+", "Serum Magnesium")),
    ReferenceRange("Phosphorus", "mg/dL", 2.5, 4.5, 1.0, 8.0, "Minerals", None,
                   ("Phosphate", "PO4", "Inorganic Phosphorus")),

    # --------------------------------------------------------
    # PANCREATIC ENZYMES
    # --------------------------------------------------------
    ReferenceRange("Amylase", "U/L", 30.0, 110.0, None, 500.0, "Pancreatic", None,
                   ("Serum Amylase",)),
    ReferenceRange("Lipase", "U/L", 10.0, 140.0, None, 600.0, "Pancreatic", None,
                   ("Serum Lipase",)),

    # --------------------------------------------------------
    # URIC ACID
    # --------------------------------------------------------
    ReferenceRange("Uric Acid", "mg/dL", 3.5, 7.2, 1.0, 12.0, "Uric Acid", "male",
                   ("UA", "Serum Uric Acid", "Urate")),
    ReferenceRange("Uric Acid", "mg/dL", 2.6, 6.0, 1.0, 10.0, "Uric Acid", "female",
                   ("UA", "Serum Uric Acid", "Urate")),

    # --------------------------------------------------------
    # CARDIAC MARKERS
    # --------------------------------------------------------
    ReferenceRange("Troponin I", "ng/mL", 0.0, 0.04, None, 0.4, "Cardiac", None,
                   ("cTnI", "Cardiac Troponin I", "Troponin")),
    ReferenceRange("BNP", "pg/mL", 0.0, 100.0, None, 900.0, "Cardiac", None,
                   ("Brain Natriuretic Peptide", "B-Type Natriuretic Peptide", "NT-proBNP")),
    ReferenceRange("CK-MB", "ng/mL", 0.0, 5.0, None, 25.0, "Cardiac", None,
                   ("Creatine Kinase MB", "CK MB")),
    ReferenceRange("CK", "U/L", 30.0, 200.0, None, 1000.0, "Cardiac", None,
                   ("Creatine Kinase", "CPK", "Total CK", "CK Total")),

    # --------------------------------------------------------
    # URINALYSIS
    # --------------------------------------------------------
    ReferenceRange("Urine pH", "", 4.6, 8.0, None, None, "Urinalysis", None,
                   ("pH (Urine)", "UA pH")),
    ReferenceRange("Specific Gravity", "", 1.005, 1.030, None, None, "Urinalysis", None,
                   ("SG", "Urine Specific Gravity", "Sp. Gravity")),
    ReferenceRange("Urine Protein", "mg/dL", 0.0, 8.0, None, None, "Urinalysis", None,
                   ("Protein (Urine)", "UA Protein", "Urine Albumin")),
    ReferenceRange("Urine Glucose", "mg/dL", 0.0, 0.0, None, None, "Urinalysis", None,
                   ("Glucose (Urine)", "UA Glucose")),
    ReferenceRange("Urine RBC", "/hpf", 0.0, 2.0, None, None, "Urinalysis", None,
                   ("RBC (Urine)", "UA RBC", "Red Blood Cells (Urine)")),
    ReferenceRange("Urine WBC", "/hpf", 0.0, 5.0, None, None, "Urinalysis", None,
                   ("WBC (Urine)", "UA WBC", "White Blood Cells (Urine)")),
    ReferenceRange("Urobilinogen", "mg/dL", 0.2, 1.0, None, None, "Urinalysis", None,
                   ("UBG",)),

    # --------------------------------------------------------
    # PROSTATE (MALE)
    # --------------------------------------------------------
    ReferenceRange("PSA", "ng/mL", 0.0, 4.0, None, 10.0, "Prostate", "male",
                   ("Prostate-Specific Antigen", "Prostate Specific Antigen")),

    # --------------------------------------------------------
    # ELECTROLYTE EXTENDED
    # --------------------------------------------------------
    ReferenceRange("Anion Gap", "mEq/L", 8.0, 12.0, 3.0, 20.0, "Electrolytes", None,
                   ("AG",)),
    ReferenceRange("Osmolality", "mOsm/kg", 275.0, 295.0, 240.0, 320.0, "Electrolytes", None,
                   ("Serum Osmolality", "Plasma Osmolality")),
]


def _build_lookup() -> dict[str, list[ReferenceRange]]:
    """Build a lookup dictionary mapping normalized test names to reference ranges."""
    lookup: dict[str, list[ReferenceRange]] = {}

    for rr in REFERENCE_RANGES:
        # Add the primary name
        key = rr.test_name.lower().strip()
        if key not in lookup:
            lookup[key] = []
        lookup[key].append(rr)

        # Add all aliases
        for alias in rr.aliases:
            alias_key = alias.lower().strip()
            if alias_key not in lookup:
                lookup[alias_key] = []
            lookup[alias_key].append(rr)

    return lookup


# Pre-built lookup for fast access
_LOOKUP = _build_lookup()


def get_reference_range(test_name: str, gender: str = None) -> Optional[ReferenceRange]:
    """
    Look up the reference range for a given test name.

    Args:
        test_name: The test name to look up (case-insensitive, supports aliases).
        gender: Optional gender filter ("male" or "female").

    Returns:
        Matching ReferenceRange or None if not found.
    """
    key = test_name.lower().strip()
    ranges = _LOOKUP.get(key, [])

    if not ranges:
        return None

    # If gender specified, prefer gender-specific range
    if gender:
        for rr in ranges:
            if rr.gender == gender.lower():
                return rr

    # Fall back to gender-neutral range
    for rr in ranges:
        if rr.gender is None:
            return rr

    # If only gender-specific ranges exist, return the first one
    return ranges[0]


def classify_value(test_name: str, value: float, gender: str = None) -> tuple[str, Optional[float], Optional[float]]:
    """
    Classify a lab value against reference ranges.

    Args:
        test_name: The test name.
        value: The numeric value.
        gender: Optional gender for gender-specific ranges.

    Returns:
        Tuple of (status, ref_low, ref_high).
        Status is one of: "normal", "low", "high", "critical_low", "critical_high", "unknown".
    """
    rr = get_reference_range(test_name, gender)

    if rr is None:
        return ("unknown", None, None)

    # Check critical thresholds first
    if rr.critical_low is not None and value < rr.critical_low:
        return ("critical_low", rr.ref_low, rr.ref_high)
    if rr.critical_high is not None and value > rr.critical_high:
        return ("critical_high", rr.ref_low, rr.ref_high)

    # Check normal range
    is_low = rr.ref_low is not None and value < rr.ref_low
    is_high = rr.ref_high is not None and value > rr.ref_high

    if is_low:
        return ("low", rr.ref_low, rr.ref_high)
    elif is_high:
        return ("high", rr.ref_low, rr.ref_high)
    else:
        return ("normal", rr.ref_low, rr.ref_high)


def get_all_test_names() -> list[str]:
    """Return a list of all unique primary test names."""
    seen = set()
    names = []
    for rr in REFERENCE_RANGES:
        if rr.test_name not in seen:
            seen.add(rr.test_name)
            names.append(rr.test_name)
    return names


def get_categories() -> dict[str, list[str]]:
    """Return tests grouped by category."""
    categories: dict[str, list[str]] = {}
    for rr in REFERENCE_RANGES:
        if rr.category not in categories:
            categories[rr.category] = []
        if rr.test_name not in categories[rr.category]:
            categories[rr.category].append(rr.test_name)
    return categories
