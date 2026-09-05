from __future__ import annotations

from collections.abc import Mapping
from typing import Any


CAUSAL_INTELLIGENCE_VERSION = "causal_intelligence_v1"


class CausalIntelligenceError(ValueError):
    """Raised when canonical Causal Intelligence contracts are violated."""


def validate_causal_intelligence_intake_v1(
    certified_relational_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate the canonical Phase 4.6.8 Causal Intelligence intake.

    Input must be the certified output of Phase 4.6.7 Relational Intelligence.

    This stage performs validation only. It does NOT:
    - infer cause-effect relationships,
    - interpret causal language,
    - establish factual truth,
    - use external authority,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        certified_relational_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "certified_relational_result must be a mapping."
        )

    if (
        certified_relational_result.get(
            "schema_version"
        )
        != "certified_relational_intelligence_result_v1"
    ):
        raise CausalIntelligenceError(
            "Phase 4.6.8 requires certified_relational_intelligence_result_v1."
        )

    if (
        certified_relational_result.get(
            "status"
        )
        != "RELATIONAL_INTELLIGENCE_CERTIFIED"
    ):
        raise CausalIntelligenceError(
            "Relational Intelligence must be certified before Causal Intelligence."
        )

    if (
        certified_relational_result.get(
            "phase"
        )
        != "4.6.7"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence intake requires Phase 4.6.7 output."
        )

    if (
        certified_relational_result.get(
            "patch"
        )
        != "4.6.7O"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence intake requires canonical 4.6.7O output."
        )

    if (
        certified_relational_result.get(
            "next_stage"
        )
        != "causal_intelligence"
    ):
        raise CausalIntelligenceError(
            "Certified Relational Intelligence must hand off to causal_intelligence."
        )

    if (
        certified_relational_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence intake must remain article-local and transient."
        )

    certification = dict(
        certified_relational_result.get(
            "certification"
        )
        or {}
    )

    if (
        certification.get(
            "performed"
        )
        is not True
        or certification.get(
            "certified"
        )
        is not True
        or certification.get(
            "certification_stage"
        )
        != "4.6.7O"
    ):
        raise CausalIntelligenceError(
            "Relational Intelligence certification state is invalid."
        )

    if (
        certification.get(
            "causal_reasoning_performed"
        )
        is not False
    ):
        raise CausalIntelligenceError(
            "Upstream Relational Intelligence must not perform causal reasoning."
        )

    if (
        certification.get(
            "truth_assessment_performed"
        )
        is not False
    ):
        raise CausalIntelligenceError(
            "Upstream Relational Intelligence must not assess factual truth."
        )

    if (
        certification.get(
            "external_authority_check_performed"
        )
        is not False
    ):
        raise CausalIntelligenceError(
            "Upstream Relational Intelligence must not use external authority."
        )

    relational_boundaries = dict(
        certified_relational_result.get(
            "relational_boundaries"
        )
        or {}
    )

    if (
        relational_boundaries.get(
            "article_local_only"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence requires article-local Relational Intelligence."
        )

    required_false_boundaries = (
        "truth_verified",
        "truth_assessment_performed",
        "causal_reasoning_performed",
        "external_authority_checked",
        "fuzzy_similarity_performed",
        "new_relation_inference_performed",
        "linking_decisions_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for boundary_name in required_false_boundaries:
        if (
            relational_boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Invalid upstream relational boundary: "
                + boundary_name
            )

    if (
        relational_boundaries.get(
            "causal_sensitive_relations_deferred_to"
        )
        != "4.6.8"
    ):
        raise CausalIntelligenceError(
            "Causal-sensitive relations must be explicitly deferred to Phase 4.6.8."
        )

    identity = dict(
        certified_relational_result.get(
            "article_identity"
        )
        or {}
    )

    required_identity_fields = (
        "article_id",
        "workspace_id",
        "source_type",
        "content_hash",
        "body_ref",
    )

    for field in required_identity_fields:
        if not str(
            identity.get(
                field
            )
            or ""
        ).strip():
            raise CausalIntelligenceError(
                "Missing required article identity field: "
                + field
            )

    consolidated_relations = list(
        certified_relational_result.get(
            "consolidated_relations"
        )
        or []
    )

    causal_sensitive_relations = []

    for relation in consolidated_relations:
        if not isinstance(
            relation,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every consolidated relational record must be a mapping."
            )

        if (
            relation.get(
                "truth_assessed"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Relational records entering Causal Intelligence must remain unverified."
            )

        if (
            relation.get(
                "causal_reasoning_performed"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Relational records entering Causal Intelligence must not already contain causal reasoning."
            )

        if (
            relation.get(
                "external_authority_checked"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Relational records entering Causal Intelligence must not contain external-authority conclusions."
            )

        if (
            relation.get(
                "causal_sensitive_relation"
            )
            is True
        ):
            if (
                relation.get(
                    "causal_interpretation_deferred"
                )
                is not True
            ):
                raise CausalIntelligenceError(
                    "Every causal-sensitive relational record must remain explicitly deferred."
                )

            causal_sensitive_relations.append(
                dict(
                    relation
                )
            )

    relational_summary = dict(
        certified_relational_result.get(
            "article_relational_summary"
        )
        or {}
    )

    expected_causal_sensitive_count = (
        relational_summary.get(
            "causal_sensitive_relation_count"
        )
    )

    if (
        expected_causal_sensitive_count
        is not None
        and expected_causal_sensitive_count
        != len(
            causal_sensitive_relations
        )
    ):
        raise CausalIntelligenceError(
            "Causal-sensitive relation accounting does not match the certified relational summary."
        )

    return {
        "schema_version":
            "causal_intelligence_intake_v1",

        "causal_intelligence_version":
            CAUSAL_INTELLIGENCE_VERSION,

        "phase":
            "4.6.8",

        "patch":
            "4.6.8B",

        "status":
            "CAUSAL_INTELLIGENCE_INTAKE_ACCEPTED",

        "article_identity":
            identity,

        "certified_relational_result":
            dict(
                certified_relational_result
            ),

        "consolidated_relations":
            [
                dict(
                    relation
                )
                for relation in consolidated_relations
            ],

        "causal_sensitive_relations":
            causal_sensitive_relations,

        "intake_summary": {
            "consolidated_relation_count":
                len(
                    consolidated_relations
                ),

            "causal_sensitive_relation_count":
                len(
                    causal_sensitive_relations
                ),

            "zero_causal_sensitive_relations_allowed":
                True,

            "article_local_only":
                True,
        },

        "causal_boundaries": {
            "article_local_only":
                True,

            "causal_interpretation_performed":
                False,

            "cause_effect_extraction_performed":
                False,

            "causal_inference_performed":
                False,

            "truth_verified":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_checked":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "linking_decisions_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "causal_claim_unit_preparation",
    }



def build_causal_claim_units_v1(
    certified_relational_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build canonical Phase 4.6.8 Causal Claim Units from
    certified Phase 4.6.7 Relational Intelligence.

    This is a one-to-one structural preparation stage.

    It does NOT:
    - reparse the article body,
    - interpret causal language,
    - extract cause-effect pairs,
    - infer causation,
    - establish factual truth,
    - use external authority,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    intake = validate_causal_intelligence_intake_v1(
        certified_relational_result
    )

    if (
        intake.get(
            "status"
        )
        != "CAUSAL_INTELLIGENCE_INTAKE_ACCEPTED"
    ):
        raise CausalIntelligenceError(
            "Canonical Causal Intelligence intake was not accepted."
        )

    identity = dict(
        certified_relational_result.get(
            "article_identity"
        )
        or {}
    )

    article_id = str(
        identity.get(
            "article_id"
        )
        or ""
    )

    relational_units = list(
        certified_relational_result.get(
            "relational_claim_units"
        )
        or []
    )

    if not article_id:
        raise CausalIntelligenceError(
            "Certified relational article_id is required."
        )

    causal_units = []
    causal_sections = []

    seen_causal_ids = set()
    seen_relational_ids = set()
    seen_statement_ids = set()
    seen_sentence_ids = set()

    previous_global_index = None

    units_by_section = {}
    section_metadata = {}

    for relational_unit in relational_units:
        if not isinstance(
            relational_unit,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every certified Relational Claim Unit must be a mapping."
            )

        relational_claim_unit_id = str(
            relational_unit.get(
                "relational_claim_unit_id"
            )
            or ""
        )

        statement_id = str(
            relational_unit.get(
                "statement_evidence_id"
            )
            or ""
        )

        sentence_id = str(
            relational_unit.get(
                "sentence_id"
            )
            or ""
        )

        section_id = str(
            relational_unit.get(
                "section_id"
            )
            or ""
        )

        if not relational_claim_unit_id:
            raise CausalIntelligenceError(
                "Relational Claim Unit ID is required."
            )

        if not relational_claim_unit_id.startswith(
            "relational_claim_"
        ):
            raise CausalIntelligenceError(
                "Unexpected Relational Claim Unit ID format."
            )

        if not statement_id:
            raise CausalIntelligenceError(
                "statement_evidence_id is required."
            )

        if not sentence_id:
            raise CausalIntelligenceError(
                "sentence_id is required."
            )

        if not section_id:
            raise CausalIntelligenceError(
                "section_id is required."
            )

        if relational_claim_unit_id in seen_relational_ids:
            raise CausalIntelligenceError(
                "Duplicate Relational Claim Unit ID."
            )

        if statement_id in seen_statement_ids:
            raise CausalIntelligenceError(
                "Duplicate statement_evidence_id."
            )

        if sentence_id in seen_sentence_ids:
            raise CausalIntelligenceError(
                "Duplicate sentence_id."
            )

        if (
            relational_unit.get(
                "article_id"
            )
            != article_id
        ):
            raise CausalIntelligenceError(
                "Relational Claim Unit article identity mismatch."
            )

        global_index = relational_unit.get(
            "sentence_global_index"
        )

        article_position = relational_unit.get(
            "article_position"
        )

        if not isinstance(
            global_index,
            int,
        ):
            raise CausalIntelligenceError(
                "sentence_global_index must be an integer."
            )

        if not isinstance(
            article_position,
            int,
        ):
            raise CausalIntelligenceError(
                "article_position must be an integer."
            )

        if (
            previous_global_index is not None
            and global_index <= previous_global_index
        ):
            raise CausalIntelligenceError(
                "Certified Relational Claim Units are not "
                "in canonical sentence order."
            )

        relational_state = dict(
            relational_unit.get(
                "relational_analysis_state"
            )
            or {}
        )

        required_complete_relational_stages = (
            "relational_signal_interpretation",
            "subject_relation_object_extraction",
            "entity_concept_grounding",
            "relation_normalization",
            "directionality_resolution",
            "same_sentence_validation",
            "cross_sentence_validation",
            "relation_evidence_assessment",
            "duplicate_relation_resolution",
        )

        for stage_name in required_complete_relational_stages:
            if (
                relational_state.get(
                    stage_name
                )
                != "COMPLETE"
            ):
                raise CausalIntelligenceError(
                    "Relational Claim Unit analysis is incomplete at "
                    + stage_name
                    + "."
                )

        upstream_boundaries = dict(
            relational_unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            upstream_boundaries.get(
                "causal_reasoning_performed"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Upstream Relational Claim Unit already contains causal reasoning."
            )

        if (
            upstream_boundaries.get(
                "truth_assessment_performed"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Upstream Relational Claim Unit already contains truth assessment."
            )

        if (
            upstream_boundaries.get(
                "external_authority_check_performed"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Upstream Relational Claim Unit already contains external-authority reasoning."
            )

        causal_claim_unit_id = (
            "causal_claim_"
            + relational_claim_unit_id[
                len("relational_claim_"):
            ]
        )

        if causal_claim_unit_id in seen_causal_ids:
            raise CausalIntelligenceError(
                "Duplicate Causal Claim Unit ID."
            )

        causal_unit = {
            "causal_claim_unit_id":
                causal_claim_unit_id,

            "upstream_relational_claim_unit_id":
                relational_claim_unit_id,

            "upstream_logical_claim_unit_id":
                relational_unit.get(
                    "upstream_logical_claim_unit_id"
                ),

            "statement_evidence_id":
                statement_id,

            "sentence_id":
                sentence_id,

            "article_id":
                article_id,

            "section_id":
                section_id,

            "section_evidence_unit_id":
                relational_unit.get(
                    "section_evidence_unit_id"
                ),

            "section_index":
                relational_unit.get(
                    "section_index"
                ),

            "section_title":
                relational_unit.get(
                    "section_title"
                ),

            "heading_level":
                relational_unit.get(
                    "heading_level"
                ),

            "block_id":
                relational_unit.get(
                    "block_id"
                ),

            "paragraph_id":
                relational_unit.get(
                    "paragraph_id"
                ),

            "block_type":
                relational_unit.get(
                    "block_type"
                ),

            "block_index":
                relational_unit.get(
                    "block_index"
                ),

            "sentence_index":
                relational_unit.get(
                    "sentence_index"
                ),

            "sentence_global_index":
                global_index,

            "article_position":
                article_position,

            "claim_index_in_section":
                relational_unit.get(
                    "claim_index_in_section"
                ),

            "text":
                relational_unit.get(
                    "text"
                ),

            "word_count":
                relational_unit.get(
                    "word_count"
                ),

            "character_count":
                relational_unit.get(
                    "character_count"
                ),

            "statement_form":
                relational_unit.get(
                    "statement_form"
                ),

            "canonical_claim_candidate":
                relational_unit.get(
                    "canonical_claim_candidate"
                )
                is True,

            "evidence_context":
                dict(
                    relational_unit.get(
                        "evidence_context"
                    )
                    or {}
                ),

            "upstream_relational_analysis_state":
                relational_state,

            "upstream_relational_processing_boundaries":
                upstream_boundaries,

            "causal_analysis_state": {
                "causal_signal_interpretation":
                    "PENDING",

                "cause_effect_candidate_extraction":
                    "PENDING",

                "entity_concept_grounding":
                    "PENDING",

                "causal_relation_normalization":
                    "PENDING",

                "cause_effect_orientation":
                    "PENDING",

                "same_sentence_causal_validation":
                    "PENDING",

                "cross_sentence_causal_validation":
                    "PENDING",

                "causal_evidence_assessment":
                    "PENDING",

                "duplicate_causal_resolution":
                    "PENDING",
            },

            "processing_boundaries": {
                "article_local_only":
                    True,

                "causal_claim_unit_prepared":
                    True,

                "article_body_reparsed":
                    False,

                "causal_signal_interpretation_performed":
                    False,

                "cause_effect_extraction_performed":
                    False,

                "causal_inference_performed":
                    False,

                "truth_assessment_performed":
                    False,

                "external_authority_check_performed":
                    False,

                "quantitative_reasoning_performed":
                    False,

                "temporal_reasoning_performed":
                    False,

                "phrase_selected_for_linking":
                    False,

                "target_selected":
                    False,

                "url_selected":
                    False,

                "link_type_selected":
                    False,

                "highlight_color_selected":
                    False,

                "semantic_memory_write_performed":
                    False,

                "persistence_performed":
                    False,
            },
        }

        causal_units.append(
            causal_unit
        )

        units_by_section.setdefault(
            section_id,
            [],
        ).append(
            causal_unit
        )

        if section_id not in section_metadata:
            section_metadata[
                section_id
            ] = {
                "section_id":
                    section_id,

                "section_index":
                    relational_unit.get(
                        "section_index"
                    ),

                "section_title":
                    relational_unit.get(
                        "section_title"
                    ),

                "heading_level":
                    relational_unit.get(
                        "heading_level"
                    ),
            }

        seen_causal_ids.add(
            causal_claim_unit_id
        )

        seen_relational_ids.add(
            relational_claim_unit_id
        )

        seen_statement_ids.add(
            statement_id
        )

        seen_sentence_ids.add(
            sentence_id
        )

        previous_global_index = (
            global_index
        )

    ordered_section_ids = []

    for unit in causal_units:
        section_id = str(
            unit.get(
                "section_id"
            )
            or ""
        )

        if section_id not in ordered_section_ids:
            ordered_section_ids.append(
                section_id
            )

    for section_id in ordered_section_ids:
        metadata = dict(
            section_metadata.get(
                section_id
            )
            or {}
        )

        section_units = list(
            units_by_section.get(
                section_id,
                []
            )
        )

        causal_sections.append({
            **metadata,

            "upstream_relational_claim_count":
                len(
                    section_units
                ),

            "causal_claim_unit_count":
                len(
                    section_units
                ),

            "causal_claim_units":
                section_units,
        })

    if (
        len(
            causal_units
        )
        != len(
            relational_units
        )
    ):
        raise CausalIntelligenceError(
            "Causal Claim Unit construction must remain "
            "one-to-one with Relational Claim Units."
        )

    return {
        "schema_version":
            "causal_claim_units_v1",

        "causal_intelligence_version":
            CAUSAL_INTELLIGENCE_VERSION,

        "phase":
            "4.6.8",

        "patch":
            "4.6.8C",

        "status":
            "CAUSAL_CLAIM_UNITS_PREPARED",

        "article_identity":
            identity,

        "relational_claim_unit_count":
            len(
                relational_units
            ),

        "causal_claim_unit_count":
            len(
                causal_units
            ),

        "section_count":
            len(
                causal_sections
            ),

        "causal_sections":
            causal_sections,

        "causal_claim_units":
            causal_units,

        "causal_sensitive_relations":
            list(
                intake.get(
                    "causal_sensitive_relations"
                )
                or []
            ),

        "construction_summary": {
            "source_relational_claim_unit_count":
                len(
                    relational_units
                ),

            "causal_claim_unit_count":
                len(
                    causal_units
                ),

            "one_to_one_relational_mapping":
                (
                    len(
                        causal_units
                    )
                    == len(
                        relational_units
                    )
                ),

            "canonical_order_preserved":
                True,

            "canonical_text_preserved":
                True,

            "evidence_context_preserved":
                True,

            "relational_context_preserved":
                True,

            "article_body_reparsed":
                False,

            "causal_signals_interpreted":
                False,

            "cause_effect_relations_inferred":
                False,
        },

        "processing_boundaries": {
            "article_body_reparsed":
                False,

            "causal_claim_units_prepared":
                True,

            "causal_signal_interpretation_performed":
                False,

            "cause_effect_extraction_performed":
                False,

            "causal_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "linking_decisions_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "explicit_causal_signal_interpretation",
    }



def interpret_explicit_causal_signals_v1(
    causal_claim_units_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Interpret explicit article-local causal lexical signals.

    This stage identifies and classifies causal wording only.

    It does NOT:
    - extract cause-effect endpoints,
    - infer causation from proximity,
    - establish factual truth,
    - use external authority,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        causal_claim_units_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "causal_claim_units_result must be a mapping."
        )

    if (
        causal_claim_units_result.get(
            "schema_version"
        )
        != "causal_claim_units_v1"
    ):
        raise CausalIntelligenceError(
            "Stage D requires causal_claim_units_v1."
        )

    if (
        causal_claim_units_result.get(
            "status"
        )
        != "CAUSAL_CLAIM_UNITS_PREPARED"
    ):
        raise CausalIntelligenceError(
            "Causal Claim Units must be prepared before Stage D."
        )

    if (
        causal_claim_units_result.get(
            "phase"
        )
        != "4.6.8"
    ):
        raise CausalIntelligenceError(
            "Stage D requires Phase 4.6.8 input."
        )

    if (
        causal_claim_units_result.get(
            "patch"
        )
        != "4.6.8C"
    ):
        raise CausalIntelligenceError(
            "Stage D requires canonical 4.6.8C input."
        )

    if (
        causal_claim_units_result.get(
            "next_stage"
        )
        != "explicit_causal_signal_interpretation"
    ):
        raise CausalIntelligenceError(
            "Stage C must hand off to explicit_causal_signal_interpretation."
        )

    if (
        causal_claim_units_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence must remain transient."
        )

    signal_specs = (
        (
            "EXPLICIT_CAUSE",
            "STRONG",
            re.compile(
                r"\bcaus(?:e|es|ed|ing)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "BECAUSE",
            "STRONG",
            re.compile(
                r"\bbecause(?:\s+of)?\b",
                re.IGNORECASE,
            ),
        ),
        (
            "LEADS_TO",
            "STRONG",
            re.compile(
                r"\blead(?:s|ing)?\s+to\b",
                re.IGNORECASE,
            ),
        ),
        (
            "RESULTS_IN",
            "STRONG",
            re.compile(
                r"\bresult(?:s|ed|ing)?\s+in\b",
                re.IGNORECASE,
            ),
        ),
        (
            "RESULTS_FROM",
            "STRONG",
            re.compile(
                r"\bresult(?:s|ed|ing)?\s+from\b",
                re.IGNORECASE,
            ),
        ),
        (
            "DUE_TO",
            "STRONG",
            re.compile(
                r"\bdue\s+to\b",
                re.IGNORECASE,
            ),
        ),
        (
            "CONTRIBUTES_TO",
            "STRONG",
            re.compile(
                r"\bcontribut(?:e|es|ed|ing)\s+to\b",
                re.IGNORECASE,
            ),
        ),
        (
            "RESPONSIBLE_FOR",
            "STRONG",
            re.compile(
                r"\bresponsible\s+for\b",
                re.IGNORECASE,
            ),
        ),
        (
            "TRIGGERS",
            "STRONG",
            re.compile(
                r"\btrigger(?:s|ed|ing)?\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AFFECTS",
            "CAUSAL_SENSITIVE",
            re.compile(
                r"\baffect(?:s|ed|ing)?\b",
                re.IGNORECASE,
            ),
        ),
        (
            "INFLUENCES",
            "CAUSAL_SENSITIVE",
            re.compile(
                r"\binfluenc(?:e|es|ed|ing)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "IMPACTS",
            "CAUSAL_SENSITIVE",
            re.compile(
                r"\bimpact(?:s|ed|ing)?\b",
                re.IGNORECASE,
            ),
        ),
        (
            "DEPENDS_ON",
            "CAUSAL_SENSITIVE",
            re.compile(
                r"\bdepend(?:s|ed|ing)?\s+on\b",
                re.IGNORECASE,
            ),
        ),
        (
            "PREVENTS",
            "CAUSAL_SENSITIVE",
            re.compile(
                r"\bprevent(?:s|ed|ing)?\b",
                re.IGNORECASE,
            ),
        ),
        (
            "INCREASES",
            "CAUSAL_SENSITIVE",
            re.compile(
                r"\bincreas(?:e|es|ed|ing)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "DECREASES",
            "CAUSAL_SENSITIVE",
            re.compile(
                r"\bdecreas(?:e|es|ed|ing)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "REDUCES",
            "CAUSAL_SENSITIVE",
            re.compile(
                r"\breduc(?:e|es|ed|ing)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "IMPROVES",
            "CAUSAL_SENSITIVE",
            re.compile(
                r"\bimprov(?:e|es|ed|ing)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "WORSENS",
            "CAUSAL_SENSITIVE",
            re.compile(
                r"\bworsen(?:s|ed|ing)?\b",
                re.IGNORECASE,
            ),
        ),
        (
            "PRODUCES",
            "CAUSAL_SENSITIVE",
            re.compile(
                r"\bproduc(?:e|es|ed|ing)\b",
                re.IGNORECASE,
            ),
        ),
    )

    cause_for_concern_pattern = re.compile(
        r"\bcause\s+for\s+concern\b",
        re.IGNORECASE,
    )

    created_by_pattern = re.compile(
        r"\bcreat(?:ed|ing)\s+by\b",
        re.IGNORECASE,
    )

    source_units = list(
        causal_claim_units_result.get(
            "causal_claim_units"
        )
        or []
    )

    interpreted_units = []
    interpreted_by_id = {}

    total_signal_count = 0
    strong_signal_count = 0
    sensitive_signal_count = 0
    excluded_noise_count = 0
    units_with_signals = 0

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every Causal Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "causal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "causal_signal_interpretation"
            )
            != "PENDING"
        ):
            raise CausalIntelligenceError(
                "Causal signal interpretation must be PENDING before Stage D."
            )

        if (
            state.get(
                "cause_effect_candidate_extraction"
            )
            != "PENDING"
        ):
            raise CausalIntelligenceError(
                "Cause-effect extraction must remain PENDING during Stage D."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "causal_claim_unit_prepared"
            )
            is not True
        ):
            raise CausalIntelligenceError(
                "Causal Claim Unit preparation boundary is incomplete."
            )

        if (
            boundaries.get(
                "causal_inference_performed"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Stage D cannot accept prior causal inference."
            )

        source_text = str(
            unit.get(
                "text"
            )
            or ""
        )

        signals = []
        exclusions = []

        if cause_for_concern_pattern.search(
            source_text
        ):
            exclusions.append({
                "signal":
                    "CAUSE_FOR_CONCERN",

                "classification":
                    "NON_CAUSAL_IDIOM",

                "candidate_eligible":
                    False,
            })

        if created_by_pattern.search(
            source_text
        ):
            exclusions.append({
                "signal":
                    "CREATED_BY",

                "classification":
                    "NON_CAUSAL_CREATION_ATTRIBUTION",

                "candidate_eligible":
                    False,
            })

        for (
            signal_type,
            strength_class,
            pattern,
        ) in signal_specs:
            matches = list(
                pattern.finditer(
                    source_text
                )
            )

            for match in matches:
                matched_text = match.group(
                    0
                )

                if (
                    signal_type
                    == "EXPLICIT_CAUSE"
                    and cause_for_concern_pattern.search(
                        source_text
                    )
                    and re.search(
                        r"\bcause\b",
                        matched_text,
                        re.IGNORECASE,
                    )
                ):
                    continue

                signals.append({
                    "signal_type":
                        signal_type,

                    "signal_strength_class":
                        strength_class,

                    "matched_text":
                        matched_text,

                    "character_start":
                        match.start(),

                    "character_end":
                        match.end(),

                    "article_asserted_signal":
                        True,

                    "cause_effect_endpoints_extracted":
                        False,

                    "causal_inference_performed":
                        False,

                    "truth_verified":
                        False,
                })

        unit_total = len(
            signals
        )

        unit_strong = sum(
            1
            for signal in signals
            if signal.get(
                "signal_strength_class"
            )
            == "STRONG"
        )

        unit_sensitive = sum(
            1
            for signal in signals
            if signal.get(
                "signal_strength_class"
            )
            == "CAUSAL_SENSITIVE"
        )

        total_signal_count += (
            unit_total
        )

        strong_signal_count += (
            unit_strong
        )

        sensitive_signal_count += (
            unit_sensitive
        )

        excluded_noise_count += len(
            exclusions
        )

        if unit_total:
            units_with_signals += 1

        interpreted_state = dict(
            state
        )

        interpreted_state[
            "causal_signal_interpretation"
        ] = "COMPLETE"

        interpreted_boundaries = dict(
            boundaries
        )

        interpreted_boundaries[
            "causal_signal_interpretation_performed"
        ] = True

        interpreted_boundaries[
            "cause_effect_extraction_performed"
        ] = False

        interpreted_boundaries[
            "causal_inference_performed"
        ] = False

        interpreted_boundaries[
            "truth_assessment_performed"
        ] = False

        interpreted_boundaries[
            "external_authority_check_performed"
        ] = False

        interpreted_unit = dict(
            unit
        )

        interpreted_unit.update({
            "causal_signals":
                signals,

            "causal_signal_exclusions":
                exclusions,

            "causal_signal_count":
                unit_total,

            "strong_causal_signal_count":
                unit_strong,

            "causal_sensitive_signal_count":
                unit_sensitive,

            "has_explicit_causal_signal":
                unit_total > 0,

            "causal_signal_interpretation_scope":
                "ARTICLE_LOCAL_LEXICAL_AND_CONTEXTUAL_SIGNAL_ONLY",

            "causal_analysis_state":
                interpreted_state,

            "processing_boundaries":
                interpreted_boundaries,
        })

        interpreted_units.append(
            interpreted_unit
        )

        interpreted_by_id[
            interpreted_unit.get(
                "causal_claim_unit_id"
            )
        ] = interpreted_unit

    interpreted_sections = []

    for section in (
        causal_claim_units_result.get(
            "causal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "causal_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "causal_claim_unit_id"
            )

            resolved_unit = (
                interpreted_by_id.get(
                    unit_id
                )
            )

            if resolved_unit is None:
                raise CausalIntelligenceError(
                    "Causal section references an unknown claim unit."
                )

            section_units.append(
                resolved_unit
            )

        interpreted_sections.append({
            **dict(
                section
            ),

            "causal_claim_units":
                section_units,

            "causal_signal_unit_count":
                sum(
                    1
                    for unit in section_units
                    if unit.get(
                        "has_explicit_causal_signal"
                    )
                    is True
                ),

            "causal_signal_count":
                sum(
                    int(
                        unit.get(
                            "causal_signal_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),
        })

    result = dict(
        causal_claim_units_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "causal_signal_interpretation_performed"
    ] = True

    result_boundaries[
        "cause_effect_extraction_performed"
    ] = False

    result_boundaries[
        "causal_inference_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result.update({
        "schema_version":
            "causal_signal_interpretation_v1",

        "patch":
            "4.6.8D",

        "status":
            "CAUSAL_SIGNAL_INTERPRETATION_COMPLETE",

        "causal_sections":
            interpreted_sections,

        "causal_claim_units":
            interpreted_units,

        "causal_signal_summary": {
            "claim_unit_count":
                len(
                    interpreted_units
                ),

            "units_with_causal_signals":
                units_with_signals,

            "total_causal_signal_count":
                total_signal_count,

            "strong_causal_signal_count":
                strong_signal_count,

            "causal_sensitive_signal_count":
                sensitive_signal_count,

            "excluded_noncausal_lexical_noise_count":
                excluded_noise_count,

            "zero_signal_units_allowed":
                True,

            "cause_effect_endpoints_extracted":
                False,

            "causal_inference_performed":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "cause_effect_candidate_extraction",
    })

    return result



def extract_cause_effect_candidates_v1(
    causal_signal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Extract conservative article-local cause-effect candidates from
    explicitly interpreted causal signals.

    This stage extracts textual endpoint candidates only.

    It does NOT:
    - prove causation,
    - infer causation from proximity alone,
    - ground entities or concepts,
    - normalize final causal relation types,
    - establish factual truth,
    - use external authority,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import hashlib
    import re

    if not isinstance(
        causal_signal_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "causal_signal_result must be a mapping."
        )

    if (
        causal_signal_result.get(
            "schema_version"
        )
        != "causal_signal_interpretation_v1"
    ):
        raise CausalIntelligenceError(
            "Stage E requires causal_signal_interpretation_v1."
        )

    if (
        causal_signal_result.get(
            "status"
        )
        != "CAUSAL_SIGNAL_INTERPRETATION_COMPLETE"
    ):
        raise CausalIntelligenceError(
            "Causal signal interpretation must be complete."
        )

    if (
        causal_signal_result.get(
            "phase"
        )
        != "4.6.8"
    ):
        raise CausalIntelligenceError(
            "Stage E requires Phase 4.6.8 input."
        )

    if (
        causal_signal_result.get(
            "patch"
        )
        != "4.6.8D"
    ):
        raise CausalIntelligenceError(
            "Stage E requires canonical 4.6.8D input."
        )

    if (
        causal_signal_result.get(
            "next_stage"
        )
        != "cause_effect_candidate_extraction"
    ):
        raise CausalIntelligenceError(
            "Stage D must hand off to cause_effect_candidate_extraction."
        )

    if (
        causal_signal_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence must remain transient."
        )

    def clean_endpoint(
        value: str,
    ) -> str:
        cleaned = str(
            value
            or ""
        ).strip()

        cleaned = re.sub(
            r"^[,;:\-\s]+",
            "",
            cleaned,
        )

        cleaned = re.sub(
            r"[,;:\-\s]+$",
            "",
            cleaned,
        )

        return cleaned.strip()

    def build_candidate_id(
        unit_id: str,
        signal_type: str,
        cause_text: str,
        effect_text: str,
        ordinal: int,
    ) -> str:
        raw = "|".join([
            unit_id,
            signal_type,
            cause_text,
            effect_text,
            str(
                ordinal
            ),
        ])

        return (
            "causal_candidate_"
            + hashlib.sha256(
                raw.encode(
                    "utf-8"
                )
            ).hexdigest()[:24]
        )

    source_units = list(
        causal_signal_result.get(
            "causal_claim_units"
        )
        or []
    )

    extracted_units = []
    extracted_by_id = {}
    all_candidates = []

    units_with_candidates = 0
    rejected_signal_count = 0

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every Stage-D Causal Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "causal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "causal_signal_interpretation"
            )
            != "COMPLETE"
        ):
            raise CausalIntelligenceError(
                "Causal signal interpretation must be COMPLETE before Stage E."
            )

        if (
            state.get(
                "cause_effect_candidate_extraction"
            )
            != "PENDING"
        ):
            raise CausalIntelligenceError(
                "Cause-effect candidate extraction must be PENDING before Stage E."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "causal_signal_interpretation_performed"
            )
            is not True
        ):
            raise CausalIntelligenceError(
                "Stage-D interpretation boundary is incomplete."
            )

        if (
            boundaries.get(
                "causal_inference_performed"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Stage E cannot accept prior causal inference."
            )

        unit_id = str(
            unit.get(
                "causal_claim_unit_id"
            )
            or ""
        )

        sentence_text = str(
            unit.get(
                "text"
            )
            or ""
        ).strip()

        if not unit_id:
            raise CausalIntelligenceError(
                "Causal Claim Unit ID is required."
            )

        signals = list(
            unit.get(
                "causal_signals"
            )
            or []
        )

        unit_candidates = []
        unit_rejections = []

        for signal_index, signal in enumerate(
            signals,
            start=1,
        ):
            if not isinstance(
                signal,
                Mapping,
            ):
                raise CausalIntelligenceError(
                    "Every causal signal must be a mapping."
                )

            signal_type = str(
                signal.get(
                    "signal_type"
                )
                or ""
            )

            start = signal.get(
                "character_start"
            )

            end = signal.get(
                "character_end"
            )

            if (
                not isinstance(
                    start,
                    int,
                )
                or not isinstance(
                    end,
                    int,
                )
                or start < 0
                or end <= start
                or end > len(
                    sentence_text
                )
            ):
                raise CausalIntelligenceError(
                    "Causal signal character span is invalid."
                )

            before = clean_endpoint(
                sentence_text[
                    :start
                ]
            )

            after = clean_endpoint(
                sentence_text[
                    end:
                ]
            )

            cause_text = ""
            effect_text = ""
            extraction_pattern = ""
            candidate_relation = ""
            extraction_safe = False

            if signal_type == "BECAUSE":
                if (
                    before
                    and after
                ):
                    effect_text = before
                    cause_text = after
                    extraction_pattern = (
                        "EFFECT_BECAUSE_CAUSE"
                    )
                    candidate_relation = (
                        "CAUSES_OR_EXPLAINS"
                    )
                    extraction_safe = True

            elif signal_type == "DUE_TO":
                if (
                    before
                    and after
                ):
                    effect_text = before
                    cause_text = after
                    extraction_pattern = (
                        "EFFECT_DUE_TO_CAUSE"
                    )
                    candidate_relation = (
                        "CAUSES_OR_CONTRIBUTES_TO"
                    )
                    extraction_safe = True

            elif signal_type == "RESULTS_FROM":
                if (
                    before
                    and after
                ):
                    effect_text = before
                    cause_text = after
                    extraction_pattern = (
                        "EFFECT_RESULTS_FROM_CAUSE"
                    )
                    candidate_relation = (
                        "CAUSES"
                    )
                    extraction_safe = True

            elif signal_type in {
                "LEADS_TO",
                "RESULTS_IN",
                "CONTRIBUTES_TO",
                "RESPONSIBLE_FOR",
                "TRIGGERS",
                "AFFECTS",
                "INFLUENCES",
                "IMPACTS",
                "PREVENTS",
                "INCREASES",
                "DECREASES",
                "REDUCES",
                "IMPROVES",
                "WORSENS",
                "PRODUCES",
            }:
                if (
                    before
                    and after
                ):
                    cause_text = before
                    effect_text = after
                    extraction_pattern = (
                        "CAUSE_SIGNAL_EFFECT"
                    )
                    candidate_relation = (
                        signal_type
                    )
                    extraction_safe = True

            elif signal_type == "DEPENDS_ON":
                if (
                    before
                    and after
                ):
                    effect_text = before
                    cause_text = after
                    extraction_pattern = (
                        "DEPENDENT_EFFECT_DEPENDS_ON_FACTOR"
                    )
                    candidate_relation = (
                        "DEPENDS_ON"
                    )
                    extraction_safe = True

            elif signal_type == "EXPLICIT_CAUSE":
                match = re.match(
                    r"^(?P<cause>.+?)\s+"
                    r"caus(?:e|es|ed)\s+"
                    r"(?P<effect>.+)$",
                    sentence_text,
                    re.IGNORECASE,
                )

                if match:
                    cause_text = clean_endpoint(
                        match.group(
                            "cause"
                        )
                    )

                    effect_text = clean_endpoint(
                        match.group(
                            "effect"
                        )
                    )

                    extraction_pattern = (
                        "EXPLICIT_CAUSE_VERB"
                    )

                    candidate_relation = (
                        "CAUSES"
                    )

                    extraction_safe = bool(
                        cause_text
                        and effect_text
                    )

            if not extraction_safe:
                unit_rejections.append({
                    "signal_type":
                        signal_type,

                    "matched_text":
                        signal.get(
                            "matched_text"
                        ),

                    "rejection_reason":
                        "SAFE_CAUSE_EFFECT_ENDPOINTS_NOT_EXTRACTABLE",

                    "candidate_created":
                        False,
                })

                rejected_signal_count += 1
                continue

            if (
                len(
                    cause_text
                )
                < 2
                or len(
                    effect_text
                )
                < 2
            ):
                unit_rejections.append({
                    "signal_type":
                        signal_type,

                    "matched_text":
                        signal.get(
                            "matched_text"
                        ),

                    "rejection_reason":
                        "EMPTY_OR_TRIVIAL_ENDPOINT",

                    "candidate_created":
                        False,
                })

                rejected_signal_count += 1
                continue

            candidate_id = build_candidate_id(
                unit_id,
                signal_type,
                cause_text,
                effect_text,
                signal_index,
            )

            candidate = {
                "causal_candidate_id":
                    candidate_id,

                "causal_claim_unit_id":
                    unit_id,

                "upstream_relational_claim_unit_id":
                    unit.get(
                        "upstream_relational_claim_unit_id"
                    ),

                "upstream_logical_claim_unit_id":
                    unit.get(
                        "upstream_logical_claim_unit_id"
                    ),

                "statement_evidence_id":
                    unit.get(
                        "statement_evidence_id"
                    ),

                "sentence_id":
                    unit.get(
                        "sentence_id"
                    ),

                "article_id":
                    unit.get(
                        "article_id"
                    ),

                "section_id":
                    unit.get(
                        "section_id"
                    ),

                "section_index":
                    unit.get(
                        "section_index"
                    ),

                "block_id":
                    unit.get(
                        "block_id"
                    ),

                "paragraph_id":
                    unit.get(
                        "paragraph_id"
                    ),

                "sentence_global_index":
                    unit.get(
                        "sentence_global_index"
                    ),

                "article_position":
                    unit.get(
                        "article_position"
                    ),

                "source_text":
                    sentence_text,

                "signal_type":
                    signal_type,

                "signal_strength_class":
                    signal.get(
                        "signal_strength_class"
                    ),

                "signal_matched_text":
                    signal.get(
                        "matched_text"
                    ),

                "signal_character_start":
                    start,

                "signal_character_end":
                    end,

                "cause_text":
                    cause_text,

                "effect_text":
                    effect_text,

                "candidate_causal_relation":
                    candidate_relation,

                "extraction_pattern":
                    extraction_pattern,

                "article_asserted_candidate":
                    True,

                "same_sentence_candidate":
                    True,

                "entity_concept_grounded":
                    False,

                "causal_relation_normalized":
                    False,

                "cause_effect_orientation_resolved":
                    False,

                "same_sentence_causal_validated":
                    False,

                "cross_sentence_causal_validated":
                    False,

                "causal_evidence_assessed":
                    False,

                "duplicate_resolution_performed":
                    False,

                "causal_inference_performed":
                    False,

                "truth_assessed":
                    False,

                "external_authority_checked":
                    False,

                "quantitative_reasoning_performed":
                    False,

                "temporal_reasoning_performed":
                    False,
            }

            unit_candidates.append(
                candidate
            )

            all_candidates.append(
                candidate
            )

        if unit_candidates:
            units_with_candidates += 1

        extracted_state = dict(
            state
        )

        extracted_state[
            "cause_effect_candidate_extraction"
        ] = "COMPLETE"

        extracted_boundaries = dict(
            boundaries
        )

        extracted_boundaries[
            "cause_effect_extraction_performed"
        ] = True

        extracted_boundaries[
            "causal_inference_performed"
        ] = False

        extracted_boundaries[
            "truth_assessment_performed"
        ] = False

        extracted_boundaries[
            "external_authority_check_performed"
        ] = False

        extracted_unit = dict(
            unit
        )

        extracted_unit.update({
            "cause_effect_candidates":
                unit_candidates,

            "cause_effect_candidate_count":
                len(
                    unit_candidates
                ),

            "cause_effect_extraction_rejections":
                unit_rejections,

            "cause_effect_extraction_rejection_count":
                len(
                    unit_rejections
                ),

            "causal_analysis_state":
                extracted_state,

            "processing_boundaries":
                extracted_boundaries,
        })

        extracted_units.append(
            extracted_unit
        )

        extracted_by_id[
            unit_id
        ] = extracted_unit

    extracted_sections = []

    for section in (
        causal_signal_result.get(
            "causal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "causal_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "causal_claim_unit_id"
            )

            resolved_unit = (
                extracted_by_id.get(
                    unit_id
                )
            )

            if resolved_unit is None:
                raise CausalIntelligenceError(
                    "Causal section references an unknown claim unit."
                )

            section_units.append(
                resolved_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "cause_effect_candidates"
                )
                or []
            )
        ]

        extracted_sections.append({
            **dict(
                section
            ),

            "causal_claim_units":
                section_units,

            "cause_effect_candidate_count":
                len(
                    section_candidates
                ),

            "cause_effect_candidates":
                section_candidates,
        })

    result = dict(
        causal_signal_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "cause_effect_extraction_performed"
    ] = True

    result_boundaries[
        "causal_inference_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result_boundaries[
        "quantitative_reasoning_performed"
    ] = False

    result_boundaries[
        "temporal_reasoning_performed"
    ] = False

    result.update({
        "schema_version":
            "causal_effect_candidates_v1",

        "patch":
            "4.6.8E",

        "status":
            "CAUSE_EFFECT_CANDIDATE_EXTRACTION_COMPLETE",

        "causal_sections":
            extracted_sections,

        "causal_claim_units":
            extracted_units,

        "cause_effect_candidates":
            all_candidates,

        "cause_effect_extraction_summary": {
            "claim_unit_count":
                len(
                    extracted_units
                ),

            "units_with_candidates":
                units_with_candidates,

            "candidate_count":
                len(
                    all_candidates
                ),

            "rejected_signal_count":
                rejected_signal_count,

            "zero_candidates_allowed":
                True,

            "same_sentence_extraction_only":
                True,

            "cross_sentence_inference_performed":
                False,

            "entity_concept_grounding_performed":
                False,

            "causal_relation_normalization_performed":
                False,

            "causal_inference_performed":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "entity_concept_grounding",
    })

    return result



def ground_causal_candidates_v1(
    causal_effect_result: Mapping[str, Any],
    entity_concept_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Ground cause/effect endpoint candidates against canonical
    Phase 4.6.2 Entity & Concept Intelligence objects.

    This stage reuses existing article-local semantic objects only.

    It does NOT:
    - create new entities or concepts,
    - perform fuzzy similarity,
    - normalize causal relations,
    - resolve final causal orientation,
    - validate causation,
    - establish factual truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import hashlib
    import re

    if not isinstance(
        causal_effect_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "causal_effect_result must be a mapping."
        )

    if not isinstance(
        entity_concept_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "entity_concept_result must be a mapping."
        )

    if (
        causal_effect_result.get(
            "schema_version"
        )
        != "causal_effect_candidates_v1"
    ):
        raise CausalIntelligenceError(
            "Stage F requires causal_effect_candidates_v1."
        )

    if (
        causal_effect_result.get(
            "status"
        )
        != "CAUSE_EFFECT_CANDIDATE_EXTRACTION_COMPLETE"
    ):
        raise CausalIntelligenceError(
            "Cause-effect candidate extraction must be complete."
        )

    if (
        causal_effect_result.get(
            "phase"
        )
        != "4.6.8"
    ):
        raise CausalIntelligenceError(
            "Stage F requires Phase 4.6.8 input."
        )

    if (
        causal_effect_result.get(
            "patch"
        )
        != "4.6.8E"
    ):
        raise CausalIntelligenceError(
            "Stage F requires canonical 4.6.8E input."
        )

    if (
        causal_effect_result.get(
            "next_stage"
        )
        != "entity_concept_grounding"
    ):
        raise CausalIntelligenceError(
            "Stage E must hand off to entity_concept_grounding."
        )

    if (
        causal_effect_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence must remain transient."
        )

    if (
        entity_concept_result.get(
            "schema_version"
        )
        != "entity_concept_intelligence_result_v1"
    ):
        raise CausalIntelligenceError(
            "Stage F requires canonical entity_concept_intelligence_result_v1."
        )

    if (
        entity_concept_result.get(
            "status"
        )
        != "ENTITY_CONCEPT_INTELLIGENCE_COMPLETE"
    ):
        raise CausalIntelligenceError(
            "Entity & Concept Intelligence must be complete."
        )

    if (
        entity_concept_result.get(
            "phase"
        )
        != "4.6.2"
    ):
        raise CausalIntelligenceError(
            "Stage F requires Phase 4.6.2 Entity & Concept Intelligence."
        )

    semantic_objects = list(
        entity_concept_result.get(
            "semantic_objects"
        )
        or []
    )

    if not semantic_objects:
        raise CausalIntelligenceError(
            "Canonical semantic_objects are required for grounding."
        )

    entity_boundaries = dict(
        entity_concept_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        entity_boundaries.get(
            "article_local_only"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Entity & Concept Intelligence must be article-local."
        )

    if (
        entity_boundaries.get(
            "semantic_memory_write_performed"
        )
        is not False
    ):
        raise CausalIntelligenceError(
            "Unexpected Semantic Memory write detected upstream."
        )

    if (
        entity_boundaries.get(
            "reasoning_performed"
        )
        is not False
    ):
        raise CausalIntelligenceError(
            "Unexpected reasoning detected in Phase 4.6.2."
        )

    def normalize(
        value: str,
    ) -> str:
        value = str(
            value
            or ""
        ).lower()

        value = value.replace(
            "?",
            "'",
        )

        value = re.sub(
            r"[^a-z0-9']+",
            " ",
            value,
        )

        return re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

    article_identity = dict(
        causal_effect_result.get(
            "article_identity"
        )
        or {}
    )

    article_id = str(
        article_identity.get(
            "article_id"
        )
        or ""
    )

    prepared_objects = []

    for semantic_object in semantic_objects:
        if not isinstance(
            semantic_object,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every semantic object must be a mapping."
            )

        canonical_text = str(
            semantic_object.get(
                "canonical_text"
            )
            or ""
        ).strip()

        semantic_kind = semantic_object.get(
            "semantic_kind"
        )

        confidence = semantic_object.get(
            "extraction_confidence"
        )

        if not canonical_text:
            raise CausalIntelligenceError(
                "Semantic object is missing canonical_text."
            )

        if semantic_kind not in {
            "entity",
            "concept",
        }:
            raise CausalIntelligenceError(
                "Semantic object has invalid semantic_kind."
            )

        if (
            not isinstance(
                confidence,
                (int, float),
            )
            or confidence < 0.0
            or confidence > 1.0
        ):
            raise CausalIntelligenceError(
                "Semantic object has invalid extraction_confidence."
            )

        variants = {
            canonical_text,
        }

        for surface in (
            semantic_object.get(
                "surface_forms"
            )
            or []
        ):
            if (
                isinstance(
                    surface,
                    str,
                )
                and surface.strip()
            ):
                variants.add(
                    surface.strip()
                )

        normalized_variants = {
            normalize(
                variant
            ):
                variant
            for variant in variants
            if normalize(
                variant
            )
        }

        stable_material = (
            article_id
            + "|"
            + str(
                semantic_kind
            )
            + "|"
            + normalize(
                canonical_text
            )
        )

        grounding_ref = (
            "article_semantic_object_"
            + hashlib.sha256(
                stable_material.encode(
                    "utf-8"
                )
            ).hexdigest()[:16]
        )

        prepared_objects.append({
            "grounding_ref":
                grounding_ref,

            "semantic_object":
                semantic_object,

            "canonical_text":
                canonical_text,

            "semantic_kind":
                semantic_kind,

            "extraction_confidence":
                confidence,

            "normalized_variants":
                normalized_variants,
        })

    def ground_span(
        span_text: str,
    ) -> dict[str, Any]:
        normalized_span = normalize(
            span_text
        )

        if not normalized_span:
            return {
                "grounded":
                    False,

                "grounding_status":
                    "UNGROUNDED",

                "grounding_reason":
                    "EMPTY_SPAN",

                "match_strategy":
                    None,

                "grounding_ref":
                    None,

                "canonical_text":
                    None,

                "semantic_kind":
                    None,

                "extraction_confidence":
                    None,

                "matched_surface_form":
                    None,
            }

        matches = []

        for prepared in prepared_objects:
            for (
                normalized_variant,
                original_variant,
            ) in prepared[
                "normalized_variants"
            ].items():

                if not normalized_variant:
                    continue

                strategy = None

                if (
                    normalized_span
                    == normalized_variant
                ):
                    strategy = (
                        "EXACT_CANONICAL_OR_SURFACE_MATCH"
                    )

                else:
                    variant_tokens = (
                        normalized_variant.split()
                    )

                    if len(
                        variant_tokens
                    ) >= 2:
                        bounded_pattern = (
                            r"(?<![a-z0-9'])"
                            + re.escape(
                                normalized_variant
                            )
                            + r"(?![a-z0-9'])"
                        )

                        if re.search(
                            bounded_pattern,
                            normalized_span,
                        ):
                            strategy = (
                                "BOUNDED_MULTIWORD_SURFACE_MATCH"
                            )

                if strategy is None:
                    continue

                matches.append({
                    "grounding_ref":
                        prepared[
                            "grounding_ref"
                        ],

                    "canonical_text":
                        prepared[
                            "canonical_text"
                        ],

                    "semantic_kind":
                        prepared[
                            "semantic_kind"
                        ],

                    "extraction_confidence":
                        prepared[
                            "extraction_confidence"
                        ],

                    "matched_surface_form":
                        original_variant,

                    "normalized_match":
                        normalized_variant,

                    "match_strategy":
                        strategy,

                    "match_token_count":
                        len(
                            normalized_variant.split()
                        ),
                })

        if not matches:
            return {
                "grounded":
                    False,

                "grounding_status":
                    "UNGROUNDED",

                "grounding_reason":
                    "NO_CANONICAL_ENTITY_CONCEPT_MATCH",

                "match_strategy":
                    None,

                "grounding_ref":
                    None,

                "canonical_text":
                    None,

                "semantic_kind":
                    None,

                "extraction_confidence":
                    None,

                "matched_surface_form":
                    None,
            }

        matches.sort(
            key=lambda item: (
                0
                if item[
                    "match_strategy"
                ]
                == "EXACT_CANONICAL_OR_SURFACE_MATCH"
                else 1,

                -item[
                    "match_token_count"
                ],

                -item[
                    "extraction_confidence"
                ],

                item[
                    "canonical_text"
                ],
            )
        )

        best = matches[0]

        best_rank = (
            best[
                "match_strategy"
            ],
            best[
                "match_token_count"
            ],
            best[
                "extraction_confidence"
            ],
        )

        competing = [
            item
            for item in matches[1:]
            if (
                item[
                    "match_strategy"
                ],
                item[
                    "match_token_count"
                ],
                item[
                    "extraction_confidence"
                ],
            )
            == best_rank
            and item[
                "canonical_text"
            ]
            != best[
                "canonical_text"
            ]
        ]

        if competing:
            return {
                "grounded":
                    False,

                "grounding_status":
                    "AMBIGUOUS",

                "grounding_reason":
                    "MULTIPLE_EQUAL_CANONICAL_MATCHES",

                "match_strategy":
                    None,

                "grounding_ref":
                    None,

                "canonical_text":
                    None,

                "semantic_kind":
                    None,

                "extraction_confidence":
                    None,

                "matched_surface_form":
                    None,

                "candidate_match_count":
                    1
                    + len(
                        competing
                    ),
            }

        return {
            "grounded":
                True,

            "grounding_status":
                "GROUNDED",

            "grounding_reason":
                None,

            "match_strategy":
                best[
                    "match_strategy"
                ],

            "grounding_ref":
                best[
                    "grounding_ref"
                ],

            "canonical_text":
                best[
                    "canonical_text"
                ],

            "semantic_kind":
                best[
                    "semantic_kind"
                ],

            "extraction_confidence":
                best[
                    "extraction_confidence"
                ],

            "matched_surface_form":
                best[
                    "matched_surface_form"
                ],
        }

    source_candidates = list(
        causal_effect_result.get(
            "cause_effect_candidates"
        )
        or []
    )

    grounded_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "causal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise CausalIntelligenceError(
                "Causal candidate ID is required."
            )

        if (
            candidate.get(
                "entity_concept_grounded"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Candidate must not already be entity/concept grounded."
            )

        cause_grounding = ground_span(
            str(
                candidate.get(
                    "cause_text"
                )
                or ""
            )
        )

        effect_grounding = ground_span(
            str(
                candidate.get(
                    "effect_text"
                )
                or ""
            )
        )

        cause_grounded = (
            cause_grounding.get(
                "grounded"
            )
            is True
        )

        effect_grounded = (
            effect_grounding.get(
                "grounded"
            )
            is True
        )

        if (
            cause_grounded
            and effect_grounded
        ):
            grounding_status = (
                "BOTH_GROUNDED"
            )

        elif (
            cause_grounded
            or effect_grounded
        ):
            grounding_status = (
                "PARTIALLY_GROUNDED"
            )

        else:
            grounding_status = (
                "UNGROUNDED"
            )

        grounded_candidate = dict(
            candidate
        )

        grounded_candidate.update({
            "cause_grounding":
                cause_grounding,

            "effect_grounding":
                effect_grounding,

            "cause_grounded":
                cause_grounded,

            "effect_grounded":
                effect_grounded,

            "grounding_status":
                grounding_status,

            "entity_concept_grounded":
                (
                    cause_grounded
                    and effect_grounded
                ),

            "causal_relation_normalized":
                False,

            "cause_effect_orientation_resolved":
                False,

            "same_sentence_causal_validated":
                False,

            "cross_sentence_causal_validated":
                False,

            "causal_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "causal_inference_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        grounded_candidates.append(
            grounded_candidate
        )

    grounded_by_id = {
        candidate.get(
            "causal_candidate_id"
        ):
            candidate
        for candidate in grounded_candidates
    }

    grounded_units = []

    for unit in (
        causal_effect_result.get(
            "causal_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every Causal Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "causal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "cause_effect_candidate_extraction"
            )
            != "COMPLETE"
        ):
            raise CausalIntelligenceError(
                "Cause-effect extraction must be COMPLETE before grounding."
            )

        if (
            state.get(
                "entity_concept_grounding"
            )
            != "PENDING"
        ):
            raise CausalIntelligenceError(
                "Entity/concept grounding must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "cause_effect_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "causal_candidate_id"
            )

            grounded = grounded_by_id.get(
                candidate_id
            )

            if grounded is None:
                raise CausalIntelligenceError(
                    "Causal candidate/unit identity mismatch."
                )

            unit_candidates.append(
                grounded
            )

        updated_state = dict(
            state
        )

        updated_state[
            "entity_concept_grounding"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "entity_concept_grounding_performed"
        ] = True

        updated_boundaries[
            "causal_inference_performed"
        ] = False

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "external_authority_check_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "cause_effect_candidates":
                unit_candidates,

            "fully_grounded_candidate_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "grounding_status"
                    )
                    == "BOTH_GROUNDED"
                ),

            "partially_grounded_candidate_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "grounding_status"
                    )
                    == "PARTIALLY_GROUNDED"
                ),

            "ungrounded_candidate_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "grounding_status"
                    )
                    == "UNGROUNDED"
                ),

            "causal_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        grounded_units.append(
            updated_unit
        )

    grounded_units_by_id = {
        unit.get(
            "causal_claim_unit_id"
        ):
            unit
        for unit in grounded_units
    }

    grounded_sections = []

    for section in (
        causal_effect_result.get(
            "causal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "causal_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "causal_claim_unit_id"
            )

            grounded_unit = (
                grounded_units_by_id.get(
                    unit_id
                )
            )

            if grounded_unit is None:
                raise CausalIntelligenceError(
                    "Causal section/unit grounding mismatch."
                )

            section_units.append(
                grounded_unit
            )

        grounded_sections.append({
            **dict(
                section
            ),

            "causal_claim_units":
                section_units,

            "fully_grounded_candidate_count":
                sum(
                    unit.get(
                        "fully_grounded_candidate_count",
                        0,
                    )
                    for unit in section_units
                ),

            "partially_grounded_candidate_count":
                sum(
                    unit.get(
                        "partially_grounded_candidate_count",
                        0,
                    )
                    for unit in section_units
                ),

            "ungrounded_candidate_count":
                sum(
                    unit.get(
                        "ungrounded_candidate_count",
                        0,
                    )
                    for unit in section_units
                ),

            "entity_concept_grounding_complete":
                True,
        })

    both_grounded_count = sum(
        1
        for candidate in grounded_candidates
        if candidate.get(
            "grounding_status"
        )
        == "BOTH_GROUNDED"
    )

    partial_grounded_count = sum(
        1
        for candidate in grounded_candidates
        if candidate.get(
            "grounding_status"
        )
        == "PARTIALLY_GROUNDED"
    )

    ungrounded_count = sum(
        1
        for candidate in grounded_candidates
        if candidate.get(
            "grounding_status"
        )
        == "UNGROUNDED"
    )

    result = dict(
        causal_effect_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "entity_concept_grounding_performed"
    ] = True

    boundaries[
        "causal_relation_normalization_performed"
    ] = False

    boundaries[
        "cause_effect_orientation_resolution_performed"
    ] = False

    boundaries[
        "causal_inference_performed"
    ] = False

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "external_authority_check_performed"
    ] = False

    boundaries[
        "semantic_memory_write_performed"
    ] = False

    boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "causal_entity_concept_grounding_v1",

        "patch":
            "4.6.8F",

        "status":
            "CAUSAL_ENTITY_CONCEPT_GROUNDING_COMPLETE",

        "causal_sections":
            grounded_sections,

        "causal_claim_units":
            grounded_units,

        "cause_effect_candidates":
            grounded_candidates,

        "entity_concept_grounding_summary": {
            "semantic_object_count":
                len(
                    semantic_objects
                ),

            "causal_candidate_count":
                len(
                    grounded_candidates
                ),

            "fully_grounded_candidate_count":
                both_grounded_count,

            "partially_grounded_candidate_count":
                partial_grounded_count,

            "ungrounded_candidate_count":
                ungrounded_count,

            "candidate_count_accounted_for":
                (
                    both_grounded_count
                    + partial_grounded_count
                    + ungrounded_count
                    == len(
                        grounded_candidates
                    )
                ),

            "canonical_entity_concept_objects_reused":
                True,

            "new_entity_concept_objects_created":
                False,

            "fuzzy_similarity_performed":
                False,

            "causal_relation_normalization_performed":
                False,

            "cause_effect_orientation_resolution_performed":
                False,

            "causal_validation_performed":
                False,

            "truth_assessment_performed":
                False,

            "causal_inference_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "causal_relation_normalization",
    })

    return result



def normalize_causal_relations_v1(
    entity_concept_grounding_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Normalize extracted article-local causal candidate labels into
    the canonical Phase 4.6.8 causal relation vocabulary.

    This stage normalizes relation names and relation families only.

    It does NOT:
    - prove that causation is valid,
    - reverse or finalize cause/effect orientation,
    - validate same-sentence causation,
    - validate cross-sentence causation,
    - assess causal evidence strength,
    - infer causation from correlation or proximity,
    - establish factual truth,
    - use external authority,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        entity_concept_grounding_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "entity_concept_grounding_result must be a mapping."
        )

    if (
        entity_concept_grounding_result.get(
            "schema_version"
        )
        != "causal_entity_concept_grounding_v1"
    ):
        raise CausalIntelligenceError(
            "Stage G requires causal_entity_concept_grounding_v1."
        )

    if (
        entity_concept_grounding_result.get(
            "status"
        )
        != "CAUSAL_ENTITY_CONCEPT_GROUNDING_COMPLETE"
    ):
        raise CausalIntelligenceError(
            "Entity/concept grounding must be complete before causal normalization."
        )

    if (
        entity_concept_grounding_result.get(
            "phase"
        )
        != "4.6.8"
    ):
        raise CausalIntelligenceError(
            "Stage G requires Phase 4.6.8 input."
        )

    if (
        entity_concept_grounding_result.get(
            "patch"
        )
        != "4.6.8F"
    ):
        raise CausalIntelligenceError(
            "Stage G requires canonical 4.6.8F input."
        )

    if (
        entity_concept_grounding_result.get(
            "next_stage"
        )
        != "causal_relation_normalization"
    ):
        raise CausalIntelligenceError(
            "Stage F must hand off to causal_relation_normalization."
        )

    if (
        entity_concept_grounding_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence must remain transient."
        )

    canonical_relation_map = {
        "CAUSES":
            "CAUSES",

        "CAUSES_OR_EXPLAINS":
            "CAUSES_OR_EXPLAINS",

        "CAUSES_OR_CONTRIBUTES_TO":
            "CAUSES_OR_CONTRIBUTES_TO",

        "LEADS_TO":
            "LEADS_TO",

        "RESULTS_IN":
            "RESULTS_IN",

        "CONTRIBUTES_TO":
            "CONTRIBUTES_TO",

        "RESPONSIBLE_FOR":
            "RESPONSIBLE_FOR",

        "TRIGGERS":
            "TRIGGERS",

        "AFFECTS":
            "AFFECTS",

        "INFLUENCES":
            "INFLUENCES",

        "IMPACTS":
            "IMPACTS",

        "DEPENDS_ON":
            "DEPENDS_ON",

        "PREVENTS":
            "PREVENTS",

        "INCREASES":
            "INCREASES",

        "DECREASES":
            "DECREASES",

        "REDUCES":
            "REDUCES",

        "IMPROVES":
            "IMPROVES",

        "WORSENS":
            "WORSENS",

        "PRODUCES":
            "PRODUCES",
    }

    causal_relation_families = {
        "CAUSES":
            "DIRECT_CAUSATION",

        "CAUSES_OR_EXPLAINS":
            "CAUSAL_OR_EXPLANATORY",

        "CAUSES_OR_CONTRIBUTES_TO":
            "CAUSAL_OR_CONTRIBUTORY",

        "LEADS_TO":
            "CAUSAL_OUTCOME",

        "RESULTS_IN":
            "CAUSAL_OUTCOME",

        "CONTRIBUTES_TO":
            "CONTRIBUTORY_CAUSATION",

        "RESPONSIBLE_FOR":
            "ATTRIBUTED_CAUSATION",

        "TRIGGERS":
            "TRIGGER_CAUSATION",

        "AFFECTS":
            "CAUSAL_SENSITIVE_INFLUENCE",

        "INFLUENCES":
            "CAUSAL_SENSITIVE_INFLUENCE",

        "IMPACTS":
            "CAUSAL_SENSITIVE_INFLUENCE",

        "DEPENDS_ON":
            "CAUSAL_SENSITIVE_DEPENDENCY",

        "PREVENTS":
            "PREVENTIVE_CAUSATION",

        "INCREASES":
            "DIRECTIONAL_CHANGE",

        "DECREASES":
            "DIRECTIONAL_CHANGE",

        "REDUCES":
            "DIRECTIONAL_CHANGE",

        "IMPROVES":
            "DIRECTIONAL_CHANGE",

        "WORSENS":
            "DIRECTIONAL_CHANGE",

        "PRODUCES":
            "PRODUCTION_CAUSATION",
    }

    strong_causal_relations = {
        "CAUSES",
        "LEADS_TO",
        "RESULTS_IN",
        "CONTRIBUTES_TO",
        "RESPONSIBLE_FOR",
        "TRIGGERS",
    }

    qualified_causal_relations = {
        "CAUSES_OR_EXPLAINS",
        "CAUSES_OR_CONTRIBUTES_TO",
    }

    causal_sensitive_relations = {
        "AFFECTS",
        "INFLUENCES",
        "IMPACTS",
        "DEPENDS_ON",
        "PREVENTS",
        "INCREASES",
        "DECREASES",
        "REDUCES",
        "IMPROVES",
        "WORSENS",
        "PRODUCES",
    }

    source_candidates = list(
        entity_concept_grounding_result.get(
            "cause_effect_candidates"
        )
        or []
    )

    normalized_candidates = []
    unsupported_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "causal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise CausalIntelligenceError(
                "Causal candidate ID is required."
            )

        if (
            candidate.get(
                "causal_relation_normalized"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Candidate must not already be causal-relation normalized."
            )

        raw_relation = str(
            candidate.get(
                "candidate_causal_relation"
            )
            or ""
        ).strip()

        if not raw_relation:
            raise CausalIntelligenceError(
                "Candidate causal relation label is required."
            )

        canonical_relation = (
            canonical_relation_map.get(
                raw_relation
            )
        )

        if canonical_relation is None:
            unsupported = dict(
                candidate
            )

            unsupported.update({
                "causal_relation_normalization_status":
                    "UNSUPPORTED",

                "raw_candidate_causal_relation":
                    raw_relation,

                "canonical_causal_relation":
                    None,

                "causal_relation_family":
                    None,

                "causal_relation_strength_class":
                    None,

                "causal_relation_normalized":
                    False,

                "normalization_reason":
                    "UNSUPPORTED_CAUSAL_RELATION_LABEL",

                "cause_effect_orientation_resolved":
                    False,

                "same_sentence_causal_validated":
                    False,

                "cross_sentence_causal_validated":
                    False,

                "causal_evidence_assessed":
                    False,

                "duplicate_resolution_performed":
                    False,

                "causal_inference_performed":
                    False,

                "truth_assessed":
                    False,

                "external_authority_checked":
                    False,
            })

            unsupported_candidates.append(
                unsupported
            )

            normalized_candidates.append(
                unsupported
            )

            continue

        if (
            canonical_relation
            in strong_causal_relations
        ):
            strength_class = (
                "STRONG_CAUSAL_FORM"
            )

        elif (
            canonical_relation
            in qualified_causal_relations
        ):
            strength_class = (
                "QUALIFIED_CAUSAL_FORM"
            )

        elif (
            canonical_relation
            in causal_sensitive_relations
        ):
            strength_class = (
                "CAUSAL_SENSITIVE_FORM"
            )

        else:
            raise CausalIntelligenceError(
                "Canonical causal relation is missing a strength class."
            )

        normalized = dict(
            candidate
        )

        normalized.update({
            "raw_candidate_causal_relation":
                raw_relation,

            "canonical_causal_relation":
                canonical_relation,

            "causal_relation_family":
                causal_relation_families.get(
                    canonical_relation
                ),

            "causal_relation_strength_class":
                strength_class,

            "causal_relation_normalization_status":
                "NORMALIZED",

            "causal_relation_normalized":
                True,

            "causal_relation_is_directional":
                True,

            "cause_effect_orientation_resolved":
                False,

            "same_sentence_causal_validated":
                False,

            "cross_sentence_causal_validated":
                False,

            "causal_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "causal_inference_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        normalized_candidates.append(
            normalized
        )

    normalized_by_id = {
        candidate.get(
            "causal_candidate_id"
        ):
            candidate
        for candidate in normalized_candidates
    }

    normalized_units = []

    for unit in (
        entity_concept_grounding_result.get(
            "causal_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every Causal Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "causal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "entity_concept_grounding"
            )
            != "COMPLETE"
        ):
            raise CausalIntelligenceError(
                "Entity/concept grounding must be COMPLETE before causal normalization."
            )

        if (
            state.get(
                "causal_relation_normalization"
            )
            != "PENDING"
        ):
            raise CausalIntelligenceError(
                "Causal relation normalization must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "cause_effect_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "causal_candidate_id"
            )

            normalized_candidate = (
                normalized_by_id.get(
                    candidate_id
                )
            )

            if normalized_candidate is None:
                raise CausalIntelligenceError(
                    "Causal candidate/unit normalization mismatch."
                )

            unit_candidates.append(
                normalized_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "causal_relation_normalization"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "causal_relation_normalization_performed"
        ] = True

        updated_boundaries[
            "cause_effect_orientation_resolution_performed"
        ] = False

        updated_boundaries[
            "same_sentence_causal_validation_performed"
        ] = False

        updated_boundaries[
            "cross_sentence_causal_validation_performed"
        ] = False

        updated_boundaries[
            "causal_inference_performed"
        ] = False

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "external_authority_check_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "cause_effect_candidates":
                unit_candidates,

            "normalized_causal_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "causal_relation_normalization_status"
                    )
                    == "NORMALIZED"
                ),

            "unsupported_causal_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "causal_relation_normalization_status"
                    )
                    == "UNSUPPORTED"
                ),

            "causal_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        normalized_units.append(
            updated_unit
        )

    normalized_units_by_id = {
        unit.get(
            "causal_claim_unit_id"
        ):
            unit
        for unit in normalized_units
    }

    normalized_sections = []

    for section in (
        entity_concept_grounding_result.get(
            "causal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "causal_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "causal_claim_unit_id"
            )

            normalized_unit = (
                normalized_units_by_id.get(
                    unit_id
                )
            )

            if normalized_unit is None:
                raise CausalIntelligenceError(
                    "Causal section/unit normalization mismatch."
                )

            section_units.append(
                normalized_unit
            )

        normalized_sections.append({
            **dict(
                section
            ),

            "causal_claim_units":
                section_units,

            "normalized_causal_relation_count":
                sum(
                    unit.get(
                        "normalized_causal_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "unsupported_causal_relation_count":
                sum(
                    unit.get(
                        "unsupported_causal_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "causal_relation_normalization_complete":
                True,
        })

    normalized_count = sum(
        1
        for candidate in normalized_candidates
        if candidate.get(
            "causal_relation_normalization_status"
        )
        == "NORMALIZED"
    )

    unsupported_count = sum(
        1
        for candidate in normalized_candidates
        if candidate.get(
            "causal_relation_normalization_status"
        )
        == "UNSUPPORTED"
    )

    strong_count = sum(
        1
        for candidate in normalized_candidates
        if candidate.get(
            "causal_relation_strength_class"
        )
        == "STRONG_CAUSAL_FORM"
    )

    qualified_count = sum(
        1
        for candidate in normalized_candidates
        if candidate.get(
            "causal_relation_strength_class"
        )
        == "QUALIFIED_CAUSAL_FORM"
    )

    sensitive_count = sum(
        1
        for candidate in normalized_candidates
        if candidate.get(
            "causal_relation_strength_class"
        )
        == "CAUSAL_SENSITIVE_FORM"
    )

    result = dict(
        entity_concept_grounding_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "causal_relation_normalization_performed"
    ] = True

    boundaries[
        "cause_effect_orientation_resolution_performed"
    ] = False

    boundaries[
        "same_sentence_causal_validation_performed"
    ] = False

    boundaries[
        "cross_sentence_causal_validation_performed"
    ] = False

    boundaries[
        "causal_evidence_assessment_performed"
    ] = False

    boundaries[
        "causal_inference_performed"
    ] = False

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "external_authority_check_performed"
    ] = False

    boundaries[
        "quantitative_reasoning_performed"
    ] = False

    boundaries[
        "temporal_reasoning_performed"
    ] = False

    boundaries[
        "semantic_memory_write_performed"
    ] = False

    boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "causal_relation_normalization_v1",

        "patch":
            "4.6.8G",

        "status":
            "CAUSAL_RELATION_NORMALIZATION_COMPLETE",

        "causal_sections":
            normalized_sections,

        "causal_claim_units":
            normalized_units,

        "cause_effect_candidates":
            normalized_candidates,

        "unsupported_causal_candidates":
            unsupported_candidates,

        "causal_relation_normalization_summary": {
            "candidate_count":
                len(
                    normalized_candidates
                ),

            "normalized_causal_relation_count":
                normalized_count,

            "unsupported_causal_relation_count":
                unsupported_count,

            "candidate_count_accounted_for":
                (
                    normalized_count
                    + unsupported_count
                    == len(
                        normalized_candidates
                    )
                ),

            "strong_causal_form_count":
                strong_count,

            "qualified_causal_form_count":
                qualified_count,

            "causal_sensitive_form_count":
                sensitive_count,

            "canonical_causal_vocabulary_applied":
                True,

            "cause_effect_orientation_resolution_performed":
                False,

            "same_sentence_causal_validation_performed":
                False,

            "cross_sentence_causal_validation_performed":
                False,

            "causal_evidence_assessment_performed":
                False,

            "causal_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "cause_effect_orientation",
    })

    return result



def resolve_cause_effect_orientation_v1(
    causal_normalization_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve article-local cause/effect orientation metadata for
    normalized causal candidates.

    Stage E already extracted semantic cause and effect endpoints.
    This stage confirms their directional orientation and records
    their textual order in the source sentence.

    It does NOT:
    - create new cause/effect endpoints,
    - reverse endpoints by guesswork,
    - validate that causation is correct,
    - infer causation from proximity or correlation,
    - perform same-sentence causal validation,
    - perform cross-sentence causal validation,
    - assess causal evidence strength,
    - establish factual truth,
    - use external authority,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        causal_normalization_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "causal_normalization_result must be a mapping."
        )

    if (
        causal_normalization_result.get(
            "schema_version"
        )
        != "causal_relation_normalization_v1"
    ):
        raise CausalIntelligenceError(
            "Stage H requires causal_relation_normalization_v1."
        )

    if (
        causal_normalization_result.get(
            "status"
        )
        != "CAUSAL_RELATION_NORMALIZATION_COMPLETE"
    ):
        raise CausalIntelligenceError(
            "Causal relation normalization must be complete before orientation."
        )

    if (
        causal_normalization_result.get(
            "phase"
        )
        != "4.6.8"
    ):
        raise CausalIntelligenceError(
            "Stage H requires Phase 4.6.8 input."
        )

    if (
        causal_normalization_result.get(
            "patch"
        )
        != "4.6.8G"
    ):
        raise CausalIntelligenceError(
            "Stage H requires canonical 4.6.8G input."
        )

    if (
        causal_normalization_result.get(
            "next_stage"
        )
        != "cause_effect_orientation"
    ):
        raise CausalIntelligenceError(
            "Stage G must hand off to cause_effect_orientation."
        )

    if (
        causal_normalization_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence must remain transient."
        )

    cause_before_effect_patterns = {
        "CAUSE_SIGNAL_EFFECT",
        "EXPLICIT_CAUSE_VERB",
    }

    effect_before_cause_patterns = {
        "EFFECT_BECAUSE_CAUSE",
        "EFFECT_DUE_TO_CAUSE",
        "EFFECT_RESULTS_FROM_CAUSE",
        "DEPENDENT_EFFECT_DEPENDS_ON_FACTOR",
    }

    source_candidates = list(
        causal_normalization_result.get(
            "cause_effect_candidates"
        )
        or []
    )

    resolved_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "causal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise CausalIntelligenceError(
                "Causal candidate ID is required."
            )

        if (
            candidate.get(
                "cause_effect_orientation_resolved"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Candidate must not already have resolved cause/effect orientation."
            )

        normalization_status = (
            candidate.get(
                "causal_relation_normalization_status"
            )
        )

        cause_text = str(
            candidate.get(
                "cause_text"
            )
            or ""
        ).strip()

        effect_text = str(
            candidate.get(
                "effect_text"
            )
            or ""
        ).strip()

        cause_grounding = candidate.get(
            "cause_grounding"
        )

        effect_grounding = candidate.get(
            "effect_grounding"
        )

        extraction_pattern = str(
            candidate.get(
                "extraction_pattern"
            )
            or ""
        ).strip()

        if normalization_status == "UNSUPPORTED":
            unresolved = dict(
                candidate
            )

            unresolved.update({
                "cause_effect_orientation_status":
                    "UNRESOLVED_UNSUPPORTED_CAUSAL_RELATION",

                "orientation_type":
                    None,

                "source_endpoint_order":
                    None,

                "canonical_cause_text":
                    cause_text,

                "canonical_effect_text":
                    effect_text,

                "canonical_cause_grounding":
                    cause_grounding,

                "canonical_effect_grounding":
                    effect_grounding,

                "orientation_basis":
                    None,

                "cause_effect_reversal_performed":
                    False,

                "cause_effect_orientation_resolved":
                    False,

                "same_sentence_causal_validated":
                    False,

                "cross_sentence_causal_validated":
                    False,

                "causal_evidence_assessed":
                    False,

                "causal_inference_performed":
                    False,

                "truth_assessed":
                    False,

                "external_authority_checked":
                    False,
            })

            resolved_candidates.append(
                unresolved
            )

            continue

        if normalization_status != "NORMALIZED":
            raise CausalIntelligenceError(
                "Candidate has invalid causal normalization status."
            )

        if (
            candidate.get(
                "causal_relation_normalized"
            )
            is not True
        ):
            raise CausalIntelligenceError(
                "Normalized candidate must have causal_relation_normalized=True."
            )

        canonical_relation = str(
            candidate.get(
                "canonical_causal_relation"
            )
            or ""
        ).strip()

        if not canonical_relation:
            raise CausalIntelligenceError(
                "Normalized candidate is missing canonical_causal_relation."
            )

        if (
            candidate.get(
                "causal_relation_is_directional"
            )
            is not True
        ):
            raise CausalIntelligenceError(
                "Canonical causal relations must be directional."
            )

        if not cause_text:
            raise CausalIntelligenceError(
                "Normalized causal candidate is missing cause_text."
            )

        if not effect_text:
            raise CausalIntelligenceError(
                "Normalized causal candidate is missing effect_text."
            )

        if extraction_pattern in cause_before_effect_patterns:
            source_endpoint_order = (
                "CAUSE_BEFORE_EFFECT"
            )

            orientation_basis = (
                "EXTRACTION_PATTERN_CAUSE_SIGNAL_EFFECT"
            )

        elif extraction_pattern in effect_before_cause_patterns:
            source_endpoint_order = (
                "EFFECT_BEFORE_CAUSE"
            )

            orientation_basis = (
                "EXTRACTION_PATTERN_EFFECT_SIGNAL_CAUSE"
            )

        else:
            source_endpoint_order = (
                "SOURCE_ORDER_NOT_CANONICALLY_CLASSIFIED"
            )

            orientation_basis = (
                "SEMANTIC_ENDPOINTS_PRESERVED_FROM_STAGE_E"
            )

        resolved = dict(
            candidate
        )

        resolved.update({
            "cause_effect_orientation_status":
                "RESOLVED_CAUSE_TO_EFFECT",

            "orientation_type":
                "DIRECTED_CAUSE_TO_EFFECT",

            "source_endpoint_order":
                source_endpoint_order,

            "canonical_cause_text":
                cause_text,

            "canonical_effect_text":
                effect_text,

            "canonical_cause_grounding":
                cause_grounding,

            "canonical_effect_grounding":
                effect_grounding,

            "orientation_basis":
                orientation_basis,

            "cause_effect_reversal_performed":
                False,

            "cause_effect_orientation_resolved":
                True,

            "same_sentence_causal_validated":
                False,

            "cross_sentence_causal_validated":
                False,

            "causal_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "causal_inference_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        resolved_candidates.append(
            resolved
        )

    resolved_by_id = {
        candidate.get(
            "causal_candidate_id"
        ):
            candidate
        for candidate in resolved_candidates
    }

    resolved_units = []

    for unit in (
        causal_normalization_result.get(
            "causal_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every Causal Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "causal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "causal_relation_normalization"
            )
            != "COMPLETE"
        ):
            raise CausalIntelligenceError(
                "Causal relation normalization must be COMPLETE before orientation."
            )

        if (
            state.get(
                "cause_effect_orientation"
            )
            != "PENDING"
        ):
            raise CausalIntelligenceError(
                "Cause/effect orientation must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "cause_effect_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "causal_candidate_id"
            )

            resolved_candidate = (
                resolved_by_id.get(
                    candidate_id
                )
            )

            if resolved_candidate is None:
                raise CausalIntelligenceError(
                    "Causal candidate/unit orientation mismatch."
                )

            unit_candidates.append(
                resolved_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "cause_effect_orientation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "cause_effect_orientation_resolution_performed"
        ] = True

        updated_boundaries[
            "same_sentence_causal_validation_performed"
        ] = False

        updated_boundaries[
            "cross_sentence_causal_validation_performed"
        ] = False

        updated_boundaries[
            "causal_evidence_assessment_performed"
        ] = False

        updated_boundaries[
            "causal_inference_performed"
        ] = False

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "external_authority_check_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "cause_effect_candidates":
                unit_candidates,

            "resolved_cause_effect_orientation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "cause_effect_orientation_resolved"
                    )
                    is True
                ),

            "unresolved_cause_effect_orientation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "cause_effect_orientation_resolved"
                    )
                    is False
                ),

            "cause_before_effect_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "source_endpoint_order"
                    )
                    == "CAUSE_BEFORE_EFFECT"
                ),

            "effect_before_cause_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "source_endpoint_order"
                    )
                    == "EFFECT_BEFORE_CAUSE"
                ),

            "causal_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        resolved_units.append(
            updated_unit
        )

    resolved_units_by_id = {
        unit.get(
            "causal_claim_unit_id"
        ):
            unit
        for unit in resolved_units
    }

    resolved_sections = []

    for section in (
        causal_normalization_result.get(
            "causal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "causal_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "causal_claim_unit_id"
            )

            resolved_unit = (
                resolved_units_by_id.get(
                    unit_id
                )
            )

            if resolved_unit is None:
                raise CausalIntelligenceError(
                    "Causal section/unit orientation mismatch."
                )

            section_units.append(
                resolved_unit
            )

        resolved_sections.append({
            **dict(
                section
            ),

            "causal_claim_units":
                section_units,

            "resolved_cause_effect_orientation_count":
                sum(
                    unit.get(
                        "resolved_cause_effect_orientation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "unresolved_cause_effect_orientation_count":
                sum(
                    unit.get(
                        "unresolved_cause_effect_orientation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "cause_before_effect_count":
                sum(
                    unit.get(
                        "cause_before_effect_count",
                        0,
                    )
                    for unit in section_units
                ),

            "effect_before_cause_count":
                sum(
                    unit.get(
                        "effect_before_cause_count",
                        0,
                    )
                    for unit in section_units
                ),

            "cause_effect_orientation_complete":
                True,
        })

    resolved_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "cause_effect_orientation_resolved"
        )
        is True
    )

    unresolved_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "cause_effect_orientation_resolved"
        )
        is False
    )

    cause_before_effect_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "source_endpoint_order"
        )
        == "CAUSE_BEFORE_EFFECT"
    )

    effect_before_cause_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "source_endpoint_order"
        )
        == "EFFECT_BEFORE_CAUSE"
    )

    unclassified_source_order_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "source_endpoint_order"
        )
        == "SOURCE_ORDER_NOT_CANONICALLY_CLASSIFIED"
    )

    result = dict(
        causal_normalization_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "cause_effect_orientation_resolution_performed"
    ] = True

    boundaries[
        "same_sentence_causal_validation_performed"
    ] = False

    boundaries[
        "cross_sentence_causal_validation_performed"
    ] = False

    boundaries[
        "causal_evidence_assessment_performed"
    ] = False

    boundaries[
        "causal_inference_performed"
    ] = False

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "external_authority_check_performed"
    ] = False

    boundaries[
        "quantitative_reasoning_performed"
    ] = False

    boundaries[
        "temporal_reasoning_performed"
    ] = False

    boundaries[
        "semantic_memory_write_performed"
    ] = False

    boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "causal_orientation_resolution_v1",

        "patch":
            "4.6.8H",

        "status":
            "CAUSE_EFFECT_ORIENTATION_RESOLUTION_COMPLETE",

        "causal_sections":
            resolved_sections,

        "causal_claim_units":
            resolved_units,

        "cause_effect_candidates":
            resolved_candidates,

        "cause_effect_orientation_summary": {
            "candidate_count":
                len(
                    resolved_candidates
                ),

            "resolved_orientation_count":
                resolved_count,

            "unresolved_orientation_count":
                unresolved_count,

            "candidate_count_accounted_for":
                (
                    resolved_count
                    + unresolved_count
                    == len(
                        resolved_candidates
                    )
                ),

            "cause_before_effect_count":
                cause_before_effect_count,

            "effect_before_cause_count":
                effect_before_cause_count,

            "unclassified_source_order_count":
                unclassified_source_order_count,

            "semantic_cause_effect_endpoints_preserved":
                True,

            "cause_effect_reversal_performed":
                False,

            "new_endpoints_created":
                False,

            "same_sentence_causal_validation_performed":
                False,

            "cross_sentence_causal_validation_performed":
                False,

            "causal_evidence_assessment_performed":
                False,

            "causal_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "same_sentence_causal_validation",
    })

    return result



def validate_same_sentence_causal_candidates_v1(
    orientation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate whether each causal candidate has sufficient
    same-sentence article-local textual support.

    Validation requires:
    - canonical claim-unit sentence identity,
    - supported cause endpoint,
    - supported effect endpoint,
    - supported causal signal,
    - completed causal relation normalization,
    - resolved cause/effect orientation.

    This validates article expression only.

    It does NOT:
    - establish scientific or factual truth,
    - prove real-world causation,
    - infer causation from correlation or proximity,
    - perform cross-sentence causal validation,
    - assess causal evidence strength,
    - create new causal relations,
    - infer missing endpoints,
    - use external authority,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        orientation_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "orientation_result must be a mapping."
        )

    if (
        orientation_result.get(
            "schema_version"
        )
        != "causal_orientation_resolution_v1"
    ):
        raise CausalIntelligenceError(
            "Stage I requires causal_orientation_resolution_v1."
        )

    if (
        orientation_result.get(
            "status"
        )
        != "CAUSE_EFFECT_ORIENTATION_RESOLUTION_COMPLETE"
    ):
        raise CausalIntelligenceError(
            "Cause/effect orientation resolution must be complete."
        )

    if (
        orientation_result.get(
            "phase"
        )
        != "4.6.8"
    ):
        raise CausalIntelligenceError(
            "Stage I requires Phase 4.6.8 input."
        )

    if (
        orientation_result.get(
            "patch"
        )
        != "4.6.8H"
    ):
        raise CausalIntelligenceError(
            "Stage I requires canonical 4.6.8H input."
        )

    if (
        orientation_result.get(
            "next_stage"
        )
        != "same_sentence_causal_validation"
    ):
        raise CausalIntelligenceError(
            "Stage H must hand off to same_sentence_causal_validation."
        )

    if (
        orientation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence must remain transient."
        )

    source_units = list(
        orientation_result.get(
            "causal_claim_units"
        )
        or []
    )

    if not source_units:
        raise CausalIntelligenceError(
            "Causal Claim Units are required."
        )

    candidate_to_unit = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every Causal Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "causal_claim_unit_id"
            )
            or ""
        )

        sentence_id = str(
            unit.get(
                "sentence_id"
            )
            or ""
        )

        claim_text = str(
            unit.get(
                "text"
            )
            or ""
        ).strip()

        if not unit_id:
            raise CausalIntelligenceError(
                "Causal Claim Unit ID is required."
            )

        if not sentence_id:
            raise CausalIntelligenceError(
                "Causal Claim Unit sentence_id is required."
            )

        if not claim_text:
            raise CausalIntelligenceError(
                "Causal Claim Unit text is required."
            )

        state = dict(
            unit.get(
                "causal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "cause_effect_orientation"
            )
            != "COMPLETE"
        ):
            raise CausalIntelligenceError(
                "Cause/effect orientation must be COMPLETE before Stage I."
            )

        if (
            state.get(
                "same_sentence_causal_validation"
            )
            != "PENDING"
        ):
            raise CausalIntelligenceError(
                "Same-sentence causal validation must be PENDING."
            )

        for candidate in (
            unit.get(
                "cause_effect_candidates"
            )
            or []
        ):
            if not isinstance(
                candidate,
                Mapping,
            ):
                raise CausalIntelligenceError(
                    "Every causal candidate must be a mapping."
                )

            candidate_id = str(
                candidate.get(
                    "causal_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise CausalIntelligenceError(
                    "Causal candidate ID is required."
                )

            if candidate_id in candidate_to_unit:
                raise CausalIntelligenceError(
                    "Duplicate causal candidate ID detected."
                )

            candidate_to_unit[
                candidate_id
            ] = {
                "unit":
                    unit,

                "sentence_id":
                    sentence_id,

                "claim_text":
                    claim_text,
            }

    def normalize(
        value: str,
    ) -> str:
        value = str(
            value
            or ""
        ).lower()

        value = value.replace(
            "?",
            "'",
        )

        value = re.sub(
            r"[^a-z0-9']+",
            " ",
            value,
        )

        return re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

    def span_supported(
        span_text: str,
        claim_text: str,
        grounding: Mapping[str, Any] | None,
    ) -> tuple[bool, str | None]:

        claim_norm = normalize(
            claim_text
        )

        span_norm = normalize(
            span_text
        )

        if (
            span_norm
            and span_norm in claim_norm
        ):
            return (
                True,
                "EXTRACTED_SPAN_PRESENT_IN_SENTENCE",
            )

        if isinstance(
            grounding,
            Mapping,
        ):
            matched_surface = normalize(
                grounding.get(
                    "matched_surface_form"
                )
            )

            canonical_text = normalize(
                grounding.get(
                    "canonical_text"
                )
            )

            if (
                matched_surface
                and matched_surface in claim_norm
            ):
                return (
                    True,
                    "GROUNDED_SURFACE_PRESENT_IN_SENTENCE",
                )

            if (
                canonical_text
                and canonical_text in claim_norm
            ):
                return (
                    True,
                    "GROUNDED_CANONICAL_TEXT_PRESENT_IN_SENTENCE",
                )

        return (
            False,
            None,
        )

    def signal_supported(
        candidate: Mapping[str, Any],
        claim_text: str,
    ) -> tuple[bool, str | None]:

        matched_text = str(
            candidate.get(
                "signal_matched_text"
            )
            or ""
        )

        start = candidate.get(
            "signal_character_start"
        )

        end = candidate.get(
            "signal_character_end"
        )

        if (
            isinstance(
                start,
                int,
            )
            and isinstance(
                end,
                int,
            )
            and start >= 0
            and end > start
            and end <= len(
                claim_text
            )
        ):
            source_slice = claim_text[
                start:end
            ]

            if (
                normalize(
                    source_slice
                )
                == normalize(
                    matched_text
                )
                and normalize(
                    matched_text
                )
            ):
                return (
                    True,
                    "CAUSAL_SIGNAL_SPAN_MATCHES_CANONICAL_SENTENCE",
                )

        matched_norm = normalize(
            matched_text
        )

        claim_norm = normalize(
            claim_text
        )

        if (
            matched_norm
            and matched_norm in claim_norm
        ):
            return (
                True,
                "CAUSAL_SIGNAL_TEXT_PRESENT_IN_CANONICAL_SENTENCE",
            )

        return (
            False,
            None,
        )

    source_candidates = list(
        orientation_result.get(
            "cause_effect_candidates"
        )
        or []
    )

    validated_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "causal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise CausalIntelligenceError(
                "Causal candidate ID is required."
            )

        unit_info = candidate_to_unit.get(
            candidate_id
        )

        if unit_info is None:
            raise CausalIntelligenceError(
                "Causal candidate has no canonical claim-unit sentence."
            )

        if (
            candidate.get(
                "same_sentence_causal_validated"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Candidate must not already be same-sentence causal validated."
            )

        claim_text = unit_info[
            "claim_text"
        ]

        candidate_sentence_id = str(
            candidate.get(
                "sentence_id"
            )
            or ""
        )

        canonical_sentence_id = unit_info[
            "sentence_id"
        ]

        same_sentence_identity = (
            candidate_sentence_id
            == canonical_sentence_id
        )

        cause_supported, cause_method = (
            span_supported(
                str(
                    candidate.get(
                        "canonical_cause_text"
                    )
                    or candidate.get(
                        "cause_text"
                    )
                    or ""
                ),
                claim_text,
                candidate.get(
                    "canonical_cause_grounding"
                )
                or candidate.get(
                    "cause_grounding"
                ),
            )
        )

        effect_supported, effect_method = (
            span_supported(
                str(
                    candidate.get(
                        "canonical_effect_text"
                    )
                    or candidate.get(
                        "effect_text"
                    )
                    or ""
                ),
                claim_text,
                candidate.get(
                    "canonical_effect_grounding"
                )
                or candidate.get(
                    "effect_grounding"
                ),
            )
        )

        signal_is_supported, signal_method = (
            signal_supported(
                candidate,
                claim_text,
            )
        )

        normalization_supported = (
            candidate.get(
                "causal_relation_normalization_status"
            )
            == "NORMALIZED"
            and candidate.get(
                "causal_relation_normalized"
            )
            is True
            and bool(
                candidate.get(
                    "canonical_causal_relation"
                )
            )
        )

        orientation_supported = (
            candidate.get(
                "cause_effect_orientation_resolved"
            )
            is True
            and candidate.get(
                "orientation_type"
            )
            == "DIRECTED_CAUSE_TO_EFFECT"
        )

        if (
            candidate.get(
                "causal_relation_normalization_status"
            )
            == "UNSUPPORTED"
        ):
            validation_status = (
                "NOT_VALIDATED_UNSUPPORTED_CAUSAL_RELATION"
            )

            same_sentence_valid = False

            validation_reason = (
                "CAUSAL_RELATION_NOT_CANONICALLY_NORMALIZED"
            )

        elif not same_sentence_identity:
            validation_status = (
                "NOT_VALIDATED_SENTENCE_ID_MISMATCH"
            )

            same_sentence_valid = False

            validation_reason = (
                "CANDIDATE_SENTENCE_ID_DOES_NOT_MATCH_CLAIM_UNIT"
            )

        elif not orientation_supported:
            validation_status = (
                "NOT_VALIDATED_CAUSE_EFFECT_ORIENTATION_UNRESOLVED"
            )

            same_sentence_valid = False

            validation_reason = (
                "CAUSE_EFFECT_ORIENTATION_NOT_RESOLVED"
            )

        elif not normalization_supported:
            validation_status = (
                "NOT_VALIDATED_CAUSAL_NORMALIZATION_INCOMPLETE"
            )

            same_sentence_valid = False

            validation_reason = (
                "CAUSAL_RELATION_NORMALIZATION_NOT_COMPLETE"
            )

        elif not cause_supported:
            validation_status = (
                "NOT_VALIDATED_CAUSE_UNSUPPORTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "CAUSE_NOT_SUPPORTED_BY_CANONICAL_SENTENCE"
            )

        elif not effect_supported:
            validation_status = (
                "NOT_VALIDATED_EFFECT_UNSUPPORTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "EFFECT_NOT_SUPPORTED_BY_CANONICAL_SENTENCE"
            )

        elif not signal_is_supported:
            validation_status = (
                "NOT_VALIDATED_CAUSAL_SIGNAL_UNSUPPORTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "CAUSAL_SIGNAL_NOT_SUPPORTED_BY_CANONICAL_SENTENCE"
            )

        else:
            validation_status = (
                "VALIDATED_SAME_SENTENCE_CAUSAL_EXPRESSION"
            )

            same_sentence_valid = True

            validation_reason = None

        validated = dict(
            candidate
        )

        validated.update({
            "same_sentence_causal_validation_status":
                validation_status,

            "same_sentence_causal_valid":
                same_sentence_valid,

            "same_sentence_causal_validation_reason":
                validation_reason,

            "same_sentence_id_match":
                same_sentence_identity,

            "same_sentence_cause_supported":
                cause_supported,

            "same_sentence_effect_supported":
                effect_supported,

            "same_sentence_causal_signal_supported":
                signal_is_supported,

            "cause_support_method":
                cause_method,

            "effect_support_method":
                effect_method,

            "causal_signal_support_method":
                signal_method,

            "same_sentence_causal_evidence": {
                "sentence_id":
                    canonical_sentence_id,

                "sentence_text":
                    claim_text,

                "signal_type":
                    candidate.get(
                        "signal_type"
                    ),

                "signal_matched_text":
                    candidate.get(
                        "signal_matched_text"
                    ),

                "signal_character_start":
                    candidate.get(
                        "signal_character_start"
                    ),

                "signal_character_end":
                    candidate.get(
                        "signal_character_end"
                    ),
            },

            "same_sentence_causal_validated":
                same_sentence_valid,

            "cross_sentence_causal_validated":
                False,

            "causal_evidence_assessed":
                False,

            "causal_inference_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        validated_candidates.append(
            validated
        )

    validated_by_id = {
        candidate.get(
            "causal_candidate_id"
        ):
            candidate
        for candidate in validated_candidates
    }

    validated_units = []

    for unit in source_units:
        state = dict(
            unit.get(
                "causal_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "cause_effect_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "causal_candidate_id"
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise CausalIntelligenceError(
                    "Causal candidate/unit validation mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "same_sentence_causal_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "same_sentence_causal_validation_performed"
        ] = True

        updated_boundaries[
            "cross_sentence_causal_validation_performed"
        ] = False

        updated_boundaries[
            "causal_evidence_assessment_performed"
        ] = False

        updated_boundaries[
            "causal_inference_performed"
        ] = False

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "external_authority_check_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "cause_effect_candidates":
                unit_candidates,

            "same_sentence_causal_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "same_sentence_causal_valid"
                    )
                    is True
                ),

            "same_sentence_causal_not_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "same_sentence_causal_valid"
                    )
                    is False
                ),

            "causal_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        validated_units.append(
            updated_unit
        )

    validated_units_by_id = {
        unit.get(
            "causal_claim_unit_id"
        ):
            unit
        for unit in validated_units
    }

    validated_sections = []

    for section in (
        orientation_result.get(
            "causal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "causal_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "causal_claim_unit_id"
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise CausalIntelligenceError(
                    "Causal section/unit validation mismatch."
                )

            section_units.append(
                validated_unit
            )

        validated_sections.append({
            **dict(
                section
            ),

            "causal_claim_units":
                section_units,

            "same_sentence_causal_validated_count":
                sum(
                    unit.get(
                        "same_sentence_causal_validated_count",
                        0,
                    )
                    for unit in section_units
                ),

            "same_sentence_causal_not_validated_count":
                sum(
                    unit.get(
                        "same_sentence_causal_not_validated_count",
                        0,
                    )
                    for unit in section_units
                ),

            "same_sentence_causal_validation_complete":
                True,
        })

    validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "same_sentence_causal_valid"
        )
        is True
    )

    not_validated_count = (
        len(
            validated_candidates
        )
        - validated_count
    )

    result = dict(
        orientation_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "same_sentence_causal_validation_performed"
    ] = True

    boundaries[
        "cross_sentence_causal_validation_performed"
    ] = False

    boundaries[
        "causal_evidence_assessment_performed"
    ] = False

    boundaries[
        "causal_inference_performed"
    ] = False

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "external_authority_check_performed"
    ] = False

    boundaries[
        "quantitative_reasoning_performed"
    ] = False

    boundaries[
        "temporal_reasoning_performed"
    ] = False

    boundaries[
        "semantic_memory_write_performed"
    ] = False

    boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "causal_same_sentence_validation_v1",

        "patch":
            "4.6.8I",

        "status":
            "CAUSAL_SAME_SENTENCE_VALIDATION_COMPLETE",

        "causal_sections":
            validated_sections,

        "causal_claim_units":
            validated_units,

        "cause_effect_candidates":
            validated_candidates,

        "same_sentence_causal_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "same_sentence_causal_validated_count":
                validated_count,

            "same_sentence_causal_not_validated_count":
                not_validated_count,

            "candidate_count_accounted_for":
                (
                    validated_count
                    + not_validated_count
                    == len(
                        validated_candidates
                    )
                ),

            "endpoint_support_required":
                True,

            "causal_signal_support_required":
                True,

            "orientation_support_required":
                True,

            "normalization_support_required":
                True,

            "validates_article_expression_only":
                True,

            "cross_sentence_causal_validation_performed":
                False,

            "causal_evidence_assessment_performed":
                False,

            "causal_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "cross_sentence_causal_validation",
    })

    return result



def validate_cross_sentence_causal_candidates_v1(
    same_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate narrowly bounded cross-sentence support for article-local
    causal candidates that were not already validated in Stage I.

    Cross-sentence rescue is restricted to:
    - the immediately adjacent sentence only,
    - the same section only,
    - candidates with canonical normalization,
    - candidates with resolved cause/effect orientation,
    - candidates whose canonical causal signal is already supported
      by the canonical claim sentence.

    An adjacent sentence may support a missing cause/effect endpoint.
    It may NOT create the causal bridge itself.

    This stage does NOT:
    - infer causation from sentence proximity,
    - infer causation from correlation,
    - search unrestricted surrounding context,
    - create new cause/effect endpoints,
    - create new causal relations,
    - establish factual or scientific truth,
    - use external authority,
    - assess causal evidence strength,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        same_sentence_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "same_sentence_result must be a mapping."
        )

    if (
        same_sentence_result.get(
            "schema_version"
        )
        != "causal_same_sentence_validation_v1"
    ):
        raise CausalIntelligenceError(
            "Stage J requires causal_same_sentence_validation_v1."
        )

    if (
        same_sentence_result.get(
            "status"
        )
        != "CAUSAL_SAME_SENTENCE_VALIDATION_COMPLETE"
    ):
        raise CausalIntelligenceError(
            "Same-sentence causal validation must be complete."
        )

    if (
        same_sentence_result.get(
            "phase"
        )
        != "4.6.8"
    ):
        raise CausalIntelligenceError(
            "Stage J requires Phase 4.6.8 input."
        )

    if (
        same_sentence_result.get(
            "patch"
        )
        != "4.6.8I"
    ):
        raise CausalIntelligenceError(
            "Stage J requires canonical 4.6.8I input."
        )

    if (
        same_sentence_result.get(
            "next_stage"
        )
        != "cross_sentence_causal_validation"
    ):
        raise CausalIntelligenceError(
            "Stage I must hand off to cross_sentence_causal_validation."
        )

    if (
        same_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence must remain transient."
        )

    source_units = list(
        same_sentence_result.get(
            "causal_claim_units"
        )
        or []
    )

    if not source_units:
        raise CausalIntelligenceError(
            "Causal Claim Units are required."
        )

    def normalize(
        value: str,
    ) -> str:
        value = str(
            value
            or ""
        ).lower()

        value = value.replace(
            "?",
            "'",
        )

        value = re.sub(
            r"[^a-z0-9']+",
            " ",
            value,
        )

        return re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

    def span_present(
        span_text: str,
        sentence_text: str,
        grounding: Mapping[str, Any] | None,
    ) -> tuple[bool, str | None]:

        sentence_norm = normalize(
            sentence_text
        )

        span_norm = normalize(
            span_text
        )

        if (
            span_norm
            and span_norm in sentence_norm
        ):
            return (
                True,
                "EXTRACTED_SPAN_PRESENT",
            )

        if isinstance(
            grounding,
            Mapping,
        ):
            surface = normalize(
                grounding.get(
                    "matched_surface_form"
                )
            )

            canonical = normalize(
                grounding.get(
                    "canonical_text"
                )
            )

            if (
                surface
                and surface in sentence_norm
            ):
                return (
                    True,
                    "GROUNDED_SURFACE_PRESENT",
                )

            if (
                canonical
                and canonical in sentence_norm
            ):
                return (
                    True,
                    "GROUNDED_CANONICAL_PRESENT",
                )

        return (
            False,
            None,
        )

    unit_records = []

    for position, unit in enumerate(
        source_units
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every Causal Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "causal_claim_unit_id"
            )
            or ""
        )

        sentence_id = str(
            unit.get(
                "sentence_id"
            )
            or ""
        )

        section_id = str(
            unit.get(
                "section_id"
            )
            or ""
        )

        claim_text = str(
            unit.get(
                "text"
            )
            or ""
        ).strip()

        sentence_global_index = unit.get(
            "sentence_global_index"
        )

        if not unit_id:
            raise CausalIntelligenceError(
                "Causal Claim Unit ID is required."
            )

        if not sentence_id:
            raise CausalIntelligenceError(
                "Causal Claim Unit sentence_id is required."
            )

        if not section_id:
            raise CausalIntelligenceError(
                "Causal Claim Unit section_id is required."
            )

        if not claim_text:
            raise CausalIntelligenceError(
                "Causal Claim Unit text is required."
            )

        if not isinstance(
            sentence_global_index,
            int,
        ):
            raise CausalIntelligenceError(
                "sentence_global_index must be an integer."
            )

        state = dict(
            unit.get(
                "causal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "same_sentence_causal_validation"
            )
            != "COMPLETE"
        ):
            raise CausalIntelligenceError(
                "Same-sentence causal validation must be COMPLETE before Stage J."
            )

        if (
            state.get(
                "cross_sentence_causal_validation"
            )
            != "PENDING"
        ):
            raise CausalIntelligenceError(
                "Cross-sentence causal validation must be PENDING."
            )

        unit_records.append({
            "position":
                position,

            "unit":
                unit,

            "unit_id":
                unit_id,

            "sentence_id":
                sentence_id,

            "section_id":
                section_id,

            "sentence_global_index":
                sentence_global_index,

            "text":
                claim_text,
        })

    candidate_to_unit = {}

    for record in unit_records:
        for candidate in (
            record[
                "unit"
            ].get(
                "cause_effect_candidates"
            )
            or []
        ):
            if not isinstance(
                candidate,
                Mapping,
            ):
                raise CausalIntelligenceError(
                    "Every causal candidate must be a mapping."
                )

            candidate_id = str(
                candidate.get(
                    "causal_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise CausalIntelligenceError(
                    "Causal candidate ID is required."
                )

            if candidate_id in candidate_to_unit:
                raise CausalIntelligenceError(
                    "Duplicate causal candidate ID detected."
                )

            candidate_to_unit[
                candidate_id
            ] = record

    source_candidates = list(
        same_sentence_result.get(
            "cause_effect_candidates"
        )
        or []
    )

    validated_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "causal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise CausalIntelligenceError(
                "Causal candidate ID is required."
            )

        record = candidate_to_unit.get(
            candidate_id
        )

        if record is None:
            raise CausalIntelligenceError(
                "Causal candidate has no canonical claim unit."
            )

        if (
            candidate.get(
                "cross_sentence_causal_validated"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Candidate must not already be cross-sentence causal validated."
            )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_causal_valid"
            )
            is True
        )

        normalization_supported = (
            candidate.get(
                "causal_relation_normalization_status"
            )
            == "NORMALIZED"
            and candidate.get(
                "causal_relation_normalized"
            )
            is True
            and bool(
                candidate.get(
                    "canonical_causal_relation"
                )
            )
        )

        orientation_supported = (
            candidate.get(
                "cause_effect_orientation_resolved"
            )
            is True
            and candidate.get(
                "orientation_type"
            )
            == "DIRECTED_CAUSE_TO_EFFECT"
        )

        same_cause_supported = (
            candidate.get(
                "same_sentence_cause_supported"
            )
            is True
        )

        same_effect_supported = (
            candidate.get(
                "same_sentence_effect_supported"
            )
            is True
        )

        same_signal_supported = (
            candidate.get(
                "same_sentence_causal_signal_supported"
            )
            is True
        )

        adjacent_records = []

        for other in unit_records:
            if (
                other[
                    "unit_id"
                ]
                == record[
                    "unit_id"
                ]
            ):
                continue

            if (
                other[
                    "section_id"
                ]
                != record[
                    "section_id"
                ]
            ):
                continue

            distance = abs(
                other[
                    "sentence_global_index"
                ]
                - record[
                    "sentence_global_index"
                ]
            )

            if distance == 1:
                adjacent_records.append(
                    other
                )

        adjacent_records.sort(
            key=lambda item: (
                abs(
                    item[
                        "sentence_global_index"
                    ]
                    - record[
                        "sentence_global_index"
                    ]
                ),
                item[
                    "sentence_global_index"
                ],
            )
        )

        cross_cause_supported = False
        cross_effect_supported = False

        cause_support_evidence = None
        effect_support_evidence = None

        eligible_for_cross_sentence_rescue = (
            not same_sentence_valid
            and normalization_supported
            and orientation_supported
            and candidate.get(
                "same_sentence_id_match"
            )
            is True
            and same_signal_supported
        )

        if eligible_for_cross_sentence_rescue:
            for adjacent in adjacent_records:
                if not same_cause_supported:
                    (
                        supported,
                        method,
                    ) = span_present(
                        str(
                            candidate.get(
                                "canonical_cause_text"
                            )
                            or candidate.get(
                                "cause_text"
                            )
                            or ""
                        ),
                        adjacent[
                            "text"
                        ],
                        candidate.get(
                            "canonical_cause_grounding"
                        )
                        or candidate.get(
                            "cause_grounding"
                        ),
                    )

                    if supported:
                        cross_cause_supported = True

                        cause_support_evidence = {
                            "sentence_id":
                                adjacent[
                                    "sentence_id"
                                ],

                            "sentence_global_index":
                                adjacent[
                                    "sentence_global_index"
                                ],

                            "sentence_text":
                                adjacent[
                                    "text"
                                ],

                            "support_method":
                                method,
                        }

                if not same_effect_supported:
                    (
                        supported,
                        method,
                    ) = span_present(
                        str(
                            candidate.get(
                                "canonical_effect_text"
                            )
                            or candidate.get(
                                "effect_text"
                            )
                            or ""
                        ),
                        adjacent[
                            "text"
                        ],
                        candidate.get(
                            "canonical_effect_grounding"
                        )
                        or candidate.get(
                            "effect_grounding"
                        ),
                    )

                    if supported:
                        cross_effect_supported = True

                        effect_support_evidence = {
                            "sentence_id":
                                adjacent[
                                    "sentence_id"
                                ],

                            "sentence_global_index":
                                adjacent[
                                    "sentence_global_index"
                                ],

                            "sentence_text":
                                adjacent[
                                    "text"
                                ],

                            "support_method":
                                method,
                        }

        combined_cause_supported = (
            same_cause_supported
            or cross_cause_supported
        )

        combined_effect_supported = (
            same_effect_supported
            or cross_effect_supported
        )

        if same_sentence_valid:
            cross_sentence_status = (
                "NOT_REQUIRED_ALREADY_VALIDATED"
            )

            cross_sentence_valid = False

            final_causal_expression_validated = True

            validation_reason = (
                "SAME_SENTENCE_CAUSAL_VALIDATION_ALREADY_SUFFICIENT"
            )

        elif (
            candidate.get(
                "causal_relation_normalization_status"
            )
            == "UNSUPPORTED"
        ):
            cross_sentence_status = (
                "NOT_VALIDATED_UNSUPPORTED_CAUSAL_RELATION"
            )

            cross_sentence_valid = False

            final_causal_expression_validated = False

            validation_reason = (
                "CAUSAL_RELATION_NOT_CANONICALLY_NORMALIZED"
            )

        elif (
            candidate.get(
                "same_sentence_id_match"
            )
            is not True
        ):
            cross_sentence_status = (
                "NOT_VALIDATED_SENTENCE_ID_MISMATCH"
            )

            cross_sentence_valid = False

            final_causal_expression_validated = False

            validation_reason = (
                "CANONICAL_SENTENCE_ID_MISMATCH_NOT_RESCUED"
            )

        elif not normalization_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_CAUSAL_NORMALIZATION_INCOMPLETE"
            )

            cross_sentence_valid = False

            final_causal_expression_validated = False

            validation_reason = (
                "CAUSAL_RELATION_NORMALIZATION_NOT_COMPLETE"
            )

        elif not orientation_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_CAUSE_EFFECT_ORIENTATION_UNRESOLVED"
            )

            cross_sentence_valid = False

            final_causal_expression_validated = False

            validation_reason = (
                "CAUSE_EFFECT_ORIENTATION_NOT_RESOLVED"
            )

        elif not same_signal_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_CAUSAL_SIGNAL_UNSUPPORTED"
            )

            cross_sentence_valid = False

            final_causal_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_CAUSAL_SIGNAL"
            )

        elif (
            combined_cause_supported
            and combined_effect_supported
            and (
                cross_cause_supported
                or cross_effect_supported
            )
        ):
            cross_sentence_status = (
                "VALIDATED_CROSS_SENTENCE_CAUSAL_EXPRESSION"
            )

            cross_sentence_valid = True

            final_causal_expression_validated = True

            validation_reason = None

        else:
            cross_sentence_status = (
                "NOT_VALIDATED_INSUFFICIENT_ADJACENT_CAUSAL_SUPPORT"
            )

            cross_sentence_valid = False

            final_causal_expression_validated = False

            validation_reason = (
                "IMMEDIATE_SAME_SECTION_ADJACENT_ENDPOINT_SUPPORT_INSUFFICIENT"
            )

        validated = dict(
            candidate
        )

        validated.update({
            "cross_sentence_causal_validation_status":
                cross_sentence_status,

            "cross_sentence_causal_valid":
                cross_sentence_valid,

            "cross_sentence_causal_validation_reason":
                validation_reason,

            "cross_sentence_cause_supported":
                cross_cause_supported,

            "cross_sentence_effect_supported":
                cross_effect_supported,

            "combined_cause_supported":
                combined_cause_supported,

            "combined_effect_supported":
                combined_effect_supported,

            "canonical_sentence_causal_signal_supported":
                same_signal_supported,

            "cross_sentence_cause_evidence":
                cause_support_evidence,

            "cross_sentence_effect_evidence":
                effect_support_evidence,

            "adjacent_same_section_sentence_count":
                len(
                    adjacent_records
                ),

            "cross_sentence_rescue_policy":
                (
                    "ENDPOINT_SUPPORT_ONLY_WITH_CANONICAL_"
                    "SENTENCE_CAUSAL_SIGNAL"
                ),

            "final_causal_expression_validated":
                final_causal_expression_validated,

            "cross_sentence_causal_validated":
                cross_sentence_valid,

            "causal_evidence_assessed":
                False,

            "causal_inference_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        validated_candidates.append(
            validated
        )

    validated_by_id = {
        candidate.get(
            "causal_candidate_id"
        ):
            candidate
        for candidate in validated_candidates
    }

    validated_units = []

    for record in unit_records:
        unit = record[
            "unit"
        ]

        state = dict(
            unit.get(
                "causal_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "cause_effect_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "causal_candidate_id"
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise CausalIntelligenceError(
                    "Causal candidate/unit cross-sentence validation mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "cross_sentence_causal_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "cross_sentence_causal_validation_performed"
        ] = True

        updated_boundaries[
            "causal_evidence_assessment_performed"
        ] = False

        updated_boundaries[
            "causal_inference_performed"
        ] = False

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "external_authority_check_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "cause_effect_candidates":
                unit_candidates,

            "cross_sentence_causal_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "cross_sentence_causal_valid"
                    )
                    is True
                ),

            "final_causal_expression_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "final_causal_expression_validated"
                    )
                    is True
                ),

            "causal_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        validated_units.append(
            updated_unit
        )

    validated_units_by_id = {
        unit.get(
            "causal_claim_unit_id"
        ):
            unit
        for unit in validated_units
    }

    validated_sections = []

    for section in (
        same_sentence_result.get(
            "causal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "causal_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "causal_claim_unit_id"
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise CausalIntelligenceError(
                    "Causal section/unit cross-sentence validation mismatch."
                )

            section_units.append(
                validated_unit
            )

        validated_sections.append({
            **dict(
                section
            ),

            "causal_claim_units":
                section_units,

            "cross_sentence_causal_validated_count":
                sum(
                    unit.get(
                        "cross_sentence_causal_validated_count",
                        0,
                    )
                    for unit in section_units
                ),

            "final_causal_expression_validated_count":
                sum(
                    unit.get(
                        "final_causal_expression_validated_count",
                        0,
                    )
                    for unit in section_units
                ),

            "cross_sentence_causal_validation_complete":
                True,
        })

    cross_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "cross_sentence_causal_valid"
        )
        is True
    )

    already_same_sentence_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "same_sentence_causal_valid"
        )
        is True
    )

    final_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "final_causal_expression_validated"
        )
        is True
    )

    final_not_validated_count = (
        len(
            validated_candidates
        )
        - final_validated_count
    )

    result = dict(
        same_sentence_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "cross_sentence_causal_validation_performed"
    ] = True

    boundaries[
        "causal_evidence_assessment_performed"
    ] = False

    boundaries[
        "causal_inference_performed"
    ] = False

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "external_authority_check_performed"
    ] = False

    boundaries[
        "quantitative_reasoning_performed"
    ] = False

    boundaries[
        "temporal_reasoning_performed"
    ] = False

    boundaries[
        "semantic_memory_write_performed"
    ] = False

    boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "causal_cross_sentence_validation_v1",

        "patch":
            "4.6.8J",

        "status":
            "CAUSAL_CROSS_SENTENCE_VALIDATION_COMPLETE",

        "causal_sections":
            validated_sections,

        "causal_claim_units":
            validated_units,

        "cause_effect_candidates":
            validated_candidates,

        "cross_sentence_causal_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "already_same_sentence_validated_count":
                already_same_sentence_count,

            "cross_sentence_causal_validated_count":
                cross_validated_count,

            "final_causal_expression_validated_count":
                final_validated_count,

            "final_causal_expression_not_validated_count":
                final_not_validated_count,

            "candidate_count_accounted_for":
                (
                    final_validated_count
                    + final_not_validated_count
                    == len(
                        validated_candidates
                    )
                ),

            "adjacency_policy":
                "IMMEDIATE_SENTENCE_DISTANCE_1_SAME_SECTION_ONLY",

            "adjacent_sentence_may_supply_endpoint_only":
                True,

            "canonical_sentence_causal_signal_required":
                True,

            "adjacent_sentence_may_create_causal_bridge":
                False,

            "unrestricted_cross_sentence_inference_performed":
                False,

            "causal_evidence_assessment_performed":
                False,

            "causal_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "causal_evidence_confidence_assessment",
    })

    return result



def assess_causal_confidence_evidence_v1(
    cross_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Assess article-local evidence strength for causal expressions
    already processed through same- and cross-sentence validation.

    Confidence measures how strongly the article itself supports the
    extracted causal expression. It does NOT measure scientific truth
    or real-world causal validity.

    Safeguards:
    - unvalidated causal expressions receive zero evidence confidence,
    - same-sentence evidence is stronger than cross-sentence rescue,
    - causal-sensitive relation forms cannot be promoted to STRONG,
    - cross-sentence rescued expressions cannot be promoted to STRONG,
    - upstream causal-form classification is preserved.

    This stage does NOT:
    - establish factual or scientific truth,
    - perform external verification,
    - discover new causal relations,
    - infer causation from correlation or proximity,
    - alter cause/effect orientation,
    - perform duplicate resolution,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        cross_sentence_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "cross_sentence_result must be a mapping."
        )

    if (
        cross_sentence_result.get(
            "schema_version"
        )
        != "causal_cross_sentence_validation_v1"
    ):
        raise CausalIntelligenceError(
            "Stage K requires causal_cross_sentence_validation_v1."
        )

    if (
        cross_sentence_result.get(
            "status"
        )
        != "CAUSAL_CROSS_SENTENCE_VALIDATION_COMPLETE"
    ):
        raise CausalIntelligenceError(
            "Cross-sentence causal validation must be complete."
        )

    if (
        cross_sentence_result.get(
            "phase"
        )
        != "4.6.8"
    ):
        raise CausalIntelligenceError(
            "Stage K requires Phase 4.6.8 input."
        )

    if (
        cross_sentence_result.get(
            "patch"
        )
        != "4.6.8J"
    ):
        raise CausalIntelligenceError(
            "Stage K requires canonical 4.6.8J input."
        )

    if (
        cross_sentence_result.get(
            "next_stage"
        )
        != "causal_evidence_confidence_assessment"
    ):
        raise CausalIntelligenceError(
            "Stage J must hand off to causal_evidence_confidence_assessment."
        )

    if (
        cross_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence must remain transient."
        )

    source_candidates = list(
        cross_sentence_result.get(
            "cause_effect_candidates"
        )
        or []
    )

    assessed_candidates = []

    valid_strength_classes = {
        "STRONG_CAUSAL_FORM",
        "QUALIFIED_CAUSAL_FORM",
        "CAUSAL_SENSITIVE_FORM",
    }

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "causal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise CausalIntelligenceError(
                "Causal candidate ID is required."
            )

        if (
            candidate.get(
                "causal_evidence_assessed"
            )
            is True
        ):
            raise CausalIntelligenceError(
                "Candidate must not already have causal evidence assessment."
            )

        final_validated = (
            candidate.get(
                "final_causal_expression_validated"
            )
            is True
        )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_causal_valid"
            )
            is True
        )

        cross_sentence_valid = (
            candidate.get(
                "cross_sentence_causal_valid"
            )
            is True
        )

        normalization_status = candidate.get(
            "causal_relation_normalization_status"
        )

        if normalization_status == "NORMALIZED":
            strength_class = str(
                candidate.get(
                    "causal_relation_strength_class"
                )
                or ""
            )

            if strength_class not in valid_strength_classes:
                raise CausalIntelligenceError(
                    "Normalized causal candidate has invalid causal strength class."
                )

        elif normalization_status == "UNSUPPORTED":
            strength_class = None

        else:
            raise CausalIntelligenceError(
                "Candidate has invalid causal normalization status."
            )

        cause_grounding = (
            candidate.get(
                "canonical_cause_grounding"
            )
            or candidate.get(
                "cause_grounding"
            )
            or {}
        )

        effect_grounding = (
            candidate.get(
                "canonical_effect_grounding"
            )
            or candidate.get(
                "effect_grounding"
            )
            or {}
        )

        cause_grounded = (
            isinstance(
                cause_grounding,
                Mapping,
            )
            and cause_grounding.get(
                "grounded"
            )
            is True
        )

        effect_grounded = (
            isinstance(
                effect_grounding,
                Mapping,
            )
            and effect_grounding.get(
                "grounded"
            )
            is True
        )

        cause_confidence = (
            cause_grounding.get(
                "extraction_confidence"
            )
            if isinstance(
                cause_grounding,
                Mapping,
            )
            else None
        )

        effect_confidence = (
            effect_grounding.get(
                "extraction_confidence"
            )
            if isinstance(
                effect_grounding,
                Mapping,
            )
            else None
        )

        grounding_confidences = [
            value
            for value in (
                cause_confidence,
                effect_confidence,
            )
            if isinstance(
                value,
                (int, float),
            )
            and 0.0 <= value <= 1.0
        ]

        if grounding_confidences:
            grounding_confidence = round(
                sum(
                    grounding_confidences
                )
                / len(
                    grounding_confidences
                ),
                3,
            )

        else:
            grounding_confidence = None

        if not final_validated:
            evidence_score = 0.0

            evidence_strength = (
                "INSUFFICIENT"
            )

            primary_basis = (
                "CAUSAL_EXPRESSION_NOT_VALIDATED"
            )

            confidence_cap_applied = None

        else:
            evidence_score = 0.45

            if same_sentence_valid:
                evidence_score += 0.25

                primary_basis = (
                    "SAME_SENTENCE_CAUSAL_EXPRESSION_VALIDATED"
                )

            elif cross_sentence_valid:
                evidence_score += 0.12

                primary_basis = (
                    "ADJACENT_CROSS_SENTENCE_CAUSAL_EXPRESSION_VALIDATED"
                )

            else:
                primary_basis = (
                    "VALIDATED_WITHOUT_RECOGNIZED_CAUSAL_EVIDENCE_MODE"
                )

            if (
                cause_grounded
                and effect_grounded
            ):
                evidence_score += 0.08

            elif (
                cause_grounded
                or effect_grounded
            ):
                evidence_score += 0.04

            if grounding_confidence is not None:
                evidence_score += (
                    grounding_confidence
                    * 0.08
                )

            if strength_class == "STRONG_CAUSAL_FORM":
                evidence_score += 0.10

            elif strength_class == "QUALIFIED_CAUSAL_FORM":
                evidence_score += 0.06

            elif strength_class == "CAUSAL_SENSITIVE_FORM":
                evidence_score += 0.02

            evidence_score = min(
                evidence_score,
                0.99,
            )

            confidence_cap_applied = None

            if cross_sentence_valid:
                if evidence_score > 0.79:
                    evidence_score = 0.79

                    confidence_cap_applied = (
                        "CROSS_SENTENCE_MAX_MODERATE"
                    )

            if strength_class == "CAUSAL_SENSITIVE_FORM":
                if evidence_score > 0.79:
                    evidence_score = 0.79

                    confidence_cap_applied = (
                        "CAUSAL_SENSITIVE_MAX_MODERATE"
                    )

            evidence_score = round(
                evidence_score,
                3,
            )

            if evidence_score >= 0.85:
                evidence_strength = "STRONG"

            elif evidence_score >= 0.70:
                evidence_strength = "MODERATE"

            else:
                evidence_strength = "LIMITED"

        assessed = dict(
            candidate
        )

        assessed.update({
            "causal_evidence_assessed":
                True,

            "causal_evidence_score":
                evidence_score,

            "causal_evidence_strength":
                evidence_strength,

            "causal_evidence_basis":
                primary_basis,

            "causal_confidence_cap_applied":
                confidence_cap_applied,

            "causal_evidence_factors": {
                "final_causal_expression_validated":
                    final_validated,

                "same_sentence_causal_valid":
                    same_sentence_valid,

                "cross_sentence_causal_valid":
                    cross_sentence_valid,

                "causal_relation_strength_class":
                    strength_class,

                "cause_grounded":
                    cause_grounded,

                "effect_grounded":
                    effect_grounded,

                "grounding_confidence":
                    grounding_confidence,
            },

            "causal_form_class_preserved":
                True,

            "causal_sensitive_form_promoted_to_strong":
                False,

            "cross_sentence_expression_promoted_to_strong":
                False,

            "confidence_scope":
                "ARTICLE_LOCAL_CAUSAL_EXPRESSION_EVIDENCE_ONLY",

            "causal_inference_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        assessed_candidates.append(
            assessed
        )

    assessed_by_id = {
        candidate.get(
            "causal_candidate_id"
        ):
            candidate
        for candidate in assessed_candidates
    }

    assessed_units = []

    for unit in (
        cross_sentence_result.get(
            "causal_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every Causal Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "causal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "cross_sentence_causal_validation"
            )
            != "COMPLETE"
        ):
            raise CausalIntelligenceError(
                "Cross-sentence causal validation must be COMPLETE before Stage K."
            )

        if (
            state.get(
                "causal_evidence_assessment"
            )
            != "PENDING"
        ):
            raise CausalIntelligenceError(
                "Causal evidence assessment must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "cause_effect_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "causal_candidate_id"
            )

            assessed_candidate = (
                assessed_by_id.get(
                    candidate_id
                )
            )

            if assessed_candidate is None:
                raise CausalIntelligenceError(
                    "Causal candidate/unit evidence mismatch."
                )

            unit_candidates.append(
                assessed_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "causal_evidence_assessment"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "causal_evidence_assessment_performed"
        ] = True

        updated_boundaries[
            "duplicate_causal_resolution_performed"
        ] = False

        updated_boundaries[
            "causal_inference_performed"
        ] = False

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "external_authority_check_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "cause_effect_candidates":
                unit_candidates,

            "strong_causal_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "causal_evidence_strength"
                    )
                    == "STRONG"
                ),

            "moderate_causal_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "causal_evidence_strength"
                    )
                    == "MODERATE"
                ),

            "limited_causal_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "causal_evidence_strength"
                    )
                    == "LIMITED"
                ),

            "insufficient_causal_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "causal_evidence_strength"
                    )
                    == "INSUFFICIENT"
                ),

            "causal_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        assessed_units.append(
            updated_unit
        )

    assessed_units_by_id = {
        unit.get(
            "causal_claim_unit_id"
        ):
            unit
        for unit in assessed_units
    }

    assessed_sections = []

    for section in (
        cross_sentence_result.get(
            "causal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "causal_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "causal_claim_unit_id"
            )

            assessed_unit = (
                assessed_units_by_id.get(
                    unit_id
                )
            )

            if assessed_unit is None:
                raise CausalIntelligenceError(
                    "Causal section/unit evidence mismatch."
                )

            section_units.append(
                assessed_unit
            )

        assessed_sections.append({
            **dict(
                section
            ),

            "causal_claim_units":
                section_units,

            "strong_causal_evidence_count":
                sum(
                    unit.get(
                        "strong_causal_evidence_count",
                        0,
                    )
                    for unit in section_units
                ),

            "moderate_causal_evidence_count":
                sum(
                    unit.get(
                        "moderate_causal_evidence_count",
                        0,
                    )
                    for unit in section_units
                ),

            "limited_causal_evidence_count":
                sum(
                    unit.get(
                        "limited_causal_evidence_count",
                        0,
                    )
                    for unit in section_units
                ),

            "insufficient_causal_evidence_count":
                sum(
                    unit.get(
                        "insufficient_causal_evidence_count",
                        0,
                    )
                    for unit in section_units
                ),

            "causal_evidence_assessment_complete":
                True,
        })

    strong_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "causal_evidence_strength"
        )
        == "STRONG"
    )

    moderate_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "causal_evidence_strength"
        )
        == "MODERATE"
    )

    limited_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "causal_evidence_strength"
        )
        == "LIMITED"
    )

    insufficient_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "causal_evidence_strength"
        )
        == "INSUFFICIENT"
    )

    sensitive_strong_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "causal_relation_strength_class"
        )
        == "CAUSAL_SENSITIVE_FORM"
        and candidate.get(
            "causal_evidence_strength"
        )
        == "STRONG"
    )

    cross_sentence_strong_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "cross_sentence_causal_valid"
        )
        is True
        and candidate.get(
            "causal_evidence_strength"
        )
        == "STRONG"
    )

    result = dict(
        cross_sentence_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "causal_evidence_assessment_performed"
    ] = True

    boundaries[
        "duplicate_causal_resolution_performed"
    ] = False

    boundaries[
        "causal_inference_performed"
    ] = False

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "external_authority_check_performed"
    ] = False

    boundaries[
        "quantitative_reasoning_performed"
    ] = False

    boundaries[
        "temporal_reasoning_performed"
    ] = False

    boundaries[
        "semantic_memory_write_performed"
    ] = False

    boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "causal_evidence_assessment_v1",

        "patch":
            "4.6.8K",

        "status":
            "CAUSAL_EVIDENCE_ASSESSMENT_COMPLETE",

        "causal_sections":
            assessed_sections,

        "causal_claim_units":
            assessed_units,

        "cause_effect_candidates":
            assessed_candidates,

        "causal_evidence_summary": {
            "candidate_count":
                len(
                    assessed_candidates
                ),

            "strong_causal_evidence_count":
                strong_count,

            "moderate_causal_evidence_count":
                moderate_count,

            "limited_causal_evidence_count":
                limited_count,

            "insufficient_causal_evidence_count":
                insufficient_count,

            "candidate_count_accounted_for":
                (
                    strong_count
                    + moderate_count
                    + limited_count
                    + insufficient_count
                    == len(
                        assessed_candidates
                    )
                ),

            "causal_sensitive_strong_count":
                sensitive_strong_count,

            "cross_sentence_strong_count":
                cross_sentence_strong_count,

            "causal_sensitive_strong_promotion_prohibited":
                True,

            "cross_sentence_strong_promotion_prohibited":
                True,

            "confidence_scope":
                "ARTICLE_LOCAL_CAUSAL_EXPRESSION_EVIDENCE_ONLY",

            "scientific_truth_confidence_computed":
                False,

            "real_world_causation_verified":
                False,

            "causal_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "duplicate_redundant_causal_resolution",
    })

    return result



def resolve_duplicate_redundant_causal_relations_v1(
    evidence_assessment_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve exact article-local duplicate causal candidates.

    Duplicate identity is based strictly on:
    canonical cause + canonical causal relation + canonical effect.

    Causal direction is preserved. Endpoint order is never treated
    as symmetric.

    The strongest article-supported candidate becomes the
    representative while all duplicate provenance is preserved.

    This stage does NOT:
    - perform fuzzy semantic similarity,
    - merge different causal relation types,
    - reverse cause/effect endpoints,
    - infer new causal relations,
    - establish factual or scientific truth,
    - use external authority,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import hashlib
    import re

    if not isinstance(
        evidence_assessment_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "evidence_assessment_result must be a mapping."
        )

    if (
        evidence_assessment_result.get(
            "schema_version"
        )
        != "causal_evidence_assessment_v1"
    ):
        raise CausalIntelligenceError(
            "Stage L requires causal_evidence_assessment_v1."
        )

    if (
        evidence_assessment_result.get(
            "status"
        )
        != "CAUSAL_EVIDENCE_ASSESSMENT_COMPLETE"
    ):
        raise CausalIntelligenceError(
            "Causal evidence assessment must be complete."
        )

    if (
        evidence_assessment_result.get(
            "phase"
        )
        != "4.6.8"
    ):
        raise CausalIntelligenceError(
            "Stage L requires Phase 4.6.8 input."
        )

    if (
        evidence_assessment_result.get(
            "patch"
        )
        != "4.6.8K"
    ):
        raise CausalIntelligenceError(
            "Stage L requires canonical 4.6.8K input."
        )

    if (
        evidence_assessment_result.get(
            "next_stage"
        )
        != "duplicate_redundant_causal_resolution"
    ):
        raise CausalIntelligenceError(
            "Stage K must hand off to duplicate_redundant_causal_resolution."
        )

    if (
        evidence_assessment_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence must remain transient."
        )

    def normalize(
        value: Any,
    ) -> str:
        value = str(
            value
            or ""
        ).lower()

        value = value.replace(
            "?",
            "'",
        )

        value = re.sub(
            r"[^a-z0-9']+",
            " ",
            value,
        )

        return re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

    def endpoint_text(
        candidate: Mapping[str, Any],
        side: str,
    ) -> str:
        grounding = (
            candidate.get(
                "canonical_" + side + "_grounding"
            )
            or candidate.get(
                side + "_grounding"
            )
            or {}
        )

        if isinstance(
            grounding,
            Mapping,
        ):
            canonical_text = grounding.get(
                "canonical_text"
            )

            if canonical_text:
                return normalize(
                    canonical_text
                )

        return normalize(
            candidate.get(
                "canonical_" + side + "_text"
            )
            or candidate.get(
                side + "_text"
            )
        )

    def duplicate_key(
        candidate: Mapping[str, Any],
    ) -> tuple[str, str, str] | None:

        relation = normalize(
            candidate.get(
                "canonical_causal_relation"
            )
        )

        cause = endpoint_text(
            candidate,
            "cause",
        )

        effect = endpoint_text(
            candidate,
            "effect",
        )

        if (
            not relation
            or not cause
            or not effect
        ):
            return None

        return (
            cause,
            relation,
            effect,
        )

    source_candidates = list(
        evidence_assessment_result.get(
            "cause_effect_candidates"
        )
        or []
    )

    groups: dict[
        tuple[str, str, str],
        list[dict[str, Any]],
    ] = {}

    non_groupable = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "causal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise CausalIntelligenceError(
                "Causal candidate ID is required."
            )

        if (
            candidate.get(
                "causal_evidence_assessed"
            )
            is not True
        ):
            raise CausalIntelligenceError(
                "Every causal candidate must have completed evidence assessment."
            )

        if (
            candidate.get(
                "duplicate_resolution_performed"
            )
            is True
        ):
            raise CausalIntelligenceError(
                "Candidate must not already have duplicate resolution."
            )

        copied = dict(
            candidate
        )

        key = duplicate_key(
            copied
        )

        if key is None:
            non_groupable.append(
                copied
            )

            continue

        groups.setdefault(
            key,
            [],
        ).append(
            copied
        )

    strength_rank = {
        "STRONG":
            4,

        "MODERATE":
            3,

        "LIMITED":
            2,

        "INSUFFICIENT":
            1,
    }

    resolved_by_id = {}

    representative_candidates = []

    duplicate_group_count = 0
    duplicate_candidate_count = 0

    for key, members in groups.items():
        ordered = sorted(
            members,
            key=lambda candidate: (
                -strength_rank.get(
                    str(
                        candidate.get(
                            "causal_evidence_strength"
                        )
                        or ""
                    ),
                    0,
                ),
                -float(
                    candidate.get(
                        "causal_evidence_score"
                    )
                    or 0.0
                ),
                0
                if candidate.get(
                    "same_sentence_causal_valid"
                )
                is True
                else 1,
                0
                if candidate.get(
                    "cross_sentence_causal_valid"
                )
                is True
                else 1,
                str(
                    candidate.get(
                        "causal_candidate_id"
                    )
                    or ""
                ),
            ),
        )

        representative = ordered[
            0
        ]

        member_ids = [
            str(
                member.get(
                    "causal_candidate_id"
                )
            )
            for member in ordered
        ]

        raw_key = "|".join(
            key
        )

        group_id = (
            "causal_duplicate_group_"
            + hashlib.sha256(
                raw_key.encode(
                    "utf-8"
                )
            ).hexdigest()[
                :16
            ]
        )

        is_duplicate_group = (
            len(
                ordered
            )
            > 1
        )

        if is_duplicate_group:
            duplicate_group_count += 1

            duplicate_candidate_count += (
                len(
                    ordered
                )
                - 1
            )

        representative_id = str(
            representative.get(
                "causal_candidate_id"
            )
        )

        for index, member in enumerate(
            ordered
        ):
            member_id = str(
                member.get(
                    "causal_candidate_id"
                )
            )

            is_representative = (
                index == 0
            )

            resolved = dict(
                member
            )

            resolved.update({
                "duplicate_resolution_performed":
                    True,

                "causal_duplicate_group_id":
                    group_id,

                "causal_duplicate_group_size":
                    len(
                        ordered
                    ),

                "causal_duplicate_member_ids":
                    member_ids,

                "is_causal_duplicate_group":
                    is_duplicate_group,

                "is_representative_causal_relation":
                    is_representative,

                "representative_causal_candidate_id":
                    representative_id,

                "duplicate_of_causal_candidate_id":
                    (
                        None
                        if is_representative
                        else representative_id
                    ),

                "causal_duplicate_resolution_status":
                    (
                        "REPRESENTATIVE"
                        if is_representative
                        else "DUPLICATE_REDUNDANT"
                    ),

                "causal_duplicate_key": {
                    "cause":
                        key[
                            0
                        ],

                    "relation":
                        key[
                            1
                        ],

                    "effect":
                        key[
                            2
                        ],
                },

                "causal_direction_preserved":
                    True,

                "endpoint_order_symmetrized":
                    False,

                "different_causal_relations_merged":
                    False,

                "fuzzy_similarity_performed":
                    False,

                "causal_inference_performed":
                    False,

                "truth_assessed":
                    False,

                "external_authority_checked":
                    False,
            })

            resolved_by_id[
                member_id
            ] = resolved

            if is_representative:
                representative_candidates.append(
                    resolved
                )

    for member in non_groupable:
        member_id = str(
            member.get(
                "causal_candidate_id"
            )
        )

        resolved = dict(
            member
        )

        resolved.update({
            "duplicate_resolution_performed":
                True,

            "causal_duplicate_group_id":
                None,

            "causal_duplicate_group_size":
                1,

            "causal_duplicate_member_ids": [
                member_id,
            ],

            "is_causal_duplicate_group":
                False,

            "is_representative_causal_relation":
                True,

            "representative_causal_candidate_id":
                member_id,

            "duplicate_of_causal_candidate_id":
                None,

            "causal_duplicate_resolution_status":
                "UNIQUE_NON_GROUPABLE",

            "causal_duplicate_key":
                None,

            "causal_direction_preserved":
                True,

            "endpoint_order_symmetrized":
                False,

            "different_causal_relations_merged":
                False,

            "fuzzy_similarity_performed":
                False,

            "causal_inference_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        resolved_by_id[
            member_id
        ] = resolved

        representative_candidates.append(
            resolved
        )

    resolved_candidates = []

    for candidate in source_candidates:
        candidate_id = str(
            candidate.get(
                "causal_candidate_id"
            )
        )

        resolved = resolved_by_id.get(
            candidate_id
        )

        if resolved is None:
            raise CausalIntelligenceError(
                "Duplicate causal resolution lost a candidate."
            )

        resolved_candidates.append(
            resolved
        )

    representative_candidates.sort(
        key=lambda candidate: str(
            candidate.get(
                "causal_candidate_id"
            )
            or ""
        )
    )

    resolved_units = []

    for unit in (
        evidence_assessment_result.get(
            "causal_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every Causal Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "causal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "causal_evidence_assessment"
            )
            != "COMPLETE"
        ):
            raise CausalIntelligenceError(
                "Causal evidence assessment must be COMPLETE before Stage L."
            )

        if (
            state.get(
                "duplicate_causal_resolution"
            )
            != "PENDING"
        ):
            raise CausalIntelligenceError(
                "Duplicate causal resolution must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "cause_effect_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "causal_candidate_id"
            )

            resolved_candidate = (
                resolved_by_id.get(
                    candidate_id
                )
            )

            if resolved_candidate is None:
                raise CausalIntelligenceError(
                    "Causal candidate/unit duplicate mismatch."
                )

            unit_candidates.append(
                resolved_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "duplicate_causal_resolution"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "duplicate_causal_resolution_performed"
        ] = True

        updated_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        updated_boundaries[
            "causal_inference_performed"
        ] = False

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "external_authority_check_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "cause_effect_candidates":
                unit_candidates,

            "representative_causal_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "is_representative_causal_relation"
                    )
                    is True
                ),

            "duplicate_redundant_causal_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "causal_duplicate_resolution_status"
                    )
                    == "DUPLICATE_REDUNDANT"
                ),

            "causal_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        resolved_units.append(
            updated_unit
        )

    resolved_units_by_id = {
        unit.get(
            "causal_claim_unit_id"
        ):
            unit
        for unit in resolved_units
    }

    resolved_sections = []

    for section in (
        evidence_assessment_result.get(
            "causal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "causal_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "causal_claim_unit_id"
            )

            resolved_unit = (
                resolved_units_by_id.get(
                    unit_id
                )
            )

            if resolved_unit is None:
                raise CausalIntelligenceError(
                    "Causal section/unit duplicate mismatch."
                )

            section_units.append(
                resolved_unit
            )

        resolved_sections.append({
            **dict(
                section
            ),

            "causal_claim_units":
                section_units,

            "representative_causal_relation_count":
                sum(
                    unit.get(
                        "representative_causal_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "duplicate_redundant_causal_relation_count":
                sum(
                    unit.get(
                        "duplicate_redundant_causal_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "duplicate_causal_resolution_complete":
                True,
        })

    representative_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "is_representative_causal_relation"
        )
        is True
    )

    redundant_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "causal_duplicate_resolution_status"
        )
        == "DUPLICATE_REDUNDANT"
    )

    result = dict(
        evidence_assessment_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "duplicate_causal_resolution_performed"
    ] = True

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "causal_inference_performed"
    ] = False

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "external_authority_check_performed"
    ] = False

    boundaries[
        "quantitative_reasoning_performed"
    ] = False

    boundaries[
        "temporal_reasoning_performed"
    ] = False

    boundaries[
        "semantic_memory_write_performed"
    ] = False

    boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "causal_duplicate_resolution_v1",

        "patch":
            "4.6.8L",

        "status":
            "CAUSAL_DUPLICATE_RESOLUTION_COMPLETE",

        "causal_sections":
            resolved_sections,

        "causal_claim_units":
            resolved_units,

        "cause_effect_candidates":
            resolved_candidates,

        "representative_causal_candidates":
            representative_candidates,

        "causal_duplicate_resolution_summary": {
            "candidate_count":
                len(
                    resolved_candidates
                ),

            "representative_causal_relation_count":
                representative_count,

            "duplicate_redundant_causal_relation_count":
                redundant_count,

            "duplicate_group_count":
                duplicate_group_count,

            "duplicate_candidate_count":
                duplicate_candidate_count,

            "candidate_count_accounted_for":
                (
                    representative_count
                    + redundant_count
                    == len(
                        resolved_candidates
                    )
                ),

            "exact_canonical_key_only":
                True,

            "duplicate_key_fields": [
                "canonical_cause",
                "canonical_causal_relation",
                "canonical_effect",
            ],

            "causal_endpoint_order_preserved":
                True,

            "symmetric_endpoint_normalization_performed":
                False,

            "different_causal_relations_merged":
                False,

            "strongest_evidence_representative_selected":
                True,

            "duplicate_provenance_preserved":
                True,

            "fuzzy_similarity_performed":
                False,

            "causal_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "article_causal_consolidation",
    })

    return result



def consolidate_article_causal_intelligence_v1(
    duplicate_resolution_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Consolidate completed article-local Causal Intelligence into
    article-level and section-level summaries.

    Only representative causal relations are included in the canonical
    consolidated causal set. Full candidate provenance remains preserved
    in the complete source candidate collection.

    This stage does NOT:
    - create new causal relations,
    - infer missing causal relations,
    - infer causal chains,
    - merge different causal relation types,
    - reverse cause/effect direction,
    - strengthen causal-sensitive relation forms,
    - establish factual or scientific truth,
    - use external authority,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform fuzzy semantic similarity,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        duplicate_resolution_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "duplicate_resolution_result must be a mapping."
        )

    if (
        duplicate_resolution_result.get(
            "schema_version"
        )
        != "causal_duplicate_resolution_v1"
    ):
        raise CausalIntelligenceError(
            "Stage M requires causal_duplicate_resolution_v1."
        )

    if (
        duplicate_resolution_result.get(
            "status"
        )
        != "CAUSAL_DUPLICATE_RESOLUTION_COMPLETE"
    ):
        raise CausalIntelligenceError(
            "Duplicate causal resolution must be complete."
        )

    if (
        duplicate_resolution_result.get(
            "phase"
        )
        != "4.6.8"
    ):
        raise CausalIntelligenceError(
            "Stage M requires Phase 4.6.8 input."
        )

    if (
        duplicate_resolution_result.get(
            "patch"
        )
        != "4.6.8L"
    ):
        raise CausalIntelligenceError(
            "Stage M requires canonical 4.6.8L input."
        )

    if (
        duplicate_resolution_result.get(
            "next_stage"
        )
        != "article_causal_consolidation"
    ):
        raise CausalIntelligenceError(
            "Stage L must hand off to article_causal_consolidation."
        )

    if (
        duplicate_resolution_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence must remain transient."
        )

    source_candidates = list(
        duplicate_resolution_result.get(
            "cause_effect_candidates"
        )
        or []
    )

    representative_candidates = list(
        duplicate_resolution_result.get(
            "representative_causal_candidates"
        )
        or []
    )

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "causal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise CausalIntelligenceError(
                "Causal candidate ID is required."
            )

        if (
            candidate.get(
                "duplicate_resolution_performed"
            )
            is not True
        ):
            raise CausalIntelligenceError(
                "All causal candidates must complete duplicate resolution before Stage M."
            )

    for candidate in representative_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every representative causal relation must be a mapping."
            )

        if (
            candidate.get(
                "is_representative_causal_relation"
            )
            is not True
        ):
            raise CausalIntelligenceError(
                "Representative causal list contains a non-representative candidate."
            )

    representative_ids = {
        str(
            candidate.get(
                "causal_candidate_id"
            )
            or ""
        )
        for candidate in representative_candidates
    }

    if "" in representative_ids:
        raise CausalIntelligenceError(
            "Representative causal candidate ID is required."
        )

    expected_representative_ids = {
        str(
            candidate.get(
                "causal_candidate_id"
            )
            or ""
        )
        for candidate in source_candidates
        if candidate.get(
            "is_representative_causal_relation"
        )
        is True
    }

    if representative_ids != expected_representative_ids:
        raise CausalIntelligenceError(
            "Representative causal list does not match resolved candidates."
        )

    causal_family_counts = {}
    causal_relation_type_counts = {}

    causal_form_class_counts = {
        "STRONG_CAUSAL_FORM":
            0,

        "QUALIFIED_CAUSAL_FORM":
            0,

        "CAUSAL_SENSITIVE_FORM":
            0,

        "UNSPECIFIED":
            0,
    }

    evidence_strength_counts = {
        "STRONG":
            0,

        "MODERATE":
            0,

        "LIMITED":
            0,

        "INSUFFICIENT":
            0,
    }

    validated_count = 0
    unvalidated_count = 0

    same_sentence_validated_count = 0
    cross_sentence_validated_count = 0

    consolidated_causal_relations = []

    for candidate in representative_candidates:
        causal_family = str(
            candidate.get(
                "causal_relation_family"
            )
            or "UNSPECIFIED"
        )

        canonical_relation = str(
            candidate.get(
                "canonical_causal_relation"
            )
            or ""
        )

        causal_form_class = str(
            candidate.get(
                "causal_relation_strength_class"
            )
            or "UNSPECIFIED"
        )

        evidence_strength = str(
            candidate.get(
                "causal_evidence_strength"
            )
            or "INSUFFICIENT"
        )

        final_validated = (
            candidate.get(
                "final_causal_expression_validated"
            )
            is True
        )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_causal_valid"
            )
            is True
        )

        cross_sentence_valid = (
            candidate.get(
                "cross_sentence_causal_valid"
            )
            is True
        )

        causal_family_counts[
            causal_family
        ] = (
            causal_family_counts.get(
                causal_family,
                0,
            )
            + 1
        )

        causal_relation_type_counts[
            canonical_relation
        ] = (
            causal_relation_type_counts.get(
                canonical_relation,
                0,
            )
            + 1
        )

        causal_form_class_counts[
            causal_form_class
        ] = (
            causal_form_class_counts.get(
                causal_form_class,
                0,
            )
            + 1
        )

        evidence_strength_counts[
            evidence_strength
        ] = (
            evidence_strength_counts.get(
                evidence_strength,
                0,
            )
            + 1
        )

        if final_validated:
            validated_count += 1
        else:
            unvalidated_count += 1

        if same_sentence_valid:
            same_sentence_validated_count += 1

        if cross_sentence_valid:
            cross_sentence_validated_count += 1

        consolidated_causal_relations.append({
            "causal_candidate_id":
                candidate.get(
                    "causal_candidate_id"
                ),

            "cause_text":
                candidate.get(
                    "canonical_cause_text"
                )
                or candidate.get(
                    "cause_text"
                ),

            "canonical_causal_relation":
                candidate.get(
                    "canonical_causal_relation"
                ),

            "effect_text":
                candidate.get(
                    "canonical_effect_text"
                )
                or candidate.get(
                    "effect_text"
                ),

            "causal_relation_family":
                candidate.get(
                    "causal_relation_family"
                ),

            "causal_relation_strength_class":
                candidate.get(
                    "causal_relation_strength_class"
                ),

            "cause_effect_orientation_resolved":
                candidate.get(
                    "cause_effect_orientation_resolved"
                )
                is True,

            "orientation_type":
                candidate.get(
                    "orientation_type"
                ),

            "final_causal_expression_validated":
                final_validated,

            "same_sentence_causal_valid":
                same_sentence_valid,

            "cross_sentence_causal_valid":
                cross_sentence_valid,

            "causal_evidence_score":
                candidate.get(
                    "causal_evidence_score"
                ),

            "causal_evidence_strength":
                evidence_strength,

            "causal_evidence_basis":
                candidate.get(
                    "causal_evidence_basis"
                ),

            "causal_confidence_cap_applied":
                candidate.get(
                    "causal_confidence_cap_applied"
                ),

            "section_id":
                candidate.get(
                    "section_id"
                ),

            "sentence_id":
                candidate.get(
                    "sentence_id"
                ),

            "causal_duplicate_group_id":
                candidate.get(
                    "causal_duplicate_group_id"
                ),

            "causal_duplicate_group_size":
                candidate.get(
                    "causal_duplicate_group_size"
                ),

            "causal_direction_preserved":
                candidate.get(
                    "causal_direction_preserved"
                )
                is True,

            "causal_form_class_preserved":
                candidate.get(
                    "causal_form_class_preserved"
                )
                is True,

            "causal_sensitive_form_promoted_to_strong":
                False,

            "cross_sentence_expression_promoted_to_strong":
                False,

            "causal_inference_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

    consolidated_causal_relations.sort(
        key=lambda relation: (
            str(
                relation.get(
                    "section_id"
                )
                or ""
            ),
            str(
                relation.get(
                    "canonical_causal_relation"
                )
                or ""
            ),
            str(
                relation.get(
                    "cause_text"
                )
                or ""
            ),
            str(
                relation.get(
                    "effect_text"
                )
                or ""
            ),
            str(
                relation.get(
                    "causal_candidate_id"
                )
                or ""
            ),
        )
    )

    consolidated_sections = []

    for section in (
        duplicate_resolution_result.get(
            "causal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every causal section must be a mapping."
            )

        section_id = str(
            section.get(
                "section_id"
            )
            or ""
        )

        if not section_id:
            raise CausalIntelligenceError(
                "Causal section ID is required."
            )

        section_relations = [
            relation
            for relation in consolidated_causal_relations
            if str(
                relation.get(
                    "section_id"
                )
                or ""
            )
            == section_id
        ]

        section_family_counts = {}

        section_form_class_counts = {
            "STRONG_CAUSAL_FORM":
                0,

            "QUALIFIED_CAUSAL_FORM":
                0,

            "CAUSAL_SENSITIVE_FORM":
                0,

            "UNSPECIFIED":
                0,
        }

        section_strength_counts = {
            "STRONG":
                0,

            "MODERATE":
                0,

            "LIMITED":
                0,

            "INSUFFICIENT":
                0,
        }

        for relation in section_relations:
            family = str(
                relation.get(
                    "causal_relation_family"
                )
                or "UNSPECIFIED"
            )

            section_family_counts[
                family
            ] = (
                section_family_counts.get(
                    family,
                    0,
                )
                + 1
            )

            form_class = str(
                relation.get(
                    "causal_relation_strength_class"
                )
                or "UNSPECIFIED"
            )

            section_form_class_counts[
                form_class
            ] = (
                section_form_class_counts.get(
                    form_class,
                    0,
                )
                + 1
            )

            strength = str(
                relation.get(
                    "causal_evidence_strength"
                )
                or "INSUFFICIENT"
            )

            section_strength_counts[
                strength
            ] = (
                section_strength_counts.get(
                    strength,
                    0,
                )
                + 1
            )

        consolidated_sections.append({
            "section_id":
                section_id,

            "representative_causal_relations":
                section_relations,

            "representative_causal_relation_count":
                len(
                    section_relations
                ),

            "validated_causal_relation_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "final_causal_expression_validated"
                    )
                    is True
                ),

            "unvalidated_causal_relation_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "final_causal_expression_validated"
                    )
                    is False
                ),

            "same_sentence_validated_causal_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "same_sentence_causal_valid"
                    )
                    is True
                ),

            "cross_sentence_validated_causal_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "cross_sentence_causal_valid"
                    )
                    is True
                ),

            "causal_relation_family_counts":
                section_family_counts,

            "causal_form_class_counts":
                section_form_class_counts,

            "causal_evidence_strength_counts":
                section_strength_counts,

            "causal_consolidation_complete":
                True,
        })

    total_candidate_count = len(
        source_candidates
    )

    representative_count = len(
        representative_candidates
    )

    redundant_count = sum(
        1
        for candidate in source_candidates
        if candidate.get(
            "causal_duplicate_resolution_status"
        )
        == "DUPLICATE_REDUNDANT"
    )

    causal_sensitive_count = sum(
        1
        for relation in consolidated_causal_relations
        if relation.get(
            "causal_relation_strength_class"
        )
        == "CAUSAL_SENSITIVE_FORM"
    )

    strong_causal_form_count = sum(
        1
        for relation in consolidated_causal_relations
        if relation.get(
            "causal_relation_strength_class"
        )
        == "STRONG_CAUSAL_FORM"
    )

    qualified_causal_form_count = sum(
        1
        for relation in consolidated_causal_relations
        if relation.get(
            "causal_relation_strength_class"
        )
        == "QUALIFIED_CAUSAL_FORM"
    )

    result = dict(
        duplicate_resolution_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "article_causal_consolidation_performed"
    ] = True

    boundaries[
        "new_causal_relation_inference_performed"
    ] = False

    boundaries[
        "causal_chain_inference_performed"
    ] = False

    boundaries[
        "causal_form_strengthening_performed"
    ] = False

    boundaries[
        "cause_effect_reversal_performed"
    ] = False

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "external_authority_check_performed"
    ] = False

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "quantitative_reasoning_performed"
    ] = False

    boundaries[
        "temporal_reasoning_performed"
    ] = False

    boundaries[
        "semantic_memory_write_performed"
    ] = False

    boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "causal_article_consolidation_v1",

        "patch":
            "4.6.8M",

        "status":
            "CAUSAL_ARTICLE_CONSOLIDATION_COMPLETE",

        "consolidated_causal_sections":
            consolidated_sections,

        "consolidated_causal_relations":
            consolidated_causal_relations,

        "article_causal_summary": {
            "total_candidate_count":
                total_candidate_count,

            "representative_causal_relation_count":
                representative_count,

            "duplicate_redundant_causal_relation_count":
                redundant_count,

            "validated_causal_relation_count":
                validated_count,

            "unvalidated_causal_relation_count":
                unvalidated_count,

            "same_sentence_validated_causal_count":
                same_sentence_validated_count,

            "cross_sentence_validated_causal_count":
                cross_sentence_validated_count,

            "causal_relation_family_counts":
                causal_family_counts,

            "causal_relation_type_counts":
                causal_relation_type_counts,

            "causal_form_class_counts":
                causal_form_class_counts,

            "causal_evidence_strength_counts":
                evidence_strength_counts,

            "strong_causal_form_count":
                strong_causal_form_count,

            "qualified_causal_form_count":
                qualified_causal_form_count,

            "causal_sensitive_form_count":
                causal_sensitive_count,

            "representative_count_matches_consolidated":
                (
                    representative_count
                    == len(
                        consolidated_causal_relations
                    )
                ),

            "candidate_accounting_valid":
                (
                    representative_count
                    + redundant_count
                    == total_candidate_count
                ),

            "representatives_only_in_consolidated_set":
                True,

            "causal_direction_preserved":
                True,

            "causal_form_classes_preserved":
                True,

            "causal_sensitive_strong_promotion_performed":
                False,

            "cross_sentence_strong_promotion_performed":
                False,

            "article_local_only":
                True,

            "new_causal_relation_inference_performed":
                False,

            "causal_chain_inference_performed":
                False,

            "causal_form_strengthening_performed":
                False,

            "cause_effect_reversal_performed":
                False,

            "scientific_truth_verified":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "fuzzy_similarity_performed":
                False,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "final_causal_intelligence_result",
    })

    return result



def build_final_causal_intelligence_result_v1(
    article_consolidation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build the final canonical Phase 4.6.8 Causal Intelligence result.

    This stage packages the completed article-local causal analysis
    without adding new interpretation.

    It does NOT:
    - certify the result,
    - create or infer causal relations,
    - infer causal chains,
    - strengthen causal-sensitive forms,
    - reverse cause/effect direction,
    - establish factual or scientific truth,
    - use external authority,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform fuzzy similarity,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        article_consolidation_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "article_consolidation_result must be a mapping."
        )

    if (
        article_consolidation_result.get(
            "schema_version"
        )
        != "causal_article_consolidation_v1"
    ):
        raise CausalIntelligenceError(
            "Stage N requires causal_article_consolidation_v1."
        )

    if (
        article_consolidation_result.get(
            "status"
        )
        != "CAUSAL_ARTICLE_CONSOLIDATION_COMPLETE"
    ):
        raise CausalIntelligenceError(
            "Article causal consolidation must be complete."
        )

    if (
        article_consolidation_result.get(
            "phase"
        )
        != "4.6.8"
    ):
        raise CausalIntelligenceError(
            "Stage N requires Phase 4.6.8 input."
        )

    if (
        article_consolidation_result.get(
            "patch"
        )
        != "4.6.8M"
    ):
        raise CausalIntelligenceError(
            "Stage N requires canonical 4.6.8M input."
        )

    if (
        article_consolidation_result.get(
            "next_stage"
        )
        != "final_causal_intelligence_result"
    ):
        raise CausalIntelligenceError(
            "Stage M must hand off to final_causal_intelligence_result."
        )

    if (
        article_consolidation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence must remain transient."
        )

    consolidated_relations = list(
        article_consolidation_result.get(
            "consolidated_causal_relations"
        )
        or []
    )

    consolidated_sections = list(
        article_consolidation_result.get(
            "consolidated_causal_sections"
        )
        or []
    )

    full_candidates = list(
        article_consolidation_result.get(
            "cause_effect_candidates"
        )
        or []
    )

    representative_candidates = list(
        article_consolidation_result.get(
            "representative_causal_candidates"
        )
        or []
    )

    summary = dict(
        article_consolidation_result.get(
            "article_causal_summary"
        )
        or {}
    )

    if (
        summary.get(
            "representative_count_matches_consolidated"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Representative/consolidated causal accounting must be valid."
        )

    if (
        summary.get(
            "candidate_accounting_valid"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Candidate accounting must be valid before Stage N."
        )

    if (
        summary.get(
            "representatives_only_in_consolidated_set"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Consolidated causal set must contain representatives only."
        )

    if (
        summary.get(
            "causal_direction_preserved"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Causal direction must remain preserved."
        )

    if (
        summary.get(
            "causal_form_classes_preserved"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Causal form classes must remain preserved."
        )

    required_false_summary_fields = (
        "causal_sensitive_strong_promotion_performed",
        "cross_sentence_strong_promotion_performed",
        "new_causal_relation_inference_performed",
        "causal_chain_inference_performed",
        "causal_form_strengthening_performed",
        "cause_effect_reversal_performed",
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "fuzzy_similarity_performed",
    )

    for field_name in required_false_summary_fields:
        if (
            summary.get(
                field_name
            )
            is not False
        ):
            raise CausalIntelligenceError(
                field_name
                + " must remain False before final Causal Intelligence packaging."
            )

    for relation in consolidated_relations:
        if not isinstance(
            relation,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every consolidated causal relation must be a mapping."
            )

        if (
            relation.get(
                "causal_direction_preserved"
            )
            is not True
        ):
            raise CausalIntelligenceError(
                "Every consolidated causal relation must preserve direction."
            )

        if (
            relation.get(
                "causal_sensitive_form_promoted_to_strong"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Causal-sensitive forms must not be promoted to STRONG."
            )

        if (
            relation.get(
                "cross_sentence_expression_promoted_to_strong"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Cross-sentence causal expressions must not be promoted to STRONG."
            )

        if (
            relation.get(
                "causal_inference_performed"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Final Causal Intelligence must not add causal inference."
            )

        if (
            relation.get(
                "truth_assessed"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Causal Intelligence must not assess factual truth."
            )

        if (
            relation.get(
                "external_authority_checked"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Causal Intelligence must not use external authority."
            )

    boundaries = dict(
        article_consolidation_result.get(
            "processing_boundaries"
        )
        or {}
    )

    required_false_boundaries = (
        "new_causal_relation_inference_performed",
        "causal_chain_inference_performed",
        "causal_form_strengthening_performed",
        "cause_effect_reversal_performed",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "fuzzy_similarity_performed",
        "quantitative_reasoning_performed",
        "temporal_reasoning_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for boundary_name in required_false_boundaries:
        if (
            boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise CausalIntelligenceError(
                boundary_name
                + " must remain False in final Causal Intelligence."
            )

    if (
        boundaries.get(
            "article_causal_consolidation_performed"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Article causal consolidation boundary must be complete."
        )

    final_boundaries = dict(
        boundaries
    )

    final_boundaries[
        "final_causal_result_built"
    ] = True

    final_boundaries[
        "causal_certification_performed"
    ] = False

    result = {
        "schema_version":
            "causal_intelligence_result_v1",

        "causal_intelligence_version":
            article_consolidation_result.get(
                "causal_intelligence_version"
            )
            or "causal_intelligence_v1",

        "phase":
            "4.6.8",

        "patch":
            "4.6.8N",

        "status":
            "CAUSAL_INTELLIGENCE_RESULT_COMPLETE",

        "article_identity": {
            "article_id":
                article_consolidation_result.get(
                    "article_id"
                ),

            "workspace_id":
                article_consolidation_result.get(
                    "workspace_id"
                ),

            "source_type":
                article_consolidation_result.get(
                    "source_type"
                ),

            "source_id":
                article_consolidation_result.get(
                    "source_id"
                ),

            "document_id":
                article_consolidation_result.get(
                    "document_id"
                ),

            "content_hash":
                article_consolidation_result.get(
                    "content_hash"
                ),

            "body_ref":
                article_consolidation_result.get(
                    "body_ref"
                ),

            "title":
                article_consolidation_result.get(
                    "title"
                ),
        },

        "consolidated_causal_relations":
            consolidated_relations,

        "consolidated_causal_sections":
            consolidated_sections,

        "representative_causal_candidates":
            representative_candidates,

        "cause_effect_candidates":
            full_candidates,

        "causal_claim_units":
            list(
                article_consolidation_result.get(
                    "causal_claim_units"
                )
                or []
            ),

        "article_causal_summary":
            summary,

        "causal_boundaries": {
            "article_local_only":
                True,

            "scientific_truth_verified":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_checked":
                False,

            "new_causal_relation_inference_performed":
                False,

            "causal_chain_inference_performed":
                False,

            "causal_form_strengthening_performed":
                False,

            "cause_effect_reversal_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "linking_decisions_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,
        },

        "processing_boundaries":
            final_boundaries,

        "certification": {
            "performed":
                False,

            "certified":
                False,

            "certification_stage":
                "4.6.8O",
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "causal_intelligence_certification",
    }

    return result



def certify_causal_intelligence_v1(
    final_causal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Certify the final Phase 4.6.8 Causal Intelligence result.

    Certification validates structure, accounting, provenance,
    causal-direction integrity, causal-form integrity, boundaries,
    and handoff readiness.

    Certification does NOT:
    - create or infer causal relations,
    - infer causal chains,
    - strengthen causal-sensitive forms,
    - reverse cause/effect direction,
    - establish factual or scientific truth,
    - use external authority,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform fuzzy similarity,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        final_causal_result,
        Mapping,
    ):
        raise CausalIntelligenceError(
            "final_causal_result must be a mapping."
        )

    if (
        final_causal_result.get(
            "schema_version"
        )
        != "causal_intelligence_result_v1"
    ):
        raise CausalIntelligenceError(
            "Stage O requires causal_intelligence_result_v1."
        )

    if (
        final_causal_result.get(
            "status"
        )
        != "CAUSAL_INTELLIGENCE_RESULT_COMPLETE"
    ):
        raise CausalIntelligenceError(
            "Final Causal Intelligence result must be complete."
        )

    if (
        final_causal_result.get(
            "phase"
        )
        != "4.6.8"
    ):
        raise CausalIntelligenceError(
            "Stage O requires Phase 4.6.8 input."
        )

    if (
        final_causal_result.get(
            "patch"
        )
        != "4.6.8N"
    ):
        raise CausalIntelligenceError(
            "Stage O requires canonical 4.6.8N input."
        )

    if (
        final_causal_result.get(
            "next_stage"
        )
        != "causal_intelligence_certification"
    ):
        raise CausalIntelligenceError(
            "Stage N must hand off to causal_intelligence_certification."
        )

    if (
        final_causal_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CausalIntelligenceError(
            "Causal Intelligence must remain transient."
        )

    identity = dict(
        final_causal_result.get(
            "article_identity"
        )
        or {}
    )

    required_identity_fields = (
        "article_id",
        "workspace_id",
        "source_type",
        "content_hash",
        "body_ref",
    )

    for field in required_identity_fields:
        if not str(
            identity.get(
                field
            )
            or ""
        ).strip():
            raise CausalIntelligenceError(
                "Required article identity field missing: "
                + field
            )

    consolidated_relations = list(
        final_causal_result.get(
            "consolidated_causal_relations"
        )
        or []
    )

    representative_candidates = list(
        final_causal_result.get(
            "representative_causal_candidates"
        )
        or []
    )

    full_candidates = list(
        final_causal_result.get(
            "cause_effect_candidates"
        )
        or []
    )

    claim_units = list(
        final_causal_result.get(
            "causal_claim_units"
        )
        or []
    )

    consolidated_sections = list(
        final_causal_result.get(
            "consolidated_causal_sections"
        )
        or []
    )

    summary = dict(
        final_causal_result.get(
            "article_causal_summary"
        )
        or {}
    )

    if (
        summary.get(
            "representative_count_matches_consolidated"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Representative/consolidated causal accounting is invalid."
        )

    if (
        summary.get(
            "candidate_accounting_valid"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Causal candidate accounting is invalid."
        )

    if (
        summary.get(
            "representatives_only_in_consolidated_set"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Consolidated causal set must contain representatives only."
        )

    if (
        summary.get(
            "causal_direction_preserved"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Causal direction preservation must be verified."
        )

    if (
        summary.get(
            "causal_form_classes_preserved"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Causal form classes must remain preserved."
        )

    if (
        summary.get(
            "representative_causal_relation_count"
        )
        != len(
            consolidated_relations
        )
    ):
        raise CausalIntelligenceError(
            "Consolidated causal relation count does not match summary."
        )

    if (
        len(
            representative_candidates
        )
        != len(
            consolidated_relations
        )
    ):
        raise CausalIntelligenceError(
            "Representative candidate count does not match consolidated causal relations."
        )

    if (
        summary.get(
            "total_candidate_count"
        )
        != len(
            full_candidates
        )
    ):
        raise CausalIntelligenceError(
            "Full causal candidate count does not match summary."
        )

    consolidated_ids = [
        str(
            relation.get(
                "causal_candidate_id"
            )
            or ""
        )
        for relation in consolidated_relations
    ]

    representative_ids = [
        str(
            candidate.get(
                "causal_candidate_id"
            )
            or ""
        )
        for candidate in representative_candidates
    ]

    if any(
        not candidate_id
        for candidate_id in consolidated_ids
    ):
        raise CausalIntelligenceError(
            "Every consolidated causal relation requires a candidate ID."
        )

    if (
        set(
            consolidated_ids
        )
        != set(
            representative_ids
        )
    ):
        raise CausalIntelligenceError(
            "Consolidated causal relations and representative candidates disagree."
        )

    if (
        len(
            consolidated_ids
        )
        != len(
            set(
                consolidated_ids
            )
        )
    ):
        raise CausalIntelligenceError(
            "Duplicate consolidated causal candidate IDs are not allowed."
        )

    strong_sensitive_count = 0
    strong_cross_sentence_count = 0

    for relation in consolidated_relations:
        if not isinstance(
            relation,
            Mapping,
        ):
            raise CausalIntelligenceError(
                "Every consolidated causal relation must be a mapping."
            )

        if (
            relation.get(
                "causal_direction_preserved"
            )
            is not True
        ):
            raise CausalIntelligenceError(
                "Every consolidated causal relation must preserve cause/effect direction."
            )

        if (
            relation.get(
                "causal_sensitive_form_promoted_to_strong"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Causal-sensitive forms must not be promoted to STRONG."
            )

        if (
            relation.get(
                "cross_sentence_expression_promoted_to_strong"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Cross-sentence causal expressions must not be promoted to STRONG."
            )

        if (
            relation.get(
                "causal_inference_performed"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Final Causal Intelligence must not add causal inference."
            )

        if (
            relation.get(
                "truth_assessed"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Causal Intelligence must not assess factual truth."
            )

        if (
            relation.get(
                "external_authority_checked"
            )
            is not False
        ):
            raise CausalIntelligenceError(
                "Causal Intelligence must not use external authority."
            )

        if (
            relation.get(
                "causal_relation_strength_class"
            )
            == "CAUSAL_SENSITIVE_FORM"
            and relation.get(
                "causal_evidence_strength"
            )
            == "STRONG"
        ):
            strong_sensitive_count += 1

        if (
            relation.get(
                "cross_sentence_causal_valid"
            )
            is True
            and relation.get(
                "causal_evidence_strength"
            )
            == "STRONG"
        ):
            strong_cross_sentence_count += 1

    if strong_sensitive_count != 0:
        raise CausalIntelligenceError(
            "CAUSAL_SENSITIVE_FORM must never certify with STRONG evidence."
        )

    if strong_cross_sentence_count != 0:
        raise CausalIntelligenceError(
            "Cross-sentence causal expressions must never certify with STRONG evidence."
        )

    causal_boundaries = dict(
        final_causal_result.get(
            "causal_boundaries"
        )
        or {}
    )

    if (
        causal_boundaries.get(
            "article_local_only"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Final Causal Intelligence must remain article-local."
        )

    required_false_causal_boundaries = (
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_checked",
        "new_causal_relation_inference_performed",
        "causal_chain_inference_performed",
        "causal_form_strengthening_performed",
        "cause_effect_reversal_performed",
        "fuzzy_similarity_performed",
        "quantitative_reasoning_performed",
        "temporal_reasoning_performed",
        "linking_decisions_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for boundary_name in required_false_causal_boundaries:
        if (
            causal_boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise CausalIntelligenceError(
                boundary_name
                + " must remain False."
            )

    processing_boundaries = dict(
        final_causal_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        processing_boundaries.get(
            "article_causal_consolidation_performed"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Article causal consolidation must be complete."
        )

    if (
        processing_boundaries.get(
            "final_causal_result_built"
        )
        is not True
    ):
        raise CausalIntelligenceError(
            "Final Causal Intelligence result must already be built."
        )

    if (
        processing_boundaries.get(
            "causal_certification_performed"
        )
        is not False
    ):
        raise CausalIntelligenceError(
            "Input must not already be certified."
        )

    certification = dict(
        final_causal_result.get(
            "certification"
        )
        or {}
    )

    if (
        certification.get(
            "performed"
        )
        is not False
        or certification.get(
            "certified"
        )
        is not False
        or certification.get(
            "certification_stage"
        )
        != "4.6.8O"
    ):
        raise CausalIntelligenceError(
            "Stage N certification state is invalid."
        )

    if (
        summary.get(
            "causal_sensitive_strong_promotion_performed"
        )
        is not False
    ):
        raise CausalIntelligenceError(
            "Causal-sensitive STRONG promotion must remain prohibited."
        )

    if (
        summary.get(
            "cross_sentence_strong_promotion_performed"
        )
        is not False
    ):
        raise CausalIntelligenceError(
            "Cross-sentence STRONG promotion must remain prohibited."
        )

    if (
        summary.get(
            "scientific_truth_verified"
        )
        is not False
    ):
        raise CausalIntelligenceError(
            "Scientific truth must not be claimed by Causal Intelligence."
        )

    certified_processing_boundaries = dict(
        processing_boundaries
    )

    certified_processing_boundaries[
        "causal_certification_performed"
    ] = True

    certified_processing_boundaries[
        "causal_intelligence_certified"
    ] = True

    result = dict(
        final_causal_result
    )

    result.update({
        "schema_version":
            "certified_causal_intelligence_result_v1",

        "patch":
            "4.6.8O",

        "status":
            "CAUSAL_INTELLIGENCE_CERTIFIED",

        "processing_boundaries":
            certified_processing_boundaries,

        "certification": {
            "performed":
                True,

            "certified":
                True,

            "certification_stage":
                "4.6.8O",

            "certification_scope":
                "ARTICLE_LOCAL_CAUSAL_INTELLIGENCE",

            "structural_integrity_verified":
                True,

            "candidate_accounting_verified":
                True,

            "representative_causal_integrity_verified":
                True,

            "provenance_preserved":
                True,

            "causal_direction_integrity_verified":
                True,

            "causal_form_class_integrity_verified":
                True,

            "causal_sensitive_strength_cap_verified":
                True,

            "cross_sentence_strength_cap_verified":
                True,

            "boundary_integrity_verified":
                True,

            "scientific_truth_verified":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "causal_chain_inference_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,
        },

        "causal_certification_summary": {
            "article_id":
                identity.get(
                    "article_id"
                ),

            "candidate_count":
                len(
                    full_candidates
                ),

            "claim_unit_count":
                len(
                    claim_units
                ),

            "section_count":
                len(
                    consolidated_sections
                ),

            "representative_causal_relation_count":
                len(
                    representative_candidates
                ),

            "consolidated_causal_relation_count":
                len(
                    consolidated_relations
                ),

            "validated_causal_relation_count":
                summary.get(
                    "validated_causal_relation_count"
                ),

            "unvalidated_causal_relation_count":
                summary.get(
                    "unvalidated_causal_relation_count"
                ),

            "strong_causal_form_count":
                summary.get(
                    "strong_causal_form_count"
                ),

            "qualified_causal_form_count":
                summary.get(
                    "qualified_causal_form_count"
                ),

            "causal_sensitive_form_count":
                summary.get(
                    "causal_sensitive_form_count"
                ),

            "causal_sensitive_strong_count":
                strong_sensitive_count,

            "cross_sentence_strong_count":
                strong_cross_sentence_count,

            "causal_direction_preserved":
                True,

            "article_local_only":
                True,

            "scientific_truth_verified":
                False,

            "certification_passed":
                True,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "quantitative_intelligence",
    })

    return result
