
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Set


BUILD_ID = "PHASE-2.3.4-ANCHOR-PURPOSE-ANALYSIS-V1-ADVISORY-ONLY"


PURPOSE_KEYWORDS: Dict[str, Set[str]] = {
    "INFORMATIONAL": {
        "what", "why", "meaning", "definition", "symptoms", "signs",
        "causes", "benefits", "overview", "explained", "guide"
    },
    "INSTRUCTIONAL": {
        "how", "steps", "tutorial", "learn", "setup", "install",
        "configure", "build", "create", "use"
    },
    "COMPARISON": {
        "vs", "versus", "compare", "comparison", "alternative",
        "alternatives", "best", "top", "review", "reviews"
    },
    "SAFETY": {
        "warning", "risk", "risks", "side", "effects", "safe",
        "safety", "danger", "precaution", "contraindication"
    },
    "TRANSACTIONAL": {
        "buy", "price", "pricing", "cost", "deal", "discount",
        "order", "subscribe", "plan", "plans"
    },
    "TOOL_USAGE": {
        "calculator", "checker", "monitor", "generator", "planner",
        "tracker", "tool", "assistant", "analyzer"
    },
    "NAVIGATIONAL": {
        "login", "sign", "account", "dashboard", "pricing",
        "contact", "support", "homepage", "docs"
    },
    "ACTIONABLE": {
        "checklist", "template", "strategy", "tips", "actions",
        "fix", "optimize", "improve", "audit"
    },
    "REFERENCE": {
        "citation", "reference", "examples", "table", "list",
        "requirements", "policy", "regulation", "standard"
    },
}


@dataclass(frozen=True)
class AnchorPurposeResult:
    build_id: str
    layer: str
    advisory_only: bool
    can_change_runtime: bool
    anchor_phrase: str
    context: str
    primary_purpose: str
    confidence: float
    purpose_scores: Dict[str, float] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    existing_intent_sources_referenced: List[str] = field(default_factory=list)
    safety_flags: Dict[str, bool] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _tokens(text: str) -> List[str]:
    clean = "".join(ch.lower() if ch.isalnum() else " " for ch in str(text or ""))
    return [t for t in clean.split() if t]


def _token_set(text: str) -> Set[str]:
    return set(_tokens(text))


def analyze_anchor_purpose_v1(
    anchor_phrase: str,
    context: str = "",
    link_type: str = "internal",
) -> Dict[str, Any]:
    """
    2.3.4 Anchor-Purpose Analysis.

    Advisory only:
    - Does not change runtime.
    - Does not change scores.
    - Does not change highlights.
    - Does not change target selection.
    - Does not assign URLs.
    """

    anchor_tokens = _token_set(anchor_phrase)
    context_tokens = _token_set(context)
    combined = anchor_tokens | context_tokens

    purpose_scores: Dict[str, float] = {}
    evidence: List[str] = []

    for purpose, keywords in PURPOSE_KEYWORDS.items():
        anchor_hits = anchor_tokens & keywords
        context_hits = context_tokens & keywords

        score = 0.0
        score += len(anchor_hits) * 0.35
        score += len(context_hits) * 0.12

        if anchor_hits:
            evidence.append(f"{purpose}: anchor matched {sorted(anchor_hits)}")
        if context_hits:
            evidence.append(f"{purpose}: context matched {sorted(context_hits)}")

        purpose_scores[purpose] = round(min(1.0, score), 3)

    if not combined:
        primary = "UNKNOWN"
        confidence = 0.0
    else:
        primary = max(purpose_scores, key=lambda k: purpose_scores[k])
        confidence = purpose_scores.get(primary, 0.0)

        if confidence <= 0:
            primary = "INFORMATIONAL"
            confidence = 0.15
            evidence.append("Fallback: no strong purpose terms found; defaulted to informational review.")

    result = AnchorPurposeResult(
        build_id=BUILD_ID,
        layer="2.3.4 Anchor-Purpose Analysis",
        advisory_only=True,
        can_change_runtime=False,
        anchor_phrase=anchor_phrase,
        context=context,
        primary_purpose=primary,
        confidence=round(confidence, 3),
        purpose_scores=purpose_scores,
        evidence=evidence,
        existing_intent_sources_referenced=[
            "upload_phrase_selector._is_intent_phrase",
            "semantic_completeness_intelligence.analyze_anchor_intent_completeness_v1",
            "cross_document_reasoning.intent_aware_linking_schema_v1",
        ],
        safety_flags={
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "keeps_internal_and_semantic_linking_separate": True,
            "metadata_only": True,
        },
    )

    return asdict(result)


def explain_anchor_purpose_capabilities_v1() -> Dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "layer": "2.3.4 Anchor-Purpose Analysis",
        "status": "available",
        "mode": "advisory_only",
        "purpose_taxonomy": sorted(PURPOSE_KEYWORDS.keys()),
        "references_existing_2_3_layers": {
            "2.3.1_user_intent_detection": "existing_upload_phrase_selector",
            "2.3.2_content_intent_detection": "existing_semantic_completeness_intelligence",
            "2.3.3_link_intent_reasoning": "existing_cross_document_reasoning",
        },
        "runtime_permissions": {
            "can_change_highlights": False,
            "can_change_scores": False,
            "can_change_targets": False,
            "can_assign_urls": False,
            "can_block_links": False,
        },
    }
