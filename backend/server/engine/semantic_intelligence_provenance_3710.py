"""Phase 3.7.10: observational provenance association.

References existing candidate and registry evidence.
Does not authenticate evidence or authorize linking.
"""
from copy import deepcopy
import re


CANDIDATE_FIELDS = (
    "selection_occurrence_id",
    "selection_source_span",
    "selection_source_span_status",
    "article_sha256",
    "source_span",
    "sentence_span",
)


def associate_candidate_provenance(
    *,
    candidate_index,
    original_candidate,
    evidence_association,
    evidence_registry,
):
    output = {
        "schema_version": "candidate_provenance_v1",
        "candidate_index": candidate_index,
        "status": "no_evidence",
        "reason": None,
        "candidate_origin": {},
        "evidence_lineage": [],
        "evidence_ids": [],
        "evidence_count": 0,
        "registry_references_resolved": False,
        "independent_provenance_verified": False,
        "semantic_proof_certified": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }

    def invalid(reason):
        output["status"] = "invalid"
        output["reason"] = reason
        return output

    if (
        type(candidate_index) is not int
        or candidate_index < 0
        or not isinstance(original_candidate, dict)
        or not isinstance(evidence_association, dict)
        or not isinstance(evidence_registry, dict)
    ):
        return invalid("invalid_provenance_input")

    association_status = evidence_association.get("status")
    if association_status not in ("no_evidence", "evidence_associated"):
        return invalid("invalid_evidence_association_status")

    if type(evidence_association.get("candidate_index")) is not int:
        return invalid("invalid_evidence_candidate_index")

    if evidence_association["candidate_index"] != candidate_index:
        return invalid("cross_candidate_association")

    ids = evidence_association.get("evidence_ids")
    trace = evidence_association.get("evidence_trace")
    if (
        not isinstance(ids, list)
        or not isinstance(trace, list)
        or len(ids) != len(trace)
        or any(not isinstance(eid, str) or not eid for eid in ids)
        or len(set(ids)) != len(ids)
    ):
        return invalid("invalid_evidence_references")

    if (association_status == "no_evidence") != (len(ids) == 0):
        return invalid("evidence_status_count_mismatch")

    if evidence_association.get("evidence_count") != len(ids):
        return invalid("evidence_count_mismatch")

    if (
        evidence_association.get("independently_verified") is not False
        or evidence_association.get("semantic_proof_certified") is not False
        or evidence_association.get("automatic_linking_authorized") is not False
    ):
        return invalid("unsupported_association_authority")

    # candidate_origin_guard_37103
    # Verify the structure of origin fields when supplied.
    # Do not invent absent metadata or re-certify source content.
    occurrence_id = original_candidate.get("selection_occurrence_id")
    if "selection_occurrence_id" in original_candidate:
        if (
            not isinstance(occurrence_id, str)
            or not occurrence_id.strip()
        ):
            return invalid("invalid_selection_occurrence_id")

    article_hash = original_candidate.get("article_sha256")
    if "article_sha256" in original_candidate:
        if (
            not isinstance(article_hash, str)
            or re.fullmatch(r"[0-9a-fA-F]{64}", article_hash) is None
        ):
            return invalid("invalid_article_sha256")

    for field in ("selection_source_span", "source_span",
                  "sentence_span"):
        if field in original_candidate:
            value = original_candidate[field]
            if not isinstance(value, dict):
                return invalid("invalid_candidate_origin_span:" + field)

    if "selection_source_span_status" in original_candidate:
        status = original_candidate["selection_source_span_status"]
        if not isinstance(status, str) or not status.strip():
            return invalid("invalid_source_span_status")

    lineage = []

    for eid, item in zip(ids, trace):
        if not isinstance(item, dict) or eid not in evidence_registry:
            return invalid("unresolved_evidence_lineage")

        record = evidence_registry[eid]
        if (
            not isinstance(record, dict)
            or type(record.get("candidate_index")) is not int
            or record["candidate_index"] != candidate_index
            or record.get("certified") is not False
            or item.get("evidence_id") != eid
            or item.get("candidate_index") != candidate_index
            or item.get("source") != record.get("source")
        ):
            return invalid("evidence_registry_lineage_mismatch")

        reference = item.get("evidence_lineage")
        if (
            not isinstance(reference, dict)
            or reference.get("registry_evidence_id") != eid
            or reference.get("candidate_index") != candidate_index
            or reference.get("source") != record.get("source")
            or reference.get("independent_provenance_verified") is not False
        ):
            return invalid("explanation_lineage_mismatch")

        # evidence_source_lineage_guard_37104
        # Reconcile Phase 3.7.9 metadata with the original registry.
        # Do not invent or independently certify source metadata.
        tracked_fields = (
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

        source_metadata = reference.get("source_metadata")
        if not isinstance(source_metadata, dict):
            return invalid("invalid_source_lineage_metadata")

        expected_metadata = {
            field: record[field]
            for field in tracked_fields
            if field in record
        }

        if source_metadata != expected_metadata:
            return invalid("source_registry_metadata_mismatch")

        if reference.get("evidence_type") != item.get("evidence_type"):
            return invalid("source_evidence_type_mismatch")

        registry_evidence_type = record.get("evidence_type")
        if (
            registry_evidence_type is None
            and record.get("source") == "semantic_memory"
        ):
            registry_evidence_type = "legacy_semantic_memory_record"

        if item.get("evidence_type") != registry_evidence_type:
            return invalid("registry_evidence_type_mismatch")

        source_lineage = {
            "registry_evidence_id": eid,
            "source": deepcopy(record["source"]),
            "evidence_type": deepcopy(registry_evidence_type),
            "source_metadata": deepcopy(expected_metadata),
            "lineage_consistency": "registry_fields_match",
            "source_authenticity_verified": False,
        }

        lineage.append({
            "evidence_id": eid,
            "candidate_index": candidate_index,
            "source": deepcopy(record.get("source")),
            "explanation_lineage": deepcopy(reference),
            "source_lineage": source_lineage,
            "registry_reference_resolved": True,
            "independently_verified": False,
        })

    output["candidate_origin"] = {
        field: deepcopy(original_candidate[field])
        for field in CANDIDATE_FIELDS
        if field in original_candidate
    }
    output["candidate_origin_status"] = (
        "source_fields_preserved_unverified"
        if output["candidate_origin"]
        else "no_candidate_origin_metadata"
    )
    output["origin_fields_present"] = list(
        output["candidate_origin"].keys()
    )
    output["source_content_independently_verified"] = False
    output["evidence_ids"] = list(ids)
    output["evidence_lineage"] = lineage
    output["evidence_count"] = len(lineage)
    output["registry_references_resolved"] = True
    output["status"] = (
        "provenance_references_associated"
        if lineage else "no_evidence"
    )
    return output


# cross_intelligence_provenance_37105
# Observational inventory only: no cross-source identity equivalence.
PROVENANCE_SCOPES = {
    "explainability": "registry_backed_evidence_reference",
    "reasoning_intelligence": "document_context_reasoning",
    "intelligence_graph": "graph_observation",
    "confidence_evidence": "source_relationship_confidence",
}

PROVENANCE_REFERENCE_FIELDS = (
    "evidence_ids",
    "source_evidence_id",
    "evidence_id",
    "document_relationship_provenance",
    "provenance",
    "evidence_lineage",
    "source_lineage",
    "reasoning_signal_association",
    "semantic_relationship_confidence_evidence",
    "semantic_relationship_evidence_ids",
)


def inventory_cross_intelligence_provenance(*, candidate_index, sections):
    """Inventory supplied source fields without certifying their truth."""
    result = {
        "schema_version": "cross_intelligence_provenance_v1",
        "candidate_index": candidate_index,
        "status": "no_sources",
        "reason": None,
        "sources": [],
        "source_count": 0,
        "cross_source_identity_equivalence": "not_established",
        "independent_provenance_verified": False,
        "semantic_proof_certified": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }

    if (
        type(candidate_index) is not int
        or candidate_index < 0
        or not isinstance(sections, dict)
    ):
        result["status"] = "invalid"
        result["reason"] = "invalid_cross_intelligence_input"
        return result

    if any(name not in PROVENANCE_SCOPES for name in sections):
        result["status"] = "invalid"
        result["reason"] = "unknown_intelligence_section"
        return result

    observations = []
    for name in PROVENANCE_SCOPES:
        if name not in sections:
            continue

        section = sections[name]
        if section is None:
            observations.append({
                "source": name,
                "scope": PROVENANCE_SCOPES[name],
                "status": "unavailable",
                "reference_fields": {},
                "independently_verified": False,
            })
            continue

        if not isinstance(section, dict):
            result["status"] = "invalid"
            result["reason"] = "malformed_intelligence_section:" + name
            return result

        # provenance_reference_guard_37106
        # Validate only reference shapes with an established contract.
        # Do not infer source freshness, authenticity, or identity.
        list_reference_fields = (
            "evidence_ids",
            "semantic_relationship_evidence_ids",
        )
        single_reference_fields = (
            "evidence_id",
            "source_evidence_id",
        )

        for field in list_reference_fields:
            if field not in section:
                continue

            values = section[field]
            if (
                not isinstance(values, list)
                or any(
                    not isinstance(value, str) or not value.strip()
                    for value in values
                )
                or len(values) != len(set(values))
            ):
                result["status"] = "invalid"
                result["reason"] = (
                    "invalid_provenance_reference:" + name + ":" + field
                )
                return result

        for field in single_reference_fields:
            if field not in section:
                continue

            value = section[field]
            if not isinstance(value, str) or not value.strip():
                result["status"] = "invalid"
                result["reason"] = (
                    "invalid_provenance_reference:" + name + ":" + field
                )
                return result

        references = {
            field: deepcopy(section[field])
            for field in PROVENANCE_REFERENCE_FIELDS
            if field in section
        }

        observations.append({
            "source": name,
            "scope": PROVENANCE_SCOPES[name],
            "status": (
                "source_fields_present_unverified"
                if any(
                    value not in (None, [], {})
                    for value in references.values()
                )
                else "no_evidence_references"
                if references else "no_provenance_fields"
            ),
            "reference_fields": references,
            "independently_verified": False,
        })

    result["sources"] = observations
    result["source_count"] = len(observations)
    result["status"] = (
        "source_inventory_created" if observations else "no_sources"
    )
    return result


# provenance_consistency_37107
def validate_provenance_consistency(
    *,
    candidate_index,
    candidate_provenance,
    evidence_association,
    cross_intelligence_provenance,
):
    """Check shared references; never equate different source scopes."""
    result = {
        "schema_version": "provenance_consistency_v1",
        "candidate_index": candidate_index,
        "status": "invalid",
        "reason": None,
        "checked_evidence_ids": [],
        "checked_evidence_count": 0,
        "cross_source_identity_equivalence": "not_established",
        "independent_provenance_verified": False,
        "semantic_proof_certified": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }

    def reject(reason):
        result["reason"] = reason
        return result

    if (
        type(candidate_index) is not int
        or candidate_index < 0
        or not all(
            isinstance(value, dict)
            for value in (
                candidate_provenance,
                evidence_association,
                cross_intelligence_provenance,
            )
        )
    ):
        return reject("invalid_consistency_input")

    if any(
        type(section.get("candidate_index")) is not int
        or section["candidate_index"] != candidate_index
        for section in (
            candidate_provenance,
            evidence_association,
            cross_intelligence_provenance,
        )
    ):
        return reject("candidate_index_mismatch")

    ids = evidence_association.get("evidence_ids")
    trace = evidence_association.get("evidence_trace")
    signals = evidence_association.get("explanation_signals")
    lineage = candidate_provenance.get("evidence_lineage")

    if (
        not isinstance(ids, list)
        or not isinstance(trace, list)
        or not isinstance(signals, list)
        or not isinstance(lineage, list)
        or any(not isinstance(eid, str) or not eid for eid in ids)
        or len(ids) != len(set(ids))
        or any(len(collection) != len(ids)
               for collection in (trace, signals, lineage))
    ):
        return reject("inconsistent_evidence_collection")

    if (
        evidence_association.get("status")
        != ("evidence_associated" if ids else "no_evidence")
        or candidate_provenance.get("status")
        != ("provenance_references_associated" if ids else "no_evidence")
        or candidate_provenance.get("evidence_ids") != ids
        or evidence_association.get("evidence_count") != len(ids)
        or candidate_provenance.get("evidence_count") != len(ids)
    ):
        return reject("provenance_association_mismatch")

    for index, eid in enumerate(ids):
        for item in (trace[index], signals[index], lineage[index]):
            if (
                not isinstance(item, dict)
                or item.get("evidence_id") != eid
                or type(item.get("candidate_index")) is not int
                or item["candidate_index"] != candidate_index
            ):
                return reject("evidence_identity_or_order_mismatch")

        if not (
            trace[index].get("source")
            == signals[index].get("source")
            == lineage[index].get("source")
        ):
            return reject("evidence_source_mismatch")

        if (
            signals[index].get("evidence_lineage")
            != trace[index].get("evidence_lineage")
            or lineage[index].get("explanation_lineage")
            != trace[index].get("evidence_lineage")
        ):
            return reject("evidence_lineage_mismatch")

    if cross_intelligence_provenance.get("status") not in (
        "source_inventory_created", "no_sources",
    ):
        return reject("invalid_cross_intelligence_inventory")

    sources = cross_intelligence_provenance.get("sources")
    if (
        not isinstance(sources, list)
        or cross_intelligence_provenance.get("source_count") != len(sources)
    ):
        return reject("invalid_cross_intelligence_source_count")

    explainability_seen = False
    for source in sources:
        if not isinstance(source, dict):
            return reject("invalid_cross_intelligence_source")
        if source.get("source") != "explainability":
            continue
        if explainability_seen:
            return reject("duplicate_explainability_source")
        explainability_seen = True
        references = source.get("reference_fields")
        if (
            not isinstance(references, dict)
            or references.get("evidence_ids") != ids
        ):
            return reject("explainability_inventory_mismatch")

    # Missing Explainability inventory is acceptable only if it is
    # explicitly absent and there are no shared registry references.
    if ids and not explainability_seen:
        return reject("missing_explainability_inventory")

    if any(
        section.get("independent_provenance_verified") is not False
        or section.get("automatic_linking_authorized") is not False
        for section in (
            candidate_provenance,
            cross_intelligence_provenance,
        )
    ):
        return reject("unsupported_provenance_authority")

    result["status"] = (
        "shared_references_consistent" if ids else "no_evidence"
    )
    result["checked_evidence_ids"] = list(ids)
    result["checked_evidence_count"] = len(ids)
    return result
