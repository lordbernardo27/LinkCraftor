from __future__ import annotations

from typing import Any, Mapping


RELATIONAL_INTELLIGENCE_VERSION = "relational_intelligence_v1"


class RelationalIntelligenceError(ValueError):
    pass


def validate_relational_intelligence_intake_v1(
    certified_logical_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate the canonical Phase 4.6.7 Relational Intelligence intake.

    This stage validates upstream readiness only.

    It does NOT:
    - infer semantic relations,
    - create subject-relation-object mappings,
    - perform causal reasoning,
    - assess factual truth,
    - use external authority,
    - perform linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        certified_logical_result,
        Mapping,
    ):
        raise RelationalIntelligenceError(
            "certified_logical_result must be a mapping."
        )

    if (
        certified_logical_result.get(
            "schema_version"
        )
        != "certified_logical_intelligence_result_v1"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence requires "
            "certified_logical_intelligence_result_v1."
        )

    if (
        certified_logical_result.get(
            "status"
        )
        != "LOGICAL_INTELLIGENCE_CERTIFIED"
    ):
        raise RelationalIntelligenceError(
            "Logical Intelligence must be certified before "
            "Relational Intelligence intake."
        )

    if (
        certified_logical_result.get(
            "phase"
        )
        != "4.6.6"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence intake requires Phase 4.6.6 output."
        )

    if (
        certified_logical_result.get(
            "patch"
        )
        != "4.6.6O"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence intake requires the certified O-stage result."
        )

    if (
        certified_logical_result.get(
            "next_stage"
        )
        != "relational_intelligence"
    ):
        raise RelationalIntelligenceError(
            "Certified Logical Intelligence must hand off to relational_intelligence."
        )

    if (
        certified_logical_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence intake must remain article-local transient intelligence."
        )

    certification = dict(
        certified_logical_result.get(
            "logical_intelligence_certification"
        )
        or {}
    )

    if (
        certification.get(
            "certified"
        )
        is not True
    ):
        raise RelationalIntelligenceError(
            "Logical Intelligence certification must be successful."
        )

    if (
        certification.get(
            "certification_status"
        )
        != "CERTIFIED"
    ):
        raise RelationalIntelligenceError(
            "Logical Intelligence certification status must be CERTIFIED."
        )

    boundaries = dict(
        certified_logical_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "logical_intelligence_certification_performed"
        )
        is not True
    ):
        raise RelationalIntelligenceError(
            "Logical Intelligence certification boundary must be complete."
        )

    forbidden_boundary_fields = (
        "causal_reasoning_performed",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for field in forbidden_boundary_fields:
        if (
            boundaries.get(
                field
            )
            is not False
        ):
            raise RelationalIntelligenceError(
                "Forbidden upstream work detected: "
                + field
            )

    logical_units = list(
        certified_logical_result.get(
            "logical_claim_units"
        )
        or []
    )

    if not logical_units:
        raise RelationalIntelligenceError(
            "Certified Logical Claim Units are required."
        )

    logical_sections = list(
        certified_logical_result.get(
            "consolidated_logical_sections"
        )
        or []
    )

    if not logical_sections:
        raise RelationalIntelligenceError(
            "Certified consolidated logical sections are required."
        )

    identity_fields = (
        "article_id",
        "workspace_id",
        "source_type",
        "source_id",
        "document_id",
        "content_hash",
        "title",
    )

    identity = {
        field:
            certified_logical_result.get(
                field
            )
        for field in identity_fields
    }

    return {
        "schema_version":
            "relational_intelligence_intake_v1",

        "relational_intelligence_version":
            RELATIONAL_INTELLIGENCE_VERSION,

        "phase":
            "4.6.7",

        "patch":
            "4.6.7B",

        "status":
            "RELATIONAL_INTELLIGENCE_INTAKE_ACCEPTED",

        **identity,

        "logical_claim_unit_count":
            len(
                logical_units
            ),

        "logical_section_count":
            len(
                logical_sections
            ),

        "upstream_schema_version":
            certified_logical_result.get(
                "schema_version"
            ),

        "upstream_status":
            certified_logical_result.get(
                "status"
            ),

        "article_local_only":
            True,

        "truth_assessment_performed":
            False,

        "causal_reasoning_performed":
            False,

        "external_authority_check_performed":
            False,

        "semantic_memory_write_performed":
            False,

        "persistence_performed":
            False,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "relational_claim_unit_preparation",
    }



def build_relational_claim_units_v1(
    certified_logical_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build canonical Phase 4.6.7 Relational Claim Units from
    certified Phase 4.6.6 Logical Intelligence.

    This is a one-to-one structural preparation stage.

    It does NOT:
    - infer semantic relations,
    - assign relation types,
    - create subject-relation-object triples,
    - perform causal reasoning,
    - assess factual truth,
    - use external authority,
    - perform linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    intake = validate_relational_intelligence_intake_v1(
        certified_logical_result
    )

    if (
        intake.get("status")
        != "RELATIONAL_INTELLIGENCE_INTAKE_ACCEPTED"
    ):
        raise RelationalIntelligenceError(
            "Canonical Relational Intelligence intake "
            "was not accepted."
        )

    logical_units = list(
        certified_logical_result.get(
            "logical_claim_units"
        )
        or []
    )

    logical_sections = list(
        certified_logical_result.get(
            "consolidated_logical_sections"
        )
        or []
    )

    article_id = str(
        certified_logical_result.get(
            "article_id"
        )
        or ""
    )

    relational_units = []
    relational_sections = []

    seen_relational_ids = set()
    seen_logical_ids = set()
    seen_statement_ids = set()
    seen_sentence_ids = set()

    previous_global_index = None

    units_by_section = {}

    for logical_unit in logical_units:
        if not isinstance(
            logical_unit,
            Mapping,
        ):
            raise RelationalIntelligenceError(
                "Every certified Logical Claim Unit "
                "must be a mapping."
            )

        logical_claim_unit_id = str(
            logical_unit.get(
                "logical_claim_unit_id"
            )
            or ""
        )

        statement_id = str(
            logical_unit.get(
                "statement_evidence_id"
            )
            or ""
        )

        sentence_id = str(
            logical_unit.get(
                "sentence_id"
            )
            or ""
        )

        section_id = str(
            logical_unit.get(
                "section_id"
            )
            or ""
        )

        if not logical_claim_unit_id:
            raise RelationalIntelligenceError(
                "Logical Claim Unit ID is required."
            )

        if not logical_claim_unit_id.startswith(
            "logical_claim_"
        ):
            raise RelationalIntelligenceError(
                "Unexpected Logical Claim Unit ID format."
            )

        if not statement_id:
            raise RelationalIntelligenceError(
                "statement_evidence_id is required."
            )

        if not sentence_id:
            raise RelationalIntelligenceError(
                "sentence_id is required."
            )

        if not section_id:
            raise RelationalIntelligenceError(
                "section_id is required."
            )

        if logical_claim_unit_id in seen_logical_ids:
            raise RelationalIntelligenceError(
                "Duplicate Logical Claim Unit ID."
            )

        if statement_id in seen_statement_ids:
            raise RelationalIntelligenceError(
                "Duplicate statement_evidence_id."
            )

        if sentence_id in seen_sentence_ids:
            raise RelationalIntelligenceError(
                "Duplicate sentence_id."
            )

        if (
            logical_unit.get(
                "article_id"
            )
            != article_id
        ):
            raise RelationalIntelligenceError(
                "Logical Claim Unit article identity mismatch."
            )

        global_index = logical_unit.get(
            "sentence_global_index"
        )

        article_position = logical_unit.get(
            "article_position"
        )

        if not isinstance(
            global_index,
            int,
        ):
            raise RelationalIntelligenceError(
                "sentence_global_index must be an integer."
            )

        if not isinstance(
            article_position,
            int,
        ):
            raise RelationalIntelligenceError(
                "article_position must be an integer."
            )

        if (
            previous_global_index is not None
            and global_index <= previous_global_index
        ):
            raise RelationalIntelligenceError(
                "Certified Logical Claim Units are not "
                "in canonical sentence order."
            )

        logical_state = dict(
            logical_unit.get(
                "logical_analysis_state"
            )
            or {}
        )

        if (
            logical_state.get(
                "logical_tension_detection"
            )
            != "COMPLETE"
        ):
            raise RelationalIntelligenceError(
                "Logical Claim Unit analysis is incomplete."
            )

        relational_claim_unit_id = (
            "relational_claim_"
            + logical_claim_unit_id[
                len("logical_claim_"):
            ]
        )

        if relational_claim_unit_id in seen_relational_ids:
            raise RelationalIntelligenceError(
                "Duplicate Relational Claim Unit ID."
            )

        upstream_boundaries = dict(
            logical_unit.get(
                "processing_boundaries"
            )
            or {}
        )

        relational_unit = {
            "relational_claim_unit_id":
                relational_claim_unit_id,

            "upstream_logical_claim_unit_id":
                logical_claim_unit_id,

            "statement_evidence_id":
                statement_id,

            "sentence_id":
                sentence_id,

            "article_id":
                article_id,

            "section_id":
                section_id,

            "section_evidence_unit_id":
                logical_unit.get(
                    "section_evidence_unit_id"
                ),

            "section_index":
                logical_unit.get(
                    "section_index"
                ),

            "section_title":
                logical_unit.get(
                    "section_title"
                ),

            "heading_level":
                logical_unit.get(
                    "heading_level"
                ),

            "block_id":
                logical_unit.get(
                    "block_id"
                ),

            "paragraph_id":
                logical_unit.get(
                    "paragraph_id"
                ),

            "block_type":
                logical_unit.get(
                    "block_type"
                ),

            "block_index":
                logical_unit.get(
                    "block_index"
                ),

            "sentence_index":
                logical_unit.get(
                    "sentence_index"
                ),

            "sentence_global_index":
                global_index,

            "article_position":
                article_position,

            "claim_index_in_section":
                logical_unit.get(
                    "claim_index_in_section"
                ),

            "text":
                logical_unit.get(
                    "text"
                ),

            "word_count":
                logical_unit.get(
                    "word_count"
                ),

            "character_count":
                logical_unit.get(
                    "character_count"
                ),

            "statement_form":
                logical_unit.get(
                    "statement_form"
                ),

            "canonical_claim_candidate":
                logical_unit.get(
                    "canonical_claim_candidate"
                )
                is True,

            "evidence_context":
                dict(
                    logical_unit.get(
                        "evidence_context"
                    )
                    or {}
                ),

            "upstream_logical_analysis_state":
                logical_state,

            "upstream_logical_processing_boundaries":
                upstream_boundaries,

            "relational_analysis_state": {
                "relational_signal_interpretation":
                    "PENDING",

                "subject_relation_object_extraction":
                    "PENDING",

                "entity_concept_grounding":
                    "PENDING",

                "relation_normalization":
                    "PENDING",

                "directionality_resolution":
                    "PENDING",

                "same_sentence_validation":
                    "PENDING",

                "cross_sentence_validation":
                    "PENDING",

                "relation_evidence_assessment":
                    "PENDING",

                "duplicate_relation_resolution":
                    "PENDING",
            },

            "processing_boundaries": {
                "article_local_only":
                    True,

                "relational_claim_unit_prepared":
                    True,

                "relational_signal_interpretation_performed":
                    False,

                "semantic_relation_inference_performed":
                    False,

                "subject_relation_object_mapping_performed":
                    False,

                "causal_reasoning_performed":
                    False,

                "truth_assessment_performed":
                    False,

                "external_authority_check_performed":
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

        relational_units.append(
            relational_unit
        )

        units_by_section.setdefault(
            section_id,
            [],
        ).append(
            relational_unit
        )

        seen_relational_ids.add(
            relational_claim_unit_id
        )

        seen_logical_ids.add(
            logical_claim_unit_id
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

    for logical_section in logical_sections:
        section_id = str(
            logical_section.get(
                "section_id"
            )
            or ""
        )

        if not section_id:
            raise RelationalIntelligenceError(
                "Certified logical section has no section_id."
            )

        if (
            logical_section.get(
                "logical_analysis_complete"
            )
            is not True
        ):
            raise RelationalIntelligenceError(
                "Certified logical section is incomplete."
            )

        section_relational_units = list(
            units_by_section.get(
                section_id,
                []
            )
        )

        relational_sections.append({
            "section_id":
                section_id,

            "section_index":
                logical_section.get(
                    "section_index"
                ),

            "section_title":
                logical_section.get(
                    "section_title"
                ),

            "heading_level":
                logical_section.get(
                    "heading_level"
                ),

            "upstream_logical_claim_count":
                logical_section.get(
                    "logical_claim_count"
                ),

            "relational_claim_unit_count":
                len(
                    section_relational_units
                ),

            "relational_claim_units":
                section_relational_units,
        })

    if (
        len(relational_units)
        != len(logical_units)
    ):
        raise RelationalIntelligenceError(
            "Relational Claim Unit construction must "
            "remain one-to-one with Logical Claim Units."
        )

    if (
        len(relational_sections)
        != len(logical_sections)
    ):
        raise RelationalIntelligenceError(
            "Relational section count must match "
            "certified logical section count."
        )

    return {
        "schema_version":
            "relational_claim_units_v1",

        "relational_intelligence_version":
            RELATIONAL_INTELLIGENCE_VERSION,

        "phase":
            "4.6.7",

        "patch":
            "4.6.7C",

        "status":
            "RELATIONAL_CLAIM_UNITS_PREPARED",

        "workspace_id":
            certified_logical_result.get(
                "workspace_id"
            ),

        "document_id":
            certified_logical_result.get(
                "document_id"
            ),

        "source_type":
            certified_logical_result.get(
                "source_type"
            ),

        "source_id":
            certified_logical_result.get(
                "source_id"
            ),

        "content_hash":
            certified_logical_result.get(
                "content_hash"
            ),

        "body_ref":
            certified_logical_result.get(
                "body_ref"
            ),

        "article_id":
            article_id,

        "title":
            certified_logical_result.get(
                "title"
            ),

        "logical_claim_unit_count":
            len(
                logical_units
            ),

        "relational_claim_unit_count":
            len(
                relational_units
            ),

        "section_count":
            len(
                relational_sections
            ),

        "relational_sections":
            relational_sections,

        "relational_claim_units":
            relational_units,

        "construction_summary": {
            "source_logical_claim_unit_count":
                len(
                    logical_units
                ),

            "relational_claim_unit_count":
                len(
                    relational_units
                ),

            "one_to_one_logical_mapping":
                (
                    len(relational_units)
                    == len(logical_units)
                ),

            "canonical_order_preserved":
                True,

            "canonical_text_preserved":
                True,

            "evidence_context_preserved":
                True,

            "logical_context_preserved":
                True,

            "semantic_relations_inferred":
                False,
        },

        "processing_boundaries": {
            "article_body_reparsed":
                False,

            "relational_claim_units_prepared":
                True,

            "relational_signal_interpretation_performed":
                False,

            "semantic_relation_inference_performed":
                False,

            "subject_relation_object_mapping_performed":
                False,

            "causal_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
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

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "explicit_relational_signal_interpretation",
    }



def interpret_relational_signals_v1(
    relational_claim_units_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Interpret explicit article-local relational language in
    canonical Relational Claim Units.

    Signals are candidates only.

    This stage does NOT:
    - infer a semantic relation,
    - create subject-relation-object triples,
    - determine relation direction,
    - perform causal reasoning,
    - assess factual truth,
    - use external authority,
    - perform linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        relational_claim_units_result,
        Mapping,
    ):
        raise RelationalIntelligenceError(
            "relational_claim_units_result must be a mapping."
        )

    if (
        relational_claim_units_result.get(
            "schema_version"
        )
        != "relational_claim_units_v1"
    ):
        raise RelationalIntelligenceError(
            "Stage D requires relational_claim_units_v1."
        )

    if (
        relational_claim_units_result.get(
            "status"
        )
        != "RELATIONAL_CLAIM_UNITS_PREPARED"
    ):
        raise RelationalIntelligenceError(
            "Relational Claim Units must be prepared before "
            "signal interpretation."
        )

    if (
        relational_claim_units_result.get(
            "phase"
        )
        != "4.6.7"
    ):
        raise RelationalIntelligenceError(
            "Stage D requires Phase 4.6.7 input."
        )

    if (
        relational_claim_units_result.get(
            "patch"
        )
        != "4.6.7C"
    ):
        raise RelationalIntelligenceError(
            "Stage D requires canonical 4.6.7C input."
        )

    if (
        relational_claim_units_result.get(
            "next_stage"
        )
        != "explicit_relational_signal_interpretation"
    ):
        raise RelationalIntelligenceError(
            "Stage C must hand off to explicit relational "
            "signal interpretation."
        )

    if (
        relational_claim_units_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence must remain transient."
        )

    patterns = (
        (
            "TRACK_OR_MEASURE",
            re.compile(
                r"\b(?:track|tracks|tracked|tracking|"
                r"measure|measures|measured|measuring)\b",
                re.IGNORECASE,
            ),
        ),

        (
            "USE_OR_USED_FOR",
            re.compile(
                r"\b(?:use|uses|used|using)\b",
                re.IGNORECASE,
            ),
        ),

        (
            "INCLUDE_OR_CONTAIN",
            re.compile(
                r"\b(?:include|includes|included|including|"
                r"contain|contains|contained|containing)\b",
                re.IGNORECASE,
            ),
        ),

        (
            "PART_OF",
            re.compile(
                r"\b(?:part of|component of|consists of|"
                r"composed of|made up of)\b",
                re.IGNORECASE,
            ),
        ),

        (
            "BASED_ON_OR_DERIVED_FROM",
            re.compile(
                r"\b(?:based on|derived from)\b",
                re.IGNORECASE,
            ),
        ),

        (
            "REPRESENT_OR_INDICATE",
            re.compile(
                r"\b(?:represent|represents|represented|"
                r"indicate|indicates|indicated)\b",
                re.IGNORECASE,
            ),
        ),

        (
            "ASSOCIATED_OR_RELATED",
            re.compile(
                r"\b(?:associated with|related to|"
                r"linked to|connected to)\b",
                re.IGNORECASE,
            ),
        ),

        (
            "DEPEND_OR_REQUIRE",
            re.compile(
                r"\b(?:depend on|depends on|dependent on|"
                r"require|requires|required)\b",
                re.IGNORECASE,
            ),
        ),

        (
            "PRODUCE_OR_PROVIDE",
            re.compile(
                r"\b(?:produce|produces|produced|producing|"
                r"provide|provides|provided|providing)\b",
                re.IGNORECASE,
            ),
        ),

        (
            "COMPARE",
            re.compile(
                r"\b(?:compare|compares|compared|comparing)\b",
                re.IGNORECASE,
            ),
        ),

        (
            "AFFECT_OR_INFLUENCE",
            re.compile(
                r"\b(?:affect|affects|affected|affecting|"
                r"influence|influences|influenced|influencing)\b",
                re.IGNORECASE,
            ),
        ),

        (
            "NAMED_OR_DEFINED",
            re.compile(
                r"\b(?:called|known as|defined as|"
                r"refers to)\b",
                re.IGNORECASE,
            ),
        ),

        (
            "EXPLICIT_CLASSIFICATION",
            re.compile(
                r"\b(?:is|are|was|were)\s+"
                r"(?:an?|the)\s+"
                r"[A-Za-z][A-Za-z0-9'-]*",
                re.IGNORECASE,
            ),
        ),
    )

    source_units = list(
        relational_claim_units_result.get(
            "relational_claim_units"
        )
        or []
    )

    if not source_units:
        raise RelationalIntelligenceError(
            "Relational Claim Units are required."
        )

    interpreted_units = []
    signal_records = []

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise RelationalIntelligenceError(
                "Every Relational Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "relational_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "relational_signal_interpretation"
            )
            != "PENDING"
        ):
            raise RelationalIntelligenceError(
                "Relational signal interpretation must be PENDING."
            )

        claim_text = str(
            unit.get(
                "text"
            )
            or ""
        ).strip()

        unit_id = str(
            unit.get(
                "relational_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise RelationalIntelligenceError(
                "Relational Claim Unit ID is required."
            )

        signals = []

        for signal_type, pattern in patterns:
            for match in pattern.finditer(
                claim_text
            ):
                signal = {
                    "signal_type":
                        signal_type,

                    "matched_text":
                        match.group(0),

                    "character_start":
                        match.start(),

                    "character_end":
                        match.end(),

                    "explicit_text_signal":
                        True,

                    "relation_inferred":
                        False,

                    "truth_assessed":
                        False,

                    "causal_reasoning_performed":
                        False,
                }

                signals.append(
                    signal
                )

                signal_records.append({
                    "relational_claim_unit_id":
                        unit_id,

                    "statement_evidence_id":
                        unit.get(
                            "statement_evidence_id"
                        ),

                    "sentence_id":
                        unit.get(
                            "sentence_id"
                        ),

                    "section_id":
                        unit.get(
                            "section_id"
                        ),

                    "sentence_global_index":
                        unit.get(
                            "sentence_global_index"
                        ),

                    **signal,
                })

        updated_state = dict(
            state
        )

        updated_state[
            "relational_signal_interpretation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "relational_signal_interpretation_performed"
        ] = True

        updated_boundaries[
            "semantic_relation_inference_performed"
        ] = False

        updated_boundaries[
            "subject_relation_object_mapping_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "relational_signals":
                signals,

            "relational_signal_count":
                len(
                    signals
                ),

            "has_explicit_relational_signal":
                bool(
                    signals
                ),

            "relational_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        interpreted_units.append(
            updated_unit
        )

    source_sections = list(
        relational_claim_units_result.get(
            "relational_sections"
        )
        or []
    )

    interpreted_by_id = {
        unit.get(
            "relational_claim_unit_id"
        ):
            unit
        for unit in interpreted_units
    }

    interpreted_sections = []

    for section in source_sections:
        section_units = []

        for original_unit in (
            section.get(
                "relational_claim_units"
            )
            or []
        ):
            unit_id = original_unit.get(
                "relational_claim_unit_id"
            )

            interpreted = interpreted_by_id.get(
                unit_id
            )

            if interpreted is None:
                raise RelationalIntelligenceError(
                    "Relational section/unit identity mismatch."
                )

            section_units.append(
                interpreted
            )

        interpreted_sections.append({
            **dict(section),

            "relational_claim_units":
                section_units,

            "relational_signal_count":
                sum(
                    unit.get(
                        "relational_signal_count",
                        0,
                    )
                    for unit in section_units
                ),

            "relational_signal_interpretation_complete":
                True,
        })

    signal_type_counts = {}

    for record in signal_records:
        signal_type = record.get(
            "signal_type"
        )

        signal_type_counts[
            signal_type
        ] = (
            signal_type_counts.get(
                signal_type,
                0,
            )
            + 1
        )

    result = dict(
        relational_claim_units_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "relational_signal_interpretation_performed"
    ] = True

    boundaries[
        "semantic_relation_inference_performed"
    ] = False

    boundaries[
        "subject_relation_object_mapping_performed"
    ] = False

    result.update({
        "schema_version":
            "relational_signal_interpretation_v1",

        "patch":
            "4.6.7D",

        "status":
            "RELATIONAL_SIGNAL_INTERPRETATION_COMPLETE",

        "relational_sections":
            interpreted_sections,

        "relational_claim_units":
            interpreted_units,

        "relational_signal_records":
            signal_records,

        "relational_signal_summary": {
            "relational_claim_unit_count":
                len(
                    interpreted_units
                ),

            "claim_units_with_signals":
                sum(
                    1
                    for unit in interpreted_units
                    if unit.get(
                        "has_explicit_relational_signal"
                    )
                    is True
                ),

            "claim_units_without_signals":
                sum(
                    1
                    for unit in interpreted_units
                    if unit.get(
                        "has_explicit_relational_signal"
                    )
                    is False
                ),

            "explicit_signal_count":
                len(
                    signal_records
                ),

            "signal_type_counts":
                signal_type_counts,

            "relations_inferred":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "subject_relation_object_extraction",
    })

    return result



def extract_subject_relation_object_candidates_v1(
    relational_signal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Extract conservative article-local Subject-Relation-Object
    candidates from explicit relational signals.

    Extraction creates candidate mappings only.

    It does NOT:
    - entity-ground subjects or objects,
    - normalize final relation ontology,
    - resolve final directionality,
    - prove factual truth,
    - perform causal reasoning,
    - infer relations from mere proximity,
    - use external authority,
    - perform linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import hashlib
    import re

    if not isinstance(
        relational_signal_result,
        Mapping,
    ):
        raise RelationalIntelligenceError(
            "relational_signal_result must be a mapping."
        )

    if (
        relational_signal_result.get(
            "schema_version"
        )
        != "relational_signal_interpretation_v1"
    ):
        raise RelationalIntelligenceError(
            "Stage E requires relational_signal_interpretation_v1."
        )

    if (
        relational_signal_result.get(
            "status"
        )
        != "RELATIONAL_SIGNAL_INTERPRETATION_COMPLETE"
    ):
        raise RelationalIntelligenceError(
            "Relational signal interpretation must be complete."
        )

    if (
        relational_signal_result.get(
            "patch"
        )
        != "4.6.7D"
    ):
        raise RelationalIntelligenceError(
            "Stage E requires canonical 4.6.7D input."
        )

    if (
        relational_signal_result.get(
            "next_stage"
        )
        != "subject_relation_object_extraction"
    ):
        raise RelationalIntelligenceError(
            "Stage D must hand off to Subject-Relation-Object extraction."
        )

    if (
        relational_signal_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence must remain transient."
        )

    source_units = list(
        relational_signal_result.get(
            "relational_claim_units"
        )
        or []
    )

    if not source_units:
        raise RelationalIntelligenceError(
            "Relational Claim Units are required."
        )

    def clean_span(value: str) -> str:
        value = re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

        value = value.strip(
            " ,;:-"
        )

        return value

    def credible_span(value: str) -> bool:
        if not value:
            return False

        tokens = re.findall(
            r"[A-Za-z0-9][A-Za-z0-9'?-]*",
            value,
        )

        if not tokens:
            return False

        if len(tokens) > 24:
            return False

        low = value.lower().strip()

        if low in {
            "what",
            "who",
            "which",
            "that",
            "this",
            "it",
            "to",
            "and",
            "or",
        }:
            return False

        return True

    def reject_reason(
        signal_type: str,
        claim_text: str,
        matched_text: str,
    ) -> str | None:

        stripped = claim_text.strip()

        if stripped.endswith("?"):
            return "INTERROGATIVE_NOT_ARTICLE_ASSERTION"

        low_match = matched_text.lower()

        if (
            signal_type == "TRACK_OR_MEASURE"
            and low_match == "measuring"
            and re.search(
                r"\bmeasuring\s+tape\b",
                claim_text,
                re.IGNORECASE,
            )
        ):
            return "MEASURING_IS_NOMINAL_MODIFIER"

        if (
            signal_type == "TRACK_OR_MEASURE"
            and low_match == "measures"
            and re.search(
                r"\bother\s+measures\b",
                claim_text,
                re.IGNORECASE,
            )
        ):
            return "MEASURES_IS_NOUN_NOT_RELATIONAL_VERB"

        if (
            signal_type == "TRACK_OR_MEASURE"
            and re.search(
                r"\b(?:will\s+be|is|are|was|were)\s+"
                r"(?:weighed\s+and\s+)?measured\b",
                claim_text,
                re.IGNORECASE,
            )
        ):
            return "PASSIVE_MEASUREMENT_WITHOUT_SAFE_OBJECT"

        if (
            signal_type == "TRACK_OR_MEASURE"
            and re.search(
                r"^\s*to\s+measure\b",
                claim_text,
                re.IGNORECASE,
            )
        ):
            return "INFINITIVE_PROCEDURAL_MEASUREMENT"

        if (
            signal_type == "COMPARE"
        ):
            return "COMPARISON_DIRECTION_DEFERRED"

        if (
            signal_type == "PART_OF"
        ):
            return "PART_OF_REQUIRES_ENTITY_GROUNDING_BEFORE_ACCEPTANCE"

        if (
            signal_type == "INCLUDE_OR_CONTAIN"
            and claim_text.rstrip().endswith(":")
        ):
            return "LIST_OBJECT_NOT_PRESENT_IN_CURRENT_CLAIM"

        return None

    extracted_units = []
    all_candidates = []
    all_rejections = []

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise RelationalIntelligenceError(
                "Every Relational Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "relational_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "relational_signal_interpretation"
            )
            != "COMPLETE"
        ):
            raise RelationalIntelligenceError(
                "Signal interpretation must be COMPLETE before Stage E."
            )

        if (
            state.get(
                "subject_relation_object_extraction"
            )
            != "PENDING"
        ):
            raise RelationalIntelligenceError(
                "Subject-Relation-Object extraction must be PENDING."
            )

        unit_id = str(
            unit.get(
                "relational_claim_unit_id"
            )
            or ""
        )

        claim_text = str(
            unit.get(
                "text"
            )
            or ""
        ).strip()

        signals = list(
            unit.get(
                "relational_signals"
            )
            or []
        )

        unit_candidates = []
        unit_rejections = []

        for signal_index, signal in enumerate(
            signals
        ):
            signal_type = str(
                signal.get(
                    "signal_type"
                )
                or ""
            )

            matched_text = str(
                signal.get(
                    "matched_text"
                )
                or ""
            )

            start = signal.get(
                "character_start"
            )

            end = signal.get(
                "character_end"
            )

            if not isinstance(start, int) or not isinstance(end, int):
                raise RelationalIntelligenceError(
                    "Relational signal offsets must be integers."
                )

            if (
                start < 0
                or end <= start
                or end > len(claim_text)
            ):
                raise RelationalIntelligenceError(
                    "Relational signal offsets are invalid."
                )

            reason = reject_reason(
                signal_type,
                claim_text,
                matched_text,
            )

            candidate_relation = None
            subject_text = ""
            object_text = ""
            extraction_pattern = ""

            if reason is None:
                if signal_type == "BASED_ON_OR_DERIVED_FROM":
                    left = clean_span(
                        claim_text[:start]
                    )

                    left = re.sub(
                        r"\b(?:is|are|was|were)\s*$",
                        "",
                        left,
                        flags=re.IGNORECASE,
                    ).strip()

                    subject_text = clean_span(left)
                    object_text = clean_span(
                        claim_text[end:]
                    )

                    candidate_relation = (
                        "DERIVED_FROM"
                        if "derived" in matched_text.lower()
                        else "BASED_ON"
                    )

                    extraction_pattern = (
                        "PASSIVE_RELATIONAL_PREDICATE"
                    )

                elif signal_type == "DEPEND_OR_REQUIRE":
                    subject_text = clean_span(
                        claim_text[:start]
                    )

                    object_text = clean_span(
                        claim_text[end:]
                    )

                    candidate_relation = (
                        "DEPENDS_ON"
                        if "depend" in matched_text.lower()
                        else "REQUIRES"
                    )

                    extraction_pattern = (
                        "DIRECT_RELATIONAL_PREDICATE"
                    )

                elif signal_type == "PRODUCE_OR_PROVIDE":
                    subject_text = clean_span(
                        claim_text[:start]
                    )

                    if ", but " in subject_text.lower():
                        subject_text = clean_span(
                            re.split(
                                r",\s*but\s+",
                                subject_text,
                                flags=re.IGNORECASE,
                            )[-1]
                        )

                    object_text = clean_span(
                        claim_text[end:]
                    )

                    candidate_relation = (
                        "PROVIDES"
                        if "provid" in matched_text.lower()
                        else "PRODUCES"
                    )

                    extraction_pattern = (
                        "DIRECT_TRANSITIVE_RELATION"
                    )

                elif signal_type == "AFFECT_OR_INFLUENCE":
                    subject_text = clean_span(
                        claim_text[:start]
                    )

                    object_text = clean_span(
                        claim_text[end:]
                    )

                    candidate_relation = (
                        "AFFECTS"
                        if "affect" in matched_text.lower()
                        else "INFLUENCES"
                    )

                    extraction_pattern = (
                        "DIRECT_TRANSITIVE_RELATION"
                    )

                elif signal_type == "REPRESENT_OR_INDICATE":
                    subject_text = clean_span(
                        claim_text[:start]
                    )

                    subject_text = re.sub(
                        r"\bcan\s*$",
                        "",
                        subject_text,
                        flags=re.IGNORECASE,
                    ).strip()

                    object_text = clean_span(
                        claim_text[end:]
                    )

                    candidate_relation = (
                        "INDICATES"
                        if "indicat" in matched_text.lower()
                        else "REPRESENTS"
                    )

                    extraction_pattern = (
                        "DIRECT_PROPOSITIONAL_RELATION"
                    )

                elif signal_type == "USE_OR_USED_FOR":
                    direct = re.search(
                        r"(?P<subject>"
                        r"[A-Z][^,:;]{0,100}?)"
                        r"\s+"
                        r"(?:use|uses)\s+"
                        r"(?P<object>[^.;:]+)",
                        claim_text,
                        re.IGNORECASE,
                    )

                    if direct:
                        subject_text = clean_span(
                            direct.group(
                                "subject"
                            )
                        )

                        object_text = clean_span(
                            direct.group(
                                "object"
                            )
                        )

                        candidate_relation = "USES"

                        extraction_pattern = (
                            "DIRECT_USE_RELATION"
                        )
                    else:
                        reason = (
                            "USE_SIGNAL_HAS_NO_SAFE_DIRECT_ARGUMENT_STRUCTURE"
                        )

                elif signal_type == "TRACK_OR_MEASURE":
                    relative = re.search(
                        r"(?P<subject>"
                        r"(?:an?|the)\s+[^,:;]{1,80}?)"
                        r"\s+that\s+"
                        r"(?P<verb>"
                        r"track|tracks|measure|measures"
                        r")\s+"
                        r"(?P<object>[^.;:]+)",
                        claim_text,
                        re.IGNORECASE,
                    )

                    direct = re.search(
                        r"(?P<subject>"
                        r"[A-Z][^,:;]{0,100}?)"
                        r"\s+"
                        r"(?P<verb>"
                        r"track|tracks|measure|measures"
                        r")\s+"
                        r"(?P<object>[^.;:]+)",
                        claim_text,
                        re.IGNORECASE,
                    )

                    chosen = relative or direct

                    if chosen:
                        subject_text = clean_span(
                            chosen.group(
                                "subject"
                            )
                        )

                        object_text = clean_span(
                            chosen.group(
                                "object"
                            )
                        )

                        verb = chosen.group(
                            "verb"
                        ).lower()

                        candidate_relation = (
                            "TRACKS"
                            if verb.startswith("track")
                            else "MEASURES"
                        )

                        extraction_pattern = (
                            "RELATIVE_OR_DIRECT_TRANSITIVE_RELATION"
                        )
                    else:
                        reason = (
                            "MEASURE_TRACK_SIGNAL_HAS_NO_SAFE_ARGUMENT_STRUCTURE"
                        )

                elif signal_type == "EXPLICIT_CLASSIFICATION":
                    classification = re.match(
                        r"^\s*(?P<subject>.+?)\s+"
                        r"(?:is|are|was|were)\s+"
                        r"(?P<object>"
                        r"(?:an?|the)\s+.+?)"
                        r"[.!]?\s*$",
                        claim_text,
                        re.IGNORECASE,
                    )

                    if classification:
                        subject_text = clean_span(
                            classification.group(
                                "subject"
                            )
                        )

                        object_text = clean_span(
                            classification.group(
                                "object"
                            )
                        )

                        candidate_relation = "IS_A_OR_ROLE"

                        extraction_pattern = (
                            "DECLARATIVE_CLASSIFICATION"
                        )
                    else:
                        reason = (
                            "CLASSIFICATION_HAS_NO_SAFE_DECLARATIVE_STRUCTURE"
                        )

                elif signal_type == "NAMED_OR_DEFINED":
                    left = clean_span(
                        claim_text[:start]
                    )

                    right = clean_span(
                        claim_text[end:]
                    )

                    subject_text = left
                    object_text = right
                    candidate_relation = "NAMED_OR_DEFINED_AS"
                    extraction_pattern = (
                        "EXPLICIT_NAMING_DEFINITION"
                    )

                else:
                    reason = (
                        "SIGNAL_TYPE_DEFERRED_FOR_LATER_VALIDATION"
                    )

            if reason is None:
                if not credible_span(subject_text):
                    reason = "SUBJECT_SPAN_NOT_CREDIBLE"

                elif not credible_span(object_text):
                    reason = "OBJECT_SPAN_NOT_CREDIBLE"

            if reason is not None:
                rejection = {
                    "relational_claim_unit_id":
                        unit_id,

                    "signal_index":
                        signal_index,

                    "signal_type":
                        signal_type,

                    "matched_text":
                        matched_text,

                    "rejection_reason":
                        reason,

                    "relation_created":
                        False,

                    "truth_assessed":
                        False,

                    "causal_reasoning_performed":
                        False,
                }

                unit_rejections.append(
                    rejection
                )

                all_rejections.append(
                    rejection
                )

                continue

            stable_material = (
                unit_id
                + "|"
                + str(signal_index)
                + "|"
                + candidate_relation
                + "|"
                + subject_text
                + "|"
                + object_text
            )

            candidate_id = (
                "relational_candidate_"
                + hashlib.sha256(
                    stable_material.encode(
                        "utf-8"
                    )
                ).hexdigest()[:16]
            )

            candidate = {
                "relational_candidate_id":
                    candidate_id,

                "relational_claim_unit_id":
                    unit_id,

                "statement_evidence_id":
                    unit.get(
                        "statement_evidence_id"
                    ),

                "sentence_id":
                    unit.get(
                        "sentence_id"
                    ),

                "section_id":
                    unit.get(
                        "section_id"
                    ),

                "sentence_global_index":
                    unit.get(
                        "sentence_global_index"
                    ),

                "signal_index":
                    signal_index,

                "signal_type":
                    signal_type,

                "matched_text":
                    matched_text,

                "subject_text":
                    subject_text,

                "candidate_relation":
                    candidate_relation,

                "object_text":
                    object_text,

                "extraction_pattern":
                    extraction_pattern,

                "article_asserted_candidate":
                    True,

                "entity_concept_grounded":
                    False,

                "relation_normalized":
                    False,

                "directionality_resolved":
                    False,

                "relation_validated":
                    False,

                "truth_assessed":
                    False,

                "causal_reasoning_performed":
                    False,

                "external_authority_checked":
                    False,
            }

            unit_candidates.append(
                candidate
            )

            all_candidates.append(
                candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "subject_relation_object_extraction"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "subject_relation_object_mapping_performed"
        ] = True

        updated_boundaries[
            "semantic_relation_inference_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "relational_candidates":
                unit_candidates,

            "relational_candidate_count":
                len(
                    unit_candidates
                ),

            "relational_signal_rejections":
                unit_rejections,

            "relational_signal_rejection_count":
                len(
                    unit_rejections
                ),

            "relational_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        extracted_units.append(
            updated_unit
        )

    extracted_by_id = {
        unit.get(
            "relational_claim_unit_id"
        ):
            unit
        for unit in extracted_units
    }

    extracted_sections = []

    for section in (
        relational_signal_result.get(
            "relational_sections"
        )
        or []
    ):
        section_units = []

        for old_unit in (
            section.get(
                "relational_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "relational_claim_unit_id"
            )

            new_unit = extracted_by_id.get(
                unit_id
            )

            if new_unit is None:
                raise RelationalIntelligenceError(
                    "Relational section/unit identity mismatch."
                )

            section_units.append(
                new_unit
            )

        extracted_sections.append({
            **dict(section),

            "relational_claim_units":
                section_units,

            "relational_candidate_count":
                sum(
                    unit.get(
                        "relational_candidate_count",
                        0,
                    )
                    for unit in section_units
                ),

            "relational_signal_rejection_count":
                sum(
                    unit.get(
                        "relational_signal_rejection_count",
                        0,
                    )
                    for unit in section_units
                ),

            "subject_relation_object_extraction_complete":
                True,
        })

    result = dict(
        relational_signal_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "subject_relation_object_mapping_performed"
    ] = True

    boundaries[
        "semantic_relation_inference_performed"
    ] = False

    boundaries[
        "causal_reasoning_performed"
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
            "relational_sro_candidates_v1",

        "patch":
            "4.6.7E",

        "status":
            "RELATIONAL_SRO_EXTRACTION_COMPLETE",

        "relational_sections":
            extracted_sections,

        "relational_claim_units":
            extracted_units,

        "relational_candidates":
            all_candidates,

        "relational_signal_rejections":
            all_rejections,

        "relational_sro_summary": {
            "relational_claim_unit_count":
                len(
                    extracted_units
                ),

            "candidate_relation_count":
                len(
                    all_candidates
                ),

            "rejected_signal_count":
                len(
                    all_rejections
                ),

            "all_signals_accounted_for":
                (
                    len(
                        all_candidates
                    )
                    + len(
                        all_rejections
                    )
                    == len(
                        relational_signal_result.get(
                            "relational_signal_records"
                        )
                        or []
                    )
                ),

            "entity_concept_grounding_performed":
                False,

            "relation_normalization_performed":
                False,

            "directionality_resolution_performed":
                False,

            "relation_validation_performed":
                False,

            "truth_assessment_performed":
                False,

            "causal_reasoning_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "entity_concept_grounding",
    })

    return result



def ground_relational_candidates_v1(
    relational_sro_result: Mapping[str, Any],
    entity_concept_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Ground Phase 4.6.7 relational candidate subjects and objects
    against canonical article-local Phase 4.6.2 semantic objects.

    Grounding reuses existing Entity & Concept Intelligence.

    It does NOT:
    - create new semantic entities or concepts,
    - perform fuzzy semantic similarity,
    - normalize the final relation ontology,
    - resolve final relation directionality,
    - validate a relation as factually true,
    - perform causal reasoning,
    - use external authority,
    - perform linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import hashlib
    import re

    if not isinstance(
        relational_sro_result,
        Mapping,
    ):
        raise RelationalIntelligenceError(
            "relational_sro_result must be a mapping."
        )

    if not isinstance(
        entity_concept_result,
        Mapping,
    ):
        raise RelationalIntelligenceError(
            "entity_concept_result must be a mapping."
        )

    if (
        relational_sro_result.get(
            "schema_version"
        )
        != "relational_sro_candidates_v1"
    ):
        raise RelationalIntelligenceError(
            "Stage F requires relational_sro_candidates_v1."
        )

    if (
        relational_sro_result.get(
            "status"
        )
        != "RELATIONAL_SRO_EXTRACTION_COMPLETE"
    ):
        raise RelationalIntelligenceError(
            "Stage E SRO extraction must be complete."
        )

    if (
        relational_sro_result.get(
            "patch"
        )
        != "4.6.7E"
    ):
        raise RelationalIntelligenceError(
            "Stage F requires canonical 4.6.7E input."
        )

    if (
        relational_sro_result.get(
            "next_stage"
        )
        != "entity_concept_grounding"
    ):
        raise RelationalIntelligenceError(
            "Stage E must hand off to entity_concept_grounding."
        )

    if (
        relational_sro_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence must remain transient."
        )

    if (
        entity_concept_result.get(
            "schema_version"
        )
        != "entity_concept_intelligence_result_v1"
    ):
        raise RelationalIntelligenceError(
            "Stage F requires canonical Phase 4.6.2 "
            "Entity & Concept Intelligence."
        )

    if (
        entity_concept_result.get(
            "status"
        )
        != "ENTITY_CONCEPT_INTELLIGENCE_COMPLETE"
    ):
        raise RelationalIntelligenceError(
            "Entity & Concept Intelligence must be complete."
        )

    if (
        entity_concept_result.get(
            "phase"
        )
        != "4.6.2"
    ):
        raise RelationalIntelligenceError(
            "Entity/concept grounding requires Phase 4.6.2 output."
        )

    if (
        entity_concept_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Entity & Concept Intelligence must be article-local transient."
        )

    identity_fields = (
        "article_id",
        "workspace_id",
        "source_type",
        "source_id",
        "document_id",
        "content_hash",
    )

    for field in identity_fields:
        if (
            relational_sro_result.get(field)
            != entity_concept_result.get(field)
        ):
            raise RelationalIntelligenceError(
                "Relational/Entity-Concept identity mismatch: "
                + field
            )

    semantic_objects = list(
        entity_concept_result.get(
            "semantic_objects"
        )
        or []
    )

    if not semantic_objects:
        raise RelationalIntelligenceError(
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
        raise RelationalIntelligenceError(
            "Entity & Concept Intelligence must be article-local."
        )

    if (
        entity_boundaries.get(
            "semantic_memory_write_performed"
        )
        is not False
    ):
        raise RelationalIntelligenceError(
            "Unexpected Semantic Memory write detected upstream."
        )

    if (
        entity_boundaries.get(
            "reasoning_performed"
        )
        is not False
    ):
        raise RelationalIntelligenceError(
            "Unexpected reasoning detected in Phase 4.6.2."
        )

    def normalize(value: str) -> str:
        value = str(value or "").lower()

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

    prepared_objects = []

    for semantic_object in semantic_objects:
        if not isinstance(
            semantic_object,
            Mapping,
        ):
            raise RelationalIntelligenceError(
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
            raise RelationalIntelligenceError(
                "Semantic object is missing canonical_text."
            )

        if semantic_kind not in {
            "entity",
            "concept",
        }:
            raise RelationalIntelligenceError(
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
            raise RelationalIntelligenceError(
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
                isinstance(surface, str)
                and surface.strip()
            ):
                variants.add(
                    surface.strip()
                )

        normalized_variants = {
            normalize(variant):
                variant
            for variant in variants
            if normalize(variant)
        }

        stable_material = (
            str(
                relational_sro_result.get(
                    "article_id"
                )
                or ""
            )
            + "|"
            + semantic_kind
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

                    if len(variant_tokens) >= 2:
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
        relational_sro_result.get(
            "relational_candidates"
        )
        or []
    )

    grounded_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise RelationalIntelligenceError(
                "Every relational candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "relational_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise RelationalIntelligenceError(
                "Relational candidate ID is required."
            )

        if (
            candidate.get(
                "entity_concept_grounded"
            )
            is not False
        ):
            raise RelationalIntelligenceError(
                "Candidate must not already be entity/concept grounded."
            )

        subject_grounding = ground_span(
            str(
                candidate.get(
                    "subject_text"
                )
                or ""
            )
        )

        object_grounding = ground_span(
            str(
                candidate.get(
                    "object_text"
                )
                or ""
            )
        )

        subject_grounded = (
            subject_grounding.get(
                "grounded"
            )
            is True
        )

        object_grounded = (
            object_grounding.get(
                "grounded"
            )
            is True
        )

        if (
            subject_grounded
            and object_grounded
        ):
            grounding_status = (
                "BOTH_GROUNDED"
            )

        elif (
            subject_grounded
            or object_grounded
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
            "subject_grounding":
                subject_grounding,

            "object_grounding":
                object_grounding,

            "subject_grounded":
                subject_grounded,

            "object_grounded":
                object_grounded,

            "grounding_status":
                grounding_status,

            "entity_concept_grounded":
                (
                    subject_grounded
                    and object_grounded
                ),

            "relation_normalized":
                False,

            "directionality_resolved":
                False,

            "relation_validated":
                False,

            "truth_assessed":
                False,

            "causal_reasoning_performed":
                False,

            "external_authority_checked":
                False,
        })

        grounded_candidates.append(
            grounded_candidate
        )

    grounded_by_id = {
        candidate.get(
            "relational_candidate_id"
        ):
            candidate
        for candidate in grounded_candidates
    }

    grounded_units = []

    for unit in (
        relational_sro_result.get(
            "relational_claim_units"
        )
        or []
    ):
        state = dict(
            unit.get(
                "relational_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "subject_relation_object_extraction"
            )
            != "COMPLETE"
        ):
            raise RelationalIntelligenceError(
                "SRO extraction must be COMPLETE before grounding."
            )

        if (
            state.get(
                "entity_concept_grounding"
            )
            != "PENDING"
        ):
            raise RelationalIntelligenceError(
                "Entity/concept grounding must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "relational_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "relational_candidate_id"
            )

            grounded = grounded_by_id.get(
                candidate_id
            )

            if grounded is None:
                raise RelationalIntelligenceError(
                    "Relational candidate/unit identity mismatch."
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
            "semantic_relation_inference_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "relational_candidates":
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

            "relational_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        grounded_units.append(
            updated_unit
        )

    grounded_units_by_id = {
        unit.get(
            "relational_claim_unit_id"
        ):
            unit
        for unit in grounded_units
    }

    grounded_sections = []

    for section in (
        relational_sro_result.get(
            "relational_sections"
        )
        or []
    ):
        section_units = []

        for old_unit in (
            section.get(
                "relational_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "relational_claim_unit_id"
            )

            grounded_unit = (
                grounded_units_by_id.get(
                    unit_id
                )
            )

            if grounded_unit is None:
                raise RelationalIntelligenceError(
                    "Relational section/unit grounding mismatch."
                )

            section_units.append(
                grounded_unit
            )

        grounded_sections.append({
            **dict(section),

            "relational_claim_units":
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
        relational_sro_result
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
        "semantic_relation_inference_performed"
    ] = False

    boundaries[
        "causal_reasoning_performed"
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
            "relational_entity_concept_grounding_v1",

        "patch":
            "4.6.7F",

        "status":
            "RELATIONAL_ENTITY_CONCEPT_GROUNDING_COMPLETE",

        "relational_sections":
            grounded_sections,

        "relational_claim_units":
            grounded_units,

        "relational_candidates":
            grounded_candidates,

        "entity_concept_grounding_summary": {
            "semantic_object_count":
                len(
                    semantic_objects
                ),

            "relational_candidate_count":
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

            "relation_normalization_performed":
                False,

            "directionality_resolution_performed":
                False,

            "relation_validation_performed":
                False,

            "truth_assessment_performed":
                False,

            "causal_reasoning_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "relation_normalization",
    })

    return result



def normalize_relational_relations_v1(
    entity_concept_grounding_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Normalize extracted article-local relational candidate labels
    into the canonical Phase 4.6.7 relation vocabulary.

    This stage normalizes relation names only.

    It does NOT:
    - reverse or finalize relation direction,
    - validate the final relationship,
    - infer causal meaning,
    - assess factual truth,
    - require both endpoints to be entity/concept grounded,
    - use external authority,
    - perform linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        entity_concept_grounding_result,
        Mapping,
    ):
        raise RelationalIntelligenceError(
            "entity_concept_grounding_result must be a mapping."
        )

    if (
        entity_concept_grounding_result.get(
            "schema_version"
        )
        != "relational_entity_concept_grounding_v1"
    ):
        raise RelationalIntelligenceError(
            "Stage G requires relational_entity_concept_grounding_v1."
        )

    if (
        entity_concept_grounding_result.get(
            "status"
        )
        != "RELATIONAL_ENTITY_CONCEPT_GROUNDING_COMPLETE"
    ):
        raise RelationalIntelligenceError(
            "Entity/concept grounding must be complete before normalization."
        )

    if (
        entity_concept_grounding_result.get(
            "phase"
        )
        != "4.6.7"
    ):
        raise RelationalIntelligenceError(
            "Stage G requires Phase 4.6.7 input."
        )

    if (
        entity_concept_grounding_result.get(
            "patch"
        )
        != "4.6.7F"
    ):
        raise RelationalIntelligenceError(
            "Stage G requires canonical 4.6.7F input."
        )

    if (
        entity_concept_grounding_result.get(
            "next_stage"
        )
        != "relation_normalization"
    ):
        raise RelationalIntelligenceError(
            "Stage F must hand off to relation_normalization."
        )

    if (
        entity_concept_grounding_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence must remain transient."
        )

    canonical_relation_map = {
        "TRACKS":
            "TRACKS",

        "MEASURES":
            "MEASURES",

        "USES":
            "USES",

        "USED_FOR":
            "USED_FOR",

        "DERIVED_FROM":
            "DERIVED_FROM",

        "BASED_ON":
            "BASED_ON",

        "DEPENDS_ON":
            "DEPENDS_ON",

        "REQUIRES":
            "REQUIRES",

        "PROVIDES":
            "PROVIDES",

        "PRODUCES":
            "PRODUCES",

        "AFFECTS":
            "AFFECTS",

        "INFLUENCES":
            "INFLUENCES",

        "INDICATES":
            "INDICATES",

        "REPRESENTS":
            "REPRESENTS",

        "IS_A_OR_ROLE":
            "IS_A",

        "NAMED_OR_DEFINED_AS":
            "DEFINED_AS",

        "INCLUDES":
            "INCLUDES",

        "CONTAINS":
            "CONTAINS",

        "PART_OF":
            "PART_OF",

        "ASSOCIATED_WITH":
            "ASSOCIATED_WITH",

        "RELATED_TO":
            "RELATED_TO",
    }

    relation_families = {
        "TRACKS":
            "MEASUREMENT_MONITORING",

        "MEASURES":
            "MEASUREMENT_MONITORING",

        "USES":
            "USAGE_FUNCTION",

        "USED_FOR":
            "USAGE_FUNCTION",

        "DERIVED_FROM":
            "ORIGIN_DERIVATION",

        "BASED_ON":
            "ORIGIN_DERIVATION",

        "DEPENDS_ON":
            "DEPENDENCY_REQUIREMENT",

        "REQUIRES":
            "DEPENDENCY_REQUIREMENT",

        "PROVIDES":
            "PRODUCTION_PROVISION",

        "PRODUCES":
            "PRODUCTION_PROVISION",

        "AFFECTS":
            "INFLUENCE_ASSOCIATION",

        "INFLUENCES":
            "INFLUENCE_ASSOCIATION",

        "INDICATES":
            "REPRESENTATION_INDICATION",

        "REPRESENTS":
            "REPRESENTATION_INDICATION",

        "IS_A":
            "CLASSIFICATION",

        "DEFINED_AS":
            "DEFINITION_NAMING",

        "INCLUDES":
            "COMPOSITION_MEMBERSHIP",

        "CONTAINS":
            "COMPOSITION_MEMBERSHIP",

        "PART_OF":
            "COMPOSITION_MEMBERSHIP",

        "ASSOCIATED_WITH":
            "ASSOCIATION",

        "RELATED_TO":
            "ASSOCIATION",
    }

    symmetric_relations = {
        "ASSOCIATED_WITH",
        "RELATED_TO",
    }

    causal_sensitive_relations = {
        "AFFECTS",
        "INFLUENCES",
    }

    source_candidates = list(
        entity_concept_grounding_result.get(
            "relational_candidates"
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
            raise RelationalIntelligenceError(
                "Every relational candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "relational_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise RelationalIntelligenceError(
                "Relational candidate ID is required."
            )

        if (
            candidate.get(
                "relation_normalized"
            )
            is not False
        ):
            raise RelationalIntelligenceError(
                "Candidate must not already be relation-normalized."
            )

        raw_relation = str(
            candidate.get(
                "candidate_relation"
            )
            or ""
        ).strip()

        if not raw_relation:
            raise RelationalIntelligenceError(
                "Candidate relation label is required."
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
                "relation_normalization_status":
                    "UNSUPPORTED",

                "canonical_relation":
                    None,

                "relation_family":
                    None,

                "relation_normalized":
                    False,

                "normalization_reason":
                    "UNSUPPORTED_RELATION_LABEL",

                "directionality_resolved":
                    False,

                "relation_validated":
                    False,

                "truth_assessed":
                    False,

                "causal_reasoning_performed":
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

        causal_sensitive = (
            canonical_relation
            in causal_sensitive_relations
        )

        normalized = dict(
            candidate
        )

        normalized.update({
            "raw_candidate_relation":
                raw_relation,

            "canonical_relation":
                canonical_relation,

            "relation_family":
                relation_families.get(
                    canonical_relation
                ),

            "relation_normalization_status":
                "NORMALIZED",

            "relation_normalized":
                True,

            "relation_is_symmetric":
                canonical_relation
                in symmetric_relations,

            "causal_sensitive_relation":
                causal_sensitive,

            "causal_interpretation_deferred":
                causal_sensitive,

            "causal_reasoning_stage":
                (
                    "4.6.8"
                    if causal_sensitive
                    else None
                ),

            "directionality_resolved":
                False,

            "relation_validated":
                False,

            "truth_assessed":
                False,

            "causal_reasoning_performed":
                False,

            "external_authority_checked":
                False,
        })

        normalized_candidates.append(
            normalized
        )

    normalized_by_id = {
        candidate.get(
            "relational_candidate_id"
        ):
            candidate
        for candidate in normalized_candidates
    }

    normalized_units = []

    for unit in (
        entity_concept_grounding_result.get(
            "relational_claim_units"
        )
        or []
    ):
        state = dict(
            unit.get(
                "relational_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "entity_concept_grounding"
            )
            != "COMPLETE"
        ):
            raise RelationalIntelligenceError(
                "Entity/concept grounding must be COMPLETE "
                "before relation normalization."
            )

        if (
            state.get(
                "relation_normalization"
            )
            != "PENDING"
        ):
            raise RelationalIntelligenceError(
                "Relation normalization must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "relational_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "relational_candidate_id"
            )

            normalized_candidate = (
                normalized_by_id.get(
                    candidate_id
                )
            )

            if normalized_candidate is None:
                raise RelationalIntelligenceError(
                    "Relational candidate/unit normalization mismatch."
                )

            unit_candidates.append(
                normalized_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "relation_normalization"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "relation_normalization_performed"
        ] = True

        updated_boundaries[
            "directionality_resolution_performed"
        ] = False

        updated_boundaries[
            "semantic_relation_inference_performed"
        ] = False

        updated_boundaries[
            "causal_reasoning_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "relational_candidates":
                unit_candidates,

            "normalized_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "relation_normalization_status"
                    )
                    == "NORMALIZED"
                ),

            "unsupported_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "relation_normalization_status"
                    )
                    == "UNSUPPORTED"
                ),

            "relational_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        normalized_units.append(
            updated_unit
        )

    normalized_units_by_id = {
        unit.get(
            "relational_claim_unit_id"
        ):
            unit
        for unit in normalized_units
    }

    normalized_sections = []

    for section in (
        entity_concept_grounding_result.get(
            "relational_sections"
        )
        or []
    ):
        section_units = []

        for old_unit in (
            section.get(
                "relational_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "relational_claim_unit_id"
            )

            normalized_unit = (
                normalized_units_by_id.get(
                    unit_id
                )
            )

            if normalized_unit is None:
                raise RelationalIntelligenceError(
                    "Relational section/unit normalization mismatch."
                )

            section_units.append(
                normalized_unit
            )

        normalized_sections.append({
            **dict(section),

            "relational_claim_units":
                section_units,

            "normalized_relation_count":
                sum(
                    unit.get(
                        "normalized_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "unsupported_relation_count":
                sum(
                    unit.get(
                        "unsupported_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "relation_normalization_complete":
                True,
        })

    normalized_count = sum(
        1
        for candidate in normalized_candidates
        if candidate.get(
            "relation_normalization_status"
        )
        == "NORMALIZED"
    )

    unsupported_count = sum(
        1
        for candidate in normalized_candidates
        if candidate.get(
            "relation_normalization_status"
        )
        == "UNSUPPORTED"
    )

    causal_sensitive_count = sum(
        1
        for candidate in normalized_candidates
        if candidate.get(
            "causal_sensitive_relation"
        )
        is True
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
        "relation_normalization_performed"
    ] = True

    boundaries[
        "directionality_resolution_performed"
    ] = False

    boundaries[
        "semantic_relation_inference_performed"
    ] = False

    boundaries[
        "causal_reasoning_performed"
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
            "relational_relation_normalization_v1",

        "patch":
            "4.6.7G",

        "status":
            "RELATIONAL_RELATION_NORMALIZATION_COMPLETE",

        "relational_sections":
            normalized_sections,

        "relational_claim_units":
            normalized_units,

        "relational_candidates":
            normalized_candidates,

        "unsupported_relational_candidates":
            unsupported_candidates,

        "relation_normalization_summary": {
            "candidate_count":
                len(
                    normalized_candidates
                ),

            "normalized_relation_count":
                normalized_count,

            "unsupported_relation_count":
                unsupported_count,

            "candidate_count_accounted_for":
                (
                    normalized_count
                    + unsupported_count
                    == len(
                        normalized_candidates
                    )
                ),

            "causal_sensitive_relation_count":
                causal_sensitive_count,

            "causal_sensitive_relations_deferred_to":
                "4.6.8",

            "canonical_vocabulary_applied":
                True,

            "directionality_resolution_performed":
                False,

            "relation_validation_performed":
                False,

            "truth_assessment_performed":
                False,

            "causal_reasoning_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "relation_directionality_resolution",
    })

    return result



def resolve_relational_directionality_v1(
    relation_normalization_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve canonical directionality metadata for normalized
    article-local relational candidates.

    This stage does NOT:
    - create new relations,
    - infer missing subject/object spans,
    - validate factual truth,
    - perform causal reasoning,
    - use external authority,
    - perform linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        relation_normalization_result,
        Mapping,
    ):
        raise RelationalIntelligenceError(
            "relation_normalization_result must be a mapping."
        )

    if (
        relation_normalization_result.get(
            "schema_version"
        )
        != "relational_relation_normalization_v1"
    ):
        raise RelationalIntelligenceError(
            "Stage H requires relational_relation_normalization_v1."
        )

    if (
        relation_normalization_result.get(
            "status"
        )
        != "RELATIONAL_RELATION_NORMALIZATION_COMPLETE"
    ):
        raise RelationalIntelligenceError(
            "Relation normalization must be complete before directionality."
        )

    if (
        relation_normalization_result.get(
            "phase"
        )
        != "4.6.7"
    ):
        raise RelationalIntelligenceError(
            "Stage H requires Phase 4.6.7 input."
        )

    if (
        relation_normalization_result.get(
            "patch"
        )
        != "4.6.7G"
    ):
        raise RelationalIntelligenceError(
            "Stage H requires canonical 4.6.7G input."
        )

    if (
        relation_normalization_result.get(
            "next_stage"
        )
        != "relation_directionality_resolution"
    ):
        raise RelationalIntelligenceError(
            "Stage G must hand off to relation_directionality_resolution."
        )

    if (
        relation_normalization_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence must remain transient."
        )

    inverse_relation_map = {
        "PART_OF":
            "HAS_PART",

        "DERIVED_FROM":
            "SOURCE_OF",

        "BASED_ON":
            "BASIS_FOR",

        "USED_FOR":
            "HAS_USE",

        "DEFINED_AS":
            "DEFINES",
    }

    source_candidates = list(
        relation_normalization_result.get(
            "relational_candidates"
        )
        or []
    )

    resolved_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise RelationalIntelligenceError(
                "Every relational candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "relational_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise RelationalIntelligenceError(
                "Relational candidate ID is required."
            )

        if (
            candidate.get(
                "directionality_resolved"
            )
            is not False
        ):
            raise RelationalIntelligenceError(
                "Candidate must not already have resolved directionality."
            )

        normalization_status = (
            candidate.get(
                "relation_normalization_status"
            )
        )

        if normalization_status == "UNSUPPORTED":
            unresolved = dict(
                candidate
            )

            unresolved.update({
                "directionality_status":
                    "UNRESOLVED_UNSUPPORTED_RELATION",

                "directionality_type":
                    None,

                "canonical_subject_text":
                    candidate.get(
                        "subject_text"
                    ),

                "canonical_object_text":
                    candidate.get(
                        "object_text"
                    ),

                "canonical_subject_grounding":
                    candidate.get(
                        "subject_grounding"
                    ),

                "canonical_object_grounding":
                    candidate.get(
                        "object_grounding"
                    ),

                "inverse_relation":
                    None,

                "directionality_resolved":
                    False,

                "relation_validated":
                    False,

                "truth_assessed":
                    False,

                "causal_reasoning_performed":
                    False,
            })

            resolved_candidates.append(
                unresolved
            )

            continue

        if normalization_status != "NORMALIZED":
            raise RelationalIntelligenceError(
                "Candidate has invalid normalization status."
            )

        canonical_relation = str(
            candidate.get(
                "canonical_relation"
            )
            or ""
        )

        if not canonical_relation:
            raise RelationalIntelligenceError(
                "Normalized candidate is missing canonical_relation."
            )

        is_symmetric = (
            candidate.get(
                "relation_is_symmetric"
            )
            is True
        )

        subject_text = candidate.get(
            "subject_text"
        )

        object_text = candidate.get(
            "object_text"
        )

        subject_grounding = candidate.get(
            "subject_grounding"
        )

        object_grounding = candidate.get(
            "object_grounding"
        )

        if is_symmetric:
            directionality_type = "SYMMETRIC"
            directionality_status = "RESOLVED_SYMMETRIC"
            inverse_relation = canonical_relation

        else:
            directionality_type = "DIRECTED"
            directionality_status = "RESOLVED_DIRECTED"
            inverse_relation = inverse_relation_map.get(
                canonical_relation
            )

        resolved = dict(
            candidate
        )

        resolved.update({
            "directionality_status":
                directionality_status,

            "directionality_type":
                directionality_type,

            "canonical_subject_text":
                subject_text,

            "canonical_object_text":
                object_text,

            "canonical_subject_grounding":
                subject_grounding,

            "canonical_object_grounding":
                object_grounding,

            "inverse_relation":
                inverse_relation,

            "subject_object_reversed":
                False,

            "directionality_resolved":
                True,

            "relation_validated":
                False,

            "truth_assessed":
                False,

            "causal_reasoning_performed":
                False,

            "external_authority_checked":
                False,
        })

        resolved_candidates.append(
            resolved
        )

    resolved_by_id = {
        candidate.get(
            "relational_candidate_id"
        ):
            candidate
        for candidate in resolved_candidates
    }

    resolved_units = []

    for unit in (
        relation_normalization_result.get(
            "relational_claim_units"
        )
        or []
    ):
        state = dict(
            unit.get(
                "relational_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "relation_normalization"
            )
            != "COMPLETE"
        ):
            raise RelationalIntelligenceError(
                "Relation normalization must be COMPLETE before directionality."
            )

        if (
            state.get(
                "directionality_resolution"
            )
            != "PENDING"
        ):
            raise RelationalIntelligenceError(
                "Directionality resolution must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "relational_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "relational_candidate_id"
            )

            resolved_candidate = (
                resolved_by_id.get(
                    candidate_id
                )
            )

            if resolved_candidate is None:
                raise RelationalIntelligenceError(
                    "Relational candidate/unit directionality mismatch."
                )

            unit_candidates.append(
                resolved_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "directionality_resolution"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "directionality_resolution_performed"
        ] = True

        updated_boundaries[
            "relation_validation_performed"
        ] = False

        updated_boundaries[
            "causal_reasoning_performed"
        ] = False

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "relational_candidates":
                unit_candidates,

            "directed_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "directionality_type"
                    )
                    == "DIRECTED"
                ),

            "symmetric_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "directionality_type"
                    )
                    == "SYMMETRIC"
                ),

            "unresolved_directionality_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "directionality_resolved"
                    )
                    is False
                ),

            "relational_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        resolved_units.append(
            updated_unit
        )

    resolved_units_by_id = {
        unit.get(
            "relational_claim_unit_id"
        ):
            unit
        for unit in resolved_units
    }

    resolved_sections = []

    for section in (
        relation_normalization_result.get(
            "relational_sections"
        )
        or []
    ):
        section_units = []

        for old_unit in (
            section.get(
                "relational_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "relational_claim_unit_id"
            )

            resolved_unit = (
                resolved_units_by_id.get(
                    unit_id
                )
            )

            if resolved_unit is None:
                raise RelationalIntelligenceError(
                    "Relational section/unit directionality mismatch."
                )

            section_units.append(
                resolved_unit
            )

        resolved_sections.append({
            **dict(section),

            "relational_claim_units":
                section_units,

            "directed_relation_count":
                sum(
                    unit.get(
                        "directed_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "symmetric_relation_count":
                sum(
                    unit.get(
                        "symmetric_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "unresolved_directionality_count":
                sum(
                    unit.get(
                        "unresolved_directionality_count",
                        0,
                    )
                    for unit in section_units
                ),

            "directionality_resolution_complete":
                True,
        })

    directed_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "directionality_type"
        )
        == "DIRECTED"
    )

    symmetric_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "directionality_type"
        )
        == "SYMMETRIC"
    )

    unresolved_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "directionality_resolved"
        )
        is False
    )

    result = dict(
        relation_normalization_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "directionality_resolution_performed"
    ] = True

    boundaries[
        "relation_validation_performed"
    ] = False

    boundaries[
        "causal_reasoning_performed"
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
            "relational_directionality_resolution_v1",

        "patch":
            "4.6.7H",

        "status":
            "RELATIONAL_DIRECTIONALITY_RESOLUTION_COMPLETE",

        "relational_sections":
            resolved_sections,

        "relational_claim_units":
            resolved_units,

        "relational_candidates":
            resolved_candidates,

        "directionality_summary": {
            "candidate_count":
                len(
                    resolved_candidates
                ),

            "directed_relation_count":
                directed_count,

            "symmetric_relation_count":
                symmetric_count,

            "unresolved_directionality_count":
                unresolved_count,

            "candidate_count_accounted_for":
                (
                    directed_count
                    + symmetric_count
                    + unresolved_count
                    == len(
                        resolved_candidates
                    )
                ),

            "subject_object_reversal_performed":
                False,

            "inverse_relation_metadata_added":
                True,

            "relation_validation_performed":
                False,

            "truth_assessment_performed":
                False,

            "causal_reasoning_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "same_sentence_relation_validation",
    })

    return result



def validate_same_sentence_relations_v1(
    directionality_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate whether each relational candidate has sufficient
    same-sentence article-local textual support.

    This is textual-evidence validation only.

    It does NOT:
    - establish factual truth,
    - perform external verification,
    - perform cross-sentence validation,
    - perform causal reasoning,
    - create new relations,
    - infer missing endpoints,
    - perform linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        directionality_result,
        Mapping,
    ):
        raise RelationalIntelligenceError(
            "directionality_result must be a mapping."
        )

    if (
        directionality_result.get(
            "schema_version"
        )
        != "relational_directionality_resolution_v1"
    ):
        raise RelationalIntelligenceError(
            "Stage I requires relational_directionality_resolution_v1."
        )

    if (
        directionality_result.get(
            "status"
        )
        != "RELATIONAL_DIRECTIONALITY_RESOLUTION_COMPLETE"
    ):
        raise RelationalIntelligenceError(
            "Directionality resolution must be complete."
        )

    if (
        directionality_result.get(
            "phase"
        )
        != "4.6.7"
    ):
        raise RelationalIntelligenceError(
            "Stage I requires Phase 4.6.7 input."
        )

    if (
        directionality_result.get(
            "patch"
        )
        != "4.6.7H"
    ):
        raise RelationalIntelligenceError(
            "Stage I requires canonical 4.6.7H input."
        )

    if (
        directionality_result.get(
            "next_stage"
        )
        != "same_sentence_relation_validation"
    ):
        raise RelationalIntelligenceError(
            "Stage H must hand off to same_sentence_relation_validation."
        )

    if (
        directionality_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence must remain transient."
        )

    source_units = list(
        directionality_result.get(
            "relational_claim_units"
        )
        or []
    )

    if not source_units:
        raise RelationalIntelligenceError(
            "Relational Claim Units are required."
        )

    candidate_to_unit = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise RelationalIntelligenceError(
                "Every Relational Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "relational_claim_unit_id"
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
            raise RelationalIntelligenceError(
                "Relational Claim Unit ID is required."
            )

        if not sentence_id:
            raise RelationalIntelligenceError(
                "Relational Claim Unit sentence_id is required."
            )

        if not claim_text:
            raise RelationalIntelligenceError(
                "Relational Claim Unit text is required."
            )

        state = dict(
            unit.get(
                "relational_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "directionality_resolution"
            )
            != "COMPLETE"
        ):
            raise RelationalIntelligenceError(
                "Directionality resolution must be COMPLETE before Stage I."
            )

        if (
            state.get(
                "same_sentence_validation"
            )
            != "PENDING"
        ):
            raise RelationalIntelligenceError(
                "Same-sentence validation must be PENDING."
            )

        for candidate in (
            unit.get(
                "relational_candidates"
            )
            or []
        ):
            candidate_id = str(
                candidate.get(
                    "relational_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise RelationalIntelligenceError(
                    "Relational candidate ID is required."
                )

            if candidate_id in candidate_to_unit:
                raise RelationalIntelligenceError(
                    "Duplicate relational candidate ID detected."
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

    def normalize(value: str) -> str:
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

    source_candidates = list(
        directionality_result.get(
            "relational_candidates"
        )
        or []
    )

    validated_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise RelationalIntelligenceError(
                "Every relational candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "relational_candidate_id"
            )
            or ""
        )

        unit_info = candidate_to_unit.get(
            candidate_id
        )

        if unit_info is None:
            raise RelationalIntelligenceError(
                "Relational candidate has no canonical claim-unit sentence."
            )

        if (
            candidate.get(
                "relation_validated"
            )
            is not False
        ):
            raise RelationalIntelligenceError(
                "Candidate must not already be relation-validated."
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

        subject_supported, subject_method = (
            span_supported(
                str(
                    candidate.get(
                        "canonical_subject_text"
                    )
                    or candidate.get(
                        "subject_text"
                    )
                    or ""
                ),
                claim_text,
                candidate.get(
                    "canonical_subject_grounding"
                )
                or candidate.get(
                    "subject_grounding"
                ),
            )
        )

        object_supported, object_method = (
            span_supported(
                str(
                    candidate.get(
                        "canonical_object_text"
                    )
                    or candidate.get(
                        "object_text"
                    )
                    or ""
                ),
                claim_text,
                candidate.get(
                    "canonical_object_grounding"
                )
                or candidate.get(
                    "object_grounding"
                ),
            )
        )

        normalization_supported = (
            candidate.get(
                "relation_normalization_status"
            )
            == "NORMALIZED"
            and bool(
                candidate.get(
                    "canonical_relation"
                )
            )
        )

        directionality_supported = (
            candidate.get(
                "directionality_resolved"
            )
            is True
        )

        if (
            candidate.get(
                "relation_normalization_status"
            )
            == "UNSUPPORTED"
        ):
            validation_status = (
                "NOT_VALIDATED_UNSUPPORTED_RELATION"
            )

            same_sentence_valid = False

            validation_reason = (
                "RELATION_NOT_CANONICALLY_NORMALIZED"
            )

        elif not same_sentence_identity:
            validation_status = (
                "NOT_VALIDATED_SENTENCE_ID_MISMATCH"
            )

            same_sentence_valid = False

            validation_reason = (
                "CANDIDATE_SENTENCE_ID_DOES_NOT_MATCH_CLAIM_UNIT"
            )

        elif not directionality_supported:
            validation_status = (
                "NOT_VALIDATED_DIRECTIONALITY_UNRESOLVED"
            )

            same_sentence_valid = False

            validation_reason = (
                "DIRECTIONALITY_NOT_RESOLVED"
            )

        elif not normalization_supported:
            validation_status = (
                "NOT_VALIDATED_NORMALIZATION_INCOMPLETE"
            )

            same_sentence_valid = False

            validation_reason = (
                "RELATION_NORMALIZATION_NOT_COMPLETE"
            )

        elif not subject_supported:
            validation_status = (
                "NOT_VALIDATED_SUBJECT_UNSUPPORTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "SUBJECT_NOT_SUPPORTED_BY_CANONICAL_SENTENCE"
            )

        elif not object_supported:
            validation_status = (
                "NOT_VALIDATED_OBJECT_UNSUPPORTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "OBJECT_NOT_SUPPORTED_BY_CANONICAL_SENTENCE"
            )

        else:
            validation_status = (
                "VALIDATED_SAME_SENTENCE"
            )

            same_sentence_valid = True

            validation_reason = None

        validated = dict(
            candidate
        )

        validated.update({
            "same_sentence_validation_status":
                validation_status,

            "same_sentence_valid":
                same_sentence_valid,

            "same_sentence_validation_reason":
                validation_reason,

            "same_sentence_id_match":
                same_sentence_identity,

            "same_sentence_subject_supported":
                subject_supported,

            "same_sentence_object_supported":
                object_supported,

            "subject_support_method":
                subject_method,

            "object_support_method":
                object_method,

            "same_sentence_evidence": {
                "sentence_id":
                    canonical_sentence_id,

                "sentence_text":
                    claim_text,
            },

            "relation_validated":
                same_sentence_valid,

            "cross_sentence_validation_performed":
                False,

            "truth_assessed":
                False,

            "causal_reasoning_performed":
                False,

            "external_authority_checked":
                False,
        })

        validated_candidates.append(
            validated
        )

    validated_by_id = {
        candidate.get(
            "relational_candidate_id"
        ):
            candidate
        for candidate in validated_candidates
    }

    validated_units = []

    for unit in source_units:
        state = dict(
            unit.get(
                "relational_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "relational_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "relational_candidate_id"
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise RelationalIntelligenceError(
                    "Relational candidate/unit validation mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "same_sentence_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "same_sentence_relation_validation_performed"
        ] = True

        updated_boundaries[
            "cross_sentence_relation_validation_performed"
        ] = False

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "causal_reasoning_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "relational_candidates":
                unit_candidates,

            "same_sentence_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "same_sentence_valid"
                    )
                    is True
                ),

            "same_sentence_not_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "same_sentence_valid"
                    )
                    is False
                ),

            "relational_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        validated_units.append(
            updated_unit
        )

    validated_units_by_id = {
        unit.get(
            "relational_claim_unit_id"
        ):
            unit
        for unit in validated_units
    }

    validated_sections = []

    for section in (
        directionality_result.get(
            "relational_sections"
        )
        or []
    ):
        section_units = []

        for old_unit in (
            section.get(
                "relational_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "relational_claim_unit_id"
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise RelationalIntelligenceError(
                    "Relational section/unit validation mismatch."
                )

            section_units.append(
                validated_unit
            )

        validated_sections.append({
            **dict(section),

            "relational_claim_units":
                section_units,

            "same_sentence_validated_count":
                sum(
                    unit.get(
                        "same_sentence_validated_count",
                        0,
                    )
                    for unit in section_units
                ),

            "same_sentence_not_validated_count":
                sum(
                    unit.get(
                        "same_sentence_not_validated_count",
                        0,
                    )
                    for unit in section_units
                ),

            "same_sentence_validation_complete":
                True,
        })

    validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "same_sentence_valid"
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
        directionality_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "same_sentence_relation_validation_performed"
    ] = True

    boundaries[
        "cross_sentence_relation_validation_performed"
    ] = False

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "causal_reasoning_performed"
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
            "relational_same_sentence_validation_v1",

        "patch":
            "4.6.7I",

        "status":
            "RELATIONAL_SAME_SENTENCE_VALIDATION_COMPLETE",

        "relational_sections":
            validated_sections,

        "relational_claim_units":
            validated_units,

        "relational_candidates":
            validated_candidates,

        "same_sentence_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "same_sentence_validated_count":
                validated_count,

            "same_sentence_not_validated_count":
                not_validated_count,

            "candidate_count_accounted_for":
                (
                    validated_count
                    + not_validated_count
                    == len(
                        validated_candidates
                    )
                ),

            "cross_sentence_validation_performed":
                False,

            "truth_assessment_performed":
                False,

            "causal_reasoning_performed":
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
            "cross_sentence_relation_validation",
    })

    return result



def validate_cross_sentence_relations_v1(
    same_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Conservatively validate article-local relational candidates
    using immediately adjacent sentences in the same section.

    Cross-sentence validation may support a missing subject or object
    endpoint only when:
    - the relation is canonically normalized,
    - directionality is resolved,
    - the candidate belongs to a canonical claim unit,
    - an immediately adjacent same-section sentence explicitly
      contains the missing endpoint.

    This stage does NOT:
    - perform unrestricted paragraph/document inference,
    - infer factual truth,
    - perform causal reasoning,
    - use external authority,
    - create new relations,
    - change relation direction,
    - perform linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        same_sentence_result,
        Mapping,
    ):
        raise RelationalIntelligenceError(
            "same_sentence_result must be a mapping."
        )

    if (
        same_sentence_result.get(
            "schema_version"
        )
        != "relational_same_sentence_validation_v1"
    ):
        raise RelationalIntelligenceError(
            "Stage J requires relational_same_sentence_validation_v1."
        )

    if (
        same_sentence_result.get(
            "status"
        )
        != "RELATIONAL_SAME_SENTENCE_VALIDATION_COMPLETE"
    ):
        raise RelationalIntelligenceError(
            "Same-sentence validation must be complete."
        )

    if (
        same_sentence_result.get(
            "phase"
        )
        != "4.6.7"
    ):
        raise RelationalIntelligenceError(
            "Stage J requires Phase 4.6.7 input."
        )

    if (
        same_sentence_result.get(
            "patch"
        )
        != "4.6.7I"
    ):
        raise RelationalIntelligenceError(
            "Stage J requires canonical 4.6.7I input."
        )

    if (
        same_sentence_result.get(
            "next_stage"
        )
        != "cross_sentence_relation_validation"
    ):
        raise RelationalIntelligenceError(
            "Stage I must hand off to cross_sentence_relation_validation."
        )

    if (
        same_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence must remain transient."
        )

    source_units = list(
        same_sentence_result.get(
            "relational_claim_units"
        )
        or []
    )

    if not source_units:
        raise RelationalIntelligenceError(
            "Relational Claim Units are required."
        )

    def normalize(value: str) -> str:
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
            raise RelationalIntelligenceError(
                "Every Relational Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "relational_claim_unit_id"
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
            raise RelationalIntelligenceError(
                "Relational Claim Unit ID is required."
            )

        if not sentence_id:
            raise RelationalIntelligenceError(
                "Relational Claim Unit sentence_id is required."
            )

        if not section_id:
            raise RelationalIntelligenceError(
                "Relational Claim Unit section_id is required."
            )

        if not claim_text:
            raise RelationalIntelligenceError(
                "Relational Claim Unit text is required."
            )

        if not isinstance(
            sentence_global_index,
            int,
        ):
            raise RelationalIntelligenceError(
                "sentence_global_index must be an integer."
            )

        state = dict(
            unit.get(
                "relational_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "same_sentence_validation"
            )
            != "COMPLETE"
        ):
            raise RelationalIntelligenceError(
                "Same-sentence validation must be COMPLETE before Stage J."
            )

        if (
            state.get(
                "cross_sentence_validation"
            )
            != "PENDING"
        ):
            raise RelationalIntelligenceError(
                "Cross-sentence validation must be PENDING."
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

    units_by_id = {
        record[
            "unit_id"
        ]:
            record
        for record in unit_records
    }

    candidate_to_unit = {}

    for record in unit_records:
        for candidate in (
            record[
                "unit"
            ].get(
                "relational_candidates"
            )
            or []
        ):
            candidate_id = str(
                candidate.get(
                    "relational_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise RelationalIntelligenceError(
                    "Relational candidate ID is required."
                )

            if candidate_id in candidate_to_unit:
                raise RelationalIntelligenceError(
                    "Duplicate relational candidate ID detected."
                )

            candidate_to_unit[
                candidate_id
            ] = record

    source_candidates = list(
        same_sentence_result.get(
            "relational_candidates"
        )
        or []
    )

    validated_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise RelationalIntelligenceError(
                "Every relational candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "relational_candidate_id"
            )
            or ""
        )

        record = candidate_to_unit.get(
            candidate_id
        )

        if record is None:
            raise RelationalIntelligenceError(
                "Relational candidate has no canonical claim unit."
            )

        if (
            candidate.get(
                "cross_sentence_validation_performed"
            )
            is not False
        ):
            raise RelationalIntelligenceError(
                "Candidate must not already have cross-sentence validation."
            )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_valid"
            )
            is True
        )

        normalization_supported = (
            candidate.get(
                "relation_normalization_status"
            )
            == "NORMALIZED"
            and bool(
                candidate.get(
                    "canonical_relation"
                )
            )
        )

        directionality_supported = (
            candidate.get(
                "directionality_resolved"
            )
            is True
        )

        same_subject_supported = (
            candidate.get(
                "same_sentence_subject_supported"
            )
            is True
        )

        same_object_supported = (
            candidate.get(
                "same_sentence_object_supported"
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

        cross_subject_supported = False
        cross_object_supported = False

        subject_support_evidence = None
        object_support_evidence = None

        if (
            not same_sentence_valid
            and normalization_supported
            and directionality_supported
            and candidate.get(
                "same_sentence_id_match"
            )
            is True
        ):
            for adjacent in adjacent_records:
                if not same_subject_supported:
                    (
                        supported,
                        method,
                    ) = span_present(
                        str(
                            candidate.get(
                                "canonical_subject_text"
                            )
                            or candidate.get(
                                "subject_text"
                            )
                            or ""
                        ),
                        adjacent[
                            "text"
                        ],
                        candidate.get(
                            "canonical_subject_grounding"
                        )
                        or candidate.get(
                            "subject_grounding"
                        ),
                    )

                    if supported:
                        cross_subject_supported = True

                        subject_support_evidence = {
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

                if not same_object_supported:
                    (
                        supported,
                        method,
                    ) = span_present(
                        str(
                            candidate.get(
                                "canonical_object_text"
                            )
                            or candidate.get(
                                "object_text"
                            )
                            or ""
                        ),
                        adjacent[
                            "text"
                        ],
                        candidate.get(
                            "canonical_object_grounding"
                        )
                        or candidate.get(
                            "object_grounding"
                        ),
                    )

                    if supported:
                        cross_object_supported = True

                        object_support_evidence = {
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

        combined_subject_supported = (
            same_subject_supported
            or cross_subject_supported
        )

        combined_object_supported = (
            same_object_supported
            or cross_object_supported
        )

        if same_sentence_valid:
            cross_sentence_status = (
                "NOT_REQUIRED_ALREADY_VALIDATED"
            )

            cross_sentence_valid = False

            final_relation_validated = True

            validation_reason = (
                "SAME_SENTENCE_VALIDATION_ALREADY_SUFFICIENT"
            )

        elif (
            candidate.get(
                "relation_normalization_status"
            )
            == "UNSUPPORTED"
        ):
            cross_sentence_status = (
                "NOT_VALIDATED_UNSUPPORTED_RELATION"
            )

            cross_sentence_valid = False

            final_relation_validated = False

            validation_reason = (
                "RELATION_NOT_CANONICALLY_NORMALIZED"
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

            final_relation_validated = False

            validation_reason = (
                "CANONICAL_SENTENCE_ID_MISMATCH_NOT_RESCUED"
            )

        elif not normalization_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_NORMALIZATION_INCOMPLETE"
            )

            cross_sentence_valid = False

            final_relation_validated = False

            validation_reason = (
                "RELATION_NORMALIZATION_NOT_COMPLETE"
            )

        elif not directionality_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_DIRECTIONALITY_UNRESOLVED"
            )

            cross_sentence_valid = False

            final_relation_validated = False

            validation_reason = (
                "DIRECTIONALITY_NOT_RESOLVED"
            )

        elif (
            combined_subject_supported
            and combined_object_supported
            and (
                cross_subject_supported
                or cross_object_supported
            )
        ):
            cross_sentence_status = (
                "VALIDATED_CROSS_SENTENCE"
            )

            cross_sentence_valid = True

            final_relation_validated = True

            validation_reason = None

        else:
            cross_sentence_status = (
                "NOT_VALIDATED_INSUFFICIENT_ADJACENT_SUPPORT"
            )

            cross_sentence_valid = False

            final_relation_validated = False

            validation_reason = (
                "IMMEDIATE_SAME_SECTION_ADJACENT_EVIDENCE_INSUFFICIENT"
            )

        validated = dict(
            candidate
        )

        validated.update({
            "cross_sentence_validation_status":
                cross_sentence_status,

            "cross_sentence_valid":
                cross_sentence_valid,

            "cross_sentence_validation_reason":
                validation_reason,

            "cross_sentence_subject_supported":
                cross_subject_supported,

            "cross_sentence_object_supported":
                cross_object_supported,

            "combined_subject_supported":
                combined_subject_supported,

            "combined_object_supported":
                combined_object_supported,

            "cross_sentence_subject_evidence":
                subject_support_evidence,

            "cross_sentence_object_evidence":
                object_support_evidence,

            "adjacent_same_section_sentence_count":
                len(
                    adjacent_records
                ),

            "relation_validated":
                final_relation_validated,

            "cross_sentence_validation_performed":
                True,

            "truth_assessed":
                False,

            "causal_reasoning_performed":
                False,

            "external_authority_checked":
                False,
        })

        validated_candidates.append(
            validated
        )

    validated_by_id = {
        candidate.get(
            "relational_candidate_id"
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
                "relational_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "relational_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "relational_candidate_id"
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise RelationalIntelligenceError(
                    "Relational candidate/unit cross-sentence mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "cross_sentence_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "cross_sentence_relation_validation_performed"
        ] = True

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "causal_reasoning_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "relational_candidates":
                unit_candidates,

            "cross_sentence_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "cross_sentence_valid"
                    )
                    is True
                ),

            "final_relation_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "relation_validated"
                    )
                    is True
                ),

            "relational_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        validated_units.append(
            updated_unit
        )

    validated_units_by_id = {
        unit.get(
            "relational_claim_unit_id"
        ):
            unit
        for unit in validated_units
    }

    validated_sections = []

    for section in (
        same_sentence_result.get(
            "relational_sections"
        )
        or []
    ):
        section_units = []

        for old_unit in (
            section.get(
                "relational_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "relational_claim_unit_id"
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise RelationalIntelligenceError(
                    "Relational section/unit cross-sentence mismatch."
                )

            section_units.append(
                validated_unit
            )

        validated_sections.append({
            **dict(section),

            "relational_claim_units":
                section_units,

            "cross_sentence_validated_count":
                sum(
                    unit.get(
                        "cross_sentence_validated_count",
                        0,
                    )
                    for unit in section_units
                ),

            "final_relation_validated_count":
                sum(
                    unit.get(
                        "final_relation_validated_count",
                        0,
                    )
                    for unit in section_units
                ),

            "cross_sentence_validation_complete":
                True,
        })

    cross_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "cross_sentence_valid"
        )
        is True
    )

    already_same_sentence_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "same_sentence_valid"
        )
        is True
    )

    final_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "relation_validated"
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
        "cross_sentence_relation_validation_performed"
    ] = True

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "causal_reasoning_performed"
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
            "relational_cross_sentence_validation_v1",

        "patch":
            "4.6.7J",

        "status":
            "RELATIONAL_CROSS_SENTENCE_VALIDATION_COMPLETE",

        "relational_sections":
            validated_sections,

        "relational_claim_units":
            validated_units,

        "relational_candidates":
            validated_candidates,

        "cross_sentence_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "already_same_sentence_validated_count":
                already_same_sentence_count,

            "cross_sentence_validated_count":
                cross_validated_count,

            "final_relation_validated_count":
                final_validated_count,

            "final_relation_not_validated_count":
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

            "unrestricted_cross_sentence_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "causal_reasoning_performed":
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
            "relation_confidence_evidence_assessment",
    })

    return result



def assess_relational_confidence_evidence_v1(
    cross_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Assess article-local relational evidence strength.

    Confidence reflects support quality inside the article only.

    It does NOT:
    - establish factual truth,
    - perform causal reasoning,
    - use external authority,
    - perform ontology alignment,
    - perform duplicate resolution,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        cross_sentence_result,
        Mapping,
    ):
        raise RelationalIntelligenceError(
            "cross_sentence_result must be a mapping."
        )

    if (
        cross_sentence_result.get(
            "schema_version"
        )
        != "relational_cross_sentence_validation_v1"
    ):
        raise RelationalIntelligenceError(
            "Stage K requires relational_cross_sentence_validation_v1."
        )

    if (
        cross_sentence_result.get(
            "status"
        )
        != "RELATIONAL_CROSS_SENTENCE_VALIDATION_COMPLETE"
    ):
        raise RelationalIntelligenceError(
            "Cross-sentence validation must be complete."
        )

    if (
        cross_sentence_result.get(
            "phase"
        )
        != "4.6.7"
    ):
        raise RelationalIntelligenceError(
            "Stage K requires Phase 4.6.7 input."
        )

    if (
        cross_sentence_result.get(
            "patch"
        )
        != "4.6.7J"
    ):
        raise RelationalIntelligenceError(
            "Stage K requires canonical 4.6.7J input."
        )

    if (
        cross_sentence_result.get(
            "next_stage"
        )
        != "relation_confidence_evidence_assessment"
    ):
        raise RelationalIntelligenceError(
            "Stage J must hand off to relation_confidence_evidence_assessment."
        )

    if (
        cross_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence must remain transient."
        )

    source_candidates = list(
        cross_sentence_result.get(
            "relational_candidates"
        )
        or []
    )

    assessed_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise RelationalIntelligenceError(
                "Every relational candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "relational_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise RelationalIntelligenceError(
                "Relational candidate ID is required."
            )

        if (
            candidate.get(
                "relation_evidence_assessed"
            )
            is True
        ):
            raise RelationalIntelligenceError(
                "Candidate must not already have evidence assessment."
            )

        relation_validated = (
            candidate.get(
                "relation_validated"
            )
            is True
        )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_valid"
            )
            is True
        )

        cross_sentence_valid = (
            candidate.get(
                "cross_sentence_valid"
            )
            is True
        )

        subject_grounding = (
            candidate.get(
                "canonical_subject_grounding"
            )
            or candidate.get(
                "subject_grounding"
            )
            or {}
        )

        object_grounding = (
            candidate.get(
                "canonical_object_grounding"
            )
            or candidate.get(
                "object_grounding"
            )
            or {}
        )

        subject_grounded = (
            isinstance(
                subject_grounding,
                Mapping,
            )
            and subject_grounding.get(
                "grounded"
            )
            is True
        )

        object_grounded = (
            isinstance(
                object_grounding,
                Mapping,
            )
            and object_grounding.get(
                "grounded"
            )
            is True
        )

        subject_confidence = (
            subject_grounding.get(
                "extraction_confidence"
            )
            if isinstance(
                subject_grounding,
                Mapping,
            )
            else None
        )

        object_confidence = (
            object_grounding.get(
                "extraction_confidence"
            )
            if isinstance(
                object_grounding,
                Mapping,
            )
            else None
        )

        grounding_confidences = [
            value
            for value in (
                subject_confidence,
                object_confidence,
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

        if not relation_validated:
            evidence_score = 0.0
            evidence_strength = "INSUFFICIENT"
            primary_basis = "RELATION_NOT_VALIDATED"

        else:
            evidence_score = 0.50

            if same_sentence_valid:
                evidence_score += 0.30
                primary_basis = "SAME_SENTENCE_VALIDATED"

            elif cross_sentence_valid:
                evidence_score += 0.18
                primary_basis = "ADJACENT_CROSS_SENTENCE_VALIDATED"

            else:
                primary_basis = "VALIDATED_WITHOUT_RECOGNIZED_EVIDENCE_MODE"

            if (
                subject_grounded
                and object_grounded
            ):
                evidence_score += 0.10

            elif (
                subject_grounded
                or object_grounded
            ):
                evidence_score += 0.05

            if grounding_confidence is not None:
                evidence_score += (
                    grounding_confidence
                    * 0.10
                )

            evidence_score = round(
                min(
                    evidence_score,
                    0.99,
                ),
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
            "relation_evidence_assessed":
                True,

            "relation_evidence_score":
                evidence_score,

            "relation_evidence_strength":
                evidence_strength,

            "relation_evidence_basis":
                primary_basis,

            "relation_evidence_factors": {
                "relation_validated":
                    relation_validated,

                "same_sentence_valid":
                    same_sentence_valid,

                "cross_sentence_valid":
                    cross_sentence_valid,

                "subject_grounded":
                    subject_grounded,

                "object_grounded":
                    object_grounded,

                "grounding_confidence":
                    grounding_confidence,
            },

            "truth_assessed":
                False,

            "causal_reasoning_performed":
                False,

            "external_authority_checked":
                False,
        })

        assessed_candidates.append(
            assessed
        )

    assessed_by_id = {
        candidate.get(
            "relational_candidate_id"
        ):
            candidate
        for candidate in assessed_candidates
    }

    assessed_units = []

    for unit in (
        cross_sentence_result.get(
            "relational_claim_units"
        )
        or []
    ):
        state = dict(
            unit.get(
                "relational_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "cross_sentence_validation"
            )
            != "COMPLETE"
        ):
            raise RelationalIntelligenceError(
                "Cross-sentence validation must be COMPLETE before Stage K."
            )

        if (
            state.get(
                "relation_evidence_assessment"
            )
            != "PENDING"
        ):
            raise RelationalIntelligenceError(
                "Relation evidence assessment must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "relational_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "relational_candidate_id"
            )

            assessed_candidate = (
                assessed_by_id.get(
                    candidate_id
                )
            )

            if assessed_candidate is None:
                raise RelationalIntelligenceError(
                    "Relational candidate/unit evidence mismatch."
                )

            unit_candidates.append(
                assessed_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "relation_evidence_assessment"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "relation_evidence_assessment_performed"
        ] = True

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "causal_reasoning_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "relational_candidates":
                unit_candidates,

            "strong_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "relation_evidence_strength"
                    )
                    == "STRONG"
                ),

            "moderate_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "relation_evidence_strength"
                    )
                    == "MODERATE"
                ),

            "limited_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "relation_evidence_strength"
                    )
                    == "LIMITED"
                ),

            "insufficient_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "relation_evidence_strength"
                    )
                    == "INSUFFICIENT"
                ),

            "relational_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        assessed_units.append(
            updated_unit
        )

    assessed_units_by_id = {
        unit.get(
            "relational_claim_unit_id"
        ):
            unit
        for unit in assessed_units
    }

    assessed_sections = []

    for section in (
        cross_sentence_result.get(
            "relational_sections"
        )
        or []
    ):
        section_units = []

        for old_unit in (
            section.get(
                "relational_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "relational_claim_unit_id"
            )

            assessed_unit = (
                assessed_units_by_id.get(
                    unit_id
                )
            )

            if assessed_unit is None:
                raise RelationalIntelligenceError(
                    "Relational section/unit evidence mismatch."
                )

            section_units.append(
                assessed_unit
            )

        assessed_sections.append({
            **dict(section),

            "relational_claim_units":
                section_units,

            "strong_relation_count":
                sum(
                    unit.get(
                        "strong_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "moderate_relation_count":
                sum(
                    unit.get(
                        "moderate_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "limited_relation_count":
                sum(
                    unit.get(
                        "limited_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "insufficient_relation_count":
                sum(
                    unit.get(
                        "insufficient_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "relation_evidence_assessment_complete":
                True,
        })

    strong_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "relation_evidence_strength"
        )
        == "STRONG"
    )

    moderate_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "relation_evidence_strength"
        )
        == "MODERATE"
    )

    limited_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "relation_evidence_strength"
        )
        == "LIMITED"
    )

    insufficient_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "relation_evidence_strength"
        )
        == "INSUFFICIENT"
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
        "relation_evidence_assessment_performed"
    ] = True

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "causal_reasoning_performed"
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
            "relational_evidence_assessment_v1",

        "patch":
            "4.6.7K",

        "status":
            "RELATIONAL_EVIDENCE_ASSESSMENT_COMPLETE",

        "relational_sections":
            assessed_sections,

        "relational_claim_units":
            assessed_units,

        "relational_candidates":
            assessed_candidates,

        "relation_evidence_summary": {
            "candidate_count":
                len(
                    assessed_candidates
                ),

            "strong_relation_count":
                strong_count,

            "moderate_relation_count":
                moderate_count,

            "limited_relation_count":
                limited_count,

            "insufficient_relation_count":
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

            "confidence_scope":
                "ARTICLE_LOCAL_EVIDENCE_STRENGTH_ONLY",

            "truth_assessment_performed":
                False,

            "causal_reasoning_performed":
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
            "duplicate_redundant_relation_resolution",
    })

    return result



def resolve_duplicate_redundant_relations_v1(
    evidence_assessment_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve exact article-local duplicate relational candidates.

    Duplicate identity is based on canonical subject + canonical relation
    + canonical object. Symmetric relations use an order-independent
    endpoint key.

    The strongest candidate becomes the representative. Duplicate
    provenance is preserved.

    This stage does NOT:
    - perform fuzzy semantic similarity,
    - merge merely related relations,
    - infer new relations,
    - establish factual truth,
    - perform causal reasoning,
    - use external authority,
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
        raise RelationalIntelligenceError(
            "evidence_assessment_result must be a mapping."
        )

    if (
        evidence_assessment_result.get(
            "schema_version"
        )
        != "relational_evidence_assessment_v1"
    ):
        raise RelationalIntelligenceError(
            "Stage L requires relational_evidence_assessment_v1."
        )

    if (
        evidence_assessment_result.get(
            "status"
        )
        != "RELATIONAL_EVIDENCE_ASSESSMENT_COMPLETE"
    ):
        raise RelationalIntelligenceError(
            "Relation evidence assessment must be complete."
        )

    if (
        evidence_assessment_result.get(
            "phase"
        )
        != "4.6.7"
    ):
        raise RelationalIntelligenceError(
            "Stage L requires Phase 4.6.7 input."
        )

    if (
        evidence_assessment_result.get(
            "patch"
        )
        != "4.6.7K"
    ):
        raise RelationalIntelligenceError(
            "Stage L requires canonical 4.6.7K input."
        )

    if (
        evidence_assessment_result.get(
            "next_stage"
        )
        != "duplicate_redundant_relation_resolution"
    ):
        raise RelationalIntelligenceError(
            "Stage K must hand off to duplicate_redundant_relation_resolution."
        )

    if (
        evidence_assessment_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence must remain transient."
        )

    def normalize(value: Any) -> str:
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
                "canonical_relation"
            )
        )

        subject = endpoint_text(
            candidate,
            "subject",
        )

        object_ = endpoint_text(
            candidate,
            "object",
        )

        if (
            not relation
            or not subject
            or not object_
        ):
            return None

        if (
            candidate.get(
                "relation_is_symmetric"
            )
            is True
        ):
            subject, object_ = sorted(
                (
                    subject,
                    object_,
                )
            )

        return (
            subject,
            relation,
            object_,
        )

    source_candidates = list(
        evidence_assessment_result.get(
            "relational_candidates"
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
            raise RelationalIntelligenceError(
                "Every relational candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "relational_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise RelationalIntelligenceError(
                "Relational candidate ID is required."
            )

        if (
            candidate.get(
                "relation_evidence_assessed"
            )
            is not True
        ):
            raise RelationalIntelligenceError(
                "Every candidate must have completed evidence assessment."
            )

        if (
            candidate.get(
                "duplicate_resolution_performed"
            )
            is True
        ):
            raise RelationalIntelligenceError(
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
                            "relation_evidence_strength"
                        )
                        or ""
                    ),
                    0,
                ),
                -float(
                    candidate.get(
                        "relation_evidence_score"
                    )
                    or 0.0
                ),
                0
                if candidate.get(
                    "same_sentence_valid"
                )
                is True
                else 1,
                0
                if candidate.get(
                    "cross_sentence_valid"
                )
                is True
                else 1,
                str(
                    candidate.get(
                        "relational_candidate_id"
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
                    "relational_candidate_id"
                )
            )
            for member in ordered
        ]

        raw_key = "|".join(
            key
        )

        group_id = (
            "relational_duplicate_group_"
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
                "relational_candidate_id"
            )
        )

        for index, member in enumerate(
            ordered
        ):
            member_id = str(
                member.get(
                    "relational_candidate_id"
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

                "duplicate_group_id":
                    group_id,

                "duplicate_group_size":
                    len(
                        ordered
                    ),

                "duplicate_member_ids":
                    member_ids,

                "is_duplicate_group":
                    is_duplicate_group,

                "is_representative_relation":
                    is_representative,

                "representative_relation_candidate_id":
                    representative_id,

                "duplicate_of_relation_candidate_id":
                    (
                        None
                        if is_representative
                        else representative_id
                    ),

                "duplicate_resolution_status":
                    (
                        "REPRESENTATIVE"
                        if is_representative
                        else "DUPLICATE_REDUNDANT"
                    ),

                "duplicate_key": {
                    "subject":
                        key[
                            0
                        ],

                    "relation":
                        key[
                            1
                        ],

                    "object":
                        key[
                            2
                        ],
                },

                "fuzzy_similarity_performed":
                    False,

                "truth_assessed":
                    False,

                "causal_reasoning_performed":
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
                "relational_candidate_id"
            )
        )

        resolved = dict(
            member
        )

        resolved.update({
            "duplicate_resolution_performed":
                True,

            "duplicate_group_id":
                None,

            "duplicate_group_size":
                1,

            "duplicate_member_ids": [
                member_id,
            ],

            "is_duplicate_group":
                False,

            "is_representative_relation":
                True,

            "representative_relation_candidate_id":
                member_id,

            "duplicate_of_relation_candidate_id":
                None,

            "duplicate_resolution_status":
                "UNIQUE_NON_GROUPABLE",

            "duplicate_key":
                None,

            "fuzzy_similarity_performed":
                False,

            "truth_assessed":
                False,

            "causal_reasoning_performed":
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
                "relational_candidate_id"
            )
        )

        resolved = resolved_by_id.get(
            candidate_id
        )

        if resolved is None:
            raise RelationalIntelligenceError(
                "Duplicate resolution lost a candidate."
            )

        resolved_candidates.append(
            resolved
        )

    representative_candidates.sort(
        key=lambda candidate: str(
            candidate.get(
                "relational_candidate_id"
            )
            or ""
        )
    )

    resolved_units = []

    for unit in (
        evidence_assessment_result.get(
            "relational_claim_units"
        )
        or []
    ):
        state = dict(
            unit.get(
                "relational_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "relation_evidence_assessment"
            )
            != "COMPLETE"
        ):
            raise RelationalIntelligenceError(
                "Relation evidence assessment must be COMPLETE before Stage L."
            )

        if (
            state.get(
                "duplicate_relation_resolution"
            )
            != "PENDING"
        ):
            raise RelationalIntelligenceError(
                "Duplicate relation resolution must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "relational_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "relational_candidate_id"
            )

            resolved_candidate = (
                resolved_by_id.get(
                    candidate_id
                )
            )

            if resolved_candidate is None:
                raise RelationalIntelligenceError(
                    "Relational candidate/unit duplicate mismatch."
                )

            unit_candidates.append(
                resolved_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "duplicate_relation_resolution"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "duplicate_relation_resolution_performed"
        ] = True

        updated_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "causal_reasoning_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "relational_candidates":
                unit_candidates,

            "representative_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "is_representative_relation"
                    )
                    is True
                ),

            "duplicate_redundant_relation_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "duplicate_resolution_status"
                    )
                    == "DUPLICATE_REDUNDANT"
                ),

            "relational_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        resolved_units.append(
            updated_unit
        )

    resolved_units_by_id = {
        unit.get(
            "relational_claim_unit_id"
        ):
            unit
        for unit in resolved_units
    }

    resolved_sections = []

    for section in (
        evidence_assessment_result.get(
            "relational_sections"
        )
        or []
    ):
        section_units = []

        for old_unit in (
            section.get(
                "relational_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "relational_claim_unit_id"
            )

            resolved_unit = (
                resolved_units_by_id.get(
                    unit_id
                )
            )

            if resolved_unit is None:
                raise RelationalIntelligenceError(
                    "Relational section/unit duplicate mismatch."
                )

            section_units.append(
                resolved_unit
            )

        resolved_sections.append({
            **dict(section),

            "relational_claim_units":
                section_units,

            "representative_relation_count":
                sum(
                    unit.get(
                        "representative_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "duplicate_redundant_relation_count":
                sum(
                    unit.get(
                        "duplicate_redundant_relation_count",
                        0,
                    )
                    for unit in section_units
                ),

            "duplicate_relation_resolution_complete":
                True,
        })

    representative_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "is_representative_relation"
        )
        is True
    )

    redundant_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "duplicate_resolution_status"
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
        "duplicate_relation_resolution_performed"
    ] = True

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "causal_reasoning_performed"
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
            "relational_duplicate_resolution_v1",

        "patch":
            "4.6.7L",

        "status":
            "RELATIONAL_DUPLICATE_RESOLUTION_COMPLETE",

        "relational_sections":
            resolved_sections,

        "relational_claim_units":
            resolved_units,

        "relational_candidates":
            resolved_candidates,

        "representative_relational_candidates":
            representative_candidates,

        "duplicate_resolution_summary": {
            "candidate_count":
                len(
                    resolved_candidates
                ),

            "representative_relation_count":
                representative_count,

            "duplicate_redundant_relation_count":
                redundant_count,

            "duplicate_group_count":
                duplicate_group_count,

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

            "symmetric_endpoint_order_normalized":
                True,

            "strongest_evidence_representative_selected":
                True,

            "duplicate_provenance_preserved":
                True,

            "fuzzy_similarity_performed":
                False,

            "truth_assessment_performed":
                False,

            "causal_reasoning_performed":
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
            "article_relational_consolidation",
    })

    return result



def consolidate_article_relational_intelligence_v1(
    duplicate_resolution_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Consolidate completed article-local relational intelligence
    into article-level and section-level summaries.

    Only representative relations are used for the canonical
    consolidated relation set. Full candidate provenance remains
    preserved in the source candidate collection.

    This stage does NOT:
    - create new relations,
    - infer missing relations,
    - perform factual truth assessment,
    - perform causal reasoning,
    - use external authority,
    - perform fuzzy similarity,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        duplicate_resolution_result,
        Mapping,
    ):
        raise RelationalIntelligenceError(
            "duplicate_resolution_result must be a mapping."
        )

    if (
        duplicate_resolution_result.get(
            "schema_version"
        )
        != "relational_duplicate_resolution_v1"
    ):
        raise RelationalIntelligenceError(
            "Stage M requires relational_duplicate_resolution_v1."
        )

    if (
        duplicate_resolution_result.get(
            "status"
        )
        != "RELATIONAL_DUPLICATE_RESOLUTION_COMPLETE"
    ):
        raise RelationalIntelligenceError(
            "Duplicate resolution must be complete."
        )

    if (
        duplicate_resolution_result.get(
            "phase"
        )
        != "4.6.7"
    ):
        raise RelationalIntelligenceError(
            "Stage M requires Phase 4.6.7 input."
        )

    if (
        duplicate_resolution_result.get(
            "patch"
        )
        != "4.6.7L"
    ):
        raise RelationalIntelligenceError(
            "Stage M requires canonical 4.6.7L input."
        )

    if (
        duplicate_resolution_result.get(
            "next_stage"
        )
        != "article_relational_consolidation"
    ):
        raise RelationalIntelligenceError(
            "Stage L must hand off to article_relational_consolidation."
        )

    if (
        duplicate_resolution_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence must remain transient."
        )

    source_candidates = list(
        duplicate_resolution_result.get(
            "relational_candidates"
        )
        or []
    )

    representative_candidates = list(
        duplicate_resolution_result.get(
            "representative_relational_candidates"
        )
        or []
    )

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise RelationalIntelligenceError(
                "Every relational candidate must be a mapping."
            )

        if (
            candidate.get(
                "duplicate_resolution_performed"
            )
            is not True
        ):
            raise RelationalIntelligenceError(
                "All candidates must complete duplicate resolution before Stage M."
            )

    for candidate in representative_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise RelationalIntelligenceError(
                "Every representative relation must be a mapping."
            )

        if (
            candidate.get(
                "is_representative_relation"
            )
            is not True
        ):
            raise RelationalIntelligenceError(
                "Representative relation list contains a non-representative candidate."
            )

    representative_ids = {
        str(
            candidate.get(
                "relational_candidate_id"
            )
            or ""
        )
        for candidate in representative_candidates
    }

    if "" in representative_ids:
        raise RelationalIntelligenceError(
            "Representative relation candidate ID is required."
        )

    expected_representative_ids = {
        str(
            candidate.get(
                "relational_candidate_id"
            )
            or ""
        )
        for candidate in source_candidates
        if candidate.get(
            "is_representative_relation"
        )
        is True
    }

    if representative_ids != expected_representative_ids:
        raise RelationalIntelligenceError(
            "Representative relation list does not match resolved candidates."
        )

    relation_family_counts = {}
    relation_type_counts = {}
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

    consolidated_relations = []

    for candidate in representative_candidates:
        relation_family = str(
            candidate.get(
                "relation_family"
            )
            or "UNSPECIFIED"
        )

        canonical_relation = str(
            candidate.get(
                "canonical_relation"
            )
            or ""
        )

        evidence_strength = str(
            candidate.get(
                "relation_evidence_strength"
            )
            or "INSUFFICIENT"
        )

        relation_validated = (
            candidate.get(
                "relation_validated"
            )
            is True
        )

        relation_family_counts[
            relation_family
        ] = (
            relation_family_counts.get(
                relation_family,
                0,
            )
            + 1
        )

        relation_type_counts[
            canonical_relation
        ] = (
            relation_type_counts.get(
                canonical_relation,
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

        if relation_validated:
            validated_count += 1
        else:
            unvalidated_count += 1

        consolidated_relations.append({
            "relational_candidate_id":
                candidate.get(
                    "relational_candidate_id"
                ),

            "subject_text":
                candidate.get(
                    "canonical_subject_text"
                )
                or candidate.get(
                    "subject_text"
                ),

            "canonical_relation":
                candidate.get(
                    "canonical_relation"
                ),

            "object_text":
                candidate.get(
                    "canonical_object_text"
                )
                or candidate.get(
                    "object_text"
                ),

            "relation_family":
                candidate.get(
                    "relation_family"
                ),

            "directionality_type":
                candidate.get(
                    "directionality_type"
                ),

            "inverse_relation":
                candidate.get(
                    "inverse_relation"
                ),

            "relation_validated":
                relation_validated,

            "relation_evidence_score":
                candidate.get(
                    "relation_evidence_score"
                ),

            "relation_evidence_strength":
                evidence_strength,

            "same_sentence_valid":
                candidate.get(
                    "same_sentence_valid"
                )
                is True,

            "cross_sentence_valid":
                candidate.get(
                    "cross_sentence_valid"
                )
                is True,

            "section_id":
                candidate.get(
                    "section_id"
                ),

            "sentence_id":
                candidate.get(
                    "sentence_id"
                ),

            "duplicate_group_id":
                candidate.get(
                    "duplicate_group_id"
                ),

            "duplicate_group_size":
                candidate.get(
                    "duplicate_group_size"
                ),

            "causal_sensitive_relation":
                candidate.get(
                    "causal_sensitive_relation"
                )
                is True,

            "causal_interpretation_deferred":
                candidate.get(
                    "causal_interpretation_deferred"
                )
                is True,

            "truth_assessed":
                False,

            "causal_reasoning_performed":
                False,

            "external_authority_checked":
                False,
        })

    consolidated_relations.sort(
        key=lambda relation: (
            str(
                relation.get(
                    "section_id"
                )
                or ""
            ),
            str(
                relation.get(
                    "canonical_relation"
                )
                or ""
            ),
            str(
                relation.get(
                    "subject_text"
                )
                or ""
            ),
            str(
                relation.get(
                    "object_text"
                )
                or ""
            ),
            str(
                relation.get(
                    "relational_candidate_id"
                )
                or ""
            ),
        )
    )

    consolidated_sections = []

    for section in (
        duplicate_resolution_result.get(
            "relational_sections"
        )
        or []
    ):
        section_id = str(
            section.get(
                "section_id"
            )
            or ""
        )

        section_relations = [
            relation
            for relation in consolidated_relations
            if str(
                relation.get(
                    "section_id"
                )
                or ""
            )
            == section_id
        ]

        section_family_counts = {}

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
                    "relation_family"
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

            strength = str(
                relation.get(
                    "relation_evidence_strength"
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

            "representative_relations":
                section_relations,

            "representative_relation_count":
                len(
                    section_relations
                ),

            "validated_relation_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "relation_validated"
                    )
                    is True
                ),

            "unvalidated_relation_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "relation_validated"
                    )
                    is False
                ),

            "relation_family_counts":
                section_family_counts,

            "evidence_strength_counts":
                section_strength_counts,

            "relational_consolidation_complete":
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
            "duplicate_resolution_status"
        )
        == "DUPLICATE_REDUNDANT"
    )

    causal_sensitive_count = sum(
        1
        for relation in consolidated_relations
        if relation.get(
            "causal_sensitive_relation"
        )
        is True
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
        "article_relational_consolidation_performed"
    ] = True

    boundaries[
        "new_relation_inference_performed"
    ] = False

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "causal_reasoning_performed"
    ] = False

    boundaries[
        "external_authority_check_performed"
    ] = False

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "semantic_memory_write_performed"
    ] = False

    boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "relational_article_consolidation_v1",

        "patch":
            "4.6.7M",

        "status":
            "RELATIONAL_ARTICLE_CONSOLIDATION_COMPLETE",

        "consolidated_relational_sections":
            consolidated_sections,

        "consolidated_relations":
            consolidated_relations,

        "article_relational_summary": {
            "total_candidate_count":
                total_candidate_count,

            "representative_relation_count":
                representative_count,

            "duplicate_redundant_relation_count":
                redundant_count,

            "validated_relation_count":
                validated_count,

            "unvalidated_relation_count":
                unvalidated_count,

            "relation_family_counts":
                relation_family_counts,

            "relation_type_counts":
                relation_type_counts,

            "evidence_strength_counts":
                evidence_strength_counts,

            "causal_sensitive_relation_count":
                causal_sensitive_count,

            "causal_sensitive_relations_deferred_to":
                "4.6.8",

            "representative_count_matches_consolidated":
                (
                    representative_count
                    == len(
                        consolidated_relations
                    )
                ),

            "candidate_accounting_valid":
                (
                    representative_count
                    + redundant_count
                    == total_candidate_count
                ),

            "article_local_only":
                True,

            "new_relation_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "causal_reasoning_performed":
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
            "final_relational_intelligence_result",
    })

    return result



def build_final_relational_intelligence_result_v1(
    article_consolidation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build the final canonical Phase 4.6.7 Relational Intelligence result.

    This stage packages the completed article-local relational analysis
    without adding new interpretation.

    It does NOT:
    - certify the result,
    - create or infer relations,
    - establish factual truth,
    - perform causal reasoning,
    - use external authority,
    - perform fuzzy similarity,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        article_consolidation_result,
        Mapping,
    ):
        raise RelationalIntelligenceError(
            "article_consolidation_result must be a mapping."
        )

    if (
        article_consolidation_result.get(
            "schema_version"
        )
        != "relational_article_consolidation_v1"
    ):
        raise RelationalIntelligenceError(
            "Stage N requires relational_article_consolidation_v1."
        )

    if (
        article_consolidation_result.get(
            "status"
        )
        != "RELATIONAL_ARTICLE_CONSOLIDATION_COMPLETE"
    ):
        raise RelationalIntelligenceError(
            "Article relational consolidation must be complete."
        )

    if (
        article_consolidation_result.get(
            "phase"
        )
        != "4.6.7"
    ):
        raise RelationalIntelligenceError(
            "Stage N requires Phase 4.6.7 input."
        )

    if (
        article_consolidation_result.get(
            "patch"
        )
        != "4.6.7M"
    ):
        raise RelationalIntelligenceError(
            "Stage N requires canonical 4.6.7M input."
        )

    if (
        article_consolidation_result.get(
            "next_stage"
        )
        != "final_relational_intelligence_result"
    ):
        raise RelationalIntelligenceError(
            "Stage M must hand off to final_relational_intelligence_result."
        )

    if (
        article_consolidation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence must remain transient."
        )

    consolidated_relations = list(
        article_consolidation_result.get(
            "consolidated_relations"
        )
        or []
    )

    consolidated_sections = list(
        article_consolidation_result.get(
            "consolidated_relational_sections"
        )
        or []
    )

    full_candidates = list(
        article_consolidation_result.get(
            "relational_candidates"
        )
        or []
    )

    representative_candidates = list(
        article_consolidation_result.get(
            "representative_relational_candidates"
        )
        or []
    )

    summary = dict(
        article_consolidation_result.get(
            "article_relational_summary"
        )
        or {}
    )

    if (
        summary.get(
            "representative_count_matches_consolidated"
        )
        is not True
    ):
        raise RelationalIntelligenceError(
            "Representative/consolidated relation accounting must be valid."
        )

    if (
        summary.get(
            "candidate_accounting_valid"
        )
        is not True
    ):
        raise RelationalIntelligenceError(
            "Candidate accounting must be valid before Stage N."
        )

    if (
        summary.get(
            "causal_sensitive_relations_deferred_to"
        )
        != "4.6.8"
    ):
        raise RelationalIntelligenceError(
            "Causal-sensitive relations must remain deferred to Phase 4.6.8."
        )

    for relation in consolidated_relations:
        if not isinstance(
            relation,
            Mapping,
        ):
            raise RelationalIntelligenceError(
                "Every consolidated relation must be a mapping."
            )

        if (
            relation.get(
                "truth_assessed"
            )
            is not False
        ):
            raise RelationalIntelligenceError(
                "Relational Intelligence must not assess factual truth."
            )

        if (
            relation.get(
                "causal_reasoning_performed"
            )
            is not False
        ):
            raise RelationalIntelligenceError(
                "Relational Intelligence must not perform causal reasoning."
            )

        if (
            relation.get(
                "external_authority_checked"
            )
            is not False
        ):
            raise RelationalIntelligenceError(
                "Relational Intelligence must not use external authority."
            )

    boundaries = dict(
        article_consolidation_result.get(
            "processing_boundaries"
        )
        or {}
    )

    required_false_boundaries = (
        "new_relation_inference_performed",
        "truth_assessment_performed",
        "causal_reasoning_performed",
        "external_authority_check_performed",
        "fuzzy_similarity_performed",
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
            raise RelationalIntelligenceError(
                boundary_name
                + " must remain False in final Relational Intelligence."
            )

    if (
        boundaries.get(
            "article_relational_consolidation_performed"
        )
        is not True
    ):
        raise RelationalIntelligenceError(
            "Article relational consolidation boundary must be complete."
        )

    final_boundaries = dict(
        boundaries
    )

    final_boundaries[
        "final_relational_result_built"
    ] = True

    final_boundaries[
        "relational_certification_performed"
    ] = False

    result = {
        "schema_version":
            "relational_intelligence_result_v1",

        "relational_intelligence_version":
            article_consolidation_result.get(
                "relational_intelligence_version"
            )
            or "relational_intelligence_v1",

        "phase":
            "4.6.7",

        "patch":
            "4.6.7N",

        "status":
            "RELATIONAL_INTELLIGENCE_RESULT_COMPLETE",

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

        "consolidated_relations":
            consolidated_relations,

        "consolidated_relational_sections":
            consolidated_sections,

        "representative_relational_candidates":
            representative_candidates,

        "relational_candidates":
            full_candidates,

        "relational_claim_units":
            list(
                article_consolidation_result.get(
                    "relational_claim_units"
                )
                or []
            ),

        "article_relational_summary":
            summary,

        "relational_boundaries": {
            "article_local_only":
                True,

            "truth_verified":
                False,

            "truth_assessment_performed":
                False,

            "causal_reasoning_performed":
                False,

            "external_authority_checked":
                False,

            "fuzzy_similarity_performed":
                False,

            "new_relation_inference_performed":
                False,

            "linking_decisions_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,

            "causal_sensitive_relations_deferred_to":
                "4.6.8",
        },

        "processing_boundaries":
            final_boundaries,

        "certification": {
            "performed":
                False,

            "certified":
                False,

            "certification_stage":
                "4.6.7O",
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "relational_intelligence_certification",
    }

    return result



def certify_relational_intelligence_v1(
    final_relational_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Certify the final Phase 4.6.7 Relational Intelligence result.

    Certification validates structure, accounting, boundaries,
    provenance preservation, and handoff readiness.

    Certification does NOT:
    - add or infer relations,
    - establish factual truth,
    - perform causal reasoning,
    - use external authority,
    - perform similarity reasoning,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        final_relational_result,
        Mapping,
    ):
        raise RelationalIntelligenceError(
            "final_relational_result must be a mapping."
        )

    if (
        final_relational_result.get(
            "schema_version"
        )
        != "relational_intelligence_result_v1"
    ):
        raise RelationalIntelligenceError(
            "Stage O requires relational_intelligence_result_v1."
        )

    if (
        final_relational_result.get(
            "status"
        )
        != "RELATIONAL_INTELLIGENCE_RESULT_COMPLETE"
    ):
        raise RelationalIntelligenceError(
            "Final Relational Intelligence result must be complete."
        )

    if (
        final_relational_result.get(
            "phase"
        )
        != "4.6.7"
    ):
        raise RelationalIntelligenceError(
            "Stage O requires Phase 4.6.7 input."
        )

    if (
        final_relational_result.get(
            "patch"
        )
        != "4.6.7N"
    ):
        raise RelationalIntelligenceError(
            "Stage O requires canonical 4.6.7N input."
        )

    if (
        final_relational_result.get(
            "next_stage"
        )
        != "relational_intelligence_certification"
    ):
        raise RelationalIntelligenceError(
            "Stage N must hand off to relational_intelligence_certification."
        )

    if (
        final_relational_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise RelationalIntelligenceError(
            "Relational Intelligence must remain transient."
        )

    identity = dict(
        final_relational_result.get(
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
            raise RelationalIntelligenceError(
                "Required article identity field missing: "
                + field
            )

    consolidated_relations = list(
        final_relational_result.get(
            "consolidated_relations"
        )
        or []
    )

    representative_candidates = list(
        final_relational_result.get(
            "representative_relational_candidates"
        )
        or []
    )

    full_candidates = list(
        final_relational_result.get(
            "relational_candidates"
        )
        or []
    )

    claim_units = list(
        final_relational_result.get(
            "relational_claim_units"
        )
        or []
    )

    consolidated_sections = list(
        final_relational_result.get(
            "consolidated_relational_sections"
        )
        or []
    )

    summary = dict(
        final_relational_result.get(
            "article_relational_summary"
        )
        or {}
    )

    if (
        summary.get(
            "representative_count_matches_consolidated"
        )
        is not True
    ):
        raise RelationalIntelligenceError(
            "Representative/consolidated accounting is invalid."
        )

    if (
        summary.get(
            "candidate_accounting_valid"
        )
        is not True
    ):
        raise RelationalIntelligenceError(
            "Candidate accounting is invalid."
        )

    if (
        summary.get(
            "representative_relation_count"
        )
        != len(
            consolidated_relations
        )
    ):
        raise RelationalIntelligenceError(
            "Consolidated relation count does not match summary."
        )

    if (
        len(
            representative_candidates
        )
        != len(
            consolidated_relations
        )
    ):
        raise RelationalIntelligenceError(
            "Representative candidate count does not match consolidated relations."
        )

    if (
        summary.get(
            "total_candidate_count"
        )
        != len(
            full_candidates
        )
    ):
        raise RelationalIntelligenceError(
            "Full candidate count does not match summary."
        )

    consolidated_ids = [
        str(
            relation.get(
                "relational_candidate_id"
            )
            or ""
        )
        for relation in consolidated_relations
    ]

    representative_ids = [
        str(
            candidate.get(
                "relational_candidate_id"
            )
            or ""
        )
        for candidate in representative_candidates
    ]

    if any(
        not candidate_id
        for candidate_id in consolidated_ids
    ):
        raise RelationalIntelligenceError(
            "Every consolidated relation requires a candidate ID."
        )

    if (
        set(
            consolidated_ids
        )
        != set(
            representative_ids
        )
    ):
        raise RelationalIntelligenceError(
            "Consolidated relations and representative candidates disagree."
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
        raise RelationalIntelligenceError(
            "Duplicate consolidated relation IDs are not allowed."
        )

    for relation in consolidated_relations:
        if not isinstance(
            relation,
            Mapping,
        ):
            raise RelationalIntelligenceError(
                "Every consolidated relation must be a mapping."
            )

        if (
            relation.get(
                "truth_assessed"
            )
            is not False
        ):
            raise RelationalIntelligenceError(
                "Relational Intelligence must not assess factual truth."
            )

        if (
            relation.get(
                "causal_reasoning_performed"
            )
            is not False
        ):
            raise RelationalIntelligenceError(
                "Relational Intelligence must not perform causal reasoning."
            )

        if (
            relation.get(
                "external_authority_checked"
            )
            is not False
        ):
            raise RelationalIntelligenceError(
                "Relational Intelligence must not use external authority."
            )

        if (
            relation.get(
                "causal_sensitive_relation"
            )
            is True
            and relation.get(
                "causal_interpretation_deferred"
            )
            is not True
        ):
            raise RelationalIntelligenceError(
                "Causal-sensitive relations must remain explicitly deferred."
            )

    relational_boundaries = dict(
        final_relational_result.get(
            "relational_boundaries"
        )
        or {}
    )

    required_false_relational_boundaries = (
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

    if (
        relational_boundaries.get(
            "article_local_only"
        )
        is not True
    ):
        raise RelationalIntelligenceError(
            "Final Relational Intelligence must remain article-local."
        )

    for boundary_name in required_false_relational_boundaries:
        if (
            relational_boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise RelationalIntelligenceError(
                boundary_name
                + " must remain False."
            )

    if (
        relational_boundaries.get(
            "causal_sensitive_relations_deferred_to"
        )
        != "4.6.8"
    ):
        raise RelationalIntelligenceError(
            "Causal-sensitive relations must hand off to Phase 4.6.8."
        )

    processing_boundaries = dict(
        final_relational_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        processing_boundaries.get(
            "article_relational_consolidation_performed"
        )
        is not True
    ):
        raise RelationalIntelligenceError(
            "Article relational consolidation must be complete."
        )

    if (
        processing_boundaries.get(
            "final_relational_result_built"
        )
        is not True
    ):
        raise RelationalIntelligenceError(
            "Final Relational Intelligence result must already be built."
        )

    if (
        processing_boundaries.get(
            "relational_certification_performed"
        )
        is not False
    ):
        raise RelationalIntelligenceError(
            "Input must not already be certified."
        )

    certification = dict(
        final_relational_result.get(
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
        != "4.6.7O"
    ):
        raise RelationalIntelligenceError(
            "Stage N certification state is invalid."
        )

    causal_sensitive_count = sum(
        1
        for relation in consolidated_relations
        if relation.get(
            "causal_sensitive_relation"
        )
        is True
    )

    if (
        summary.get(
            "causal_sensitive_relation_count"
        )
        != causal_sensitive_count
    ):
        raise RelationalIntelligenceError(
            "Causal-sensitive relation count does not match summary."
        )

    certified_processing_boundaries = dict(
        processing_boundaries
    )

    certified_processing_boundaries[
        "relational_certification_performed"
    ] = True

    certified_processing_boundaries[
        "relational_intelligence_certified"
    ] = True

    result = dict(
        final_relational_result
    )

    result.update({
        "schema_version":
            "certified_relational_intelligence_result_v1",

        "patch":
            "4.6.7O",

        "status":
            "RELATIONAL_INTELLIGENCE_CERTIFIED",

        "processing_boundaries":
            certified_processing_boundaries,

        "certification": {
            "performed":
                True,

            "certified":
                True,

            "certification_stage":
                "4.6.7O",

            "certification_scope":
                "ARTICLE_LOCAL_RELATIONAL_INTELLIGENCE",

            "structural_integrity_verified":
                True,

            "candidate_accounting_verified":
                True,

            "representative_relation_integrity_verified":
                True,

            "provenance_preserved":
                True,

            "boundary_integrity_verified":
                True,

            "causal_deferral_verified":
                True,

            "truth_assessment_performed":
                False,

            "causal_reasoning_performed":
                False,

            "external_authority_check_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,
        },

        "relational_certification_summary": {
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

            "representative_relation_count":
                len(
                    representative_candidates
                ),

            "consolidated_relation_count":
                len(
                    consolidated_relations
                ),

            "validated_relation_count":
                summary.get(
                    "validated_relation_count"
                ),

            "unvalidated_relation_count":
                summary.get(
                    "unvalidated_relation_count"
                ),

            "causal_sensitive_relation_count":
                causal_sensitive_count,

            "causal_sensitive_relations_deferred_to":
                "4.6.8",

            "article_local_only":
                True,

            "certification_passed":
                True,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "causal_intelligence",
    })

    return result
