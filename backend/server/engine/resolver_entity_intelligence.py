from __future__ import annotations

import re
from typing import Any, Dict, Set


def _tokenize(value: Any) -> Set[str]:
    return {
        t
        for t in re.findall(r"[a-z0-9]+", str(value or "").lower())
        if len(t) >= 3
    }


def _collect_target_entities(target: Dict[str, Any]) -> Set[str]:
    entities = set()

    entities |= _tokenize(target.get("title"))
    entities |= _tokenize(target.get("url"))

    aliases = target.get("aliases") or []
    if isinstance(aliases, list):
        for item in aliases:
            entities |= _tokenize(item)

    metadata = target.get("metadata") or {}
    if isinstance(metadata, dict):
        for value in metadata.values():
            if isinstance(value, str):
                entities |= _tokenize(value)

    return entities


def analyze_entity_intelligence_v1(
    anchor_phrase: str,
    target: Dict[str, Any],
) -> Dict[str, Any]:

    anchor_entities = _tokenize(anchor_phrase)
    target_entities = _collect_target_entities(target)

    overlap = anchor_entities & target_entities

    overlap_ratio = (
        len(overlap) / max(1, len(anchor_entities))
        if anchor_entities
        else 0.0
    )

    if overlap_ratio >= 0.80:
        level = "high"
        boost = 35.0
    elif overlap_ratio >= 0.50:
        level = "medium"
        boost = 20.0
    elif overlap_ratio > 0:
        level = "low"
        boost = 8.0
    else:
        level = "none"
        boost = 0.0

    return {
        "has_entity_analysis": True,
        "entity_overlap_terms": sorted(overlap),
        "entity_overlap_count": len(overlap),
        "anchor_entity_count": len(anchor_entities),
        "target_entity_count": len(target_entities),
        "entity_overlap_ratio": round(overlap_ratio, 4),
        "entity_confidence": level,
        "entity_boost": boost,
    }


def explain_entity_intelligence_v1() -> Dict[str, Any]:
    return {
        "layer": "entity_intelligence_v1",
        "purpose": "Match anchor entities against target entities using universal entity overlap.",
        "universal": True,
        "uses": [
            "anchor entities",
            "target entities",
            "aliases",
            "metadata",
            "url tokens",
            "title tokens",
        ],
        "does_not_use": [
            "health terms",
            "finance terms",
            "legal terms",
            "industry-specific hardcoded rules",
        ],
    }
