
import os
import numpy as np
import pandas as pd
import joblib

_ARTIFACT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
_cache = {}


def _load_artifacts():
    if "bundle" not in _cache:
        _cache["bundle"] = {
            "model": joblib.load(os.path.join(_ARTIFACT_DIR, "model.pkl")),
            "scaler": joblib.load(os.path.join(_ARTIFACT_DIR, "scaler.pkl")),
            "encoders": joblib.load(os.path.join(_ARTIFACT_DIR, "label_encoders.pkl")),
            "feature_columns": joblib.load(os.path.join(_ARTIFACT_DIR, "feature_columns.pkl")),
        }
    return _cache["bundle"]


def categorize(probability: float) -> str:
    if probability < 0.40:
        return "Low"
    elif probability < 0.70:
        return "Medium"
    else:
        return "High"


def _encode_input(answers: dict) -> pd.DataFrame:
    bundle = _load_artifacts()
    feature_columns = bundle["feature_columns"]
    encoders = bundle["encoders"]

    input_df = pd.DataFrame([answers])

    for col in feature_columns:
        if col not in input_df.columns:
            input_df[col] = 0
    input_df = input_df[feature_columns]

    for col, le in encoders.items():
        if col in input_df.columns:
            value = str(input_df.loc[0, col])
            if value in le.classes_:
                input_df[col] = le.transform([value])[0]
            else:
                input_df[col] = 0

    input_df = input_df.apply(pd.to_numeric, errors="coerce").fillna(0)
    return input_df


def predict_risk(answers: dict) -> dict:
    bundle = _load_artifacts()
    model = bundle["model"]
    scaler = bundle["scaler"]

    input_df = _encode_input(answers)
    input_scaled = scaler.transform(input_df)

    proba = float(model.predict_proba(input_scaled)[0][1])
    category = categorize(proba)

    base_probs = {}
    try:
        for name, est in model.named_estimators_.items():
            p = est.predict_proba(input_scaled)[0][1]
            base_probs[name] = float(p)
        spread = float(np.std(list(base_probs.values())))
        confidence = float(np.clip(1.0 - (spread / 0.5), 0.0, 1.0))
    except Exception:
        confidence = 0.75

    return {
        "probability": proba,
        "category": category,
        "confidence": confidence,
        "base_probs": base_probs,
    }


def get_model_metrics() -> dict:
    return {
        "accuracy": 0.8333,
        "precision": 0.7867,
        "recall": 0.9219,
        "f1_score": 0.8489,
        "roc_auc": 0.8953,
        "n_samples": 1259,
        "n_features": 23,
        "n_test_samples": 252,
    }
