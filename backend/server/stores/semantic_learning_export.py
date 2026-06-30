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



def _signature(parts: List[Any]) -> str:
    normalized = json.dumps(parts, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]


def _nodes_by_type(graph_model: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    grouped = defaultdict(list)

    for node in graph_model.get("graph", {}).get("nodes", []):
        grouped[node.get("node_type")].append(node)

    return grouped


def _edges_by_type(graph_model: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    grouped = defaultdict(list)

    for edge in graph_model.get("graph", {}).get("edges", []):
        grouped[edge.get("edge_type")].append(edge)

    return grouped


def build_semantic_learning_export_v1(
    graph_model: Dict[str, Any],
) -> Dict[str, Any]:
    article = graph_model.get("article", {})
    article_id = article.get("article_id")

    nodes_by_type = _nodes_by_type(graph_model)
    edges_by_type = _edges_by_type(graph_model)

    semantic_objects = []
    for node in nodes_by_type.get("semantic_object", []):
        props = node.get("properties", {})
        semantic_objects.append({
            "semantic_object_id": props.get("semantic_object_id"),
            "canonical_text": props.get("canonical_text"),
            "display_text": props.get("display_text"),
            "object_type": props.get("object_type"),
            "category": props.get("category"),
            "domain_label": props.get("domain_label"),
            "aliases": props.get("aliases", []),
            "extraction_confidence": props.get("extraction_confidence"),
            "source_node_id": node.get("node_id"),
        })

    learned_relationships = []
    for edge in edges_by_type.get("relates_to", []):
        props = edge.get("properties", {})
        learned_relationships.append({
            "relationship_id": _stable_id(
                "learned_relationship",
                article_id,
                edge.get("source_id"),
                edge.get("target_id"),
                props.get("relationship_type"),
            ),
            "source_node_id": edge.get("source_id"),
            "target_node_id": edge.get("target_id"),
            "relationship_type": props.get("relationship_type"),
            "relationship_family": props.get("relationship_family"),
            "relationship_confidence": props.get("relationship_confidence"),
            "relationship_strength": props.get("neighborhood_strength"),
            "neighborhood_id": props.get("neighborhood_id"),
            "provenance": {
                "edge_id": edge.get("edge_id"),
                "edge_type": edge.get("edge_type"),
            },
        })

    section_intent_patterns = []
    for node in nodes_by_type.get("section_intent", []):
        props = node.get("properties", {})
        section_intent_patterns.append({
            "section_intent_id": props.get("section_intent_id"),
            "intent_scope": props.get("intent_scope"),
            "intent_family": props.get("intent_family"),
            "topic_intent": props.get("topic_intent"),
            "reader_goal": props.get("reader_goal"),
            "section_role": props.get("section_role"),
            "information_type": props.get("information_type"),
            "intent_confidence": props.get("intent_confidence"),
            "decision_evidence": props.get("decision_evidence", {}),
            "source_node_id": node.get("node_id"),
        })

    article_intent_summary = {}
    article_intent_nodes = nodes_by_type.get("article_intent", [])
    if article_intent_nodes:
        article_intent_summary = article_intent_nodes[0].get("properties", {})

    evidence_summaries = []
    for node in nodes_by_type.get("section_evidence", []):
        props = node.get("properties", {})
        evidence_metrics = props.get("evidence_metrics", {})
        evidence_summaries.append({
            "section_evidence_id": props.get("section_evidence_id"),
            "evidence_scope": props.get("evidence_scope"),
            "article_reference": props.get("article_reference", {}),
            "evidence_metrics": evidence_metrics,
            "evidence_lineage": props.get("evidence_lineage", {}),
            "provenance": props.get("provenance", {}),
            "source_node_id": node.get("node_id"),
        })

    concept_frequency = Counter()
    category_frequency = Counter()
    confidence_values = []

    for obj in semantic_objects:
        if obj.get("canonical_text"):
            concept_frequency[obj["canonical_text"]] += 1
        if obj.get("category"):
            category_frequency[obj["category"]] += 1
        if isinstance(obj.get("extraction_confidence"), (int, float)):
            confidence_values.append(obj["extraction_confidence"])

    relationship_family_frequency = Counter()
    relationship_type_frequency = Counter()
    relationship_confidence_values = []

    for rel in learned_relationships:
        if rel.get("relationship_family"):
            relationship_family_frequency[rel["relationship_family"]] += 1
        if rel.get("relationship_type"):
            relationship_type_frequency[rel["relationship_type"]] += 1
        if isinstance(rel.get("relationship_confidence"), (int, float)):
            relationship_confidence_values.append(rel["relationship_confidence"])

    intent_family_frequency = Counter()
    topic_intent_frequency = Counter()
    intent_confidence_values = []

    for pattern in section_intent_patterns:
        if pattern.get("intent_family"):
            intent_family_frequency[pattern["intent_family"]] += 1
        if pattern.get("topic_intent"):
            topic_intent_frequency[pattern["topic_intent"]] += 1
        if isinstance(pattern.get("intent_confidence"), (int, float)):
            intent_confidence_values.append(pattern["intent_confidence"])

    average_extraction_confidence = (
        round(sum(confidence_values) / len(confidence_values), 2)
        if confidence_values else 0.0
    )

    average_relationship_confidence = (
        round(sum(relationship_confidence_values) / len(relationship_confidence_values), 2)
        if relationship_confidence_values else 0.0
    )

    average_intent_confidence = (
        round(sum(intent_confidence_values) / len(intent_confidence_values), 2)
        if intent_confidence_values else 0.0
    )

    graph_stats = graph_model.get("metadata", {})

    learning_pack_id = _stable_id(
        "semantic_learning_pack",
        article_id,
        graph_model.get("schema_version"),
        graph_model.get("phase"),
        graph_model.get("patch"),
    )

    concept_signature = _signature([
        {
            "canonical_text": item.get("canonical_text"),
            "category": item.get("category"),
            "aliases": sorted(item.get("aliases", [])),
        }
        for item in semantic_objects
    ])

    relationship_signature = _signature([
        {
            "relationship_type": item.get("relationship_type"),
            "relationship_family": item.get("relationship_family"),
            "source_node_id": item.get("source_node_id"),
            "target_node_id": item.get("target_node_id"),
        }
        for item in learned_relationships
    ])

    intent_signature = _signature([
        {
            "intent_family": item.get("intent_family"),
            "topic_intent": item.get("topic_intent"),
            "section_role": item.get("section_role"),
            "information_type": item.get("information_type"),
        }
        for item in section_intent_patterns
    ])

    article_signature = _signature([
        article.get("article_id"),
        article.get("title"),
        graph_model.get("domain_label"),
        article_intent_summary.get("article_intent"),
        article_intent_summary.get("article_intent_family"),
    ])

    overall_signature = _signature([
        concept_signature,
        relationship_signature,
        intent_signature,
        article_signature,
    ])

    concept_diversity = len(category_frequency)
    relationship_diversity = len(relationship_type_frequency)
    intent_diversity = len(topic_intent_frequency)

    source_node_count = graph_stats.get("node_count", 0) or 0
    source_edge_count = graph_stats.get("edge_count", 0) or 0
    graph_density = round(source_edge_count / source_node_count, 2) if source_node_count else 0.0

    semantic_richness_score = round(
        min(
            1.0,
            (
                (len(semantic_objects) * 0.03)
                + (len(learned_relationships) * 0.02)
                + (concept_diversity * 0.04)
                + (relationship_diversity * 0.04)
                + (intent_diversity * 0.04)
                + (average_extraction_confidence * 0.15)
                + (average_relationship_confidence * 0.15)
                + (average_intent_confidence * 0.15)
            ),
        ),
        2,
    )

    learning_fingerprint = {
        "concept_signature": concept_signature,
        "relationship_signature": relationship_signature,
        "intent_signature": intent_signature,
        "article_signature": article_signature,
        "overall_signature": overall_signature,
    }

    learning_statistics = {
        "concept_diversity": concept_diversity,
        "relationship_diversity": relationship_diversity,
        "intent_diversity": intent_diversity,
        "graph_density": graph_density,
        "semantic_richness_score": semantic_richness_score,
        "source_node_count": source_node_count,
        "source_edge_count": source_edge_count,
    }

    return {
        "schema_version": "semantic_learning_export_v1",
        "phase": "4.6.8",
        "patch": "4.6.8A",
        "patch": "4.6.8A",
        "created_at": _now_iso(),
        "learning_pack_id": learning_pack_id,
        "learning_fingerprint": learning_fingerprint,
        "learning_statistics": learning_statistics,
        "article": article,
        "domain_label": graph_model.get("domain_label"),
        "source_graph": {
            "schema_version": graph_model.get("schema_version"),
            "phase": graph_model.get("phase"),
            "patch": graph_model.get("patch"),
            "graph_lineage": graph_model.get("graph_lineage", {}),
            "graph_metadata": graph_stats,
        },
        "article_intent_summary": article_intent_summary,
        "canonical_concepts": sorted(
            semantic_objects,
            key=lambda item: (
                item.get("category") or "",
                item.get("canonical_text") or "",
            ),
        ),
        "learned_relationships": sorted(
            learned_relationships,
            key=lambda item: (
                item.get("relationship_family") or "",
                item.get("relationship_type") or "",
                item.get("relationship_confidence") or 0,
            ),
            reverse=True,
        ),
        "intent_patterns": sorted(
            section_intent_patterns,
            key=lambda item: (
                item.get("intent_family") or "",
                item.get("topic_intent") or "",
            ),
        ),
        "section_evidence_summaries": evidence_summaries,
        "learning_signals": {
            "concept_frequency": dict(concept_frequency),
            "category_frequency": dict(category_frequency),
            "relationship_family_frequency": dict(relationship_family_frequency),
            "relationship_type_frequency": dict(relationship_type_frequency),
            "intent_family_frequency": dict(intent_family_frequency),
            "topic_intent_frequency": dict(topic_intent_frequency),
            "average_extraction_confidence": average_extraction_confidence,
            "average_relationship_confidence": average_relationship_confidence,
            "average_intent_confidence": average_intent_confidence,
        },
        "export_contract": {
            "consumer": "Semantic Workspace Learner",
            "contract_type": "compiled_semantic_learning_pack",
            "graph_internal_details_hidden": True,
            "resolver_safe": True,
            "memory_write_performed": False,
            "resolver_decision_performed": False,
        },
        "metadata": {
            "canonical_concept_count": len(semantic_objects),
            "learned_relationship_count": len(learned_relationships),
            "intent_pattern_count": len(section_intent_patterns),
            "section_evidence_summary_count": len(evidence_summaries),
            "source_node_count": source_node_count,
            "source_edge_count": source_edge_count,
        },
        "boundary_rule": (
            "Semantic Learning Export compiles the semantic graph into a learner-friendly Learning Pack only. "
            "It does not resolve links, create blue highlights, create yellow highlights, score target pages, "
            "write memory, perform reasoning, or generate explanations."
        ),
    }


def save_semantic_learning_export_v1(
    graph_model: Dict[str, Any],
    output_path: str | Path,
) -> Dict[str, Any]:
    learning_pack = build_semantic_learning_export_v1(graph_model)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(learning_pack, indent=2, ensure_ascii=False), encoding="utf-8")
    return learning_pack


def explain_semantic_learning_export_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.8",
        "patch": "4.6.8A",
        "name": "Semantic Learning Export",
        "purpose": "Compile the semantic relationship graph into a stable learner-friendly Learning Pack.",
        "input": "Semantic Relationship Graph from Phase 4.6.7A",
        "output": "Semantic Learning Pack",
        "does": [
            "compiles canonical concepts",
            "compiles learned relationships",
            "compiles intent patterns",
            "compiles section evidence summaries",
            "preserves graph lineage",
            "preserves provenance",
            "preserves confidence distributions",
            "creates stable learning fingerprints",
            "computes semantic learning statistics",
            "preserves relationship families and relationship types",
            "creates learner-friendly export contract",
            "hides graph internals from downstream consumers",
            "works across multiple niches",
        ],
        "does_not": [
            "perform internal link resolving",
            "perform semantic link resolving",
            "create blue highlights",
            "create yellow highlights",
            "score target pages",
            "write memory",
            "perform reasoning",
            "generate explanations",
        ],
    }
