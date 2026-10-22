"""
LinkCraftor Phase 3.3 ? read-only workspace concept evidence.

Concept and alias matches are not certified graph relationships.
This adapter does not infer edges or perform target resolution.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any
import re

from backend.server.engine.workspace_concept_store import (
    concept_store_path,
    load_workspace_concepts,
    normalize_concept_text,
)


def retrieve_workspace_concept_evidence(
    *,
    workspace_id: str,
    phrase: str,
    max_results: int = 25,
) -> dict[str, Any]:
    if not isinstance(workspace_id, str) or not re.fullmatch(
        r"[A-Za-z0-9_-]+", workspace_id
    ):
        raise ValueError("Valid workspace_id required.")

    if not isinstance(phrase, str) or not phrase.strip():
        raise ValueError("Nonempty phrase required.")

    if type(max_results) is not int:
        raise TypeError("max_results must be an integer.")

    if not 1 <= max_results <= 100:
        raise ValueError("max_results must be between 1 and 100.")

    query = normalize_concept_text(phrase)

    if not query:
        raise ValueError("Normalized phrase is empty.")

    path = concept_store_path(workspace_id)

    result = {
        "status": "no_evidence",
        "workspace_id": workspace_id,
        "query": phrase.strip(),
        "source": "workspace_concept_store",
        "concept_matches": [],
        "relationship_edges": [],
        "relationship_retrieval_status": "not_implemented",
        "match_method": "exact_normalized_concept_or_alias",
        "certified": False,
    }

    if not path.is_file():
        result["storage_status"] = "missing"
        return result

    store = load_workspace_concepts(workspace_id)

    # Existing loader returns {} on malformed/unreadable storage.
    # It must not be confused with a valid empty concept store.
    if not isinstance(store, dict) or not store:
        raise RuntimeError("Concept store unreadable or invalid.")

    if store.get("workspace_id") != workspace_id:
        raise RuntimeError("Concept store workspace mismatch.")

    if store.get("type") != "workspace_concepts":
        raise RuntimeError("Unexpected concept store type.")

    concepts = store.get("concepts")

    if not isinstance(concepts, dict):
        raise RuntimeError("Invalid concept collection.")

    matches = []

    for key, record in concepts.items():
        if not isinstance(record, dict):
            raise RuntimeError("Invalid concept record.")

        concept = record.get("concept", key)
        aliases = record.get("aliases", [])

        if not isinstance(concept, str):
            raise RuntimeError("Invalid concept text.")

        if not isinstance(aliases, list) or any(
            not isinstance(alias, str) for alias in aliases
        ):
            raise RuntimeError("Invalid concept aliases.")

        is_concept = normalize_concept_text(concept) == query
        is_alias = any(
            normalize_concept_text(alias) == query
            for alias in aliases
        )

        if not is_concept and not is_alias:
            continue

        matches.append({
            "concept_key": str(key),
            "concept": concept,
            "match_type": (
                "exact_concept" if is_concept else "exact_alias"
            ),
            "original_record": deepcopy(record),
            "source": record.get(
                "source", "workspace_concept_store"
            ),
            "certified": False,
        })

        if len(matches) >= max_results:
            break

    result["concept_matches"] = matches
    result["storage_status"] = "loaded"
    result["status"] = (
        "concept_evidence_found" if matches else "no_evidence"
    )

    return result


__all__ = ["retrieve_workspace_concept_evidence"]
