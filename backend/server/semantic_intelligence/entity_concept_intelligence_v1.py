"""Canonical Entity & Concept Intelligence v1.

Phase 4.6.2.

Consumes only the certified output contract of the Phase 4.6.1
Semantic Intelligence Runtime Reader.

This component owns entity and concept intelligence. It does not own
phrase-neighborhood intelligence, topic-intent intelligence, reasoning,
ontology alignment, learning, Semantic Memory, scoring, or linking.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import spacy
from collections import Counter
from typing import Any, Mapping


_DATA_ROOT = Path(__file__).resolve().parents[1] / "data"
SEMANTIC_VOCAB_ROOT = _DATA_ROOT / "semantic_vocab"

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9'-]*")

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "because", "been",
    "being", "but", "by", "can", "could", "did", "do", "does",
    "for", "from", "had", "has", "have", "how", "if", "in", "into",
    "is", "it", "its", "may", "more", "most", "of", "on", "or",
    "our", "over", "such", "than", "that", "the", "their", "them",
    "these", "they", "this", "to", "too", "use", "used", "using",
    "was", "were", "what", "when", "where", "which", "while",
    "with", "would",
}


_SPACY_MODEL = None

_ENTITY_LABELS = {
    "PERSON",
    "ORG",
    "GPE",
    "LOC",
    "FAC",
    "PRODUCT",
    "EVENT",
    "WORK_OF_ART",
    "LAW",
    "LANGUAGE",
}


def _get_spacy_model():
    global _SPACY_MODEL

    if _SPACY_MODEL is None:
        try:
            _SPACY_MODEL = spacy.load("en_core_web_sm")
        except Exception as exc:
            raise EntityConceptIntelligenceError(
                "Required spaCy model en_core_web_sm could not be loaded."
            ) from exc

    return _SPACY_MODEL


ENTITY_CONCEPT_INTELLIGENCE_VERSION = (
    "entity_concept_intelligence_v1"
)


class EntityConceptIntelligenceError(RuntimeError):
    """Base fail-closed error for Phase 4.6.2."""



def _normalize_text(value: str) -> str:
    return " ".join(
        token.casefold()
        for token in _WORD_RE.findall(value or "")
    )


def load_semantic_vocabularies_v1() -> dict[str, Any]:
    """Load optional semantic vocabulary packs for enrichment."""

    domains: dict[str, dict[str, Any]] = {}
    alias_to_canonical: dict[str, str] = {}
    canonical_terms: dict[str, dict[str, Any]] = {}

    if not SEMANTIC_VOCAB_ROOT.exists():
        return {
            "domains": {},
            "alias_to_canonical": {},
            "canonical_terms": {},
            "vocab_file_count": 0,
        }

    files = sorted(SEMANTIC_VOCAB_ROOT.glob("*.json"))

    for path in files:
        try:
            payload = json.loads(
                path.read_text(encoding="utf-8-sig")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise EntityConceptIntelligenceError(
                f"Invalid semantic vocabulary file: {path.name}"
            ) from exc

        if not isinstance(payload, dict):
            raise EntityConceptIntelligenceError(
                f"Semantic vocabulary must be an object: {path.name}"
            )

        domain = payload.get("domain")
        terms = payload.get("terms")

        if (
            not isinstance(domain, str)
            or not domain.strip()
            or not isinstance(terms, dict)
        ):
            raise EntityConceptIntelligenceError(
                f"Malformed semantic vocabulary: {path.name}"
            )

        normalized_domain = domain.strip().casefold()
        domains[normalized_domain] = terms

        for canonical, spec in terms.items():
            if not isinstance(canonical, str) or not canonical.strip():
                continue

            normalized_canonical = _normalize_text(canonical)

            if not normalized_canonical:
                continue

            spec = spec if isinstance(spec, dict) else {}

            canonical_terms[normalized_canonical] = {
                "canonical_text": canonical.strip(),
                "domain": normalized_domain,
                "category": spec.get("category"),
                "aliases": [
                    alias.strip()
                    for alias in spec.get("aliases", [])
                    if isinstance(alias, str) and alias.strip()
                ],
            }

            alias_to_canonical[normalized_canonical] = (
                normalized_canonical
            )

            for alias in canonical_terms[
                normalized_canonical
            ]["aliases"]:
                normalized_alias = _normalize_text(alias)

                if normalized_alias:
                    alias_to_canonical[
                        normalized_alias
                    ] = normalized_canonical

    return {
        "domains": domains,
        "alias_to_canonical": alias_to_canonical,
        "canonical_terms": canonical_terms,
        "vocab_file_count": len(files),
    }


def detect_entity_concept_mentions_v1(
    runtime_reader_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Detect article-local entity and concept mentions with NLP evidence."""

    intake = validate_entity_concept_intake_v1(
        runtime_reader_result
    )

    model = runtime_reader_result["semantic_reading_model"]
    vocabulary = load_semantic_vocabularies_v1()
    nlp = _get_spacy_model()

    mentions: list[dict[str, Any]] = []

    for block in model.get("blocks") or []:
        if not isinstance(block, Mapping):
            continue

        text = block.get("text")

        if not isinstance(text, str) or not text.strip():
            continue

        doc = nlp(text)
        block_type = block.get("block_type")
        block_start = block.get("start_char")

        # Named-entity evidence is taken from prose blocks.
        # Heading fragments are intentionally not trusted as NER labels.
        if block_type != "heading":
            for ent in doc.ents:
                if ent.label_ not in _ENTITY_LABELS:
                    continue

                normalized = " ".join(
                    token.lemma_.casefold()
                    for token in ent
                    if not token.is_space
                    and not token.is_punct
                ).strip()

                if not normalized:
                    continue

                vocab_canonical = vocabulary[
                    "alias_to_canonical"
                ].get(normalized)

                canonical = vocab_canonical or normalized
                vocab_spec = vocabulary[
                    "canonical_terms"
                ].get(canonical, {})

                mentions.append({
                    "mention_text": ent.text.strip(),
                    "normalized_text": normalized,
                    "canonical_text": canonical,
                    "candidate_kind": "named_entity",
                    "nlp_entity_label": ent.label_,
                    "nlp_has_proper_noun": any(
                        token.pos_ == "PROPN"
                        for token in ent
                    ),
                    "registry_backed": bool(vocab_canonical),
                    "registry_domain": vocab_spec.get("domain"),
                    "registry_category": vocab_spec.get("category"),
                    "section_id": block.get("section_id"),
                    "block_id": block.get("block_id"),
                    "paragraph_id": block.get("paragraph_id"),
                    "block_type": block_type,
                    "block_start_char": block_start,
                    "local_start_char": ent.start_char,
                    "local_end_char": ent.end_char,
                    "article_start_char": (
                        block_start + ent.start_char
                        if isinstance(block_start, int)
                        else None
                    ),
                    "article_end_char": (
                        block_start + ent.end_char
                        if isinstance(block_start, int)
                        else None
                    ),
                })

        # Noun phrases are the primary concept-detection signal.
        for chunk in doc.noun_chunks:
            semantic_tokens = [
                token
                for token in chunk
                if not token.is_stop
                and not token.is_punct
                and not token.is_space
            ]

            if not semantic_tokens:
                continue

            if not any(
                token.pos_ in {"NOUN", "PROPN"}
                for token in semantic_tokens
            ):
                continue

            normalized = " ".join(
                token.lemma_.casefold()
                for token in semantic_tokens
            ).strip()

            if len(normalized) < 3:
                continue

            vocab_canonical = vocabulary[
                "alias_to_canonical"
            ].get(normalized)

            canonical = vocab_canonical or normalized
            vocab_spec = vocabulary[
                "canonical_terms"
            ].get(canonical, {})

            mentions.append({
                "mention_text": chunk.text.strip(),
                "normalized_text": normalized,
                "canonical_text": canonical,
                "candidate_kind": "concept_phrase",
                "nlp_root_pos": chunk.root.pos_,
                "registry_backed": bool(vocab_canonical),
                "registry_domain": vocab_spec.get("domain"),
                "registry_category": vocab_spec.get("category"),
                "section_id": block.get("section_id"),
                "block_id": block.get("block_id"),
                "paragraph_id": block.get("paragraph_id"),
                "block_type": block_type,
                "block_start_char": block_start,
                "local_start_char": chunk.start_char,
                "local_end_char": chunk.end_char,
                "article_start_char": (
                    block_start + chunk.start_char
                    if isinstance(block_start, int)
                    else None
                ),
                "article_end_char": (
                    block_start + chunk.end_char
                    if isinstance(block_start, int)
                    else None
                ),
            })

    if not mentions:
        raise EntityConceptIntelligenceError(
            "No entity or concept mentions were detected."
        )

    return {
        "schema_version":
            "entity_concept_mention_detection_v1",
        "phase":
            "4.6.2",
        "status":
            "ENTITY_CONCEPT_MENTIONS_DETECTED",
        "intake":
            intake,
        "nlp_engine": {
            "library": "spacy",
            "model": "en_core_web_sm",
            "role": "DETECTION_SIGNAL_NOT_AUTHORITATIVE_WORLD_KNOWLEDGE",
        },
        "mention_count":
            len(mentions),
        "mentions":
            mentions,
        "vocabulary_enrichment": {
            "enabled": True,
            "required_for_detection": False,
            "vocab_file_count":
                vocabulary["vocab_file_count"],
        },
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "global_vocabulary_write_performed":
            False,
        "semantic_memory_write_performed":
            False,
        "next_stage":
            "entity_concept_canonicalization_and_classification",
    }



def build_entity_concept_objects_v1(
    runtime_reader_result: Mapping[str, Any],
    *,
    min_mentions: int = 2,
    max_objects: int = 60,
) -> dict[str, Any]:
    """Aggregate raw mentions into article-local semantic objects."""

    if not isinstance(min_mentions, int) or min_mentions < 1:
        raise EntityConceptIntelligenceError(
            "min_mentions must be a positive integer."
        )

    if not isinstance(max_objects, int) or max_objects < 1:
        raise EntityConceptIntelligenceError(
            "max_objects must be a positive integer."
        )

    detection = detect_entity_concept_mentions_v1(
        runtime_reader_result
    )

    groups: dict[str, list[dict[str, Any]]] = {}

    for mention in detection["mentions"]:
        canonical = mention.get("canonical_text")

        if not isinstance(canonical, str) or not canonical.strip():
            continue

        groups.setdefault(
            canonical.strip(),
            [],
        ).append(mention)

    objects: list[dict[str, Any]] = []

    for canonical, mentions in groups.items():
        mention_count = len(mentions)

        named_entity_mentions = [
            item
            for item in mentions
            if item.get("candidate_kind") == "named_entity"
        ]

        concept_mentions = [
            item
            for item in mentions
            if item.get("candidate_kind") == "concept_phrase"
        ]

        registry_backed = any(
            item.get("registry_backed") is True
            for item in mentions
        )

        heading_supported = any(
            item.get("block_type") == "heading"
            for item in mentions
        )

        section_ids = {
            item.get("section_id")
            for item in mentions
            if item.get("section_id")
        }

        block_ids = {
            item.get("block_id")
            for item in mentions
            if item.get("block_id")
        }

        proper_noun_entity_evidence = any(
            item.get("nlp_has_proper_noun") is True
            for item in named_entity_mentions
        )

        # NER is supporting evidence, not authoritative classification.
        # A free article-local object becomes an entity only when NER is
        # reinforced by proper-noun evidence. Otherwise it remains a concept.
        if proper_noun_entity_evidence:
            semantic_kind = "entity"
        else:
            semantic_kind = "concept"

        # Article-local extraction confidence only.
        # This is not a claim that the object is globally true.
        confidence = 0.40

        confidence += min(mention_count, 6) * 0.05
        confidence += min(len(section_ids), 4) * 0.04

        if registry_backed:
            confidence += 0.10

        if named_entity_mentions and concept_mentions:
            confidence += 0.08

        if heading_supported:
            confidence += 0.05

        confidence = round(
            min(confidence, 0.99),
            3,
        )

        # Free article-local objects need recurring evidence unless
        # supported by NER, registry evidence, or canonical heading use.
        if (
            mention_count < min_mentions
            and not named_entity_mentions
            and not registry_backed
            and not heading_supported
        ):
            continue

        entity_labels = sorted({
            item.get("nlp_entity_label")
            for item in named_entity_mentions
            if item.get("nlp_entity_label")
        })

        surface_forms = sorted({
            item.get("mention_text")
            for item in mentions
            if isinstance(item.get("mention_text"), str)
            and item.get("mention_text").strip()
        })

        objects.append({
            "canonical_text":
                canonical,
            "semantic_kind":
                semantic_kind,
            "surface_forms":
                surface_forms,
            "mention_count":
                mention_count,
            "named_entity_mention_count":
                len(named_entity_mentions),
            "concept_mention_count":
                len(concept_mentions),
            "entity_labels":
                entity_labels,
            "proper_noun_entity_evidence":
                proper_noun_entity_evidence,
            "section_count":
                len(section_ids),
            "block_count":
                len(block_ids),
            "section_ids":
                sorted(section_ids),
            "block_ids":
                sorted(block_ids),
            "registry_backed":
                registry_backed,
            "registry_domain":
                next(
                    (
                        item.get("registry_domain")
                        for item in mentions
                        if item.get("registry_domain")
                    ),
                    None,
                ),
            "registry_category":
                next(
                    (
                        item.get("registry_category")
                        for item in mentions
                        if item.get("registry_category")
                    ),
                    None,
                ),
            "heading_supported":
                heading_supported,
            "extraction_confidence":
                confidence,
            "evidence":
                mentions,
        })

    objects.sort(
        key=lambda item: (
            -item["extraction_confidence"],
            -item["mention_count"],
            -item["section_count"],
            item["canonical_text"],
        )
    )

    objects = objects[:max_objects]

    entity_count = sum(
        1
        for item in objects
        if item["semantic_kind"] == "entity"
    )

    concept_count = sum(
        1
        for item in objects
        if item["semantic_kind"] == "concept"
    )

    return {
        "schema_version":
            "entity_concept_semantic_objects_v1",
        "phase":
            "4.6.2",
        "status":
            "ENTITY_CONCEPT_OBJECTS_BUILT",
        "article_id":
            detection["intake"]["article_id"],
        "raw_mention_count":
            detection["mention_count"],
        "semantic_object_count":
            len(objects),
        "entity_count":
            entity_count,
        "concept_count":
            concept_count,
        "semantic_objects":
            objects,
        "canonicalization": {
            "article_local_deduplication":
                True,
            "surface_forms_collapsed":
                True,
            "registry_alias_resolution":
                True,
        },
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "global_vocabulary_write_performed":
            False,
        "semantic_memory_write_performed":
            False,
        "classification_rule": (
            "Named-entity evidence produces an entity classification; "
            "otherwise noun/concept evidence produces a concept classification. "
            "Extraction confidence measures article-local evidence strength only."
        ),
        "next_stage":
            "entity_concept_output_consolidation",
    }



def run_entity_concept_intelligence_v1(
    runtime_reader_result: Mapping[str, Any],
    *,
    min_mentions: int = 2,
    max_objects: int = 60,
) -> dict[str, Any]:
    """Run canonical Phase 4.6.2 Entity & Concept Intelligence."""

    intake = validate_entity_concept_intake_v1(
        runtime_reader_result
    )

    objects = build_entity_concept_objects_v1(
        runtime_reader_result,
        min_mentions=min_mentions,
        max_objects=max_objects,
    )

    if (
        objects.get("status")
        != "ENTITY_CONCEPT_OBJECTS_BUILT"
    ):
        raise EntityConceptIntelligenceError(
            "Entity/concept semantic objects were not successfully built."
        )

    semantic_objects = objects.get("semantic_objects")

    if not isinstance(semantic_objects, list):
        raise EntityConceptIntelligenceError(
            "Entity/concept semantic object collection is invalid."
        )

    if not semantic_objects:
        raise EntityConceptIntelligenceError(
            "Entity & Concept Intelligence produced no semantic objects."
        )

    for item in semantic_objects:
        if not isinstance(item, Mapping):
            raise EntityConceptIntelligenceError(
                "Invalid semantic object in Entity & Concept Intelligence output."
            )

        canonical_text = item.get("canonical_text")
        semantic_kind = item.get("semantic_kind")
        confidence = item.get("extraction_confidence")

        if (
            not isinstance(canonical_text, str)
            or not canonical_text.strip()
        ):
            raise EntityConceptIntelligenceError(
                "Semantic object is missing canonical_text."
            )

        if semantic_kind not in {"entity", "concept"}:
            raise EntityConceptIntelligenceError(
                "Semantic object has invalid semantic_kind."
            )

        if (
            not isinstance(confidence, (int, float))
            or confidence < 0.0
            or confidence > 1.0
        ):
            raise EntityConceptIntelligenceError(
                "Semantic object has invalid extraction_confidence."
            )

    return {
        "schema_version":
            "entity_concept_intelligence_result_v1",
        "engine_version":
            ENTITY_CONCEPT_INTELLIGENCE_VERSION,
        "phase":
            "4.6.2",
        "status":
            "ENTITY_CONCEPT_INTELLIGENCE_COMPLETE",
        "workspace_id":
            intake.get("workspace_id"),
        "document_id":
            intake.get("document_id"),
        "source_type":
            intake.get("source_type"),
        "source_id":
            intake.get("source_id"),
        "content_hash":
            intake.get("content_hash"),
        "body_ref":
            intake.get("body_ref"),
        "article_id":
            intake.get("article_id"),
        "title":
            intake.get("title"),
        "final_primary_topic":
            intake.get("final_primary_topic"),
        "raw_mention_count":
            objects["raw_mention_count"],
        "semantic_object_count":
            objects["semantic_object_count"],
        "entity_count":
            objects["entity_count"],
        "concept_count":
            objects["concept_count"],
        "semantic_objects":
            semantic_objects,
        "canonicalization":
            objects["canonicalization"],
        "processing_boundaries": {
            "article_local_only":
                True,
            "global_vocabulary_write_performed":
                False,
            "semantic_memory_write_performed":
                False,
            "phrase_neighborhood_intelligence_performed":
                False,
            "topic_intent_intelligence_performed":
                False,
            "reasoning_performed":
                False,
            "ontology_alignment_performed":
                False,
            "learning_performed":
                False,
            "link_scoring_performed":
                False,
            "target_resolution_performed":
                False,
            "highlighting_performed":
                False,
        },
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "phrase_neighborhood_intelligence",
    }


def validate_entity_concept_intake_v1(
    runtime_reader_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate the canonical 4.6.1 -> 4.6.2 handoff."""

    if not isinstance(runtime_reader_result, Mapping):
        raise EntityConceptIntelligenceError(
            "runtime_reader_result must be a mapping."
        )

    if (
        runtime_reader_result.get("schema_version")
        != "semantic_intelligence_runtime_reader_result_v1"
    ):
        raise EntityConceptIntelligenceError(
            "Unsupported Semantic Runtime Reader result schema."
        )

    if (
        runtime_reader_result.get("status")
        != "SEMANTIC_RUNTIME_READING_COMPLETE"
    ):
        raise EntityConceptIntelligenceError(
            "Semantic Runtime Reader is not complete."
        )

    if (
        runtime_reader_result.get("next_stage")
        != "entity_and_concept_intelligence"
    ):
        raise EntityConceptIntelligenceError(
            "Runtime Reader is not authorized to hand off to "
            "Entity & Concept Intelligence."
        )

    readiness = runtime_reader_result.get(
        "semantic_readiness"
    )

    if (
        not isinstance(readiness, Mapping)
        or readiness.get("eligible") is not True
        or readiness.get("readiness_status") != "READY"
    ):
        raise EntityConceptIntelligenceError(
            "Semantic Readiness evidence is not READY."
        )

    body_verification = runtime_reader_result.get(
        "body_verification"
    )

    if (
        not isinstance(body_verification, Mapping)
        or body_verification.get("verification_status") != "VERIFIED"
    ):
        raise EntityConceptIntelligenceError(
            "Canonical Body Store verification is not VERIFIED."
        )

    semantic_reading_model = runtime_reader_result.get(
        "semantic_reading_model"
    )

    if not isinstance(semantic_reading_model, Mapping):
        raise EntityConceptIntelligenceError(
            "Semantic Reading Model is missing."
        )

    structural_validation = semantic_reading_model.get(
        "validation"
    )

    if (
        not isinstance(structural_validation, Mapping)
        or structural_validation.get("valid") is not True
    ):
        raise EntityConceptIntelligenceError(
            "Semantic Reading Model failed structural validation."
        )

    if (
        semantic_reading_model.get("structure_source")
        != "canonical_uucd"
    ):
        raise EntityConceptIntelligenceError(
            "Entity & Concept Intelligence requires canonical UUCD "
            "structural evidence."
        )

    final_orientation = runtime_reader_result.get(
        "final_domain_topic_reconciliation"
    )

    if (
        not isinstance(final_orientation, Mapping)
        or final_orientation.get("status")
        != "FINAL_ORIENTATION_RECONCILED"
        or final_orientation.get("topic_reconciled") is not True
    ):
        raise EntityConceptIntelligenceError(
            "Final domain/topic orientation is not reconciled."
        )

    article = semantic_reading_model.get("article")

    if not isinstance(article, Mapping):
        raise EntityConceptIntelligenceError(
            "Semantic Reading Model article identity is missing."
        )

    article_id = article.get("article_id")

    if not isinstance(article_id, str) or not article_id.strip():
        raise EntityConceptIntelligenceError(
            "Canonical article_id is missing."
        )

    blocks = semantic_reading_model.get("blocks")

    if not isinstance(blocks, list) or not blocks:
        raise EntityConceptIntelligenceError(
            "No canonical article blocks are available."
        )

    if (
        runtime_reader_result.get(
            "entity_concept_intelligence_performed"
        )
        is not False
    ):
        raise EntityConceptIntelligenceError(
            "Runtime Reader contract incorrectly indicates that "
            "Entity & Concept Intelligence was already performed."
        )

    return {
        "schema_version":
            "entity_concept_intelligence_intake_v1",
        "phase":
            "4.6.2",
        "status":
            "ENTITY_CONCEPT_INTAKE_ACCEPTED",
        "workspace_id":
            runtime_reader_result.get("workspace_id"),
        "document_id":
            runtime_reader_result.get("document_id"),
        "source_type":
            runtime_reader_result.get("source_type"),
        "source_id":
            runtime_reader_result.get("source_id"),
        "content_hash":
            runtime_reader_result.get("content_hash"),
        "body_ref":
            runtime_reader_result.get("body_ref"),
        "article_id":
            article_id,
        "title":
            article.get("title"),
        "final_primary_topic":
            final_orientation.get("final_primary_topic"),
        "canonical_block_count":
            len(blocks),
        "canonical_section_count":
            len(semantic_reading_model.get("sections") or []),
        "canonical_structure_verified":
            True,
        "semantic_readiness_verified":
            True,
        "body_store_verified":
            True,
        "intake_authorized":
            True,
        "next_stage":
            "entity_discovery",
    }


__all__ = [
    "ENTITY_CONCEPT_INTELLIGENCE_VERSION",
    "EntityConceptIntelligenceError",
    "load_semantic_vocabularies_v1",
    "detect_entity_concept_mentions_v1",
    "build_entity_concept_objects_v1",
    "run_entity_concept_intelligence_v1",
    "validate_entity_concept_intake_v1",
]

