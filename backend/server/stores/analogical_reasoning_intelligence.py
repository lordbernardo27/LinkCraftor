
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Set


BUILD_ID = "PHASE-2.2-ANALOGICAL-REASONING-V1-ADVISORY-ONLY"


QUESTION_STARTERS = {
    "how", "what", "why", "when", "where", "can", "does", "do", "is", "are"
}

INTENT_WORDS = {

    # Universal
    "guide", "tutorial", "tips", "strategy", "strategies",
    "checklist", "template", "examples", "comparison",
    "compare", "review", "reviews", "alternatives",
    "features", "pricing", "cost", "requirements",
    "benefits", "advantages", "disadvantages",
    "best", "top", "improve", "improvement",
    "optimization", "management", "planning",
    "analysis", "analytics", "report", "reports",
    "setup", "configuration", "installation",

    # Health
    "symptoms", "causes", "treatment", "signs",
    "diagnosis", "prevention", "risk", "effects",

    # Business
    "revenue", "sales", "marketing", "conversion",
    "roi", "profit", "growth",

    # SEO
    "ranking", "keyword", "backlink",
    "internal", "external", "cluster",

    # Software
    "api", "sdk", "integration",
    "deployment", "architecture",

    # Education
    "course", "lesson", "training",
    "exam", "study",

    # Finance
    "investment", "investing",
    "budget", "budgeting",
    "loan", "mortgage",

    # Legal
    "compliance", "regulation",
    "policy", "contract",

    # Generic tool class
    "calculator", "checker", "monitor",
    "generator", "planner", "tracker"
}

FUNCTIONAL_WORDS = {
    "calculator", "checker", "monitor", "generator", "planner", "tracker",
    "guide", "tool", "assistant"
}


@dataclass(frozen=True)
class AnalogicalReasoningResult:
    build_id: str
    layer: str
    advisory_only: bool
    can_change_runtime: bool
    anchor_phrase: str
    target_title: str
    target_url: str
    analogy_score: float
    decision: str
    pattern_analogy: Dict[str, Any] = field(default_factory=dict)
    semantic_analogy: Dict[str, Any] = field(default_factory=dict)
    cross_topic_mapping: Dict[str, Any] = field(default_factory=dict)
    similar_structure_learning: Dict[str, Any] = field(default_factory=dict)
    reasoning_output: List[str] = field(default_factory=list)
    safety_flags: Dict[str, bool] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _tokens(text: str) -> List[str]:
    clean = "".join(ch.lower() if ch.isalnum() else " " for ch in str(text or ""))
    return [t for t in clean.split() if t]


def _token_set(text: str) -> Set[str]:
    return set(_tokens(text))


def _shape_signature(text: str) -> List[str]:
    out: List[str] = []
    for tok in _tokens(text):
        if tok in QUESTION_STARTERS:
            out.append("QUESTION")
        elif tok in INTENT_WORDS:
            out.append("INTENT")
        elif tok in FUNCTIONAL_WORDS:
            out.append("FUNCTION")
        elif tok.isdigit():
            out.append("NUMBER")
        else:
            out.append("TOPIC")
    return out[:8]


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))


def _shape_similarity(a: List[str], b: List[str]) -> float:
    if not a or not b:
        return 0.0
    max_len = max(len(a), len(b))
    matches = sum(1 for x, y in zip(a, b) if x == y)
    return matches / max_len


def analyze_analogical_reasoning_v1(
    anchor_phrase: str,
    target_title: str,
    target_url: str = "",
    context: str = "",
    link_type: str = "internal",
) -> Dict[str, Any]:
    """
    Phase 2.2 Analogical Reasoning Intelligence.

    Advisory only:
    - Does not change scores.
    - Does not change buckets.
    - Does not change highlights.
    - Does not change target selection.
    - Does not assign URLs.
    """

    anchor_tokens = _token_set(anchor_phrase)
    title_tokens = _token_set(target_title)
    context_tokens = _token_set(context)

    anchor_shape = _shape_signature(anchor_phrase)
    title_shape = _shape_signature(target_title)

    lexical_overlap = _jaccard(anchor_tokens, title_tokens)
    context_overlap = _jaccard(context_tokens, title_tokens)
    structure_overlap = _shape_similarity(anchor_shape, title_shape)

    shared_intent_words = sorted((anchor_tokens | context_tokens) & title_tokens & INTENT_WORDS)
    shared_function_words = sorted((anchor_tokens | context_tokens) & title_tokens & FUNCTIONAL_WORDS)

    pattern_score = structure_overlap
    semantic_score = max(lexical_overlap, context_overlap)
    functional_score = 0.25 if shared_function_words else 0.0

    analogy_score = round(
        min(1.0, (pattern_score * 0.40) + (semantic_score * 0.45) + functional_score),
        3,
    )

    # SAFETY PATCH:
    # Structure alone must never create a moderate/strong analogy.
    no_semantic_connection = (
        lexical_overlap <= 0.0 and
        context_overlap <= 0.0 and
        not shared_intent_words and
        not shared_function_words
    )

    if no_semantic_connection:
        analogy_score = min(analogy_score, 0.29)
        decision = "weak_analogical_support"

    elif analogy_score >= 0.55:
        decision = "strong_analogical_support"

    elif analogy_score >= 0.30:
        decision = "moderate_analogical_support"

    else:
        decision = "weak_analogical_support"

    reasoning_output = [
        f"Anchor shape: {' > '.join(anchor_shape) if anchor_shape else 'none'}",
        f"Target shape: {' > '.join(title_shape) if title_shape else 'none'}",
        f"Pattern similarity score: {round(pattern_score, 3)}",
        f"Semantic overlap score: {round(semantic_score, 3)}",
        f"Functional analogy bonus: {round(functional_score, 3)}",
        "Runtime impact blocked: analogical reasoning is advisory-only.",
    ]

    result = AnalogicalReasoningResult(
        build_id=BUILD_ID,
        layer="2.2 Analogical Reasoning",
        advisory_only=True,
        can_change_runtime=False,
        anchor_phrase=anchor_phrase,
        target_title=target_title,
        target_url=target_url,
        analogy_score=analogy_score,
        decision=decision,
        pattern_analogy={
            "capability": "2.2.1 Pattern Analogy Detection",
            "anchor_shape": anchor_shape,
            "target_shape": title_shape,
            "structure_overlap": round(structure_overlap, 3),
        },
        semantic_analogy={
            "capability": "2.2.2 Semantic Analogy Relationships",
            "lexical_overlap": round(lexical_overlap, 3),
            "context_overlap": round(context_overlap, 3),
            "shared_intent_words": shared_intent_words,
        },
        cross_topic_mapping={
            "capability": "2.2.3 Cross-Topic Analogical Mapping",
            "shared_function_words": shared_function_words,
            "can_detect_same_tool_family": bool(shared_function_words),
            "link_type_reviewed": link_type,
        },
        similar_structure_learning={
            "capability": "2.2.4 Similar-Structure Learning",
            "structure_can_be_reused_as_pattern": structure_overlap >= 0.50,
            "pattern_learning_mode": "metadata_only",
        },
        reasoning_output=reasoning_output,
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


def explain_analogical_reasoning_capabilities_v1() -> Dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "layer": "2.2 Analogical Reasoning",
        "status": "available",
        "mode": "advisory_only",
        "capabilities": [
            "2.2.1 Pattern Analogy Detection",
            "2.2.2 Semantic Analogy Relationships",
            "2.2.3 Cross-Topic Analogical Mapping",
            "2.2.4 Similar-Structure Learning",
        ],
        "runtime_permissions": {
            "can_change_highlights": False,
            "can_change_scores": False,
            "can_change_targets": False,
            "can_assign_urls": False,
            "can_block_links": False,
        },
    }
