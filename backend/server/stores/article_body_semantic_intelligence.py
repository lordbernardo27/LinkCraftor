"""
Article Body Semantic Intelligence

Phase 4.6 responsibility:
- Read extracted article bodies from UnifiedContentDocument.
- Preserve paragraph order.
- Preserve section/heading context.
- Prepare article content for semantic learning.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class SemanticParagraph:
    index: int
    text: str
    word_count: int
    char_count: int
    heading_context: str


@dataclass
class SemanticArticleReadResult:
    source_identifier: str
    title: str
    page_type: str
    paragraph_count: int
    word_count: int
    heading_count: int
    paragraphs: List[SemanticParagraph]
    metadata: Dict[str, Any]
    created_at: str


def _split_semantic_paragraphs_v1(text: str) -> List[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    blocks = [p.strip() for p in normalized.split("\n") if p.strip()]
    return blocks


def read_unified_article_semantically_v1(document: Dict[str, Any]) -> SemanticArticleReadResult:
    source_identifier = document.get("source_identifier", "")
    title = document.get("title", "")
    page_type = document.get("page_type", "")
    content = document.get("primary_content", "") or ""
    headings = document.get("headings", []) or []

    raw_paragraphs = _split_semantic_paragraphs_v1(content)

    semantic_paragraphs: List[SemanticParagraph] = []

    current_heading = title

    heading_set = {str(h).strip() for h in headings if str(h).strip()}

    for index, paragraph in enumerate(raw_paragraphs, start=1):
        if paragraph in heading_set:
            current_heading = paragraph

        semantic_paragraphs.append(
            SemanticParagraph(
                index=index,
                text=paragraph,
                word_count=len(paragraph.split()),
                char_count=len(paragraph),
                heading_context=current_heading,
            )
        )

    return SemanticArticleReadResult(
        source_identifier=source_identifier,
        title=title,
        page_type=page_type,
        paragraph_count=len(semantic_paragraphs),
        word_count=sum(p.word_count for p in semantic_paragraphs),
        heading_count=len(headings),
        paragraphs=semantic_paragraphs,
        metadata={
            "phase": "4.6.1",
            "reader": "read_unified_article_semantically_v1",
            "input_contract": "UnifiedContentDocument",
        },
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def serialize_semantic_article_read_result_v1(result: SemanticArticleReadResult) -> Dict[str, Any]:
    payload = asdict(result)
    return payload





@dataclass
class SemanticContextWindow:
    paragraph_index: int
    heading_context: str
    previous_text: str
    current_text: str
    next_text: str
    combined_context: str
    word_count: int
    context_terms: List[str]


def _semantic_terms_v1(text: str) -> List[str]:
    import re

    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "your", "you",
        "are", "was", "were", "has", "have", "had", "into", "about", "when",
        "what", "how", "why", "can", "will", "would", "should", "could",
        "their", "there", "then", "than", "they", "them", "its", "it's",
        "also", "because", "while", "after", "before", "during", "between",
        "using", "use", "used", "uses", "one", "two", "three", "may", "most",
    }

    words = re.findall(r"[A-Za-z][A-Za-z0-9'-]{2,}", text.lower())
    terms = []

    for word in words:
        if word not in stopwords and len(word) >= 4:
            terms.append(word)

    seen = set()
    unique_terms = []

    for term in terms:
        if term not in seen:
            seen.add(term)
            unique_terms.append(term)

    return unique_terms[:40]


def build_semantic_context_windows_v1(
    read_result: SemanticArticleReadResult,
) -> List[SemanticContextWindow]:

    paragraphs = read_result.paragraphs
    windows: List[SemanticContextWindow] = []

    for idx, paragraph in enumerate(paragraphs):
        previous_text = paragraphs[idx - 1].text if idx > 0 else ""
        current_text = paragraph.text
        next_text = paragraphs[idx + 1].text if idx < len(paragraphs) - 1 else ""

        combined = "\n".join(
            part for part in [previous_text, current_text, next_text]
            if part.strip()
        )

        windows.append(
            SemanticContextWindow(
                paragraph_index=paragraph.index,
                heading_context=paragraph.heading_context,
                previous_text=previous_text,
                current_text=current_text,
                next_text=next_text,
                combined_context=combined,
                word_count=len(combined.split()),
                context_terms=_semantic_terms_v1(combined),
            )
        )

    return windows


def serialize_semantic_context_windows_v1(
    windows: List[SemanticContextWindow],
) -> List[Dict[str, Any]]:
    return [asdict(w) for w in windows]


def explain_semantic_context_builder_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.2",
        "module": "article_body_semantic_intelligence.py",
        "status": "created",
        "responsibility": "Build previous-current-next paragraph context windows for semantic learning.",
        "outputs": [
            "paragraph_index",
            "heading_context",
            "previous_text",
            "current_text",
            "next_text",
            "combined_context",
            "word_count",
            "context_terms",
        ],
        "next_phase": "4.6.3 Entity & Concept Extraction completed",
    }





@dataclass
class SemanticEntityConceptResult:
    title: str
    source_identifier: str
    entity_candidates: List[str]
    concept_candidates: List[str]
    dominant_terms: List[str]
    paragraph_evidence: List[Dict[str, Any]]
    metadata: Dict[str, Any]


def _normalize_semantic_term_v1(term: str) -> str:
    return " ".join(str(term).lower().strip().split())


def _extract_candidate_phrases_v1(text: str) -> List[str]:
    import re

    words = re.findall(r"[A-Za-z][A-Za-z0-9'-]{2,}", text.lower())

    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "your", "you",
        "are", "was", "were", "has", "have", "had", "into", "about", "when",
        "what", "how", "why", "can", "will", "would", "should", "could",
        "their", "there", "then", "than", "they", "them", "its", "also",
        "because", "while", "after", "before", "during", "between", "using",
        "used", "uses", "most", "many", "often", "likely", "around", "through",
    }

    cleaned = [w for w in words if w not in stopwords and len(w) >= 4]

    phrases: List[str] = []

    for i in range(len(cleaned)):
        phrases.append(cleaned[i])
        if i + 1 < len(cleaned):
            phrases.append(f"{cleaned[i]} {cleaned[i+1]}")
        if i + 2 < len(cleaned):
            phrases.append(f"{cleaned[i]} {cleaned[i+1]} {cleaned[i+2]}")

    return [_normalize_semantic_term_v1(p) for p in phrases if p.strip()]


def extract_entities_and_concepts_v1(
    read_result: SemanticArticleReadResult,
    context_windows: List[SemanticContextWindow],
) -> SemanticEntityConceptResult:

    from collections import Counter

    phrase_counter: Counter[str] = Counter()
    paragraph_evidence: List[Dict[str, Any]] = []

    for window in context_windows:
        candidates = _extract_candidate_phrases_v1(window.combined_context)
        phrase_counter.update(candidates)

        paragraph_evidence.append({
            "paragraph_index": window.paragraph_index,
            "heading_context": window.heading_context,
            "top_terms": window.context_terms[:20],
            "candidate_count": len(candidates),
        })

    dominant_terms = [
        term for term, count in phrase_counter.most_common(40)
        if count >= 2
    ]

    concept_candidates = [
        term for term in dominant_terms
        if len(term.split()) >= 2
    ][:30]

    entity_candidates = [
        term for term in dominant_terms
        if len(term.split()) == 1
    ][:30]

    return SemanticEntityConceptResult(
        title=read_result.title,
        source_identifier=read_result.source_identifier,
        entity_candidates=entity_candidates,
        concept_candidates=concept_candidates,
        dominant_terms=dominant_terms,
        paragraph_evidence=paragraph_evidence,
        metadata={
            "phase": "4.6.3",
            "extractor": "extract_entities_and_concepts_v1",
            "paragraph_count": read_result.paragraph_count,
            "context_window_count": len(context_windows),
            "dominant_term_count": len(dominant_terms),
            "entity_candidate_count": len(entity_candidates),
            "concept_candidate_count": len(concept_candidates),
        },
    )


def serialize_entity_concept_result_v1(
    result: SemanticEntityConceptResult,
) -> Dict[str, Any]:
    return asdict(result)


def explain_entity_concept_extraction_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.3",
        "module": "article_body_semantic_intelligence.py",
        "status": "created",
        "responsibility": "Extract entity and concept candidates from semantic context windows.",
        "outputs": [
            "entity_candidates",
            "concept_candidates",
            "dominant_terms",
            "paragraph_evidence",
            "metadata",
        ],
        "next_phase": "4.6.4 Phrase Neighborhood Intelligence completed",
    }





from collections import Counter, defaultdict


@dataclass
class PhraseNeighborhood:
    phrase: str
    frequency: int
    neighboring_terms: List[str]
    supporting_paragraphs: List[int]
    neighborhood_strength: float


@dataclass
class PhraseNeighborhoodResult:
    title: str
    source_identifier: str
    neighborhoods: List[PhraseNeighborhood]
    metadata: Dict[str, Any]


def build_phrase_neighborhoods_v1(
    extraction: SemanticEntityConceptResult,
) -> PhraseNeighborhoodResult:

    neighborhood_map = defaultdict(Counter)
    paragraph_support = defaultdict(set)

    for evidence in extraction.paragraph_evidence:

        terms = evidence["top_terms"]
        paragraph = evidence["paragraph_index"]

        for i, term in enumerate(terms):

            for j, other in enumerate(terms):

                if i == j:
                    continue

                if term == other:
                    continue

                neighborhood_map[term][other] += 1
                paragraph_support[term].add(paragraph)

    neighborhoods = []

    for phrase, counter in neighborhood_map.items():

        neighbors = [
            n
            for n, c in counter.most_common(20)
            if c >= 2
        ]

        if not neighbors:
            continue

        strength = round(
            min(
                1.0,
                (
                    len(paragraph_support[phrase]) +
                    sum(counter.values()) / 10
                ) / 10
            ),
            3,
        )

        neighborhoods.append(
            PhraseNeighborhood(
                phrase=phrase,
                frequency=sum(counter.values()),
                neighboring_terms=neighbors,
                supporting_paragraphs=sorted(paragraph_support[phrase]),
                neighborhood_strength=strength,
            )
        )

    neighborhoods.sort(
        key=lambda n: (
            n.neighborhood_strength,
            n.frequency,
        ),
        reverse=True,
    )

    return PhraseNeighborhoodResult(
        title=extraction.title,
        source_identifier=extraction.source_identifier,
        neighborhoods=neighborhoods,
        metadata={
            "phase": "4.6.4",
            "neighborhood_count": len(neighborhoods),
        },
    )


def serialize_phrase_neighborhood_result_v1(
    result: PhraseNeighborhoodResult,
) -> Dict[str, Any]:
    return asdict(result)


def explain_phrase_neighborhood_intelligence_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.4",
        "status": "created",
        "responsibility": (
            "Learn stable semantic neighborhoods instead of "
            "isolated keyword pairs."
        ),
        "outputs": [
            "phrase",
            "neighboring_terms",
            "supporting_paragraphs",
            "neighborhood_strength",
        ],
        "next_phase": "4.6.5 Semantic Co-occurrence Intelligence completed",
    }





@dataclass
class SemanticCooccurrenceEdge:
    source: str
    target: str
    weight: int
    supporting_paragraphs: List[int]
    strength: float


@dataclass
class SemanticCooccurrenceGraph:
    title: str
    source_identifier: str
    edges: List[SemanticCooccurrenceEdge]
    metadata: Dict[str, Any]





SEMANTIC_GRAPH_NOISE_TERMS_V1 = {
    "want", "just", "first", "people", "started", "like", "many", "more",
    "most", "often", "likely", "around", "through", "using", "used", "uses",
    "make", "makes", "made", "take", "takes", "taken", "give", "given",
    "good", "better", "best", "simple", "easy", "common", "different",
    "important", "helpful", "clear", "sure", "thing", "things", "way",
    "ways", "part", "parts", "time", "times", "day", "days", "month",
    "months", "year", "years", "example", "examples", "question",
    "questions", "answer", "answers", "guide", "search", "searches",
}


def filter_semantic_graph_terms_v1(terms: List[str]) -> List[str]:
    filtered: List[str] = []

    for term in terms:
        normalized = _normalize_semantic_term_v1(term)

        if not normalized:
            continue

        parts = normalized.split()

        if len(parts) == 1 and normalized in SEMANTIC_GRAPH_NOISE_TERMS_V1:
            continue

        if len(parts) == 1 and len(normalized) < 4:
            continue

        if len(parts) >= 2:
            noisy_parts = [p for p in parts if p in SEMANTIC_GRAPH_NOISE_TERMS_V1]
            if len(noisy_parts) == len(parts):
                continue

        filtered.append(normalized)

    seen = set()
    clean: List[str] = []

    for term in filtered:
        if term not in seen:
            seen.add(term)
            clean.append(term)

    return clean


def explain_semantic_graph_noise_filter_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5A",
        "status": "created",
        "responsibility": "Remove weak/common terms before semantic co-occurrence graph construction.",
        "noise_terms_count": len(SEMANTIC_GRAPH_NOISE_TERMS_V1),
        "next_phase": "4.6.6 Section Evidence Builder",
    }


def build_semantic_cooccurrence_graph_v1(
    extraction: SemanticEntityConceptResult,
) -> SemanticCooccurrenceGraph:

    from collections import defaultdict

    pair_counts = defaultdict(int)
    pair_support = defaultdict(set)

    for evidence in extraction.paragraph_evidence:
        paragraph_index = evidence["paragraph_index"]
        terms = filter_semantic_graph_terms_v1(evidence.get("top_terms", [])[:20])[:15]

        for i in range(len(terms)):
            for j in range(i + 1, len(terms)):
                a = _normalize_semantic_term_v1(terms[i])
                b = _normalize_semantic_term_v1(terms[j])

                if not a or not b or a == b:
                    continue

                source, target = sorted([a, b])
                pair = (source, target)

                pair_counts[pair] += 1
                pair_support[pair].add(paragraph_index)

    edges: List[SemanticCooccurrenceEdge] = []

    for (source, target), weight in pair_counts.items():
        if weight < 2:
            continue

        supporting = sorted(pair_support[(source, target)])
        strength = round(min(1.0, (weight + len(supporting)) / 10), 3)

        edges.append(
            SemanticCooccurrenceEdge(
                source=source,
                target=target,
                weight=weight,
                supporting_paragraphs=supporting,
                strength=strength,
            )
        )

    edges.sort(
        key=lambda e: (e.strength, e.weight, len(e.supporting_paragraphs)),
        reverse=True,
    )

    return SemanticCooccurrenceGraph(
        title=extraction.title,
        source_identifier=extraction.source_identifier,
        edges=edges,
        metadata={
            "phase": "4.6.5",
            "edge_count": len(edges),
            "source": extraction.source_identifier,
            "title": extraction.title,
        },
    )


def serialize_semantic_cooccurrence_graph_v1(
    graph: SemanticCooccurrenceGraph,
) -> Dict[str, Any]:
    return asdict(graph)


def explain_semantic_cooccurrence_intelligence_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5",
        "status": "created",
        "responsibility": "Build weighted semantic co-occurrence edges from paragraph-level evidence.",
        "outputs": [
            "source",
            "target",
            "weight",
            "supporting_paragraphs",
            "strength",
        ],
        "next_phase": "4.6.6 Section Evidence Builder",
    }


def explain_semantic_article_reader_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.1",
        "module": "article_body_semantic_intelligence.py",
        "status": "created",
        "responsibility": "Read UnifiedContentDocument article bodies paragraph-by-paragraph while preserving order and heading context.",
        "outputs": [
            "source_identifier",
            "title",
            "page_type",
            "paragraph_count",
            "word_count",
            "heading_count",
            "paragraphs",
            "heading_context",
        ],
        "next_phase": "4.6.2 Semantic Context Builder completed",
    }
