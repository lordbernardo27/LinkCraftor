from __future__ import annotations

import re
from typing import Any, Dict, Set


INTENT_TAXONOMY = {
    "calculator": {
        "calculate", "calculator", "calculation", "estimate", "estimated",
        "estimator", "predict", "prediction", "formula", "tool", "checker",
    },
    "guide": {
        "guide", "tips", "advice", "help", "how", "steps", "ways",
        "learn", "explained", "explanation",
    },
    "comparison": {
        "compare", "comparison", "versus", "vs", "difference",
        "differences", "better", "alternative", "alternatives",
    },
    "review": {
        "review", "reviews", "rating", "ratings", "experience",
        "pros", "cons", "verdict",
    },
    "pricing": {
        "price", "pricing", "cost", "costs", "fee", "fees",
        "quote", "subscription", "plan", "plans",
    },
    "risk": {
        "risk", "risks", "chance", "chances", "probability",
        "danger", "warning", "warnings",
    },
    "symptoms": {
        "symptom", "symptoms", "sign", "signs", "indication",
        "indications",
    },
    "treatment": {
        "treatment", "treat", "therapy", "medicine", "medication",
        "management", "manage", "remedy", "remedies",
    },
    "testing": {
        "test", "testing", "screening", "scan", "exam", "assessment",
        "diagnosis", "diagnostic",
    },
    "policy": {
        "policy", "policies", "rule", "rules", "requirement",
        "requirements", "law", "laws", "regulation", "regulations",
    },
    "reference": {
        "definition", "meaning", "reference", "overview", "facts",
        "information", "info",
    },
    "checklist": {
        "checklist", "list", "requirements", "items", "steps",
    },
    "tutorial": {
        "tutorial", "walkthrough", "setup", "install", "implementation",
        "configure", "configuration",
    },
    "news": {
        "news", "latest", "update", "updates", "announcement",
        "announced",
    },
    "research": {
        "study", "studies", "research", "evidence", "trial",
        "paper", "journal", "meta", "analysis",
    },
    "product": {
        "product", "products", "buy", "purchase", "shop",
        "brand", "brands", "device", "devices",
    },
    "location": {
        "near", "nearby", "location", "locations", "local",
        "clinic", "clinics", "hospital", "office", "offices",
    },
    "event": {
        "event", "events", "schedule", "date", "dates",
        "calendar", "deadline",
    },
}


COMPATIBLE_INTENTS = {
    ("guide", "tutorial"): 0.85,
    ("tutorial", "guide"): 0.85,
    ("reference", "guide"): 0.65,
    ("guide", "reference"): 0.65,
    ("testing", "research"): 0.55,
    ("research", "testing"): 0.55,
    ("pricing", "product"): 0.55,
    ("product", "pricing"): 0.55,
    ("checklist", "guide"): 0.60,
    ("guide", "checklist"): 0.60,
}


def _tokens(value: str) -> Set[str]:
    return {
        t for t in re.findall(r"[a-z0-9]+", str(value or "").lower())
        if len(t) >= 2
    }


def _detect_intent(value: str) -> Dict[str, Any]:
    tokens = _tokens(value)
    scores = {}

    for intent, terms in INTENT_TAXONOMY.items():
        overlap = tokens.intersection(terms)
        if overlap:
            scores[intent] = {
                "intent": intent,
                "score": min(1.0, len(overlap) / max(1, min(3, len(terms)))),
                "matched_terms": sorted(overlap),
            }

    if not scores:
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "matched_terms": [],
            "all_intents": [],
        }

    ranked = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
    best = ranked[0]

    return {
        "intent": best["intent"],
        "confidence": round(float(best["score"]), 4),
        "matched_terms": best["matched_terms"],
        "all_intents": ranked,
    }


def _intent_match_score(phrase_intent: str, target_intent: str) -> float:
    if not phrase_intent or phrase_intent == "unknown":
        return 0.50

    if not target_intent or target_intent == "unknown":
        return 0.25

    if phrase_intent == target_intent:
        return 1.0

    return float(COMPATIBLE_INTENTS.get((phrase_intent, target_intent), 0.0))


def _boost_for_score(score: float) -> float:
    if score >= 0.90:
        return 35.0
    if score >= 0.70:
        return 20.0
    if score >= 0.50:
        return 5.0
    if score >= 0.25:
        return -10.0
    return -25.0


def analyze_intent_v1(
    *,
    phrase: str,
    title: str = "",
    url: str = "",
    path: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    # Target intent must be derived from visible target identity.
    # Avoid noisy resolver metadata because it can incorrectly inject intent words.
    target_text = " ".join([
        str(title or ""),
        str(url or "").replace("-", " ").replace("/", " "),
        str(path or "").replace("-", " ").replace("/", " "),
    ])

    phrase_analysis = _detect_intent(phrase)
    target_analysis = _detect_intent(target_text)

    phrase_intent = phrase_analysis.get("intent")
    target_intent = target_analysis.get("intent")

    match_score = _intent_match_score(phrase_intent, target_intent)
    boost = _boost_for_score(match_score)

    return {
        "has_intent_intelligence": True,
        "phrase_intent": phrase_intent,
        "target_intent": target_intent,
        "phrase_intent_confidence": phrase_analysis.get("confidence"),
        "target_intent_confidence": target_analysis.get("confidence"),
        "phrase_intent_terms": phrase_analysis.get("matched_terms", []),
        "target_intent_terms": target_analysis.get("matched_terms", []),
        "intent_match": match_score >= 0.70,
        "intent_match_score": round(match_score, 4),
        "intent_boost": boost,
        "phrase_intents": phrase_analysis.get("all_intents", []),
        "target_intents": target_analysis.get("all_intents", []),
    }


def explain_intent_intelligence_v1() -> Dict[str, Any]:
    return {
        "layer": "resolver_intent_intelligence_v1",
        "purpose": "Classify phrase intent and target-page intent, then boost or penalize resolver candidates universally.",
        "universal": True,
        "intents": sorted(INTENT_TAXONOMY.keys()),
        "outputs": [
            "phrase_intent",
            "target_intent",
            "intent_match_score",
            "intent_boost",
            "intent explainability",
        ],
    }
