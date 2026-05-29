
from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize(text: str) -> str:
    return " ".join(_safe_text(text).lower().split())


def _relationship_key(source: str, target: str, relationship_type: str) -> Tuple[str, str, str]:
    return (_normalize(source), _normalize(target), _normalize(relationship_type))


def _score_relationship(source: str, target: str, evidence: List[str] | None = None) -> float:
    score = 0.0

    if source and target and _normalize(source) != _normalize(target):
        score += 0.35

    if evidence:
        score += min(0.35, len(evidence) * 0.10)

    if any(x in f"{source} {target}".lower() for x in ["how", "guide", "strategy", "method", "cause", "effect", "risk", "benefit"]):
        score += 0.20

    return round(min(1.0, score), 4)


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
            "does_not_create_new_graph_database": True,
            "does_not_replace_existing_graph_score": True,
        },
    }


def expand_runtime_graph_v1(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    max_nodes: int = 100,
    max_edges: int = 200,
) -> Dict[str, Any]:
    """
    1.9.1 Runtime Graph Expansion.
    """

    clean_nodes: List[Dict[str, Any]] = []
    seen_nodes = set()

    for node in nodes or []:
        label = _safe_text(node.get("label") or node.get("text") or node.get("entity") if isinstance(node, dict) else node)
        key = _normalize(label)

        if not key or key in seen_nodes:
            continue

        seen_nodes.add(key)
        clean_nodes.append({
            "label": label,
            "node_type": node.get("node_type", "semantic_node") if isinstance(node, dict) else "semantic_node",
            "graph_role": "runtime_graph_node",
        })

    clean_edges: List[Dict[str, Any]] = []
    seen_edges = set()

    for edge in edges or []:
        source = _safe_text(edge.get("source") if isinstance(edge, dict) else "")
        target = _safe_text(edge.get("target") if isinstance(edge, dict) else "")
        relationship_type = _safe_text(edge.get("relationship_type", "semantic_related") if isinstance(edge, dict) else "semantic_related")
        evidence = edge.get("evidence", []) if isinstance(edge, dict) else []

        key = _relationship_key(source, target, relationship_type)

        if not source or not target or source == target or key in seen_edges:
            continue

        seen_edges.add(key)
        clean_edges.append({
            "source": source,
            "target": target,
            "relationship_type": relationship_type,
            "confidence": _score_relationship(source, target, evidence),
            "graph_role": "runtime_graph_edge",
        })

    return _make_response(
        "1.9.1",
        "Runtime Graph Expansion",
        "Governed runtime graph node and edge expansion without creating a new graph database.",
        [
            "runtime_graph_node_creation",
            "runtime_graph_edge_creation",
            "graph_expansion_governance",
            "graph_expansion_safety_rules",
            "graph_expansion_explainability",
            "graph_expansion_audit",
        ],
    ) | {
        "nodes": clean_nodes[:max_nodes],
        "edges": clean_edges[:max_edges],
        "node_count": min(len(clean_nodes), max_nodes),
        "edge_count": min(len(clean_edges), max_edges),
    }


def grow_entity_relationships_v1(
    relationships: List[Dict[str, Any]],
    min_confidence: float = 0.35,
) -> Dict[str, Any]:
    """
    1.9.2 Auto-Growing Entity Relationships.
    """

    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    seen = set()

    for rel in relationships or []:
        source = _safe_text(rel.get("source") if isinstance(rel, dict) else "")
        target = _safe_text(rel.get("target") if isinstance(rel, dict) else "")
        evidence = rel.get("evidence", []) if isinstance(rel, dict) else []
        relationship_type = _safe_text(rel.get("relationship_type", "entity_related") if isinstance(rel, dict) else "entity_related")

        score = _score_relationship(source, target, evidence)
        key = _relationship_key(source, target, relationship_type)

        if not source or not target or source == target:
            rejected.append({"source": source, "target": target, "reason": "invalid_entity_relationship"})
            continue

        if key in seen:
            rejected.append({"source": source, "target": target, "reason": "duplicate_entity_relationship"})
            continue

        if score < min_confidence:
            rejected.append({"source": source, "target": target, "reason": "weak_entity_relationship", "confidence": score})
            continue

        seen.add(key)
        accepted.append({
            "source": source,
            "target": target,
            "relationship_type": relationship_type,
            "confidence": score,
            "graph_role": "auto_growing_entity_relationship",
        })

    return _make_response(
        "1.9.2",
        "Auto-Growing Entity Relationships",
        "Adds governed entity relationship growth with duplicate and weak-relationship suppression.",
        [
            "entity_relationship_growth",
            "entity_to_entity_connection_scoring",
            "duplicate_relationship_suppression",
            "weak_relationship_rejection",
            "entity_relationship_explainability",
            "entity_relationship_audit",
        ],
    ) | {
        "accepted_relationships": accepted,
        "rejected_relationships": rejected,
    }


def expand_topics_dynamically_v1(
    topics: List[Dict[str, Any]],
    max_topics: int = 50,
) -> Dict[str, Any]:
    """
    1.9.3 Dynamic Topic Expansion.
    """

    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    seen = set()

    for topic in topics or []:
        label = _safe_text(topic.get("topic") or topic.get("label") or topic.get("text") if isinstance(topic, dict) else topic)
        evidence = topic.get("evidence", []) if isinstance(topic, dict) else []
        key = _normalize(label)

        if not key:
            continue

        if key in seen:
            rejected.append({"topic": label, "reason": "duplicate_topic_expansion"})
            continue

        score = _score_relationship(label, label + " topic", evidence)

        if score < 0.35:
            rejected.append({"topic": label, "reason": "weak_topic_expansion", "confidence": score})
            continue

        seen.add(key)
        accepted.append({
            "topic": label,
            "confidence": score,
            "expansion_role": "dynamic_topic_expansion",
        })

    return _make_response(
        "1.9.3",
        "Dynamic Topic Expansion",
        "Expands related topics from semantic evidence while suppressing weak or duplicate topic growth.",
        [
            "topic_expansion_from_semantic_evidence",
            "related_topic_discovery",
            "topic_variant_governance",
            "weak_topic_expansion_suppression",
            "topic_expansion_explainability",
            "topic_expansion_audit",
        ],
    ) | {
        "accepted_topics": accepted[:max_topics],
        "rejected_topics": rejected,
    }


def enrich_graph_continuously_v1(
    runtime_signals: List[Dict[str, Any]],
    max_enrichments: int = 75,
) -> Dict[str, Any]:
    """
    1.9.4 Continuous Graph Enrichment.
    """

    enrichments: List[Dict[str, Any]] = []

    for signal in runtime_signals or []:
        source = _safe_text(signal.get("source") or signal.get("phrase") or signal.get("topic") if isinstance(signal, dict) else signal)
        target = _safe_text(signal.get("target") or signal.get("related") if isinstance(signal, dict) else "")
        evidence = signal.get("evidence", []) if isinstance(signal, dict) else []

        if not source:
            continue

        score = _score_relationship(source, target or source + " context", evidence)

        enrichments.append({
            "source": source,
            "target": target,
            "enrichment_score": score,
            "enrichment_role": "continuous_graph_enrichment",
        })

    enrichments.sort(key=lambda x: x["enrichment_score"], reverse=True)

    return _make_response(
        "1.9.4",
        "Continuous Graph Enrichment",
        "Prioritizes graph enrichment from runtime, retrieval, and target-intelligence signals.",
        [
            "graph_enrichment_from_runtime_signals",
            "graph_enrichment_from_retrieval_support",
            "graph_enrichment_from_target_intelligence",
            "graph_enrichment_prioritization",
            "graph_enrichment_explainability",
            "graph_enrichment_audit",
        ],
    ) | {
        "enrichments": enrichments[:max_enrichments],
    }


def learn_semantic_graph_patterns_v1(
    relationship_events: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.9.5 Semantic Graph Learning.
    """

    pattern_counts: Dict[str, int] = {}

    for event in relationship_events or []:
        relationship_type = _safe_text(event.get("relationship_type", "semantic_related") if isinstance(event, dict) else "semantic_related")
        pattern_counts[relationship_type] = pattern_counts.get(relationship_type, 0) + 1

    learned_patterns = [
        {
            "relationship_type": relationship_type,
            "event_count": count,
            "learning_role": "semantic_graph_pattern",
            "confidence_adjustment": round(min(0.25, count * 0.03), 4),
        }
        for relationship_type, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    return _make_response(
        "1.9.5",
        "Semantic Graph Learning",
        "Learns repeated relationship patterns for governed semantic graph confidence adjustment.",
        [
            "semantic_graph_learning_rules",
            "repeated_relationship_pattern_learning",
            "graph_confidence_adjustment",
            "graph_learning_safety_rules",
            "graph_learning_explainability",
            "semantic_graph_learning_audit",
        ],
    ) | {
        "learned_patterns": learned_patterns,
    }


def explain_dynamic_knowledge_graph_expansion_v1() -> Dict[str, Any]:
    return {
        "layer": "1.9",
        "name": "Dynamic Knowledge Graph Expansion",
        "status": "active",
        "scope": "graph_expansion_governance",
        "sub_layers": [
            "1.9.1 Runtime Graph Expansion",
            "1.9.2 Auto-Growing Entity Relationships",
            "1.9.3 Dynamic Topic Expansion",
            "1.9.4 Continuous Graph Enrichment",
            "1.9.5 Semantic Graph Learning",
        ],
        "safety_rules": {
            "governance_only": True,
            "runtime_support_only": True,
            "does_not_modify_uploaded_article": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_target_selector": True,
            "does_not_create_new_graph_database": True,
            "does_not_replace_existing_graph_score": True,
        },
    }
