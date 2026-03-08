"""
Training script for the RandomForestClassifier.
Combines ALL datasets into a unified multi-class model that can detect:
  Anemia, Diabetes, Hypertension, High Cholesterol, Cardiovascular Disease,
  Heart Disease, Chronic Kidney Disease (CKD), and Fit/Healthy.

Run: python -m app.ml.train_model
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib

# Paths
DATASETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "datasets")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "classifier_model.joblib")
FEATURE_NAMES_PATH = os.path.join(MODEL_DIR, "feature_names.joblib")
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.joblib")

# ---------------------------------------------------------------
# DATASET CONFIGS: maps each CSV to how we extract a label from it
# ---------------------------------------------------------------
DATASET_CONFIGS = {
    "health_markers_dataset": {
        "target": "condition",
        "label_map": {
            "Fit": "Fit",
            "Anemia": "Anemia",
            "Diabetes": "Diabetes",
            "Hypertension": "Hypertension",
            "High_Cholesterol": "High Cholesterol",
        },
    },
    "cardio_train": {
        "target": "cardio",
        "sep": ";",
        "label_map": {
            "1": "Cardiovascular Disease",
            1: "Cardiovascular Disease",
            "0": "Fit",
            0: "Fit",
        },
    },
    "heart": {
        "target": "target",
        "label_map": {
            1: "Heart Disease",
            "1": "Heart Disease",
            0: "Fit",
            "0": "Fit",
        },
    },
    "kidney_disease": {
        "target": "classification",
        "label_map": {
            "ckd": "Chronic Kidney Disease",
            "ckd\t": "Chronic Kidney Disease",
            "notckd": "Fit",
        },
    },
    "diabetes": {
        "target": "outcome",
        "label_map": {
            1: "Diabetes",
            "1": "Diabetes",
            0: "Fit",
            "0": "Fit",
        },
    },
    "diabetes_prediction_dataset": {
        "target": "diabetes",
        "label_map": {
            1: "Diabetes",
            "1": "Diabetes",
            0: "Fit",
            "0": "Fit",
        },
    },
    "blood_count_dataset": {
        "target": None,  # No label — skip for training
    },
}

# Unified feature name mapping (standardize across datasets)
FEATURE_ALIASES = {
    "haemoglobin": "hemoglobin",
    "hb": "hemoglobin",
    "hgb": "hemoglobin",
    "hemoglobin": "hemoglobin",
    "glucose": "glucose",
    "blood_glucose": "glucose",
    "blood_glucose_level": "glucose",
    "plasma_glucose": "glucose",
    "hba1c": "hba1c",
    "hba1c_level": "hba1c",
    "systolic_bp": "systolic_bp",
    "ap_hi": "systolic_bp",
    "trestbps": "systolic_bp",
    "diastolic_bp": "diastolic_bp",
    "ap_lo": "diastolic_bp",
    "ldl": "ldl",
    "hdl": "hdl",
    "triglycerides": "triglycerides",
    "tg": "triglycerides",
    "chol": "total_cholesterol",
    "cholesterol": "total_cholesterol",
    "total_cholesterol": "total_cholesterol",
    "mcv": "mcv",
    "mch": "mch",
    "mchc": "mchc",
    "platelet_count": "platelets",
    "plt": "platelets",
    "pc": "platelets",
    "white_blood_cells": "wbc",
    "wc": "wbc",
    "wbcc": "wbc",
    "red_blood_cells": "rbc",
    "rc": "rbc",
    "rbcc": "rbc",
    "age": "age",
    "bmi": "bmi",
    "weight": "weight",
    "height": "height",
    "bp": "systolic_bp",
    "sg": "specific_gravity",
    "al": "albumin_urine",
    "su": "sugar_urine",
    "bgr": "glucose",
    "bu": "bun",
    "sc": "creatinine",
    "sod": "sodium",
    "pot": "potassium",
    "hemo": "hemoglobin",
    "pcv": "hematocrit",
    "rbc": "rbc",
    "wbc": "wbc",
    "oldpeak": "oldpeak",
    "thalach": "max_heart_rate",
    "ca": "calcium",
    "insulin": "insulin",
    "skin_thickness": "skin_thickness",
    "skinthickness": "skin_thickness",
    "bloodpressure": "systolic_bp",
    "diabetespedigreefunction": "diabetes_pedigree",
    "pregnancies": "pregnancies",
    "fbs": "fasting_blood_sugar",
    "restecg": "rest_ecg",
    "exang": "exercise_angina",
    "slope": "slope",
    "thal": "thal",
    "cp": "chest_pain_type",
    "sex": "gender",
    "gender": "gender",
    "smoke": "smoking",
    "smoking_history": "smoking",
    "alco": "alcohol",
    "active": "active",
    "hypertension": "has_hypertension",
    "heart_disease": "has_heart_disease",
    "htn": "has_hypertension",
}


def load_and_combine_all() -> tuple[pd.DataFrame, pd.Series]:
    """
    Load ALL datasets, map labels to a unified set, normalize feature names,
    and combine into a single training DataFrame.
    """
    datasets_path = os.path.abspath(DATASETS_DIR)
    print(f"Looking for datasets in: {datasets_path}\n")

    csv_files = [f for f in os.listdir(datasets_path) if f.endswith(".csv")]
    if not csv_files:
        print("ERROR: No CSV files found in datasets/.")
        sys.exit(1)

    all_frames = []

    for csv_file in csv_files:
        # Skip duplicates
        if " copy" in csv_file.lower():
            continue

        filepath = os.path.join(datasets_path, csv_file)
        base_name = os.path.splitext(csv_file)[0].lower()

        # Find matching config
        config = None
        for key, cfg in DATASET_CONFIGS.items():
            if key in base_name:
                config = cfg
                break

        if config is None:
            print(f"  ⚠ {csv_file}: No config found, skipping.")
            continue

        if config.get("target") is None:
            print(f"  ⊘ {csv_file}: No target column, skipping.")
            continue

        # Load CSV
        sep = config.get("sep", ",")
        try:
            df = pd.read_csv(filepath, sep=sep)
        except Exception as e:
            print(f"  ✗ {csv_file}: Failed to load — {e}")
            continue

        # Normalize column names
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # Find the target column
        target_col = config["target"]
        if target_col not in df.columns:
            # Try fuzzy match
            matches = [c for c in df.columns if target_col in c]
            if matches:
                target_col = matches[0]
            else:
                print(f"  ✗ {csv_file}: Target '{config['target']}' not found. Cols: {list(df.columns)}")
                continue

        # Map labels
        label_map = config["label_map"]
        y = df[target_col].copy()

        # Clean string labels
        if y.dtype == "object":
            y = y.str.strip()

        y = y.map(label_map)
        valid_mask = y.notna()
        df = df[valid_mask].copy()
        y = y[valid_mask].copy()

        # Drop the target column from features
        feature_df = df.drop(columns=[target_col], errors="ignore")

        # Normalize feature column names using aliases
        new_cols = {}
        for col in feature_df.columns:
            col_lower = col.lower().strip()
            if col_lower in FEATURE_ALIASES:
                new_cols[col] = FEATURE_ALIASES[col_lower]
            else:
                new_cols[col] = col_lower
        feature_df = feature_df.rename(columns=new_cols)

        # Keep only numeric columns
        numeric_cols = feature_df.select_dtypes(include=[np.number]).columns.tolist()
        feature_df = feature_df[numeric_cols]

        # Attach the label
        feature_df = feature_df.copy()
        feature_df["__label__"] = y.values

        class_counts = y.value_counts()
        print(f"  ✓ {csv_file}: {len(feature_df)} rows, {len(numeric_cols)} features, "
              f"classes: {dict(class_counts)}")

        all_frames.append(feature_df)

    if not all_frames:
        print("\nERROR: No valid datasets could be processed.")
        sys.exit(1)

    # Combine all datasets — missing features become NaN
    print(f"\nCombining {len(all_frames)} datasets...")
    combined = pd.concat(all_frames, ignore_index=True, sort=False)

    # Separate labels
    y_combined = combined["__label__"]
    X_combined = combined.drop(columns=["__label__"])

    # Fill NaN with 0 (feature not present in that dataset)
    X_combined = X_combined.fillna(0)

    # Drop any columns that are all zeros (no information)
    nonzero_cols = X_combined.columns[(X_combined != 0).any()]
    X_combined = X_combined[nonzero_cols]

    print(f"Combined dataset: {len(X_combined)} rows × {len(X_combined.columns)} features")
    print(f"\nClass distribution:")
    for cls, count in y_combined.value_counts().sort_index().items():
        print(f"  {cls:30s} {count:>6d} samples")

    return X_combined, y_combined


def train_model():
    """Main training pipeline."""
    print("=" * 60)
    print("Lab Report Classifier — Unified Training Pipeline")
    print("=" * 60)

    # Step 1: Load and combine all datasets
    print("\n[Step 1] Loading and combining ALL datasets...\n")
    X, y = load_and_combine_all()

    # Step 2: Encode labels
    print(f"\n[Step 2] Encoding labels...")
    le = LabelEncoder()
    y_encoded = le.fit_transform(y.astype(str))
    print(f"  Classes: {list(le.classes_)}")

    # Step 3: Train/test split
    print(f"\n[Step 3] Splitting data (80/20 stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    print(f"  Training: {len(X_train)} samples")
    print(f"  Testing:  {len(X_test)} samples")

    # Step 4: Train
    print(f"\n[Step 4] Training RandomForestClassifier (200 trees)...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",  # Handle class imbalance
    )
    model.fit(X_train, y_train)
    print("  Done!")

    # Step 5: Evaluate
    print(f"\n[Step 5] Evaluation Results")
    print("-" * 50)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"  Overall Accuracy: {accuracy:.4f} ({accuracy * 100:.1f}%)\n")

    target_names = [str(c) for c in le.classes_]
    print(classification_report(y_test, y_pred, target_names=target_names))

    # Top 15 feature importances
    print("  Top 15 Feature Importances:")
    importances = model.feature_importances_
    feature_imp = sorted(zip(X.columns, importances), key=lambda x: x[1], reverse=True)
    for name, imp in feature_imp[:15]:
        bar = "█" * int(imp * 50)
        print(f"    {name:30s} {imp:.4f} {bar}")

    # Step 6: Save
    print(f"\n[Step 6] Saving model...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(list(X.columns), FEATURE_NAMES_PATH)
    joblib.dump(le, LABEL_ENCODER_PATH)
    print(f"  ✓ Model saved:         {MODEL_PATH}")
    print(f"  ✓ Feature names saved: {FEATURE_NAMES_PATH}")
    print(f"  ✓ Label encoder saved: {LABEL_ENCODER_PATH}")

    print("\n" + "=" * 60)
    print("Training complete!")
    print(f"Model can detect: {list(le.classes_)}")
    print("=" * 60)


if __name__ == "__main__":
    train_model()
