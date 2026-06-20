from __future__ import annotations

from typing import Any, Dict


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def calibrate_resolver_score_v1(
    *,
    target_score: Any,
    resolver_confidence: Any = None,
    auto_floor: float = 0.70,
    suggest_floor: float = 0.45,
) -> Dict[str, Any]:

    raw_score = _to_float(target_score, 0.0)

    # Soft saturation curve:
    # 300 = strong
    # 600 = very strong
    # Above 600 still approaches 1.0 but does not explode.
    normalized = raw_score / (raw_score + 120.0) if raw_score > 0 else 0.0
    normalized = max(0.0, min(1.0, normalized))

    existing_confidence = _to_float(resolver_confidence, normalized)

    calibrated_confidence = max(normalized, min(1.0, existing_confidence))

    if calibrated_confidence >= 0.85:
        band = "very_high"
    elif calibrated_confidence >= auto_floor:
        band = "high"
    elif calibrated_confidence >= suggest_floor:
        band = "medium"
    elif calibrated_confidence > 0:
        band = "low"
    else:
        band = "none"

    return {
        "has_score_calibration": True,
        "raw_score": round(raw_score, 4),
        "normalized_score": round(normalized, 4),
        "calibrated_confidence": round(calibrated_confidence, 4),
        "confidence_band": band,
        "auto_floor": auto_floor,
        "suggest_floor": suggest_floor,
    }


def explain_score_calibration_v1() -> Dict[str, Any]:
    return {
        "layer": "resolver_score_calibration_v1",
        "purpose": "Normalize raw resolver scores into stable confidence bands.",
        "universal": True,
        "uses": [
            "raw target score",
            "existing resolver confidence",
            "auto-link floor",
            "suggestion floor",
        ],
        "does_not_use": [
            "health rules",
            "finance rules",
            "legal rules",
            "industry-specific hardcoding",
        ],
    }
