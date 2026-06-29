"""
Semantic Concept Normalizer

Phase 4.6.5B responsibility:
- Convert raw semantic terms into canonical concepts.
- Merge aliases, plurals, acronyms, and multi-word concept variants.
- Provide reusable concept IDs for downstream semantic graph engines.
"""


from __future__ import annotations

SOURCE_KIND_REGISTRY = {
    "uploaded_docx": {
        "weight": 1.00,
        "trusted": True,
        "editable": False,
    },
    "uploaded_pdf": {
        "weight": 0.95,
        "trusted": True,
        "editable": False,
    },
    "html_import": {
        "weight": 0.90,
        "trusted": True,
        "editable": True,
    },
    "markdown_import": {
        "weight": 0.90,
        "trusted": True,
        "editable": True,
    },
    "crawled_page": {
        "weight": 0.85,
        "trusted": False,
        "editable": True,
    },
    "wordpress": {
        "weight": 0.88,
        "trusted": False,
        "editable": True,
    },
    "google_docs": {
        "weight": 0.92,
        "trusted": True,
        "editable": True,
    },
    "notion": {
        "weight": 0.88,
        "trusted": False,
        "editable": True,
    },
    "api_connector": {
        "weight": 0.90,
        "trusted": False,
        "editable": False,
    },
    "semantic_memory": {
        "weight": 0.82,
        "trusted": False,
        "editable": False,
    },
    "external_knowledge_base": {
        "weight": 0.80,
        "trusted": False,
        "editable": False,
    },
    "manual": {
        "weight": 1.00,
        "trusted": True,
        "editable": True,
    },
    "trusted_reference": {
        "weight": 1.00,
        "trusted": True,
        "editable": False,
    },
    "certification": {
        "weight": 1.00,
        "trusted": True,
        "editable": False,
    },
}

DEFAULT_SOURCE_KIND_PROFILE = {
    "weight": 0.75,
    "trusted": False,
    "editable": True,
}

def get_source_kind_profile_v1(source_kind):
    key = str(source_kind or "").strip().lower()
    return SOURCE_KIND_REGISTRY.get(key, DEFAULT_SOURCE_KIND_PROFILE)

def get_source_kind_weight_v1(source_kind):
    return float(get_source_kind_profile_v1(source_kind).get("weight", 0.75))


from dataclasses import dataclass, asdict, field

from datetime import datetime, timezone

from typing import Any, Dict, List
import hashlib
import re


@dataclass
class NormalizedConcept:
    concept_id: str
    canonical: str
    aliases: List[str] = field(default_factory=list)
    evidence_count: int = 0
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


ACRONYM_MAP_V1 = {
    "seo": "search engine optimization",
    "llm": "large language model",
    "lmp": "last menstrual period",
    "edd": "estimated due date",
    "opk": "ovulation predictor kit",
    "opks": "ovulation predictor kit",
    "bbt": "basal body temperature",
    "iui": "intrauterine insemination",
    "ivf": "in vitro fertilization",
    "fet": "frozen embryo transfer",
}


SINGULARIZATION_EXCEPTIONS_V1 = {
    "mucus",
    "status",
    "news",
    "analysis",
    "diabetes",
    "series",
    "species",
}


ALIAS_MAP_V1 = {
    "fertile window": "fertility window",
    "fertile days": "fertility window",
    "web page": "page",
    "webpage": "page",
    "article guide": "article",
}


def normalize_concept_text_v1(term: str) -> str:
    text = str(term or "").lower().strip()
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = " ".join(text.split())

    if text in ACRONYM_MAP_V1:
        return ACRONYM_MAP_V1[text]

    if text in ALIAS_MAP_V1:
        return ALIAS_MAP_V1[text]

    parts = []
    for part in text.split():
        if part in SINGULARIZATION_EXCEPTIONS_V1:
            parts.append(part)
            continue

        if len(part) > 4 and part.endswith("ies"):
            part = part[:-3] + "y"
        elif len(part) > 3 and part.endswith("s") and not part.endswith("ss"):
            part = part[:-1]
        parts.append(part)

    text = " ".join(parts)

    if text in ALIAS_MAP_V1:
        return ALIAS_MAP_V1[text]

    return text


def concept_id_for_v1(canonical: str) -> str:
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
    return f"concept_{digest}"


def build_normalized_concept_registry_v1(
    raw_terms: List[str],
) -> Dict[str, NormalizedConcept]:

    registry: Dict[str, NormalizedConcept] = {}

    for raw in raw_terms:
        raw_clean = " ".join(str(raw or "").lower().strip().split())
        canonical = normalize_concept_text_v1(raw_clean)

        if not canonical:
            continue

        concept_id = concept_id_for_v1(canonical)

        if concept_id not in registry:
            registry[concept_id] = NormalizedConcept(
                concept_id=concept_id,
                canonical=canonical,
                aliases=[],
                evidence_count=0,
                confidence=0.0,
                metadata={
                    "phase": "4.6.5B",
                    "normalizer": "semantic_concept_normalizer",
                    "first_seen": datetime.now(timezone.utc).isoformat(),
                },
            )

        concept = registry[concept_id]
        concept.evidence_count += 1

        if raw_clean and raw_clean != canonical and raw_clean not in concept.aliases:
            concept.aliases.append(raw_clean)

    for concept in registry.values():
        concept.confidence = round(min(0.99, 0.40 + (concept.evidence_count / 20)), 4)
        concept.metadata["last_seen"] = datetime.now(timezone.utc).isoformat()

    return registry


def serialize_concept_registry_v1(
    registry: Dict[str, NormalizedConcept],
) -> Dict[str, Any]:
    return {
        concept_id: asdict(concept)
        for concept_id, concept in registry.items()
    }


def explain_semantic_concept_normalizer_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5B.1",
        "module": "semantic_concept_normalizer.py",
        "status": "created",
        "responsibility": "Normalize raw semantic terms into canonical concept records with stable concept IDs.",
        "capabilities": [
            "canonical lowercase normalization",
            "plural normalization",
            "acronym expansion",
            "alias merging",
            "concept ID generation",
            "concept confidence scoring",
            "concept registry serialization",
        ],
        "next_phase": "4.6.5B.2 ? Concept Normalizer Integration",
    }



@dataclass
class NormalizedSemanticEdge:
    source_concept_id: str
    target_concept_id: str
    source_canonical: str
    target_canonical: str
    weight: int
    strength: float
    supporting_paragraphs: List[int]
    raw_source: str
    raw_target: str


@dataclass
class NormalizedSemanticGraph:
    title: str
    source_identifier: str
    concepts: Dict[str, NormalizedConcept]
    edges: List[NormalizedSemanticEdge]
    metadata: Dict[str, Any]


def normalize_semantic_graph_edges_v1(
    *,
    title: str,
    source_identifier: str,
    edges: List[Dict[str, Any]],
) -> NormalizedSemanticGraph:

    raw_terms: List[str] = []

    for edge in edges:
        raw_terms.append(edge.get("source", ""))
        raw_terms.append(edge.get("target", ""))

    registry = build_normalized_concept_registry_v1(raw_terms)

    canonical_lookup = {
        concept.canonical: concept
        for concept in registry.values()
    }

    normalized_edges: List[NormalizedSemanticEdge] = []

    for edge in edges:
        raw_source = edge.get("source", "")
        raw_target = edge.get("target", "")

        source_canonical = normalize_concept_text_v1(raw_source)
        target_canonical = normalize_concept_text_v1(raw_target)

        if not source_canonical or not target_canonical:
            continue

        if source_canonical == target_canonical:
            continue

        source_concept = canonical_lookup.get(source_canonical)
        target_concept = canonical_lookup.get(target_canonical)

        if not source_concept or not target_concept:
            continue

        normalized_edges.append(
            NormalizedSemanticEdge(
                source_concept_id=source_concept.concept_id,
                target_concept_id=target_concept.concept_id,
                source_canonical=source_canonical,
                target_canonical=target_canonical,
                weight=int(edge.get("weight", 0)),
                strength=float(edge.get("strength", 0.0)),
                supporting_paragraphs=edge.get("supporting_paragraphs", []),
                raw_source=raw_source,
                raw_target=raw_target,
            )
        )

    return NormalizedSemanticGraph(
        title=title,
        source_identifier=source_identifier,
        concepts=registry,
        edges=normalized_edges,
        metadata={
            "phase": "4.6.5B.2",
            "normalizer": "normalize_semantic_graph_edges_v1",
            "raw_edge_count": len(edges),
            "normalized_edge_count": len(normalized_edges),
            "concept_count": len(registry),
        },
    )


def serialize_normalized_semantic_graph_v1(
    graph: NormalizedSemanticGraph,
) -> Dict[str, Any]:
    return {
        "title": graph.title,
        "source_identifier": graph.source_identifier,
        "concepts": serialize_concept_registry_v1(graph.concepts),
        "edges": [asdict(edge) for edge in graph.edges],
        "metadata": graph.metadata,
    }


def explain_concept_normalizer_integration_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5B.2",
        "module": "semantic_concept_normalizer.py",
        "status": "created",
        "responsibility": "Convert semantic graph edges from raw strings into canonical concept IDs.",
        "outputs": [
            "source_concept_id",
            "target_concept_id",
            "source_canonical",
            "target_canonical",
            "concept_registry",
            "normalized_edges",
        ],
        "next_phase": "4.6.5B.3 ? Concept Registry Provenance",
    }



def _safe_unique_append_v1(items: List[Any], value: Any) -> List[Any]:
    if value is None:
        return items
    if value not in items:
        items.append(value)
    return items


def infer_semantic_type_v1(canonical: str) -> str:
    text = normalize_concept_text_v1(canonical)

    medical_terms = {
        "ovulation", "fertilization", "pregnancy", "luteal phase",
        "menstrual cycle", "last menstrual period", "basal body temperature",
        "cervical mucus", "estimated due date", "embryo transfer",
        "in vitro fertilization", "intrauterine insemination",
    }

    seo_terms = {
        "search engine optimization", "search engine", "google",
        "page", "website", "ranking", "optimization", "internal linking",
        "anchor text", "topic cluster", "knowledge graph",
    }

    if text in medical_terms:
        return "medical_reproductive_health_concept"

    if text in seo_terms:
        return "seo_concept"

    if any(token in text.split() for token in ["date", "period", "cycle", "phase"]):
        return "time_or_cycle_concept"

    if any(token in text.split() for token in ["engine", "search", "page", "website"]):
        return "web_or_search_concept"

    return "generic_concept"


def enrich_concept_registry_with_provenance_v1(
    registry: Dict[str, NormalizedConcept],
    *,
    document_id: str,
    source_identifier: str,
    source_kind: str,
    workspace_id: str = "",
    paragraph_map: Dict[str, List[int]] | None = None,
    language: str = "en",
) -> Dict[str, NormalizedConcept]:

    now = datetime.now(timezone.utc).isoformat()
    paragraph_map = paragraph_map or {}

    for concept in registry.values():
        md = concept.metadata

        md.setdefault("documents", [])
        md.setdefault("paragraphs", [])
        md.setdefault("workspaces", [])
        md.setdefault("sources", [])
        md.setdefault("source_kinds", [])
        md.setdefault("language", language)
        md.setdefault("semantic_type", infer_semantic_type_v1(concept.canonical))
        md.setdefault("first_seen", now)

        _safe_unique_append_v1(md["documents"], document_id)
        _safe_unique_append_v1(md["sources"], source_identifier)
        _safe_unique_append_v1(md["source_kinds"], source_kind)

        if workspace_id:
            _safe_unique_append_v1(md["workspaces"], workspace_id)

        for paragraph_index in paragraph_map.get(concept.canonical, []):
            _safe_unique_append_v1(md["paragraphs"], paragraph_index)

        md["last_seen"] = now
        md["provenance_enabled"] = True

    return registry


def build_paragraph_provenance_map_v1(
    edges: List[Dict[str, Any]],
) -> Dict[str, List[int]]:

    paragraph_map: Dict[str, List[int]] = {}

    for edge in edges:
        for key in ["source", "target"]:
            canonical = normalize_concept_text_v1(edge.get(key, ""))
            if not canonical:
                continue

            paragraph_map.setdefault(canonical, [])

            for p in edge.get("supporting_paragraphs", []):
                if p not in paragraph_map[canonical]:
                    paragraph_map[canonical].append(p)

    for key in paragraph_map:
        paragraph_map[key] = sorted(paragraph_map[key])

    return paragraph_map


def explain_concept_registry_provenance_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5B.3",
        "module": "semantic_concept_normalizer.py",
        "status": "created",
        "responsibility": "Attach provenance to normalized concepts for explainability, diagnostics, and cross-workspace learning.",
        "fields_added": [
            "documents",
            "paragraphs",
            "workspaces",
            "sources",
            "source_kinds",
            "language",
            "semantic_type",
            "first_seen",
            "last_seen",
            "provenance_enabled",
        ],
        "next_phase": "4.6.5B.4 ? Multi-Word Concept Detector",
    }



KNOWN_MULTIWORD_CONCEPTS_V1 = {
    "search engine optimization",
    "search engine",
    "large language model",
    "knowledge graph",
    "semantic search",
    "internal linking",
    "anchor text",
    "topic cluster",
    "page authority",
    "domain authority",
    "last menstrual period",
    "menstrual cycle",
    "luteal phase",
    "fertility window",
    "fertile window",
    "basal body temperature",
    "cervical mucus",
    "ovulation predictor kit",
    "estimated due date",
    "embryo transfer",
    "in vitro fertilization",
    "intrauterine insemination",
    "white hat",
    "black hat",
    "white hat seo",
    "black hat seo",
}


def detect_multiword_concepts_v1(text: str) -> List[str]:
    normalized = normalize_concept_text_v1(text)

    found: List[str] = []

    for concept in sorted(KNOWN_MULTIWORD_CONCEPTS_V1, key=len, reverse=True):
        canonical = normalize_concept_text_v1(concept)
        if canonical and canonical in normalized:
            found.append(canonical)

    seen = set()
    clean: List[str] = []

    for concept in found:
        if concept not in seen:
            seen.add(concept)
            clean.append(concept)

    return clean


def build_multiword_concepts_from_edges_v1(
    edges: List[Dict[str, Any]],
) -> List[str]:

    raw_text_parts: List[str] = []

    for edge in edges:
        raw_text_parts.append(str(edge.get("source", "")))
        raw_text_parts.append(str(edge.get("target", "")))

    raw_text = " ".join(raw_text_parts)

    detected = detect_multiword_concepts_v1(raw_text)

    return detected


def explain_multiword_concept_detector_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5B.4",
        "module": "semantic_concept_normalizer.py",
        "status": "created",
        "responsibility": "Detect complete multi-word semantic concepts before graph normalization.",
        "known_multiword_concepts": len(KNOWN_MULTIWORD_CONCEPTS_V1),
        "next_phase": "4.6.5B.5 ? Multi-Word Graph Integration",
    }



def normalize_semantic_graph_with_multiword_concepts_v1(
    *,
    title: str,
    source_identifier: str,
    edges: List[Dict[str, Any]],
    source_text: str = "",
) -> NormalizedSemanticGraph:

    raw_terms: List[str] = []

    for edge in edges:
        raw_terms.append(edge.get("source", ""))
        raw_terms.append(edge.get("target", ""))

    multiword_terms = detect_multiword_concepts_v1(source_text)

    raw_terms.extend(multiword_terms)

    registry = build_normalized_concept_registry_v1(raw_terms)

    canonical_lookup = {
        concept.canonical: concept
        for concept in registry.values()
    }

    normalized_edges: List[NormalizedSemanticEdge] = []

    for edge in edges:
        raw_source = edge.get("source", "")
        raw_target = edge.get("target", "")

        source_canonical = normalize_concept_text_v1(raw_source)
        target_canonical = normalize_concept_text_v1(raw_target)

        if not source_canonical or not target_canonical:
            continue

        if source_canonical == target_canonical:
            continue

        source_concept = canonical_lookup.get(source_canonical)
        target_concept = canonical_lookup.get(target_canonical)

        if not source_concept or not target_concept:
            continue

        normalized_edges.append(
            NormalizedSemanticEdge(
                source_concept_id=source_concept.concept_id,
                target_concept_id=target_concept.concept_id,
                source_canonical=source_canonical,
                target_canonical=target_canonical,
                weight=int(edge.get("weight", 0)),
                strength=float(edge.get("strength", 0.0)),
                supporting_paragraphs=edge.get("supporting_paragraphs", []),
                raw_source=raw_source,
                raw_target=raw_target,
            )
        )

    # Add light bridge edges from detected multi-word concepts to included component concepts.
    for mw in multiword_terms:
        mw_canonical = normalize_concept_text_v1(mw)
        mw_concept = canonical_lookup.get(mw_canonical)

        if not mw_concept:
            continue

        for part in mw_canonical.split():
            part_canonical = normalize_concept_text_v1(part)
            part_concept = canonical_lookup.get(part_canonical)

            if not part_concept:
                continue

            if part_concept.concept_id == mw_concept.concept_id:
                continue

            normalized_edges.append(
                NormalizedSemanticEdge(
                    source_concept_id=mw_concept.concept_id,
                    target_concept_id=part_concept.concept_id,
                    source_canonical=mw_canonical,
                    target_canonical=part_canonical,
                    weight=1,
                    strength=0.35,
                    supporting_paragraphs=[],
                    raw_source=mw,
                    raw_target=part,
                )
            )

    return NormalizedSemanticGraph(
        title=title,
        source_identifier=source_identifier,
        concepts=registry,
        edges=normalized_edges,
        metadata={
            "phase": "4.6.5B.5",
            "normalizer": "normalize_semantic_graph_with_multiword_concepts_v1",
            "raw_edge_count": len(edges),
            "normalized_edge_count": len(normalized_edges),
            "concept_count": len(registry),
            "multiword_concept_count": len(multiword_terms),
            "multiword_concepts": multiword_terms,
        },
    )


def explain_multiword_graph_integration_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5B.5",
        "module": "semantic_concept_normalizer.py",
        "status": "created",
        "responsibility": "Inject detected multi-word concepts into normalized semantic graph output.",
        "outputs": [
            "multiword_concepts",
            "concept_registry",
            "normalized_edges",
            "multiword_bridge_edges",
        ],
        "next_phase": "4.6.5B.6 ? Concept Normalization Certification",
    }



def consolidate_multiword_concept_fragments_v1(
    *,
    graph: NormalizedSemanticGraph,
) -> NormalizedSemanticGraph:

    multiwords = graph.metadata.get("multiword_concepts", []) or []

    if not multiwords:
        return graph

    canonical_multiwords = [
        normalize_concept_text_v1(mw)
        for mw in multiwords
        if normalize_concept_text_v1(mw)
    ]

    concept_lookup = {
        concept.canonical: concept
        for concept in graph.concepts.values()
    }

    replacement_map: Dict[str, str] = {}

    for mw in canonical_multiwords:
        mw_concept = concept_lookup.get(mw)

        if not mw_concept:
            continue

        for part in mw.split():
            part_canonical = normalize_concept_text_v1(part)
            part_concept = concept_lookup.get(part_canonical)

            if not part_concept:
                continue

            if part_concept.concept_id == mw_concept.concept_id:
                continue

            replacement_map[part_concept.concept_id] = mw_concept.concept_id

            mw_concept.evidence_count += part_concept.evidence_count

            for alias in part_concept.aliases:
                if alias not in mw_concept.aliases:
                    mw_concept.aliases.append(alias)

            if part_concept.canonical not in mw_concept.aliases:
                mw_concept.aliases.append(part_concept.canonical)

    consolidated_edges: List[NormalizedSemanticEdge] = []

    for edge in graph.edges:
        source_id = replacement_map.get(edge.source_concept_id, edge.source_concept_id)
        target_id = replacement_map.get(edge.target_concept_id, edge.target_concept_id)

        if source_id == target_id:
            continue

        source_concept = graph.concepts.get(source_id)
        target_concept = graph.concepts.get(target_id)

        if not source_concept or not target_concept:
            continue

        consolidated_edges.append(
            NormalizedSemanticEdge(
                source_concept_id=source_id,
                target_concept_id=target_id,
                source_canonical=source_concept.canonical,
                target_canonical=target_concept.canonical,
                weight=edge.weight,
                strength=edge.strength,
                supporting_paragraphs=edge.supporting_paragraphs,
                raw_source=edge.raw_source,
                raw_target=edge.raw_target,
            )
        )

    # Merge duplicate edges after replacement.
    merged: Dict[tuple[str, str], NormalizedSemanticEdge] = {}

    for edge in consolidated_edges:
        key = tuple(sorted([edge.source_concept_id, edge.target_concept_id]))

        if key not in merged:
            merged[key] = edge
            continue

        existing = merged[key]
        existing.weight += edge.weight
        existing.strength = round(max(existing.strength, edge.strength), 3)

        for p in edge.supporting_paragraphs:
            if p not in existing.supporting_paragraphs:
                existing.supporting_paragraphs.append(p)

        existing.supporting_paragraphs = sorted(existing.supporting_paragraphs)

    consolidated_concepts = {
        concept_id: concept
        for concept_id, concept in graph.concepts.items()
        if concept_id not in replacement_map
    }

    for concept in consolidated_concepts.values():
        concept.confidence = round(min(0.99, 0.40 + (concept.evidence_count / 20)), 4)

    return NormalizedSemanticGraph(
        title=graph.title,
        source_identifier=graph.source_identifier,
        concepts=consolidated_concepts,
        edges=list(merged.values()),
        metadata={
            **graph.metadata,
            "phase": "4.6.5B.5A",
            "consolidation_enabled": True,
            "multiword_concepts": canonical_multiwords,
            "fragments_replaced": len(replacement_map),
            "concept_count_after_consolidation": len(consolidated_concepts),
            "edge_count_after_consolidation": len(merged),
        },
    )


def explain_multiword_concept_consolidation_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5B.5A",
        "module": "semantic_concept_normalizer.py",
        "status": "created",
        "responsibility": "Replace fragmented single-word concept nodes with canonical multi-word concept nodes.",
        "outputs": [
            "consolidated_concepts",
            "consolidated_edges",
            "fragments_replaced",
            "concept_count_after_consolidation",
            "edge_count_after_consolidation",
        ],
        "next_phase": "4.6.5B.6 ? Concept Normalization Certification",
    }



def extract_terms_with_reserved_spans_v1(text: str) -> Dict[str, Any]:
    import re

    original = str(text or "")
    normalized = normalize_concept_text_v1(original)

    detected_multiwords = detect_multiword_concepts_v1(normalized)

    reserved_tokens = set()
    canonical_terms: List[str] = []

    for concept in detected_multiwords:
        canonical = normalize_concept_text_v1(concept)
        if not canonical:
            continue

        canonical_terms.append(canonical)

        for token in canonical.split():
            reserved_tokens.add(token)

    raw_words = re.findall(r"[a-z][a-z0-9'-]{2,}", normalized.lower())

    remaining_terms: List[str] = []

    for word in raw_words:
        canonical_word = normalize_concept_text_v1(word)

        if not canonical_word:
            continue

        if canonical_word in reserved_tokens:
            continue

        remaining_terms.append(canonical_word)

    seen = set()
    final_terms: List[str] = []

    for term in canonical_terms + remaining_terms:
        if term not in seen:
            seen.add(term)
            final_terms.append(term)

    return {
        "input_length": len(original),
        "multiword_concepts": canonical_terms,
        "reserved_tokens": sorted(reserved_tokens),
        "remaining_terms": remaining_terms,
        "final_terms": final_terms,
        "fragment_suppression_enabled": True,
    }


def explain_reserved_span_extractor_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5B.5B",
        "module": "semantic_concept_normalizer.py",
        "status": "created",
        "responsibility": "Detect multi-word concepts before token extraction and suppress their component-word fragments.",
        "outputs": [
            "multiword_concepts",
            "reserved_tokens",
            "remaining_terms",
            "final_terms",
            "fragment_suppression_enabled",
        ],
        "next_phase": "4.6.5B.6 ? Concept Normalization Certification",
    }



SEMANTIC_CONCEPT_DISCARD_TERMS_V1 = {
    "the", "a", "an", "and", "or", "but", "if", "then", "than",
    "can", "will", "would", "should", "could", "may", "might",
    "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "at", "by", "for", "with", "from",
    "during", "before", "after", "between", "through", "into",
    "this", "that", "these", "those", "it", "its", "they", "them",
    "you", "your", "we", "our", "he", "she", "his", "her",
    "help", "helps", "helpful", "thing", "things", "way", "ways",
    "only", "just", "very", "really", "also", "often", "usually",
}


SEMANTIC_CONCEPT_CONDITIONAL_TERMS_V1 = {
    "calculate", "calculating", "estimate", "estimating", "improve",
    "improving", "confirm", "track", "tracking", "rank", "ranking",
    "crawl", "crawling", "index", "indexing", "optimize", "optimizing",
}


def classify_semantic_concept_candidate_v1(term: str) -> str:
    canonical = normalize_concept_text_v1(term)

    if not canonical:
        return "DISCARD"

    if canonical in SEMANTIC_CONCEPT_DISCARD_TERMS_V1:
        return "DISCARD"

    if canonical in SEMANTIC_CONCEPT_CONDITIONAL_TERMS_V1:
        return "CONDITIONAL"

    if len(canonical.split()) >= 2:
        return "KEEP"

    if len(canonical) < 4:
        return "DISCARD"

    return "KEEP"


def filter_semantic_concept_candidates_v1(
    terms: List[str],
    *,
    keep_conditional: bool = True,
) -> Dict[str, Any]:

    kept: List[str] = []
    discarded: List[str] = []
    conditional: List[str] = []

    for term in terms:
        canonical = normalize_concept_text_v1(term)
        label = classify_semantic_concept_candidate_v1(canonical)

        if label == "KEEP":
            kept.append(canonical)

        elif label == "CONDITIONAL":
            conditional.append(canonical)
            if keep_conditional:
                kept.append(canonical)

        else:
            discarded.append(canonical)

    seen = set()
    final_terms: List[str] = []

    for term in kept:
        if term and term not in seen:
            seen.add(term)
            final_terms.append(term)

    return {
        "final_terms": final_terms,
        "discarded_terms": sorted(set(t for t in discarded if t)),
        "conditional_terms": sorted(set(t for t in conditional if t)),
        "kept_count": len(final_terms),
        "discarded_count": len(set(discarded)),
        "conditional_count": len(set(conditional)),
        "quality_filter_enabled": True,
    }


def extract_quality_filtered_terms_v1(text: str) -> Dict[str, Any]:
    reserved = extract_terms_with_reserved_spans_v1(text)
    filtered = filter_semantic_concept_candidates_v1(reserved["final_terms"])

    return {
        **reserved,
        "quality_filtered_terms": filtered["final_terms"],
        "discarded_terms": filtered["discarded_terms"],
        "conditional_terms": filtered["conditional_terms"],
        "quality_filter_enabled": True,
    }


def explain_semantic_concept_quality_filter_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5B.5C",
        "module": "semantic_concept_normalizer.py",
        "status": "created",
        "responsibility": "Remove grammatical/filler terms and retain semantically useful concepts after reserved-span extraction.",
        "outputs": [
            "quality_filtered_terms",
            "discarded_terms",
            "conditional_terms",
            "quality_filter_enabled",
        ],
        "next_phase": "4.6.5B.6 ? Concept Normalization Certification",
    }



SAFE_CANONICAL_ALIAS_MAP_V1 = {
    "engines": "engine",
    "search engines": "search engine",
    "search engine optimizations": "search engine optimization",
    "ovulations": "ovulation",
    "pregnancies": "pregnancy",
    "cycles": "cycle",
    "articles": "article",
    "categories": "category",
    "directories": "directory",
    "links": "link",
    "anchors": "anchor",
}


SEMANTIC_SUBSTITUTION_BLOCKLIST_V1 = {
    ("conception", "fertilization"),
    ("fertilization", "conception"),
    ("pregnancy", "implantation"),
    ("implantation", "pregnancy"),
    ("seo", "search marketing"),
    ("search engine optimization", "digital marketing"),
}


def safe_canonicalize_concept_v1(term: str) -> str:

    canonical = normalize_concept_text_v1(term)

    if canonical in SAFE_CANONICAL_ALIAS_MAP_V1:
        return SAFE_CANONICAL_ALIAS_MAP_V1[canonical]

    return canonical


def validate_safe_normalization_v1(
    original: str,
    normalized: str,
) -> bool:

    original = normalize_concept_text_v1(original)
    normalized = normalize_concept_text_v1(normalized)

    if (original, normalized) in SEMANTIC_SUBSTITUTION_BLOCKLIST_V1:
        return False

    return True


def normalize_concepts_safely_v1(
    concepts: List[str],
) -> Dict[str, Any]:

    normalized: List[str] = []
    rejected: List[Dict[str, str]] = []

    for concept in concepts:

        candidate = safe_canonicalize_concept_v1(concept)

        if validate_safe_normalization_v1(concept, candidate):
            normalized.append(candidate)
        else:
            rejected.append({
                "original": concept,
                "candidate": candidate,
            })
            normalized.append(normalize_concept_text_v1(concept))

    seen = set()
    final = []

    for concept in normalized:
        if concept and concept not in seen:
            seen.add(concept)
            final.append(concept)

    return {
        "normalized_concepts": final,
        "rejected_semantic_substitutions": rejected,
        "safe_normalization_enabled": True,
    }


def explain_safe_canonical_normalization_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5B.5D",
        "module": "semantic_concept_normalizer.py",
        "status": "created",
        "responsibility": (
            "Normalize lexical variants while preventing semantic "
            "meaning changes."
        ),
        "rules": [
            "plural ? singular allowed",
            "capitalization normalization allowed",
            "whitespace normalization allowed",
            "punctuation normalization allowed",
            "semantic substitution forbidden",
        ],
        "next_phase": "4.6.5B.6 ? Concept Normalization Certification",
    }



CONCEPT_TYPE_MAP_V1 = {
    "ovulation": "BIOLOGICAL_PROCESS",
    "conception": "BIOLOGICAL_PROCESS",
    "fertilization": "BIOLOGICAL_PROCESS",
    "pregnancy": "BIOLOGICAL_STATE",
    "menstrual cycle": "BIOLOGICAL_PROCESS",
    "luteal phase": "BIOLOGICAL_PHASE",
    "fertility window": "TIME_WINDOW",
    "last menstrual period": "DATE_REFERENCE",
    "estimated due date": "DATE_REFERENCE",
    "basal body temperature": "MEASUREMENT",
    "cervical mucus": "BIOLOGICAL_SIGNAL",
    "ovulation predictor kit": "PRODUCT_OR_TOOL",
    "embryo transfer": "MEDICAL_PROCEDURE",
    "in vitro fertilization": "MEDICAL_PROCEDURE",
    "intrauterine insemination": "MEDICAL_PROCEDURE",

    "search engine optimization": "SEO_CONCEPT",
    "search engine": "WEB_SYSTEM",
    "semantic search": "SEARCH_CONCEPT",
    "white hat seo": "SEO_METHOD",
    "black hat seo": "SEO_METHOD",
    "white hat": "SEO_METHOD",
    "black hat": "SEO_METHOD",
    "google": "ORGANIZATION",
    "website": "WEB_ENTITY",
    "page": "WEB_ENTITY",
    "ranking": "SEO_METRIC",
    "visibility": "SEO_METRIC",
    "traffic": "SEO_METRIC",
    "anchor text": "LINKING_CONCEPT",
    "internal linking": "LINKING_CONCEPT",
    "topic cluster": "SEO_STRUCTURE",
    "knowledge graph": "SEMANTIC_STRUCTURE",
}


ACTION_TERMS_V1 = {
    "calculate", "calculating", "estimate", "estimating", "confirm",
    "track", "tracking", "improve", "improving", "rank", "ranking",
    "crawl", "crawling", "index", "indexing", "optimize", "optimizing",
    "avoid", "detect", "predict", "measure", "compare",
}


ATTRIBUTE_TERMS_V1 = {
    "length", "average", "personal", "irregular", "recent", "early",
    "brief", "typical", "different", "quality", "quantity",
}


GENERIC_LOW_VALUE_TERMS_V1 = {
    "only", "rather", "which", "need", "help", "usually", "typically",
    "thing", "things", "way", "ways", "user", "people",
}


def classify_concept_type_v1(concept: str) -> str:
    canonical = safe_canonicalize_concept_v1(concept)

    if canonical in CONCEPT_TYPE_MAP_V1:
        return CONCEPT_TYPE_MAP_V1[canonical]

    if canonical in ACTION_TERMS_V1:
        return "ACTION"

    if canonical in ATTRIBUTE_TERMS_V1:
        return "ATTRIBUTE"

    if canonical in GENERIC_LOW_VALUE_TERMS_V1:
        return "LOW_VALUE_GENERIC"

    if len(canonical.split()) >= 2:
        return "MULTI_WORD_CONCEPT"

    if any(token in canonical for token in ["date", "period", "cycle", "phase", "window"]):
        return "TIME_OR_CYCLE_CONCEPT"

    if any(token in canonical for token in ["search", "engine", "page", "website", "ranking"]):
        return "WEB_OR_SEARCH_CONCEPT"

    return "GENERIC_CONCEPT"


def apply_semantic_concept_typing_v1(
    registry: Dict[str, NormalizedConcept],
) -> Dict[str, NormalizedConcept]:

    for concept in registry.values():
        concept.metadata.setdefault("semantic_type", classify_concept_type_v1(concept.canonical))
        concept.metadata["semantic_type"] = classify_concept_type_v1(concept.canonical)
        concept.metadata["semantic_typing_enabled"] = True

    return registry


def explain_semantic_concept_typing_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5B.6A",
        "module": "semantic_concept_normalizer.py",
        "status": "created",
        "responsibility": "Assign durable semantic_type labels to normalized concepts for downstream graph reasoning and filtering.",
        "types_supported": [
            "BIOLOGICAL_PROCESS",
            "BIOLOGICAL_STATE",
            "BIOLOGICAL_PHASE",
            "BIOLOGICAL_SIGNAL",
            "DATE_REFERENCE",
            "TIME_WINDOW",
            "MEASUREMENT",
            "PRODUCT_OR_TOOL",
            "MEDICAL_PROCEDURE",
            "SEO_CONCEPT",
            "WEB_SYSTEM",
            "SEARCH_CONCEPT",
            "SEO_METHOD",
            "ORGANIZATION",
            "WEB_ENTITY",
            "SEO_METRIC",
            "LINKING_CONCEPT",
            "SEO_STRUCTURE",
            "SEMANTIC_STRUCTURE",
            "ACTION",
            "ATTRIBUTE",
            "MULTI_WORD_CONCEPT",
            "LOW_VALUE_GENERIC",
            "GENERIC_CONCEPT",
        ],
        "next_phase": "4.6.5B.7 ? Final Semantic Concept Normalizer Freeze Marker",
    }



def enrich_concept_registry_schema_v1(
    registry: Dict[str, NormalizedConcept],
    *,
    default_language: str = "en",
) -> Dict[str, NormalizedConcept]:

    now = datetime.now(timezone.utc).isoformat()

    for concept in registry.values():
        md = concept.metadata

        md.setdefault("documents", [])
        md.setdefault("paragraphs", [])
        md.setdefault("workspaces", [])
        md.setdefault("sources", [])
        md.setdefault("source_kinds", [])

        md.setdefault("language", default_language)
        md.setdefault("semantic_type", classify_concept_type_v1(concept.canonical))
        md.setdefault("first_seen", now)
        md.setdefault("last_seen", now)

        md.setdefault("schema_version", "concept_registry_v1")
        md.setdefault("registry_ready", True)

        md["semantic_type"] = classify_concept_type_v1(concept.canonical)
        md["semantic_typing_enabled"] = True
        md["last_seen"] = now

    return registry


def explain_rich_concept_registry_schema_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5B.6B",
        "module": "semantic_concept_normalizer.py",
        "status": "created",
        "responsibility": "Ensure every normalized concept carries the full long-term registry schema.",
        "required_registry_fields": [
            "concept_id",
            "canonical",
            "aliases",
            "evidence_count",
            "confidence",
            "documents",
            "paragraphs",
            "workspaces",
            "sources",
            "source_kinds",
            "first_seen",
            "last_seen",
            "semantic_type",
            "language",
            "schema_version",
            "registry_ready",
        ],
        "next_phase": "4.6.5B.7 ? Final Semantic Concept Normalizer Freeze Marker",
    }



def add_concept_evidence_ledger_v1(
    registry: Dict[str, NormalizedConcept],
    *,
    workspace_id: str = "",
    document_id: str = "",
    source_identifier: str = "",
    source_kind: str = "",
    paragraph_index: int | None = None,
    snippet: str = "",
    confidence: float = 0.0,
) -> Dict[str, NormalizedConcept]:

    now = datetime.now(timezone.utc).isoformat()

    for concept in registry.values():
        md = concept.metadata
        md.setdefault("evidence", [])

        evidence_record = {
            "workspace_id": workspace_id,
            "document_id": document_id,
            "source_identifier": source_identifier,
            "source_kind": source_kind,
            "paragraph_index": paragraph_index,
            "confidence": confidence if confidence else concept.confidence,
            "timestamp": now,
            "snippet": snippet[:500] if snippet else "",
        }

        md["evidence"].append(evidence_record)
        md["evidence_count_detailed"] = len(md["evidence"])
        md["evidence_ledger_enabled"] = True
        md["last_seen"] = now

    return registry


def explain_concept_evidence_ledger_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5B.6C",
        "module": "semantic_concept_normalizer.py",
        "status": "created",
        "responsibility": "Attach structured evidence records to each normalized concept for explainability and diagnostics.",
        "evidence_fields": [
            "workspace_id",
            "document_id",
            "source_identifier",
            "source_kind",
            "paragraph_index",
            "confidence",
            "timestamp",
            "snippet",
        ],
        "next_phase": "4.6.5B.7 ? Final Semantic Concept Normalizer Freeze Marker",
    }



SOURCE_KIND_WEIGHTS_V1 = {
    "uploaded_docx": 1.00,
    "crawled_page": 0.85,
    "certification": 0.90,
    "manual": 1.00,
    "trusted_reference": 1.00,
    "unknown": 0.60,
}


def aggregate_evidence_confidence_v1(
    registry: Dict[str, NormalizedConcept],
) -> Dict[str, NormalizedConcept]:

    now = datetime.now(timezone.utc).isoformat()

    for concept in registry.values():
        md = concept.metadata
        evidence = md.get("evidence", []) or []

        if not evidence:
            concept.confidence = round(min(0.99, 0.40 + (concept.evidence_count / 20)), 4)
            md["confidence_aggregation_enabled"] = True
            md["confidence_factors"] = {
                "evidence_records": 0,
                "workspace_diversity": 0,
                "document_diversity": 0,
                "paragraph_diversity": 0,
                "source_kind_score": 0.0,
            }
            md["last_confidence_update"] = now
            continue

        workspaces = {e.get("workspace_id") for e in evidence if e.get("workspace_id")}
        documents = {e.get("document_id") for e in evidence if e.get("document_id")}
        paragraphs = {
            e.get("paragraph_index")
            for e in evidence
            if e.get("paragraph_index") is not None
        }

        source_weights = []
        for e in evidence:
            kind = e.get("source_kind") or "unknown"
            source_weights.append(SOURCE_KIND_WEIGHTS_V1.get(kind, SOURCE_KIND_WEIGHTS_V1["unknown"]))

        avg_source_weight = (
            sum(source_weights) / len(source_weights)
            if source_weights else 0.60
        )

        evidence_score = min(0.25, len(evidence) * 0.04)
        workspace_score = min(0.20, len(workspaces) * 0.05)
        document_score = min(0.20, len(documents) * 0.04)
        paragraph_score = min(0.20, len(paragraphs) * 0.02)
        source_score = min(0.15, avg_source_weight * 0.15)

        confidence = round(
            min(
                0.99,
                0.20
                + evidence_score
                + workspace_score
                + document_score
                + paragraph_score
                + source_score
            ),
            4,
        )

        concept.confidence = confidence

        md["confidence_aggregation_enabled"] = True
        md["last_confidence_update"] = now
        md["confidence_factors"] = {
            "evidence_records": len(evidence),
            "workspace_diversity": len(workspaces),
            "document_diversity": len(documents),
            "paragraph_diversity": len(paragraphs),
            "avg_source_weight": round(avg_source_weight, 4),
            "evidence_score": round(evidence_score, 4),
            "workspace_score": round(workspace_score, 4),
            "document_score": round(document_score, 4),
            "paragraph_score": round(paragraph_score, 4),
            "source_score": round(source_score, 4),
            "final_confidence": confidence,
        }

    return registry


def explain_evidence_confidence_aggregation_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5B.6D",
        "module": "semantic_concept_normalizer.py",
        "status": "created",
        "responsibility": "Compute concept confidence from evidence diversity, source type, documents, workspaces, and paragraph support.",
        "signals": [
            "evidence_records",
            "workspace_diversity",
            "document_diversity",
            "paragraph_diversity",
            "source_kind_weight",
        ],
        "next_phase": "4.6.5B.7 ? Final Semantic Concept Normalizer Freeze Marker",
    }


