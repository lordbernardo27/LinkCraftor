from __future__ import annotations

from typing import Any, Dict, List, Optional


def build_link_decision(
    phrase_ctx: Dict[str, Any],
    scored_results: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Convert scored candidate results into one normalized link decision.

    Returns the top-ranked result as a structured decision object,
    or None if there are no scored results.
    """
    if not phrase_ctx or not scored_results:
        return None

    top = scored_results[0]
    if not top:
        return None

    return {
        "workspaceId": phrase_ctx.get("workspaceId"),
        "docId": phrase_ctx.get("docId"),
        "sectionId": phrase_ctx.get("sectionId"),
        "position": phrase_ctx.get("position"),
        "phraseText": phrase_ctx.get("phraseText"),
        "contextText": phrase_ctx.get("contextText"),
        "selectedTarget": {
            "id": top.get("id"),
            "title": top.get("title"),
            "url": top.get("url"),
            "topicId": top.get("topicId"),
        },
        "decision": {
            "kind": top.get("kind"),
            "tier": top.get("tier"),
            "score": top.get("score"),
            "profile_id": top.get("profile_id"),
        },
        "scores": top.get("scores", {}),
        "feedback": top.get("feedback", {}),
    }