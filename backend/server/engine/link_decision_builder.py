from __future__ import annotations

from typing import Any, Dict, List, Optional

def build_link_decision(
    phrase_ctx: Dict[str, Any],
    scored_results: List[Dict[str, Any]],
    supporting_intelligence_inputs: Optional[Dict[str, Any]] = None,
    imported_di_signal: Optional[Dict[str, Any]] = None,
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

    supporting = (
        supporting_intelligence_inputs
        if isinstance(supporting_intelligence_inputs, dict)
        else {}
    )

    sources = supporting.get("sources") if isinstance(supporting.get("sources"), dict) else {}

    imported_signal = imported_di_signal if isinstance(imported_di_signal, dict) else {}

    di_support_summary = {
        "enabled": bool(supporting.get("enabled")),
        "runtime_highlight_injection_allowed": False,
        "live_domain_feeds_di": bool((sources.get("live_domain") or {}).get("feeds_di")),
        "draft_feeds_di": bool((sources.get("draft") or {}).get("feeds_di")),
        "imported_feeds_di": bool((sources.get("imported") or {}).get("feeds_di")),
        "live_domain_phrase_count": int((sources.get("live_domain") or {}).get("phrase_count") or 0),
        "draft_phrase_count": int((sources.get("draft") or {}).get("phrase_count") or 0),
        "imported_phrase_count": int((sources.get("imported") or {}).get("phrase_count") or 0),
    }

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
        "di_score_adjustments": top.get("di_score_adjustments", {}),
        "feedback": top.get("feedback", {}),
        "di_support_summary": di_support_summary,
        "imported_di_signal": imported_signal,
        "di_supporting_intelligence": {
            "enabled": bool(supporting.get("enabled")),
            "purpose": supporting.get("purpose"),
            "runtime_highlight_injection_allowed": False,
            "layers": supporting.get("layers") if isinstance(supporting.get("layers"), list) else [],
            "sources": supporting.get("sources") if isinstance(supporting.get("sources"), dict) else {},
        },
    }