"""
Read-only Semantic Memory adapter for LinkCraftor Phase 3.2.
Existing retrieval recall scores are not certified confidence.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from backend.server.stores.semantic_memory_engine import (
    load_semantic_memory_store_v1,
    MEMORY_DIR,
)
from backend.server.stores.semantic_memory_layer import (
    retrieve_semantic_memory_v1,
)


def retrieve_phrase_memory_evidence(
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

    if isinstance(max_results, bool) or not isinstance(max_results, int):
        raise TypeError("max_results must be an integer.")

    if not 1 <= max_results <= 100:
        raise ValueError("max_results must be between 1 and 100.")

    path = MEMORY_DIR / f"semantic_memory_{workspace_id}.json"

    if not path.is_file():
        return {
            "status": "no_evidence",
            "workspace_id": workspace_id,
            "query": phrase.strip(),
            "retrieved_memory": [],
            "retrieval_method": "existing_lexical_recall_v1",
            "certified": False,
        }

    store = load_semantic_memory_store_v1(workspace_id)

    if not isinstance(store, dict):
        raise RuntimeError("Invalid Semantic Memory store.")

    if store.get("recovered_from_error"):
        raise RuntimeError("Semantic Memory recovery detected.")

    if store.get("workspace_id") != workspace_id:
        raise RuntimeError("Workspace mismatch.")

    memories = store.get("memories")

    if not isinstance(memories, dict):
        raise RuntimeError("Memory records must be a dictionary.")

    items = []

    for key, value in memories.items():
        if not isinstance(value, dict):
            raise RuntimeError("Unsupported memory record.")

        item = deepcopy(value)
        item.setdefault("memory_id", str(key))
        items.append(item)

    result = retrieve_semantic_memory_v1(
        query=phrase.strip(),
        memory_items=items,
        max_results=max_results,
    )

    if not isinstance(result, dict) or not isinstance(
        result.get("retrieved_memory"), list
    ):
        raise RuntimeError("Invalid memory retrieval response.")

    matches = deepcopy(result["retrieved_memory"])

    if any(not isinstance(match, dict) for match in matches):
        raise RuntimeError("Invalid retrieved memory.")

    return {
        "status": "evidence_found" if matches else "no_evidence",
        "workspace_id": workspace_id,
        "query": phrase.strip(),
        "retrieved_memory": matches,
        "retrieval_method": "existing_lexical_recall_v1",
        "certified": False,
    }


__all__ = ["retrieve_phrase_memory_evidence"]
