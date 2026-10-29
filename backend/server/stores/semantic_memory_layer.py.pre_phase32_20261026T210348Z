
from __future__ import annotations

from typing import Any, Dict, List


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize(text: str) -> str:
    return " ".join(_safe_text(text).lower().split())


def _make_response(layer: str, name: str, summary: str, actions: List[str]) -> Dict[str, Any]:
    return {
        "layer": layer,
        "name": name,
        "status": "active",
        "summary": summary,
        "actions": actions,
        "safety": {
            "governance_only": True,
            "runtime_support_only": True,
            "does_not_modify_uploaded_article": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_target_selector": True,
            "does_not_replace_existing_scoring": True,
            "does_not_force_link_decisions": True,
            "does_not_force_highlights": True,
            "workspace_safe": True,
        },
    }


def register_semantic_memory_items_v1(memory_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    registry = []
    rejected = []
    seen = set()

    for item in memory_items or []:
        text = _safe_text(item.get("text") or item.get("phrase") or item.get("entity") if isinstance(item, dict) else item)
        memory_id = _normalize(item.get("memory_id") or text if isinstance(item, dict) else text)

        if not text or not memory_id:
            rejected.append({"reason": "missing_memory_text_or_id"})
            continue

        if memory_id in seen:
            rejected.append({"memory_id": memory_id, "text": text, "reason": "duplicate_memory_item"})
            continue

        seen.add(memory_id)
        registry.append({
            "memory_id": memory_id.replace(" ", "_"),
            "text": text,
            "metadata": item.get("metadata", {}) if isinstance(item, dict) else {},
            "memory_role": "semantic_memory_registry",
        })

    return _make_response(
        "1.12.1",
        "Semantic Memory Registry",
        "Registers governed semantic memory items and metadata.",
        [
            "semantic_memory_registry",
            "memory_identifier_storage",
            "memory_metadata_storage",
            "memory_governance_rules",
            "memory_registry_audit",
        ],
    ) | {
        "registered_memory": registry,
        "rejected_memory": rejected,
    }


def persist_semantic_memory_v1(
    workspace_id: str,
    memory_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    registered = register_semantic_memory_items_v1(memory_items)

    persisted = [
        {
            **item,
            "workspace_id": _safe_text(workspace_id),
            "persistence_role": "semantic_memory_persistence",
            "retention_policy": "workspace_scoped",
        }
        for item in registered["registered_memory"]
    ]

    return _make_response(
        "1.12.2",
        "Semantic Memory Persistence",
        "Creates workspace-safe semantic memory persistence records.",
        [
            "memory_persistence_contract",
            "workspace_safe_memory_records",
            "memory_retention_metadata",
            "persistence_governance",
            "persistence_audit",
        ],
    ) | {
        "persisted_memory": persisted,
        "rejected_memory": registered["rejected_memory"],
    }


def retrieve_semantic_memory_v1(
    query: str,
    memory_items: List[Dict[str, Any]],
    max_results: int = 25,
) -> Dict[str, Any]:
    q = _normalize(query)
    results = []
    seen = set()

    for item in memory_items or []:
        text = _safe_text(item.get("text") or item.get("phrase") or item.get("entity") if isinstance(item, dict) else item)
        key = _normalize(text)

        if not text or key in seen:
            continue

        seen.add(key)

        score = 0.0
        if q and q in key:
            score += 0.7
        elif q and any(part in key for part in q.split()):
            score += 0.35

        if score > 0:
            results.append({
                "text": text,
                "memory_id": item.get("memory_id", key.replace(" ", "_")) if isinstance(item, dict) else key.replace(" ", "_"),
                "recall_score": round(score, 4),
                "memory_role": "semantic_memory_retrieval",
            })

    results.sort(key=lambda x: x["recall_score"], reverse=True)

    return _make_response(
        "1.12.3",
        "Semantic Memory Retrieval",
        "Retrieves semantic memory using relevance-based recall and duplicate suppression.",
        [
            "semantic_memory_retrieval",
            "relevance_based_recall",
            "duplicate_recall_suppression",
            "retrieval_governance",
            "memory_retrieval_audit",
        ],
    ) | {
        "query": query,
        "retrieved_memory": results[:max_results],
    }


def consolidate_semantic_memory_v1(memory_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    consolidated = []
    merged = []
    seen = {}

    for item in memory_items or []:
        text = _safe_text(item.get("text") or item.get("phrase") or item.get("entity") if isinstance(item, dict) else item)
        key = _normalize(text)

        if not text:
            continue

        if key in seen:
            merged.append({
                "text": text,
                "reason": "duplicate_memory_merged",
                "merged_into": seen[key],
            })
            continue

        memory_id = item.get("memory_id", key.replace(" ", "_")) if isinstance(item, dict) else key.replace(" ", "_")
        seen[key] = memory_id

        consolidated.append({
            "memory_id": memory_id,
            "text": text,
            "memory_role": "semantic_memory_consolidation",
            "stale": bool(item.get("stale", False)) if isinstance(item, dict) else False,
        })

    return _make_response(
        "1.12.4",
        "Semantic Memory Consolidation",
        "Consolidates semantic memory by merging duplicates and marking stale memory safely.",
        [
            "memory_consolidation",
            "duplicate_memory_merging",
            "stale_memory_handling",
            "consolidation_governance",
            "memory_consolidation_audit",
        ],
    ) | {
        "consolidated_memory": consolidated,
        "merged_memory": merged,
    }


def support_runtime_semantic_memory_v1(
    runtime_context: Dict[str, Any],
    memory_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    query = _safe_text(runtime_context.get("query") or runtime_context.get("phrase") or runtime_context.get("topic") if isinstance(runtime_context, dict) else "")
    retrieved = retrieve_semantic_memory_v1(query, memory_items)

    return _make_response(
        "1.12.5",
        "Runtime Semantic Memory Support",
        "Provides runtime semantic memory support and recall reporting without changing runtime routing.",
        [
            "runtime_memory_support",
            "runtime_recall_reporting",
            "memory_assisted_semantic_support",
            "runtime_memory_audit",
        ],
    ) | {
        "runtime_query": query,
        "runtime_memory_support": retrieved["retrieved_memory"],
        "runtime_memory_count": len(retrieved["retrieved_memory"]),
    }


def explain_semantic_memory_layer_v1() -> Dict[str, Any]:
    return {
        "layer": "1.12",
        "name": "Semantic Memory Layer",
        "status": "active",
        "scope": "semantic_memory_governance",
        "sub_layers": [
            "1.12.1 Semantic Memory Registry",
            "1.12.2 Semantic Memory Persistence",
            "1.12.3 Semantic Memory Retrieval",
            "1.12.4 Semantic Memory Consolidation",
            "1.12.5 Runtime Semantic Memory Support",
        ],
        "safety_rules": {
            "governance_only": True,
            "runtime_support_only": True,
            "does_not_modify_uploaded_article": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_target_selector": True,
            "does_not_replace_existing_scoring": True,
            "does_not_force_link_decisions": True,
            "does_not_force_highlights": True,
            "workspace_safe": True,
        },
    }
