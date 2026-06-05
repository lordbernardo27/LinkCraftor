
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


BUILD_ID = "PHASE-2.1-LOGICAL-INFERENCE-V1-ADVISORY-ONLY"


@dataclass(frozen=True)
class LogicalInferenceResult:
    build_id: str
    layer: str
    advisory_only: bool
    can_change_runtime: bool
    anchor_phrase: str
    target_title: str
    target_url: str
    inference_score: float
    decision: str
    rule_based_reasons: List[str] = field(default_factory=list)
    semantic_inference_chain: List[str] = field(default_factory=list)
    runtime_reasoning: List[str] = field(default_factory=list)
    link_reasoning: List[str] = field(default_factory=list)
    safety_flags: Dict[str, bool] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _tokens(text: str) -> set[str]:
    stop = {"the", "a", "an", "of", "for", "to", "and", "in", "on", "with", "by", "is", "are"}
    clean = "".join(ch.lower() if ch.isalnum() else " " for ch in str(text or ""))
    return {t for t in clean.split() if t and t not in stop}


def _overlap_score(a: str, b: str) -> float:
    ta = _tokens(a)
    tb = _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(1, len(ta | tb))


def analyze_logical_inference_v1(
    anchor_phrase: str,
    target_title: str,
    target_url: str = "",
    context: str = "",
    link_type: str = "internal",
) -> Dict[str, Any]:
    """
    Phase 2.1 Logical Inference Intelligence.

    IMPORTANT:
    - Advisory only.
    - Does not change highlights.
    - Does not change target selection.
    - Does not change scoring.
    - Does not assign URLs.
    """

    rule_reasons: List[str] = []
    chain: List[str] = []
    runtime_reasoning: List[str] = []
    link_reasoning: List[str] = []

    anchor_title_score = _overlap_score(anchor_phrase, target_title)
    context_title_score = _overlap_score(context, target_title)
    anchor_context_score = _overlap_score(anchor_phrase, context)

    if len(anchor_phrase.split()) >= 2:
        rule_reasons.append("Anchor phrase has enough words to carry linking intent.")
    else:
        rule_reasons.append("Anchor phrase may be too short for strong linking intent.")

    if anchor_title_score > 0:
        rule_reasons.append("Anchor phrase shares meaning tokens with the target title.")
    else:
        rule_reasons.append("Anchor phrase has weak direct token overlap with the target title.")

    if target_url:
        rule_reasons.append("Target URL is present for reasoning review.")
    else:
        rule_reasons.append("Target URL is missing; reasoning can only inspect phrase/title fit.")

    if link_type == "internal":
        rule_reasons.append("Link type is internal; reasoning must preserve internal-linking rules.")
    elif link_type == "semantic":
        rule_reasons.append("Link type is semantic; reasoning must remain separate from internal linking.")
    else:
        rule_reasons.append("Link type is unknown; reasoning should not influence runtime.")

    chain.append(f"Anchor phrase reviewed: {anchor_phrase}")
    chain.append(f"Target title reviewed: {target_title}")
    chain.append(f"Anchor-to-title overlap score: {round(anchor_title_score, 3)}")
    chain.append(f"Context-to-title overlap score: {round(context_title_score, 3)}")
    chain.append(f"Anchor-to-context overlap score: {round(anchor_context_score, 3)}")

    runtime_reasoning.append("Runtime impact blocked: this layer is advisory-only.")
    runtime_reasoning.append("No highlight selection, scoring, target selection, or URL assignment is changed.")

    if anchor_title_score >= 0.35 or context_title_score >= 0.25:
        decision = "strong_reasoning_support"
        link_reasoning.append("The anchor/context appears logically connected to the target.")
    elif anchor_title_score >= 0.15 or context_title_score >= 0.15:
        decision = "moderate_reasoning_support"
        link_reasoning.append("The link may be reasonable, but needs stronger supporting evidence.")
    else:
        decision = "weak_reasoning_support"
        link_reasoning.append("The link has weak visible reasoning support and should be reviewed.")

    inference_score = round(
        min(1.0, (anchor_title_score * 0.55) + (context_title_score * 0.30) + (anchor_context_score * 0.15)),
        3,
    )

    result = LogicalInferenceResult(
        build_id=BUILD_ID,
        layer="2.1 Logical Inference",
        advisory_only=True,
        can_change_runtime=False,
        anchor_phrase=anchor_phrase,
        target_title=target_title,
        target_url=target_url,
        inference_score=inference_score,
        decision=decision,
        rule_based_reasons=rule_reasons,
        semantic_inference_chain=chain,
        runtime_reasoning=runtime_reasoning,
        link_reasoning=link_reasoning,
        safety_flags={
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "keeps_internal_and_semantic_linking_separate": True,
        },
    )

    return asdict(result)


def explain_logical_inference_capabilities_v1() -> Dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "layer": "2.1 Logical Inference",
        "status": "available",
        "mode": "advisory_only",
        "capabilities": [
            "2.1.1 Rule-Based Reasoning",
            "2.1.2 Semantic Inference Chains",
            "2.1.3 Runtime Inference Engine",
            "2.1.4 Link Reasoning Logic",
        ],
        "runtime_permissions": {
            "can_change_highlights": False,
            "can_change_scores": False,
            "can_change_targets": False,
            "can_assign_urls": False,
            "can_block_links": False,
        },
    }
