"""
Training script for the RandomForestClassifier.
Loads datasets from the datasets/ folder, engineers features,
trains the model, and saves it for use by the condition predictor.

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


def load_and_prepare_datasets() -> pd.DataFrame:
    """
    Load all CSV datasets and prepare a unified training dataset.
    Each dataset is loaded, its target column identified, and features normalized.
    The best dataset (most features + a clear condition label) is selected.
    """
    datasets_path = os.path.abspath(DATASETS_DIR)
    print(f"Looking for datasets in: {datasets_path}")

    if not os.path.exists(datasets_path):
        print(f"ERROR: Datasets directory not found: {datasets_path}")
        sys.exit(1)

    csv_files = [f for f in os.listdir(datasets_path) if f.endswith(".csv")]
    if not csv_files:
        print("ERROR: No CSV files found in datasets/. See datasets/README.md for download links.")
        sys.exit(1)

    print(f"Found {len(csv_files)} CSV file(s)")

    candidates = []

    for csv_file in csv_files:
        filepath = os.path.join(datasets_path, csv_file)
        try:
            # Try different separators
            df = pd.read_csv(filepath)
            if df.shape[1] == 1:
                df = pd.read_csv(filepath, sep=";")
        except Exception as e:
            print(f"  WARNING: Could not load {csv_file}: {e}")
            continue

        # Skip duplicate files
        if " copy" in csv_file.lower():
            print(f"  Skipping duplicate: {csv_file}")
            continue

        # Normalize column names
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        print(f"\n  {csv_file}: {df.shape[0]} rows × {df.shape[1]} cols")

        # Find the target column
        target_col = _find_target(df)
        if target_col is None:
            print(f"    No suitable target column found, skipping.")
            continue

        # Find numeric feature columns
        feature_cols = [
            col for col in df.columns
            if col != target_col
            and df[col].dtype in ["float64", "int64", "float32", "int32"]
        ]

        if len(feature_cols) < 2:
            print(f"    Not enough numeric features ({len(feature_cols)}), skipping.")
            continue

        # Clean target labels
        if df[target_col].dtype == "object":
            df[target_col] = df[target_col].str.strip()

        n_classes = df[target_col].nunique()
        print(f"    Target: '{target_col}' ({n_classes} classes: {list(df[target_col].unique()[:8])})")
        print(f"    Features: {len(feature_cols)} → {feature_cols[:8]}{'...' if len(feature_cols) > 8 else ''}")

        candidates.append({
            "file": csv_file,
            "df": df,
            "target": target_col,
            "features": feature_cols,
            "n_classes": n_classes,
            "score": len(feature_cols) * n_classes  # Prefer more features AND more classes
        })

    if not candidates:
        print("\nERROR: No suitable datasets found for training.")
        sys.exit(1)

    # Pick the dataset with the best score (most features × most classes)
    best = max(candidates, key=lambda c: c["score"])
    print(f"\n  ★ Selected: {best['file']} (score={best['score']}, "
          f"{len(best['features'])} features, {best['n_classes']} classes)")

    return best["df"], best["target"], best["features"]


def _find_target(df: pd.DataFrame) -> str:
    """Find the target/label column in a dataset."""
    target_names = [
        "condition", "diagnosis", "classification", "target", "label",
        "class", "outcome", "cardio", "diabetes", "disease", "result",
        "status", "category", "health_condition",
    ]

    for candidate in target_names:
        for col in df.columns:
            if candidate in col.lower():
                unique = df[col].nunique()
                if 2 <= unique <= 20:
                    return col

    # Fallback: look for categorical columns with few unique values
    for col in df.columns:
        if df[col].dtype == "object":
            if 2 <= df[col].nunique() <= 10:
                return col

    return None


def train_model():
    """Main training pipeline."""
    print("=" * 60)
    print("Lab Report Classifier — Training Pipeline")
    print("=" * 60)

    # Step 1: Load and prepare data
    print("\n[Step 1] Loading datasets...")
    df, target_col, feature_cols = load_and_prepare_datasets()

    # Step 2: Prepare features and labels
    print(f"\n[Step 2] Preparing data...")
    X = df[feature_cols].copy()
    y = df[target_col].copy()

    # Fill numeric NaN with median
    for col in feature_cols:
        X[col] = pd.to_numeric(X[col], errors="coerce")
        median_val = X[col].median()
        X[col] = X[col].fillna(median_val if not pd.isna(median_val) else 0)

    # Drop rows where target is NaN
    mask = y.notna()
    X = X[mask].reset_index(drop=True)
    y = y[mask].reset_index(drop=True)

    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y.astype(str))

    print(f"  Samples: {len(X)}")
    print(f"  Features: {len(feature_cols)}")
    print(f"  Classes: {list(le.classes_)}")
    class_counts = pd.Series(y_encoded).value_counts()
    for cls_idx, count in class_counts.items():
        print(f"    {le.classes_[cls_idx]}: {count} samples")

    # Step 3: Train/test split
    print(f"\n[Step 3] Splitting data (80% train / 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    print(f"  Training: {len(X_train)} samples")
    print(f"  Testing:  {len(X_test)} samples")

    # Step 4: Train
    print(f"\n[Step 4] Training RandomForestClassifier (100 trees)...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    print("  Done!")

    # Step 5: Evaluate
    print(f"\n[Step 5] Evaluation Results")
    print("-" * 40)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"  Accuracy: {accuracy:.4f} ({accuracy * 100:.1f}%)\n")

    target_names = [str(c) for c in le.classes_]
    print(classification_report(y_test, y_pred, target_names=target_names))

    # Feature importance
    print("  Feature Importance:")
    importances = model.feature_importances_
    for name, imp in sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True):
        bar = "█" * int(imp * 50)
        print(f"    {name:30s} {imp:.4f} {bar}")

    # Step 6: Save
    print(f"\n[Step 6] Saving model...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(list(X.columns), FEATURE_NAMES_PATH)
    joblib.dump(le, LABEL_ENCODER_PATH)
    print(f"  ✓ Model:          {MODEL_PATH}")
    print(f"  ✓ Feature names:  {FEATURE_NAMES_PATH}")
    print(f"  ✓ Label encoder:  {LABEL_ENCODER_PATH}")

    print("\n" + "=" * 60)
    print(f"Training complete! Model can detect: {list(le.classes_)}")
    print("=" * 60)


if __name__ == "__main__":
    train_model()
