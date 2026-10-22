"""
Phase 3.7 ? Enricher-to-original-Scorer advisory handoff.

This module packages information but never scores, ranks,
filters, allocates highlights, resolves targets or inserts links.
It is not a production Scorer integration.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class HandoffContractError(ValueError):
    pass


def prepare_original_scorer_handoff(
    *, enrichment_package: dict[str, Any]
) -> dict[str, Any]:
    if not isinstance(enrichment_package, dict):
        raise HandoffContractError("Invalid enrichment package")

    if enrichment_package.get("ok") is not True:
        raise HandoffContractError("Enrichment package is not successful")

    contract = enrichment_package.get("downstream_contract")
    if not isinstance(contract, dict):
        raise HandoffContractError("Missing downstream contract")

    if (
        contract.get("consumer") != "original_scorer"
        or contract.get("enrichment_is_advisory") is not True
    ):
        raise HandoffContractError("Scorer authority contract mismatch")

    for boundary in (
        "final_link_allocation_performed",
        "route_dispatch_performed",
        "target_resolution_performed",
        "final_highlight_validation_performed",
    ):
        if contract.get(boundary) is not False:
            raise HandoffContractError(
                "Premature downstream action: " + boundary
            )

    candidates = enrichment_package.get("candidates")
    enriched = enrichment_package.get("enriched_candidates")
    registry = enrichment_package.get("evidence_registry")

    if not isinstance(candidates, list):
        raise HandoffContractError("Invalid candidate list")
    if not isinstance(enriched, list):
        raise HandoffContractError("Invalid enriched candidate list")
    if not isinstance(registry, dict):
        raise HandoffContractError("Invalid evidence registry")

    if (
        len(candidates) != len(enriched)
        or enrichment_package.get("candidate_count")
           != len(candidates)
    ):
        raise HandoffContractError("Candidate count mismatch")

    output = []

    for index, (candidate, entry) in enumerate(
        zip(candidates, enriched)
    ):
        if not isinstance(candidate, dict):
            raise HandoffContractError("Invalid original candidate")
        if not isinstance(entry, dict):
            raise HandoffContractError("Invalid enriched candidate")

        if type(entry.get("candidate_index")) is not int or (
            entry["candidate_index"] != index
        ):
            raise HandoffContractError("Candidate order mismatch")

        if entry.get("original_candidate") != candidate:
            raise HandoffContractError("Original candidate mismatch")

        candidate_id = entry.get("candidate_id")
        if candidate_id is None:
            raise HandoffContractError("Missing candidate identity")

        integrity = entry.get("evidence_certification")
        explanation = entry.get("explainability")
        readiness = entry.get("scorer_readiness")

        if not isinstance(integrity, dict):
            raise HandoffContractError("Missing integrity result")
        if not isinstance(explanation, dict):
            raise HandoffContractError("Missing explanation")
        if not isinstance(readiness, dict):
            raise HandoffContractError("Missing readiness information")

        if (
            integrity.get("certified") is not False
            or integrity.get("certification_performed") is not False
            or integrity.get("semantic_certification_status")
               != "not_performed"
        ):
            raise HandoffContractError("Unexpected certification claim")

        if (
            integrity.get("workspace_id")
            != enrichment_package.get("context", {}).get("workspace_id")
            or integrity.get("candidate_index") != index
        ):
            raise HandoffContractError("Integrity identity mismatch")

        if integrity.get("status") not in (
            "integrity_passed",
            "integrity_failed",
            "no_evidence",
        ):
            raise HandoffContractError("Unknown integrity status")

        if explanation.get("certified") is not False:
            raise HandoffContractError("Unexpected explanation certification")

        if explanation.get("scorer_decision_performed") is not False:
            raise HandoffContractError("Premature Scorer decision")

        if readiness.get("ready") is not False:
            raise HandoffContractError("Premature readiness approval")

        references = [
            key for key, record in registry.items()
            if isinstance(record, dict)
            and type(record.get("candidate_index")) is int
            and record["candidate_index"] == index
        ]

        if (
            not isinstance(explanation.get("evidence_ids"), list)
            or set(explanation["evidence_ids"]) != set(references)
            or len(explanation["evidence_ids"]) != len(
                set(explanation["evidence_ids"])
            )
        ):
            raise HandoffContractError("Evidence references mismatch")

        output.append({
            "candidate_id": deepcopy(candidate_id),
            "candidate_index": index,
            "original_candidate": deepcopy(candidate),
            "advisory_enrichment": deepcopy(entry),
            "evidence_ids": deepcopy(references),
            "evidence_integrity_status": integrity["status"],
            "scorer_decision": "not_performed",
            "linking_decision": "not_performed",
        })

    return {
        "ok": True,
        "component": "semantic_enricher_scorer_handoff",
        "consumer": "original_scorer",
        "status": "advisory_handoff_prepared",
        "production_scorer_invoked": False,
        "candidates_received": len(candidates),
        "candidates_forwarded": len(output),
        "candidates_removed": 0,
        "candidates": output,
        "evidence_registry": deepcopy(registry),
        "downstream_contract": deepcopy(contract),
        "semantic_certification_performed": False,
        "scoring_performed": False,
        "highlight_allocation_performed": False,
        "linking_performed": False,
    }


__all__ = [
    "HandoffContractError",
    "prepare_original_scorer_handoff",
]
