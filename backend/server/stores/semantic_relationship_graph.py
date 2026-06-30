from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:12]}"




_NODE_LAYER_MAP = {
    "article": "document",
    "section": "structure",
    "article_intent": "intent",
    "section_intent": "intent",
    "semantic_object": "semantic",
    "mention": "mention",
    "phrase_neighborhood": "relationship",
    "section_evidence": "evidence",
}


_NODE_PARTITION_MAP = {
    "article": "document",
    "section": "structure",
    "article_intent": "intent",
    "section_intent": "intent",
    "semantic_object": "semantic",
    "mention": "mention",
    "phrase_neighborhood": "relationship",
    "section_evidence": "evidence",
}


def _node_layer(node_type: str) -> str:
    return _NODE_LAYER_MAP.get(node_type, "general")


def _node_partition(node_type: str) -> str:
    return _NODE_PARTITION_MAP.get(node_type, "general")


def _add_node(
    nodes: Dict[str, Dict[str, Any]],
    node_id: str,
    node_type: str,
    label: str,
    properties: Dict[str, Any],
) -> None:
    if node_id not in nodes:
        nodes[node_id] = {
            "node_id": node_id,
            "node_type": node_type,
            "node_layer": _node_layer(node_type),
            "partition": _node_partition(node_type),
            "label": label,
            "properties": properties,
        }


def _add_edge(
    edges: List[Dict[str, Any]],
    seen_edges: Set[Tuple[str, str, str]],
    source_id: str,
    target_id: str,
    edge_type: str,
    properties: Dict[str, Any] | None = None,
) -> None:
    key = (source_id, target_id, edge_type)
    if key in seen_edges:
        return

    seen_edges.add(key)

    edges.append({
        "edge_id": _stable_id("edge", source_id, target_id, edge_type),
        "source_id": source_id,
        "target_id": target_id,
        "edge_type": edge_type,
        "properties": properties or {},
    })


def build_semantic_relationship_graph_v1(
    evidence_model: Dict[str, Any],
) -> Dict[str, Any]:
    article = evidence_model.get("article", {})
    article_id = article.get("article_id")
    article_title = article.get("title") or article_id

    nodes: Dict[str, Dict[str, Any]] = {}
    edges: List[Dict[str, Any]] = []
    seen_edges: Set[Tuple[str, str, str]] = set()

    article_node_id = _stable_id("article_node", article_id)

    _add_node(
        nodes,
        article_node_id,
        "article",
        article_title,
        {
            "article_id": article_id,
            "title": article_title,
            "source_url": article.get("source_url"),
            "domain_label": evidence_model.get("domain_label"),
        },
    )

    article_intent = evidence_model.get("article_evidence_summary", {}).get("article_intent", {})
    article_intent_id = article_intent.get("article_intent_id")

    if article_intent_id:
        article_intent_node_id = _stable_id("article_intent_node", article_intent_id)

        _add_node(
            nodes,
            article_intent_node_id,
            "article_intent",
            article_intent.get("article_intent") or "article_intent",
            article_intent,
        )

        _add_edge(
            edges,
            seen_edges,
            article_node_id,
            article_intent_node_id,
            "has_article_intent",
            {
                "confidence": article_intent.get("article_intent_confidence"),
                "intent_family": article_intent.get("article_intent_family"),
            },
        )

    for section_record in evidence_model.get("section_evidence", []):
        section_id = section_record["section_id"]
        section_node_id = _stable_id("section_node", article_id, section_id)

        _add_node(
            nodes,
            section_node_id,
            "section",
            section_record.get("section_title") or section_id,
            {
                "section_id": section_id,
                "section_index": section_record.get("section_index"),
                "section_position": section_record.get("section_position"),
                "section_title": section_record.get("section_title"),
                "heading_level": section_record.get("heading_level"),
                "breadcrumb": section_record.get("structural_context", {}).get("breadcrumb"),
            },
        )

        _add_edge(
            edges,
            seen_edges,
            article_node_id,
            section_node_id,
            "contains_section",
            {
                "section_index": section_record.get("section_index"),
                "section_position": section_record.get("section_position"),
            },
        )

        evidence_node_id = _stable_id("section_evidence_node", section_record["section_evidence_id"])

        _add_node(
            nodes,
            evidence_node_id,
            "section_evidence",
            section_record.get("section_title") or section_record["section_evidence_id"],
            {
                "section_evidence_id": section_record["section_evidence_id"],
                "evidence_scope": section_record.get("evidence_scope"),
                "evidence_metrics": section_record.get("evidence_metrics", {}),
                "article_reference": section_record.get("article_reference", {}),
                "provenance": section_record.get("provenance", {}),
                "evidence_lineage": section_record.get("evidence_lineage", {}),
            },
        )

        _add_edge(
            edges,
            seen_edges,
            section_node_id,
            evidence_node_id,
            "has_section_evidence",
            {
                "evidence_confidence": section_record.get("evidence_metrics", {}).get("evidence_confidence"),
            },
        )

        section_intent = section_record.get("section_intent") or {}
        section_intent_id = section_intent.get("section_intent_id")

        if section_intent_id:
            section_intent_node_id = _stable_id("section_intent_node", section_intent_id)

            _add_node(
                nodes,
                section_intent_node_id,
                "section_intent",
                section_intent.get("topic_intent") or section_intent_id,
                {
                    "section_intent_id": section_intent_id,
                    "intent_scope": section_intent.get("intent_scope"),
                    "intent_family": section_intent.get("intent_family"),
                    "topic_intent": section_intent.get("topic_intent"),
                    "reader_goal": section_intent.get("reader_goal"),
                    "section_role": section_intent.get("section_role"),
                    "information_type": section_intent.get("information_type"),
                    "intent_confidence": section_intent.get("intent_confidence"),
                    "decision_evidence": section_intent.get("decision_evidence", {}),
                },
            )

            _add_edge(
                edges,
                seen_edges,
                section_node_id,
                section_intent_node_id,
                "has_section_intent",
                {
                    "intent_family": section_intent.get("intent_family"),
                    "topic_intent": section_intent.get("topic_intent"),
                    "confidence": section_intent.get("intent_confidence"),
                },
            )

            _add_edge(
                edges,
                seen_edges,
                section_intent_node_id,
                evidence_node_id,
                "supported_by_evidence",
                {
                    "section_evidence_id": section_record["section_evidence_id"],
                },
            )

        for semantic_object in section_record.get("semantic_objects", []):
            object_id = semantic_object["semantic_object_id"]
            object_node_id = _stable_id("semantic_object_node", object_id)

            _add_node(
                nodes,
                object_node_id,
                "semantic_object",
                semantic_object.get("canonical_text") or object_id,
                {
                    "semantic_object_id": object_id,
                    "canonical_text": semantic_object.get("canonical_text"),
                    "display_text": semantic_object.get("display_text"),
                    "object_type": semantic_object.get("object_type"),
                    "category": semantic_object.get("category"),
                    "domain_label": semantic_object.get("domain_label"),
                    "aliases": semantic_object.get("aliases", []),
                    "extraction_confidence": semantic_object.get("extraction_confidence"),
                    "normalization_source": semantic_object.get("normalization_source"),
                },
            )

            _add_edge(
                edges,
                seen_edges,
                section_node_id,
                object_node_id,
                "mentions_object",
                {
                    "category": semantic_object.get("category"),
                    "confidence": semantic_object.get("extraction_confidence"),
                },
            )

            _add_edge(
                edges,
                seen_edges,
                object_node_id,
                evidence_node_id,
                "evidenced_in_section",
                {
                    "section_id": section_id,
                },
            )

        for mention in section_record.get("mentions", []):
            mention_id = mention["mention_id"]
            mention_node_id = _stable_id("mention_node", mention_id)
            object_node_id = _stable_id("semantic_object_node", mention["semantic_object_id"])

            _add_node(
                nodes,
                mention_node_id,
                "mention",
                mention.get("canonical_text") or mention_id,
                {
                    "mention_id": mention_id,
                    "semantic_object_id": mention.get("semantic_object_id"),
                    "surface_text": mention.get("surface_text"),
                    "canonical_text": mention.get("canonical_text"),
                    "category": mention.get("category"),
                    "location": mention.get("location", {}),
                    "evidence": mention.get("evidence", {}),
                },
            )

            _add_edge(
                edges,
                seen_edges,
                object_node_id,
                mention_node_id,
                "has_mention",
                {
                    "section_id": section_id,
                    "unit_type": mention.get("location", {}).get("unit_type"),
                },
            )

            _add_edge(
                edges,
                seen_edges,
                mention_node_id,
                evidence_node_id,
                "mention_supports_evidence",
                {
                    "section_id": section_id,
                },
            )

        for neighborhood in section_record.get("phrase_neighborhoods", []):
            neighborhood_id = neighborhood["neighborhood_id"]
            neighborhood_node_id = _stable_id("neighborhood_node", neighborhood_id)
            left_node_id = _stable_id("semantic_object_node", neighborhood["left_object_id"])
            right_node_id = _stable_id("semantic_object_node", neighborhood["right_object_id"])

            _add_node(
                nodes,
                neighborhood_node_id,
                "phrase_neighborhood",
                f'{neighborhood.get("left_text")} ↔ {neighborhood.get("right_text")}',
                {
                    "neighborhood_id": neighborhood_id,
                    "left_text": neighborhood.get("left_text"),
                    "right_text": neighborhood.get("right_text"),
                    "left_category": neighborhood.get("left_category"),
                    "right_category": neighborhood.get("right_category"),
                    "relationship_type": neighborhood.get("relationship_type"),
                    "relationship_family": neighborhood.get("relationship_family"),
                    "relationship_confidence": neighborhood.get("relationship_confidence"),
                    "neighborhood_strength": neighborhood.get("neighborhood_strength"),
                    "cooccurrence_count": neighborhood.get("cooccurrence_count"),
                    "unit_type_counts": neighborhood.get("unit_type_counts", {}),
                },
            )

            _add_edge(
                edges,
                seen_edges,
                left_node_id,
                right_node_id,
                "relates_to",
                {
                    "relationship_type": neighborhood.get("relationship_type"),
                    "relationship_family": neighborhood.get("relationship_family"),
                    "relationship_confidence": neighborhood.get("relationship_confidence"),
                    "neighborhood_strength": neighborhood.get("neighborhood_strength"),
                    "neighborhood_id": neighborhood_id,
                },
            )

            _add_edge(
                edges,
                seen_edges,
                neighborhood_node_id,
                left_node_id,
                "connects_left_object",
                {
                    "relationship_type": neighborhood.get("relationship_type"),
                },
            )

            _add_edge(
                edges,
                seen_edges,
                neighborhood_node_id,
                right_node_id,
                "connects_right_object",
                {
                    "relationship_type": neighborhood.get("relationship_type"),
                },
            )

            _add_edge(
                edges,
                seen_edges,
                neighborhood_node_id,
                evidence_node_id,
                "supports_section_evidence",
                {
                    "section_id": section_id,
                    "relationship_family": neighborhood.get("relationship_family"),
                },
            )

    node_type_counts = {}
    for node in nodes.values():
        node_type_counts[node["node_type"]] = node_type_counts.get(node["node_type"], 0) + 1

    edge_type_counts = {}
    for edge in edges:
        edge_type_counts[edge["edge_type"]] = edge_type_counts.get(edge["edge_type"], 0) + 1

    node_layer_counts = {}
    partition_counts = {}

    for node in nodes.values():
        node_layer_counts[node["node_layer"]] = node_layer_counts.get(node["node_layer"], 0) + 1
        partition_counts[node["partition"]] = partition_counts.get(node["partition"], 0) + 1

    graph_lineage = {
        "semantic_context_model": evidence_model.get("source_models", {}).get("semantic_context", {}),
        "entity_concept_extraction_model": evidence_model.get("source_models", {}).get("entity_concept_extraction", {}),
        "phrase_neighborhood_model": evidence_model.get("source_models", {}).get("phrase_neighborhoods", {}),
        "topic_intent_model": evidence_model.get("source_models", {}).get("topic_intent", {}),
        "section_evidence_model": {
            "schema_version": evidence_model.get("schema_version"),
            "phase": evidence_model.get("phase"),
            "patch": evidence_model.get("patch"),
        },
    }

    graph_model = {
        "schema_version": "semantic_relationship_graph_v1",
        "phase": "4.6.7",
        "patch": "4.6.7A",
        "patch": "4.6.7A",
        "created_at": _now_iso(),
        "source_models": {
            "section_evidence": {
                "schema_version": evidence_model.get("schema_version"),
                "phase": evidence_model.get("phase"),
                "patch": evidence_model.get("patch"),
            },
        },
        "graph_lineage": graph_lineage,
        "article": article,
        "domain_label": evidence_model.get("domain_label"),
        "graph": {
            "nodes": sorted(nodes.values(), key=lambda item: (item["node_type"], item["label"], item["node_id"])),
            "edges": sorted(edges, key=lambda item: (item["edge_type"], item["source_id"], item["target_id"])),
        },
        "metadata": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "node_type_counts": node_type_counts,
            "edge_type_counts": edge_type_counts,
            "node_layer_counts": node_layer_counts,
            "partition_counts": partition_counts,
            "article_node_id": article_node_id,
        },
        "boundary_rule": (
            "Semantic Relationship Graph converts section evidence into a graph representation only. "
            "It does not resolve links, create blue highlights, create yellow highlights, score target pages, "
            "write memory, perform reasoning, or generate explanations."
        ),
    }

    return graph_model


def save_semantic_relationship_graph_v1(
    evidence_model: Dict[str, Any],
    output_path: str | Path,
) -> Dict[str, Any]:
    graph_model = build_semantic_relationship_graph_v1(evidence_model)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(graph_model, indent=2, ensure_ascii=False), encoding="utf-8")
    return graph_model


def explain_semantic_relationship_graph_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.7",
        "patch": "4.6.7A",
        "name": "Semantic Relationship Graph",
        "purpose": "Convert consolidated section evidence into a multi-layer semantic graph for export, memory, reasoning, and resolver systems.",
        "input": "Section Evidence Model from Phase 4.6.6A",
        "output": "Semantic Relationship Graph Model",
        "does": [
            "creates article nodes",
            "creates section nodes",
            "creates article intent nodes",
            "creates section intent nodes",
            "creates semantic object nodes",
            "creates mention nodes",
            "creates phrase neighborhood nodes",
            "creates section evidence nodes",
            "creates typed graph edges",
            "preserves evidence lineage",
            "preserves provenance",
            "preserves relationship families and relationship types",
            "adds node_layer to every node",
            "adds partition metadata to every node",
            "adds graph-level lineage",
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
