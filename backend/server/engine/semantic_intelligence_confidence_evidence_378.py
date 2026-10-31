"""Phase 3.7.8 ? source-aware confidence evidence.

Preserves original confidence values without combining unrelated
measurements or authorizing linking decisions.
"""

from collections.abc import Mapping
from copy import deepcopy
import math


def preserve_confidence_evidence(signals):
    output = {
        "schema_version": "confidence_evidence_v1",
        "status": "no_evidence",
        "source_count": 0,
        "confidence_records": [],
        "overall_confidence": None,
        # confidence_aggregation_safeguard_v1
        "aggregation_authorized": False,
        "aggregation_performed": False,
        "aggregation_method": None,
        "aggregate_confidence_calibrated": False,
        "confidence_inventory": {
            "scope": "source_concept_relationship",
            "concept_confidence_count": 0,
            "evidence_confidence_count": 0,
            "distinct_evidence_count": 0,
            "metric_types": [
                "concept_confidence",
                "evidence_confidence",
            ],
            "cross_source_comparability": "not_established",
            "phrase_level_confidence": None,
        },
        "overall_confidence_status": "not_established",
        "semantic_proof_certified": False,
        "linking_decision_performed": False,
        "automatic_linking_authorized": False,
    }

    if not isinstance(signals, list):
        output["status"] = "invalid"
        return output

    records = []
    seen_ids = set()

    for position, signal in enumerate(signals):
        if not isinstance(signal, Mapping):
            output["status"] = "invalid"
            return output

        evidence_id = signal.get("evidence_id")

        if (
            not isinstance(evidence_id, str)
            or not evidence_id.strip()
            or evidence_id in seen_ids
        ):
            output["status"] = "invalid"
            return output

        seen_ids.add(evidence_id)

        if (
            signal.get("certified") is not False
            or signal.get("approved_link_target") is not False
            or signal.get("semantic_equivalence_asserted") is not False
        ):
            output["status"] = "invalid"
            return output

        # confidence_evidence_scope_guard_v1
        # The source and relationship identity must be identifiable
        # before its numeric confidence values can be preserved.
        required_context = (
            "source",
            "source_role",
            "signal_type",
            "recorded_relation_type",
            "canonical_phrase",
            "related_phrase",
        )

        for field in required_context:
            value = signal.get(field)
            if not isinstance(value, str) or not value.strip():
                output["status"] = "invalid"
                output["reason"] = (
                    "missing_or_invalid_confidence_context:" + field
                )
                return output

        # A score from this adapter is specifically scoped to
        # a source concept relationship, not the selected phrase
        # or a verified link target.
        if signal.get("signal_type") not in (
            "recorded_synonym_observation",
            "recorded_topical_association",
        ):
            output["status"] = "invalid"
            output["reason"] = "unsupported_confidence_signal_type"
            return output

        # confidence_evidence_state_guard_v1
        # Only source-declared state is used. An absent declaration
        # means unknown, never automatically current or certified.
        declared_state = signal.get("evidence_status", "unknown")

        if (
            not isinstance(declared_state, str)
            or declared_state not in (
                "available", "stale", "invalid", "unknown"
            )
        ):
            output["status"] = "invalid"
            output["reason"] = "invalid_evidence_status"
            return output

        if declared_state == "invalid":
            output["status"] = "invalid"
            output["reason"] = "source_declared_evidence_invalid"
            return output

        if declared_state == "stale":
            output["status"] = "stale_evidence"
            output["reason"] = "source_declared_evidence_stale"
            return output

        # "available" means the source reports availability.
        # It does not establish independent validity or freshness.

        preserved = {}

        for field in ("concept_confidence", "evidence_confidence"):
            value = signal.get(field)

            if (
                type(value) not in (int, float)
                or not math.isfinite(value)
                or not 0 <= value <= 1
            ):
                output["status"] = "invalid"
                return output

            preserved[field] = value

        records.append({
            "source_index": position,
            "evidence_id": evidence_id,
            "source": deepcopy(signal.get("source")),
            "source_role": deepcopy(signal.get("source_role")),
            "signal_type": deepcopy(signal.get("signal_type")),
            "recorded_relation_type": deepcopy(
                signal.get("recorded_relation_type")
            ),
            "canonical_phrase": deepcopy(
                signal.get("canonical_phrase")
            ),
            "related_phrase": deepcopy(
                signal.get("related_phrase")
            ),
            "confidence_scope": "source_concept_relationship",
            "evidence_validity": "structurally_valid_unverified",
            "source_declared_evidence_status": declared_state,
            "freshness_status": "not_independently_established",
            "source_availability_status": (
                "source_reported_available"
                if declared_state == "available"
                else "unknown"
            ),
            "confidence_applicability": "source_relationship_only",
            "selected_phrase_confidence_authorized": False,
            "concept_confidence": preserved["concept_confidence"],
            "evidence_confidence": preserved["evidence_confidence"],
            "phrase_level_semantic_confidence": None,
            "confidence_calibrated": False,
            "independently_verified": False,
            "certified": False,
        })

    output["status"] = (
        "source_confidence_preserved" if records else "no_evidence"
    )
    output["source_count"] = len(records)
    output["confidence_records"] = records
    output["confidence_inventory"] = {
        "scope": "source_concept_relationship",
        "concept_confidence_count": len(records),
        "evidence_confidence_count": len(records),
        "distinct_evidence_count": len(seen_ids),
        "metric_types": [
            "concept_confidence",
            "evidence_confidence",
        ],
        "cross_source_comparability": "not_established",
        "phrase_level_confidence": None,
    }
    return output
