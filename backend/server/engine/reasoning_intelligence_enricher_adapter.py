"""
Phase 3.4 ? read-only cross-document reasoning evidence adapter.

Document relationships are advisory context, never proof of
phrase-level relevance or authorization to create a link.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from backend.server.stores.cross_document_reasoning import (
    _ws_safe,
    build_document_registry,
    build_semantic_relationship_scores,
)


def retrieve_phrase_reasoning_evidence(
    *,
    workspace_id: str,
    phrase: str,
    max_relationships: int = 20,
) -> dict[str, Any]:

    if (
        not isinstance(workspace_id, str)
        or not re.fullmatch(r"[A-Za-z0-9_-]{1,97}", workspace_id)
    ):
        raise ValueError("Invalid workspace_id")

    if not isinstance(phrase, str) or not phrase.strip():
        raise ValueError("Nonempty phrase required")

    if type(max_relationships) is not int or not (
        1 <= max_relationships <= 100
    ):
        raise ValueError("Invalid relationship limit")

    expected_ws = _ws_safe(workspace_id)
    normalized_phrase = " ".join(phrase.casefold().split())

    output = {
        "status": "no_evidence",
        "workspace_id": workspace_id,
        "normalized_workspace_id": expected_ws,
        "phrase": phrase.strip(),
        "source": "workspace_cross_document_reasoning",
        "matched_documents": [],
        "document_relationships": [],
        "reasoning_observations": [],
        "phrase_level_semantic_proof": False,
        "linking_decision_performed": False,
        "certified": False,
    }

    registry = build_document_registry(workspace_id)

    if (
        not isinstance(registry, dict)
        or registry.get("workspace_id") != expected_ws
        or registry.get("type") != "cross_document_registry"
        or not isinstance(registry.get("documents"), dict)
    ):
        raise RuntimeError("Invalid workspace registry contract")

    matched = []

    for document_id, document in registry["documents"].items():
        if not isinstance(document, dict):
            raise RuntimeError("Invalid document record")

        phrases = document.get("phrases", [])

        if not isinstance(phrases, list):
            raise RuntimeError("Invalid document phrase collection")

        exact_match = any(
            isinstance(value, str)
            and " ".join(value.casefold().split()) == normalized_phrase
            for value in phrases
        )

        if exact_match:
            matched.append({
                "document_id": str(document_id),
                "title": document.get("title"),
                "is_active": document.get("is_active"),
                "match_type": "exact_document_phrase",
            })

    output["matched_documents"] = deepcopy(matched)

    if not matched:
        return output

    scores = build_semantic_relationship_scores(workspace_id)

    if (
        not isinstance(scores, dict)
        or scores.get("workspace_id") != expected_ws
        or not isinstance(scores.get("relationships"), list)
    ):
        raise RuntimeError("Invalid cross-document reasoning contract")

    matched_ids = {item["document_id"] for item in matched}
    selected = []

    for relationship in scores["relationships"]:
        if not isinstance(relationship, dict):
            raise RuntimeError("Invalid reasoning relationship")

        left = str(relationship.get("left_document_id", ""))
        right = str(relationship.get("right_document_id", ""))

        if left not in matched_ids and right not in matched_ids:
            continue

        # Preserve the original document-level assessment.
        selected.append(deepcopy(relationship))

        if len(selected) >= max_relationships:
            break

    output["document_relationships"] = selected
    output["reasoning_observations"] = [
        {
            "observation": "phrase_present_in_workspace_documents",
            "document_count": len(matched),
            "interpretation": "document_occurrence_only",
            "certified": False,
        },
        {
            "observation": "associated_document_relationships",
            "relationship_count": len(selected),
            "interpretation": "document_level_context_only",
            "certified": False,
        },
    ]
    output["status"] = "document_context_found"

    return output


__all__ = ["retrieve_phrase_reasoning_evidence"]
