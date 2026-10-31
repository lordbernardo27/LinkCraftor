"""Phase 3.7.9 ? observational explanation evidence association.

No evidence retrieval, source mutation, score aggregation, semantic
certification, or linking decisions are performed here.
"""
from copy import deepcopy


def associate_explanation_evidence(
    *,
    candidate_index,
    evidence_ids,
    evidence_registry,
):
    output = {
        "schema_version": "explanation_evidence_association_v1",
        "candidate_index": candidate_index,
        "status": "no_evidence",
        # explanation_evidence_safeguards_3796
        "reason": None,
        "upstream_retrieval_status": "not_supplied",
        "source_availability_verified": False,
        "evidence_ids": [],
        "evidence_count": 0,
        # explanation_scorer_handoff_3797
        "scorer_evidence_handoff": {
            "schema_version": "explanation_scorer_evidence_v1",
            "status": "no_evidence",
            "candidate_index": candidate_index,
            "evidence_ids": [],
            "evidence_count": 0,
            "evidence_sources": [],
            "traceability": "not_established",
            "semantic_evidence_verified": False,
            "independent_validation_required": True,
            "candidate_score": None,
            "link_target": None,
            "scorer_decision": None,
            "scorer_decision_performed": False,
            "automatic_linking_authorized": False,
        },
        "evidence_trace": [],
        # explanation_signals_3794
        "explanation_signals": [],
        "explanation_signal_count": 0,
        "explanation_status": "no_evidence",
        "explanation_scope": "source_evidence_observation_only",
        "independently_verified": False,
        "semantic_proof_certified": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }

    if (
        type(candidate_index) is not int
        or candidate_index < 0
        or not isinstance(evidence_ids, list)
        or not isinstance(evidence_registry, dict)
    ):
        output["status"] = "invalid"
        output["reason"] = "invalid_association_input"
        return output

    if any(
        not isinstance(eid, str) or not eid
        for eid in evidence_ids
    ) or len(set(evidence_ids)) != len(evidence_ids):
        output["status"] = "invalid"
        output["reason"] = "invalid_or_duplicate_evidence_ids"
        return output

    trace = []

    for eid in evidence_ids:
        if eid not in evidence_registry:
            output["status"] = "invalid"
            output["reason"] = "unresolved_evidence_reference"
            return output

        record = evidence_registry[eid]
        if (
            not isinstance(record, dict)
            or type(record.get("candidate_index")) is not int
            or record["candidate_index"] != candidate_index
            or record.get("certified") is not False
        ):
            output["status"] = "invalid"
            output["reason"] = "invalid_evidence_record_or_attribution"
            return output

        source = record.get("source")
        evidence_type = record.get("evidence_type")

        if not isinstance(source, str) or not source.strip():
            output["status"] = "invalid"
            output["reason"] = "missing_evidence_source"
            return output

        if evidence_type is None and source == "semantic_memory":
            evidence_type = "legacy_semantic_memory_record"

        if not isinstance(evidence_type, str) or not evidence_type.strip():
            output["status"] = "invalid"
            output["reason"] = "missing_evidence_type"
            return output

        # explanation_lineage_3795
        # Preserve only metadata actually present in the source record.
        # Presence is not independent authentication or verification.
        lineage_fields = (
            "workspace_id",
            "document_id",
            "source_id",
            "source_reference",
            "source_url",
            "source_feed_version",
            "first_seen_at",
            "last_seen_at",
            "created_at",
            "article_sha256",
            "selection_occurrence_id",
        )

        source_lineage = {
            field: deepcopy(record[field])
            for field in lineage_fields
            if field in record
        }

        evidence_lineage = {
            "registry_evidence_id": eid,
            "candidate_index": candidate_index,
            "source": deepcopy(source),
            "evidence_type": deepcopy(evidence_type),
            "source_metadata": source_lineage,
            "source_metadata_status": (
                "source_fields_preserved_unverified"
                if source_lineage else "no_additional_source_metadata"
            ),
            "registry_reference_resolved": True,
            "independent_provenance_verified": False,
            "semantic_proof_certified": False,
        }

        trace.append({
            "evidence_id": eid,
            "candidate_index": candidate_index,
            "source": deepcopy(source),
            "evidence_type": deepcopy(evidence_type),
            "evidence_lineage": evidence_lineage,
            "source_evidence_record_preserved": True,
            "independently_verified": False,
            "semantic_proof_certified": False,
        })

    output["status"] = "evidence_associated" if trace else "no_evidence"
    output["evidence_ids"] = list(evidence_ids)
    output["evidence_count"] = len(trace)
    output["evidence_trace"] = trace
    # Every signal is derived from an already validated trace.
    # No semantic conclusion is inferred from its source label.
    explanation_signals = [
        {
            "evidence_id": item["evidence_id"],
            "candidate_index": item["candidate_index"],
            "source": deepcopy(item["source"]),
            "evidence_type": deepcopy(item["evidence_type"]),
            "evidence_lineage": deepcopy(item["evidence_lineage"]),
            "observation": "source_evidence_record_referenced",
            "observation_scope": "evidence_reference_only",
            "semantic_relationship_asserted": False,
            "semantic_equivalence_asserted": False,
            "phrase_level_confidence": None,
            "independently_verified": False,
            "certified": False,
            "scorer_decision_performed": False,
            "automatic_linking_authorized": False,
        }
        for item in trace
    ]

    output["explanation_signals"] = explanation_signals
    output["explanation_signal_count"] = len(explanation_signals)
    # An evidence-reference handoff, not an executable scorer input.
    # Existing evidence ordering and attribution remain authoritative.
    handoff = output["scorer_evidence_handoff"]

    handoff["status"] = (
        "advisory_evidence_available" if trace else "no_evidence"
    )
    handoff["evidence_ids"] = [item["evidence_id"] for item in trace]
    handoff["evidence_count"] = len(trace)
    handoff["evidence_sources"] = list(dict.fromkeys(
        item["source"] for item in trace
    ))
    handoff["traceability"] = (
        "registry_references_resolved_unverified"
        if trace else "not_established"
    )
    output["explanation_status"] = (
        "observational_signals_found"
        if explanation_signals else "no_evidence"
    )
    return output
