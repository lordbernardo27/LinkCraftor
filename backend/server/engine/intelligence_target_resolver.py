from __future__ import annotations

import re
import json
from pathlib import Path
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

from backend.server.engine.concept_intelligence import concept_match_score
from backend.server.engine.workspace_topic_cluster_store import find_topic_clusters_for_text
from backend.server.engine.workspace_topic_cluster_feedback import get_cluster_feedback
from backend.server.engine.workspace_concept_bridge import bridge_workspace_phrase_to_targets


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



def _is_non_linkable_asset_url(url: str) -> bool:
    u = str(url or "").lower().strip()
    if not u:
        return True

    return (
        "images." in u
        or "/images/" in u
        or "/gcms/" in u
        or "/wp-content/uploads/" in u
        or u.endswith((
            ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif",
            ".pdf", ".mp4", ".mov", ".mp3", ".wav", ".zip"
        ))
    )


# ---------------------------------------------------------
# Active Target Set runtime filter
# ---------------------------------------------------------

def _resolver_data_dir() -> Path:
    here = Path(__file__).resolve()
    return here.parents[1] / "data"


def _active_target_set_path(workspace_id: str) -> Path:
    ws = str(workspace_id or "default").strip() or "default"
    return _resolver_data_dir() / "target_pools" / f"active_target_set_{ws}.json"


def _load_active_target_set(workspace_id: str) -> Dict[str, Any]:
    fp = _active_target_set_path(workspace_id)
    if not fp.exists():
        return {}
    try:
        obj = json.loads(fp.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _norm_url_for_active(value: Any) -> str:
    return str(value or "").strip().rstrip("/").lower()


def _active_values(active: Dict[str, Any], key: str) -> set[str]:
    return {
        _norm_url_for_active(x)
        for x in (active.get(key) or [])
        if str(x or "").strip()
    }


def _filter_targets_by_active_membership(
    workspace_id: str,
    source_type: str,
    targets: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    active = _load_active_target_set(workspace_id)
    if not active:
        return targets

    live_urls = _active_values(active, "active_live_domain_urls")
    imported_urls = _active_values(active, "active_imported_urls")
    draft_ids = _active_values(active, "active_draft_ids")
    document_ids = _active_values(active, "active_document_ids")

    # If the active file exists but all memberships are empty, do not wipe the resolver.
    if not (live_urls or imported_urls or draft_ids or document_ids):
        return targets

    # If this source has no active membership list, it should not participate.
    if source_type == "live_domain" and not live_urls:
        return []
    if source_type == "imported" and not imported_urls:
        return []
    if source_type == "draft" and not draft_ids:
        return []
    if source_type == "document_registry" and not document_ids:
        return []

    out: List[Dict[str, Any]] = []

    for target in targets or []:
        if not isinstance(target, dict):
            continue

        url = _norm_url_for_active(
            target.get("url")
            or target.get("planned_url")
            or target.get("published_url")
            or target.get("placeholder_url")
        )

        target_id = _norm_url_for_active(
            target.get("id")
            or target.get("topic_id")
            or target.get("draft_id")
            or target.get("doc_id")
            or target.get("document_id")
            or target.get("documentId")
        )

        keep = False

        if source_type == "live_domain":
            keep = bool(url and url in live_urls)

        elif source_type == "imported":
            keep = bool(url and url in imported_urls)

        elif source_type == "draft":
            keep = bool(
                (target_id and target_id in draft_ids)
                or (url and url in draft_ids)
            )

        elif source_type == "document_registry":
            keep = bool(target_id and target_id in document_ids)

        if keep:
            out.append(target)

    return out


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

    broad_single_anchor_terms = {
        "baby", "babies", "pregnancy", "pregnant", "health", "care",
        "parent", "parents", "child", "children", "toddler", "toddlers",
    }

    if len(phrase_tokens) <= 1 and next(iter(phrase_tokens), "") in broad_single_anchor_terms:
        return []


    # Dedicated Topic Cluster Resolver first-pass override.
    # If it finds strong cluster candidates, trust those before broad semantic target scoring.
    from backend.server.engine.workspace_topic_cluster_resolver import resolve_topic_cluster_candidates as _cluster_first_pass_resolver

    cluster_first_pass = _cluster_first_pass_resolver(
        workspace_id,
        anchor_phrase,
        limit=limit,
    )
    if cluster_first_pass:
        return cluster_first_pass[: max(1, int(limit or 5))]


    live_domain_targets = load_live_domain_targets(workspace_id)
    imported_targets = load_imported_targets(workspace_id)
    draft_targets = load_draft_targets(workspace_id)
    document_registry_targets = load_document_registry_targets(workspace_id)

    live_domain_targets = _filter_targets_by_active_membership(
        workspace_id,
        "live_domain",
        live_domain_targets,
    )
    imported_targets = _filter_targets_by_active_membership(
        workspace_id,
        "imported",
        imported_targets,
    )
    draft_targets = _filter_targets_by_active_membership(
        workspace_id,
        "draft",
        draft_targets,
    )
    document_registry_targets = _filter_targets_by_active_membership(
        workspace_id,
        "document_registry",
        document_registry_targets,
    )

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

            target_text_for_concepts = " ".join([
                title,
                str(target.get("h1") or ""),
                str(target.get("label") or ""),
                str(target.get("description") or ""),
                str(target.get("path") or ""),
                url.replace("-", " ").replace("/", " "),
            ])

            concept_signal = concept_match_score(anchor_phrase, target_text_for_concepts)
            concept_score = float(concept_signal.get("score") or 0)

            if _is_non_linkable_asset_url(url):
                continue

            target_tokens = (
                _tokens(title)
                |
                _tokens(url.replace("-", " "))
            )

            # Phrase-aware fields from target pools can validate a match
            # even when title/url token overlap is weak.
            phrase_aware_matches_pre = target.get("matched_phrases") if isinstance(target.get("matched_phrases"), list) else []
            phrase_aware_aliases_pre = target.get("aliases") if isinstance(target.get("aliases"), list) else []
            phrase_aware_terms_pre = phrase_aware_matches_pre + phrase_aware_aliases_pre
            anchor_norm_pre = _norm_text(anchor_phrase)

            phrase_pool_exact_pre = any(_norm_text(x) == anchor_norm_pre for x in phrase_aware_terms_pre)
            phrase_pool_contains_pre = any(
                anchor_norm_pre and (
                    anchor_norm_pre in _norm_text(x) or _norm_text(x) in anchor_norm_pre
                )
                for x in phrase_aware_terms_pre
            )

            early_cluster_matches = []
            early_cluster_score = 0.0
            early_cluster_terms = []

            if source_type == "live_domain":
                early_cluster_matches = find_topic_clusters_for_text(
                    workspace_id,
                    " ".join([
                        str(anchor_phrase or ""),
                        str(title or ""),
                        str(url or ""),
                        str(target.get("path") or ""),
                    ]),
                    limit=3,
                )
                early_top_cluster = early_cluster_matches[0] if early_cluster_matches else {}
                early_cluster_score = float(early_top_cluster.get("score") or 0)
                early_cluster_terms = early_top_cluster.get("matched_terms") or []

            weak, reason = _is_weak_target_match(
                phrase_tokens,
                target_tokens,
                intelligence.get("target_score", 0),
            )

            anchor_cluster_terms = sorted(list(_meaningful_tokens(anchor_phrase) & set(early_cluster_terms)))

            cluster_candidate_pass = (
                source_type == "live_domain"
                and early_cluster_score >= 0.65
                and len(anchor_cluster_terms) >= 2
            )

            live_domain_exact_surface_pass = (
                source_type == "live_domain"
                and len(phrase_tokens & target_tokens) >= 2
            )

            # Never allow weak single-word draft/imported matches to bypass safety.
            # But live-domain phrase-aware, concept-aware, or cluster-aware target-pool matches are allowed through.
            if weak and not (
                source_type == "live_domain"
                and (
                    phrase_pool_exact_pre
                    or phrase_pool_contains_pre
                    or concept_score >= 0.25
                    or cluster_candidate_pass
                    or live_domain_exact_surface_pass
                )
            ):
                continue

            target_score = intelligence.get("target_score")
            if target_score is None:
                target_score = intelligence.get("score", 0)

            # Phrase-aware target-pool boost:
            # live_domain_target_pool.py now stores matched_phrases, aliases,
            # active_phrase_matches, semantic_route_score, and target_score.
            # Use those fields as first-class resolver signals.
            phrase_aware_matches = target.get("matched_phrases") if isinstance(target.get("matched_phrases"), list) else []
            phrase_aware_aliases = target.get("aliases") if isinstance(target.get("aliases"), list) else []
            phrase_aware_count = int(target.get("active_phrase_matches") or 0)

            anchor_norm = _norm_text(anchor_phrase)
            phrase_pool_exact = any(_norm_text(x) == anchor_norm for x in phrase_aware_matches + phrase_aware_aliases)
            phrase_pool_contains = any(
                anchor_norm and (
                    anchor_norm in _norm_text(x) or _norm_text(x) in anchor_norm
                )
                for x in phrase_aware_matches + phrase_aware_aliases
            )

            try:
                pool_target_score = float(target.get("target_score") or 0)
            except Exception:
                pool_target_score = 0.0

            if source_type == "live_domain" and phrase_aware_count:
                boost = 0
                if phrase_pool_exact:
                    boost += 180
                elif phrase_pool_contains:
                    boost += 110
                else:
                    boost += min(80, phrase_aware_count * 12)

                target_score = max(float(target_score or 0), pool_target_score) + boost

            if source_type == "live_domain" and live_domain_exact_surface_pass:
                target_score = max(float(target_score or 0), 170)

            if source_type == "live_domain" and concept_score > 0:
                concept_boost = concept_score * 160
                target_score = float(target_score or 0) + concept_boost

            diagnostics = intelligence.get("diagnostics") or {}

            semantic_route_score = intelligence.get("semantic_route_score")
            if semantic_route_score is None:
                semantic_route_score = diagnostics.get("semantic_route_score", 0)

            if source_type == "live_domain":
                try:
                    semantic_route_score = max(
                        float(semantic_route_score or 0),
                        float(target.get("semantic_route_score") or 0),
                    )
                except Exception:
                    pass

            authority_score = intelligence.get("authority_score")
            if authority_score is None:
                authority_score = diagnostics.get("authority_score", 0)

            topic_graph_score = intelligence.get("topic_graph_score")
            if topic_graph_score is None:
                topic_graph_score = diagnostics.get("topic_graph_score", 0)

            rb2_weight_score = intelligence.get("rb2_weight_score")
            if rb2_weight_score is None:
                rb2_weight_score = diagnostics.get("rb2_weight_score", 0)

            cluster_matches = find_topic_clusters_for_text(
                workspace_id,
                " ".join([
                    str(anchor_phrase or ""),
                    str(title or ""),
                    str(url or ""),
                    str(intelligence.get("path") or ""),
                ]),
                limit=3,
            )

            top_cluster = cluster_matches[0] if cluster_matches else {}
            cluster_score = float(top_cluster.get("score") or 0)
            cluster_name = top_cluster.get("cluster_name")
            cluster_matched_terms = top_cluster.get("matched_terms") or []
            cluster_purity_score = float(top_cluster.get("purity_score") or 0)

            target_surface_terms = _meaningful_tokens(" ".join([
                str(title or ""),
                str(url or "").replace("-", " ").replace("/", " "),
                str(intelligence.get("path") or ""),
            ]))
            anchor_surface_overlap = set(_meaningful_tokens(anchor_phrase)) & target_surface_terms

            cluster_runtime_trusted = (
                source_type == "live_domain"
                and cluster_score >= 0.70
                and cluster_purity_score >= 0.75
                and len(set(_meaningful_tokens(anchor_phrase)) & set(cluster_matched_terms)) >= 2
                and len(anchor_surface_overlap) >= 1
            )

            cluster_feedback = get_cluster_feedback(workspace_id, str(cluster_name or "")) if cluster_name else {}
            cluster_acceptance_rate = float(cluster_feedback.get("acceptance_rate") or 0) if isinstance(cluster_feedback, dict) else 0.0
            cluster_rejection_rate = float(cluster_feedback.get("rejection_rate") or 0) if isinstance(cluster_feedback, dict) else 0.0
            cluster_feedback_total = int(cluster_feedback.get("total") or 0) if isinstance(cluster_feedback, dict) else 0

            if cluster_runtime_trusted:
                target_score = float(target_score or 0) + (cluster_score * 90)

            if cluster_feedback_total >= 3 and cluster_acceptance_rate >= 0.75:
                target_score = float(target_score or 0) + 25

            if cluster_feedback_total >= 3 and cluster_rejection_rate >= 0.60:
                target_score = float(target_score or 0) - 45

            runtime_normalized_score = _runtime_normalized_score(
                source_type,
                intelligence,
                target_score,
            )

            # Cluster Confidence Gating v1:
            # Safe auto-linking requires either strong phrase-aware evidence,
            # trusted same-cluster evidence, or high runtime confidence.
            confidence_floor = 0.70

            strong_phrase_evidence = bool(
                phrase_pool_exact
                or phrase_pool_contains
                or phrase_aware_count >= 2
            )

            strong_cluster_evidence = bool(cluster_runtime_trusted)

            auto_link_allowed = bool(
                runtime_normalized_score >= confidence_floor
                and (
                    strong_phrase_evidence
                    or strong_cluster_evidence
                    or live_domain_exact_surface_pass
                    or concept_score >= 0.45
                )
            )

            suggest_only = not auto_link_allowed

            resolver_reason = (
                "topic_cluster_match"
                if strong_cluster_evidence
                else "phrase_aware_target_pool_match"
                if strong_phrase_evidence
                else "concept_intelligence_match"
                if concept_score >= 0.45
                else "semantic_authority_topic_match"
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
                    "resolver_reason": resolver_reason,
                    "auto_link_allowed": auto_link_allowed,
                    "suggest_only": suggest_only,
                    "confidence_floor": confidence_floor,
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

                    # Phrase-aware target-pool diagnostics
                    "target_pool_matched_phrases": phrase_aware_matches,
                    "target_pool_aliases": phrase_aware_aliases,
                    "target_pool_active_phrase_matches": phrase_aware_count,
                    "target_pool_phrase_exact_match": phrase_pool_exact,
                    "target_pool_phrase_contains_match": phrase_pool_contains,

                    # Concept Intelligence diagnostics
                    "concept_score": concept_score,
                    "concept_matched_terms": concept_signal.get("matched_terms", []),
                    "concepts": concept_signal.get("concepts", []),
                    "concept_expansions": concept_signal.get("expansions", []),

                    # Topic Cluster Intelligence diagnostics
                    "cluster_score": cluster_score,
                    "cluster_name": cluster_name,
                    "cluster_matched_terms": cluster_matched_terms,
                    "cluster_matches": cluster_matches,
                    "cluster_purity_score": cluster_purity_score,
                    "cluster_runtime_trusted": cluster_runtime_trusted,
                    "cluster_boost_applied": bool(cluster_runtime_trusted),
                    "cluster_feedback_total": cluster_feedback_total,
                    "cluster_acceptance_rate": cluster_acceptance_rate,
                    "cluster_rejection_rate": cluster_rejection_rate,

                    "weak_match_suppressed": False,
                }
            )

    # Workspace Concept Bridge fallback:
    # If normal resolver found nothing, try safe workspace-level concept bridging.
    if not resolved:
        bridge_hits = bridge_workspace_phrase_to_targets(workspace_id, anchor_phrase, limit=limit)
        for hit in bridge_hits:
            score = float(hit.get("bridge_score") or 0)
            resolved.append({
                "phrase": anchor_phrase,
                "url": hit.get("url"),
                "title": hit.get("title"),
                "target_score": score * 300,
                "semantic_route_score": score * 100,
                "authority_score": 0,
                "topic_graph_score": 0,
                "rb2_weight_score": 0,
                "path_score": None,
                "matched_title_tokens": hit.get("bridge_overlap_tokens", []),
                "matched_url_tokens": hit.get("bridge_overlap_tokens", []),
                "runtime_normalized_score": score,
                "resolver_confidence": score,
                "resolver_reason": "workspace_concept_bridge_fallback",
                "source_type": "live_domain",
                "page_type_hint": None,
                "priority_bucket": None,
                "import_source": None,
                "draft_id": None,
                "planned_url": None,
                "placeholder_url": None,
                "published_url": None,
                "semantic_intent_score": None,
                "freshness_score": None,
                "publish_transition_score": None,
                "semantic_gate_multiplier": None,
                "path": None,
                "target_pool_matched_phrases": [],
                "target_pool_aliases": [],
                "target_pool_active_phrase_matches": 0,
                "target_pool_phrase_exact_match": False,
                "target_pool_phrase_contains_match": False,
                "concept_score": score,
                "concept_matched_terms": hit.get("bridge_overlap_tokens", []),
                "concepts": [],
                "concept_expansions": [],
                "bridge_score": score,
                "bridge_reason": hit.get("bridge_reason"),
                "cluster_score": 0,
                "cluster_name": None,
                "cluster_matched_terms": [],
                "cluster_matches": [],
                "cluster_boost_applied": False,
                "weak_match_suppressed": False,
            })

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

        cluster_guard_pass = bool(item.get("cluster_runtime_trusted"))

        phrase_aware_guard_pass = bool(
            str(item.get("source_type") or "") == "live_domain"
            and (
                bool(item.get("target_pool_phrase_exact_match"))
                or bool(item.get("target_pool_phrase_contains_match"))
                or int(item.get("target_pool_active_phrase_matches") or 0) >= 2
            )
        )

        if (
            not cluster_guard_pass
            and not phrase_aware_guard_pass
            and not _passes_phrase_title_overlap_guard(
                str(item.get("phrase") or item.get("anchor") or ""),
                str(item.get("title") or ""),
                str(item.get("source_type") or ""),
            )
        ):
            item["resolver_rejected"] = True
            item["resolver_rejection_reason"] = "weak_phrase_title_overlap"
            item["resolver_rejection_stage"] = "phrase_title_overlap_guard"
            continue

        if cluster_guard_pass:
            item["resolver_reason"] = "topic_cluster_match"
            item["cluster_guard_pass"] = True
        elif item.get("resolver_reason") == "topic_cluster_match":
            item["resolver_reason"] = "semantic_authority_topic_match"
            item["cluster_guard_pass"] = False

        # Ensure all resolver outputs, including fallback/bridge outputs,
        # carry auto-link gating fields.
        if "confidence_floor" not in item:
            item["confidence_floor"] = SAFE_AUTO_LINK_FLOOR

        if "auto_link_allowed" not in item:
            item["auto_link_allowed"] = bool(confidence >= float(item.get("confidence_floor") or SAFE_AUTO_LINK_FLOOR))

        if "suggest_only" not in item:
            item["suggest_only"] = not bool(item.get("auto_link_allowed"))

        filtered.append(item)

    return filtered[: max(1, int(limit or 5))]
