"""
LinkCraftor Semantic Intelligence
Phase 4.6.24 ? Authority Intelligence

Patch 4.6.24A:
Certified 4.6.23K Input Contract Inspection.

Authority Intelligence is downstream of certified Transfer Learning.

This module must not:
- modify Transfer Learning outcomes,
- silently promote conditional or blocked transfers,
- write Semantic Memory,
- make linking decisions,
- perform Authority scoring before its assigned stage.
"""

from __future__ import annotations
import copy

import hashlib
import json

from copy import deepcopy
from typing import Any


AUTHORITY_INTELLIGENCE_VERSION = "authority_intelligence_v1"
AUTHORITY_INTELLIGENCE_PHASE = "4.6.24"


class AuthorityIntelligenceError(ValueError):
    """Raised when an Authority Intelligence contract is violated."""


def inspect_certified_transfer_learning_input_v1(
    certified_transfer_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Inspect and bind the certified 4.6.23K Transfer Learning result.

    This is an input-contract inspection only.

    No Authority evaluation, scoring, external authority lookup,
    Semantic Memory write, or linking decision is performed.
    """

    if not isinstance(
        certified_transfer_result,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "certified_transfer_result must be a dict."
        )

    # -------------------------------------------------------------
    # Exact 4.6.23K lifecycle
    # -------------------------------------------------------------

    expected_top = {
        "schema_version":
            "certified_transfer_learning_result_v1",

        "version":
            "transfer_learning_v1",

        "phase":
            "4.6.23",

        "patch":
            "4.6.23K",

        "status":
            "TRANSFER_LEARNING_CERTIFIED",

        "transfer_policy":
            "FULL_TRANSFER_LEARNING_CERTIFIED",

        "next_stage":
            "authority",
    }

    for field, expected in expected_top.items():

        if certified_transfer_result.get(
            field
        ) != expected:
            raise AuthorityIntelligenceError(
                f"Invalid certified Transfer Learning field: {field}"
            )

    workspace_id = certified_transfer_result.get(
        "workspace_id"
    )

    certified_final = certified_transfer_result.get(
        "certified_final_transfer_learning_result"
    )

    certification = certified_transfer_result.get(
        "full_transfer_learning_certification"
    )

    source_final_envelope = certified_transfer_result.get(
        "source_final_result_envelope"
    )

    boundaries = certified_transfer_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "certified_final_transfer_learning_result",
            certified_final,
        ),
        (
            "full_transfer_learning_certification",
            certification,
        ),
        (
            "source_final_result_envelope",
            source_final_envelope,
        ),
        (
            "processing_boundaries",
            boundaries,
        ),
    ):

        if not isinstance(
            value,
            dict,
        ):
            raise AuthorityIntelligenceError(
                name + " is missing or invalid."
            )

    if not isinstance(
        workspace_id,
        str,
    ) or not workspace_id:
        raise AuthorityIntelligenceError(
            "workspace_id is required."
        )

    # -------------------------------------------------------------
    # Certified final-result contract
    # -------------------------------------------------------------

    for field, expected in (
        (
            "final_result_schema",
            "final_transfer_learning_result_v1",
        ),
        (
            "final_result_version",
            "v1",
        ),
        (
            "full_transfer_learning_certified",
            True,
        ),
        (
            "certification_status",
            "CERTIFIED",
        ),
        (
            "certification_patch",
            "4.6.23K",
        ),
        (
            "next_owner",
            "4.6.24_AUTHORITY",
        ),
        (
            "dynamic_semantic_graph_owner",
            "4.6.26_DYNAMIC_SEMANTIC_GRAPH",
        ),
        (
            "learning_engine_owner",
            "4.6.27_LEARNING_ENGINE",
        ),
        (
            "semantic_memory_owner",
            "4.6.28_SEMANTIC_MEMORY",
        ),
    ):

        if certified_final.get(
            field
        ) != expected:
            raise AuthorityIntelligenceError(
                f"Certified final Transfer Learning contract drifted: {field}"
            )

    if certified_final.get(
        "workspace_id"
    ) != workspace_id:
        raise AuthorityIntelligenceError(
            "Certified final workspace binding drifted."
        )

    # -------------------------------------------------------------
    # Transfer outcome containers
    # -------------------------------------------------------------

    approved = certified_final.get(
        "approved_transfers"
    )

    conditional = certified_final.get(
        "conditionally_approved_transfers"
    )

    blocked = certified_final.get(
        "blocked_transfers"
    )

    restricted = certified_final.get(
        "restricted_transfers"
    )

    for name, value in (
        (
            "approved_transfers",
            approved,
        ),
        (
            "conditionally_approved_transfers",
            conditional,
        ),
        (
            "blocked_transfers",
            blocked,
        ),
        (
            "restricted_transfers",
            restricted,
        ),
    ):

        if not isinstance(
            value,
            list,
        ):
            raise AuthorityIntelligenceError(
                name + " must be a list."
            )

    if certified_final.get(
        "approved_transfer_count"
    ) != len(
        approved
    ):
        raise AuthorityIntelligenceError(
            "Approved transfer count drifted."
        )

    if certified_final.get(
        "conditionally_approved_transfer_count"
    ) != len(
        conditional
    ):
        raise AuthorityIntelligenceError(
            "Conditional transfer count drifted."
        )

    if certified_final.get(
        "blocked_transfer_count"
    ) != len(
        blocked
    ):
        raise AuthorityIntelligenceError(
            "Blocked transfer count drifted."
        )

    if certified_final.get(
        "restricted_transfer_trace_count"
    ) != len(
        restricted
    ):
        raise AuthorityIntelligenceError(
            "Restricted transfer count drifted."
        )

    if certified_final.get(
        "transfer_trace_count"
    ) != (
        len(
            approved
        )
        + len(
            conditional
        )
        + len(
            blocked
        )
    ):
        raise AuthorityIntelligenceError(
            "Total Transfer Learning trace count drifted."
        )

    # -------------------------------------------------------------
    # Outcome semantics
    # -------------------------------------------------------------

    for item in approved:

        if not isinstance(
            item,
            dict,
        ):
            raise AuthorityIntelligenceError(
                "Invalid approved transfer record."
            )

        if item.get(
            "negative_transfer_guard_decision"
        ) != "APPROVED":
            raise AuthorityIntelligenceError(
                "Approved transfer decision drifted."
            )

        if item.get(
            "final_transfer_approved"
        ) is not True:
            raise AuthorityIntelligenceError(
                "Approved transfer is not finally approved."
            )

        if item.get(
            "provenance_complete"
        ) is not True:
            raise AuthorityIntelligenceError(
                "Approved transfer lacks complete provenance."
            )

    for item in conditional:

        if not isinstance(
            item,
            dict,
        ):
            raise AuthorityIntelligenceError(
                "Invalid conditional transfer record."
            )

        if item.get(
            "negative_transfer_guard_decision"
        ) != "CONDITIONALLY_APPROVED":
            raise AuthorityIntelligenceError(
                "Conditional transfer decision drifted."
            )

        if item.get(
            "final_transfer_approved"
        ) is not False:
            raise AuthorityIntelligenceError(
                "Conditional transfer cannot already be finally approved."
            )

    for item in blocked:

        if not isinstance(
            item,
            dict,
        ):
            raise AuthorityIntelligenceError(
                "Invalid blocked transfer record."
            )

        if item.get(
            "negative_transfer_guard_decision"
        ) != "BLOCKED":
            raise AuthorityIntelligenceError(
                "Blocked transfer decision drifted."
            )

        if item.get(
            "final_transfer_approved"
        ) is not False:
            raise AuthorityIntelligenceError(
                "Blocked transfer cannot be approved."
            )

    for item in restricted:

        if not isinstance(
            item,
            dict,
        ):
            raise AuthorityIntelligenceError(
                "Invalid restricted transfer record."
            )

        if item.get(
            "negative_transfer_guard_decision"
        ) != "BLOCKED":
            raise AuthorityIntelligenceError(
                "Restricted transfer must remain blocked."
            )

        if item.get(
            "final_transfer_approved"
        ) is not False:
            raise AuthorityIntelligenceError(
                "Restricted transfer cannot be approved."
            )

    # -------------------------------------------------------------
    # Certification package contract
    # -------------------------------------------------------------

    for field, expected in (
        (
            "certification_schema",
            "full_transfer_learning_certification_v1",
        ),
        (
            "certification_version",
            "v1",
        ),
        (
            "certification_phase",
            "4.6.23",
        ),
        (
            "certification_patch",
            "4.6.23K",
        ),
        (
            "certification_status",
            "CERTIFIED",
        ),
        (
            "certification_scope",
            "FULL_TRANSFER_LEARNING_PIPELINE",
        ),
        (
            "authority_ready",
            True,
        ),
        (
            "next_owner",
            "4.6.24_AUTHORITY",
        ),
    ):

        if certification.get(
            field
        ) != expected:
            raise AuthorityIntelligenceError(
                f"Transfer Learning certification drifted: {field}"
            )

    # -------------------------------------------------------------
    # Identity bindings
    # -------------------------------------------------------------

    for cert_field, final_field in (
        (
            "source_final_result_id",
            "final_result_id",
        ),
        (
            "source_final_result_digest",
            "final_result_digest",
        ),
        (
            "provenance_id",
            "provenance_id",
        ),
        (
            "provenance_digest",
            "provenance_digest",
        ),
        (
            "guard_id",
            "guard_id",
        ),
        (
            "guard_digest",
            "guard_digest",
        ),
        (
            "transfer_scope_id",
            "transfer_scope_id",
        ),
    ):

        if certification.get(
            cert_field
        ) != certified_final.get(
            final_field
        ):
            raise AuthorityIntelligenceError(
                f"Certification/final identity binding drifted: {cert_field}"
            )

    if certification.get(
        "certification_id"
    ) != certified_final.get(
        "certification_id"
    ):
        raise AuthorityIntelligenceError(
            "Certification ID binding drifted."
        )

    if certification.get(
        "certification_digest"
    ) != certified_final.get(
        "certification_digest"
    ):
        raise AuthorityIntelligenceError(
            "Certification digest binding drifted."
        )

    # -------------------------------------------------------------
    # Certification truth requirements
    # -------------------------------------------------------------

    for field in (
        "final_result_identity_verified",
        "final_result_digest_verified",
        "provenance_identity_verified",
        "guard_identity_verified",
        "transfer_scope_identity_verified",
        "outcome_counts_verified",
        "approved_transfer_integrity_verified",
        "conditional_transfer_integrity_verified",
        "blocked_transfer_integrity_verified",
        "restricted_transfer_integrity_verified",
        "transfer_integrity_verified",
        "negative_transfer_guard_verified",
        "transfer_provenance_verified",
        "source_ontology_preserved",
        "source_reasoning_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "authority_ready",
    ):

        if certification.get(
            field
        ) is not True:
            raise AuthorityIntelligenceError(
                f"Required Transfer Learning certification flag is not True: {field}"
            )

    for field in (
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if certification.get(
            field
        ) is not False:
            raise AuthorityIntelligenceError(
                f"Forbidden Transfer Learning certification flag is not False: {field}"
            )

    # -------------------------------------------------------------
    # K processing boundaries
    # -------------------------------------------------------------

    for field in (
        "certified_ontology_alignment_input_inspected",
        "certified_ontology_alignment_input_preserved",
        "ontology_alignment_integrity_preserved",
        "ontology_alignment_provenance_preserved",
        "alignment_outcomes_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "transfer_learning_architecture_defined",
        "transfer_learning_intake_validated",
        "transfer_scope_defined",
        "transfer_eligibility_evaluated",
        "transferable_knowledge_extracted",
        "knowledge_adaptation_performed",
        "transfer_learning_performed",
        "transfer_execution_provisional",
        "transfer_integrity_verification_performed",
        "negative_transfer_guard_performed",
        "transfer_provenance_built",
        "final_transfer_learning_result_built",
        "full_transfer_learning_certification_performed",
    ):

        if boundaries.get(
            field
        ) is not True:
            raise AuthorityIntelligenceError(
                f"Required certified Transfer Learning boundary is not True: {field}"
            )

    for field in (
        "source_ontology_alignment_modified",
        "source_reasoning_modified",
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(
            field
        ) is not False:
            raise AuthorityIntelligenceError(
                f"Forbidden certified Transfer Learning boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Authority-stage inspection result
    # -------------------------------------------------------------

    inspection = {
        "inspection_schema":
            "certified_transfer_learning_input_inspection_v1",

        "inspection_version":
            "v1",

        "workspace_id":
            workspace_id,

        "source_schema_version":
            certified_transfer_result[
                "schema_version"
            ],

        "source_phase":
            certified_transfer_result[
                "phase"
            ],

        "source_patch":
            certified_transfer_result[
                "patch"
            ],

        "source_status":
            certified_transfer_result[
                "status"
            ],

        "source_final_result_id":
            certified_final[
                "final_result_id"
            ],

        "source_final_result_digest":
            certified_final[
                "final_result_digest"
            ],

        "source_certification_id":
            certification[
                "certification_id"
            ],

        "source_certification_digest":
            certification[
                "certification_digest"
            ],

        "provenance_id":
            certified_final[
                "provenance_id"
            ],

        "guard_id":
            certified_final[
                "guard_id"
            ],

        "transfer_scope_id":
            certified_final[
                "transfer_scope_id"
            ],

        "approved_transfer_count":
            len(
                approved
            ),

        "conditionally_approved_transfer_count":
            len(
                conditional
            ),

        "blocked_transfer_count":
            len(
                blocked
            ),

        "restricted_transfer_count":
            len(
                restricted
            ),

        "certified_transfer_learning_verified":
            True,

        "transfer_outcomes_preserved":
            True,

        "transfer_provenance_preserved":
            True,

        "negative_transfer_guard_preserved":
            True,

        "authority_ready_verified":
            True,

        "authority_assessment_performed":
            False,

        "authority_scoring_performed":
            False,

        "external_authority_lookup_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "authority_input_inspection_result_v1",

        "version":
            AUTHORITY_INTELLIGENCE_VERSION,

        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,

        "patch":
            "4.6.24A",

        "status":
            "CERTIFIED_TRANSFER_LEARNING_INPUT_INSPECTED",

        "workspace_id":
            workspace_id,

        "inspection":
            inspection,

        "certified_final_transfer_learning_result":
            deepcopy(
                certified_final
            ),

        "full_transfer_learning_certification":
            deepcopy(
                certification
            ),

        "source_certified_transfer_learning_result":
            deepcopy(
                certified_transfer_result
            ),

        "processing_boundaries": {
            "certified_transfer_learning_input_inspected":
                True,

            "certified_transfer_learning_input_preserved":
                True,

            "transfer_outcomes_preserved":
                True,

            "transfer_integrity_preserved":
                True,

            "negative_transfer_guard_preserved":
                True,

            "transfer_provenance_preserved":
                True,

            "authority_architecture_defined":
                False,

            "authority_intake_validated":
                False,

            "authority_scope_defined":
                False,

            "authority_evidence_extracted":
                False,

            "source_authority_assessed":
                False,

            "authority_scoring_performed":
                False,

            "authority_integrity_guard_performed":
                False,

            "authority_provenance_built":
                False,

            "final_authority_result_built":
                False,

            "full_authority_certification_performed":
                False,

            "source_transfer_learning_modified":
                False,

            "external_authority_lookup_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "authority_policy":
            "CERTIFIED_TRANSFER_LEARNING_INPUT_ONLY",

        "next_stage":
            "authority_intelligence_architecture_definition",
    }


# =====================================================================
# PATCH 4.6.24B ? Authority Intelligence Architecture Definition
# =====================================================================

def define_authority_intelligence_architecture_v1(
    inspection_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Define the canonical Authority Intelligence architecture.

    B defines what Authority Intelligence is allowed to evaluate and
    what remains owned by surrounding LinkCraftor systems.

    No source is scored and no authority decision is made here.
    """

    if not isinstance(
        inspection_result,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "inspection_result must be a dict."
        )

    # -------------------------------------------------------------
    # Exact 4.6.24A lifecycle
    # -------------------------------------------------------------

    expected = {
        "schema_version":
            "authority_input_inspection_result_v1",

        "version":
            AUTHORITY_INTELLIGENCE_VERSION,

        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,

        "patch":
            "4.6.24A",

        "status":
            "CERTIFIED_TRANSFER_LEARNING_INPUT_INSPECTED",

        "authority_policy":
            "CERTIFIED_TRANSFER_LEARNING_INPUT_ONLY",

        "next_stage":
            "authority_intelligence_architecture_definition",
    }

    for field, value in expected.items():

        if inspection_result.get(
            field
        ) != value:
            raise AuthorityIntelligenceError(
                f"Invalid 4.6.24A lifecycle field: {field}"
            )

    workspace_id = inspection_result.get(
        "workspace_id"
    )

    inspection = inspection_result.get(
        "inspection"
    )

    boundaries = inspection_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        inspection,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "4.6.24A inspection package is missing."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "4.6.24A processing boundaries are missing."
        )

    if not isinstance(
        workspace_id,
        str,
    ) or not workspace_id:
        raise AuthorityIntelligenceError(
            "workspace_id is required."
        )

    # -------------------------------------------------------------
    # A inspection authority
    # -------------------------------------------------------------

    for field in (
        "certified_transfer_learning_verified",
        "transfer_outcomes_preserved",
        "transfer_provenance_preserved",
        "negative_transfer_guard_preserved",
        "authority_ready_verified",
    ):

        if inspection.get(
            field
        ) is not True:
            raise AuthorityIntelligenceError(
                f"Required inspection flag is not True: {field}"
            )

    for field in (
        "authority_assessment_performed",
        "authority_scoring_performed",
        "external_authority_lookup_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if inspection.get(
            field
        ) is not False:
            raise AuthorityIntelligenceError(
                f"Premature Authority action detected: {field}"
            )

    # -------------------------------------------------------------
    # A boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_transfer_learning_input_inspected",
        "certified_transfer_learning_input_preserved",
        "transfer_outcomes_preserved",
        "transfer_integrity_preserved",
        "negative_transfer_guard_preserved",
        "transfer_provenance_preserved",
    ):

        if boundaries.get(
            field
        ) is not True:
            raise AuthorityIntelligenceError(
                f"Required 4.6.24A boundary is not True: {field}"
            )

    for field in (
        "authority_architecture_defined",
        "authority_intake_validated",
        "authority_scope_defined",
        "authority_evidence_extracted",
        "source_authority_assessed",
        "authority_scoring_performed",
        "authority_integrity_guard_performed",
        "authority_provenance_built",
        "final_authority_result_built",
        "full_authority_certification_performed",
        "source_transfer_learning_modified",
        "external_authority_lookup_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(
            field
        ) is not False:
            raise AuthorityIntelligenceError(
                f"Forbidden 4.6.24A boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Canonical Authority architecture
    # -------------------------------------------------------------

    authority_subject_types = (
        "TRANSFERRED_KNOWLEDGE",
        "SOURCE",
        "EVIDENCE",
        "EXTERNAL_TARGET",
        "INTERNAL_DOCUMENT",
    )

    authority_dimensions = (
        "SOURCE_IDENTITY",
        "PRIMARY_SOURCE_STATUS",
        "INSTITUTIONAL_AUTHORITY",
        "DOMAIN_EXPERTISE",
        "EVIDENCE_QUALITY",
        "PROVENANCE_QUALITY",
        "TOPIC_APPLICABILITY",
        "RECENCY_APPLICABILITY",
        "SOURCE_INDEPENDENCE",
        "AUTHORITY_CONSISTENCY",
    )

    authority_source_classes = (
        "PRIMARY_OFFICIAL_SOURCE",
        "REGULATORY_OR_GOVERNMENT_SOURCE",
        "PROFESSIONAL_OR_STANDARDS_BODY",
        "ACADEMIC_OR_RESEARCH_SOURCE",
        "FIRST_PARTY_TECHNICAL_SOURCE",
        "INSTITUTIONAL_SOURCE",
        "EXPERT_SECONDARY_SOURCE",
        "GENERAL_SECONDARY_SOURCE",
        "COMMUNITY_SOURCE",
        "UNKNOWN_SOURCE",
    )

    authority_evidence_classes = (
        "PRIMARY_DOCUMENTATION",
        "REGULATORY_GUIDANCE",
        "STANDARD_OR_SPECIFICATION",
        "SYSTEMATIC_OR_SYNTHESIZED_EVIDENCE",
        "PEER_REVIEWED_RESEARCH",
        "OFFICIAL_DATA",
        "INSTITUTIONAL_GUIDANCE",
        "EXPERT_ANALYSIS",
        "SECONDARY_REPORTING",
        "COMMUNITY_DISCUSSION",
        "ANECDOTAL_OR_UNVERIFIED",
        "UNKNOWN_EVIDENCE",
    )

    authority_classes = (
        "VERY_HIGH",
        "HIGH",
        "MODERATE",
        "LOW",
        "VERY_LOW",
        "UNRESOLVED",
        "BLOCKED",
    )

    authority_confidence_classes = (
        "HIGH_CONFIDENCE",
        "MODERATE_CONFIDENCE",
        "LOW_CONFIDENCE",
        "INSUFFICIENT_EVIDENCE",
    )

    architecture = {
        "architecture_schema":
            "authority_intelligence_architecture_v1",

        "architecture_version":
            "v1",

        "workspace_id":
            workspace_id,

        "authority_subject_types":
            list(
                authority_subject_types
            ),

        "authority_dimensions":
            list(
                authority_dimensions
            ),

        "authority_source_classes":
            list(
                authority_source_classes
            ),

        "authority_evidence_classes":
            list(
                authority_evidence_classes
            ),

        "authority_classes":
            list(
                authority_classes
            ),

        "authority_confidence_classes":
            list(
                authority_confidence_classes
            ),

        "core_question":
            (
                "HOW_AUTHORITATIVE_IS_THE_SOURCE_OR_EVIDENCE_"
                "FOR_THIS_SPECIFIC_CONTEXT"
            ),

        "authority_is_contextual":
            True,

        "authority_is_domain_sensitive":
            True,

        "authority_is_evidence_bound":
            True,

        "authority_is_provenance_bound":
            True,

        "authority_is_not_truth_assessment":
            True,

        "authority_is_not_semantic_relevance":
            True,

        "authority_is_not_url_discovery":
            True,

        "authority_is_not_final_link_selection":
            True,

        "active_target_set_owns_candidate_targets":
            True,

        "authority_consumes_supplied_external_candidates":
            True,

        "authority_may_enrich_external_candidates":
            True,

        "external_resolver_owns_final_external_target_selection":
            True,

        "primary_source_preference_supported":
            True,

        "secondary_source_penalty_supported":
            True,

        "source_independence_analysis_supported":
            True,

        "domain_specific_authority_supported":
            True,

        "recency_applicability_supported":
            True,

        "authority_conflict_preserved":
            True,

        "unknown_authority_preserved":
            True,

        "authority_manipulation_guard_required":
            True,

        "source_transfer_learning_must_remain_immutable":
            True,

        "semantic_memory_write_allowed":
            False,

        "linking_decision_allowed":
            False,

        "external_url_discovery_allowed":
            False,

        "truth_adjudication_allowed":
            False,

        "silent_conflict_resolution_allowed":
            False,

        "unsupported_authority_invention_allowed":
            False,

        "owner":
            "4.6.24_AUTHORITY",

        "source_owner":
            "4.6.23_TRANSFER_LEARNING",

        "next_owner":
            "4.6.25_CLAIM_INTEGRITY_AND_CONFLICT",

        "dynamic_semantic_graph_owner":
            "4.6.26_DYNAMIC_SEMANTIC_GRAPH",

        "learning_engine_owner":
            "4.6.27_LEARNING_ENGINE",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",

        "explainability_owner":
            "4.6.29_EXPLAINABILITY",

        "active_target_set_owner":
            "ACTIVE_TARGET_SET",

        "external_target_partition":
            "EXTERNAL_AUTHORITY",

        "external_target_route_eligibility":
            "EXTERNAL",

        "external_resolver_owner":
            "EXTERNAL_TARGET_RESOLVER",

        "architecture_policy":
            "CONTEXTUAL_EVIDENCE_BOUND_AUTHORITY_EVALUATION_ONLY",
    }

    return {
        "architecture_question":
            "HOW_AUTHORITATIVE_IS_THE_SOURCE_OR_EVIDENCE_FOR_THIS_SPECIFIC_CONTEXT",

        "schema_version":
            "authority_architecture_definition_result_v1",

        "version":
            AUTHORITY_INTELLIGENCE_VERSION,

        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,

        "patch":
            "4.6.24B",

        "status":
            "AUTHORITY_INTELLIGENCE_ARCHITECTURE_DEFINED",

        "workspace_id":
            workspace_id,

        "authority_architecture":
            architecture,

        "source_inspection_result":
            deepcopy(
                inspection_result
            ),

        "processing_boundaries": {
            "certified_transfer_learning_input_inspected":
                True,

            "certified_transfer_learning_input_preserved":
                True,

            "transfer_outcomes_preserved":
                True,

            "transfer_integrity_preserved":
                True,

            "negative_transfer_guard_preserved":
                True,

            "transfer_provenance_preserved":
                True,

            "authority_architecture_defined":
                True,

            "authority_intake_validated":
                False,

            "authority_scope_defined":
                False,

            "authority_evidence_extracted":
                False,

            "source_authority_assessed":
                False,

            "authority_scoring_performed":
                False,

            "authority_integrity_guard_performed":
                False,

            "authority_provenance_built":
                False,

            "final_authority_result_built":
                False,

            "full_authority_certification_performed":
                False,

            "source_transfer_learning_modified":
                False,

            "external_authority_lookup_performed":
                False,

            "external_target_selected":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "authority_policy":
            "AUTHORITY_INTELLIGENCE_ARCHITECTURE_DEFINED",

        "next_stage":
            "authority_intake_validation",
    }


# =====================================================================
# PATCH 4.6.24C ? Authority Intake Validation
# =====================================================================

def validate_authority_intake_v1(
    architecture_result: dict[str, Any],
) -> dict[str, Any]:

    if not isinstance(
        architecture_result,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "architecture_result must be a dict."
        )

    expected = {
        "schema_version":
            "authority_architecture_definition_result_v1",
        "version":
            AUTHORITY_INTELLIGENCE_VERSION,
        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,
        "patch":
            "4.6.24B",
        "status":
            "AUTHORITY_INTELLIGENCE_ARCHITECTURE_DEFINED",
        "authority_policy":
            "AUTHORITY_INTELLIGENCE_ARCHITECTURE_DEFINED",
        "next_stage":
            "authority_intake_validation",
    }

    for field, value in expected.items():

        if architecture_result.get(field) != value:
            raise AuthorityIntelligenceError(
                f"Invalid 4.6.24B lifecycle field: {field}"
            )

    workspace_id = architecture_result.get(
        "workspace_id"
    )

    architecture = architecture_result.get(
        "authority_architecture"
    )

    source_inspection = architecture_result.get(
        "source_inspection_result"
    )

    boundaries = architecture_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("authority_architecture", architecture),
        ("source_inspection_result", source_inspection),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(value, dict):
            raise AuthorityIntelligenceError(
                name + " is missing or invalid."
            )

    if not isinstance(
        workspace_id,
        str,
    ) or not workspace_id:
        raise AuthorityIntelligenceError(
            "workspace_id is required."
        )

    if architecture.get(
        "architecture_schema"
    ) != "authority_intelligence_architecture_v1":
        raise AuthorityIntelligenceError(
            "Authority architecture schema drifted."
        )

    if architecture.get(
        "architecture_version"
    ) != "v1":
        raise AuthorityIntelligenceError(
            "Authority architecture version drifted."
        )

    if architecture.get(
        "workspace_id"
    ) != workspace_id:
        raise AuthorityIntelligenceError(
            "Authority workspace drifted."
        )

    required_subjects = {
        "TRANSFERRED_KNOWLEDGE",
        "SOURCE",
        "EVIDENCE",
        "EXTERNAL_TARGET",
        "INTERNAL_DOCUMENT",
    }

    if set(
        architecture.get(
            "authority_subject_types",
            [],
        )
    ) != required_subjects:
        raise AuthorityIntelligenceError(
            "Authority subject contract drifted."
        )

    required_dimensions = {
        "SOURCE_IDENTITY",
        "PRIMARY_SOURCE_STATUS",
        "INSTITUTIONAL_AUTHORITY",
        "DOMAIN_EXPERTISE",
        "EVIDENCE_QUALITY",
        "PROVENANCE_QUALITY",
        "TOPIC_APPLICABILITY",
        "RECENCY_APPLICABILITY",
        "SOURCE_INDEPENDENCE",
        "AUTHORITY_CONSISTENCY",
    }

    if set(
        architecture.get(
            "authority_dimensions",
            [],
        )
    ) != required_dimensions:
        raise AuthorityIntelligenceError(
            "Authority dimension contract drifted."
        )

    for field in (
        "authority_is_contextual",
        "authority_is_domain_sensitive",
        "authority_is_evidence_bound",
        "authority_is_provenance_bound",
        "authority_is_not_truth_assessment",
        "authority_is_not_semantic_relevance",
        "authority_is_not_url_discovery",
        "authority_is_not_final_link_selection",
        "active_target_set_owns_candidate_targets",
        "authority_consumes_supplied_external_candidates",
        "authority_may_enrich_external_candidates",
        "external_resolver_owns_final_external_target_selection",
        "primary_source_preference_supported",
        "secondary_source_penalty_supported",
        "source_independence_analysis_supported",
        "domain_specific_authority_supported",
        "recency_applicability_supported",
        "authority_conflict_preserved",
        "unknown_authority_preserved",
        "authority_manipulation_guard_required",
        "source_transfer_learning_must_remain_immutable",
    ):

        if architecture.get(field) is not True:
            raise AuthorityIntelligenceError(
                f"Required architecture flag false: {field}"
            )

    for field in (
        "semantic_memory_write_allowed",
        "linking_decision_allowed",
        "external_url_discovery_allowed",
        "truth_adjudication_allowed",
        "silent_conflict_resolution_allowed",
        "unsupported_authority_invention_allowed",
    ):

        if architecture.get(field) is not False:
            raise AuthorityIntelligenceError(
                f"Forbidden architecture permission true: {field}"
            )

    owners = {
        "owner":
            "4.6.24_AUTHORITY",
        "source_owner":
            "4.6.23_TRANSFER_LEARNING",
        "next_owner":
            "4.6.25_CLAIM_INTEGRITY_AND_CONFLICT",
        "dynamic_semantic_graph_owner":
            "4.6.26_DYNAMIC_SEMANTIC_GRAPH",
        "learning_engine_owner":
            "4.6.27_LEARNING_ENGINE",
        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",
        "explainability_owner":
            "4.6.29_EXPLAINABILITY",
        "active_target_set_owner":
            "ACTIVE_TARGET_SET",

        "external_target_partition":
            "EXTERNAL_AUTHORITY",

        "external_target_route_eligibility":
            "EXTERNAL",
        "external_resolver_owner":
            "EXTERNAL_TARGET_RESOLVER",
    }

    for field, expected_value in owners.items():

        if architecture.get(field) != expected_value:
            raise AuthorityIntelligenceError(
                f"Authority ownership drifted: {field}"
            )

    for field in (
        "certified_transfer_learning_input_inspected",
        "certified_transfer_learning_input_preserved",
        "transfer_outcomes_preserved",
        "transfer_integrity_preserved",
        "negative_transfer_guard_preserved",
        "transfer_provenance_preserved",
        "authority_architecture_defined",
    ):

        if boundaries.get(field) is not True:
            raise AuthorityIntelligenceError(
                f"Required B boundary false: {field}"
            )

    for field in (
        "authority_intake_validated",
        "authority_scope_defined",
        "authority_evidence_extracted",
        "source_authority_assessed",
        "authority_scoring_performed",
        "authority_integrity_guard_performed",
        "authority_provenance_built",
        "final_authority_result_built",
        "full_authority_certification_performed",
        "source_transfer_learning_modified",
        "external_authority_lookup_performed",
        "external_target_selected",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise AuthorityIntelligenceError(
                f"Forbidden B boundary true: {field}"
            )

    if source_inspection.get(
        "schema_version"
    ) != "authority_input_inspection_result_v1":
        raise AuthorityIntelligenceError(
            "Embedded A schema drifted."
        )

    if source_inspection.get(
        "patch"
    ) != "4.6.24A":
        raise AuthorityIntelligenceError(
            "Embedded A patch drifted."
        )

    if source_inspection.get(
        "status"
    ) != "CERTIFIED_TRANSFER_LEARNING_INPUT_INSPECTED":
        raise AuthorityIntelligenceError(
            "Embedded A status drifted."
        )

    if source_inspection.get(
        "workspace_id"
    ) != workspace_id:
        raise AuthorityIntelligenceError(
            "Embedded A workspace drifted."
        )

    intake = {
        "intake_schema":
            "authority_intake_validation_v1",
        "intake_version":
            "v1",
        "workspace_id":
            workspace_id,
        "authority_architecture_verified":
            True,
        "authority_subject_contract_verified":
            True,
        "authority_dimension_contract_verified":
            True,
        "authority_ownership_verified":
            True,
        "external_target_ownership_verified":
            True,
        "external_resolver_ownership_verified":
            True,
        "transfer_learning_preserved":
            True,
        "negative_transfer_guard_preserved":
            True,
        "transfer_provenance_preserved":
            True,
        "authority_evaluation_ready":
            True,
        "authority_scope_defined":
            False,
        "authority_evidence_extracted":
            False,
        "source_authority_assessed":
            False,
        "authority_scoring_performed":
            False,
        "external_authority_lookup_performed":
            False,
        "external_target_selected":
            False,
        "semantic_memory_written":
            False,
        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "authority_intake_validation_result_v1",
        "version":
            AUTHORITY_INTELLIGENCE_VERSION,
        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,
        "patch":
            "4.6.24C",
        "status":
            "AUTHORITY_INTAKE_VALIDATED",
        "workspace_id":
            workspace_id,
        "authority_intake":
            intake,
        "authority_architecture":
            deepcopy(architecture),
        "source_architecture_result":
            deepcopy(architecture_result),
        "processing_boundaries": {
            **deepcopy(boundaries),
            "authority_intake_validated":
                True,
        },
        "authority_policy":
            "CERTIFIED_AUTHORITY_INTAKE_VALIDATED",
        "next_stage":
            "authority_scope_and_evaluation_contract",
    }


# =====================================================================
# PATCH 4.6.24D ? Authority Scope & Evaluation Contract
# =====================================================================

def define_authority_scope_and_evaluation_contract_v1(
    intake_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Define the certified Authority evaluation scope.

    D defines:
    - what may be evaluated,
    - which dimensions must be considered,
    - how external targets enter Authority,
    - which subjects remain blocked or unresolved,
    - what downstream stages still own.

    No authority scoring or classification is performed here.
    """

    if not isinstance(
        intake_result,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "intake_result must be a dict."
        )

    expected = {
        "schema_version":
            "authority_intake_validation_result_v1",
        "version":
            AUTHORITY_INTELLIGENCE_VERSION,
        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,
        "patch":
            "4.6.24C",
        "status":
            "AUTHORITY_INTAKE_VALIDATED",
        "authority_policy":
            "CERTIFIED_AUTHORITY_INTAKE_VALIDATED",
        "next_stage":
            "authority_scope_and_evaluation_contract",
    }

    for field, value in expected.items():

        if intake_result.get(
            field
        ) != value:
            raise AuthorityIntelligenceError(
                f"Invalid 4.6.24C lifecycle field: {field}"
            )

    workspace_id = intake_result.get(
        "workspace_id"
    )

    intake = intake_result.get(
        "authority_intake"
    )

    architecture = intake_result.get(
        "authority_architecture"
    )

    boundaries = intake_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("authority_intake", intake),
        ("authority_architecture", architecture),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            dict,
        ):
            raise AuthorityIntelligenceError(
                name + " is missing or invalid."
            )

    if not isinstance(
        workspace_id,
        str,
    ) or not workspace_id:
        raise AuthorityIntelligenceError(
            "workspace_id is required."
        )

    if intake.get(
        "workspace_id"
    ) != workspace_id:
        raise AuthorityIntelligenceError(
            "Authority intake workspace drifted."
        )

    for field in (
        "authority_architecture_verified",
        "authority_subject_contract_verified",
        "authority_dimension_contract_verified",
        "authority_ownership_verified",
        "external_target_ownership_verified",
        "external_resolver_ownership_verified",
        "transfer_learning_preserved",
        "negative_transfer_guard_preserved",
        "transfer_provenance_preserved",
        "authority_evaluation_ready",
    ):

        if intake.get(
            field
        ) is not True:
            raise AuthorityIntelligenceError(
                f"Required Authority intake flag is not True: {field}"
            )

    for field in (
        "authority_scope_defined",
        "authority_evidence_extracted",
        "source_authority_assessed",
        "authority_scoring_performed",
        "external_authority_lookup_performed",
        "external_target_selected",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if intake.get(
            field
        ) is not False:
            raise AuthorityIntelligenceError(
                f"Premature Authority intake action detected: {field}"
            )

    required_subject_types = (
        "TRANSFERRED_KNOWLEDGE",
        "SOURCE",
        "EVIDENCE",
        "EXTERNAL_TARGET",
        "INTERNAL_DOCUMENT",
    )

    actual_subject_types = tuple(
        architecture.get(
            "authority_subject_types",
            [],
        )
    )

    if set(
        actual_subject_types
    ) != set(
        required_subject_types
    ):
        raise AuthorityIntelligenceError(
            "Authority subject types drifted."
        )

    required_dimensions = (
        "SOURCE_IDENTITY",
        "PRIMARY_SOURCE_STATUS",
        "INSTITUTIONAL_AUTHORITY",
        "DOMAIN_EXPERTISE",
        "EVIDENCE_QUALITY",
        "PROVENANCE_QUALITY",
        "TOPIC_APPLICABILITY",
        "RECENCY_APPLICABILITY",
        "SOURCE_INDEPENDENCE",
        "AUTHORITY_CONSISTENCY",
    )

    actual_dimensions = tuple(
        architecture.get(
            "authority_dimensions",
            [],
        )
    )

    if set(
        actual_dimensions
    ) != set(
        required_dimensions
    ):
        raise AuthorityIntelligenceError(
            "Authority evaluation dimensions drifted."
        )

    # -------------------------------------------------------------
    # Scope definitions
    # -------------------------------------------------------------

    scope_subject_rules = {
        "TRANSFERRED_KNOWLEDGE": {
            "eligible":
                True,
            "requires_certified_transfer_provenance":
                True,
            "requires_negative_transfer_guard":
                True,
            "may_modify_transfer_decision":
                False,
        },

        "SOURCE": {
            "eligible":
                True,
            "requires_source_identity":
                True,
            "requires_context":
                True,
            "truth_assessment_allowed":
                False,
        },

        "EVIDENCE": {
            "eligible":
                True,
            "requires_provenance":
                True,
            "requires_context":
                True,
            "claim_integrity_decision_allowed":
                False,
        },

        "EXTERNAL_TARGET": {
            "eligible":
                True,
            "must_be_supplied_by_active_target_set":
                True,
            "authority_may_discover_url":
                False,

            "authority_may_create_target":
                False,

            "authority_may_select_final_target":
                False,

            "semantic_memory_write_allowed":
                False,
            "authority_may_select_final_url":
                False,
            "external_resolver_owns_selection":
                True,
        },

        "INTERNAL_DOCUMENT": {
            "eligible":
                True,
            "requires_workspace_context":
                True,
            "may_be_used_for_internal_authority_assessment":
                True,
            "linking_decision_allowed":
                False,
        },
    }

    eligibility_classes = (
        "ELIGIBLE",
        "CONDITIONALLY_ELIGIBLE",
        "BLOCKED",
        "UNRESOLVED",
    )

    evaluation_requirements = {
        "all_subjects_require_context":
            True,

        "all_subjects_require_provenance_where_available":
            True,

        "authority_must_be_domain_sensitive":
            True,

        "authority_must_be_topic_sensitive":
            True,

        "authority_must_preserve_unknowns":
            True,

        "authority_must_preserve_conflicts":
            True,

        "authority_must_not_invent_missing_evidence":
            True,

        "authority_must_not_convert_relevance_into_authority":
            True,

        "authority_must_not_convert_popularity_into_authority":
            True,

        "authority_must_not_convert_domain_metrics_into_truth":
            True,

        "authority_must_not_use_url_presence_as_authority":
            True,

        "authority_must_not_override_claim_integrity":
            True,

        "authority_must_not_override_external_resolver":
            True,

        "authority_must_not_write_semantic_memory":
            True,
    }

    external_target_contract = {
        "candidate_target_owner":
            "ACTIVE_TARGET_SET",

        "required_target_partition":
            "EXTERNAL_AUTHORITY",

        "required_route_eligibility":
            "EXTERNAL",

        "authority_role":
            "EVALUATE_AND_ENRICH_SUPPLIED_CANDIDATE",

        "authority_url_discovery_allowed":
            False,

        "authority_candidate_creation_allowed":
            False,

        "authority_final_target_selection_allowed":
            False,

        "final_selection_owner":
            "EXTERNAL_TARGET_RESOLVER",

        "authority_metadata_may_be_attached":
            True,

        "authority_metadata_may_be_consumed_by_resolver":
            True,
    }

    scope_material = {
        "workspace_id":
            workspace_id,

        "subject_types":
            list(
                required_subject_types
            ),

        "dimensions":
            list(
                required_dimensions
            ),

        "eligibility_classes":
            list(
                eligibility_classes
            ),

        "scope_subject_rules":
            scope_subject_rules,

        "evaluation_requirements":
            evaluation_requirements,

        "external_target_contract":
            external_target_contract,
    }

    scope_digest = hashlib.sha256(
        json.dumps(
            scope_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    authority_scope = {
        "scope_schema":
            "authority_scope_and_evaluation_contract_v1",

        "scope_version":
            "v1",

        "scope_id":
            "authscope:v1:"
            + scope_digest,

        "scope_digest":
            scope_digest,

        "workspace_id":
            workspace_id,

        "authority_subject_types":
            list(
                required_subject_types
            ),

        "authority_dimensions":
            list(
                required_dimensions
            ),

        "eligibility_classes":
            list(
                eligibility_classes
            ),

        "scope_subject_rules":
            deepcopy(
                scope_subject_rules
            ),

        "evaluation_requirements":
            deepcopy(
                evaluation_requirements
            ),

        "external_target_contract":
            deepcopy(
                external_target_contract
            ),

        "authority_scope_defined":
            True,

        "authority_evidence_extracted":
            False,

        "authority_assessment_performed":
            False,

        "authority_scoring_performed":
            False,

        "authority_classification_performed":
            False,

        "authority_integrity_guard_performed":
            False,

        "external_authority_lookup_performed":
            False,

        "external_target_selected":
            False,

        "truth_assessment_performed":
            False,

        "claim_integrity_decision_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "owner":
            "4.6.24_AUTHORITY",

        "next_owner":
            "4.6.25_CLAIM_INTEGRITY_AND_CONFLICT",

        "active_target_set_owner":
            "ACTIVE_TARGET_SET",

        "external_target_partition":
            "EXTERNAL_AUTHORITY",

        "external_target_route_eligibility":
            "EXTERNAL",

        "external_resolver_owner":
            "EXTERNAL_TARGET_RESOLVER",

        "scope_policy":
            "CONTEXTUAL_EVIDENCE_BOUND_AUTHORITY_SCOPE_ONLY",
    }

    return {
        "schema_version":
            "authority_scope_evaluation_contract_result_v1",

        "version":
            AUTHORITY_INTELLIGENCE_VERSION,

        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,

        "patch":
            "4.6.24D",

        "status":
            "AUTHORITY_SCOPE_AND_EVALUATION_CONTRACT_DEFINED",

        "workspace_id":
            workspace_id,

        "authority_scope":
            authority_scope,

        "authority_intake":
            deepcopy(
                intake
            ),

        "authority_architecture":
            deepcopy(
                architecture
            ),

        "source_intake_result":
            deepcopy(
                intake_result
            ),

        "processing_boundaries": {
            **deepcopy(
                boundaries
            ),

            "authority_scope_defined":
                True,
        },

        "authority_policy":
            "CERTIFIED_AUTHORITY_SCOPE_DEFINED",

        "next_stage":
            "authority_evidence_extraction",
    }


# =====================================================================
# PATCH 4.6.24E ? Authority Evidence Extraction
# =====================================================================

def extract_authority_evidence_v1(
    scope_result: dict[str, Any],
    authority_subjects: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Extract authority-relevant evidence from supplied Authority subjects.

    Important:
    - External URLs must already be supplied by Active Target Set.
    - No web lookup or URL discovery is performed.
    - No authority score/classification is produced.
    - Missing evidence remains missing/unresolved.
    """

    if not isinstance(
        scope_result,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "scope_result must be a dict."
        )

    if not isinstance(
        authority_subjects,
        list,
    ):
        raise AuthorityIntelligenceError(
            "authority_subjects must be a list."
        )

    expected = {
        "schema_version":
            "authority_scope_evaluation_contract_result_v1",
        "version":
            AUTHORITY_INTELLIGENCE_VERSION,
        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,
        "patch":
            "4.6.24D",
        "status":
            "AUTHORITY_SCOPE_AND_EVALUATION_CONTRACT_DEFINED",
        "authority_policy":
            "CERTIFIED_AUTHORITY_SCOPE_DEFINED",
        "next_stage":
            "authority_evidence_extraction",
    }

    for field, value in expected.items():

        if scope_result.get(
            field
        ) != value:
            raise AuthorityIntelligenceError(
                f"Invalid 4.6.24D lifecycle field: {field}"
            )

    workspace_id = scope_result.get(
        "workspace_id"
    )

    scope = scope_result.get(
        "authority_scope"
    )

    boundaries = scope_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        scope,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "authority_scope is missing or invalid."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "processing_boundaries are missing or invalid."
        )

    if scope.get(
        "authority_scope_defined"
    ) is not True:
        raise AuthorityIntelligenceError(
            "Authority scope has not been defined."
        )

    for field in (
        "authority_evidence_extracted",
        "authority_assessment_performed",
        "authority_scoring_performed",
        "authority_classification_performed",
        "authority_integrity_guard_performed",
        "external_authority_lookup_performed",
        "external_target_selected",
        "truth_assessment_performed",
        "claim_integrity_decision_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if scope.get(
            field
        ) is not False:
            raise AuthorityIntelligenceError(
                f"Premature Authority operation detected: {field}"
            )

    allowed_subject_types = set(
        scope.get(
            "authority_subject_types",
            [],
        )
    )

    required_dimensions = list(
        scope.get(
            "authority_dimensions",
            [],
        )
    )

    if not allowed_subject_types:
        raise AuthorityIntelligenceError(
            "Authority subject contract is empty."
        )

    if len(
        required_dimensions
    ) != 10:
        raise AuthorityIntelligenceError(
            "Authority dimension contract drifted."
        )

    extracted_records = []
    unresolved_records = []

    seen_subject_ids = set()

    evidence_field_map = {
        "SOURCE_IDENTITY":
            "source_identity",

        "PRIMARY_SOURCE_STATUS":
            "primary_source_status",

        "INSTITUTIONAL_AUTHORITY":
            "institutional_authority",

        "DOMAIN_EXPERTISE":
            "domain_expertise",

        "EVIDENCE_QUALITY":
            "evidence_quality",

        "PROVENANCE_QUALITY":
            "provenance_quality",

        "TOPIC_APPLICABILITY":
            "topic_applicability",

        "RECENCY_APPLICABILITY":
            "recency_applicability",

        "SOURCE_INDEPENDENCE":
            "source_independence",

        "AUTHORITY_CONSISTENCY":
            "authority_consistency",
    }

    for index, subject in enumerate(
        authority_subjects
    ):

        if not isinstance(
            subject,
            dict,
        ):
            raise AuthorityIntelligenceError(
                f"Authority subject at index {index} must be a dict."
            )

        subject_id = subject.get(
            "subject_id"
        )

        subject_type = subject.get(
            "subject_type"
        )

        if not isinstance(
            subject_id,
            str,
        ) or not subject_id.strip():
            raise AuthorityIntelligenceError(
                f"Authority subject at index {index} lacks subject_id."
            )

        if subject_id in seen_subject_ids:
            raise AuthorityIntelligenceError(
                f"Duplicate authority subject_id: {subject_id}"
            )

        seen_subject_ids.add(
            subject_id
        )

        if subject_type not in allowed_subject_types:
            raise AuthorityIntelligenceError(
                f"Unsupported authority subject_type: {subject_type}"
            )

        if subject.get(
            "workspace_id"
        ) != workspace_id:
            raise AuthorityIntelligenceError(
                f"Authority subject workspace drifted: {subject_id}"
            )

        context = subject.get(
            "context"
        )

        if not isinstance(
            context,
            dict,
        ) or not context:
            raise AuthorityIntelligenceError(
                f"Authority subject lacks context: {subject_id}"
            )

        if subject_type == "EXTERNAL_TARGET":

            if subject.get(
                "candidate_target_owner"
            ) != "ACTIVE_TARGET_SET":
                raise AuthorityIntelligenceError(
                    "External target was not supplied by Active Target Set."
                )

            candidate_url = subject.get(
                "candidate_url"
            )

            if not isinstance(
                candidate_url,
                str,
            ) or not candidate_url.strip():
                raise AuthorityIntelligenceError(
                    "External target candidate_url is required."
                )

        if subject_type == "EXTERNAL_TARGET":

            if subject.get(
                "target_partition"
            ) != "EXTERNAL_AUTHORITY":
                raise AuthorityIntelligenceError(
                    "External Authority target must come from "
                    "the EXTERNAL_AUTHORITY partition of the "
                    "Active Target Set."
                )

            route_eligibility = subject.get(
                "route_eligibility"
            )

            if isinstance(
                route_eligibility,
                str,
            ):
                external_route_eligible = (
                    route_eligibility
                    == "EXTERNAL"
                )

            elif isinstance(
                route_eligibility,
                (
                    list,
                    tuple,
                    set,
                ),
            ):
                external_route_eligible = (
                    "EXTERNAL"
                    in route_eligibility
                )

            else:
                external_route_eligible = False

            if not external_route_eligible:
                raise AuthorityIntelligenceError(
                    "External Authority target must be "
                    "EXTERNAL-route eligible."
                )

        supplied_evidence = subject.get(
            "authority_evidence",
            {}
        )

        if not isinstance(
            supplied_evidence,
            dict,
        ):
            raise AuthorityIntelligenceError(
                f"authority_evidence must be a dict: {subject_id}"
            )

        dimension_evidence = {}

        present_dimensions = []
        missing_dimensions = []

        for dimension in required_dimensions:

            source_field = evidence_field_map[
                dimension
            ]

            value = supplied_evidence.get(
                source_field
            )

            present = (
                value is not None
                and value != ""
                and value != []
                and value != {}
            )

            dimension_evidence[
                dimension
            ] = {
                "source_field":
                    source_field,

                "evidence_present":
                    present,

                "evidence_value":
                    deepcopy(
                        value
                    ) if present else None,

                "evidence_invented":
                    False,
            }

            if present:
                present_dimensions.append(
                    dimension
                )
            else:
                missing_dimensions.append(
                    dimension
                )

        provenance = subject.get(
            "provenance"
        )

        provenance_present = (
            isinstance(
                provenance,
                dict,
            )
            and bool(
                provenance
            )
        )

        source_url = subject.get(
            "candidate_url"
        ) if subject_type == "EXTERNAL_TARGET" else subject.get(
            "source_url"
        )

        record_material = {
            "workspace_id":
                workspace_id,

            "subject_id":
                subject_id,

            "subject_type":
                subject_type,

            "source_url":
                source_url,

            "context":
                context,

            "dimension_evidence":
                dimension_evidence,

            "provenance":
                provenance if provenance_present else None,
        }

        record_digest = hashlib.sha256(
            json.dumps(
                record_material,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        eligibility = (
            "ELIGIBLE"
            if provenance_present
            and len(
                present_dimensions
            ) >= 5
            else
            "CONDITIONALLY_ELIGIBLE"
            if provenance_present
            or len(
                present_dimensions
            ) >= 3
            else
            "UNRESOLVED"
        )

        record = {
            "evidence_record_schema":
                "authority_evidence_record_v1",

            "evidence_record_id":
                "authevidence:v1:"
                + record_digest,

            "evidence_record_digest":
                record_digest,

            "workspace_id":
                workspace_id,

            "subject_id":
                subject_id,

            "subject_type":
                subject_type,

            "source_url":
                source_url,

            "context":
                deepcopy(
                    context
                ),

            "dimension_evidence":
                dimension_evidence,

            "present_dimensions":
                present_dimensions,

            "missing_dimensions":
                missing_dimensions,

            "present_dimension_count":
                len(
                    present_dimensions
                ),

            "missing_dimension_count":
                len(
                    missing_dimensions
                ),

            "provenance_present":
                provenance_present,

            "provenance":
                deepcopy(
                    provenance
                ) if provenance_present else None,

            "evidence_eligibility":
                eligibility,

            "evidence_extracted":
                True,

            "authority_assessed":
                False,

            "authority_scored":
                False,

            "authority_classified":
                False,

            "external_lookup_performed":
                False,

            "external_target_selected":
                False,

            "truth_assessed":
                False,

            "claim_integrity_decided":
                False,

            "semantic_memory_written":
                False,

            "linking_decision_performed":
                False,
        }

        extracted_records.append(
            record
        )

        if eligibility == "UNRESOLVED":
            unresolved_records.append(
                deepcopy(
                    record
                )
            )

    package_material = {
        "workspace_id":
            workspace_id,

        "scope_id":
            scope.get(
                "scope_id"
            ),

        "record_ids": [
            row[
                "evidence_record_id"
            ]
            for row in extracted_records
        ],
    }

    package_digest = hashlib.sha256(
        json.dumps(
            package_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    evidence_package = {
        "package_schema":
            "authority_evidence_extraction_package_v1",

        "package_version":
            "v1",

        "package_id":
            "authevidencepkg:v1:"
            + package_digest,

        "package_digest":
            package_digest,

        "workspace_id":
            workspace_id,

        "scope_id":
            scope.get(
                "scope_id"
            ),

        "scope_digest":
            scope.get(
                "scope_digest"
            ),

        "subject_count":
            len(
                authority_subjects
            ),

        "evidence_record_count":
            len(
                extracted_records
            ),

        "unresolved_record_count":
            len(
                unresolved_records
            ),

        "evidence_records":
            extracted_records,

        "unresolved_records":
            unresolved_records,

        "authority_evidence_extracted":
            True,

        "authority_assessment_performed":
            False,

        "authority_scoring_performed":
            False,

        "external_authority_lookup_performed":
            False,

        "external_target_selected":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "active_target_set_ownership_preserved":
            True,

        "external_authority_partition_preserved":
            True,

        "external_route_eligibility_preserved":
            True,

        "external_resolver_ownership_preserved":
            True,

        "missing_evidence_invented":
            False,

        "evidence_policy":
            "SUPPLIED_EVIDENCE_EXTRACTION_ONLY",
    }

    return {
        "schema_version":
            "authority_evidence_extraction_result_v1",

        "version":
            AUTHORITY_INTELLIGENCE_VERSION,

        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,

        "patch":
            "4.6.24E",

        "status":
            "AUTHORITY_EVIDENCE_EXTRACTED",

        "workspace_id":
            workspace_id,

        "authority_evidence_package":
            evidence_package,

        "authority_scope":
            deepcopy(
                scope
            ),

        "source_scope_result":
            deepcopy(
                scope_result
            ),

        "processing_boundaries": {
            **deepcopy(
                boundaries
            ),

            "authority_evidence_extracted":
                True,
        },

        "authority_policy":
            "CERTIFIED_AUTHORITY_EVIDENCE_EXTRACTED",

        "next_stage":
            "source_and_evidence_authority_assessment",
    }


# =====================================================================
# PATCH 4.6.24F ? Source & Evidence Authority Assessment
# =====================================================================

def assess_source_and_evidence_authority_v1(
    evidence_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Assess supplied Authority evidence without producing a final score.

    F determines the evidentiary state of every Authority dimension.

    It does NOT:
    - discover external URLs,
    - select an external target,
    - calculate the final Authority score,
    - assign the final Authority class,
    - adjudicate truth,
    - resolve claim conflicts,
    - write Semantic Memory,
    - make linking decisions.
    """

    if not isinstance(
        evidence_result,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "evidence_result must be a dict."
        )

    expected = {
        "schema_version":
            "authority_evidence_extraction_result_v1",

        "version":
            AUTHORITY_INTELLIGENCE_VERSION,

        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,

        "patch":
            "4.6.24E",

        "status":
            "AUTHORITY_EVIDENCE_EXTRACTED",

        "authority_policy":
            "CERTIFIED_AUTHORITY_EVIDENCE_EXTRACTED",

        "next_stage":
            "source_and_evidence_authority_assessment",
    }

    for field, value in expected.items():

        if evidence_result.get(
            field
        ) != value:
            raise AuthorityIntelligenceError(
                f"Invalid 4.6.24E lifecycle field: {field}"
            )

    workspace_id = evidence_result.get(
        "workspace_id"
    )

    package = evidence_result.get(
        "authority_evidence_package"
    )

    scope = evidence_result.get(
        "authority_scope"
    )

    boundaries = evidence_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "authority_evidence_package",
            package,
        ),
        (
            "authority_scope",
            scope,
        ),
        (
            "processing_boundaries",
            boundaries,
        ),
    ):

        if not isinstance(
            value,
            dict,
        ):
            raise AuthorityIntelligenceError(
                name + " is missing or invalid."
            )

    if package.get(
        "package_schema"
    ) != "authority_evidence_extraction_package_v1":
        raise AuthorityIntelligenceError(
            "Authority evidence package schema drifted."
        )

    if package.get(
        "workspace_id"
    ) != workspace_id:
        raise AuthorityIntelligenceError(
            "Authority evidence workspace drifted."
        )

    if package.get(
        "authority_evidence_extracted"
    ) is not True:
        raise AuthorityIntelligenceError(
            "Authority evidence has not been extracted."
        )

    for field in (
        "authority_assessment_performed",
        "authority_scoring_performed",
        "external_authority_lookup_performed",
        "external_target_selected",
        "semantic_memory_written",
        "linking_decisions_performed",
        "missing_evidence_invented",
    ):

        if package.get(
            field
        ) is not False:
            raise AuthorityIntelligenceError(
                f"Invalid evidence-package boundary: {field}"
            )

    if package.get(
        "active_target_set_ownership_preserved"
    ) is not True:
        raise AuthorityIntelligenceError(
            "Active Target Set ownership was not preserved."
        )

    if package.get(
        "external_resolver_ownership_preserved"
    ) is not True:
        raise AuthorityIntelligenceError(
            "External Resolver ownership was not preserved."
        )

    dimensions = list(
        scope.get(
            "authority_dimensions",
            [],
        )
    )

    if len(
        dimensions
    ) != 10:
        raise AuthorityIntelligenceError(
            "Authority dimension contract drifted."
        )

    records = package.get(
        "evidence_records"
    )

    if not isinstance(
        records,
        list,
    ):
        raise AuthorityIntelligenceError(
            "Authority evidence records are invalid."
        )

    if package.get(
        "evidence_record_count"
    ) != len(
        records
    ):
        raise AuthorityIntelligenceError(
            "Authority evidence record count drifted."
        )

    assessment_states = (
        "STRONG_EVIDENCE",
        "SUPPORTED_EVIDENCE",
        "LIMITED_EVIDENCE",
        "MISSING_EVIDENCE",
        "UNRESOLVED_EVIDENCE",
    )

    assessments = []

    for record in records:

        if not isinstance(
            record,
            dict,
        ):
            raise AuthorityIntelligenceError(
                "Authority evidence record must be a dict."
            )

        if record.get(
            "evidence_record_schema"
        ) != "authority_evidence_record_v1":
            raise AuthorityIntelligenceError(
                "Authority evidence record schema drifted."
            )

        subject_id = record.get(
            "subject_id"
        )

        subject_type = record.get(
            "subject_type"
        )

        dimension_evidence = record.get(
            "dimension_evidence"
        )

        if not isinstance(
            dimension_evidence,
            dict,
        ):
            raise AuthorityIntelligenceError(
                f"Missing dimension evidence: {subject_id}"
            )

        dimension_assessments = {}

        strong_count = 0
        supported_count = 0
        limited_count = 0
        missing_count = 0
        unresolved_count = 0

        for dimension in dimensions:

            evidence = dimension_evidence.get(
                dimension
            )

            if not isinstance(
                evidence,
                dict,
            ):
                raise AuthorityIntelligenceError(
                    f"Missing Authority dimension: {dimension}"
                )

            if evidence.get(
                "evidence_invented"
            ) is not False:
                raise AuthorityIntelligenceError(
                    "Invented authority evidence detected."
                )

            present = evidence.get(
                "evidence_present"
            )

            value = evidence.get(
                "evidence_value"
            )

            if present is False:

                state = "MISSING_EVIDENCE"

                missing_count += 1

            elif present is True:

                normalized = str(
                    value
                ).strip().upper()

                strong_markers = {
                    "PRIMARY",
                    "OFFICIAL",
                    "DIRECT",
                    "CERTIFIED",
                    "CURRENT",
                    "INDEPENDENT",
                    "CONSISTENT",
                    "REGULATORY",
                    "PEER_REVIEWED",
                    "STANDARD",
                    "SYSTEMATIC_REVIEW",
                    "META_ANALYSIS",
                }

                weak_markers = {
                    "UNKNOWN",
                    "UNVERIFIED",
                    "ANECDOTAL",
                    "INDIRECT",
                    "UNCLEAR",
                    "UNRESOLVED",
                    "CONFLICTING",
                }

                if any(
                    marker in normalized
                    for marker in weak_markers
                ):

                    state = "LIMITED_EVIDENCE"

                    limited_count += 1

                elif any(
                    marker in normalized
                    for marker in strong_markers
                ):

                    state = "STRONG_EVIDENCE"

                    strong_count += 1

                else:

                    state = "SUPPORTED_EVIDENCE"

                    supported_count += 1

            else:

                state = "UNRESOLVED_EVIDENCE"

                unresolved_count += 1

            dimension_assessments[
                dimension
            ] = {
                "dimension":
                    dimension,

                "assessment_state":
                    state,

                "evidence_present":
                    present,

                "evidence_value":
                    deepcopy(
                        value
                    ),

                "evidence_invented":
                    False,

                "authority_score":
                    None,

                "authority_class":
                    None,
            }

        if record.get(
            "evidence_eligibility"
        ) == "UNRESOLVED":

            overall_evidence_state = "UNRESOLVED_EVIDENCE"

        elif (
            missing_count == 0
            and limited_count == 0
            and unresolved_count == 0
            and strong_count >= 5
        ):

            overall_evidence_state = "STRONG_EVIDENCE"

        elif (
            strong_count
            + supported_count
            >= 5
        ):

            overall_evidence_state = "SUPPORTED_EVIDENCE"

        elif (
            strong_count
            + supported_count
            + limited_count
            >= 3
        ):

            overall_evidence_state = "LIMITED_EVIDENCE"

        else:

            overall_evidence_state = "UNRESOLVED_EVIDENCE"

        material = {
            "workspace_id":
                workspace_id,

            "subject_id":
                subject_id,

            "subject_type":
                subject_type,

            "evidence_record_id":
                record.get(
                    "evidence_record_id"
                ),

            "dimension_assessments":
                dimension_assessments,

            "overall_evidence_state":
                overall_evidence_state,
        }

        digest = hashlib.sha256(
            json.dumps(
                material,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        assessment = {
            "assessment_schema":
                "source_evidence_authority_assessment_v1",

            "assessment_id":
                "authassess:v1:"
                + digest,

            "assessment_digest":
                digest,

            "workspace_id":
                workspace_id,

            "subject_id":
                subject_id,

            "subject_type":
                subject_type,

            "source_url":
                record.get(
                    "source_url"
                ),

            "evidence_record_id":
                record.get(
                    "evidence_record_id"
                ),

            "evidence_record_digest":
                record.get(
                    "evidence_record_digest"
                ),

            "evidence_eligibility":
                record.get(
                    "evidence_eligibility"
                ),

            "dimension_assessments":
                dimension_assessments,

            "strong_evidence_count":
                strong_count,

            "supported_evidence_count":
                supported_count,

            "limited_evidence_count":
                limited_count,

            "missing_evidence_count":
                missing_count,

            "unresolved_evidence_count":
                unresolved_count,

            "overall_evidence_state":
                overall_evidence_state,

            "assessment_states_allowed":
                list(
                    assessment_states
                ),

            "source_and_evidence_assessed":
                True,

            "authority_score":
                None,

            "authority_class":
                None,

            "authority_scoring_performed":
                False,

            "authority_classification_performed":
                False,

            "authority_integrity_guard_performed":
                False,

            "external_authority_lookup_performed":
                False,

            "external_target_selected":
                False,

            "truth_assessment_performed":
                False,

            "claim_integrity_decision_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        }

        assessments.append(
            assessment
        )

    package_material = {
        "workspace_id":
            workspace_id,

        "source_evidence_package_id":
            package.get(
                "package_id"
            ),

        "assessment_ids": [
            item[
                "assessment_id"
            ]
            for item in assessments
        ],
    }

    assessment_package_digest = hashlib.sha256(
        json.dumps(
            package_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    assessment_package = {
        "package_schema":
            "source_evidence_authority_assessment_package_v1",

        "package_version":
            "v1",

        "package_id":
            "authassesspkg:v1:"
            + assessment_package_digest,

        "package_digest":
            assessment_package_digest,

        "workspace_id":
            workspace_id,

        "source_evidence_package_id":
            package.get(
                "package_id"
            ),

        "source_evidence_package_digest":
            package.get(
                "package_digest"
            ),

        "assessment_count":
            len(
                assessments
            ),

        "assessments":
            assessments,

        "source_and_evidence_assessment_performed":
            True,

        "authority_scoring_performed":
            False,

        "authority_classification_performed":
            False,

        "authority_integrity_guard_performed":
            False,

        "external_authority_lookup_performed":
            False,

        "external_target_selected":
            False,

        "truth_assessment_performed":
            False,

        "claim_integrity_decision_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "active_target_set_ownership_preserved":
            True,

        "external_authority_partition_preserved":
            True,

        "external_route_eligibility_preserved":
            True,

        "external_resolver_ownership_preserved":
            True,

        "unsupported_authority_invention_performed":
            False,

        "assessment_policy":
            "EVIDENCE_BOUND_SOURCE_AUTHORITY_ASSESSMENT_ONLY",
    }

    return {
        "schema_version":
            "source_evidence_authority_assessment_result_v1",

        "version":
            AUTHORITY_INTELLIGENCE_VERSION,

        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,

        "patch":
            "4.6.24F",

        "status":
            "SOURCE_AND_EVIDENCE_AUTHORITY_ASSESSED",

        "workspace_id":
            workspace_id,

        "authority_assessment_package":
            assessment_package,

        "authority_evidence_package":
            deepcopy(
                package
            ),

        "authority_scope":
            deepcopy(
                scope
            ),

        "source_evidence_result":
            deepcopy(
                evidence_result
            ),

        "processing_boundaries": {
            **deepcopy(
                boundaries
            ),

            "source_authority_assessed":
                True,
        },

        "authority_policy":
            "CERTIFIED_SOURCE_EVIDENCE_AUTHORITY_ASSESSMENT",

        "next_stage":
            "authority_scoring_and_classification",
    }


# =====================================================================
# PATCH 4.6.24G ? Authority Scoring & Classification
# =====================================================================

def score_and_classify_authority_v1(
    assessment_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert certified F assessments into Authority scores and classes.

    G owns:
    - dimension-level authority scoring,
    - aggregate authority scoring,
    - authority classification.

    G does NOT:
    - discover URLs,
    - select an external target,
    - adjudicate truth,
    - resolve claim conflicts,
    - write Semantic Memory,
    - make linking decisions.
    """

    if not isinstance(
        assessment_result,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "assessment_result must be a dict."
        )

    expected = {
        "schema_version":
            "source_evidence_authority_assessment_result_v1",
        "version":
            AUTHORITY_INTELLIGENCE_VERSION,
        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,
        "patch":
            "4.6.24F",
        "status":
            "SOURCE_AND_EVIDENCE_AUTHORITY_ASSESSED",
        "authority_policy":
            "CERTIFIED_SOURCE_EVIDENCE_AUTHORITY_ASSESSMENT",
        "next_stage":
            "authority_scoring_and_classification",
    }

    for field, value in expected.items():

        if assessment_result.get(
            field
        ) != value:
            raise AuthorityIntelligenceError(
                f"Invalid 4.6.24F lifecycle field: {field}"
            )

    workspace_id = assessment_result.get(
        "workspace_id"
    )

    package = assessment_result.get(
        "authority_assessment_package"
    )

    boundaries = assessment_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        package,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "authority_assessment_package is missing or invalid."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "processing_boundaries are missing or invalid."
        )

    if package.get(
        "package_schema"
    ) != "source_evidence_authority_assessment_package_v1":
        raise AuthorityIntelligenceError(
            "Authority assessment package schema drifted."
        )

    if package.get(
        "workspace_id"
    ) != workspace_id:
        raise AuthorityIntelligenceError(
            "Authority assessment workspace drifted."
        )

    if package.get(
        "source_and_evidence_assessment_performed"
    ) is not True:
        raise AuthorityIntelligenceError(
            "Source/evidence assessment has not been performed."
        )

    for field in (
        "authority_scoring_performed",
        "authority_classification_performed",
        "authority_integrity_guard_performed",
        "external_authority_lookup_performed",
        "external_target_selected",
        "truth_assessment_performed",
        "claim_integrity_decision_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
        "unsupported_authority_invention_performed",
    ):

        if package.get(
            field
        ) is not False:
            raise AuthorityIntelligenceError(
                f"Invalid F boundary: {field}"
            )

    if package.get(
        "active_target_set_ownership_preserved"
    ) is not True:
        raise AuthorityIntelligenceError(
            "Active Target Set ownership was not preserved."
        )

    if package.get(
        "external_resolver_ownership_preserved"
    ) is not True:
        raise AuthorityIntelligenceError(
            "External Resolver ownership was not preserved."
        )

    assessments = package.get(
        "assessments"
    )

    if not isinstance(
        assessments,
        list,
    ):
        raise AuthorityIntelligenceError(
            "Authority assessments are invalid."
        )

    if package.get(
        "assessment_count"
    ) != len(
        assessments
    ):
        raise AuthorityIntelligenceError(
            "Authority assessment count drifted."
        )

    score_map = {
        "STRONG_EVIDENCE":
            1.00,
        "SUPPORTED_EVIDENCE":
            0.75,
        "LIMITED_EVIDENCE":
            0.40,
        "MISSING_EVIDENCE":
            0.00,
        "UNRESOLVED_EVIDENCE":
            0.00,
    }

    dimension_weights = {
        "SOURCE_IDENTITY":
            0.10,
        "PRIMARY_SOURCE_STATUS":
            0.12,
        "INSTITUTIONAL_AUTHORITY":
            0.12,
        "DOMAIN_EXPERTISE":
            0.12,
        "EVIDENCE_QUALITY":
            0.14,
        "PROVENANCE_QUALITY":
            0.12,
        "TOPIC_APPLICABILITY":
            0.10,
        "RECENCY_APPLICABILITY":
            0.06,
        "SOURCE_INDEPENDENCE":
            0.06,
        "AUTHORITY_CONSISTENCY":
            0.06,
    }

    weight_sum = round(
        sum(
            dimension_weights.values()
        ),
        10,
    )

    if weight_sum != 1.0:
        raise AuthorityIntelligenceError(
            "Authority dimension weights must total 1.0."
        )

    score_records = []

    for assessment in assessments:

        if not isinstance(
            assessment,
            dict,
        ):
            raise AuthorityIntelligenceError(
                "Authority assessment must be a dict."
            )

        if assessment.get(
            "assessment_schema"
        ) != "source_evidence_authority_assessment_v1":
            raise AuthorityIntelligenceError(
                "Authority assessment schema drifted."
            )

        subject_id = assessment.get(
            "subject_id"
        )

        dimension_assessments = assessment.get(
            "dimension_assessments"
        )

        if not isinstance(
            dimension_assessments,
            dict,
        ):
            raise AuthorityIntelligenceError(
                f"Dimension assessments missing: {subject_id}"
            )

        if set(
            dimension_assessments.keys()
        ) != set(
            dimension_weights.keys()
        ):
            raise AuthorityIntelligenceError(
                f"Authority dimension set drifted: {subject_id}"
            )

        dimension_scores = {}

        weighted_total = 0.0

        for dimension, weight in dimension_weights.items():

            dim_assessment = dimension_assessments[
                dimension
            ]

            state = dim_assessment.get(
                "assessment_state"
            )

            if state not in score_map:
                raise AuthorityIntelligenceError(
                    f"Unknown assessment state: {state}"
                )

            if dim_assessment.get(
                "authority_score"
            ) is not None:
                raise AuthorityIntelligenceError(
                    "F must not pre-score Authority dimensions."
                )

            if dim_assessment.get(
                "authority_class"
            ) is not None:
                raise AuthorityIntelligenceError(
                    "F must not pre-classify Authority dimensions."
                )

            raw_score = score_map[
                state
            ]

            weighted_score = round(
                raw_score
                * weight,
                6,
            )

            weighted_total += weighted_score

            dimension_scores[
                dimension
            ] = {
                "assessment_state":
                    state,

                "dimension_weight":
                    weight,

                "raw_dimension_score":
                    raw_score,

                "weighted_dimension_score":
                    weighted_score,

                "score_source":
                    "CERTIFIED_4.6.24F_ASSESSMENT_STATE",

                "unsupported_score_invention":
                    False,
            }

        authority_score = round(
            max(
                0.0,
                min(
                    1.0,
                    weighted_total,
                ),
            ),
            4,
        )

        eligibility = assessment.get(
            "evidence_eligibility"
        )

        overall_state = assessment.get(
            "overall_evidence_state"
        )

        if eligibility == "UNRESOLVED" or (
            overall_state
            == "UNRESOLVED_EVIDENCE"
            and authority_score < 0.25
        ):

            authority_class = "UNRESOLVED"

        elif eligibility == "BLOCKED":

            authority_class = "BLOCKED"

        elif authority_score >= 0.90:

            authority_class = "VERY_HIGH"

        elif authority_score >= 0.75:

            authority_class = "HIGH"

        elif authority_score >= 0.55:

            authority_class = "MODERATE"

        elif authority_score >= 0.35:

            authority_class = "LOW"

        else:

            authority_class = "VERY_LOW"

        if authority_class in {
            "UNRESOLVED",
            "BLOCKED",
        }:

            authority_confidence = (
                "INSUFFICIENT_EVIDENCE"
            )

        elif assessment.get(
            "missing_evidence_count",
            0,
        ) == 0 and assessment.get(
            "unresolved_evidence_count",
            0,
        ) == 0:

            authority_confidence = (
                "HIGH_CONFIDENCE"
            )

        elif assessment.get(
            "strong_evidence_count",
            0,
        ) + assessment.get(
            "supported_evidence_count",
            0,
        ) >= 5:

            authority_confidence = (
                "MODERATE_CONFIDENCE"
            )

        else:

            authority_confidence = (
                "LOW_CONFIDENCE"
            )

        material = {
            "workspace_id":
                workspace_id,

            "subject_id":
                subject_id,

            "assessment_id":
                assessment.get(
                    "assessment_id"
                ),

            "dimension_scores":
                dimension_scores,

            "authority_score":
                authority_score,

            "authority_class":
                authority_class,

            "authority_confidence":
                authority_confidence,
        }

        digest = hashlib.sha256(
            json.dumps(
                material,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        score_record = {
            "score_record_schema":
                "authority_score_classification_record_v1",

            "score_record_id":
                "authscore:v1:"
                + digest,

            "score_record_digest":
                digest,

            "workspace_id":
                workspace_id,

            "subject_id":
                subject_id,

            "subject_type":
                assessment.get(
                    "subject_type"
                ),

            "source_url":
                assessment.get(
                    "source_url"
                ),

            "assessment_id":
                assessment.get(
                    "assessment_id"
                ),

            "assessment_digest":
                assessment.get(
                    "assessment_digest"
                ),

            "evidence_eligibility":
                eligibility,

            "overall_evidence_state":
                overall_state,

            "dimension_scores":
                dimension_scores,

            "authority_score":
                authority_score,

            "authority_class":
                authority_class,

            "authority_confidence":
                authority_confidence,

            "authority_scoring_performed":
                True,

            "authority_classification_performed":
                True,

            "authority_integrity_guard_performed":
                False,

            "external_authority_lookup_performed":
                False,

            "external_target_selected":
                False,

            "truth_assessment_performed":
                False,

            "claim_integrity_decision_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "active_target_set_ownership_preserved":
                True,

            "external_authority_partition_preserved":
                True,

            "external_route_eligibility_preserved":
                True,

            "external_resolver_ownership_preserved":
                True,

            "unsupported_authority_invention_performed":
                False,
        }

        score_records.append(
            score_record
        )

    package_material = {
        "workspace_id":
            workspace_id,

        "source_assessment_package_id":
            package.get(
                "package_id"
            ),

        "score_record_ids": [
            record[
                "score_record_id"
            ]
            for record in score_records
        ],
    }

    scoring_package_digest = hashlib.sha256(
        json.dumps(
            package_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    scoring_package = {
        "package_schema":
            "authority_scoring_classification_package_v1",

        "package_version":
            "v1",

        "package_id":
            "authscorepkg:v1:"
            + scoring_package_digest,

        "package_digest":
            scoring_package_digest,

        "workspace_id":
            workspace_id,

        "source_assessment_package_id":
            package.get(
                "package_id"
            ),

        "source_assessment_package_digest":
            package.get(
                "package_digest"
            ),

        "dimension_weights":
            deepcopy(
                dimension_weights
            ),

        "score_state_map":
            deepcopy(
                score_map
            ),

        "score_record_count":
            len(
                score_records
            ),

        "score_records":
            score_records,

        "authority_scoring_performed":
            True,

        "authority_classification_performed":
            True,

        "authority_integrity_guard_performed":
            False,

        "external_authority_lookup_performed":
            False,

        "external_target_selected":
            False,

        "truth_assessment_performed":
            False,

        "claim_integrity_decision_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "active_target_set_ownership_preserved":
            True,

        "external_authority_partition_preserved":
            True,

        "external_route_eligibility_preserved":
            True,

        "external_resolver_ownership_preserved":
            True,

        "unsupported_authority_invention_performed":
            False,

        "scoring_policy":
            "EVIDENCE_STATE_WEIGHTED_AUTHORITY_SCORING_V1",
    }

    return {
        "schema_version":
            "authority_scoring_classification_result_v1",

        "version":
            AUTHORITY_INTELLIGENCE_VERSION,

        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,

        "patch":
            "4.6.24G",

        "status":
            "AUTHORITY_SCORED_AND_CLASSIFIED",

        "workspace_id":
            workspace_id,

        "authority_scoring_package":
            scoring_package,

        "authority_assessment_package":
            deepcopy(
                package
            ),

        "source_assessment_result":
            deepcopy(
                assessment_result
            ),

        "processing_boundaries": {
            **deepcopy(
                boundaries
            ),

            "authority_scoring_performed":
                True,
        },

        "authority_policy":
            "CERTIFIED_AUTHORITY_SCORING_AND_CLASSIFICATION",

        "next_stage":
            "authority_integrity_and_manipulation_guard",
    }


# =====================================================================
# PATCH 4.6.24H ? Authority Integrity & Manipulation Guard
# =====================================================================

def guard_authority_integrity_and_manipulation_v1(
    scoring_result: dict[str, Any],
    integrity_signals: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Guard Authority results against manipulation and integrity defects.

    H preserves the G score/class and attaches a guard outcome.

    It does NOT:
    - discover URLs,
    - select external targets,
    - silently rescore Authority,
    - adjudicate truth,
    - resolve claim conflicts,
    - write Semantic Memory,
    - make linking decisions.
    """

    if not isinstance(
        scoring_result,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "scoring_result must be a dict."
        )

    if integrity_signals is None:
        integrity_signals = {}

    if not isinstance(
        integrity_signals,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "integrity_signals must be a dict."
        )

    expected = {
        "schema_version":
            "authority_scoring_classification_result_v1",
        "version":
            AUTHORITY_INTELLIGENCE_VERSION,
        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,
        "patch":
            "4.6.24G",
        "status":
            "AUTHORITY_SCORED_AND_CLASSIFIED",
        "authority_policy":
            "CERTIFIED_AUTHORITY_SCORING_AND_CLASSIFICATION",
        "next_stage":
            "authority_integrity_and_manipulation_guard",
    }

    for field, value in expected.items():

        if scoring_result.get(
            field
        ) != value:
            raise AuthorityIntelligenceError(
                f"Invalid 4.6.24G lifecycle field: {field}"
            )

    workspace_id = scoring_result.get(
        "workspace_id"
    )

    package = scoring_result.get(
        "authority_scoring_package"
    )

    boundaries = scoring_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        package,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "authority_scoring_package is missing or invalid."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "processing_boundaries are missing or invalid."
        )

    if package.get(
        "package_schema"
    ) != "authority_scoring_classification_package_v1":
        raise AuthorityIntelligenceError(
            "Authority scoring package schema drifted."
        )

    if package.get(
        "workspace_id"
    ) != workspace_id:
        raise AuthorityIntelligenceError(
            "Authority scoring workspace drifted."
        )

    for field in (
        "authority_scoring_performed",
        "authority_classification_performed",
        "active_target_set_ownership_preserved",
        "external_resolver_ownership_preserved",
    ):

        if package.get(
            field
        ) is not True:
            raise AuthorityIntelligenceError(
                f"Required G flag is not True: {field}"
            )

    for field in (
        "authority_integrity_guard_performed",
        "external_authority_lookup_performed",
        "external_target_selected",
        "truth_assessment_performed",
        "claim_integrity_decision_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
        "unsupported_authority_invention_performed",
    ):

        if package.get(
            field
        ) is not False:
            raise AuthorityIntelligenceError(
                f"Invalid G boundary: {field}"
            )

    score_records = package.get(
        "score_records"
    )

    if not isinstance(
        score_records,
        list,
    ):
        raise AuthorityIntelligenceError(
            "Authority score records are invalid."
        )

    if package.get(
        "score_record_count"
    ) != len(
        score_records
    ):
        raise AuthorityIntelligenceError(
            "Authority score record count drifted."
        )

    allowed_signal_keys = {
        "authority_inflation_detected",
        "circular_sourcing_detected",
        "duplicate_evidence_detected",
        "false_expertise_detected",
        "popularity_substitution_detected",
        "self_citation_loop_detected",
        "source_identity_conflict_detected",
        "provenance_conflict_detected",
    }

    blocking_signals = {
        "authority_inflation_detected",
        "circular_sourcing_detected",
        "false_expertise_detected",
        "self_citation_loop_detected",
        "source_identity_conflict_detected",
        "provenance_conflict_detected",
    }

    conditional_signals = {
        "duplicate_evidence_detected",
        "popularity_substitution_detected",
    }

    guard_records = []

    for record in score_records:

        if not isinstance(
            record,
            dict,
        ):
            raise AuthorityIntelligenceError(
                "Authority score record must be a dict."
            )

        if record.get(
            "score_record_schema"
        ) != "authority_score_classification_record_v1":
            raise AuthorityIntelligenceError(
                "Authority score record schema drifted."
            )

        subject_id = record.get(
            "subject_id"
        )

        if not isinstance(
            subject_id,
            str,
        ) or not subject_id:
            raise AuthorityIntelligenceError(
                "Authority score record lacks subject_id."
            )

        signals = integrity_signals.get(
            subject_id,
            {}
        )

        if not isinstance(
            signals,
            dict,
        ):
            raise AuthorityIntelligenceError(
                f"Integrity signals must be a dict: {subject_id}"
            )

        unknown_signal_keys = (
            set(signals.keys())
            - allowed_signal_keys
        )

        if unknown_signal_keys:
            raise AuthorityIntelligenceError(
                f"Unsupported integrity signal(s): "
                f"{sorted(unknown_signal_keys)}"
            )

        normalized_signals = {}

        for signal in sorted(
            allowed_signal_keys
        ):

            value = signals.get(
                signal,
                False,
            )

            if not isinstance(
                value,
                bool,
            ):
                raise AuthorityIntelligenceError(
                    f"Integrity signal must be bool: {signal}"
                )

            normalized_signals[
                signal
            ] = value

        triggered = [
            signal
            for signal, active
            in normalized_signals.items()
            if active
        ]

        blocking_triggered = [
            signal
            for signal in triggered
            if signal in blocking_signals
        ]

        conditional_triggered = [
            signal
            for signal in triggered
            if signal in conditional_signals
        ]

        if (
            record.get(
                "authority_class"
            )
            in {
                "UNRESOLVED",
                "BLOCKED",
            }
        ):

            guard_outcome = "BLOCKED"

            guard_reason = (
                "SOURCE_ALREADY_UNRESOLVED_OR_BLOCKED"
            )

        elif blocking_triggered:

            guard_outcome = "BLOCKED"

            guard_reason = (
                "AUTHORITY_INTEGRITY_BLOCKING_SIGNAL"
            )

        elif conditional_triggered:

            guard_outcome = "CONDITIONALLY_APPROVED"

            guard_reason = (
                "AUTHORITY_INTEGRITY_CONDITIONAL_SIGNAL"
            )

        else:

            guard_outcome = "APPROVED"

            guard_reason = (
                "NO_AUTHORITY_INTEGRITY_DEFECT_DETECTED"
            )

        material = {
            "workspace_id":
                workspace_id,
            "subject_id":
                subject_id,
            "score_record_id":
                record.get(
                    "score_record_id"
                ),
            "authority_score":
                record.get(
                    "authority_score"
                ),
            "authority_class":
                record.get(
                    "authority_class"
                ),
            "normalized_signals":
                normalized_signals,
            "guard_outcome":
                guard_outcome,
            "guard_reason":
                guard_reason,
        }

        digest = hashlib.sha256(
            json.dumps(
                material,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        guard_record = {
            "guard_record_schema":
                "authority_integrity_guard_record_v1",

            "guard_record_id":
                "authguard:v1:"
                + digest,

            "guard_record_digest":
                digest,

            "workspace_id":
                workspace_id,

            "subject_id":
                subject_id,

            "subject_type":
                record.get(
                    "subject_type"
                ),

            "source_url":
                record.get(
                    "source_url"
                ),

            "score_record_id":
                record.get(
                    "score_record_id"
                ),

            "score_record_digest":
                record.get(
                    "score_record_digest"
                ),

            "authority_score":
                record.get(
                    "authority_score"
                ),

            "authority_class":
                record.get(
                    "authority_class"
                ),

            "authority_confidence":
                record.get(
                    "authority_confidence"
                ),

            "normalized_integrity_signals":
                normalized_signals,

            "triggered_integrity_signals":
                triggered,

            "blocking_integrity_signals":
                blocking_triggered,

            "conditional_integrity_signals":
                conditional_triggered,

            "guard_outcome":
                guard_outcome,

            "guard_reason":
                guard_reason,

            "authority_score_preserved":
                True,

            "authority_class_preserved":
                True,

            "silent_rescoring_performed":
                False,

            "authority_integrity_guard_performed":
                True,

            "external_authority_lookup_performed":
                False,

            "external_target_selected":
                False,

            "truth_assessment_performed":
                False,

            "claim_integrity_decision_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "active_target_set_ownership_preserved":
                True,

            "external_authority_partition_preserved":
                True,

            "external_route_eligibility_preserved":
                True,

            "external_resolver_ownership_preserved":
                True,

            "unsupported_authority_invention_performed":
                False,
        }

        guard_records.append(
            guard_record
        )

    package_material = {
        "workspace_id":
            workspace_id,

        "source_scoring_package_id":
            package.get(
                "package_id"
            ),

        "guard_record_ids": [
            row[
                "guard_record_id"
            ]
            for row in guard_records
        ],
    }

    guard_package_digest = hashlib.sha256(
        json.dumps(
            package_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    guard_package = {
        "package_schema":
            "authority_integrity_manipulation_guard_package_v1",

        "package_version":
            "v1",

        "package_id":
            "authguardpkg:v1:"
            + guard_package_digest,

        "package_digest":
            guard_package_digest,

        "workspace_id":
            workspace_id,

        "source_scoring_package_id":
            package.get(
                "package_id"
            ),

        "source_scoring_package_digest":
            package.get(
                "package_digest"
            ),

        "guard_record_count":
            len(
                guard_records
            ),

        "guard_records":
            guard_records,

        "allowed_integrity_signals":
            sorted(
                allowed_signal_keys
            ),

        "blocking_integrity_signals":
            sorted(
                blocking_signals
            ),

        "conditional_integrity_signals":
            sorted(
                conditional_signals
            ),

        "authority_integrity_guard_performed":
            True,

        "authority_scores_preserved":
            True,

        "authority_classes_preserved":
            True,

        "silent_rescoring_performed":
            False,

        "external_authority_lookup_performed":
            False,

        "external_target_selected":
            False,

        "truth_assessment_performed":
            False,

        "claim_integrity_decision_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "active_target_set_ownership_preserved":
            True,

        "external_authority_partition_preserved":
            True,

        "external_route_eligibility_preserved":
            True,

        "external_resolver_ownership_preserved":
            True,

        "unsupported_authority_invention_performed":
            False,

        "guard_policy":
            "PRESERVE_SCORE_AND_BLOCK_AUTHORITY_MANIPULATION_V1",
    }

    return {
        "schema_version":
            "authority_integrity_guard_result_v1",

        "version":
            AUTHORITY_INTELLIGENCE_VERSION,

        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,

        "patch":
            "4.6.24H",

        "status":
            "AUTHORITY_INTEGRITY_GUARD_COMPLETED",

        "workspace_id":
            workspace_id,

        "authority_guard_package":
            guard_package,

        "authority_scoring_package":
            deepcopy(
                package
            ),

        "source_scoring_result":
            deepcopy(
                scoring_result
            ),

        "processing_boundaries": {
            **deepcopy(
                boundaries
            ),

            "authority_integrity_guard_performed":
                True,
        },

        "authority_policy":
            "CERTIFIED_AUTHORITY_INTEGRITY_GUARD",

        "next_stage":
            "authority_provenance_and_evidence_trace",
    }


# =====================================================================
# PATCH 4.6.24I ? Authority Provenance & Evidence Trace
# =====================================================================

def build_authority_provenance_and_evidence_trace_v1(
    guard_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the complete Authority provenance and evidence trace.

    I binds together:
    E evidence extraction,
    F source/evidence assessment,
    G scoring/classification,
    H integrity/manipulation guard.

    No Authority result is changed here.
    """

    if not isinstance(
        guard_result,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "guard_result must be a dict."
        )

    expected = {
        "schema_version":
            "authority_integrity_guard_result_v1",

        "version":
            AUTHORITY_INTELLIGENCE_VERSION,

        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,

        "patch":
            "4.6.24H",

        "status":
            "AUTHORITY_INTEGRITY_GUARD_COMPLETED",

        "authority_policy":
            "CERTIFIED_AUTHORITY_INTEGRITY_GUARD",

        "next_stage":
            "authority_provenance_and_evidence_trace",
    }

    for field, value in expected.items():

        if guard_result.get(
            field
        ) != value:
            raise AuthorityIntelligenceError(
                f"Invalid 4.6.24H lifecycle field: {field}"
            )

    workspace_id = guard_result.get(
        "workspace_id"
    )

    guard_package = guard_result.get(
        "authority_guard_package"
    )

    scoring_package = guard_result.get(
        "authority_scoring_package"
    )

    source_scoring_result = guard_result.get(
        "source_scoring_result"
    )

    boundaries = guard_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "authority_guard_package",
            guard_package,
        ),
        (
            "authority_scoring_package",
            scoring_package,
        ),
        (
            "source_scoring_result",
            source_scoring_result,
        ),
        (
            "processing_boundaries",
            boundaries,
        ),
    ):

        if not isinstance(
            value,
            dict,
        ):
            raise AuthorityIntelligenceError(
                name + " is missing or invalid."
            )

    if guard_package.get(
        "package_schema"
    ) != "authority_integrity_manipulation_guard_package_v1":
        raise AuthorityIntelligenceError(
            "Authority guard package schema drifted."
        )

    if scoring_package.get(
        "package_schema"
    ) != "authority_scoring_classification_package_v1":
        raise AuthorityIntelligenceError(
            "Authority scoring package schema drifted."
        )

    if guard_package.get(
        "workspace_id"
    ) != workspace_id:
        raise AuthorityIntelligenceError(
            "Authority guard workspace drifted."
        )

    if scoring_package.get(
        "workspace_id"
    ) != workspace_id:
        raise AuthorityIntelligenceError(
            "Authority scoring workspace drifted."
        )

    for field in (
        "authority_integrity_guard_performed",
        "authority_scores_preserved",
        "authority_classes_preserved",
        "active_target_set_ownership_preserved",
        "external_resolver_ownership_preserved",
    ):

        if guard_package.get(
            field
        ) is not True:
            raise AuthorityIntelligenceError(
                f"Required H flag is not True: {field}"
            )

    for field in (
        "silent_rescoring_performed",
        "external_authority_lookup_performed",
        "external_target_selected",
        "truth_assessment_performed",
        "claim_integrity_decision_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
        "unsupported_authority_invention_performed",
    ):

        if guard_package.get(
            field
        ) is not False:
            raise AuthorityIntelligenceError(
                f"Invalid H boundary: {field}"
            )

    guard_records = guard_package.get(
        "guard_records"
    )

    score_records = scoring_package.get(
        "score_records"
    )

    if not isinstance(
        guard_records,
        list,
    ):
        raise AuthorityIntelligenceError(
            "Authority guard records are invalid."
        )

    if not isinstance(
        score_records,
        list,
    ):
        raise AuthorityIntelligenceError(
            "Authority score records are invalid."
        )

    if guard_package.get(
        "guard_record_count"
    ) != len(
        guard_records
    ):
        raise AuthorityIntelligenceError(
            "Authority guard record count drifted."
        )

    if scoring_package.get(
        "score_record_count"
    ) != len(
        score_records
    ):
        raise AuthorityIntelligenceError(
            "Authority score record count drifted."
        )

    score_by_id = {}

    for score_record in score_records:

        if not isinstance(
            score_record,
            dict,
        ):
            raise AuthorityIntelligenceError(
                "Authority score record must be a dict."
            )

        subject_id = score_record.get(
            "subject_id"
        )

        if subject_id in score_by_id:
            raise AuthorityIntelligenceError(
                f"Duplicate score subject_id: {subject_id}"
            )

        score_by_id[
            subject_id
        ] = score_record

    trace_records = []

    for guard_record in guard_records:

        if not isinstance(
            guard_record,
            dict,
        ):
            raise AuthorityIntelligenceError(
                "Authority guard record must be a dict."
            )

        if guard_record.get(
            "guard_record_schema"
        ) != "authority_integrity_guard_record_v1":
            raise AuthorityIntelligenceError(
                "Authority guard record schema drifted."
            )

        subject_id = guard_record.get(
            "subject_id"
        )

        if subject_id not in score_by_id:
            raise AuthorityIntelligenceError(
                f"Missing score record for guard subject: {subject_id}"
            )

        score_record = score_by_id[
            subject_id
        ]

        if guard_record.get(
            "score_record_id"
        ) != score_record.get(
            "score_record_id"
        ):
            raise AuthorityIntelligenceError(
                f"Score identity mismatch: {subject_id}"
            )

        if guard_record.get(
            "score_record_digest"
        ) != score_record.get(
            "score_record_digest"
        ):
            raise AuthorityIntelligenceError(
                f"Score digest mismatch: {subject_id}"
            )

        if guard_record.get(
            "authority_score"
        ) != score_record.get(
            "authority_score"
        ):
            raise AuthorityIntelligenceError(
                f"Authority score preservation drifted: {subject_id}"
            )

        if guard_record.get(
            "authority_class"
        ) != score_record.get(
            "authority_class"
        ):
            raise AuthorityIntelligenceError(
                f"Authority class preservation drifted: {subject_id}"
            )

        provenance_chain = {
            "source_scoring_result_schema":
                source_scoring_result.get(
                    "schema_version"
                ),

            "source_scoring_result_patch":
                source_scoring_result.get(
                    "patch"
                ),

            "scoring_package_id":
                scoring_package.get(
                    "package_id"
                ),

            "scoring_package_digest":
                scoring_package.get(
                    "package_digest"
                ),

            "score_record_id":
                score_record.get(
                    "score_record_id"
                ),

            "score_record_digest":
                score_record.get(
                    "score_record_digest"
                ),

            "assessment_id":
                score_record.get(
                    "assessment_id"
                ),

            "assessment_digest":
                score_record.get(
                    "assessment_digest"
                ),

            "guard_package_id":
                guard_package.get(
                    "package_id"
                ),

            "guard_package_digest":
                guard_package.get(
                    "package_digest"
                ),

            "guard_record_id":
                guard_record.get(
                    "guard_record_id"
                ),

            "guard_record_digest":
                guard_record.get(
                    "guard_record_digest"
                ),
        }

        evidence_trace = {
            "subject_id":
                subject_id,

            "subject_type":
                guard_record.get(
                    "subject_type"
                ),

            "source_url":
                guard_record.get(
                    "source_url"
                ),

            "authority_score":
                guard_record.get(
                    "authority_score"
                ),

            "authority_class":
                guard_record.get(
                    "authority_class"
                ),

            "authority_confidence":
                guard_record.get(
                    "authority_confidence"
                ),

            "guard_outcome":
                guard_record.get(
                    "guard_outcome"
                ),

            "guard_reason":
                guard_record.get(
                    "guard_reason"
                ),

            "triggered_signals": guard_record.get("triggered_signals", []),
            "blocking_signals": guard_record.get("blocking_signals", []),
            "conditional_signals": guard_record.get("conditional_signals", []),
            "triggered_integrity_signals":
                deepcopy(
                    guard_record.get(
                        "triggered_integrity_signals",
                        [],
                    )
                ),

            "blocking_integrity_signals":
                deepcopy(
                    guard_record.get(
                        "blocking_integrity_signals",
                        [],
                    )
                ),

            "conditional_integrity_signals":
                deepcopy(
                    guard_record.get(
                        "conditional_integrity_signals",
                        [],
                    )
                ),

            "score_preserved":
                guard_record.get(
                    "authority_score_preserved"
                ) is True,

            "class_preserved":
                guard_record.get(
                    "authority_class_preserved"
                ) is True,

            "active_target_set_ownership_preserved":
                guard_record.get(
                    "active_target_set_ownership_preserved"
                ) is True,

            "external_resolver_ownership_preserved":
                guard_record.get(
                    "external_resolver_ownership_preserved"
                ) is True,
        }

        trace_material = {
            "workspace_id":
                workspace_id,

            "subject_id":
                subject_id,

            "provenance_chain":
                provenance_chain,

            "evidence_trace":
                evidence_trace,
        }

        trace_digest = hashlib.sha256(
            json.dumps(
                trace_material,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        trace_record = {
            "trace_schema":
                "authority_provenance_evidence_trace_record_v1",

            "trace_id":
                "authtrace:v1:"
                + trace_digest,

            "trace_digest":
                trace_digest,

            "workspace_id":
                workspace_id,

            "subject_id":
                subject_id,

            "subject_type":
                guard_record.get(
                    "subject_type"
                ),

            "source_url":
                guard_record.get(
                    "source_url"
                ),

            "provenance_chain":
                provenance_chain,

            "evidence_trace":
                evidence_trace,

            "authority_score":
                guard_record.get(
                    "authority_score"
                ),

            "authority_class":
                guard_record.get(
                    "authority_class"
                ),

            "authority_confidence":
                guard_record.get(
                    "authority_confidence"
                ),

            "guard_outcome":
                guard_record.get(
                    "guard_outcome"
                ),

            "guard_reason":
                guard_record.get(
                    "guard_reason"
                ),

            "authority_provenance_built":
                True,

            "authority_evidence_trace_built":
                True,

            "score_identity_verified":
                True,

            "score_digest_verified":
                True,

            "guard_identity_verified":
                True,

            "guard_digest_verified":
                True,

            "authority_score_preserved":
                True,

            "authority_class_preserved":
                True,

            "guard_outcome_preserved":
                True,

            "external_authority_lookup_performed":
                False,

            "external_target_selected":
                False,

            "truth_assessment_performed":
                False,

            "claim_integrity_decision_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "active_target_set_ownership_preserved":
                True,

            "external_authority_partition_preserved":
                True,

            "external_route_eligibility_preserved":
                True,

            "external_resolver_ownership_preserved":
                True,

            "unsupported_authority_invention_performed":
                False,
        }

        trace_records.append(
            trace_record
        )

    package_material = {
        "workspace_id":
            workspace_id,

        "source_guard_package_id":
            guard_package.get(
                "package_id"
            ),

        "trace_ids": [
            row[
                "trace_id"
            ]
            for row in trace_records
        ],
    }

    trace_package_digest = hashlib.sha256(
        json.dumps(
            package_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    trace_package = {
        "package_schema":
            "authority_provenance_evidence_trace_package_v1",

        "package_version":
            "v1",

        "package_id":
            "authtracepkg:v1:"
            + trace_package_digest,

        "package_digest":
            trace_package_digest,

        "workspace_id":
            workspace_id,

        "source_guard_package_id":
            guard_package.get(
                "package_id"
            ),

        "source_guard_package_digest":
            guard_package.get(
                "package_digest"
            ),

        "source_scoring_package_id":
            scoring_package.get(
                "package_id"
            ),

        "source_scoring_package_digest":
            scoring_package.get(
                "package_digest"
            ),

        "trace_record_count":
            len(
                trace_records
            ),

        "trace_records":
            trace_records,

        "authority_provenance_built":
            True,

        "authority_evidence_trace_built":
            True,

        "score_identity_verified":
            True,

        "guard_identity_verified":
            True,

        "authority_scores_preserved":
            True,

        "authority_classes_preserved":
            True,

        "guard_outcomes_preserved":
            True,

        "external_authority_lookup_performed":
            False,

        "external_target_selected":
            False,

        "truth_assessment_performed":
            False,

        "claim_integrity_decision_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "active_target_set_ownership_preserved":
            True,

        "external_authority_partition_preserved":
            True,

        "external_route_eligibility_preserved":
            True,

        "external_resolver_ownership_preserved":
            True,

        "unsupported_authority_invention_performed":
            False,

        "trace_policy":
            "FULL_AUTHORITY_PROVENANCE_AND_EVIDENCE_TRACE_V1",
    }

    return {
        "schema_version":
            "authority_provenance_evidence_trace_result_v1",

        "version":
            AUTHORITY_INTELLIGENCE_VERSION,

        "phase":
            AUTHORITY_INTELLIGENCE_PHASE,

        "patch":
            "4.6.24I",

        "status":
            "AUTHORITY_PROVENANCE_AND_EVIDENCE_TRACE_BUILT",

        "workspace_id":
            workspace_id,

        "authority_trace_package":
            trace_package,

        "authority_guard_package":
            deepcopy(
                guard_package
            ),

        "authority_scoring_package":
            deepcopy(
                scoring_package
            ),

        "source_guard_result":
            deepcopy(
                guard_result
            ),

        "processing_boundaries": {
            **deepcopy(
                boundaries
            ),

            "authority_provenance_built":
                True,
        },

        "authority_policy":
            "CERTIFIED_AUTHORITY_PROVENANCE_AND_EVIDENCE_TRACE",

        "next_stage":
            "final_authority_result",
    }

# =====================================================================
# ACTIVE_TARGET_SET_AUTHORITY_MIGRATION_2026_09_21
#
# Canonical Authority ownership:
#   ACTIVE_TARGET_SET
#     -> target_partition = EXTERNAL_AUTHORITY
#     -> route_eligibility includes EXTERNAL
#     -> Authority evaluates/enriches
#     -> EXTERNAL_TARGET_RESOLVER selects final external target
#
# External URL discovery/routing into Active Target Set is intentionally
# outside this migration and will be designed separately.
# =====================================================================

def build_final_authority_result_v1(
    trace_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.24J ? Final Authority Result.

    Builds the certified final Authority result from the certified
    4.6.24I provenance/evidence trace.

    This stage preserves:
    - Authority score
    - Authority class
    - Confidence
    - Integrity guard outcome
    - Provenance/evidence trace
    - Active Target Set ownership
    - EXTERNAL_AUTHORITY partition
    - EXTERNAL route eligibility
    - External Resolver final-selection ownership

    It does not:
    - discover external URLs,
    - create targets,
    - select the final external URL,
    - adjudicate truth,
    - decide claim integrity,
    - write Semantic Memory,
    - make linking decisions.
    """

    if not isinstance(
        trace_result,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "trace_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "authority_provenance_evidence_trace_result_v1",
        "authority_intelligence_version":
            AUTHORITY_INTELLIGENCE_VERSION,
        "phase":
            "4.6.24",
        "patch":
            "4.6.24I",
        "status":
            "AUTHORITY_PROVENANCE_AND_EVIDENCE_TRACE_BUILT",
        "policy":
            "CERTIFIED_AUTHORITY_PROVENANCE_AND_EVIDENCE_TRACE",
        "next":
            "final_authority_result",
    }

    for key, expected in expected_lifecycle.items():
        if trace_result.get(key) != expected:
            raise AuthorityIntelligenceError(
                f"Invalid 4.6.24I lifecycle field: {key}"
            )

    trace_package = trace_result.get(
        "authority_trace_package"
    )

    guard_package = trace_result.get(
        "authority_guard_package"
    )

    scoring_package = trace_result.get(
        "authority_scoring_package"
    )

    processing_boundaries = trace_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        trace_package,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "authority_trace_package must be a dictionary."
        )

    if not isinstance(
        guard_package,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "authority_guard_package must be a dictionary."
        )

    if not isinstance(
        scoring_package,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "authority_scoring_package must be a dictionary."
        )

    if not isinstance(
        processing_boundaries,
        dict,
    ):
        raise AuthorityIntelligenceError(
            "processing_boundaries must be a dictionary."
        )

    if (
        trace_package.get("schema")
        != "authority_provenance_evidence_trace_package_v1"
    ):
        raise AuthorityIntelligenceError(
            "Invalid Authority trace package schema."
        )

    required_true = (
        "authority_provenance_built",
        "authority_evidence_trace_built",
        "score_identity_verified",
        "guard_identity_verified",
        "authority_scores_preserved",
        "authority_classes_preserved",
        "guard_outcomes_preserved",
        "active_target_set_ownership_preserved",
        "external_authority_partition_preserved",
        "external_route_eligibility_preserved",
        "external_resolver_ownership_preserved",
    )

    for flag in required_true:
        if trace_package.get(flag) is not True:
            raise AuthorityIntelligenceError(
                f"Required trace preservation flag is not true: {flag}"
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
        if trace_package.get(flag) is not False:
            raise AuthorityIntelligenceError(
                f"Forbidden Authority operation detected: {flag}"
            )

    trace_records = trace_package.get(
        "authority_trace_records",
        trace_package.get(
            "trace_records",
            [],
        ),
    )

    if not isinstance(
        trace_records,
        list,
    ):
        raise AuthorityIntelligenceError(
            "Authority trace records must be a list."
        )

    expected_count = trace_package.get(
        "authority_trace_record_count",
        trace_package.get(
            "trace_record_count",
            len(trace_records),
        ),
    )

    if expected_count != len(trace_records):
        raise AuthorityIntelligenceError(
            "Authority trace record count mismatch."
        )

    final_records = []

    allowed_guard_outcomes = {
        "APPROVED",
        "CONDITIONALLY_APPROVED",
        "BLOCKED",
    }

    for trace in trace_records:

        if not isinstance(
            trace,
            dict,
        ):
            raise AuthorityIntelligenceError(
                "Authority trace record must be a dictionary."
            )

        if (
            trace.get("schema")
            != "authority_provenance_evidence_trace_record_v1"
        ):
            raise AuthorityIntelligenceError(
                "Invalid Authority trace record schema."
            )

        authority_score = trace.get(
            "authority_score"
        )

        authority_class = trace.get(
            "authority_class"
        )

        confidence = trace.get(
            "confidence"
        )

        guard_outcome = trace.get(
            "guard_outcome"
        )

        guard_reason = trace.get(
            "guard_reason"
        )

        if guard_outcome not in allowed_guard_outcomes:
            raise AuthorityIntelligenceError(
                "Invalid Authority guard outcome."
            )

        if authority_class in {
            "UNRESOLVED",
            "BLOCKED",
        }:
            final_disposition = (
                "NOT_AUTHORITY_ELIGIBLE"
            )

        elif guard_outcome == "APPROVED":
            final_disposition = (
                "AUTHORITATIVE"
            )

        elif (
            guard_outcome
            == "CONDITIONALLY_APPROVED"
        ):
            final_disposition = (
                "AUTHORITATIVE_WITH_CAUTION"
            )

        else:
            final_disposition = (
                "NOT_AUTHORITY_ELIGIBLE"
            )

        record_core = {
            "schema":
                "final_authority_record_v1",

            "authority_intelligence_version":
                AUTHORITY_INTELLIGENCE_VERSION,

            "phase":
                "4.6.24",

            "patch":
                "4.6.24J",

            "workspace_id":
                trace.get("workspace_id"),

            "subject_id":
                trace.get("subject_id"),

            "subject_type":
                trace.get("subject_type"),

            "source_url":
                trace.get("source_url"),

            "trace_id":
                trace.get("trace_id"),

            "trace_digest":
                trace.get("trace_digest"),

            "authority_score":
                authority_score,

            "authority_class":
                authority_class,

            "confidence":
                confidence,

            "guard_outcome":
                guard_outcome,

            "guard_reason":
                guard_reason,

            "triggered_signals":
                copy.deepcopy(
                    trace.get(
                        "triggered_signals",
                        [],
                    )
                ),

            "blocking_signals":
                copy.deepcopy(
                    trace.get(
                        "blocking_signals",
                        [],
                    )
                ),

            "conditional_signals":
                copy.deepcopy(
                    trace.get(
                        "conditional_signals",
                        [],
                    )
                ),

            "final_authority_disposition":
                final_disposition,

            "provenance_chain":
                copy.deepcopy(
                    trace.get(
                        "provenance_chain",
                        {},
                    )
                ),

            "evidence_trace":
                copy.deepcopy(
                    trace.get(
                        "evidence_trace",
                        {},
                    )
                ),

            "authority_score_preserved":
                True,

            "authority_class_preserved":
                True,

            "guard_outcome_preserved":
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

            "final_authority_result_built":
                True,

            "external_authority_lookup_performed":
                False,

            "external_target_selected":
                False,

            "truth_assessment_performed":
                False,

            "claim_integrity_decision_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "unsupported_authority_invention_performed":
                False,
        }

        canonical = json.dumps(
            record_core,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        digest = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

        record = {
            **record_core,
            "final_authority_id":
                f"authfinal:v1:{digest}",
            "final_authority_digest":
                digest,
        }

        final_records.append(
            record
        )

    package_core = {
        "schema":
            "final_authority_result_package_v1",

        "authority_intelligence_version":
            AUTHORITY_INTELLIGENCE_VERSION,

        "phase":
            "4.6.24",

        "patch":
            "4.6.24J",

        "workspace_id":
            trace_package.get("workspace_id"),

        "source_trace_package_id":
            trace_package.get(
                "authority_trace_package_id",
                trace_package.get(
                    "trace_package_id",
                ),
            ),

        "source_trace_package_digest":
            trace_package.get(
                "authority_trace_package_digest",
                trace_package.get(
                    "trace_package_digest",
                ),
            ),

        "final_authority_record_count":
            len(final_records),

        "final_authority_records":
            final_records,

        "authority_result_built":
            True,

        "authority_scores_preserved":
            True,

        "authority_classes_preserved":
            True,

        "guard_outcomes_preserved":
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

        "external_authority_lookup_performed":
            False,

        "external_target_selected":
            False,

        "truth_assessment_performed":
            False,

        "claim_integrity_decision_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "unsupported_authority_invention_performed":
            False,

        "final_policy":
            "CERTIFIED_AUTHORITY_RESULT_FOR_DOWNSTREAM_CONSUMPTION",
    }

    canonical_package = json.dumps(
        package_core,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    package_digest = hashlib.sha256(
        canonical_package.encode("utf-8")
    ).hexdigest()

    final_package = {
        **package_core,
        "final_authority_package_id":
            f"authfinalpkg:v1:{package_digest}",
        "final_authority_package_digest":
            package_digest,
    }

    return {
        "schema":
            "final_authority_result_v1",

        "authority_intelligence_version":
            AUTHORITY_INTELLIGENCE_VERSION,

        "phase":
            "4.6.24",

        "patch":
            "4.6.24J",

        "status":
            "FINAL_AUTHORITY_RESULT_BUILT",

        "final_authority_package":
            final_package,

        "authority_trace_package":
            copy.deepcopy(trace_package),

        "authority_guard_package":
            copy.deepcopy(guard_package),

        "authority_scoring_package":
            copy.deepcopy(scoring_package),

        "source_trace_result":
            copy.deepcopy(trace_result),

        "processing_boundaries": {
            "final_authority_result_built":
                True,

            "active_target_set_ownership_preserved":
                True,

            "external_authority_partition_preserved":
                True,

            "external_route_eligibility_preserved":
                True,

            "external_resolver_ownership_preserved":
                True,

            "external_authority_lookup_performed":
                False,

            "external_target_selected":
                False,

            "truth_assessment_performed":
                False,

            "claim_integrity_decision_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "unsupported_authority_invention_performed":
                False,
        },

        "policy":
            "CERTIFIED_FINAL_AUTHORITY_RESULT",

        "next":
            "full_authority_hard_certification",
    }
