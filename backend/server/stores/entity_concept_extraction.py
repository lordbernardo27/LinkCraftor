from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "your", "you",
    "are", "was", "were", "has", "have", "had", "into", "about", "when",
    "what", "how", "why", "can", "will", "would", "should", "could",
    "their", "there", "then", "than", "they", "them", "its", "also",
    "because", "while", "after", "before", "during", "between", "using",
    "used", "uses", "most", "many", "often", "likely", "around", "through",
    "some", "people", "another", "term", "helps", "track", "changes",
    "increase", "related", "conditions", "condition", "health", "risks",
    "notice",
}

_FRAGMENT_TERMS = {
    "blood", "pressure", "high", "gestational", "pregnancy-related",
    "health", "risks", "notice"
}

VOCAB_DIR = Path("backend/server/data/semantic_vocab")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:12]}"


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _words(text: str) -> List[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9'-]{2,}", text or "")


def load_semantic_vocabularies_v1(vocab_dir: Path = VOCAB_DIR) -> Dict[str, Any]:
    vocab_dir.mkdir(parents=True, exist_ok=True)

    domains: Dict[str, Dict[str, Any]] = {}
    alias_to_canonical: Dict[str, str] = {}
    canonical_to_domain: Dict[str, str] = {}

    for path in sorted(vocab_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            print(f"[Semantic Vocabulary] Skipping {path.name}: {exc}")
            continue
        domain = payload.get("domain") or path.stem
        terms = payload.get("terms", {})

        domains[domain] = terms

        for canonical, data in terms.items():
            canonical_norm = _normalize(canonical)
            alias_to_canonical[canonical_norm] = canonical_norm
            canonical_to_domain[canonical_norm] = domain

            for alias in data.get("aliases", []):
                alias_norm = _normalize(alias)
                alias_to_canonical[alias_norm] = canonical_norm

    return {
        "domains": domains,
        "alias_to_canonical": alias_to_canonical,
        "canonical_to_domain": canonical_to_domain,
        "vocab_file_count": len(list(vocab_dir.glob("*.json"))),
    }


def _detect_domain_label(text: str, vocab: Dict[str, Any]) -> str:
    lowered = _normalize(text)
    hits: Dict[str, int] = {}

    for domain, terms in vocab["domains"].items():
        domain_hits = 0

        for canonical, payload in terms.items():
            variants = [canonical] + payload.get("aliases", [])

            for variant in variants:
                if re.search(r"\b" + re.escape(_normalize(variant)) + r"\b", lowered):
                    domain_hits += 1

        hits[domain] = domain_hits

    if not hits:
        return "general"

    best_domain = max(hits, key=hits.get)
    return best_domain if hits[best_domain] > 0 else "general"


def _canonicalize(term: str, vocab: Dict[str, Any]) -> str:
    normalized = _normalize(term)
    return vocab["alias_to_canonical"].get(normalized, normalized)


def _get_category(canonical: str, domain_label: str, vocab: Dict[str, Any]) -> str:
    for domain, terms in vocab["domains"].items():
        if canonical in terms:
            return terms[canonical].get("category", f"{domain}_concept")

    if domain_label != "general":
        return f"{domain_label}_candidate"

    if len(canonical.split()) >= 2:
        return "concept"

    return "term"


def _candidate_spans(text: str, domain_label: str, vocab: Dict[str, Any]) -> Set[str]:
    lowered = _normalize(text)
    spans: Set[str] = set()

    domain_order = []

    if domain_label in vocab["domains"]:
        domain_order.append(domain_label)

    domain_order.extend(
        domain for domain in vocab["domains"].keys()
        if domain != domain_label
    )

    for domain in domain_order:
        terms = vocab["domains"][domain]

        for canonical, payload in terms.items():
            variants = [canonical] + payload.get("aliases", [])

            for variant in variants:
                pattern = r"\b" + re.escape(_normalize(variant)) + r"\b"

                if re.search(pattern, lowered):
                    spans.add(_canonicalize(variant, vocab))

    tokens = [_normalize(w) for w in _words(text)]
    tokens = [t for t in tokens if t not in _STOPWORDS and len(t) >= 4]

    for token in tokens:
        canonical = _canonicalize(token, vocab)

        if canonical in _FRAGMENT_TERMS:
            continue

        if canonical in vocab["canonical_to_domain"]:
            spans.add(canonical)

    for i in range(len(tokens) - 1):
        phrase2 = f"{tokens[i]} {tokens[i + 1]}"
        canonical2 = _canonicalize(phrase2, vocab)

        if canonical2 in vocab["canonical_to_domain"]:
            spans.add(canonical2)

    for i in range(len(tokens) - 2):
        phrase3 = f"{tokens[i]} {tokens[i + 1]} {tokens[i + 2]}"
        canonical3 = _canonicalize(phrase3, vocab)

        if canonical3 in vocab["canonical_to_domain"]:
            spans.add(canonical3)

    return spans


def _object_type(canonical: str) -> str:
    return "concept" if len(canonical.split()) >= 2 else "entity_candidate"


def _confidence(canonical: str, count: int, category: str, vocab: Dict[str, Any]) -> float:
    confidence = 0.55

    if category not in {"term", "concept"}:
        confidence += 0.20

    if len(canonical.split()) >= 2:
        confidence += 0.10

    if count >= 2:
        confidence += 0.10

    if count >= 3:
        confidence += 0.05

    if canonical in vocab["canonical_to_domain"]:
        confidence += 0.05

    return round(min(confidence, 0.98), 2)


def _collect_context_units(semantic_context_model: Dict[str, Any]) -> List[Dict[str, Any]]:
    units: List[Dict[str, Any]] = []

    for block_context in semantic_context_model.get("block_contexts", []):
        text = block_context.get("context", {}).get("current_text", "")
        if not text.strip():
            continue

        units.append({
            "unit_type": "block",
            "unit_id": block_context.get("block_id"),
            "text": text,
            "section_id": block_context.get("section_id"),
            "block_id": block_context.get("block_id"),
            "paragraph_id": block_context.get("paragraph_id"),
            "sentence_id": None,
            "breadcrumb": block_context.get("context", {}).get("breadcrumb", ""),
            "heading_ancestry": block_context.get("context", {}).get("heading_ancestry", []),
            "context_fingerprint": block_context.get("context_fingerprint"),
        })

    for sentence_context in semantic_context_model.get("sentence_contexts", []):
        text = sentence_context.get("context", {}).get("current_sentence_text", "")
        if not text.strip():
            continue

        units.append({
            "unit_type": "sentence",
            "unit_id": sentence_context.get("sentence_id"),
            "text": text,
            "section_id": sentence_context.get("section_id"),
            "block_id": sentence_context.get("block_id"),
            "paragraph_id": sentence_context.get("paragraph_id"),
            "sentence_id": sentence_context.get("sentence_id"),
            "breadcrumb": sentence_context.get("context", {}).get("breadcrumb", ""),
            "heading_ancestry": sentence_context.get("context", {}).get("heading_ancestry", []),
            "context_fingerprint": sentence_context.get("context_fingerprint"),
        })

    return units


def extract_entities_and_concepts_v1(
    semantic_context_model: Dict[str, Any],
    *,
    min_frequency: int = 1,
    max_semantic_objects: int = 40,
) -> Dict[str, Any]:
    vocab = load_semantic_vocabularies_v1()

    article = semantic_context_model.get("article", {})
    document_text = semantic_context_model.get("document_context", {}).get("document_text", "")
    domain_label = _detect_domain_label(document_text, vocab)

    context_units = _collect_context_units(semantic_context_model)

    phrase_counter: Counter[str] = Counter()
    phrase_evidence_units: Dict[str, List[Dict[str, Any]]] = {}
    surface_forms: Dict[str, Set[str]] = {}

    for unit in context_units:
        spans = _candidate_spans(unit["text"], domain_label, vocab)
        seen_in_unit: Set[str] = set()

        for span in spans:
            canonical = _canonicalize(span, vocab)

            if canonical in _FRAGMENT_TERMS:
                continue

            if canonical in seen_in_unit:
                continue

            seen_in_unit.add(canonical)
            phrase_counter[canonical] += 1
            phrase_evidence_units.setdefault(canonical, []).append(unit)
            surface_forms.setdefault(canonical, set()).add(span)

    valid_terms = [
        term for term, count in phrase_counter.most_common()
        if count >= min_frequency
    ][:max_semantic_objects]

    concept_candidates = [term for term in valid_terms if len(term.split()) >= 2]
    entity_candidates = [term for term in valid_terms if len(term.split()) == 1]

    semantic_objects: List[Dict[str, Any]] = []
    mentions: List[Dict[str, Any]] = []

    for term in valid_terms:
        count = phrase_counter[term]
        category = _get_category(term, domain_label, vocab)
        object_type = _object_type(term)
        confidence = _confidence(term, count, category, vocab)

        semantic_object_id = _stable_id(
            "semantic_object",
            article.get("article_id"),
            term,
            object_type,
            category,
        )

        aliases = {term}

        for alias, canonical in vocab["alias_to_canonical"].items():
            if canonical == term and alias != term:
                aliases.add(alias)

        aliases.update(surface_forms.get(term, set()))

        mention_ids = []
        locations = []

        for unit in phrase_evidence_units.get(term, []):
            mention_id = _stable_id(
                "mention",
                semantic_object_id,
                unit["unit_type"],
                unit["unit_id"],
                term,
            )

            mention = {
                "mention_id": mention_id,
                "semantic_object_id": semantic_object_id,
                "article_id": article.get("article_id"),
                "surface_text": term,
                "normalized_text": term,
                "canonical_text": term,
                "object_type": object_type,
                "category": category,
                "domain_label": domain_label,
                "extraction_confidence": confidence,
                "location": {
                    "section_id": unit["section_id"],
                    "block_id": unit["block_id"],
                    "paragraph_id": unit["paragraph_id"],
                    "sentence_id": unit["sentence_id"],
                    "unit_type": unit["unit_type"],
                    "unit_id": unit["unit_id"],
                },
                "evidence": {
                    "evidence_text": unit["text"],
                    "breadcrumb": unit["breadcrumb"],
                    "heading_ancestry": unit["heading_ancestry"],
                    "context_fingerprint": unit["context_fingerprint"],
                    "normalization_source": "external_semantic_vocab_registry",
                },
            }

            mentions.append(mention)
            mention_ids.append(mention_id)
            locations.append(mention["location"])

        section_ids = {loc.get("section_id") for loc in locations if loc.get("section_id")}
        block_ids = {loc.get("block_id") for loc in locations if loc.get("block_id")}
        sentence_ids = {loc.get("sentence_id") for loc in locations if loc.get("sentence_id")}

        semantic_objects.append({
            "semantic_object_id": semantic_object_id,
            "canonical_text": term,
            "display_text": term,
            "object_type": object_type,
            "category": category,
            "domain_label": domain_label,
            "aliases": sorted(aliases),
            "mention_ids": mention_ids,
            "locations": locations,
            "extraction_confidence": confidence,
            "normalization_source": "external_semantic_vocab_registry",
            "metadata": {
                "mention_count": len(mention_ids),
                "frequency": count,
                "section_count": len(section_ids),
                "block_count": len(block_ids),
                "sentence_count": len(sentence_ids),
            },
        })

    object_type_counts: Dict[str, int] = {}
    category_counts: Dict[str, int] = {}

    for item in semantic_objects:
        object_type_counts[item["object_type"]] = object_type_counts.get(item["object_type"], 0) + 1
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1

    paragraph_evidence = [
        {
            "unit_type": unit["unit_type"],
            "unit_id": unit["unit_id"],
            "section_id": unit["section_id"],
            "block_id": unit["block_id"],
            "paragraph_id": unit["paragraph_id"],
            "sentence_id": unit["sentence_id"],
            "breadcrumb": unit["breadcrumb"],
            "top_terms": [
                term for term in valid_terms
                if re.search(r"\b" + re.escape(term) + r"\b", _normalize(unit["text"]))
                or any(
                    re.search(r"\b" + re.escape(alias) + r"\b", _normalize(unit["text"]))
                    for alias, canonical in vocab["alias_to_canonical"].items()
                    if canonical == term
                )
            ][:20],
        }
        for unit in context_units
    ]

    return {
        "schema_version": "entity_concept_extraction_v1",
        "phase": "4.6.3",
        "patch": "4.6.3C",
        "created_at": _now_iso(),
        "source_schema_version": semantic_context_model.get("schema_version"),
        "source_phase": semantic_context_model.get("phase"),
        "source_patch": semantic_context_model.get("patch"),
        "article": {
            "article_id": article.get("article_id"),
            "title": article.get("title"),
            "source_url": article.get("source_url"),
        },
        "domain_label": domain_label,
        "dominant_terms": valid_terms,
        "entity_candidates": entity_candidates,
        "concept_candidates": concept_candidates,
        "semantic_objects": semantic_objects,
        "mentions": mentions,
        "paragraph_evidence": paragraph_evidence,
        "vocabulary_registry": {
            "path": str(VOCAB_DIR),
            "vocab_file_count": vocab["vocab_file_count"],
            "domains": sorted(vocab["domains"].keys()),
        },
        "metadata": {
            "semantic_object_count": len(semantic_objects),
            "mention_count": len(mentions),
            "dominant_term_count": len(valid_terms),
            "entity_candidate_count": len(entity_candidates),
            "concept_candidate_count": len(concept_candidates),
            "context_unit_count": len(context_units),
            "min_frequency": min_frequency,
            "max_semantic_objects": max_semantic_objects,
            "object_type_counts": object_type_counts,
            "category_counts": category_counts,
        },
        "boundary_rule": (
            "Entity & Concept Extraction identifies clean semantic objects using the external semantic vocabulary registry. "
            "It does not resolve links, create blue highlights, create yellow highlights, score targets, "
            "write memory, reason, or build semantic relationship graphs."
        ),
    }


def save_entities_and_concepts_v1(
    semantic_context_model: Dict[str, Any],
    output_path: str | Path,
    *,
    min_frequency: int = 1,
    max_semantic_objects: int = 40,
) -> Dict[str, Any]:
    extraction_model = extract_entities_and_concepts_v1(
        semantic_context_model,
        min_frequency=min_frequency,
        max_semantic_objects=max_semantic_objects,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(extraction_model, indent=2, ensure_ascii=False), encoding="utf-8")
    return extraction_model


def explain_entity_concept_extraction_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.3",
        "patch": "4.6.3C",
        "name": "Entity & Concept Extraction",
        "purpose": "Extract clean canonical semantic objects using a universal external semantic vocabulary registry.",
        "input": "Semantic Context Model from Phase 4.6.2A",
        "output": "Entity & Concept Extraction Model",
        "does": [
            "loads semantic vocabularies from JSON registry files",
            "supports multiple niches without changing extractor code",
            "detects article domain from available vocabulary registries",
            "extracts validated candidate spans",
            "matches domain vocabulary",
            "canonicalizes aliases into one semantic object",
            "suppresses phrase fragments",
            "separates entity candidates and concept candidates",
            "assigns semantic categories",
            "stores extraction confidence",
            "stores normalization provenance",
            "stores article, section, block, paragraph, and sentence evidence",
            "preserves breadcrumbs, heading ancestry, and context fingerprints",
        ],
        "does_not": [
            "perform internal link resolving",
            "perform semantic link resolving",
            "create blue highlights",
            "create yellow highlights",
            "score target pages",
            "infer topic intent",
            "build relationship graphs",
            "write memory",
            "perform reasoning",
            "generate explanations",
        ],
    }
