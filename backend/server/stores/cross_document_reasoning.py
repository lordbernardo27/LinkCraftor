from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _data_dir() -> Path:
    return Path("backend/server/data")


def _ws_safe(workspace_id: str) -> str:
    s = str(workspace_id or "workspace").strip()
    s = re.sub(r"[^a-zA-Z0-9_\-]+", "_", s)
    if not s.startswith("ws_"):
        s = f"ws_{s}"
    return s[:100]


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _upload_struct_path(ws: str) -> Path:
    return _data_dir() / f"upload_struct_{_ws_safe(ws)}.json"


def _upload_entity_graph_path(ws: str) -> Path:
    return _data_dir() / f"upload_entity_graph_{_ws_safe(ws)}.json"


def _upload_phrase_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "upload" / f"upload_phrase_pool_{_ws_safe(ws)}.json"


def _active_phrase_set_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "active" / f"active_phrase_set_{_ws_safe(ws)}.json"


def _norm_text(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9\s\-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_docs_from_struct(struct: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    docs = struct.get("docs") if isinstance(struct, dict) else {}
    if isinstance(docs, dict):
        return docs
    if isinstance(docs, list):
        out: Dict[str, Dict[str, Any]] = {}
        for idx, doc in enumerate(docs):
            if not isinstance(doc, dict):
                continue
            doc_id = str(doc.get("document_id") or doc.get("doc_id") or doc.get("id") or f"doc_{idx+1}")
            out[doc_id] = doc
        return out
    return {}


def _extract_phrases_by_doc(pool: Dict[str, Any]) -> Dict[str, Set[str]]:
    phrases_by_doc: Dict[str, Set[str]] = {}

    phrases = pool.get("phrases", {})

    if not isinstance(phrases, dict):
        return phrases_by_doc

    for phrase_key, payload in phrases.items():

        if not isinstance(payload, dict):
            continue

        phrase = _norm_text(
            payload.get("phrase")
            or phrase_key
        )

        if not phrase:
            continue

        docs = payload.get("docs", {})

        if not isinstance(docs, dict):
            continue

        for doc_id in docs.keys():

            did = str(doc_id or "").strip()

            if not did:
                continue

            phrases_by_doc.setdefault(did, set()).add(phrase)

    return phrases_by_doc


def _extract_entities_by_doc(graph: Dict[str, Any]) -> Dict[str, Set[str]]:
    entities_by_doc: Dict[str, Set[str]] = {}

    nodes = graph.get("nodes") if isinstance(graph, dict) else {}
    if isinstance(nodes, dict):
        iterable = nodes.values()
    elif isinstance(nodes, list):
        iterable = nodes
    else:
        iterable = []

    for node in iterable:
        if not isinstance(node, dict):
            continue

        entity = _norm_text(
            node.get("entity")
            or node.get("name")
            or node.get("label")
            or node.get("text")
        )

        doc_ids = (
            node.get("document_ids")
            or node.get("docs")
            or node.get("doc_ids")
            or []
        )

        if isinstance(doc_ids, str):
            doc_ids = [doc_ids]

        if entity and isinstance(doc_ids, list):
            for doc_id in doc_ids:
                did = str(doc_id or "").strip()
                if did:
                    entities_by_doc.setdefault(did, set()).add(entity)

    return entities_by_doc


def load_cross_document_inputs(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)

    struct_path = _upload_struct_path(ws)
    graph_path = _upload_entity_graph_path(ws)
    phrase_pool_path = _upload_phrase_pool_path(ws)
    active_set_path = _active_phrase_set_path(ws)

    struct = _read_json(struct_path, {"workspace_id": ws, "docs": {}})
    graph = _read_json(graph_path, {"workspace_id": ws, "nodes": {}, "edges": []})
    phrase_pool = _read_json(phrase_pool_path, {"workspace_id": ws, "phrases": []})
    active_set = _read_json(active_set_path, {"workspace_id": ws, "active_document_ids": []})

    return {
        "workspace_id": ws,
        "loaded_at": _now_iso(),
        "paths": {
            "upload_struct": str(struct_path),
            "upload_entity_graph": str(graph_path),
            "upload_phrase_pool": str(phrase_pool_path),
            "active_phrase_set": str(active_set_path),
        },
        "exists": {
            "upload_struct": struct_path.exists(),
            "upload_entity_graph": graph_path.exists(),
            "upload_phrase_pool": phrase_pool_path.exists(),
            "active_phrase_set": active_set_path.exists(),
        },
        "upload_struct": struct,
        "upload_entity_graph": graph,
        "upload_phrase_pool": phrase_pool,
        "active_phrase_set": active_set,
    }


def build_document_registry(workspace_id: str) -> Dict[str, Any]:
    inputs = load_cross_document_inputs(workspace_id)
    ws = inputs["workspace_id"]

    docs = _extract_docs_from_struct(inputs["upload_struct"])
    phrases_by_doc = _extract_phrases_by_doc(inputs["upload_phrase_pool"])
    entities_by_doc = _extract_entities_by_doc(inputs["upload_entity_graph"])

    active_ids = inputs["active_phrase_set"].get("active_document_ids", [])
    if not isinstance(active_ids, list):
        active_ids = []

    registry: Dict[str, Dict[str, Any]] = {}

    all_doc_ids = set(docs.keys()) | set(phrases_by_doc.keys()) | set(entities_by_doc.keys())

    for doc_id in sorted(all_doc_ids):
        doc_obj = docs.get(doc_id, {}) if isinstance(docs.get(doc_id), dict) else {}

        title = (
            doc_obj.get("title")
            or doc_obj.get("filename")
            or doc_obj.get("name")
            or doc_id
        )

        registry[doc_id] = {
            "document_id": doc_id,
            "title": str(title),
            "is_active": doc_id in active_ids,
            "phrase_count": len(phrases_by_doc.get(doc_id, set())),
            "entity_count": len(entities_by_doc.get(doc_id, set())),
            "phrases": sorted(phrases_by_doc.get(doc_id, set())),
            "entities": sorted(entities_by_doc.get(doc_id, set())),
        }

    return {
        "workspace_id": ws,
        "type": "cross_document_registry",
        "generated_at": _now_iso(),
        "documents_count": len(registry),
        "active_document_ids_count": len(active_ids),
        "source_files_exist": inputs["exists"],
        "documents": registry,
        "runtime_effect": "read_only_no_runtime_injection",
    }

def _jaccard_similarity(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0

    union = a | b
    if not union:
        return 0.0

    intersection = a & b
    return round(len(intersection) / len(union), 4)


def _relationship_strength(score: float) -> str:
    if score >= 0.75:
        return "very_high"
    if score >= 0.50:
        return "high"
    if score >= 0.25:
        return "moderate"
    if score >= 0.10:
        return "low"
    return "minimal"


def build_cross_document_phrase_relationships(
    workspace_id: str,
) -> Dict[str, Any]:

    registry_data = build_document_registry(workspace_id)

    docs = registry_data.get("documents", {})

    relationships: List[Dict[str, Any]] = []

    doc_ids = sorted(docs.keys())

    for i in range(len(doc_ids)):
        for j in range(i + 1, len(doc_ids)):

            left_id = doc_ids[i]
            right_id = doc_ids[j]

            left_doc = docs.get(left_id, {})
            right_doc = docs.get(right_id, {})

            left_phrases = set(left_doc.get("phrases", []))
            right_phrases = set(right_doc.get("phrases", []))

            shared_phrases = sorted(left_phrases & right_phrases)

            phrase_overlap_score = _jaccard_similarity(
                left_phrases,
                right_phrases,
            )

            relationship = {
                "left_document_id": left_id,
                "left_title": left_doc.get("title"),
                "right_document_id": right_id,
                "right_title": right_doc.get("title"),

                "shared_phrase_count": len(shared_phrases),
                "shared_phrases": shared_phrases[:100],

                "left_phrase_count": len(left_phrases),
                "right_phrase_count": len(right_phrases),

                "phrase_overlap_score": phrase_overlap_score,

                "relationship_strength": _relationship_strength(
                    phrase_overlap_score
                ),

                "reasoning_type": "cross_document_phrase_overlap",
            }

            relationships.append(relationship)

    relationships.sort(
        key=lambda x: (
            x.get("phrase_overlap_score", 0.0),
            x.get("shared_phrase_count", 0),
        ),
        reverse=True,
    )

    return {
        "workspace_id": registry_data["workspace_id"],
        "generated_at": _now_iso(),

        "documents_count": registry_data["documents_count"],

        "relationship_pairs_count": len(relationships),

        "relationships": relationships,

        "runtime_effect": "read_only_no_runtime_injection",

        "layer": "1.6.1.4_cross_document_phrase_matching",
    }


def build_cross_document_entity_relationships(
    workspace_id: str,
) -> Dict[str, Any]:

    registry_data = build_document_registry(workspace_id)

    docs = registry_data.get("documents", {})

    relationships: List[Dict[str, Any]] = []

    doc_ids = sorted(docs.keys())

    for i in range(len(doc_ids)):
        for j in range(i + 1, len(doc_ids)):

            left_id = doc_ids[i]
            right_id = doc_ids[j]

            left_doc = docs.get(left_id, {})
            right_doc = docs.get(right_id, {})

            left_entities = set(left_doc.get("entities", []))
            right_entities = set(right_doc.get("entities", []))

            shared_entities = sorted(
                left_entities & right_entities
            )

            entity_overlap_score = _jaccard_similarity(
                left_entities,
                right_entities,
            )

            dominant_entities = sorted(
                shared_entities,
                key=lambda x: len(x),
                reverse=True,
            )[:20]

            relationship = {
                "left_document_id": left_id,
                "left_title": left_doc.get("title"),

                "right_document_id": right_id,
                "right_title": right_doc.get("title"),

                "shared_entity_count": len(shared_entities),

                "shared_entities": shared_entities[:100],

                "dominant_entities": dominant_entities,

                "left_entity_count": len(left_entities),
                "right_entity_count": len(right_entities),

                "entity_overlap_score": entity_overlap_score,

                "relationship_strength": _relationship_strength(
                    entity_overlap_score
                ),

                "reasoning_type": "cross_document_entity_overlap",
            }

            relationships.append(relationship)

    relationships.sort(
        key=lambda x: (
            x.get("entity_overlap_score", 0.0),
            x.get("shared_entity_count", 0),
        ),
        reverse=True,
    )

    return {
        "workspace_id": registry_data["workspace_id"],

        "generated_at": _now_iso(),

        "documents_count": registry_data["documents_count"],

        "relationship_pairs_count": len(relationships),

        "relationships": relationships,

        "runtime_effect": "read_only_no_runtime_injection",

        "layer": "1.6.1.5_cross_document_entity_matching",
    }


def build_semantic_relationship_scores(
    workspace_id: str,
) -> Dict[str, Any]:

    phrase_data = build_cross_document_phrase_relationships(
        workspace_id
    )

    entity_data = build_cross_document_entity_relationships(
        workspace_id
    )

    entity_index = {}

    for rel in entity_data.get("relationships", []):

        pair_key = (
            rel.get("left_document_id"),
            rel.get("right_document_id"),
        )

        entity_index[pair_key] = rel

    unified_relationships = []

    for phrase_rel in phrase_data.get("relationships", []):

        left_id = phrase_rel.get("left_document_id")
        right_id = phrase_rel.get("right_document_id")

        pair_key = (left_id, right_id)

        entity_rel = entity_index.get(pair_key, {})

        phrase_score = float(
            phrase_rel.get("phrase_overlap_score", 0.0)
        )

        entity_score = float(
            entity_rel.get("entity_overlap_score", 0.0)
        )

        semantic_relationship_score = round(
            (
                phrase_score * 0.85
            ) + (
                entity_score * 0.15
            ),
            4,
        )

        relationship_reasons = []

        if phrase_rel.get("shared_phrase_count", 0) > 0:
            relationship_reasons.append(
                "shared_phrases"
            )

        if entity_rel.get("shared_entity_count", 0) > 0:
            relationship_reasons.append(
                "shared_entities"
            )

        future_support_layers = []

        if entity_rel.get("shared_entity_count", 0) == 0:
            future_support_layers.append(
                "entity_overlap_pending"
            )

        future_support_layers.extend([
            "ontology_alignment_pending",
            "semantic_family_clustering_pending",
            "canonical_topic_resolution_pending",
        ])

        unified = {
            "left_document_id": left_id,
            "left_title": phrase_rel.get("left_title"),

            "right_document_id": right_id,
            "right_title": phrase_rel.get("right_title"),

            "semantic_relationship_score":
                semantic_relationship_score,

            "relationship_strength":
                _relationship_strength(
                    semantic_relationship_score
                ),

            "shared_phrase_count":
                phrase_rel.get("shared_phrase_count", 0),

            "shared_entity_count":
                entity_rel.get("shared_entity_count", 0),

            "relationship_reasons":
                relationship_reasons,

            "future_support_layers":
                future_support_layers,

            "reasoning_type":
                "unified_semantic_relationship",
        }

        unified_relationships.append(unified)

    unified_relationships.sort(
        key=lambda x: (
            x.get("semantic_relationship_score", 0.0),
            x.get("shared_phrase_count", 0),
        ),
        reverse=True,
    )

    return {
        "workspace_id": phrase_data["workspace_id"],

        "generated_at": _now_iso(),

        "documents_count": phrase_data["documents_count"],

        "relationship_pairs_count":
            len(unified_relationships),

        "relationships":
            unified_relationships,

        "runtime_effect":
            "read_only_no_runtime_injection",

        "layer":
            "1.6.1.6_semantic_relationship_scores",
    }


def build_topic_clusters(
    workspace_id: str,
    minimum_score: float = 0.02,
) -> Dict[str, Any]:

    semantic_data = build_semantic_relationship_scores(
        workspace_id
    )

    relationships = semantic_data.get(
        "relationships",
        []
    )

    graph: Dict[str, Set[str]] = {}

    document_titles: Dict[str, str] = {}

    for rel in relationships:

        score = float(
            rel.get(
                "semantic_relationship_score",
                0.0,
            )
        )

        if score < minimum_score:
            continue

        left_id = str(
            rel.get("left_document_id")
        )

        right_id = str(
            rel.get("right_document_id")
        )

        left_title = str(
            rel.get("left_title")
        )

        right_title = str(
            rel.get("right_title")
        )

        document_titles[left_id] = left_title
        document_titles[right_id] = right_title

        graph.setdefault(left_id, set()).add(right_id)
        graph.setdefault(right_id, set()).add(left_id)

    visited: Set[str] = set()

    clusters: List[Dict[str, Any]] = []

    cluster_id = 0

    for start_doc in graph.keys():

        if start_doc in visited:
            continue

        cluster_id += 1

        stack = [start_doc]

        component: Set[str] = set()

        while stack:

            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)

            component.add(current)

            for neighbor in graph.get(current, set()):

                if neighbor not in visited:
                    stack.append(neighbor)

        cluster_documents = []

        for doc_id in sorted(component):

            cluster_documents.append({
                "document_id": doc_id,
                "title": document_titles.get(
                    doc_id,
                    doc_id,
                ),
            })

        cluster = {
            "cluster_id":
                f"cluster_{cluster_id}",

            "documents_count":
                len(cluster_documents),

            "documents":
                cluster_documents,

            "cluster_strength":
                "emerging"
                if len(cluster_documents) <= 2
                else "strong",

            "reasoning_type":
                "semantic_topic_cluster",
        }

        clusters.append(cluster)

    clusters.sort(
        key=lambda x: x.get(
            "documents_count",
            0,
        ),
        reverse=True,
    )

    clustered_docs = sum(
        c.get("documents_count", 0)
        for c in clusters
    )

    return {
        "workspace_id":
            semantic_data["workspace_id"],

        "generated_at":
            _now_iso(),

        "clusters_detected":
            len(clusters),

        "clustered_documents":
            clustered_docs,

        "minimum_score_threshold":
            minimum_score,

        "clusters":
            clusters,

        "runtime_effect":
            "read_only_no_runtime_injection",

        "layer":
            "1.6.1.7_topic_cluster_detection",
    }


def build_cross_document_reasoning_summary(
    workspace_id: str,
) -> Dict[str, Any]:

    semantic_data = build_semantic_relationship_scores(
        workspace_id
    )

    cluster_data = build_topic_clusters(
        workspace_id
    )

    relationships = semantic_data.get(
        "relationships",
        []
    )

    clusters = cluster_data.get(
        "clusters",
        []
    )

    strongest_relationships = sorted(
        relationships,
        key=lambda x: x.get(
            "semantic_relationship_score",
            0.0,
        ),
        reverse=True,
    )[:10]

    total_relationship_score = sum(
        float(
            r.get(
                "semantic_relationship_score",
                0.0,
            )
        )
        for r in relationships
    )

    avg_relationship_score = round(
        (
            total_relationship_score
            / max(len(relationships), 1)
        ),
        4,
    )

    dominant_cluster = None

    if clusters:
        dominant_cluster = max(
            clusters,
            key=lambda x: x.get(
                "documents_count",
                0,
            )
        )

    semantic_density = "low"

    if avg_relationship_score >= 0.05:
        semantic_density = "moderate"

    if avg_relationship_score >= 0.10:
        semantic_density = "high"

    workspace_focus = []

    for rel in strongest_relationships:

        workspace_focus.extend(
            rel.get(
                "relationship_reasons",
                []
            )
        )

    workspace_focus = sorted(
        list(set(workspace_focus))
    )

    summary = {
        "workspace_id":
            workspace_id,

        "generated_at":
            _now_iso(),

        "documents_count":
            semantic_data.get(
                "documents_count",
                0,
            ),

        "relationship_pairs_count":
            semantic_data.get(
                "relationship_pairs_count",
                0,
            ),

        "clusters_detected":
            cluster_data.get(
                "clusters_detected",
                0,
            ),

        "average_relationship_score":
            avg_relationship_score,

        "semantic_density":
            semantic_density,

        "workspace_focus":
            workspace_focus,

        "dominant_cluster":
            dominant_cluster,

        "strongest_relationships":
            strongest_relationships,

        "reasoning_state": {
            "phrase_overlap":
                "active",

            "entity_overlap":
                "dormant_pending_entity_graph_v2",

            "ontology_alignment":
                "pending",

            "semantic_families":
                "pending",

            "canonical_topics":
                "pending",

            "contextual_windowing":
                "pending",
        },

        "runtime_effect":
            "read_only_no_runtime_injection",

        "layer":
            "1.6.1.8_cross_document_reasoning_summary",
    }

    return summary


def explain_cross_document_intelligence_governance_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    summary = build_cross_document_reasoning_summary(
        workspace_id
    )

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "governance_type": "cross_document_intelligence_explanation",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "protected_systems": [
            "rb2_runtime",
            "active_phrase_pool",
            "highlight_selection_engine",
            "highlight_density_engine",
            "internal_linking_logic",
            "semantic_linking_logic",
        ],
        "existing_summary": summary,
        "explanation": {
            "purpose": "Explain existing cross-document relationships, topic clusters, semantic relationships, and document reinforcement without rebuilding or mutating them.",
            "decision": "orchestration_explanation_only",
            "reason": "cross-document phrase relationships, entity relationships, semantic scores, and topic clusters already exist.",
        },
        "layer": "1.7.6_cross_document_intelligence_governance_explanation_v2",
    }


def explain_semantic_memory_governance_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    cross_doc_summary = build_cross_document_reasoning_summary(
        workspace_id
    )

    semantic_memory_status = {
        "semantic_duplicate_suppression": "existing_distributed",
        "wrapper_phrase_compression": "existing_distributed",
        "semantic_root_suppression": "existing_distributed",
        "relationship_collapsing": "existing_distributed",
        "canonical_topic_family_grouping": "existing_distributed",
        "runtime_duplicate_url_guard": "existing_distributed",
        "dedicated_semantic_memory_layer": "governance_explanation_only",
    }

    protected_boundaries = {
        "blue_internal_linking": "not_modified",
        "yellow_semantic_linking": "not_modified",
        "rb2_runtime": "not_modified",
        "active_phrase_pool": "not_modified",
        "highlight_selection_engine": "not_modified",
        "highlight_density_engine": "not_modified",
        "canonical_governance": "not_modified",
    }

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "governance_type": "semantic_memory_reduction_explanation",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "semantic_memory_status": semantic_memory_status,
        "protected_boundaries": protected_boundaries,
        "existing_cross_document_summary": {
            "documents_count": cross_doc_summary.get("documents_count"),
            "relationship_pairs_count": cross_doc_summary.get("relationship_pairs_count"),
            "clusters_detected": cross_doc_summary.get("clusters_detected"),
            "semantic_density": cross_doc_summary.get("semantic_density"),
            "average_relationship_score": cross_doc_summary.get("average_relationship_score"),
        },
        "explanation": {
            "purpose": "Explain and govern existing distributed semantic memory reduction signals without rebuilding or mutating them.",
            "decision": "read_only_governance_layer",
            "reason": "semantic deduplication, wrapper compression, semantic roots, relationship collapsing, and canonical family grouping already exist across the system.",
        },
        "layer": "1.7.5_semantic_memory_governance_v2",
    }


def explain_long_article_compression_governance_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "governance_type": "long_article_compression_explanation",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "existing_capabilities": {
            "paragraph_segmentation": "existing_distributed",
            "heading_aware_extraction": "existing_distributed",
            "context_window_extraction": "existing_distributed",
            "article_length_classification": "existing_distributed",
            "paragraph_tokenization": "existing_distributed",
            "rb2_paragraph_contexts": "existing_distributed",
        },
        "protected_boundaries": {
            "rb2_runtime": "not_modified",
            "active_phrase_pool": "not_modified",
            "highlight_selection_engine": "not_modified",
            "highlight_density_engine": "not_modified",
            "internal_linking_logic": "not_modified",
            "semantic_linking_logic": "not_modified",
        },
        "explanation": {
            "purpose": "Explain existing long-article compression primitives without rebuilding paragraph extraction, chunking, or runtime systems.",
            "decision": "read_only_governance_layer",
            "reason": "paragraph segmentation, heading-aware extraction, context windows, and article length classification already exist.",
        },
        "layer": "1.7.1_long_article_compression_governance_v2",
    }


def explain_semantic_context_compression_governance_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "governance_type": "semantic_context_compression_explanation",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "existing_capabilities": {
            "semantic_phrase_contexts": "existing_distributed",
            "paragraph_level_context": "existing_distributed",
            "heading_context_signals": "existing_distributed",
            "phrase_relevance_scoring": "existing_distributed",
            "semantic_similarity_signals": "existing_distributed",
            "contextual_linking_signals": "existing_distributed",
        },
        "protected_boundaries": {
            "internal_linking_logic": "not_modified",
            "semantic_linking_logic": "not_modified",
            "rb2_runtime": "not_modified",
            "active_phrase_pool": "not_modified",
            "target_pool_resolution": "not_modified",
            "highlight_selection_engine": "not_modified",
            "highlight_density_engine": "not_modified",
        },
        "explanation": {
            "purpose": "Explain how existing semantic context signals are compressed for governance visibility without rebuilding semantic linking or changing runtime decisions.",
            "decision": "read_only_governance_layer",
            "reason": "semantic context extraction, paragraph relevance, heading signals, and phrase scoring already exist across the current intelligence pipeline.",
        },
        "layer": "1.7.2_semantic_context_compression_governance_v2",
    }


def explain_runtime_context_optimization_governance_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "governance_type": "runtime_context_optimization_explanation",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "existing_capabilities": {
            "rb2_runtime_contexts": "existing_distributed",
            "active_pool_runtime_filtering": "existing_distributed",
            "highlight_selection_runtime_signals": "existing_distributed",
            "highlight_density_runtime_signals": "existing_distributed",
            "target_resolution_runtime_context": "existing_distributed",
            "article_occurrence_matching": "existing_distributed",
        },
        "protected_boundaries": {
            "rb2_runtime": "not_modified",
            "engine_run_endpoint": "not_modified",
            "active_phrase_pool": "not_modified",
            "target_pool_resolution": "not_modified",
            "internal_linking_logic": "not_modified",
            "semantic_linking_logic": "not_modified",
            "highlight_selection_engine": "not_modified",
            "highlight_density_engine": "not_modified",
        },
        "explanation": {
            "purpose": "Explain existing runtime context optimization controls without changing RB2 execution, target resolution, highlight selection, or semantic/internal linking behavior.",
            "decision": "read_only_governance_layer",
            "reason": "runtime filtering, occurrence matching, target context, and highlight runtime signals already exist in the current pipeline.",
        },
        "layer": "1.7.3_runtime_context_optimization_governance_v2",
    }


def explain_large_document_reasoning_governance_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "governance_type": "large_document_reasoning_explanation",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "existing_capabilities": {
            "cross_paragraph_reasoning": "existing_distributed",
            "multi_section_context_awareness": "existing_distributed",
            "heading_to_paragraph_mapping": "existing_distributed",
            "document_structure_awareness": "existing_distributed",
            "rb2_context_reasoning": "existing_distributed",
            "phrase_to_context_resolution": "existing_distributed",
            "workspace_document_isolation": "existing_distributed",
        },
        "protected_boundaries": {
            "rb2_runtime": "not_modified",
            "engine_runtime_flow": "not_modified",
            "active_phrase_pool": "not_modified",
            "target_pool_resolution": "not_modified",
            "internal_linking_logic": "not_modified",
            "semantic_linking_logic": "not_modified",
            "highlight_selection_engine": "not_modified",
            "highlight_density_engine": "not_modified",
            "workspace_boundaries": "not_modified",
        },
        "explanation": {
            "purpose": "Explain how existing large-document reasoning primitives already operate across sections, headings, contexts, and phrase relationships without rebuilding document reasoning engines.",
            "decision": "read_only_governance_layer",
            "reason": "cross-section reasoning, contextual mapping, RB2 reasoning, and document-aware phrase resolution already exist across the current architecture.",
        },
        "layer": "1.7.4_large_document_reasoning_governance_v2",
    }


def explain_semantic_memory_reduction_governance_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "governance_type": "semantic_memory_reduction_explanation",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "existing_capabilities": {
            "semantic_signal_reuse": "existing_distributed",
            "compressed_context_references": "existing_distributed",
            "decision_intelligence_reuse": "existing_distributed",
            "workspace_scoped_memory": "existing_distributed",
            "historical_context_summarization": "existing_distributed",
        },
        "protected_boundaries": {
            "decision_intelligence": "not_modified",
            "rb2_runtime": "not_modified",
            "active_phrase_pool": "not_modified",
            "target_pool_resolution": "not_modified",
            "internal_linking_logic": "not_modified",
            "semantic_linking_logic": "not_modified",
        },
        "explanation": {
            "purpose": "Explain existing semantic memory reduction governance without changing memory stores, runtime behavior, or linking intelligence.",
            "decision": "read_only_governance_layer",
            "reason": "semantic signal reuse, workspace-scoped context, and compressed historical references already exist as distributed capabilities.",
        },
        "layer": "1.7.5_semantic_memory_reduction_governance_v2",
    }


UNIFIED_SEMANTIC_INTENT_SCHEMA_V1 = {
    "schema_name": "unified_semantic_intent_schema",
    "schema_version": "1.8.1.1_v1",
    "scope": "universal_cross_niche_semantic_intent",
    "runtime_effect": "schema_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "allowed_intent_types": [
        "informational",
        "transactional",
        "preventive",
        "diagnostic",
        "comparison",
        "mixed",
        "unknown",
    ],
    "required_fields": [
        "intent_type",
        "intent_confidence",
        "intent_evidence",
        "intent_source",
        "intent_scope",
    ],
    "optional_fields": [
        "secondary_intents",
        "vertical_context",
        "workspace_id",
        "document_id",
        "phrase",
        "target_url",
        "notes",
    ],
    "field_contract": {
        "intent_type": "one of allowed_intent_types",
        "intent_confidence": "float_between_0_and_1",
        "intent_evidence": "list_of_evidence_strings",
        "intent_source": "source_engine_or_layer_name",
        "intent_scope": "where_this_intent_signal_applies",
        "secondary_intents": "optional_list_of_additional_intent_types",
        "vertical_context": "optional_vertical_or_domain_context_without_hardcoding",
    },
    "universal_design_rules": {
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "runtime_safe": True,
    },
}

def get_unified_semantic_intent_schema_v1() -> Dict[str, Any]:
    return dict(UNIFIED_SEMANTIC_INTENT_SCHEMA_V1)


SEMANTIC_INTENT_REGISTRY_V1 = {
    "registry_name": "semantic_intent_registry",
    "registry_version": "1.8.1.2_v1",
    "scope": "universal_cross_niche_intent_registry",
    "runtime_effect": "registry_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "registered_intents": {
        "informational": {
            "purpose": "User or content is seeking explanation, education, guidance, or understanding.",
            "universal_examples": [
                "how to automate internal linking",
                "what is semantic SEO",
                "guide to cash flow management",
            ],
        },
        "transactional": {
            "purpose": "User or content is oriented toward purchase, subscription, pricing, signup, or commercial action.",
            "universal_examples": [
                "buy accounting software",
                "pricing for SEO tools",
                "subscribe to project management platform",
            ],
        },
        "preventive": {
            "purpose": "User or content is focused on avoiding harm, reducing risk, preventing problems, or improving safety.",
            "universal_examples": [
                "how to avoid credit card debt",
                "prevent phishing attacks",
                "reduce legal compliance risk",
            ],
        },
        "diagnostic": {
            "purpose": "User or content is trying to identify a problem, cause, symptom, failure, or root issue.",
            "universal_examples": [
                "why website traffic dropped",
                "symptoms of server overload",
                "causes of failed payment processing",
            ],
        },
        "comparison": {
            "purpose": "User or content is evaluating differences, alternatives, tradeoffs, or best-fit options.",
            "universal_examples": [
                "WordPress vs Webflow",
                "LLC vs corporation",
                "best CRM for small business",
            ],
        },
        "mixed": {
            "purpose": "Multiple intent types are present and should be preserved without forcing a single label.",
            "universal_examples": [
                "best software to prevent invoice errors",
                "compare pricing for security tools",
            ],
        },
        "unknown": {
            "purpose": "Intent signal is weak, unclear, or insufficiently evidenced.",
            "universal_examples": [
                "general topic mention without clear purpose",
            ],
        },
    },
    "registry_rules": {
        "universal": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "allows_mixed_intent": True,
        "default_when_unclear": "unknown",
    },
}

def get_semantic_intent_registry_v1() -> Dict[str, Any]:
    return dict(SEMANTIC_INTENT_REGISTRY_V1)


SEMANTIC_INTENT_EVIDENCE_CONTRACT_V1 = {
    "contract_name": "semantic_intent_evidence_contract",
    "contract_version": "1.8.1.3_v1",
    "scope": "universal_cross_niche_intent_evidence",
    "runtime_effect": "evidence_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "required_evidence_fields": [
        "intent_type",
        "intent_confidence",
        "intent_evidence",
        "evidence_sources",
        "evidence_reasoning",
    ],
    "optional_evidence_fields": [
        "secondary_intents",
        "semantic_route_signals",
        "target_transition_signals",
        "comparison_signals",
        "diagnostic_signals",
        "preventive_signals",
        "transactional_signals",
        "informational_signals",
        "notes",
    ],
    "evidence_field_contract": {
        "intent_type": "normalized_primary_intent",
        "intent_confidence": "float_between_0_and_1",
        "intent_evidence": "list_of_human_readable_evidence_strings",
        "evidence_sources": "list_of_source_engines_or_runtime_layers",
        "evidence_reasoning": "human_readable_explanation_of_why_intent_was_detected",
    },
    "design_rules": {
        "human_explainable": True,
        "runtime_safe": True,
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "supports_future_ai_learning": True,
        "supports_owner_console_explainability": True,
    },
}

def get_semantic_intent_evidence_contract_v1() -> Dict[str, Any]:
    return dict(SEMANTIC_INTENT_EVIDENCE_CONTRACT_V1)


def explain_intent_classification_orchestration_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "orchestration_type": "intent_classification_orchestration",
        "layer": "1.8.1_intent_classification_orchestration_v1",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "schema": get_unified_semantic_intent_schema_v1(),
        "registry": get_semantic_intent_registry_v1(),
        "evidence_contract": get_semantic_intent_evidence_contract_v1(),
        "existing_distributed_sources": {
            "phrase_quality_gate": [
                "_intent_lane",
                "_score_after_lane",
                "classify_phrase_strength",
            ],
            "upload_phrase_selector": [
                "_is_intent_phrase",
                "_score_with_strength",
                "_semantic_overlap",
            ],
            "document_registry_pool": [
                "_classify_page_type",
                "_semantic_intent_signals",
            ],
            "target_intelligence": [
                "semantic_intent_score",
                "semantic_route_score",
                "normalized_target_score",
            ],
        },
        "protected_boundaries": {
            "rb2_runtime": "not_modified",
            "engine_run": "not_modified",
            "target_ranking": "not_modified",
            "semantic_route_score": "not_modified",
            "semantic_intent_score": "not_modified",
            "active_phrase_pool": "not_modified",
            "highlight_selection": "not_modified",
            "highlight_density": "not_modified",
        },
        "orchestration_decision": {
            "decision": "govern_existing_distributed_intent_intelligence",
            "reason": "Intent classification already exists across phrase gates, upload selectors, registry pools, and target intelligence. This wrapper centralizes explanation and contracts without changing runtime behavior.",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "runtime_safe": True,
        },
    }


def explain_intent_classification_explainability_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "explainability_type": "intent_classification_explainability",
        "layer": "1.8.1_intent_classification_explainability_v1",
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "uses_existing_layers_only": True,
        "explainability_contract": {
            "answers": [
                "what_intent_was_detected",
                "why_this_intent_was_detected",
                "which_existing_layers_contributed",
                "what_confidence_or_evidence_supported_it",
                "which_runtime_boundaries_were_not_changed",
            ],
            "evidence_model": get_semantic_intent_evidence_contract_v1(),
            "schema_model": get_unified_semantic_intent_schema_v1(),
            "registry_model": get_semantic_intent_registry_v1(),
        },
        "supported_explanations": {
            "intent_type": "Explains the normalized universal intent category.",
            "intent_confidence": "Explains confidence as evidence strength without forcing runtime decisions.",
            "intent_evidence": "Lists human-readable reasons from distributed semantic systems.",
            "evidence_sources": "Shows which existing engines contributed intent signals.",
            "runtime_boundaries": "Confirms no RB2, scoring, ranking, pool, or highlight mutation occurred.",
        },
        "protected_boundaries": {
            "rb2_runtime": "not_modified",
            "engine_run": "not_modified",
            "target_ranking": "not_modified",
            "semantic_scoring": "not_modified",
            "active_phrase_pool": "not_modified",
            "highlight_runtime": "not_modified",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "owner_console_ready": True,
            "api_sdk_ready": True,
        },
    }


INFORMATIONAL_INTENT_SCHEMA_V1 = {
    "schema_name": "informational_intent_schema",
    "schema_version": "1.8.2.1_v1",
    "parent_schema": "unified_semantic_intent_schema",
    "intent_type": "informational",
    "scope": "universal_cross_niche_informational_intelligence",
    "runtime_effect": "schema_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "core_characteristics": {
        "educational": True,
        "guidance_oriented": True,
        "explanatory": True,
        "learning_focused": True,
        "tutorial_capable": True,
    },
    "recognized_patterns": [
        "how to",
        "what is",
        "guide",
        "tutorial",
        "walkthrough",
        "learn",
        "educational",
        "explains",
        "explanation",
    ],
    "existing_runtime_sources": [
        "_extract_intent_candidates",
        "_looks_like_intent_phrase",
        "_is_intent_phrase",
        "_semantic_intent_signals",
        "semantic_intent_score",
        "semantic_route_score",
    ],
    "supported_verticals": {
        "health": True,
        "finance": True,
        "legal": True,
        "technology": True,
        "education": True,
        "ecommerce": True,
        "saas": True,
        "marketing": True,
        "universal": True,
    },
    "design_rules": {
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "runtime_safe": True,
    },
}

def get_informational_intent_schema_v1() -> Dict[str, Any]:
    return dict(INFORMATIONAL_INTENT_SCHEMA_V1)


INFORMATIONAL_INTENT_EVIDENCE_NORMALIZATION_V1 = {
    "normalizer_name": "informational_intent_evidence_normalization",
    "normalizer_version": "1.8.2.2_v1",
    "intent_type": "informational",
    "scope": "universal_cross_niche_informational_evidence",
    "runtime_effect": "normalization_contract_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "normalized_evidence_fields": {
        "intent_type": "informational",
        "intent_confidence": "float_between_0_and_1",
        "intent_evidence": "human_readable_evidence_list",
        "evidence_sources": "distributed_engine_source_list",
        "evidence_reasoning": "why_the_signal_is_informational",
    },
    "accepted_signal_families": {
        "question_patterns": [
            "how to",
            "what is",
            "why does",
            "how does",
        ],
        "education_patterns": [
            "guide",
            "tutorial",
            "walkthrough",
            "learn",
            "educational",
            "explains",
            "explanation",
        ],
        "runtime_sources": [
            "_extract_intent_candidates",
            "_looks_like_intent_phrase",
            "_is_intent_phrase",
            "_semantic_intent_signals",
            "semantic_intent_score",
            "semantic_route_score",
        ],
    },
    "normalization_rules": {
        "primary_intent": "informational",
        "allow_secondary_intents": True,
        "preserve_mixed_intent": True,
        "do_not_override_existing_scores": True,
        "do_not_modify_runtime_ranking": True,
        "do_not_modify_target_selection": True,
    },
    "design_rules": {
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "runtime_safe": True,
    },
}

def get_informational_intent_evidence_normalization_v1() -> Dict[str, Any]:
    return dict(INFORMATIONAL_INTENT_EVIDENCE_NORMALIZATION_V1)


def explain_informational_intent_orchestration_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "orchestration_type": "informational_intent_orchestration",
        "layer": "1.8.2_informational_intent_orchestration_v1",
        "intent_type": "informational",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "schema": get_informational_intent_schema_v1(),
        "evidence_normalization": get_informational_intent_evidence_normalization_v1(),
        "existing_distributed_sources": {
            "smart_phrase_extractor": [
                "_extract_intent_candidates",
                "_score_topic_alignment",
                "_weighted_extractor_score",
            ],
            "phrase_quality_gate": [
                "_intent_lane",
                "_score_after_lane",
                "classify_phrase_strength",
            ],
            "phrase_selectors": [
                "_looks_like_intent_phrase",
                "_is_intent_phrase",
                "_looks_like_question_or_intent",
            ],
            "target_pools": [
                "_classify_page_type",
                "_semantic_intent_signals",
                "_classify_page_type_hint",
            ],
            "target_intelligence": [
                "semantic_intent_score",
                "semantic_route_score",
                "normalized_target_score",
                "transition_score",
            ],
        },
        "orchestration_decision": {
            "decision": "govern_existing_informational_intent_intelligence",
            "reason": "Informational intent signals already exist across extraction, phrase selection, target pools, and target intelligence. This wrapper centralizes explanation and contracts without changing runtime behavior.",
        },
        "protected_boundaries": {
            "rb2_runtime": "not_modified",
            "engine_run": "not_modified",
            "semantic_route_score": "not_modified",
            "semantic_intent_score": "not_modified",
            "target_ranking": "not_modified",
            "target_pools": "not_modified",
            "active_phrase_pool": "not_modified",
            "highlight_runtime": "not_modified",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "runtime_safe": True,
        },
    }


def explain_informational_intent_explainability_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "explainability_type": "informational_intent_explainability",
        "layer": "1.8.2_informational_intent_explainability_v1",
        "intent_type": "informational",
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "uses_existing_layers_only": True,
        "schema": get_informational_intent_schema_v1(),
        "evidence_normalization": get_informational_intent_evidence_normalization_v1(),
        "explains": {
            "what": "Explains when a phrase, page, or target appears educational, explanatory, tutorial-based, or guidance-oriented.",
            "why": "Uses normalized evidence such as how-to patterns, guide/tutorial language, educational signals, and existing semantic route signals.",
            "how": "Reports distributed informational intent sources without changing extraction, scoring, ranking, routing, or highlights.",
        },
        "supported_explanation_fields": {
            "intent_type": "informational",
            "recognized_patterns": [
                "how to",
                "what is",
                "guide",
                "tutorial",
                "walkthrough",
                "learn",
                "educational",
                "explanation",
            ],
            "evidence_sources": [
                "smart_phrase_extractor",
                "phrase_quality_gate",
                "phrase_selectors",
                "target_pools",
                "target_intelligence",
            ],
            "runtime_boundaries": [
                "rb2_runtime_not_modified",
                "engine_run_not_modified",
                "semantic_scoring_not_modified",
                "target_ranking_not_modified",
                "highlight_runtime_not_modified",
            ],
        },
        "owner_console_summary": {
            "ready": True,
            "summary": "Can explain informational intent decisions for future Owner Console, API, SDK, and diagnostics views.",
        },
        "api_sdk_summary": {
            "ready": True,
            "summary": "Can expose normalized informational intent metadata without exposing or changing core scoring logic.",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "runtime_safe": True,
        },
    }


TRANSACTIONAL_INTENT_SCHEMA_V1 = {
    "schema_name": "transactional_intent_schema",
    "schema_version": "1.8.3.1_v1",
    "parent_schema": "unified_semantic_intent_schema",
    "intent_type": "transactional",
    "scope": "universal_cross_niche_transactional_intelligence",
    "runtime_effect": "schema_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "core_characteristics": {
        "commercial_action_oriented": True,
        "pricing_oriented": True,
        "purchase_or_signup_oriented": True,
        "conversion_focused": True,
        "subscription_or_checkout_capable": True,
    },
    "recognized_patterns": [
        "buy",
        "price",
        "pricing",
        "purchase",
        "order",
        "subscribe",
        "subscription",
        "checkout",
        "commercial",
        "conversion",
        "signup",
        "sign up",
    ],
    "existing_runtime_sources": [
        "_extract_intent_candidates",
        "_intent_lane",
        "semantic_intent_score",
        "semantic_route_score",
        "normalized_target_score",
        "transition_score",
        "apply_vertical_policy_score",
    ],
    "supported_verticals": {
        "health": True,
        "finance": True,
        "legal": True,
        "technology": True,
        "education": True,
        "ecommerce": True,
        "saas": True,
        "marketing": True,
        "insurance": True,
        "real_estate": True,
        "universal": True,
    },
    "design_rules": {
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "runtime_safe": True,
    },
}

def get_transactional_intent_schema_v1() -> Dict[str, Any]:
    return dict(TRANSACTIONAL_INTENT_SCHEMA_V1)


TRANSACTIONAL_INTENT_EVIDENCE_NORMALIZATION_V1 = {
    "normalizer_name": "transactional_intent_evidence_normalization",
    "normalizer_version": "1.8.3.2_v1",
    "intent_type": "transactional",
    "scope": "universal_cross_niche_transactional_evidence",
    "runtime_effect": "normalization_contract_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "normalized_evidence_fields": {
        "intent_type": "transactional",
        "intent_confidence": "float_between_0_and_1",
        "intent_evidence": "human_readable_evidence_list",
        "evidence_sources": "distributed_engine_source_list",
        "evidence_reasoning": "why_the_signal_is_transactional",
    },
    "accepted_signal_families": {
        "commercial_action_patterns": [
            "buy",
            "purchase",
            "order",
            "subscribe",
            "signup",
            "sign up",
        ],
        "pricing_patterns": [
            "price",
            "pricing",
            "subscription",
            "checkout",
        ],
        "conversion_patterns": [
            "commercial",
            "conversion",
            "checkout",
        ],
        "runtime_sources": [
            "_extract_intent_candidates",
            "_intent_lane",
            "semantic_intent_score",
            "semantic_route_score",
            "normalized_target_score",
            "transition_score",
            "apply_vertical_policy_score",
        ],
    },
    "normalization_rules": {
        "primary_intent": "transactional",
        "allow_secondary_intents": True,
        "preserve_mixed_intent": True,
        "do_not_override_existing_scores": True,
        "do_not_modify_runtime_ranking": True,
        "do_not_modify_target_selection": True,
        "do_not_modify_conversion_logic": True,
    },
    "design_rules": {
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "runtime_safe": True,
    },
}

def get_transactional_intent_evidence_normalization_v1() -> Dict[str, Any]:
    return dict(TRANSACTIONAL_INTENT_EVIDENCE_NORMALIZATION_V1)


def explain_transactional_intent_orchestration_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "orchestration_type": "transactional_intent_orchestration",
        "layer": "1.8.3_transactional_intent_orchestration_v1",
        "intent_type": "transactional",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "schema": get_transactional_intent_schema_v1(),
        "evidence_normalization": get_transactional_intent_evidence_normalization_v1(),
        "existing_distributed_sources": {
            "smart_phrase_extractor": [
                "_extract_intent_candidates",
                "_weighted_extractor_score",
                "_score_topic_alignment",
            ],
            "phrase_quality_gate": [
                "_intent_lane",
                "_score_after_lane",
                "classify_phrase_strength",
            ],
            "phrase_vertical_policy": [
                "apply_vertical_policy_score",
                "get_vertical_min_score",
            ],
            "target_pools": [
                "_classify_page_type",
                "_semantic_intent_signals",
                "_classify_page_type_hint",
            ],
            "target_intelligence": [
                "semantic_intent_score",
                "semantic_route_score",
                "normalized_target_score",
                "transition_score",
            ],
        },
        "orchestration_decision": {
            "decision": "govern_existing_transactional_intent_intelligence",
            "reason": "Transactional intent signals already exist across phrase extraction, phrase gates, vertical policy, target pools, and target intelligence. This wrapper centralizes explanation and contracts without changing runtime behavior.",
        },
        "protected_boundaries": {
            "rb2_runtime": "not_modified",
            "engine_run": "not_modified",
            "semantic_route_score": "not_modified",
            "semantic_intent_score": "not_modified",
            "target_ranking": "not_modified",
            "target_pools": "not_modified",
            "conversion_logic": "not_modified",
            "active_phrase_pool": "not_modified",
            "highlight_runtime": "not_modified",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "runtime_safe": True,
        },
    }


def explain_transactional_intent_explainability_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "explainability_type": "transactional_intent_explainability",
        "layer": "1.8.3_transactional_intent_explainability_v1",
        "intent_type": "transactional",
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "uses_existing_layers_only": True,
        "schema": get_transactional_intent_schema_v1(),
        "evidence_normalization": get_transactional_intent_evidence_normalization_v1(),
        "explains": {
            "what": "Explains when a phrase, page, or target appears commercial, pricing-oriented, purchase-oriented, signup-oriented, subscription-oriented, or conversion-focused.",
            "why": "Uses normalized evidence such as buy, price, pricing, subscription, checkout, commercial, conversion, signup, and existing semantic route signals.",
            "how": "Reports distributed transactional intent sources without changing extraction, scoring, ranking, conversion logic, routing, or highlights.",
        },
        "supported_explanation_fields": {
            "intent_type": "transactional",
            "recognized_patterns": [
                "buy",
                "price",
                "pricing",
                "purchase",
                "order",
                "subscribe",
                "subscription",
                "checkout",
                "commercial",
                "conversion",
                "signup",
                "sign up",
            ],
            "evidence_sources": [
                "smart_phrase_extractor",
                "phrase_quality_gate",
                "phrase_vertical_policy",
                "target_pools",
                "target_intelligence",
            ],
            "runtime_boundaries": [
                "rb2_runtime_not_modified",
                "engine_run_not_modified",
                "semantic_scoring_not_modified",
                "target_ranking_not_modified",
                "conversion_logic_not_modified",
                "target_pools_not_modified",
                "highlight_runtime_not_modified",
            ],
        },
        "owner_console_summary": {
            "ready": True,
            "summary": "Can explain transactional/commercial intent decisions for future Owner Console, API, SDK, and diagnostics views.",
        },
        "api_sdk_summary": {
            "ready": True,
            "summary": "Can expose normalized transactional intent metadata without exposing or changing core scoring, ranking, or conversion logic.",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "runtime_safe": True,
        },
    }


PREVENTIVE_INTENT_SCHEMA_V1 = {
    "schema_name": "preventive_intent_schema",
    "schema_version": "1.8.4.1_v1",
    "parent_schema": "unified_semantic_intent_schema",
    "intent_type": "preventive",
    "scope": "universal_cross_niche_preventive_intelligence",
    "runtime_effect": "schema_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "core_characteristics": {
        "risk_reduction_oriented": True,
        "warning_oriented": True,
        "protection_oriented": True,
        "safety_oriented": True,
        "mitigation_capable": True,
    },
    "recognized_patterns": [
        "prevent",
        "avoid",
        "risk",
        "reduce risk",
        "warning",
        "protect",
        "safe",
        "safety",
        "mitigate",
        "mitigation",
        "reduce",
        "stop",
    ],
    "existing_runtime_sources": [
        "_extract_intent_candidates",
        "_intent_lane",
        "semantic_intent_score",
        "semantic_route_score",
        "normalized_target_score",
        "transition_score",
        "link_worthiness_score",
    ],
    "supported_verticals": {
        "health": True,
        "finance": True,
        "legal": True,
        "technology": True,
        "education": True,
        "ecommerce": True,
        "saas": True,
        "marketing": True,
        "security": True,
        "compliance": True,
        "universal": True,
    },
    "design_rules": {
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "runtime_safe": True,
    },
}

def get_preventive_intent_schema_v1() -> Dict[str, Any]:
    return dict(PREVENTIVE_INTENT_SCHEMA_V1)


PREVENTIVE_INTENT_EVIDENCE_NORMALIZATION_V1 = {
    "normalizer_name": "preventive_intent_evidence_normalization",
    "normalizer_version": "1.8.4.2_v1",
    "intent_type": "preventive",
    "scope": "universal_cross_niche_preventive_evidence",
    "runtime_effect": "normalization_contract_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "normalized_evidence_fields": {
        "intent_type": "preventive",
        "intent_confidence": "float_between_0_and_1",
        "intent_evidence": "human_readable_evidence_list",
        "evidence_sources": "distributed_engine_source_list",
        "evidence_reasoning": "why_the_signal_is_preventive",
    },
    "accepted_signal_families": {
        "risk_reduction_patterns": [
            "prevent",
            "avoid",
            "risk",
            "reduce risk",
            "reduce",
        ],
        "protection_patterns": [
            "protect",
            "safe",
            "safety",
            "warning",
        ],
        "mitigation_patterns": [
            "mitigate",
            "mitigation",
            "stop",
        ],
        "runtime_sources": [
            "_extract_intent_candidates",
            "_intent_lane",
            "semantic_intent_score",
            "semantic_route_score",
            "normalized_target_score",
            "transition_score",
            "link_worthiness_score",
        ],
    },
    "normalization_rules": {
        "primary_intent": "preventive",
        "allow_secondary_intents": True,
        "preserve_mixed_intent": True,
        "do_not_override_existing_scores": True,
        "do_not_modify_runtime_ranking": True,
        "do_not_modify_target_selection": True,
        "do_not_modify_safety_logic": True,
    },
    "design_rules": {
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "runtime_safe": True,
    },
}

def get_preventive_intent_evidence_normalization_v1() -> Dict[str, Any]:
    return dict(PREVENTIVE_INTENT_EVIDENCE_NORMALIZATION_V1)


def explain_preventive_intent_orchestration_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "orchestration_type": "preventive_intent_orchestration",
        "layer": "1.8.4_preventive_intent_orchestration_v1",
        "intent_type": "preventive",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "schema": get_preventive_intent_schema_v1(),
        "evidence_normalization": get_preventive_intent_evidence_normalization_v1(),
        "existing_distributed_sources": {
            "smart_phrase_extractor": [
                "_extract_intent_candidates",
                "_weighted_extractor_score",
                "_score_topic_alignment",
            ],
            "phrase_quality_gate": [
                "_intent_lane",
                "_score_after_lane",
                "classify_phrase_strength",
            ],
            "phrase_strength_scorer": [
                "score_phrase_strength",
                "_universal_precision_score",
                "_domain_cohesion_score",
            ],
            "target_pools": [
                "_classify_page_type",
                "_semantic_intent_signals",
                "_classify_page_type_hint",
            ],
            "target_intelligence": [
                "semantic_intent_score",
                "semantic_route_score",
                "normalized_target_score",
                "transition_score",
            ],
            "highlight_intelligence": [
                "link_worthiness_score",
                "contextual_naturalness_score",
            ],
        },
        "orchestration_decision": {
            "decision": "govern_existing_preventive_intent_intelligence",
            "reason": "Preventive intent signals already exist across phrase extraction, phrase gates, phrase scoring, target pools, target intelligence, and highlight intelligence. This wrapper centralizes explanation and contracts without changing runtime behavior.",
        },
        "protected_boundaries": {
            "rb2_runtime": "not_modified",
            "engine_run": "not_modified",
            "semantic_route_score": "not_modified",
            "semantic_intent_score": "not_modified",
            "target_ranking": "not_modified",
            "target_pools": "not_modified",
            "safety_logic": "not_modified",
            "active_phrase_pool": "not_modified",
            "highlight_runtime": "not_modified",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "runtime_safe": True,
        },
    }


def explain_preventive_intent_explainability_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "explainability_type": "preventive_intent_explainability",
        "layer": "1.8.4_preventive_intent_explainability_v1",
        "intent_type": "preventive",
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "uses_existing_layers_only": True,
        "schema": get_preventive_intent_schema_v1(),
        "evidence_normalization": get_preventive_intent_evidence_normalization_v1(),
        "explains": {
            "what": "Explains when a phrase, page, or target appears risk-reduction, warning, protection, safety, or mitigation oriented.",
            "why": "Uses normalized evidence such as prevent, avoid, risk, warning, protect, safety, mitigation, reduce, stop, and existing semantic route signals.",
            "how": "Reports distributed preventive intent sources without changing extraction, scoring, ranking, safety logic, routing, or highlights.",
        },
        "supported_explanation_fields": {
            "intent_type": "preventive",
            "recognized_patterns": [
                "prevent",
                "avoid",
                "risk",
                "reduce risk",
                "warning",
                "protect",
                "safe",
                "safety",
                "mitigate",
                "mitigation",
                "reduce",
                "stop",
            ],
            "evidence_sources": [
                "smart_phrase_extractor",
                "phrase_quality_gate",
                "phrase_strength_scorer",
                "target_pools",
                "target_intelligence",
                "highlight_intelligence",
            ],
            "runtime_boundaries": [
                "rb2_runtime_not_modified",
                "engine_run_not_modified",
                "semantic_scoring_not_modified",
                "target_ranking_not_modified",
                "safety_logic_not_modified",
                "target_pools_not_modified",
                "highlight_runtime_not_modified",
            ],
        },
        "owner_console_summary": {
            "ready": True,
            "summary": "Can explain preventive/risk-reduction intent decisions for future Owner Console, API, SDK, and diagnostics views.",
        },
        "api_sdk_summary": {
            "ready": True,
            "summary": "Can expose normalized preventive intent metadata without exposing or changing core scoring, ranking, routing, or safety logic.",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "runtime_safe": True,
        },
    }


DIAGNOSTIC_INTENT_SCHEMA_V1 = {
    "schema_name": "diagnostic_intent_schema",
    "schema_version": "1.8.5.1_v1",
    "parent_schema": "unified_semantic_intent_schema",
    "intent_type": "diagnostic",
    "scope": "universal_cross_niche_diagnostic_intelligence",
    "runtime_effect": "schema_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "core_characteristics": {
        "problem_identification_oriented": True,
        "cause_analysis_oriented": True,
        "symptom_or_issue_oriented": True,
        "troubleshooting_capable": True,
        "failure_analysis_capable": True,
    },
    "recognized_patterns": [
        "diagnostic",
        "diagnose",
        "diagnosis",
        "symptom",
        "symptoms",
        "cause",
        "causes",
        "why",
        "problem",
        "issue",
        "error",
        "troubleshoot",
        "troubleshooting",
        "root cause",
        "check",
        "failure",
        "failed",
    ],
    "existing_runtime_sources": [
        "_extract_intent_candidates",
        "_looks_like_intent_phrase",
        "_is_intent_phrase",
        "_intent_lane",
        "semantic_intent_score",
        "semantic_route_score",
        "normalized_target_score",
        "transition_score",
        "diagnostics_for_document_registry_targets",
    ],
    "supported_verticals": {
        "health": True,
        "finance": True,
        "legal": True,
        "technology": True,
        "education": True,
        "ecommerce": True,
        "saas": True,
        "marketing": True,
        "security": True,
        "compliance": True,
        "software_debugging": True,
        "universal": True,
    },
    "design_rules": {
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "runtime_safe": True,
    },
}

def get_diagnostic_intent_schema_v1() -> Dict[str, Any]:
    return dict(DIAGNOSTIC_INTENT_SCHEMA_V1)


DIAGNOSTIC_INTENT_EVIDENCE_NORMALIZATION_V1 = {
    "normalizer_name": "diagnostic_intent_evidence_normalization",
    "normalizer_version": "1.8.5.2_v1",
    "intent_type": "diagnostic",
    "scope": "universal_cross_niche_diagnostic_evidence",
    "runtime_effect": "normalization_contract_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "normalized_evidence_fields": {
        "intent_type": "diagnostic",
        "intent_confidence": "float_between_0_and_1",
        "intent_evidence": "human_readable_evidence_list",
        "evidence_sources": "distributed_engine_source_list",
        "evidence_reasoning": "why_the_signal_is_diagnostic",
    },
    "accepted_signal_families": {
        "problem_identification_patterns": [
            "problem",
            "issue",
            "check",
            "why",
        ],
        "cause_analysis_patterns": [
            "cause",
            "causes",
            "root cause",
        ],
        "symptom_diagnosis_patterns": [
            "diagnostic",
            "diagnose",
            "diagnosis",
            "symptom",
            "symptoms",
        ],
        "troubleshooting_patterns": [
            "error",
            "troubleshoot",
            "troubleshooting",
            "failure",
            "failed",
        ],
        "runtime_sources": [
            "_extract_intent_candidates",
            "_looks_like_intent_phrase",
            "_is_intent_phrase",
            "_intent_lane",
            "semantic_intent_score",
            "semantic_route_score",
            "normalized_target_score",
            "transition_score",
            "diagnostics_for_document_registry_targets",
        ],
    },
    "normalization_rules": {
        "primary_intent": "diagnostic",
        "allow_secondary_intents": True,
        "preserve_mixed_intent": True,
        "do_not_override_existing_scores": True,
        "do_not_modify_runtime_ranking": True,
        "do_not_modify_target_selection": True,
        "do_not_modify_diagnostic_logic": True,
        "do_not_modify_dis_learning": True,
    },
    "design_rules": {
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "runtime_safe": True,
    },
}

def get_diagnostic_intent_evidence_normalization_v1() -> Dict[str, Any]:
    return dict(DIAGNOSTIC_INTENT_EVIDENCE_NORMALIZATION_V1)


def explain_diagnostic_intent_orchestration_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "orchestration_type": "diagnostic_intent_orchestration",
        "layer": "1.8.5_diagnostic_intent_orchestration_v1",
        "intent_type": "diagnostic",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "schema": get_diagnostic_intent_schema_v1(),
        "evidence_normalization": get_diagnostic_intent_evidence_normalization_v1(),
        "existing_distributed_sources": {
            "smart_phrase_extractor": [
                "_extract_intent_candidates",
                "_weighted_extractor_score",
                "_score_topic_alignment",
            ],
            "phrase_quality_gate": [
                "_intent_lane",
                "_score_after_lane",
                "classify_phrase_strength",
            ],
            "phrase_strength_scorer": [
                "score_phrase_strength",
                "_universal_precision_score",
                "_domain_cohesion_score",
            ],
            "phrase_selectors": [
                "_looks_like_intent_phrase",
                "_is_intent_phrase",
                "_looks_like_question_or_intent",
            ],
            "target_pools": [
                "_classify_page_type",
                "_semantic_intent_signals",
                "_classify_page_type_hint",
            ],
            "target_intelligence": [
                "semantic_intent_score",
                "semantic_route_score",
                "normalized_target_score",
                "transition_score",
                "diagnostics_for_document_registry_targets",
            ],
            "dis_learning": [
                "_infer_failure_category",
                "rejection_signatures",
                "pipeline_failure_patterns",
            ],
        },
        "orchestration_decision": {
            "decision": "govern_existing_diagnostic_intent_intelligence",
            "reason": "Diagnostic intent signals already exist across phrase extraction, phrase gates, phrase scoring, phrase selectors, target pools, target intelligence, and DIS learning. This wrapper centralizes explanation and contracts without changing runtime behavior.",
        },
        "protected_boundaries": {
            "rb2_runtime": "not_modified",
            "engine_run": "not_modified",
            "semantic_route_score": "not_modified",
            "semantic_intent_score": "not_modified",
            "target_ranking": "not_modified",
            "target_pools": "not_modified",
            "diagnostic_logic": "not_modified",
            "dis_learning": "not_modified",
            "active_phrase_pool": "not_modified",
            "highlight_runtime": "not_modified",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "runtime_safe": True,
        },
    }


def explain_diagnostic_intent_explainability_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "explainability_type": "diagnostic_intent_explainability",
        "layer": "1.8.5_diagnostic_intent_explainability_v1",
        "intent_type": "diagnostic",
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "uses_existing_layers_only": True,
        "schema": get_diagnostic_intent_schema_v1(),
        "evidence_normalization": get_diagnostic_intent_evidence_normalization_v1(),
        "explains": {
            "what": "Explains when a phrase, page, or target appears problem-identification, cause-analysis, symptom/diagnosis, troubleshooting, or failure-analysis oriented.",
            "why": "Uses normalized evidence such as diagnostic, diagnose, symptom, cause, why, problem, issue, error, troubleshooting, root cause, failure, and existing semantic route signals.",
            "how": "Reports distributed diagnostic intent sources without changing extraction, scoring, ranking, diagnostic logic, DIS learning, routing, or highlights.",
        },
        "supported_explanation_fields": {
            "intent_type": "diagnostic",
            "recognized_patterns": [
                "diagnostic",
                "diagnose",
                "diagnosis",
                "symptom",
                "symptoms",
                "cause",
                "causes",
                "why",
                "problem",
                "issue",
                "error",
                "troubleshoot",
                "troubleshooting",
                "root cause",
                "check",
                "failure",
                "failed",
            ],
            "evidence_sources": [
                "smart_phrase_extractor",
                "phrase_quality_gate",
                "phrase_strength_scorer",
                "phrase_selectors",
                "target_pools",
                "target_intelligence",
                "dis_learning",
            ],
            "runtime_boundaries": [
                "rb2_runtime_not_modified",
                "engine_run_not_modified",
                "semantic_scoring_not_modified",
                "target_ranking_not_modified",
                "diagnostic_logic_not_modified",
                "dis_learning_not_modified",
                "target_pools_not_modified",
                "highlight_runtime_not_modified",
            ],
        },
        "owner_console_summary": {
            "ready": True,
            "summary": "Can explain diagnostic/problem-analysis intent decisions for future Owner Console, API, SDK, diagnostics, and support intelligence views.",
        },
        "api_sdk_summary": {
            "ready": True,
            "summary": "Can expose normalized diagnostic intent metadata without exposing or changing core scoring, ranking, routing, diagnostic logic, or DIS learning.",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "runtime_safe": True,
        },
    }


COMPARISON_INTENT_SCHEMA_V1 = {
    "schema_name": "comparison_intent_schema",
    "schema_version": "1.8.6.1_v1",
    "parent_schema": "unified_semantic_intent_schema",
    "intent_type": "comparison",
    "scope": "universal_cross_niche_comparison_intelligence",
    "runtime_effect": "schema_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "core_characteristics": {
        "alternative_evaluation_oriented": True,
        "difference_analysis_oriented": True,
        "versus_oriented": True,
        "best_fit_oriented": True,
        "tradeoff_analysis_capable": True,
    },
    "recognized_patterns": [
        "comparison",
        "compare",
        "versus",
        "vs",
        "difference",
        "differences",
        "alternative",
        "alternatives",
        "better than",
        "best",
        "pros",
        "cons",
        "tradeoff",
        "trade-off",
        "which is better",
    ],
    "existing_runtime_sources": [
        "_extract_intent_candidates",
        "_looks_like_intent_phrase",
        "_is_intent_phrase",
        "_intent_lane",
        "semantic_intent_score",
        "semantic_route_score",
        "normalized_target_score",
        "publish_transition_score",
        "rank_draft_targets",
        "best_draft_target",
    ],
    "supported_verticals": {
        "health": True,
        "finance": True,
        "legal": True,
        "technology": True,
        "education": True,
        "ecommerce": True,
        "saas": True,
        "marketing": True,
        "security": True,
        "software": True,
        "real_estate": True,
        "universal": True,
    },
    "design_rules": {
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "runtime_safe": True,
    },
}

def get_comparison_intent_schema_v1() -> Dict[str, Any]:
    return dict(COMPARISON_INTENT_SCHEMA_V1)


COMPARISON_INTENT_EVIDENCE_NORMALIZATION_V1 = {
    "normalizer_name": "comparison_intent_evidence_normalization",
    "normalizer_version": "1.8.6.2_v1",
    "intent_type": "comparison",
    "scope": "universal_cross_niche_comparison_evidence",
    "runtime_effect": "normalization_contract_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "normalized_evidence_fields": {
        "intent_type": "comparison",
        "intent_confidence": "float_between_0_and_1",
        "intent_evidence": "human_readable_evidence_list",
        "evidence_sources": "distributed_engine_source_list",
        "evidence_reasoning": "why_the_signal_is_comparison_oriented",
    },
    "accepted_signal_families": {
        "direct_comparison_patterns": [
            "comparison",
            "compare",
            "versus",
            "vs",
            "which is better",
        ],
        "difference_patterns": [
            "difference",
            "differences",
            "better than",
        ],
        "alternative_evaluation_patterns": [
            "alternative",
            "alternatives",
            "best",
            "pros",
            "cons",
            "tradeoff",
            "trade-off",
        ],
        "runtime_sources": [
            "_extract_intent_candidates",
            "_looks_like_intent_phrase",
            "_is_intent_phrase",
            "_intent_lane",
            "semantic_intent_score",
            "semantic_route_score",
            "normalized_target_score",
            "publish_transition_score",
            "rank_draft_targets",
            "best_draft_target",
        ],
    },
    "normalization_rules": {
        "primary_intent": "comparison",
        "allow_secondary_intents": True,
        "preserve_mixed_intent": True,
        "do_not_override_existing_scores": True,
        "do_not_modify_runtime_ranking": True,
        "do_not_modify_target_selection": True,
        "do_not_modify_comparison_logic": True,
    },
    "design_rules": {
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "runtime_safe": True,
    },
}

def get_comparison_intent_evidence_normalization_v1() -> Dict[str, Any]:
    return dict(COMPARISON_INTENT_EVIDENCE_NORMALIZATION_V1)


def explain_comparison_intent_orchestration_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "orchestration_type": "comparison_intent_orchestration",
        "layer": "1.8.6_comparison_intent_orchestration_v1",
        "intent_type": "comparison",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "schema": get_comparison_intent_schema_v1(),
        "evidence_normalization": get_comparison_intent_evidence_normalization_v1(),
        "existing_distributed_sources": {
            "smart_phrase_extractor": [
                "_extract_intent_candidates",
                "_weighted_extractor_score",
                "_score_topic_alignment",
            ],
            "phrase_quality_gate": [
                "_intent_lane",
                "_score_after_lane",
                "classify_phrase_strength",
            ],
            "phrase_strength_scorer": [
                "score_phrase_strength",
                "_universal_precision_score",
                "_domain_cohesion_score",
            ],
            "phrase_selectors": [
                "_looks_like_intent_phrase",
                "_is_intent_phrase",
                "_looks_like_question_or_intent",
            ],
            "target_pools": [
                "_classify_page_type",
                "_semantic_intent_signals",
                "_classify_page_type_hint",
                "_apply_strong_intent_balance",
            ],
            "target_intelligence": [
                "semantic_intent_score",
                "semantic_route_score",
                "normalized_target_score",
                "publish_transition_score",
                "rank_draft_targets",
                "best_draft_target",
            ],
            "runtime_ui": [
                "engine_scoring",
                "context_hooks",
                "il_modal",
                "engine_highlights",
            ],
        },
        "orchestration_decision": {
            "decision": "govern_existing_comparison_intent_intelligence",
            "reason": "Comparison intent signals already exist across phrase extraction, phrase gates, phrase scoring, phrase selectors, target pools, target intelligence, and runtime UI systems. This wrapper centralizes explanation and contracts without changing runtime behavior.",
        },
        "protected_boundaries": {
            "rb2_runtime": "not_modified",
            "engine_run": "not_modified",
            "semantic_route_score": "not_modified",
            "semantic_intent_score": "not_modified",
            "target_ranking": "not_modified",
            "target_pools": "not_modified",
            "comparison_logic": "not_modified",
            "runtime_ui": "not_modified",
            "active_phrase_pool": "not_modified",
            "highlight_runtime": "not_modified",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "runtime_safe": True,
        },
    }


def explain_comparison_intent_explainability_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "explainability_type": "comparison_intent_explainability",
        "layer": "1.8.6_comparison_intent_explainability_v1",
        "intent_type": "comparison",
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "uses_existing_layers_only": True,
        "schema": get_comparison_intent_schema_v1(),
        "evidence_normalization": get_comparison_intent_evidence_normalization_v1(),
        "explains": {
            "what": "Explains when a phrase, page, or target appears comparison, alternative-evaluation, difference-analysis, versus, best-fit, or tradeoff oriented.",
            "why": "Uses normalized evidence such as compare, comparison, versus, vs, difference, alternatives, best, pros, cons, tradeoff, and existing semantic route signals.",
            "how": "Reports distributed comparison intent sources without changing extraction, scoring, ranking, comparison logic, runtime UI, routing, or highlights.",
        },
        "supported_explanation_fields": {
            "intent_type": "comparison",
            "recognized_patterns": [
                "comparison",
                "compare",
                "versus",
                "vs",
                "difference",
                "differences",
                "alternative",
                "alternatives",
                "better than",
                "best",
                "pros",
                "cons",
                "tradeoff",
                "trade-off",
                "which is better",
            ],
            "evidence_sources": [
                "smart_phrase_extractor",
                "phrase_quality_gate",
                "phrase_strength_scorer",
                "phrase_selectors",
                "target_pools",
                "target_intelligence",
                "runtime_ui",
            ],
            "runtime_boundaries": [
                "rb2_runtime_not_modified",
                "engine_run_not_modified",
                "semantic_scoring_not_modified",
                "target_ranking_not_modified",
                "comparison_logic_not_modified",
                "runtime_ui_not_modified",
                "target_pools_not_modified",
                "highlight_runtime_not_modified",
            ],
        },
        "owner_console_summary": {
            "ready": True,
            "summary": "Can explain comparison/alternative-evaluation intent decisions for future Owner Console, API, SDK, diagnostics, and target-intelligence views.",
        },
        "api_sdk_summary": {
            "ready": True,
            "summary": "Can expose normalized comparison intent metadata without exposing or changing core scoring, ranking, routing, comparison logic, or runtime UI behavior.",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "runtime_safe": True,
        },
    }


INTENT_AWARE_LINKING_SCHEMA_V1 = {
    "schema_name": "intent_aware_linking_schema",
    "schema_version": "1.8.7.1_v1",
    "parent_schema": "unified_semantic_intent_schema",
    "scope": "universal_cross_niche_intent_aware_linking_governance",
    "runtime_effect": "schema_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "purpose": "Govern how existing intent signals support link selection, target ranking, semantic routing, and highlight naturalness without changing runtime behavior.",
    "core_linking_signals": {
        "semantic_intent_score": "existing_target_intelligence_signal",
        "semantic_route_score": "existing_target_routing_signal",
        "normalized_target_score": "existing_target_ranking_signal",
        "transition_score": "existing_context_transition_signal",
        "link_worthiness_score": "existing_highlight_selection_signal",
        "contextual_naturalness_score": "existing_highlight_naturalness_signal",
    },
    "supported_intent_types": [
        "informational",
        "transactional",
        "preventive",
        "diagnostic",
        "comparison",
        "mixed",
        "unknown",
    ],
    "existing_runtime_sources": [
        "resolve_intelligent_targets",
        "_runtime_normalized_score",
        "_runtime_semantic_dominance_ok",
        "_filter_and_balance_runtime_targets",
        "rank_document_registry_targets",
        "rank_draft_targets",
        "rank_live_domain_targets",
        "rank_imported_targets",
        "best_draft_target",
        "best_live_domain_target",
        "best_imported_target",
        "link_worthiness_score",
        "contextual_naturalness_score",
    ],
    "protected_runtime_boundaries": {
        "rb2_runtime": "not_modified",
        "engine_run": "not_modified",
        "semantic_scoring": "not_modified",
        "target_ranking": "not_modified",
        "target_intelligence": "not_modified",
        "runtime_balancing": "not_modified",
        "highlight_runtime": "not_modified",
        "active_phrase_pool": "not_modified",
    },
    "design_rules": {
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "runtime_safe": True,
        "schema_only": True,
    },
}

def get_intent_aware_linking_schema_v1() -> Dict[str, Any]:
    return dict(INTENT_AWARE_LINKING_SCHEMA_V1)


INTENT_AWARE_LINKING_EVIDENCE_NORMALIZATION_V1 = {
    "normalizer_name": "intent_aware_linking_evidence_normalization",
    "normalizer_version": "1.8.7.2_v1",
    "scope": "universal_cross_niche_intent_aware_linking_evidence",
    "runtime_effect": "normalization_contract_only_no_runtime_injection",
    "mutates_existing_intelligence": False,
    "normalized_evidence_fields": {
        "intent_type": "normalized_primary_or_mixed_intent",
        "linking_confidence": "float_between_0_and_1",
        "linking_evidence": "human_readable_evidence_list",
        "target_evidence_sources": "distributed_target_engine_source_list",
        "linking_reasoning": "why_the_linking_signal_supports_this_target_or_anchor",
    },
    "accepted_signal_families": {
        "target_intent_signals": [
            "semantic_intent_score",
            "semantic_route_score",
            "normalized_target_score",
            "transition_score",
        ],
        "highlight_linking_signals": [
            "link_worthiness_score",
            "contextual_naturalness_score",
        ],
        "runtime_resolution_signals": [
            "resolve_intelligent_targets",
            "_runtime_normalized_score",
            "_runtime_semantic_dominance_ok",
            "_filter_and_balance_runtime_targets",
        ],
        "target_ranking_sources": [
            "rank_document_registry_targets",
            "rank_draft_targets",
            "rank_live_domain_targets",
            "rank_imported_targets",
            "best_draft_target",
            "best_live_domain_target",
            "best_imported_target",
        ],
    },
    "normalization_rules": {
        "preserve_existing_runtime_scores": True,
        "do_not_override_target_ranking": True,
        "do_not_modify_semantic_route_score": True,
        "do_not_modify_semantic_intent_score": True,
        "do_not_modify_runtime_balancing": True,
        "do_not_modify_highlight_selection": True,
        "do_not_modify_rb2_runtime": True,
    },
    "design_rules": {
        "cross_niche": True,
        "vertical_aware": True,
        "health_specific": False,
        "hardcoded_industry_logic": False,
        "runtime_safe": True,
    },
}

def get_intent_aware_linking_evidence_normalization_v1() -> Dict[str, Any]:
    return dict(INTENT_AWARE_LINKING_EVIDENCE_NORMALIZATION_V1)


def explain_intent_aware_linking_orchestration_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "orchestration_type": "intent_aware_linking_orchestration",
        "layer": "1.8.7_intent_aware_linking_orchestration_v1",
        "uses_existing_layers_only": True,
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "schema": get_intent_aware_linking_schema_v1(),
        "evidence_normalization": get_intent_aware_linking_evidence_normalization_v1(),
        "existing_distributed_sources": {
            "target_resolution": [
                "resolve_intelligent_targets",
                "_runtime_normalized_score",
                "_runtime_semantic_dominance_ok",
                "_filter_and_balance_runtime_targets",
            ],
            "target_intelligence": [
                "semantic_intent_score",
                "semantic_route_score",
                "normalized_target_score",
                "transition_score",
                "rank_document_registry_targets",
                "rank_draft_targets",
                "rank_live_domain_targets",
                "rank_imported_targets",
            ],
            "best_target_selection": [
                "best_draft_target",
                "best_live_domain_target",
                "best_imported_target",
            ],
            "highlight_intelligence": [
                "link_worthiness_score",
                "contextual_naturalness_score",
                "score_link_opportunity",
            ],
            "semantic_scoring": [
                "semantic_similarity_score",
                "ontology_alignment_score",
                "context_score",
                "graph_score",
                "compute_semantic_score",
            ],
        },
        "orchestration_decision": {
            "decision": "govern_existing_intent_aware_linking_intelligence",
            "reason": "Intent-aware linking already exists across target resolution, target intelligence, semantic scoring, best-target selection, and highlight intelligence. This wrapper centralizes governance and explanation without changing runtime behavior.",
        },
        "protected_boundaries": {
            "rb2_runtime": "not_modified",
            "engine_run": "not_modified",
            "semantic_scoring": "not_modified",
            "target_ranking": "not_modified",
            "target_intelligence": "not_modified",
            "target_selection": "not_modified",
            "runtime_balancing": "not_modified",
            "active_phrase_pool": "not_modified",
            "highlight_runtime": "not_modified",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "runtime_safe": True,
        },
    }


def explain_intent_aware_linking_explainability_v1(
    workspace_id: str,
) -> Dict[str, Any]:

    return {
        "workspace_id": workspace_id,
        "generated_at": _now_iso(),
        "explainability_type": "intent_aware_linking_explainability",
        "layer": "1.8.7_intent_aware_linking_explainability_v1",
        "runtime_effect": "read_only_no_runtime_injection",
        "mutates_existing_intelligence": False,
        "uses_existing_layers_only": True,
        "schema": get_intent_aware_linking_schema_v1(),
        "evidence_normalization": get_intent_aware_linking_evidence_normalization_v1(),
        "explains": {
            "what": "Explains how existing intent signals support link selection, target ranking, semantic routing, best-target selection, and highlight naturalness.",
            "why": "Uses normalized evidence from semantic intent score, semantic route score, normalized target score, transition score, link worthiness score, contextual naturalness score, and runtime target resolution signals.",
            "how": "Reports distributed intent-aware linking sources without changing semantic scoring, target ranking, runtime balancing, target intelligence, RB2 runtime, or highlights.",
        },
        "supported_explanation_fields": {
            "linking_signals": [
                "semantic_intent_score",
                "semantic_route_score",
                "normalized_target_score",
                "transition_score",
                "link_worthiness_score",
                "contextual_naturalness_score",
            ],
            "evidence_sources": [
                "target_resolution",
                "target_intelligence",
                "best_target_selection",
                "highlight_intelligence",
                "semantic_scoring",
            ],
            "runtime_boundaries": [
                "rb2_runtime_not_modified",
                "engine_run_not_modified",
                "semantic_scoring_not_modified",
                "target_ranking_not_modified",
                "target_intelligence_not_modified",
                "target_selection_not_modified",
                "runtime_balancing_not_modified",
                "active_phrase_pool_not_modified",
                "highlight_runtime_not_modified",
            ],
        },
        "owner_console_summary": {
            "ready": True,
            "summary": "Can explain intent-aware linking decisions for future Owner Console, target diagnostics, route diagnostics, API, SDK, and audit views.",
        },
        "api_sdk_summary": {
            "ready": True,
            "summary": "Can expose normalized intent-aware linking metadata without exposing or changing core scoring, ranking, routing, target intelligence, or runtime balancing logic.",
        },
        "universal_design_rules": {
            "cross_niche": True,
            "vertical_aware": True,
            "health_specific": False,
            "hardcoded_industry_logic": False,
            "runtime_safe": True,
        },
    }

