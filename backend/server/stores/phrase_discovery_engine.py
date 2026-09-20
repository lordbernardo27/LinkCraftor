from __future__ import annotations

import html as html_lib
import re

from typing import Any, Dict, List


"""
Phrase Discovery Engine

Niche-neutral discovery layer for uploaded documents.

This engine revisits the uploaded document after Smart Phrase Extractor
and discovers additional literal phrase candidates that the extractor
may have missed.

Internal discovery components:
- Semantic Discovery
- Relationship Discovery
- Content Context Discovery
- Long-tail Discovery
- Pattern Discovery
- External Authority Discovery

Hard architectural boundaries:
- Every emitted phrase must exist literally in the document.
- This engine does not replace Candidate Window Guard.
- This engine does not replace Phrase Strength Scorer.
- This engine does not select final highlights.
- This engine does not determine link targets.
- This engine does not determine highlight density.
- The engine must remain niche-neutral.
"""


__all__ = ["discover_phrases"]
def _normalize_span_text(value: str) -> str:
    return " ".join(str(value or "").split())


def _html_to_visible_text(value: str) -> str:
    raw = html_lib.unescape(str(value or ""))
    raw = re.sub(r"(?is)<script\b[^>]*>.*?</script>", " ", raw)
    raw = re.sub(r"(?is)<style\b[^>]*>.*?</style>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return _normalize_span_text(raw)


def _verify_literal_span(
    phrase: str,
    *,
    text: str = "",
    html: str = "",
    title: str = "",
) -> bool:
    """
    Return True only when the candidate phrase exists literally in the
    uploaded document text, visible HTML text, or title after whitespace
    normalization.

    This is a discovery-stage eligibility check only. It does not perform
    Guard or Scorer quality decisions.
    """
    needle = _normalize_span_text(phrase)
    if not needle:
        return False

    searchable_parts = [
        _normalize_span_text(title),
        _normalize_span_text(text),
        _html_to_visible_text(html),
    ]

    needle_cf = needle.casefold()

    return any(
        needle_cf in part.casefold()
        for part in searchable_parts
        if part
    )

def _find_literal_positions(
    phrase: str,
    *,
    text: str = "",
    html: str = "",
    title: str = "",
) -> Dict[str, Any]:
    """
    Recover literal candidate positions from the uploaded document.

    Positions are measured against the normalized searchable document text.
    This function performs no Guard, Scorer, or selection logic.
    """
    needle = _normalize_span_text(phrase)
    if not needle:
        return {
            "first_position": -1,
            "all_positions": [],
            "occurrence_count": 0,
        }

    body_text = (
        _normalize_span_text(text)
        if str(text or "").strip()
        else _html_to_visible_text(html)
    )
    title_text = _normalize_span_text(title)

    target = needle.casefold()
    haystack = body_text.casefold()

    positions: List[int] = []
    start = 0

    while haystack:
        index = haystack.find(target, start)
        if index < 0:
            break
        positions.append(index)
        start = index + max(1, len(target))

    found_in = "body"

    if not positions and title_text:
        title_index = title_text.casefold().find(target)
        if title_index >= 0:
            positions = [title_index]
            found_in = "title"

    return {
        "first_position": positions[0] if positions else -1,
        "all_positions": positions,
        "occurrence_count": len(positions),
        "position_source": found_in if positions else "none",
    }

def _new_component_diagnostics(component: str) -> Dict[str, Any]:
    """
    Create the standard diagnostics payload used by every discovery component.
    """
    return {
        "component": str(component or "").strip(),
        "proposed": 0,
        "literal_verified": 0,
        "rejected_nonliteral": 0,
        "overlap_with_extractor": 0,
        "net_new": 0,
        "errors": [],
    }

def _build_discovery_candidate(
    *,
    phrase: str,
    component: str,
    section_id: str = "",
    doc_id: str = "",
    snippet: str = "",
    intelligence: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Build one canonical Phrase Discovery candidate.

    All six internal discovery components must emit this common base shape.
    """
    return {
        "phrase": str(phrase or "").strip(),
        "source_type": "phrase_discovery",
        "section_id": str(section_id or "").strip(),
        "doc_id": str(doc_id or "").strip(),
        "snippet": str(snippet or ""),
        "provenance": {
            "origin": "phrase_discovery",
            "component": str(component or "").strip(),
        },
        "discovery_intelligence": {
            "component": str(component or "").strip(),
            **dict(intelligence or {}),
        },
    }



def _split_discovery_sentences(value: str) -> List[str]:
    """
    Lightweight niche-neutral sentence segmentation for Phrase Discovery.
    """
    clean = _normalize_span_text(value)
    if not clean:
        return []

    return [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+|[\r\n]+", clean)
        if part.strip()
    ]


def _discovery_tokens(value: str) -> List[str]:
    """
    Return normalized lexical tokens without applying niche-specific vocabulary.
    """
    return re.findall(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*", str(value or ""))

def _detect_semantic_concepts(
    context: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Detect document-supported semantic concept seeds without niche-specific rules.

    Concept evidence may come from:
    - Smart Phrase Extractor candidates,
    - title wording,
    - repeated lexical terms in the document.

    These are discovery seeds only, not final phrase candidates.
    """
    text = str(context.get("text", "") or "")
    html = str(context.get("html", "") or "")
    title = str(context.get("title", "") or "")
    extractor_candidates = context.get("extractor_candidates", []) or []

    body_text = text if text.strip() else _html_to_visible_text(html)
    sentences = _split_discovery_sentences(body_text)

    concepts: Dict[str, Dict[str, Any]] = {}

    for candidate in extractor_candidates:
        if not isinstance(candidate, dict):
            continue

        phrase = _normalize_span_text(candidate.get("phrase", ""))
        if not phrase:
            continue

        key = phrase.casefold()
        record = concepts.setdefault(
            key,
            {
                "concept": phrase,
                "sources": set(),
                "support_count": 0,
            },
        )
        record["sources"].add("extractor_candidate")
        record["support_count"] += 1

    title_tokens = _discovery_tokens(title)
    for token in title_tokens:
        if len(token) < 3:
            continue

        key = token.casefold()
        record = concepts.setdefault(
            key,
            {
                "concept": token,
                "sources": set(),
                "support_count": 0,
            },
        )
        record["sources"].add("title")
        record["support_count"] += 1

    lexical_counts: Dict[str, int] = {}

    for sentence in sentences:
        seen_in_sentence = set()

        for token in _discovery_tokens(sentence):
            normalized = token.casefold()

            if len(normalized) < 3:
                continue

            if normalized in seen_in_sentence:
                continue

            seen_in_sentence.add(normalized)
            lexical_counts[normalized] = lexical_counts.get(normalized, 0) + 1

    for token, count in lexical_counts.items():
        if count < 2:
            continue

        record = concepts.setdefault(
            token,
            {
                "concept": token,
                "sources": set(),
                "support_count": 0,
            },
        )
        record["sources"].add("repeated_document_term")
        record["support_count"] += count

    output: List[Dict[str, Any]] = []

    for record in concepts.values():
        output.append(
            {
                "concept": record["concept"],
                "sources": sorted(record["sources"]),
                "support_count": int(record["support_count"]),
            }
        )

    output.sort(
        key=lambda item: (
            -int(item.get("support_count", 0)),
            -len(_discovery_tokens(item.get("concept", ""))),
            str(item.get("concept", "")).casefold(),
        )
    )

    return output

def _semantic_span_search(
    context: Dict[str, Any],
    concept_seeds: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Search document sentences for literal multi-token spans surrounding
    document-supported semantic concept seeds.

    This function generates literal span proposals only.
    It does not perform final completeness, salience, Guard, or Scorer decisions.
    """
    text = str(context.get("text", "") or "")
    html = str(context.get("html", "") or "")

    body_text = text if text.strip() else _html_to_visible_text(html)
    sentences = _split_discovery_sentences(body_text)

    proposals: List[Dict[str, Any]] = []
    seen = set()

    for seed in concept_seeds:
        concept = _normalize_span_text(seed.get("concept", ""))
        if not concept:
            continue

        concept_cf = concept.casefold()

        for sentence in sentences:
            sentence_tokens = _discovery_tokens(sentence)
            if not sentence_tokens:
                continue

            token_values = [token.casefold() for token in sentence_tokens]
            concept_tokens = [token.casefold() for token in _discovery_tokens(concept)]

            if not concept_tokens:
                continue

            width = len(concept_tokens)

            for start in range(0, len(token_values) - width + 1):
                if token_values[start:start + width] != concept_tokens:
                    continue

                for left_extra in range(0, 3):
                    for right_extra in range(0, 3):
                        left = max(0, start - left_extra)
                        right = min(
                            len(sentence_tokens),
                            start + width + right_extra,
                        )

                        span_tokens = sentence_tokens[left:right]

                        if len(span_tokens) < 2:
                            continue

                        span = " ".join(span_tokens).strip()
                        key = (
                            span.casefold(),
                            sentence.casefold(),
                            concept_cf,
                        )

                        if key in seen:
                            continue

                        seen.add(key)

                        proposals.append(
                            {
                                "phrase": span,
                                "seed_concept": concept,
                                "seed_support_count": int(
                                    seed.get("support_count", 0) or 0
                                ),
                                "seed_sources": list(seed.get("sources", []) or []),
                                "sentence": sentence,
                                "token_start": left,
                                "token_end": right,
                            }
                        )

    return proposals

def _filter_extractor_misses(
    proposals: List[Dict[str, Any]],
    extractor_candidates: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Keep only phrase proposals not already produced by Smart Phrase Extractor.

    Comparison is intentionally conservative: case and whitespace are normalized,
    but related or expanded phrases remain distinct candidates.
    """
    extractor_phrases = {
        _normalize_span_text(candidate.get("phrase", "")).casefold()
        for candidate in extractor_candidates
        if isinstance(candidate, dict)
        and _normalize_span_text(candidate.get("phrase", ""))
    }

    misses: List[Dict[str, Any]] = []
    seen = set()

    for proposal in proposals:
        phrase = _normalize_span_text(proposal.get("phrase", ""))
        if not phrase:
            continue

        key = phrase.casefold()

        if key in extractor_phrases:
            continue

        if key in seen:
            continue

        seen.add(key)
        misses.append(dict(proposal))

    return misses

def _semantic_discovery(
    context: Dict[str, Any],
    diagnostics: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Semantic Discovery.

    Revisit the uploaded document and identify meaningful, semantically
    important literal phrase spans that Smart Phrase Extractor may have missed.

    This component proposes candidates only.
    It does not perform Guard, Scorer, selection, target-resolution,
    or density decisions.
    """
    candidates: List[Dict[str, Any]] = []

    concept_seeds = _detect_semantic_concepts(context)

    diagnostics["concept_seed_count"] = len(concept_seeds)
    diagnostics["concept_seeds"] = concept_seeds
    span_proposals = _semantic_span_search(
        context,
        concept_seeds,
    )

    diagnostics["semantic_span_proposal_count"] = len(span_proposals)

    return candidates

def discover_phrases(
    *,
    text: str = "",
    html: str = "",
    title: str = "",
    extractor_candidates: List[Dict[str, Any]] | None = None,
    document_id: str = "",
    workspace_id: str = "default",
    vertical: str = "general",
    max_candidates: int = 500,
) -> List[Dict[str, Any]]:
    """
    Canonical public entry point for Phrase Discovery.

    The implementation of the six discovery components will be added
    incrementally in later Phase 2+ steps.

    For now, the skeleton deliberately returns no candidates so it cannot
    change existing pipeline behavior before the engine is fully built and tested.
    """
    if extractor_candidates is None:
        clean_extractor_candidates: List[Dict[str, Any]] = []
    elif not isinstance(extractor_candidates, list):
        raise TypeError("extractor_candidates must be a list.")
    else:
        clean_extractor_candidates = [
            dict(candidate)
            for candidate in extractor_candidates
            if isinstance(candidate, dict)
        ]
    clean_text = str(text or "")
    clean_html = str(html or "")
    clean_title = str(title or "")
    clean_document_id = str(document_id or "").strip()
    clean_workspace_id = str(workspace_id or "default").strip() or "default"
    clean_vertical = str(vertical or "general").strip() or "general"
    safe_max_candidates = max(1, min(int(max_candidates or 500), 5000))

    discovery_context: Dict[str, Any] = {
        "text": clean_text,
        "html": clean_html,
        "title": clean_title,
        "document_id": clean_document_id,
        "workspace_id": clean_workspace_id,
        "vertical": clean_vertical,
        "max_candidates": safe_max_candidates,
        "extractor_candidates": clean_extractor_candidates,
    }
    component_diagnostics = {
        "semantic_discovery": _new_component_diagnostics("semantic_discovery"),
        "relationship_discovery": _new_component_diagnostics("relationship_discovery"),
        "content_context_discovery": _new_component_diagnostics("content_context_discovery"),
        "long_tail_discovery": _new_component_diagnostics("long_tail_discovery"),
        "pattern_discovery": _new_component_diagnostics("pattern_discovery"),
        "external_authority_discovery": _new_component_diagnostics("external_authority_discovery"),
    }

    discovery_candidates: List[Dict[str, Any]] = []

    if not clean_text and not clean_html and not clean_title:
        return []

    return discovery_candidates

















