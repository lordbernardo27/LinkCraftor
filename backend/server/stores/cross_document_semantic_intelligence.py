
from __future__ import annotations

from typing import Any, Dict, List


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize(text: str) -> str:
    return " ".join(_safe_text(text).lower().split())


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _clamp_score(value: Any) -> float:
    score = _safe_float(value, 0.0)
    if score > 1:
        score = score / 100
    return round(max(0.0, min(1.0, score)), 4)


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
            "does_not_alter_internal_linking_logic": True,
            "does_not_alter_semantic_linking_logic": True,
        },
    }


def graph_multi_article_semantics_v1(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    1.15.1 Multi-Article Semantic Graphing.
    """

    nodes = []
    edges = []
    seen_nodes = set()

    for doc in documents or []:
        doc_id = _safe_text(doc.get("doc_id") or doc.get("id") or doc.get("title") if isinstance(doc, dict) else "")
        title = _safe_text(doc.get("title") or doc.get("name") or doc_id if isinstance(doc, dict) else doc)

        key = _normalize(doc_id or title)

        if not key or key in seen_nodes:
            continue

        seen_nodes.add(key)

        topics = doc.get("topics", []) if isinstance(doc, dict) else []
        nodes.append({
            "doc_id": doc_id or key.replace(" ", "_"),
            "title": title,
            "topics": topics,
            "node_role": "cross_document_article_node",
        })

    for i, source in enumerate(nodes):
        for target in nodes[i + 1:]:
            shared_topics = sorted(set(map(_normalize, source.get("topics", []))) & set(map(_normalize, target.get("topics", []))))

            if not shared_topics:
                continue

            edges.append({
                "source_doc_id": source["doc_id"],
                "target_doc_id": target["doc_id"],
                "relationship_type": "shared_semantic_topic",
                "shared_topics": shared_topics,
                "relationship_strength": round(min(1.0, len(shared_topics) * 0.25), 4),
                "edge_role": "cross_article_relationship",
            })

    return _make_response(
        "1.15.1",
        "Multi-Article Semantic Graphing",
        "Builds governed multi-article semantic graph support without creating a new runtime router.",
        [
            "multi_article_graph_support",
            "cross_article_relationship_mapping",
            "document_node_governance",
            "graphing_audit",
        ],
    ) | {
        "document_nodes": nodes,
        "semantic_edges": edges,
    }


def cluster_cross_document_topics_v1(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    1.15.2 Cross-Document Topic Clustering.
    """

    clusters: Dict[str, Dict[str, Any]] = {}

    for doc in documents or []:
        doc_id = _safe_text(doc.get("doc_id") or doc.get("id") or doc.get("title") if isinstance(doc, dict) else "")
        title = _safe_text(doc.get("title") or doc_id if isinstance(doc, dict) else doc)
        topics = doc.get("topics", []) if isinstance(doc, dict) else []

        for topic in topics:
            topic_key = _normalize(topic)
            if not topic_key:
                continue

            if topic_key not in clusters:
                clusters[topic_key] = {
                    "topic": topic,
                    "documents": [],
                    "cluster_role": "cross_document_topic_cluster",
                }

            clusters[topic_key]["documents"].append({
                "doc_id": doc_id or _normalize(title).replace(" ", "_"),
                "title": title,
            })

    cluster_list = []
    for cluster in clusters.values():
        cluster_list.append({
            **cluster,
            "document_count": len(cluster["documents"]),
            "cluster_relevance": round(min(1.0, len(cluster["documents"]) * 0.25), 4),
        })

    cluster_list.sort(key=lambda x: x["document_count"], reverse=True)

    return _make_response(
        "1.15.2",
        "Cross-Document Topic Clustering",
        "Groups topics across multiple documents into governed semantic clusters.",
        [
            "cross_document_topic_clustering",
            "topic_cluster_grouping",
            "cluster_relevance_support",
            "clustering_audit",
        ],
    ) | {
        "topic_clusters": cluster_list,
    }


def detect_orphan_pages_semantically_v1(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    1.15.3 Orphan-Page Semantic Detection.
    """

    graph = graph_multi_article_semantics_v1(documents)
    connected_ids = set()

    for edge in graph["semantic_edges"]:
        connected_ids.add(edge["source_doc_id"])
        connected_ids.add(edge["target_doc_id"])

    orphan_pages = []
    weakly_connected = []

    for node in graph["document_nodes"]:
        doc_id = node["doc_id"]
        topic_count = len(node.get("topics", []))

        if doc_id not in connected_ids:
            orphan_pages.append({
                "doc_id": doc_id,
                "title": node["title"],
                "reason": "no_cross_document_semantic_edges",
                "orphan_role": "semantic_orphan_page",
            })
        elif topic_count <= 1:
            weakly_connected.append({
                "doc_id": doc_id,
                "title": node["title"],
                "reason": "low_topic_connectivity",
                "orphan_role": "weakly_connected_content",
            })

    return _make_response(
        "1.15.3",
        "Orphan-Page Semantic Detection",
        "Detects semantically orphaned or weakly connected content across documents.",
        [
            "orphan_page_detection",
            "weakly_connected_content_detection",
            "orphan_cluster_reporting",
            "orphan_detection_audit",
        ],
    ) | {
        "orphan_pages": orphan_pages,
        "weakly_connected_pages": weakly_connected,
    }


def support_cross_document_semantic_linking_v1(
    source_documents: List[Dict[str, Any]],
    target_documents: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.15.4 Cross-Document Semantic Linking.
    """

    link_support = []

    for source in source_documents or []:
        source_id = _safe_text(source.get("doc_id") or source.get("id") or source.get("title") if isinstance(source, dict) else "")
        source_title = _safe_text(source.get("title") or source_id if isinstance(source, dict) else source)
        source_topics = set(map(_normalize, source.get("topics", []) if isinstance(source, dict) else []))

        for target in target_documents or []:
            target_id = _safe_text(target.get("doc_id") or target.get("id") or target.get("title") if isinstance(target, dict) else "")
            target_title = _safe_text(target.get("title") or target_id if isinstance(target, dict) else target)
            target_topics = set(map(_normalize, target.get("topics", []) if isinstance(target, dict) else []))

            if source_id and target_id and source_id == target_id:
                continue

            shared_topics = sorted(source_topics & target_topics)

            if not shared_topics:
                continue

            support_score = round(min(1.0, len(shared_topics) * 0.25), 4)

            link_support.append({
                "source_doc_id": source_id,
                "source_title": source_title,
                "target_doc_id": target_id,
                "target_title": target_title,
                "shared_topics": shared_topics,
                "support_score": support_score,
                "linking_role": "cross_document_semantic_linking_support",
                "requires_existing_link_decision_flow": True,
            })

    link_support.sort(key=lambda x: x["support_score"], reverse=True)

    return _make_response(
        "1.15.4",
        "Cross-Document Semantic Linking",
        "Provides cross-document semantic linking support without forcing link decisions.",
        [
            "cross_document_linking_support",
            "source_target_semantic_support",
            "cross_document_link_governance",
            "linking_support_audit",
        ],
    ) | {
        "cross_document_link_support": link_support,
    }


def analyze_content_cluster_intelligence_v1(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    1.15.5 Content Cluster Intelligence.
    """

    clusters = cluster_cross_document_topics_v1(documents)["topic_clusters"]

    intelligence = []

    for cluster in clusters:
        document_count = int(cluster.get("document_count", 0))
        cluster_strength = round(min(1.0, document_count * 0.25), 4)

        gap_signal = "needs_more_supporting_content" if document_count == 1 else "cluster_supported"

        intelligence.append({
            "topic": cluster["topic"],
            "document_count": document_count,
            "cluster_strength": cluster_strength,
            "gap_signal": gap_signal,
            "cluster_role": "content_cluster_intelligence",
        })

    return _make_response(
        "1.15.5",
        "Content Cluster Intelligence",
        "Reports content cluster strength, gaps, and cross-document semantic support.",
        [
            "content_cluster_intelligence",
            "cluster_strength_reporting",
            "cluster_gap_support",
            "content_cluster_audit",
        ],
    ) | {
        "content_cluster_intelligence": intelligence,
    }


def explain_cross_document_semantic_intelligence_v1() -> Dict[str, Any]:
    return {
        "layer": "1.15",
        "name": "Cross-Document Semantic Intelligence",
        "status": "active",
        "scope": "cross_document_semantic_intelligence_governance",
        "sub_layers": [
            "1.15.1 Multi-Article Semantic Graphing",
            "1.15.2 Cross-Document Topic Clustering",
            "1.15.3 Orphan-Page Semantic Detection",
            "1.15.4 Cross-Document Semantic Linking",
            "1.15.5 Content Cluster Intelligence",
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
            "does_not_alter_internal_linking_logic": True,
            "does_not_alter_semantic_linking_logic": True,
        },
    }
