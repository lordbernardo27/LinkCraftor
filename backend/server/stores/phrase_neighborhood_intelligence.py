from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:12]}"


def _relationship_family_v1(relationship_type: str) -> str:
    if relationship_type in {
        "peer_symptoms",
        "related_conditions",
        "peer_concepts",
        "peer_category_association",
    }:
        return "peer"

    if relationship_type in {
        "condition_context",
        "monitoring_context",
        "measurement_context",
        "symptom_context",
        "contextual_association",
    }:
        return "contextual"

    if relationship_type in {
        "measurement_condition_association",
        "symptom_condition_association",
    }:
        return "clinical"

    return "general"


def _classify_relationship_v1(
    left_category: str,
    right_category: str,
    unit_type_counts: Dict[str, int],
) -> Dict[str, Any]:
    categories = {left_category, right_category}

    sentence_hits = unit_type_counts.get("sentence", 0)
    paragraph_hits = unit_type_counts.get("paragraph", 0)
    block_hits = unit_type_counts.get("block", 0)
    section_hits = unit_type_counts.get("section", 0)

    relationship_type = "contextual_association"
    confidence = 0.50

    if left_category == right_category:
        if left_category == "symptom_or_sign":
            relationship_type = "peer_symptoms"
            confidence = 0.78
        elif left_category == "medical_condition":
            relationship_type = "related_conditions"
            confidence = 0.76
        elif left_category.endswith("_concept"):
            relationship_type = "peer_concepts"
            confidence = 0.72
        else:
            relationship_type = "peer_category_association"
            confidence = 0.66

    elif "medical_monitoring" in categories:
        relationship_type = "monitoring_context"
        confidence = 0.76

    elif "life_stage_or_condition" in categories and "medical_condition" in categories:
        relationship_type = "condition_context"
        confidence = 0.78

    elif "life_stage_or_condition" in categories and "medical_measurement" in categories:
        relationship_type = "measurement_context"
        confidence = 0.74

    elif "medical_measurement" in categories and "medical_condition" in categories:
        relationship_type = "measurement_condition_association"
        confidence = 0.76

    elif "symptom_or_sign" in categories and "medical_condition" in categories:
        relationship_type = "symptom_condition_association"
        confidence = 0.74

    elif "symptom_or_sign" in categories and "life_stage_or_condition" in categories:
        relationship_type = "symptom_context"
        confidence = 0.70

    if sentence_hits:
        confidence += 0.08

    if paragraph_hits:
        confidence += 0.04

    if block_hits:
        confidence += 0.03

    if section_hits:
        confidence += 0.02

    relationship_family = _relationship_family_v1(relationship_type)

    return {
        "relationship_type": relationship_type,
        "relationship_family": relationship_family,
        "relationship_confidence": round(min(confidence, 0.95), 2),
        "classification_basis": {
            "left_category": left_category,
            "right_category": right_category,
            "unit_type_counts": unit_type_counts,
        },
    }


def build_phrase_neighborhoods_v1(
    extraction_model: Dict[str, Any],
) -> Dict[str, Any]:
    article = extraction_model.get("article", {})
    semantic_objects = extraction_model.get("semantic_objects", [])
    mentions = extraction_model.get("mentions", [])

    object_by_id = {
        obj["semantic_object_id"]: obj
        for obj in semantic_objects
    }

    units: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for mention in mentions:
        loc = mention.get("location", {})
        section_id = loc.get("section_id")
        block_id = loc.get("block_id")
        paragraph_id = loc.get("paragraph_id")
        sentence_id = loc.get("sentence_id")
        breadcrumb = mention.get("evidence", {}).get("breadcrumb", "")

        if section_id:
            units[f"section:{section_id}"].append(mention)

        if block_id:
            units[f"block:{block_id}"].append(mention)

        if paragraph_id:
            units[f"paragraph:{paragraph_id}"].append(mention)

        if sentence_id:
            units[f"sentence:{sentence_id}"].append(mention)

        if breadcrumb:
            units[f"breadcrumb:{breadcrumb}"].append(mention)

    pair_counts: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for unit_key, unit_mentions in units.items():
        unique_object_ids = sorted({
            mention["semantic_object_id"]
            for mention in unit_mentions
            if mention["semantic_object_id"] in object_by_id
        })

        if len(unique_object_ids) < 2:
            continue

        for left_id, right_id in combinations(unique_object_ids, 2):
            pair_key = tuple(sorted([left_id, right_id]))

            if pair_key not in pair_counts:
                pair_counts[pair_key] = {
                    "left_object_id": pair_key[0],
                    "right_object_id": pair_key[1],
                    "cooccurrence_count": 0,
                    "unit_keys": [],
                    "unit_type_counts": defaultdict(int),
                    "evidence": [],
                }

            pair_counts[pair_key]["cooccurrence_count"] += 1
            pair_counts[pair_key]["unit_keys"].append(unit_key)

            unit_type = unit_key.split(":", 1)[0]
            pair_counts[pair_key]["unit_type_counts"][unit_type] += 1

            pair_counts[pair_key]["evidence"].append({
                "unit_key": unit_key,
                "unit_type": unit_type,
                "objects": [
                    object_by_id[pair_key[0]]["canonical_text"],
                    object_by_id[pair_key[1]]["canonical_text"],
                ],
            })

    neighborhoods = []

    relationship_type_counts: Dict[str, int] = {}
    relationship_family_counts: Dict[str, int] = {}

    for pair_key, payload in pair_counts.items():
        left = object_by_id[payload["left_object_id"]]
        right = object_by_id[payload["right_object_id"]]

        unit_type_counts = dict(payload["unit_type_counts"])

        strength = (
            unit_type_counts.get("sentence", 0) * 4
            + unit_type_counts.get("paragraph", 0) * 3
            + unit_type_counts.get("block", 0) * 2
            + unit_type_counts.get("section", 0)
            + unit_type_counts.get("breadcrumb", 0)
        )

        relationship = _classify_relationship_v1(
            left.get("category", "unknown"),
            right.get("category", "unknown"),
            unit_type_counts,
        )

        relationship_type_counts[relationship["relationship_type"]] = (
            relationship_type_counts.get(relationship["relationship_type"], 0) + 1
        )
        relationship_family_counts[relationship["relationship_family"]] = (
            relationship_family_counts.get(relationship["relationship_family"], 0) + 1
        )

        neighborhoods.append({
            "neighborhood_id": _stable_id(
                "phrase_neighborhood",
                article.get("article_id"),
                payload["left_object_id"],
                payload["right_object_id"],
            ),
            "article_id": article.get("article_id"),
            "left_object_id": payload["left_object_id"],
            "right_object_id": payload["right_object_id"],
            "left_text": left["canonical_text"],
            "right_text": right["canonical_text"],
            "left_category": left.get("category"),
            "right_category": right.get("category"),
            "relationship_type": relationship["relationship_type"],
            "relationship_family": relationship["relationship_family"],
            "relationship_confidence": relationship["relationship_confidence"],
            "classification_basis": relationship["classification_basis"],
            "cooccurrence_count": payload["cooccurrence_count"],
            "neighborhood_strength": strength,
            "unit_type_counts": unit_type_counts,
            "unit_keys": sorted(set(payload["unit_keys"])),
            "evidence": payload["evidence"],
        })

    neighborhoods = sorted(
        neighborhoods,
        key=lambda item: (
            item["relationship_confidence"],
            item["neighborhood_strength"],
            item["cooccurrence_count"],
            item["left_text"],
            item["right_text"],
        ),
        reverse=True,
    )

    object_neighbors: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for neighborhood in neighborhoods:
        object_neighbors[neighborhood["left_object_id"]].append({
            "neighbor_object_id": neighborhood["right_object_id"],
            "neighbor_text": neighborhood["right_text"],
            "neighborhood_id": neighborhood["neighborhood_id"],
            "relationship_type": neighborhood["relationship_type"],
            "relationship_family": neighborhood["relationship_family"],
            "relationship_confidence": neighborhood["relationship_confidence"],
            "neighborhood_strength": neighborhood["neighborhood_strength"],
            "cooccurrence_count": neighborhood["cooccurrence_count"],
        })

        object_neighbors[neighborhood["right_object_id"]].append({
            "neighbor_object_id": neighborhood["left_object_id"],
            "neighbor_text": neighborhood["left_text"],
            "neighborhood_id": neighborhood["neighborhood_id"],
            "relationship_type": neighborhood["relationship_type"],
            "relationship_family": neighborhood["relationship_family"],
            "relationship_confidence": neighborhood["relationship_confidence"],
            "neighborhood_strength": neighborhood["neighborhood_strength"],
            "cooccurrence_count": neighborhood["cooccurrence_count"],
        })

    object_neighborhoods = []

    for object_id, neighbors in object_neighbors.items():
        obj = object_by_id[object_id]

        object_neighborhoods.append({
            "semantic_object_id": object_id,
            "canonical_text": obj["canonical_text"],
            "category": obj.get("category"),
            "neighbor_count": len(neighbors),
            "neighbors": sorted(
                neighbors,
                key=lambda item: (
                    item["relationship_confidence"],
                    item["neighborhood_strength"],
                    item["cooccurrence_count"],
                    item["neighbor_text"],
                ),
                reverse=True,
            ),
        })

    object_neighborhoods = sorted(
        object_neighborhoods,
        key=lambda item: (item["neighbor_count"], item["canonical_text"]),
        reverse=True,
    )

    return {
        "schema_version": "phrase_neighborhood_intelligence_v1",
        "phase": "4.6.4",
        "patch": "4.6.4B",
        "created_at": _now_iso(),
        "source_schema_version": extraction_model.get("schema_version"),
        "source_phase": extraction_model.get("phase"),
        "source_patch": extraction_model.get("patch"),
        "article": article,
        "domain_label": extraction_model.get("domain_label"),
        "neighborhoods": neighborhoods,
        "object_neighborhoods": object_neighborhoods,
        "metadata": {
            "semantic_object_count": len(semantic_objects),
            "mention_count": len(mentions),
            "neighborhood_count": len(neighborhoods),
            "object_neighborhood_count": len(object_neighborhoods),
            "relationship_type_counts": relationship_type_counts,
            "relationship_family_counts": relationship_family_counts,
        },
        "boundary_rule": (
            "Phrase Neighborhood Intelligence builds typed co-occurrence neighborhoods between extracted semantic objects only. "
            "It does not resolve links, create blue highlights, create yellow highlights, score targets, "
            "write memory, reason, infer topic intent, or build final semantic relationship graphs."
        ),
    }


def save_phrase_neighborhoods_v1(
    extraction_model: Dict[str, Any],
    output_path: str | Path,
) -> Dict[str, Any]:
    model = build_phrase_neighborhoods_v1(extraction_model)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(model, indent=2, ensure_ascii=False), encoding="utf-8")
    return model


def explain_phrase_neighborhood_intelligence_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.4",
        "patch": "4.6.4B",
        "name": "Phrase Neighborhood Intelligence",
        "purpose": "Build typed co-occurrence neighborhoods between clean semantic objects extracted in Phase 4.6.3.",
        "input": "Entity & Concept Extraction Model from Phase 4.6.3C",
        "output": "Phrase Neighborhood Intelligence Model",
        "does": [
            "builds semantic object neighborhoods",
            "detects sentence-level co-occurrence",
            "detects paragraph-level co-occurrence",
            "detects block-level co-occurrence",
            "detects section-level co-occurrence",
            "detects breadcrumb-level co-occurrence",
            "calculates structural neighborhood strength",
            "classifies lightweight neighborhood relationship type",
            "assigns neighborhood relationship confidence",
            "assigns relationship family",
            "stores classification basis",
            "stores neighborhood evidence",
            "builds per-object neighbor lists",
        ],
        "does_not": [
            "perform internal link resolving",
            "perform semantic link resolving",
            "create blue highlights",
            "create yellow highlights",
            "score target pages",
            "infer topic intent",
            "build final relationship graphs",
            "write memory",
            "perform reasoning",
            "generate explanations",
        ],
    }
