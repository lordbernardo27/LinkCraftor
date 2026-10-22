"""
Phase 3.6: read-only integrity checks for advisory evidence.

Structural validity does not imply semantic correctness, evidence
certification, a phrase score, or authorization to insert links.
"""

from __future__ import annotations

import re
from typing import Any


ALLOWED_SOURCES = {
    "semantic_memory",
    "workspace_concept_store",
    "uploaded_entity_graph",
    "workspace_cross_document_reasoning",
}

ALLOWED_TYPES = {
    "semantic_memory": {
        "historical_memory_match",
        "memory_recall_match",
    },
    "workspace_concept_store": {
        "concept_or_alias_match",
    },
    "uploaded_entity_graph": {
        "observed_graph_relationship",
    },
    "workspace_cross_document_reasoning": {
        "document_phrase_occurrence",
        "document_relationship_context",
    },
}


def validate_candidate_evidence_integrity(
    *,
    workspace_id: str,
    candidate_index: int,
    evidence_ids: list[str],
    evidence_registry: dict[str, Any],
) -> dict[str, Any]:
    if (
        not isinstance(workspace_id, str)
        or not re.fullmatch(r"[A-Za-z0-9_-]+", workspace_id)
    ):
        raise ValueError("Invalid workspace identity")

    if type(candidate_index) is not int or candidate_index < 0:
        raise ValueError("Invalid candidate index")

    if not isinstance(evidence_ids, list):
        raise ValueError("Evidence references must be a list")

    if not isinstance(evidence_registry, dict):
        raise ValueError("Invalid evidence registry")

    failures = []
    checked = []
    seen = set()

    for evidence_id in evidence_ids:
        if not isinstance(evidence_id, str) or not evidence_id:
            failures.append({
                "evidence_id": None,
                "reason": "invalid_evidence_id",
            })
            continue

        if evidence_id in seen:
            failures.append({
                "evidence_id": evidence_id,
                "reason": "duplicate_evidence_reference",
            })
            continue

        seen.add(evidence_id)

        record = evidence_registry.get(evidence_id)

        if not isinstance(record, dict):
            failures.append({
                "evidence_id": evidence_id,
                "reason": "missing_or_invalid_evidence_record",
            })
            continue

        problems = []
        source = record.get("source")
        kind = record.get("evidence_type")

        if source not in ALLOWED_SOURCES:
            problems.append("unknown_source")
        elif source != "semantic_memory" and kind not in ALLOWED_TYPES[source]:
            problems.append("unrecognized_evidence_type")
        elif source == "semantic_memory" and kind not in (
            None, "historical_memory_match", "memory_recall_match"
        ):
            problems.append("unrecognized_memory_evidence_type")

        if record.get("workspace_id") != workspace_id:
            problems.append("workspace_identity_mismatch")

        if type(record.get("candidate_index")) is not int or (
            record["candidate_index"] != candidate_index
        ):
            problems.append("candidate_identity_mismatch")

        if record.get("certified") is not False:
            problems.append("unexpected_certification_claim")

        if record.get("approved_link_target", False) is not False:
            problems.append("premature_link_approval")

        if record.get("phrase_level_semantic_proof", False) is not False:
            problems.append("unsupported_semantic_proof")

        if record.get("semantic_equivalence_asserted", False) is not False:
            problems.append("unsupported_semantic_equivalence")

        if source == "workspace_concept_store":
            if (
                not isinstance(record.get("concept_key"), str)
                or not record["concept_key"].strip()
                or record.get("match_type") not in (
                    "exact_concept", "exact_alias"
                )
                or not isinstance(record.get("source_record"), dict)
            ):
                problems.append("invalid_concept_provenance")

        elif source == "uploaded_entity_graph":
            original = record.get("original_edge")
            if (
                not isinstance(original, dict)
                or not record.get("source_node_id")
                or not record.get("target_node_id")
                or not isinstance(record.get("source_node"), dict)
                or not isinstance(record.get("target_node"), dict)
                or original.get("src") is None
                or original.get("dst") is None
                or str(original["src"]) != str(
                    record["source_node_id"]
                )
                or str(original["dst"]) != str(
                    record["target_node_id"]
                )
                or original.get("type") != record.get(
                    "relationship_type"
                )
                or original.get("w") != record.get(
                    "relationship_weight"
                )
            ):
                problems.append("invalid_graph_provenance")

        elif source == "workspace_cross_document_reasoning":
            original = record.get("original_record")
            if not isinstance(original, dict):
                problems.append("invalid_reasoning_provenance")
            elif kind == "document_phrase_occurrence":
                if not original.get("document_id"):
                    problems.append("missing_document_identity")
            elif kind == "document_relationship_context":
                if not (
                    original.get("left_document_id")
                    and original.get("right_document_id")
                ):
                    problems.append("missing_relationship_identity")

        elif source == "semantic_memory":
            if (
                record.get("memory_id") is None
                or not str(record["memory_id"]).strip()
                or not isinstance(record.get("text"), str)
                or not record["text"].strip()
                or not isinstance(record.get("retrieval_method"), str)
                or not record["retrieval_method"].strip()
            ):
                problems.append("invalid_memory_provenance")
            if record.get("validity_status") == "certified":
                problems.append("unsupported_memory_certification")

        if problems:
            failures.append({
                "evidence_id": evidence_id,
                "reason": "record_integrity_failed",
                "details": problems,
            })
        else:
            checked.append({
                "evidence_id": evidence_id,
                "source": source,
                "evidence_type": kind,
                "integrity_valid": True,
                "semantically_certified": False,
            })

    if failures:
        status = "integrity_failed"
    elif not evidence_ids:
        status = "no_evidence"
    else:
        status = "integrity_passed"

    return {
        "status": status,
        "workspace_id": workspace_id,
        "candidate_index": candidate_index,
        "checked_count": len(checked),
        "failure_count": len(failures),
        "checked_evidence": checked,
        "failures": failures,
        "all_references_resolved": not failures,
        "evidence_integrity_valid": (
            status == "integrity_passed"
        ),
        "semantic_certification_status": "not_performed",
        "certified": False,
        "linking_decision_performed": False,
        "scorer_decision_performed": False,
    }


__all__ = ["validate_candidate_evidence_integrity"]
