"""Phase 4 I4-A3: Original Scorer input assembly.

Reuses the existing Phase 3.7 advisory handoff.
Adds validated document and existing-link capacity context.
Does not bind phrase occurrences, score, classify, or insert links.
"""

from __future__ import annotations

from copy import deepcopy

from backend.server.engine.scorer_document_contract import (
    validate_scorer_document_contract,
)
from backend.server.engine.scorer_existing_link_profile import (
    evaluate_existing_link_capacity,
)
from backend.server.engine.semantic_enricher_scorer_handoff import (
    prepare_original_scorer_handoff,
)


class ScorerInputBridgeError(ValueError):
    pass


def prepare_scorer_input_foundation(
    *,
    enrichment_package,
    document,
    existing_link_profile,
):
    """Produce a fail-closed input foundation for the new Scorer."""

    validated = validate_scorer_document_contract(document)

    if not isinstance(enrichment_package, dict):
        raise ScorerInputBridgeError(
            "enrichment package must be a mapping"
        )

    context = enrichment_package.get("context")

    if not isinstance(context, dict):
        raise ScorerInputBridgeError(
            "Enricher context is missing"
        )

    if context.get("workspace_id") != validated["workspace_id"]:
        raise ScorerInputBridgeError(
            "Enricher workspace differs from document"
        )

    # Reuse Phase 3.7 rather than reimplementing its
    # candidate lineage and evidence checks.
    handoff = prepare_original_scorer_handoff(
        enrichment_package=enrichment_package
    )

    if (
        handoff.get("ok") is not True
        or handoff.get("consumer") != "original_scorer"
        or handoff.get("production_scorer_invoked") is not False
        or handoff.get("scoring_performed") is not False
        or handoff.get("highlight_allocation_performed") is not False
        or handoff.get("linking_performed") is not False
        or handoff.get("candidates_removed") != 0
        or handoff.get("candidates_forwarded")
        != handoff.get("candidates_received")
    ):
        raise ScorerInputBridgeError(
            "Phase 3.7 handoff safety boundary mismatch"
        )

    # Validate both the document and existing-link profile,
    # including unchanged hyperlink inventory and capacity.
    capacity = evaluate_existing_link_capacity(
        existing_link_profile,
        validated,
    )

    if (
        capacity.get("automatic_linking_authorized") is not False
        or capacity.get("scorer_selection_performed") is not False
    ):
        raise ScorerInputBridgeError(
            "Unexpected capacity-stage execution authority"
        )

    return {
        "bridge_version": "linkcraftor_scorer_input_v1",
        "consumer": "original_scorer",
        "status": "foundation_prepared_occurrences_unbound",
        "document_identity": {
            "workspace_id": validated["workspace_id"],
            "document_id": validated["document_id"],
            "content_version": validated["content_version"],
            "content_sha256": validated["content_sha256"],
            "source_format": validated["source_format"],
        },
        "semantic_handoff": deepcopy(handoff),
        "existing_link_profile": deepcopy(existing_link_profile),
        "link_capacity": deepcopy(capacity),
        "candidate_count": handoff["candidates_forwarded"],
        "candidate_order_preserved": True,
        "candidate_occurrence_binding_verified": False,
        "original_source_insertion_verified": False,
        "relationship_evidence_authenticated": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }


def bind_scorer_candidate_occurrences(
    *, foundation, document, occurrences
):
    """Validate explicitly supplied canonical occurrence locations.

    No text-search fallback, ranking, or source insertion.
    Structural matching does not authenticate upstream provenance.
    """
    validated = validate_scorer_document_contract(document)

    if not isinstance(foundation, dict):
        raise ScorerInputBridgeError("foundation must be a mapping")

    if (
        foundation.get("bridge_version")
        != "linkcraftor_scorer_input_v1"
        or foundation.get("consumer") != "original_scorer"
        or foundation.get("automatic_linking_authorized") is not False
        or foundation.get("scorer_decision_performed") is not False
        or foundation.get("candidate_occurrence_binding_verified")
        is not False
    ):
        raise ScorerInputBridgeError("unsafe or invalid foundation")

    identity = foundation.get("document_identity")
    if not isinstance(identity, dict):
        raise ScorerInputBridgeError("missing document identity")

    for field in (
        "workspace_id", "document_id", "content_version",
        "content_sha256", "source_format",
    ):
        if identity.get(field) != validated.get(field):
            raise ScorerInputBridgeError(
                "document identity mismatch: " + field
            )

    handoff = foundation.get("semantic_handoff")
    if not isinstance(handoff, dict):
        raise ScorerInputBridgeError("missing semantic handoff")

    candidates = handoff.get("candidates")
    if (
        not isinstance(candidates, list)
        or foundation.get("candidate_count") != len(candidates)
        or handoff.get("candidates_forwarded") != len(candidates)
        or handoff.get("candidates_removed") != 0
    ):
        raise ScorerInputBridgeError(
            "candidate lineage count mismatch"
        )

    if not isinstance(occurrences, list):
        raise ScorerInputBridgeError("occurrences must be a list")

    if len(occurrences) != len(candidates):
        raise ScorerInputBridgeError(
            "one explicit occurrence required per candidate"
        )

    regions = {
        region["region_id"]: region
        for region in validated["regions"]
        if region.get("eligible_for_linking") is True
    }

    canonical = validated["canonical_text"]
    seen_locations = set()
    checked = []

    for index, (candidate, occurrence) in enumerate(
        zip(candidates, occurrences)
    ):
        if not isinstance(candidate, dict):
            raise ScorerInputBridgeError("invalid candidate")

        if not isinstance(occurrence, dict):
            raise ScorerInputBridgeError("invalid occurrence")

        if candidate.get("candidate_index") != index:
            raise ScorerInputBridgeError(
                "candidate order mismatch"
            )

        candidate_id = candidate.get("candidate_id")

        if (
            occurrence.get("candidate_index") != index
            or occurrence.get("candidate_id") != candidate_id
        ):
            raise ScorerInputBridgeError(
                "occurrence identity mismatch"
            )

        original_candidate = candidate.get("original_candidate")
        if not isinstance(original_candidate, dict):
            raise ScorerInputBridgeError(
                "missing original candidate"
            )

        phrase = original_candidate.get("phrase")
        start = occurrence.get("char_start")
        end = occurrence.get("char_end")
        region_id = occurrence.get("region_id")

        if (
            not isinstance(phrase, str)
            or not phrase
            or type(start) is not int
            or type(end) is not int
            or not 0 <= start < end <= len(canonical)
            or canonical[start:end] != phrase
            or occurrence.get("text") != phrase
        ):
            raise ScorerInputBridgeError(
                "phrase or canonical offsets mismatch"
            )

        region = regions.get(region_id)

        if (
            region is None
            or not region["char_start"] <= start
            or not end <= region["char_end"]
        ):
            raise ScorerInputBridgeError(
                "occurrence outside eligible body paragraph"
            )

        location = (start, end)

        if location in seen_locations:
            raise ScorerInputBridgeError(
                "duplicate occurrence location"
            )

        seen_locations.add(location)

        checked.append({
            "candidate_index": index,
            "candidate_id": deepcopy(candidate_id),
            "region_id": region_id,
            "char_start": start,
            "char_end": end,
            "text": phrase,
            "source_node_id": region["source_node_id"],
        })

    # Reuse I3-A4 protected-span and capacity checks.
    capacity = evaluate_existing_link_capacity(
        foundation["existing_link_profile"],
        validated,
        [
            {
                **record,
                "candidate_id": "position_" + str(index),
            }
            for index, record in enumerate(checked)
        ],
    )

    prechecks = capacity["candidate_prechecks"]

    for record, precheck in zip(checked, prechecks):
        status = precheck["status"]

        if status in {
            "PROTECTED_SPAN_COLLISION",
            "CANDIDATE_COLLISION",
            "INELIGIBLE_REGION",
            "OUTSIDE_ELIGIBLE_PARAGRAPH",
        }:
            raise ScorerInputBridgeError(
                "unsafe occurrence placement: " + status
            )

        record["capacity_precheck_status"] = status
        record["scorer_review_possible"] = (
            status == "ELIGIBLE_FOR_SCORER_REVIEW"
        )

    result = deepcopy(foundation)
    result["status"] = (
        "canonical_occurrence_geometry_validated"
    )
    result["candidate_occurrences"] = checked
    result["candidate_occurrence_geometry_validated"] = True
    result["candidate_occurrence_binding_verified"] = False
    result["occurrence_provenance_authenticated"] = False
    result["original_source_insertion_verified"] = False
    result["scorer_decision_performed"] = False
    result["automatic_linking_authorized"] = False

    return result
