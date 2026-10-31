"""Phase 3.7.7 ? evidence-grounded reasoning signal association.

Uses existing cross-document reasoning observations.
Document context is never promoted into phrase-level semantic proof.
"""

from collections.abc import Mapping
from copy import deepcopy


def associate_reasoning_signals(candidate, retrieval, *, expected_workspace_id=None):
    result = {
        "schema_version": "reasoning_signal_association_v1",
        "status": "unavailable",
        "source": "workspace_cross_document_reasoning",
        "phrase_context_verified": False,
        "matched_documents": [],
        "document_relationships": [],
        "reasoning_observations": [],
        "confidence": None,
        "confidence_status": "not_established",
        "phrase_level_semantic_proof": False,
        "certified": False,
        "automatic_linking_authorized": False,
        "linking_decision_performed": False,
    }

    if not isinstance(candidate, Mapping):
        return result

    occurrence = candidate.get("selection_source_span")
    sentence = candidate.get("selection_sentence_context")
    phrase = candidate.get("phrase")

    if (
        candidate.get("selection_source_span_status") != "verified"
        or candidate.get("selection_sentence_context_status")
            != "derived_from_verified_span"
        or not isinstance(occurrence, Mapping)
        or not isinstance(sentence, Mapping)
        or not isinstance(phrase, str)
        or not phrase.strip()
        or occurrence.get("coordinate_space") != "original_article"
        or sentence.get("coordinate_space") != "original_article"
    ):
        return result

    os_, oe = occurrence.get("start"), occurrence.get("end")
    ss, se = sentence.get("start"), sentence.get("end")
    observed = occurrence.get("text")
    sentence_text = sentence.get("text")

    if (
        any(type(v) is not int for v in (os_, oe, ss, se))
        or not (0 <= ss <= os_ < oe <= se)
        or not isinstance(observed, str)
        or not isinstance(sentence_text, str)
        or len(observed) != oe - os_
        or len(sentence_text) != se - ss
        or sentence_text[os_ - ss:oe - ss] != observed
        or observed.casefold() != phrase.casefold()
    ):
        return result

    result["phrase_context_verified"] = True
    result["source_occurrence"] = {
        "phrase": phrase,
        "selection_occurrence_id": candidate.get(
            "selection_occurrence_id"
        ),
        "article_sha256": candidate.get(
            "selection_article_text_sha256"
        ),
        "source_span": {"start": os_, "end": oe},
        "sentence_span": {"start": ss, "end": se},
        "sentence": sentence_text,
    }

    if not isinstance(retrieval, Mapping):
        result["status"] = "source_verified_retrieval_unavailable"
        return result

    if (
        retrieval.get("status") not in (
            "no_evidence", "document_context_found"
        )
        or retrieval.get("certified") is not False
        or retrieval.get("phrase_level_semantic_proof") is not False
        or retrieval.get("linking_decision_performed") is not False
        or not isinstance(retrieval.get("phrase"), str)
        or " ".join(retrieval["phrase"].casefold().split())
            != " ".join(phrase.casefold().split())
        or not isinstance(retrieval.get("workspace_id"), str)
        or retrieval.get("source")
            != "workspace_cross_document_reasoning"
    ):
        result["status"] = "invalid"
        return result


    # reasoning_context_binding_guard_v1
    # Verify workspace ownership and source lineage before accepting
    # cross-document reasoning context.
    import re

    workspace = expected_workspace_id

    if workspace is None:
        workspace = candidate.get("workspace_id")

    if workspace is not None:
        if (
            not isinstance(workspace, str)
            or re.fullmatch(r"[A-Za-z0-9_-]{1,97}", workspace) is None
        ):
            result["status"] = "invalid"
            return result

        candidate_workspace = candidate.get("workspace_id")
        if (
            candidate_workspace is not None
            and candidate_workspace != workspace
        ):
            result["status"] = "invalid"
            return result

        if retrieval["workspace_id"] != workspace:
            result["status"] = "invalid"
            return result

    occurrence_id = candidate.get("selection_occurrence_id")
    if occurrence_id is not None and (
        not isinstance(occurrence_id, (str, int))
        or isinstance(occurrence_id, bool)
        or not str(occurrence_id).strip()
    ):
        result["status"] = "invalid"
        return result

    article_hash = candidate.get("selection_article_text_sha256")
    if article_hash is not None and (
        not isinstance(article_hash, str)
        or re.fullmatch(r"[0-9a-f]{64}", article_hash) is None
    ):
        result["status"] = "invalid"
        return result

    documents = retrieval.get("matched_documents")
    relationships = retrieval.get("document_relationships")
    observations = retrieval.get("reasoning_observations")

    if (
        not isinstance(documents, list)
        or not isinstance(relationships, list)
        or not isinstance(observations, list)
        or any(not isinstance(item, Mapping)
               for item in documents + relationships + observations)
    ):
        result["status"] = "invalid"
        return result

    if retrieval["status"] == "no_evidence":
        if documents or relationships or observations:
            result["status"] = "invalid"
        else:
            result["status"] = "no_evidence"
        return result

    if not documents:
        result["status"] = "invalid"
        return result

    matched_ids = set()
    for item in documents:
        doc_id = item.get("document_id")
        if (
            not isinstance(doc_id, str)
            or not doc_id
            or item.get("match_type") != "exact_document_phrase"
            or doc_id in matched_ids
        ):
            result["status"] = "invalid"
            return result
        matched_ids.add(doc_id)

    for relationship in relationships:
        left = str(relationship.get("left_document_id", ""))
        right = str(relationship.get("right_document_id", ""))
        if left not in matched_ids and right not in matched_ids:
            result["status"] = "invalid"
            return result


    # reasoning_confidence_preservation_v1
    # Preserve source relationship scores individually.
    # Never promote them to phrase-level semantic confidence.
    import math

    confidence_observations = []

    # A score describes the relationship returned by its source.
    # Absence of a score is not a zero score.
    for position, relationship in enumerate(relationships):
        record = {
            "relationship_index": position,
            "left_document_id": relationship.get("left_document_id"),
            "right_document_id": relationship.get("right_document_id"),
            "scope": "document_relationship_only",
            "phrase_level_confidence": None,
            "confidence_certified": False,
            "source_score_present": False,
            "source_score": None,
            "source_score_status": "not_provided",
        }

        if "score" in relationship:
            score = relationship["score"]

            if (
                isinstance(score, bool)
                or not isinstance(score, (int, float))
                or not math.isfinite(score)
                or not (0 <= score <= 1)
            ):
                result["status"] = "invalid"
                result["reason"] = "invalid_document_relationship_score"
                return result

            record["source_score_present"] = True
            record["source_score"] = score
            record["source_score_status"] = "preserved_unverified"

        confidence_observations.append(record)


    # reasoning_relationship_provenance_v1
    # Bind each source relationship to the exact retrieval context.
    # References are traceability records, not independent proof.
    relationship_provenance = []

    occurrence_id = candidate.get("selection_occurrence_id")
    occurrence_id = (
        str(occurrence_id) if occurrence_id is not None else None
    )

    for position, relationship in enumerate(relationships):
        left = relationship.get("left_document_id")
        right = relationship.get("right_document_id")

        if (
            not isinstance(left, (str, int))
            or isinstance(left, bool)
            or not str(left).strip()
            or not isinstance(right, (str, int))
            or isinstance(right, bool)
            or not str(right).strip()
        ):
            result["status"] = "invalid"
            result["reason"] = "invalid_relationship_provenance"
            return result

        # A retained relationship must connect at least one
        # document in the exact-phrase document match set.
        if str(left) not in matched_ids and str(right) not in matched_ids:
            result["status"] = "invalid"
            result["reason"] = "unrelated_relationship_provenance"
            return result

        record = {
            "relationship_index": position,
            "retrieval_source": retrieval["source"],
            "workspace_id": retrieval["workspace_id"],
            "selected_phrase": phrase,
            "selected_occurrence_id": occurrence_id,
            "article_sha256": candidate.get(
                "selection_article_text_sha256"
            ),
            "source_span": {"start": os_, "end": oe},
            "sentence_span": {"start": ss, "end": se},
            "left_document_id": str(left),
            "right_document_id": str(right),
            "matched_left_document": str(left) in matched_ids,
            "matched_right_document": str(right) in matched_ids,
            "source_relationship_reference": {
                "relationship_index": position,
                "left_document_id": str(left),
                "right_document_id": str(right),
            },
            "source_evidence_id": None,
            "independent_evidence_verified": False,
            "phrase_semantic_proof": False,
        }

        # Preserve an existing explicit evidence ID only if supplied
        # by the source; never synthesize one.
        if "evidence_id" in relationship:
            evidence_id = relationship["evidence_id"]
            if (
                not isinstance(evidence_id, str)
                or not evidence_id.strip()
            ):
                result["status"] = "invalid"
                result["reason"] = "invalid_source_evidence_id"
                return result
            record["source_evidence_id"] = evidence_id

        relationship_provenance.append(record)

    result["status"] = "document_context_found"
    result["workspace_id"] = retrieval["workspace_id"]
    result["matched_documents"] = deepcopy(documents)
    result["document_relationships"] = deepcopy(relationships)
    result["document_relationship_confidence"] = (
        confidence_observations
    )
    result["confidence"] = None
    result["confidence_status"] = (
        "document_scores_preserved_no_phrase_confidence"
    )
    result["reasoning_observations"] = deepcopy(observations)
    result["reasoning_scope"] = "document_context_only"
    result["document_relationship_provenance"] = (
        relationship_provenance
    )
    result["provenance_status"] = "source_references_preserved_unverified"
    result["provenance"] = {
        "retrieval_source": retrieval["source"],
        "workspace_id": retrieval["workspace_id"],
        "matched_document_ids": sorted(matched_ids),
        "source_occurrence_id": candidate.get(
            "selection_occurrence_id"
        ),
        "independent_phrase_proof": False,
    }
    return result
