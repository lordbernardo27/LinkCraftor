"""Phase 4 - Canonical Original Scorer document contract.

CMS-neutral structural validation foundation.
Does not score phrases, modify documents, or authorize linking.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import re
from typing import Any


SCORER_DOCUMENT_CONTRACT_VERSION = (
    "linkcraftor_scorer_document_v1"
)

SUPPORTED_FORMATS = frozenset({
    "docx", "txt", "md", "markdown", "html", "htm"
})

EXCLUDED_REGION_TYPES = frozenset({
    "title",
    "heading",
    "faq",
    "references",
    "bibliography",
    "image",
    "caption",
    "gallery",
    "navigation",
    "sidebar",
    "footer",
    "author_bio",
    "table",
    "code",
    "widget",
    "form",
    "button",
    "cta",
    "promotional",
    "related_posts",
    "unknown",
})


class ScorerDocumentContractError(ValueError):
    """Document evidence is insufficient or inconsistent."""


def _required_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ScorerDocumentContractError(
            f"{field} must be a nonempty string"
        )
    return value.strip()


def validate_scorer_document_contract(
    document: dict[str, Any],
) -> dict[str, Any]:
    """Validate structural evidence without inventing missing data.

    This validates records supplied by trusted format adapters.
    It does not certify that an adapter's assertions are truthful;
    source-to-document verification is required downstream.
    """
    if not isinstance(document, dict):
        raise ScorerDocumentContractError(
            "document must be a dictionary"
        )

    if document.get("schema_version") != (
        SCORER_DOCUMENT_CONTRACT_VERSION
    ):
        raise ScorerDocumentContractError(
            "unsupported document contract version"
        )

    for field in (
        "workspace_id",
        "document_id",
        "content_version",
    ):
        _required_string(document.get(field), field)

    fingerprint = _required_string(
        document.get("content_sha256"),
        "content_sha256",
    )
    if not re.fullmatch(r"[0-9a-fA-F]{64}", fingerprint):
        raise ScorerDocumentContractError(
            "content_sha256 must be a SHA256 hexadecimal digest"
        )

    canonical_text = document.get("canonical_text")

    if not isinstance(canonical_text, str):
        raise ScorerDocumentContractError(
            "canonical_text must be a string"
        )

    actual_hash = hashlib.sha256(
        canonical_text.encode("utf-8")
    ).hexdigest()

    if actual_hash != fingerprint.lower():
        raise ScorerDocumentContractError(
            "canonical article fingerprint mismatch"
        )

    source_format = _required_string(
        document.get("source_format"),
        "source_format",
    ).lower().lstrip(".")

    if source_format not in SUPPORTED_FORMATS:
        raise ScorerDocumentContractError(
            "unsupported document format"
        )

    if document.get("structure_complete") is not True:
        raise ScorerDocumentContractError(
            "verified document structure is required"
        )

    regions = document.get("regions")
    if not isinstance(regions, list):
        raise ScorerDocumentContractError(
            "regions must be an explicit list"
        )

    seen_ids = set()
    eligible_spans = []
    eligible_word_count = 0

    for index, region in enumerate(regions):
        if not isinstance(region, dict):
            raise ScorerDocumentContractError(
                f"region {index} must be a dictionary"
            )

        region_id = _required_string(
            region.get("region_id"),
            f"region {index} region_id",
        )

        if region_id in seen_ids:
            raise ScorerDocumentContractError(
                "duplicate region_id"
            )
        seen_ids.add(region_id)

        region_type = _required_string(
            region.get("region_type"),
            f"region {index} region_type",
        ).lower()

        eligible = region.get("eligible_for_linking")

        if type(eligible) is not bool:
            raise ScorerDocumentContractError(
                "region eligibility must be explicit"
            )

        if eligible:
            if region_type != "body_paragraph":
                raise ScorerDocumentContractError(
                    "only verified body paragraphs may be eligible"
                )

            if region.get("source_mapping_verified") is not True:
                raise ScorerDocumentContractError(
                    "eligible paragraph lacks verified source mapping"
                )

            word_count = region.get("word_count")
            if type(word_count) is not int or word_count < 0:
                raise ScorerDocumentContractError(
                    "eligible paragraph requires valid word_count"
                )

            start = region.get("char_start")
            end = region.get("char_end")
            region_text = region.get("text")

            if (
                type(start) is not int
                or type(end) is not int
                or not 0 <= start < end <= len(canonical_text)
            ):
                raise ScorerDocumentContractError(
                    "invalid eligible paragraph offsets"
                )

            if (
                not isinstance(region_text, str)
                or canonical_text[start:end] != region_text
            ):
                raise ScorerDocumentContractError(
                    "eligible paragraph text/span mismatch"
                )

            if len(region_text.split()) != word_count:
                raise ScorerDocumentContractError(
                    "eligible paragraph word count mismatch"
                )

            for previous_start, previous_end in eligible_spans:
                if start < previous_end and previous_start < end:
                    raise ScorerDocumentContractError(
                        "overlapping eligible paragraph spans"
                    )

            eligible_spans.append((start, end))

            section_id = _required_string(
                region.get("section_id"),
                "eligible paragraph section_id",
            )

            _required_string(
                region.get("source_node_id"),
                "eligible paragraph source_node_id",
            )

            # Trusted format adapters must supply the complete
            # structural lineage, from article body to this section.
            # An unverified or protected ancestor blocks placement.
            lineage = region.get("section_lineage")
            if not isinstance(lineage, list) or not lineage:
                raise ScorerDocumentContractError(
                    "eligible paragraph requires section lineage"
                )

            allowed_sections = {
                "article_body",
                "editorial_section",
                "subsection",
            }
            lineage_ids = set()

            for depth, ancestor in enumerate(lineage):
                if not isinstance(ancestor, dict):
                    raise ScorerDocumentContractError(
                        "invalid section lineage record"
                    )

                ancestor_id = _required_string(
                    ancestor.get("section_id"),
                    "ancestor section_id",
                )
                ancestor_type = _required_string(
                    ancestor.get("section_type"),
                    "ancestor section_type",
                ).lower()

                if ancestor_id in lineage_ids:
                    raise ScorerDocumentContractError(
                        "repeated section ancestor"
                    )
                lineage_ids.add(ancestor_id)

                if depth == 0 and ancestor_type != "article_body":
                    raise ScorerDocumentContractError(
                        "section lineage must start at article body"
                    )

                if ancestor_type not in allowed_sections:
                    raise ScorerDocumentContractError(
                        "protected or unknown section ancestor"
                    )

            if lineage[-1]["section_id"] != section_id:
                raise ScorerDocumentContractError(
                    "section lineage does not match paragraph"
                )

            eligible_word_count += word_count

        elif region_type in EXCLUDED_REGION_TYPES:
            pass

    # Protected spans are independent of paragraph eligibility.
    # An existing hyperlink does not disqualify its whole paragraph.
    protected = document.get("protected_spans")

    if document.get("protected_spans_complete") is not True:
        raise ScorerDocumentContractError(
            "verified protected-span inventory required"
        )

    if not isinstance(protected, list):
        raise ScorerDocumentContractError(
            "protected_spans must be an explicit list"
        )

    protected_ids = set()
    protected_ranges = []

    for index, span in enumerate(protected):
        if not isinstance(span, dict):
            raise ScorerDocumentContractError(
                "invalid protected-span record"
            )

        span_id = _required_string(
            span.get("span_id"),
            "protected span_id",
        )

        if span_id in protected_ids:
            raise ScorerDocumentContractError(
                "duplicate protected span_id"
            )
        protected_ids.add(span_id)

        kind = _required_string(
            span.get("kind"),
            "protected span kind",
        ).lower()

        if kind not in {
            "hyperlink",
            "image",
            "code",
            "other_protected",
        }:
            raise ScorerDocumentContractError(
                "unknown protected span kind"
            )

        start = span.get("char_start")
        end = span.get("char_end")
        span_text = span.get("text")

        if (
            type(start) is not int
            or type(end) is not int
            or not 0 <= start < end <= len(canonical_text)
        ):
            raise ScorerDocumentContractError(
                "invalid protected span offsets"
            )

        if (
            not isinstance(span_text, str)
            or canonical_text[start:end] != span_text
        ):
            raise ScorerDocumentContractError(
                "protected span text mismatch"
            )

        _required_string(
            span.get("source_node_id"),
            "protected span source_node_id",
        )

        if kind == "hyperlink":
            _required_string(
                span.get("destination"),
                "hyperlink destination",
            )

        for previous_start, previous_end in protected_ranges:
            if start < previous_end and previous_start < end:
                raise ScorerDocumentContractError(
                    "overlapping protected spans"
                )

        protected_ranges.append((start, end))

    supplied_count = document.get("eligible_body_word_count")

    if (
        type(supplied_count) is not int
        or supplied_count != eligible_word_count
    ):
        raise ScorerDocumentContractError(
            "eligible-body word count mismatch"
        )

    result = deepcopy(document)
    result["source_format"] = source_format
    result["validation_status"] = (
        "structural_contract_validated"
    )
    result["automatic_linking_authorized"] = False
    result["scorer_decision_performed"] = False

    return result
