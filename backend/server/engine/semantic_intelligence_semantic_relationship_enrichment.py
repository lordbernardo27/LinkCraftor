"""Phase 3.7.5: explicit, source-grounded semantic relationships.

No inferred synonyms, graph edges, URL decisions or certification.
"""

import re
from collections.abc import Mapping


_PATTERNS = (
    (
        "synonym",
        re.compile(
            r"(?P<left>[A-Za-z][A-Za-z0-9 -]{1,70}?)"
            r"\s+is also known as\s+"
            r"(?P<right>[A-Za-z][A-Za-z0-9 -]{1,70}?)"
            r"(?=[.;]|$)",
            re.IGNORECASE,
        ),
    ),
    (
        "type_of",
        re.compile(
            r"(?P<left>[A-Za-z][A-Za-z0-9 -]{1,70}?)"
            r"\s+is a type of\s+"
            r"(?P<right>[A-Za-z][A-Za-z0-9 -]{1,70}?)"
            r"(?=[.;]|$)",
            re.IGNORECASE,
        ),
    ),
)


def enrich_explicit_semantic_relationship(candidate):
    """Interpret only a verified Selector-owned occurrence."""

    result = {
        "schema_version": "semantic_relationship_v1",
        "status": "unavailable",
        "relationships": [],
        "certified": False,
        "automatic_linking_authorized": False,
        "linking_decision_performed": False,
        "graph_mutation_performed": False,
    }

    if not isinstance(candidate, Mapping):
        return result

    phrase = candidate.get("phrase")
    occurrence = candidate.get("selection_source_span")
    sentence = candidate.get("selection_sentence_context")

    if (
        candidate.get("selection_source_span_status") != "verified"
        or candidate.get("selection_sentence_context_status")
            != "derived_from_verified_span"
        or not isinstance(phrase, str)
        or not phrase.strip()
        or not isinstance(occurrence, Mapping)
        or not isinstance(sentence, Mapping)
    ):
        return result

    if (
        occurrence.get("coordinate_space") != "original_article"
        or sentence.get("coordinate_space") != "original_article"
    ):
        return result

    os_, oe = occurrence.get("start"), occurrence.get("end")
    ss, se = sentence.get("start"), sentence.get("end")
    observed = occurrence.get("text")
    text = sentence.get("text")

    if (
        any(type(x) is not int for x in (os_, oe, ss, se))
        or not (0 <= ss <= os_ < oe <= se)
        or not isinstance(observed, str)
        or not isinstance(text, str)
        or len(observed) != oe - os_
        or len(text) != se - ss
        or text[os_ - ss:oe - ss] != observed
        or observed.casefold() != phrase.casefold()
    ):
        return result


    # semantic_relation_uncertainty_guard_v1
    # Conservative sentence-scope abstention. This is not a
    # full negation-scope or linguistic reasoning system.
    uncertainty_patterns = (
        r"\b(?:dispute|disputes|disputed|disputing|"
        r"debate|debated|whether|unclear|uncertain|"
        r"controversial|contested)\b",
        r"\b(?:alleged|allegedly|claimed|claims|"
        r"claiming|hypothetical|hypothetically|"
        r"possibly|perhaps|might|may|could)\b",
    )

    negation_patterns = (
        r"\b(?:not|never|incorrect|false|untrue|"
        r"misleading|misconception|myth)\b",
        r"\b(?:isn't|aren't|wasn't|weren't|"
        r"doesn't|don't|didn't|cannot|can't)\b",
    )

    if any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in uncertainty_patterns
    ):
        result["status"] = "ambiguous"
        result["reason"] = "disputed_or_qualified_statement"
        return result

    if any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in negation_patterns
    ):
        result["status"] = "no_evidence"
        result["reason"] = "negated_or_rejected_statement"
        return result

    # A quoted assertion is not necessarily endorsed by its author.
    # Abstain on explicit quotation marks rather than promoting
    # an attributed statement to an affirmative relationship.
    if any(mark in text for mark in ('"', "\u201c", "\u201d")):
        result["status"] = "no_evidence"
        result["reason"] = "quoted_statement_requires_attribution"
        return result

    result["status"] = "no_evidence"

    matches = []

    for kind, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            left = match.group("left").strip()
            right = match.group("right").strip()

            # The selected occurrence must be exactly one endpoint,
            # not merely another mention in the same sentence.
            local_start = os_ - ss
            local_end = oe - ss
            endpoints = (
                (match.start("left"), match.end("left"), left),
                (match.start("right"), match.end("right"), right),
            )

            selected_endpoint = None
            for position, (start, end, value) in enumerate(endpoints):
                if (
                    start == local_start
                    and end == local_end
                    and value.casefold() == phrase.casefold()
                ):
                    selected_endpoint = position
                    break

            if selected_endpoint is None:
                continue

            if left.casefold() == right.casefold():
                continue

            matches.append({
                "relation_type": (
                    "synonym_of" if kind == "synonym"
                    else "narrower_than"
                ),
                "source_concept_surface": left,
                "target_concept_surface": right,
                "selected_endpoint": (
                    "source" if selected_endpoint == 0 else "target"
                ),
                "evidence_quote": match.group(0),
                "evidence_sentence": text,
                "source_span": {"start": os_, "end": oe},
                "sentence_span": {"start": ss, "end": se},
                "interpretation_status": "supported_unverified",
                "certified": False,
            })

    if len(matches) == 1:
        result["status"] = "supported_unverified"
        result["relationships"] = matches
    elif len(matches) > 1:
        result["status"] = "ambiguous"

    return result





def _semantic_relationship_lineage(candidate, index, result):
    """Build occurrence-bound provenance without certifying a relationship."""
    import hashlib
    import json

    if not isinstance(candidate, Mapping):
        return None

    if not isinstance(result, Mapping):
        return None

    occurrence = candidate.get("selection_source_span")
    sentence = candidate.get("selection_sentence_context")

    if not isinstance(occurrence, Mapping) or not isinstance(sentence, Mapping):
        return None

    if (
        candidate.get("selection_source_span_status") != "verified"
        or candidate.get("selection_sentence_context_status")
            != "derived_from_verified_span"
    ):
        return None

    os_, oe = occurrence.get("start"), occurrence.get("end")
    ss, se = sentence.get("start"), sentence.get("end")
    ot, st = occurrence.get("text"), sentence.get("text")
    phrase = candidate.get("phrase")

    if (
        any(type(v) is not int for v in (os_, oe, ss, se))
        or not (0 <= ss <= os_ < oe <= se)
        or not isinstance(ot, str)
        or not isinstance(st, str)
        or not isinstance(phrase, str)
        or not (phrase and ot)
        or len(ot) != oe - os_
        or len(st) != se - ss
        or st[os_ - ss:oe - ss] != ot
        or phrase.casefold() != ot.casefold()
        or occurrence.get("coordinate_space") != "original_article"
        or sentence.get("coordinate_space") != "original_article"
    ):
        return None

    occurrence_id = candidate.get("selection_occurrence_id")
    if not isinstance(occurrence_id, (str, int)) or not str(
        occurrence_id
    ).strip():
        occurrence_id = None

    candidate_id = candidate.get("upstream_candidate_id")
    if not isinstance(candidate_id, (str, int)) or not str(
        candidate_id
    ).strip():
        candidate_id = None

    article_hash = candidate.get("selection_article_text_sha256")
    if not isinstance(article_hash, str) or not article_hash.strip():
        article_hash = None

    workspace_id = candidate.get("workspace_id")
    doc_id = candidate.get("doc_id")

    identity = {
        "workspace_id": workspace_id,
        "document_id": doc_id,
        "candidate_id": candidate_id,
        "candidate_index": index,
        "occurrence_id": occurrence_id,
        "article_sha256": article_hash,
        "phrase": phrase,
        "occurrence_start": os_,
        "occurrence_end": oe,
        "sentence_start": ss,
        "sentence_end": se,
        "sentence_text": st,
    }

    fingerprint = hashlib.sha256(
        json.dumps(
            identity, sort_keys=True, ensure_ascii=False,
            separators=(",", ":"), default=str
        ).encode("utf-8")
    ).hexdigest()

    return {
        "schema_version": "semantic_relationship_lineage_v1",
        "candidate_id": candidate_id,
        "candidate_index": index,
        "selection_occurrence_id": occurrence_id,
        "workspace_id": workspace_id,
        "document_id": doc_id,
        "article_sha256": article_hash,
        "source_coordinate_space": "original_article",
        "source_span": {"start": os_, "end": oe},
        "sentence_span": {"start": ss, "end": se},
        "source_phrase": phrase,
        "source_sentence": st,
        "interpretation_method": "explicit_sentence_pattern_v1",
        "evidence_fingerprint": fingerprint,
        "source_observation_verified": True,
        "semantic_claim_certified": False,
        "automatic_linking_authorized": False,
    }


def attach_provisional_semantic_relationships(enriched_candidates):
    """Attach nonauthoritative relationships without replacing prior evidence.

    Source: each candidate's original Selector-verified occurrence.
    No candidate deletion, graph mutation, scoring or linking.
    """
    if not isinstance(enriched_candidates, list):
        raise TypeError("Expected enriched candidate list")

    for candidate_index, row in enumerate(enriched_candidates):
        if not isinstance(row, dict):
            continue

        semantic = row.get("semantic_context")
        original = row.get("original_candidate")

        if not isinstance(semantic, dict):
            continue

        # Never overwrite an existing field, regardless of its value.
        if "provisional_semantic_relationships" in semantic:
            continue

        if not isinstance(original, dict):
            semantic["provisional_semantic_relationships"] = {
                "schema_version": "semantic_relationship_v1",
                "status": "unavailable",
                "reason": "original_candidate_missing",
                "relationships": [],
                "certified": False,
                "automatic_linking_authorized": False,
                "linking_decision_performed": False,
                "graph_mutation_performed": False,
            }
            continue

        result = enrich_explicit_semantic_relationship(original)

        # Never promote heuristic relationships to certified evidence.
        result["certified"] = False
        result["automatic_linking_authorized"] = False
        result["linking_decision_performed"] = False
        result["graph_mutation_performed"] = False

        # Lineage is created only from a verified original occurrence.
        lineage = _semantic_relationship_lineage(
            original, candidate_index, result
        )

        if lineage is not None:
            relationships = result.get("relationships")

            if isinstance(relationships, list):
                for relation_index, relationship in enumerate(relationships):
                    if not isinstance(relationship, dict):
                        continue

                    # A matched relationship must refer to this exact
                    # sentence and selected source occurrence.
                    if (
                        relationship.get("evidence_sentence")
                            != lineage["source_sentence"]
                        or relationship.get("source_span")
                            != lineage["source_span"]
                        or relationship.get("sentence_span")
                            != lineage["sentence_span"]
                    ):
                        result["status"] = "invalid"
                        result["reason"] = "relationship_lineage_mismatch"
                        result["relationships"] = []
                        break

                    relationship["evidence_id"] = (
                        "semantic_relation:"
                        + lineage["evidence_fingerprint"]
                        + ":"
                        + str(relation_index)
                    )
                    relationship["evidence_fingerprint"] = (
                        lineage["evidence_fingerprint"]
                    )
                    relationship["source_candidate_index"] = candidate_index
                    relationship["selection_occurrence_id"] = (
                        lineage["selection_occurrence_id"]
                    )
                    relationship["interpretation_method"] = (
                        lineage["interpretation_method"]
                    )
                    relationship["direction"] = (
                        "bidirectional"
                        if relationship.get("relation_type") == "synonym_of"
                        else "source_to_target"
                    )
                    relationship["certified"] = False

            result["lineage"] = lineage

        semantic["provisional_semantic_relationships"] = result

    return enriched_candidates
