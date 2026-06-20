from __future__ import annotations

import json
from typing import Any, Dict, List

from backend.server.engine.resolver_competition_intelligence import analyze_resolver_competition_v1
from backend.server.engine.resolver_decision_intelligence import decide_resolver_action_v1
from backend.server.engine.resolver_entity_intelligence import analyze_entity_intelligence_v1
from backend.server.engine.resolver_topic_authority import analyze_topic_authority_v1


def run_false_positive_attack_test_v1(
    *,
    anchor_phrase: str,
    candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:

    enriched = []

    for c in candidates:
        item = dict(c)
        item.setdefault("phrase", anchor_phrase)

        entity = analyze_entity_intelligence_v1(anchor_phrase, item)
        authority = analyze_topic_authority_v1(item)

        score = float(item.get("target_score") or item.get("score") or 0)
        score += float(entity.get("entity_boost") or 0)
        score += float(authority.get("topic_authority_boost") or 0)

        item["target_score"] = score
        item["resolver_confidence"] = min(1.0, score / 300.0)
        item["entity_intelligence"] = entity
        item["topic_authority_intelligence"] = authority
        item["auto_link_allowed"] = score >= 210

        enriched.append(item)

    ranked = sorted(enriched, key=lambda x: float(x.get("target_score") or 0), reverse=True)

    competition = analyze_resolver_competition_v1(ranked)

    results = []
    for item in ranked:
        item["competition_intelligence"] = {
            "competition_action": competition.get("competition_action"),
            "close_call": competition.get("close_call"),
            "score_margin": competition.get("score_margin"),
        }

        decision = decide_resolver_action_v1(item)
        item["decision_intelligence"] = decision
        item["resolver_decision"] = decision.get("decision")
        item["auto_link_allowed"] = decision.get("decision") == "AUTO_LINK"

        results.append(item)

    risky = [
        r for r in results
        if r.get("expected") == "bad" and r.get("resolver_decision") == "AUTO_LINK"
    ]

    return {
        "anchor_phrase": anchor_phrase,
        "passed": len(risky) == 0,
        "bad_auto_links": len(risky),
        "results": [
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "expected": r.get("expected"),
                "target_score": r.get("target_score"),
                "resolver_decision": r.get("resolver_decision"),
                "auto_link_allowed": r.get("auto_link_allowed"),
                "entity_overlap": r.get("entity_intelligence", {}).get("entity_overlap_terms"),
                "competition": r.get("competition_intelligence"),
            }
            for r in results
        ],
    }


def explain_false_positive_attack_test_v1() -> Dict[str, Any]:
    return {
        "layer": "false_positive_attack_test_v1",
        "purpose": "Attack the resolver with confusing candidates and detect unsafe auto-links.",
        "universal": True,
        "checks": [
            "bad candidate auto-linked",
            "close-call downgraded",
            "entity overlap quality",
            "decision safety",
        ],
    }
