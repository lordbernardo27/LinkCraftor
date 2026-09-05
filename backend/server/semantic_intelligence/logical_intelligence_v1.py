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
        r"(because)"
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

            initial_reason_signals = [
                signal
                for signal in initial_right_signals
                if (
                    signal.get("signal_type")
                    == "REASON"
                )
            ]

            reason_deferred = bool(
                initial_reason_signals
            )

            deferred_reason_signal_text = (
                initial_reason_signals[0].get(
                    "matched_text"
                )
                if initial_reason_signals
                else None
            )

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

                "reason_signal_deferred":
                    reason_deferred,

                "reason_signal_text":
                    deferred_reason_signal_text,

                "reason_reasoning_stage":
                    (
                        "4.6.8"
                        if reason_deferred
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


def map_premise_conclusion_v1(
    non_adjacent_relation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Map explicit article-local premise/conclusion structures.

    This stage is deliberately conservative.

    It maps only explicit intra-claim structures supported by
    accepted REASON or CONCLUSION discourse signals.

    It does NOT:
    - force premise/conclusion roles onto every logical relation,
    - infer unstated premises,
    - perform causal reasoning,
    - perform truth assessment,
    - perform external authority checking,
    - finalize conditional structures,
    - build logical chains,
    - adjudicate logical tension,
    - select links, targets, URLs, or highlight colors,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        non_adjacent_relation_result,
        Mapping,
    ):
        raise LogicalIntelligenceError(
            "non_adjacent_relation_result must be a mapping."
        )

    if (
        non_adjacent_relation_result.get("schema_version")
        != "non_adjacent_logical_relation_result_v1"
    ):
        raise LogicalIntelligenceError(
            "Premise/conclusion mapping requires "
            "non_adjacent_logical_relation_result_v1."
        )

    if (
        non_adjacent_relation_result.get("status")
        != "NON_ADJACENT_LOGICAL_RELATIONS_DETECTED"
    ):
        raise LogicalIntelligenceError(
            "Non-adjacent relation detection is incomplete."
        )

    if (
        non_adjacent_relation_result.get("phase")
        != "4.6.6"
    ):
        raise LogicalIntelligenceError(
            "Premise/conclusion mapping requires Phase 4.6.6 input."
        )

    source_units = list(
        non_adjacent_relation_result.get(
            "logical_claim_units"
        )
        or []
    )

    if not source_units:
        raise LogicalIntelligenceError(
            "Logical Claim Units are missing."
        )

    mappings = []
    updated_units = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
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
                "non_adjacent_relation_detection"
            )
            != "COMPLETE"
        ):
            raise LogicalIntelligenceError(
                "Non-adjacent relation detection must be COMPLETE "
                "before premise/conclusion mapping."
            )

        if (
            state.get(
                "premise_conclusion_mapping"
            )
            != "PENDING"
        ):
            raise LogicalIntelligenceError(
                "Premise/conclusion mapping state was not PENDING."
            )

        state[
            "premise_conclusion_mapping"
        ] = "COMPLETE"

        updated[
            "logical_analysis_state"
        ] = state

        updated[
            "premise_conclusion_context"
        ] = {
            "mapping_ids": [],
            "mapping_complete": True,
            "explicit_mapping_count": 0,
        }

        text_value = str(
            unit.get("text")
            or ""
        )

        signals = list(
            (
                unit.get(
                    "discourse_signal_analysis"
                )
                or {}
            ).get(
                "signals",
                [],
            )
        )

        selected_signals = [
            signal
            for signal in signals
            if (
                signal.get("accepted") is True
                and signal.get("signal_type")
                in (
                    "REASON",
                    "CONCLUSION",
                )
            )
        ]

        for signal in selected_signals:
            signal_type = signal.get(
                "signal_type"
            )

            start = signal.get(
                "start_char"
            )

            end = signal.get(
                "end_char"
            )

            if not (
                isinstance(start, int)
                and isinstance(end, int)
                and 0 <= start < end <= len(text_value)
            ):
                raise LogicalIntelligenceError(
                    "Invalid discourse-signal character span."
                )

            marker = text_value[
                start:end
            ]

            before = text_value[
                :start
            ].strip(
                " \t\r\n,;:"
            )

            after = text_value[
                end:
            ].strip(
                " \t\r\n,;:"
            )

            premise_text = None
            conclusion_text = None
            mapping_pattern = None

            if signal_type == "REASON":
                if start <= 1:
                    comma_index = after.find(
                        ","
                    )

                    if comma_index <= 0:
                        continue

                    premise_text = after[
                        :comma_index
                    ].strip(
                        " \t\r\n,;:"
                    )

                    conclusion_text = after[
                        comma_index + 1:
                    ].strip(
                        " \t\r\n,;:"
                    )

                    mapping_pattern = (
                        "INITIAL_REASON_CLAUSE_THEN_CONCLUSION"
                    )

                else:
                    if not before or not after:
                        continue

                    conclusion_text = before
                    premise_text = after

                    mapping_pattern = (
                        "CONCLUSION_THEN_REASON_CLAUSE"
                    )

            elif signal_type == "CONCLUSION":
                if not before or not after:
                    continue

                premise_text = before
                conclusion_text = after

                mapping_pattern = (
                    "PREMISE_THEN_CONCLUSION_MARKER"
                )

            if not premise_text or not conclusion_text:
                continue

            mapping_material = (
                str(
                    non_adjacent_relation_result.get(
                        "article_id"
                    )
                    or ""
                )
                + "|"
                + str(unit_id)
                + "|"
                + str(signal_type)
                + "|"
                + str(start)
                + "|"
                + premise_text
                + "|"
                + conclusion_text
            )

            mapping_id = (
                "premise_conclusion_"
                + hashlib.sha256(
                    mapping_material.encode(
                        "utf-8"
                    )
                ).hexdigest()[:16]
            )

            mapping = {
                "premise_conclusion_mapping_id":
                    mapping_id,

                "mapping_scope":
                    "INTRA_CLAIM_EXPLICIT",

                "logical_claim_unit_id":
                    unit_id,

                "section_id":
                    unit.get(
                        "section_id"
                    ),

                "sentence_id":
                    unit.get(
                        "sentence_id"
                    ),

                "sentence_global_index":
                    unit.get(
                        "sentence_global_index"
                    ),

                "discourse_signal_type":
                    signal_type,

                "discourse_marker":
                    marker,

                "mapping_pattern":
                    mapping_pattern,

                "premise": {
                    "text":
                        premise_text,

                    "role":
                        "PREMISE",

                    "explicit":
                        True,
                },

                "conclusion": {
                    "text":
                        conclusion_text,

                    "role":
                        "CONCLUSION",

                    "explicit":
                        True,
                },

                "mapping_confidence":
                    (
                        0.96
                        if signal_type == "CONCLUSION"
                        else 0.95
                    ),

                "premise_conclusion_roles_finalized":
                    True,

                "cross_claim_role_assignment":
                    False,

                "unstated_premise_inferred":
                    False,

                "causal_relation_inferred":
                    False,

                "truth_assessed":
                    False,

                "article_local_only":
                    True,
            }

            mappings.append(
                mapping
            )

            updated[
                "premise_conclusion_context"
            ][
                "mapping_ids"
            ].append(
                mapping_id
            )

            updated[
                "premise_conclusion_context"
            ][
                "explicit_mapping_count"
            ] += 1

        updated_units[
            unit_id
        ] = updated

    ordered_units = [
        updated_units[
            unit.get(
                "logical_claim_unit_id"
            )
        ]
        for unit in source_units
    ]

    mapping_ids = [
        mapping.get(
            "premise_conclusion_mapping_id"
        )
        for mapping in mappings
    ]

    if (
        len(mapping_ids)
        != len(set(mapping_ids))
    ):
        raise LogicalIntelligenceError(
            "Duplicate premise/conclusion mapping IDs detected."
        )

    rebuilt_sections = []

    for section in (
        non_adjacent_relation_result.get(
            "logical_sections"
        )
        or []
    ):
        section_id = section.get(
            "section_id"
        )

        section_claims = [
            unit
            for unit in ordered_units
            if (
                unit.get(
                    "section_id"
                )
                == section_id
            )
        ]

        section_mappings = [
            mapping
            for mapping in mappings
            if (
                mapping.get(
                    "section_id"
                )
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
            "premise_conclusion_mapping_count"
        ] = len(
            section_mappings
        )

        rebuilt[
            "premise_conclusion_mappings"
        ] = section_mappings

        rebuilt_sections.append(
            rebuilt
        )

    adjacent_relations = []

    for relation in (
        non_adjacent_relation_result.get(
            "adjacent_relations"
        )
        or []
    ):
        copied = dict(
            relation
        )

        copied[
            "premise_conclusion_roles_finalized"
        ] = False

        adjacent_relations.append(
            copied
        )

    non_adjacent_relations = []

    for relation in (
        non_adjacent_relation_result.get(
            "non_adjacent_relations"
        )
        or []
    ):
        copied = dict(
            relation
        )

        copied[
            "premise_conclusion_roles_finalized"
        ] = False

        non_adjacent_relations.append(
            copied
        )

    boundaries = dict(
        non_adjacent_relation_result.get(
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
    ] = True

    boundaries[
        "qualification_exception_mapping_performed"
    ] = False

    boundaries[
        "conditional_mapping_performed"
    ] = False

    boundaries[
        "support_clarification_contrast_mapping_performed"
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
            "premise_conclusion_mapping_result_v1",

        "logical_intelligence_version":
            LOGICAL_INTELLIGENCE_VERSION,

        "phase":
            "4.6.6",

        "patch":
            "4.6.6G",

        "status":
            "PREMISE_CONCLUSION_MAPPING_COMPLETE",

        "workspace_id":
            non_adjacent_relation_result.get(
                "workspace_id"
            ),

        "document_id":
            non_adjacent_relation_result.get(
                "document_id"
            ),

        "source_type":
            non_adjacent_relation_result.get(
                "source_type"
            ),

        "source_id":
            non_adjacent_relation_result.get(
                "source_id"
            ),

        "content_hash":
            non_adjacent_relation_result.get(
                "content_hash"
            ),

        "body_ref":
            non_adjacent_relation_result.get(
                "body_ref"
            ),

        "article_id":
            non_adjacent_relation_result.get(
                "article_id"
            ),

        "title":
            non_adjacent_relation_result.get(
                "title"
            ),

        "canonical_section_order":
            list(
                non_adjacent_relation_result.get(
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
            non_adjacent_relation_result.get(
                "adjacent_pair_count"
            ),

        "adjacent_relation_count":
            non_adjacent_relation_result.get(
                "adjacent_relation_count"
            ),

        "adjacent_pair_evaluations":
            list(
                non_adjacent_relation_result.get(
                    "adjacent_pair_evaluations"
                )
                or []
            ),

        "adjacent_relations":
            adjacent_relations,

        "non_adjacent_pair_evaluations":
            list(
                non_adjacent_relation_result.get(
                    "non_adjacent_pair_evaluations"
                )
                or []
            ),

        "non_adjacent_relation_count":
            non_adjacent_relation_result.get(
                "non_adjacent_relation_count"
            ),

        "non_adjacent_relations":
            non_adjacent_relations,

        "premise_conclusion_mapping_count":
            len(
                mappings
            ),

        "premise_conclusion_mappings":
            mappings,

        "logical_sections":
            rebuilt_sections,

        "logical_claim_units":
            ordered_units,

        "premise_conclusion_summary": {
            "explicit_mapping_count":
                len(
                    mappings
                ),

            "intra_claim_mapping_only":
                True,

            "cross_claim_role_assignment_performed":
                False,

            "unstated_premise_inference_performed":
                False,

            "causal_reasoning_performed":
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
            "qualification_exception_mapping",
    }


def map_qualification_exception_v1(
    premise_conclusion_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Map explicit article-local qualification and exception structures.

    Qualification mapping is scope-aware and conservative.

    It does NOT:
    - treat every lexical occurrence of often/usually/etc. as a
      logical qualification,
    - infer unstated qualifications or exceptions,
    - perform conditional mapping,
    - perform causal reasoning,
    - assess factual truth,
    - perform external authority checking,
    - build logical chains,
    - adjudicate logical tension,
    - select links, targets, URLs, or highlight colors,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        premise_conclusion_result,
        Mapping,
    ):
        raise LogicalIntelligenceError(
            "premise_conclusion_result must be a mapping."
        )

    if (
        premise_conclusion_result.get("schema_version")
        != "premise_conclusion_mapping_result_v1"
    ):
        raise LogicalIntelligenceError(
            "Qualification/exception mapping requires "
            "premise_conclusion_mapping_result_v1."
        )

    if (
        premise_conclusion_result.get("status")
        != "PREMISE_CONCLUSION_MAPPING_COMPLETE"
    ):
        raise LogicalIntelligenceError(
            "Premise/conclusion mapping is incomplete."
        )

    if (
        premise_conclusion_result.get("phase")
        != "4.6.6"
    ):
        raise LogicalIntelligenceError(
            "Qualification/exception mapping requires Phase 4.6.6 input."
        )

    source_units = list(
        premise_conclusion_result.get(
            "logical_claim_units"
        )
        or []
    )

    if not source_units:
        raise LogicalIntelligenceError(
            "Logical Claim Units are missing."
        )

    qualification_mappings = []
    exception_mappings = []
    rejected_signal_records = []
    updated_units = {}

    qualification_kind_map = {
        "may": "EPISTEMIC_POSSIBILITY",
        "might": "EPISTEMIC_POSSIBILITY",
        "probably": "EPISTEMIC_PROBABILITY",
        "likely": "EPISTEMIC_LIKELIHOOD",
        "usually": "FREQUENCY_TYPICALITY",
        "sometimes": "FREQUENCY_OCCASIONALITY",
        "often": "FREQUENCY_COMMONALITY",
        "generally": "GENERALITY_QUALIFIER",
        "typically": "TYPICALITY_QUALIFIER",
    }

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
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
                "premise_conclusion_mapping"
            )
            != "COMPLETE"
        ):
            raise LogicalIntelligenceError(
                "Premise/conclusion mapping must be COMPLETE "
                "before qualification/exception mapping."
            )

        if (
            state.get(
                "qualification_exception_mapping"
            )
            != "PENDING"
        ):
            raise LogicalIntelligenceError(
                "Qualification/exception mapping state was not PENDING."
            )

        state[
            "qualification_exception_mapping"
        ] = "COMPLETE"

        updated[
            "logical_analysis_state"
        ] = state

        updated[
            "qualification_exception_context"
        ] = {
            "qualification_mapping_ids": [],
            "exception_mapping_ids": [],
            "rejected_signal_count": 0,
            "mapping_complete": True,
        }

        text_value = str(
            unit.get("text")
            or ""
        )

        signals = list(
            (
                unit.get(
                    "discourse_signal_analysis"
                )
                or {}
            ).get(
                "signals",
                [],
            )
        )

        selected = [
            signal
            for signal in signals
            if (
                signal.get("accepted") is True
                and signal.get("signal_type")
                in (
                    "QUALIFICATION",
                    "EXCEPTION",
                )
            )
        ]

        for signal in selected:
            signal_type = signal.get(
                "signal_type"
            )

            start = signal.get(
                "start_char"
            )

            end = signal.get(
                "end_char"
            )

            if not (
                isinstance(start, int)
                and isinstance(end, int)
                and 0 <= start < end <= len(text_value)
            ):
                raise LogicalIntelligenceError(
                    "Invalid qualification/exception signal span."
                )

            marker = text_value[
                start:end
            ]

            marker_lower = marker.lower()

            before = text_value[
                :start
            ]

            after = text_value[
                end:
            ]

            local_left = before[
                max(0, len(before) - 12):
            ].lower()

            # "how often" is a frequency quantity/question phrase,
            # not a proposition-level logical qualification.
            how_often = (
                marker_lower == "often"
                and re.search(
                    r"\bhow\s*$",
                    local_left,
                )
                is not None
            )

            # "too often" is a degree/frequency expression rather
            # than a logical hedge on the proposition.
            too_often = (
                marker_lower == "often"
                and re.search(
                    r"\btoo\s*$",
                    local_left,
                )
                is not None
            )

            # "as often" is comparative event frequency, not
            # proposition-level qualification.
            as_often = (
                marker_lower == "often"
                and re.search(
                    r"\bas\s*$",
                    local_left,
                )
                is not None
            )

            # "probably heard..." qualifies assumed reader familiarity,
            # not the substantive proposition being asserted.
            probably_heard = (
                marker_lower == "probably"
                and re.match(
                    r"\s*heard\b",
                    after,
                    flags=re.IGNORECASE,
                )
                is not None
            )

            if (
                how_often
                or too_often
                or as_often
                or probably_heard
            ):
                if how_often:
                    rejection_reason = (
                        "HOW_OFTEN_FREQUENCY_QUANTITY"
                    )
                elif too_often:
                    rejection_reason = (
                        "TOO_OFTEN_DEGREE_EXPRESSION"
                    )
                elif as_often:
                    rejection_reason = (
                        "AS_OFTEN_COMPARATIVE_FREQUENCY"
                    )
                else:
                    rejection_reason = (
                        "PROBABLY_HEARD_READER_FAMILIARITY"
                    )

                rejected_signal_records.append({
                    "logical_claim_unit_id":
                        unit_id,

                    "sentence_global_index":
                        unit.get(
                            "sentence_global_index"
                        ),

                    "signal_type":
                        signal_type,

                    "marker":
                        marker,

                    "start_char":
                        start,

                    "rejection_reason":
                        rejection_reason,

                    "logical_qualification_created":
                        False,
                })

                updated[
                    "qualification_exception_context"
                ][
                    "rejected_signal_count"
                ] += 1

                continue

            if signal_type == "QUALIFICATION":
                qualification_kind = (
                    qualification_kind_map.get(
                        marker_lower,
                        "QUALIFICATION",
                    )
                )

                qualified_scope = None
                scope_strategy = None

                if marker_lower in {
                    "may",
                    "might",
                    "probably",
                    "likely",
                    "usually",
                }:
                    qualified_scope = (
                        before.strip(
                            " \t\r\n,;:"
                        )
                        + " "
                        + marker
                        + " "
                        + after.strip()
                    ).strip()

                    scope_strategy = (
                        "CLAUSE_WITH_EXPLICIT_QUALIFIER"
                    )

                elif marker_lower in {
                    "sometimes",
                    "often",
                    "generally",
                    "typically",
                }:
                    qualified_scope = (
                        text_value.strip()
                    )

                    scope_strategy = (
                        "PROPOSITION_LEVEL_FREQUENCY_OR_TYPICALITY"
                    )

                if not qualified_scope:
                    continue

                mapping_material = (
                    str(
                        premise_conclusion_result.get(
                            "article_id"
                        )
                        or ""
                    )
                    + "|"
                    + str(unit_id)
                    + "|QUALIFICATION|"
                    + str(start)
                    + "|"
                    + marker_lower
                    + "|"
                    + qualified_scope
                )

                mapping_id = (
                    "qualification_"
                    + hashlib.sha256(
                        mapping_material.encode(
                            "utf-8"
                        )
                    ).hexdigest()[:16]
                )

                qualification = {
                    "qualification_mapping_id":
                        mapping_id,

                    "mapping_scope":
                        "INTRA_CLAIM_EXPLICIT",

                    "logical_claim_unit_id":
                        unit_id,

                    "section_id":
                        unit.get(
                            "section_id"
                        ),

                    "sentence_id":
                        unit.get(
                            "sentence_id"
                        ),

                    "sentence_global_index":
                        unit.get(
                            "sentence_global_index"
                        ),

                    "discourse_marker":
                        marker,

                    "qualification_kind":
                        qualification_kind,

                    "scope_strategy":
                        scope_strategy,

                    "qualified_scope":
                        qualified_scope,

                    "signal_start_char":
                        start,

                    "explicit":
                        True,

                    "qualification_finalized":
                        True,

                    "exception_mapping":
                        False,

                    "conditional_structure_finalized":
                        False,

                    "causal_relation_inferred":
                        False,

                    "truth_assessed":
                        False,

                    "article_local_only":
                        True,
                }

                qualification_mappings.append(
                    qualification
                )

                updated[
                    "qualification_exception_context"
                ][
                    "qualification_mapping_ids"
                ].append(
                    mapping_id
                )

            elif signal_type == "EXCEPTION":
                exception_scope = text_value.strip()

                if not exception_scope:
                    continue

                mapping_material = (
                    str(
                        premise_conclusion_result.get(
                            "article_id"
                        )
                        or ""
                    )
                    + "|"
                    + str(unit_id)
                    + "|EXCEPTION|"
                    + str(start)
                    + "|"
                    + marker_lower
                )

                mapping_id = (
                    "exception_"
                    + hashlib.sha256(
                        mapping_material.encode(
                            "utf-8"
                        )
                    ).hexdigest()[:16]
                )

                exception = {
                    "exception_mapping_id":
                        mapping_id,

                    "mapping_scope":
                        "INTRA_CLAIM_EXPLICIT",

                    "logical_claim_unit_id":
                        unit_id,

                    "section_id":
                        unit.get(
                            "section_id"
                        ),

                    "sentence_id":
                        unit.get(
                            "sentence_id"
                        ),

                    "sentence_global_index":
                        unit.get(
                            "sentence_global_index"
                        ),

                    "discourse_marker":
                        marker,

                    "exception_scope":
                        exception_scope,

                    "explicit":
                        True,

                    "exception_finalized":
                        True,

                    "qualification_mapping":
                        False,

                    "conditional_structure_finalized":
                        False,

                    "causal_relation_inferred":
                        False,

                    "truth_assessed":
                        False,

                    "article_local_only":
                        True,
                }

                exception_mappings.append(
                    exception
                )

                updated[
                    "qualification_exception_context"
                ][
                    "exception_mapping_ids"
                ].append(
                    mapping_id
                )

        updated_units[
            unit_id
        ] = updated

    ordered_units = [
        updated_units[
            unit.get(
                "logical_claim_unit_id"
            )
        ]
        for unit in source_units
    ]

    all_mapping_ids = (
        [
            item.get(
                "qualification_mapping_id"
            )
            for item in qualification_mappings
        ]
        + [
            item.get(
                "exception_mapping_id"
            )
            for item in exception_mappings
        ]
    )

    if (
        len(all_mapping_ids)
        != len(set(all_mapping_ids))
    ):
        raise LogicalIntelligenceError(
            "Duplicate qualification/exception mapping IDs detected."
        )

    rebuilt_sections = []

    for section in (
        premise_conclusion_result.get(
            "logical_sections"
        )
        or []
    ):
        section_id = section.get(
            "section_id"
        )

        section_claims = [
            unit
            for unit in ordered_units
            if (
                unit.get(
                    "section_id"
                )
                == section_id
            )
        ]

        section_qualifications = [
            item
            for item in qualification_mappings
            if (
                item.get(
                    "section_id"
                )
                == section_id
            )
        ]

        section_exceptions = [
            item
            for item in exception_mappings
            if (
                item.get(
                    "section_id"
                )
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
            "qualification_mapping_count"
        ] = len(
            section_qualifications
        )

        rebuilt[
            "qualification_mappings"
        ] = section_qualifications

        rebuilt[
            "exception_mapping_count"
        ] = len(
            section_exceptions
        )

        rebuilt[
            "exception_mappings"
        ] = section_exceptions

        rebuilt_sections.append(
            rebuilt
        )

    boundaries = dict(
        premise_conclusion_result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "premise_conclusion_mapping_performed"
    ] = True

    boundaries[
        "qualification_exception_mapping_performed"
    ] = True

    boundaries[
        "conditional_mapping_performed"
    ] = False

    boundaries[
        "support_clarification_contrast_mapping_performed"
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
            "qualification_exception_mapping_result_v1",

        "logical_intelligence_version":
            LOGICAL_INTELLIGENCE_VERSION,

        "phase":
            "4.6.6",

        "patch":
            "4.6.6H",

        "status":
            "QUALIFICATION_EXCEPTION_MAPPING_COMPLETE",

        "workspace_id":
            premise_conclusion_result.get(
                "workspace_id"
            ),

        "document_id":
            premise_conclusion_result.get(
                "document_id"
            ),

        "source_type":
            premise_conclusion_result.get(
                "source_type"
            ),

        "source_id":
            premise_conclusion_result.get(
                "source_id"
            ),

        "content_hash":
            premise_conclusion_result.get(
                "content_hash"
            ),

        "body_ref":
            premise_conclusion_result.get(
                "body_ref"
            ),

        "article_id":
            premise_conclusion_result.get(
                "article_id"
            ),

        "title":
            premise_conclusion_result.get(
                "title"
            ),

        "canonical_section_order":
            list(
                premise_conclusion_result.get(
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
            premise_conclusion_result.get(
                "adjacent_pair_count"
            ),

        "adjacent_relation_count":
            premise_conclusion_result.get(
                "adjacent_relation_count"
            ),

        "adjacent_pair_evaluations":
            list(
                premise_conclusion_result.get(
                    "adjacent_pair_evaluations"
                )
                or []
            ),

        "adjacent_relations":
            list(
                premise_conclusion_result.get(
                    "adjacent_relations"
                )
                or []
            ),

        "non_adjacent_pair_evaluations":
            list(
                premise_conclusion_result.get(
                    "non_adjacent_pair_evaluations"
                )
                or []
            ),

        "non_adjacent_relation_count":
            premise_conclusion_result.get(
                "non_adjacent_relation_count"
            ),

        "non_adjacent_relations":
            list(
                premise_conclusion_result.get(
                    "non_adjacent_relations"
                )
                or []
            ),

        "premise_conclusion_mapping_count":
            premise_conclusion_result.get(
                "premise_conclusion_mapping_count"
            ),

        "premise_conclusion_mappings":
            list(
                premise_conclusion_result.get(
                    "premise_conclusion_mappings"
                )
                or []
            ),

        "qualification_mapping_count":
            len(
                qualification_mappings
            ),

        "qualification_mappings":
            qualification_mappings,

        "exception_mapping_count":
            len(
                exception_mappings
            ),

        "exception_mappings":
            exception_mappings,

        "rejected_qualification_exception_signal_count":
            len(
                rejected_signal_records
            ),

        "rejected_qualification_exception_signals":
            rejected_signal_records,

        "logical_sections":
            rebuilt_sections,

        "logical_claim_units":
            ordered_units,

        "qualification_exception_summary": {
            "qualification_mapping_count":
                len(
                    qualification_mappings
                ),

            "exception_mapping_count":
                len(
                    exception_mappings
                ),

            "rejected_signal_count":
                len(
                    rejected_signal_records
                ),

            "contextual_false_positive_filtering":
                True,

            "how_often_rejected":
                any(
                    item.get(
                        "rejection_reason"
                    )
                    == "HOW_OFTEN_FREQUENCY_QUANTITY"
                    for item in rejected_signal_records
                ),

            "too_often_rejected":
                any(
                    item.get(
                        "rejection_reason"
                    )
                    == "TOO_OFTEN_DEGREE_EXPRESSION"
                    for item in rejected_signal_records
                ),

            "as_often_rejected":
                any(
                    item.get(
                        "rejection_reason"
                    )
                    == "AS_OFTEN_COMPARATIVE_FREQUENCY"
                    for item in rejected_signal_records
                ),

            "probably_heard_rejected":
                any(
                    item.get(
                        "rejection_reason"
                    )
                    == "PROBABLY_HEARD_READER_FAMILIARITY"
                    for item in rejected_signal_records
                ),

            "article_local_only":
                True,

            "causal_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "conditional_logical_mapping",
    }


def map_conditional_logic_v1(
    qualification_exception_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Map explicit article-local logical condition/consequent structures.

    This stage distinguishes genuine logical conditions from
    embedded whether-like complements such as:
    - determine if X
    - let you know if X

    It does NOT:
    - infer causation,
    - assess factual truth,
    - infer unstated conditions,
    - perform support/clarification/contrast mapping,
    - build logical chains,
    - adjudicate logical tension,
    - perform external authority checking,
    - select links, targets, URLs, or highlight colors,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        qualification_exception_result,
        Mapping,
    ):
        raise LogicalIntelligenceError(
            "qualification_exception_result must be a mapping."
        )

    if (
        qualification_exception_result.get("schema_version")
        != "qualification_exception_mapping_result_v1"
    ):
        raise LogicalIntelligenceError(
            "Conditional mapping requires "
            "qualification_exception_mapping_result_v1."
        )

    if (
        qualification_exception_result.get("status")
        != "QUALIFICATION_EXCEPTION_MAPPING_COMPLETE"
    ):
        raise LogicalIntelligenceError(
            "Qualification/exception mapping is incomplete."
        )

    if (
        qualification_exception_result.get("phase")
        != "4.6.6"
    ):
        raise LogicalIntelligenceError(
            "Conditional mapping requires Phase 4.6.6 input."
        )

    source_units = list(
        qualification_exception_result.get(
            "logical_claim_units"
        )
        or []
    )

    if not source_units:
        raise LogicalIntelligenceError(
            "Logical Claim Units are missing."
        )

    conditional_mappings = []
    rejected_condition_signals = []
    updated_units = {}

    def clean_clause(value: str) -> str:
        return value.strip(
            " \t\r\n,;:"
        )

    def first_clause_boundary(value: str):
        comma = value.find(",")
        colon = value.find(":")

        indexes = [
            index
            for index in (
                comma,
                colon,
            )
            if index >= 0
        ]

        if not indexes:
            return None

        return min(indexes)

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
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
                "qualification_exception_mapping"
            )
            != "COMPLETE"
        ):
            raise LogicalIntelligenceError(
                "Qualification/exception mapping must be COMPLETE "
                "before conditional mapping."
            )

        if (
            state.get(
                "conditional_mapping"
            )
            != "PENDING"
        ):
            raise LogicalIntelligenceError(
                "Conditional mapping state was not PENDING."
            )

        state[
            "conditional_mapping"
        ] = "COMPLETE"

        updated[
            "logical_analysis_state"
        ] = state

        updated[
            "conditional_mapping_context"
        ] = {
            "conditional_mapping_ids": [],
            "rejected_condition_signal_count": 0,
            "mapping_complete": True,
        }

        text_value = str(
            unit.get("text")
            or ""
        )

        signals = list(
            (
                unit.get(
                    "discourse_signal_analysis"
                )
                or {}
            ).get(
                "signals",
                [],
            )
        )

        conditions = [
            signal
            for signal in signals
            if (
                signal.get("accepted") is True
                and signal.get("signal_type")
                    == "CONDITION"
            )
        ]

        for signal in conditions:
            start = signal.get(
                "start_char"
            )

            end = signal.get(
                "end_char"
            )

            if not (
                isinstance(start, int)
                and isinstance(end, int)
                and 0 <= start < end <= len(text_value)
            ):
                raise LogicalIntelligenceError(
                    "Invalid CONDITION signal span."
                )

            marker = text_value[
                start:end
            ]

            marker_lower = marker.lower()

            before = text_value[
                :start
            ]

            after = text_value[
                end:
            ]

            before_clean = clean_clause(
                before
            )

            after_clean = clean_clause(
                after
            )

            local_left = before[
                max(
                    0,
                    len(before) - 45,
                ):
            ].lower()

            embedded_question_complement = (
                marker_lower == "if"
                and (
                    re.search(
                        r"\bdetermine\s*$",
                        local_left,
                    )
                    is not None
                    or re.search(
                        r"\blet\s+you\s+know\s*$",
                        local_left,
                    )
                    is not None
                )
            )

            if embedded_question_complement:
                rejection_reason = (
                    "EMBEDDED_WHETHER_COMPLEMENT"
                )

                rejected_condition_signals.append({
                    "logical_claim_unit_id":
                        unit_id,

                    "sentence_global_index":
                        unit.get(
                            "sentence_global_index"
                        ),

                    "marker":
                        marker,

                    "start_char":
                        start,

                    "rejection_reason":
                        rejection_reason,

                    "conditional_mapping_created":
                        False,
                })

                updated[
                    "conditional_mapping_context"
                ][
                    "rejected_condition_signal_count"
                ] += 1

                continue

            condition_text = None
            consequent_text = None
            mapping_pattern = None

            boundary = first_clause_boundary(
                after
            )

            if start <= 5:
                if boundary is None:
                    continue

                condition_text = clean_clause(
                    after[
                        :boundary
                    ]
                )

                consequent_text = clean_clause(
                    after[
                        boundary + 1:
                    ]
                )

                mapping_pattern = (
                    "INITIAL_CONDITION_THEN_CONSEQUENT"
                )

            else:
                left_context = before_clean.lower()

                # A postposed condition may end at an em dash,
                # after which the sentence continues with separate
                # explanatory material. Example:
                # "Don't be concerned if X [em dash] explanation..."
                em_dash_index = after.find("\u2014")

                if (
                    em_dash_index >= 0
                    and before_clean
                ):
                    condition_text = clean_clause(
                        after[
                            :em_dash_index
                        ]
                    )

                    consequent_text = before_clean

                    mapping_pattern = (
                        "CONSEQUENT_THEN_POSTPOSED_CONDITION"
                    )

                elif boundary is not None:
                    condition_text = clean_clause(
                        after[
                            :boundary
                        ]
                    )

                    trailing = clean_clause(
                        after[
                            boundary + 1:
                        ]
                    )

                    if (
                        left_context.endswith("but")
                        or left_context.endswith("so")
                        or left_context.endswith("and")
                        or left_context.endswith("or")
                        or left_context.endswith("meaning")
                        or left_context.endswith("example")
                        or left_context.endswith("for example")
                    ):
                        consequent_text = trailing

                        mapping_pattern = (
                            "EMBEDDED_CONDITION_THEN_CONSEQUENT"
                        )

                    elif trailing:
                        consequent_text = trailing

                        mapping_pattern = (
                            "EMBEDDED_CONDITION_THEN_CONSEQUENT"
                        )

                    else:
                        consequent_text = before_clean

                        mapping_pattern = (
                            "CONSEQUENT_THEN_POSTPOSED_CONDITION"
                        )

                else:
                    condition_text = after_clean

                    # Parenthetical/nested postposed conditions
                    # attach only to the nearest local action, not
                    # automatically to the entire preceding sentence.
                    #
                    # Example:
                    # "...not letting her use your breast as a pacifier
                    # if you're nursing"
                    nearest_action_match = re.search(
                        r"(not\s+letting\b.+)$",
                        before_clean,
                        flags=re.IGNORECASE,
                    )

                    if nearest_action_match is not None:
                        consequent_text = clean_clause(
                            nearest_action_match.group(1)
                        )

                        mapping_pattern = (
                            "LOCAL_ACTION_THEN_POSTPOSED_CONDITION"
                        )

                    else:
                        consequent_text = before_clean

                        mapping_pattern = (
                            "CONSEQUENT_THEN_POSTPOSED_CONDITION"
                        )

            if (
                not condition_text
                or not consequent_text
            ):
                continue

            mapping_material = (
                str(
                    qualification_exception_result.get(
                        "article_id"
                    )
                    or ""
                )
                + "|"
                + str(unit_id)
                + "|CONDITION|"
                + str(start)
                + "|"
                + condition_text
                + "|"
                + consequent_text
            )

            mapping_id = (
                "conditional_"
                + hashlib.sha256(
                    mapping_material.encode(
                        "utf-8"
                    )
                ).hexdigest()[:16]
            )

            mapping = {
                "conditional_mapping_id":
                    mapping_id,

                "mapping_scope":
                    "INTRA_CLAIM_EXPLICIT",

                "logical_claim_unit_id":
                    unit_id,

                "section_id":
                    unit.get(
                        "section_id"
                    ),

                "sentence_id":
                    unit.get(
                        "sentence_id"
                    ),

                "sentence_global_index":
                    unit.get(
                        "sentence_global_index"
                    ),

                "discourse_marker":
                    marker,

                "mapping_pattern":
                    mapping_pattern,

                "condition": {
                    "text":
                        condition_text,

                    "role":
                        "CONDITION",

                    "explicit":
                        True,
                },

                "consequent": {
                    "text":
                        consequent_text,

                    "role":
                        "CONSEQUENT",

                    "explicit":
                        True,
                },

                "conditional_structure_finalized":
                    True,

                "causal_relation_inferred":
                    False,

                "truth_assessed":
                    False,

                "article_local_only":
                    True,
            }

            conditional_mappings.append(
                mapping
            )

            updated[
                "conditional_mapping_context"
            ][
                "conditional_mapping_ids"
            ].append(
                mapping_id
            )

        updated_units[
            unit_id
        ] = updated

    ordered_units = [
        updated_units[
            unit.get(
                "logical_claim_unit_id"
            )
        ]
        for unit in source_units
    ]

    mapping_ids = [
        item.get(
            "conditional_mapping_id"
        )
        for item in conditional_mappings
    ]

    if (
        len(mapping_ids)
        != len(set(mapping_ids))
    ):
        raise LogicalIntelligenceError(
            "Duplicate conditional mapping IDs detected."
        )

    rebuilt_sections = []

    for section in (
        qualification_exception_result.get(
            "logical_sections"
        )
        or []
    ):
        section_id = section.get(
            "section_id"
        )

        section_claims = [
            unit
            for unit in ordered_units
            if (
                unit.get(
                    "section_id"
                )
                == section_id
            )
        ]

        section_conditionals = [
            item
            for item in conditional_mappings
            if (
                item.get(
                    "section_id"
                )
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
            "conditional_mapping_count"
        ] = len(
            section_conditionals
        )

        rebuilt[
            "conditional_mappings"
        ] = section_conditionals

        rebuilt_sections.append(
            rebuilt
        )

    updated_adjacent_evaluations = []

    for evaluation in (
        qualification_exception_result.get(
            "adjacent_pair_evaluations"
        )
        or []
    ):
        copied = dict(
            evaluation
        )

        if copied.get(
            "condition_signal_deferred"
        ) is True:
            target_index = copied.get(
                "target_sentence_global_index"
            )

            target_has_mapping = any(
                item.get(
                    "sentence_global_index"
                )
                == target_index
                for item in conditional_mappings
            )

            copied[
                "condition_mapping_completed"
            ] = target_has_mapping

            copied[
                "condition_mapping_stage"
            ] = (
                "4.6.6I"
                if target_has_mapping
                else copied.get(
                    "condition_mapping_stage"
                )
            )

        updated_adjacent_evaluations.append(
            copied
        )

    updated_non_adjacent_relations = []

    finalized_cross_claim_count = 0

    for relation in (
        qualification_exception_result.get(
            "non_adjacent_relations"
        )
        or []
    ):
        copied = dict(
            relation
        )

        if (
            copied.get("relation_type")
            == "CONDITIONAL_APPLICATION"
        ):
            target_index = copied.get(
                "target_sentence_global_index"
            )

            target_mapping = next(
                (
                    item
                    for item in conditional_mappings
                    if (
                        item.get(
                            "sentence_global_index"
                        )
                        == target_index
                    )
                ),
                None,
            )

            if target_mapping is not None:
                copied[
                    "conditional_structure_finalized"
                ] = True

                copied[
                    "conditional_mapping_id"
                ] = target_mapping.get(
                    "conditional_mapping_id"
                )

                copied[
                    "conditional_mapping_stage"
                ] = "4.6.6I"

                copied[
                    "causal_relation_inferred"
                ] = False

                finalized_cross_claim_count += 1

        updated_non_adjacent_relations.append(
            copied
        )

    boundaries = dict(
        qualification_exception_result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "conditional_mapping_performed"
    ] = True

    boundaries[
        "support_clarification_contrast_mapping_performed"
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
            "conditional_logical_mapping_result_v1",

        "logical_intelligence_version":
            LOGICAL_INTELLIGENCE_VERSION,

        "phase":
            "4.6.6",

        "patch":
            "4.6.6I",

        "status":
            "CONDITIONAL_LOGICAL_MAPPING_COMPLETE",

        "workspace_id":
            qualification_exception_result.get(
                "workspace_id"
            ),

        "document_id":
            qualification_exception_result.get(
                "document_id"
            ),

        "source_type":
            qualification_exception_result.get(
                "source_type"
            ),

        "source_id":
            qualification_exception_result.get(
                "source_id"
            ),

        "content_hash":
            qualification_exception_result.get(
                "content_hash"
            ),

        "body_ref":
            qualification_exception_result.get(
                "body_ref"
            ),

        "article_id":
            qualification_exception_result.get(
                "article_id"
            ),

        "title":
            qualification_exception_result.get(
                "title"
            ),

        "canonical_section_order":
            list(
                qualification_exception_result.get(
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
            qualification_exception_result.get(
                "adjacent_pair_count"
            ),

        "adjacent_relation_count":
            qualification_exception_result.get(
                "adjacent_relation_count"
            ),

        "adjacent_pair_evaluations":
            updated_adjacent_evaluations,

        "adjacent_relations":
            list(
                qualification_exception_result.get(
                    "adjacent_relations"
                )
                or []
            ),

        "non_adjacent_pair_evaluations":
            list(
                qualification_exception_result.get(
                    "non_adjacent_pair_evaluations"
                )
                or []
            ),

        "non_adjacent_relation_count":
            qualification_exception_result.get(
                "non_adjacent_relation_count"
            ),

        "non_adjacent_relations":
            updated_non_adjacent_relations,

        "premise_conclusion_mapping_count":
            qualification_exception_result.get(
                "premise_conclusion_mapping_count"
            ),

        "premise_conclusion_mappings":
            list(
                qualification_exception_result.get(
                    "premise_conclusion_mappings"
                )
                or []
            ),

        "qualification_mapping_count":
            qualification_exception_result.get(
                "qualification_mapping_count"
            ),

        "qualification_mappings":
            list(
                qualification_exception_result.get(
                    "qualification_mappings"
                )
                or []
            ),

        "exception_mapping_count":
            qualification_exception_result.get(
                "exception_mapping_count"
            ),

        "exception_mappings":
            list(
                qualification_exception_result.get(
                    "exception_mappings"
                )
                or []
            ),

        "rejected_qualification_exception_signal_count":
            qualification_exception_result.get(
                "rejected_qualification_exception_signal_count"
            ),

        "rejected_qualification_exception_signals":
            list(
                qualification_exception_result.get(
                    "rejected_qualification_exception_signals"
                )
                or []
            ),

        "conditional_mapping_count":
            len(
                conditional_mappings
            ),

        "conditional_mappings":
            conditional_mappings,

        "rejected_condition_signal_count":
            len(
                rejected_condition_signals
            ),

        "rejected_condition_signals":
            rejected_condition_signals,

        "cross_claim_conditional_application_finalized_count":
            finalized_cross_claim_count,

        "logical_sections":
            rebuilt_sections,

        "logical_claim_units":
            ordered_units,

        "conditional_mapping_summary": {
            "conditional_mapping_count":
                len(
                    conditional_mappings
                ),

            "rejected_condition_signal_count":
                len(
                    rejected_condition_signals
                ),

            "embedded_question_complements_rejected":
                len(
                    [
                        item
                        for item in rejected_condition_signals
                        if (
                            item.get(
                                "rejection_reason"
                            )
                            == "EMBEDDED_WHETHER_COMPLEMENT"
                        )
                    ]
                ),

            "cross_claim_conditional_application_finalized_count":
                finalized_cross_claim_count,

            "explicit_conditions_only":
                True,

            "causal_reasoning_performed":
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
            "support_clarification_contrast_mapping",
    }


def map_support_clarification_contrast_v1(
    conditional_mapping_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Map explicit article-local support, clarification,
    example, and contrast structures.

    This stage operates conservatively.

    It may finalize:
    - explicit intra-claim contrast,
    - explicit intra-claim elaboration/example,
    - strong adjacent cross-claim contrast,
    - strong adjacent cross-claim example/clarification.

    It does NOT:
    - infer causal relations,
    - assess factual truth,
    - adjudicate contradictions,
    - build logical chains,
    - infer unsupported cross-claim support,
    - perform authority checking,
    - select links or targets,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        conditional_mapping_result,
        Mapping,
    ):
        raise LogicalIntelligenceError(
            "conditional_mapping_result must be a mapping."
        )

    if (
        conditional_mapping_result.get(
            "schema_version"
        )
        != "conditional_logical_mapping_result_v1"
    ):
        raise LogicalIntelligenceError(
            "4.6.6J requires "
            "conditional_logical_mapping_result_v1."
        )

    if (
        conditional_mapping_result.get(
            "status"
        )
        != "CONDITIONAL_LOGICAL_MAPPING_COMPLETE"
    ):
        raise LogicalIntelligenceError(
            "Conditional logical mapping is incomplete."
        )

    if (
        conditional_mapping_result.get(
            "phase"
        )
        != "4.6.6"
    ):
        raise LogicalIntelligenceError(
            "4.6.6J requires Phase 4.6.6 input."
        )

    source_units = list(
        conditional_mapping_result.get(
            "logical_claim_units"
        )
        or []
    )

    if not source_units:
        raise LogicalIntelligenceError(
            "Logical Claim Units are missing."
        )

    units_by_id = {
        unit.get(
            "logical_claim_unit_id"
        ): unit
        for unit in source_units
    }

    intra_claim_mappings = []
    cross_claim_mappings = []
    rejected_intra_claim_candidates = []
    rejected_cross_claim_candidates = []
    updated_units = {}

    def clean_clause(value: str) -> str:
        return value.strip(
            " \t\r\n,;:"
        )

    def stable_mapping_id(
        *,
        scope: str,
        relation_type: str,
        source_id: str,
        target_id: str = "",
        marker: str = "",
        start_char: int | None = None,
    ) -> str:
        material = (
            str(
                conditional_mapping_result.get(
                    "article_id"
                )
                or ""
            )
            + "|"
            + scope
            + "|"
            + relation_type
            + "|"
            + str(source_id)
            + "|"
            + str(target_id)
            + "|"
            + str(marker)
            + "|"
            + str(start_char)
        )

        return (
            "support_logic_"
            + hashlib.sha256(
                material.encode(
                    "utf-8"
                )
            ).hexdigest()[:16]
        )

    # ---------------------------------------------------------
    # 1. Prepare units and map explicit intra-claim structures.
    # ---------------------------------------------------------

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
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
                "conditional_mapping"
            )
            != "COMPLETE"
        ):
            raise LogicalIntelligenceError(
                "Conditional mapping must be COMPLETE "
                "before 4.6.6J."
            )

        if (
            state.get(
                "support_clarification_contrast_mapping"
            )
            != "PENDING"
        ):
            raise LogicalIntelligenceError(
                "Support/clarification/contrast state "
                "was not PENDING."
            )

        state[
            "support_clarification_contrast_mapping"
        ] = "COMPLETE"

        updated[
            "logical_analysis_state"
        ] = state

        updated[
            "support_clarification_contrast_context"
        ] = {
            "intra_claim_mapping_ids": [],
            "cross_claim_incoming_mapping_ids": [],
            "cross_claim_outgoing_mapping_ids": [],
            "mapping_complete": True,
        }

        text_value = str(
            updated.get("text")
            or ""
        )

        signals = list(
            (
                updated.get(
                    "discourse_signal_analysis"
                )
                or {}
            ).get(
                "signals",
                [],
            )
        )

        relevant_signals = [
            signal
            for signal in signals
            if (
                signal.get(
                    "accepted"
                )
                is True
                and signal.get(
                    "signal_type"
                )
                in (
                    "CONTRAST",
                    "ELABORATION",
                )
            )
        ]

        for signal in relevant_signals:
            signal_type = signal.get(
                "signal_type"
            )

            start = signal.get(
                "start_char"
            )

            end = signal.get(
                "end_char"
            )

            if not (
                isinstance(start, int)
                and isinstance(end, int)
                and 0 <= start < end <= len(text_value)
            ):
                raise LogicalIntelligenceError(
                    "Invalid J discourse-signal span."
                )

            marker = text_value[
                start:end
            ]

            raw_before = text_value[:start]
            raw_after = text_value[end:]

            before = clean_clause(
                raw_before
            )

            after = clean_clause(
                raw_after
            )

            relation_type = None
            left_text = None
            right_text = None
            pattern = None

            if signal_type == "CONTRAST":
                if start <= 5:
                    # Initial Although/Though is only treated as
                    # intra-claim when its subordinate clause has
                    # an explicit comma-delimited main clause.
                    marker_lower = marker.lower()

                    if marker_lower in (
                        "although",
                        "though",
                    ):
                        comma_index = after.find(
                            ","
                        )

                        if comma_index > 0:
                            left_text = clean_clause(
                                after[
                                    :comma_index
                                ]
                            )

                            right_text = clean_clause(
                                after[
                                    comma_index + 1:
                                ]
                            )

                            if (
                                left_text
                                and right_text
                            ):
                                relation_type = (
                                    "INTRA_CLAIM_CONTRAST"
                                )

                                pattern = (
                                    "INITIAL_CONCESSIVE_CLAUSE_"
                                    "THEN_MAIN_CLAUSE"
                                )

                else:
                    if (
                        before
                        and after
                    ):
                        relation_type = (
                            "INTRA_CLAIM_CONTRAST"
                        )

                        left_text = before
                        right_text = after

                        pattern = (
                            "CLAUSE_CONTRAST_CONNECTOR"
                        )

            elif signal_type == "ELABORATION":
                # Initial "For example" normally points backward
                # to the previous claim and is handled in the
                # cross-claim pass below. Do not duplicate it here.
                if start > 5:
                    marker_lower = marker.lower()

                    # Parenthetical ", for example," does not
                    # introduce the clause to its right.
                    # It comments on the preceding phrase instead.
                    parenthetical_example = (
                        marker_lower
                        in (
                            "for example",
                            "for instance",
                        )
                        and raw_before.rstrip().endswith(",")
                        and raw_after.lstrip().startswith(",")
                    )

                    if parenthetical_example:
                        rejected_intra_claim_candidates.append({
                            "logical_claim_unit_id":
                                unit_id,

                            "sentence_global_index":
                                updated.get(
                                    "sentence_global_index"
                                ),

                            "signal_type":
                                signal_type,

                            "discourse_marker":
                                marker,

                            "start_char":
                                start,

                            "rejection_reason":
                                "PARENTHETICAL_EXAMPLE_MARKER",

                            "final_intra_claim_mapping_created":
                                False,
                        })

                        continue

                    if marker_lower == "such as":
                        # Restrict the example to the local
                        # parenthetical/list span.
                        closing_index = after.find(
                            ")"
                        )

                        example_span = (
                            after[
                                :closing_index
                            ]
                            if closing_index >= 0
                            else after
                        )

                        right_text = clean_clause(
                            example_span
                        )

                        anchor_source = before.rstrip()

                        if anchor_source.endswith("("):
                            anchor_source = (
                                anchor_source[:-1]
                                .rstrip()
                            )

                        anchor_match = re.search(
                            r"([A-Za-z][A-Za-z\s'-]{1,80})$",
                            anchor_source,
                        )

                        left_text = (
                            clean_clause(
                                anchor_match.group(1)
                            )
                            if anchor_match is not None
                            else clean_clause(
                                anchor_source
                            )
                        )

                        relation_type = (
                            "INTRA_CLAIM_CLARIFICATION_EXAMPLE"
                        )

                        pattern = (
                            "LOCAL_SUCH_AS_EXAMPLE"
                        )

                    elif marker_lower in (
                        "for example",
                        "for instance",
                    ):
                        # For a parenthesized example such as
                        # "(for example, X)", map the local
                        # anchor immediately before the parenthesis
                        # to the content inside that parenthesis.
                        opening_index = before.rfind(
                            "("
                        )

                        closing_index = after.find(
                            ")"
                        )

                        if opening_index >= 0:
                            anchor_source = clean_clause(
                                before[
                                    :opening_index
                                ]
                            )

                            anchor_match = re.search(
                                r"([^,;:.]{1,100})$",
                                anchor_source,
                            )

                            left_text = (
                                clean_clause(
                                    anchor_match.group(1)
                                )
                                if anchor_match is not None
                                else anchor_source
                            )

                            example_span = (
                                after[
                                    :closing_index
                                ]
                                if closing_index >= 0
                                else after
                            )

                            right_text = clean_clause(
                                example_span.lstrip(
                                    " ,"
                                )
                            )

                            relation_type = (
                                "INTRA_CLAIM_CLARIFICATION_EXAMPLE"
                            )

                            pattern = (
                                "PARENTHESIZED_LOCAL_EXAMPLE"
                            )

            if relation_type is None:
                continue

            mapping_id = stable_mapping_id(
                scope="INTRA_CLAIM",
                relation_type=relation_type,
                source_id=str(
                    unit_id
                ),
                marker=marker,
                start_char=start,
            )

            mapping = {
                "support_clarification_contrast_mapping_id":
                    mapping_id,

                "mapping_scope":
                    "INTRA_CLAIM_EXPLICIT",

                "relation_type":
                    relation_type,

                "logical_claim_unit_id":
                    unit_id,

                "section_id":
                    updated.get(
                        "section_id"
                    ),

                "sentence_id":
                    updated.get(
                        "sentence_id"
                    ),

                "sentence_global_index":
                    updated.get(
                        "sentence_global_index"
                    ),

                "discourse_marker":
                    marker,

                "mapping_pattern":
                    pattern,

                "left_clause": {
                    "text":
                        left_text,

                    "explicit":
                        True,
                },

                "right_clause": {
                    "text":
                        right_text,

                    "explicit":
                        True,
                },

                "relation_finalized":
                    True,

                "causal_relation_inferred":
                    False,

                "truth_assessed":
                    False,

                "contradiction_adjudicated":
                    False,

                "article_local_only":
                    True,
            }

            intra_claim_mappings.append(
                mapping
            )

            updated[
                "support_clarification_contrast_context"
            ][
                "intra_claim_mapping_ids"
            ].append(
                mapping_id
            )

        updated_units[
            unit_id
        ] = updated

    # ---------------------------------------------------------
    # 2. Finalize only strong explicit adjacent cross-claim
    #    contrast / clarification candidates.
    # ---------------------------------------------------------

    for relation in (
        conditional_mapping_result.get(
            "adjacent_relations"
        )
        or []
    ):
        relation_type = relation.get(
            "relation_type"
        )

        if relation_type not in (
            "CONTRAST",
            "ELABORATION",
        ):
            continue

        source_id = relation.get(
            "source_logical_claim_unit_id"
        )

        target_id = relation.get(
            "target_logical_claim_unit_id"
        )

        source_unit = units_by_id.get(
            source_id
        )

        target_unit = units_by_id.get(
            target_id
        )

        if (
            source_unit is None
            or target_unit is None
        ):
            raise LogicalIntelligenceError(
                "Adjacent J relation lost unit identity."
            )

        target_text = str(
            target_unit.get("text")
            or ""
        )

        target_signals = list(
            (
                target_unit.get(
                    "discourse_signal_analysis"
                )
                or {}
            ).get(
                "signals",
                [],
            )
        )

        initial_signal = next(
            (
                signal
                for signal in target_signals
                if (
                    signal.get(
                        "accepted"
                    )
                    is True
                    and signal.get(
                        "signal_type"
                    )
                    == relation_type
                    and isinstance(
                        signal.get(
                            "start_char"
                        ),
                        int,
                    )
                    and signal.get(
                        "start_char"
                    ) <= 5
                )
            ),
            None,
        )

        if initial_signal is None:
            continue

        marker = str(
            initial_signal.get(
                "matched_text"
            )
            or ""
        )

        marker_lower = marker.lower()

        source_index = relation.get(
            "source_sentence_global_index"
        )

        target_index = relation.get(
            "target_sentence_global_index"
        )

        final_relation_type = None
        rejection_reason = None

        if relation_type == "CONTRAST":
            if marker_lower == "but":
                final_relation_type = (
                    "CROSS_CLAIM_CONTRAST"
                )

            elif marker_lower in (
                "although",
                "though",
            ):
                after = target_text[
                    int(
                        initial_signal.get(
                            "end_char"
                        )
                    ):
                ]

                comma_index = after.find(
                    ","
                )

                if comma_index > 0:
                    rejection_reason = (
                        "INITIAL_CONCESSION_IS_INTRA_CLAIM"
                    )
                else:
                    rejection_reason = (
                        "RHETORICAL_OR_INCOMPLETE_CONCESSION"
                    )

            else:
                rejection_reason = (
                    "UNSUPPORTED_INITIAL_CONTRAST_FORM"
                )

        elif relation_type == "ELABORATION":
            if marker_lower in (
                "for example",
                "for instance",
            ):
                final_relation_type = (
                    "CROSS_CLAIM_CLARIFICATION_EXAMPLE"
                )

            else:
                rejection_reason = (
                    "UNSUPPORTED_CROSS_CLAIM_ELABORATION_FORM"
                )

        if final_relation_type is None:
            rejected_cross_claim_candidates.append({
                "source_logical_claim_unit_id":
                    source_id,

                "target_logical_claim_unit_id":
                    target_id,

                "source_sentence_global_index":
                    source_index,

                "target_sentence_global_index":
                    target_index,

                "provisional_relation_type":
                    relation_type,

                "discourse_marker":
                    marker,

                "rejection_reason":
                    rejection_reason,

                "final_cross_claim_mapping_created":
                    False,
            })

            continue

        mapping_id = stable_mapping_id(
            scope="CROSS_CLAIM",
            relation_type=final_relation_type,
            source_id=str(
                source_id
            ),
            target_id=str(
                target_id
            ),
            marker=marker,
            start_char=initial_signal.get(
                "start_char"
            ),
        )

        cross_mapping = {
            "support_clarification_contrast_mapping_id":
                mapping_id,

            "mapping_scope":
                "CROSS_CLAIM_ADJACENT_EXPLICIT",

            "relation_type":
                final_relation_type,

            "source_logical_claim_unit_id":
                source_id,

            "target_logical_claim_unit_id":
                target_id,

            "source_sentence_global_index":
                source_index,

            "target_sentence_global_index":
                target_index,

            "section_id":
                relation.get(
                    "section_id"
                ),

            "discourse_marker":
                marker,

            "provisional_relation_type":
                relation_type,

            "relation_finalized":
                True,

            "causal_relation_inferred":
                False,

            "truth_assessed":
                False,

            "contradiction_adjudicated":
                False,

            "article_local_only":
                True,
        }

        cross_claim_mappings.append(
            cross_mapping
        )

        updated_units[
            source_id
        ][
            "support_clarification_contrast_context"
        ][
            "cross_claim_outgoing_mapping_ids"
        ].append(
            mapping_id
        )

        updated_units[
            target_id
        ][
            "support_clarification_contrast_context"
        ][
            "cross_claim_incoming_mapping_ids"
        ].append(
            mapping_id
        )

    ordered_units = [
        updated_units[
            unit.get(
                "logical_claim_unit_id"
            )
        ]
        for unit in source_units
    ]

    all_mapping_ids = [
        item.get(
            "support_clarification_contrast_mapping_id"
        )
        for item in (
            intra_claim_mappings
            + cross_claim_mappings
        )
    ]

    if (
        len(all_mapping_ids)
        != len(
            set(all_mapping_ids)
        )
    ):
        raise LogicalIntelligenceError(
            "Duplicate 4.6.6J mapping IDs detected."
        )

    rebuilt_sections = []

    for section in (
        conditional_mapping_result.get(
            "logical_sections"
        )
        or []
    ):
        section_id = section.get(
            "section_id"
        )

        section_units = [
            unit
            for unit in ordered_units
            if (
                unit.get(
                    "section_id"
                )
                == section_id
            )
        ]

        section_intra = [
            item
            for item in intra_claim_mappings
            if (
                item.get(
                    "section_id"
                )
                == section_id
            )
        ]

        section_cross = [
            item
            for item in cross_claim_mappings
            if (
                item.get(
                    "section_id"
                )
                == section_id
            )
        ]

        rebuilt = dict(
            section
        )

        rebuilt[
            "logical_claim_units"
        ] = section_units

        rebuilt[
            "support_clarification_contrast_mapping_count"
        ] = (
            len(section_intra)
            + len(section_cross)
        )

        rebuilt[
            "intra_claim_support_clarification_contrast_mappings"
        ] = section_intra

        rebuilt[
            "cross_claim_support_clarification_contrast_mappings"
        ] = section_cross

        rebuilt_sections.append(
            rebuilt
        )

    boundaries = dict(
        conditional_mapping_result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "support_clarification_contrast_mapping_performed"
    ] = True

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
            "support_clarification_contrast_mapping_result_v1",

        "logical_intelligence_version":
            LOGICAL_INTELLIGENCE_VERSION,

        "phase":
            "4.6.6",

        "patch":
            "4.6.6J",

        "status":
            "SUPPORT_CLARIFICATION_CONTRAST_MAPPING_COMPLETE",

        "workspace_id":
            conditional_mapping_result.get(
                "workspace_id"
            ),

        "document_id":
            conditional_mapping_result.get(
                "document_id"
            ),

        "source_type":
            conditional_mapping_result.get(
                "source_type"
            ),

        "source_id":
            conditional_mapping_result.get(
                "source_id"
            ),

        "content_hash":
            conditional_mapping_result.get(
                "content_hash"
            ),

        "body_ref":
            conditional_mapping_result.get(
                "body_ref"
            ),

        "article_id":
            conditional_mapping_result.get(
                "article_id"
            ),

        "title":
            conditional_mapping_result.get(
                "title"
            ),

        "canonical_section_order":
            list(
                conditional_mapping_result.get(
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
            conditional_mapping_result.get(
                "adjacent_pair_count"
            ),

        "adjacent_relation_count":
            conditional_mapping_result.get(
                "adjacent_relation_count"
            ),

        "adjacent_pair_evaluations":
            list(
                conditional_mapping_result.get(
                    "adjacent_pair_evaluations"
                )
                or []
            ),

        "adjacent_relations":
            list(
                conditional_mapping_result.get(
                    "adjacent_relations"
                )
                or []
            ),

        "non_adjacent_pair_evaluations":
            list(
                conditional_mapping_result.get(
                    "non_adjacent_pair_evaluations"
                )
                or []
            ),

        "non_adjacent_relation_count":
            conditional_mapping_result.get(
                "non_adjacent_relation_count"
            ),

        "non_adjacent_relations":
            list(
                conditional_mapping_result.get(
                    "non_adjacent_relations"
                )
                or []
            ),

        "premise_conclusion_mapping_count":
            conditional_mapping_result.get(
                "premise_conclusion_mapping_count"
            ),

        "premise_conclusion_mappings":
            list(
                conditional_mapping_result.get(
                    "premise_conclusion_mappings"
                )
                or []
            ),

        "qualification_mapping_count":
            conditional_mapping_result.get(
                "qualification_mapping_count"
            ),

        "qualification_mappings":
            list(
                conditional_mapping_result.get(
                    "qualification_mappings"
                )
                or []
            ),

        "exception_mapping_count":
            conditional_mapping_result.get(
                "exception_mapping_count"
            ),

        "exception_mappings":
            list(
                conditional_mapping_result.get(
                    "exception_mappings"
                )
                or []
            ),

        "conditional_mapping_count":
            conditional_mapping_result.get(
                "conditional_mapping_count"
            ),

        "conditional_mappings":
            list(
                conditional_mapping_result.get(
                    "conditional_mappings"
                )
                or []
            ),

        "rejected_condition_signal_count":
            conditional_mapping_result.get(
                "rejected_condition_signal_count"
            ),

        "rejected_condition_signals":
            list(
                conditional_mapping_result.get(
                    "rejected_condition_signals"
                )
                or []
            ),

        "cross_claim_conditional_application_finalized_count":
            conditional_mapping_result.get(
                "cross_claim_conditional_application_finalized_count"
            ),

        "intra_claim_support_clarification_contrast_mapping_count":
            len(
                intra_claim_mappings
            ),

        "intra_claim_support_clarification_contrast_mappings":
            intra_claim_mappings,

        "cross_claim_support_clarification_contrast_mapping_count":
            len(
                cross_claim_mappings
            ),

        "cross_claim_support_clarification_contrast_mappings":
            cross_claim_mappings,

        "rejected_intra_claim_support_clarification_contrast_candidate_count":
            len(
                rejected_intra_claim_candidates
            ),

        "rejected_intra_claim_support_clarification_contrast_candidates":
            rejected_intra_claim_candidates,

        "rejected_cross_claim_support_clarification_contrast_candidate_count":
            len(
                rejected_cross_claim_candidates
            ),

        "rejected_cross_claim_support_clarification_contrast_candidates":
            rejected_cross_claim_candidates,

        "support_clarification_contrast_mapping_count":
            (
                len(
                    intra_claim_mappings
                )
                + len(
                    cross_claim_mappings
                )
            ),

        "logical_sections":
            rebuilt_sections,

        "logical_claim_units":
            ordered_units,

        "support_clarification_contrast_summary": {
            "intra_claim_mapping_count":
                len(
                    intra_claim_mappings
                ),

            "cross_claim_mapping_count":
                len(
                    cross_claim_mappings
                ),

            "rejected_intra_claim_candidate_count":
                len(
                    rejected_intra_claim_candidates
                ),

            "rejected_cross_claim_candidate_count":
                len(
                    rejected_cross_claim_candidates
                ),

            "causal_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "contradiction_adjudication_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "logical_chain_construction",
    }


def construct_logical_chains_v1(
    support_clarification_contrast_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Construct article-local multi-step logical chains from
    already-finalized cross-claim logical relations.

    A logical chain requires at least two connected finalized
    relation edges:

        A -> B -> C

    This stage does NOT:
    - promote provisional relations,
    - invent missing relations,
    - infer causation,
    - assess factual truth,
    - adjudicate contradictions,
    - perform logical-tension analysis,
    - perform authority checking,
    - select links or targets,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        support_clarification_contrast_result,
        Mapping,
    ):
        raise LogicalIntelligenceError(
            "support_clarification_contrast_result "
            "must be a mapping."
        )

    if (
        support_clarification_contrast_result.get(
            "schema_version"
        )
        != "support_clarification_contrast_mapping_result_v1"
    ):
        raise LogicalIntelligenceError(
            "4.6.6K requires "
            "support_clarification_contrast_mapping_result_v1."
        )

    if (
        support_clarification_contrast_result.get(
            "status"
        )
        != "SUPPORT_CLARIFICATION_CONTRAST_MAPPING_COMPLETE"
    ):
        raise LogicalIntelligenceError(
            "4.6.6J must be complete before "
            "Logical-chain construction."
        )

    if (
        support_clarification_contrast_result.get(
            "phase"
        )
        != "4.6.6"
    ):
        raise LogicalIntelligenceError(
            "4.6.6K requires Phase 4.6.6 input."
        )

    source_units = list(
        support_clarification_contrast_result.get(
            "logical_claim_units"
        )
        or []
    )

    if not source_units:
        raise LogicalIntelligenceError(
            "Logical Claim Units are missing."
        )

    units_by_id = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
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

        units_by_id[
            unit_id
        ] = unit

    eligible_edges = []

    # ---------------------------------------------------------
    # 1. Finalized J cross-claim relations.
    # ---------------------------------------------------------

    for relation in (
        support_clarification_contrast_result.get(
            "cross_claim_support_clarification_contrast_mappings"
        )
        or []
    ):
        if (
            relation.get(
                "relation_finalized"
            )
            is not True
        ):
            continue

        source_id = relation.get(
            "source_logical_claim_unit_id"
        )

        target_id = relation.get(
            "target_logical_claim_unit_id"
        )

        if (
            source_id not in units_by_id
            or target_id not in units_by_id
        ):
            raise LogicalIntelligenceError(
                "Finalized J relation references "
                "an unknown Logical Claim Unit."
            )

        edge_id = relation.get(
            "support_clarification_contrast_mapping_id"
        )

        if not edge_id:
            raise LogicalIntelligenceError(
                "Finalized J relation has no mapping ID."
            )

        eligible_edges.append({
            "logical_chain_edge_id":
                edge_id,

            "source_logical_claim_unit_id":
                source_id,

            "target_logical_claim_unit_id":
                target_id,

            "source_sentence_global_index":
                relation.get(
                    "source_sentence_global_index"
                ),

            "target_sentence_global_index":
                relation.get(
                    "target_sentence_global_index"
                ),

            "section_id":
                relation.get(
                    "section_id"
                ),

            "relation_type":
                relation.get(
                    "relation_type"
                ),

            "relation_origin":
                "4.6.6J_FINALIZED",

            "relation_finalized":
                True,

            "causal_relation_inferred":
                False,

            "truth_assessed":
                False,

            "article_local_only":
                True,
        })

    # ---------------------------------------------------------
    # 2. Finalized non-adjacent conditional applications from I.
    # ---------------------------------------------------------

    for relation in (
        support_clarification_contrast_result.get(
            "non_adjacent_relations"
        )
        or []
    ):
        if (
            relation.get(
                "relation_type"
            )
            != "CONDITIONAL_APPLICATION"
            or relation.get(
                "conditional_structure_finalized"
            )
            is not True
        ):
            continue

        source_id = relation.get(
            "source_logical_claim_unit_id"
        )

        target_id = relation.get(
            "target_logical_claim_unit_id"
        )

        if (
            source_id not in units_by_id
            or target_id not in units_by_id
        ):
            raise LogicalIntelligenceError(
                "Finalized conditional relation references "
                "an unknown Logical Claim Unit."
            )

        edge_id = relation.get(
            "conditional_mapping_id"
        )

        if not edge_id:
            raise LogicalIntelligenceError(
                "Finalized conditional relation has "
                "no mapping ID."
            )

        eligible_edges.append({
            "logical_chain_edge_id":
                edge_id,

            "source_logical_claim_unit_id":
                source_id,

            "target_logical_claim_unit_id":
                target_id,

            "source_sentence_global_index":
                relation.get(
                    "source_sentence_global_index"
                ),

            "target_sentence_global_index":
                relation.get(
                    "target_sentence_global_index"
                ),

            "section_id":
                relation.get(
                    "section_id"
                ),

            "relation_type":
                "CONDITIONAL_APPLICATION",

            "relation_origin":
                "4.6.6I_FINALIZED",

            "relation_finalized":
                True,

            "causal_relation_inferred":
                False,

            "truth_assessed":
                False,

            "article_local_only":
                True,
        })

    edge_ids = [
        edge.get(
            "logical_chain_edge_id"
        )
        for edge in eligible_edges
    ]

    if (
        len(edge_ids)
        != len(
            set(edge_ids)
        )
    ):
        raise LogicalIntelligenceError(
            "Duplicate finalized chain-edge IDs detected."
        )

    # ---------------------------------------------------------
    # 3. Build directed adjacency from finalized relations only.
    # ---------------------------------------------------------

    outgoing = {}

    for edge in eligible_edges:
        source_id = edge[
            "source_logical_claim_unit_id"
        ]

        outgoing.setdefault(
            source_id,
            [],
        ).append(
            edge
        )

    chain_candidates = []

    def walk(
        *,
        current_unit_id: str,
        path_unit_ids: list[str],
        path_edges: list[dict[str, Any]],
    ) -> None:
        next_edges = outgoing.get(
            current_unit_id,
            [],
        )

        extended = False

        for edge in next_edges:
            target_id = edge[
                "target_logical_claim_unit_id"
            ]

            # Prevent cycles from being turned into artificial chains.
            if target_id in path_unit_ids:
                continue

            extended = True

            walk(
                current_unit_id=target_id,
                path_unit_ids=(
                    path_unit_ids
                    + [target_id]
                ),
                path_edges=(
                    path_edges
                    + [edge]
                ),
            )

        # A logical chain must contain at least two relation edges.
        if (
            not extended
            and len(path_edges) >= 2
        ):
            chain_candidates.append({
                "unit_ids":
                    list(
                        path_unit_ids
                    ),

                "edges":
                    list(
                        path_edges
                    ),
            })

    # Only start from nodes that have outgoing edges and no
    # finalized incoming edge. This produces maximal chains.
    incoming_targets = {
        edge[
            "target_logical_claim_unit_id"
        ]
        for edge in eligible_edges
    }

    start_nodes = sorted(
        {
            edge[
                "source_logical_claim_unit_id"
            ]
            for edge in eligible_edges
            if (
                edge[
                    "source_logical_claim_unit_id"
                ]
                not in incoming_targets
            )
        }
    )

    for start_id in start_nodes:
        walk(
            current_unit_id=start_id,
            path_unit_ids=[
                start_id
            ],
            path_edges=[],
        )

    logical_chains = []
    seen_chain_signatures = set()

    for candidate in chain_candidates:
        unit_ids = candidate[
            "unit_ids"
        ]

        edges = candidate[
            "edges"
        ]

        signature = tuple(
            edge[
                "logical_chain_edge_id"
            ]
            for edge in edges
        )

        if signature in seen_chain_signatures:
            continue

        seen_chain_signatures.add(
            signature
        )

        material = (
            str(
                support_clarification_contrast_result.get(
                    "article_id"
                )
                or ""
            )
            + "|"
            + "|".join(
                signature
            )
        )

        chain_id = (
            "logical_chain_"
            + hashlib.sha256(
                material.encode(
                    "utf-8"
                )
            ).hexdigest()[:16]
        )

        sentence_indexes = [
            (
                units_by_id[
                    unit_id
                ].get(
                    "sentence_global_index"
                )
            )
            for unit_id in unit_ids
        ]

        section_ids = [
            (
                units_by_id[
                    unit_id
                ].get(
                    "section_id"
                )
            )
            for unit_id in unit_ids
        ]

        logical_chains.append({
            "logical_chain_id":
                chain_id,

            "logical_claim_unit_ids":
                unit_ids,

            "sentence_global_indexes":
                sentence_indexes,

            "edge_count":
                len(
                    edges
                ),

            "claim_count":
                len(
                    unit_ids
                ),

            "relation_sequence": [
                edge.get(
                    "relation_type"
                )
                for edge in edges
            ],

            "edge_ids": [
                edge.get(
                    "logical_chain_edge_id"
                )
                for edge in edges
            ],

            "edges":
                edges,

            "section_ids":
                section_ids,

            "single_section":
                (
                    len(
                        {
                            section_id
                            for section_id in section_ids
                            if section_id
                        }
                    )
                    <= 1
                ),

            "chain_finalized":
                True,

            "relations_preexisting":
                True,

            "new_relation_inferred":
                False,

            "causal_relation_inferred":
                False,

            "truth_assessed":
                False,

            "contradiction_adjudicated":
                False,

            "article_local_only":
                True,
        })

    # ---------------------------------------------------------
    # 4. Complete K state without performing L or later work.
    # ---------------------------------------------------------

    updated_units = []

    chain_ids_by_unit = {}

    for chain in logical_chains:
        for unit_id in chain.get(
            "logical_claim_unit_ids",
            [],
        ):
            chain_ids_by_unit.setdefault(
                unit_id,
                [],
            ).append(
                chain.get(
                    "logical_chain_id"
                )
            )

    for unit in source_units:
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
                "support_clarification_contrast_mapping"
            )
            != "COMPLETE"
        ):
            raise LogicalIntelligenceError(
                "4.6.6J state must be COMPLETE "
                "before 4.6.6K."
            )

        if (
            state.get(
                "logical_chain_construction"
            )
            != "PENDING"
        ):
            raise LogicalIntelligenceError(
                "Logical-chain construction state "
                "was not PENDING."
            )

        state[
            "logical_chain_construction"
        ] = "COMPLETE"

        updated[
            "logical_analysis_state"
        ] = state

        updated[
            "logical_chain_context"
        ] = {
            "logical_chain_ids":
                list(
                    chain_ids_by_unit.get(
                        unit.get(
                            "logical_claim_unit_id"
                        ),
                        [],
                    )
                ),

            "participates_in_logical_chain":
                bool(
                    chain_ids_by_unit.get(
                        unit.get(
                            "logical_claim_unit_id"
                        ),
                        [],
                    )
                ),

            "logical_chain_construction_complete":
                True,
        }

        updated_units.append(
            updated
        )

    updated_units_by_id = {
        unit.get(
            "logical_claim_unit_id"
        ): unit
        for unit in updated_units
    }

    rebuilt_sections = []

    for section in (
        support_clarification_contrast_result.get(
            "logical_sections"
        )
        or []
    ):
        rebuilt = dict(
            section
        )

        section_id = rebuilt.get(
            "section_id"
        )

        section_units = [
            updated_units_by_id[
                unit.get(
                    "logical_claim_unit_id"
                )
            ]
            for unit in (
                section.get(
                    "logical_claim_units"
                )
                or []
            )
            if (
                unit.get(
                    "logical_claim_unit_id"
                )
                in updated_units_by_id
            )
        ]

        section_chains = [
            chain
            for chain in logical_chains
            if (
                section_id
                in (
                    chain.get(
                        "section_ids"
                    )
                    or []
                )
            )
        ]

        rebuilt[
            "logical_claim_units"
        ] = section_units

        rebuilt[
            "logical_chain_count"
        ] = len(
            section_chains
        )

        rebuilt[
            "logical_chain_ids"
        ] = [
            chain.get(
                "logical_chain_id"
            )
            for chain in section_chains
        ]

        rebuilt_sections.append(
            rebuilt
        )

    boundaries = dict(
        support_clarification_contrast_result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "logical_chain_construction_performed"
    ] = True

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

    result = dict(
        support_clarification_contrast_result
    )

    result.update({
        "schema_version":
            "logical_chain_construction_result_v1",

        "patch":
            "4.6.6K",

        "status":
            "LOGICAL_CHAIN_CONSTRUCTION_COMPLETE",

        "logical_claim_units":
            updated_units,

        "logical_sections":
            rebuilt_sections,

        "eligible_finalized_chain_edge_count":
            len(
                eligible_edges
            ),

        "eligible_finalized_chain_edges":
            eligible_edges,

        "logical_chain_count":
            len(
                logical_chains
            ),

        "logical_chains":
            logical_chains,

        "logical_chain_summary": {
            "eligible_finalized_edge_count":
                len(
                    eligible_edges
                ),

            "logical_chain_count":
                len(
                    logical_chains
                ),

            "minimum_edges_per_chain":
                2,

            "provisional_relations_promoted":
                False,

            "new_relations_inferred":
                False,

            "zero_chains_is_valid_result":
                True,

            "causal_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "contradiction_adjudication_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "logical_tension_candidate_detection",
    })

    return result


def detect_logical_tension_candidates_v1(
    logical_chain_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Detect conservative article-local logical-tension candidates.

    A tension candidate is not a contradiction verdict.
    This stage only identifies already-explicit competing logical
    interpretations that warrant later consolidation/review.

    Candidate policy:
    - begin only from finalized J cross-claim contrasts,
    - require same-section article-local relation,
    - exclude pairs where either claim is governed by an explicit
      conditional mapping, because those commonly represent
      separate scenarios rather than competing propositions.

    This stage does NOT:
    - assess factual truth,
    - adjudicate contradiction,
    - infer causation,
    - use external authority,
    - create new cross-claim relations,
    - perform linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        logical_chain_result,
        Mapping,
    ):
        raise LogicalIntelligenceError(
            "logical_chain_result must be a mapping."
        )

    if (
        logical_chain_result.get(
            "schema_version"
        )
        != "logical_chain_construction_result_v1"
    ):
        raise LogicalIntelligenceError(
            "4.6.6L requires "
            "logical_chain_construction_result_v1."
        )

    if (
        logical_chain_result.get(
            "status"
        )
        != "LOGICAL_CHAIN_CONSTRUCTION_COMPLETE"
    ):
        raise LogicalIntelligenceError(
            "4.6.6K must be complete before "
            "logical-tension detection."
        )

    if (
        logical_chain_result.get(
            "phase"
        )
        != "4.6.6"
    ):
        raise LogicalIntelligenceError(
            "4.6.6L requires Phase 4.6.6 input."
        )

    source_units = list(
        logical_chain_result.get(
            "logical_claim_units"
        )
        or []
    )

    if not source_units:
        raise LogicalIntelligenceError(
            "Logical Claim Units are missing."
        )

    units_by_id = {}
    units_by_sentence_index = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise LogicalIntelligenceError(
                "Invalid Logical Claim Unit."
            )

        unit_id = unit.get(
            "logical_claim_unit_id"
        )

        sentence_index = unit.get(
            "sentence_global_index"
        )

        if not unit_id:
            raise LogicalIntelligenceError(
                "Logical Claim Unit has no ID."
            )

        units_by_id[
            unit_id
        ] = unit

        if isinstance(
            sentence_index,
            int,
        ):
            units_by_sentence_index[
                sentence_index
            ] = unit

    conditional_sentence_indexes = {
        mapping.get(
            "sentence_global_index"
        )
        for mapping in (
            logical_chain_result.get(
                "conditional_mappings"
            )
            or []
        )
        if isinstance(
            mapping.get(
                "sentence_global_index"
            ),
            int,
        )
    }

    qualifications_by_sentence = {}

    for mapping in (
        logical_chain_result.get(
            "qualification_mappings"
        )
        or []
    ):
        sentence_index = mapping.get(
            "sentence_global_index"
        )

        if not isinstance(
            sentence_index,
            int,
        ):
            continue

        qualifications_by_sentence.setdefault(
            sentence_index,
            [],
        ).append(
            mapping
        )

    tension_candidates = []
    rejected_contrast_candidates = []

    for relation in (
        logical_chain_result.get(
            "cross_claim_support_clarification_contrast_mappings"
        )
        or []
    ):
        if (
            relation.get(
                "relation_type"
            )
            != "CROSS_CLAIM_CONTRAST"
            or relation.get(
                "relation_finalized"
            )
            is not True
        ):
            continue

        source_id = relation.get(
            "source_logical_claim_unit_id"
        )

        target_id = relation.get(
            "target_logical_claim_unit_id"
        )

        source_unit = units_by_id.get(
            source_id
        )

        target_unit = units_by_id.get(
            target_id
        )

        if (
            source_unit is None
            or target_unit is None
        ):
            raise LogicalIntelligenceError(
                "Finalized J contrast references "
                "an unknown Logical Claim Unit."
            )

        source_index = relation.get(
            "source_sentence_global_index"
        )

        target_index = relation.get(
            "target_sentence_global_index"
        )

        source_section = source_unit.get(
            "section_id"
        )

        target_section = target_unit.get(
            "section_id"
        )

        same_section = (
            source_section
            == target_section
            and source_section is not None
        )

        source_conditional = (
            source_index
            in conditional_sentence_indexes
        )

        target_conditional = (
            target_index
            in conditional_sentence_indexes
        )

        if not same_section:
            rejected_contrast_candidates.append({
                "source_logical_claim_unit_id":
                    source_id,

                "target_logical_claim_unit_id":
                    target_id,

                "source_sentence_global_index":
                    source_index,

                "target_sentence_global_index":
                    target_index,

                "relation_type":
                    "CROSS_CLAIM_CONTRAST",

                "rejection_reason":
                    "CROSS_SECTION_CONTRAST_NOT_TENSION",

                "logical_tension_candidate_created":
                    False,
            })

            continue

        if (
            source_conditional
            or target_conditional
        ):
            rejected_contrast_candidates.append({
                "source_logical_claim_unit_id":
                    source_id,

                "target_logical_claim_unit_id":
                    target_id,

                "source_sentence_global_index":
                    source_index,

                "target_sentence_global_index":
                    target_index,

                "relation_type":
                    "CROSS_CLAIM_CONTRAST",

                "source_has_explicit_condition":
                    source_conditional,

                "target_has_explicit_condition":
                    target_conditional,

                "rejection_reason":
                    "CONDITIONAL_SCENARIO_CONTRAST_NOT_TENSION",

                "logical_tension_candidate_created":
                    False,
            })

            continue

        source_qualifications = list(
            qualifications_by_sentence.get(
                source_index,
                [],
            )
        )

        target_qualifications = list(
            qualifications_by_sentence.get(
                target_index,
                [],
            )
        )

        mapping_id = relation.get(
            "support_clarification_contrast_mapping_id"
        )

        if not mapping_id:
            raise LogicalIntelligenceError(
                "Finalized J contrast has no mapping ID."
            )

        material = (
            str(
                logical_chain_result.get(
                    "article_id"
                )
                or ""
            )
            + "|"
            + str(mapping_id)
            + "|QUALIFIED_INTERPRETIVE_TENSION"
        )

        tension_id = (
            "logical_tension_"
            + hashlib.sha256(
                material.encode(
                    "utf-8"
                )
            ).hexdigest()[:16]
        )

        tension_candidates.append({
            "logical_tension_candidate_id":
                tension_id,

            "source_logical_claim_unit_id":
                source_id,

            "target_logical_claim_unit_id":
                target_id,

            "source_sentence_global_index":
                source_index,

            "target_sentence_global_index":
                target_index,

            "section_id":
                source_section,

            "tension_type":
                "QUALIFIED_INTERPRETIVE_TENSION",

            "source_text":
                source_unit.get(
                    "text"
                ),

            "target_text":
                target_unit.get(
                    "text"
                ),

            "source_qualification_kinds": [
                mapping.get(
                    "qualification_kind"
                )
                for mapping in source_qualifications
            ],

            "target_qualification_kinds": [
                mapping.get(
                    "qualification_kind"
                )
                for mapping in target_qualifications
            ],

            "source_contrast_mapping_id":
                mapping_id,

            "same_section":
                True,

            "explicit_finalized_contrast":
                True,

            "competing_interpretations":
                True,

            "qualified_compatibility_possible":
                True,

            "logical_tension_candidate":
                True,

            "contradiction_candidate":
                False,

            "contradiction_adjudicated":
                False,

            "truth_assessed":
                False,

            "causal_relation_inferred":
                False,

            "article_local_only":
                True,
        })

    tension_ids = [
        item.get(
            "logical_tension_candidate_id"
        )
        for item in tension_candidates
    ]

    if (
        len(tension_ids)
        != len(
            set(tension_ids)
        )
    ):
        raise LogicalIntelligenceError(
            "Duplicate logical-tension candidate IDs detected."
        )

    tension_ids_by_unit = {}

    for candidate in tension_candidates:
        candidate_id = candidate.get(
            "logical_tension_candidate_id"
        )

        for unit_id in (
            candidate.get(
                "source_logical_claim_unit_id"
            ),
            candidate.get(
                "target_logical_claim_unit_id"
            ),
        ):
            tension_ids_by_unit.setdefault(
                unit_id,
                [],
            ).append(
                candidate_id
            )

    updated_units = []

    for unit in source_units:
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
                "logical_chain_construction"
            )
            != "COMPLETE"
        ):
            raise LogicalIntelligenceError(
                "4.6.6K state must be COMPLETE "
                "before 4.6.6L."
            )

        if (
            state.get(
                "logical_tension_detection"
            )
            != "PENDING"
        ):
            raise LogicalIntelligenceError(
                "Logical-tension detection state "
                "was not PENDING."
            )

        state[
            "logical_tension_detection"
        ] = "COMPLETE"

        updated[
            "logical_analysis_state"
        ] = state

        unit_id = unit.get(
            "logical_claim_unit_id"
        )

        unit_tension_ids = list(
            tension_ids_by_unit.get(
                unit_id,
                [],
            )
        )

        updated[
            "logical_tension_context"
        ] = {
            "logical_tension_candidate_ids":
                unit_tension_ids,

            "participates_in_logical_tension_candidate":
                bool(
                    unit_tension_ids
                ),

            "logical_tension_detection_complete":
                True,

            "contradiction_adjudicated":
                False,

            "truth_assessed":
                False,
        }

        updated_units.append(
            updated
        )

    updated_units_by_id = {
        unit.get(
            "logical_claim_unit_id"
        ): unit
        for unit in updated_units
    }

    rebuilt_sections = []

    for section in (
        logical_chain_result.get(
            "logical_sections"
        )
        or []
    ):
        rebuilt = dict(
            section
        )

        section_id = rebuilt.get(
            "section_id"
        )

        section_units = [
            updated_units_by_id[
                unit.get(
                    "logical_claim_unit_id"
                )
            ]
            for unit in (
                section.get(
                    "logical_claim_units"
                )
                or []
            )
            if (
                unit.get(
                    "logical_claim_unit_id"
                )
                in updated_units_by_id
            )
        ]

        section_candidates = [
            candidate
            for candidate in tension_candidates
            if (
                candidate.get(
                    "section_id"
                )
                == section_id
            )
        ]

        rebuilt[
            "logical_claim_units"
        ] = section_units

        rebuilt[
            "logical_tension_candidate_count"
        ] = len(
            section_candidates
        )

        rebuilt[
            "logical_tension_candidate_ids"
        ] = [
            candidate.get(
                "logical_tension_candidate_id"
            )
            for candidate in section_candidates
        ]

        rebuilt_sections.append(
            rebuilt
        )

    boundaries = dict(
        logical_chain_result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "logical_tension_detection_performed"
    ] = True

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

    result = dict(
        logical_chain_result
    )

    result.update({
        "schema_version":
            "logical_tension_candidate_detection_result_v1",

        "patch":
            "4.6.6L",

        "status":
            "LOGICAL_TENSION_CANDIDATE_DETECTION_COMPLETE",

        "logical_claim_units":
            updated_units,

        "logical_sections":
            rebuilt_sections,

        "logical_tension_candidate_count":
            len(
                tension_candidates
            ),

        "logical_tension_candidates":
            tension_candidates,

        "rejected_finalized_contrast_candidate_count":
            len(
                rejected_contrast_candidates
            ),

        "rejected_finalized_contrast_candidates":
            rejected_contrast_candidates,

        "logical_tension_summary": {
            "finalized_cross_claim_contrasts_examined":
                (
                    len(
                        tension_candidates
                    )
                    + len(
                        rejected_contrast_candidates
                    )
                ),

            "logical_tension_candidate_count":
                len(
                    tension_candidates
                ),

            "rejected_contrast_candidate_count":
                len(
                    rejected_contrast_candidates
                ),

            "contradiction_candidates_created":
                0,

            "contradictions_adjudicated":
                0,

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
            "article_level_logical_consolidation",
    })

    return result


def consolidate_article_logic_v1(
    logical_tension_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Consolidate completed article-local Logical Intelligence
    outputs into one article-level logical profile.

    This stage summarizes and organizes already-completed A-L
    logical analysis only.

    It does NOT:
    - create new logical relations,
    - perform causal reasoning,
    - assess factual truth,
    - adjudicate contradictions,
    - use external authority,
    - perform linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        logical_tension_result,
        Mapping,
    ):
        raise LogicalIntelligenceError(
            "logical_tension_result must be a mapping."
        )

    if (
        logical_tension_result.get(
            "schema_version"
        )
        != "logical_tension_candidate_detection_result_v1"
    ):
        raise LogicalIntelligenceError(
            "4.6.6M requires "
            "logical_tension_candidate_detection_result_v1."
        )

    if (
        logical_tension_result.get(
            "status"
        )
        != "LOGICAL_TENSION_CANDIDATE_DETECTION_COMPLETE"
    ):
        raise LogicalIntelligenceError(
            "4.6.6L must be complete before "
            "article-level logical consolidation."
        )

    if (
        logical_tension_result.get(
            "phase"
        )
        != "4.6.6"
    ):
        raise LogicalIntelligenceError(
            "4.6.6M requires Phase 4.6.6 input."
        )

    source_units = list(
        logical_tension_result.get(
            "logical_claim_units"
        )
        or []
    )

    if not source_units:
        raise LogicalIntelligenceError(
            "Logical Claim Units are missing."
        )

    logical_sections = list(
        logical_tension_result.get(
            "logical_sections"
        )
        or []
    )

    premise_conclusion_mappings = list(
        logical_tension_result.get(
            "premise_conclusion_mappings"
        )
        or []
    )

    qualification_mappings = list(
        logical_tension_result.get(
            "qualification_mappings"
        )
        or []
    )

    exception_mappings = list(
        logical_tension_result.get(
            "exception_mappings"
        )
        or []
    )

    conditional_mappings = list(
        logical_tension_result.get(
            "conditional_mappings"
        )
        or []
    )

    intra_j_mappings = list(
        logical_tension_result.get(
            "intra_claim_support_clarification_contrast_mappings"
        )
        or []
    )

    cross_j_mappings = list(
        logical_tension_result.get(
            "cross_claim_support_clarification_contrast_mappings"
        )
        or []
    )

    finalized_chain_edges = list(
        logical_tension_result.get(
            "eligible_finalized_chain_edges"
        )
        or []
    )

    logical_chains = list(
        logical_tension_result.get(
            "logical_chains"
        )
        or []
    )

    tension_candidates = list(
        logical_tension_result.get(
            "logical_tension_candidates"
        )
        or []
    )

    rejected_tension_candidates = list(
        logical_tension_result.get(
            "rejected_finalized_contrast_candidates"
        )
        or []
    )

    relation_type_counts = {}

    for mapping in (
        intra_j_mappings
        + cross_j_mappings
    ):
        relation_type = mapping.get(
            "relation_type"
        )

        if not relation_type:
            continue

        relation_type_counts[
            relation_type
        ] = (
            relation_type_counts.get(
                relation_type,
                0,
            )
            + 1
        )

    qualification_kind_counts = {}

    for mapping in qualification_mappings:
        kind = mapping.get(
            "qualification_kind"
        )

        if not kind:
            continue

        qualification_kind_counts[
            kind
        ] = (
            qualification_kind_counts.get(
                kind,
                0,
            )
            + 1
        )

    tension_type_counts = {}

    for candidate in tension_candidates:
        tension_type = candidate.get(
            "tension_type"
        )

        if not tension_type:
            continue

        tension_type_counts[
            tension_type
        ] = (
            tension_type_counts.get(
                tension_type,
                0,
            )
            + 1
        )

    # ---------------------------------------------------------
    # Build section-level consolidated summaries.
    # ---------------------------------------------------------

    consolidated_sections = []

    for section in logical_sections:
        section_id = section.get(
            "section_id"
        )

        section_units = list(
            section.get(
                "logical_claim_units"
            )
            or []
        )

        sentence_indexes = {
            unit.get(
                "sentence_global_index"
            )
            for unit in section_units
            if isinstance(
                unit.get(
                    "sentence_global_index"
                ),
                int,
            )
        }

        section_premise = [
            item
            for item in premise_conclusion_mappings
            if item.get(
                "sentence_global_index"
            )
            in sentence_indexes
        ]

        section_qualifications = [
            item
            for item in qualification_mappings
            if item.get(
                "sentence_global_index"
            )
            in sentence_indexes
        ]

        section_exceptions = [
            item
            for item in exception_mappings
            if item.get(
                "sentence_global_index"
            )
            in sentence_indexes
        ]

        section_conditionals = [
            item
            for item in conditional_mappings
            if item.get(
                "sentence_global_index"
            )
            in sentence_indexes
        ]

        section_intra_j = [
            item
            for item in intra_j_mappings
            if item.get(
                "sentence_global_index"
            )
            in sentence_indexes
        ]

        section_cross_j = [
            item
            for item in cross_j_mappings
            if (
                item.get(
                    "source_sentence_global_index"
                )
                in sentence_indexes
                or item.get(
                    "target_sentence_global_index"
                )
                in sentence_indexes
            )
        ]

        section_chain_edges = [
            item
            for item in finalized_chain_edges
            if (
                item.get(
                    "source_sentence_global_index"
                )
                in sentence_indexes
                or item.get(
                    "target_sentence_global_index"
                )
                in sentence_indexes
            )
        ]

        section_chains = [
            item
            for item in logical_chains
            if section_id
            in (
                item.get(
                    "section_ids"
                )
                or []
            )
        ]

        section_tensions = [
            item
            for item in tension_candidates
            if item.get(
                "section_id"
            )
            == section_id
        ]

        consolidated_sections.append({
            "section_id":
                section_id,

            "section_title":
                section.get(
                    "section_title"
                ),

            "logical_claim_unit_count":
                len(
                    section_units
                ),

            "premise_conclusion_mapping_count":
                len(
                    section_premise
                ),

            "qualification_mapping_count":
                len(
                    section_qualifications
                ),

            "exception_mapping_count":
                len(
                    section_exceptions
                ),

            "conditional_mapping_count":
                len(
                    section_conditionals
                ),

            "intra_claim_support_clarification_contrast_mapping_count":
                len(
                    section_intra_j
                ),

            "cross_claim_support_clarification_contrast_mapping_count":
                len(
                    section_cross_j
                ),

            "eligible_finalized_chain_edge_count":
                len(
                    section_chain_edges
                ),

            "logical_chain_count":
                len(
                    section_chains
                ),

            "logical_tension_candidate_count":
                len(
                    section_tensions
                ),

            "logical_analysis_complete":
                all(
                    (
                        unit.get(
                            "logical_analysis_state"
                        )
                        or {}
                    ).get(
                        "logical_tension_detection"
                    )
                    == "COMPLETE"
                    for unit in section_units
                ),

            "article_local_only":
                True,
        })

    # ---------------------------------------------------------
    # Verify all A-L unit states are complete.
    # ---------------------------------------------------------

    required_state_fields = (
        "discourse_signal_interpretation",
        "adjacent_relation_detection",
        "non_adjacent_relation_detection",
        "premise_conclusion_mapping",
        "qualification_exception_mapping",
        "conditional_mapping",
        "support_clarification_contrast_mapping",
        "logical_chain_construction",
        "logical_tension_detection",
    )

    incomplete_units = []

    for unit in source_units:
        state = (
            unit.get(
                "logical_analysis_state"
            )
            or {}
        )

        missing = [
            field
            for field in required_state_fields
            if state.get(
                field
            )
            != "COMPLETE"
        ]

        if missing:
            incomplete_units.append({
                "logical_claim_unit_id":
                    unit.get(
                        "logical_claim_unit_id"
                    ),

                "sentence_global_index":
                    unit.get(
                        "sentence_global_index"
                    ),

                "incomplete_states":
                    missing,
            })

    all_a_to_l_complete = (
        len(
            incomplete_units
        )
        == 0
    )

    if not all_a_to_l_complete:
        raise LogicalIntelligenceError(
            "Cannot consolidate article logic: "
            "one or more A-L unit states are incomplete."
        )

    boundaries = dict(
        logical_tension_result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "article_level_logical_consolidation_performed"
    ] = True

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

    article_profile = {
        "article_id":
            logical_tension_result.get(
                "article_id"
            ),

        "workspace_id":
            logical_tension_result.get(
                "workspace_id"
            ),

        "source_type":
            logical_tension_result.get(
                "source_type"
            ),

        "source_id":
            logical_tension_result.get(
                "source_id"
            ),

        "document_id":
            logical_tension_result.get(
                "document_id"
            ),

        "content_hash":
            logical_tension_result.get(
                "content_hash"
            ),

        "title":
            logical_tension_result.get(
                "title"
            ),

        "logical_claim_unit_count":
            len(
                source_units
            ),

        "logical_section_count":
            len(
                logical_sections
            ),

        "premise_conclusion_mapping_count":
            len(
                premise_conclusion_mappings
            ),

        "qualification_mapping_count":
            len(
                qualification_mappings
            ),

        "exception_mapping_count":
            len(
                exception_mappings
            ),

        "conditional_mapping_count":
            len(
                conditional_mappings
            ),

        "intra_claim_support_clarification_contrast_mapping_count":
            len(
                intra_j_mappings
            ),

        "cross_claim_support_clarification_contrast_mapping_count":
            len(
                cross_j_mappings
            ),

        "relation_type_counts":
            relation_type_counts,

        "qualification_kind_counts":
            qualification_kind_counts,

        "eligible_finalized_chain_edge_count":
            len(
                finalized_chain_edges
            ),

        "logical_chain_count":
            len(
                logical_chains
            ),

        "logical_tension_candidate_count":
            len(
                tension_candidates
            ),

        "logical_tension_type_counts":
            tension_type_counts,

        "rejected_tension_candidate_count":
            len(
                rejected_tension_candidates
            ),

        "contradiction_candidate_count":
            0,

        "contradiction_verdict_count":
            0,

        "truth_assessment_performed":
            False,

        "causal_reasoning_performed":
            False,

        "external_authority_check_performed":
            False,

        "all_a_to_l_logical_states_complete":
            True,

        "article_local_only":
            True,
    }

    result = dict(
        logical_tension_result
    )

    result.update({
        "schema_version":
            "article_level_logical_consolidation_result_v1",

        "patch":
            "4.6.6M",

        "status":
            "ARTICLE_LEVEL_LOGICAL_CONSOLIDATION_COMPLETE",

        "article_logical_profile":
            article_profile,

        "consolidated_logical_sections":
            consolidated_sections,

        "logical_consolidation_summary": {
            "logical_claim_unit_count":
                len(
                    source_units
                ),

            "logical_section_count":
                len(
                    logical_sections
                ),

            "premise_conclusion_mapping_count":
                len(
                    premise_conclusion_mappings
                ),

            "qualification_mapping_count":
                len(
                    qualification_mappings
                ),

            "exception_mapping_count":
                len(
                    exception_mappings
                ),

            "conditional_mapping_count":
                len(
                    conditional_mappings
                ),

            "intra_claim_support_clarification_contrast_mapping_count":
                len(
                    intra_j_mappings
                ),

            "cross_claim_support_clarification_contrast_mapping_count":
                len(
                    cross_j_mappings
                ),

            "eligible_finalized_chain_edge_count":
                len(
                    finalized_chain_edges
                ),

            "logical_chain_count":
                len(
                    logical_chains
                ),

            "logical_tension_candidate_count":
                len(
                    tension_candidates
                ),

            "contradiction_candidate_count":
                0,

            "contradiction_verdict_count":
                0,

            "all_a_to_l_logical_states_complete":
                True,

            "new_logical_inference_created":
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
            "final_logical_intelligence_result",
    })

    return result


def build_final_logical_intelligence_result_v1(
    article_logical_consolidation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build the canonical final Phase 4.6.6 Logical Intelligence
    result from the already-completed article-level consolidation.

    This stage performs packaging only.

    It does NOT:
    - create new logical relations,
    - alter any finalized mapping,
    - infer causation,
    - assess factual truth,
    - adjudicate contradictions,
    - use external authority,
    - perform linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        article_logical_consolidation_result,
        Mapping,
    ):
        raise LogicalIntelligenceError(
            "article_logical_consolidation_result "
            "must be a mapping."
        )

    if (
        article_logical_consolidation_result.get(
            "schema_version"
        )
        != "article_level_logical_consolidation_result_v1"
    ):
        raise LogicalIntelligenceError(
            "4.6.6N requires "
            "article_level_logical_consolidation_result_v1."
        )

    if (
        article_logical_consolidation_result.get(
            "status"
        )
        != "ARTICLE_LEVEL_LOGICAL_CONSOLIDATION_COMPLETE"
    ):
        raise LogicalIntelligenceError(
            "4.6.6M must be complete before "
            "building the final Logical Intelligence result."
        )

    if (
        article_logical_consolidation_result.get(
            "phase"
        )
        != "4.6.6"
    ):
        raise LogicalIntelligenceError(
            "4.6.6N requires Phase 4.6.6 input."
        )

    article_profile = dict(
        article_logical_consolidation_result.get(
            "article_logical_profile"
        )
        or {}
    )

    consolidation_summary = dict(
        article_logical_consolidation_result.get(
            "logical_consolidation_summary"
        )
        or {}
    )

    consolidated_sections = list(
        article_logical_consolidation_result.get(
            "consolidated_logical_sections"
        )
        or []
    )

    logical_claim_units = list(
        article_logical_consolidation_result.get(
            "logical_claim_units"
        )
        or []
    )

    if not article_profile:
        raise LogicalIntelligenceError(
            "Article logical profile is missing."
        )

    if not consolidation_summary:
        raise LogicalIntelligenceError(
            "Logical consolidation summary is missing."
        )

    if not consolidated_sections:
        raise LogicalIntelligenceError(
            "Consolidated logical sections are missing."
        )

    if not logical_claim_units:
        raise LogicalIntelligenceError(
            "Logical Claim Units are missing."
        )

    if (
        article_profile.get(
            "all_a_to_l_logical_states_complete"
        )
        is not True
    ):
        raise LogicalIntelligenceError(
            "Cannot build final Logical Intelligence result: "
            "A-L logical states are not complete."
        )

    if (
        consolidation_summary.get(
            "all_a_to_l_logical_states_complete"
        )
        is not True
    ):
        raise LogicalIntelligenceError(
            "Consolidation summary does not confirm "
            "A-L completion."
        )

    if (
        consolidation_summary.get(
            "new_logical_inference_created"
        )
        is not False
    ):
        raise LogicalIntelligenceError(
            "Final packaging cannot consume a consolidation "
            "that created new logical inference."
        )

    boundaries = dict(
        article_logical_consolidation_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "article_level_logical_consolidation_performed"
        )
        is not True
    ):
        raise LogicalIntelligenceError(
            "Article-level logical consolidation boundary "
            "is not complete."
        )

    forbidden_boundary_fields = (
        "causal_reasoning_performed",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for field in forbidden_boundary_fields:
        if boundaries.get(
            field
        ) is not False:
            raise LogicalIntelligenceError(
                "Forbidden work detected before final "
                "Logical Intelligence packaging: "
                + field
            )

    boundaries[
        "final_logical_intelligence_result_built"
    ] = True

    boundaries[
        "logical_intelligence_certification_performed"
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

    final_summary = {
        "logical_claim_unit_count":
            article_profile.get(
                "logical_claim_unit_count"
            ),

        "logical_section_count":
            article_profile.get(
                "logical_section_count"
            ),

        "premise_conclusion_mapping_count":
            article_profile.get(
                "premise_conclusion_mapping_count"
            ),

        "qualification_mapping_count":
            article_profile.get(
                "qualification_mapping_count"
            ),

        "exception_mapping_count":
            article_profile.get(
                "exception_mapping_count"
            ),

        "conditional_mapping_count":
            article_profile.get(
                "conditional_mapping_count"
            ),

        "intra_claim_support_clarification_contrast_mapping_count":
            article_profile.get(
                "intra_claim_support_clarification_contrast_mapping_count"
            ),

        "cross_claim_support_clarification_contrast_mapping_count":
            article_profile.get(
                "cross_claim_support_clarification_contrast_mapping_count"
            ),

        "eligible_finalized_chain_edge_count":
            article_profile.get(
                "eligible_finalized_chain_edge_count"
            ),

        "logical_chain_count":
            article_profile.get(
                "logical_chain_count"
            ),

        "logical_tension_candidate_count":
            article_profile.get(
                "logical_tension_candidate_count"
            ),

        "rejected_tension_candidate_count":
            article_profile.get(
                "rejected_tension_candidate_count"
            ),

        "contradiction_candidate_count":
            article_profile.get(
                "contradiction_candidate_count"
            ),

        "contradiction_verdict_count":
            article_profile.get(
                "contradiction_verdict_count"
            ),

        "all_logical_analysis_complete":
            True,

        "new_logical_inference_created":
            False,

        "causal_reasoning_performed":
            False,

        "truth_assessment_performed":
            False,

        "external_authority_check_performed":
            False,

        "semantic_memory_write_performed":
            False,

        "persistence_performed":
            False,

        "article_local_only":
            True,
    }

    result = dict(
        article_logical_consolidation_result
    )

    result.update({
        "schema_version":
            "logical_intelligence_result_v1",

        "logical_intelligence_version":
            LOGICAL_INTELLIGENCE_VERSION,

        "patch":
            "4.6.6N",

        "status":
            "LOGICAL_INTELLIGENCE_RESULT_COMPLETE",

        "article_logical_profile":
            article_profile,

        "consolidated_logical_sections":
            consolidated_sections,

        "logical_claim_units":
            logical_claim_units,

        "premise_conclusion_mappings":
            list(
                article_logical_consolidation_result.get(
                    "premise_conclusion_mappings"
                )
                or []
            ),

        "qualification_mappings":
            list(
                article_logical_consolidation_result.get(
                    "qualification_mappings"
                )
                or []
            ),

        "exception_mappings":
            list(
                article_logical_consolidation_result.get(
                    "exception_mappings"
                )
                or []
            ),

        "conditional_mappings":
            list(
                article_logical_consolidation_result.get(
                    "conditional_mappings"
                )
                or []
            ),

        "intra_claim_support_clarification_contrast_mappings":
            list(
                article_logical_consolidation_result.get(
                    "intra_claim_support_clarification_contrast_mappings"
                )
                or []
            ),

        "cross_claim_support_clarification_contrast_mappings":
            list(
                article_logical_consolidation_result.get(
                    "cross_claim_support_clarification_contrast_mappings"
                )
                or []
            ),

        "eligible_finalized_chain_edges":
            list(
                article_logical_consolidation_result.get(
                    "eligible_finalized_chain_edges"
                )
                or []
            ),

        "logical_chains":
            list(
                article_logical_consolidation_result.get(
                    "logical_chains"
                )
                or []
            ),

        "logical_tension_candidates":
            list(
                article_logical_consolidation_result.get(
                    "logical_tension_candidates"
                )
                or []
            ),

        "rejected_finalized_contrast_candidates":
            list(
                article_logical_consolidation_result.get(
                    "rejected_finalized_contrast_candidates"
                )
                or []
            ),

        "logical_consolidation_summary":
            consolidation_summary,

        "final_logical_summary":
            final_summary,

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "logical_intelligence_certification",
    })

    return result


def certify_logical_intelligence_v1(
    final_logical_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Certify the canonical final Phase 4.6.6 Logical Intelligence result.

    Certification validates the already-produced result only.

    It does NOT:
    - create or alter logical relations,
    - infer causation,
    - assess factual truth,
    - adjudicate contradictions,
    - use external authority,
    - perform linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        final_logical_result,
        Mapping,
    ):
        raise LogicalIntelligenceError(
            "final_logical_result must be a mapping."
        )

    checks = []

    def record_check(
        name: str,
        passed: bool,
        detail: str,
    ) -> None:
        checks.append({
            "check":
                name,
            "passed":
                bool(passed),
            "detail":
                detail,
        })

    schema_valid = (
        final_logical_result.get(
            "schema_version"
        )
        == "logical_intelligence_result_v1"
    )

    record_check(
        "schema_version",
        schema_valid,
        "Final schema must be logical_intelligence_result_v1.",
    )

    version_valid = (
        final_logical_result.get(
            "logical_intelligence_version"
        )
        == LOGICAL_INTELLIGENCE_VERSION
    )

    record_check(
        "logical_intelligence_version",
        version_valid,
        "Logical Intelligence version must match canonical version.",
    )

    phase_valid = (
        final_logical_result.get(
            "phase"
        )
        == "4.6.6"
    )

    record_check(
        "phase",
        phase_valid,
        "Final result must remain Phase 4.6.6.",
    )

    patch_valid = (
        final_logical_result.get(
            "patch"
        )
        == "4.6.6N"
    )

    record_check(
        "final_result_patch",
        patch_valid,
        "Certification input must be the certified N-stage result.",
    )

    status_valid = (
        final_logical_result.get(
            "status"
        )
        == "LOGICAL_INTELLIGENCE_RESULT_COMPLETE"
    )

    record_check(
        "final_result_status",
        status_valid,
        "Final Logical Intelligence result must be complete.",
    )

    next_stage_valid = (
        final_logical_result.get(
            "next_stage"
        )
        == "logical_intelligence_certification"
    )

    record_check(
        "certification_handoff",
        next_stage_valid,
        "N must hand off directly to Logical Intelligence certification.",
    )

    persistence_valid = (
        final_logical_result.get(
            "persistence_policy"
        )
        == "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    )

    record_check(
        "persistence_policy",
        persistence_valid,
        "Logical Intelligence must remain article-local transient intelligence.",
    )

    profile = dict(
        final_logical_result.get(
            "article_logical_profile"
        )
        or {}
    )

    summary = dict(
        final_logical_result.get(
            "final_logical_summary"
        )
        or {}
    )

    consolidation_summary = dict(
        final_logical_result.get(
            "logical_consolidation_summary"
        )
        or {}
    )

    logical_units = list(
        final_logical_result.get(
            "logical_claim_units"
        )
        or []
    )

    logical_sections = list(
        final_logical_result.get(
            "consolidated_logical_sections"
        )
        or []
    )

    profile_present = bool(
        profile
    )

    summary_present = bool(
        summary
    )

    consolidation_summary_present = bool(
        consolidation_summary
    )

    units_present = bool(
        logical_units
    )

    sections_present = bool(
        logical_sections
    )

    record_check(
        "article_logical_profile_present",
        profile_present,
        "Article logical profile must be present.",
    )

    record_check(
        "final_logical_summary_present",
        summary_present,
        "Final logical summary must be present.",
    )

    record_check(
        "logical_consolidation_summary_present",
        consolidation_summary_present,
        "Logical consolidation summary must be preserved.",
    )

    record_check(
        "logical_claim_units_present",
        units_present,
        "Logical Claim Units must be present.",
    )

    record_check(
        "logical_sections_present",
        sections_present,
        "Consolidated logical sections must be present.",
    )

    profile_count_matches = (
        profile.get(
            "logical_claim_unit_count"
        )
        == len(
            logical_units
        )
    )

    record_check(
        "profile_claim_count_matches_units",
        profile_count_matches,
        "Profile claim-unit count must equal packaged Logical Claim Units.",
    )

    profile_section_count_matches = (
        profile.get(
            "logical_section_count"
        )
        == len(
            logical_sections
        )
    )

    record_check(
        "profile_section_count_matches_sections",
        profile_section_count_matches,
        "Profile section count must equal consolidated logical sections.",
    )

    artifact_count_pairs = (
        (
            "premise_conclusion_mapping_count",
            "premise_conclusion_mappings",
        ),
        (
            "qualification_mapping_count",
            "qualification_mappings",
        ),
        (
            "exception_mapping_count",
            "exception_mappings",
        ),
        (
            "conditional_mapping_count",
            "conditional_mappings",
        ),
        (
            "intra_claim_support_clarification_contrast_mapping_count",
            "intra_claim_support_clarification_contrast_mappings",
        ),
        (
            "cross_claim_support_clarification_contrast_mapping_count",
            "cross_claim_support_clarification_contrast_mappings",
        ),
        (
            "eligible_finalized_chain_edge_count",
            "eligible_finalized_chain_edges",
        ),
        (
            "logical_chain_count",
            "logical_chains",
        ),
        (
            "logical_tension_candidate_count",
            "logical_tension_candidates",
        ),
        (
            "rejected_tension_candidate_count",
            "rejected_finalized_contrast_candidates",
        ),
    )

    artifact_counts_consistent = True

    for profile_key, artifact_key in artifact_count_pairs:
        expected = profile.get(
            profile_key
        )

        actual = len(
            final_logical_result.get(
                artifact_key
            )
            or []
        )

        pair_valid = (
            expected
            == actual
        )

        if not pair_valid:
            artifact_counts_consistent = False

        record_check(
            "artifact_count_"
            + artifact_key,
            pair_valid,
            (
                profile_key
                + "="
                + str(expected)
                + ", packaged="
                + str(actual)
            ),
        )

    summary_profile_fields = (
        "logical_claim_unit_count",
        "logical_section_count",
        "premise_conclusion_mapping_count",
        "qualification_mapping_count",
        "exception_mapping_count",
        "conditional_mapping_count",
        "intra_claim_support_clarification_contrast_mapping_count",
        "cross_claim_support_clarification_contrast_mapping_count",
        "eligible_finalized_chain_edge_count",
        "logical_chain_count",
        "logical_tension_candidate_count",
        "rejected_tension_candidate_count",
        "contradiction_candidate_count",
        "contradiction_verdict_count",
    )

    summary_matches_profile = all(
        summary.get(
            field
        )
        == profile.get(
            field
        )
        for field in summary_profile_fields
    )

    record_check(
        "summary_matches_article_profile",
        summary_matches_profile,
        "Final logical summary counts must match article logical profile.",
    )

    consolidation_matches_profile = all(
        consolidation_summary.get(
            field
        )
        == profile.get(
            field
        )
        for field in (
            "logical_claim_unit_count",
            "logical_section_count",
            "premise_conclusion_mapping_count",
            "qualification_mapping_count",
            "exception_mapping_count",
            "conditional_mapping_count",
            "intra_claim_support_clarification_contrast_mapping_count",
            "cross_claim_support_clarification_contrast_mapping_count",
            "eligible_finalized_chain_edge_count",
            "logical_chain_count",
            "logical_tension_candidate_count",
            "contradiction_candidate_count",
            "contradiction_verdict_count",
        )
    )

    record_check(
        "consolidation_matches_article_profile",
        consolidation_matches_profile,
        "M consolidation counts must match the final article logical profile.",
    )

    all_unit_states_complete = all(
        (
            unit.get(
                "logical_analysis_state"
            )
            or {}
        ).get(
            "logical_tension_detection"
        )
        == "COMPLETE"
        for unit in logical_units
    )

    record_check(
        "all_logical_unit_states_complete",
        all_unit_states_complete,
        "Every Logical Claim Unit must have completed logical-tension detection.",
    )

    all_sections_complete = all(
        section.get(
            "logical_analysis_complete"
        )
        is True
        for section in logical_sections
    )

    record_check(
        "all_logical_sections_complete",
        all_sections_complete,
        "Every consolidated logical section must be complete.",
    )

    article_local_valid = all([
        profile.get(
            "article_local_only"
        ) is True,

        summary.get(
            "article_local_only"
        ) is True,

        consolidation_summary.get(
            "article_local_only"
        ) is True,

        all(
            (
                unit.get(
                    "logical_tension_context"
                )
                or {}
            ).get(
                "truth_assessed"
            )
            is False
            for unit in logical_units
        ),
    ])

    record_check(
        "article_local_boundary",
        article_local_valid,
        "Logical Intelligence must remain article-local.",
    )

    no_new_inference = all([
        summary.get(
            "new_logical_inference_created"
        ) is False,

        consolidation_summary.get(
            "new_logical_inference_created"
        ) is False,
    ])

    record_check(
        "no_new_logical_inference_in_packaging",
        no_new_inference,
        "M and N must not create new logical inference.",
    )

    no_contradiction_verdict = (
        profile.get(
            "contradiction_verdict_count"
        )
        == 0
        and summary.get(
            "contradiction_verdict_count"
        )
        == 0
    )

    record_check(
        "no_contradiction_verdict",
        no_contradiction_verdict,
        "4.6.6 must not adjudicate factual contradiction.",
    )

    boundaries = dict(
        final_logical_result.get(
            "processing_boundaries"
        )
        or {}
    )

    upstream_boundaries_valid = all([
        boundaries.get(
            "logical_chain_construction_performed"
        ) is True,

        boundaries.get(
            "logical_tension_detection_performed"
        ) is True,

        boundaries.get(
            "article_level_logical_consolidation_performed"
        ) is True,

        boundaries.get(
            "final_logical_intelligence_result_built"
        ) is True,

        boundaries.get(
            "logical_intelligence_certification_performed"
        ) is False,
    ])

    record_check(
        "upstream_logical_boundaries",
        upstream_boundaries_valid,
        "K, L, M and N boundaries must be complete before O.",
    )

    forbidden_boundary_fields = (
        "causal_reasoning_performed",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    forbidden_work_absent = all(
        boundaries.get(
            field
        )
        is False
        for field in forbidden_boundary_fields
    )

    record_check(
        "forbidden_work_absent",
        forbidden_work_absent,
        "No causal, truth, authority, memory or persistence work may occur.",
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

    identity_preserved = all(
        profile.get(
            field
        )
        == final_logical_result.get(
            field
        )
        for field in identity_fields
    )

    record_check(
        "identity_preserved",
        identity_preserved,
        "Final article identity must match article logical profile identity.",
    )

    failed_checks = [
        check
        for check in checks
        if check.get(
            "passed"
        )
        is not True
    ]

    certified = (
        len(
            failed_checks
        )
        == 0
    )

    certification_status = (
        "CERTIFIED"
        if certified
        else "CERTIFICATION_FAILED"
    )

    certification_result = {
        "schema_version":
            "logical_intelligence_certification_v1",

        "phase":
            "4.6.6",

        "logical_intelligence_version":
            LOGICAL_INTELLIGENCE_VERSION,

        "certification_status":
            certification_status,

        "certified":
            certified,

        "check_count":
            len(
                checks
            ),

        "passed_check_count":
            len(
                checks
            )
            - len(
                failed_checks
            ),

        "failed_check_count":
            len(
                failed_checks
            ),

        "checks":
            checks,

        "failed_checks":
            failed_checks,

        "article_id":
            final_logical_result.get(
                "article_id"
            ),

        "workspace_id":
            final_logical_result.get(
                "workspace_id"
            ),

        "source_type":
            final_logical_result.get(
                "source_type"
            ),

        "source_id":
            final_logical_result.get(
                "source_id"
            ),

        "document_id":
            final_logical_result.get(
                "document_id"
            ),

        "content_hash":
            final_logical_result.get(
                "content_hash"
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
    }

    if not certified:
        return certification_result

    certified_boundaries = dict(
        boundaries
    )

    certified_boundaries[
        "logical_intelligence_certification_performed"
    ] = True

    certified_result = dict(
        final_logical_result
    )

    certified_result.update({
        "schema_version":
            "certified_logical_intelligence_result_v1",

        "patch":
            "4.6.6O",

        "status":
            "LOGICAL_INTELLIGENCE_CERTIFIED",

        "logical_intelligence_certification":
            certification_result,

        "processing_boundaries":
            certified_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "relational_intelligence",
    })

    return certified_result


__all__ = [
    "LOGICAL_INTELLIGENCE_VERSION",
    "LogicalIntelligenceError",
    "validate_logical_intelligence_intake_v1",
    "build_logical_claim_units_v1",
    "interpret_discourse_signals_v1",
    "detect_adjacent_claim_relations_v1",
    "detect_non_adjacent_same_section_relations_v1",
    "map_premise_conclusion_v1",
    "map_qualification_exception_v1",
    "map_conditional_logic_v1",
    "map_support_clarification_contrast_v1",
    "construct_logical_chains_v1",
    "detect_logical_tension_candidates_v1",
    "consolidate_article_logic_v1",
    "build_final_logical_intelligence_result_v1",
    "certify_logical_intelligence_v1",
]

