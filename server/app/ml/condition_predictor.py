"""
Condition Predictor module using a trained RandomForestClassifier.
Predicts health conditions (Anemia, Diabetes, etc.) from lab values.
"""

import os
from typing import Optional

import numpy as np

try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False

# Path to the trained model
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "classifier_model.joblib")
FEATURE_NAMES_PATH = os.path.join(MODEL_DIR, "feature_names.joblib")

# Cached model instance
_model = None
_feature_names = None


def _load_model():
    """Load the trained model and feature names from disk."""
    global _model, _feature_names

    if not HAS_JOBLIB:
        return False

    if not os.path.exists(MODEL_PATH):
        return False

    try:
        _model = joblib.load(MODEL_PATH)
        if os.path.exists(FEATURE_NAMES_PATH):
            _feature_names = joblib.load(FEATURE_NAMES_PATH)
        return True
    except Exception:
        _model = None
        _feature_names = None
        return False


def is_model_available() -> bool:
    """Check if a trained model is available."""
    global _model
    if _model is not None:
        return True
    return _load_model()


def predict_conditions(lab_values: list[dict]) -> list[dict]:
    """
    Predict health conditions from a set of lab values using the
    trained RandomForestClassifier.

    Args:
        lab_values: List of dicts, each with 'test_name' and 'value' keys.

    Returns:
        List of predicted conditions with confidence scores.
        Each item: {"condition": str, "probability": float}
        Returns empty list if model is not available.
    """
    if not is_model_available():
        return []

    # Build feature vector from lab values
    features = _build_feature_vector(lab_values)
    if features is None:
        return []

    try:
        # Reshape for single prediction
        X = np.array(features).reshape(1, -1)

        # Get class probabilities
        probabilities = _model.predict_proba(X)[0]
        classes = _model.classes_

        # Return all conditions with probability > 0.1
        results = []
        for cls, prob in zip(classes, probabilities):
            if prob > 0.1:
                results.append({
                    "condition": str(cls),
                    "probability": round(float(prob), 3)
                })

        # Sort by probability descending
        results.sort(key=lambda x: x["probability"], reverse=True)
        return results

    except Exception:
        return []


def _build_feature_vector(lab_values: list[dict]) -> Optional[list[float]]:
    """
    Build a feature vector from lab values matching the training features.

    Args:
        lab_values: List of dicts with 'test_name' and 'value' keys.

    Returns:
        Feature vector as list of floats, or None if insufficient data.
    """
    global _feature_names

    if _feature_names is None:
        return None

    # Create a mapping of test_name -> value
    value_map = {}
    for lv in lab_values:
        name = lv.get("test_name", "").lower().strip()
        value = lv.get("value")
        if name and value is not None:
            value_map[name] = float(value)

    # Build feature vector in the same order as training
    features = []
    for feature_name in _feature_names:
        feature_lower = feature_name.lower().strip()
        if feature_lower in value_map:
            features.append(value_map[feature_lower])
        else:
            features.append(0.0)  # Default for missing features

    return features
