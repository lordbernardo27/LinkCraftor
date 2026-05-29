
from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize(text: str) -> str:
    return " ".join(_safe_text(text).lower().split())


def _pair_key(source: str, target: str, relationship_type: str) -> Tuple[str, str, str]:
    return (_normalize(source), _normalize(target), _normalize(relationship_type))


def _confidence_from_evidence(evidence: List[str] | None = None) -> float:
    evidence = evidence or []
    return round(min(1.0, 0.35 + (len(evidence) * 0.1)), 4)


def _make_response(
    layer: str,
    name: str,
    summary: str,
    actions: List[str],
) -> Dict[str, Any]:
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
        },
    }


def govern_ontology_aware_relationships_v1(
    relationships: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.11.1 Ontology-Aware Relationships.
    """

    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    seen = set()

    for rel in relationships or []:
        source = _safe_text(rel.get("source") if isinstance(rel, dict) else "")
        target = _safe_text(rel.get("target") if isinstance(rel, dict) else "")
        relationship_type = _safe_text(rel.get("relationship_type", "ontology_related") if isinstance(rel, dict) else "ontology_related")
        evidence = rel.get("evidence", []) if isinstance(rel, dict) else []

        key = _pair_key(source, target, relationship_type)

        if not source or not target or _normalize(source) == _normalize(target):
            rejected.append({"source": source, "target": target, "reason": "invalid_ontology_relationship"})
            continue

        if key in seen:
            rejected.append({"source": source, "target": target, "reason": "duplicate_ontology_relationship"})
            continue

        seen.add(key)
        accepted.append({
            "source": source,
            "target": target,
            "relationship_type": relationship_type,
            "confidence": _confidence_from_evidence(evidence),
            "ontology_role": "ontology_aware_relationship",
        })

    return _make_response(
        "1.11.1",
        "Ontology-Aware Relationships",
        "Governs ontology-aware relationships between entities, topics, and concepts.",
        [
            "ontology_aware_relationships",
            "ontology_relationship_validation",
            "duplicate_relationship_suppression",
            "relationship_confidence_support",
            "ontology_relationship_explainability",
            "ontology_relationship_audit",
        ],
    ) | {
        "accepted_relationships": accepted,
        "rejected_relationships": rejected,
    }


def align_topic_hierarchy_v1(
    topics: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.11.2 Topic Hierarchy Alignment.
    """

    hierarchy: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    seen = set()

    for item in topics or []:
        parent = _safe_text(item.get("parent") if isinstance(item, dict) else "")
        child = _safe_text(item.get("child") if isinstance(item, dict) else "")
        evidence = item.get("evidence", []) if isinstance(item, dict) else []

        key = _pair_key(parent, child, "parent_child")

        if not parent or not child or _normalize(parent) == _normalize(child):
            rejected.append({"parent": parent, "child": child, "reason": "invalid_topic_hierarchy"})
            continue

        if key in seen:
            rejected.append({"parent": parent, "child": child, "reason": "duplicate_topic_hierarchy"})
            continue

        seen.add(key)
        hierarchy.append({
            "parent": parent,
            "child": child,
            "relationship_type": "parent_child",
            "confidence": _confidence_from_evidence(evidence),
            "ontology_role": "topic_hierarchy_alignment",
        })

    return _make_response(
        "1.11.2",
        "Topic Hierarchy Alignment",
        "Aligns parent-child topic relationships for ontology-aware semantic structure.",
        [
            "topic_hierarchy_alignment",
            "parent_child_topic_validation",
            "hierarchy_confidence_support",
            "duplicate_hierarchy_suppression",
            "hierarchy_explainability",
            "hierarchy_audit",
        ],
    ) | {
        "aligned_hierarchy": hierarchy,
        "rejected_hierarchy": rejected,
    }


def support_concept_relationships_v1(
    concepts: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.11.3 Concept Relationship Support.
    """

    supported: List[Dict[str, Any]] = []

    for item in concepts or []:
        concept = _safe_text(item.get("concept") if isinstance(item, dict) else item)
        related = _safe_text(item.get("related") if isinstance(item, dict) else "")
        evidence = item.get("evidence", []) if isinstance(item, dict) else []

        if not concept:
            continue

        supported.append({
            "concept": concept,
            "related": related,
            "confidence": _confidence_from_evidence(evidence),
            "ontology_role": "concept_relationship_support",
        })

    return _make_response(
        "1.11.3",
        "Concept Relationship Support",
        "Supports ontology-aware relationships between concepts and related semantic contexts.",
        [
            "concept_relationship_support",
            "concept_similarity_support",
            "semantic_relationship_support",
            "concept_confidence_support",
            "concept_relationship_explainability",
            "concept_relationship_audit",
        ],
    ) | {
        "supported_concepts": supported,
    }


def map_semantic_relationships_v1(
    mappings: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.11.4 Semantic Relationship Mapping.
    """

    mapped: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    for item in mappings or []:
        source = _safe_text(item.get("source") if isinstance(item, dict) else "")
        target = _safe_text(item.get("target") if isinstance(item, dict) else "")
        relationship_type = _safe_text(item.get("relationship_type", "semantic_related") if isinstance(item, dict) else "semantic_related")
        evidence = item.get("evidence", []) if isinstance(item, dict) else []

        if not source or not target:
            rejected.append({"source": source, "target": target, "reason": "missing_mapping_endpoint"})
            continue

        mapped.append({
            "source": source,
            "target": target,
            "relationship_type": relationship_type,
            "confidence": _confidence_from_evidence(evidence),
            "ontology_role": "semantic_relationship_mapping",
        })

    return _make_response(
        "1.11.4",
        "Semantic Relationship Mapping",
        "Maps semantic relationships into ontology-aware support structures.",
        [
            "semantic_relationship_mapping",
            "relationship_type_mapping",
            "ontology_mapping_support",
            "mapping_confidence_support",
            "semantic_mapping_explainability",
            "semantic_mapping_audit",
        ],
    ) | {
        "mapped_relationships": mapped,
        "rejected_mappings": rejected,
    }


def assist_runtime_ontology_v1(
    runtime_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.11.5 Runtime Ontology Assistance.
    """

    assistance: List[Dict[str, Any]] = []

    for item in runtime_items or []:
        text = _safe_text(item.get("text") or item.get("phrase") or item.get("topic") if isinstance(item, dict) else item)
        ontology_hint = _safe_text(item.get("ontology_hint", "semantic_context") if isinstance(item, dict) else "semantic_context")

        if not text:
            continue

        assistance.append({
            "text": text,
            "ontology_hint": ontology_hint,
            "ontology_role": "runtime_ontology_assistance",
        })

    return _make_response(
        "1.11.5",
        "Runtime Ontology Assistance",
        "Provides runtime ontology assistance without changing runtime routing or target selection.",
        [
            "runtime_ontology_assistance",
            "runtime_semantic_structure_support",
            "ontology_hint_support",
            "runtime_ontology_governance",
            "runtime_ontology_explainability",
            "runtime_ontology_audit",
        ],
    ) | {
        "runtime_ontology_assistance": assistance,
    }


def support_semantic_relevance_v1(
    relevance_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.11.6 Semantic Relevance Support.
    """

    supported: List[Dict[str, Any]] = []

    for item in relevance_items or []:
        text = _safe_text(item.get("text") or item.get("phrase") or item.get("topic") if isinstance(item, dict) else item)
        score = item.get("score", item.get("confidence", 0.0)) if isinstance(item, dict) else 0.0

        if not text:
            continue

        supported.append({
            "text": text,
            "semantic_relevance": round(max(0.0, min(1.0, float(score or 0.0))), 4),
            "ontology_role": "semantic_relevance_support",
        })

    return _make_response(
        "1.11.6",
        "Semantic Relevance Support",
        "Supports ontology-aware semantic relevance interpretation for existing engines.",
        [
            "semantic_relevance_support",
            "ontology_relevance_support",
            "relevance_confidence_support",
            "semantic_support_governance",
            "semantic_relevance_explainability",
            "semantic_relevance_audit",
        ],
    ) | {
        "semantic_relevance_support": supported,
    }


def explain_ontology_alignment_layer_v1() -> Dict[str, Any]:
    return {
        "layer": "1.11",
        "name": "Ontology Alignment Layer",
        "status": "active",
        "scope": "ontology_alignment_governance",
        "sub_layers": [
            "1.11.1 Ontology-Aware Relationships",
            "1.11.2 Topic Hierarchy Alignment",
            "1.11.3 Concept Relationship Support",
            "1.11.4 Semantic Relationship Mapping",
            "1.11.5 Runtime Ontology Assistance",
            "1.11.6 Semantic Relevance Support",
        ],
        "safety_rules": {
            "governance_only": True,
            "runtime_support_only": True,
            "does_not_modify_uploaded_article": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_target_selector": True,
            "does_not_replace_existing_scoring": True,
            "does_not_force_link_decisions": True,
        },
    }
