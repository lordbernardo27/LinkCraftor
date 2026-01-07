from typing import Dict

def bucket_from_score(score: float, phase: str) -> str:
    # mirror your FLOORS (looser in prepublish)
    strong = 0.70 if phase == "publish" else 0.65
    opt    = 0.45 if phase == "publish" else 0.40
    if score >= strong: return "strong"
    if score >= opt: return "optional"
    return "drop"

def meta_floors(phase: str) -> Dict:
    return {
        "STRONG": 0.70 if phase=="publish" else 0.65,
        "OPTIONAL": 0.45 if phase=="publish" else 0.40,
        "MIN_OVERLAP": 2 if phase=="publish" else 1
    }
