"""Phase 3.8: conservative sparse intelligence assessment."""
from copy import deepcopy


def assess_sparse_intelligence(
    *,
    candidate_index,
    original_candidate,
    evidence_association,
    source_states=None,
    confidence_signal=None,
    confidence_evidence=None,
):
    result = {
        "schema_version": "sparse_intelligence_v1",
        "candidate_index": candidate_index,
        "status": "invalid",
        "reason": None,
        "original_candidate": None,
        "evidence_ids": [],
        "evidence_count": 0,
        "confidence_status": "not_assessed",
        "confidence_score": None,
        # sparse_low_confidence_contract_382
        "low_confidence_state": "unknown",
        "low_confidence_reason": None,
        "confidence_signal_source": None,
        "confidence_signal_verified": False,
        # sparse_confidence_producer_connection_382
        "confidence_evidence_context": None,
        "phrase_confidence_established": False,
        "source_availability": "not_assessed",
        # sparse_source_states_383
        "source_states": {},
        "source_issues": [],
        "source_issue_count": 0,
        "scorer_handoff_status": "not_prepared",
        "candidate_retained": False,
        "semantic_certification_performed": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }

    def reject(reason):
        result["reason"] = reason
        return result

    if (
        type(candidate_index) is not int
        or candidate_index < 0
        or not isinstance(original_candidate, dict)
        or not isinstance(evidence_association, dict)
    ):
        return reject("invalid_sparse_intelligence_input")

    if (
        type(evidence_association.get("candidate_index")) is not int
        or evidence_association["candidate_index"] != candidate_index
    ):
        return reject("candidate_attribution_mismatch")

    status = evidence_association.get("status")
    ids = evidence_association.get("evidence_ids")
    count = evidence_association.get("evidence_count")

    if (
        status not in ("no_evidence", "evidence_associated")
        or not isinstance(ids, list)
        or any(not isinstance(eid, str) or not eid.strip() for eid in ids)
        or len(set(ids)) != len(ids)
        or type(count) is not int
        or count != len(ids)
        or (status == "no_evidence") != (len(ids) == 0)
    ):
        return reject("invalid_evidence_association_contract")

    if (
        evidence_association.get("independently_verified") is not False
        or evidence_association.get("semantic_proof_certified") is not False
        or evidence_association.get("automatic_linking_authorized") is not False
    ):
        return reject("unsupported_evidence_authority")

    # Preserve supplied upstream states without inferring retrieval.
    # The mapping is advisory, never source authentication.
    allowed_sources = (
        "semantic_memory",
        "intelligence_graph",
        "reasoning_intelligence",
        "confidence_evidence",
        "explainability",
    )
    allowed_states = (
        "available",
        "no_evidence",
        "unavailable",
        "error",
        "stale",
        "invalid",
    )

    if source_states is not None:
        if not isinstance(source_states, dict):
            return reject("invalid_source_states_input")

        if any(
            name not in allowed_sources
            or not isinstance(state, str)
            or state not in allowed_states
            for name, state in source_states.items()
        ):
            return reject("unknown_or_invalid_source_state")

        result["source_states"] = deepcopy(source_states)
        result["source_issues"] = [
            {
                "source": name,
                "state": source_states[name],
                "source_truth_verified": False,
            }
            for name in allowed_sources
            if source_states.get(name) in (
                "unavailable", "error", "stale", "invalid"
            )
        ]
        result["source_issue_count"] = len(
            result["source_issues"]
        )
        result["source_availability"] = (
            "issues_reported"
            if result["source_issues"]
            else "reported_no_issues"
            if source_states else "not_assessed"
        )

    # Explicit upstream classification only; no invented threshold.
    # Presence or absence of evidence is not a numeric confidence score.

    # Preserve the actual confidence producer output without converting
    # concept/evidence confidence into selected-phrase confidence.
    if confidence_evidence is not None:
        if not isinstance(confidence_evidence, dict):
            return reject("invalid_confidence_evidence_output")

        if (
            confidence_evidence.get("schema_version")
            != "confidence_evidence_v1"
            or confidence_evidence.get("status")
            != "source_confidence_preserved"
            or not isinstance(
                confidence_evidence.get("confidence_records"), list
            )
            or type(confidence_evidence.get("source_count")) is not int
            or confidence_evidence["source_count"]
            != len(confidence_evidence["confidence_records"])
            or confidence_evidence.get("overall_confidence") is not None
            or confidence_evidence.get("overall_confidence_status")
            != "not_established"
            or confidence_evidence.get("aggregation_authorized") is not False
            or confidence_evidence.get("aggregation_performed") is not False
            or confidence_evidence.get("aggregate_confidence_calibrated")
            is not False
            or confidence_evidence.get("semantic_proof_certified") is not False
            or confidence_evidence.get("linking_decision_performed") is not False
            or confidence_evidence.get("automatic_linking_authorized")
            is not False
        ):
            return reject("unsupported_confidence_evidence_contract")

        records = confidence_evidence["confidence_records"]
        if any(
            not isinstance(record, dict)
            or record.get("phrase_level_semantic_confidence") is not None
            or record.get("selected_phrase_confidence_authorized")
            is not False
            or record.get("confidence_calibrated") is not False
            or record.get("independently_verified") is not False
            or record.get("certified") is not False
            for record in records
        ):
            return reject("unsupported_phrase_confidence_claim")

        result["confidence_evidence_context"] = deepcopy(
            confidence_evidence
        )

        if confidence_signal is not None:
            return reject("unverified_confidence_signal_conflict")

    if confidence_signal is not None:
        if (
            not isinstance(confidence_signal, dict)
            or set(confidence_signal) != {"state", "source"}
            or confidence_signal.get("source") not in (
                "confidence_evidence",
                "reasoning_intelligence",
                "intelligence_graph",
            )
            or confidence_signal.get("state") not in (
                "low_confidence",
                "not_low_confidence",
            )
        ):
            return reject("invalid_confidence_signal")

        if not ids:
            return reject("confidence_without_associated_evidence")

        result["low_confidence_state"] = confidence_signal["state"]
        result["low_confidence_reason"] = (
            "explicit_upstream_confidence_indicator"
        )
        result["confidence_signal_source"] = confidence_signal["source"]

    elif not ids:
        result["low_confidence_state"] = "not_assessable"
        result["low_confidence_reason"] = "no_associated_evidence"

    else:
        result["low_confidence_state"] = "unknown"
        result["low_confidence_reason"] = (
            "no_explicit_confidence_indicator"
        )

    result["original_candidate"] = deepcopy(original_candidate)
    result["candidate_retained"] = True
    result["evidence_ids"] = list(ids)
    result["evidence_count"] = count
    result["scorer_handoff_status"] = "advisory_only"

    if not ids:
        result["status"] = "INSUFFICIENT_INTELLIGENCE"
        result["reason"] = "no_associated_evidence"
        result["confidence_status"] = "not_available"
    else:
        result["status"] = "EVIDENCE_PRESENT_UNVERIFIED"
        result["confidence_status"] = "not_assessed"

    return result


# sparse_candidate_retention_384
def validate_sparse_candidate_retention(
    *,
    selected_candidates,
    sparse_assessments,
):
    """Validate one-to-one retention; never filter selected candidates."""
    result = {
        "schema_version": "sparse_candidate_retention_v1",
        "status": "invalid",
        "reason": None,
        "selected_count": 0,
        "retained_count": 0,
        "retained_candidates": [],
        "sparse_count": 0,
        "evidence_present_count": 0,
        "candidate_deletion_performed": False,
        "candidate_reordering_performed": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }

    def reject(reason):
        result["reason"] = reason
        return result

    if (
        not isinstance(selected_candidates, list)
        or not isinstance(sparse_assessments, list)
        or any(not isinstance(item, dict) for item in selected_candidates)
    ):
        return reject("invalid_retention_input")

    result["selected_count"] = len(selected_candidates)

    if len(selected_candidates) != len(sparse_assessments):
        return reject("candidate_count_mismatch")

    sparse_count = 0
    evidence_count = 0

    for index, (candidate, assessment) in enumerate(
        zip(selected_candidates, sparse_assessments)
    ):
        if not isinstance(assessment, dict):
            return reject("invalid_sparse_assessment")

        if (
            assessment.get("schema_version") != "sparse_intelligence_v1"
            or type(assessment.get("candidate_index")) is not int
            or assessment["candidate_index"] != index
        ):
            return reject("candidate_identity_or_order_mismatch")

        if (
            assessment.get("candidate_retained") is not True
            or assessment.get("original_candidate") != candidate
        ):
            return reject("candidate_not_preserved")

        status = assessment.get("status")
        ids = assessment.get("evidence_ids")
        count = assessment.get("evidence_count")

        if (
            status not in (
                "INSUFFICIENT_INTELLIGENCE",
                "EVIDENCE_PRESENT_UNVERIFIED",
            )
            or not isinstance(ids, list)
            or any(
                not isinstance(eid, str) or not eid.strip()
                for eid in ids
            )
            or len(set(ids)) != len(ids)
            or type(count) is not int
            or count != len(ids)
            or (status == "INSUFFICIENT_INTELLIGENCE")
            != (count == 0)
        ):
            return reject("invalid_sparse_assessment_contract")

        if (
            assessment.get("semantic_certification_performed") is not False
            or assessment.get("scorer_decision_performed") is not False
            or assessment.get("automatic_linking_authorized") is not False
        ):
            return reject("unsupported_sparse_authority")

        if status == "INSUFFICIENT_INTELLIGENCE":
            sparse_count += 1
        else:
            evidence_count += 1

    # Commit outputs only after every candidate passes validation.
    result["retained_candidates"] = deepcopy(selected_candidates)
    result["retained_count"] = len(selected_candidates)
    result["sparse_count"] = sparse_count
    result["evidence_present_count"] = evidence_count
    result["status"] = "all_candidates_retained"
    return result


# sparse_scorer_handoff_385
def prepare_sparse_scorer_handoff(
    *,
    selected_candidates,
    sparse_assessments,
):
    """Prepare advisory candidate records, without invoking the Scorer."""
    result = {
        "schema_version": "sparse_scorer_handoff_v1",
        "status": "invalid",
        "reason": None,
        "candidate_count": 0,
        "candidates": [],
        "insufficient_intelligence_count": 0,
        "evidence_present_count": 0,
        "scorer_contract_finalized": False,
        "scorer_invoked": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }

    retention = validate_sparse_candidate_retention(
        selected_candidates=selected_candidates,
        sparse_assessments=sparse_assessments,
    )

    if retention["status"] != "all_candidates_retained":
        result["reason"] = (
            "candidate_retention_failed:"
            + str(retention.get("reason"))
        )
        return result

    prepared = []

    for index, assessment in enumerate(sparse_assessments):
        ids = assessment["evidence_ids"]

        if (
            assessment.get("scorer_handoff_status") != "advisory_only"
            or assessment.get("confidence_score") is not None
            or assessment.get("confidence_status") not in (
                "not_available", "not_assessed"
            )
            or assessment.get("source_availability") not in (
                "not_assessed", "reported_no_issues", "issues_reported"
            )
            or not isinstance(assessment.get("source_states"), dict)
            or not isinstance(assessment.get("source_issues"), list)
            or type(assessment.get("source_issue_count")) is not int
            or assessment["source_issue_count"]
            != len(assessment["source_issues"])
        ):
            result["reason"] = "invalid_advisory_assessment"
            return result

        if (
            assessment["status"] == "INSUFFICIENT_INTELLIGENCE"
            and assessment.get("reason") != "no_associated_evidence"
        ):
            result["reason"] = "invalid_sparse_reason"
            return result

        prepared.append({
            "candidate_index": index,
            "original_candidate": deepcopy(selected_candidates[index]),
            "intelligence_status": assessment["status"],
            "evidence_ids": list(ids),
            "evidence_count": len(ids),
            "confidence_status": assessment["confidence_status"],
            "confidence_score": None,
            "source_availability": assessment["source_availability"],
            "source_states": deepcopy(assessment["source_states"]),
            "source_issues": deepcopy(assessment["source_issues"]),
            "confidence_evidence_context": deepcopy(
                assessment.get("confidence_evidence_context")
            ),
            "low_confidence_state": assessment.get(
                "low_confidence_state", "unknown"
            ),
            "phrase_confidence_established": False,
            "candidate_preserved": True,
            "scorer_decision": None,
            "scorer_invoked": False,
            "automatic_linking_authorized": False,
        })

    result["candidates"] = prepared
    result["candidate_count"] = len(prepared)
    result["insufficient_intelligence_count"] = (
        retention["sparse_count"]
    )
    result["evidence_present_count"] = (
        retention["evidence_present_count"]
    )
    result["status"] = "advisory_handoff_prepared"
    return result
