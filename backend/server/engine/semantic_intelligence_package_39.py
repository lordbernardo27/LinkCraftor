"""Phase 3.9.1: Canonical Semantic Intelligence package schema."""

from copy import deepcopy

PACKAGE_SCHEMA_VERSION = "semantic_intelligence_package_v1"


def build_semantic_intelligence_package(
    *,
    selected_candidates,
    enriched_candidates,
    evidence_registry,
    sparse_candidate_retention,
    sparse_scorer_advisory_handoff,
):
    """Build a versioned, non-authorizing package envelope."""
    package = {
        "schema_version": PACKAGE_SCHEMA_VERSION,
        "status": "invalid",
        "reason": None,
        "candidate_count": 0,
        "enriched_candidates": [],
        "phrase_identity": [],
        "phrase_context": [],
        "semantic_intelligence": [],
        "reasoning": [],
        "confidence": [],
        "explainability": [],
        "provenance": [],
        "certification_state": [],
        "intelligence_status": [],
        "evidence_registry": {},
        "sparse_candidate_retention": None,
        "sparse_scorer_advisory_handoff": None,
        "original_candidates_preserved": False,
        "evidence_certification_performed": False,
        "semantic_certification_performed": False,
        "scorer_contract_finalized": False,
        "scorer_invoked": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }

    def reject(reason):
        package["reason"] = reason
        return package

    if (
        not isinstance(selected_candidates, list)
        or not isinstance(enriched_candidates, list)
        or not isinstance(evidence_registry, dict)
        or not isinstance(sparse_candidate_retention, dict)
        or not isinstance(sparse_scorer_advisory_handoff, dict)
        or any(not isinstance(c, dict) for c in selected_candidates)
    ):
        return reject("invalid_package_input")

    count = len(selected_candidates)

    if len(enriched_candidates) != count:
        return reject("candidate_count_mismatch")

    for index, (candidate, entry) in enumerate(
        zip(selected_candidates, enriched_candidates)
    ):
        if (
            not isinstance(entry, dict)
            or type(entry.get("candidate_index")) is not int
            or entry["candidate_index"] != index
            or entry.get("original_candidate") != candidate
        ):
            return reject("candidate_identity_or_order_mismatch")

    retention = sparse_candidate_retention
    if (
        retention.get("status") != "all_candidates_retained"
        or type(retention.get("selected_count")) is not int
        or retention["selected_count"] != count
        or type(retention.get("retained_count")) is not int
        or retention["retained_count"] != count
        or retention.get("retained_candidates") != selected_candidates
    ):
        return reject("sparse_retention_contract_mismatch")

    advisory = sparse_scorer_advisory_handoff
    records = advisory.get("candidates")

    if (
        advisory.get("status") != "advisory_handoff_prepared"
        or type(advisory.get("candidate_count")) is not int
        or advisory["candidate_count"] != count
        or not isinstance(records, list)
        or len(records) != count
    ):
        return reject("sparse_advisory_contract_mismatch")

    for index, record in enumerate(records):
        if (
            not isinstance(record, dict)
            or type(record.get("candidate_index")) is not int
            or record["candidate_index"] != index
            or record.get("original_candidate") != selected_candidates[index]
            or record.get("scorer_decision") is not None
            or record.get("scorer_invoked") is not False
            or record.get("automatic_linking_authorized") is not False
        ):
            return reject("sparse_advisory_candidate_mismatch")

    for field in (
        "scorer_contract_finalized",
        "scorer_invoked",
        "scorer_decision_performed",
        "automatic_linking_authorized",
    ):
        if advisory.get(field) is not False:
            return reject("unsupported_scorer_authority")

    # package_phrase_identity_392
    # Preserve each selected occurrence independently, without
    # inventing identifiers or collapsing duplicate phrase text.
    phrase_identity = [
        {
            "candidate_index": index,
            "original_candidate": deepcopy(candidate),
            "identity_status": "original_candidate_preserved",
            "identity_modified": False,
            "identity_invented": False,
        }
        for index, candidate in enumerate(selected_candidates)
    ]


    # package_phrase_context_393
    # Capture existing context only; do not infer text or offsets.
    source_context_keys = (
        "context",
        "sentence",
        "sentence_text",
        "paragraph",
        "section",
        "position",
        "start",
        "end",
        "start_offset",
        "end_offset",
        "surrounding_text",
        "document_context",
    )
    enriched_context_keys = (
        "context",
        "semantic_context",
        "phrase_context",
        "document_context",
    )

    phrase_context = []

    for index, (candidate, entry) in enumerate(
        zip(selected_candidates, enriched_candidates)
    ):
        original_context = {
            key: deepcopy(candidate[key])
            for key in source_context_keys
            if key in candidate
        }
        intelligence_context = {
            key: deepcopy(entry[key])
            for key in enriched_context_keys
            if key in entry
        }

        context_available = bool(
            original_context or intelligence_context
        )

        phrase_context.append({
            "candidate_index": index,
            "status": (
                "context_preserved"
                if context_available else "not_provided"
            ),
            "original_candidate_context": original_context,
            "enriched_candidate_context": intelligence_context,
            "source_context_fields": list(original_context),
            "enriched_context_fields": list(intelligence_context),
            "context_inferred": False,
            "context_certified": False,
        })


    # package_semantic_intelligence_394
    # Package existing observations only. Semantic retrieval,
    # inference, and independent certification are not performed here.
    semantic_section_names = (
        "semantic_memory",
        "intelligence_graph",
        "canonical_concept",
        "canonical_concepts",
        "alias_enrichment",
        "topic_intent",
        "semantic_relationships",
        "semantic_relationship_signals",
        "semantic_context",
    )

    semantic_intelligence = []

    for index, entry in enumerate(enriched_candidates):
        sections = {
            name: deepcopy(entry[name])
            for name in semantic_section_names
            if name in entry
        }

        semantic_intelligence.append({
            "candidate_index": index,
            "status": (
                "semantic_sections_preserved"
                if sections else "semantic_sections_not_provided"
            ),
            "sections": sections,
            "present_section_names": list(sections),
            "missing_section_names": [
                name for name in semantic_section_names
                if name not in sections
            ],
            "source": "existing_enriched_candidate",
            "semantic_inference_performed": False,
            "semantic_proof_certified": False,
            "scorer_decision_performed": False,
            "automatic_linking_authorized": False,
        })


    # package_reasoning_395
    # Preserve the existing Reasoning Intelligence section as data.
    # Do not infer a reasoning conclusion or perform reasoning again.
    reasoning = []

    for index, entry in enumerate(enriched_candidates):
        section_present = "reasoning_intelligence" in entry
        source_output = (
            deepcopy(entry["reasoning_intelligence"])
            if section_present else None
        )

        if section_present:
            if not isinstance(source_output, dict):
                return reject("invalid_reasoning_section")

            source_status = source_output.get("status")

            if source_status is not None and not isinstance(
                source_status, str
            ):
                return reject("invalid_reasoning_status")
        else:
            source_status = None

        reasoning.append({
            "candidate_index": index,
            "status": (
                "reasoning_preserved"
                if section_present
                else "reasoning_not_provided"
            ),
            "source_section": "reasoning_intelligence",
            "source_status": source_status,
            "reasoning_output": source_output,
            "reasoning_available": section_present,
            "reasoning_executed_by_package": False,
            "independent_reasoning_verified": False,
            "semantic_proof_certified": False,
            "scorer_decision_performed": False,
            "automatic_linking_authorized": False,
        })


    # package_confidence_396
    # Preserve source confidence and sparse-state evidence without
    # fabricating selected-phrase confidence or rerunning producers.
    confidence = []

    for index, entry in enumerate(enriched_candidates):
        graph = entry.get("intelligence_graph")
        sparse = entry.get("sparse_intelligence")

        if graph is not None and not isinstance(graph, dict):
            return reject("invalid_confidence_graph_section")
        if sparse is not None and not isinstance(sparse, dict):
            return reject("invalid_sparse_confidence_section")

        graph_evidence = (
            graph.get("semantic_relationship_confidence_evidence")
            if isinstance(graph, dict) else None
        )
        sparse_evidence = (
            sparse.get("confidence_evidence_context")
            if isinstance(sparse, dict) else None
        )

        if graph_evidence is not None:
            if not isinstance(graph_evidence, dict):
                return reject("invalid_confidence_evidence_section")
            if (
                graph_evidence.get("schema_version")
                != "confidence_evidence_v1"
                or graph_evidence.get("status")
                != "source_confidence_preserved"
                or graph_evidence.get("overall_confidence") is not None
                or graph_evidence.get("overall_confidence_status")
                != "not_established"
                or graph_evidence.get("aggregation_authorized") is not False
                or graph_evidence.get("aggregation_performed") is not False
                or graph_evidence.get("aggregate_confidence_calibrated")
                is not False
                or graph_evidence.get("semantic_proof_certified") is not False
                or graph_evidence.get("automatic_linking_authorized")
                is not False
            ):
                return reject("unsupported_confidence_evidence_contract")

            records = graph_evidence.get("confidence_records")
            if (
                not isinstance(records, list)
                or type(graph_evidence.get("source_count")) is not int
                or len(records) != graph_evidence["source_count"]
            ):
                return reject("invalid_confidence_source_inventory")

            if any(
                not isinstance(record, dict)
                or record.get("phrase_level_semantic_confidence")
                is not None
                or record.get("selected_phrase_confidence_authorized")
                is not False
                or record.get("confidence_calibrated") is not False
                or record.get("independently_verified") is not False
                or record.get("certified") is not False
                for record in records
            ):
                return reject("unsupported_phrase_confidence_claim")

        if isinstance(sparse, dict):
            if (
                sparse.get("candidate_index") != index
                or sparse.get("original_candidate")
                != selected_candidates[index]
                or sparse.get("candidate_retained") is not True
                or sparse.get("confidence_score") is not None
                or sparse.get("scorer_decision_performed") is not False
                or sparse.get("automatic_linking_authorized") is not False
            ):
                return reject("invalid_sparse_confidence_contract")

            low_state = sparse.get("low_confidence_state")
            if low_state not in (
                "unknown",
                "not_assessable",
                "low_confidence",
                "not_low_confidence",
            ):
                return reject("invalid_low_confidence_state")

            if (
                graph_evidence != sparse_evidence
                or sparse.get("phrase_confidence_established") is not False
            ):
                return reject("confidence_producer_handoff_mismatch")

            if (
                graph_evidence is not None
                and low_state != "unknown"
            ):
                return reject("unverified_confidence_classification")

            confidence_status = low_state
        else:
            if graph_evidence is not None:
                return reject("confidence_producer_handoff_missing")
            confidence_status = "not_provided"

        confidence.append({
            "candidate_index": index,
            "status": (
                "confidence_evidence_preserved"
                if graph_evidence is not None
                else (
                    "sparse_confidence_preserved"
                    if sparse is not None
                    else "confidence_not_provided"
                )
            ),
            "source_confidence_evidence": deepcopy(graph_evidence),
            "sparse_confidence": deepcopy(sparse),
            "low_confidence_state": confidence_status,
            "phrase_level_confidence": None,
            "phrase_confidence_established": False,
            "source_confidence_aggregated_by_package": False,
            "confidence_calibrated_by_package": False,
            "semantic_proof_certified": False,
            "scorer_decision_performed": False,
            "automatic_linking_authorized": False,
        })


    # package_explainability_397
    # Preserve existing explanations and evidence associations.
    # The package does not generate explanations or certify evidence.
    explainability = []

    for index, entry in enumerate(enriched_candidates):
        present = "explainability" in entry

        if present:
            source_output = entry["explainability"]
            if not isinstance(source_output, dict):
                return reject("invalid_explainability_section")

            source_status = source_output.get("status")
            if source_status is not None and not isinstance(
                source_status, str
            ):
                return reject("invalid_explainability_status")

            association = source_output.get("evidence_association")
            if association is not None:
                if not isinstance(association, dict):
                    return reject("invalid_explainability_association")

                ids = association.get("evidence_ids")
                if (
                    not isinstance(ids, list)
                    or any(
                        not isinstance(eid, str) or not eid
                        for eid in ids
                    )
                    or type(association.get("evidence_count")) is not int
                    or association["evidence_count"] != len(ids)
                ):
                    return reject("invalid_explainability_evidence_ids")

                for evidence_id in ids:
                    evidence = evidence_registry.get(evidence_id)
                    if not isinstance(evidence, dict):
                        return reject("unresolved_explainability_evidence")
                    if (
                        type(evidence.get("candidate_index")) is not int
                        or evidence["candidate_index"] != index
                    ):
                        return reject("cross_candidate_explainability_evidence")
            else:
                ids = []
        else:
            source_output = None
            source_status = None
            association = None
            ids = []

        explainability.append({
            "candidate_index": index,
            "status": (
                "explainability_preserved"
                if present else "explainability_not_provided"
            ),
            "source_status": source_status,
            "explanation_output": deepcopy(source_output),
            "evidence_association": deepcopy(association),
            "evidence_ids": deepcopy(ids),
            "evidence_count": len(ids),
            "explanation_generated_by_package": False,
            "evidence_independently_verified_by_package": False,
            "semantic_proof_certified": False,
            "scorer_decision_performed": False,
            "automatic_linking_authorized": False,
        })


    # package_provenance_398
    # Preserve the Phase 3.7.10 provenance bundle exactly.
    # Do not create new provenance or claim independent verification.
    provenance = []

    for index, entry in enumerate(enriched_candidates):
        explanation = entry.get("explainability")

        if explanation is not None and not isinstance(
            explanation, dict
        ):
            return reject("invalid_provenance_explainability_source")

        present = (
            isinstance(explanation, dict)
            and "provenance" in explanation
        )

        if present:
            bundle = explanation["provenance"]
            if not isinstance(bundle, dict):
                return reject("invalid_provenance_bundle")

            if bundle.get("schema_version") != (
                "semantic_provenance_bundle_v1"
            ):
                return reject("unsupported_provenance_schema")

            candidate_provenance = bundle.get("candidate")
            cross_intelligence = bundle.get("cross_intelligence")
            consistency = bundle.get("consistency")

            if (
                not isinstance(candidate_provenance, dict)
                or not isinstance(cross_intelligence, dict)
                or not isinstance(consistency, dict)
            ):
                return reject("invalid_provenance_components")

            if any(
                bundle.get(field) is not False
                for field in (
                    "independent_provenance_verified",
                    "semantic_proof_certified",
                    "scorer_decision_performed",
                    "automatic_linking_authorized",
                )
            ):
                return reject("unsupported_provenance_authority")

            association = explanation.get("evidence_association")
            if not isinstance(association, dict):
                return reject("missing_provenance_evidence_association")

            evidence_ids = association.get("evidence_ids")
            if (
                not isinstance(evidence_ids, list)
                or any(
                    not isinstance(eid, str) or not eid
                    for eid in evidence_ids
                )
            ):
                return reject("invalid_provenance_evidence_ids")

            if (
                candidate_provenance.get("evidence_ids")
                != evidence_ids
                or consistency.get("checked_evidence_ids")
                != evidence_ids
            ):
                return reject("provenance_evidence_mismatch")

            for evidence_id in evidence_ids:
                record = evidence_registry.get(evidence_id)
                if not isinstance(record, dict):
                    return reject("unresolved_provenance_evidence")
                if (
                    type(record.get("candidate_index")) is not int
                    or record["candidate_index"] != index
                ):
                    return reject("cross_candidate_provenance_evidence")

            provenance_status = "provenance_preserved"
            output = deepcopy(bundle)
        else:
            evidence_ids = []
            provenance_status = "provenance_not_provided"
            output = None

        provenance.append({
            "candidate_index": index,
            "status": provenance_status,
            "source_section": "explainability.provenance",
            "provenance_output": output,
            "evidence_ids": deepcopy(evidence_ids),
            "evidence_count": len(evidence_ids),
            "provenance_generated_by_package": False,
            "independent_provenance_verified_by_package": False,
            "semantic_proof_certified": False,
            "scorer_decision_performed": False,
            "automatic_linking_authorized": False,
        })


    # package_certification_state_399
    # Observe existing certification state; never certify here.
    certification_state = []

    for index, entry in enumerate(enriched_candidates):
        explanation = entry.get("explainability")
        sparse = entry.get("sparse_intelligence")

        if explanation is not None and not isinstance(
            explanation, dict
        ):
            return reject("invalid_certification_explanation")

        if sparse is not None and not isinstance(sparse, dict):
            return reject("invalid_certification_sparse_section")

        association = (
            explanation.get("evidence_association")
            if isinstance(explanation, dict) else None
        )

        if association is not None:
            if not isinstance(association, dict):
                return reject("invalid_certification_association")

            evidence_ids = association.get("evidence_ids")
            if (
                not isinstance(evidence_ids, list)
                or any(
                    not isinstance(eid, str) or not eid
                    for eid in evidence_ids
                )
                or type(association.get("evidence_count")) is not int
                or association["evidence_count"] != len(evidence_ids)
            ):
                return reject("invalid_certification_evidence_ids")
        else:
            evidence_ids = []

        if isinstance(sparse, dict):
            if (
                type(sparse.get("candidate_index")) is not int
                or sparse["candidate_index"] != index
                or sparse.get("original_candidate")
                != selected_candidates[index]
                or sparse.get("candidate_retained") is not True
            ):
                return reject("invalid_certification_candidate_identity")

            # Phase 3.9.6 fixtures may contain confidence state only.
            # Validate evidence consistency when an evidence inventory
            # exists; do not silently treat a partial inventory as complete.
            has_ids = "evidence_ids" in sparse
            has_count = "evidence_count" in sparse

            if has_ids != has_count:
                return reject("incomplete_sparse_evidence_inventory")

            if has_ids:
                sparse_ids = sparse["evidence_ids"]
                sparse_count = sparse["evidence_count"]

                if (
                    not isinstance(sparse_ids, list)
                    or any(
                        not isinstance(eid, str) or not eid
                        for eid in sparse_ids
                    )
                    or type(sparse_count) is not int
                    or sparse_count != len(sparse_ids)
                    or sparse_ids != evidence_ids
                ):
                    return reject("certification_sparse_evidence_mismatch")

        provenance_bundle = (
            explanation.get("provenance")
            if isinstance(explanation, dict) else None
        )

        for source in (association, sparse, provenance_bundle):
            if source is None:
                continue
            if not isinstance(source, dict):
                return reject("invalid_certification_source")

            for flag in (
                "certified",
                "independently_verified",
                "independent_provenance_verified",
                "semantic_proof_certified",
                "semantic_certification_performed",
                "automatic_linking_authorized",
                "scorer_decision_performed",
            ):
                if flag in source and source[flag] is not False:
                    return reject("unsupported_certification_authority")

        for evidence_id in evidence_ids:
            record = evidence_registry.get(evidence_id)

            if (
                not isinstance(record, dict)
                or type(record.get("candidate_index")) is not int
                or record["candidate_index"] != index
            ):
                return reject("invalid_certification_evidence_reference")

            for flag in (
                "certified",
                "independently_verified",
                "semantic_proof_certified",
                "automatic_linking_authorized",
            ):
                if flag in record and record[flag] is not False:
                    return reject("unsupported_evidence_certification")

        if evidence_ids:
            state = "evidence_present_uncertified"
        elif association is not None:
            state = "no_evidence"
        else:
            state = "certification_not_established"

        certification_state.append({
            "candidate_index": index,
            "status": state,
            "evidence_ids": deepcopy(evidence_ids),
            "evidence_count": len(evidence_ids),
            "independent_evidence_verification": "not_established",
            "semantic_proof_certification": "not_established",
            "candidate_certification": "not_established",
            "certification_performed_by_package": False,
            "scorer_decision_performed": False,
            "automatic_linking_authorized": False,
        })


    # package_intelligence_status_3910
    # Preserve source-reported states. Do not infer overall readiness,
    # semantic validity, or authorization from the presence of records.
    intelligence_status = []

    for index, entry in enumerate(enriched_candidates):
        source_sections = {
            "sparse_intelligence": entry.get("sparse_intelligence"),
            "reasoning_intelligence": entry.get("reasoning_intelligence"),
            "semantic_memory": entry.get("semantic_memory"),
            "intelligence_graph": entry.get("intelligence_graph"),
            "explainability": entry.get("explainability"),
            "scorer_readiness": entry.get("scorer_readiness"),
        }

        source_statuses = {}
        missing_sections = []

        for name, section in source_sections.items():
            if name not in entry:
                missing_sections.append(name)
                continue

            if not isinstance(section, dict):
                # Existing earlier validators cover some sections.
                # A status-bearing section must be structurally valid.
                return reject("invalid_intelligence_status_section")

            status = section.get("status")
            if status is not None and not isinstance(status, str):
                return reject("invalid_intelligence_source_status")

            source_statuses[name] = status

        sparse = entry.get("sparse_intelligence")
        if isinstance(sparse, dict):
            sparse_classification = sparse.get(
                "intelligence_status",
                sparse.get("classification"),
            )
            if (
                sparse_classification is not None
                and not isinstance(sparse_classification, str)
            ):
                return reject("invalid_sparse_intelligence_status")
        else:
            sparse_classification = None

        packaged_statuses = {
            "phrase_context": phrase_context[index]["status"],
            "semantic_intelligence": semantic_intelligence[index]["status"],
            "reasoning": reasoning[index]["status"],
            "confidence": confidence[index]["status"],
            "explainability": explainability[index]["status"],
            "provenance": provenance[index]["status"],
            "certification_state": certification_state[index]["status"],
        }

        intelligence_status.append({
            "candidate_index": index,
            "status": (
                "source_statuses_preserved"
                if source_statuses
                else "source_statuses_not_provided"
            ),
            "source_statuses": deepcopy(source_statuses),
            "missing_source_sections": missing_sections,
            "sparse_intelligence_classification": (
                sparse_classification
            ),
            "packaged_section_statuses": packaged_statuses,
            "overall_intelligence_readiness": "not_determined",
            "semantic_validity_certified": False,
            "status_inference_performed_by_package": False,
            "scorer_decision_performed": False,
            "automatic_linking_authorized": False,
        })

    package.update({
        "status": "package_envelope_created",
        "intelligence_status": intelligence_status,
        "certification_state": certification_state,
        "provenance": provenance,
        "explainability": explainability,
        "confidence": confidence,
        "reasoning": reasoning,
        "semantic_intelligence": semantic_intelligence,
        "phrase_context": phrase_context,
        "phrase_identity": phrase_identity,
        "candidate_count": count,
        "enriched_candidates": deepcopy(enriched_candidates),
        "evidence_registry": deepcopy(evidence_registry),
        "sparse_candidate_retention": deepcopy(retention),
        "sparse_scorer_advisory_handoff": deepcopy(advisory),
        "original_candidates_preserved": True,
    })
    return package
