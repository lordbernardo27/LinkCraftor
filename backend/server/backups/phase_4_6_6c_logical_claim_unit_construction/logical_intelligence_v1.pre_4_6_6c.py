from __future__ import annotations

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


__all__ = [
    "LOGICAL_INTELLIGENCE_VERSION",
    "LogicalIntelligenceError",
    "validate_logical_intelligence_intake_v1",
]
