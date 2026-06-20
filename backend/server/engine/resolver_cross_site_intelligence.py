from __future__ import annotations

from typing import Any, Dict, List


def analyze_cross_site_intelligence_v1(
    *,
    workspace_id: str,
    target_url: str,
    related_workspace_signals: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:

    related_workspace_signals = related_workspace_signals or []

    supporting_sites = 0
    aggregate_score = 0.0

    for signal in related_workspace_signals:
        supporting_sites += 1

        try:
            aggregate_score += float(
                signal.get("support_score") or 0
            )
        except Exception:
            pass

    average_support = (
        aggregate_score / supporting_sites
        if supporting_sites > 0
        else 0.0
    )

    if average_support >= 80:
        confidence = "high"
        boost = 20.0
    elif average_support >= 50:
        confidence = "medium"
        boost = 10.0
    elif supporting_sites > 0:
        confidence = "low"
        boost = 5.0
    else:
        confidence = "none"
        boost = 0.0

    return {
        "has_cross_site_analysis": True,
        "workspace_id": workspace_id,
        "target_url": target_url,
        "supporting_sites": supporting_sites,
        "average_support_score": round(average_support, 4),
        "cross_site_confidence": confidence,
        "cross_site_boost": boost,
    }


def explain_cross_site_intelligence_v1() -> Dict[str, Any]:
    return {
        "layer": "resolver_cross_site_intelligence_v1",
        "purpose": "Use network-wide linking intelligence across multiple workspaces and sites.",
        "universal": True,
        "uses": [
            "related workspace signals",
            "cross-site support",
            "network consensus",
            "organization-wide intelligence",
        ],
        "does_not_use": [
            "health rules",
            "finance rules",
            "legal rules",
            "industry-specific hardcoding",
        ],
    }
