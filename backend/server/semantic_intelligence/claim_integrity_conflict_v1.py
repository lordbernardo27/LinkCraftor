"""
LinkCraftor Semantic Intelligence
4.6.25 ? Claim Integrity & Conflict

Canonical responsibility:
Evaluate claim support, contradiction, consistency, integrity,
and conflict from certified upstream Authority output without
mutating Authority decisions or performing downstream linking work.
"""

from __future__ import annotations

import copy
from typing import Any


import json
import hashlib
CLAIM_INTEGRITY_CONFLICT_VERSION = (
    "claim_integrity_conflict_v1"
)

CLAIM_INTEGRITY_CONFLICT_PHASE = "4.6.25"


class ClaimIntegrityConflictError(ValueError):
    """Raised when Claim Integrity & Conflict contracts are violated."""


def inspect_certified_authority_input_v1(
    authority_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.25A ? Certified Authority Input Inspection.

    Accepts only the certified 4.6.24J Final Authority Result.

    This stage performs inspection only. It does not:
    - rescore Authority,
    - alter Authority classes,
    - adjudicate claims,
    - detect conflicts,
    - select external targets,
    - write Semantic Memory,
    - make linking decisions.
    """

    if not isinstance(authority_result, dict):
        raise ClaimIntegrityConflictError(
            "authority_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "final_authority_result_v1",

        "authority_intelligence_version":
            "authority_intelligence_v1",

        "phase":
            "4.6.24",

        "patch":
            "4.6.24J",

        "status":
            "FINAL_AUTHORITY_RESULT_BUILT",

        "policy":
            "CERTIFIED_FINAL_AUTHORITY_RESULT",

        "next":
            "full_authority_hard_certification",
    }

    for key, expected in expected_lifecycle.items():
        if authority_result.get(key) != expected:
            raise ClaimIntegrityConflictError(
                "Invalid certified Authority input "
                f"lifecycle field: {key}"
            )

    final_package = authority_result.get(
        "final_authority_package"
    )

    if not isinstance(final_package, dict):
        raise ClaimIntegrityConflictError(
            "final_authority_package must be a dictionary."
        )

    if (
        final_package.get("schema")
        != "final_authority_result_package_v1"
    ):
        raise ClaimIntegrityConflictError(
            "Invalid Final Authority package schema."
        )

    if (
        final_package.get("final_policy")
        !=
        "CERTIFIED_AUTHORITY_RESULT_FOR_DOWNSTREAM_CONSUMPTION"
    ):
        raise ClaimIntegrityConflictError(
            "Final Authority package is not certified "
            "for downstream consumption."
        )

    required_true = (
        "authority_result_built",
        "authority_scores_preserved",
        "authority_classes_preserved",
        "guard_outcomes_preserved",
        "authority_provenance_preserved",
        "active_target_set_ownership_preserved",
        "external_authority_partition_preserved",
        "external_route_eligibility_preserved",
        "external_resolver_ownership_preserved",
    )

    for flag in required_true:
        if final_package.get(flag) is not True:
            raise ClaimIntegrityConflictError(
                "Required Authority preservation flag "
                f"is not true: {flag}"
            )

    required_false = (
        "external_authority_lookup_performed",
        "external_target_selected",
        "truth_assessment_performed",
        "claim_integrity_decision_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
        "unsupported_authority_invention_performed",
    )

    for flag in required_false:
        if final_package.get(flag) is not False:
            raise ClaimIntegrityConflictError(
                "Forbidden upstream Authority operation "
                f"detected: {flag}"
            )

    records = final_package.get(
        "final_authority_records"
    )

    if not isinstance(records, list):
        raise ClaimIntegrityConflictError(
            "final_authority_records must be a list."
        )

    expected_count = final_package.get(
        "final_authority_record_count"
    )

    if expected_count != len(records):
        raise ClaimIntegrityConflictError(
            "Final Authority record count mismatch."
        )

    for record in records:

        if not isinstance(record, dict):
            raise ClaimIntegrityConflictError(
                "Each Final Authority record "
                "must be a dictionary."
            )

        if (
            record.get("schema")
            != "final_authority_record_v1"
        ):
            raise ClaimIntegrityConflictError(
                "Invalid Final Authority record schema."
            )

        required_record_fields = (
            "subject_id",
            "subject_type",
            "authority_score",
            "authority_class",
            "confidence",
            "guard_outcome",
            "final_authority_disposition",
            "final_authority_id",
            "final_authority_digest",
        )

        for field in required_record_fields:
            if field not in record:
                raise ClaimIntegrityConflictError(
                    "Missing Final Authority record field: "
                    f"{field}"
                )

    return {
        "schema":
            "claim_integrity_authority_input_inspection_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25A",

        "status":
            "CERTIFIED_AUTHORITY_INPUT_INSPECTED",

        "authority_input_schema":
            authority_result.get("schema"),

        "authority_input_patch":
            authority_result.get("patch"),

        "authority_record_count":
            len(records),

        "final_authority_package":
            copy.deepcopy(final_package),

        "authority_input":
            copy.deepcopy(authority_result),

        "preservation_contract": {
            "authority_scores_must_be_preserved":
                True,

            "authority_classes_must_be_preserved":
                True,

            "authority_guard_outcomes_must_be_preserved":
                True,

            "authority_provenance_must_be_preserved":
                True,

            "active_target_set_ownership_must_be_preserved":
                True,

            "external_authority_partition_must_be_preserved":
                True,

            "external_route_eligibility_must_be_preserved":
                True,

            "external_resolver_ownership_must_be_preserved":
                True,
        },

        "processing_boundaries": {
            "authority_input_inspection_performed":
                True,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "claim_integrity_decision_performed":
                False,

            "claim_conflict_detection_performed":
                False,

            "external_target_selected":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "policy":
            "CERTIFIED_FINAL_AUTHORITY_INPUT_ONLY",

        "next":
            "claim_integrity_conflict_architecture_definition",
    }

def define_claim_integrity_conflict_architecture_v1(
    inspection_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.25B ? Claim Integrity & Conflict Architecture Definition.

    Defines the canonical architecture for evaluating:
    - what a claim asserts,
    - what evidence supports or opposes it,
    - whether claims agree or conflict,
    - whether disagreement is material,
    - and what integrity state may later be assigned.

    Architecture definition only.
    No claim extraction, support scoring, conflict detection,
    or final claim-integrity decision occurs here.
    """

    if not isinstance(
        inspection_result,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "inspection_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "claim_integrity_authority_input_inspection_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25A",

        "status":
            "CERTIFIED_AUTHORITY_INPUT_INSPECTED",

        "policy":
            "CERTIFIED_FINAL_AUTHORITY_INPUT_ONLY",

        "next":
            "claim_integrity_conflict_architecture_definition",
    }

    for key, expected in expected_lifecycle.items():
        if inspection_result.get(key) != expected:
            raise ClaimIntegrityConflictError(
                "Invalid 4.6.25A inspection lifecycle "
                f"field: {key}"
            )

    final_authority_package = inspection_result.get(
        "final_authority_package"
    )

    preservation_contract = inspection_result.get(
        "preservation_contract"
    )

    if not isinstance(
        final_authority_package,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "final_authority_package must be a dictionary."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "preservation_contract must be a dictionary."
        )

    required_preservation = (
        "authority_scores_must_be_preserved",
        "authority_classes_must_be_preserved",
        "authority_guard_outcomes_must_be_preserved",
        "authority_provenance_must_be_preserved",
        "active_target_set_ownership_must_be_preserved",
        "external_authority_partition_must_be_preserved",
        "external_route_eligibility_must_be_preserved",
        "external_resolver_ownership_must_be_preserved",
    )

    for flag in required_preservation:
        if preservation_contract.get(flag) is not True:
            raise ClaimIntegrityConflictError(
                "Required upstream preservation contract "
                f"is not true: {flag}"
            )

    architecture = {
        "schema":
            "claim_integrity_conflict_architecture_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25B",

        "architecture_question":
            (
                "WHAT_DOES_EACH_CLAIM_ASSERT_AND_HOW_WELL_DOES_IT_"
                "AGREE_WITH_OR_CONFLICT_WITH_THE_AVAILABLE_EVIDENCE_"
                "AND_OTHER_CLAIMS"
            ),

        "architecture_policy":
            (
                "CONTEXTUAL_EVIDENCE_BOUND_CLAIM_INTEGRITY_"
                "AND_CONFLICT_EVALUATION_ONLY"
            ),

        "canonical_objects": (
            "CLAIM",
            "EVIDENCE_ITEM",
            "CLAIM_EVIDENCE_RELATION",
            "CLAIM_CLAIM_RELATION",
            "CONFLICT_SET",
        ),

        "claim_scope_types": (
            "FACTUAL_CLAIM",
            "CAUSAL_CLAIM",
            "QUANTITATIVE_CLAIM",
            "COMPARATIVE_CLAIM",
            "TEMPORAL_CLAIM",
            "DEFINITIONAL_CLAIM",
            "ATTRIBUTION_CLAIM",
            "CONDITIONAL_CLAIM",
        ),

        "evidence_relationships": (
            "SUPPORTS",
            "PARTIALLY_SUPPORTS",
            "NEUTRAL",
            "CHALLENGES",
            "CONTRADICTS",
            "INSUFFICIENT",
            "UNRESOLVED",
        ),

        "claim_relationships": (
            "AGREES",
            "COMPATIBLE",
            "PARTIALLY_OVERLAPS",
            "QUALIFIES",
            "DISAGREES",
            "CONTRADICTS",
            "UNRELATED",
            "UNRESOLVED",
        ),

        "conflict_classes": (
            "NO_CONFLICT",
            "MINOR_CONFLICT",
            "MATERIAL_CONFLICT",
            "DIRECT_CONTRADICTION",
            "CONTEXT_DEPENDENT_CONFLICT",
            "TEMPORAL_CONFLICT",
            "SCOPE_CONFLICT",
            "QUANTITATIVE_CONFLICT",
            "ATTRIBUTION_CONFLICT",
            "UNRESOLVED_CONFLICT",
        ),

        "claim_integrity_states": (
            "WELL_SUPPORTED",
            "SUPPORTED",
            "PARTIALLY_SUPPORTED",
            "DISPUTED",
            "CONTRADICTED",
            "INSUFFICIENT_EVIDENCE",
            "UNRESOLVED",
            "BLOCKED",
        ),

        "evaluation_dimensions": (
            "CLAIM_CLARITY",
            "CLAIM_SPECIFICITY",
            "EVIDENCE_SUPPORT",
            "EVIDENCE_CONSISTENCY",
            "SOURCE_AUTHORITY_ALIGNMENT",
            "PROVENANCE_CONTINUITY",
            "CONTEXT_ALIGNMENT",
            "SCOPE_ALIGNMENT",
            "TEMPORAL_ALIGNMENT",
            "QUANTITATIVE_ALIGNMENT",
            "CROSS_CLAIM_CONSISTENCY",
            "CONFLICT_MATERIALITY",
        ),

        "authority_relationship": {
            "authority_is_upstream":
                True,

            "authority_score_is_input":
                True,

            "authority_class_is_input":
                True,

            "authority_confidence_is_input":
                True,

            "authority_guard_outcome_is_input":
                True,

            "authority_provenance_is_input":
                True,

            "authority_may_be_rescored":
                False,

            "authority_may_be_reclassified":
                False,

            "high_authority_does_not_equal_claim_truth":
                True,

            "low_authority_does_not_automatically_equal_false_claim":
                True,
        },

        "target_ownership_relationship": {
            "canonical_target_owner":
                "ACTIVE_TARGET_SET",

            "external_target_partition":
                "EXTERNAL_AUTHORITY",

            "external_route_eligibility":
                "EXTERNAL",

            "final_external_target_selection_owner":
                "EXTERNAL_TARGET_RESOLVER",

            "claim_integrity_may_create_target":
                False,

            "claim_integrity_may_select_final_target":
                False,

            "active_target_set_ownership_preserved":
                True,

            "external_authority_partition_preserved":
                True,

            "external_route_eligibility_preserved":
                True,

            "external_resolver_ownership_preserved":
                True,
        },

        "processing_boundaries": {
            "architecture_definition_performed":
                True,

            "claim_extraction_performed":
                False,

            "claim_support_assessment_performed":
                False,

            "claim_conflict_detection_performed":
                False,

            "claim_integrity_decision_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "unsupported_claim_invention_performed":
                False,
        },

        "invariants": (
            "CLAIMS_MUST_BE_EVIDENCE_BOUND",
            "CONFLICT_MUST_BE_CONTEXT_SPECIFIC",
            "CONFLICT_MUST_IDENTIFY_THE_DISAGREEING_PROPOSITIONS",
            "SOURCE_AUTHORITY_AND_CLAIM_INTEGRITY_MUST_REMAIN_DISTINCT",
            "AUTHORITY_OUTPUT_MUST_REMAIN_IMMUTABLE",
            "NO_UNSUPPORTED_CLAIM_INVENTION",
            "NO_EXTERNAL_TARGET_CREATION",
            "NO_FINAL_TARGET_SELECTION",
            "NO_SEMANTIC_MEMORY_WRITE",
            "NO_LINKING_DECISION",
        ),
    }

    return {
        "schema":
            "claim_integrity_conflict_architecture_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25B",

        "status":
            "CLAIM_INTEGRITY_CONFLICT_ARCHITECTURE_DEFINED",

        "architecture":
            architecture,

        "final_authority_package":
            copy.deepcopy(final_authority_package),

        "authority_input":
            copy.deepcopy(
                inspection_result.get(
                    "authority_input"
                )
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries":
            copy.deepcopy(
                architecture[
                    "processing_boundaries"
                ]
            ),

        "policy":
            "CERTIFIED_CLAIM_INTEGRITY_CONFLICT_ARCHITECTURE",

        "next":
            "claim_intake_validation",
    }

def validate_claim_intake_v1(
    architecture_result: dict[str, Any],
    claim_items: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    4.6.25C ? Claim Intake Validation.

    Validates explicitly supplied claim candidates against the
    certified Claim Integrity & Conflict architecture and certified
    upstream Authority records.

    This stage does not:
    - extract claims from documents,
    - invent claims,
    - create evidence,
    - assess claim support,
    - detect conflicts,
    - decide claim integrity,
    - rescore/reclassify Authority,
    - create/select external targets,
    - write Semantic Memory,
    - make linking decisions.
    """

    if not isinstance(
        architecture_result,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "architecture_result must be a dictionary."
        )

    if not isinstance(
        claim_items,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "claim_items must be a list."
        )

    expected_lifecycle = {
        "schema":
            "claim_integrity_conflict_architecture_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25B",

        "status":
            "CLAIM_INTEGRITY_CONFLICT_ARCHITECTURE_DEFINED",

        "policy":
            "CERTIFIED_CLAIM_INTEGRITY_CONFLICT_ARCHITECTURE",

        "next":
            "claim_intake_validation",
    }

    for key, expected in expected_lifecycle.items():
        if architecture_result.get(key) != expected:
            raise ClaimIntegrityConflictError(
                "Invalid 4.6.25B architecture lifecycle "
                f"field: {key}"
            )

    architecture = architecture_result.get(
        "architecture"
    )

    final_authority_package = architecture_result.get(
        "final_authority_package"
    )

    preservation_contract = architecture_result.get(
        "preservation_contract"
    )

    if not isinstance(
        architecture,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "architecture must be a dictionary."
        )

    if (
        architecture.get("schema")
        != "claim_integrity_conflict_architecture_v1"
    ):
        raise ClaimIntegrityConflictError(
            "Invalid Claim Integrity architecture schema."
        )

    if not isinstance(
        final_authority_package,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "final_authority_package must be a dictionary."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "preservation_contract must be a dictionary."
        )

    allowed_claim_types = set(
        architecture.get(
            "claim_scope_types",
            (),
        )
    )

    expected_claim_types = {
        "FACTUAL_CLAIM",
        "CAUSAL_CLAIM",
        "QUANTITATIVE_CLAIM",
        "COMPARATIVE_CLAIM",
        "TEMPORAL_CLAIM",
        "DEFINITIONAL_CLAIM",
        "ATTRIBUTION_CLAIM",
        "CONDITIONAL_CLAIM",
    }

    if allowed_claim_types != expected_claim_types:
        raise ClaimIntegrityConflictError(
            "Claim type architecture drift detected."
        )

    authority_records = final_authority_package.get(
        "final_authority_records"
    )

    if not isinstance(
        authority_records,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "final_authority_records must be a list."
        )

    authority_by_subject = {}

    for record in authority_records:

        if not isinstance(
            record,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Authority record must be a dictionary."
            )

        subject_id = record.get(
            "subject_id"
        )

        if (
            not isinstance(subject_id, str)
            or not subject_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "Authority record requires subject_id."
            )

        if subject_id in authority_by_subject:
            raise ClaimIntegrityConflictError(
                "Duplicate Authority subject_id detected."
            )

        authority_by_subject[
            subject_id
        ] = record

    validated_claims = []

    seen_claim_ids = set()

    required_claim_fields = (
        "claim_id",
        "claim_type",
        "claim_text",
        "source_subject_id",
        "context",
    )

    for item in claim_items:

        if not isinstance(
            item,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Each claim item must be a dictionary."
            )

        for field in required_claim_fields:
            if field not in item:
                raise ClaimIntegrityConflictError(
                    "Missing claim intake field: "
                    f"{field}"
                )

        claim_id = item.get(
            "claim_id"
        )

        claim_type = item.get(
            "claim_type"
        )

        claim_text = item.get(
            "claim_text"
        )

        source_subject_id = item.get(
            "source_subject_id"
        )

        context = item.get(
            "context"
        )

        if (
            not isinstance(claim_id, str)
            or not claim_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "claim_id must be a non-empty string."
            )

        if claim_id in seen_claim_ids:
            raise ClaimIntegrityConflictError(
                "Duplicate claim_id detected."
            )

        seen_claim_ids.add(
            claim_id
        )

        if claim_type not in allowed_claim_types:
            raise ClaimIntegrityConflictError(
                "Unsupported claim_type."
            )

        if (
            not isinstance(claim_text, str)
            or not claim_text.strip()
        ):
            raise ClaimIntegrityConflictError(
                "claim_text must be a non-empty string."
            )

        if (
            not isinstance(source_subject_id, str)
            or not source_subject_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "source_subject_id must be a non-empty string."
            )

        if source_subject_id not in authority_by_subject:
            raise ClaimIntegrityConflictError(
                "Claim source_subject_id has no certified "
                "Authority record."
            )

        if not isinstance(
            context,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "context must be a dictionary."
            )

        authority_record = authority_by_subject[
            source_subject_id
        ]

        validated_claims.append(
            {
                "schema":
                    "validated_claim_intake_record_v1",

                "claim_id":
                    claim_id,

                "claim_type":
                    claim_type,

                "claim_text":
                    claim_text,

                "source_subject_id":
                    source_subject_id,

                "context":
                    copy.deepcopy(context),

                "supplied_evidence_ids":
                    copy.deepcopy(
                        item.get(
                            "evidence_ids",
                            [],
                        )
                    ),

                "authority_reference": {
                    "final_authority_id":
                        authority_record.get(
                            "final_authority_id"
                        ),

                    "final_authority_digest":
                        authority_record.get(
                            "final_authority_digest"
                        ),

                    "authority_score":
                        authority_record.get(
                            "authority_score"
                        ),

                    "authority_class":
                        authority_record.get(
                            "authority_class"
                        ),

                    "confidence":
                        authority_record.get(
                            "confidence"
                        ),

                    "guard_outcome":
                        authority_record.get(
                            "guard_outcome"
                        ),

                    "final_authority_disposition":
                        authority_record.get(
                            "final_authority_disposition"
                        ),
                },

                "claim_supplied_by_upstream_or_runtime":
                    True,

                "claim_invented_by_claim_integrity":
                    False,
            }
        )

    return {
        "schema":
            "claim_intake_validation_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25C",

        "status":
            "CLAIM_INTAKE_VALIDATED",

        "validated_claim_count":
            len(validated_claims),

        "validated_claims":
            validated_claims,

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "final_authority_package":
            copy.deepcopy(
                final_authority_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "claim_intake_validation_performed":
                True,

            "claim_extraction_performed":
                False,

            "unsupported_claim_invention_performed":
                False,

            "claim_support_assessment_performed":
                False,

            "claim_conflict_detection_performed":
                False,

            "claim_integrity_decision_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "policy":
            "CERTIFIED_CLAIM_INTAKE_VALIDATION",

        "next":
            "claim_scope_and_evaluation_contract",
    }

def define_claim_scope_and_evaluation_contract_v1(
    validation_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.25D ? Claim Scope & Evaluation Contract.

    Defines the immutable evaluation scope for each validated claim.

    This stage determines what may later be evaluated, but performs
    no evidence extraction, support assessment, conflict detection,
    or final integrity decision.
    """

    if not isinstance(
        validation_result,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "validation_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "claim_intake_validation_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25C",

        "status":
            "CLAIM_INTAKE_VALIDATED",

        "policy":
            "CERTIFIED_CLAIM_INTAKE_VALIDATION",

        "next":
            "claim_scope_and_evaluation_contract",
    }

    for key, expected in expected_lifecycle.items():
        if validation_result.get(key) != expected:
            raise ClaimIntegrityConflictError(
                "Invalid 4.6.25C validation lifecycle "
                f"field: {key}"
            )

    validated_claims = validation_result.get(
        "validated_claims"
    )

    architecture = validation_result.get(
        "architecture"
    )

    final_authority_package = validation_result.get(
        "final_authority_package"
    )

    preservation_contract = validation_result.get(
        "preservation_contract"
    )

    if not isinstance(
        validated_claims,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "validated_claims must be a list."
        )

    if (
        validation_result.get(
            "validated_claim_count"
        )
        != len(validated_claims)
    ):
        raise ClaimIntegrityConflictError(
            "Validated claim count mismatch."
        )

    if not isinstance(
        architecture,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "architecture must be a dictionary."
        )

    if not isinstance(
        final_authority_package,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "final_authority_package must be a dictionary."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "preservation_contract must be a dictionary."
        )

    evaluation_dimensions = architecture.get(
        "evaluation_dimensions"
    )

    if not isinstance(
        evaluation_dimensions,
        (list, tuple),
    ):
        raise ClaimIntegrityConflictError(
            "evaluation_dimensions are required."
        )

    required_dimensions = {
        "CLAIM_CLARITY",
        "CLAIM_SPECIFICITY",
        "EVIDENCE_SUPPORT",
        "EVIDENCE_CONSISTENCY",
        "SOURCE_AUTHORITY_ALIGNMENT",
        "PROVENANCE_CONTINUITY",
        "CONTEXT_ALIGNMENT",
        "SCOPE_ALIGNMENT",
        "TEMPORAL_ALIGNMENT",
        "QUANTITATIVE_ALIGNMENT",
        "CROSS_CLAIM_CONSISTENCY",
        "CONFLICT_MATERIALITY",
    }

    if set(evaluation_dimensions) != required_dimensions:
        raise ClaimIntegrityConflictError(
            "Claim evaluation dimension drift detected."
        )

    scope_records = []

    seen_scope_claim_ids = set()

    for claim in validated_claims:

        if not isinstance(
            claim,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Validated claim must be a dictionary."
            )

        if (
            claim.get("schema")
            != "validated_claim_intake_record_v1"
        ):
            raise ClaimIntegrityConflictError(
                "Invalid validated claim schema."
            )

        claim_id = claim.get(
            "claim_id"
        )

        if claim_id in seen_scope_claim_ids:
            raise ClaimIntegrityConflictError(
                "Duplicate claim_id in scope definition."
            )

        seen_scope_claim_ids.add(
            claim_id
        )

        authority_reference = claim.get(
            "authority_reference"
        )

        if not isinstance(
            authority_reference,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "authority_reference must be a dictionary."
            )

        required_authority_fields = (
            "final_authority_id",
            "final_authority_digest",
            "authority_score",
            "authority_class",
            "confidence",
            "guard_outcome",
            "final_authority_disposition",
        )

        for field in required_authority_fields:
            if field not in authority_reference:
                raise ClaimIntegrityConflictError(
                    "Missing Authority reference field: "
                    f"{field}"
                )

        scope_core = {
            "schema":
                "claim_scope_evaluation_contract_record_v1",

            "claim_id":
                claim_id,

            "claim_type":
                claim.get("claim_type"),

            "claim_text":
                claim.get("claim_text"),

            "source_subject_id":
                claim.get("source_subject_id"),

            "context":
                copy.deepcopy(
                    claim.get("context")
                ),

            "supplied_evidence_ids":
                copy.deepcopy(
                    claim.get(
                        "supplied_evidence_ids",
                        [],
                    )
                ),

            "authority_reference":
                copy.deepcopy(
                    authority_reference
                ),

            "evaluation_dimensions":
                tuple(
                    evaluation_dimensions
                ),

            "evaluation_scope": {
                "claim_text_may_be_evaluated":
                    True,

                "claim_context_may_be_evaluated":
                    True,

                "supplied_evidence_may_be_evaluated":
                    True,

                "cross_claim_comparison_may_be_evaluated":
                    True,

                "source_authority_may_inform_evaluation":
                    True,

                "claim_scope_may_be_normalized":
                    True,

                "temporal_scope_may_be_compared":
                    True,

                "quantitative_scope_may_be_compared":
                    True,

                "attribution_scope_may_be_compared":
                    True,
            },

            "forbidden_operations": {
                "unsupported_claim_invention_allowed":
                    False,

                "unsupported_evidence_invention_allowed":
                    False,

                "authority_rescoring_allowed":
                    False,

                "authority_reclassification_allowed":
                    False,

                "authority_guard_override_allowed":
                    False,

                "external_target_creation_allowed":
                    False,

                "final_external_target_selection_allowed":
                    False,

                "semantic_memory_write_allowed":
                    False,

                "linking_decision_allowed":
                    False,
            },

            "claim_truth_not_presumed_from_authority":
                True,

            "claim_falsehood_not_presumed_from_low_authority":
                True,

            "claim_must_remain_evidence_bound":
                True,

            "conflict_must_remain_context_specific":
                True,

            "active_target_set_ownership_preserved":
                True,

            "external_authority_partition_preserved":
                True,

            "external_route_eligibility_preserved":
                True,

            "external_resolver_ownership_preserved":
                True,
        }

        canonical = json.dumps(
            scope_core,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        digest = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

        scope_record = {
            **scope_core,

            "claim_scope_contract_id":
                f"claimscope:v1:{digest}",

            "claim_scope_contract_digest":
                digest,
        }

        scope_records.append(
            scope_record
        )

    return {
        "schema":
            "claim_scope_evaluation_contract_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25D",

        "status":
            "CLAIM_SCOPE_AND_EVALUATION_CONTRACT_DEFINED",

        "scope_record_count":
            len(scope_records),

        "claim_scope_contracts":
            scope_records,

        "validated_claims":
            copy.deepcopy(
                validated_claims
            ),

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "final_authority_package":
            copy.deepcopy(
                final_authority_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "claim_scope_definition_performed":
                True,

            "claim_extraction_performed":
                False,

            "evidence_extraction_performed":
                False,

            "claim_support_assessment_performed":
                False,

            "claim_conflict_detection_performed":
                False,

            "claim_integrity_decision_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "authority_guard_override_performed":
                False,

            "unsupported_claim_invention_performed":
                False,

            "unsupported_evidence_invention_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "policy":
            "CERTIFIED_CLAIM_SCOPE_AND_EVALUATION_CONTRACT",

        "next":
            "claim_and_evidence_extraction",
    }

def extract_claim_and_evidence_v1(
    scope_result: dict[str, Any],
    evidence_items: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    4.6.25E ? Claim & Evidence Extraction.

    Binds explicitly supplied evidence records to certified claim
    scope contracts.

    This stage does not:
    - fetch external evidence,
    - invent evidence,
    - infer missing evidence,
    - assess support,
    - detect claim conflicts,
    - make claim-integrity decisions,
    - rescore Authority,
    - create/select external targets,
    - write Semantic Memory,
    - make linking decisions.
    """

    if not isinstance(
        scope_result,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "scope_result must be a dictionary."
        )

    if not isinstance(
        evidence_items,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "evidence_items must be a list."
        )

    expected_lifecycle = {
        "schema":
            "claim_scope_evaluation_contract_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25D",

        "status":
            "CLAIM_SCOPE_AND_EVALUATION_CONTRACT_DEFINED",

        "policy":
            "CERTIFIED_CLAIM_SCOPE_AND_EVALUATION_CONTRACT",

        "next":
            "claim_and_evidence_extraction",
    }

    for key, expected in expected_lifecycle.items():
        if scope_result.get(key) != expected:
            raise ClaimIntegrityConflictError(
                "Invalid 4.6.25D scope lifecycle field: "
                f"{key}"
            )

    contracts = scope_result.get(
        "claim_scope_contracts"
    )

    architecture = scope_result.get(
        "architecture"
    )

    final_authority_package = scope_result.get(
        "final_authority_package"
    )

    preservation_contract = scope_result.get(
        "preservation_contract"
    )

    if not isinstance(
        contracts,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "claim_scope_contracts must be a list."
        )

    if (
        scope_result.get("scope_record_count")
        != len(contracts)
    ):
        raise ClaimIntegrityConflictError(
            "Claim scope record count mismatch."
        )

    if not isinstance(
        architecture,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "architecture must be a dictionary."
        )

    if not isinstance(
        final_authority_package,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "final_authority_package must be a dictionary."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "preservation_contract must be a dictionary."
        )

    contract_by_claim_id = {}

    expected_evidence_ids_by_claim = {}

    for contract in contracts:

        if not isinstance(
            contract,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Claim scope contract must be a dictionary."
            )

        if (
            contract.get("schema")
            != "claim_scope_evaluation_contract_record_v1"
        ):
            raise ClaimIntegrityConflictError(
                "Invalid claim scope contract schema."
            )

        claim_id = contract.get(
            "claim_id"
        )

        if (
            not isinstance(claim_id, str)
            or not claim_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "Claim scope contract requires claim_id."
            )

        if claim_id in contract_by_claim_id:
            raise ClaimIntegrityConflictError(
                "Duplicate claim_id in scope contracts."
            )

        forbidden = contract.get(
            "forbidden_operations"
        )

        if not isinstance(
            forbidden,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "forbidden_operations must be a dictionary."
            )

        required_false = (
            "unsupported_claim_invention_allowed",
            "unsupported_evidence_invention_allowed",
            "authority_rescoring_allowed",
            "authority_reclassification_allowed",
            "authority_guard_override_allowed",
            "external_target_creation_allowed",
            "final_external_target_selection_allowed",
            "semantic_memory_write_allowed",
            "linking_decision_allowed",
        )

        for flag in required_false:
            if forbidden.get(flag) is not False:
                raise ClaimIntegrityConflictError(
                    "Scope forbidden-operation drift detected: "
                    f"{flag}"
                )

        supplied_ids = contract.get(
            "supplied_evidence_ids",
            [],
        )

        if not isinstance(
            supplied_ids,
            list,
        ):
            raise ClaimIntegrityConflictError(
                "supplied_evidence_ids must be a list."
            )

        if len(supplied_ids) != len(set(supplied_ids)):
            raise ClaimIntegrityConflictError(
                "Duplicate supplied evidence ID detected."
            )

        for evidence_id in supplied_ids:
            if (
                not isinstance(evidence_id, str)
                or not evidence_id.strip()
            ):
                raise ClaimIntegrityConflictError(
                    "Evidence IDs must be non-empty strings."
                )

        contract_by_claim_id[
            claim_id
        ] = contract

        expected_evidence_ids_by_claim[
            claim_id
        ] = tuple(supplied_ids)

    evidence_by_id = {}

    required_evidence_fields = (
        "evidence_id",
        "claim_id",
        "evidence_text",
        "source_subject_id",
        "evidence_type",
        "context",
        "provenance",
    )

    for item in evidence_items:

        if not isinstance(
            item,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Each evidence item must be a dictionary."
            )

        for field in required_evidence_fields:
            if field not in item:
                raise ClaimIntegrityConflictError(
                    "Missing evidence field: "
                    f"{field}"
                )

        evidence_id = item.get(
            "evidence_id"
        )

        claim_id = item.get(
            "claim_id"
        )

        evidence_text = item.get(
            "evidence_text"
        )

        source_subject_id = item.get(
            "source_subject_id"
        )

        evidence_type = item.get(
            "evidence_type"
        )

        context = item.get(
            "context"
        )

        provenance = item.get(
            "provenance"
        )

        if (
            not isinstance(evidence_id, str)
            or not evidence_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "evidence_id must be a non-empty string."
            )

        if evidence_id in evidence_by_id:
            raise ClaimIntegrityConflictError(
                "Duplicate evidence_id detected."
            )

        if claim_id not in contract_by_claim_id:
            raise ClaimIntegrityConflictError(
                "Evidence references unknown claim_id."
            )

        if evidence_id not in (
            expected_evidence_ids_by_claim[
                claim_id
            ]
        ):
            raise ClaimIntegrityConflictError(
                "Evidence was not declared in the certified "
                "claim scope contract."
            )

        if (
            not isinstance(evidence_text, str)
            or not evidence_text.strip()
        ):
            raise ClaimIntegrityConflictError(
                "evidence_text must be a non-empty string."
            )

        if (
            not isinstance(source_subject_id, str)
            or not source_subject_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "source_subject_id must be a non-empty string."
            )

        if (
            not isinstance(evidence_type, str)
            or not evidence_type.strip()
        ):
            raise ClaimIntegrityConflictError(
                "evidence_type must be a non-empty string."
            )

        if not isinstance(
            context,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "evidence context must be a dictionary."
            )

        if not isinstance(
            provenance,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "evidence provenance must be a dictionary."
            )

        evidence_by_id[
            evidence_id
        ] = copy.deepcopy(item)

    extraction_records = []

    all_expected_ids = set()

    for claim_id, expected_ids in (
        expected_evidence_ids_by_claim.items()
    ):

        all_expected_ids.update(
            expected_ids
        )

        missing = [
            evidence_id
            for evidence_id in expected_ids
            if evidence_id not in evidence_by_id
        ]

        if missing:
            raise ClaimIntegrityConflictError(
                "Certified claim scope references evidence "
                "that was not supplied."
            )

        contract = contract_by_claim_id[
            claim_id
        ]

        extracted_evidence = []

        for evidence_id in expected_ids:

            item = evidence_by_id[
                evidence_id
            ]

            if (
                item.get("source_subject_id")
                != contract.get("source_subject_id")
            ):
                raise ClaimIntegrityConflictError(
                    "Evidence source_subject_id does not match "
                    "the certified claim source_subject_id."
                )

            extracted_evidence.append(
                {
                    "schema":
                        "claim_evidence_extraction_record_v1",

                    "evidence_id":
                        item.get("evidence_id"),

                    "claim_id":
                        claim_id,

                    "evidence_text":
                        item.get("evidence_text"),

                    "evidence_type":
                        item.get("evidence_type"),

                    "source_subject_id":
                        item.get("source_subject_id"),

                    "context":
                        copy.deepcopy(
                            item.get("context")
                        ),

                    "provenance":
                        copy.deepcopy(
                            item.get("provenance")
                        ),

                    "evidence_supplied_explicitly":
                        True,

                    "evidence_invented_by_claim_integrity":
                        False,

                    "evidence_fetched_externally":
                        False,
                }
            )

        extraction_records.append(
            {
                "schema":
                    "claim_and_evidence_extraction_bundle_v1",

                "claim_id":
                    claim_id,

                "claim_type":
                    contract.get("claim_type"),

                "claim_text":
                    contract.get("claim_text"),

                "source_subject_id":
                    contract.get("source_subject_id"),

                "claim_context":
                    copy.deepcopy(
                        contract.get("context")
                    ),

                "claim_scope_contract_id":
                    contract.get(
                        "claim_scope_contract_id"
                    ),

                "claim_scope_contract_digest":
                    contract.get(
                        "claim_scope_contract_digest"
                    ),

                "authority_reference":
                    copy.deepcopy(
                        contract.get(
                            "authority_reference"
                        )
                    ),

                "evaluation_dimensions":
                    copy.deepcopy(
                        contract.get(
                            "evaluation_dimensions"
                        )
                    ),

                "evidence_count":
                    len(extracted_evidence),

                "evidence_records":
                    extracted_evidence,

                "claim_extracted_from_certified_scope":
                    True,

                "claim_invented":
                    False,

                "unsupported_evidence_invented":
                    False,

                "authority_preserved":
                    True,

                "active_target_set_ownership_preserved":
                    True,

                "external_authority_partition_preserved":
                    True,

                "external_route_eligibility_preserved":
                    True,

                "external_resolver_ownership_preserved":
                    True,
            }
        )

    supplied_ids = set(
        evidence_by_id.keys()
    )

    if supplied_ids != all_expected_ids:
        raise ClaimIntegrityConflictError(
            "Evidence intake contains undeclared or unbound "
            "evidence records."
        )

    return {
        "schema":
            "claim_and_evidence_extraction_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25E",

        "status":
            "CLAIM_AND_EVIDENCE_EXTRACTED",

        "extraction_bundle_count":
            len(extraction_records),

        "claim_evidence_bundles":
            extraction_records,

        "claim_scope_contracts":
            copy.deepcopy(
                contracts
            ),

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "final_authority_package":
            copy.deepcopy(
                final_authority_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "claim_extraction_performed":
                True,

            "evidence_extraction_performed":
                True,

            "external_evidence_fetch_performed":
                False,

            "unsupported_claim_invention_performed":
                False,

            "unsupported_evidence_invention_performed":
                False,

            "claim_support_assessment_performed":
                False,

            "claim_conflict_detection_performed":
                False,

            "claim_integrity_decision_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "authority_guard_override_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "policy":
            "CERTIFIED_EVIDENCE_BOUND_CLAIM_EXTRACTION",

        "next":
            "claim_support_assessment",
    }

def assess_claim_support_v1(
    extraction_result: dict[str, Any],
    support_observations: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    4.6.25F ? Claim Support Assessment.

    Determines how certified, explicitly supplied evidence relates
    to each claim.

    This stage assesses claim-to-evidence support only.

    It does not:
    - compare claims against other claims,
    - classify claim conflicts,
    - make a final claim-integrity decision,
    - alter Authority,
    - fetch or invent evidence,
    - create/select external targets,
    - write Semantic Memory,
    - make linking decisions.
    """

    if not isinstance(
        extraction_result,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "extraction_result must be a dictionary."
        )

    if not isinstance(
        support_observations,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "support_observations must be a list."
        )

    expected_lifecycle = {
        "schema":
            "claim_and_evidence_extraction_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25E",

        "status":
            "CLAIM_AND_EVIDENCE_EXTRACTED",

        "policy":
            "CERTIFIED_EVIDENCE_BOUND_CLAIM_EXTRACTION",

        "next":
            "claim_support_assessment",
    }

    for key, expected in expected_lifecycle.items():
        if extraction_result.get(key) != expected:
            raise ClaimIntegrityConflictError(
                "Invalid 4.6.25E extraction lifecycle field: "
                f"{key}"
            )

    bundles = extraction_result.get(
        "claim_evidence_bundles"
    )

    if not isinstance(
        bundles,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "claim_evidence_bundles must be a list."
        )

    if (
        extraction_result.get(
            "extraction_bundle_count"
        )
        != len(bundles)
    ):
        raise ClaimIntegrityConflictError(
            "Extraction bundle count mismatch."
        )

    allowed_relationships = {
        "SUPPORTS",
        "PARTIALLY_SUPPORTS",
        "NEUTRAL",
        "CHALLENGES",
        "CONTRADICTS",
        "INSUFFICIENT",
        "UNRESOLVED",
    }

    claim_bundle_by_id = {}
    evidence_owner = {}

    for bundle in bundles:

        if not isinstance(
            bundle,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Claim evidence bundle must be a dictionary."
            )

        if (
            bundle.get("schema")
            != "claim_and_evidence_extraction_bundle_v1"
        ):
            raise ClaimIntegrityConflictError(
                "Invalid claim evidence bundle schema."
            )

        claim_id = bundle.get(
            "claim_id"
        )

        if (
            not isinstance(claim_id, str)
            or not claim_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "Bundle requires claim_id."
            )

        if claim_id in claim_bundle_by_id:
            raise ClaimIntegrityConflictError(
                "Duplicate claim_id in extraction bundles."
            )

        evidence_records = bundle.get(
            "evidence_records"
        )

        if not isinstance(
            evidence_records,
            list,
        ):
            raise ClaimIntegrityConflictError(
                "evidence_records must be a list."
            )

        if (
            bundle.get("evidence_count")
            != len(evidence_records)
        ):
            raise ClaimIntegrityConflictError(
                "Evidence count mismatch."
            )

        claim_bundle_by_id[
            claim_id
        ] = bundle

        for evidence in evidence_records:

            if not isinstance(
                evidence,
                dict,
            ):
                raise ClaimIntegrityConflictError(
                    "Evidence record must be a dictionary."
                )

            if (
                evidence.get("schema")
                != "claim_evidence_extraction_record_v1"
            ):
                raise ClaimIntegrityConflictError(
                    "Invalid evidence extraction schema."
                )

            evidence_id = evidence.get(
                "evidence_id"
            )

            if evidence_id in evidence_owner:
                raise ClaimIntegrityConflictError(
                    "Duplicate evidence_id across bundles."
                )

            evidence_owner[
                evidence_id
            ] = claim_id

    observations_by_evidence = {}

    required_observation_fields = (
        "observation_id",
        "claim_id",
        "evidence_id",
        "relationship",
        "basis",
    )

    for observation in support_observations:

        if not isinstance(
            observation,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Each support observation must be a dictionary."
            )

        for field in required_observation_fields:
            if field not in observation:
                raise ClaimIntegrityConflictError(
                    "Missing support observation field: "
                    f"{field}"
                )

        observation_id = observation.get(
            "observation_id"
        )

        claim_id = observation.get(
            "claim_id"
        )

        evidence_id = observation.get(
            "evidence_id"
        )

        relationship = observation.get(
            "relationship"
        )

        basis = observation.get(
            "basis"
        )

        if (
            not isinstance(observation_id, str)
            or not observation_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "observation_id must be a non-empty string."
            )

        if claim_id not in claim_bundle_by_id:
            raise ClaimIntegrityConflictError(
                "Support observation references unknown claim_id."
            )

        if evidence_id not in evidence_owner:
            raise ClaimIntegrityConflictError(
                "Support observation references unknown evidence_id."
            )

        if evidence_owner[
            evidence_id
        ] != claim_id:
            raise ClaimIntegrityConflictError(
                "Support observation claim/evidence ownership mismatch."
            )

        if relationship not in allowed_relationships:
            raise ClaimIntegrityConflictError(
                "Unsupported evidence relationship."
            )

        if (
            not isinstance(basis, dict)
            or not basis
        ):
            raise ClaimIntegrityConflictError(
                "Support observation basis must be a non-empty dictionary."
            )

        if evidence_id in observations_by_evidence:
            raise ClaimIntegrityConflictError(
                "Each evidence item may have only one certified "
                "support relationship observation."
            )

        observations_by_evidence[
            evidence_id
        ] = copy.deepcopy(
            observation
        )

    expected_evidence_ids = set(
        evidence_owner.keys()
    )

    observed_evidence_ids = set(
        observations_by_evidence.keys()
    )

    if expected_evidence_ids != observed_evidence_ids:
        raise ClaimIntegrityConflictError(
            "Every extracted evidence item must have exactly "
            "one support observation."
        )

    assessment_records = []

    relationship_rank = {
        "SUPPORTS":
            3,

        "PARTIALLY_SUPPORTS":
            2,

        "NEUTRAL":
            1,

        "CHALLENGES":
            -2,

        "CONTRADICTS":
            -3,

        "INSUFFICIENT":
            0,

        "UNRESOLVED":
            0,
    }

    for claim_id, bundle in (
        claim_bundle_by_id.items()
    ):

        evidence_assessments = []

        relationship_counts = {
            relationship: 0
            for relationship
            in allowed_relationships
        }

        support_balance = 0

        for evidence in bundle[
            "evidence_records"
        ]:

            evidence_id = evidence[
                "evidence_id"
            ]

            observation = observations_by_evidence[
                evidence_id
            ]

            relationship = observation[
                "relationship"
            ]

            relationship_counts[
                relationship
            ] += 1

            support_balance += relationship_rank[
                relationship
            ]

            evidence_assessments.append(
                {
                    "schema":
                        "claim_evidence_support_assessment_record_v1",

                    "observation_id":
                        observation.get(
                            "observation_id"
                        ),

                    "claim_id":
                        claim_id,

                    "evidence_id":
                        evidence_id,

                    "relationship":
                        relationship,

                    "basis":
                        copy.deepcopy(
                            observation.get(
                                "basis"
                            )
                        ),

                    "evidence_text":
                        evidence.get(
                            "evidence_text"
                        ),

                    "evidence_type":
                        evidence.get(
                            "evidence_type"
                        ),

                    "evidence_context":
                        copy.deepcopy(
                            evidence.get(
                                "context"
                            )
                        ),

                    "evidence_provenance":
                        copy.deepcopy(
                            evidence.get(
                                "provenance"
                            )
                        ),

                    "relationship_supplied_explicitly":
                        True,

                    "relationship_invented":
                        False,
                }
            )

        total = len(
            evidence_assessments
        )

        supports = (
            relationship_counts["SUPPORTS"]
            + relationship_counts[
                "PARTIALLY_SUPPORTS"
            ]
        )

        opposes = (
            relationship_counts["CHALLENGES"]
            + relationship_counts[
                "CONTRADICTS"
            ]
        )

        unresolved = (
            relationship_counts["UNRESOLVED"]
            + relationship_counts[
                "INSUFFICIENT"
            ]
        )

        if total == 0:
            support_state = (
                "INSUFFICIENT_EVIDENCE"
            )

        elif (
            relationship_counts[
                "CONTRADICTS"
            ] > 0
            and supports == 0
        ):
            support_state = "CONTRADICTED"

        elif (
            supports > 0
            and opposes > 0
        ):
            support_state = "DISPUTED"

        elif (
            relationship_counts[
                "SUPPORTS"
            ] == total
        ):
            support_state = "STRONGLY_SUPPORTED"

        elif (
            supports > 0
            and opposes == 0
            and unresolved == 0
        ):
            support_state = "SUPPORTED"

        elif supports > 0:
            support_state = (
                "PARTIALLY_SUPPORTED"
            )

        elif opposes > 0:
            support_state = "CHALLENGED"

        elif unresolved > 0:
            support_state = (
                "INSUFFICIENT_EVIDENCE"
            )

        else:
            support_state = "NEUTRAL"

        assessment_records.append(
            {
                "schema":
                    "claim_support_assessment_record_v1",

                "claim_id":
                    claim_id,

                "claim_type":
                    bundle.get(
                        "claim_type"
                    ),

                "claim_text":
                    bundle.get(
                        "claim_text"
                    ),

                "source_subject_id":
                    bundle.get(
                        "source_subject_id"
                    ),

                "claim_context":
                    copy.deepcopy(
                        bundle.get(
                            "claim_context"
                        )
                    ),

                "authority_reference":
                    copy.deepcopy(
                        bundle.get(
                            "authority_reference"
                        )
                    ),

                "claim_scope_contract_id":
                    bundle.get(
                        "claim_scope_contract_id"
                    ),

                "claim_scope_contract_digest":
                    bundle.get(
                        "claim_scope_contract_digest"
                    ),

                "evidence_assessment_count":
                    total,

                "evidence_assessments":
                    evidence_assessments,

                "relationship_counts":
                    relationship_counts,

                "support_balance":
                    support_balance,

                "claim_support_state":
                    support_state,

                "authority_score_preserved":
                    True,

                "authority_class_preserved":
                    True,

                "authority_guard_outcome_preserved":
                    True,

                "authority_provenance_preserved":
                    True,

                "active_target_set_ownership_preserved":
                    True,

                "external_authority_partition_preserved":
                    True,

                "external_route_eligibility_preserved":
                    True,

                "external_resolver_ownership_preserved":
                    True,

                "claim_conflict_detection_performed":
                    False,

                "claim_integrity_decision_performed":
                    False,
            }
        )

    return {
        "schema":
            "claim_support_assessment_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25F",

        "status":
            "CLAIM_SUPPORT_ASSESSED",

        "assessment_record_count":
            len(assessment_records),

        "claim_support_assessments":
            assessment_records,

        "claim_evidence_bundles":
            copy.deepcopy(
                bundles
            ),

        "architecture":
            copy.deepcopy(
                extraction_result.get(
                    "architecture"
                )
            ),

        "final_authority_package":
            copy.deepcopy(
                extraction_result.get(
                    "final_authority_package"
                )
            ),

        "preservation_contract":
            copy.deepcopy(
                extraction_result.get(
                    "preservation_contract"
                )
            ),

        "processing_boundaries": {
            "claim_support_assessment_performed":
                True,

            "claim_conflict_detection_performed":
                False,

            "claim_integrity_decision_performed":
                False,

            "external_evidence_fetch_performed":
                False,

            "unsupported_claim_invention_performed":
                False,

            "unsupported_evidence_invention_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "authority_guard_override_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "policy":
            "CERTIFIED_EVIDENCE_BOUND_CLAIM_SUPPORT_ASSESSMENT",

        "next":
            "conflict_detection_and_classification",
    }

def detect_and_classify_claim_conflicts_v1(
    support_result: dict[str, Any],
    conflict_observations: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    4.6.25G ? Conflict Detection & Classification.

    Evaluates explicitly supplied claim-to-claim relationship
    observations and classifies the resulting conflict.

    This stage does not:
    - invent claim relationships,
    - make a final claim-integrity decision,
    - rescore/reclassify Authority,
    - fetch external evidence,
    - create/select external targets,
    - write Semantic Memory,
    - make linking decisions.
    """

    if not isinstance(
        support_result,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "support_result must be a dictionary."
        )

    if not isinstance(
        conflict_observations,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "conflict_observations must be a list."
        )

    expected_lifecycle = {
        "schema":
            "claim_support_assessment_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25F",

        "status":
            "CLAIM_SUPPORT_ASSESSED",

        "policy":
            "CERTIFIED_EVIDENCE_BOUND_CLAIM_SUPPORT_ASSESSMENT",

        "next":
            "conflict_detection_and_classification",
    }

    for key, expected in expected_lifecycle.items():
        if support_result.get(key) != expected:
            raise ClaimIntegrityConflictError(
                "Invalid 4.6.25F lifecycle field: "
                f"{key}"
            )

    assessments = support_result.get(
        "claim_support_assessments"
    )

    if not isinstance(
        assessments,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "claim_support_assessments must be a list."
        )

    if (
        support_result.get(
            "assessment_record_count"
        )
        != len(assessments)
    ):
        raise ClaimIntegrityConflictError(
            "Claim support assessment count mismatch."
        )

    allowed_claim_relationships = {
        "AGREES",
        "COMPATIBLE",
        "PARTIALLY_OVERLAPS",
        "QUALIFIES",
        "DISAGREES",
        "CONTRADICTS",
        "UNRELATED",
        "UNRESOLVED",
    }

    allowed_conflict_classes = {
        "NO_CONFLICT",
        "MINOR_CONFLICT",
        "MATERIAL_CONFLICT",
        "DIRECT_CONTRADICTION",
        "CONTEXT_DEPENDENT_CONFLICT",
        "TEMPORAL_CONFLICT",
        "SCOPE_CONFLICT",
        "QUANTITATIVE_CONFLICT",
        "ATTRIBUTION_CONFLICT",
        "UNRESOLVED_CONFLICT",
    }

    claims_by_id = {}

    for assessment in assessments:

        if not isinstance(
            assessment,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Claim support assessment must be a dictionary."
            )

        if (
            assessment.get("schema")
            != "claim_support_assessment_record_v1"
        ):
            raise ClaimIntegrityConflictError(
                "Invalid claim support assessment schema."
            )

        claim_id = assessment.get(
            "claim_id"
        )

        if (
            not isinstance(claim_id, str)
            or not claim_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "Claim support assessment requires claim_id."
            )

        if claim_id in claims_by_id:
            raise ClaimIntegrityConflictError(
                "Duplicate claim_id in support assessments."
            )

        claims_by_id[
            claim_id
        ] = assessment

    seen_observation_ids = set()
    seen_pairs = set()
    conflict_records = []

    required_fields = (
        "observation_id",
        "claim_a_id",
        "claim_b_id",
        "claim_relationship",
        "conflict_class",
        "materiality",
        "basis",
    )

    for observation in conflict_observations:

        if not isinstance(
            observation,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Each conflict observation must be a dictionary."
            )

        for field in required_fields:
            if field not in observation:
                raise ClaimIntegrityConflictError(
                    "Missing conflict observation field: "
                    f"{field}"
                )

        observation_id = observation.get(
            "observation_id"
        )

        claim_a_id = observation.get(
            "claim_a_id"
        )

        claim_b_id = observation.get(
            "claim_b_id"
        )

        claim_relationship = observation.get(
            "claim_relationship"
        )

        conflict_class = observation.get(
            "conflict_class"
        )

        materiality = observation.get(
            "materiality"
        )

        basis = observation.get(
            "basis"
        )

        if (
            not isinstance(observation_id, str)
            or not observation_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "observation_id must be a non-empty string."
            )

        if observation_id in seen_observation_ids:
            raise ClaimIntegrityConflictError(
                "Duplicate conflict observation_id detected."
            )

        seen_observation_ids.add(
            observation_id
        )

        if claim_a_id not in claims_by_id:
            raise ClaimIntegrityConflictError(
                "Unknown claim_a_id."
            )

        if claim_b_id not in claims_by_id:
            raise ClaimIntegrityConflictError(
                "Unknown claim_b_id."
            )

        if claim_a_id == claim_b_id:
            raise ClaimIntegrityConflictError(
                "A claim cannot be compared against itself."
            )

        pair_key = tuple(
            sorted(
                (
                    claim_a_id,
                    claim_b_id,
                )
            )
        )

        if pair_key in seen_pairs:
            raise ClaimIntegrityConflictError(
                "Duplicate claim pair observation detected."
            )

        seen_pairs.add(
            pair_key
        )

        if (
            claim_relationship
            not in allowed_claim_relationships
        ):
            raise ClaimIntegrityConflictError(
                "Unsupported claim relationship."
            )

        if (
            conflict_class
            not in allowed_conflict_classes
        ):
            raise ClaimIntegrityConflictError(
                "Unsupported conflict class."
            )

        if not isinstance(
            materiality,
            dict,
        ) or not materiality:
            raise ClaimIntegrityConflictError(
                "materiality must be a non-empty dictionary."
            )

        if not isinstance(
            basis,
            dict,
        ) or not basis:
            raise ClaimIntegrityConflictError(
                "basis must be a non-empty dictionary."
            )

        no_conflict_relationships = {
            "AGREES",
            "COMPATIBLE",
            "UNRELATED",
        }

        conflict_relationships = {
            "DISAGREES",
            "CONTRADICTS",
        }

        if (
            claim_relationship
            in no_conflict_relationships
            and conflict_class
            != "NO_CONFLICT"
        ):
            raise ClaimIntegrityConflictError(
                "Non-conflicting relationship cannot carry "
                "a conflicting class."
            )

        if (
            claim_relationship
            == "CONTRADICTS"
            and conflict_class
            == "NO_CONFLICT"
        ):
            raise ClaimIntegrityConflictError(
                "Contradicting claims cannot be classified "
                "as NO_CONFLICT."
            )

        if (
            claim_relationship
            in conflict_relationships
            and conflict_class
            == "NO_CONFLICT"
        ):
            raise ClaimIntegrityConflictError(
                "Conflicting relationship cannot be NO_CONFLICT."
            )

        if (
            conflict_class
            == "DIRECT_CONTRADICTION"
            and claim_relationship
            != "CONTRADICTS"
        ):
            raise ClaimIntegrityConflictError(
                "DIRECT_CONTRADICTION requires CONTRADICTS."
            )

        claim_a = claims_by_id[
            claim_a_id
        ]

        claim_b = claims_by_id[
            claim_b_id
        ]

        conflict_records.append(
            {
                "schema":
                    "claim_conflict_classification_record_v1",

                "observation_id":
                    observation_id,

                "claim_a_id":
                    claim_a_id,

                "claim_b_id":
                    claim_b_id,

                "claim_a_text":
                    claim_a.get(
                        "claim_text"
                    ),

                "claim_b_text":
                    claim_b.get(
                        "claim_text"
                    ),

                "claim_a_type":
                    claim_a.get(
                        "claim_type"
                    ),

                "claim_b_type":
                    claim_b.get(
                        "claim_type"
                    ),

                "claim_a_support_state":
                    claim_a.get(
                        "claim_support_state"
                    ),

                "claim_b_support_state":
                    claim_b.get(
                        "claim_support_state"
                    ),

                "claim_relationship":
                    claim_relationship,

                "conflict_class":
                    conflict_class,

                "materiality":
                    copy.deepcopy(
                        materiality
                    ),

                "basis":
                    copy.deepcopy(
                        basis
                    ),

                "relationship_supplied_explicitly":
                    True,

                "conflict_class_supplied_explicitly":
                    True,

                "unsupported_relationship_invention_performed":
                    False,

                "authority_score_preserved":
                    True,

                "authority_class_preserved":
                    True,

                "authority_guard_outcome_preserved":
                    True,

                "authority_provenance_preserved":
                    True,

                "active_target_set_ownership_preserved":
                    True,

                "external_authority_partition_preserved":
                    True,

                "external_route_eligibility_preserved":
                    True,

                "external_resolver_ownership_preserved":
                    True,

                "claim_integrity_decision_performed":
                    False,
            }
        )

    claims_with_conflicts = {
        claim_id: []
        for claim_id
        in claims_by_id
    }

    for record in conflict_records:

        claim_a_id = record[
            "claim_a_id"
        ]

        claim_b_id = record[
            "claim_b_id"
        ]

        claims_with_conflicts[
            claim_a_id
        ].append(
            copy.deepcopy(record)
        )

        claims_with_conflicts[
            claim_b_id
        ].append(
            copy.deepcopy(record)
        )

    conflict_summaries = []

    for claim_id, assessment in (
        claims_by_id.items()
    ):

        records = claims_with_conflicts[
            claim_id
        ]

        conflict_classes = [
            record[
                "conflict_class"
            ]
            for record in records
            if record[
                "conflict_class"
            ] != "NO_CONFLICT"
        ]

        relationship_values = [
            record[
                "claim_relationship"
            ]
            for record in records
        ]

        direct_contradiction_count = sum(
            1
            for record in records
            if record[
                "conflict_class"
            ]
            == "DIRECT_CONTRADICTION"
        )

        material_conflict_count = sum(
            1
            for record in records
            if record[
                "conflict_class"
            ]
            == "MATERIAL_CONFLICT"
        )

        unresolved_conflict_count = sum(
            1
            for record in records
            if record[
                "conflict_class"
            ]
            == "UNRESOLVED_CONFLICT"
        )

        conflict_summaries.append(
            {
                "schema":
                    "claim_conflict_summary_record_v1",

                "claim_id":
                    claim_id,

                "claim_support_state":
                    assessment.get(
                        "claim_support_state"
                    ),

                "comparison_count":
                    len(records),

                "conflict_count":
                    len(
                        conflict_classes
                    ),

                "conflict_classes":
                    tuple(
                        conflict_classes
                    ),

                "claim_relationships":
                    tuple(
                        relationship_values
                    ),

                "direct_contradiction_count":
                    direct_contradiction_count,

                "material_conflict_count":
                    material_conflict_count,

                "unresolved_conflict_count":
                    unresolved_conflict_count,

                "has_conflict":
                    bool(
                        conflict_classes
                    ),

                "claim_integrity_decision_performed":
                    False,
            }
        )

    return {
        "schema":
            "claim_conflict_detection_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25G",

        "status":
            "CLAIM_CONFLICTS_DETECTED_AND_CLASSIFIED",

        "conflict_record_count":
            len(conflict_records),

        "claim_conflict_records":
            conflict_records,

        "claim_conflict_summary_count":
            len(conflict_summaries),

        "claim_conflict_summaries":
            conflict_summaries,

        "claim_support_assessments":
            copy.deepcopy(
                assessments
            ),

        "architecture":
            copy.deepcopy(
                support_result.get(
                    "architecture"
                )
            ),

        "final_authority_package":
            copy.deepcopy(
                support_result.get(
                    "final_authority_package"
                )
            ),

        "preservation_contract":
            copy.deepcopy(
                support_result.get(
                    "preservation_contract"
                )
            ),

        "processing_boundaries": {
            "claim_conflict_detection_performed":
                True,

            "claim_conflict_classification_performed":
                True,

            "claim_integrity_decision_performed":
                False,

            "unsupported_relationship_invention_performed":
                False,

            "external_evidence_fetch_performed":
                False,

            "unsupported_claim_invention_performed":
                False,

            "unsupported_evidence_invention_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "authority_guard_override_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "policy":
            "CERTIFIED_CONTEXT_SPECIFIC_CLAIM_CONFLICT_CLASSIFICATION",

        "next":
            "claim_integrity_decision",
    }

def decide_claim_integrity_v1(
    conflict_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.25H ? Claim Integrity Decision.

    Combines certified claim-support assessment and certified
    claim-conflict classification into an evidence-bound claim
    integrity decision.

    Authority remains preserved input context and does not by itself
    determine claim truth or falsehood.

    Operational blocking is deferred to 4.6.25I.
    """

    if not isinstance(
        conflict_result,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "conflict_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "claim_conflict_detection_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25G",

        "status":
            "CLAIM_CONFLICTS_DETECTED_AND_CLASSIFIED",

        "policy":
            "CERTIFIED_CONTEXT_SPECIFIC_CLAIM_CONFLICT_CLASSIFICATION",

        "next":
            "claim_integrity_decision",
    }

    for key, expected in expected_lifecycle.items():

        if conflict_result.get(key) != expected:
            raise ClaimIntegrityConflictError(
                "Invalid 4.6.25G lifecycle field: "
                f"{key}"
            )

    assessments = conflict_result.get(
        "claim_support_assessments"
    )

    summaries = conflict_result.get(
        "claim_conflict_summaries"
    )

    conflict_records = conflict_result.get(
        "claim_conflict_records"
    )

    if not isinstance(
        assessments,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "claim_support_assessments must be a list."
        )

    if not isinstance(
        summaries,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "claim_conflict_summaries must be a list."
        )

    if not isinstance(
        conflict_records,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "claim_conflict_records must be a list."
        )

    if (
        conflict_result.get(
            "claim_conflict_summary_count"
        )
        != len(summaries)
    ):
        raise ClaimIntegrityConflictError(
            "Claim conflict summary count mismatch."
        )

    if (
        conflict_result.get(
            "conflict_record_count"
        )
        != len(conflict_records)
    ):
        raise ClaimIntegrityConflictError(
            "Conflict record count mismatch."
        )

    allowed_support_states = {
        "STRONGLY_SUPPORTED",
        "SUPPORTED",
        "PARTIALLY_SUPPORTED",
        "DISPUTED",
        "CONTRADICTED",
        "CHALLENGED",
        "INSUFFICIENT_EVIDENCE",
        "NEUTRAL",
    }

    allowed_integrity_states = {
        "WELL_SUPPORTED",
        "SUPPORTED",
        "PARTIALLY_SUPPORTED",
        "DISPUTED",
        "CONTRADICTED",
        "INSUFFICIENT_EVIDENCE",
        "UNRESOLVED",
        "BLOCKED",
    }

    assessment_by_claim = {}

    for assessment in assessments:

        if not isinstance(
            assessment,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Claim support assessment must be a dictionary."
            )

        if (
            assessment.get("schema")
            != "claim_support_assessment_record_v1"
        ):
            raise ClaimIntegrityConflictError(
                "Invalid claim support assessment schema."
            )

        claim_id = assessment.get(
            "claim_id"
        )

        if (
            not isinstance(claim_id, str)
            or not claim_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "Claim support assessment requires claim_id."
            )

        if claim_id in assessment_by_claim:
            raise ClaimIntegrityConflictError(
                "Duplicate claim support assessment."
            )

        support_state = assessment.get(
            "claim_support_state"
        )

        if support_state not in allowed_support_states:
            raise ClaimIntegrityConflictError(
                "Unsupported claim support state."
            )

        assessment_by_claim[
            claim_id
        ] = assessment

    summary_by_claim = {}

    for summary in summaries:

        if not isinstance(
            summary,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Claim conflict summary must be a dictionary."
            )

        if (
            summary.get("schema")
            != "claim_conflict_summary_record_v1"
        ):
            raise ClaimIntegrityConflictError(
                "Invalid claim conflict summary schema."
            )

        claim_id = summary.get(
            "claim_id"
        )

        if claim_id not in assessment_by_claim:
            raise ClaimIntegrityConflictError(
                "Conflict summary references unknown claim."
            )

        if claim_id in summary_by_claim:
            raise ClaimIntegrityConflictError(
                "Duplicate conflict summary for claim."
            )

        for field in (
            "comparison_count",
            "conflict_count",
            "direct_contradiction_count",
            "material_conflict_count",
            "unresolved_conflict_count",
        ):
            value = summary.get(field)

            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                raise ClaimIntegrityConflictError(
                    "Invalid conflict summary counter: "
                    f"{field}"
                )

        if (
            summary.get("conflict_count")
            > summary.get("comparison_count")
        ):
            raise ClaimIntegrityConflictError(
                "Conflict count cannot exceed comparison count."
            )

        has_conflict = summary.get(
            "has_conflict"
        )

        if not isinstance(
            has_conflict,
            bool,
        ):
            raise ClaimIntegrityConflictError(
                "has_conflict must be boolean."
            )

        if (
            has_conflict
            != (
                summary.get(
                    "conflict_count"
                ) > 0
            )
        ):
            raise ClaimIntegrityConflictError(
                "Conflict presence flag is inconsistent."
            )

        summary_by_claim[
            claim_id
        ] = summary

    if (
        set(assessment_by_claim)
        != set(summary_by_claim)
    ):
        raise ClaimIntegrityConflictError(
            "Every claim support assessment must have exactly "
            "one conflict summary."
        )

    integrity_records = []

    for claim_id, assessment in (
        assessment_by_claim.items()
    ):

        summary = summary_by_claim[
            claim_id
        ]

        support_state = assessment[
            "claim_support_state"
        ]

        has_conflict = summary[
            "has_conflict"
        ]

        direct_count = summary[
            "direct_contradiction_count"
        ]

        material_count = summary[
            "material_conflict_count"
        ]

        unresolved_count = summary[
            "unresolved_conflict_count"
        ]

        if support_state == "CONTRADICTED":

            integrity_state = (
                "CONTRADICTED"
            )

            decision_basis = (
                "CLAIM_EVIDENCE_CONTRADICTS"
            )

        elif unresolved_count > 0:

            integrity_state = (
                "UNRESOLVED"
            )

            decision_basis = (
                "UNRESOLVED_CLAIM_CONFLICT"
            )

        elif (
            direct_count > 0
            or material_count > 0
        ):

            integrity_state = (
                "DISPUTED"
            )

            decision_basis = (
                "MATERIAL_OR_DIRECT_CLAIM_CONFLICT"
            )

        elif has_conflict:

            integrity_state = (
                "DISPUTED"
            )

            decision_basis = (
                "CONTEXT_SPECIFIC_CLAIM_CONFLICT"
            )

        elif (
            support_state
            == "STRONGLY_SUPPORTED"
        ):

            integrity_state = (
                "WELL_SUPPORTED"
            )

            decision_basis = (
                "STRONG_EVIDENCE_SUPPORT_NO_CONFLICT"
            )

        elif support_state == "SUPPORTED":

            integrity_state = (
                "SUPPORTED"
            )

            decision_basis = (
                "EVIDENCE_SUPPORT_NO_CONFLICT"
            )

        elif (
            support_state
            == "PARTIALLY_SUPPORTED"
        ):

            integrity_state = (
                "PARTIALLY_SUPPORTED"
            )

            decision_basis = (
                "PARTIAL_EVIDENCE_SUPPORT"
            )

        elif support_state in {
            "DISPUTED",
            "CHALLENGED",
        }:

            integrity_state = (
                "DISPUTED"
            )

            decision_basis = (
                "EVIDENCE_SUPPORT_IS_DISPUTED"
            )

        elif support_state in {
            "INSUFFICIENT_EVIDENCE",
            "NEUTRAL",
        }:

            integrity_state = (
                "INSUFFICIENT_EVIDENCE"
            )

            decision_basis = (
                "INSUFFICIENT_DECISION_EVIDENCE"
            )

        else:

            integrity_state = (
                "UNRESOLVED"
            )

            decision_basis = (
                "UNRESOLVED_INTEGRITY_STATE"
            )

        if (
            integrity_state
            not in allowed_integrity_states
        ):
            raise ClaimIntegrityConflictError(
                "Invalid derived claim integrity state."
            )

        authority_reference = assessment.get(
            "authority_reference"
        )

        if not isinstance(
            authority_reference,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "authority_reference must be a dictionary."
            )

        integrity_records.append(
            {
                "schema":
                    "claim_integrity_decision_record_v1",

                "claim_id":
                    claim_id,

                "claim_type":
                    assessment.get(
                        "claim_type"
                    ),

                "claim_text":
                    assessment.get(
                        "claim_text"
                    ),

                "claim_support_state":
                    support_state,

                "conflict_summary":
                    copy.deepcopy(
                        summary
                    ),

                "claim_integrity_state":
                    integrity_state,

                "decision_basis":
                    decision_basis,

                "authority_reference":
                    copy.deepcopy(
                        authority_reference
                    ),

                "authority_used_as_truth_proxy":
                    False,

                "authority_used_as_falsehood_proxy":
                    False,

                "claim_truth_not_presumed_from_authority":
                    True,

                "claim_falsehood_not_presumed_from_low_authority":
                    True,

                "integrity_decision_is_evidence_and_conflict_bound":
                    True,

                "operational_blocking_deferred_to_guard":
                    True,

                "authority_score_preserved":
                    True,

                "authority_class_preserved":
                    True,

                "authority_guard_outcome_preserved":
                    True,

                "authority_provenance_preserved":
                    True,

                "active_target_set_ownership_preserved":
                    True,

                "external_authority_partition_preserved":
                    True,

                "external_route_eligibility_preserved":
                    True,

                "external_resolver_ownership_preserved":
                    True,
            }
        )

    return {
        "schema":
            "claim_integrity_decision_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25H",

        "status":
            "CLAIM_INTEGRITY_DECISIONS_BUILT",

        "integrity_record_count":
            len(integrity_records),

        "claim_integrity_decisions":
            integrity_records,

        "claim_support_assessments":
            copy.deepcopy(
                assessments
            ),

        "claim_conflict_records":
            copy.deepcopy(
                conflict_records
            ),

        "claim_conflict_summaries":
            copy.deepcopy(
                summaries
            ),

        "architecture":
            copy.deepcopy(
                conflict_result.get(
                    "architecture"
                )
            ),

        "final_authority_package":
            copy.deepcopy(
                conflict_result.get(
                    "final_authority_package"
                )
            ),

        "preservation_contract":
            copy.deepcopy(
                conflict_result.get(
                    "preservation_contract"
                )
            ),

        "processing_boundaries": {
            "claim_integrity_decision_performed":
                True,

            "integrity_guard_performed":
                False,

            "operational_blocking_performed":
                False,

            "unsupported_integrity_invention_performed":
                False,

            "authority_used_as_truth_proxy":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "authority_guard_override_performed":
                False,

            "external_evidence_fetch_performed":
                False,

            "unsupported_claim_invention_performed":
                False,

            "unsupported_evidence_invention_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "policy":
            "CERTIFIED_EVIDENCE_AND_CONFLICT_BOUND_CLAIM_INTEGRITY_DECISION",

        "next":
            "integrity_conflict_guard",
    }

def apply_integrity_conflict_guard_v1(
    integrity_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.25I ? Integrity / Conflict Guard.

    Applies operational guard dispositions to certified claim
    integrity decisions.

    The guard does not change the upstream integrity state.
    It only controls downstream claim eligibility.
    """

    if not isinstance(
        integrity_result,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "integrity_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "claim_integrity_decision_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25H",

        "status":
            "CLAIM_INTEGRITY_DECISIONS_BUILT",

        "policy":
            "CERTIFIED_EVIDENCE_AND_CONFLICT_BOUND_CLAIM_INTEGRITY_DECISION",

        "next":
            "integrity_conflict_guard",
    }

    for key, expected in expected_lifecycle.items():

        if integrity_result.get(key) != expected:
            raise ClaimIntegrityConflictError(
                "Invalid 4.6.25H lifecycle field: "
                f"{key}"
            )

    decisions = integrity_result.get(
        "claim_integrity_decisions"
    )

    if not isinstance(
        decisions,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "claim_integrity_decisions must be a list."
        )

    if (
        integrity_result.get(
            "integrity_record_count"
        )
        != len(decisions)
    ):
        raise ClaimIntegrityConflictError(
            "Claim integrity record count mismatch."
        )

    allowed_integrity_states = {
        "WELL_SUPPORTED",
        "SUPPORTED",
        "PARTIALLY_SUPPORTED",
        "DISPUTED",
        "CONTRADICTED",
        "INSUFFICIENT_EVIDENCE",
        "UNRESOLVED",
        "BLOCKED",
    }

    guard_map = {
        "WELL_SUPPORTED":
            "PASS",

        "SUPPORTED":
            "PASS",

        "PARTIALLY_SUPPORTED":
            "CAUTION",

        "DISPUTED":
            "HOLD",

        "CONTRADICTED":
            "BLOCK",

        "INSUFFICIENT_EVIDENCE":
            "HOLD",

        "UNRESOLVED":
            "HOLD",

        "BLOCKED":
            "BLOCK",
    }

    downstream_eligibility = {
        "PASS":
            True,

        "CAUTION":
            True,

        "HOLD":
            False,

        "BLOCK":
            False,
    }

    guard_records = []

    seen_claim_ids = set()

    for decision in decisions:

        if not isinstance(
            decision,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Claim integrity decision must be a dictionary."
            )

        if (
            decision.get("schema")
            != "claim_integrity_decision_record_v1"
        ):
            raise ClaimIntegrityConflictError(
                "Invalid claim integrity decision schema."
            )

        claim_id = decision.get(
            "claim_id"
        )

        if (
            not isinstance(claim_id, str)
            or not claim_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "Claim integrity decision requires claim_id."
            )

        if claim_id in seen_claim_ids:
            raise ClaimIntegrityConflictError(
                "Duplicate claim integrity decision detected."
            )

        seen_claim_ids.add(
            claim_id
        )

        integrity_state = decision.get(
            "claim_integrity_state"
        )

        if integrity_state not in allowed_integrity_states:
            raise ClaimIntegrityConflictError(
                "Unsupported claim integrity state."
            )

        if (
            decision.get(
                "authority_used_as_truth_proxy"
            )
            is not False
        ):
            raise ClaimIntegrityConflictError(
                "Authority truth-proxy boundary violated."
            )

        if (
            decision.get(
                "authority_used_as_falsehood_proxy"
            )
            is not False
        ):
            raise ClaimIntegrityConflictError(
                "Authority falsehood-proxy boundary violated."
            )

        if (
            decision.get(
                "integrity_decision_is_evidence_and_conflict_bound"
            )
            is not True
        ):
            raise ClaimIntegrityConflictError(
                "Integrity decision must remain evidence "
                "and conflict bound."
            )

        if (
            decision.get(
                "operational_blocking_deferred_to_guard"
            )
            is not True
        ):
            raise ClaimIntegrityConflictError(
                "Operational blocking ownership drift detected."
            )

        guard_disposition = guard_map[
            integrity_state
        ]

        eligible = downstream_eligibility[
            guard_disposition
        ]

        guard_records.append(
            {
                "schema":
                    "claim_integrity_guard_record_v1",

                "claim_id":
                    claim_id,

                "claim_type":
                    decision.get(
                        "claim_type"
                    ),

                "claim_text":
                    decision.get(
                        "claim_text"
                    ),

                "claim_support_state":
                    decision.get(
                        "claim_support_state"
                    ),

                "claim_integrity_state":
                    integrity_state,

                "integrity_decision_basis":
                    decision.get(
                        "decision_basis"
                    ),

                "conflict_summary":
                    copy.deepcopy(
                        decision.get(
                            "conflict_summary"
                        )
                    ),

                "authority_reference":
                    copy.deepcopy(
                        decision.get(
                            "authority_reference"
                        )
                    ),

                "guard_disposition":
                    guard_disposition,

                "downstream_claim_eligible":
                    eligible,

                "operational_blocking_applied":
                    (
                        guard_disposition
                        == "BLOCK"
                    ),

                "operational_hold_applied":
                    (
                        guard_disposition
                        == "HOLD"
                    ),

                "caution_applied":
                    (
                        guard_disposition
                        == "CAUTION"
                    ),

                "integrity_state_mutated":
                    False,

                "authority_used_as_truth_proxy":
                    False,

                "authority_rescoring_performed":
                    False,

                "authority_reclassification_performed":
                    False,

                "authority_guard_override_performed":
                    False,

                "authority_score_preserved":
                    True,

                "authority_class_preserved":
                    True,

                "authority_guard_outcome_preserved":
                    True,

                "authority_provenance_preserved":
                    True,

                "active_target_set_ownership_preserved":
                    True,

                "external_authority_partition_preserved":
                    True,

                "external_route_eligibility_preserved":
                    True,

                "external_resolver_ownership_preserved":
                    True,

                "external_target_created":
                    False,

                "external_target_selected":
                    False,

                "semantic_memory_written":
                    False,

                "linking_decisions_performed":
                    False,
            }
        )

    return {
        "schema":
            "claim_integrity_guard_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25I",

        "status":
            "CLAIM_INTEGRITY_GUARD_APPLIED",

        "guard_record_count":
            len(guard_records),

        "claim_integrity_guard_records":
            guard_records,

        "claim_integrity_decisions":
            copy.deepcopy(
                decisions
            ),

        "claim_support_assessments":
            copy.deepcopy(
                integrity_result.get(
                    "claim_support_assessments"
                )
            ),

        "claim_conflict_records":
            copy.deepcopy(
                integrity_result.get(
                    "claim_conflict_records"
                )
            ),

        "claim_conflict_summaries":
            copy.deepcopy(
                integrity_result.get(
                    "claim_conflict_summaries"
                )
            ),

        "architecture":
            copy.deepcopy(
                integrity_result.get(
                    "architecture"
                )
            ),

        "final_authority_package":
            copy.deepcopy(
                integrity_result.get(
                    "final_authority_package"
                )
            ),

        "preservation_contract":
            copy.deepcopy(
                integrity_result.get(
                    "preservation_contract"
                )
            ),

        "processing_boundaries": {
            "integrity_guard_performed":
                True,

            "operational_blocking_performed":
                any(
                    record[
                        "operational_blocking_applied"
                    ]
                    for record in guard_records
                ),

            "operational_hold_performed":
                any(
                    record[
                        "operational_hold_applied"
                    ]
                    for record in guard_records
                ),

            "integrity_state_mutation_performed":
                False,

            "authority_used_as_truth_proxy":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "authority_guard_override_performed":
                False,

            "external_evidence_fetch_performed":
                False,

            "unsupported_claim_invention_performed":
                False,

            "unsupported_evidence_invention_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "policy":
            "CERTIFIED_CLAIM_INTEGRITY_CONFLICT_GUARD",

        "next":
            "provenance_and_conflict_evidence_trace",
    }

def build_provenance_conflict_evidence_trace_v1(
    guard_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.25J ? Provenance & Conflict Evidence Trace.

    Builds an immutable audit trace for each guarded claim from:
    Authority ? Evidence ? Support ? Conflict ? Integrity ? Guard.

    This stage performs no rescoring, reclassification, decision
    mutation, target selection, Semantic Memory write, or linking
    decision.
    """

    if not isinstance(
        guard_result,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "guard_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "claim_integrity_guard_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25I",

        "status":
            "CLAIM_INTEGRITY_GUARD_APPLIED",

        "policy":
            "CERTIFIED_CLAIM_INTEGRITY_CONFLICT_GUARD",

        "next":
            "provenance_and_conflict_evidence_trace",
    }

    for key, expected in expected_lifecycle.items():

        if guard_result.get(key) != expected:
            raise ClaimIntegrityConflictError(
                "Invalid 4.6.25I lifecycle field: "
                f"{key}"
            )

    guard_records = guard_result.get(
        "claim_integrity_guard_records"
    )

    decisions = guard_result.get(
        "claim_integrity_decisions"
    )

    assessments = guard_result.get(
        "claim_support_assessments"
    )

    conflict_records = guard_result.get(
        "claim_conflict_records"
    )

    conflict_summaries = guard_result.get(
        "claim_conflict_summaries"
    )

    for name, value in (
        (
            "claim_integrity_guard_records",
            guard_records,
        ),
        (
            "claim_integrity_decisions",
            decisions,
        ),
        (
            "claim_support_assessments",
            assessments,
        ),
        (
            "claim_conflict_records",
            conflict_records,
        ),
        (
            "claim_conflict_summaries",
            conflict_summaries,
        ),
    ):
        if not isinstance(
            value,
            list,
        ):
            raise ClaimIntegrityConflictError(
                f"{name} must be a list."
            )

    if (
        guard_result.get(
            "guard_record_count"
        )
        != len(guard_records)
    ):
        raise ClaimIntegrityConflictError(
            "Guard record count mismatch."
        )

    def index_unique(
        records,
        schema,
        name,
    ):
        result = {}

        for record in records:

            if not isinstance(
                record,
                dict,
            ):
                raise ClaimIntegrityConflictError(
                    f"{name} record must be a dictionary."
                )

            if record.get("schema") != schema:
                raise ClaimIntegrityConflictError(
                    f"Invalid {name} schema."
                )

            claim_id = record.get(
                "claim_id"
            )

            if (
                not isinstance(claim_id, str)
                or not claim_id.strip()
            ):
                raise ClaimIntegrityConflictError(
                    f"{name} requires claim_id."
                )

            if claim_id in result:
                raise ClaimIntegrityConflictError(
                    f"Duplicate {name} claim_id."
                )

            result[
                claim_id
            ] = record

        return result

    guard_by_claim = index_unique(
        guard_records,
        "claim_integrity_guard_record_v1",
        "guard",
    )

    decision_by_claim = index_unique(
        decisions,
        "claim_integrity_decision_record_v1",
        "integrity decision",
    )

    assessment_by_claim = index_unique(
        assessments,
        "claim_support_assessment_record_v1",
        "support assessment",
    )

    summary_by_claim = index_unique(
        conflict_summaries,
        "claim_conflict_summary_record_v1",
        "conflict summary",
    )

    claim_ids = set(
        guard_by_claim
    )

    for indexed in (
        decision_by_claim,
        assessment_by_claim,
        summary_by_claim,
    ):
        if set(indexed) != claim_ids:
            raise ClaimIntegrityConflictError(
                "Claim trace alignment drift detected."
            )

    conflicts_by_claim = {
        claim_id: []
        for claim_id in claim_ids
    }

    seen_conflict_ids = set()

    for record in conflict_records:

        if not isinstance(
            record,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Conflict record must be a dictionary."
            )

        if (
            record.get("schema")
            != "claim_conflict_classification_record_v1"
        ):
            raise ClaimIntegrityConflictError(
                "Invalid conflict record schema."
            )

        observation_id = record.get(
            "observation_id"
        )

        if (
            not isinstance(observation_id, str)
            or not observation_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "Conflict record requires observation_id."
            )

        if observation_id in seen_conflict_ids:
            raise ClaimIntegrityConflictError(
                "Duplicate conflict observation_id."
            )

        seen_conflict_ids.add(
            observation_id
        )

        claim_a = record.get(
            "claim_a_id"
        )

        claim_b = record.get(
            "claim_b_id"
        )

        if (
            claim_a not in claim_ids
            or claim_b not in claim_ids
        ):
            raise ClaimIntegrityConflictError(
                "Conflict record references unknown claim."
            )

        conflicts_by_claim[
            claim_a
        ].append(
            record
        )

        conflicts_by_claim[
            claim_b
        ].append(
            record
        )

    trace_records = []

    for claim_id in sorted(
        claim_ids
    ):

        guard = guard_by_claim[
            claim_id
        ]

        decision = decision_by_claim[
            claim_id
        ]

        assessment = assessment_by_claim[
            claim_id
        ]

        summary = summary_by_claim[
            claim_id
        ]

        if (
            guard.get(
                "claim_integrity_state"
            )
            != decision.get(
                "claim_integrity_state"
            )
        ):
            raise ClaimIntegrityConflictError(
                "Integrity state trace mismatch."
            )

        if (
            guard.get(
                "claim_support_state"
            )
            != assessment.get(
                "claim_support_state"
            )
        ):
            raise ClaimIntegrityConflictError(
                "Support state trace mismatch."
            )

        authority_reference = decision.get(
            "authority_reference"
        )

        if not isinstance(
            authority_reference,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "authority_reference must be a dictionary."
            )

        evidence_assessments = assessment.get(
            "evidence_assessments"
        )

        if not isinstance(
            evidence_assessments,
            list,
        ):
            raise ClaimIntegrityConflictError(
                "evidence_assessments must be a list."
            )

        evidence_trace = []

        for evidence in evidence_assessments:

            if not isinstance(
                evidence,
                dict,
            ):
                raise ClaimIntegrityConflictError(
                    "Evidence assessment must be a dictionary."
                )

            if (
                evidence.get("schema")
                != "claim_evidence_support_assessment_record_v1"
            ):
                raise ClaimIntegrityConflictError(
                    "Invalid evidence assessment schema."
                )

            if (
                evidence.get(
                    "claim_id"
                )
                != claim_id
            ):
                raise ClaimIntegrityConflictError(
                    "Evidence assessment claim mismatch."
                )

            evidence_trace.append(
                {
                    "schema":
                        "claim_integrity_evidence_trace_record_v1",

                    "observation_id":
                        evidence.get(
                            "observation_id"
                        ),

                    "evidence_id":
                        evidence.get(
                            "evidence_id"
                        ),

                    "relationship":
                        evidence.get(
                            "relationship"
                        ),

                    "basis":
                        copy.deepcopy(
                            evidence.get(
                                "basis"
                            )
                        ),

                    "evidence_text":
                        evidence.get(
                            "evidence_text"
                        ),

                    "evidence_type":
                        evidence.get(
                            "evidence_type"
                        ),

                    "evidence_context":
                        copy.deepcopy(
                            evidence.get(
                                "evidence_context"
                            )
                        ),

                    "evidence_provenance":
                        copy.deepcopy(
                            evidence.get(
                                "evidence_provenance"
                            )
                        ),
                }
            )

        conflict_trace = []

        for conflict in conflicts_by_claim[
            claim_id
        ]:

            conflict_trace.append(
                {
                    "schema":
                        "claim_integrity_conflict_trace_record_v1",

                    "observation_id":
                        conflict.get(
                            "observation_id"
                        ),

                    "claim_a_id":
                        conflict.get(
                            "claim_a_id"
                        ),

                    "claim_b_id":
                        conflict.get(
                            "claim_b_id"
                        ),

                    "claim_relationship":
                        conflict.get(
                            "claim_relationship"
                        ),

                    "conflict_class":
                        conflict.get(
                            "conflict_class"
                        ),

                    "materiality":
                        copy.deepcopy(
                            conflict.get(
                                "materiality"
                            )
                        ),

                    "basis":
                        copy.deepcopy(
                            conflict.get(
                                "basis"
                            )
                        ),
                }
            )

        trace_core = {
            "schema":
                "claim_integrity_provenance_trace_record_v1",

            "claim_id":
                claim_id,

            "claim_type":
                decision.get(
                    "claim_type"
                ),

            "claim_text":
                decision.get(
                    "claim_text"
                ),

            "authority_reference":
                copy.deepcopy(
                    authority_reference
                ),

            "evidence_trace":
                evidence_trace,

            "support_state":
                assessment.get(
                    "claim_support_state"
                ),

            "support_balance":
                assessment.get(
                    "support_balance"
                ),

            "relationship_counts":
                copy.deepcopy(
                    assessment.get(
                        "relationship_counts"
                    )
                ),

            "conflict_trace":
                conflict_trace,

            "conflict_summary":
                copy.deepcopy(
                    summary
                ),

            "integrity_state":
                decision.get(
                    "claim_integrity_state"
                ),

            "integrity_decision_basis":
                decision.get(
                    "decision_basis"
                ),

            "guard_disposition":
                guard.get(
                    "guard_disposition"
                ),

            "downstream_claim_eligible":
                guard.get(
                    "downstream_claim_eligible"
                ),

            "operational_blocking_applied":
                guard.get(
                    "operational_blocking_applied"
                ),

            "operational_hold_applied":
                guard.get(
                    "operational_hold_applied"
                ),

            "caution_applied":
                guard.get(
                    "caution_applied"
                ),

            "authority_preserved":
                True,

            "support_preserved":
                True,

            "conflict_preserved":
                True,

            "integrity_decision_preserved":
                True,

            "guard_disposition_preserved":
                True,

            "active_target_set_ownership_preserved":
                True,

            "external_authority_partition_preserved":
                True,

            "external_route_eligibility_preserved":
                True,

            "external_resolver_ownership_preserved":
                True,
        }

        canonical = json.dumps(
            trace_core,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        digest = hashlib.sha256(
            canonical.encode(
                "utf-8"
            )
        ).hexdigest()

        trace_records.append(
            {
                **trace_core,

                "trace_id":
                    f"claimtrace:v1:{digest}",

                "trace_digest":
                    digest,
            }
        )

    return {
        "schema":
            "claim_integrity_provenance_trace_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25J",

        "status":
            "CLAIM_PROVENANCE_AND_CONFLICT_TRACE_BUILT",

        "trace_record_count":
            len(trace_records),

        "claim_integrity_provenance_traces":
            trace_records,

        "claim_integrity_guard_records":
            copy.deepcopy(
                guard_records
            ),

        "claim_integrity_decisions":
            copy.deepcopy(
                decisions
            ),

        "claim_support_assessments":
            copy.deepcopy(
                assessments
            ),

        "claim_conflict_records":
            copy.deepcopy(
                conflict_records
            ),

        "claim_conflict_summaries":
            copy.deepcopy(
                conflict_summaries
            ),

        "architecture":
            copy.deepcopy(
                guard_result.get(
                    "architecture"
                )
            ),

        "final_authority_package":
            copy.deepcopy(
                guard_result.get(
                    "final_authority_package"
                )
            ),

        "preservation_contract":
            copy.deepcopy(
                guard_result.get(
                    "preservation_contract"
                )
            ),

        "processing_boundaries": {
            "provenance_trace_built":
                True,

            "conflict_evidence_trace_built":
                True,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "authority_guard_override_performed":
                False,

            "support_reassessment_performed":
                False,

            "conflict_reclassification_performed":
                False,

            "integrity_decision_mutation_performed":
                False,

            "guard_disposition_mutation_performed":
                False,

            "external_evidence_fetch_performed":
                False,

            "unsupported_claim_invention_performed":
                False,

            "unsupported_evidence_invention_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "policy":
            "CERTIFIED_CLAIM_PROVENANCE_AND_CONFLICT_EVIDENCE_TRACE",

        "next":
            "final_claim_integrity_result",
    }

def build_final_claim_integrity_result_v1(
    trace_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.25K ? Final Claim Integrity Result.

    Packages certified provenance traces into the immutable
    downstream-consumable Claim Integrity & Conflict result.

    No new support assessment, conflict detection, integrity
    decision, guard decision, Authority mutation, target selection,
    Semantic Memory write, or linking decision is performed.
    """

    if not isinstance(
        trace_result,
        dict,
    ):
        raise ClaimIntegrityConflictError(
            "trace_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "claim_integrity_provenance_trace_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25J",

        "status":
            "CLAIM_PROVENANCE_AND_CONFLICT_TRACE_BUILT",

        "policy":
            "CERTIFIED_CLAIM_PROVENANCE_AND_CONFLICT_EVIDENCE_TRACE",

        "next":
            "final_claim_integrity_result",
    }

    for key, expected in expected_lifecycle.items():

        if trace_result.get(key) != expected:
            raise ClaimIntegrityConflictError(
                "Invalid 4.6.25J lifecycle field: "
                f"{key}"
            )

    traces = trace_result.get(
        "claim_integrity_provenance_traces"
    )

    if not isinstance(
        traces,
        list,
    ):
        raise ClaimIntegrityConflictError(
            "claim_integrity_provenance_traces must be a list."
        )

    if (
        trace_result.get(
            "trace_record_count"
        )
        != len(traces)
    ):
        raise ClaimIntegrityConflictError(
            "Trace record count mismatch."
        )

    allowed_integrity_states = {
        "WELL_SUPPORTED",
        "SUPPORTED",
        "PARTIALLY_SUPPORTED",
        "DISPUTED",
        "CONTRADICTED",
        "INSUFFICIENT_EVIDENCE",
        "UNRESOLVED",
        "BLOCKED",
    }

    allowed_guard_dispositions = {
        "PASS",
        "CAUTION",
        "HOLD",
        "BLOCK",
    }

    final_records = []
    seen_claim_ids = set()
    seen_trace_ids = set()

    for trace in traces:

        if not isinstance(
            trace,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "Provenance trace must be a dictionary."
            )

        if (
            trace.get("schema")
            != "claim_integrity_provenance_trace_record_v1"
        ):
            raise ClaimIntegrityConflictError(
                "Invalid provenance trace schema."
            )

        claim_id = trace.get(
            "claim_id"
        )

        trace_id = trace.get(
            "trace_id"
        )

        trace_digest = trace.get(
            "trace_digest"
        )

        if (
            not isinstance(claim_id, str)
            or not claim_id.strip()
        ):
            raise ClaimIntegrityConflictError(
                "Trace requires claim_id."
            )

        if claim_id in seen_claim_ids:
            raise ClaimIntegrityConflictError(
                "Duplicate claim_id in provenance traces."
            )

        seen_claim_ids.add(
            claim_id
        )

        if (
            not isinstance(trace_id, str)
            or not trace_id.startswith(
                "claimtrace:v1:"
            )
        ):
            raise ClaimIntegrityConflictError(
                "Invalid trace_id."
            )

        if trace_id in seen_trace_ids:
            raise ClaimIntegrityConflictError(
                "Duplicate trace_id."
            )

        seen_trace_ids.add(
            trace_id
        )

        if (
            not isinstance(trace_digest, str)
            or len(trace_digest) != 64
        ):
            raise ClaimIntegrityConflictError(
                "Invalid trace_digest."
            )

        integrity_state = trace.get(
            "integrity_state"
        )

        guard_disposition = trace.get(
            "guard_disposition"
        )

        downstream_eligible = trace.get(
            "downstream_claim_eligible"
        )

        if integrity_state not in allowed_integrity_states:
            raise ClaimIntegrityConflictError(
                "Unsupported integrity state."
            )

        if guard_disposition not in allowed_guard_dispositions:
            raise ClaimIntegrityConflictError(
                "Unsupported guard disposition."
            )

        if not isinstance(
            downstream_eligible,
            bool,
        ):
            raise ClaimIntegrityConflictError(
                "downstream_claim_eligible must be boolean."
            )

        expected_eligibility = (
            guard_disposition
            in {
                "PASS",
                "CAUTION",
            }
        )

        if (
            downstream_eligible
            is not expected_eligibility
        ):
            raise ClaimIntegrityConflictError(
                "Guard disposition and downstream eligibility drift."
            )

        for preservation_flag in (
            "authority_preserved",
            "support_preserved",
            "conflict_preserved",
            "integrity_decision_preserved",
            "guard_disposition_preserved",
            "active_target_set_ownership_preserved",
            "external_authority_partition_preserved",
            "external_route_eligibility_preserved",
            "external_resolver_ownership_preserved",
        ):

            if trace.get(
                preservation_flag
            ) is not True:
                raise ClaimIntegrityConflictError(
                    "Trace preservation contract violated: "
                    f"{preservation_flag}"
                )

        evidence_trace = trace.get(
            "evidence_trace"
        )

        conflict_trace = trace.get(
            "conflict_trace"
        )

        authority_reference = trace.get(
            "authority_reference"
        )

        conflict_summary = trace.get(
            "conflict_summary"
        )

        relationship_counts = trace.get(
            "relationship_counts"
        )

        if not isinstance(
            evidence_trace,
            list,
        ):
            raise ClaimIntegrityConflictError(
                "evidence_trace must be a list."
            )

        if not isinstance(
            conflict_trace,
            list,
        ):
            raise ClaimIntegrityConflictError(
                "conflict_trace must be a list."
            )

        if not isinstance(
            authority_reference,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "authority_reference must be a dictionary."
            )

        if not isinstance(
            conflict_summary,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "conflict_summary must be a dictionary."
            )

        if not isinstance(
            relationship_counts,
            dict,
        ):
            raise ClaimIntegrityConflictError(
                "relationship_counts must be a dictionary."
            )

        final_core = {
            "schema":
                "final_claim_integrity_record_v1",

            "claim_id":
                claim_id,

            "claim_type":
                trace.get(
                    "claim_type"
                ),

            "claim_text":
                trace.get(
                    "claim_text"
                ),

            "authority_reference":
                copy.deepcopy(
                    authority_reference
                ),

            "support_state":
                trace.get(
                    "support_state"
                ),

            "support_balance":
                trace.get(
                    "support_balance"
                ),

            "relationship_counts":
                copy.deepcopy(
                    relationship_counts
                ),

            "evidence_trace":
                copy.deepcopy(
                    evidence_trace
                ),

            "conflict_trace":
                copy.deepcopy(
                    conflict_trace
                ),

            "conflict_summary":
                copy.deepcopy(
                    conflict_summary
                ),

            "claim_integrity_state":
                integrity_state,

            "integrity_decision_basis":
                trace.get(
                    "integrity_decision_basis"
                ),

            "guard_disposition":
                guard_disposition,

            "downstream_claim_eligible":
                downstream_eligible,

            "operational_blocking_applied":
                trace.get(
                    "operational_blocking_applied"
                ),

            "operational_hold_applied":
                trace.get(
                    "operational_hold_applied"
                ),

            "caution_applied":
                trace.get(
                    "caution_applied"
                ),

            "provenance_trace_id":
                trace_id,

            "provenance_trace_digest":
                trace_digest,

            "authority_preserved":
                True,

            "support_preserved":
                True,

            "conflict_preserved":
                True,

            "integrity_decision_preserved":
                True,

            "guard_disposition_preserved":
                True,

            "provenance_preserved":
                True,

            "active_target_set_ownership_preserved":
                True,

            "external_authority_partition_preserved":
                True,

            "external_route_eligibility_preserved":
                True,

            "external_resolver_ownership_preserved":
                True,

            "authority_used_as_truth_proxy":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        }

        canonical = json.dumps(
            final_core,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        digest = hashlib.sha256(
            canonical.encode(
                "utf-8"
            )
        ).hexdigest()

        final_records.append(
            {
                **final_core,

                "final_claim_integrity_id":
                    f"claimintegrity:v1:{digest}",

                "final_claim_integrity_digest":
                    digest,
            }
        )

    return {
        "schema":
            "final_claim_integrity_result_v1",

        "claim_integrity_conflict_version":
            CLAIM_INTEGRITY_CONFLICT_VERSION,

        "phase":
            CLAIM_INTEGRITY_CONFLICT_PHASE,

        "patch":
            "4.6.25K",

        "status":
            "FINAL_CLAIM_INTEGRITY_RESULT_BUILT",

        "final_claim_integrity_record_count":
            len(final_records),

        "final_claim_integrity_records":
            final_records,

        "final_claim_integrity_package": {
            "schema":
                "final_claim_integrity_result_package_v1",

            "record_count":
                len(final_records),

            "final_policy":
                "CERTIFIED_CLAIM_INTEGRITY_RESULT_FOR_DOWNSTREAM_CONSUMPTION",

            "authority_preserved":
                True,

            "support_preserved":
                True,

            "conflict_preserved":
                True,

            "integrity_preserved":
                True,

            "guard_preserved":
                True,

            "provenance_preserved":
                True,

            "active_target_set_ownership_preserved":
                True,

            "external_authority_partition_preserved":
                True,

            "external_route_eligibility_preserved":
                True,

            "external_resolver_ownership_preserved":
                True,
        },

        "architecture":
            copy.deepcopy(
                trace_result.get(
                    "architecture"
                )
            ),

        "final_authority_package":
            copy.deepcopy(
                trace_result.get(
                    "final_authority_package"
                )
            ),

        "preservation_contract":
            copy.deepcopy(
                trace_result.get(
                    "preservation_contract"
                )
            ),

        "processing_boundaries": {
            "final_claim_integrity_result_built":
                True,

            "support_reassessment_performed":
                False,

            "conflict_redetection_performed":
                False,

            "conflict_reclassification_performed":
                False,

            "integrity_redecision_performed":
                False,

            "guard_redisposition_performed":
                False,

            "authority_used_as_truth_proxy":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "authority_guard_override_performed":
                False,

            "external_evidence_fetch_performed":
                False,

            "unsupported_claim_invention_performed":
                False,

            "unsupported_evidence_invention_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "policy":
            "CERTIFIED_FINAL_CLAIM_INTEGRITY_RESULT",

        "next":
            "full_claim_integrity_conflict_hard_certification",
    }
