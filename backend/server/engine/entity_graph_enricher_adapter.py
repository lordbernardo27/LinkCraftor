"""
Phase 3.3: read-only retrieval of persisted entity graph edges.

Co-occurrence is observational evidence, not semantic certification
or an approved internal-link relationship.
"""

from __future__ import annotations

from copy import deepcopy
import json
import re
from typing import Any

from backend.server.stores.cross_document_reasoning import (
    _upload_entity_graph_path,
)


def retrieve_phrase_graph_relationships(
    *,
    workspace_id: str,
    phrase: str,
    max_edges: int = 25,
) -> dict[str, Any]:
    if not isinstance(workspace_id, str) or not re.fullmatch(
        r"[A-Za-z0-9_-]+", workspace_id
    ):
        raise ValueError("Valid workspace_id required.")

    if not isinstance(phrase, str) or not phrase.strip():
        raise ValueError("Nonempty phrase required.")

    if type(max_edges) is not int or not 1 <= max_edges <= 100:
        raise ValueError("max_edges must be an integer from 1 to 100.")

    normalized = " ".join(phrase.casefold().split())
    path = _upload_entity_graph_path(workspace_id)

    output = {
        "status": "no_evidence",
        "workspace_id": workspace_id,
        "query": phrase.strip(),
        "source": "uploaded_entity_graph",
        "matched_nodes": [],
        "relationship_edges": [],
        "match_method": "exact_normalized_node_label",
        "relationship_retrieval_status": "completed",
        "certified": False,
    }

    if not path.is_file():
        output["storage_status"] = "missing"
        return output

    try:
        graph = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, UnicodeError) as exc:
        raise RuntimeError("Graph storage unreadable") from exc

    if not isinstance(graph, dict):
        raise RuntimeError("Invalid graph root.")

    if graph.get("workspace_id") != workspace_id:
        raise RuntimeError("Graph workspace identity mismatch.")

    nodes = graph.get("nodes")
    edges = graph.get("edges")

    if not isinstance(nodes, dict) or not isinstance(edges, list):
        raise RuntimeError("Invalid persisted graph schema.")

    matched_ids = set()
    matched_nodes = []

    for node_id, record in nodes.items():
        if not isinstance(record, dict):
            raise RuntimeError("Invalid graph node.")

        label = record.get("label")

        if isinstance(label, str) and (
            " ".join(label.casefold().split()) == normalized
        ):
            key = str(node_id)
            matched_ids.add(key)
            matched_nodes.append({
                "node_id": key,
                "original_record": deepcopy(record),
            })

    result_edges = []

    if matched_ids:
        for index, edge in enumerate(edges):
            if not isinstance(edge, dict):
                raise RuntimeError("Invalid graph edge.")

            src = edge.get("src")
            dst = edge.get("dst")

            if src is None or dst is None:
                raise RuntimeError("Graph edge missing endpoints.")

            if str(src) not in matched_ids and str(dst) not in matched_ids:
                continue

            if str(src) not in nodes or str(dst) not in nodes:
                # Skip dangling edges rather than fabricating nodes.
                continue

            result_edges.append({
                "edge_index": index,
                "source_node_id": str(src),
                "target_node_id": str(dst),
                "relationship_type": edge.get("type"),
                "relationship_weight": edge.get("w"),
                "source_node": deepcopy(nodes[str(src)]),
                "target_node": deepcopy(nodes[str(dst)]),
                "original_record": deepcopy(edge),
                "certified": False,
            })

            if len(result_edges) >= max_edges:
                break

    output["matched_nodes"] = matched_nodes
    output["relationship_edges"] = result_edges
    output["storage_status"] = "loaded"

    if result_edges:
        output["status"] = "relationship_evidence_found"
    elif matched_nodes:
        output["status"] = "node_evidence_found"

    return output


__all__ = ["retrieve_phrase_graph_relationships"]
