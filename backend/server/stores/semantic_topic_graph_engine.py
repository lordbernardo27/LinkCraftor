
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
            "does_not_replace_dynamic_knowledge_graph": True,
            "does_not_replace_ontology_alignment": True,
            "does_not_replace_cross_document_semantic_intelligence": True,
        },
    }


def build_unified_semantic_topic_graph_v1(
    topics: List[Dict[str, Any]],
    relationships: List[Dict[str, Any]],
) -> Dict[str, Any]:
    nodes = []
    edges = []
    seen_nodes = set()
    seen_edges = set()

    for item in topics or []:
        topic = _safe_text(item.get("topic") or item.get("label") or item.get("title") if isinstance(item, dict) else item)
        topic_type = _safe_text(item.get("type", "semantic_topic") if isinstance(item, dict) else "semantic_topic")

        key = _normalize(topic)

        if not key or key in seen_nodes:
            continue

        seen_nodes.add(key)

        nodes.append({
            "topic_id": key.replace(" ", "_"),
            "topic": topic,
            "topic_type": topic_type,
            "node_role": "unified_semantic_topic_node",
        })

    for rel in relationships or []:
        source = _safe_text(rel.get("source") if isinstance(rel, dict) else "")
        target = _safe_text(rel.get("target") if isinstance(rel, dict) else "")
        relationship_type = _safe_text(rel.get("relationship_type", "semantic_related") if isinstance(rel, dict) else "semantic_related")

        if not source or not target:
            continue

        edge_key = (_normalize(source), _normalize(target), _normalize(relationship_type))

        if edge_key in seen_edges:
            continue

        seen_edges.add(edge_key)

        edges.append({
            "source": source,
            "target": target,
            "relationship_type": relationship_type,
            "edge_role": "unified_semantic_topic_edge",
        })

    return _make_response(
        "1.16.1",
        "Unified Semantic Topic Graph",
        "Unifies topic nodes and semantic relationships into a governed topic graph support layer.",
        [
            "unified_topic_graph_support",
            "topic_node_governance",
            "topic_edge_governance",
            "topic_graph_audit",
        ],
    ) | {
        "topic_nodes": nodes,
        "topic_edges": edges,
    }


def fuse_entity_ontology_topics_v1(
    entities: List[Dict[str, Any]],
    ontology_relationships: List[Dict[str, Any]],
) -> Dict[str, Any]:
    fused = []

    for entity in entities or []:
        entity_name = _safe_text(entity.get("entity") or entity.get("name") if isinstance(entity, dict) else entity)
        entity_type = _safe_text(entity.get("type", "entity") if isinstance(entity, dict) else "entity")

        if not entity_name:
            continue

        related_ontology = []

        for rel in ontology_relationships or []:
            source = _safe_text(rel.get("source") if isinstance(rel, dict) else "")
            target = _safe_text(rel.get("target") if isinstance(rel, dict) else "")
            relationship_type = _safe_text(rel.get("relationship_type", "ontology_related") if isinstance(rel, dict) else "ontology_related")

            if _normalize(entity_name) in {_normalize(source), _normalize(target)}:
                related_ontology.append({
                    "source": source,
                    "target": target,
                    "relationship_type": relationship_type,
                })

        fused.append({
            "entity": entity_name,
            "entity_type": entity_type,
            "related_ontology": related_ontology,
            "fusion_role": "entity_ontology_topic_fusion",
        })

    return _make_response(
        "1.16.2",
        "Entity + Ontology Fusion",
        "Fuses entity signals with ontology relationships without replacing ontology alignment.",
        [
            "entity_ontology_fusion_support",
            "entity_topic_alignment",
            "ontology_topic_alignment",
            "fusion_audit",
        ],
    ) | {
        "fused_entity_ontology_topics": fused,
    }


def reason_cross_document_topic_graph_v1(
    document_graph: Dict[str, Any],
) -> Dict[str, Any]:
    nodes = document_graph.get("document_nodes", []) if isinstance(document_graph, dict) else []
    edges = document_graph.get("semantic_edges", []) if isinstance(document_graph, dict) else []

    reasoning = []
    connected_docs = set()

    for edge in edges:
        source = _safe_text(edge.get("source_doc_id") if isinstance(edge, dict) else "")
        target = _safe_text(edge.get("target_doc_id") if isinstance(edge, dict) else "")
        shared_topics = edge.get("shared_topics", []) if isinstance(edge, dict) else []

        if source:
            connected_docs.add(source)
        if target:
            connected_docs.add(target)

        reasoning.append({
            "source_doc_id": source,
            "target_doc_id": target,
            "shared_topics": shared_topics,
            "reasoning_type": "cross_document_topic_graph_reasoning",
            "reasoning_summary": "Documents are semantically connected by shared topic signals.",
        })

    orphan_candidates = []

    for node in nodes:
        doc_id = _safe_text(node.get("doc_id") if isinstance(node, dict) else "")
        if doc_id and doc_id not in connected_docs:
            orphan_candidates.append({
                "doc_id": doc_id,
                "title": node.get("title", "") if isinstance(node, dict) else "",
                "reason": "no_topic_graph_edges",
            })

    return _make_response(
        "1.16.3",
        "Cross-Document Graph Reasoning",
        "Provides governed reasoning over existing cross-document semantic graph outputs.",
        [
            "cross_document_graph_reasoning",
            "document_topic_graph_support",
            "graph_relationship_reasoning",
            "graph_reasoning_audit",
        ],
    ) | {
        "graph_reasoning": reasoning,
        "orphan_candidates": orphan_candidates,
    }


def explain_semantic_topic_graph_engine_v1() -> Dict[str, Any]:
    return {
        "layer": "1.16",
        "name": "Semantic Topic Graph Engine",
        "status": "active",
        "scope": "semantic_topic_graph_governance",
        "sub_layers": [
            "1.16.1 Unified Semantic Topic Graph",
            "1.16.2 Entity + Ontology Fusion",
            "1.16.3 Cross-Document Graph Reasoning",
        ],
        "held_for_architectural_review": [
            "AGI-Style Topic Reasoning",
            "Autonomous Semantic Intelligence Foundations",
            "Enterprise Semantic Graph Infrastructure",
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
            "does_not_replace_dynamic_knowledge_graph": True,
            "does_not_replace_ontology_alignment": True,
            "does_not_replace_cross_document_semantic_intelligence": True,
        },
    }
