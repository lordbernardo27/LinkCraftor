from __future__ import annotations

import re
from typing import Any, Dict, List, Set


STOPWORDS = {
    "the","a","an","and","or","to","of","in","on","for","with","by","from",
    "after","before","how","what","why","when","where","can","does","do",
    "is","are","was","were","this","that","these","those","your","you",
    "it","as","at","be","been","being","into","than","then","also"
}


UNIVERSAL_JOURNEY_PATTERNS = {
    "planning": {
        "plan","planning","prepare","preparing","schedule","timeline","calendar",
        "estimate","calculate","predict","forecast"
    },
    "learning": {
        "guide","learn","understand","explained","explanation","meaning","overview",
        "definition","basics","introduction"
    },
    "decision": {
        "choose","compare","comparison","vs","versus","best","better","option",
        "alternative","pros","cons"
    },
    "problem_solving": {
        "fix","solve","avoid","prevent","issue","problem","mistake","error",
        "troubleshoot","troubleshooting"
    },
    "risk_assessment": {
        "risk","risks","chance","warning","danger","safe","unsafe","probability",
        "concern","concerns"
    },
    "action": {
        "apply","submit","buy","purchase","book","register","renew","cancel",
        "download","install","setup","configure"
    },
    "monitoring": {
        "track","tracking","monitor","measure","check","checker","test","testing",
        "scan","screening","assessment"
    },
    "compliance": {
        "rule","rules","policy","policies","law","laws","requirement",
        "requirements","deadline","license","renewal","permit"
    },
    "optimization": {
        "improve","increase","reduce","lower","boost","optimize","optimization",
        "saving","savings","performance"
    },
    "transaction": {
        "price","pricing","cost","fee","fees","quote","payment","subscription",
        "plan","plans"
    },
}


def _tokens(value: str) -> Set[str]:
    return {
        t for t in re.findall(r"[a-z0-9]+", str(value or "").lower())
        if len(t) >= 3 and t not in STOPWORDS
    }


def analyze_topic_intent_graph_v1(
    *,
    phrase: str,
    title: str = "",
    url: str = "",
    aliases: List[str] | None = None,
    context_terms: List[str] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    text = " ".join([
        str(phrase or ""),
        str(title or ""),
        str(url or "").replace("-", " ").replace("/", " "),
        " ".join(aliases or []),
        " ".join(context_terms or []),
    ])

    tokens = _tokens(text)
    journeys = []

    for journey, terms in UNIVERSAL_JOURNEY_PATTERNS.items():
        overlap = sorted(tokens.intersection(terms))
        if not overlap:
            continue

        score = min(1.0, len(overlap) / max(1, min(4, len(terms))))
        journeys.append({
            "journey": journey,
            "score": round(score, 4),
            "matched_terms": overlap,
        })

    journeys = sorted(journeys, key=lambda x: x["score"], reverse=True)

    primary = journeys[0]["journey"] if journeys else "unknown"
    confidence = float(journeys[0]["score"]) if journeys else 0.0

    if confidence >= 0.75:
        boost = 30.0
    elif confidence >= 0.50:
        boost = 18.0
    elif confidence >= 0.25:
        boost = 8.0
    else:
        boost = 0.0

    return {
        "has_topic_intent_graph": True,
        "primary_journey": primary,
        "journey_confidence": round(confidence, 4),
        "journeys": journeys[:6],
        "journey_boost": boost,
        "universal": True,
        "method": "universal_topic_intent_graph_v1",
    }


def explain_topic_intent_graph_v1() -> Dict[str, Any]:
    return {
        "layer": "resolver_topic_intent_graph_v1",
        "purpose": "Detect the universal user/topic journey behind a phrase and target candidate.",
        "universal": True,
        "journeys": sorted(UNIVERSAL_JOURNEY_PATTERNS.keys()),
        "outputs": [
            "primary_journey",
            "journey_confidence",
            "journeys",
            "journey_boost",
        ],
    }
