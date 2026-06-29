from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def build_semantic_graph_node_from_concept_v1(
    concept_id: str,
    concept_entry: Dict[str, Any],
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()

    return {
        "node_id": concept_id,
        "node_type": "semantic_concept",
        "canonical": concept_entry.get("canonical"),
        "display": concept_entry.get("display"),
        "semantic_type": concept_entry.get("semantic_type"),
        "confidence": concept_entry.get("confidence", 0.0),
        "confidence_factors": concept_entry.get("confidence_factors", {}),
        "aliases": concept_entry.get("aliases", []),
        "source_count": len(concept_entry.get("sources", []) or []),
        "evidence_count": len(concept_entry.get("evidence", []) or []),
        "created_from": "semantic_map_v2",
        "created_at": now,
    }


def infer_semantic_graph_edge_candidates_v1(
    nodes: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    edges: List[Dict[str, Any]] = []
    seen = set()

    for left in nodes:
        for right in nodes:
            if left.get("node_id") == right.get("node_id"):
                continue

            pair_key = tuple(sorted([left.get("node_id"), right.get("node_id")]))
            if pair_key in seen:
                continue
            seen.add(pair_key)

            left_tokens = set(str(left.get("canonical") or "").split())
            right_tokens = set(str(right.get("canonical") or "").split())

            overlap = sorted(left_tokens & right_tokens)
            if not overlap:
                continue

            edge_id = f"edge::{pair_key[0]}::{pair_key[1]}"

            edges.append(
                {
                    "edge_id": edge_id,
                    "source_node_id": pair_key[0],
                    "target_node_id": pair_key[1],
                    "edge_type": "lexical_semantic_overlap",
                    "weight": round(min(1.0, len(overlap) / max(len(left_tokens | right_tokens), 1)), 4),
                    "evidence": {
                        "shared_tokens": overlap,
                        "method": "canonical_token_overlap_v1",
                    },
                    "created_from": "semantic_graph_feed_bridge_v1",
                }
            )

    return edges


def build_semantic_graph_feed_from_map_v1(
    semantic_map: Dict[str, Any],
) -> Dict[str, Any]:
    concepts = semantic_map.get("concepts", {}) or {}

    nodes = [
        build_semantic_graph_node_from_concept_v1(concept_id, concept_entry)
        for concept_id, concept_entry in concepts.items()
    ]

    edges = infer_semantic_graph_edge_candidates_v1(nodes)

    return {
        "version": "semantic_graph_feed_v1",
        "source_version": semantic_map.get("version", "semantic_map_v2"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
        },
    }
