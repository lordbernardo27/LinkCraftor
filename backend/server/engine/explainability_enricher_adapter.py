"""
Phase 3.5: read-only, evidence-grounded Enricher explanations.

Explains observed evidence, not linking decisions or certified facts.
Does not invoke downstream Resolver or certified Explainability.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


SOURCE_DESCRIPTIONS = {
    "semantic_memory": (
        "Historical Semantic Memory retrieval evidence"
    ),
    "workspace_concept_store": (
        "Stored workspace concept or alias evidence"
    ),
    "uploaded_entity_graph": (
        "Observed entity graph relationship evidence"
    ),
    "workspace_cross_document_reasoning": (
        "Document occurrence or cross-document context"
    ),
}


def explain_candidate_evidence(
    *,
    candidate_index: int,
    candidate: dict[str, Any],
    evidence_ids: list[str],
    evidence_registry: dict[str, Any],
) -> dict[str, Any]:
    if type(candidate_index) is not int or candidate_index < 0:
        raise ValueError("Invalid candidate index")

    if not isinstance(candidate, dict):
        raise ValueError("Candidate must be a dictionary")

    if not isinstance(evidence_ids, list) or any(
        not isinstance(eid, str) or not eid
        for eid in evidence_ids
    ):
        raise ValueError("Invalid evidence ID list")

    if len(set(evidence_ids)) != len(evidence_ids):
        raise ValueError("Duplicate evidence IDs")

    if not isinstance(evidence_registry, dict):
        raise ValueError("Invalid evidence registry")

    sources = []
    trace = []
    evidence_types = []

    # Validate the complete set before constructing explanations.
    for evidence_id in evidence_ids:
        if evidence_id not in evidence_registry:
            raise ValueError(
                f"Unresolved evidence reference: {evidence_id}"
            )

        record = evidence_registry[evidence_id]

        if not isinstance(record, dict):
            raise ValueError("Invalid evidence record")

        if record.get("candidate_index") != candidate_index:
            raise ValueError("Cross-candidate evidence reference")

        if record.get("certified") is not False:
            raise ValueError(
                "Expected uncertified advisory evidence"
            )

        source = record.get("source")
        kind = record.get("evidence_type")

        if source not in SOURCE_DESCRIPTIONS:
            raise ValueError("Unknown evidence source")

        # Preserve the legacy Semantic Memory evidence contract.
        if source == "semantic_memory" and kind is None:
            kind = "legacy_semantic_memory_record"
        if not isinstance(kind, str) or not kind:
            raise ValueError("Missing evidence type")

        if source not in sources:
            sources.append(source)

        evidence_types.append(kind)
        trace.append({
            "evidence_id": evidence_id,
            "source": source,
            "evidence_type": kind,
            "certified": False,
            "source_record": deepcopy(record),
        })

    observations = [
        {
            "source": source,
            "description": SOURCE_DESCRIPTIONS[source],
            "evidence_ids": [
                item["evidence_id"] for item in trace
                if item["source"] == source
            ],
            "interpretation": "supporting_observation_only",
        }
        for source in sources
    ]

    if trace:
        summary = (
            "Supporting evidence was retrieved from "
            + ", ".join(
                SOURCE_DESCRIPTIONS[source] for source in sources
            )
            + ". This evidence has not been certified and "
            + "does not establish that a link should be added."
        )
        status = "evidence_explained"
    else:
        summary = (
            "No supporting evidence was registered for this "
            "candidate. This does not establish that the "
            "phrase is irrelevant or unsuitable for linking."
        )
        status = "no_evidence"

    return {
        "status": status,
        "candidate_index": candidate_index,
        "candidate_id": candidate.get("upstream_candidate_id"),
        "phrase": candidate.get("phrase"),
        "explanation_type": "pre_scorer_evidence_explanation",
        "human_summary": summary,
        "source_count": len(sources),
        "evidence_count": len(trace),
        "evidence_ids": list(evidence_ids),
        "evidence_types": evidence_types,
        "source_observations": observations,
        "evidence_trace": trace,
        "uncertainty": {
            "evidence_certified": False,
            "semantic_equivalence_proven": False,
            "phrase_relevance_finalized": False,
            "linking_decision_performed": False,
            "confidence_score_assigned": False,
        },
        "certified": False,
        "approved_link_target": False,
        "scorer_decision_performed": False,
    }


__all__ = ["explain_candidate_evidence"]
