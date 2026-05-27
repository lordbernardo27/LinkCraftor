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

