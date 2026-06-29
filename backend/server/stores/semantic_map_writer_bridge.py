from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def build_semantic_map_concept_entry_v1(record: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()

    return {
        "concept_id": record.get("concept_id"),
        "canonical": record.get("canonical"),
        "display": record.get("display"),
        "semantic_type": record.get("semantic_type"),
        "confidence": record.get("confidence", 0.0),
        "confidence_factors": record.get("confidence_factors", {}),
        "aliases": record.get("aliases", []),
        "evidence": record.get("evidence", []),
        "sources": [
            {
                "workspace_id": record.get("workspace_id"),
                "source_kind": record.get("source_kind"),
                "source_id": record.get("source_id"),
                "metadata": record.get("metadata", {}),
                "observed_at": now,
            }
        ],
        "registry_version": record.get("registry_version", "v1"),
        "updated_at": now,
    }


def merge_semantic_map_concept_entry_v1(
    existing: Dict[str, Any] | None,
    incoming: Dict[str, Any],
) -> Dict[str, Any]:
    if not existing:
        return incoming

    merged = dict(existing)

    merged["canonical"] = incoming.get("canonical") or existing.get("canonical")
    merged["display"] = incoming.get("display") or existing.get("display")
    merged["semantic_type"] = incoming.get("semantic_type") or existing.get("semantic_type")

    merged["confidence"] = max(
        float(existing.get("confidence", 0.0) or 0.0),
        float(incoming.get("confidence", 0.0) or 0.0),
    )

    merged["confidence_factors"] = {
        **existing.get("confidence_factors", {}),
        **incoming.get("confidence_factors", {}),
    }

    merged["aliases"] = sorted(
        set(existing.get("aliases", []) or []) |
        set(incoming.get("aliases", []) or [])
    )

    merged["evidence"] = list(existing.get("evidence", []) or []) + list(incoming.get("evidence", []) or [])
    merged["sources"] = list(existing.get("sources", []) or []) + list(incoming.get("sources", []) or [])

    merged["registry_version"] = incoming.get("registry_version", existing.get("registry_version", "v1"))
    merged["updated_at"] = incoming.get("updated_at")

    return merged


def write_concepts_to_semantic_map_v2_v1(
    semantic_map: Dict[str, Any] | None,
    records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    semantic_map = semantic_map or {}

    semantic_map.setdefault("version", "semantic_map_v2")
    semantic_map.setdefault("concepts", {})
    semantic_map.setdefault("updated_at", datetime.now(timezone.utc).isoformat())

    for record in records:
        concept_id = record.get("concept_id")
        if not concept_id:
            continue

        incoming = build_semantic_map_concept_entry_v1(record)
        existing = semantic_map["concepts"].get(concept_id)

        semantic_map["concepts"][concept_id] = merge_semantic_map_concept_entry_v1(
            existing,
            incoming,
        )

    semantic_map["updated_at"] = datetime.now(timezone.utc).isoformat()
    return semantic_map
