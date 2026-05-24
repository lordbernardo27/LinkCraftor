from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from backend.server.pools.target_pools.live_domain_target_intelligence import (
    load_live_domain_targets,
    score_live_domain_target,
)

from backend.server.pools.target_pools.imported_target_intelligence import (
    load_imported_targets,
    score_imported_target,
)

from backend.server.pools.target_pools.draft_target_intelligence import (
    load_draft_targets,
    score_draft_target,
)

from backend.server.pools.target_pools.document_registry_target_intelligence import (
    load_document_registry_targets,
    runtime_safe_payload as score_document_registry_target,
)


# ---------------------------------------------------------
# Tokenization
# ---------------------------------------------------------

def _norm_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def _stem_token(token: str) -> str:
    token = str(token or "").lower().strip()

    irregular = {
        "tracking": "track",
        "tracked": "track",
        "tracks": "track",
        "accurately": "accurate",
        "calculating": "calculate",
        "calculated": "calculate",
        "calculates": "calculate",
        "pregnancies": "pregnancy",
        "fertility": "fertile",
    }

    if token in irregular:
        return irregular[token]

    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]

    if len(token) > 4 and token.endswith("ed"):
        return token[:-2]

    if len(token) > 4 and token.endswith("s"):
        return token[:-1]

    return token


def _tokens(value: Any) -> set[str]:
    text = _norm_text(value)

    return {
        _stem_token(t)
        for t in re.split(r"[^a-z0-9]+", text)
        if len(t) >= 3
    }


# ---------------------------------------------------------
# Weak Match Suppression
# ---------------------------------------------------------

def _is_weak_target_match(
    phrase_tokens: set[str],
    target_tokens: set[str],
    score: float,
) -> Tuple[bool, str]:

    overlap = phrase_tokens & target_tokens

    if not overlap:
        return True, "no_token_overlap"

    if len(overlap) == 1 and score < 120:
        return True, "single_weak_overlap"

    return False, ""


def _runtime_normalized_score(source_type: str, intelligence: Dict[str, Any], target_score: Any) -> float:
    try:
        raw = float(target_score or 0)
    except Exception:
        raw = 0.0

    if source_type in {"draft", "document_registry"}:
        return max(0.0, min(1.0, raw))

    # Live-domain/imported legacy scores commonly use larger numeric scales.
    if source_type in {"live_domain", "imported"}:
        return max(0.0, min(1.0, raw / 300.0))

    return max(0.0, min(1.0, raw))


def _meaningful_tokens(text: str) -> set[str]:
    stop = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "how", "in", "into", "is", "it", "of", "on", "or", "the", "to",
        "what", "when", "where", "why", "with", "your", "you"
    }
    tokens = re.findall(r"[a-z0-9]+", str(text or "").lower())
    return {_stem_token(t) for t in tokens if len(t) >= 3 and t not in stop}


def _passes_phrase_title_overlap_guard(phrase: str, title: str, source_type: str) -> bool:
    # Guard mainly protects draft/imported semantic drift.
    if source_type not in {"draft", "imported"}:
        return True

    p = _meaningful_tokens(phrase)
    t = _meaningful_tokens(title)
    overlap = p & t

    # Require at least two meaningful shared tokens for draft/imported auto-linking.
    return len(overlap) >= 2


# ---------------------------------------------------------
# Resolver
# ---------------------------------------------------------

def resolve_intelligent_targets(
    workspace_id: str,
    anchor_phrase: str,
    limit: int = 5,
) -> List[Dict[str, Any]]:

    anchor_phrase = _norm_text(anchor_phrase)

    if not anchor_phrase:
        return []

    phrase_tokens = _tokens(anchor_phrase)

    live_domain_targets = load_live_domain_targets(workspace_id)
    imported_targets = load_imported_targets(workspace_id)
    draft_targets = load_draft_targets(workspace_id)
    document_registry_targets = load_document_registry_targets(workspace_id)

    resolved: List[Dict[str, Any]] = []

    source_batches = [
        ("live_domain", live_domain_targets, score_live_domain_target),
        ("imported", imported_targets, score_imported_target),
        ("draft", draft_targets, score_draft_target),
        ("document_registry", document_registry_targets, score_document_registry_target),
    ]

    for source_type, targets, scorer in source_batches:
        for target in targets:
            intelligence = scorer(
                anchor_phrase,
                target,
            )

            title = str(target.get("title") or target.get("h1") or "")
            url = str(target.get("url") or "")

            target_tokens = (
                _tokens(title)
                |
                _tokens(url.replace("-", " "))
            )

            weak, reason = _is_weak_target_match(
                phrase_tokens,
                target_tokens,
                intelligence.get("target_score", 0),
            )

            # Never allow weak single-word draft/imported matches to bypass safety.
            if weak:
                continue

            target_score = intelligence.get("target_score")
            if target_score is None:
                target_score = intelligence.get("score", 0)

            diagnostics = intelligence.get("diagnostics") or {}

            semantic_route_score = intelligence.get("semantic_route_score")
            if semantic_route_score is None:
                semantic_route_score = diagnostics.get("semantic_route_score", 0)

            authority_score = intelligence.get("authority_score")
            if authority_score is None:
                authority_score = diagnostics.get("authority_score", 0)

            topic_graph_score = intelligence.get("topic_graph_score")
            if topic_graph_score is None:
                topic_graph_score = diagnostics.get("topic_graph_score", 0)

            rb2_weight_score = intelligence.get("rb2_weight_score")
            if rb2_weight_score is None:
                rb2_weight_score = diagnostics.get("rb2_weight_score", 0)

            runtime_normalized_score = _runtime_normalized_score(
                source_type,
                intelligence,
                target_score,
            )

            resolved.append(
                {
                    "phrase": anchor_phrase,
                    "url": url,
                    "title": title,
                    "target_score": target_score,
                    "semantic_route_score": semantic_route_score,
                    "authority_score": authority_score,
                    "topic_graph_score": topic_graph_score,
                    "rb2_weight_score": rb2_weight_score,
                    "path_score": intelligence.get("path_score"),
                    "matched_title_tokens": intelligence.get("matched_title_tokens"),
                    "matched_url_tokens": intelligence.get("matched_url_tokens"),
                    "runtime_normalized_score": runtime_normalized_score,
                    "resolver_confidence": (
                        min(1.0, float(target_score or 0) / 300.0)
                        if source_type != "document_registry"
                        else float(target_score or 0)
                    ),
                    "resolver_reason": "semantic_authority_topic_match",
                    "source_type": source_type,
                    "page_type_hint": intelligence.get("page_type_hint"),
                    "priority_bucket": intelligence.get("priority_bucket"),
                    "import_source": intelligence.get("import_source"),

                    # Draft intelligence diagnostics
                    "draft_id": intelligence.get("draft_id"),
                    "planned_url": intelligence.get("planned_url"),
                    "placeholder_url": intelligence.get("placeholder_url"),
                    "published_url": intelligence.get("published_url"),
                    "semantic_intent_score": intelligence.get("semantic_intent_score"),
                    "freshness_score": intelligence.get("freshness_score"),
                    "publish_transition_score": intelligence.get("publish_transition_score"),
                    "semantic_gate_multiplier": intelligence.get("semantic_gate_multiplier"),

                    "path": intelligence.get("path"),
                    "weak_match_suppressed": False,
                }
            )

    resolved.sort(
        key=lambda x: (
            float(x.get("runtime_normalized_score", 0) or 0),
            float(x.get("semantic_route_score", 0) or 0),
            float(x.get("authority_score", 0) or 0),
        ),
        reverse=True,
    )

    # ---------------------------------------------------------
    # Runtime auto-link protection
    # Prevent weak semantic drift / forced nearest-neighbor links.
    # Anything below this floor is not safe enough for automatic linking.
    # ---------------------------------------------------------
    SAFE_AUTO_LINK_FLOOR = 0.48

    filtered: List[Dict[str, Any]] = []

    for item in resolved:
        confidence = float(item.get("runtime_normalized_score", 0) or 0)

        if confidence < SAFE_AUTO_LINK_FLOOR:
            item["resolver_rejected"] = True
            item["resolver_rejection_reason"] = "domain_mismatch"
            item["resolver_rejection_stage"] = "runtime_auto_link_floor"
            continue

        if not _passes_phrase_title_overlap_guard(
            str(item.get("phrase") or item.get("anchor") or ""),
            str(item.get("title") or ""),
            str(item.get("source_type") or ""),
        ):
            item["resolver_rejected"] = True
            item["resolver_rejection_reason"] = "weak_phrase_title_overlap"
            item["resolver_rejection_stage"] = "phrase_title_overlap_guard"
            continue

        filtered.append(item)

    return filtered[: max(1, int(limit or 5))]