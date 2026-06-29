from __future__ import annotations

import inspect
from typing import Any, Dict, List

from backend.server.stores.semantic_concept_normalizer import (
    build_normalized_concept_registry_v1,
)


def _call_build_registry_safely_v1(
    concepts: List[str],
    *,
    workspace_id: str,
    source_kind: str,
    source_id: str,
    metadata: Dict[str, Any],
) -> Any:
    sig = inspect.signature(build_normalized_concept_registry_v1)
    params = sig.parameters

    kwargs: Dict[str, Any] = {}

    if "workspace_id" in params:
        kwargs["workspace_id"] = workspace_id
    if "source_kind" in params:
        kwargs["source_kind"] = source_kind
    if "source_id" in params:
        kwargs["source_id"] = source_id
    if "metadata" in params:
        kwargs["metadata"] = metadata

    return build_normalized_concept_registry_v1(concepts, **kwargs)


def _coerce_registry_item_v1(item: Any, raw_text: str) -> Dict[str, Any]:
    if isinstance(item, dict):
        return item

    data: Dict[str, Any] = {}

    for key in (
        "concept_id",
        "canonical",
        "display",
        "semantic_type",
        "concept_type",
        "confidence",
        "confidence_factors",
        "evidence",
        "aliases",
    ):
        if hasattr(item, key):
            data[key] = getattr(item, key)

    if not data:
        data["canonical"] = str(raw_text or "").strip().lower()

    return data


def _extract_first_registry_item_v1(registry: Any) -> Any:
    if isinstance(registry, dict):
        if "concepts" in registry and registry["concepts"]:
            return registry["concepts"][0]
        if "registry" in registry and registry["registry"]:
            reg = registry["registry"]
            if isinstance(reg, dict):
                return next(iter(reg.values()))
            if isinstance(reg, list):
                return reg[0]
        if registry:
            return next(iter(registry.values()))

    if isinstance(registry, list) and registry:
        return registry[0]

    return {}


def _normalize_one_concept_v1(
    raw_text: str,
    *,
    workspace_id: str,
    source_kind: str,
    source_id: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    registry = _call_build_registry_safely_v1(
        [raw_text],
        workspace_id=workspace_id,
        source_kind=source_kind,
        source_id=source_id,
        metadata=metadata,
    )

    item = _extract_first_registry_item_v1(registry)
    return _coerce_registry_item_v1(item, raw_text)


def build_semantic_concept_registry_record_v1(
    raw_text: str,
    *,
    workspace_id: str = "default",
    source_kind: str = "manual",
    source_id: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    metadata = metadata or {}

    normalized = _normalize_one_concept_v1(
        raw_text,
        workspace_id=workspace_id,
        source_kind=source_kind,
        source_id=source_id,
        metadata=metadata,
    )

    canonical = (
        normalized.get("canonical")
        or normalized.get("normalized")
        or normalized.get("canonical_text")
        or str(raw_text or "").strip().lower()
    )

    concept_id = (
        normalized.get("concept_id")
        or normalized.get("id")
        or f"concept::{canonical.replace(' ', '_')}"
    )

    return {
        "concept_id": concept_id,
        "canonical": canonical,
        "display": normalized.get("display") or normalized.get("label") or str(raw_text or "").strip(),
        "semantic_type": normalized.get("semantic_type") or normalized.get("concept_type") or "unknown",
        "confidence": normalized.get("confidence", 0.0),
        "confidence_factors": normalized.get("confidence_factors", {}),
        "evidence": normalized.get("evidence", []),
        "aliases": normalized.get("aliases", []),
        "workspace_id": workspace_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "metadata": metadata,
        "registry_version": "v1",
    }


def build_semantic_concept_registry_batch_v1(
    concepts: List[str],
    *,
    workspace_id: str = "default",
    source_kind: str = "manual",
    source_id: str = "",
    metadata: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    for concept in concepts:
        if not str(concept or "").strip():
            continue

        records.append(
            build_semantic_concept_registry_record_v1(
                concept,
                workspace_id=workspace_id,
                source_kind=source_kind,
                source_id=source_id,
                metadata=metadata,
            )
        )

    return records
