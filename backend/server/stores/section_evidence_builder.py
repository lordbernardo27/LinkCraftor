from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:12]}"


def build_section_evidence_v1(
    semantic_context_model: Dict[str, Any],
    extraction_model: Dict[str, Any],
    neighborhood_model: Dict[str, Any],
    intent_model: Dict[str, Any],
) -> Dict[str, Any]:
    article = semantic_context_model.get("article", {})
    section_contexts = semantic_context_model.get("section_contexts", [])

    mentions_by_section = defaultdict(list)
    objects_by_id = {
        obj["semantic_object_id"]: obj
        for obj in extraction_model.get("semantic_objects", [])
    }

    for mention in extraction_model.get("mentions", []):
        section_id = mention.get("location", {}).get("section_id")
        if section_id:
            mentions_by_section[section_id].append(mention)

    neighborhoods_by_section = defaultdict(list)

    for neighborhood in neighborhood_model.get("neighborhoods", []):
        seen_sections = set()

        for evidence in neighborhood.get("evidence", []):
            unit_key = evidence.get("unit_key", "")
            if unit_key.startswith("section:"):
                seen_sections.add(unit_key.split(":", 1)[1])

        for section_id in seen_sections:
            neighborhoods_by_section[section_id].append(neighborhood)

    intents_by_section = {
        item["section_id"]: item
        for item in intent_model.get("section_intents", [])
    }

    section_evidence_records = []

    for section in section_contexts:
        section_id = section["section_id"]
        section_mentions = mentions_by_section.get(section_id, [])

        semantic_object_ids = sorted({
            mention["semantic_object_id"]
            for mention in section_mentions
            if mention["semantic_object_id"] in objects_by_id
        })

        semantic_objects = [
            objects_by_id[obj_id]
            for obj_id in semantic_object_ids
        ]

        section_neighborhoods = neighborhoods_by_section.get(section_id, [])
        section_intent = intents_by_section.get(section_id)

        object_category_counts = Counter(obj.get("category") for obj in semantic_objects)
        relationship_family_counts = Counter(
            item.get("relationship_family")
            for item in section_neighborhoods
            if item.get("relationship_family")
        )
        relationship_type_counts = Counter(
            item.get("relationship_type")
            for item in section_neighborhoods
            if item.get("relationship_type")
        )

        confidence_values = []

        for obj in semantic_objects:
            if isinstance(obj.get("extraction_confidence"), (int, float)):
                confidence_values.append(obj["extraction_confidence"])

        for neighborhood in section_neighborhoods:
            if isinstance(neighborhood.get("relationship_confidence"), (int, float)):
                confidence_values.append(neighborhood["relationship_confidence"])

        if section_intent and isinstance(section_intent.get("intent_confidence"), (int, float)):
            confidence_values.append(section_intent["intent_confidence"])

        evidence_confidence = (
            round(sum(confidence_values) / len(confidence_values), 2)
            if confidence_values
            else 0.0
        )

        section_evidence_records.append({
            "section_evidence_id": _stable_id("section_evidence", article.get("article_id"), section_id),
            "article_id": article.get("article_id"),
            "section_id": section_id,
            "section_index": section.get("section_index"),
            "section_position": section_intent.get("section_position") if section_intent else None,
            "section_title": section.get("section_title"),
            "heading_level": section.get("heading_level"),
            "evidence_scope": "section",
            "article_reference": {
                "article_intent_id": intent_model.get("article_intent", {}).get("article_intent_id"),
                "article_id": intent_model.get("article_intent", {}).get("article_id"),
                "article_intent": intent_model.get("article_intent", {}).get("article_intent"),
                "article_intent_family": intent_model.get("article_intent", {}).get("article_intent_family"),
                "article_purpose": intent_model.get("article_intent", {}).get("article_purpose"),
            },
            "section_intent": section_intent,
            "semantic_objects": semantic_objects,
            "mentions": section_mentions,
            "phrase_neighborhoods": section_neighborhoods,
            "object_category_counts": dict(object_category_counts),
            "relationship_family_counts": dict(relationship_family_counts),
            "relationship_type_counts": dict(relationship_type_counts),
            "structural_context": {
                "breadcrumb": section.get("context", {}).get("breadcrumb", ""),
                "heading_ancestry": section.get("context", {}).get("heading_ancestry", []),
                "parent_section_title": section.get("context", {}).get("parent_section_title"),
                "child_section_titles": section.get("context", {}).get("child_section_titles", []),
                "entry_block_id": section.get("context", {}).get("entry_block_id"),
                "exit_block_id": section.get("context", {}).get("exit_block_id"),
                "block_ids": section.get("context", {}).get("block_ids", []),
                "section_text": section.get("context", {}).get("section_text", ""),
            },
            "provenance": {
                "semantic_context_phase": semantic_context_model.get("phase"),
                "semantic_context_patch": semantic_context_model.get("patch"),
                "extraction_phase": extraction_model.get("phase"),
                "extraction_patch": extraction_model.get("patch"),
                "neighborhood_phase": neighborhood_model.get("phase"),
                "neighborhood_patch": neighborhood_model.get("patch"),
                "intent_phase": intent_model.get("phase"),
                "intent_patch": intent_model.get("patch"),
            },
            "evidence_lineage": {
                "semantic_context_section_id": section_id,
                "semantic_object_ids": semantic_object_ids,
                "mention_ids": [mention.get("mention_id") for mention in section_mentions],
                "relationship_ids": [
                    neighborhood.get("neighborhood_id")
                    for neighborhood in section_neighborhoods
                ],
                "section_intent_id": section_intent.get("section_intent_id") if section_intent else None,
                "article_intent_id": intent_model.get("article_intent", {}).get("article_intent_id"),
            },
            "evidence_metrics": {
                "semantic_object_count": len(semantic_objects),
                "mention_count": len(section_mentions),
                "phrase_neighborhood_count": len(section_neighborhoods),
                "object_category_count": len(object_category_counts),
                "relationship_family_count": len(relationship_family_counts),
                "relationship_type_count": len(relationship_type_counts),
                "evidence_confidence": evidence_confidence,
            },
        })

    article_evidence_summary = {
        "article_id": article.get("article_id"),
        "intent_scope": "article",
        "article_intent": intent_model.get("article_intent", {}),
        "section_evidence_count": len(section_evidence_records),
        "total_semantic_objects": sum(
            record["evidence_metrics"]["semantic_object_count"]
            for record in section_evidence_records
        ),
        "total_mentions": sum(
            record["evidence_metrics"]["mention_count"]
            for record in section_evidence_records
        ),
        "total_phrase_neighborhoods": sum(
            record["evidence_metrics"]["phrase_neighborhood_count"]
            for record in section_evidence_records
        ),
    }

    return {
        "schema_version": "section_evidence_builder_v1",
        "phase": "4.6.6",
        "patch": "4.6.6A",
        "created_at": _now_iso(),
        "source_models": {
            "semantic_context": {
                "schema_version": semantic_context_model.get("schema_version"),
                "phase": semantic_context_model.get("phase"),
                "patch": semantic_context_model.get("patch"),
            },
            "entity_concept_extraction": {
                "schema_version": extraction_model.get("schema_version"),
                "phase": extraction_model.get("phase"),
                "patch": extraction_model.get("patch"),
            },
            "phrase_neighborhoods": {
                "schema_version": neighborhood_model.get("schema_version"),
                "phase": neighborhood_model.get("phase"),
                "patch": neighborhood_model.get("patch"),
            },
            "topic_intent": {
                "schema_version": intent_model.get("schema_version"),
                "phase": intent_model.get("phase"),
                "patch": intent_model.get("patch"),
            },
        },
        "article": article,
        "domain_label": extraction_model.get("domain_label"),
        "article_evidence_summary": article_evidence_summary,
        "section_evidence": section_evidence_records,
        "metadata": {
            "section_evidence_count": len(section_evidence_records),
            "article_intent_present": bool(intent_model.get("article_intent")),
            "total_semantic_objects": article_evidence_summary["total_semantic_objects"],
            "total_mentions": article_evidence_summary["total_mentions"],
            "total_phrase_neighborhoods": article_evidence_summary["total_phrase_neighborhoods"],
        },
        "boundary_rule": (
            "Section Evidence Builder consolidates evidence per section only. "
            "It does not resolve links, create blue highlights, create yellow highlights, score target pages, "
            "write memory, perform reasoning, or build final semantic relationship graphs."
        ),
    }


def save_section_evidence_v1(
    semantic_context_model: Dict[str, Any],
    extraction_model: Dict[str, Any],
    neighborhood_model: Dict[str, Any],
    intent_model: Dict[str, Any],
    output_path: str | Path,
) -> Dict[str, Any]:
    model = build_section_evidence_v1(
        semantic_context_model,
        extraction_model,
        neighborhood_model,
        intent_model,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(model, indent=2, ensure_ascii=False), encoding="utf-8")
    return model


def explain_section_evidence_builder_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.6",
        "patch": "4.6.6A",
        "name": "Section Evidence Builder",
        "purpose": "Consolidate all semantic evidence per section for downstream graph, export, memory, and resolver systems.",
        "input": [
            "Semantic Context Model from Phase 4.6.2A",
            "Entity & Concept Extraction Model from Phase 4.6.3C",
            "Phrase Neighborhood Model from Phase 4.6.4B",
            "Topic Intent Model from Phase 4.6.5B",
        ],
        "output": "Section Evidence Model",
        "does": [
            "consolidates evidence per section",
            "attaches lightweight article reference",
            "adds evidence lineage",
            "attaches section intent",
            "attaches semantic objects",
            "attaches mentions",
            "attaches phrase neighborhoods",
            "attaches relationship families",
            "attaches relationship types",
            "attaches structural context",
            "stores provenance from all upstream semantic phases",
            "computes section evidence metrics",
            "works across multiple niches",
        ],
        "does_not": [
            "perform internal link resolving",
            "perform semantic link resolving",
            "create blue highlights",
            "create yellow highlights",
            "score target pages",
            "build final relationship graphs",
            "write memory",
            "perform reasoning",
            "generate explanations",
        ],
    }
