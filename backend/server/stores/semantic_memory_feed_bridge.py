from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def build_semantic_memory_feed_v1(
    graph_feed: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Converts the graph feed into a stable memory-ingestion payload.
    This bridge performs no learning or persistence—it only prepares
    normalized observations for downstream memory engines.
    """

    now = datetime.now(timezone.utc).isoformat()

    observations = []

    for node in graph_feed.get("nodes", []):
        observations.append(
            {
                "memory_id": node.get("node_id"),
                "memory_type": "semantic_concept",
                "canonical": node.get("canonical"),
                "semantic_type": node.get("semantic_type"),
                "confidence": node.get("confidence", 0.0),
                "confidence_factors": node.get("confidence_factors", {}),
                "aliases": node.get("aliases", []),
                "source_count": node.get("source_count", 0),
                "evidence_count": node.get("evidence_count", 0),
                "observed_at": now,
            }
        )

    return {
        "version": "semantic_memory_feed_v1",
        "source_version": graph_feed.get("version", "semantic_graph_feed_v1"),
        "created_at": now,
        "observations": observations,
        "stats": {
            "observation_count": len(observations),
        },
    }
