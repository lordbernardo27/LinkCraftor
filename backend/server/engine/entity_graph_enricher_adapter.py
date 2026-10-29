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



def retrieve_phrase_graph_paths(
    *,
    workspace_id: str,
    phrase: str,
    max_hops: int = 2,
    max_paths: int = 25,
) -> dict[str, Any]:
    """Retrieve bounded paths from persisted graph edges only."""
    if not isinstance(workspace_id, str) or not re.fullmatch(
        r"[A-Za-z0-9_-]+", workspace_id
    ):
        raise ValueError("Valid workspace_id required.")

    if not isinstance(phrase, str) or not phrase.strip():
        raise ValueError("Nonempty phrase required.")

    if type(max_hops) is not int or not 1 <= max_hops <= 2:
        raise ValueError("max_hops must be 1 or 2.")

    if type(max_paths) is not int or not 1 <= max_paths <= 100:
        raise ValueError("max_paths must be between 1 and 100.")

    output = {
        "status": "no_evidence",
        "workspace_id": workspace_id,
        "query": phrase.strip(),
        "source": "uploaded_entity_graph",
        "graph_paths": [],
        "path_count": 0,
        "max_hops": max_hops,
        "certified": False,
        "retrieval_method": "bounded_persisted_edge_traversal_v1",
    }

    path = _upload_entity_graph_path(workspace_id)
    if not path.is_file():
        output["storage_status"] = "missing"
        return output

    try:
        graph = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise RuntimeError("Graph storage unreadable") from exc

    if not isinstance(graph, dict):
        raise RuntimeError("Invalid graph root.")

    if graph.get("workspace_id") != workspace_id:
        raise RuntimeError("Graph workspace identity mismatch.")

    nodes = graph.get("nodes")
    edges = graph.get("edges")

    if not isinstance(nodes, dict) or not isinstance(edges, list):
        raise RuntimeError("Invalid persisted graph schema.")

    normalized = " ".join(phrase.casefold().split())

    starts = []
    for key, node in nodes.items():
        if not isinstance(node, dict):
            raise RuntimeError("Invalid graph node.")
        label = node.get("label")
        if isinstance(label, str) and (
            " ".join(label.casefold().split()) == normalized
        ):
            starts.append(str(key))

    adjacency = {}
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            raise RuntimeError("Invalid graph edge.")

        src = edge.get("src")
        dst = edge.get("dst")

        if src is None or dst is None:
            raise RuntimeError("Graph edge missing endpoints.")

        src, dst = str(src), str(dst)

        if src not in nodes or dst not in nodes:
            continue

        # Edges are traversed only in their recorded direction.
        adjacency.setdefault(src, []).append(
            (dst, index, edge)
        )

    paths = []

    def walk(node_id, visited, steps):
        if len(paths) >= max_paths:
            return

        if steps:
            paths.append({
                "node_ids": list(visited),
                "nodes": [
                    {
                        "node_id": key,
                        "original_record": deepcopy(nodes[key]),
                    }
                    for key in visited
                ],
                "edges": deepcopy(steps),
                "hop_count": len(steps),
                "certified": False,
            })

        if len(steps) >= max_hops:
            return

        for target, index, edge in adjacency.get(node_id, []):
            if target in visited:
                continue

            if len(paths) >= max_paths:
                return

            step = {
                "edge_index": index,
                "source_node_id": node_id,
                "target_node_id": target,
                "relationship_type": edge.get("type"),
                "relationship_weight": edge.get("w"),
                "original_record": deepcopy(edge),
                "certified": False,
            }

            walk(
                target,
                visited + [target],
                steps + [step],
            )

    for start in starts:
        if len(paths) >= max_paths:
            break
        walk(start, [start], [])

    output["graph_paths"] = paths
    output["path_count"] = len(paths)
    output["storage_status"] = "loaded"

    if paths:
        output["status"] = "path_evidence_found"
    elif starts:
        output["status"] = "node_evidence_found"

    return output


__all__ = ["retrieve_phrase_graph_relationships", "retrieve_phrase_graph_paths"]
