"""Phase 3.7.6: provisional graph observation adapter.

Transforms previously attached, occurrence-bound semantic relationships
into nonauthoritative graph-compatible observations.

Does not retrieve, certify, or mutate Intelligence Graph records.
"""

from collections.abc import Mapping
from copy import deepcopy


SUPPORTED = {
    "synonym_of": "bidirectional",
    "narrower_than": "source_to_target",
}


def prepare_provisional_graph_observations(row):
    result = {
        "schema_version": "provisional_graph_observation_v1",
        "status": "unavailable",
        "observations": [],
        "source": "provisional_semantic_relationships",
        "certified": False,
        "graph_mutation_authorized": False,
        "graph_mutation_performed": False,
        "automatic_linking_authorized": False,
        "linking_decision_performed": False,
    }

    if not isinstance(row, Mapping):
        return result

    semantic = row.get("semantic_context")
    if not isinstance(semantic, Mapping):
        return result

    parent = semantic.get("provisional_semantic_relationships")
    if not isinstance(parent, Mapping):
        return result

    parent_status = parent.get("status")
    if parent_status != "supported_unverified":
        result["status"] = (
            parent_status
            if parent_status in (
                "no_evidence", "ambiguous", "invalid", "unavailable"
            )
            else "unavailable"
        )
        return result

    lineage = parent.get("lineage")
    relations = parent.get("relationships")

    if not isinstance(lineage, Mapping) or not isinstance(relations, list):
        result["status"] = "invalid"
        return result

    if (
        lineage.get("schema_version") != "semantic_relationship_lineage_v1"
        or lineage.get("source_observation_verified") is not True
        or lineage.get("semantic_claim_certified") is not False
        or lineage.get("source_coordinate_space") != "original_article"
        or not isinstance(lineage.get("evidence_fingerprint"), str)
        or len(lineage["evidence_fingerprint"]) != 64
        or not isinstance(lineage.get("source_sentence"), str)
        or parent.get("certified") is not False
        or parent.get("automatic_linking_authorized") is not False
        or parent.get("graph_mutation_performed") is not False
    ):
        result["status"] = "invalid"
        return result

    index = row.get("candidate_index")
    if type(index) is not int or lineage.get("candidate_index") != index:
        result["status"] = "invalid"
        return result

    original = row.get("original_candidate")
    if not isinstance(original, Mapping):
        result["status"] = "invalid"
        return result

    occurrence = original.get("selection_source_span")
    sentence = original.get("selection_sentence_context")

    if (
        original.get("selection_source_span_status") != "verified"
        or original.get("selection_sentence_context_status")
            != "derived_from_verified_span"
        or not isinstance(occurrence, Mapping)
        or not isinstance(sentence, Mapping)
        or occurrence.get("coordinate_space") != "original_article"
        or sentence.get("coordinate_space") != "original_article"
        or lineage.get("selection_occurrence_id")
            != original.get("selection_occurrence_id")
        or lineage.get("source_phrase") != original.get("phrase")
        or lineage.get("source_sentence") != sentence.get("text")
        or lineage.get("source_span") != {
            "start": occurrence.get("start"),
            "end": occurrence.get("end"),
        }
        or lineage.get("sentence_span") != {
            "start": sentence.get("start"),
            "end": sentence.get("end"),
        }
    ):
        result["status"] = "invalid"
        return result


    # graph_observation_identity_guard_v1
    # Validate actual sentence-to-occurrence ownership before
    # promoting a provisional relationship to a graph observation.
    import re

    fingerprint = lineage["evidence_fingerprint"]
    os_, oe = occurrence.get("start"), occurrence.get("end")
    ss, se = sentence.get("start"), sentence.get("end")
    observed = occurrence.get("text")
    sentence_text = sentence.get("text")
    phrase = original.get("phrase")

    if (
        re.fullmatch(r"[0-9a-f]{64}", fingerprint) is None
        or any(type(v) is not int for v in (os_, oe, ss, se))
        or not (0 <= ss <= os_ < oe <= se)
        or not isinstance(observed, str)
        or not isinstance(sentence_text, str)
        or not isinstance(phrase, str)
        or len(observed) != oe - os_
        or len(sentence_text) != se - ss
        or sentence_text[os_ - ss:oe - ss] != observed
        or observed.casefold() != phrase.casefold()
        or not isinstance(lineage.get("source_span"), dict)
        or not isinstance(lineage.get("sentence_span"), dict)
    ):
        result["status"] = "invalid"
        return result


    # graph_evidence_lineage_readiness_v1
    # Recompute the Phase 3.7.5 fingerprint from the original
    # occurrence. This detects inconsistent lineage records;
    # it is not cryptographic authentication of source truth.
    import hashlib
    import json

    def normalized_identifier(value):
        if isinstance(value, (str, int)) and str(value).strip():
            return value
        return None

    article_hash = original.get("selection_article_text_sha256")
    if not isinstance(article_hash, str) or not article_hash.strip():
        article_hash = None

    identity = {
        "workspace_id": original.get("workspace_id"),
        "document_id": original.get("doc_id"),
        "candidate_id": normalized_identifier(
            original.get("upstream_candidate_id")
        ),
        "candidate_index": index,
        "occurrence_id": normalized_identifier(
            original.get("selection_occurrence_id")
        ),
        "article_sha256": article_hash,
        "phrase": original.get("phrase"),
        "occurrence_start": os_,
        "occurrence_end": oe,
        "sentence_start": ss,
        "sentence_end": se,
        "sentence_text": sentence_text,
    }

    recalculated = hashlib.sha256(
        json.dumps(
            identity,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    if (
        lineage.get("evidence_fingerprint") != recalculated
        or lineage.get("candidate_id") != identity["candidate_id"]
        or lineage.get("candidate_index") != index
        or lineage.get("selection_occurrence_id")
            != identity["occurrence_id"]
        or lineage.get("workspace_id") != identity["workspace_id"]
        or lineage.get("document_id") != identity["document_id"]
        or lineage.get("article_sha256") != identity["article_sha256"]
        or lineage.get("interpretation_method")
            != "explicit_sentence_pattern_v1"
        or parent.get("linking_decision_performed") is not False
        or not isinstance(relations, list)
        or len(relations) == 0
    ):
        result["status"] = "invalid"
        result["reason"] = "graph_evidence_lineage_mismatch"
        return result

    prepared = []
    seen = set()

    for relation_index, rel in enumerate(relations):
        if not isinstance(rel, Mapping):
            result["status"] = "invalid"
            return result

        kind = rel.get("relation_type")
        left = rel.get("source_concept_surface")
        right = rel.get("target_concept_surface")
        evidence_id = rel.get("evidence_id")

        if (
            kind not in SUPPORTED
            or rel.get("direction") != SUPPORTED.get(kind)
            or rel.get("interpretation_status") != "supported_unverified"
            or rel.get("certified") is not False
            or rel.get("source_candidate_index") != index
            or rel.get("selection_occurrence_id")
                != lineage.get("selection_occurrence_id")
            or rel.get("evidence_fingerprint")
                != lineage.get("evidence_fingerprint")
            or rel.get("source_span") != lineage.get("source_span")
            or rel.get("sentence_span") != lineage.get("sentence_span")
            or rel.get("evidence_sentence") != lineage.get("source_sentence")
            or not isinstance(evidence_id, str)
            or not evidence_id.startswith(
                "semantic_relation:" + lineage["evidence_fingerprint"] + ":"
            )
            or evidence_id in seen
            or re.fullmatch(
                r"semantic_relation:"
                + re.escape(lineage["evidence_fingerprint"])
                + r":[0-9]+",
                evidence_id,
            ) is None
            or not isinstance(left, str)
            or not isinstance(right, str)
            or not left.strip()
            or not right.strip()
            or left.strip().casefold() == right.strip().casefold()
            or rel.get("selected_endpoint") not in ("source", "target")
        ):
            result["status"] = "invalid"
            result["observations"] = []
            return result

        selected_surface = (
            left if rel["selected_endpoint"] == "source" else right
        )
        if selected_surface.casefold() != original["phrase"].casefold():
            result["status"] = "invalid"
            result["observations"] = []
            return result

        expected_id = (
            "semantic_relation:"
            + recalculated
            + ":"
            + str(relation_index)
        )

        if (
            evidence_id != expected_id
            or rel.get("interpretation_method")
                != "explicit_sentence_pattern_v1"
            or rel.get("evidence_quote") not in sentence_text
        ):
            result["status"] = "invalid"
            result["reason"] = "graph_relationship_evidence_mismatch"
            result["observations"] = []
            return result

        seen.add(evidence_id)

        prepared.append({
            "observation_id": "graph_observation:" + evidence_id,
            "source_node": {
                "surface": left.strip(),
                "canonical_concept_id": None,
                "resolution_status": "unresolved",
            },
            "target_node": {
                "surface": right.strip(),
                "canonical_concept_id": None,
                "resolution_status": "unresolved",
            },
            "relation_type": kind,
            "direction": SUPPORTED[kind],
            "selected_endpoint": rel["selected_endpoint"],
            "candidate_index": index,
            "selection_occurrence_id": lineage.get(
                "selection_occurrence_id"
            ),
            "source_evidence_id": evidence_id,
            "evidence_fingerprint": lineage["evidence_fingerprint"],
            "source_span": deepcopy(lineage["source_span"]),
            "sentence_span": deepcopy(lineage["sentence_span"]),
            "source_sentence": lineage["source_sentence"],
            "observation_status": "supported_unverified",
            "graph_evidence_readiness": "requires_independent_validation",
            "independent_validation_status": "not_performed",
            "node_resolution_status": "unresolved",
            "graph_edge_authorized": False,
            "certified": False,
            "graph_mutation_authorized": False,
            "automatic_linking_authorized": False,
        })

    result["status"] = (
        "supported_unverified" if prepared else "no_evidence"
    )
    result["observations"] = prepared
    return result



def attach_provisional_graph_observations(enriched_candidates):
    """Attach graph observations without modifying authoritative graph evidence."""
    if not isinstance(enriched_candidates, list):
        raise TypeError("Expected enriched candidate list")

    for row in enriched_candidates:
        if not isinstance(row, dict):
            continue

        semantic = row.get("semantic_context")
        if not isinstance(semantic, dict):
            continue

        # An existing field is owned by its producer. Never replace it.
        if "provisional_graph_relationships" in semantic:
            continue

        semantic["provisional_graph_relationships"] = (
            prepare_provisional_graph_observations(row)
        )

    return enriched_candidates
