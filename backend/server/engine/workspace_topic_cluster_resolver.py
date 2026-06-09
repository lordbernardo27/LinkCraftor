from __future__ import annotations

import re
from typing import Any, Dict, List

from backend.server.engine.workspace_topic_cluster_store import (
    find_topic_clusters_for_text,
    load_workspace_topic_clusters,
)


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def _tokens(value: Any) -> set[str]:
    stop = {
        "a","an","and","are","as","at","be","by","for","from","how","in","into",
        "is","it","of","on","or","the","to","what","when","where","why","with",
        "your","you"
    }
    return {
        t for t in re.findall(r"[a-z0-9]+", _norm(value))
        if len(t) >= 3 and t not in stop
    }


def resolve_topic_cluster_candidates(
    workspace_id: str,
    anchor_phrase: str,
    limit: int = 5,
    min_cluster_score: float = 0.70,
    min_purity_score: float = 0.75,
) -> List[Dict[str, Any]]:
    anchor = _norm(anchor_phrase)
    if not anchor:
        return []

    anchor_terms = _tokens(anchor)
    if not anchor_terms:
        return []

    cluster_matches = find_topic_clusters_for_text(workspace_id, anchor, limit=5)
    if not cluster_matches:
        return []

    cluster_data = load_workspace_topic_clusters(workspace_id)
    clusters = cluster_data.get("clusters") or {}
    if not isinstance(clusters, dict):
        return []

    candidates: List[Dict[str, Any]] = []

    for match in cluster_matches:
        cluster_score = float(match.get("score") or 0)
        purity_score = float(match.get("purity_score") or 0)

        if cluster_score < min_cluster_score or purity_score < min_purity_score:
            continue

        cluster_id = match.get("cluster_id")
        cluster = clusters.get(cluster_id) if cluster_id else None
        if not isinstance(cluster, dict):
            continue

        cluster_name = match.get("cluster_name") or cluster.get("name")
        urls = cluster.get("urls") or []
        if not isinstance(urls, list):
            continue

        for row in urls:
            if not isinstance(row, dict):
                continue

            title = str(row.get("title") or "")
            url = str(row.get("url") or "")
            surface = " ".join([title, url.replace("-", " ").replace("/", " ")])
            surface_terms = _tokens(surface)
            overlap = sorted(list(anchor_terms & surface_terms))

            if not overlap:
                continue

            matched_terms = row.get("matched_terms") or []
            matched_terms_set = set(str(x).lower() for x in matched_terms)

            anchor_cluster_overlap = sorted(list(anchor_terms & matched_terms_set))

            if len(anchor_cluster_overlap) < 2 and len(overlap) < 2:
                continue

            score = (
                0.45 * cluster_score
                + 0.35 * purity_score
                + 0.20 * min(1.0, len(overlap) / max(1, len(anchor_terms)))
            )

            normalized_score = round(min(1.0, score), 4)
            cluster_confidence_floor = 0.82
            auto_link_allowed = bool(
                normalized_score >= cluster_confidence_floor
                and cluster_score >= 0.70
                and purity_score >= 0.75
                and len(overlap) >= 2
            )
            suggest_only = not auto_link_allowed
            confidence_reason = (
                "cluster_confidence_pass"
                if auto_link_allowed
                else "cluster_confidence_suggest_only"
            )

            candidates.append({
                "phrase": anchor,
                "url": url,
                "title": title,
                "source_type": "live_domain",
                "resolver_reason": "topic_cluster_candidate_resolver",
                "target_score": round(score * 300, 4),
                "runtime_normalized_score": normalized_score,
                "resolver_confidence": normalized_score,
                "cluster_confidence_floor": cluster_confidence_floor,
                "auto_link_allowed": auto_link_allowed,
                "suggest_only": suggest_only,
                "confidence_reason": confidence_reason,
                "cluster_id": cluster_id,
                "cluster_name": cluster_name,
                "cluster_score": cluster_score,
                "cluster_purity_score": purity_score,
                "cluster_matched_terms": match.get("matched_terms") or [],
                "anchor_surface_overlap": overlap,
                "anchor_cluster_overlap": anchor_cluster_overlap,
                "cluster_runtime_trusted": True,
                "cluster_boost_applied": False,
                "cluster_guard_pass": True,
                "weak_match_suppressed": False,
            })

    candidates.sort(
        key=lambda x: (
            float(x.get("runtime_normalized_score") or 0),
            len(x.get("anchor_surface_overlap") or []),
        ),
        reverse=True,
    )

    seen = set()
    final: List[Dict[str, Any]] = []
    for c in candidates:
        url = c.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        final.append(c)
        if len(final) >= max(1, int(limit or 5)):
            break

    return final
