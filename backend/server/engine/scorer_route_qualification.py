"""LinkCraftor replacement Scorer: route qualification.

Phase 4.4.1: Internal qualification only.
No resolver execution, target selection, color assignment,
highlight allocation, or production linking authorization.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class RouteQualificationError(ValueError):
    pass


def qualify_internal_route(
    *,
    candidate: dict[str, Any],
    phrase_evidence: dict[str, Any],
    evidence_registry: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate direct-internal eligibility from explicit advisory evidence.

    No old Scorer score thresholds are imported.
    Evidence references are checked for presence, not authenticated.
    """
    if not isinstance(candidate, dict):
        raise RouteQualificationError("candidate must be a mapping")

    if not isinstance(phrase_evidence, dict):
        raise RouteQualificationError(
            "phrase_evidence must be a mapping"
        )

    if not isinstance(evidence_registry, dict):
        raise RouteQualificationError(
            "evidence_registry must be a mapping"
        )

    candidate_id = candidate.get("upstream_candidate_id")
    phrase = candidate.get("phrase")

    if (
        not isinstance(candidate_id, str)
        or not candidate_id.strip()
        or not isinstance(phrase, str)
        or not phrase.strip()
    ):
        raise RouteQualificationError(
            "candidate identity and phrase are required"
        )

    if (
        phrase_evidence.get("candidate_id") != candidate_id
        or phrase_evidence.get("phrase") != phrase
    ):
        raise RouteQualificationError(
            "phrase evidence identity mismatch"
        )

    reason_codes = []

    if phrase_evidence.get("anchor_suitable") is not True:
        reason_codes.append("ANCHOR_NOT_ESTABLISHED")

    if phrase_evidence.get("context_clear") is not True:
        reason_codes.append("CONTEXT_NOT_ESTABLISHED")

    if (
        phrase_evidence.get("direct_topic_supported")
        is not True
    ):
        reason_codes.append(
            "DIRECT_TOPIC_RELATIONSHIP_NOT_ESTABLISHED"
        )

    evidence_ids = phrase_evidence.get(
        "direct_topic_evidence_ids", []
    )

    if (
        not isinstance(evidence_ids, list)
        or any(
            not isinstance(value, str) or not value
            for value in evidence_ids
        )
        or len(evidence_ids) != len(set(evidence_ids))
    ):
        raise RouteQualificationError(
            "invalid direct-topic evidence IDs"
        )

    missing = [
        value for value in evidence_ids
        if value not in evidence_registry
    ]

    if missing:
        reason_codes.append(
            "DIRECT_TOPIC_EVIDENCE_REFERENCE_MISSING"
        )

    if not evidence_ids:
        reason_codes.append(
            "DIRECT_TOPIC_EVIDENCE_ABSENT"
        )

    qualified = not reason_codes

    return {
        "candidate_id": candidate_id,
        "phrase": phrase,
        "route": "INTERNAL",
        "qualified": qualified,
        "qualification_status": (
            "ADVISORY_QUALIFIED"
            if qualified else "NOT_ESTABLISHED"
        ),
        "reason_codes": (
            ["DIRECT_INTERNAL_QUALIFICATION_SUPPORTED"]
            if qualified else reason_codes
        ),
        "evidence_ids": deepcopy(evidence_ids),
        "evidence_reference_presence_checked": True,
        "evidence_provenance_authenticated": False,
        "ats_searched": False,
        "target_resolved": False,
        "route_ranked": False,
        "ui_classification_assigned": False,
        "highlight_allocated": False,
        "automatic_linking_authorized": False,
    }



def qualify_internal_from_enricher_handoff(
    *, handoff: dict[str, Any],
    candidate_index: int,
    workspace_id: str,
) -> dict[str, Any]:
    """Consume genuine Enricher evidence without inventing direct matches.

    Semantic memory, concept and graph evidence are retained but cannot
    alone certify a direct relationship to an owned ATS target.
    """
    if not isinstance(handoff, dict):
        raise RouteQualificationError("Invalid Enricher handoff")

    if (
        handoff.get("ok") is not True
        or handoff.get("consumer") != "original_scorer"
        or handoff.get("candidates_removed") != 0
        or handoff.get("automatic_linking_authorized") is True
    ):
        raise RouteQualificationError("Unsafe Enricher handoff")

    rows = handoff.get("candidates")
    registry = handoff.get("evidence_registry")

    if not isinstance(rows, list) or not isinstance(registry, dict):
        raise RouteQualificationError("Invalid handoff records")

    if (
        type(candidate_index) is not int
        or not 0 <= candidate_index < len(rows)
        or not isinstance(workspace_id, str)
        or not workspace_id.strip()
    ):
        raise RouteQualificationError("Invalid candidate scope")

    row = rows[candidate_index]

    if not isinstance(row, dict):
        raise RouteQualificationError("Invalid candidate row")

    candidate = row.get("original_candidate")
    enrichment = row.get("advisory_enrichment")
    evidence_ids = row.get("evidence_ids")

    if (
        not isinstance(candidate, dict)
        or not isinstance(enrichment, dict)
        or not isinstance(evidence_ids, list)
        or row.get("candidate_index") != candidate_index
        or enrichment.get("candidate_index") != candidate_index
        or row.get("candidate_id")
        != candidate.get("upstream_candidate_id")
        or enrichment.get("candidate_id") != row.get("candidate_id")
        or enrichment.get("original_candidate") != candidate
        or len(evidence_ids) != len(set(evidence_ids))
    ):
        raise RouteQualificationError("Candidate lineage mismatch")

    observed = []

    for evidence_id in evidence_ids:
        if not isinstance(evidence_id, str) or not evidence_id:
            raise RouteQualificationError("Invalid evidence ID")

        record = registry.get(evidence_id)

        if not isinstance(record, dict):
            raise RouteQualificationError("Missing evidence record")

        if (
            record.get("workspace_id") != workspace_id
            or record.get("candidate_index") != candidate_index
        ):
            raise RouteQualificationError(
                "Cross-workspace or cross-candidate evidence"
            )

        observed.append({
            "evidence_id": evidence_id,
            "source": record.get("source"),
            "evidence_type": record.get("evidence_type"),
        })

    # A directly named topic may qualify provisionally even before
    # ATS resolves an owned destination. Do not treat semantic
    # associations or evidence IDs alone as direct-topic proof.
    context = enrichment.get("semantic_context")
    if not isinstance(context, dict):
        context = {}

    topic = context.get("detected_topic")
    phrase = candidate.get("phrase")

    def normalize_topic(value):
        if not isinstance(value, str):
            return ""
        return " ".join(value.casefold().split())

    source_context = extract_candidate_qualification_context(
        candidate=candidate,
    )

    import re

    phrase_key = normalize_topic(phrase)

    def contains_complete_phrase(value):
        if not isinstance(value, str) or not phrase_key:
            return False

        normalized = normalize_topic(value)

        return re.search(
            r"(?<!\w)" + re.escape(phrase_key) + r"(?!\w)",
            normalized,
        ) is not None

    phrase_in_verified_context = any(
        contains_complete_phrase(source_context[key])
        for key in ("sentence_context", "paragraph_context")
    )

    topic_identity = (
        context.get("status") in {"completed", "ok"}
        and bool(phrase_key)
        and phrase_key == normalize_topic(topic)
        and phrase_in_verified_context
    )

    result = qualify_internal_route(
        candidate=candidate,
        phrase_evidence={
            "candidate_id": row["candidate_id"],
            "phrase": phrase,
            "anchor_suitable": False,
            "context_clear": False,
            "direct_topic_supported": False,
            "direct_topic_evidence_ids": [],
        },
        evidence_registry=registry,
    )

    result["observed_enricher_evidence"] = deepcopy(observed)
    result["enricher_evidence_inspected"] = True
    result["verified_candidate_context"] = deepcopy(source_context)
    result["phrase_in_verified_context"] = phrase_in_verified_context
    result["direct_topic_identity_observed"] = topic_identity
    result["direct_topic_identity_source"] = (
        "semantic_context.detected_topic"
        if topic_identity else None
    )

    if topic_identity:
        result["qualified"] = True
        result["qualification_status"] = "ADVISORY_QUALIFIED"
        result["reason_codes"] = [
            "DIRECT_TOPIC_IDENTITY_OBSERVED"
        ]
    else:
        result["qualified"] = False
        result["qualification_status"] = "INSUFFICIENT_EVIDENCE"
        result["reason_codes"] = [
            "DIRECT_TOPIC_IDENTITY_NOT_ESTABLISHED"
            if observed or topic
            else "ENRICHER_EVIDENCE_UNAVAILABLE"
        ]

    # Topic identity is not target ownership or provenance proof.
    result["qualification_decision_final"] = False
    result["direct_owned_target_evidence_available"] = False
    result["direct_target_qualification_pending"] = True
    result["evidence_provenance_authenticated"] = False
    result["ats_searched"] = False
    result["target_resolved"] = False
    result["route_ranked"] = False
    result["ui_classification_assigned"] = False
    result["highlight_allocated"] = False
    result["automatic_linking_authorized"] = False

    return result



def qualify_semantic_from_enricher_handoff(
    *,
    handoff: dict[str, Any],
    candidate_index: int,
    workspace_id: str,
) -> dict[str, Any]:
    """Evaluate explicit candidate-scoped conceptual relationships.

    A supported graph relationship establishes advisory route suitability,
    not the existence or suitability of an owned ATS target.
    """
    # Reuse the established lineage and workspace-evidence validation.
    base = qualify_internal_from_enricher_handoff(
        handoff=handoff,
        candidate_index=candidate_index,
        workspace_id=workspace_id,
    )

    row = handoff["candidates"][candidate_index]
    registry = handoff["evidence_registry"]

    supported = []
    observed = []

    for evidence_id in row["evidence_ids"]:
        record = registry[evidence_id]

        if (
            record.get("source") != "uploaded_entity_graph"
            or record.get("evidence_type")
            != "observed_graph_relationship"
        ):
            continue

        relationship = record.get("relationship_type")
        source_node = record.get("source_node_id")
        target_node = record.get("target_node_id")

        observed.append({
            "evidence_id": evidence_id,
            "relationship_type": deepcopy(relationship),
            "source_node_id": deepcopy(source_node),
            "target_node_id": deepcopy(target_node),
        })

        # Evaluate whether this graph edge involves the candidate.
        # This remains advisory; semantic depth and provenance are
        # not independently certified here.
        import re

        def concept_key(value):
            if not isinstance(value, str):
                return ""
            return " ".join(
                re.findall(r"\w+", value.casefold().replace("_", " "))
            )

        candidate_key = concept_key(base["phrase"])
        source_key = concept_key(source_node)
        target_key = concept_key(target_node)

        candidate_in_edge = (
            bool(candidate_key)
            and candidate_key in (source_key, target_key)
        )

        verified_context = (
            base.get("phrase_in_verified_context") is True
        )

        if (
            relationship == "related_to"
            and bool(source_key)
            and bool(target_key)
            and source_key != target_key
            and candidate_in_edge
            and verified_context
        ):
            supported.append(evidence_id)

    qualified = bool(supported)

    return {
        "candidate_id": deepcopy(base["candidate_id"]),
        "phrase": deepcopy(base["phrase"]),
        "route": "SEMANTIC",
        "qualified": qualified,
        "qualification_status": (
            "ADVISORY_QUALIFIED"
            if qualified else "INSUFFICIENT_EVIDENCE"
        ),
        "qualification_decision_final": False,
        "reason_codes": (
            ["EXPLICIT_CONCEPT_RELATIONSHIP_OBSERVED"]
            if qualified else
            ["SEMANTIC_RELATIONSHIP_NOT_ESTABLISHED"]
        ),
        "relationship_evidence_ids": deepcopy(supported),
        "observed_graph_relationships": deepcopy(observed),
        "candidate_relationship_context_verified": (
            base.get("phrase_in_verified_context") is True
        ),
        "evidence_provenance_authenticated": False,
        "candidate_graph_relevance_certified": False,
        "ats_searched": False,
        "target_resolved": False,
        "route_ranked": False,
        "ui_classification_assigned": False,
        "highlight_allocated": False,
        "automatic_linking_authorized": False,
    }



def extract_candidate_qualification_context(
    *,
    candidate: dict[str, Any],
) -> dict[str, Any]:
    """Read the existing verified-context contract.

    Consumes upstream verification markers; does not independently
    authenticate original document spans or perform qualification.
    """
    if not isinstance(candidate, dict):
        raise RouteQualificationError("Candidate must be a mapping")

    candidate_id = candidate.get("upstream_candidate_id")
    phrase = candidate.get("phrase")

    if (
        not isinstance(candidate_id, str)
        or not candidate_id.strip()
        or not isinstance(phrase, str)
        or not phrase.strip()
    ):
        raise RouteQualificationError(
            "Candidate identity and phrase required"
        )

    span_verified = (
        candidate.get("selection_source_span_status") == "verified"
    )

    contexts = {}
    statuses = {}

    for kind in ("sentence", "paragraph"):
        field = f"selection_{kind}_context"
        status_field = f"selection_{kind}_context_status"

        raw = candidate.get(field)
        status = candidate.get(status_field)

        accepted = (
            span_verified
            and status == "derived_from_verified_span"
            and isinstance(raw, str)
            and bool(raw.strip())
        )

        contexts[kind] = deepcopy(raw) if accepted else None
        statuses[kind] = (
            "available_upstream_verified"
            if accepted
            else "unavailable_or_unverified"
        )

    return {
        "candidate_id": candidate_id,
        "phrase": phrase,
        "source_span_marked_verified": span_verified,
        "sentence_context": contexts["sentence"],
        "paragraph_context": contexts["paragraph"],
        "sentence_status": statuses["sentence"],
        "paragraph_status": statuses["paragraph"],
        "usable_context_available": any(
            value is not None for value in contexts.values()
        ),
        "independent_source_authentication_performed": False,
        "qualification_decision_performed": False,
        "automatic_linking_authorized": False,
    }



def qualify_external_from_enricher_handoff(
    *,
    handoff: dict[str, Any],
    candidate_index: int,
    workspace_id: str,
) -> dict[str, Any]:
    """Identify explicit source-attribution needs in verified context.

    This is a conservative advisory signal, not source verification,
    authority certification or external URL resolution.
    """
    import re

    base = qualify_internal_from_enricher_handoff(
        handoff=handoff,
        candidate_index=candidate_index,
        workspace_id=workspace_id,
    )

    row = handoff["candidates"][candidate_index]
    candidate = row["original_candidate"]

    context = extract_candidate_qualification_context(
        candidate=candidate,
    )

    phrase = candidate["phrase"]
    sentence = context["sentence_context"]

    patterns = {
        "EXPLICIT_SOURCE_ATTRIBUTION": (
            r"\baccording\s+to\s+(?:the\s+)?{phrase}(?!\w)"
        ),
        "EXPLICIT_REPORT_ATTRIBUTION": (
            r"\b(?:a|an|the)\s+(?:published\s+)?"
            r"(?:report|study|analysis)\s+by\s+"
            r"(?:the\s+)?{phrase}(?!\w)"
        ),
        "EXPLICIT_SOURCE_REPORTING": (
            r"(?<!\w){phrase}\s+"
            r"(?:reported|found|estimated|published)\b"
        ),
    }

    matched = []

    if isinstance(sentence, str) and sentence.strip():
        normalized_sentence = " ".join(sentence.casefold().split())
        normalized_phrase = " ".join(phrase.casefold().split())

        if normalized_phrase:
            escaped_phrase = re.escape(normalized_phrase)

            for reason, template in patterns.items():
                expression = template.format(phrase=escaped_phrase)

                if re.search(expression, normalized_sentence):
                    matched.append(reason)

    # Quantified factual statements may justify independent
    # evidence even when no source is named. This identifies
    # citation need, not truth, authority, or source existence.
    if isinstance(sentence, str) and sentence.strip():
        normalized_sentence = " ".join(sentence.casefold().split())
        normalized_phrase = " ".join(phrase.casefold().split())

        phrase_present = (
            bool(normalized_phrase)
            and re.search(
                r"(?<!\w)"
                + re.escape(normalized_phrase)
                + r"(?!\w)",
                normalized_sentence,
            ) is not None
        )

        quantified_claim = re.search(
            r"\b\d+(?:\.\d+)?\s*"
            r"(?:%|percent\b|percentage points\b)",
            normalized_sentence,
        ) is not None

        magnitude_claim = re.search(
            r"\b(?:increased|decreased|grew|declined|"
            r"rose|fell|dropped)\s+by\s+"
            r"\d+(?:\.\d+)?\s*"
            r"(?:million|billion)\b",
            normalized_sentence,
        ) is not None

        if phrase_present and (quantified_claim or magnitude_claim):
            matched.append("QUANTIFIED_CLAIM_REQUIRES_EVIDENCE")

    qualified = bool(matched)

    return {
        "candidate_id": deepcopy(base["candidate_id"]),
        "phrase": deepcopy(phrase),
        "route": "EXTERNAL",
        "qualified": qualified,
        "qualification_status": (
            "ADVISORY_QUALIFIED"
            if qualified else "INSUFFICIENT_EVIDENCE"
        ),
        "qualification_decision_final": False,
        "reason_codes": (
            deepcopy(matched)
            if qualified else
            ["EXTERNAL_EVIDENCE_NEED_NOT_ESTABLISHED"]
        ),
        "citation_need_observed": qualified,
        "citation_need_basis": (
            "verified_sentence_explicit_attribution"
            if qualified else None
        ),
        "verified_sentence_available": (
            isinstance(sentence, str) and bool(sentence.strip())
        ),
        "evidence_ids": deepcopy(row["evidence_ids"]),
        "source_claim_verified": False,
        "source_authority_certified": False,
        "evidence_provenance_authenticated": False,
        "ats_searched": False,
        "target_resolved": False,
        "route_ranked": False,
        "ui_classification_assigned": False,
        "highlight_allocated": False,
        "automatic_linking_authorized": False,
    }



def evaluate_independent_route_qualifications(
    *,
    handoff: dict[str, Any],
    candidate_index: int,
    workspace_id: str,
) -> dict[str, Any]:
    """Preserve three independent advisory route assessments.

    No route ranking, fallback, target resolution, allocation,
    color assignment or final linking decision occurs here.
    """
    evaluators = (
        ("INTERNAL", qualify_internal_from_enricher_handoff),
        ("SEMANTIC", qualify_semantic_from_enricher_handoff),
        ("EXTERNAL", qualify_external_from_enricher_handoff),
    )

    decisions = {}
    qualified_routes = []

    for route, evaluator in evaluators:
        decision = evaluator(
            handoff=handoff,
            candidate_index=candidate_index,
            workspace_id=workspace_id,
        )

        if (
            decision.get("route") != route
            or decision.get("qualification_decision_final") is not False
            or decision.get("automatic_linking_authorized") is not False
            or decision.get("ats_searched") is not False
            or decision.get("target_resolved") is not False
            or decision.get("ui_classification_assigned") is not False
        ):
            raise RouteQualificationError(
                "Route assessment crossed qualification boundary"
            )

        decisions[route] = deepcopy(decision)

        if decision.get("qualified") is True:
            qualified_routes.append(route)

    identities = {
        (value["candidate_id"], value["phrase"])
        for value in decisions.values()
    }

    if len(identities) != 1:
        raise RouteQualificationError(
            "Independent route identity disagreement"
        )

    candidate_id, phrase = next(iter(identities))

    unresolved_routes = [
        route
        for route, decision in decisions.items()
        if decision.get("qualification_status")
        == "INSUFFICIENT_EVIDENCE"
    ]

    return {
        "candidate_id": candidate_id,
        "phrase": phrase,
        "route_qualifications": decisions,
        "provisionally_qualified_routes": qualified_routes,
        "qualification_combination": (
            "+".join(qualified_routes)
            if qualified_routes else "NONE"
        ),
        "unresolved_routes": unresolved_routes,
        "qualification_evidence_complete": False,
        "none_is_definitive": False,
        "qualification_review_required": True,
        "route_ranking_performed": False,
        "primary_route_selected": False,
        "target_resolution_performed": False,
        "ui_classification_assigned": False,
        "highlight_allocation_performed": False,
        "automatic_linking_authorized": False,
        "qualification_certified": False,
    }
