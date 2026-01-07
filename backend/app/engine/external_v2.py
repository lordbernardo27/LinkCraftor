# backend/app/engine/external_v2.py
"""
External suggestions (server-side stub).
Exports: run_external_local(plain_text: str, internal_pool: list | None) -> dict
Returns:
{
  "suggestions": [ ... ],
  "meta": { "passed": int, "filtered": int }
}
"""

from __future__ import annotations
from typing import Any, Dict, List

def _wiki_suggestion(title: str) -> Dict[str, Any]:
    slug = title.replace(" ", "_")
    return {
        "title": title,
        "url": f"https://en.wikipedia.org/wiki/{slug}",
        "domainRoot": "wikipedia.org",
        "provider": "heuristic",
        "score": 0.6,
    }

def _shape_external(anchor: str, section_idx: int, score: float = 0.66, tier: str = "optional") -> Dict[str, Any]:
    return {
        "anchor": {"text": anchor, "sectionIdx": section_idx},
        "target": {
            "topicId": f"x:{anchor.lower()}",
            "title": anchor,
            "kind": "external",
            "url": "",
        },
        "bucket": tier,
        "finalScore": max(0.0, min(1.0, score)),
        "posCues": ["cat:wikipedia-heuristic"],
        "posBoost": 0.06,
        "suggestions": [_wiki_suggestion(anchor)],
    }

def run_external_local(plain_text: str, internal_pool: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    if not (plain_text or "").strip():
        return {"suggestions": [], "meta": {"passed": 0, "filtered": 0}}

    t = plain_text.lower()
    suggestions: List[Dict[str, Any]] = []

    if "http" in t and "api" in t:
        suggestions.append(_shape_external("OpenAPI", 0, 0.7, "optional"))
    if "oauth" in t:
        suggestions.append(_shape_external("OAuth 2.0", 0, 0.74, "optional"))

    return {"suggestions": suggestions, "meta": {"passed": len(suggestions), "filtered": 0}}

__all__ = ["run_external_local"]
