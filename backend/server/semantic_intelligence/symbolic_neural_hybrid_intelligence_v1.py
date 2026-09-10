from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


class SymbolicNeuralHybridIntelligenceError(ValueError):
    """Raised when the canonical Symbolic-Neural Hybrid contract is violated."""


_SYMBOLIC_NEURAL_HYBRID_ARCHITECTURE_V1 = {
    "schema_version":
        "symbolic_neural_hybrid_architecture_v1",

    "intelligence_version":
        "symbolic_neural_hybrid_intelligence_v1",

    "phase":
        "4.6.15",

    "patch":
        "4.6.15C",

    "status":
        "SYMBOLIC_NEURAL_HYBRID_ARCHITECTURE_DEFINED",

    "architecture_scope":
        "ARTICLE_LOCAL_CERTIFIED_INTELLIGENCE_FUSION",

    "upstream_intelligence_layers": [
        "logical_intelligence",
        "causal_intelligence",
        "quantitative_intelligence",
        "procedural_intelligence",
        "analogical_intelligence",
        "similarity_intelligence",
        "temporal_intelligence",
        "uncertainty_intelligence",
    ],

    "symbolic_evidence_roles": {
        "logical_intelligence":
            "Preserve explicit logical relations, conditions, "
            "qualifications, contradictions, and discourse constraints.",

        "causal_intelligence":
            "Preserve certified cause-effect relations and causal direction.",

        "quantitative_intelligence":
            "Preserve certified numeric expressions, quantities, units, "
            "ranges, comparisons, and quantitative boundaries.",

        "procedural_intelligence":
            "Preserve certified procedures, participant roles, explicit "
            "steps, and procedural relations without inventing missing steps.",

        "temporal_intelligence":
            "Preserve certified temporal expressions, ordering, duration, "
            "frequency, and time-related constraints.",

        "uncertainty_intelligence":
            "Preserve certified source commitment, possibility, likelihood, "
            "approximation, limitation, and uncertainty boundaries.",
    },

    "neural_semantic_evidence_roles": {
        "analogical_intelligence":
            "Provide certified contextual analogy evidence without "
            "extending or inventing mappings.",

        "similarity_intelligence":
            "Provide certified semantic similarity and difference evidence "
            "without converting similarity into identity.",

        "article_context":
            "Provide contextual interpretation only from certified "
            "article-local evidence already supplied to this layer.",
    },

    "authority_policy": {
        "rule":
            "NEURAL_CONTEXT_MUST_NOT_OVERRIDE_CERTIFIED_SYMBOLIC_CONSTRAINTS",

        "symbolic_constraint_authority":
            "HARD_WHEN_EXPLICIT_AND_CERTIFIED",

        "neural_context_authority":
            "INTERPRETIVE_ONLY",

        "conflict_policy":
            "PRESERVE_CONFLICT_FOR_EXPLICIT_RESOLUTION",

        "uncertainty_preservation":
            "NEVER_STRENGTHEN_SOURCE_COMMITMENT",

        "causal_preservation":
            "NEVER_CREATE_OR_REVERSE_CAUSAL_DIRECTION",

        "temporal_preservation":
            "NEVER_INVENT_TEMPORAL_ORDER",

        "quantitative_preservation":
            "NEVER_INVENT_OR_RECALCULATE_QUANTITATIVE_FACTS",

        "procedural_preservation":
            "NEVER_INVENT_MISSING_STEPS_OR_PREREQUISITES",

        "logical_preservation":
            "NEVER_REMOVE_EXPLICIT_QUALIFICATION_OR_CONDITION",
    },

    "fusion_policy": {
        "fusion_type":
            "EVIDENCE_PRESERVING_GOVERNED_FUSION",

        "allowed":
            [
                "align_certified_evidence",
                "detect_agreement",
                "detect_conflict",
                "preserve_symbolic_constraints",
                "interpret_certified_context",
                "build_hybrid_reasoning_candidates",
                "consolidate_article_local_hybrid_evidence",
            ],

        "forbidden":
            [
                "rerun_upstream_specialist_intelligence",
                "invent_unstated_article_facts",
                "invent_new_causal_relations",
                "invent_numeric_probability",
                "perform_truth_assessment",
                "perform_external_authority_validation",
                "write_semantic_memory",
                "make_linking_decisions",
                "select_target_urls",
                "create_editor_highlights",
                "persist_hybrid_intelligence",
            ],
    },

    "processing_order": [
        "hybrid_intelligence_intake",
        "upstream_intelligence_normalization",
        "symbolic_evidence_preparation",
        "neural_semantic_evidence_preparation",
        "symbolic_neural_evidence_alignment",
        "agreement_conflict_detection",
        "hybrid_reasoning_candidate_construction",
        "symbolic_constraint_enforcement",
        "neural_context_interpretation",
        "hybrid_evidence_fusion",
        "contradiction_conflict_resolution",
        "hybrid_confidence_assessment",
        "reasoning_provenance_explainability_preparation",
        "duplicate_redundant_hybrid_resolution",
        "article_level_hybrid_consolidation",
        "final_symbolic_neural_hybrid_result",
        "symbolic_neural_hybrid_certification",
    ],

    "processing_boundaries": {
        "upstream_specialist_reasoning_reperformed":
            False,

        "new_article_fact_inference_performed":
            False,

        "numeric_probability_inference_performed":
            False,

        "truth_assessment_performed":
            False,

        "external_authority_check_performed":
            False,

        "semantic_memory_write_performed":
            False,

        "linking_decisions_performed":
            False,

        "target_resolution_performed":
            False,

        "editor_highlight_performed":
            False,

        "persistence_performed":
            False,
    },

    "persistence_policy":
        "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

    "next_stage":
        "hybrid_intelligence_intake",
}


def get_symbolic_neural_hybrid_architecture_v1(
) -> dict[str, Any]:
    """
    Return an isolated copy of the canonical Phase 4.6.15
    Symbolic-Neural Hybrid Intelligence architecture.
    """

    return deepcopy(
        _SYMBOLIC_NEURAL_HYBRID_ARCHITECTURE_V1
    )


# ============================================================================
# PATCH 4.6.15D â€” Hybrid Intelligence Intake
# ============================================================================

from collections.abc import Mapping


_REQUIRED_HYBRID_UPSTREAM_STATUSES = {
    "logical_intelligence":
        "LOGICAL_INTELLIGENCE_CERTIFIED",

    "causal_intelligence":
        "CAUSAL_INTELLIGENCE_CERTIFIED",

    "quantitative_intelligence":
        "QUANTITATIVE_INTELLIGENCE_CERTIFIED",

    "procedural_intelligence":
        "PROCEDURAL_INTELLIGENCE_CERTIFIED",

    "analogical_intelligence":
        "ANALOGICAL_INTELLIGENCE_CERTIFIED",

    "similarity_intelligence":
        "SIMILARITY_INTELLIGENCE_CERTIFIED",

    "temporal_intelligence":
        "TEMPORAL_INTELLIGENCE_CERTIFIED",

    "uncertainty_intelligence":
        "UNCERTAINTY_INTELLIGENCE_CERTIFIED",
}


def build_hybrid_intelligence_intake(
    upstream_intelligence_bundle: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Admit the already-certified upstream intelligence required by
    Symbolic-Neural Hybrid Intelligence.

    4.6.15D performs intake only.

    It does not:
    - rerun upstream reasoning
    - normalize upstream intelligence
    - prepare symbolic or semantic evidence
    - align evidence
    - detect agreement or conflict
    - construct hybrid candidates
    - enforce symbolic constraints
    - interpret neural/semantic context
    - fuse evidence
    - calculate hybrid confidence
    """

    if not isinstance(
        upstream_intelligence_bundle,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid intelligence intake requires an upstream "
            "intelligence mapping."
        )

    missing_layers = [
        layer
        for layer in _REQUIRED_HYBRID_UPSTREAM_STATUSES
        if layer not in upstream_intelligence_bundle
    ]

    if missing_layers:
        raise SymbolicNeuralHybridIntelligenceError(
            "Missing required upstream intelligence layer(s): "
            + ", ".join(missing_layers)
        )

    admitted_upstream: dict[str, Any] = {}

    for (
        layer_name,
        expected_status,
    ) in _REQUIRED_HYBRID_UPSTREAM_STATUSES.items():

        upstream_result = upstream_intelligence_bundle[
            layer_name
        ]

        if not isinstance(
            upstream_result,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} must provide a mapping result."
            )

        if (
            upstream_result.get("status")
            != expected_status
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} is not certified for hybrid "
                f"intelligence intake."
            )

        if (
            upstream_result.get("persistence_policy")
            != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} violates the required article-local "
                f"transient persistence boundary."
            )

        admitted_upstream[layer_name] = deepcopy(
            dict(upstream_result)
        )

    uncertainty_result = admitted_upstream[
        "uncertainty_intelligence"
    ]

    if (
        uncertainty_result.get("next_stage")
        != "symbolic_neural_hybrid_intelligence"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Uncertainty Intelligence does not provide the canonical "
            "handoff to symbolic_neural_hybrid_intelligence."
        )

    article_identity = uncertainty_result.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Canonical article_identity is missing from the immediate "
            "Uncertainty Intelligence handoff."
        )

    for (
        layer_name,
        upstream_result,
    ) in admitted_upstream.items():

        layer_article_identity = upstream_result.get(
            "article_identity"
        )

        if (
            layer_article_identity is not None
            and layer_article_identity != article_identity
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} belongs to a different article."
            )

    return {
        "schema_version":
            "symbolic_neural_hybrid_intake_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15D",

        "status":
            "HYBRID_INTELLIGENCE_INTAKE_READY",

        "article_identity":
            deepcopy(article_identity),

        "certified_upstream_intelligence":
            admitted_upstream,

        "intake_summary": {
            "required_upstream_layer_count":
                8,

            "admitted_upstream_layer_count":
                len(admitted_upstream),

            "all_required_layers_present":
                True,

            "all_upstream_results_certified":
                True,

            "article_identity_established":
                True,

            "immediate_handoff_verified":
                True,
        },

        "processing_boundaries": {
            "upstream_reasoning_reexecuted":
                False,

            "upstream_results_reclassified":
                False,

            "upstream_results_mutated":
                False,

            "normalization_performed":
                False,

            "symbolic_evidence_prepared":
                False,

            "semantic_evidence_prepared":
                False,

            "evidence_alignment_performed":
                False,

            "agreement_conflict_detection_performed":
                False,

            "hybrid_reasoning_performed":
                False,

            "symbolic_constraint_enforcement_performed":
                False,

            "neural_context_interpretation_performed":
                False,

            "hybrid_evidence_fusion_performed":
                False,

            "hybrid_confidence_calculated":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "upstream_intelligence_normalization",
    }


# ============================================================================
# PATCH 4.6.15E â€” Upstream Intelligence Normalization
# ============================================================================

def normalize_hybrid_upstream_intelligence(
    hybrid_intake: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Normalize the eight admitted certified upstream intelligence contracts
    into a common hybrid-layer envelope.

    4.6.15E performs structural normalization only.
    It does not classify evidence as symbolic/semantic, interpret findings,
    align evidence, detect conflict, construct candidates, or perform fusion.
    """

    if not isinstance(hybrid_intake, Mapping):
        raise SymbolicNeuralHybridIntelligenceError(
            "Upstream normalization requires the canonical hybrid intake."
        )

    if (
        hybrid_intake.get("status")
        != "HYBRID_INTELLIGENCE_INTAKE_READY"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid intake is not ready for upstream normalization."
        )

    if (
        hybrid_intake.get("next_stage")
        != "upstream_intelligence_normalization"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid intake does not hand off to upstream normalization."
        )

    article_identity = hybrid_intake.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid intake is missing article_identity."
        )

    admitted = hybrid_intake.get(
        "certified_upstream_intelligence"
    )

    if not isinstance(admitted, Mapping):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid intake is missing certified upstream intelligence."
        )

    missing_layers = [
        layer
        for layer in _REQUIRED_HYBRID_UPSTREAM_STATUSES
        if layer not in admitted
    ]

    if missing_layers:
        raise SymbolicNeuralHybridIntelligenceError(
            "Normalization input is missing required layer(s): "
            + ", ".join(missing_layers)
        )

    normalized_layers: dict[str, Any] = {}

    for (
        layer_name,
        expected_status,
    ) in _REQUIRED_HYBRID_UPSTREAM_STATUSES.items():

        source_result = admitted[layer_name]

        if not isinstance(source_result, Mapping):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} normalization source must be a mapping."
            )

        if (
            source_result.get("status")
            != expected_status
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} lost its certified status before normalization."
            )

        if (
            source_result.get("persistence_policy")
            != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} violates the hybrid persistence boundary."
            )

        source_article_identity = source_result.get(
            "article_identity"
        )

        if (
            source_article_identity is not None
            and source_article_identity != article_identity
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} article identity changed before normalization."
            )

        normalized_layers[layer_name] = {
            "source_layer":
                layer_name,

            "source_status":
                source_result.get("status"),

            "source_schema_version":
                source_result.get("schema_version"),

            "source_phase":
                source_result.get("phase"),

            "source_patch":
                source_result.get("patch"),

            "source_persistence_policy":
                source_result.get("persistence_policy"),

            "article_identity":
                deepcopy(article_identity),

            "certification":
                deepcopy(
                    source_result.get("certification")
                ),

            "source_payload":
                deepcopy(dict(source_result)),

            "normalization": {
                "structural_normalization_only":
                    True,

                "source_payload_preserved":
                    True,

                "semantic_interpretation_performed":
                    False,

                "evidence_role_assigned":
                    False,

                "upstream_reasoning_reexecuted":
                    False,
            },
        }

    return {
        "schema_version":
            "symbolic_neural_hybrid_normalized_upstream_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15E",

        "status":
            "HYBRID_UPSTREAM_INTELLIGENCE_NORMALIZED",

        "article_identity":
            deepcopy(article_identity),

        "normalized_upstream_intelligence":
            normalized_layers,

        "normalization_summary": {
            "required_layer_count":
                8,

            "normalized_layer_count":
                len(normalized_layers),

            "all_layers_normalized":
                len(normalized_layers) == 8,

            "source_payloads_preserved":
                True,

            "evidence_roles_assigned":
                False,
        },

        "processing_boundaries": {
            "upstream_reasoning_reexecuted":
                False,

            "semantic_interpretation_performed":
                False,

            "symbolic_evidence_prepared":
                False,

            "semantic_evidence_prepared":
                False,

            "evidence_alignment_performed":
                False,

            "agreement_conflict_detection_performed":
                False,

            "hybrid_candidates_constructed":
                False,

            "symbolic_constraints_enforced":
                False,

            "hybrid_fusion_performed":
                False,

            "hybrid_confidence_calculated":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "symbolic_evidence_preparation",
    }


# ============================================================================
# PATCH 4.6.15F â€” Symbolic Evidence Preparation
# ============================================================================

_SYMBOLIC_SOURCE_LAYERS = (
    "logical_intelligence",
    "causal_intelligence",
    "quantitative_intelligence",
    "procedural_intelligence",
    "temporal_intelligence",
    "uncertainty_intelligence",
)


_SYMBOLIC_PRESERVATION_RULES = {
    "logical_intelligence":
        "NEVER_REMOVE_EXPLICIT_QUALIFICATION_OR_CONDITION",

    "causal_intelligence":
        "NEVER_CREATE_OR_REVERSE_CAUSAL_DIRECTION",

    "quantitative_intelligence":
        "NEVER_INVENT_OR_RECALCULATE_QUANTITATIVE_FACTS",

    "procedural_intelligence":
        "NEVER_INVENT_MISSING_STEPS_OR_PREREQUISITES",

    "temporal_intelligence":
        "NEVER_INVENT_TEMPORAL_ORDER",

    "uncertainty_intelligence":
        "NEVER_STRENGTHEN_SOURCE_COMMITMENT",
}


def prepare_symbolic_hybrid_evidence(
    normalized_upstream: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Prepare the certified symbolic evidence side of the hybrid layer.

    4.6.15F performs evidence preparation only.

    It does not:
    - infer new symbolic facts
    - reinterpret upstream findings
    - process neural/semantic evidence
    - align symbolic and semantic evidence
    - detect agreement or conflict
    - enforce constraints against candidates
    - perform evidence fusion
    - calculate hybrid confidence
    """

    if not isinstance(normalized_upstream, Mapping):
        raise SymbolicNeuralHybridIntelligenceError(
            "Symbolic evidence preparation requires normalized upstream "
            "intelligence."
        )

    if (
        normalized_upstream.get("status")
        != "HYBRID_UPSTREAM_INTELLIGENCE_NORMALIZED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Upstream intelligence is not normalized for symbolic "
            "evidence preparation."
        )

    if (
        normalized_upstream.get("next_stage")
        != "symbolic_evidence_preparation"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Normalized upstream intelligence does not hand off to "
            "symbolic evidence preparation."
        )

    article_identity = normalized_upstream.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Normalized upstream intelligence is missing article_identity."
        )

    normalized_layers = normalized_upstream.get(
        "normalized_upstream_intelligence"
    )

    if not isinstance(normalized_layers, Mapping):
        raise SymbolicNeuralHybridIntelligenceError(
            "Normalized upstream intelligence is missing its layer map."
        )

    architecture_roles = (
        _SYMBOLIC_NEURAL_HYBRID_ARCHITECTURE_V1.get(
            "symbolic_evidence_roles",
            {},
        )
    )

    symbolic_evidence_sources: dict[str, Any] = {}

    for layer_name in _SYMBOLIC_SOURCE_LAYERS:

        normalized_source = normalized_layers.get(
            layer_name
        )

        if not isinstance(normalized_source, Mapping):
            raise SymbolicNeuralHybridIntelligenceError(
                f"Missing normalized symbolic source: {layer_name}."
            )

        expected_status = _REQUIRED_HYBRID_UPSTREAM_STATUSES[
            layer_name
        ]

        if (
            normalized_source.get("source_status")
            != expected_status
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} lost its certified source status."
            )

        if (
            normalized_source.get(
                "source_persistence_policy"
            )
            != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} violates the symbolic evidence "
                f"persistence boundary."
            )

        source_article_identity = normalized_source.get(
            "article_identity"
        )

        if (
            source_article_identity is not None
            and source_article_identity != article_identity
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} belongs to a different article."
            )

        role_definition = architecture_roles.get(
            layer_name
        )

        if not role_definition:
            raise SymbolicNeuralHybridIntelligenceError(
                f"No frozen symbolic evidence role exists for "
                f"{layer_name}."
            )

        preservation_rule = _SYMBOLIC_PRESERVATION_RULES.get(
            layer_name
        )

        if not preservation_rule:
            raise SymbolicNeuralHybridIntelligenceError(
                f"No symbolic preservation rule exists for "
                f"{layer_name}."
            )

        symbolic_evidence_sources[layer_name] = {
            "evidence_side":
                "SYMBOLIC",

            "source_layer":
                layer_name,

            "source_status":
                normalized_source.get(
                    "source_status"
                ),

            "article_identity":
                deepcopy(article_identity),

            "role_definition":
                role_definition,

            "preservation_rule":
                preservation_rule,

            "constraint_authority":
                "HARD_WHEN_EXPLICIT_AND_CERTIFIED",

            "normalized_source":
                deepcopy(dict(normalized_source)),

            "preparation": {
                "symbolic_role_assigned":
                    True,

                "source_payload_preserved":
                    True,

                "new_symbolic_fact_inferred":
                    False,

                "source_commitment_strengthened":
                    False,

                "semantic_interpretation_performed":
                    False,

                "constraint_enforcement_performed":
                    False,
            },
        }

    return {
        "schema_version":
            "symbolic_neural_hybrid_symbolic_evidence_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15F",

        "status":
            "HYBRID_SYMBOLIC_EVIDENCE_PREPARED",

        "article_identity":
            deepcopy(article_identity),

        "symbolic_evidence_sources":
            symbolic_evidence_sources,

        "symbolic_evidence_summary": {
            "expected_symbolic_source_count":
                6,

            "prepared_symbolic_source_count":
                len(symbolic_evidence_sources),

            "all_symbolic_sources_prepared":
                len(symbolic_evidence_sources) == 6,

            "symbolic_constraint_authority":
                "HARD_WHEN_EXPLICIT_AND_CERTIFIED",

            "new_symbolic_intelligence_created":
                False,
        },

        "processing_boundaries": {
            "upstream_reasoning_reexecuted":
                False,

            "new_symbolic_facts_inferred":
                False,

            "semantic_evidence_prepared":
                False,

            "semantic_interpretation_performed":
                False,

            "evidence_alignment_performed":
                False,

            "agreement_conflict_detection_performed":
                False,

            "hybrid_candidates_constructed":
                False,

            "symbolic_constraint_enforcement_performed":
                False,

            "hybrid_evidence_fusion_performed":
                False,

            "hybrid_confidence_calculated":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "neural_semantic_evidence_preparation",
    }


# ============================================================================
# PATCH 4.6.15G â€” Neural / Semantic Evidence Preparation
# ============================================================================

_NEURAL_SEMANTIC_SOURCE_LAYERS = (
    "analogical_intelligence",
    "similarity_intelligence",
)


def prepare_neural_semantic_hybrid_evidence(
    normalized_upstream: Mapping[str, Any],
    symbolic_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Prepare the governed neural/semantic evidence side of the hybrid layer.

    4.6.15G does not perform neural interpretation. It prepares certified
    semantic/contextual evidence and preserves the completed symbolic side
    for the later alignment stage.
    """

    if not isinstance(normalized_upstream, Mapping):
        raise SymbolicNeuralHybridIntelligenceError(
            "Neural/semantic evidence preparation requires normalized "
            "upstream intelligence."
        )

    if (
        normalized_upstream.get("status")
        != "HYBRID_UPSTREAM_INTELLIGENCE_NORMALIZED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Upstream intelligence is not normalized."
        )

    if not isinstance(symbolic_evidence, Mapping):
        raise SymbolicNeuralHybridIntelligenceError(
            "Neural/semantic preparation requires the completed "
            "symbolic evidence result."
        )

    if (
        symbolic_evidence.get("status")
        != "HYBRID_SYMBOLIC_EVIDENCE_PREPARED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Symbolic evidence has not been prepared."
        )

    if (
        symbolic_evidence.get("next_stage")
        != "neural_semantic_evidence_preparation"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Symbolic evidence does not hand off to neural/semantic "
            "evidence preparation."
        )

    article_identity = normalized_upstream.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Normalized upstream intelligence is missing article_identity."
        )

    if (
        symbolic_evidence.get("article_identity")
        != article_identity
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Symbolic and normalized upstream evidence belong to "
            "different articles."
        )

    normalized_layers = normalized_upstream.get(
        "normalized_upstream_intelligence"
    )

    if not isinstance(normalized_layers, Mapping):
        raise SymbolicNeuralHybridIntelligenceError(
            "Normalized upstream layer map is missing."
        )

    semantic_roles = (
        _SYMBOLIC_NEURAL_HYBRID_ARCHITECTURE_V1.get(
            "neural_semantic_evidence_roles",
            {},
        )
    )

    neural_semantic_sources: dict[str, Any] = {}

    for layer_name in _NEURAL_SEMANTIC_SOURCE_LAYERS:

        normalized_source = normalized_layers.get(
            layer_name
        )

        if not isinstance(normalized_source, Mapping):
            raise SymbolicNeuralHybridIntelligenceError(
                f"Missing normalized semantic source: {layer_name}."
            )

        expected_status = _REQUIRED_HYBRID_UPSTREAM_STATUSES[
            layer_name
        ]

        if (
            normalized_source.get("source_status")
            != expected_status
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} lost its certified source status."
            )

        if (
            normalized_source.get("source_persistence_policy")
            != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} violates the article-local semantic "
                "evidence boundary."
            )

        if (
            normalized_source.get("article_identity")
            != article_identity
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} belongs to a different article."
            )

        role_definition = semantic_roles.get(
            layer_name
        )

        if not role_definition:
            raise SymbolicNeuralHybridIntelligenceError(
                f"No frozen neural/semantic evidence role exists for "
                f"{layer_name}."
            )

        neural_semantic_sources[layer_name] = {
            "evidence_side":
                "NEURAL_SEMANTIC",

            "source_layer":
                layer_name,

            "source_status":
                normalized_source.get("source_status"),

            "article_identity":
                deepcopy(article_identity),

            "role_definition":
                role_definition,

            "authority":
                "INTERPRETIVE_ONLY",

            "normalized_source":
                deepcopy(dict(normalized_source)),

            "preparation": {
                "semantic_role_assigned":
                    True,

                "source_payload_preserved":
                    True,

                "semantic_interpretation_performed":
                    False,

                "new_semantic_fact_inferred":
                    False,

                "symbolic_constraint_overridden":
                    False,

                "external_model_called":
                    False,
            },
        }

    article_context_role = semantic_roles.get(
        "article_context"
    )

    if not article_context_role:
        raise SymbolicNeuralHybridIntelligenceError(
            "Frozen article_context semantic role is missing."
        )

    neural_semantic_sources["article_context"] = {
        "evidence_side":
            "NEURAL_SEMANTIC",

        "source_layer":
            "article_context",

        "article_identity":
            deepcopy(article_identity),

        "role_definition":
            article_context_role,

        "authority":
            "INTERPRETIVE_ONLY",

        "context_access_policy":
            "CERTIFIED_ARTICLE_LOCAL_EVIDENCE_ONLY",

        "external_knowledge_allowed":
            False,

        "external_model_required":
            False,

        "preparation": {
            "context_boundary_prepared":
                True,

            "semantic_interpretation_performed":
                False,

            "new_context_inferred":
                False,

            "external_knowledge_added":
                False,
        },
    }

    return {
        "schema_version":
            "symbolic_neural_hybrid_neural_semantic_evidence_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15G",

        "status":
            "HYBRID_NEURAL_SEMANTIC_EVIDENCE_PREPARED",

        "article_identity":
            deepcopy(article_identity),

        "symbolic_evidence":
            deepcopy(dict(symbolic_evidence)),

        "neural_semantic_evidence_sources":
            neural_semantic_sources,

        "neural_semantic_evidence_summary": {
            "certified_semantic_source_count":
                2,

            "article_context_boundary_prepared":
                True,

            "prepared_semantic_entry_count":
                len(neural_semantic_sources),

            "semantic_authority":
                "INTERPRETIVE_ONLY",

            "external_model_called":
                False,

            "new_semantic_intelligence_created":
                False,
        },

        "processing_boundaries": {
            "upstream_reasoning_reexecuted":
                False,

            "new_semantic_facts_inferred":
                False,

            "neural_context_interpretation_performed":
                False,

            "evidence_alignment_performed":
                False,

            "agreement_conflict_detection_performed":
                False,

            "hybrid_candidates_constructed":
                False,

            "symbolic_constraint_enforcement_performed":
                False,

            "hybrid_evidence_fusion_performed":
                False,

            "hybrid_confidence_calculated":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "symbolic_neural_evidence_alignment",
    }


# ============================================================================
# PATCH 4.6.15H â€” Symbolic-Neural Evidence Alignment
# ============================================================================

_HYBRID_ALIGNMENT_COLLECTIONS = {
    "logical_intelligence": (
        "logical_claim_units",
    ),
    "causal_intelligence": (
        "representative_causal_candidates",
        "cause_effect_candidates",
    ),
    "quantitative_intelligence": (
        "representative_quantitative_candidates",
        "quantitative_candidates",
    ),
    "procedural_intelligence": (
        "representative_procedural_candidates",
        "procedural_candidates",
    ),
    "temporal_intelligence": (
        "temporal_candidates",
    ),
    "uncertainty_intelligence": (
        "uncertainty_candidates",
    ),
    "analogical_intelligence": (
        "representative_analogical_candidates",
        "analogical_candidates",
    ),
    "similarity_intelligence": (
        "representative_similarity_candidates",
        "similarity_candidates",
    ),
}


def _hybrid_collect_grounding_anchors(
    value: Any,
) -> set[str]:
    """
    Extract explicit grounding anchors only.

    No embeddings, fuzzy matching, semantic equivalence, or inferred
    proposition identity is used.
    """

    anchors: set[str] = set()

    def walk(item: Any) -> None:
        if isinstance(item, Mapping):

            lower_map = {
                str(key).lower(): val
                for key, val in item.items()
            }

            for start_key, end_key, label in (
                ("start_char", "end_char", "CHAR_RANGE"),
                ("char_start", "char_end", "CHAR_RANGE"),
                ("token_start", "token_end", "TOKEN_RANGE"),
            ):
                if (
                    start_key in lower_map
                    and end_key in lower_map
                    and lower_map[start_key] is not None
                    and lower_map[end_key] is not None
                ):
                    anchors.add(
                        f"{label}:"
                        f"{lower_map[start_key]}:"
                        f"{lower_map[end_key]}"
                    )

            for key, nested in item.items():
                key_lower = str(key).lower()

                values = (
                    nested
                    if isinstance(nested, (list, tuple, set))
                    else [nested]
                )

                for scalar in values:
                    if isinstance(
                        scalar,
                        (str, int, float),
                    ):
                        scalar_text = " ".join(
                            str(scalar).split()
                        )

                        if not scalar_text:
                            continue

                        if (
                            key_lower.endswith("claim_unit_id")
                            or key_lower.endswith("claim_unit_ids")
                            or key_lower == "claim_unit_id"
                        ):
                            anchors.add(
                                f"CLAIM_UNIT:{scalar_text}"
                            )

                        elif "sentence_id" in key_lower:
                            anchors.add(
                                f"SENTENCE:{scalar_text}"
                            )

                        elif (
                            key_lower.endswith("span_id")
                            or key_lower == "span_id"
                            or key_lower == "source_span_id"
                        ):
                            anchors.add(
                                f"SPAN:{scalar_text}"
                            )

                        elif key_lower in {
                            "claim_text",
                            "sentence_text",
                            "evidence_text",
                            "source_text",
                            "target_text",
                        }:
                            anchors.add(
                                f"EXACT_TEXT:{scalar_text}"
                            )

                walk(nested)

        elif isinstance(item, (list, tuple, set)):
            for nested in item:
                walk(nested)

    walk(value)

    return anchors


def _hybrid_get_evidence_collection(
    source_payload: Mapping[str, Any],
    layer_name: str,
) -> tuple[str, list[Any]]:

    collection_names = _HYBRID_ALIGNMENT_COLLECTIONS.get(
        layer_name,
        (),
    )

    first_existing_empty: tuple[str, list[Any]] | None = None

    for collection_name in collection_names:
        collection = source_payload.get(
            collection_name
        )

        if not isinstance(collection, list):
            continue

        if collection:
            return (
                collection_name,
                collection,
            )

        if first_existing_empty is None:
            first_existing_empty = (
                collection_name,
                collection,
            )

    if first_existing_empty is not None:
        return first_existing_empty

    return (
        collection_names[0]
        if collection_names
        else "unknown",
        [],
    )


def align_symbolic_neural_hybrid_evidence(
    neural_semantic_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Align prepared symbolic and neural/semantic evidence using only
    explicit article-local grounding shared by the evidence records.

    4.6.15H does not decide agreement, conflict, truth, or fusion.
    """

    if not isinstance(
        neural_semantic_evidence,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Evidence alignment requires the canonical G result."
        )

    if (
        neural_semantic_evidence.get("status")
        != "HYBRID_NEURAL_SEMANTIC_EVIDENCE_PREPARED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Neural/semantic evidence has not been prepared."
        )

    if (
        neural_semantic_evidence.get("next_stage")
        != "symbolic_neural_evidence_alignment"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "G does not hand off to symbolic-neural evidence alignment."
        )

    article_identity = neural_semantic_evidence.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Alignment input is missing article_identity."
        )

    symbolic_result = neural_semantic_evidence.get(
        "symbolic_evidence"
    )

    if not isinstance(symbolic_result, Mapping):
        raise SymbolicNeuralHybridIntelligenceError(
            "Prepared symbolic evidence is missing."
        )

    if (
        symbolic_result.get("status")
        != "HYBRID_SYMBOLIC_EVIDENCE_PREPARED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Carried symbolic evidence is not canonical."
        )

    if (
        symbolic_result.get("article_identity")
        != article_identity
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Symbolic and semantic evidence belong to different articles."
        )

    symbolic_sources = symbolic_result.get(
        "symbolic_evidence_sources"
    )

    semantic_sources = neural_semantic_evidence.get(
        "neural_semantic_evidence_sources"
    )

    if not isinstance(symbolic_sources, Mapping):
        raise SymbolicNeuralHybridIntelligenceError(
            "Symbolic evidence source map is missing."
        )

    if not isinstance(semantic_sources, Mapping):
        raise SymbolicNeuralHybridIntelligenceError(
            "Neural/semantic evidence source map is missing."
        )

    symbolic_records: list[dict[str, Any]] = []
    semantic_records: list[dict[str, Any]] = []

    for layer_name in _SYMBOLIC_SOURCE_LAYERS:

        source_wrapper = symbolic_sources.get(
            layer_name
        )

        if not isinstance(source_wrapper, Mapping):
            raise SymbolicNeuralHybridIntelligenceError(
                f"Missing symbolic source for alignment: {layer_name}."
            )

        normalized_source = source_wrapper.get(
            "normalized_source"
        )

        if not isinstance(normalized_source, Mapping):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} is missing its normalized source."
            )

        source_payload = normalized_source.get(
            "source_payload"
        )

        if not isinstance(source_payload, Mapping):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} is missing its certified source payload."
            )

        collection_name, collection = (
            _hybrid_get_evidence_collection(
                source_payload,
                layer_name,
            )
        )

        for index, evidence in enumerate(collection):

            evidence_id = (
                f"SYMBOLIC:"
                f"{layer_name}:"
                f"{collection_name}:"
                f"{index}"
            )

            symbolic_records.append({
                "evidence_id":
                    evidence_id,

                "evidence_side":
                    "SYMBOLIC",

                "source_layer":
                    layer_name,

                "source_collection":
                    collection_name,

                "source_index":
                    index,

                "grounding_anchors":
                    sorted(
                        _hybrid_collect_grounding_anchors(
                            evidence
                        )
                    ),

                "evidence":
                    deepcopy(evidence),
            })

    for layer_name in _NEURAL_SEMANTIC_SOURCE_LAYERS:

        source_wrapper = semantic_sources.get(
            layer_name
        )

        if not isinstance(source_wrapper, Mapping):
            raise SymbolicNeuralHybridIntelligenceError(
                f"Missing semantic source for alignment: {layer_name}."
            )

        normalized_source = source_wrapper.get(
            "normalized_source"
        )

        if not isinstance(normalized_source, Mapping):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} is missing its normalized source."
            )

        source_payload = normalized_source.get(
            "source_payload"
        )

        if not isinstance(source_payload, Mapping):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{layer_name} is missing its certified source payload."
            )

        collection_name, collection = (
            _hybrid_get_evidence_collection(
                source_payload,
                layer_name,
            )
        )

        for index, evidence in enumerate(collection):

            evidence_id = (
                f"NEURAL_SEMANTIC:"
                f"{layer_name}:"
                f"{collection_name}:"
                f"{index}"
            )

            semantic_records.append({
                "evidence_id":
                    evidence_id,

                "evidence_side":
                    "NEURAL_SEMANTIC",

                "source_layer":
                    layer_name,

                "source_collection":
                    collection_name,

                "source_index":
                    index,

                "grounding_anchors":
                    sorted(
                        _hybrid_collect_grounding_anchors(
                            evidence
                        )
                    ),

                "evidence":
                    deepcopy(evidence),
            })

    alignment_pairs: list[dict[str, Any]] = []

    aligned_symbolic_ids: set[str] = set()
    aligned_semantic_ids: set[str] = set()

    for symbolic_record in symbolic_records:

        symbolic_anchors = set(
            symbolic_record[
                "grounding_anchors"
            ]
        )

        if not symbolic_anchors:
            continue

        for semantic_record in semantic_records:

            semantic_anchors = set(
                semantic_record[
                    "grounding_anchors"
                ]
            )

            shared_anchors = sorted(
                symbolic_anchors
                & semantic_anchors
            )

            if not shared_anchors:
                continue

            strong_shared = [
                anchor
                for anchor in shared_anchors
                if (
                    anchor.startswith("CLAIM_UNIT:")
                    or anchor.startswith("SPAN:")
                    or anchor.startswith("CHAR_RANGE:")
                    or anchor.startswith("TOKEN_RANGE:")
                    or anchor.startswith("EXACT_TEXT:")
                )
            ]

            sentence_shared = [
                anchor
                for anchor in shared_anchors
                if anchor.startswith("SENTENCE:")
            ]

            if strong_shared:
                alignment_basis = (
                    "EXPLICIT_SHARED_GROUNDING"
                )
            elif sentence_shared:
                alignment_basis = (
                    "SAME_SENTENCE_GROUNDING"
                )
            else:
                continue

            pair_id = (
                f"ALIGNMENT:"
                f"{len(alignment_pairs) + 1}"
            )

            alignment_pairs.append({
                "alignment_id":
                    pair_id,

                "symbolic_evidence_id":
                    symbolic_record[
                        "evidence_id"
                    ],

                "neural_semantic_evidence_id":
                    semantic_record[
                        "evidence_id"
                    ],

                "alignment_basis":
                    alignment_basis,

                "shared_grounding_anchors":
                    shared_anchors,

                "agreement_assessed":
                    False,

                "conflict_assessed":
                    False,

                "fusion_performed":
                    False,
            })

            aligned_symbolic_ids.add(
                symbolic_record[
                    "evidence_id"
                ]
            )

            aligned_semantic_ids.add(
                semantic_record[
                    "evidence_id"
                ]
            )

    unaligned_symbolic_ids = [
        record["evidence_id"]
        for record in symbolic_records
        if record["evidence_id"]
        not in aligned_symbolic_ids
    ]

    unaligned_semantic_ids = [
        record["evidence_id"]
        for record in semantic_records
        if record["evidence_id"]
        not in aligned_semantic_ids
    ]

    article_context = semantic_sources.get(
        "article_context"
    )

    return {
        "schema_version":
            "symbolic_neural_hybrid_evidence_alignment_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15H",

        "status":
            "HYBRID_EVIDENCE_ALIGNED",

        "article_identity":
            deepcopy(article_identity),

        "symbolic_evidence_records":
            symbolic_records,

        "neural_semantic_evidence_records":
            semantic_records,

        "alignment_pairs":
            alignment_pairs,

        "unaligned_symbolic_evidence_ids":
            unaligned_symbolic_ids,

        "unaligned_neural_semantic_evidence_ids":
            unaligned_semantic_ids,

        "article_context_boundary":
            deepcopy(article_context),

        "alignment_summary": {
            "symbolic_evidence_record_count":
                len(symbolic_records),

            "neural_semantic_evidence_record_count":
                len(semantic_records),

            "alignment_pair_count":
                len(alignment_pairs),

            "aligned_symbolic_evidence_count":
                len(aligned_symbolic_ids),

            "aligned_neural_semantic_evidence_count":
                len(aligned_semantic_ids),

            "semantic_equivalence_guessing_performed":
                False,

            "embedding_alignment_performed":
                False,

            "fuzzy_alignment_performed":
                False,

            "section_only_alignment_allowed":
                False,
        },

        "processing_boundaries": {
            "explicit_grounding_alignment_performed":
                True,

            "agreement_detection_performed":
                False,

            "conflict_detection_performed":
                False,

            "hybrid_candidates_constructed":
                False,

            "symbolic_constraint_enforcement_performed":
                False,

            "neural_context_interpretation_performed":
                False,

            "hybrid_evidence_fusion_performed":
                False,

            "hybrid_confidence_calculated":
                False,

            "new_article_fact_inference_performed":
                False,

            "semantic_equivalence_inference_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "agreement_conflict_detection",
    }



# ============================================================================
# PATCH 4.6.15I — Agreement / Conflict Detection
# ============================================================================

_HYBRID_EXPLICIT_COMPARABLE_FIELDS = {
    "logical_intelligence": {
        "polarity",
        "negated",
        "is_negated",
        "source_has_explicit_condition",
        "target_has_explicit_condition",
        "explicit_finalized_contrast",
    },

    "causal_intelligence": {
        "polarity",
        "negated",
        "is_negated",
        "causal_direction",
        "cause_before_effect",
        "effect_before_cause",
    },

    "quantitative_intelligence": {
        "polarity",
        "negated",
        "is_negated",
        "normalized_value",
        "normalized_values",
        "canonical_unit",
        "unit_symbol",
        "rate_denominator_unit",
        "quantitative_direction",
        "comparison_orientation",
        "comparison_present",
        "directional_change_present",
    },

    "procedural_intelligence": {
        "polarity",
        "negated",
        "is_negated",
        "conditional_frame_present",
        "termination_condition_present",
    },

    "temporal_intelligence": {
        "polarity",
        "negated",
        "is_negated",
        "temporal_value_kind",
        "normalized_value",
        "normalized_values",
        "canonical_unit",
        "direction",
    },

    "uncertainty_intelligence": {
        "polarity",
        "negated",
        "is_negated",
        "uncertainty_type",
        "commitment_class",
        "certainty_class",
        "likelihood_class",
        "possibility_class",
        "contains_explicit_uncertainty",
    },
}


def _hybrid_freeze_explicit_fact_value(
    value: Any,
) -> Any:
    """
    Convert an explicit certified value into a deterministic comparable
    representation without semantic transformation.
    """

    if isinstance(value, Mapping):
        return tuple(
            sorted(
                (
                    str(key),
                    _hybrid_freeze_explicit_fact_value(
                        nested
                    ),
                )
                for key, nested in value.items()
            )
        )

    if isinstance(value, (list, tuple)):
        return tuple(
            _hybrid_freeze_explicit_fact_value(
                item
            )
            for item in value
        )

    if isinstance(value, set):
        return tuple(
            sorted(
                (
                    _hybrid_freeze_explicit_fact_value(
                        item
                    )
                    for item in value
                ),
                key=repr,
            )
        )

    if isinstance(value, str):
        return " ".join(
            value.split()
        )

    return value


def _hybrid_unique_explicit_values(
    values: list[Any],
) -> list[Any]:

    unique_values: list[Any] = []
    seen: set[Any] = set()

    for value in values:

        frozen = _hybrid_freeze_explicit_fact_value(
            value
        )

        if frozen in seen:
            continue

        seen.add(
            frozen
        )

        unique_values.append(
            deepcopy(value)
        )

    return unique_values


def _hybrid_extract_explicit_comparable_facts(
    evidence: Any,
    symbolic_layer: str,
) -> dict[str, list[Any]]:
    """
    Extract only fields explicitly approved as comparable for the
    symbolic evidence domain.

    The semantic evidence is evaluated against the symbolic layer's
    field policy so unrelated reasoning domains are never compared.
    """

    approved_fields = (
        _HYBRID_EXPLICIT_COMPARABLE_FIELDS.get(
            symbolic_layer,
            set(),
        )
    )

    facts: dict[str, list[Any]] = {}

    def walk(item: Any) -> None:

        if isinstance(item, Mapping):

            for key, value in item.items():

                key_text = str(
                    key
                ).lower()

                if (
                    key_text in approved_fields
                    and value is not None
                ):
                    facts.setdefault(
                        key_text,
                        [],
                    ).append(
                        deepcopy(value)
                    )

                walk(
                    value
                )

        elif isinstance(
            item,
            (list, tuple, set),
        ):
            for nested in item:
                walk(
                    nested
                )

    walk(
        evidence
    )

    return {
        field_name:
            _hybrid_unique_explicit_values(
                values
            )
        for field_name, values in facts.items()
    }


def _hybrid_compare_explicit_fact_sets(
    symbolic_values: list[Any],
    semantic_values: list[Any],
) -> str:
    """
    Compare explicit certified values only.

    Returns:
    - AGREEMENT
    - CONFLICT
    - UNRESOLVED

    Partial overlap is intentionally UNRESOLVED rather than forced into
    agreement or conflict.
    """

    symbolic_set = {
        _hybrid_freeze_explicit_fact_value(
            value
        )
        for value in symbolic_values
    }

    semantic_set = {
        _hybrid_freeze_explicit_fact_value(
            value
        )
        for value in semantic_values
    }

    if (
        not symbolic_set
        or not semantic_set
    ):
        return "UNRESOLVED"

    if symbolic_set == semantic_set:
        return "AGREEMENT"

    if symbolic_set.isdisjoint(
        semantic_set
    ):
        return "CONFLICT"

    return "UNRESOLVED"


def detect_hybrid_agreement_conflict(
    aligned_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Detect explicit agreement or conflict within H-aligned evidence.

    4.6.15I performs classification only. It does not resolve conflicts,
    construct hybrid candidates, enforce symbolic constraints, interpret
    neural context, fuse evidence, or calculate hybrid confidence.
    """

    if not isinstance(
        aligned_evidence,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Agreement/conflict detection requires the canonical H result."
        )

    if (
        aligned_evidence.get("status")
        != "HYBRID_EVIDENCE_ALIGNED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Evidence has not passed canonical H alignment."
        )

    if (
        aligned_evidence.get("next_stage")
        != "agreement_conflict_detection"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "H does not hand off to agreement/conflict detection."
        )

    article_identity = aligned_evidence.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Agreement/conflict input is missing article_identity."
        )

    symbolic_records = aligned_evidence.get(
        "symbolic_evidence_records"
    )

    semantic_records = aligned_evidence.get(
        "neural_semantic_evidence_records"
    )

    alignment_pairs = aligned_evidence.get(
        "alignment_pairs"
    )

    if not isinstance(
        symbolic_records,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "H symbolic evidence records are missing."
        )

    if not isinstance(
        semantic_records,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "H neural/semantic evidence records are missing."
        )

    if not isinstance(
        alignment_pairs,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "H alignment pairs are missing."
        )

    symbolic_index: dict[str, Mapping[str, Any]] = {}

    for record in symbolic_records:

        if not isinstance(
            record,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid symbolic evidence record."
            )

        evidence_id = record.get(
            "evidence_id"
        )

        if not evidence_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Symbolic evidence record is missing evidence_id."
            )

        if evidence_id in symbolic_index:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate symbolic evidence_id: {evidence_id}."
            )

        symbolic_index[
            evidence_id
        ] = record

    semantic_index: dict[str, Mapping[str, Any]] = {}

    for record in semantic_records:

        if not isinstance(
            record,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid neural/semantic evidence record."
            )

        evidence_id = record.get(
            "evidence_id"
        )

        if not evidence_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Neural/semantic evidence record is missing evidence_id."
            )

        if evidence_id in semantic_index:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate neural/semantic evidence_id: {evidence_id}."
            )

        semantic_index[
            evidence_id
        ] = record

    assessments: list[dict[str, Any]] = []

    for pair in alignment_pairs:

        if not isinstance(
            pair,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid H alignment pair."
            )

        alignment_id = pair.get(
            "alignment_id"
        )

        symbolic_id = pair.get(
            "symbolic_evidence_id"
        )

        semantic_id = pair.get(
            "neural_semantic_evidence_id"
        )

        if (
            not alignment_id
            or not symbolic_id
            or not semantic_id
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Alignment pair is missing canonical identifiers."
            )

        symbolic_record = symbolic_index.get(
            symbolic_id
        )

        semantic_record = semantic_index.get(
            semantic_id
        )

        if symbolic_record is None:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Alignment references unknown symbolic evidence: "
                f"{symbolic_id}."
            )

        if semantic_record is None:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Alignment references unknown neural/semantic evidence: "
                f"{semantic_id}."
            )

        symbolic_layer = symbolic_record.get(
            "source_layer"
        )

        if (
            symbolic_layer
            not in _SYMBOLIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"Alignment has invalid symbolic layer: "
                f"{symbolic_layer}."
            )

        symbolic_evidence = symbolic_record.get(
            "evidence"
        )

        semantic_evidence = semantic_record.get(
            "evidence"
        )

        symbolic_facts = (
            _hybrid_extract_explicit_comparable_facts(
                symbolic_evidence,
                symbolic_layer,
            )
        )

        semantic_facts = (
            _hybrid_extract_explicit_comparable_facts(
                semantic_evidence,
                symbolic_layer,
            )
        )

        shared_fields = sorted(
            set(
                symbolic_facts
            )
            & set(
                semantic_facts
            )
        )

        field_assessments: list[dict[str, Any]] = []

        for field_name in shared_fields:

            field_state = (
                _hybrid_compare_explicit_fact_sets(
                    symbolic_facts[
                        field_name
                    ],
                    semantic_facts[
                        field_name
                    ],
                )
            )

            field_assessments.append({
                "field":
                    field_name,

                "state":
                    field_state,

                "symbolic_values":
                    deepcopy(
                        symbolic_facts[
                            field_name
                        ]
                    ),

                "neural_semantic_values":
                    deepcopy(
                        semantic_facts[
                            field_name
                        ]
                    ),
            })

        field_states = {
            field[
                "state"
            ]
            for field in field_assessments
        }

        if "CONFLICT" in field_states:
            overall_state = (
                "CONFLICT"
            )

            decision_basis = (
                "EXPLICIT_COMPARABLE_FIELD_CONFLICT"
            )

        elif (
            field_assessments
            and field_states == {
                "AGREEMENT"
            }
        ):
            overall_state = (
                "AGREEMENT"
            )

            decision_basis = (
                "EXPLICIT_COMPARABLE_FIELD_AGREEMENT"
            )

        else:
            overall_state = (
                "UNRESOLVED"
            )

            decision_basis = (
                "INSUFFICIENT_OR_PARTIAL_EXPLICIT_COMPARABLE_EVIDENCE"
            )

        assessments.append({
            "assessment_id":
                f"AGREEMENT_CONFLICT:{len(assessments) + 1}",

            "alignment_id":
                alignment_id,

            "symbolic_evidence_id":
                symbolic_id,

            "neural_semantic_evidence_id":
                semantic_id,

            "symbolic_source_layer":
                symbolic_layer,

            "neural_semantic_source_layer":
                semantic_record.get(
                    "source_layer"
                ),

            "alignment_basis":
                pair.get(
                    "alignment_basis"
                ),

            "shared_grounding_anchors":
                deepcopy(
                    pair.get(
                        "shared_grounding_anchors",
                        [],
                    )
                ),

            "shared_comparable_fields":
                shared_fields,

            "field_assessments":
                field_assessments,

            "state":
                overall_state,

            "decision_basis":
                decision_basis,

            "agreement_detected":
                overall_state
                == "AGREEMENT",

            "conflict_detected":
                overall_state
                == "CONFLICT",

            "unresolved":
                overall_state
                == "UNRESOLVED",

            "conflict_resolved":
                False,

            "hybrid_candidate_constructed":
                False,

            "symbolic_constraint_enforced":
                False,

            "fusion_performed":
                False,
        })

    agreement_count = sum(
        assessment["state"] == "AGREEMENT"
        for assessment in assessments
    )

    conflict_count = sum(
        assessment["state"] == "CONFLICT"
        for assessment in assessments
    )

    unresolved_count = sum(
        assessment["state"] == "UNRESOLVED"
        for assessment in assessments
    )

    return {
        "schema_version":
            "symbolic_neural_hybrid_agreement_conflict_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15I",

        "status":
            "HYBRID_AGREEMENT_CONFLICT_DETECTED",

        "article_identity":
            deepcopy(
                article_identity
            ),

        "symbolic_evidence_records":
            deepcopy(
                symbolic_records
            ),

        "neural_semantic_evidence_records":
            deepcopy(
                semantic_records
            ),

        "alignment_pairs":
            deepcopy(
                alignment_pairs
            ),

        "agreement_conflict_assessments":
            assessments,

        "unaligned_symbolic_evidence_ids":
            deepcopy(
                aligned_evidence.get(
                    "unaligned_symbolic_evidence_ids",
                    [],
                )
            ),

        "unaligned_neural_semantic_evidence_ids":
            deepcopy(
                aligned_evidence.get(
                    "unaligned_neural_semantic_evidence_ids",
                    [],
                )
            ),

        "article_context_boundary":
            deepcopy(
                aligned_evidence.get(
                    "article_context_boundary"
                )
            ),

        "agreement_conflict_summary": {
            "alignment_pair_count":
                len(
                    alignment_pairs
                ),

            "assessment_count":
                len(
                    assessments
                ),

            "agreement_count":
                agreement_count,

            "conflict_count":
                conflict_count,

            "unresolved_count":
                unresolved_count,

            "all_alignment_pairs_assessed":
                len(
                    assessments
                )
                == len(
                    alignment_pairs
                ),

            "semantic_equivalence_guessing_performed":
                False,

            "cross_domain_relation_type_comparison_performed":
                False,

            "conflict_resolution_performed":
                False,
        },

        "processing_boundaries": {
            "agreement_conflict_detection_performed":
                True,

            "explicit_comparable_fact_detection_only":
                True,

            "semantic_equivalence_inference_performed":
                False,

            "cross_domain_relation_comparison_performed":
                False,

            "conflict_resolution_performed":
                False,

            "hybrid_candidates_constructed":
                False,

            "symbolic_constraint_enforcement_performed":
                False,

            "neural_context_interpretation_performed":
                False,

            "hybrid_evidence_fusion_performed":
                False,

            "hybrid_confidence_calculated":
                False,

            "new_article_fact_inference_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "hybrid_reasoning_candidate_construction",
    }


# ============================================================================
# PATCH 4.6.15J — Hybrid Reasoning Candidate Construction
# ============================================================================

_HYBRID_CANDIDATE_DISPOSITIONS = {
    "AGREEMENT":
        "AGREEMENT_EVIDENCE_AVAILABLE",

    "CONFLICT":
        "CONFLICT_PRESERVED_FOR_LATER_RESOLUTION",

    "UNRESOLVED":
        "UNRESOLVED_EVIDENCE_PRESERVED",
}


def construct_hybrid_reasoning_candidates(
    agreement_conflict_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Construct governed hybrid reasoning candidates from canonical
    4.6.15I agreement/conflict assessments.

    4.6.15J packages evidence for later reasoning only.

    It does not:
    - enforce symbolic constraints
    - interpret neural context
    - fuse evidence
    - resolve conflicts
    - calculate hybrid confidence
    - infer new article facts
    """

    if not isinstance(
        agreement_conflict_result,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid candidate construction requires the canonical I result."
        )

    if (
        agreement_conflict_result.get("status")
        != "HYBRID_AGREEMENT_CONFLICT_DETECTED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Agreement/conflict detection has not been completed."
        )

    if (
        agreement_conflict_result.get("next_stage")
        != "hybrid_reasoning_candidate_construction"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "I does not hand off to hybrid reasoning candidate construction."
        )

    article_identity = agreement_conflict_result.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid candidate construction is missing article_identity."
        )

    symbolic_records = agreement_conflict_result.get(
        "symbolic_evidence_records"
    )

    semantic_records = agreement_conflict_result.get(
        "neural_semantic_evidence_records"
    )

    assessments = agreement_conflict_result.get(
        "agreement_conflict_assessments"
    )

    if not isinstance(
        symbolic_records,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "I symbolic evidence records are missing."
        )

    if not isinstance(
        semantic_records,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "I neural/semantic evidence records are missing."
        )

    if not isinstance(
        assessments,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "I agreement/conflict assessments are missing."
        )

    symbolic_index: dict[str, Mapping[str, Any]] = {}

    for record in symbolic_records:

        if not isinstance(
            record,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid symbolic evidence record in I."
            )

        evidence_id = record.get(
            "evidence_id"
        )

        if not evidence_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Symbolic evidence record is missing evidence_id."
            )

        if evidence_id in symbolic_index:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate symbolic evidence_id: {evidence_id}."
            )

        symbolic_index[
            evidence_id
        ] = record

    semantic_index: dict[str, Mapping[str, Any]] = {}

    for record in semantic_records:

        if not isinstance(
            record,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid neural/semantic evidence record in I."
            )

        evidence_id = record.get(
            "evidence_id"
        )

        if not evidence_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Neural/semantic evidence record is missing evidence_id."
            )

        if evidence_id in semantic_index:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate neural/semantic evidence_id: {evidence_id}."
            )

        semantic_index[
            evidence_id
        ] = record

    hybrid_candidates: list[dict[str, Any]] = []
    assessment_ids: set[str] = set()

    for assessment in assessments:

        if not isinstance(
            assessment,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid agreement/conflict assessment."
            )

        assessment_id = assessment.get(
            "assessment_id"
        )

        if not assessment_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Agreement/conflict assessment is missing assessment_id."
            )

        if assessment_id in assessment_ids:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate agreement/conflict assessment_id: "
                f"{assessment_id}."
            )

        assessment_ids.add(
            assessment_id
        )

        alignment_id = assessment.get(
            "alignment_id"
        )

        symbolic_id = assessment.get(
            "symbolic_evidence_id"
        )

        semantic_id = assessment.get(
            "neural_semantic_evidence_id"
        )

        if (
            not alignment_id
            or not symbolic_id
            or not semantic_id
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Assessment is missing canonical evidence references."
            )

        symbolic_record = symbolic_index.get(
            symbolic_id
        )

        semantic_record = semantic_index.get(
            semantic_id
        )

        if symbolic_record is None:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Assessment references unknown symbolic evidence: "
                f"{symbolic_id}."
            )

        if semantic_record is None:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Assessment references unknown neural/semantic evidence: "
                f"{semantic_id}."
            )

        symbolic_layer = symbolic_record.get(
            "source_layer"
        )

        if (
            symbolic_layer
            not in _SYMBOLIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"Invalid symbolic source layer for candidate: "
                f"{symbolic_layer}."
            )

        preservation_rule = (
            _SYMBOLIC_PRESERVATION_RULES.get(
                symbolic_layer
            )
        )

        if not preservation_rule:
            raise SymbolicNeuralHybridIntelligenceError(
                f"No symbolic preservation rule exists for "
                f"{symbolic_layer}."
            )

        assessment_state = assessment.get(
            "state"
        )

        if (
            assessment_state
            not in _HYBRID_CANDIDATE_DISPOSITIONS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"Invalid agreement/conflict state: "
                f"{assessment_state}."
            )

        expected_agreement = (
            assessment_state == "AGREEMENT"
        )

        expected_conflict = (
            assessment_state == "CONFLICT"
        )

        expected_unresolved = (
            assessment_state == "UNRESOLVED"
        )

        if (
            assessment.get("agreement_detected")
            is not expected_agreement
            or assessment.get("conflict_detected")
            is not expected_conflict
            or assessment.get("unresolved")
            is not expected_unresolved
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"Assessment state flags are inconsistent for "
                f"{assessment_id}."
            )

        candidate_id = (
            f"HYBRID_CANDIDATE:"
            f"{len(hybrid_candidates) + 1}"
        )

        hybrid_candidates.append({
            "hybrid_candidate_id":
                candidate_id,

            "assessment_id":
                assessment_id,

            "alignment_id":
                alignment_id,

            "article_identity":
                deepcopy(
                    article_identity
                ),

            "symbolic_evidence_id":
                symbolic_id,

            "neural_semantic_evidence_id":
                semantic_id,

            "symbolic_source_layer":
                symbolic_layer,

            "neural_semantic_source_layer":
                semantic_record.get(
                    "source_layer"
                ),

            "symbolic_evidence":
                deepcopy(
                    symbolic_record
                ),

            "neural_semantic_evidence":
                deepcopy(
                    semantic_record
                ),

            "agreement_conflict_assessment":
                deepcopy(
                    assessment
                ),

            "assessment_state":
                assessment_state,

            "candidate_disposition":
                _HYBRID_CANDIDATE_DISPOSITIONS[
                    assessment_state
                ],

            "symbolic_preservation_rule":
                preservation_rule,

            "symbolic_constraint_authority":
                "HARD_WHEN_EXPLICIT_AND_CERTIFIED",

            "neural_semantic_authority":
                "INTERPRETIVE_ONLY",

            "shared_grounding_anchors":
                deepcopy(
                    assessment.get(
                        "shared_grounding_anchors",
                        [],
                    )
                ),

            "shared_comparable_fields":
                deepcopy(
                    assessment.get(
                        "shared_comparable_fields",
                        [],
                    )
                ),

            "candidate_processing_state": {
                "constructed":
                    True,

                "agreement_preserved":
                    assessment_state
                    == "AGREEMENT",

                "conflict_preserved":
                    assessment_state
                    == "CONFLICT",

                "unresolved_preserved":
                    assessment_state
                    == "UNRESOLVED",

                "symbolic_constraint_enforced":
                    False,

                "neural_context_interpreted":
                    False,

                "evidence_fused":
                    False,

                "conflict_resolved":
                    False,

                "hybrid_confidence_calculated":
                    False,
            },
        })

    agreement_candidate_count = sum(
        candidate["assessment_state"]
        == "AGREEMENT"
        for candidate in hybrid_candidates
    )

    conflict_candidate_count = sum(
        candidate["assessment_state"]
        == "CONFLICT"
        for candidate in hybrid_candidates
    )

    unresolved_candidate_count = sum(
        candidate["assessment_state"]
        == "UNRESOLVED"
        for candidate in hybrid_candidates
    )

    return {
        "schema_version":
            "symbolic_neural_hybrid_reasoning_candidates_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15J",

        "status":
            "HYBRID_REASONING_CANDIDATES_CONSTRUCTED",

        "article_identity":
            deepcopy(
                article_identity
            ),

        "symbolic_evidence_records":
            deepcopy(
                symbolic_records
            ),

        "neural_semantic_evidence_records":
            deepcopy(
                semantic_records
            ),

        "alignment_pairs":
            deepcopy(
                agreement_conflict_result.get(
                    "alignment_pairs",
                    [],
                )
            ),

        "agreement_conflict_assessments":
            deepcopy(
                assessments
            ),

        "hybrid_reasoning_candidates":
            hybrid_candidates,

        "unaligned_symbolic_evidence_ids":
            deepcopy(
                agreement_conflict_result.get(
                    "unaligned_symbolic_evidence_ids",
                    [],
                )
            ),

        "unaligned_neural_semantic_evidence_ids":
            deepcopy(
                agreement_conflict_result.get(
                    "unaligned_neural_semantic_evidence_ids",
                    [],
                )
            ),

        "article_context_boundary":
            deepcopy(
                agreement_conflict_result.get(
                    "article_context_boundary"
                )
            ),

        "candidate_construction_summary": {
            "assessment_count":
                len(
                    assessments
                ),

            "candidate_count":
                len(
                    hybrid_candidates
                ),

            "agreement_candidate_count":
                agreement_candidate_count,

            "conflict_candidate_count":
                conflict_candidate_count,

            "unresolved_candidate_count":
                unresolved_candidate_count,

            "all_assessments_preserved":
                len(
                    hybrid_candidates
                )
                == len(
                    assessments
                ),

            "conflicts_discarded":
                False,

            "unresolved_evidence_discarded":
                False,

            "symbolic_constraints_enforced":
                False,

            "neural_context_interpreted":
                False,

            "evidence_fused":
                False,
        },

        "processing_boundaries": {
            "hybrid_candidates_constructed":
                True,

            "agreement_conflict_state_preserved":
                True,

            "symbolic_constraint_enforcement_performed":
                False,

            "neural_context_interpretation_performed":
                False,

            "hybrid_evidence_fusion_performed":
                False,

            "conflict_resolution_performed":
                False,

            "hybrid_confidence_calculated":
                False,

            "new_article_fact_inference_performed":
                False,

            "semantic_equivalence_inference_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "symbolic_constraint_enforcement",
    }


# ============================================================================
# PATCH 4.6.15K — Symbolic Constraint Enforcement
# ============================================================================

_HYBRID_CONSTRAINT_OUTCOMES = {
    "AGREEMENT":
        "SYMBOLIC_BOUNDARY_ENFORCED_AGREEMENT_PRESERVED",

    "CONFLICT":
        "SYMBOLIC_BOUNDARY_ENFORCED_CONFLICT_PRESERVED",

    "UNRESOLVED":
        "SYMBOLIC_BOUNDARY_ENFORCED_UNRESOLVED_PRESERVED",
}


def enforce_hybrid_symbolic_constraints(
    candidate_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Enforce the frozen symbolic authority boundary on every canonical
    hybrid reasoning candidate.

    4.6.15K does not:
    - interpret neural/semantic context
    - resolve conflicts
    - fuse evidence
    - calculate confidence
    - infer new article facts
    - alter certified symbolic evidence
    """

    if not isinstance(
        candidate_result,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Symbolic constraint enforcement requires the canonical J result."
        )

    if (
        candidate_result.get("status")
        != "HYBRID_REASONING_CANDIDATES_CONSTRUCTED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid reasoning candidates have not been constructed."
        )

    if (
        candidate_result.get("next_stage")
        != "symbolic_constraint_enforcement"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "J does not hand off to symbolic constraint enforcement."
        )

    article_identity = candidate_result.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Symbolic constraint enforcement is missing article_identity."
        )

    candidates = candidate_result.get(
        "hybrid_reasoning_candidates"
    )

    if not isinstance(
        candidates,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "J hybrid reasoning candidates are missing."
        )

    enforced_candidates: list[dict[str, Any]] = []
    enforcement_records: list[dict[str, Any]] = []

    candidate_ids: set[str] = set()

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid hybrid reasoning candidate."
            )

        candidate_id = candidate.get(
            "hybrid_candidate_id"
        )

        if not candidate_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Hybrid reasoning candidate is missing hybrid_candidate_id."
            )

        if candidate_id in candidate_ids:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate hybrid_candidate_id: {candidate_id}."
            )

        candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get("article_identity")
            != article_identity
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} belongs to a different article."
            )

        symbolic_layer = candidate.get(
            "symbolic_source_layer"
        )

        if (
            symbolic_layer
            not in _SYMBOLIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"Invalid symbolic source layer: {symbolic_layer}."
            )

        expected_rule = (
            _SYMBOLIC_PRESERVATION_RULES.get(
                symbolic_layer
            )
        )

        supplied_rule = candidate.get(
            "symbolic_preservation_rule"
        )

        if supplied_rule != expected_rule:
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid symbolic preservation rule."
            )

        if (
            candidate.get("symbolic_constraint_authority")
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} lost hard symbolic constraint authority."
            )

        if (
            candidate.get("neural_semantic_authority")
            != "INTERPRETIVE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic authority."
            )

        assessment_state = candidate.get(
            "assessment_state"
        )

        if (
            assessment_state
            not in _HYBRID_CONSTRAINT_OUTCOMES
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid assessment state."
            )

        processing_state = candidate.get(
            "candidate_processing_state"
        )

        if not isinstance(
            processing_state,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing candidate_processing_state."
            )

        if (
            processing_state.get("constructed")
            is not True
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} was not canonically constructed."
            )

        if (
            processing_state.get(
                "symbolic_constraint_enforced"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} entered K with constraints already enforced."
            )

        symbolic_evidence = candidate.get(
            "symbolic_evidence"
        )

        neural_semantic_evidence = candidate.get(
            "neural_semantic_evidence"
        )

        if not isinstance(
            symbolic_evidence,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing symbolic evidence."
            )

        if not isinstance(
            neural_semantic_evidence,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing neural/semantic evidence."
            )

        if (
            symbolic_evidence.get("evidence_side")
            != "SYMBOLIC"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid symbolic evidence-side identity."
            )

        if (
            symbolic_evidence.get("source_layer")
            != symbolic_layer
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} symbolic source-layer identity changed."
            )

        if (
            neural_semantic_evidence.get("evidence_side")
            != "NEURAL_SEMANTIC"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic evidence-side identity."
            )

        semantic_layer = candidate.get(
            "neural_semantic_source_layer"
        )

        if (
            semantic_layer
            not in _NEURAL_SEMANTIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid neural/semantic source layer."
            )

        if (
            neural_semantic_evidence.get("source_layer")
            != semantic_layer
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} neural/semantic source-layer identity changed."
            )

        symbolic_evidence_id = candidate.get(
            "symbolic_evidence_id"
        )

        neural_semantic_evidence_id = candidate.get(
            "neural_semantic_evidence_id"
        )

        if (
            not symbolic_evidence_id
            or symbolic_evidence.get("evidence_id")
            != symbolic_evidence_id
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent symbolic evidence identity."
            )

        if (
            not neural_semantic_evidence_id
            or neural_semantic_evidence.get("evidence_id")
            != neural_semantic_evidence_id
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent neural/semantic evidence identity."
            )

        expected_disposition = (
            _HYBRID_CANDIDATE_DISPOSITIONS[
                assessment_state
            ]
        )

        if (
            candidate.get("candidate_disposition")
            != expected_disposition
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an inconsistent candidate disposition."
            )

        expected_agreement = (
            assessment_state == "AGREEMENT"
        )

        expected_conflict = (
            assessment_state == "CONFLICT"
        )

        expected_unresolved = (
            assessment_state == "UNRESOLVED"
        )

        if (
            processing_state.get("agreement_preserved")
            is not expected_agreement
            or processing_state.get("conflict_preserved")
            is not expected_conflict
            or processing_state.get("unresolved_preserved")
            is not expected_unresolved
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent preserved assessment-state flags."
            )

        enforced_candidate = deepcopy(
            dict(candidate)
        )

        enforced_processing_state = deepcopy(
            dict(processing_state)
        )

        enforced_processing_state[
            "symbolic_constraint_enforced"
        ] = True

        enforced_candidate[
            "candidate_processing_state"
        ] = enforced_processing_state

        enforced_candidate[
            "symbolic_constraint_enforcement"
        ] = {
            "enforcement_status":
                "ENFORCED",

            "preservation_rule":
                expected_rule,

            "constraint_authority":
                "HARD_WHEN_EXPLICIT_AND_CERTIFIED",

            "neural_semantic_authority":
                "INTERPRETIVE_ONLY",

            "semantic_override_allowed":
                False,

            "symbolic_evidence_mutated":
                False,

            "symbolic_evidence_discarded":
                False,

            "symbolic_constraint_relaxed":
                False,

            "source_commitment_strengthened":
                False,

            "new_symbolic_fact_inferred":
                False,

            "assessment_state_preserved":
                True,

            "constraint_outcome":
                _HYBRID_CONSTRAINT_OUTCOMES[
                    assessment_state
                ],
        }

        enforced_candidates.append(
            enforced_candidate
        )

        enforcement_records.append({
            "constraint_enforcement_id":
                f"SYMBOLIC_CONSTRAINT:{len(enforcement_records) + 1}",

            "hybrid_candidate_id":
                candidate_id,

            "symbolic_source_layer":
                symbolic_layer,

            "assessment_state":
                assessment_state,

            "preservation_rule":
                expected_rule,

            "constraint_authority":
                "HARD_WHEN_EXPLICIT_AND_CERTIFIED",

            "semantic_override_allowed":
                False,

            "constraint_outcome":
                _HYBRID_CONSTRAINT_OUTCOMES[
                    assessment_state
                ],

            "enforced":
                True,
        })

    return {
        "schema_version":
            "symbolic_neural_hybrid_symbolic_constraint_enforcement_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15K",

        "status":
            "HYBRID_SYMBOLIC_CONSTRAINTS_ENFORCED",

        "article_identity":
            deepcopy(
                article_identity
            ),

        "symbolic_evidence_records":
            deepcopy(
                candidate_result.get(
                    "symbolic_evidence_records",
                    [],
                )
            ),

        "neural_semantic_evidence_records":
            deepcopy(
                candidate_result.get(
                    "neural_semantic_evidence_records",
                    [],
                )
            ),

        "alignment_pairs":
            deepcopy(
                candidate_result.get(
                    "alignment_pairs",
                    [],
                )
            ),

        "agreement_conflict_assessments":
            deepcopy(
                candidate_result.get(
                    "agreement_conflict_assessments",
                    [],
                )
            ),

        "hybrid_reasoning_candidates":
            enforced_candidates,

        "symbolic_constraint_enforcement_records":
            enforcement_records,

        "unaligned_symbolic_evidence_ids":
            deepcopy(
                candidate_result.get(
                    "unaligned_symbolic_evidence_ids",
                    [],
                )
            ),

        "unaligned_neural_semantic_evidence_ids":
            deepcopy(
                candidate_result.get(
                    "unaligned_neural_semantic_evidence_ids",
                    [],
                )
            ),

        "article_context_boundary":
            deepcopy(
                candidate_result.get(
                    "article_context_boundary"
                )
            ),

        "symbolic_constraint_summary": {
            "candidate_count":
                len(
                    candidates
                ),

            "enforcement_record_count":
                len(
                    enforcement_records
                ),

            "all_candidates_enforced":
                len(
                    enforcement_records
                )
                == len(
                    candidates
                ),

            "semantic_override_allowed":
                False,

            "symbolic_evidence_mutated":
                False,

            "symbolic_constraints_relaxed":
                False,

            "new_symbolic_intelligence_created":
                False,
        },

        "processing_boundaries": {
            "symbolic_constraint_enforcement_performed":
                True,

            "hard_symbolic_authority_preserved":
                True,

            "semantic_override_allowed":
                False,

            "symbolic_evidence_mutation_performed":
                False,

            "symbolic_constraint_relaxation_performed":
                False,

            "neural_context_interpretation_performed":
                False,

            "hybrid_evidence_fusion_performed":
                False,

            "conflict_resolution_performed":
                False,

            "hybrid_confidence_calculated":
                False,

            "new_article_fact_inference_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "neural_context_interpretation",
    }



# ============================================================================
# PATCH 4.6.15L — Neural Context Interpretation
# ============================================================================

_HYBRID_NEURAL_CONTEXT_FIELDS = {
    "analogical_intelligence": {
        "unique_directional_grounding_supported",
        "directional_grounding_supported",
        "directional_grounding_confidence",
        "directional_grounding_integrity_preserved",
        "exact_directional_analogical_identity_used",
        "analogy_direction_preserved",
        "analogy_direction_is_identity",
    },

    "similarity_intelligence": {
        "relation_class",
        "relation_class_is_identity",
        "difference_dimension_text",
        "difference_contrast_valid",
        "explicit_difference_dimension_found",
        "difference_dimension_extraction_pattern",
        "difference_dimension_is_identity_when_present",
        "relation_classes_preserved",
        "difference_dimensions_preserved",
        "unstated_difference_inference_performed",
    },
}


_HYBRID_NEURAL_CONTEXT_OUTCOMES = {
    "AGREEMENT":
        "CONTEXT_INTERPRETED_AGREEMENT_PRESERVED",

    "CONFLICT":
        "CONTEXT_INTERPRETED_CONFLICT_PRESERVED_NO_OVERRIDE",

    "UNRESOLVED":
        "CONTEXT_INTERPRETED_UNRESOLVED_PRESERVED",
}


def _hybrid_extract_certified_neural_context(
    evidence: Any,
    semantic_layer: str,
) -> dict[str, list[Any]]:
    """
    Extract already-certified semantic/contextual signals only.

    No new analogy, similarity, semantic relation, or article fact is
    generated here.
    """

    approved_fields = (
        _HYBRID_NEURAL_CONTEXT_FIELDS.get(
            semantic_layer,
            set(),
        )
    )

    signals: dict[str, list[Any]] = {}

    def walk(item: Any) -> None:

        if isinstance(item, Mapping):

            for key, value in item.items():

                key_text = str(
                    key
                ).lower()

                if (
                    key_text in approved_fields
                    and value is not None
                ):
                    signals.setdefault(
                        key_text,
                        [],
                    ).append(
                        deepcopy(value)
                    )

                walk(
                    value
                )

        elif isinstance(
            item,
            (list, tuple, set),
        ):
            for nested in item:
                walk(
                    nested
                )

    walk(
        evidence
    )

    return {
        field_name:
            _hybrid_unique_explicit_values(
                values
            )
        for field_name, values in signals.items()
    }


def interpret_hybrid_neural_context(
    constraint_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Interpret certified neural/semantic context inside the symbolic
    authority boundary established by 4.6.15K.

    In v1, "neural context interpretation" means governed use of the
    already-certified Analogical and Similarity intelligence outputs.
    It does not call an external model and does not invent new meaning.
    """

    if not isinstance(
        constraint_result,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Neural context interpretation requires the canonical K result."
        )

    if (
        constraint_result.get("status")
        != "HYBRID_SYMBOLIC_CONSTRAINTS_ENFORCED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Symbolic constraints have not been canonically enforced."
        )

    if (
        constraint_result.get("next_stage")
        != "neural_context_interpretation"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "K does not hand off to neural context interpretation."
        )

    article_identity = constraint_result.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Neural context interpretation is missing article_identity."
        )

    article_context_boundary = constraint_result.get(
        "article_context_boundary"
    )

    if not isinstance(
        article_context_boundary,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Certified article-context boundary is missing."
        )

    if (
        article_context_boundary.get(
            "context_access_policy"
        )
        != "CERTIFIED_ARTICLE_LOCAL_EVIDENCE_ONLY"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Neural context interpretation received an invalid context-access policy."
        )

    candidates = constraint_result.get(
        "hybrid_reasoning_candidates"
    )

    if not isinstance(
        candidates,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "K hybrid reasoning candidates are missing."
        )

    interpreted_candidates: list[dict[str, Any]] = []
    interpretation_records: list[dict[str, Any]] = []

    candidate_ids: set[str] = set()

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid K hybrid reasoning candidate."
            )

        candidate_id = candidate.get(
            "hybrid_candidate_id"
        )

        if not candidate_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Hybrid reasoning candidate is missing hybrid_candidate_id."
            )

        if candidate_id in candidate_ids:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate hybrid_candidate_id: {candidate_id}."
            )

        candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get("article_identity")
            != article_identity
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} belongs to a different article."
            )

        symbolic_layer = candidate.get(
            "symbolic_source_layer"
        )

        if (
            symbolic_layer
            not in _SYMBOLIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid symbolic source layer."
            )

        semantic_layer = candidate.get(
            "neural_semantic_source_layer"
        )

        if (
            semantic_layer
            not in _NEURAL_SEMANTIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid neural/semantic source layer."
            )

        expected_rule = (
            _SYMBOLIC_PRESERVATION_RULES.get(
                symbolic_layer
            )
        )

        if (
            candidate.get(
                "symbolic_preservation_rule"
            )
            != expected_rule
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost its canonical symbolic preservation rule."
            )

        if (
            candidate.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost hard symbolic authority."
            )

        if (
            candidate.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic authority."
            )

        assessment_state = candidate.get(
            "assessment_state"
        )

        if (
            assessment_state
            not in _HYBRID_NEURAL_CONTEXT_OUTCOMES
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid assessment state."
            )

        processing_state = candidate.get(
            "candidate_processing_state"
        )

        if not isinstance(
            processing_state,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing candidate_processing_state."
            )

        if (
            processing_state.get("constructed")
            is not True
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} was not canonically constructed."
            )

        if (
            processing_state.get(
                "symbolic_constraint_enforced"
            )
            is not True
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} reached L without K enforcement."
            )

        if (
            processing_state.get(
                "neural_context_interpreted"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} entered L with neural context already interpreted."
            )

        expected_agreement = (
            assessment_state == "AGREEMENT"
        )

        expected_conflict = (
            assessment_state == "CONFLICT"
        )

        expected_unresolved = (
            assessment_state == "UNRESOLVED"
        )

        if (
            processing_state.get(
                "agreement_preserved"
            )
            is not expected_agreement
            or processing_state.get(
                "conflict_preserved"
            )
            is not expected_conflict
            or processing_state.get(
                "unresolved_preserved"
            )
            is not expected_unresolved
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has corrupted assessment-state preservation."
            )

        enforcement = candidate.get(
            "symbolic_constraint_enforcement"
        )

        if not isinstance(
            enforcement,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing K symbolic enforcement."
            )

        expected_disposition = (
            _HYBRID_CANDIDATE_DISPOSITIONS[
                assessment_state
            ]
        )

        if (
            candidate.get(
                "candidate_disposition"
            )
            != expected_disposition
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an inconsistent candidate disposition."
            )

        if (
            symbolic_evidence.get(
                "evidence_side"
            )
            != "SYMBOLIC"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid symbolic evidence-side provenance."
            )

        if (
            semantic_evidence.get(
                "evidence_side"
            )
            != "NEURAL_SEMANTIC"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic evidence-side provenance."
            )

        if (
            enforcement.get(
                "constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
            or enforcement.get(
                "semantic_override_allowed"
            )
            is not False
            or enforcement.get(
                "symbolic_evidence_mutated"
            )
            is not False
            or enforcement.get(
                "symbolic_evidence_discarded"
            )
            is not False
            or enforcement.get(
                "symbolic_constraint_relaxed"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains corrupted K provenance."
            )

        if (
            interpretation.get(
                "source_layer"
            )
            != semantic_layer
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent L source provenance."
            )

        if (
            interpretation.get(
                "context_access_policy"
            )
            != "CERTIFIED_ARTICLE_LOCAL_EVIDENCE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid L context provenance."
            )

        expected_context_outcome = (
            _HYBRID_NEURAL_CONTEXT_OUTCOMES[
                assessment_state
            ]
        )

        if (
            interpretation.get(
                "context_outcome"
            )
            != expected_context_outcome
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid L context outcome provenance."
            )

        certified_context_signals = (
            interpretation.get(
                "certified_context_signals"
            )
        )

        if not isinstance(
            certified_context_signals,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid L certified context signals."
            )

        expected_semantic_signal_count = sum(
            len(values)
            for values
            in certified_context_signals.values()
        )

        if (
            interpretation.get(
                "semantic_signal_count"
            )
            != expected_semantic_signal_count
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent L semantic signal accounting."
            )

        expected_interpretation_status = (
            "CERTIFIED_SEMANTIC_CONTEXT_INTERPRETED"
            if expected_semantic_signal_count
            else "NO_EXPLICIT_SEMANTIC_CONTEXT_SIGNAL_AVAILABLE"
        )

        if (
            interpretation.get(
                "interpretation_status"
            )
            != expected_interpretation_status
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid L interpretation-status provenance."
            )

        if (
            interpretation.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
            or interpretation.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
            or interpretation.get(
                "semantic_override_allowed"
            )
            is not False
            or interpretation.get(
                "semantic_override_attempted"
            )
            is not False
            or interpretation.get(
                "symbolic_evidence_mutated"
            )
            is not False
            or interpretation.get(
                "symbolic_constraint_relaxed"
            )
            is not False
            or interpretation.get(
                "new_semantic_fact_inferred"
            )
            is not False
            or interpretation.get(
                "new_article_fact_inferred"
            )
            is not False
            or interpretation.get(
                "semantic_equivalence_inferred"
            )
            is not False
            or interpretation.get(
                "conflict_resolved"
            )
            is not False
            or interpretation.get(
                "evidence_fused"
            )
            is not False
            or interpretation.get(
                "external_model_called"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains corrupted L provenance."
            )

        expected_fusion_mode = (
            _HYBRID_FUSION_MODES[
                assessment_state
            ]
        )

        expected_fusion_outcome = (
            _HYBRID_FUSION_OUTCOMES[
                assessment_state
            ]
        )

        if (
            fusion.get(
                "fusion_status"
            )
            != "FUSED"
            or fusion.get(
                "fusion_mode"
            )
            != expected_fusion_mode
            or fusion.get(
                "fusion_outcome"
            )
            != expected_fusion_outcome
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid M fusion provenance."
            )

        if (
            fusion.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
            or fusion.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
            or fusion.get(
                "semantic_override_allowed"
            )
            is not False
            or fusion.get(
                "symbolic_evidence_mutated"
            )
            is not False
            or fusion.get(
                "neural_semantic_evidence_mutated"
            )
            is not False
            or fusion.get(
                "symbolic_constraint_relaxed"
            )
            is not False
            or fusion.get(
                "score_averaging_performed"
            )
            is not False
            or fusion.get(
                "raw_evidence_concatenation_performed"
            )
            is not False
            or fusion.get(
                "new_hybrid_fact_inferred"
            )
            is not False
            or fusion.get(
                "new_article_fact_inferred"
            )
            is not False
            or fusion.get(
                "conflict_resolved"
            )
            is not False
            or fusion.get(
                "hybrid_confidence_calculated"
            )
            is not False
            or fusion.get(
                "external_model_called"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains corrupted M provenance."
            )

        expected_resolution_policy = (
            _HYBRID_CONFLICT_RESOLUTION_POLICIES[
                assessment_state
            ]
        )

        for resolution_field in (
            "resolution_status",
            "governance_decision",
            "selected_authority",
            "final_resolution_state",
        ):
            if (
                resolution.get(
                    resolution_field
                )
                != expected_resolution_policy[
                    resolution_field
                ]
            ):
                raise SymbolicNeuralHybridIntelligenceError(
                    f"{candidate_id} has invalid N {resolution_field} provenance."
                )

        if (
            resolution.get(
                "conflict_present"
            )
            is not expected_conflict
            or resolution.get(
                "resolution_required"
            )
            is not expected_conflict
            or resolution.get(
                "conflict_operationally_resolved"
            )
            is not expected_conflict
            or resolution.get(
                "abstention_required"
            )
            is not expected_unresolved
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent N governance provenance."
            )

        if (
            resolution.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
            or resolution.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
            or resolution.get(
                "symbolic_component_preserved"
            )
            is not True
            or resolution.get(
                "neural_semantic_component_preserved"
            )
            is not True
            or resolution.get(
                "neural_context_component_preserved"
            )
            is not True
            or resolution.get(
                "semantic_evidence_discarded"
            )
            is not False
            or resolution.get(
                "semantic_evidence_declared_false"
            )
            is not False
            or resolution.get(
                "symbolic_evidence_mutated"
            )
            is not False
            or resolution.get(
                "symbolic_constraint_relaxed"
            )
            is not False
            or resolution.get(
                "semantic_override_allowed"
            )
            is not False
            or resolution.get(
                "truth_assessment_performed"
            )
            is not False
            or resolution.get(
                "external_validation_performed"
            )
            is not False
            or resolution.get(
                "new_hybrid_fact_inferred"
            )
            is not False
            or resolution.get(
                "new_article_fact_inferred"
            )
            is not False
            or resolution.get(
                "hybrid_confidence_calculated"
            )
            is not False
            or resolution.get(
                "external_model_called"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains corrupted N provenance."
            )

        if (
            confidence.get(
                "final_resolution_state"
            )
            != resolution.get(
                "final_resolution_state"
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} O confidence is attached to the wrong N resolution state."
            )

        if (
            confidence.get(
                "confidence_scope"
            )
            != "STRUCTURAL_REASONING_CONFIDENCE_NOT_TRUTH_PROBABILITY"
            or confidence.get(
                "source_uncertainty_preserved"
            )
            is not True
            or confidence.get(
                "hard_symbolic_authority_preserved"
            )
            is not True
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains corrupted O confidence provenance."
            )

        if (
            enforcement.get(
                "enforcement_status"
            )
            != "ENFORCED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} symbolic constraint is not enforced."
            )

        if (
            enforcement.get(
                "preservation_rule"
            )
            != expected_rule
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} K preservation rule is inconsistent."
            )

        if (
            enforcement.get(
                "constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} K authority boundary is invalid."
            )

        if (
            enforcement.get(
                "semantic_override_allowed"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} incorrectly permits semantic override."
            )

        if (
            enforcement.get(
                "symbolic_evidence_mutated"
            )
            is not False
            or enforcement.get(
                "symbolic_evidence_discarded"
            )
            is not False
            or enforcement.get(
                "symbolic_constraint_relaxed"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains corrupted K symbolic enforcement state."
            )

        symbolic_evidence = candidate.get(
            "symbolic_evidence"
        )

        neural_semantic_evidence = candidate.get(
            "neural_semantic_evidence"
        )

        if not isinstance(
            symbolic_evidence,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing symbolic evidence."
            )

        if not isinstance(
            neural_semantic_evidence,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing neural/semantic evidence."
            )

        if (
            symbolic_evidence.get(
                "evidence_side"
            )
            != "SYMBOLIC"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid symbolic evidence-side identity."
            )

        if (
            symbolic_evidence.get(
                "source_layer"
            )
            != symbolic_layer
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} symbolic source identity changed."
            )

        if (
            neural_semantic_evidence.get(
                "evidence_side"
            )
            != "NEURAL_SEMANTIC"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic evidence-side identity."
            )

        if (
            neural_semantic_evidence.get(
                "source_layer"
            )
            != semantic_layer
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} neural/semantic source identity changed."
            )

        if (
            symbolic_evidence.get(
                "evidence_id"
            )
            != candidate.get(
                "symbolic_evidence_id"
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} symbolic evidence identity is inconsistent."
            )

        if (
            neural_semantic_evidence.get(
                "evidence_id"
            )
            != candidate.get(
                "neural_semantic_evidence_id"
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} neural/semantic evidence identity is inconsistent."
            )

        semantic_payload = (
            neural_semantic_evidence.get(
                "evidence"
            )
        )

        if not isinstance(
            semantic_payload,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} neural/semantic evidence payload is invalid."
            )

        certified_context_signals = (
            _hybrid_extract_certified_neural_context(
                semantic_payload,
                semantic_layer,
            )
        )

        semantic_signal_count = sum(
            len(values)
            for values in certified_context_signals.values()
        )

        if semantic_signal_count:
            interpretation_status = (
                "CERTIFIED_SEMANTIC_CONTEXT_INTERPRETED"
            )
        else:
            interpretation_status = (
                "NO_EXPLICIT_SEMANTIC_CONTEXT_SIGNAL_AVAILABLE"
            )

        interpreted_candidate = deepcopy(
            dict(candidate)
        )

        interpreted_processing_state = deepcopy(
            dict(processing_state)
        )

        interpreted_processing_state[
            "neural_context_interpreted"
        ] = True

        interpreted_candidate[
            "candidate_processing_state"
        ] = interpreted_processing_state

        interpreted_candidate[
            "neural_context_interpretation"
        ] = {
            "interpretation_status":
                interpretation_status,

            "source_layer":
                semantic_layer,

            "interpretation_basis":
                "CERTIFIED_NEURAL_SEMANTIC_EVIDENCE_ONLY",

            "context_access_policy":
                "CERTIFIED_ARTICLE_LOCAL_EVIDENCE_ONLY",

            "certified_context_signals":
                deepcopy(
                    certified_context_signals
                ),

            "semantic_signal_count":
                semantic_signal_count,

            "assessment_state":
                assessment_state,

            "context_outcome":
                _HYBRID_NEURAL_CONTEXT_OUTCOMES[
                    assessment_state
                ],

            "symbolic_preservation_rule":
                expected_rule,

            "symbolic_constraint_authority":
                "HARD_WHEN_EXPLICIT_AND_CERTIFIED",

            "neural_semantic_authority":
                "INTERPRETIVE_ONLY",

            "semantic_override_allowed":
                False,

            "semantic_override_attempted":
                False,

            "symbolic_evidence_mutated":
                False,

            "symbolic_constraint_relaxed":
                False,

            "new_semantic_fact_inferred":
                False,

            "new_article_fact_inferred":
                False,

            "semantic_equivalence_inferred":
                False,

            "conflict_resolved":
                False,

            "evidence_fused":
                False,

            "external_model_called":
                False,
        }

        interpreted_candidates.append(
            interpreted_candidate
        )

        interpretation_records.append({
            "neural_context_interpretation_id":
                f"NEURAL_CONTEXT:{len(interpretation_records) + 1}",

            "hybrid_candidate_id":
                candidate_id,

            "neural_semantic_source_layer":
                semantic_layer,

            "assessment_state":
                assessment_state,

            "interpretation_status":
                interpretation_status,

            "semantic_signal_count":
                semantic_signal_count,

            "context_outcome":
                _HYBRID_NEURAL_CONTEXT_OUTCOMES[
                    assessment_state
                ],

            "symbolic_boundary_respected":
                True,

            "semantic_override_allowed":
                False,

            "conflict_resolved":
                False,

            "interpreted":
                True,
        })

    candidates_with_explicit_context = sum(
        record["semantic_signal_count"] > 0
        for record in interpretation_records
    )

    candidates_without_explicit_context = (
        len(interpretation_records)
        - candidates_with_explicit_context
    )

    return {
        "schema_version":
            "symbolic_neural_hybrid_neural_context_interpretation_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15L",

        "status":
            "HYBRID_NEURAL_CONTEXT_INTERPRETED",

        "article_identity":
            deepcopy(
                article_identity
            ),

        "symbolic_evidence_records":
            deepcopy(
                constraint_result.get(
                    "symbolic_evidence_records",
                    [],
                )
            ),

        "neural_semantic_evidence_records":
            deepcopy(
                constraint_result.get(
                    "neural_semantic_evidence_records",
                    [],
                )
            ),

        "alignment_pairs":
            deepcopy(
                constraint_result.get(
                    "alignment_pairs",
                    [],
                )
            ),

        "agreement_conflict_assessments":
            deepcopy(
                constraint_result.get(
                    "agreement_conflict_assessments",
                    [],
                )
            ),

        "hybrid_reasoning_candidates":
            interpreted_candidates,

        "symbolic_constraint_enforcement_records":
            deepcopy(
                constraint_result.get(
                    "symbolic_constraint_enforcement_records",
                    [],
                )
            ),

        "neural_context_interpretation_records":
            interpretation_records,

        "unaligned_symbolic_evidence_ids":
            deepcopy(
                constraint_result.get(
                    "unaligned_symbolic_evidence_ids",
                    [],
                )
            ),

        "unaligned_neural_semantic_evidence_ids":
            deepcopy(
                constraint_result.get(
                    "unaligned_neural_semantic_evidence_ids",
                    [],
                )
            ),

        "article_context_boundary":
            deepcopy(
                article_context_boundary
            ),

        "neural_context_summary": {
            "candidate_count":
                len(
                    candidates
                ),

            "interpretation_record_count":
                len(
                    interpretation_records
                ),

            "all_candidates_interpreted":
                len(
                    interpretation_records
                )
                == len(
                    candidates
                ),

            "candidates_with_explicit_context_signals":
                candidates_with_explicit_context,

            "candidates_without_explicit_context_signals":
                candidates_without_explicit_context,

            "symbolic_boundary_respected":
                True,

            "semantic_override_allowed":
                False,

            "new_semantic_facts_created":
                False,

            "conflicts_resolved":
                False,

            "evidence_fused":
                False,

            "external_model_called":
                False,
        },

        "processing_boundaries": {
            "neural_context_interpretation_performed":
                True,

            "certified_semantic_evidence_only":
                True,

            "article_local_context_only":
                True,

            "hard_symbolic_authority_preserved":
                True,

            "semantic_override_allowed":
                False,

            "symbolic_evidence_mutation_performed":
                False,

            "symbolic_constraint_relaxation_performed":
                False,

            "new_semantic_fact_inference_performed":
                False,

            "semantic_equivalence_inference_performed":
                False,

            "hybrid_evidence_fusion_performed":
                False,

            "conflict_resolution_performed":
                False,

            "hybrid_confidence_calculated":
                False,

            "new_article_fact_inference_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "hybrid_evidence_fusion",
    }


# ============================================================================
# PATCH 4.6.15M — Hybrid Evidence Fusion
# ============================================================================

_HYBRID_FUSION_MODES = {
    "AGREEMENT":
        "GOVERNED_COMPATIBLE_EVIDENCE_FUSION",

    "CONFLICT":
        "GOVERNED_CONFLICT_PRESERVING_FUSION",

    "UNRESOLVED":
        "GOVERNED_UNRESOLVED_EVIDENCE_FUSION",
}


_HYBRID_FUSION_OUTCOMES = {
    "AGREEMENT":
        "FUSED_AGREEMENT_EVIDENCE_PRESERVED",

    "CONFLICT":
        "FUSED_WITH_CONFLICT_PRESERVED_FOR_RESOLUTION",

    "UNRESOLVED":
        "FUSED_WITH_UNRESOLVED_EVIDENCE_PRESERVED",
}


def fuse_hybrid_evidence(
    neural_context_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Perform evidence-preserving governed fusion after symbolic constraint
    enforcement and neural context interpretation.

    Fusion means packaging certified symbolic evidence, certified
    neural/semantic evidence, and certified semantic context into one
    governed hybrid evidence envelope.

    It does not:
    - average scores
    - rewrite symbolic evidence
    - collapse evidence into generated prose
    - resolve conflicts
    - strengthen unresolved evidence
    - calculate hybrid confidence
    - infer new article facts
    """

    if not isinstance(
        neural_context_result,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid evidence fusion requires the canonical L result."
        )

    if (
        neural_context_result.get("status")
        != "HYBRID_NEURAL_CONTEXT_INTERPRETED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Neural context has not been canonically interpreted."
        )

    if (
        neural_context_result.get("next_stage")
        != "hybrid_evidence_fusion"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "L does not hand off to hybrid evidence fusion."
        )

    article_identity = neural_context_result.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid evidence fusion is missing article_identity."
        )

    article_context_boundary = neural_context_result.get(
        "article_context_boundary"
    )

    if not isinstance(
        article_context_boundary,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid evidence fusion is missing the article-context boundary."
        )

    if (
        article_context_boundary.get(
            "context_access_policy"
        )
        != "CERTIFIED_ARTICLE_LOCAL_EVIDENCE_ONLY"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid fusion received an invalid article-context policy."
        )

    candidates = neural_context_result.get(
        "hybrid_reasoning_candidates"
    )

    if not isinstance(
        candidates,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "L hybrid reasoning candidates are missing."
        )

    fused_candidates: list[dict[str, Any]] = []
    fusion_records: list[dict[str, Any]] = []

    candidate_ids: set[str] = set()

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid L hybrid reasoning candidate."
            )

        candidate_id = candidate.get(
            "hybrid_candidate_id"
        )

        if not candidate_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Hybrid reasoning candidate is missing hybrid_candidate_id."
            )

        if candidate_id in candidate_ids:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate hybrid_candidate_id: {candidate_id}."
            )

        candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get("article_identity")
            != article_identity
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} belongs to a different article."
            )

        symbolic_layer = candidate.get(
            "symbolic_source_layer"
        )

        semantic_layer = candidate.get(
            "neural_semantic_source_layer"
        )

        if (
            symbolic_layer
            not in _SYMBOLIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid symbolic source layer."
            )

        if (
            semantic_layer
            not in _NEURAL_SEMANTIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid neural/semantic source layer."
            )

        expected_rule = (
            _SYMBOLIC_PRESERVATION_RULES.get(
                symbolic_layer
            )
        )

        if (
            candidate.get(
                "symbolic_preservation_rule"
            )
            != expected_rule
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost its symbolic preservation rule."
            )

        if (
            candidate.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost hard symbolic authority."
            )

        if (
            candidate.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic authority."
            )

        assessment_state = candidate.get(
            "assessment_state"
        )

        if (
            assessment_state
            not in _HYBRID_FUSION_MODES
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid assessment state."
            )

        expected_disposition = (
            _HYBRID_CANDIDATE_DISPOSITIONS[
                assessment_state
            ]
        )

        if (
            candidate.get(
                "candidate_disposition"
            )
            != expected_disposition
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an inconsistent candidate disposition."
            )

        processing_state = candidate.get(
            "candidate_processing_state"
        )

        if not isinstance(
            processing_state,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing candidate_processing_state."
            )

        if (
            processing_state.get("constructed")
            is not True
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} was not canonically constructed."
            )

        if (
            processing_state.get(
                "symbolic_constraint_enforced"
            )
            is not True
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} reached M without K enforcement."
            )

        if (
            processing_state.get(
                "neural_context_interpreted"
            )
            is not True
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} reached M without L interpretation."
            )

        if (
            processing_state.get(
                "evidence_fused"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} entered M with evidence already fused."
            )

        if (
            processing_state.get(
                "conflict_resolved"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} entered M with conflict resolution already performed."
            )

        if (
            processing_state.get(
                "hybrid_confidence_calculated"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} entered M with confidence already calculated."
            )

        expected_agreement = (
            assessment_state == "AGREEMENT"
        )

        expected_conflict = (
            assessment_state == "CONFLICT"
        )

        expected_unresolved = (
            assessment_state == "UNRESOLVED"
        )

        if (
            processing_state.get(
                "agreement_preserved"
            )
            is not expected_agreement
            or processing_state.get(
                "conflict_preserved"
            )
            is not expected_conflict
            or processing_state.get(
                "unresolved_preserved"
            )
            is not expected_unresolved
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has corrupted assessment-state preservation."
            )

        symbolic_enforcement = candidate.get(
            "symbolic_constraint_enforcement"
        )

        if not isinstance(
            symbolic_enforcement,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing K symbolic enforcement."
            )

        if (
            symbolic_enforcement.get(
                "enforcement_status"
            )
            != "ENFORCED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} does not have canonical K enforcement."
            )

        if (
            symbolic_enforcement.get(
                "preservation_rule"
            )
            != expected_rule
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} K preservation rule is inconsistent."
            )

        if (
            symbolic_enforcement.get(
                "constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} K symbolic authority is invalid."
            )

        if (
            symbolic_enforcement.get(
                "semantic_override_allowed"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} incorrectly permits semantic override."
            )

        if (
            symbolic_enforcement.get(
                "symbolic_evidence_mutated"
            )
            is not False
            or symbolic_enforcement.get(
                "symbolic_evidence_discarded"
            )
            is not False
            or symbolic_enforcement.get(
                "symbolic_constraint_relaxed"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains corrupted K enforcement state."
            )

        neural_context = candidate.get(
            "neural_context_interpretation"
        )

        if not isinstance(
            neural_context,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing L neural context interpretation."
            )

        if (
            neural_context.get(
                "source_layer"
            )
            != semantic_layer
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} neural-context source identity changed."
            )

        if (
            neural_context.get(
                "assessment_state"
            )
            != assessment_state
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} neural-context assessment state changed."
            )

        expected_context_outcome = (
            _HYBRID_NEURAL_CONTEXT_OUTCOMES[
                assessment_state
            ]
        )

        if (
            neural_context.get(
                "context_outcome"
            )
            != expected_context_outcome
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid L context outcome."
            )

        if (
            neural_context.get(
                "context_access_policy"
            )
            != "CERTIFIED_ARTICLE_LOCAL_EVIDENCE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid L context-access policy."
            )

        if (
            neural_context.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} lost hard symbolic authority inside L."
            )

        if (
            neural_context.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid L semantic authority."
            )

        if (
            neural_context.get(
                "semantic_override_allowed"
            )
            is not False
            or neural_context.get(
                "semantic_override_attempted"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains semantic override corruption."
            )

        if (
            neural_context.get(
                "symbolic_evidence_mutated"
            )
            is not False
            or neural_context.get(
                "symbolic_constraint_relaxed"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains symbolic-boundary corruption from L."
            )

        if (
            neural_context.get(
                "new_semantic_fact_inferred"
            )
            is not False
            or neural_context.get(
                "new_article_fact_inferred"
            )
            is not False
            or neural_context.get(
                "semantic_equivalence_inferred"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains unsupported L inference."
            )

        if (
            neural_context.get(
                "conflict_resolved"
            )
            is not False
            or neural_context.get(
                "evidence_fused"
            )
            is not False
            or neural_context.get(
                "external_model_called"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains invalid L downstream-stage state."
            )

        certified_context_signals = (
            neural_context.get(
                "certified_context_signals"
            )
        )

        if not isinstance(
            certified_context_signals,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid certified context signals."
            )

        symbolic_evidence = candidate.get(
            "symbolic_evidence"
        )

        semantic_evidence = candidate.get(
            "neural_semantic_evidence"
        )

        if not isinstance(
            symbolic_evidence,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing symbolic evidence."
            )

        if not isinstance(
            semantic_evidence,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing neural/semantic evidence."
            )

        if (
            symbolic_evidence.get(
                "evidence_side"
            )
            != "SYMBOLIC"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid symbolic evidence-side identity."
            )

        if (
            semantic_evidence.get(
                "evidence_side"
            )
            != "NEURAL_SEMANTIC"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic evidence-side identity."
            )

        if (
            symbolic_evidence.get(
                "source_layer"
            )
            != symbolic_layer
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} symbolic source identity changed."
            )

        if (
            semantic_evidence.get(
                "source_layer"
            )
            != semantic_layer
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} neural/semantic source identity changed."
            )

        if (
            symbolic_evidence.get(
                "evidence_id"
            )
            != candidate.get(
                "symbolic_evidence_id"
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} symbolic evidence identity is inconsistent."
            )

        if (
            semantic_evidence.get(
                "evidence_id"
            )
            != candidate.get(
                "neural_semantic_evidence_id"
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} neural/semantic evidence identity is inconsistent."
            )

        fused_candidate = deepcopy(
            dict(candidate)
        )

        fused_processing_state = deepcopy(
            dict(processing_state)
        )

        fused_processing_state[
            "evidence_fused"
        ] = True

        fused_candidate[
            "candidate_processing_state"
        ] = fused_processing_state

        fused_candidate[
            "hybrid_evidence_fusion"
        ] = {
            "fusion_status":
                "FUSED",

            "fusion_mode":
                _HYBRID_FUSION_MODES[
                    assessment_state
                ],

            "fusion_outcome":
                _HYBRID_FUSION_OUTCOMES[
                    assessment_state
                ],

            "assessment_state":
                assessment_state,

            "symbolic_component":
                deepcopy(
                    symbolic_evidence
                ),

            "neural_semantic_component":
                deepcopy(
                    semantic_evidence
                ),

            "neural_context_component":
                deepcopy(
                    neural_context
                ),

            "shared_grounding_anchors":
                deepcopy(
                    candidate.get(
                        "shared_grounding_anchors",
                        [],
                    )
                ),

            "shared_comparable_fields":
                deepcopy(
                    candidate.get(
                        "shared_comparable_fields",
                        [],
                    )
                ),

            "symbolic_preservation_rule":
                expected_rule,

            "symbolic_constraint_authority":
                "HARD_WHEN_EXPLICIT_AND_CERTIFIED",

            "neural_semantic_authority":
                "INTERPRETIVE_ONLY",

            "agreement_preserved":
                expected_agreement,

            "conflict_preserved":
                expected_conflict,

            "unresolved_preserved":
                expected_unresolved,

            "semantic_override_allowed":
                False,

            "symbolic_evidence_mutated":
                False,

            "neural_semantic_evidence_mutated":
                False,

            "symbolic_constraint_relaxed":
                False,

            "score_averaging_performed":
                False,

            "raw_evidence_concatenation_performed":
                False,

            "new_hybrid_fact_inferred":
                False,

            "new_article_fact_inferred":
                False,

            "conflict_resolved":
                False,

            "hybrid_confidence_calculated":
                False,

            "external_model_called":
                False,
        }

        fused_candidates.append(
            fused_candidate
        )

        fusion_records.append({
            "hybrid_fusion_id":
                f"HYBRID_FUSION:{len(fusion_records) + 1}",

            "hybrid_candidate_id":
                candidate_id,

            "assessment_state":
                assessment_state,

            "fusion_mode":
                _HYBRID_FUSION_MODES[
                    assessment_state
                ],

            "fusion_outcome":
                _HYBRID_FUSION_OUTCOMES[
                    assessment_state
                ],

            "symbolic_source_layer":
                symbolic_layer,

            "neural_semantic_source_layer":
                semantic_layer,

            "symbolic_boundary_respected":
                True,

            "semantic_override_allowed":
                False,

            "conflict_preserved":
                expected_conflict,

            "unresolved_preserved":
                expected_unresolved,

            "conflict_resolved":
                False,

            "fused":
                True,
        })

    agreement_fusion_count = sum(
        candidate["assessment_state"]
        == "AGREEMENT"
        for candidate in fused_candidates
    )

    conflict_fusion_count = sum(
        candidate["assessment_state"]
        == "CONFLICT"
        for candidate in fused_candidates
    )

    unresolved_fusion_count = sum(
        candidate["assessment_state"]
        == "UNRESOLVED"
        for candidate in fused_candidates
    )

    return {
        "schema_version":
            "symbolic_neural_hybrid_evidence_fusion_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15M",

        "status":
            "HYBRID_EVIDENCE_FUSED",

        "article_identity":
            deepcopy(
                article_identity
            ),

        "symbolic_evidence_records":
            deepcopy(
                neural_context_result.get(
                    "symbolic_evidence_records",
                    [],
                )
            ),

        "neural_semantic_evidence_records":
            deepcopy(
                neural_context_result.get(
                    "neural_semantic_evidence_records",
                    [],
                )
            ),

        "alignment_pairs":
            deepcopy(
                neural_context_result.get(
                    "alignment_pairs",
                    [],
                )
            ),

        "agreement_conflict_assessments":
            deepcopy(
                neural_context_result.get(
                    "agreement_conflict_assessments",
                    [],
                )
            ),

        "hybrid_reasoning_candidates":
            fused_candidates,

        "symbolic_constraint_enforcement_records":
            deepcopy(
                neural_context_result.get(
                    "symbolic_constraint_enforcement_records",
                    [],
                )
            ),

        "neural_context_interpretation_records":
            deepcopy(
                neural_context_result.get(
                    "neural_context_interpretation_records",
                    [],
                )
            ),

        "hybrid_evidence_fusion_records":
            fusion_records,

        "unaligned_symbolic_evidence_ids":
            deepcopy(
                neural_context_result.get(
                    "unaligned_symbolic_evidence_ids",
                    [],
                )
            ),

        "unaligned_neural_semantic_evidence_ids":
            deepcopy(
                neural_context_result.get(
                    "unaligned_neural_semantic_evidence_ids",
                    [],
                )
            ),

        "article_context_boundary":
            deepcopy(
                article_context_boundary
            ),

        "hybrid_fusion_summary": {
            "candidate_count":
                len(
                    candidates
                ),

            "fusion_record_count":
                len(
                    fusion_records
                ),

            "all_candidates_fused":
                len(
                    fusion_records
                )
                == len(
                    candidates
                ),

            "agreement_fusion_count":
                agreement_fusion_count,

            "conflict_preserving_fusion_count":
                conflict_fusion_count,

            "unresolved_preserving_fusion_count":
                unresolved_fusion_count,

            "symbolic_boundary_respected":
                True,

            "semantic_override_allowed":
                False,

            "score_averaging_performed":
                False,

            "raw_evidence_concatenation_performed":
                False,

            "new_hybrid_facts_created":
                False,

            "conflicts_resolved":
                False,

            "hybrid_confidence_calculated":
                False,
        },

        "processing_boundaries": {
            "hybrid_evidence_fusion_performed":
                True,

            "evidence_preserving_governed_fusion":
                True,

            "hard_symbolic_authority_preserved":
                True,

            "semantic_override_allowed":
                False,

            "symbolic_evidence_mutation_performed":
                False,

            "neural_semantic_evidence_mutation_performed":
                False,

            "symbolic_constraint_relaxation_performed":
                False,

            "score_averaging_performed":
                False,

            "raw_evidence_concatenation_performed":
                False,

            "new_hybrid_fact_inference_performed":
                False,

            "conflict_resolution_performed":
                False,

            "hybrid_confidence_calculated":
                False,

            "new_article_fact_inference_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "contradiction_conflict_resolution",
    }


# ============================================================================
# PATCH 4.6.15N — Contradiction / Conflict Resolution
# ============================================================================

_HYBRID_CONFLICT_RESOLUTION_POLICIES = {
    "AGREEMENT": {
        "resolution_status":
            "NO_CONFLICT_TO_RESOLVE",

        "governance_decision":
            "AGREEMENT_PRESERVED",

        "selected_authority":
            "NONE_REQUIRED",

        "final_resolution_state":
            "AGREEMENT",
    },

    "CONFLICT": {
        "resolution_status":
            "RESOLVED_BY_HARD_SYMBOLIC_AUTHORITY",

        "governance_decision":
            "SYMBOLIC_CONSTRAINT_PREVAILS_FOR_HYBRID_OUTPUT",

        "selected_authority":
            "SYMBOLIC",

        "final_resolution_state":
            "SYMBOLIC_CONSTRAINT_GOVERNED",
    },

    "UNRESOLVED": {
        "resolution_status":
            "UNRESOLVED_PRESERVED",

        "governance_decision":
            "ABSTAIN_PRESERVE_UNRESOLVED",

        "selected_authority":
            "NONE",

        "final_resolution_state":
            "UNRESOLVED",
    },
}


def resolve_hybrid_contradictions_conflicts(
    fusion_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve hybrid governance conflicts after evidence-preserving fusion.

    A certified explicit symbolic constraint has hard authority when an
    already-detected conflict exists. This is an operational governance
    decision, not an external truth assessment.

    Both evidence sides remain preserved.

    UNRESOLVED evidence remains unresolved and is never forced into a
    winner.
    """

    if not isinstance(
        fusion_result,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Conflict resolution requires the canonical M result."
        )

    if (
        fusion_result.get("status")
        != "HYBRID_EVIDENCE_FUSED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid evidence has not been canonically fused."
        )

    if (
        fusion_result.get("next_stage")
        != "contradiction_conflict_resolution"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "M does not hand off to contradiction/conflict resolution."
        )

    article_identity = fusion_result.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Conflict resolution is missing article_identity."
        )

    article_context_boundary = fusion_result.get(
        "article_context_boundary"
    )

    if not isinstance(
        article_context_boundary,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Conflict resolution is missing the article-context boundary."
        )

    if (
        article_context_boundary.get(
            "context_access_policy"
        )
        != "CERTIFIED_ARTICLE_LOCAL_EVIDENCE_ONLY"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Conflict resolution received an invalid article-context policy."
        )

    candidates = fusion_result.get(
        "hybrid_reasoning_candidates"
    )

    if not isinstance(
        candidates,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "M hybrid reasoning candidates are missing."
        )

    resolved_candidates: list[dict[str, Any]] = []
    resolution_records: list[dict[str, Any]] = []

    candidate_ids: set[str] = set()

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid M hybrid reasoning candidate."
            )

        candidate_id = candidate.get(
            "hybrid_candidate_id"
        )

        if not candidate_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Hybrid reasoning candidate is missing hybrid_candidate_id."
            )

        if candidate_id in candidate_ids:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate hybrid_candidate_id: {candidate_id}."
            )

        candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get("article_identity")
            != article_identity
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} belongs to a different article."
            )

        symbolic_layer = candidate.get(
            "symbolic_source_layer"
        )

        semantic_layer = candidate.get(
            "neural_semantic_source_layer"
        )

        if (
            symbolic_layer
            not in _SYMBOLIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid symbolic source layer."
            )

        if (
            semantic_layer
            not in _NEURAL_SEMANTIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid neural/semantic source layer."
            )

        expected_rule = (
            _SYMBOLIC_PRESERVATION_RULES.get(
                symbolic_layer
            )
        )

        if (
            candidate.get(
                "symbolic_preservation_rule"
            )
            != expected_rule
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost its symbolic preservation rule."
            )

        if (
            candidate.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost hard symbolic authority."
            )

        if (
            candidate.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic authority."
            )

        assessment_state = candidate.get(
            "assessment_state"
        )

        if (
            assessment_state
            not in _HYBRID_CONFLICT_RESOLUTION_POLICIES
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid assessment state."
            )

        expected_disposition = (
            _HYBRID_CANDIDATE_DISPOSITIONS[
                assessment_state
            ]
        )

        if (
            candidate.get(
                "candidate_disposition"
            )
            != expected_disposition
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an inconsistent candidate disposition."
            )

        processing_state = candidate.get(
            "candidate_processing_state"
        )

        if not isinstance(
            processing_state,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing candidate_processing_state."
            )

        if (
            processing_state.get("constructed")
            is not True
            or processing_state.get(
                "symbolic_constraint_enforced"
            )
            is not True
            or processing_state.get(
                "neural_context_interpreted"
            )
            is not True
            or processing_state.get(
                "evidence_fused"
            )
            is not True
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has not completed J-K-L-M processing."
            )

        if (
            processing_state.get(
                "conflict_resolved"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} entered N with conflict already resolved."
            )

        if (
            processing_state.get(
                "hybrid_confidence_calculated"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} entered N with confidence already calculated."
            )

        expected_agreement = (
            assessment_state == "AGREEMENT"
        )

        expected_conflict = (
            assessment_state == "CONFLICT"
        )

        expected_unresolved = (
            assessment_state == "UNRESOLVED"
        )

        if (
            processing_state.get(
                "agreement_preserved"
            )
            is not expected_agreement
            or processing_state.get(
                "conflict_preserved"
            )
            is not expected_conflict
            or processing_state.get(
                "unresolved_preserved"
            )
            is not expected_unresolved
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has corrupted assessment-state preservation."
            )

        fusion = candidate.get(
            "hybrid_evidence_fusion"
        )

        if not isinstance(
            fusion,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing M hybrid fusion."
            )

        if (
            fusion.get("fusion_status")
            != "FUSED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} does not contain canonical M fusion."
            )

        if (
            fusion.get("assessment_state")
            != assessment_state
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} M assessment state changed."
            )

        if (
            fusion.get("fusion_mode")
            != _HYBRID_FUSION_MODES[
                assessment_state
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid M fusion mode."
            )

        if (
            fusion.get("fusion_outcome")
            != _HYBRID_FUSION_OUTCOMES[
                assessment_state
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid M fusion outcome."
            )

        if (
            fusion.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} lost symbolic authority inside M fusion."
            )

        if (
            fusion.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid semantic authority inside M."
            )

        if (
            fusion.get(
                "semantic_override_allowed"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} M fusion permits semantic override."
            )

        if (
            fusion.get(
                "symbolic_evidence_mutated"
            )
            is not False
            or fusion.get(
                "neural_semantic_evidence_mutated"
            )
            is not False
            or fusion.get(
                "symbolic_constraint_relaxed"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains mutated or relaxed M evidence."
            )

        if (
            fusion.get(
                "score_averaging_performed"
            )
            is not False
            or fusion.get(
                "raw_evidence_concatenation_performed"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains invalid M fusion mechanics."
            )

        if (
            fusion.get(
                "new_hybrid_fact_inferred"
            )
            is not False
            or fusion.get(
                "new_article_fact_inferred"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains unsupported M inference."
            )

        if (
            fusion.get(
                "conflict_resolved"
            )
            is not False
            or fusion.get(
                "hybrid_confidence_calculated"
            )
            is not False
            or fusion.get(
                "external_model_called"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains premature downstream M state."
            )

        symbolic_component = fusion.get(
            "symbolic_component"
        )

        semantic_component = fusion.get(
            "neural_semantic_component"
        )

        neural_context_component = fusion.get(
            "neural_context_component"
        )

        if not isinstance(
            symbolic_component,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} M fusion is missing symbolic component."
            )

        if not isinstance(
            semantic_component,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} M fusion is missing semantic component."
            )

        if not isinstance(
            neural_context_component,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} M fusion is missing neural context component."
            )

        if (
            symbolic_component
            != candidate.get(
                "symbolic_evidence"
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} M symbolic fusion component changed."
            )

        if (
            semantic_component
            != candidate.get(
                "neural_semantic_evidence"
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} M semantic fusion component changed."
            )

        if (
            neural_context_component
            != candidate.get(
                "neural_context_interpretation"
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} M neural-context component changed."
            )

        policy = (
            _HYBRID_CONFLICT_RESOLUTION_POLICIES[
                assessment_state
            ]
        )

        conflict_present = (
            assessment_state == "CONFLICT"
        )

        resolution_required = (
            assessment_state == "CONFLICT"
        )

        conflict_operationally_resolved = (
            assessment_state == "CONFLICT"
        )

        abstention_required = (
            assessment_state == "UNRESOLVED"
        )

        resolved_candidate = deepcopy(
            dict(candidate)
        )

        resolved_processing_state = deepcopy(
            dict(processing_state)
        )

        resolved_processing_state[
            "conflict_resolved"
        ] = conflict_operationally_resolved

        resolved_candidate[
            "candidate_processing_state"
        ] = resolved_processing_state

        resolved_candidate[
            "contradiction_conflict_resolution"
        ] = {
            "resolution_status":
                policy[
                    "resolution_status"
                ],

            "input_assessment_state":
                assessment_state,

            "conflict_present":
                conflict_present,

            "resolution_required":
                resolution_required,

            "governance_decision":
                policy[
                    "governance_decision"
                ],

            "selected_authority":
                policy[
                    "selected_authority"
                ],

            "final_resolution_state":
                policy[
                    "final_resolution_state"
                ],

            "symbolic_preservation_rule":
                expected_rule,

            "symbolic_constraint_authority":
                "HARD_WHEN_EXPLICIT_AND_CERTIFIED",

            "neural_semantic_authority":
                "INTERPRETIVE_ONLY",

            "symbolic_component_preserved":
                True,

            "neural_semantic_component_preserved":
                True,

            "neural_context_component_preserved":
                True,

            "conflict_evidence_preserved":
                conflict_present,

            "unresolved_evidence_preserved":
                expected_unresolved,

            "semantic_evidence_discarded":
                False,

            "semantic_evidence_declared_false":
                False,

            "symbolic_evidence_mutated":
                False,

            "symbolic_constraint_relaxed":
                False,

            "semantic_override_allowed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "new_hybrid_fact_inferred":
                False,

            "new_article_fact_inferred":
                False,

            "abstention_required":
                abstention_required,

            "conflict_operationally_resolved":
                conflict_operationally_resolved,

            "hybrid_confidence_calculated":
                False,

            "external_model_called":
                False,
        }

        resolved_candidates.append(
            resolved_candidate
        )

        resolution_records.append({
            "conflict_resolution_id":
                f"HYBRID_CONFLICT_RESOLUTION:"
                f"{len(resolution_records) + 1}",

            "hybrid_candidate_id":
                candidate_id,

            "input_assessment_state":
                assessment_state,

            "resolution_status":
                policy[
                    "resolution_status"
                ],

            "governance_decision":
                policy[
                    "governance_decision"
                ],

            "selected_authority":
                policy[
                    "selected_authority"
                ],

            "final_resolution_state":
                policy[
                    "final_resolution_state"
                ],

            "conflict_present":
                conflict_present,

            "conflict_operationally_resolved":
                conflict_operationally_resolved,

            "abstention_required":
                abstention_required,

            "symbolic_boundary_respected":
                True,

            "both_evidence_sides_preserved":
                True,

            "truth_assessment_performed":
                False,

            "resolved_stage_processed":
                True,
        })

    actual_conflict_count = sum(
        record["conflict_present"]
        for record in resolution_records
    )

    operationally_resolved_conflict_count = sum(
        record[
            "conflict_operationally_resolved"
        ]
        for record in resolution_records
    )

    unresolved_preserved_count = sum(
        record[
            "final_resolution_state"
        ]
        == "UNRESOLVED"
        for record in resolution_records
    )

    agreement_preserved_count = sum(
        record[
            "final_resolution_state"
        ]
        == "AGREEMENT"
        for record in resolution_records
    )

    return {
        "schema_version":
            "symbolic_neural_hybrid_conflict_resolution_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15N",

        "status":
            "HYBRID_CONFLICT_RESOLUTION_COMPLETE",

        "article_identity":
            deepcopy(
                article_identity
            ),

        "symbolic_evidence_records":
            deepcopy(
                fusion_result.get(
                    "symbolic_evidence_records",
                    [],
                )
            ),

        "neural_semantic_evidence_records":
            deepcopy(
                fusion_result.get(
                    "neural_semantic_evidence_records",
                    [],
                )
            ),

        "alignment_pairs":
            deepcopy(
                fusion_result.get(
                    "alignment_pairs",
                    [],
                )
            ),

        "agreement_conflict_assessments":
            deepcopy(
                fusion_result.get(
                    "agreement_conflict_assessments",
                    [],
                )
            ),

        "hybrid_reasoning_candidates":
            resolved_candidates,

        "symbolic_constraint_enforcement_records":
            deepcopy(
                fusion_result.get(
                    "symbolic_constraint_enforcement_records",
                    [],
                )
            ),

        "neural_context_interpretation_records":
            deepcopy(
                fusion_result.get(
                    "neural_context_interpretation_records",
                    [],
                )
            ),

        "hybrid_evidence_fusion_records":
            deepcopy(
                fusion_result.get(
                    "hybrid_evidence_fusion_records",
                    [],
                )
            ),

        "contradiction_conflict_resolution_records":
            resolution_records,

        "unaligned_symbolic_evidence_ids":
            deepcopy(
                fusion_result.get(
                    "unaligned_symbolic_evidence_ids",
                    [],
                )
            ),

        "unaligned_neural_semantic_evidence_ids":
            deepcopy(
                fusion_result.get(
                    "unaligned_neural_semantic_evidence_ids",
                    [],
                )
            ),

        "article_context_boundary":
            deepcopy(
                article_context_boundary
            ),

        "conflict_resolution_summary": {
            "candidate_count":
                len(
                    candidates
                ),

            "resolution_record_count":
                len(
                    resolution_records
                ),

            "all_candidates_processed":
                len(
                    resolution_records
                )
                == len(
                    candidates
                ),

            "actual_conflict_count":
                actual_conflict_count,

            "operationally_resolved_conflict_count":
                operationally_resolved_conflict_count,

            "agreement_preserved_count":
                agreement_preserved_count,

            "unresolved_preserved_count":
                unresolved_preserved_count,

            "hard_symbolic_authority_applied_to_conflicts":
                True,

            "both_evidence_sides_preserved":
                True,

            "semantic_evidence_discarded":
                False,

            "semantic_evidence_declared_false":
                False,

            "truth_assessment_performed":
                False,

            "forced_unresolved_resolution_performed":
                False,

            "hybrid_confidence_calculated":
                False,
        },

        "processing_boundaries": {
            "contradiction_conflict_resolution_stage_performed":
                True,

            "explicit_conflict_governance_resolution_performed":
                actual_conflict_count > 0,

            "hard_symbolic_authority_preserved":
                True,

            "semantic_override_allowed":
                False,

            "both_evidence_sides_preserved":
                True,

            "semantic_evidence_discard_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "forced_unresolved_resolution_performed":
                False,

            "symbolic_evidence_mutation_performed":
                False,

            "symbolic_constraint_relaxation_performed":
                False,

            "new_hybrid_fact_inference_performed":
                False,

            "new_article_fact_inference_performed":
                False,

            "hybrid_confidence_calculated":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "hybrid_confidence_assessment",
    }


# ============================================================================
# PATCH 4.6.15O — Hybrid Confidence Assessment
# ============================================================================

_HYBRID_CONFIDENCE_POLICIES = {
    "AGREEMENT": {
        "confidence_class":
            "EXPLICIT_AGREEMENT_SUPPORTED",

        "confidence_basis":
            "EXPLICIT_COMPARABLE_EVIDENCE_AGREEMENT",

        "downstream_reliance_mode":
            "AGREEMENT_SUPPORTED_WITH_PROVENANCE",

        "confidence_limited_by_conflict":
            False,

        "abstention_required":
            False,
    },

    "CONFLICT": {
        "confidence_class":
            "SYMBOLICALLY_GOVERNED_CONFLICT",

        "confidence_basis":
            "HARD_SYMBOLIC_AUTHORITY_WITH_PRESERVED_CONFLICT",

        "downstream_reliance_mode":
            "SYMBOLIC_CONSTRAINT_WITH_CONFLICT_PROVENANCE",

        "confidence_limited_by_conflict":
            True,

        "abstention_required":
            False,
    },

    "UNRESOLVED": {
        "confidence_class":
            "INSUFFICIENT_EVIDENCE",

        "confidence_basis":
            "UNRESOLVED_OR_PARTIAL_EXPLICIT_EVIDENCE",

        "downstream_reliance_mode":
            "ABSTAIN",

        "confidence_limited_by_conflict":
            False,

        "abstention_required":
            True,
    },
}


def assess_hybrid_confidence(
    conflict_resolution_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Assess deterministic structural confidence after canonical conflict
    governance.

    4.6.15O does NOT calculate truth probability or invent a numerical
    confidence percentage.

    Confidence classes describe the structural state of the certified
    evidence:

    - AGREEMENT:
      explicit certified agreement is available.

    - CONFLICT:
      a hard symbolic constraint governs the hybrid output, but the
      preserved disagreement limits confidence.

    - UNRESOLVED:
      evidence remains insufficient and downstream reasoning must abstain.
    """

    if not isinstance(
        conflict_resolution_result,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid confidence assessment requires the canonical N result."
        )

    if (
        conflict_resolution_result.get("status")
        != "HYBRID_CONFLICT_RESOLUTION_COMPLETE"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Conflict resolution has not been canonically completed."
        )

    if (
        conflict_resolution_result.get("next_stage")
        != "hybrid_confidence_assessment"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "N does not hand off to hybrid confidence assessment."
        )

    article_identity = conflict_resolution_result.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid confidence assessment is missing article_identity."
        )

    article_context_boundary = (
        conflict_resolution_result.get(
            "article_context_boundary"
        )
    )

    if not isinstance(
        article_context_boundary,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid confidence assessment is missing the article-context boundary."
        )

    if (
        article_context_boundary.get(
            "context_access_policy"
        )
        != "CERTIFIED_ARTICLE_LOCAL_EVIDENCE_ONLY"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid confidence assessment received an invalid context policy."
        )

    candidates = conflict_resolution_result.get(
        "hybrid_reasoning_candidates"
    )

    if not isinstance(
        candidates,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "N hybrid reasoning candidates are missing."
        )

    assessed_candidates: list[dict[str, Any]] = []
    confidence_records: list[dict[str, Any]] = []

    candidate_ids: set[str] = set()

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid N hybrid reasoning candidate."
            )

        candidate_id = candidate.get(
            "hybrid_candidate_id"
        )

        if not candidate_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Hybrid reasoning candidate is missing hybrid_candidate_id."
            )

        if candidate_id in candidate_ids:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate hybrid_candidate_id: {candidate_id}."
            )

        candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get("article_identity")
            != article_identity
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} belongs to a different article."
            )

        symbolic_layer = candidate.get(
            "symbolic_source_layer"
        )

        semantic_layer = candidate.get(
            "neural_semantic_source_layer"
        )

        if (
            symbolic_layer
            not in _SYMBOLIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid symbolic source layer."
            )

        if (
            semantic_layer
            not in _NEURAL_SEMANTIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid neural/semantic source layer."
            )

        expected_rule = (
            _SYMBOLIC_PRESERVATION_RULES.get(
                symbolic_layer
            )
        )

        if (
            candidate.get(
                "symbolic_preservation_rule"
            )
            != expected_rule
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost its symbolic preservation rule."
            )

        if (
            candidate.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost hard symbolic authority."
            )

        if (
            candidate.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic authority."
            )

        assessment_state = candidate.get(
            "assessment_state"
        )

        if (
            assessment_state
            not in _HYBRID_CONFIDENCE_POLICIES
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid assessment state."
            )

        expected_disposition = (
            _HYBRID_CANDIDATE_DISPOSITIONS[
                assessment_state
            ]
        )

        if (
            candidate.get(
                "candidate_disposition"
            )
            != expected_disposition
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an inconsistent candidate disposition."
            )

        processing_state = candidate.get(
            "candidate_processing_state"
        )

        if not isinstance(
            processing_state,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing candidate_processing_state."
            )

        if (
            processing_state.get("constructed")
            is not True
            or processing_state.get(
                "symbolic_constraint_enforced"
            )
            is not True
            or processing_state.get(
                "neural_context_interpreted"
            )
            is not True
            or processing_state.get(
                "evidence_fused"
            )
            is not True
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has not completed J-K-L-M processing."
            )

        if (
            processing_state.get(
                "hybrid_confidence_calculated"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} entered O with confidence already assessed."
            )

        expected_agreement = (
            assessment_state == "AGREEMENT"
        )

        expected_conflict = (
            assessment_state == "CONFLICT"
        )

        expected_unresolved = (
            assessment_state == "UNRESOLVED"
        )

        if (
            processing_state.get(
                "agreement_preserved"
            )
            is not expected_agreement
            or processing_state.get(
                "conflict_preserved"
            )
            is not expected_conflict
            or processing_state.get(
                "unresolved_preserved"
            )
            is not expected_unresolved
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has corrupted assessment-state preservation."
            )

        expected_conflict_resolved = (
            assessment_state == "CONFLICT"
        )

        if (
            processing_state.get(
                "conflict_resolved"
            )
            is not expected_conflict_resolved
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid N conflict-resolution state."
            )

        resolution = candidate.get(
            "contradiction_conflict_resolution"
        )

        if not isinstance(
            resolution,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing N conflict resolution."
            )

        expected_resolution_policy = (
            _HYBRID_CONFLICT_RESOLUTION_POLICIES[
                assessment_state
            ]
        )

        if (
            resolution.get(
                "input_assessment_state"
            )
            != assessment_state
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} N assessment state changed."
            )

        for policy_field in (
            "resolution_status",
            "governance_decision",
            "selected_authority",
            "final_resolution_state",
        ):
            if (
                resolution.get(
                    policy_field
                )
                != expected_resolution_policy[
                    policy_field
                ]
            ):
                raise SymbolicNeuralHybridIntelligenceError(
                    f"{candidate_id} has an invalid N {policy_field}."
                )

        if (
            resolution.get(
                "conflict_present"
            )
            is not expected_conflict
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent N conflict presence."
            )

        if (
            resolution.get(
                "resolution_required"
            )
            is not expected_conflict
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent N resolution requirement."
            )

        if (
            resolution.get(
                "conflict_operationally_resolved"
            )
            is not expected_conflict
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent operational conflict resolution."
            )

        if (
            resolution.get(
                "abstention_required"
            )
            is not expected_unresolved
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent N abstention state."
            )

        if (
            resolution.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} lost hard symbolic authority in N."
            )

        if (
            resolution.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid semantic authority in N."
            )

        if (
            resolution.get(
                "symbolic_component_preserved"
            )
            is not True
            or resolution.get(
                "neural_semantic_component_preserved"
            )
            is not True
            or resolution.get(
                "neural_context_component_preserved"
            )
            is not True
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} did not preserve canonical evidence components."
            )

        if (
            resolution.get(
                "semantic_evidence_discarded"
            )
            is not False
            or resolution.get(
                "semantic_evidence_declared_false"
            )
            is not False
            or resolution.get(
                "symbolic_evidence_mutated"
            )
            is not False
            or resolution.get(
                "symbolic_constraint_relaxed"
            )
            is not False
            or resolution.get(
                "semantic_override_allowed"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains invalid N authority/evidence state."
            )

        if (
            resolution.get(
                "truth_assessment_performed"
            )
            is not False
            or resolution.get(
                "external_validation_performed"
            )
            is not False
            or resolution.get(
                "new_hybrid_fact_inferred"
            )
            is not False
            or resolution.get(
                "new_article_fact_inferred"
            )
            is not False
            or resolution.get(
                "hybrid_confidence_calculated"
            )
            is not False
            or resolution.get(
                "external_model_called"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains unsupported or premature N state."
            )

        fusion = candidate.get(
            "hybrid_evidence_fusion"
        )

        if not isinstance(
            fusion,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing M hybrid fusion."
            )

        if (
            fusion.get(
                "fusion_status"
            )
            != "FUSED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} does not contain canonical M fusion."
            )

        policy = (
            _HYBRID_CONFIDENCE_POLICIES[
                assessment_state
            ]
        )

        explicit_shared_grounding_present = bool(
            candidate.get(
                "shared_grounding_anchors",
                [],
            )
        )

        explicit_comparable_fields_present = bool(
            candidate.get(
                "shared_comparable_fields",
                [],
            )
        )

        assessed_candidate = deepcopy(
            dict(candidate)
        )

        assessed_processing_state = deepcopy(
            dict(processing_state)
        )

        assessed_processing_state[
            "hybrid_confidence_calculated"
        ] = True

        assessed_candidate[
            "candidate_processing_state"
        ] = assessed_processing_state

        assessed_candidate[
            "hybrid_confidence_assessment"
        ] = {
            "assessment_status":
                "ASSESSED",

            "confidence_scope":
                "STRUCTURAL_REASONING_CONFIDENCE_NOT_TRUTH_PROBABILITY",

            "confidence_class":
                policy[
                    "confidence_class"
                ],

            "confidence_basis":
                policy[
                    "confidence_basis"
                ],

            "downstream_reliance_mode":
                policy[
                    "downstream_reliance_mode"
                ],

            "input_assessment_state":
                assessment_state,

            "final_resolution_state":
                resolution[
                    "final_resolution_state"
                ],

            "explicit_shared_grounding_present":
                explicit_shared_grounding_present,

            "explicit_comparable_fields_present":
                explicit_comparable_fields_present,

            "hard_symbolic_authority_preserved":
                True,

            "semantic_authority":
                "INTERPRETIVE_ONLY",

            "confidence_limited_by_conflict":
                policy[
                    "confidence_limited_by_conflict"
                ],

            "abstention_required":
                policy[
                    "abstention_required"
                ],

            "source_uncertainty_preserved":
                True,

            "source_commitment_strengthened":
                False,

            "numeric_probability_generated":
                False,

            "numeric_confidence_score_generated":
                False,

            "truth_probability_estimated":
                False,

            "semantic_override_allowed":
                False,

            "symbolic_evidence_mutated":
                False,

            "semantic_evidence_mutated":
                False,

            "symbolic_constraint_relaxed":
                False,

            "new_hybrid_fact_inferred":
                False,

            "new_article_fact_inferred":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,
        }

        assessed_candidates.append(
            assessed_candidate
        )

        confidence_records.append({
            "hybrid_confidence_id":
                f"HYBRID_CONFIDENCE:"
                f"{len(confidence_records) + 1}",

            "hybrid_candidate_id":
                candidate_id,

            "input_assessment_state":
                assessment_state,

            "final_resolution_state":
                resolution[
                    "final_resolution_state"
                ],

            "confidence_class":
                policy[
                    "confidence_class"
                ],

            "confidence_basis":
                policy[
                    "confidence_basis"
                ],

            "downstream_reliance_mode":
                policy[
                    "downstream_reliance_mode"
                ],

            "confidence_limited_by_conflict":
                policy[
                    "confidence_limited_by_conflict"
                ],

            "abstention_required":
                policy[
                    "abstention_required"
                ],

            "numeric_confidence_generated":
                False,

            "truth_probability_estimated":
                False,

            "symbolic_boundary_respected":
                True,

            "assessed":
                True,
        })

    agreement_supported_count = sum(
        record["confidence_class"]
        == "EXPLICIT_AGREEMENT_SUPPORTED"
        for record in confidence_records
    )

    governed_conflict_count = sum(
        record["confidence_class"]
        == "SYMBOLICALLY_GOVERNED_CONFLICT"
        for record in confidence_records
    )

    insufficient_evidence_count = sum(
        record["confidence_class"]
        == "INSUFFICIENT_EVIDENCE"
        for record in confidence_records
    )

    abstention_count = sum(
        record["abstention_required"]
        for record in confidence_records
    )

    return {
        "schema_version":
            "symbolic_neural_hybrid_confidence_assessment_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15O",

        "status":
            "HYBRID_CONFIDENCE_ASSESSED",

        "article_identity":
            deepcopy(
                article_identity
            ),

        "symbolic_evidence_records":
            deepcopy(
                conflict_resolution_result.get(
                    "symbolic_evidence_records",
                    [],
                )
            ),

        "neural_semantic_evidence_records":
            deepcopy(
                conflict_resolution_result.get(
                    "neural_semantic_evidence_records",
                    [],
                )
            ),

        "alignment_pairs":
            deepcopy(
                conflict_resolution_result.get(
                    "alignment_pairs",
                    [],
                )
            ),

        "agreement_conflict_assessments":
            deepcopy(
                conflict_resolution_result.get(
                    "agreement_conflict_assessments",
                    [],
                )
            ),

        "hybrid_reasoning_candidates":
            assessed_candidates,

        "symbolic_constraint_enforcement_records":
            deepcopy(
                conflict_resolution_result.get(
                    "symbolic_constraint_enforcement_records",
                    [],
                )
            ),

        "neural_context_interpretation_records":
            deepcopy(
                conflict_resolution_result.get(
                    "neural_context_interpretation_records",
                    [],
                )
            ),

        "hybrid_evidence_fusion_records":
            deepcopy(
                conflict_resolution_result.get(
                    "hybrid_evidence_fusion_records",
                    [],
                )
            ),

        "contradiction_conflict_resolution_records":
            deepcopy(
                conflict_resolution_result.get(
                    "contradiction_conflict_resolution_records",
                    [],
                )
            ),

        "hybrid_confidence_records":
            confidence_records,

        "unaligned_symbolic_evidence_ids":
            deepcopy(
                conflict_resolution_result.get(
                    "unaligned_symbolic_evidence_ids",
                    [],
                )
            ),

        "unaligned_neural_semantic_evidence_ids":
            deepcopy(
                conflict_resolution_result.get(
                    "unaligned_neural_semantic_evidence_ids",
                    [],
                )
            ),

        "article_context_boundary":
            deepcopy(
                article_context_boundary
            ),

        "hybrid_confidence_summary": {
            "candidate_count":
                len(
                    candidates
                ),

            "confidence_record_count":
                len(
                    confidence_records
                ),

            "all_candidates_assessed":
                len(
                    confidence_records
                )
                == len(
                    candidates
                ),

            "explicit_agreement_supported_count":
                agreement_supported_count,

            "symbolically_governed_conflict_count":
                governed_conflict_count,

            "insufficient_evidence_count":
                insufficient_evidence_count,

            "abstention_count":
                abstention_count,

            "confidence_scope":
                "STRUCTURAL_REASONING_CONFIDENCE_NOT_TRUTH_PROBABILITY",

            "numeric_probability_generated":
                False,

            "numeric_confidence_score_generated":
                False,

            "truth_probability_estimated":
                False,

            "source_uncertainty_preserved":
                True,

            "source_commitment_strengthened":
                False,

            "hard_symbolic_authority_preserved":
                True,
        },

        "processing_boundaries": {
            "hybrid_confidence_assessment_performed":
                True,

            "categorical_structural_confidence_only":
                True,

            "numeric_probability_generated":
                False,

            "numeric_confidence_score_generated":
                False,

            "truth_probability_estimated":
                False,

            "source_uncertainty_preserved":
                True,

            "source_commitment_strengthening_performed":
                False,

            "hard_symbolic_authority_preserved":
                True,

            "semantic_override_allowed":
                False,

            "symbolic_evidence_mutation_performed":
                False,

            "semantic_evidence_mutation_performed":
                False,

            "symbolic_constraint_relaxation_performed":
                False,

            "new_hybrid_fact_inference_performed":
                False,

            "new_article_fact_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "reasoning_provenance_explainability_preparation",
    }




# ============================================================================
# PATCH 4.6.15P — Reasoning Provenance / Explainability Preparation
# ============================================================================

_HYBRID_EXPLAINABILITY_OUTCOMES = {
    "AGREEMENT":
        "EXPLAINABLE_AGREEMENT_TRACE_PREPARED",

    "CONFLICT":
        "EXPLAINABLE_SYMBOLIC_GOVERNANCE_TRACE_PREPARED",

    "UNRESOLVED":
        "EXPLAINABLE_ABSTENTION_TRACE_PREPARED",
}


def prepare_hybrid_reasoning_provenance_explainability(
    confidence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Prepare a deterministic, structured provenance trace from the
    already-certified hybrid reasoning stages.

    No new reasoning, evidence rewriting, confidence recalculation,
    truth assessment, duplicate resolution, or article consolidation
    occurs here.
    """

    if not isinstance(
        confidence_result,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Provenance preparation requires the canonical O result."
        )

    if (
        confidence_result.get("status")
        != "HYBRID_CONFIDENCE_ASSESSED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Hybrid confidence has not been canonically assessed."
        )

    if (
        confidence_result.get("next_stage")
        != "reasoning_provenance_explainability_preparation"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "O does not hand off to provenance/explainability preparation."
        )

    if (
        confidence_result.get("persistence_policy")
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "P requires article-local transient intelligence."
        )

    article_identity = confidence_result.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Provenance preparation is missing article_identity."
        )

    article_context_boundary = confidence_result.get(
        "article_context_boundary"
    )

    if not isinstance(
        article_context_boundary,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Provenance preparation is missing the article-context boundary."
        )

    if (
        article_context_boundary.get(
            "context_access_policy"
        )
        != "CERTIFIED_ARTICLE_LOCAL_EVIDENCE_ONLY"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Provenance preparation received an invalid context policy."
        )

    candidates = confidence_result.get(
        "hybrid_reasoning_candidates"
    )

    if not isinstance(
        candidates,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "O hybrid reasoning candidates are missing."
        )

    prepared_candidates: list[dict[str, Any]] = []
    provenance_records: list[dict[str, Any]] = []

    candidate_ids: set[str] = set()

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid O hybrid reasoning candidate."
            )

        candidate_id = candidate.get(
            "hybrid_candidate_id"
        )

        if not candidate_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Hybrid reasoning candidate is missing hybrid_candidate_id."
            )

        if candidate_id in candidate_ids:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate hybrid_candidate_id: {candidate_id}."
            )

        candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get("article_identity")
            != article_identity
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} belongs to a different article."
            )

        assessment_state = candidate.get(
            "assessment_state"
        )

        if (
            assessment_state
            not in _HYBRID_EXPLAINABILITY_OUTCOMES
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid assessment state."
            )

        symbolic_layer = candidate.get(
            "symbolic_source_layer"
        )

        semantic_layer = candidate.get(
            "neural_semantic_source_layer"
        )

        if (
            symbolic_layer
            not in _SYMBOLIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid symbolic source layer."
            )

        if (
            semantic_layer
            not in _NEURAL_SEMANTIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid neural/semantic source layer."
            )

        expected_rule = (
            _SYMBOLIC_PRESERVATION_RULES[
                symbolic_layer
            ]
        )

        if (
            candidate.get(
                "symbolic_preservation_rule"
            )
            != expected_rule
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost its symbolic preservation rule."
            )

        if (
            candidate.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost hard symbolic authority."
            )

        if (
            candidate.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic authority."
            )

        processing_state = candidate.get(
            "candidate_processing_state"
        )

        if not isinstance(
            processing_state,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing candidate_processing_state."
            )

        required_true_fields = (
            "constructed",
            "symbolic_constraint_enforced",
            "neural_context_interpreted",
            "evidence_fused",
            "hybrid_confidence_calculated",
        )

        for field_name in required_true_fields:

            if (
                processing_state.get(
                    field_name
                )
                is not True
            ):
                raise SymbolicNeuralHybridIntelligenceError(
                    f"{candidate_id} reached P before completing {field_name}."
                )

        expected_conflict_resolved = (
            assessment_state == "CONFLICT"
        )

        if (
            processing_state.get(
                "conflict_resolved"
            )
            is not expected_conflict_resolved
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid conflict-resolution state."
            )

        expected_agreement = (
            assessment_state == "AGREEMENT"
        )

        expected_conflict = (
            assessment_state == "CONFLICT"
        )

        expected_unresolved = (
            assessment_state == "UNRESOLVED"
        )

        if (
            processing_state.get(
                "agreement_preserved"
            )
            is not expected_agreement
            or processing_state.get(
                "conflict_preserved"
            )
            is not expected_conflict
            or processing_state.get(
                "unresolved_preserved"
            )
            is not expected_unresolved
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has corrupted assessment-state preservation."
            )

        symbolic_evidence_id = candidate.get(
            "symbolic_evidence_id"
        )

        semantic_evidence_id = candidate.get(
            "neural_semantic_evidence_id"
        )

        alignment_id = candidate.get(
            "alignment_id"
        )

        assessment_id = candidate.get(
            "assessment_id"
        )

        if not symbolic_evidence_id:
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing symbolic_evidence_id."
            )

        if not semantic_evidence_id:
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing neural_semantic_evidence_id."
            )

        if not alignment_id:
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing alignment_id."
            )

        if not assessment_id:
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing assessment_id."
            )

        symbolic_evidence = candidate.get(
            "symbolic_evidence"
        )

        semantic_evidence = candidate.get(
            "neural_semantic_evidence"
        )

        if not isinstance(
            symbolic_evidence,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing symbolic evidence."
            )

        if not isinstance(
            semantic_evidence,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing neural/semantic evidence."
            )

        if (
            symbolic_evidence.get("evidence_id")
            != symbolic_evidence_id
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} symbolic evidence identity changed."
            )

        if (
            semantic_evidence.get("evidence_id")
            != semantic_evidence_id
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} semantic evidence identity changed."
            )

        if (
            symbolic_evidence.get("source_layer")
            != symbolic_layer
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} symbolic source identity changed."
            )

        if (
            semantic_evidence.get("source_layer")
            != semantic_layer
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} semantic source identity changed."
            )

        enforcement = candidate.get(
            "symbolic_constraint_enforcement"
        )

        interpretation = candidate.get(
            "neural_context_interpretation"
        )

        fusion = candidate.get(
            "hybrid_evidence_fusion"
        )

        resolution = candidate.get(
            "contradiction_conflict_resolution"
        )

        confidence = candidate.get(
            "hybrid_confidence_assessment"
        )

        stage_payloads = (
            (
                "symbolic constraint enforcement",
                enforcement,
            ),
            (
                "neural context interpretation",
                interpretation,
            ),
            (
                "hybrid evidence fusion",
                fusion,
            ),
            (
                "contradiction/conflict resolution",
                resolution,
            ),
            (
                "hybrid confidence assessment",
                confidence,
            ),
        )

        for stage_name, stage_payload in stage_payloads:

            if not isinstance(
                stage_payload,
                Mapping,
            ):
                raise SymbolicNeuralHybridIntelligenceError(
                    f"{candidate_id} is missing {stage_name}."
                )

        expected_disposition = (
            _HYBRID_CANDIDATE_DISPOSITIONS[
                assessment_state
            ]
        )

        if (
            candidate.get(
                "candidate_disposition"
            )
            != expected_disposition
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an inconsistent candidate disposition."
            )

        if (
            symbolic_evidence.get(
                "evidence_side"
            )
            != "SYMBOLIC"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid symbolic evidence-side provenance."
            )

        if (
            semantic_evidence.get(
                "evidence_side"
            )
            != "NEURAL_SEMANTIC"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic evidence-side provenance."
            )

        if (
            enforcement.get(
                "constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
            or enforcement.get(
                "semantic_override_allowed"
            )
            is not False
            or enforcement.get(
                "symbolic_evidence_mutated"
            )
            is not False
            or enforcement.get(
                "symbolic_evidence_discarded"
            )
            is not False
            or enforcement.get(
                "symbolic_constraint_relaxed"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains corrupted K provenance."
            )

        if (
            interpretation.get(
                "source_layer"
            )
            != semantic_layer
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent L source provenance."
            )

        if (
            interpretation.get(
                "context_access_policy"
            )
            != "CERTIFIED_ARTICLE_LOCAL_EVIDENCE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid L context provenance."
            )

        expected_context_outcome = (
            _HYBRID_NEURAL_CONTEXT_OUTCOMES[
                assessment_state
            ]
        )

        if (
            interpretation.get(
                "context_outcome"
            )
            != expected_context_outcome
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid L context outcome provenance."
            )

        certified_context_signals = (
            interpretation.get(
                "certified_context_signals"
            )
        )

        if not isinstance(
            certified_context_signals,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid L certified context signals."
            )

        expected_semantic_signal_count = sum(
            len(values)
            for values
            in certified_context_signals.values()
        )

        if (
            interpretation.get(
                "semantic_signal_count"
            )
            != expected_semantic_signal_count
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent L semantic signal accounting."
            )

        expected_interpretation_status = (
            "CERTIFIED_SEMANTIC_CONTEXT_INTERPRETED"
            if expected_semantic_signal_count
            else "NO_EXPLICIT_SEMANTIC_CONTEXT_SIGNAL_AVAILABLE"
        )

        if (
            interpretation.get(
                "interpretation_status"
            )
            != expected_interpretation_status
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid L interpretation-status provenance."
            )

        if (
            interpretation.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
            or interpretation.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
            or interpretation.get(
                "semantic_override_allowed"
            )
            is not False
            or interpretation.get(
                "semantic_override_attempted"
            )
            is not False
            or interpretation.get(
                "symbolic_evidence_mutated"
            )
            is not False
            or interpretation.get(
                "symbolic_constraint_relaxed"
            )
            is not False
            or interpretation.get(
                "new_semantic_fact_inferred"
            )
            is not False
            or interpretation.get(
                "new_article_fact_inferred"
            )
            is not False
            or interpretation.get(
                "semantic_equivalence_inferred"
            )
            is not False
            or interpretation.get(
                "conflict_resolved"
            )
            is not False
            or interpretation.get(
                "evidence_fused"
            )
            is not False
            or interpretation.get(
                "external_model_called"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains corrupted L provenance."
            )

        expected_fusion_mode = (
            _HYBRID_FUSION_MODES[
                assessment_state
            ]
        )

        expected_fusion_outcome = (
            _HYBRID_FUSION_OUTCOMES[
                assessment_state
            ]
        )

        if (
            fusion.get(
                "fusion_status"
            )
            != "FUSED"
            or fusion.get(
                "fusion_mode"
            )
            != expected_fusion_mode
            or fusion.get(
                "fusion_outcome"
            )
            != expected_fusion_outcome
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid M fusion provenance."
            )

        if (
            fusion.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
            or fusion.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
            or fusion.get(
                "semantic_override_allowed"
            )
            is not False
            or fusion.get(
                "symbolic_evidence_mutated"
            )
            is not False
            or fusion.get(
                "neural_semantic_evidence_mutated"
            )
            is not False
            or fusion.get(
                "symbolic_constraint_relaxed"
            )
            is not False
            or fusion.get(
                "score_averaging_performed"
            )
            is not False
            or fusion.get(
                "raw_evidence_concatenation_performed"
            )
            is not False
            or fusion.get(
                "new_hybrid_fact_inferred"
            )
            is not False
            or fusion.get(
                "new_article_fact_inferred"
            )
            is not False
            or fusion.get(
                "conflict_resolved"
            )
            is not False
            or fusion.get(
                "hybrid_confidence_calculated"
            )
            is not False
            or fusion.get(
                "external_model_called"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains corrupted M provenance."
            )

        expected_resolution_policy = (
            _HYBRID_CONFLICT_RESOLUTION_POLICIES[
                assessment_state
            ]
        )

        for resolution_field in (
            "resolution_status",
            "governance_decision",
            "selected_authority",
            "final_resolution_state",
        ):
            if (
                resolution.get(
                    resolution_field
                )
                != expected_resolution_policy[
                    resolution_field
                ]
            ):
                raise SymbolicNeuralHybridIntelligenceError(
                    f"{candidate_id} has invalid N {resolution_field} provenance."
                )

        if (
            resolution.get(
                "conflict_present"
            )
            is not expected_conflict
            or resolution.get(
                "resolution_required"
            )
            is not expected_conflict
            or resolution.get(
                "conflict_operationally_resolved"
            )
            is not expected_conflict
            or resolution.get(
                "abstention_required"
            )
            is not expected_unresolved
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent N governance provenance."
            )

        if (
            resolution.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
            or resolution.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
            or resolution.get(
                "symbolic_component_preserved"
            )
            is not True
            or resolution.get(
                "neural_semantic_component_preserved"
            )
            is not True
            or resolution.get(
                "neural_context_component_preserved"
            )
            is not True
            or resolution.get(
                "semantic_evidence_discarded"
            )
            is not False
            or resolution.get(
                "semantic_evidence_declared_false"
            )
            is not False
            or resolution.get(
                "symbolic_evidence_mutated"
            )
            is not False
            or resolution.get(
                "symbolic_constraint_relaxed"
            )
            is not False
            or resolution.get(
                "semantic_override_allowed"
            )
            is not False
            or resolution.get(
                "truth_assessment_performed"
            )
            is not False
            or resolution.get(
                "external_validation_performed"
            )
            is not False
            or resolution.get(
                "new_hybrid_fact_inferred"
            )
            is not False
            or resolution.get(
                "new_article_fact_inferred"
            )
            is not False
            or resolution.get(
                "hybrid_confidence_calculated"
            )
            is not False
            or resolution.get(
                "external_model_called"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains corrupted N provenance."
            )

        if (
            confidence.get(
                "final_resolution_state"
            )
            != resolution.get(
                "final_resolution_state"
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} O confidence is attached to the wrong N resolution state."
            )

        if (
            confidence.get(
                "confidence_scope"
            )
            != "STRUCTURAL_REASONING_CONFIDENCE_NOT_TRUTH_PROBABILITY"
            or confidence.get(
                "source_uncertainty_preserved"
            )
            is not True
            or confidence.get(
                "hard_symbolic_authority_preserved"
            )
            is not True
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains corrupted O confidence provenance."
            )

        if (
            enforcement.get(
                "enforcement_status"
            )
            != "ENFORCED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid K provenance."
            )

        if (
            enforcement.get(
                "preservation_rule"
            )
            != expected_rule
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent K preservation provenance."
            )

        if (
            interpretation.get(
                "assessment_state"
            )
            != assessment_state
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid L provenance."
            )

        if (
            fusion.get(
                "assessment_state"
            )
            != assessment_state
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid M provenance."
            )

        if (
            resolution.get(
                "input_assessment_state"
            )
            != assessment_state
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid N provenance."
            )

        if (
            confidence.get(
                "input_assessment_state"
            )
            != assessment_state
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid O provenance."
            )

        expected_confidence_policy = (
            _HYBRID_CONFIDENCE_POLICIES[
                assessment_state
            ]
        )

        if (
            confidence.get(
                "assessment_status"
            )
            != "ASSESSED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} does not contain canonical O confidence."
            )

        if (
            confidence.get(
                "confidence_class"
            )
            != expected_confidence_policy[
                "confidence_class"
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid O confidence class."
            )

        if (
            confidence.get(
                "confidence_basis"
            )
            != expected_confidence_policy[
                "confidence_basis"
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid O confidence basis."
            )

        if (
            confidence.get(
                "downstream_reliance_mode"
            )
            != expected_confidence_policy[
                "downstream_reliance_mode"
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid O downstream reliance mode."
            )

        if (
            confidence.get(
                "abstention_required"
            )
            is not expected_confidence_policy[
                "abstention_required"
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid O abstention state."
            )

        if (
            confidence.get(
                "numeric_probability_generated"
            )
            is not False
            or confidence.get(
                "numeric_confidence_score_generated"
            )
            is not False
            or confidence.get(
                "truth_probability_estimated"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains invalid probabilistic confidence state."
            )

        if (
            confidence.get(
                "source_commitment_strengthened"
            )
            is not False
            or confidence.get(
                "semantic_override_allowed"
            )
            is not False
            or confidence.get(
                "truth_assessment_performed"
            )
            is not False
            or confidence.get(
                "external_validation_performed"
            )
            is not False
            or confidence.get(
                "external_model_called"
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains invalid O authority state."
            )

        provenance_path = [
            {
                "stage":
                    "HYBRID_REASONING_CANDIDATE_CONSTRUCTION",

                "hybrid_candidate_id":
                    candidate_id,

                "assessment_id":
                    assessment_id,

                "alignment_id":
                    alignment_id,
            },

            {
                "stage":
                    "SYMBOLIC_CONSTRAINT_ENFORCEMENT",

                "symbolic_evidence_id":
                    symbolic_evidence_id,

                "symbolic_source_layer":
                    symbolic_layer,

                "preservation_rule":
                    expected_rule,
            },

            {
                "stage":
                    "NEURAL_CONTEXT_INTERPRETATION",

                "neural_semantic_evidence_id":
                    semantic_evidence_id,

                "neural_semantic_source_layer":
                    semantic_layer,

                "interpretation_status":
                    interpretation.get(
                        "interpretation_status"
                    ),
            },

            {
                "stage":
                    "HYBRID_EVIDENCE_FUSION",

                "fusion_mode":
                    fusion.get(
                        "fusion_mode"
                    ),

                "fusion_outcome":
                    fusion.get(
                        "fusion_outcome"
                    ),
            },

            {
                "stage":
                    "CONTRADICTION_CONFLICT_RESOLUTION",

                "resolution_status":
                    resolution.get(
                        "resolution_status"
                    ),

                "governance_decision":
                    resolution.get(
                        "governance_decision"
                    ),

                "final_resolution_state":
                    resolution.get(
                        "final_resolution_state"
                    ),
            },

            {
                "stage":
                    "HYBRID_CONFIDENCE_ASSESSMENT",

                "confidence_class":
                    confidence.get(
                        "confidence_class"
                    ),

                "confidence_basis":
                    confidence.get(
                        "confidence_basis"
                    ),

                "downstream_reliance_mode":
                    confidence.get(
                        "downstream_reliance_mode"
                    ),
            },
        ]

        prepared_candidate = deepcopy(
            dict(candidate)
        )

        prepared_processing_state = deepcopy(
            dict(processing_state)
        )

        prepared_processing_state[
            "provenance_explainability_prepared"
        ] = True

        prepared_candidate[
            "candidate_processing_state"
        ] = prepared_processing_state

        prepared_candidate[
            "reasoning_provenance_explainability"
        ] = {
            "preparation_status":
                "PREPARED",

            "explainability_outcome":
                _HYBRID_EXPLAINABILITY_OUTCOMES[
                    assessment_state
                ],

            "hybrid_candidate_id":
                candidate_id,

            "article_identity":
                deepcopy(
                    article_identity
                ),

            "symbolic_evidence_id":
                symbolic_evidence_id,

            "neural_semantic_evidence_id":
                semantic_evidence_id,

            "alignment_id":
                alignment_id,

            "assessment_id":
                assessment_id,

            "symbolic_source_layer":
                symbolic_layer,

            "neural_semantic_source_layer":
                semantic_layer,

            "assessment_state":
                assessment_state,

            "symbolic_preservation_rule":
                expected_rule,

            "symbolic_constraint_authority":
                "HARD_WHEN_EXPLICIT_AND_CERTIFIED",

            "neural_semantic_authority":
                "INTERPRETIVE_ONLY",

            "final_resolution_state":
                resolution.get(
                    "final_resolution_state"
                ),

            "governance_decision":
                resolution.get(
                    "governance_decision"
                ),

            "confidence_class":
                confidence.get(
                    "confidence_class"
                ),

            "confidence_basis":
                confidence.get(
                    "confidence_basis"
                ),

            "downstream_reliance_mode":
                confidence.get(
                    "downstream_reliance_mode"
                ),

            "abstention_required":
                confidence.get(
                    "abstention_required"
                ),

            "shared_grounding_anchors":
                deepcopy(
                    candidate.get(
                        "shared_grounding_anchors",
                        [],
                    )
                ),

            "shared_comparable_fields":
                deepcopy(
                    candidate.get(
                        "shared_comparable_fields",
                        [],
                    )
                ),

            "provenance_path":
                provenance_path,

            "evidence_rewritten":
                False,

            "new_reasoning_performed":
                False,

            "new_article_fact_inferred":
                False,

            "new_hybrid_fact_inferred":
                False,

            "confidence_recalculated":
                False,

            "numeric_probability_generated":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "duplicate_resolution_performed":
                False,

            "article_level_consolidation_performed":
                False,

            "generated_explanation_claims":
                False,

            "external_model_called":
                False,
        }

        prepared_candidates.append(
            prepared_candidate
        )

        provenance_records.append({
            "hybrid_provenance_id":
                f"HYBRID_PROVENANCE:{len(provenance_records) + 1}",

            "hybrid_candidate_id":
                candidate_id,

            "symbolic_evidence_id":
                symbolic_evidence_id,

            "neural_semantic_evidence_id":
                semantic_evidence_id,

            "alignment_id":
                alignment_id,

            "assessment_id":
                assessment_id,

            "assessment_state":
                assessment_state,

            "final_resolution_state":
                resolution.get(
                    "final_resolution_state"
                ),

            "confidence_class":
                confidence.get(
                    "confidence_class"
                ),

            "downstream_reliance_mode":
                confidence.get(
                    "downstream_reliance_mode"
                ),

            "explainability_outcome":
                _HYBRID_EXPLAINABILITY_OUTCOMES[
                    assessment_state
                ],

            "provenance_complete":
                True,

            "symbolic_boundary_respected":
                True,

            "new_reasoning_performed":
                False,

            "prepared":
                True,
        })

    agreement_trace_count = sum(
        record["assessment_state"]
        == "AGREEMENT"
        for record in provenance_records
    )

    conflict_trace_count = sum(
        record["assessment_state"]
        == "CONFLICT"
        for record in provenance_records
    )

    unresolved_trace_count = sum(
        record["assessment_state"]
        == "UNRESOLVED"
        for record in provenance_records
    )

    return {
        "schema_version":
            "symbolic_neural_hybrid_reasoning_provenance_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15P",

        "status":
            "HYBRID_REASONING_PROVENANCE_PREPARED",

        "article_identity":
            deepcopy(
                article_identity
            ),

        "symbolic_evidence_records":
            deepcopy(
                confidence_result.get(
                    "symbolic_evidence_records",
                    [],
                )
            ),

        "neural_semantic_evidence_records":
            deepcopy(
                confidence_result.get(
                    "neural_semantic_evidence_records",
                    [],
                )
            ),

        "alignment_pairs":
            deepcopy(
                confidence_result.get(
                    "alignment_pairs",
                    [],
                )
            ),

        "agreement_conflict_assessments":
            deepcopy(
                confidence_result.get(
                    "agreement_conflict_assessments",
                    [],
                )
            ),

        "hybrid_reasoning_candidates":
            prepared_candidates,

        "symbolic_constraint_enforcement_records":
            deepcopy(
                confidence_result.get(
                    "symbolic_constraint_enforcement_records",
                    [],
                )
            ),

        "neural_context_interpretation_records":
            deepcopy(
                confidence_result.get(
                    "neural_context_interpretation_records",
                    [],
                )
            ),

        "hybrid_evidence_fusion_records":
            deepcopy(
                confidence_result.get(
                    "hybrid_evidence_fusion_records",
                    [],
                )
            ),

        "contradiction_conflict_resolution_records":
            deepcopy(
                confidence_result.get(
                    "contradiction_conflict_resolution_records",
                    [],
                )
            ),

        "hybrid_confidence_records":
            deepcopy(
                confidence_result.get(
                    "hybrid_confidence_records",
                    [],
                )
            ),

        "reasoning_provenance_explainability_records":
            provenance_records,

        "unaligned_symbolic_evidence_ids":
            deepcopy(
                confidence_result.get(
                    "unaligned_symbolic_evidence_ids",
                    [],
                )
            ),

        "unaligned_neural_semantic_evidence_ids":
            deepcopy(
                confidence_result.get(
                    "unaligned_neural_semantic_evidence_ids",
                    [],
                )
            ),

        "article_context_boundary":
            deepcopy(
                article_context_boundary
            ),

        "provenance_explainability_summary": {
            "candidate_count":
                len(
                    candidates
                ),

            "provenance_record_count":
                len(
                    provenance_records
                ),

            "all_candidates_traceable":
                len(
                    provenance_records
                )
                == len(
                    candidates
                ),

            "agreement_trace_count":
                agreement_trace_count,

            "conflict_trace_count":
                conflict_trace_count,

            "unresolved_trace_count":
                unresolved_trace_count,

            "structured_explainability_only":
                True,

            "new_reasoning_performed":
                False,

            "evidence_rewritten":
                False,

            "confidence_recalculated":
                False,

            "duplicate_resolution_performed":
                False,

            "article_level_consolidation_performed":
                False,

            "generated_explanation_claims":
                False,
        },

        "processing_boundaries": {
            "reasoning_provenance_explainability_prepared":
                True,

            "structured_provenance_only":
                True,

            "complete_candidate_trace_prepared":
                True,

            "hard_symbolic_authority_preserved":
                True,

            "semantic_override_allowed":
                False,

            "evidence_rewrite_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_hybrid_fact_inference_performed":
                False,

            "new_article_fact_inference_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "numeric_probability_generated":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "duplicate_resolution_performed":
                False,

            "article_level_consolidation_performed":
                False,

            "generated_explanation_claims":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "duplicate_redundant_hybrid_resolution",
    }



# ============================================================================
# PATCH 4.6.15Q — Duplicate / Redundant Hybrid Resolution
# ============================================================================

def _hybrid_freeze_redundancy_value(
    value: Any,
) -> Any:
    """
    Convert article-local hybrid evidence into a deterministic,
    hashable structural representation.

    This helper performs no semantic interpretation and no fuzzy
    similarity comparison.
    """

    if isinstance(
        value,
        Mapping,
    ):
        return tuple(
            sorted(
                (
                    str(key),
                    _hybrid_freeze_redundancy_value(
                        item
                    ),
                )
                for key, item in value.items()
            )
        )

    if isinstance(
        value,
        (list, tuple),
    ):
        return tuple(
            _hybrid_freeze_redundancy_value(
                item
            )
            for item in value
        )

    if isinstance(
        value,
        set,
    ):
        frozen_items = [
            _hybrid_freeze_redundancy_value(
                item
            )
            for item in value
        ]

        return tuple(
            sorted(
                frozen_items,
                key=repr,
            )
        )

    try:
        hash(
            value
        )
        return value

    except TypeError:
        return repr(
            value
        )


def _hybrid_build_redundancy_signature(
    candidate: Mapping[str, Any],
) -> tuple[Any, ...]:
    """
    Build the exact structural identity used by Q.

    Candidate IDs, alignment IDs, assessment IDs, and provenance record
    IDs are intentionally excluded because they are bookkeeping IDs.

    The certified evidence and governed reasoning outcome are included.
    Therefore two candidates collapse only when their substantive
    certified hybrid structures are equivalent.
    """

    interpretation = candidate[
        "neural_context_interpretation"
    ]

    fusion = candidate[
        "hybrid_evidence_fusion"
    ]

    resolution = candidate[
        "contradiction_conflict_resolution"
    ]

    confidence = candidate[
        "hybrid_confidence_assessment"
    ]

    provenance = candidate[
        "reasoning_provenance_explainability"
    ]

    return (
        candidate.get(
            "symbolic_source_layer"
        ),

        candidate.get(
            "neural_semantic_source_layer"
        ),

        candidate.get(
            "assessment_state"
        ),

        candidate.get(
            "symbolic_preservation_rule"
        ),

        _hybrid_freeze_redundancy_value(
            candidate[
                "symbolic_evidence"
            ].get(
                "evidence"
            )
        ),

        _hybrid_freeze_redundancy_value(
            candidate[
                "neural_semantic_evidence"
            ].get(
                "evidence"
            )
        ),

        _hybrid_freeze_redundancy_value(
            candidate.get(
                "shared_grounding_anchors",
                [],
            )
        ),

        _hybrid_freeze_redundancy_value(
            candidate.get(
                "shared_comparable_fields",
                [],
            )
        ),

        interpretation.get(
            "interpretation_status"
        ),

        interpretation.get(
            "context_outcome"
        ),

        _hybrid_freeze_redundancy_value(
            interpretation.get(
                "certified_context_signals",
                {},
            )
        ),

        fusion.get(
            "fusion_mode"
        ),

        fusion.get(
            "fusion_outcome"
        ),

        resolution.get(
            "final_resolution_state"
        ),

        resolution.get(
            "governance_decision"
        ),

        confidence.get(
            "confidence_class"
        ),

        confidence.get(
            "confidence_basis"
        ),

        confidence.get(
            "downstream_reliance_mode"
        ),

        confidence.get(
            "abstention_required"
        ),

        provenance.get(
            "explainability_outcome"
        ),
    )


def resolve_duplicate_redundant_hybrid_candidates(
    provenance_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve exact structural duplicate/redundant hybrid candidates.

    Q is deliberately conservative:

    - no fuzzy semantic deduplication
    - no embedding similarity
    - no claim paraphrase inference
    - no evidence rewriting
    - no confidence recalculation
    - no conflict re-resolution
    - no article-level consolidation

    The first structurally equivalent candidate is retained as the
    canonical candidate. Later equivalent candidates are recorded as
    redundant and remain available through pre-resolution lineage.
    """

    if not isinstance(
        provenance_result,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Duplicate/redundant resolution requires the canonical P result."
        )

    if (
        provenance_result.get("status")
        != "HYBRID_REASONING_PROVENANCE_PREPARED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Reasoning provenance has not been canonically prepared."
        )

    if (
        provenance_result.get("next_stage")
        != "duplicate_redundant_hybrid_resolution"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "P does not hand off to duplicate/redundant hybrid resolution."
        )

    if (
        provenance_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q requires article-local transient intelligence."
        )

    article_identity = provenance_result.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Duplicate/redundant resolution is missing article_identity."
        )

    article_context_boundary = provenance_result.get(
        "article_context_boundary"
    )

    if not isinstance(
        article_context_boundary,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Duplicate/redundant resolution is missing the article-context boundary."
        )

    if (
        article_context_boundary.get(
            "context_access_policy"
        )
        != "CERTIFIED_ARTICLE_LOCAL_EVIDENCE_ONLY"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Duplicate/redundant resolution received an invalid context policy."
        )

    candidates = provenance_result.get(
        "hybrid_reasoning_candidates"
    )

    if not isinstance(
        candidates,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "P hybrid reasoning candidates are missing."
        )

    validated_candidates: list[
        Mapping[str, Any]
    ] = []

    candidate_ids: set[str] = set()

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid P hybrid reasoning candidate."
            )

        candidate_id = candidate.get(
            "hybrid_candidate_id"
        )

        if not candidate_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Hybrid reasoning candidate is missing hybrid_candidate_id."
            )

        if candidate_id in candidate_ids:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate hybrid_candidate_id before Q: {candidate_id}."
            )

        candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "article_identity"
            )
            != article_identity
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} belongs to a different article."
            )

        assessment_state = candidate.get(
            "assessment_state"
        )

        if (
            assessment_state
            not in _HYBRID_EXPLAINABILITY_OUTCOMES
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid assessment state."
            )

        symbolic_layer = candidate.get(
            "symbolic_source_layer"
        )

        semantic_layer = candidate.get(
            "neural_semantic_source_layer"
        )

        if (
            symbolic_layer
            not in _SYMBOLIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid symbolic source layer."
            )

        if (
            semantic_layer
            not in _NEURAL_SEMANTIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid neural/semantic source layer."
            )

        expected_rule = (
            _SYMBOLIC_PRESERVATION_RULES[
                symbolic_layer
            ]
        )

        if (
            candidate.get(
                "symbolic_preservation_rule"
            )
            != expected_rule
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost its symbolic preservation rule."
            )

        if (
            candidate.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost hard symbolic authority."
            )

        if (
            candidate.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic authority."
            )

        expected_disposition = (
            _HYBRID_CANDIDATE_DISPOSITIONS[
                assessment_state
            ]
        )

        if (
            candidate.get(
                "candidate_disposition"
            )
            != expected_disposition
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an inconsistent candidate disposition."
            )

        processing_state = candidate.get(
            "candidate_processing_state"
        )

        if not isinstance(
            processing_state,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing candidate_processing_state."
            )

        for completed_field in (
            "constructed",
            "symbolic_constraint_enforced",
            "neural_context_interpreted",
            "evidence_fused",
            "hybrid_confidence_calculated",
            "provenance_explainability_prepared",
        ):
            if (
                processing_state.get(
                    completed_field
                )
                is not True
            ):
                raise SymbolicNeuralHybridIntelligenceError(
                    f"{candidate_id} reached Q before completing {completed_field}."
                )

        if (
            processing_state.get(
                "duplicate_redundant_resolution_performed",
                False,
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} entered Q after duplicate resolution was already performed."
            )

        expected_agreement = (
            assessment_state == "AGREEMENT"
        )

        expected_conflict = (
            assessment_state == "CONFLICT"
        )

        expected_unresolved = (
            assessment_state == "UNRESOLVED"
        )

        if (
            processing_state.get(
                "agreement_preserved"
            )
            is not expected_agreement
            or processing_state.get(
                "conflict_preserved"
            )
            is not expected_conflict
            or processing_state.get(
                "unresolved_preserved"
            )
            is not expected_unresolved
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has corrupted assessment-state preservation."
            )

        if (
            processing_state.get(
                "conflict_resolved"
            )
            is not expected_conflict
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid conflict-resolution state."
            )

        symbolic_evidence = candidate.get(
            "symbolic_evidence"
        )

        semantic_evidence = candidate.get(
            "neural_semantic_evidence"
        )

        if not isinstance(
            symbolic_evidence,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing symbolic evidence."
            )

        if not isinstance(
            semantic_evidence,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing neural/semantic evidence."
            )

        if (
            symbolic_evidence.get(
                "evidence_side"
            )
            != "SYMBOLIC"
            or symbolic_evidence.get(
                "source_layer"
            )
            != symbolic_layer
            or symbolic_evidence.get(
                "evidence_id"
            )
            != candidate.get(
                "symbolic_evidence_id"
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has corrupted symbolic evidence identity."
            )

        if (
            semantic_evidence.get(
                "evidence_side"
            )
            != "NEURAL_SEMANTIC"
            or semantic_evidence.get(
                "source_layer"
            )
            != semantic_layer
            or semantic_evidence.get(
                "evidence_id"
            )
            != candidate.get(
                "neural_semantic_evidence_id"
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has corrupted neural/semantic evidence identity."
            )

        interpretation = candidate.get(
            "neural_context_interpretation"
        )

        fusion = candidate.get(
            "hybrid_evidence_fusion"
        )

        resolution = candidate.get(
            "contradiction_conflict_resolution"
        )

        confidence = candidate.get(
            "hybrid_confidence_assessment"
        )

        if not isinstance(
            interpretation,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing L neural-context interpretation."
            )

        if not isinstance(
            fusion,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing M hybrid evidence fusion."
            )

        if not isinstance(
            resolution,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing N contradiction/conflict resolution."
            )

        if not isinstance(
            confidence,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing O hybrid confidence assessment."
            )

        if (
            interpretation.get(
                "assessment_state"
            )
            != assessment_state
            or interpretation.get(
                "source_layer"
            )
            != semantic_layer
            or interpretation.get(
                "context_outcome"
            )
            != _HYBRID_NEURAL_CONTEXT_OUTCOMES[
                assessment_state
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains inconsistent L structure."
            )

        certified_context_signals = interpretation.get(
            "certified_context_signals"
        )

        if not isinstance(
            certified_context_signals,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid certified L context signals."
            )

        if (
            fusion.get(
                "fusion_status"
            )
            != "FUSED"
            or fusion.get(
                "assessment_state"
            )
            != assessment_state
            or fusion.get(
                "fusion_mode"
            )
            != _HYBRID_FUSION_MODES[
                assessment_state
            ]
            or fusion.get(
                "fusion_outcome"
            )
            != _HYBRID_FUSION_OUTCOMES[
                assessment_state
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains inconsistent M fusion structure."
            )

        expected_resolution_policy = (
            _HYBRID_CONFLICT_RESOLUTION_POLICIES[
                assessment_state
            ]
        )

        if (
            resolution.get(
                "input_assessment_state"
            )
            != assessment_state
            or resolution.get(
                "final_resolution_state"
            )
            != expected_resolution_policy[
                "final_resolution_state"
            ]
            or resolution.get(
                "governance_decision"
            )
            != expected_resolution_policy[
                "governance_decision"
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains inconsistent N resolution structure."
            )

        expected_confidence_policy = (
            _HYBRID_CONFIDENCE_POLICIES[
                assessment_state
            ]
        )

        if (
            confidence.get(
                "assessment_status"
            )
            != "ASSESSED"
            or confidence.get(
                "input_assessment_state"
            )
            != assessment_state
            or confidence.get(
                "final_resolution_state"
            )
            != expected_resolution_policy[
                "final_resolution_state"
            ]
            or confidence.get(
                "confidence_class"
            )
            != expected_confidence_policy[
                "confidence_class"
            ]
            or confidence.get(
                "confidence_basis"
            )
            != expected_confidence_policy[
                "confidence_basis"
            ]
            or confidence.get(
                "downstream_reliance_mode"
            )
            != expected_confidence_policy[
                "downstream_reliance_mode"
            ]
            or confidence.get(
                "abstention_required"
            )
            is not expected_confidence_policy[
                "abstention_required"
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains inconsistent O confidence structure."
            )

        provenance = candidate.get(
            "reasoning_provenance_explainability"
        )

        if not isinstance(
            provenance,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing P provenance/explainability."
            )

        if (
            provenance.get(
                "preparation_status"
            )
            != "PREPARED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} does not contain canonical P provenance."
            )

        if (
            provenance.get(
                "hybrid_candidate_id"
            )
            != candidate_id
            or provenance.get(
                "article_identity"
            )
            != article_identity
            or provenance.get(
                "symbolic_evidence_id"
            )
            != candidate.get(
                "symbolic_evidence_id"
            )
            or provenance.get(
                "neural_semantic_evidence_id"
            )
            != candidate.get(
                "neural_semantic_evidence_id"
            )
            or provenance.get(
                "alignment_id"
            )
            != candidate.get(
                "alignment_id"
            )
            or provenance.get(
                "assessment_id"
            )
            != candidate.get(
                "assessment_id"
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains inconsistent P provenance identifiers."
            )

        if (
            provenance.get(
                "assessment_state"
            )
            != assessment_state
            or provenance.get(
                "symbolic_source_layer"
            )
            != symbolic_layer
            or provenance.get(
                "neural_semantic_source_layer"
            )
            != semantic_layer
            or provenance.get(
                "symbolic_preservation_rule"
            )
            != expected_rule
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains inconsistent P reasoning provenance."
            )

        if (
            provenance.get(
                "explainability_outcome"
            )
            != _HYBRID_EXPLAINABILITY_OUTCOMES[
                assessment_state
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid P explainability outcome."
            )

        confidence_policy = (
            _HYBRID_CONFIDENCE_POLICIES[
                assessment_state
            ]
        )

        if (
            provenance.get(
                "confidence_class"
            )
            != confidence_policy[
                "confidence_class"
            ]
            or provenance.get(
                "confidence_basis"
            )
            != confidence_policy[
                "confidence_basis"
            ]
            or provenance.get(
                "downstream_reliance_mode"
            )
            != confidence_policy[
                "downstream_reliance_mode"
            ]
            or provenance.get(
                "abstention_required"
            )
            is not confidence_policy[
                "abstention_required"
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent P confidence provenance."
            )

        expected_resolution = (
            _HYBRID_CONFLICT_RESOLUTION_POLICIES[
                assessment_state
            ]
        )

        if (
            provenance.get(
                "final_resolution_state"
            )
            != expected_resolution[
                "final_resolution_state"
            ]
            or provenance.get(
                "governance_decision"
            )
            != expected_resolution[
                "governance_decision"
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent P governance provenance."
            )

        provenance_path = provenance.get(
            "provenance_path"
        )

        if not isinstance(
            provenance_path,
            list,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid provenance_path."
            )

        expected_stage_order = [
            "HYBRID_REASONING_CANDIDATE_CONSTRUCTION",
            "SYMBOLIC_CONSTRAINT_ENFORCEMENT",
            "NEURAL_CONTEXT_INTERPRETATION",
            "HYBRID_EVIDENCE_FUSION",
            "CONTRADICTION_CONFLICT_RESOLUTION",
            "HYBRID_CONFIDENCE_ASSESSMENT",
        ]

        actual_stage_order = []

        for stage_record in provenance_path:

            if not isinstance(
                stage_record,
                Mapping,
            ):
                raise SymbolicNeuralHybridIntelligenceError(
                    f"{candidate_id} contains invalid provenance stage record."
                )

            actual_stage_order.append(
                stage_record.get(
                    "stage"
                )
            )

        if (
            actual_stage_order
            != expected_stage_order
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid provenance stage order."
            )

        for forbidden_true_field in (
            "evidence_rewritten",
            "new_reasoning_performed",
            "new_article_fact_inferred",
            "new_hybrid_fact_inferred",
            "confidence_recalculated",
            "numeric_probability_generated",
            "truth_assessment_performed",
            "external_validation_performed",
            "duplicate_resolution_performed",
            "article_level_consolidation_performed",
            "generated_explanation_claims",
            "external_model_called",
        ):
            if (
                provenance.get(
                    forbidden_true_field
                )
                is not False
            ):
                raise SymbolicNeuralHybridIntelligenceError(
                    f"{candidate_id} contains invalid P boundary state: {forbidden_true_field}."
                )

        validated_candidates.append(
            candidate
        )

    signature_groups: dict[
        tuple[Any, ...],
        list[int],
    ] = {}

    signature_order: list[
        tuple[Any, ...]
    ] = []

    for index, candidate in enumerate(
        validated_candidates
    ):
        signature = (
            _hybrid_build_redundancy_signature(
                candidate
            )
        )

        if signature not in signature_groups:
            signature_groups[
                signature
            ] = []

            signature_order.append(
                signature
            )

        signature_groups[
            signature
        ].append(
            index
        )

    canonical_candidates: list[
        dict[str, Any]
    ] = []

    resolution_records: list[
        dict[str, Any]
    ] = []

    redundant_candidate_ids: list[
        str
    ] = []

    canonical_candidate_ids: list[
        str
    ] = []

    for group_number, signature in enumerate(
        signature_order,
        1,
    ):
        indexes = signature_groups[
            signature
        ]

        canonical_index = indexes[
            0
        ]

        canonical_source = validated_candidates[
            canonical_index
        ]

        canonical_id = canonical_source[
            "hybrid_candidate_id"
        ]

        canonical_candidate_ids.append(
            canonical_id
        )

        group_candidate_ids = [
            validated_candidates[index][
                "hybrid_candidate_id"
            ]
            for index in indexes
        ]

        redundant_ids = (
            group_candidate_ids[
                1:
            ]
        )

        redundant_candidate_ids.extend(
            redundant_ids
        )

        canonical_candidate = deepcopy(
            dict(
                canonical_source
            )
        )

        canonical_processing_state = deepcopy(
            dict(
                canonical_candidate[
                    "candidate_processing_state"
                ]
            )
        )

        canonical_processing_state[
            "duplicate_redundant_resolution_performed"
        ] = True

        canonical_candidate[
            "candidate_processing_state"
        ] = canonical_processing_state

        canonical_candidate[
            "duplicate_redundant_hybrid_resolution"
        ] = {
            "resolution_status":
                (
                    "CANONICAL_WITH_REDUNDANT_EQUIVALENTS"
                    if redundant_ids
                    else "CANONICAL_UNIQUE"
                ),

            "redundancy_group_id":
                f"HYBRID_REDUNDANCY_GROUP:{group_number}",

            "canonical_hybrid_candidate_id":
                canonical_id,

            "group_candidate_ids":
                deepcopy(
                    group_candidate_ids
                ),

            "redundant_hybrid_candidate_ids":
                deepcopy(
                    redundant_ids
                ),

            "group_size":
                len(
                    group_candidate_ids
                ),

            "redundant_count":
                len(
                    redundant_ids
                ),

            "structural_equivalence_required":
                True,

            "exact_evidence_structure_required":
                True,

            "fuzzy_similarity_used":
                False,

            "embedding_similarity_used":
                False,

            "semantic_equivalence_inferred":
                False,

            "paraphrase_equivalence_inferred":
                False,

            "evidence_rewritten":
                False,

            "candidate_meaning_changed":
                False,

            "assessment_state_changed":
                False,

            "governance_decision_changed":
                False,

            "confidence_recalculated":
                False,

            "new_reasoning_performed":
                False,

            "article_level_consolidation_performed":
                False,
        }

        canonical_candidates.append(
            canonical_candidate
        )

        for member_position, index in enumerate(
            indexes
        ):
            member = validated_candidates[
                index
            ]

            member_id = member[
                "hybrid_candidate_id"
            ]

            is_canonical = (
                member_position == 0
            )

            resolution_records.append({
                "duplicate_redundant_resolution_id":
                    f"HYBRID_REDUNDANCY_RESOLUTION:"
                    f"{len(resolution_records) + 1}",

                "redundancy_group_id":
                    f"HYBRID_REDUNDANCY_GROUP:{group_number}",

                "hybrid_candidate_id":
                    member_id,

                "canonical_hybrid_candidate_id":
                    canonical_id,

                "candidate_role":
                    (
                        "CANONICAL"
                        if is_canonical
                        else "REDUNDANT"
                    ),

                "assessment_state":
                    member[
                        "assessment_state"
                    ],

                "structurally_equivalent":
                    True,

                "retained_in_canonical_candidate_set":
                    is_canonical,

                "fuzzy_similarity_used":
                    False,

                "semantic_equivalence_inferred":
                    False,

                "evidence_discarded":
                    False,

                "lineage_preserved":
                    True,

                "resolved":
                    True,
            })

    duplicate_group_count = sum(
        len(
            signature_groups[
                signature
            ]
        ) > 1
        for signature in signature_order
    )

    unique_group_count = sum(
        len(
            signature_groups[
                signature
            ]
        ) == 1
        for signature in signature_order
    )

    return {
        "schema_version":
            "symbolic_neural_hybrid_duplicate_redundancy_resolution_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15Q",

        "status":
            "HYBRID_DUPLICATE_REDUNDANCY_RESOLVED",

        "article_identity":
            deepcopy(
                article_identity
            ),

        "symbolic_evidence_records":
            deepcopy(
                provenance_result.get(
                    "symbolic_evidence_records",
                    [],
                )
            ),

        "neural_semantic_evidence_records":
            deepcopy(
                provenance_result.get(
                    "neural_semantic_evidence_records",
                    [],
                )
            ),

        "alignment_pairs":
            deepcopy(
                provenance_result.get(
                    "alignment_pairs",
                    [],
                )
            ),

        "agreement_conflict_assessments":
            deepcopy(
                provenance_result.get(
                    "agreement_conflict_assessments",
                    [],
                )
            ),

        "pre_resolution_hybrid_reasoning_candidates":
            deepcopy(
                candidates
            ),

        "hybrid_reasoning_candidates":
            canonical_candidates,

        "symbolic_constraint_enforcement_records":
            deepcopy(
                provenance_result.get(
                    "symbolic_constraint_enforcement_records",
                    [],
                )
            ),

        "neural_context_interpretation_records":
            deepcopy(
                provenance_result.get(
                    "neural_context_interpretation_records",
                    [],
                )
            ),

        "hybrid_evidence_fusion_records":
            deepcopy(
                provenance_result.get(
                    "hybrid_evidence_fusion_records",
                    [],
                )
            ),

        "contradiction_conflict_resolution_records":
            deepcopy(
                provenance_result.get(
                    "contradiction_conflict_resolution_records",
                    [],
                )
            ),

        "hybrid_confidence_records":
            deepcopy(
                provenance_result.get(
                    "hybrid_confidence_records",
                    [],
                )
            ),

        "reasoning_provenance_explainability_records":
            deepcopy(
                provenance_result.get(
                    "reasoning_provenance_explainability_records",
                    [],
                )
            ),

        "duplicate_redundant_hybrid_resolution_records":
            resolution_records,

        "canonical_hybrid_candidate_ids":
            canonical_candidate_ids,

        "redundant_hybrid_candidate_ids":
            redundant_candidate_ids,

        "unaligned_symbolic_evidence_ids":
            deepcopy(
                provenance_result.get(
                    "unaligned_symbolic_evidence_ids",
                    [],
                )
            ),

        "unaligned_neural_semantic_evidence_ids":
            deepcopy(
                provenance_result.get(
                    "unaligned_neural_semantic_evidence_ids",
                    [],
                )
            ),

        "article_context_boundary":
            deepcopy(
                article_context_boundary
            ),

        "duplicate_redundancy_summary": {
            "input_candidate_count":
                len(
                    candidates
                ),

            "canonical_candidate_count":
                len(
                    canonical_candidates
                ),

            "redundant_candidate_count":
                len(
                    redundant_candidate_ids
                ),

            "redundancy_group_count":
                len(
                    signature_groups
                ),

            "duplicate_group_count":
                duplicate_group_count,

            "unique_group_count":
                unique_group_count,

            "all_input_candidates_accounted_for":
                len(
                    resolution_records
                )
                == len(
                    candidates
                ),

            "first_equivalent_candidate_retained":
                True,

            "structural_equivalence_only":
                True,

            "fuzzy_similarity_used":
                False,

            "embedding_similarity_used":
                False,

            "semantic_equivalence_inferred":
                False,

            "evidence_rewritten":
                False,

            "confidence_recalculated":
                False,

            "new_reasoning_performed":
                False,

            "article_level_consolidation_performed":
                False,
        },

        "processing_boundaries": {
            "duplicate_redundant_hybrid_resolution_performed":
                True,

            "exact_structural_deduplication_only":
                True,

            "candidate_lineage_preserved":
                True,

            "pre_resolution_candidate_set_preserved":
                True,

            "first_equivalent_candidate_retained":
                True,

            "hard_symbolic_authority_preserved":
                True,

            "semantic_override_allowed":
                False,

            "fuzzy_similarity_used":
                False,

            "embedding_similarity_used":
                False,

            "semantic_equivalence_inference_performed":
                False,

            "paraphrase_equivalence_inference_performed":
                False,

            "evidence_rewrite_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_hybrid_fact_inference_performed":
                False,

            "new_article_fact_inference_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "conflict_resolution_reperformed":
                False,

            "article_level_consolidation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "article_level_hybrid_consolidation",
    }




# ============================================================================
# PATCH 4.6.15R — Article-Level Hybrid Consolidation
# ============================================================================

def consolidate_article_level_hybrid_intelligence(
    duplicate_resolution_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Consolidate Q's canonical hybrid candidates into an article-level
    organizational view.

    R performs deterministic aggregation only.

    It does NOT:
    - synthesize different candidate meanings
    - infer cross-candidate facts
    - resolve conflicts again
    - recalculate confidence
    - perform fuzzy or semantic deduplication
    - select linking targets
    - persist semantic memory
    """

    if not isinstance(
        duplicate_resolution_result,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Article-level consolidation requires the canonical Q result."
        )

    if (
        duplicate_resolution_result.get("status")
        != "HYBRID_DUPLICATE_REDUNDANCY_RESOLVED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Duplicate/redundant hybrid resolution has not been canonically completed."
        )

    if (
        duplicate_resolution_result.get("next_stage")
        != "article_level_hybrid_consolidation"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q does not hand off to article-level hybrid consolidation."
        )

    if (
        duplicate_resolution_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R requires article-local transient intelligence."
        )

    article_identity = duplicate_resolution_result.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Article-level consolidation is missing article_identity."
        )

    article_context_boundary = (
        duplicate_resolution_result.get(
            "article_context_boundary"
        )
    )

    if not isinstance(
        article_context_boundary,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Article-level consolidation is missing the article-context boundary."
        )

    if (
        article_context_boundary.get(
            "context_access_policy"
        )
        != "CERTIFIED_ARTICLE_LOCAL_EVIDENCE_ONLY"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Article-level consolidation received an invalid context policy."
        )

    canonical_candidates = (
        duplicate_resolution_result.get(
            "hybrid_reasoning_candidates"
        )
    )

    if not isinstance(
        canonical_candidates,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q canonical hybrid candidates are missing."
        )

    pre_resolution_candidates = (
        duplicate_resolution_result.get(
            "pre_resolution_hybrid_reasoning_candidates"
        )
    )

    if not isinstance(
        pre_resolution_candidates,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q pre-resolution candidate lineage is missing."
        )

    declared_canonical_ids = (
        duplicate_resolution_result.get(
            "canonical_hybrid_candidate_ids"
        )
    )

    if not isinstance(
        declared_canonical_ids,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q canonical candidate identifiers are missing."
        )

    redundant_candidate_ids = (
        duplicate_resolution_result.get(
            "redundant_hybrid_candidate_ids"
        )
    )

    if not isinstance(
        redundant_candidate_ids,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q redundant candidate identifiers are missing."
        )

    q_resolution_records = (
        duplicate_resolution_result.get(
            "duplicate_redundant_hybrid_resolution_records"
        )
    )

    if not isinstance(
        q_resolution_records,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q duplicate/redundant resolution records are missing."
        )

    q_summary = duplicate_resolution_result.get(
        "duplicate_redundancy_summary"
    )

    if not isinstance(
        q_summary,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q duplicate/redundancy summary is missing."
        )

    actual_canonical_ids: list[str] = []
    seen_candidate_ids: set[str] = set()

    consolidated_candidates: list[
        dict[str, Any]
    ] = []

    agreement_candidate_ids: list[str] = []
    conflict_candidate_ids: list[str] = []
    unresolved_candidate_ids: list[str] = []
    abstention_candidate_ids: list[str] = []

    confidence_class_index: dict[
        str,
        list[str],
    ] = {
        "EXPLICIT_AGREEMENT_SUPPORTED": [],
        "SYMBOLICALLY_GOVERNED_CONFLICT": [],
        "INSUFFICIENT_EVIDENCE": [],
    }

    symbolic_source_index: dict[
        str,
        list[str],
    ] = {
        layer: []
        for layer in _SYMBOLIC_SOURCE_LAYERS
    }

    neural_semantic_source_index: dict[
        str,
        list[str],
    ] = {
        layer: []
        for layer in _NEURAL_SEMANTIC_SOURCE_LAYERS
    }

    for candidate in canonical_candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid canonical Q hybrid candidate."
            )

        candidate_id = candidate.get(
            "hybrid_candidate_id"
        )

        if not candidate_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Canonical Q candidate is missing hybrid_candidate_id."
            )

        if candidate_id in seen_candidate_ids:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate canonical hybrid_candidate_id in R input: {candidate_id}."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        actual_canonical_ids.append(
            candidate_id
        )

        if (
            candidate.get(
                "article_identity"
            )
            != article_identity
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} belongs to a different article."
            )

        assessment_state = candidate.get(
            "assessment_state"
        )

        if (
            assessment_state
            not in _HYBRID_EXPLAINABILITY_OUTCOMES
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid assessment state."
            )

        symbolic_layer = candidate.get(
            "symbolic_source_layer"
        )

        semantic_layer = candidate.get(
            "neural_semantic_source_layer"
        )

        if (
            symbolic_layer
            not in _SYMBOLIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid symbolic source layer."
            )

        if (
            semantic_layer
            not in _NEURAL_SEMANTIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid neural/semantic source layer."
            )

        expected_rule = (
            _SYMBOLIC_PRESERVATION_RULES[
                symbolic_layer
            ]
        )

        if (
            candidate.get(
                "symbolic_preservation_rule"
            )
            != expected_rule
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost its symbolic preservation rule."
            )

        if (
            candidate.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost hard symbolic authority."
            )

        if (
            candidate.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic authority."
            )

        processing_state = candidate.get(
            "candidate_processing_state"
        )

        if not isinstance(
            processing_state,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing candidate_processing_state."
            )

        for completed_field in (
            "constructed",
            "symbolic_constraint_enforced",
            "neural_context_interpreted",
            "evidence_fused",
            "hybrid_confidence_calculated",
            "provenance_explainability_prepared",
            "duplicate_redundant_resolution_performed",
        ):
            if (
                processing_state.get(
                    completed_field
                )
                is not True
            ):
                raise SymbolicNeuralHybridIntelligenceError(
                    f"{candidate_id} reached R before completing {completed_field}."
                )

        if (
            processing_state.get(
                "article_level_hybrid_consolidated",
                False,
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} entered R after article-level consolidation was already performed."
            )

        expected_agreement = (
            assessment_state == "AGREEMENT"
        )

        expected_conflict = (
            assessment_state == "CONFLICT"
        )

        expected_unresolved = (
            assessment_state == "UNRESOLVED"
        )

        if (
            processing_state.get(
                "agreement_preserved"
            )
            is not expected_agreement
            or processing_state.get(
                "conflict_preserved"
            )
            is not expected_conflict
            or processing_state.get(
                "unresolved_preserved"
            )
            is not expected_unresolved
            or processing_state.get(
                "conflict_resolved"
            )
            is not expected_conflict
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has corrupted governed assessment state."
            )

        q_resolution = candidate.get(
            "duplicate_redundant_hybrid_resolution"
        )

        if not isinstance(
            q_resolution,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing canonical Q resolution."
            )

        if (
            q_resolution.get(
                "canonical_hybrid_candidate_id"
            )
            != candidate_id
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} does not identify itself as the canonical Q candidate."
            )

        q_resolution_status = q_resolution.get(
            "resolution_status"
        )

        if q_resolution_status not in {
            "CANONICAL_UNIQUE",
            "CANONICAL_WITH_REDUNDANT_EQUIVALENTS",
        }:
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid Q resolution status."
            )

        group_candidate_ids = q_resolution.get(
            "group_candidate_ids"
        )

        group_redundant_ids = q_resolution.get(
            "redundant_hybrid_candidate_ids"
        )

        if not isinstance(
            group_candidate_ids,
            list,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid Q group candidate lineage."
            )

        if not isinstance(
            group_redundant_ids,
            list,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid Q redundant candidate lineage."
            )

        if (
            not group_candidate_ids
            or group_candidate_ids[0]
            != candidate_id
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid canonical position in its Q redundancy group."
            )

        if (
            q_resolution.get(
                "group_size"
            )
            != len(
                group_candidate_ids
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent Q group_size."
            )

        if (
            q_resolution.get(
                "redundant_count"
            )
            != len(
                group_redundant_ids
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent Q redundant_count."
            )

        if (
            group_candidate_ids[1:]
            != group_redundant_ids
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent Q redundancy lineage."
            )

        if (
            q_resolution_status
            == "CANONICAL_UNIQUE"
            and group_redundant_ids
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is marked unique but contains redundant members."
            )

        if (
            q_resolution_status
            == "CANONICAL_WITH_REDUNDANT_EQUIVALENTS"
            and not group_redundant_ids
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is marked redundant-group canonical without redundant members."
            )

        for forbidden_true_field in (
            "fuzzy_similarity_used",
            "embedding_similarity_used",
            "semantic_equivalence_inferred",
            "paraphrase_equivalence_inferred",
            "evidence_rewritten",
            "candidate_meaning_changed",
            "assessment_state_changed",
            "governance_decision_changed",
            "confidence_recalculated",
            "new_reasoning_performed",
            "article_level_consolidation_performed",
        ):
            if (
                q_resolution.get(
                    forbidden_true_field
                )
                is not False
            ):
                raise SymbolicNeuralHybridIntelligenceError(
                    f"{candidate_id} contains invalid Q boundary state: {forbidden_true_field}."
                )

        confidence = candidate.get(
            "hybrid_confidence_assessment"
        )

        if not isinstance(
            confidence,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing O confidence."
            )

        expected_confidence_policy = (
            _HYBRID_CONFIDENCE_POLICIES[
                assessment_state
            ]
        )

        if (
            confidence.get(
                "assessment_status"
            )
            != "ASSESSED"
            or confidence.get(
                "confidence_class"
            )
            != expected_confidence_policy[
                "confidence_class"
            ]
            or confidence.get(
                "confidence_basis"
            )
            != expected_confidence_policy[
                "confidence_basis"
            ]
            or confidence.get(
                "downstream_reliance_mode"
            )
            != expected_confidence_policy[
                "downstream_reliance_mode"
            ]
            or confidence.get(
                "abstention_required"
            )
            is not expected_confidence_policy[
                "abstention_required"
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains inconsistent O confidence state."
            )

        provenance = candidate.get(
            "reasoning_provenance_explainability"
        )

        if not isinstance(
            provenance,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing P provenance."
            )

        if (
            provenance.get(
                "preparation_status"
            )
            != "PREPARED"
            or provenance.get(
                "hybrid_candidate_id"
            )
            != candidate_id
            or provenance.get(
                "assessment_state"
            )
            != assessment_state
            or provenance.get(
                "confidence_class"
            )
            != expected_confidence_policy[
                "confidence_class"
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains inconsistent P provenance state."
            )

        consolidated_candidate = deepcopy(
            dict(candidate)
        )

        consolidated_processing_state = deepcopy(
            dict(processing_state)
        )

        consolidated_processing_state[
            "article_level_hybrid_consolidated"
        ] = True

        consolidated_candidate[
            "candidate_processing_state"
        ] = consolidated_processing_state

        consolidated_candidate[
            "article_level_hybrid_membership"
        ] = {
            "membership_status":
                "CANONICAL_ARTICLE_MEMBER",

            "article_identity":
                deepcopy(
                    article_identity
                ),

            "hybrid_candidate_id":
                candidate_id,

            "assessment_state":
                assessment_state,

            "confidence_class":
                expected_confidence_policy[
                    "confidence_class"
                ],

            "downstream_reliance_mode":
                expected_confidence_policy[
                    "downstream_reliance_mode"
                ],

            "abstention_required":
                expected_confidence_policy[
                    "abstention_required"
                ],

            "symbolic_source_layer":
                symbolic_layer,

            "neural_semantic_source_layer":
                semantic_layer,

            "redundancy_group_id":
                q_resolution.get(
                    "redundancy_group_id"
                ),

            "redundant_hybrid_candidate_ids":
                deepcopy(
                    group_redundant_ids
                ),

            "cross_candidate_synthesis_performed":
                False,

            "candidate_meaning_changed":
                False,

            "evidence_rewritten":
                False,

            "conflict_resolution_reperformed":
                False,

            "confidence_recalculated":
                False,

            "new_reasoning_performed":
                False,

            "new_article_fact_inferred":
                False,
        }

        consolidated_candidates.append(
            consolidated_candidate
        )

        if assessment_state == "AGREEMENT":
            agreement_candidate_ids.append(
                candidate_id
            )

        elif assessment_state == "CONFLICT":
            conflict_candidate_ids.append(
                candidate_id
            )

        else:
            unresolved_candidate_ids.append(
                candidate_id
            )

        if (
            expected_confidence_policy[
                "abstention_required"
            ]
        ):
            abstention_candidate_ids.append(
                candidate_id
            )

        confidence_class_index[
            expected_confidence_policy[
                "confidence_class"
            ]
        ].append(
            candidate_id
        )

        symbolic_source_index[
            symbolic_layer
        ].append(
            candidate_id
        )

        neural_semantic_source_index[
            semantic_layer
        ].append(
            candidate_id
        )

    if (
        actual_canonical_ids
        != declared_canonical_ids
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q canonical candidate identifier order does not match the canonical candidate set."
        )

    if (
        len(
            set(
                redundant_candidate_ids
            )
        )
        != len(
            redundant_candidate_ids
        )
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q contains duplicate redundant candidate identifiers."
        )

    if (
        set(
            actual_canonical_ids
        )
        & set(
            redundant_candidate_ids
        )
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "A Q candidate cannot be both canonical and redundant."
        )

    pre_resolution_ids: list[str] = []

    for candidate in pre_resolution_candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid Q pre-resolution candidate."
            )

        candidate_id = candidate.get(
            "hybrid_candidate_id"
        )

        if not candidate_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Q pre-resolution candidate is missing hybrid_candidate_id."
            )

        pre_resolution_ids.append(
            candidate_id
        )

    if (
        len(
            pre_resolution_ids
        )
        != len(
            set(
                pre_resolution_ids
            )
        )
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q pre-resolution candidate lineage contains duplicate candidate IDs."
        )

    if (
        set(
            pre_resolution_ids
        )
        != (
            set(
                actual_canonical_ids
            )
            | set(
                redundant_candidate_ids
            )
        )
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q pre-resolution lineage does not account for canonical and redundant candidates."
        )

    if (
        q_summary.get(
            "input_candidate_count"
        )
        != len(
            pre_resolution_candidates
        )
        or q_summary.get(
            "canonical_candidate_count"
        )
        != len(
            canonical_candidates
        )
        or q_summary.get(
            "redundant_candidate_count"
        )
        != len(
            redundant_candidate_ids
        )
        or q_summary.get(
            "all_input_candidates_accounted_for"
        )
        is not True
        or q_summary.get(
            "structural_equivalence_only"
        )
        is not True
        or q_summary.get(
            "fuzzy_similarity_used"
        )
        is not False
        or q_summary.get(
            "embedding_similarity_used"
        )
        is not False
        or q_summary.get(
            "semantic_equivalence_inferred"
        )
        is not False
        or q_summary.get(
            "new_reasoning_performed"
        )
        is not False
        or q_summary.get(
            "article_level_consolidation_performed"
        )
        is not False
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q duplicate/redundancy summary is inconsistent."
        )

    if (
        len(
            q_resolution_records
        )
        != len(
            pre_resolution_candidates
        )
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q resolution-record count does not account for the full pre-resolution candidate set."
        )

    q_record_candidate_ids: list[str] = []

    expected_q_record_lineage: dict[
        str,
        dict[str, Any],
    ] = {}

    for canonical_candidate in canonical_candidates:

        canonical_id = canonical_candidate[
            "hybrid_candidate_id"
        ]

        q_resolution = canonical_candidate[
            "duplicate_redundant_hybrid_resolution"
        ]

        redundancy_group_id = q_resolution.get(
            "redundancy_group_id"
        )

        if not redundancy_group_id:
            raise SymbolicNeuralHybridIntelligenceError(
                f"{canonical_id} is missing Q redundancy_group_id."
            )

        group_candidate_ids = q_resolution[
            "group_candidate_ids"
        ]

        for position, group_candidate_id in enumerate(
            group_candidate_ids
        ):
            if (
                group_candidate_id
                in expected_q_record_lineage
            ):
                raise SymbolicNeuralHybridIntelligenceError(
                    f"Q candidate {group_candidate_id} appears in multiple redundancy groups."
                )

            expected_q_record_lineage[
                group_candidate_id
            ] = {
                "canonical_hybrid_candidate_id":
                    canonical_id,

                "redundancy_group_id":
                    redundancy_group_id,

                "candidate_role":
                    (
                        "CANONICAL"
                        if position == 0
                        else "REDUNDANT"
                    ),

                "retained_in_canonical_candidate_set":
                    position == 0,

                "assessment_state":
                    canonical_candidate[
                        "assessment_state"
                    ],
            }

    if (
        set(
            expected_q_record_lineage
        )
        != set(
            pre_resolution_ids
        )
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q canonical group envelopes do not account for the full pre-resolution lineage."
        )

    q_record_candidate_ids: list[str] = []

    for record in q_resolution_records:

        if not isinstance(
            record,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid Q duplicate/redundant resolution record."
            )

        record_candidate_id = record.get(
            "hybrid_candidate_id"
        )

        if not record_candidate_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "Q resolution record is missing hybrid_candidate_id."
            )

        if (
            record.get(
                "resolved"
            )
            is not True
            or record.get(
                "lineage_preserved"
            )
            is not True
            or record.get(
                "evidence_discarded"
            )
            is not False
            or record.get(
                "fuzzy_similarity_used"
            )
            is not False
            or record.get(
                "semantic_equivalence_inferred"
            )
            is not False
            or record.get(
                "structurally_equivalent"
            )
            is not True
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"Q resolution record for {record_candidate_id} violates the certified Q boundary."
            )

        expected_lineage = expected_q_record_lineage.get(
            record_candidate_id
        )

        if not isinstance(
            expected_lineage,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"Q resolution record for {record_candidate_id} has no canonical group lineage."
            )

        if (
            record.get(
                "canonical_hybrid_candidate_id"
            )
            != expected_lineage[
                "canonical_hybrid_candidate_id"
            ]
            or record.get(
                "redundancy_group_id"
            )
            != expected_lineage[
                "redundancy_group_id"
            ]
            or record.get(
                "candidate_role"
            )
            != expected_lineage[
                "candidate_role"
            ]
            or record.get(
                "retained_in_canonical_candidate_set"
            )
            is not expected_lineage[
                "retained_in_canonical_candidate_set"
            ]
            or record.get(
                "assessment_state"
            )
            != expected_lineage[
                "assessment_state"
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"Q resolution record for {record_candidate_id} is inconsistent with its canonical redundancy group."
            )

        q_record_candidate_ids.append(
            record_candidate_id
        )

    if (
        len(
            q_record_candidate_ids
        )
        != len(
            set(
                q_record_candidate_ids
            )
        )
        or set(
            q_record_candidate_ids
        )
        != set(
            pre_resolution_ids
        )
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Q resolution records do not uniquely account for all pre-resolution candidates."
        )

    article_level_record = {
        "consolidation_status":
            "ARTICLE_LEVEL_HYBRID_CONSOLIDATED",

        "article_identity":
            deepcopy(
                article_identity
            ),

        "canonical_hybrid_candidate_ids":
            deepcopy(
                actual_canonical_ids
            ),

        "canonical_candidate_count":
            len(
                actual_canonical_ids
            ),

        "agreement_candidate_ids":
            deepcopy(
                agreement_candidate_ids
            ),

        "governed_conflict_candidate_ids":
            deepcopy(
                conflict_candidate_ids
            ),

        "unresolved_candidate_ids":
            deepcopy(
                unresolved_candidate_ids
            ),

        "abstention_candidate_ids":
            deepcopy(
                abstention_candidate_ids
            ),

        "redundant_hybrid_candidate_ids":
            deepcopy(
                redundant_candidate_ids
            ),

        "confidence_class_index":
            deepcopy(
                confidence_class_index
            ),

        "symbolic_source_index":
            deepcopy(
                symbolic_source_index
            ),

        "neural_semantic_source_index":
            deepcopy(
                neural_semantic_source_index
            ),

        "article_has_explicit_agreement":
            bool(
                agreement_candidate_ids
            ),

        "article_has_symbolically_governed_conflict":
            bool(
                conflict_candidate_ids
            ),

        "article_has_unresolved_hybrid_evidence":
            bool(
                unresolved_candidate_ids
            ),

        "article_requires_hybrid_abstention":
            bool(
                abstention_candidate_ids
            ),

        "canonical_candidates_preserved":
            True,

        "redundant_lineage_preserved":
            True,

        "cross_candidate_synthesis_performed":
            False,

        "cross_candidate_semantic_equivalence_inferred":
            False,

        "cross_candidate_conflict_resolution_performed":
            False,

        "candidate_meaning_changed":
            False,

        "evidence_rewritten":
            False,

        "confidence_recalculated":
            False,

        "new_reasoning_performed":
            False,

        "new_article_fact_inferred":
            False,

        "external_model_called":
            False,
    }

    return {
        "schema_version":
            "symbolic_neural_hybrid_article_level_consolidation_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15R",

        "status":
            "HYBRID_ARTICLE_LEVEL_CONSOLIDATED",

        "article_identity":
            deepcopy(
                article_identity
            ),

        "symbolic_evidence_records":
            deepcopy(
                duplicate_resolution_result.get(
                    "symbolic_evidence_records",
                    [],
                )
            ),

        "neural_semantic_evidence_records":
            deepcopy(
                duplicate_resolution_result.get(
                    "neural_semantic_evidence_records",
                    [],
                )
            ),

        "alignment_pairs":
            deepcopy(
                duplicate_resolution_result.get(
                    "alignment_pairs",
                    [],
                )
            ),

        "agreement_conflict_assessments":
            deepcopy(
                duplicate_resolution_result.get(
                    "agreement_conflict_assessments",
                    [],
                )
            ),

        "pre_resolution_hybrid_reasoning_candidates":
            deepcopy(
                pre_resolution_candidates
            ),

        "hybrid_reasoning_candidates":
            consolidated_candidates,

        "symbolic_constraint_enforcement_records":
            deepcopy(
                duplicate_resolution_result.get(
                    "symbolic_constraint_enforcement_records",
                    [],
                )
            ),

        "neural_context_interpretation_records":
            deepcopy(
                duplicate_resolution_result.get(
                    "neural_context_interpretation_records",
                    [],
                )
            ),

        "hybrid_evidence_fusion_records":
            deepcopy(
                duplicate_resolution_result.get(
                    "hybrid_evidence_fusion_records",
                    [],
                )
            ),

        "contradiction_conflict_resolution_records":
            deepcopy(
                duplicate_resolution_result.get(
                    "contradiction_conflict_resolution_records",
                    [],
                )
            ),

        "hybrid_confidence_records":
            deepcopy(
                duplicate_resolution_result.get(
                    "hybrid_confidence_records",
                    [],
                )
            ),

        "reasoning_provenance_explainability_records":
            deepcopy(
                duplicate_resolution_result.get(
                    "reasoning_provenance_explainability_records",
                    [],
                )
            ),

        "duplicate_redundant_hybrid_resolution_records":
            deepcopy(
                q_resolution_records
            ),

        "canonical_hybrid_candidate_ids":
            deepcopy(
                actual_canonical_ids
            ),

        "redundant_hybrid_candidate_ids":
            deepcopy(
                redundant_candidate_ids
            ),

        "article_level_hybrid_consolidation":
            article_level_record,

        "unaligned_symbolic_evidence_ids":
            deepcopy(
                duplicate_resolution_result.get(
                    "unaligned_symbolic_evidence_ids",
                    [],
                )
            ),

        "unaligned_neural_semantic_evidence_ids":
            deepcopy(
                duplicate_resolution_result.get(
                    "unaligned_neural_semantic_evidence_ids",
                    [],
                )
            ),

        "article_context_boundary":
            deepcopy(
                article_context_boundary
            ),

        "article_level_consolidation_summary": {
            "pre_resolution_candidate_count":
                len(
                    pre_resolution_candidates
                ),

            "canonical_candidate_count":
                len(
                    consolidated_candidates
                ),

            "redundant_candidate_count":
                len(
                    redundant_candidate_ids
                ),

            "agreement_candidate_count":
                len(
                    agreement_candidate_ids
                ),

            "governed_conflict_candidate_count":
                len(
                    conflict_candidate_ids
                ),

            "unresolved_candidate_count":
                len(
                    unresolved_candidate_ids
                ),

            "abstention_candidate_count":
                len(
                    abstention_candidate_ids
                ),

            "all_canonical_candidates_accounted_for":
                (
                    len(
                        agreement_candidate_ids
                    )
                    + len(
                        conflict_candidate_ids
                    )
                    + len(
                        unresolved_candidate_ids
                    )
                    == len(
                        consolidated_candidates
                    )
                ),

            "candidate_lineage_preserved":
                True,

            "cross_candidate_synthesis_performed":
                False,

            "semantic_equivalence_inferred":
                False,

            "conflict_resolution_reperformed":
                False,

            "confidence_recalculated":
                False,

            "new_reasoning_performed":
                False,

            "new_article_fact_inferred":
                False,
        },

        "processing_boundaries": {
            "article_level_hybrid_consolidation_performed":
                True,

            "deterministic_aggregation_only":
                True,

            "canonical_candidate_set_preserved":
                True,

            "pre_resolution_candidate_lineage_preserved":
                True,

            "redundant_candidate_lineage_preserved":
                True,

            "hard_symbolic_authority_preserved":
                True,

            "semantic_override_allowed":
                False,

            "cross_candidate_synthesis_performed":
                False,

            "cross_candidate_semantic_equivalence_inference_performed":
                False,

            "cross_candidate_conflict_resolution_performed":
                False,

            "candidate_meaning_change_performed":
                False,

            "evidence_rewrite_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_hybrid_fact_inference_performed":
                False,

            "new_article_fact_inference_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "duplicate_resolution_reperformed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "final_symbolic_neural_hybrid_result",
    }



# ============================================================================
# PATCH 4.6.15S — Final Symbolic–Neural Hybrid Intelligence Result
# ============================================================================

_HYBRID_FINAL_OUTCOMES = {
    "AGREEMENT":
        "FINAL_AGREEMENT_SUPPORTED",

    "CONFLICT":
        "FINAL_SYMBOLICALLY_GOVERNED_CONFLICT",

    "UNRESOLVED":
        "FINAL_UNRESOLVED_ABSTENTION",
}


def build_final_symbolic_neural_hybrid_intelligence_result(
    article_consolidation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build the canonical final result for Symbolic–Neural Hybrid
    Intelligence.

    S is a final packaging/handoff stage only.

    It does NOT:
    - perform new reasoning
    - alter symbolic or semantic evidence
    - re-resolve conflicts
    - recalculate confidence
    - re-run deduplication
    - synthesize new article facts
    - persist intelligence
    - make linking decisions
    """

    if not isinstance(
        article_consolidation_result,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Final hybrid result requires the canonical R result."
        )

    if (
        article_consolidation_result.get("status")
        != "HYBRID_ARTICLE_LEVEL_CONSOLIDATED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Article-level hybrid consolidation has not been canonically completed."
        )

    if (
        article_consolidation_result.get("next_stage")
        != "final_symbolic_neural_hybrid_result"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R does not hand off to the final Symbolic–Neural Hybrid result."
        )

    if (
        article_consolidation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "S requires article-local transient intelligence."
        )

    article_identity = article_consolidation_result.get(
        "article_identity"
    )

    if article_identity is None:
        raise SymbolicNeuralHybridIntelligenceError(
            "Final hybrid result is missing article_identity."
        )

    article_context_boundary = (
        article_consolidation_result.get(
            "article_context_boundary"
        )
    )

    if not isinstance(
        article_context_boundary,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Final hybrid result is missing the article-context boundary."
        )

    if (
        article_context_boundary.get(
            "context_access_policy"
        )
        != "CERTIFIED_ARTICLE_LOCAL_EVIDENCE_ONLY"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "Final hybrid result received an invalid article-context policy."
        )

    candidates = article_consolidation_result.get(
        "hybrid_reasoning_candidates"
    )

    if not isinstance(
        candidates,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R canonical hybrid candidates are missing."
        )

    canonical_candidate_ids = (
        article_consolidation_result.get(
            "canonical_hybrid_candidate_ids"
        )
    )

    if not isinstance(
        canonical_candidate_ids,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R canonical candidate identifiers are missing."
        )

    redundant_candidate_ids = (
        article_consolidation_result.get(
            "redundant_hybrid_candidate_ids"
        )
    )

    if not isinstance(
        redundant_candidate_ids,
        list,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R redundant candidate identifiers are missing."
        )

    article_consolidation = (
        article_consolidation_result.get(
            "article_level_hybrid_consolidation"
        )
    )

    if not isinstance(
        article_consolidation,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R article-level hybrid consolidation record is missing."
        )

    consolidation_summary = (
        article_consolidation_result.get(
            "article_level_consolidation_summary"
        )
    )

    if not isinstance(
        consolidation_summary,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R article-level consolidation summary is missing."
        )

    if (
        article_consolidation.get(
            "consolidation_status"
        )
        != "ARTICLE_LEVEL_HYBRID_CONSOLIDATED"
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R article-level consolidation status is invalid."
        )

    if (
        article_consolidation.get(
            "article_identity"
        )
        != article_identity
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R article-level consolidation belongs to a different article."
        )

    if (
        article_consolidation.get(
            "canonical_hybrid_candidate_ids"
        )
        != canonical_candidate_ids
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R canonical candidate lineage is inconsistent."
        )

    if (
        article_consolidation.get(
            "redundant_hybrid_candidate_ids"
        )
        != redundant_candidate_ids
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R redundant candidate lineage is inconsistent."
        )

    if (
        article_consolidation.get(
            "canonical_candidate_count"
        )
        != len(
            candidates
        )
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R canonical candidate count is inconsistent."
        )

    agreement_ids = article_consolidation.get(
        "agreement_candidate_ids"
    )

    conflict_ids = article_consolidation.get(
        "governed_conflict_candidate_ids"
    )

    unresolved_ids = article_consolidation.get(
        "unresolved_candidate_ids"
    )

    abstention_ids = article_consolidation.get(
        "abstention_candidate_ids"
    )

    for collection_name, collection in (
        (
            "agreement_candidate_ids",
            agreement_ids,
        ),
        (
            "governed_conflict_candidate_ids",
            conflict_ids,
        ),
        (
            "unresolved_candidate_ids",
            unresolved_ids,
        ),
        (
            "abstention_candidate_ids",
            abstention_ids,
        ),
    ):
        if not isinstance(
            collection,
            list,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"R {collection_name} is invalid."
            )

    expected_ids_from_states = (
        agreement_ids
        + conflict_ids
        + unresolved_ids
    )

    if (
        expected_ids_from_states
        != canonical_candidate_ids
    ):
        # R preserves canonical candidate order globally, but its state
        # collections are grouped. Compare membership as well below.
        if (
            set(
                expected_ids_from_states
            )
            != set(
                canonical_candidate_ids
            )
            or len(
                expected_ids_from_states
            )
            != len(
                canonical_candidate_ids
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "R article-level state indexes do not account for all canonical candidates."
            )

    if (
        set(
            abstention_ids
        )
        != set(
            unresolved_ids
        )
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R abstention candidates must exactly match unresolved hybrid candidates."
        )

    expected_article_flags = {
        "article_has_explicit_agreement":
            bool(
                agreement_ids
            ),

        "article_has_symbolically_governed_conflict":
            bool(
                conflict_ids
            ),

        "article_has_unresolved_hybrid_evidence":
            bool(
                unresolved_ids
            ),

        "article_requires_hybrid_abstention":
            bool(
                abstention_ids
            ),
    }

    for flag_name, expected_value in (
        expected_article_flags.items()
    ):
        if (
            article_consolidation.get(
                flag_name
            )
            is not expected_value
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"R article-level flag {flag_name} is inconsistent."
            )

    for required_true_field in (
        "canonical_candidates_preserved",
        "redundant_lineage_preserved",
    ):
        if (
            article_consolidation.get(
                required_true_field
            )
            is not True
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"R article-level boundary {required_true_field} is invalid."
            )

    for required_false_field in (
        "cross_candidate_synthesis_performed",
        "cross_candidate_semantic_equivalence_inferred",
        "cross_candidate_conflict_resolution_performed",
        "candidate_meaning_changed",
        "evidence_rewritten",
        "confidence_recalculated",
        "new_reasoning_performed",
        "new_article_fact_inferred",
        "external_model_called",
    ):
        if (
            article_consolidation.get(
                required_false_field
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"R article-level boundary {required_false_field} is invalid."
            )

    if (
        consolidation_summary.get(
            "canonical_candidate_count"
        )
        != len(
            candidates
        )
        or consolidation_summary.get(
            "redundant_candidate_count"
        )
        != len(
            redundant_candidate_ids
        )
        or consolidation_summary.get(
            "agreement_candidate_count"
        )
        != len(
            agreement_ids
        )
        or consolidation_summary.get(
            "governed_conflict_candidate_count"
        )
        != len(
            conflict_ids
        )
        or consolidation_summary.get(
            "unresolved_candidate_count"
        )
        != len(
            unresolved_ids
        )
        or consolidation_summary.get(
            "abstention_candidate_count"
        )
        != len(
            abstention_ids
        )
        or consolidation_summary.get(
            "all_canonical_candidates_accounted_for"
        )
        is not True
        or consolidation_summary.get(
            "candidate_lineage_preserved"
        )
        is not True
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R article-level consolidation summary is inconsistent."
        )

    for forbidden_summary_field in (
        "cross_candidate_synthesis_performed",
        "semantic_equivalence_inferred",
        "conflict_resolution_reperformed",
        "confidence_recalculated",
        "new_reasoning_performed",
        "new_article_fact_inferred",
    ):
        if (
            consolidation_summary.get(
                forbidden_summary_field
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"R summary boundary {forbidden_summary_field} is invalid."
            )

    actual_candidate_ids: list[str] = []
    seen_candidate_ids: set[str] = set()
    seen_group_redundant_ids: set[str] = set()

    final_candidates: list[
        dict[str, Any]
    ] = []

    final_candidate_records: list[
        dict[str, Any]
    ] = []

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                "Invalid R canonical hybrid candidate."
            )

        candidate_id = candidate.get(
            "hybrid_candidate_id"
        )

        if not candidate_id:
            raise SymbolicNeuralHybridIntelligenceError(
                "R canonical candidate is missing hybrid_candidate_id."
            )

        if candidate_id in seen_candidate_ids:
            raise SymbolicNeuralHybridIntelligenceError(
                f"Duplicate R canonical candidate ID: {candidate_id}."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        actual_candidate_ids.append(
            candidate_id
        )

        if (
            candidate.get(
                "article_identity"
            )
            != article_identity
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} belongs to a different article."
            )

        assessment_state = candidate.get(
            "assessment_state"
        )

        if (
            assessment_state
            not in _HYBRID_FINAL_OUTCOMES
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid assessment state."
            )

        symbolic_layer = candidate.get(
            "symbolic_source_layer"
        )

        semantic_layer = candidate.get(
            "neural_semantic_source_layer"
        )

        if (
            symbolic_layer
            not in _SYMBOLIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid symbolic source layer."
            )

        if (
            semantic_layer
            not in _NEURAL_SEMANTIC_SOURCE_LAYERS
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has an invalid neural/semantic source layer."
            )

        expected_rule = (
            _SYMBOLIC_PRESERVATION_RULES[
                symbolic_layer
            ]
        )

        if (
            candidate.get(
                "symbolic_preservation_rule"
            )
            != expected_rule
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost its symbolic preservation rule."
            )

        if (
            candidate.get(
                "symbolic_constraint_authority"
            )
            != "HARD_WHEN_EXPLICIT_AND_CERTIFIED"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has lost hard symbolic authority."
            )

        if (
            candidate.get(
                "neural_semantic_authority"
            )
            != "INTERPRETIVE_ONLY"
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid neural/semantic authority."
            )

        processing_state = candidate.get(
            "candidate_processing_state"
        )

        if not isinstance(
            processing_state,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing candidate_processing_state."
            )

        for completed_field in (
            "constructed",
            "symbolic_constraint_enforced",
            "neural_context_interpreted",
            "evidence_fused",
            "hybrid_confidence_calculated",
            "provenance_explainability_prepared",
            "duplicate_redundant_resolution_performed",
            "article_level_hybrid_consolidated",
        ):
            if (
                processing_state.get(
                    completed_field
                )
                is not True
            ):
                raise SymbolicNeuralHybridIntelligenceError(
                    f"{candidate_id} reached S before completing {completed_field}."
                )

        if (
            processing_state.get(
                "final_symbolic_neural_hybrid_result_prepared",
                False,
            )
            is not False
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} entered S after final-result preparation was already performed."
            )

        expected_agreement = (
            assessment_state == "AGREEMENT"
        )

        expected_conflict = (
            assessment_state == "CONFLICT"
        )

        expected_unresolved = (
            assessment_state == "UNRESOLVED"
        )

        if (
            processing_state.get(
                "agreement_preserved"
            )
            is not expected_agreement
            or processing_state.get(
                "conflict_preserved"
            )
            is not expected_conflict
            or processing_state.get(
                "unresolved_preserved"
            )
            is not expected_unresolved
            or processing_state.get(
                "conflict_resolved"
            )
            is not expected_conflict
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has corrupted governed assessment state."
            )

        membership = candidate.get(
            "article_level_hybrid_membership"
        )

        if not isinstance(
            membership,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing R article-level membership."
            )

        expected_confidence_policy = (
            _HYBRID_CONFIDENCE_POLICIES[
                assessment_state
            ]
        )

        if (
            membership.get(
                "membership_status"
            )
            != "CANONICAL_ARTICLE_MEMBER"
            or membership.get(
                "article_identity"
            )
            != article_identity
            or membership.get(
                "hybrid_candidate_id"
            )
            != candidate_id
            or membership.get(
                "assessment_state"
            )
            != assessment_state
            or membership.get(
                "confidence_class"
            )
            != expected_confidence_policy[
                "confidence_class"
            ]
            or membership.get(
                "downstream_reliance_mode"
            )
            != expected_confidence_policy[
                "downstream_reliance_mode"
            ]
            or membership.get(
                "abstention_required"
            )
            is not expected_confidence_policy[
                "abstention_required"
            ]
            or membership.get(
                "symbolic_source_layer"
            )
            != symbolic_layer
            or membership.get(
                "neural_semantic_source_layer"
            )
            != semantic_layer
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent R article-level membership."
            )

        for forbidden_membership_field in (
            "cross_candidate_synthesis_performed",
            "candidate_meaning_changed",
            "evidence_rewritten",
            "conflict_resolution_reperformed",
            "confidence_recalculated",
            "new_reasoning_performed",
            "new_article_fact_inferred",
        ):
            if (
                membership.get(
                    forbidden_membership_field
                )
                is not False
            ):
                raise SymbolicNeuralHybridIntelligenceError(
                    f"{candidate_id} contains invalid R membership boundary: {forbidden_membership_field}."
                )

        confidence = candidate.get(
            "hybrid_confidence_assessment"
        )

        provenance = candidate.get(
            "reasoning_provenance_explainability"
        )

        q_resolution = candidate.get(
            "duplicate_redundant_hybrid_resolution"
        )

        if not isinstance(
            confidence,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing O confidence."
            )

        if not isinstance(
            provenance,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing P provenance."
            )

        if not isinstance(
            q_resolution,
            Mapping,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing Q redundancy resolution."
            )

        if (
            confidence.get(
                "assessment_status"
            )
            != "ASSESSED"
            or confidence.get(
                "confidence_class"
            )
            != expected_confidence_policy[
                "confidence_class"
            ]
            or confidence.get(
                "confidence_basis"
            )
            != expected_confidence_policy[
                "confidence_basis"
            ]
            or confidence.get(
                "downstream_reliance_mode"
            )
            != expected_confidence_policy[
                "downstream_reliance_mode"
            ]
            or confidence.get(
                "abstention_required"
            )
            is not expected_confidence_policy[
                "abstention_required"
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains inconsistent O confidence."
            )

        if (
            provenance.get(
                "preparation_status"
            )
            != "PREPARED"
            or provenance.get(
                "hybrid_candidate_id"
            )
            != candidate_id
            or provenance.get(
                "assessment_state"
            )
            != assessment_state
            or provenance.get(
                "confidence_class"
            )
            != expected_confidence_policy[
                "confidence_class"
            ]
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains inconsistent P provenance."
            )

        if (
            q_resolution.get(
                "canonical_hybrid_candidate_id"
            )
            != candidate_id
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is not the canonical Q representative."
            )

        q_redundancy_group_id = q_resolution.get(
            "redundancy_group_id"
        )

        q_redundant_ids = q_resolution.get(
            "redundant_hybrid_candidate_ids"
        )

        if not q_redundancy_group_id:
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} is missing its Q redundancy-group identity."
            )

        if not isinstance(
            q_redundant_ids,
            list,
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has invalid Q redundant-candidate lineage."
            )

        if (
            membership.get(
                "redundancy_group_id"
            )
            != q_redundancy_group_id
            or membership.get(
                "redundant_hybrid_candidate_ids"
            )
            != q_redundant_ids
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} has inconsistent Q-to-R redundancy lineage."
            )

        if (
            len(
                q_redundant_ids
            )
            != len(
                set(
                    q_redundant_ids
                )
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} contains duplicate redundant candidate IDs."
            )

        if candidate_id in q_redundant_ids:
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} cannot be redundant to itself."
            )

        if (
            not set(
                q_redundant_ids
            ).issubset(
                set(
                    redundant_candidate_ids
                )
            )
        ):
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} references redundant candidates outside the canonical R lineage."
            )

        overlapping_redundant_ids = (
            seen_group_redundant_ids
            & set(
                q_redundant_ids
            )
        )

        if overlapping_redundant_ids:
            raise SymbolicNeuralHybridIntelligenceError(
                f"{candidate_id} shares redundant lineage with another canonical candidate."
            )

        seen_group_redundant_ids.update(
            q_redundant_ids
        )

        final_candidate = deepcopy(
            dict(candidate)
        )

        final_processing_state = deepcopy(
            dict(processing_state)
        )

        final_processing_state[
            "final_symbolic_neural_hybrid_result_prepared"
        ] = True

        final_candidate[
            "candidate_processing_state"
        ] = final_processing_state

        final_candidate[
            "final_symbolic_neural_hybrid_state"
        ] = {
            "final_state_status":
                "FINAL_HYBRID_CANDIDATE_READY",

            "hybrid_candidate_id":
                candidate_id,

            "article_identity":
                deepcopy(
                    article_identity
                ),

            "final_outcome":
                _HYBRID_FINAL_OUTCOMES[
                    assessment_state
                ],

            "assessment_state":
                assessment_state,

            "confidence_class":
                expected_confidence_policy[
                    "confidence_class"
                ],

            "confidence_basis":
                expected_confidence_policy[
                    "confidence_basis"
                ],

            "downstream_reliance_mode":
                expected_confidence_policy[
                    "downstream_reliance_mode"
                ],

            "abstention_required":
                expected_confidence_policy[
                    "abstention_required"
                ],

            "symbolic_source_layer":
                symbolic_layer,

            "neural_semantic_source_layer":
                semantic_layer,

            "symbolic_preservation_rule":
                expected_rule,

            "symbolic_constraint_authority":
                "HARD_WHEN_EXPLICIT_AND_CERTIFIED",

            "neural_semantic_authority":
                "INTERPRETIVE_ONLY",

            "redundancy_group_id":
                q_resolution.get(
                    "redundancy_group_id"
                ),

            "redundant_hybrid_candidate_ids":
                deepcopy(
                    q_resolution.get(
                        "redundant_hybrid_candidate_ids",
                        [],
                    )
                ),

            "provenance_prepared":
                True,

            "article_level_membership_preserved":
                True,

            "evidence_preserved":
                True,

            "semantic_override_allowed":
                False,

            "new_reasoning_performed":
                False,

            "conflict_resolution_reperformed":
                False,

            "confidence_recalculated":
                False,

            "duplicate_resolution_reperformed":
                False,

            "article_consolidation_reperformed":
                False,

            "new_hybrid_fact_inferred":
                False,

            "new_article_fact_inferred":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,
        }

        final_candidates.append(
            final_candidate
        )

        final_candidate_records.append({
            "final_hybrid_candidate_record_id":
                f"FINAL_HYBRID_CANDIDATE:"
                f"{len(final_candidate_records) + 1}",

            "hybrid_candidate_id":
                candidate_id,

            "final_outcome":
                _HYBRID_FINAL_OUTCOMES[
                    assessment_state
                ],

            "assessment_state":
                assessment_state,

            "confidence_class":
                expected_confidence_policy[
                    "confidence_class"
                ],

            "downstream_reliance_mode":
                expected_confidence_policy[
                    "downstream_reliance_mode"
                ],

            "abstention_required":
                expected_confidence_policy[
                    "abstention_required"
                ],

            "symbolic_boundary_respected":
                True,

            "provenance_available":
                True,

            "redundancy_lineage_available":
                True,

            "article_membership_available":
                True,

            "finalized":
                True,
        })

    if (
        seen_group_redundant_ids
        != set(
            redundant_candidate_ids
        )
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R redundant candidate lineage is not fully represented by canonical Q redundancy groups."
        )

    if (
        actual_candidate_ids
        != canonical_candidate_ids
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R canonical candidate order does not match canonical_hybrid_candidate_ids."
        )

    actual_agreement_ids = [
        candidate[
            "hybrid_candidate_id"
        ]
        for candidate in candidates
        if candidate.get(
            "assessment_state"
        ) == "AGREEMENT"
    ]

    actual_conflict_ids = [
        candidate[
            "hybrid_candidate_id"
        ]
        for candidate in candidates
        if candidate.get(
            "assessment_state"
        ) == "CONFLICT"
    ]

    actual_unresolved_ids = [
        candidate[
            "hybrid_candidate_id"
        ]
        for candidate in candidates
        if candidate.get(
            "assessment_state"
        ) == "UNRESOLVED"
    ]

    if (
        actual_agreement_ids
        != agreement_ids
        or actual_conflict_ids
        != conflict_ids
        or actual_unresolved_ids
        != unresolved_ids
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R article-level state indexes do not match the canonical candidate set."
        )

    confidence_class_index = (
        article_consolidation.get(
            "confidence_class_index"
        )
    )

    symbolic_source_index = (
        article_consolidation.get(
            "symbolic_source_index"
        )
    )

    neural_semantic_source_index = (
        article_consolidation.get(
            "neural_semantic_source_index"
        )
    )

    if not isinstance(
        confidence_class_index,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R article-level confidence-class index is invalid."
        )

    if not isinstance(
        symbolic_source_index,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R article-level symbolic-source index is invalid."
        )

    if not isinstance(
        neural_semantic_source_index,
        Mapping,
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R article-level neural/semantic-source index is invalid."
        )

    expected_confidence_class_index = {
        "EXPLICIT_AGREEMENT_SUPPORTED": [],
        "SYMBOLICALLY_GOVERNED_CONFLICT": [],
        "INSUFFICIENT_EVIDENCE": [],
    }

    expected_symbolic_source_index = {
        layer: []
        for layer in _SYMBOLIC_SOURCE_LAYERS
    }

    expected_neural_semantic_source_index = {
        layer: []
        for layer in _NEURAL_SEMANTIC_SOURCE_LAYERS
    }

    for candidate in candidates:

        candidate_id = candidate[
            "hybrid_candidate_id"
        ]

        assessment_state = candidate[
            "assessment_state"
        ]

        confidence_policy = (
            _HYBRID_CONFIDENCE_POLICIES[
                assessment_state
            ]
        )

        confidence_class = confidence_policy[
            "confidence_class"
        ]

        expected_confidence_class_index[
            confidence_class
        ].append(
            candidate_id
        )

        expected_symbolic_source_index[
            candidate[
                "symbolic_source_layer"
            ]
        ].append(
            candidate_id
        )

        expected_neural_semantic_source_index[
            candidate[
                "neural_semantic_source_layer"
            ]
        ].append(
            candidate_id
        )

    if (
        dict(
            confidence_class_index
        )
        != expected_confidence_class_index
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R confidence-class index does not match the canonical candidate set."
        )

    if (
        dict(
            symbolic_source_index
        )
        != expected_symbolic_source_index
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R symbolic-source index does not match the canonical candidate set."
        )

    if (
        dict(
            neural_semantic_source_index
        )
        != expected_neural_semantic_source_index
    ):
        raise SymbolicNeuralHybridIntelligenceError(
            "R neural/semantic-source index does not match the canonical candidate set."
        )

    final_article_record = {
        "final_status":
            "SYMBOLIC_NEURAL_HYBRID_INTELLIGENCE_READY",

        "article_identity":
            deepcopy(
                article_identity
            ),

        "canonical_hybrid_candidate_ids":
            deepcopy(
                canonical_candidate_ids
            ),

        "redundant_hybrid_candidate_ids":
            deepcopy(
                redundant_candidate_ids
            ),

        "agreement_candidate_ids":
            deepcopy(
                agreement_ids
            ),

        "governed_conflict_candidate_ids":
            deepcopy(
                conflict_ids
            ),

        "unresolved_candidate_ids":
            deepcopy(
                unresolved_ids
            ),

        "abstention_candidate_ids":
            deepcopy(
                abstention_ids
            ),

        "canonical_candidate_count":
            len(
                canonical_candidate_ids
            ),

        "redundant_candidate_count":
            len(
                redundant_candidate_ids
            ),

        "article_has_explicit_agreement":
            bool(
                agreement_ids
            ),

        "article_has_symbolically_governed_conflict":
            bool(
                conflict_ids
            ),

        "article_has_unresolved_hybrid_evidence":
            bool(
                unresolved_ids
            ),

        "article_requires_hybrid_abstention":
            bool(
                abstention_ids
            ),

        "hard_symbolic_authority_preserved":
            True,

        "neural_semantic_authority":
            "INTERPRETIVE_ONLY",

        "provenance_preserved":
            True,

        "redundancy_lineage_preserved":
            True,

        "article_consolidation_preserved":
            True,

        "semantic_override_allowed":
            False,

        "new_reasoning_performed":
            False,

        "cross_candidate_synthesis_performed":
            False,

        "conflict_resolution_reperformed":
            False,

        "confidence_recalculated":
            False,

        "duplicate_resolution_reperformed":
            False,

        "new_hybrid_fact_inferred":
            False,

        "new_article_fact_inferred":
            False,

        "truth_assessment_performed":
            False,

        "external_validation_performed":
            False,

        "external_model_called":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "persistence_performed":
            False,
    }

    return {
        "schema_version":
            "symbolic_neural_hybrid_intelligence_result_v1",

        "symbolic_neural_hybrid_intelligence_version":
            "symbolic_neural_hybrid_intelligence_v1",

        "phase":
            "4.6.15",

        "patch":
            "4.6.15S",

        "status":
            "SYMBOLIC_NEURAL_HYBRID_INTELLIGENCE_RESULT_READY",

        "article_identity":
            deepcopy(
                article_identity
            ),

        "symbolic_evidence_records":
            deepcopy(
                article_consolidation_result.get(
                    "symbolic_evidence_records",
                    [],
                )
            ),

        "neural_semantic_evidence_records":
            deepcopy(
                article_consolidation_result.get(
                    "neural_semantic_evidence_records",
                    [],
                )
            ),

        "alignment_pairs":
            deepcopy(
                article_consolidation_result.get(
                    "alignment_pairs",
                    [],
                )
            ),

        "agreement_conflict_assessments":
            deepcopy(
                article_consolidation_result.get(
                    "agreement_conflict_assessments",
                    [],
                )
            ),

        "pre_resolution_hybrid_reasoning_candidates":
            deepcopy(
                article_consolidation_result.get(
                    "pre_resolution_hybrid_reasoning_candidates",
                    [],
                )
            ),

        "hybrid_reasoning_candidates":
            final_candidates,

        "symbolic_constraint_enforcement_records":
            deepcopy(
                article_consolidation_result.get(
                    "symbolic_constraint_enforcement_records",
                    [],
                )
            ),

        "neural_context_interpretation_records":
            deepcopy(
                article_consolidation_result.get(
                    "neural_context_interpretation_records",
                    [],
                )
            ),

        "hybrid_evidence_fusion_records":
            deepcopy(
                article_consolidation_result.get(
                    "hybrid_evidence_fusion_records",
                    [],
                )
            ),

        "contradiction_conflict_resolution_records":
            deepcopy(
                article_consolidation_result.get(
                    "contradiction_conflict_resolution_records",
                    [],
                )
            ),

        "hybrid_confidence_records":
            deepcopy(
                article_consolidation_result.get(
                    "hybrid_confidence_records",
                    [],
                )
            ),

        "reasoning_provenance_explainability_records":
            deepcopy(
                article_consolidation_result.get(
                    "reasoning_provenance_explainability_records",
                    [],
                )
            ),

        "duplicate_redundant_hybrid_resolution_records":
            deepcopy(
                article_consolidation_result.get(
                    "duplicate_redundant_hybrid_resolution_records",
                    [],
                )
            ),

        "canonical_hybrid_candidate_ids":
            deepcopy(
                canonical_candidate_ids
            ),

        "redundant_hybrid_candidate_ids":
            deepcopy(
                redundant_candidate_ids
            ),

        "article_level_hybrid_consolidation":
            deepcopy(
                article_consolidation
            ),

        "final_hybrid_candidate_records":
            final_candidate_records,

        "final_symbolic_neural_hybrid_intelligence":
            final_article_record,

        "unaligned_symbolic_evidence_ids":
            deepcopy(
                article_consolidation_result.get(
                    "unaligned_symbolic_evidence_ids",
                    [],
                )
            ),

        "unaligned_neural_semantic_evidence_ids":
            deepcopy(
                article_consolidation_result.get(
                    "unaligned_neural_semantic_evidence_ids",
                    [],
                )
            ),

        "article_context_boundary":
            deepcopy(
                article_context_boundary
            ),

        "final_result_summary": {
            "canonical_candidate_count":
                len(
                    canonical_candidate_ids
                ),

            "redundant_candidate_count":
                len(
                    redundant_candidate_ids
                ),

            "agreement_candidate_count":
                len(
                    agreement_ids
                ),

            "governed_conflict_candidate_count":
                len(
                    conflict_ids
                ),

            "unresolved_candidate_count":
                len(
                    unresolved_ids
                ),

            "abstention_candidate_count":
                len(
                    abstention_ids
                ),

            "final_candidate_record_count":
                len(
                    final_candidate_records
                ),

            "all_canonical_candidates_finalized":
                len(
                    final_candidate_records
                )
                == len(
                    canonical_candidate_ids
                ),

            "hard_symbolic_authority_preserved":
                True,

            "provenance_preserved":
                True,

            "redundancy_lineage_preserved":
                True,

            "article_consolidation_preserved":
                True,

            "new_reasoning_performed":
                False,

            "cross_candidate_synthesis_performed":
                False,

            "conflict_resolution_reperformed":
                False,

            "confidence_recalculated":
                False,

            "duplicate_resolution_reperformed":
                False,

            "new_article_fact_inferred":
                False,
        },

        "processing_boundaries": {
            "final_symbolic_neural_hybrid_result_prepared":
                True,

            "final_packaging_only":
                True,

            "canonical_candidate_set_preserved":
                True,

            "article_level_consolidation_preserved":
                True,

            "candidate_provenance_preserved":
                True,

            "redundancy_lineage_preserved":
                True,

            "hard_symbolic_authority_preserved":
                True,

            "semantic_override_allowed":
                False,

            "new_reasoning_performed":
                False,

            "cross_candidate_synthesis_performed":
                False,

            "evidence_rewrite_performed":
                False,

            "candidate_meaning_change_performed":
                False,

            "conflict_resolution_reperformed":
                False,

            "confidence_recalculation_performed":
                False,

            "duplicate_resolution_reperformed":
                False,

            "article_consolidation_reperformed":
                False,

            "new_hybrid_fact_inference_performed":
                False,

            "new_article_fact_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "symbolic_neural_hybrid_certification",
    }


