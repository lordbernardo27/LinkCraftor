from __future__ import annotations

import hashlib
import re

from typing import Any, Mapping


LOGICAL_INTELLIGENCE_VERSION = "logical_intelligence_v1"


class LogicalIntelligenceError(ValueError):
    """Raised when canonical Logical Intelligence contracts are violated."""


def validate_logical_intelligence_intake_v1(
    section_evidence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate certified Phase 4.6.5 Section Evidence Intelligence
    before Logical Intelligence begins.

    This stage performs validation only.

    It does NOT:
    - infer logical relationships,
    - classify premises or conclusions,
    - perform causal reasoning,
    - perform factual truth verification,
    - select phrases, targets, URLs, or link types,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        section_evidence_result,
        Mapping,
    ):
        raise LogicalIntelligenceError(
            "section_evidence_result must be a mapping."
        )

    if (
        section_evidence_result.get("schema_version")
        != "section_evidence_intelligence_result_v1"
    ):
        raise LogicalIntelligenceError(
            "Logical Intelligence requires "
            "section_evidence_intelligence_result_v1."
        )

    if (
        section_evidence_result.get("status")
        != "SECTION_EVIDENCE_RESULT_COMPLETE"
    ):
        raise LogicalIntelligenceError(
            "Section Evidence Intelligence is not complete."
        )

    if (
        section_evidence_result.get("phase")
        != "4.6.5"
    ):
        raise LogicalIntelligenceError(
            "Logical Intelligence requires Phase 4.6.5 input."
        )

    if (
        section_evidence_result.get("persistence_policy")
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise LogicalIntelligenceError(
            "Logical Intelligence requires transient "
            "article-local Section Evidence."
        )

    units = section_evidence_result.get(
        "section_evidence_units"
    )

    if not isinstance(units, list) or not units:
        raise LogicalIntelligenceError(
            "Section Evidence Unit collection is missing or empty."
        )

    canonical_order = list(
        section_evidence_result.get(
            "canonical_section_order"
        )
        or []
    )

    if not canonical_order:
        raise LogicalIntelligenceError(
            "Canonical section order is missing."
        )

    if len(units) != len(canonical_order):
        raise LogicalIntelligenceError(
            "Section unit count does not match canonical order."
        )

    actual_order = [
        unit.get("section_id")
        for unit in units
        if isinstance(unit, Mapping)
    ]

    if actual_order != canonical_order:
        raise LogicalIntelligenceError(
            "Section Evidence Units are not in canonical order."
        )

    required_identity_fields = (
        "workspace_id",
        "document_id",
        "source_type",
        "source_id",
        "content_hash",
        "body_ref",
        "article_id",
    )

    for field in required_identity_fields:
        value = section_evidence_result.get(field)

        if value in (
            None,
            "",
        ):
            raise LogicalIntelligenceError(
                f"Missing canonical identity field: {field}"
            )

    required_layers = (
        "structural_evidence",
        "entity_concept_evidence",
        "phrase_neighborhood_evidence",
        "topic_intent_evidence",
        "claim_evidence",
        "evidence_strength",
        "coverage",
        "contradiction_analysis",
    )

    total_claims = 0
    total_statements = 0

    seen_section_ids = set()
    seen_sentence_ids = set()

    for unit in units:
        if not isinstance(unit, Mapping):
            raise LogicalIntelligenceError(
                "Invalid Section Evidence Unit."
            )

        section_id = str(
            unit.get("section_id") or ""
        ).strip()

        if not section_id:
            raise LogicalIntelligenceError(
                "Section Evidence Unit has no section_id."
            )

        if section_id in seen_section_ids:
            raise LogicalIntelligenceError(
                f"Duplicate section_id: {section_id}"
            )

        seen_section_ids.add(
            section_id
        )

        if (
            unit.get("article_id")
            != section_evidence_result.get("article_id")
        ):
            raise LogicalIntelligenceError(
                "Section article_id does not match "
                "the parent article."
            )

        state = (
            unit.get("evidence_attachment_state")
            or {}
        )

        for layer in required_layers:
            if state.get(layer) != "ATTACHED":
                raise LogicalIntelligenceError(
                    f"Required evidence layer is not attached: "
                    f"{layer}"
                )

            if not isinstance(
                unit.get(layer),
                Mapping,
            ):
                raise LogicalIntelligenceError(
                    f"Required evidence payload is invalid: "
                    f"{layer}"
                )

        finalization = (
            unit.get(
                "section_evidence_finalization"
            )
            or {}
        )

        if (
            finalization.get(
                "all_required_evidence_attached"
            )
            is not True
        ):
            raise LogicalIntelligenceError(
                "Section Evidence finalization is incomplete."
            )

        if (
            finalization.get("article_local_only")
            is not True
        ):
            raise LogicalIntelligenceError(
                "Logical Intelligence requires "
                "article-local Section Evidence."
            )

        claim_evidence = (
            unit.get("claim_evidence")
            or {}
        )

        statements = (
            claim_evidence.get("statements")
            or []
        )

        claims = (
            claim_evidence.get(
                "claim_candidates"
            )
            or []
        )

        if not isinstance(statements, list):
            raise LogicalIntelligenceError(
                "Section statement collection is invalid."
            )

        if not isinstance(claims, list):
            raise LogicalIntelligenceError(
                "Section claim collection is invalid."
            )

        if (
            len(statements)
            != claim_evidence.get(
                "statement_count"
            )
        ):
            raise LogicalIntelligenceError(
                "Section statement count mismatch."
            )

        if (
            len(claims)
            != claim_evidence.get(
                "claim_candidate_count"
            )
        ):
            raise LogicalIntelligenceError(
                "Section claim candidate count mismatch."
            )

        total_statements += len(
            statements
        )

        total_claims += len(
            claims
        )

        previous_global_index = None

        for claim in claims:
            if not isinstance(claim, Mapping):
                raise LogicalIntelligenceError(
                    "Invalid claim candidate record."
                )

            if claim.get("claim_candidate") is not True:
                raise LogicalIntelligenceError(
                    "Non-claim record found inside "
                    "claim_candidates."
                )

            if (
                claim.get("article_id")
                != section_evidence_result.get(
                    "article_id"
                )
            ):
                raise LogicalIntelligenceError(
                    "Claim article_id mismatch."
                )

            if claim.get("section_id") != section_id:
                raise LogicalIntelligenceError(
                    "Claim section_id mismatch."
                )

            sentence_id = str(
                claim.get("sentence_id") or ""
            ).strip()

            if not sentence_id:
                raise LogicalIntelligenceError(
                    "Claim candidate has no sentence_id."
                )

            if sentence_id in seen_sentence_ids:
                raise LogicalIntelligenceError(
                    f"Duplicate claim sentence_id: "
                    f"{sentence_id}"
                )

            seen_sentence_ids.add(
                sentence_id
            )

            global_index = claim.get(
                "sentence_global_index"
            )

            if not isinstance(
                global_index,
                int,
            ):
                raise LogicalIntelligenceError(
                    "Claim sentence_global_index "
                    "must be an integer."
                )

            if (
                previous_global_index is not None
                and global_index
                <= previous_global_index
            ):
                raise LogicalIntelligenceError(
                    "Claim order is not monotonic "
                    "inside the canonical section."
                )

            previous_global_index = (
                global_index
            )

    summary = (
        section_evidence_result.get(
            "article_evidence_summary"
        )
        or {}
    )

    if (
        total_statements
        != summary.get("statement_count")
    ):
        raise LogicalIntelligenceError(
            "Article statement count does not match "
            "Section Evidence summary."
        )

    if (
        total_claims
        != summary.get("claim_candidate_count")
    ):
        raise LogicalIntelligenceError(
            "Article claim count does not match "
            "Section Evidence summary."
        )

    boundaries = (
        section_evidence_result.get(
            "processing_boundaries"
        )
        or {}
    )

    forbidden_completed_work = (
        "truth_assessment_performed",
        "external_authority_check_performed",
        "logical_reasoning_performed",
        "claim_integrity_adjudication_performed",
        "phrase_selected_for_linking",
        "target_selected",
        "url_selected",
        "link_type_selected",
        "highlight_color_selected",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for field in forbidden_completed_work:
        if boundaries.get(field) is not False:
            raise LogicalIntelligenceError(
                f"Unexpected upstream/downstream work "
                f"detected: {field}"
            )

    return {
        "schema_version":
            "logical_intelligence_intake_v1",

        "logical_intelligence_version":
            LOGICAL_INTELLIGENCE_VERSION,

        "phase":
            "4.6.6",

        "patch":
            "4.6.6B",

        "status":
            "LOGICAL_INTELLIGENCE_INTAKE_ACCEPTED",

        "workspace_id":
            section_evidence_result.get(
                "workspace_id"
            ),

        "document_id":
            section_evidence_result.get(
                "document_id"
            ),

        "source_type":
            section_evidence_result.get(
                "source_type"
            ),

        "source_id":
            section_evidence_result.get(
                "source_id"
            ),

        "content_hash":
            section_evidence_result.get(
                "content_hash"
            ),

        "body_ref":
            section_evidence_result.get(
                "body_ref"
            ),

        "article_id":
            section_evidence_result.get(
                "article_id"
            ),

        "title":
            section_evidence_result.get(
                "title"
            ),

        "section_count":
            len(units),

        "statement_count":
            total_statements,

        "claim_candidate_count":
            total_claims,

        "canonical_section_order":
            canonical_order,

        "validation": {
            "valid":
                True,

            "canonical_4_6_5_schema":
                True,

            "canonical_section_order_preserved":
                True,

            "all_required_evidence_attached":
                True,

            "article_identity_valid":
                True,

            "claim_identity_valid":
                True,

            "claim_order_valid":
                True,

            "article_local_only":
                True,

            "logical_reasoning_performed":
                False,
        },

        "processing_boundaries": {
            "validation_only":
                True,

            "article_body_reparsed":
                False,

            "logical_claim_units_built":
                False,

            "logical_signal_interpretation_performed":
                False,

            "logical_relation_detection_performed":
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

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "logical_claim_unit_construction",
    }


def build_logical_claim_units_v1(
    section_evidence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build canonical article-local Logical Claim Units from
    certified Phase 4.6.5 Section Evidence.

    This stage normalizes claims and their existing evidence
    context for later Logical Intelligence processing.

    It does NOT:
    - interpret discourse signals,
    - infer logical relationships,
    - identify premises or conclusions,
    - perform causal reasoning,
    - determine factual truth,
    - select links, phrases, targets, URLs, or colors,
    - write Semantic Memory,
    - persist intelligence.
    """

    intake = validate_logical_intelligence_intake_v1(
        section_evidence_result
    )

    if (
        intake.get("status")
        != "LOGICAL_INTELLIGENCE_INTAKE_ACCEPTED"
    ):
        raise LogicalIntelligenceError(
            "Canonical Logical Intelligence intake "
            "was not accepted."
        )

    article_id = str(
        section_evidence_result.get(
            "article_id"
        )
        or ""
    )

    section_units = section_evidence_result.get(
        "section_evidence_units"
    ) or []

    logical_sections = []
    all_logical_claim_units = []

    seen_logical_ids = set()
    seen_statement_ids = set()
    seen_sentence_ids = set()

    previous_global_index = None

    for section in section_units:
        section_id = str(
            section.get("section_id")
            or ""
        )

        claim_evidence = (
            section.get("claim_evidence")
            or {}
        )

        claims = list(
            claim_evidence.get(
                "claim_candidates"
            )
            or []
        )

        strength = (
            section.get("evidence_strength")
            or {}
        )

        claim_scores = list(
            strength.get("claim_scores")
            or []
        )

        contradiction = (
            section.get(
                "contradiction_analysis"
            )
            or {}
        )

        claim_flags = list(
            contradiction.get(
                "claim_flags"
            )
            or []
        )

        coverage = (
            section.get("coverage")
            or {}
        )

        if (
            coverage.get("section_id")
            != section_id
        ):
            raise LogicalIntelligenceError(
                "Section coverage identity mismatch."
            )

        score_by_statement = {}
        flag_by_statement = {}

        for score in claim_scores:
            statement_id = str(
                score.get(
                    "statement_evidence_id"
                )
                or ""
            )

            if not statement_id:
                raise LogicalIntelligenceError(
                    "Evidence-strength record has no "
                    "statement_evidence_id."
                )

            if statement_id in score_by_statement:
                raise LogicalIntelligenceError(
                    "Duplicate evidence-strength mapping "
                    f"for {statement_id}."
                )

            score_by_statement[
                statement_id
            ] = score

        for flag in claim_flags:
            statement_id = str(
                flag.get(
                    "statement_evidence_id"
                )
                or ""
            )

            if not statement_id:
                raise LogicalIntelligenceError(
                    "Claim flag record has no "
                    "statement_evidence_id."
                )

            if statement_id in flag_by_statement:
                raise LogicalIntelligenceError(
                    "Duplicate claim-flag mapping "
                    f"for {statement_id}."
                )

            flag_by_statement[
                statement_id
            ] = flag

        if len(score_by_statement) != len(claims):
            raise LogicalIntelligenceError(
                "Claim-to-strength mapping is not one-to-one."
            )

        if len(flag_by_statement) != len(claims):
            raise LogicalIntelligenceError(
                "Claim-to-flag mapping is not one-to-one."
            )

        section_logical_claims = []

        for claim_index, claim in enumerate(
            claims
        ):
            statement_id = str(
                claim.get(
                    "statement_evidence_id"
                )
                or ""
            )

            sentence_id = str(
                claim.get("sentence_id")
                or ""
            )

            if not statement_id:
                raise LogicalIntelligenceError(
                    "Claim has no statement_evidence_id."
                )

            if statement_id in seen_statement_ids:
                raise LogicalIntelligenceError(
                    f"Duplicate statement_evidence_id: "
                    f"{statement_id}"
                )

            if sentence_id in seen_sentence_ids:
                raise LogicalIntelligenceError(
                    f"Duplicate logical sentence_id: "
                    f"{sentence_id}"
                )

            score = score_by_statement.get(
                statement_id
            )

            flag = flag_by_statement.get(
                statement_id
            )

            if score is None:
                raise LogicalIntelligenceError(
                    "Missing evidence-strength record "
                    f"for {statement_id}."
                )

            if flag is None:
                raise LogicalIntelligenceError(
                    "Missing contradiction/insufficiency "
                    f"record for {statement_id}."
                )

            for companion_name, companion in (
                ("evidence-strength", score),
                ("claim-flag", flag),
            ):
                if (
                    companion.get("sentence_id")
                    != sentence_id
                ):
                    raise LogicalIntelligenceError(
                        f"{companion_name} sentence_id "
                        "does not match claim."
                    )

                if (
                    companion.get("section_id")
                    != section_id
                ):
                    raise LogicalIntelligenceError(
                        f"{companion_name} section_id "
                        "does not match claim."
                    )

                if (
                    companion.get(
                        "statement_evidence_id"
                    )
                    != statement_id
                ):
                    raise LogicalIntelligenceError(
                        f"{companion_name} statement identity "
                        "does not match claim."
                    )

                if (
                    companion.get("text")
                    != claim.get("text")
                ):
                    raise LogicalIntelligenceError(
                        f"{companion_name} text "
                        "does not match canonical claim."
                    )

            global_index = claim.get(
                "sentence_global_index"
            )

            article_position = claim.get(
                "article_position"
            )

            if not isinstance(
                global_index,
                int,
            ):
                raise LogicalIntelligenceError(
                    "Canonical sentence_global_index "
                    "must be an integer."
                )

            if not isinstance(
                article_position,
                int,
            ):
                raise LogicalIntelligenceError(
                    "Canonical article_position "
                    "must be an integer."
                )

            if (
                previous_global_index
                is not None
                and global_index
                <= previous_global_index
            ):
                raise LogicalIntelligenceError(
                    "Logical claims are not in canonical "
                    "article sentence order."
                )

            stable_material = (
                article_id
                + "|"
                + statement_id
                + "|"
                + sentence_id
            )

            logical_claim_unit_id = (
                "logical_claim_"
                + hashlib.sha256(
                    stable_material.encode(
                        "utf-8"
                    )
                ).hexdigest()[:16]
            )

            if (
                logical_claim_unit_id
                in seen_logical_ids
            ):
                raise LogicalIntelligenceError(
                    "Duplicate Logical Claim Unit ID."
                )

            logical_unit = {
                "logical_claim_unit_id":
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
                    section.get(
                        "section_evidence_unit_id"
                    ),

                "section_index":
                    section.get(
                        "section_index"
                    ),

                "section_title":
                    section.get(
                        "section_title"
                    ),

                "heading_level":
                    section.get(
                        "heading_level"
                    ),

                "block_id":
                    claim.get(
                        "block_id"
                    ),

                "paragraph_id":
                    claim.get(
                        "paragraph_id"
                    ),

                "block_type":
                    claim.get(
                        "block_type"
                    ),

                "block_index":
                    claim.get(
                        "block_index"
                    ),

                "sentence_index":
                    claim.get(
                        "sentence_index"
                    ),

                "sentence_global_index":
                    global_index,

                "article_position":
                    article_position,

                "claim_index_in_section":
                    claim_index,

                "text":
                    claim.get(
                        "text"
                    ),

                "word_count":
                    claim.get(
                        "word_count"
                    ),

                "character_count":
                    claim.get(
                        "character_count"
                    ),

                "statement_form":
                    claim.get(
                        "statement_form"
                    ),

                "canonical_claim_candidate":
                    True,

                "evidence_context": {
                    "evidence_strength_id":
                        score.get(
                            "evidence_strength_id"
                        ),

                    "evidence_strength_score":
                        score.get(
                            "evidence_strength_score"
                        ),

                    "evidence_strength_band":
                        score.get(
                            "evidence_strength_band"
                        ),

                    "evidence_strength_scope":
                        score.get(
                            "score_scope"
                        ),

                    "dimension_scores":
                        dict(
                            score.get(
                                "dimension_scores"
                            )
                            or {}
                        ),

                    "raw_support_counts":
                        dict(
                            score.get(
                                "raw_support_counts"
                            )
                            or {}
                        ),

                    "section_coverage_score":
                        coverage.get(
                            "coverage_score"
                        ),

                    "section_coverage_status":
                        coverage.get(
                            "coverage_status"
                        ),

                    "insufficient_evidence_flag":
                        flag.get(
                            "insufficient_evidence_flag"
                        ),

                    "insufficient_evidence_reasons":
                        list(
                            flag.get(
                                "insufficient_evidence_reasons"
                            )
                            or []
                        ),

                    "negation_present":
                        flag.get(
                            "negation_present"
                        ),

                    "contradiction_candidate":
                        flag.get(
                            "contradiction_candidate"
                        ),

                    "contradiction_pair_ids":
                        list(
                            flag.get(
                                "contradiction_pair_ids"
                            )
                            or []
                        ),
                },

                "logical_analysis_state": {
                    "discourse_signal_interpretation":
                        "PENDING",

                    "adjacent_relation_detection":
                        "PENDING",

                    "non_adjacent_relation_detection":
                        "PENDING",

                    "premise_conclusion_mapping":
                        "PENDING",

                    "qualification_exception_mapping":
                        "PENDING",

                    "conditional_mapping":
                        "PENDING",

                    "support_clarification_contrast_mapping":
                        "PENDING",

                    "logical_chain_construction":
                        "PENDING",

                    "logical_tension_detection":
                        "PENDING",
                },

                "processing_boundaries": {
                    "article_local_only":
                        True,

                    "logical_reasoning_performed":
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

            section_logical_claims.append(
                logical_unit
            )

            all_logical_claim_units.append(
                logical_unit
            )

        logical_sections.append({
            "section_id":
                section_id,

            "section_evidence_unit_id":
                section.get(
                    "section_evidence_unit_id"
                ),

            "section_index":
                section.get(
                    "section_index"
                ),

            "section_title":
                section.get(
                    "section_title"
                ),

            "heading_level":
                section.get(
                    "heading_level"
                ),

            "logical_claim_count":
                len(
                    section_logical_claims
                ),

            "logical_claim_units":
                section_logical_claims,
        })

    expected_claim_count = (
        section_evidence_result.get(
            "article_evidence_summary",
            {},
        ).get(
            "claim_candidate_count"
        )
    )

    if (
        len(all_logical_claim_units)
        != expected_claim_count
    ):
        raise LogicalIntelligenceError(
            "Logical Claim Unit count does not match "
            "certified claim count."
        )

    if (
        len(logical_sections)
        != intake.get("section_count")
    ):
        raise LogicalIntelligenceError(
            "Logical section count does not match "
            "accepted intake."
        )

    return {
        "schema_version":
            "logical_claim_units_v1",

        "logical_intelligence_version":
            LOGICAL_INTELLIGENCE_VERSION,

        "phase":
            "4.6.6",

        "patch":
            "4.6.6C",

        "status":
            "LOGICAL_CLAIM_UNITS_BUILT",

        "workspace_id":
            section_evidence_result.get(
                "workspace_id"
            ),

        "document_id":
            section_evidence_result.get(
                "document_id"
            ),

        "source_type":
            section_evidence_result.get(
                "source_type"
            ),

        "source_id":
            section_evidence_result.get(
                "source_id"
            ),

        "content_hash":
            section_evidence_result.get(
                "content_hash"
            ),

        "body_ref":
            section_evidence_result.get(
                "body_ref"
            ),

        "article_id":
            article_id,

        "title":
            section_evidence_result.get(
                "title"
            ),

        "canonical_section_order":
            list(
                section_evidence_result.get(
                    "canonical_section_order"
                )
                or []
            ),

        "section_count":
            len(
                logical_sections
            ),

        "logical_claim_unit_count":
            len(
                all_logical_claim_units
            ),

        "logical_sections":
            logical_sections,

        "logical_claim_units":
            all_logical_claim_units,

        "construction_summary": {
            "source_claim_count":
                expected_claim_count,

            "logical_claim_unit_count":
                len(
                    all_logical_claim_units
                ),

            "one_to_one_claim_mapping":
                (
                    len(all_logical_claim_units)
                    == expected_claim_count
                ),

            "canonical_order_preserved":
                True,

            "evidence_strength_attached":
                True,

            "coverage_attached":
                True,

            "insufficiency_flags_attached":
                True,

            "contradiction_candidate_flags_attached":
                True,

            "logical_reasoning_performed":
                False,
        },

        "processing_boundaries": {
            "article_body_reparsed":
                False,

            "logical_claim_units_built":
                True,

            "logical_signal_interpretation_performed":
                False,

            "logical_relation_detection_performed":
                False,

            "premise_conclusion_mapping_performed":
                False,

            "logical_chain_construction_performed":
                False,

            "logical_tension_detection_performed":
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
            "context_aware_discourse_signal_interpretation",
    }


def interpret_discourse_signals_v1(
    logical_claim_units_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Interpret explicit article-local discourse signals inside
    canonical Logical Claim Units.

    This stage identifies candidate logical discourse roles only.

    It does NOT:
    - connect claims into logical relations,
    - classify premise/conclusion pairs,
    - perform causal reasoning,
    - adjudicate contradictions,
    - determine factual truth,
    - perform external authority checks,
    - select links, phrases, targets, URLs, or colors,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        logical_claim_units_result,
        Mapping,
    ):
        raise LogicalIntelligenceError(
            "logical_claim_units_result must be a mapping."
        )

    if (
        logical_claim_units_result.get("schema_version")
        != "logical_claim_units_v1"
    ):
        raise LogicalIntelligenceError(
            "Discourse interpretation requires "
            "logical_claim_units_v1."
        )

    if (
        logical_claim_units_result.get("status")
        != "LOGICAL_CLAIM_UNITS_BUILT"
    ):
        raise LogicalIntelligenceError(
            "Logical Claim Unit construction is incomplete."
        )

    if (
        logical_claim_units_result.get("phase")
        != "4.6.6"
    ):
        raise LogicalIntelligenceError(
            "Discourse interpretation requires Phase 4.6.6 input."
        )

    units = list(
        logical_claim_units_result.get(
            "logical_claim_units"
        )
        or []
    )

    if not units:
        raise LogicalIntelligenceError(
            "Logical Claim Units are missing."
        )

    signal_patterns = (
        (
            "CONDITION",
            re.compile(
                r"(?i)(?<!\w)"
                r"(if|unless|provided that|as long as)"
                r"(?!\w)"
            ),
        ),
        (
            "CONTRAST",
            re.compile(
                r"(?i)(?<!\w)"
                r"(but|however|although|though|whereas|yet|despite)"
                r"(?!\w)"
            ),
        ),
        (
            "EXCEPTION",
            re.compile(
                r"(?i)(?<!\w)"
                r"(except|apart from|other than)"
                r"(?!\w)"
            ),
        ),
        (
            "ALTERNATIVE",
            re.compile(
                r"(?i)(?<!\w)"
                r"(instead|rather|otherwise|either|neither)"
                r"(?!\w)"
            ),
        ),
        (
            "ELABORATION",
            re.compile(
                r"(?i)(?<!\w)"
                r"(for example|for instance|such as|"
                r"in other words|specifically)"
                r"(?!\w)"
            ),
        ),
        (
            "QUALIFICATION",
            re.compile(
                r"(?i)(?<!\w)"
                r"(usually|often|sometimes|generally|typically|"
                r"may|might|probably|likely)"
                r"(?!\w)"
            ),
        ),
    )

    conclusion_pattern = re.compile(
        r"(?i)(?<!\w)"
        r"(therefore|thus|hence|consequently)"
        r"(?!\w)"
    )

    clause_so_pattern = re.compile(
        r"(?i)"
        r"(?:^|[.;:?-]\s+|,\s+)"
        r"(so)"
        r"\b"
    )

    because_pattern = re.compile(
        r"(?i)(?<!\w)"
        r"(because|since)"
        r"(?!\w)"
    )

    interpreted_units = []
    total_signal_count = 0
    units_with_signals = 0

    signal_type_counts = {}

    for unit in units:
        if not isinstance(unit, Mapping):
            raise LogicalIntelligenceError(
                "Invalid Logical Claim Unit."
            )

        text_value = str(
            unit.get("text")
            or ""
        )

        signals = []

        def add_signal(
            signal_type: str,
            match: Any,
            contextual_role: str,
            confidence: float,
        ) -> None:
            nonlocal total_signal_count

            matched_text = match.group(1)

            signal = {
                "signal_type":
                    signal_type,

                "matched_text":
                    matched_text,

                "start_char":
                    match.start(1),

                "end_char":
                    match.end(1),

                "contextual_role":
                    contextual_role,

                "confidence":
                    confidence,

                "accepted":
                    True,

                "logical_relation_inferred":
                    False,
            }

            signals.append(
                signal
            )

            total_signal_count += 1

            signal_type_counts[
                signal_type
            ] = (
                signal_type_counts.get(
                    signal_type,
                    0,
                )
                + 1
            )

        for signal_type, pattern in signal_patterns:
            for match in pattern.finditer(
                text_value
            ):
                contextual_role = {
                    "CONDITION":
                        "introduces_or_marks_condition",

                    "CONTRAST":
                        "marks_contrast_or_concession",

                    "EXCEPTION":
                        "marks_exception",

                    "ALTERNATIVE":
                        "marks_alternative",

                    "ELABORATION":
                        "marks_example_or_elaboration",

                    "QUALIFICATION":
                        "modifies_assertion_strength_or_scope",
                }[
                    signal_type
                ]

                confidence = {
                    "CONDITION": 0.95,
                    "CONTRAST": 0.95,
                    "EXCEPTION": 0.95,
                    "ALTERNATIVE": 0.85,
                    "ELABORATION": 0.95,
                    "QUALIFICATION": 0.80,
                }[
                    signal_type
                ]

                add_signal(
                    signal_type,
                    match,
                    contextual_role,
                    confidence,
                )

        for match in conclusion_pattern.finditer(
            text_value
        ):
            add_signal(
                "CONCLUSION",
                match,
                "marks_explicit_conclusion_or_result",
                0.98,
            )

        for match in clause_so_pattern.finditer(
            text_value
        ):
            start = match.start(1)

            prefix = text_value[
                max(
                    0,
                    start - 12,
                ):
                start
            ].lower()

            suffix = text_value[
                match.end(1):
                min(
                    len(text_value),
                    match.end(1) + 12,
                )
            ].lower()

            false_positive = (
                suffix.lstrip().startswith(
                    "much"
                )
                or prefix.rstrip().endswith(
                    "heard"
                )
            )

            if not false_positive:
                add_signal(
                    "CONCLUSION",
                    match,
                    "marks_clause_level_result_or_conclusion",
                    0.88,
                )

        for match in because_pattern.finditer(
            text_value
        ):
            add_signal(
                "REASON",
                match,
                "introduces_explicit_reason_or_basis",
                0.95,
            )

        signals.sort(
            key=lambda item: (
                item["start_char"],
                item["end_char"],
                item["signal_type"],
            )
        )

        updated_unit = dict(
            unit
        )

        state = dict(
            updated_unit.get(
                "logical_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "discourse_signal_interpretation"
            )
            != "PENDING"
        ):
            raise LogicalIntelligenceError(
                "Discourse signal state was not PENDING."
            )

        state[
            "discourse_signal_interpretation"
        ] = "COMPLETE"

        updated_unit[
            "logical_analysis_state"
        ] = state

        updated_unit[
            "discourse_signal_analysis"
        ] = {
            "analysis_scope":
                "CLAIM_LOCAL_EXPLICIT_DISCOURSE_SIGNALS",

            "signal_count":
                len(signals),

            "signals":
                signals,

            "has_explicit_logical_signal":
                bool(signals),

            "context_aware_interpretation":
                True,

            "simple_keyword_classification_only":
                False,

            "logical_relation_inferred":
                False,

            "premise_conclusion_pair_mapped":
                False,

            "causal_relation_inferred":
                False,

            "truth_assessed":
                False,
        }

        if signals:
            units_with_signals += 1

        interpreted_units.append(
            updated_unit
        )

    sections = []

    by_section = {}

    for unit in interpreted_units:
        by_section.setdefault(
            unit.get("section_id"),
            [],
        ).append(
            unit
        )

    for source_section in (
        logical_claim_units_result.get(
            "logical_sections"
        )
        or []
    ):
        section_id = source_section.get(
            "section_id"
        )

        section_units = by_section.get(
            section_id,
            [],
        )

        sections.append({
            "section_id":
                section_id,

            "section_evidence_unit_id":
                source_section.get(
                    "section_evidence_unit_id"
                ),

            "section_index":
                source_section.get(
                    "section_index"
                ),

            "section_title":
                source_section.get(
                    "section_title"
                ),

            "heading_level":
                source_section.get(
                    "heading_level"
                ),

            "logical_claim_count":
                len(
                    section_units
                ),

            "claims_with_explicit_signals":
                sum(
                    1
                    for unit in section_units
                    if (
                        unit.get(
                            "discourse_signal_analysis",
                            {},
                        ).get(
                            "has_explicit_logical_signal"
                        )
                        is True
                    )
                ),

            "logical_claim_units":
                section_units,
        })

    boundaries = dict(
        logical_claim_units_result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "logical_signal_interpretation_performed"
    ] = True

    boundaries[
        "logical_relation_detection_performed"
    ] = False

    boundaries[
        "premise_conclusion_mapping_performed"
    ] = False

    boundaries[
        "logical_chain_construction_performed"
    ] = False

    boundaries[
        "logical_tension_detection_performed"
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

    return {
        "schema_version":
            "logical_discourse_signal_result_v1",

        "logical_intelligence_version":
            LOGICAL_INTELLIGENCE_VERSION,

        "phase":
            "4.6.6",

        "patch":
            "4.6.6D",

        "status":
            "LOGICAL_DISCOURSE_SIGNALS_INTERPRETED",

        "workspace_id":
            logical_claim_units_result.get(
                "workspace_id"
            ),

        "document_id":
            logical_claim_units_result.get(
                "document_id"
            ),

        "source_type":
            logical_claim_units_result.get(
                "source_type"
            ),

        "source_id":
            logical_claim_units_result.get(
                "source_id"
            ),

        "content_hash":
            logical_claim_units_result.get(
                "content_hash"
            ),

        "body_ref":
            logical_claim_units_result.get(
                "body_ref"
            ),

        "article_id":
            logical_claim_units_result.get(
                "article_id"
            ),

        "title":
            logical_claim_units_result.get(
                "title"
            ),

        "canonical_section_order":
            list(
                logical_claim_units_result.get(
                    "canonical_section_order"
                )
                or []
            ),

        "section_count":
            len(
                sections
            ),

        "logical_claim_unit_count":
            len(
                interpreted_units
            ),

        "logical_sections":
            sections,

        "logical_claim_units":
            interpreted_units,

        "discourse_signal_summary": {
            "logical_claim_unit_count":
                len(
                    interpreted_units
                ),

            "claims_with_explicit_signals":
                units_with_signals,

            "claims_without_explicit_signals":
                (
                    len(interpreted_units)
                    - units_with_signals
                ),

            "total_signal_count":
                total_signal_count,

            "signal_type_counts":
                dict(
                    sorted(
                        signal_type_counts.items()
                    )
                ),

            "context_aware_interpretation":
                True,

            "logical_relations_inferred":
                False,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "adjacent_claim_logical_relation_detection",
    }


def detect_adjacent_claim_relations_v1(
    discourse_signal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Detect conservative logical relations between immediately
    adjacent claims inside the same canonical section.

    This stage may detect an adjacent relation, but it does NOT:
    - perform non-adjacent relation detection,
    - finalize premise/conclusion roles,
    - finalize qualification/exception structures,
    - finalize conditional structures,
    - perform causal reasoning,
    - adjudicate contradictions,
    - determine factual truth,
    - select links, targets, URLs, or highlight colors,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        discourse_signal_result,
        Mapping,
    ):
        raise LogicalIntelligenceError(
            "discourse_signal_result must be a mapping."
        )

    if (
        discourse_signal_result.get("schema_version")
        != "logical_discourse_signal_result_v1"
    ):
        raise LogicalIntelligenceError(
            "Adjacent relation detection requires "
            "logical_discourse_signal_result_v1."
        )

    if (
        discourse_signal_result.get("status")
        != "LOGICAL_DISCOURSE_SIGNALS_INTERPRETED"
    ):
        raise LogicalIntelligenceError(
            "Discourse-signal interpretation is incomplete."
        )

    if (
        discourse_signal_result.get("phase")
        != "4.6.6"
    ):
        raise LogicalIntelligenceError(
            "Adjacent relation detection requires Phase 4.6.6 input."
        )

    source_sections = list(
        discourse_signal_result.get(
            "logical_sections"
        )
        or []
    )

    if not source_sections:
        raise LogicalIntelligenceError(
            "Logical sections are missing."
        )

    connector_relation_map = {
        "CONTRAST":
            (
                "CONTRAST",
                0.97,
                "right_claim_initial_contrast_connector",
            ),

        "ELABORATION":
            (
                "ELABORATION",
                0.96,
                "right_claim_initial_elaboration_connector",
            ),

        "REASON":
            (
                "EXPLANATORY_REASON",
                0.94,
                "right_claim_initial_reason_connector",
            ),

        "CONCLUSION":
            (
                "RESULT_OR_CONCLUSION",
                0.95,
                "right_claim_initial_conclusion_connector",
            ),

        "EXCEPTION":
            (
                "EXCEPTION",
                0.94,
                "right_claim_initial_exception_connector",
            ),

        "ALTERNATIVE":
            (
                "ALTERNATIVE",
                0.90,
                "right_claim_initial_alternative_connector",
            ),
    }

    referential_pattern = re.compile(
        r"(?i)^\s*"
        r"(this|that|these|those|such)\b"
    )

    sequential_pattern = re.compile(
        r"(?i)^\s*"
        r"(then|next|afterward|afterwards)\b"
    )

    pair_evaluations = []
    relations = []

    updated_units_by_id = {}

    total_pair_count = 0
    detected_relation_count = 0
    deferred_condition_pair_count = 0

    relation_type_counts = {}

    for section in source_sections:
        section_id = section.get(
            "section_id"
        )

        section_units = list(
            section.get(
                "logical_claim_units"
            )
            or []
        )

        for unit in section_units:
            if not isinstance(unit, Mapping):
                raise LogicalIntelligenceError(
                    "Invalid Logical Claim Unit."
                )

            unit_id = unit.get(
                "logical_claim_unit_id"
            )

            if not unit_id:
                raise LogicalIntelligenceError(
                    "Logical Claim Unit has no ID."
                )

            updated_unit = dict(
                unit
            )

            state = dict(
                updated_unit.get(
                    "logical_analysis_state"
                )
                or {}
            )

            if (
                state.get(
                    "discourse_signal_interpretation"
                )
                != "COMPLETE"
            ):
                raise LogicalIntelligenceError(
                    "Discourse interpretation must be COMPLETE "
                    "before adjacent relation detection."
                )

            if (
                state.get(
                    "adjacent_relation_detection"
                )
                != "PENDING"
            ):
                raise LogicalIntelligenceError(
                    "Adjacent relation state was not PENDING."
                )

            state[
                "adjacent_relation_detection"
            ] = "COMPLETE"

            updated_unit[
                "logical_analysis_state"
            ] = state

            updated_unit[
                "adjacent_relation_context"
            ] = {
                "incoming_relation_ids": [],
                "outgoing_relation_ids": [],
                "detection_complete": True,
            }

            updated_units_by_id[
                unit_id
            ] = updated_unit

        for index in range(
            len(section_units) - 1
        ):
            left = section_units[index]
            right = section_units[index + 1]

            total_pair_count += 1

            left_id = left.get(
                "logical_claim_unit_id"
            )

            right_id = right.get(
                "logical_claim_unit_id"
            )

            right_text = str(
                right.get("text")
                or ""
            )

            left_signals = list(
                (
                    left.get(
                        "discourse_signal_analysis"
                    )
                    or {}
                ).get(
                    "signals",
                    []
                )
            )

            right_signals = list(
                (
                    right.get(
                        "discourse_signal_analysis"
                    )
                    or {}
                ).get(
                    "signals",
                    []
                )
            )

            initial_right_signals = [
                signal
                for signal in right_signals
                if (
                    signal.get("accepted") is True
                    and isinstance(
                        signal.get("start_char"),
                        int,
                    )
                    and signal.get("start_char") <= 5
                )
            ]

            detected = False
            relation_type = None
            confidence = None
            detection_basis = None
            cue_text = None
            cue_signal_type = None

            priority = (
                "CONTRAST",
                "ELABORATION",
                "REASON",
                "CONCLUSION",
                "EXCEPTION",
                "ALTERNATIVE",
            )

            for wanted_type in priority:
                matching_signal = next(
                    (
                        signal
                        for signal in initial_right_signals
                        if (
                            signal.get("signal_type")
                            == wanted_type
                        )
                    ),
                    None,
                )

                if matching_signal is None:
                    continue

                (
                    relation_type,
                    confidence,
                    detection_basis,
                ) = connector_relation_map[
                    wanted_type
                ]

                cue_text = matching_signal.get(
                    "matched_text"
                )

                cue_signal_type = wanted_type

                detected = True
                break

            referential_match = (
                referential_pattern.search(
                    right_text
                )
            )

            if (
                not detected
                and referential_match is not None
            ):
                detected = True
                relation_type = (
                    "REFERENTIAL_CONTINUATION"
                )
                confidence = 0.90
                detection_basis = (
                    "right_claim_initial_referential_bridge"
                )
                cue_text = referential_match.group(1)
                cue_signal_type = (
                    "REFERENTIAL_BRIDGE"
                )

            sequential_match = (
                sequential_pattern.search(
                    right_text
                )
            )

            if (
                not detected
                and sequential_match is not None
            ):
                detected = True
                relation_type = (
                    "SEQUENTIAL_CONTINUATION"
                )
                confidence = 0.90
                detection_basis = (
                    "right_claim_initial_sequence_bridge"
                )
                cue_text = sequential_match.group(1)
                cue_signal_type = (
                    "SEQUENCE_BRIDGE"
                )

            initial_condition_signals = [
                signal
                for signal in initial_right_signals
                if (
                    signal.get("signal_type")
                    == "CONDITION"
                )
            ]

            condition_deferred = bool(
                initial_condition_signals
                and not detected
            )

            if condition_deferred:
                deferred_condition_pair_count += 1

            pair_material = (
                str(
                    discourse_signal_result.get(
                        "article_id"
                    )
                    or ""
                )
                + "|"
                + str(left_id)
                + "|"
                + str(right_id)
            )

            pair_id = (
                "adjacent_pair_"
                + hashlib.sha256(
                    pair_material.encode(
                        "utf-8"
                    )
                ).hexdigest()[:16]
            )

            relation_id = None

            if detected:
                detected_relation_count += 1

                relation_id = (
                    "logical_relation_"
                    + hashlib.sha256(
                        (
                            pair_material
                            + "|"
                            + str(relation_type)
                        ).encode(
                            "utf-8"
                        )
                    ).hexdigest()[:16]
                )

                relation = {
                    "logical_relation_id":
                        relation_id,

                    "adjacent_pair_id":
                        pair_id,

                    "relation_scope":
                        "ADJACENT_SAME_SECTION",

                    "relation_type":
                        relation_type,

                    "confidence":
                        confidence,

                    "source_logical_claim_unit_id":
                        left_id,

                    "target_logical_claim_unit_id":
                        right_id,

                    "source_sentence_id":
                        left.get(
                            "sentence_id"
                        ),

                    "target_sentence_id":
                        right.get(
                            "sentence_id"
                        ),

                    "source_sentence_global_index":
                        left.get(
                            "sentence_global_index"
                        ),

                    "target_sentence_global_index":
                        right.get(
                            "sentence_global_index"
                        ),

                    "section_id":
                        section_id,

                    "detection_evidence": {
                        "basis":
                            detection_basis,

                        "cue_text":
                            cue_text,

                        "cue_signal_type":
                            cue_signal_type,

                        "cue_belongs_to":
                            "TARGET_CLAIM",

                        "target_claim_initial":
                            True,
                    },

                    "adjacency_verified":
                        True,

                    "logical_relation_detected":
                        True,

                    "premise_conclusion_roles_finalized":
                        False,

                    "conditional_structure_finalized":
                        False,

                    "causal_relation_inferred":
                        False,

                    "truth_assessed":
                        False,
                }

                relations.append(
                    relation
                )

                relation_type_counts[
                    relation_type
                ] = (
                    relation_type_counts.get(
                        relation_type,
                        0,
                    )
                    + 1
                )

                updated_units_by_id[
                    left_id
                ][
                    "adjacent_relation_context"
                ][
                    "outgoing_relation_ids"
                ].append(
                    relation_id
                )

                updated_units_by_id[
                    right_id
                ][
                    "adjacent_relation_context"
                ][
                    "incoming_relation_ids"
                ].append(
                    relation_id
                )

            pair_evaluations.append({
                "adjacent_pair_id":
                    pair_id,

                "section_id":
                    section_id,

                "source_logical_claim_unit_id":
                    left_id,

                "target_logical_claim_unit_id":
                    right_id,

                "source_sentence_global_index":
                    left.get(
                        "sentence_global_index"
                    ),

                "target_sentence_global_index":
                    right.get(
                        "sentence_global_index"
                    ),

                "source_text":
                    left.get(
                        "text"
                    ),

                "target_text":
                    right.get(
                        "text"
                    ),

                "left_signal_types":
                    [
                        signal.get(
                            "signal_type"
                        )
                        for signal in left_signals
                    ],

                "right_initial_signal_types":
                    [
                        signal.get(
                            "signal_type"
                        )
                        for signal in initial_right_signals
                    ],

                "relation_detected":
                    detected,

                "logical_relation_id":
                    relation_id,

                "relation_type":
                    relation_type,

                "confidence":
                    confidence,

                "detection_basis":
                    detection_basis,

                "condition_signal_deferred":
                    condition_deferred,

                "condition_mapping_stage":
                    (
                        "4.6.6I"
                        if condition_deferred
                        else None
                    ),

                "left_internal_signal_does_not_bind_next_claim":
                    True,
            })

    ordered_units = []

    for unit in (
        discourse_signal_result.get(
            "logical_claim_units"
        )
        or []
    ):
        unit_id = unit.get(
            "logical_claim_unit_id"
        )

        if unit_id not in updated_units_by_id:
            raise LogicalIntelligenceError(
                "Logical Claim Unit identity was lost "
                "during adjacent relation detection."
            )

        ordered_units.append(
            updated_units_by_id[
                unit_id
            ]
        )

    rebuilt_sections = []

    for section in source_sections:
        section_id = section.get(
            "section_id"
        )

        section_claims = [
            unit
            for unit in ordered_units
            if unit.get(
                "section_id"
            ) == section_id
        ]

        section_relations = [
            relation
            for relation in relations
            if relation.get(
                "section_id"
            ) == section_id
        ]

        rebuilt_sections.append({
            "section_id":
                section_id,

            "section_evidence_unit_id":
                section.get(
                    "section_evidence_unit_id"
                ),

            "section_index":
                section.get(
                    "section_index"
                ),

            "section_title":
                section.get(
                    "section_title"
                ),

            "heading_level":
                section.get(
                    "heading_level"
                ),

            "logical_claim_count":
                len(
                    section_claims
                ),

            "adjacent_relation_count":
                len(
                    section_relations
                ),

            "logical_claim_units":
                section_claims,

            "adjacent_relations":
                section_relations,
        })

    boundaries = dict(
        discourse_signal_result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "logical_signal_interpretation_performed"
    ] = True

    boundaries[
        "logical_relation_detection_performed"
    ] = True

    boundaries[
        "adjacent_relation_detection_performed"
    ] = True

    boundaries[
        "non_adjacent_relation_detection_performed"
    ] = False

    boundaries[
        "premise_conclusion_mapping_performed"
    ] = False

    boundaries[
        "logical_chain_construction_performed"
    ] = False

    boundaries[
        "logical_tension_detection_performed"
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

    return {
        "schema_version":
            "adjacent_logical_relation_result_v1",

        "logical_intelligence_version":
            LOGICAL_INTELLIGENCE_VERSION,

        "phase":
            "4.6.6",

        "patch":
            "4.6.6E",

        "status":
            "ADJACENT_LOGICAL_RELATIONS_DETECTED",

        "workspace_id":
            discourse_signal_result.get(
                "workspace_id"
            ),

        "document_id":
            discourse_signal_result.get(
                "document_id"
            ),

        "source_type":
            discourse_signal_result.get(
                "source_type"
            ),

        "source_id":
            discourse_signal_result.get(
                "source_id"
            ),

        "content_hash":
            discourse_signal_result.get(
                "content_hash"
            ),

        "body_ref":
            discourse_signal_result.get(
                "body_ref"
            ),

        "article_id":
            discourse_signal_result.get(
                "article_id"
            ),

        "title":
            discourse_signal_result.get(
                "title"
            ),

        "canonical_section_order":
            list(
                discourse_signal_result.get(
                    "canonical_section_order"
                )
                or []
            ),

        "section_count":
            len(
                rebuilt_sections
            ),

        "logical_claim_unit_count":
            len(
                ordered_units
            ),

        "adjacent_pair_count":
            total_pair_count,

        "adjacent_relation_count":
            detected_relation_count,

        "logical_sections":
            rebuilt_sections,

        "logical_claim_units":
            ordered_units,

        "adjacent_pair_evaluations":
            pair_evaluations,

        "adjacent_relations":
            relations,

        "adjacent_relation_summary": {
            "total_adjacent_pairs":
                total_pair_count,

            "detected_relation_count":
                detected_relation_count,

            "non_relation_pair_count":
                (
                    total_pair_count
                    - detected_relation_count
                ),

            "deferred_initial_condition_pairs":
                deferred_condition_pair_count,

            "relation_type_counts":
                dict(
                    sorted(
                        relation_type_counts.items()
                    )
                ),

            "left_internal_signals_do_not_bind_next_claim":
                True,

            "bare_initial_condition_not_auto_linked":
                True,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "non_adjacent_same_section_relation_detection",
    }


def detect_non_adjacent_same_section_relations_v1(
    adjacent_relation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Detect high-confidence logical relations between non-adjacent
    claims inside the same canonical section.

    This stage is intentionally conservative.

    It does NOT:
    - connect claims merely because they share vocabulary,
    - connect claims merely because they share a paragraph,
    - construct multi-claim logical chains,
    - finalize conditional semantics,
    - finalize premise/conclusion roles,
    - perform causal reasoning,
    - determine factual truth,
    - select links, targets, URLs, or highlight colors,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        adjacent_relation_result,
        Mapping,
    ):
        raise LogicalIntelligenceError(
            "adjacent_relation_result must be a mapping."
        )

    if (
        adjacent_relation_result.get("schema_version")
        != "adjacent_logical_relation_result_v1"
    ):
        raise LogicalIntelligenceError(
            "Non-adjacent detection requires "
            "adjacent_logical_relation_result_v1."
        )

    if (
        adjacent_relation_result.get("status")
        != "ADJACENT_LOGICAL_RELATIONS_DETECTED"
    ):
        raise LogicalIntelligenceError(
            "Adjacent logical relation detection is incomplete."
        )

    if (
        adjacent_relation_result.get("phase")
        != "4.6.6"
    ):
        raise LogicalIntelligenceError(
            "Non-adjacent detection requires Phase 4.6.6 input."
        )

    source_sections = list(
        adjacent_relation_result.get(
            "logical_sections"
        )
        or []
    )

    source_units = list(
        adjacent_relation_result.get(
            "logical_claim_units"
        )
        or []
    )

    if not source_sections or not source_units:
        raise LogicalIntelligenceError(
            "Canonical Logical Claim Units are missing."
        )

    stop_terms = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "been",
        "but",
        "by",
        "can",
        "do",
        "does",
        "for",
        "from",
        "has",
        "have",
        "her",
        "his",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "may",
        "might",
        "of",
        "on",
        "or",
        "our",
        "she",
        "that",
        "the",
        "their",
        "them",
        "there",
        "these",
        "they",
        "this",
        "those",
        "to",
        "was",
        "were",
        "will",
        "with",
        "your",
        "you",
        "baby",
        "babies",
        "child",
        "children",
    }

    def substantive_terms(
        value: str,
    ) -> set[str]:
        words = re.findall(
            r"[A-Za-z][A-Za-z'-]+",
            value.lower(),
        )

        return {
            word
            for word in words
            if (
                len(word) >= 4
                and word not in stop_terms
            )
        }

    updated_units = {}

    for unit in source_units:
        unit_id = unit.get(
            "logical_claim_unit_id"
        )

        if not unit_id:
            raise LogicalIntelligenceError(
                "Logical Claim Unit has no ID."
            )

        updated = dict(
            unit
        )

        state = dict(
            updated.get(
                "logical_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "adjacent_relation_detection"
            )
            != "COMPLETE"
        ):
            raise LogicalIntelligenceError(
                "Adjacent relation detection must be COMPLETE "
                "before non-adjacent detection."
            )

        if (
            state.get(
                "non_adjacent_relation_detection"
            )
            != "PENDING"
        ):
            raise LogicalIntelligenceError(
                "Non-adjacent relation state was not PENDING."
            )

        state[
            "non_adjacent_relation_detection"
        ] = "COMPLETE"

        updated[
            "logical_analysis_state"
        ] = state

        updated[
            "non_adjacent_relation_context"
        ] = {
            "incoming_relation_ids": [],
            "outgoing_relation_ids": [],
            "detection_complete": True,
        }

        updated_units[
            unit_id
        ] = updated

    evaluations = []
    relations = []

    evaluated_pair_count = 0
    structurally_strong_pair_count = 0
    detected_relation_count = 0

    existing_relation_pairs = {
        (
            relation.get(
                "source_logical_claim_unit_id"
            ),
            relation.get(
                "target_logical_claim_unit_id"
            ),
        )
        for relation in (
            adjacent_relation_result.get(
                "adjacent_relations"
            )
            or []
        )
    }

    for section in source_sections:
        section_units = list(
            section.get(
                "logical_claim_units"
            )
            or []
        )

        for left_index in range(
            len(section_units)
        ):
            for right_index in range(
                left_index + 1,
                len(section_units),
            ):
                left = section_units[
                    left_index
                ]
                right = section_units[
                    right_index
                ]

                source_global = left.get(
                    "sentence_global_index"
                )

                target_global = right.get(
                    "sentence_global_index"
                )

                if not (
                    isinstance(
                        source_global,
                        int,
                    )
                    and isinstance(
                        target_global,
                        int,
                    )
                ):
                    continue

                distance = (
                    target_global
                    - source_global
                )

                if distance <= 1:
                    continue

                evaluated_pair_count += 1

                source_id = left.get(
                    "logical_claim_unit_id"
                )

                target_id = right.get(
                    "logical_claim_unit_id"
                )

                if (
                    source_id,
                    target_id,
                ) in existing_relation_pairs:
                    continue

                same_block = (
                    left.get("block_id")
                    == right.get("block_id")
                )

                same_paragraph = (
                    left.get("paragraph_id")
                    == right.get("paragraph_id")
                )

                short_distance = (
                    2 <= distance <= 4
                )

                structurally_strong = (
                    same_block
                    and same_paragraph
                    and short_distance
                )

                if structurally_strong:
                    structurally_strong_pair_count += 1

                right_signals = list(
                    (
                        right.get(
                            "discourse_signal_analysis"
                        )
                        or {}
                    ).get(
                        "signals",
                        [],
                    )
                )

                initial_conditions = [
                    signal
                    for signal in right_signals
                    if (
                        signal.get("accepted") is True
                        and signal.get("signal_type")
                            == "CONDITION"
                        and isinstance(
                            signal.get("start_char"),
                            int,
                        )
                        and signal.get("start_char") <= 5
                    )
                ]

                left_terms = substantive_terms(
                    str(
                        left.get("text")
                        or ""
                    )
                )

                right_terms = substantive_terms(
                    str(
                        right.get("text")
                        or ""
                    )
                )

                shared_terms = sorted(
                    left_terms.intersection(
                        right_terms
                    )
                )

                strong_shared_content = (
                    len(shared_terms) >= 2
                )

                detected = (
                    structurally_strong
                    and bool(
                        initial_conditions
                    )
                    and strong_shared_content
                )

                pair_material = (
                    str(
                        adjacent_relation_result.get(
                            "article_id"
                        )
                        or ""
                    )
                    + "|"
                    + str(source_id)
                    + "|"
                    + str(target_id)
                )

                pair_id = (
                    "non_adjacent_pair_"
                    + hashlib.sha256(
                        pair_material.encode(
                            "utf-8"
                        )
                    ).hexdigest()[:16]
                )

                relation_id = None

                if detected:
                    detected_relation_count += 1

                    relation_id = (
                        "logical_relation_"
                        + hashlib.sha256(
                            (
                                pair_material
                                + "|"
                                + "CONDITIONAL_APPLICATION"
                            ).encode(
                                "utf-8"
                            )
                        ).hexdigest()[:16]
                    )

                    cue = (
                        initial_conditions[0]
                    )

                    relation = {
                        "logical_relation_id":
                            relation_id,

                        "non_adjacent_pair_id":
                            pair_id,

                        "relation_scope":
                            "NON_ADJACENT_SAME_SECTION",

                        "relation_type":
                            "CONDITIONAL_APPLICATION",

                        "confidence":
                            0.91,

                        "source_logical_claim_unit_id":
                            source_id,

                        "target_logical_claim_unit_id":
                            target_id,

                        "source_sentence_id":
                            left.get(
                                "sentence_id"
                            ),

                        "target_sentence_id":
                            right.get(
                                "sentence_id"
                            ),

                        "source_sentence_global_index":
                            source_global,

                        "target_sentence_global_index":
                            target_global,

                        "sentence_distance":
                            distance,

                        "section_id":
                            section.get(
                                "section_id"
                            ),

                        "shared_substantive_terms":
                            shared_terms,

                        "detection_evidence": {
                            "same_block":
                                True,

                            "same_paragraph":
                                True,

                            "short_distance":
                                True,

                            "target_initial_condition":
                                True,

                            "cue_text":
                                cue.get(
                                    "matched_text"
                                ),

                            "shared_substantive_term_count":
                                len(
                                    shared_terms
                                ),
                        },

                        "logical_relation_detected":
                            True,

                        "conditional_structure_finalized":
                            False,

                        "conditional_mapping_stage":
                            "4.6.6I",

                        "premise_conclusion_roles_finalized":
                            False,

                        "causal_relation_inferred":
                            False,

                        "truth_assessed":
                            False,
                    }

                    relations.append(
                        relation
                    )

                    updated_units[
                        source_id
                    ][
                        "non_adjacent_relation_context"
                    ][
                        "outgoing_relation_ids"
                    ].append(
                        relation_id
                    )

                    updated_units[
                        target_id
                    ][
                        "non_adjacent_relation_context"
                    ][
                        "incoming_relation_ids"
                    ].append(
                        relation_id
                    )

                evaluations.append({
                    "non_adjacent_pair_id":
                        pair_id,

                    "section_id":
                        section.get(
                            "section_id"
                        ),

                    "source_logical_claim_unit_id":
                        source_id,

                    "target_logical_claim_unit_id":
                        target_id,

                    "source_sentence_global_index":
                        source_global,

                    "target_sentence_global_index":
                        target_global,

                    "sentence_distance":
                        distance,

                    "same_block":
                        same_block,

                    "same_paragraph":
                        same_paragraph,

                    "structurally_strong":
                        structurally_strong,

                    "target_initial_condition":
                        bool(
                            initial_conditions
                        ),

                    "shared_substantive_terms":
                        shared_terms,

                    "shared_substantive_term_count":
                        len(
                            shared_terms
                        ),

                    "relation_detected":
                        detected,

                    "logical_relation_id":
                        relation_id,

                    "relation_type":
                        (
                            "CONDITIONAL_APPLICATION"
                            if detected
                            else None
                        ),

                    "conditional_structure_finalized":
                        False,

                    "chain_construction_deferred":
                        True,
                })

    ordered_units = [
        updated_units[
            unit.get(
                "logical_claim_unit_id"
            )
        ]
        for unit in source_units
    ]

    rebuilt_sections = []

    for section in source_sections:
        section_id = section.get(
            "section_id"
        )

        section_claims = [
            unit
            for unit in ordered_units
            if (
                unit.get("section_id")
                == section_id
            )
        ]

        section_non_adjacent_relations = [
            relation
            for relation in relations
            if (
                relation.get("section_id")
                == section_id
            )
        ]

        rebuilt = dict(
            section
        )

        rebuilt[
            "logical_claim_units"
        ] = section_claims

        rebuilt[
            "non_adjacent_relation_count"
        ] = len(
            section_non_adjacent_relations
        )

        rebuilt[
            "non_adjacent_relations"
        ] = section_non_adjacent_relations

        rebuilt_sections.append(
            rebuilt
        )

    boundaries = dict(
        adjacent_relation_result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "logical_relation_detection_performed"
    ] = True

    boundaries[
        "adjacent_relation_detection_performed"
    ] = True

    boundaries[
        "non_adjacent_relation_detection_performed"
    ] = True

    boundaries[
        "premise_conclusion_mapping_performed"
    ] = False

    boundaries[
        "logical_chain_construction_performed"
    ] = False

    boundaries[
        "logical_tension_detection_performed"
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

    return {
        "schema_version":
            "non_adjacent_logical_relation_result_v1",

        "logical_intelligence_version":
            LOGICAL_INTELLIGENCE_VERSION,

        "phase":
            "4.6.6",

        "patch":
            "4.6.6F",

        "status":
            "NON_ADJACENT_LOGICAL_RELATIONS_DETECTED",

        "workspace_id":
            adjacent_relation_result.get(
                "workspace_id"
            ),

        "document_id":
            adjacent_relation_result.get(
                "document_id"
            ),

        "source_type":
            adjacent_relation_result.get(
                "source_type"
            ),

        "source_id":
            adjacent_relation_result.get(
                "source_id"
            ),

        "content_hash":
            adjacent_relation_result.get(
                "content_hash"
            ),

        "body_ref":
            adjacent_relation_result.get(
                "body_ref"
            ),

        "article_id":
            adjacent_relation_result.get(
                "article_id"
            ),

        "title":
            adjacent_relation_result.get(
                "title"
            ),

        "canonical_section_order":
            list(
                adjacent_relation_result.get(
                    "canonical_section_order"
                )
                or []
            ),

        "section_count":
            len(
                rebuilt_sections
            ),

        "logical_claim_unit_count":
            len(
                ordered_units
            ),

        "adjacent_pair_count":
            adjacent_relation_result.get(
                "adjacent_pair_count"
            ),

        "adjacent_relation_count":
            adjacent_relation_result.get(
                "adjacent_relation_count"
            ),

        "adjacent_pair_evaluations":
            list(
                adjacent_relation_result.get(
                    "adjacent_pair_evaluations"
                )
                or []
            ),

        "adjacent_relations":
            list(
                adjacent_relation_result.get(
                    "adjacent_relations"
                )
                or []
            ),

        "non_adjacent_pair_evaluations":
            evaluations,

        "non_adjacent_relation_count":
            detected_relation_count,

        "non_adjacent_relations":
            relations,

        "logical_sections":
            rebuilt_sections,

        "logical_claim_units":
            ordered_units,

        "non_adjacent_relation_summary": {
            "evaluated_non_adjacent_pairs":
                evaluated_pair_count,

            "structurally_strong_pairs":
                structurally_strong_pair_count,

            "detected_relation_count":
                detected_relation_count,

            "accepted_relation_type":
                "CONDITIONAL_APPLICATION",

            "same_block_required":
                True,

            "same_paragraph_required":
                True,

            "maximum_sentence_distance":
                4,

            "target_initial_condition_required":
                True,

            "minimum_shared_substantive_terms":
                2,

            "conditional_semantics_finalized":
                False,

            "logical_chain_construction_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "premise_conclusion_mapping",
    }


__all__ = [
    "LOGICAL_INTELLIGENCE_VERSION",
    "LogicalIntelligenceError",
    "validate_logical_intelligence_intake_v1",
    "build_logical_claim_units_v1",
    "interpret_discourse_signals_v1",
    "detect_adjacent_claim_relations_v1",
    "detect_non_adjacent_same_section_relations_v1",
]
