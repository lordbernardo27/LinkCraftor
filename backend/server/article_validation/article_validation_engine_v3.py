"""Canonical Article Validation Engine v3.

This engine consumes only integrity-certified UDARE article content.

It performs no writes and returns metadata-only validation results.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any, Sequence


ARTICLE_VALIDATION_ENGINE_VERSION = (
    "article_validation_engine_v3_certified_non_mutating_contextual_structure"
)

MINIMUM_PRINTABLE_RATIO = 0.98
MAXIMUM_REPLACEMENT_CHARACTER_RATIO = 0.001


def _normalize_text(
    value: Any,
) -> str:
    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


def _valid_sha256(
    value: Any,
) -> bool:
    return bool(
        re.fullmatch(
            r"[0-9a-fA-F]{64}",
            str(value or "").strip(),
        )
    )


def _paragraphs(
    article_text: str,
) -> list[str]:
    return [
        paragraph.strip()
        for paragraph in str(
            article_text or ""
        ).split("\n\n")
        if paragraph.strip()
    ]


def _duplicate_paragraph_ratio(
    paragraphs: Sequence[str],
) -> float:
    normalized = [
        _normalize_text(
            paragraph
        ).casefold()
        for paragraph in paragraphs
        if len(
            _normalize_text(
                paragraph
            )
        )
        >= 20
    ]

    if not normalized:
        return 0.0

    unique_count = len(
        set(normalized)
    )

    duplicate_count = (
        len(normalized)
        - unique_count
    )

    return (
        duplicate_count
        / len(normalized)
    )


def _printable_ratio(
    article_text: str,
) -> float:
    if not article_text:
        return 1.0

    printable_count = sum(
        1
        for character in article_text
        if (
            character.isprintable()
            or character in "\n\r\t"
        )
    )

    return (
        printable_count
        / len(article_text)
    )


def _replacement_character_ratio(
    article_text: str,
) -> float:
    if not article_text:
        return 0.0

    return (
        article_text.count("\ufffd")
        / len(article_text)
    )


class _CertifiedHTMLExtractor(
    HTMLParser
):
    """Extract article text without modifying the certified HTML."""

    SKIP_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
        "template",
        "form",
        "nav",
        "footer",
        "aside",
    }

    HEADING_TAGS = {
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }

    PARAGRAPH_TAGS = {
        "p",
        "li",
        "blockquote",
        "figcaption",
        "dt",
        "dd",
    }

    def __init__(
        self,
    ) -> None:
        super().__init__(
            convert_charrefs=True
        )

        self.skip_depth = 0
        self.title_depth = 0

        self.current_tag = ""
        self.current_parts: list[str] = []

        self.title_parts: list[str] = []
        self.paragraphs: list[str] = []
        self.headings: list[str] = []

        self.h1 = ""

    def _finish_current_block(
        self,
    ) -> None:
        if not self.current_tag:
            return

        tag = self.current_tag

        text = _normalize_text(
            " ".join(
                self.current_parts
            )
        )

        self.current_tag = ""
        self.current_parts = []

        if not text:
            return

        if tag in self.HEADING_TAGS:
            self.headings.append(
                text
            )

            if (
                tag == "h1"
                and not self.h1
            ):
                self.h1 = text

            return

        self.paragraphs.append(
            text
        )

    def handle_starttag(
        self,
        tag: str,
        attrs: list[
            tuple[str, str | None]
        ],
    ) -> None:
        del attrs

        tag = str(
            tag or ""
        ).lower()

        if self.skip_depth:
            if tag in self.SKIP_TAGS:
                self.skip_depth += 1

            return

        if tag in self.SKIP_TAGS:
            self.skip_depth = 1
            return

        if tag == "title":
            self.title_depth += 1
            return

        if tag in self.HEADING_TAGS:
            self._finish_current_block()

            self.current_tag = tag
            return

        if (
            tag in self.PARAGRAPH_TAGS
            and not self.current_tag
        ):
            self.current_tag = tag
            return

        if (
            tag == "br"
            and self.current_tag
        ):
            self.current_parts.append(
                " "
            )

    def handle_endtag(
        self,
        tag: str,
    ) -> None:
        tag = str(
            tag or ""
        ).lower()

        if self.skip_depth:
            if tag in self.SKIP_TAGS:
                self.skip_depth -= 1

            return

        if tag == "title":
            self.title_depth = max(
                self.title_depth - 1,
                0,
            )

            return

        if (
            self.current_tag
            and tag == self.current_tag
        ):
            self._finish_current_block()

    def handle_data(
        self,
        data: str,
    ) -> None:
        if self.skip_depth:
            return

        if self.title_depth:
            self.title_parts.append(
                data
            )

            return

        if self.current_tag:
            self.current_parts.append(
                data
            )

    def close(
        self,
    ) -> None:
        super().close()

        self._finish_current_block()

    @property
    def title(
        self,
    ) -> str:
        return _normalize_text(
            " ".join(
                self.title_parts
            )
        )


def extract_article_validation_document_v3(
    article_html: str,
) -> dict[str, Any]:
    """Extract transient validation text from certified HTML."""

    parser = _CertifiedHTMLExtractor()

    parser.feed(
        str(article_html or "")
    )

    parser.close()

    article_text = "\n\n".join(
        parser.paragraphs
    ).strip()

    return {
        "title": parser.title,
        "h1": parser.h1,
        "headings": list(
            parser.headings
        ),
        "article_text": article_text,
        "paragraph_count": len(
            parser.paragraphs
        ),
        "heading_count": len(
            parser.headings
        ),
        "article_html_included": False,
    }


def validate_certified_article_v3(
    *,
    article_text: str,
    title: str,
    source_record_id: str,
    article_sha256: str,
    metadata_sha256: str,
    integrity_certificate_id: str,
    integrity_certification_status: str,
    overall_integrity_status: str,
    source_url: str = "",
    h1: str = "",
    headings: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Validate one certified article and return metadata only."""

    article_text = str(
        article_text or ""
    )

    title = _normalize_text(
        title
    )

    h1 = _normalize_text(
        h1
    )

    source_record_id = str(
        source_record_id or ""
    ).strip()

    source_url = str(
        source_url or ""
    ).strip()

    article_sha256 = str(
        article_sha256 or ""
    ).strip().lower()

    metadata_sha256 = str(
        metadata_sha256 or ""
    ).strip().lower()

    integrity_certificate_id = str(
        integrity_certificate_id or ""
    ).strip()

    integrity_certification_status = str(
        integrity_certification_status
        or ""
    ).strip().upper()

    overall_integrity_status = str(
        overall_integrity_status
        or ""
    ).strip().upper()

    normalized_headings = [
        _normalize_text(
            heading
        )
        for heading in (
            headings or []
        )
        if _normalize_text(
            heading
        )
    ]

    paragraphs = _paragraphs(
        article_text
    )

    word_count = len(
        article_text.split()
    )

    duplicate_ratio = (
        _duplicate_paragraph_ratio(
            paragraphs
        )
    )

    printable_ratio = (
        _printable_ratio(
            article_text
        )
    )

    replacement_ratio = (
        _replacement_character_ratio(
            article_text
        )
    )

    explicit_headings = bool(
        normalized_headings
    )

    heading_free_narrative = (
        bool(title)
        and len(paragraphs) >= 3
    )

    checks = {
        "source_identity_present":
            bool(
                source_record_id
            ),

        "integrity_certificate_present":
            bool(
                integrity_certificate_id
            ),

        "integrity_certificate_certified":
            (
                integrity_certification_status
                == "CERTIFIED"
            ),

        "integrity_record_passed":
            (
                overall_integrity_status
                == "PASS"
            ),

        "article_sha256_valid":
            _valid_sha256(
                article_sha256
            ),

        "metadata_sha256_valid":
            _valid_sha256(
                metadata_sha256
            ),

        "title_present":
            bool(title),

        "content_present":
            bool(
                article_text.strip()
            ),

        "document_structure_present":
            bool(paragraphs),

        "heading_structure":
            (
                explicit_headings
                or heading_free_narrative
            ),

        "printable_text":
            (
                printable_ratio
                >= MINIMUM_PRINTABLE_RATIO
            ),

        "replacement_character_ratio":
            (
                replacement_ratio
                <= MAXIMUM_REPLACEMENT_CHARACTER_RATIO
            ),

        "null_byte_free":
            (
                "\x00"
                not in article_text
            ),
    }

    passed = all(
        value is True
        for value in checks.values()
    )

    validation_score = (
        sum(
            value is True
            for value in checks.values()
        )
        / len(checks)
        * 100.0
    )

    if validation_score == 100.0:
        quality_grade = "A+"

    elif validation_score >= 93.0:
        quality_grade = "A"

    elif validation_score >= 85.0:
        quality_grade = "B"

    elif validation_score >= 75.0:
        quality_grade = "C"

    else:
        quality_grade = "Rejected"

    warnings: list[str] = []

    if (
        not explicit_headings
        and heading_free_narrative
    ):
        warnings.append(
            "NO_HEADINGS_ACCEPTED_AS_NARRATIVE"
        )

    if not h1:
        warnings.append(
            "MISSING_H1"
        )

    rejection_map = {
        "source_identity_present":
            "MISSING_SOURCE_RECORD_ID",

        "integrity_certificate_present":
            "MISSING_INTEGRITY_CERTIFICATE_ID",

        "integrity_certificate_certified":
            "INTEGRITY_CERTIFICATE_NOT_CERTIFIED",

        "integrity_record_passed":
            "ARTICLE_NOT_IN_CERTIFIED_ACTIVE_SCOPE",

        "article_sha256_valid":
            "INVALID_ARTICLE_SHA256",

        "metadata_sha256_valid":
            "INVALID_METADATA_SHA256",

        "title_present":
            "MISSING_TITLE",

        "content_present":
            "EMPTY_CONTENT",

        "document_structure_present":
            "MISSING_DOCUMENT_STRUCTURE",

        "heading_structure":
            "INVALID_HEADING_STRUCTURE",

        "printable_text":
            "LOW_PRINTABLE_TEXT_RATIO",

        "replacement_character_ratio":
            "INVALID_REPLACEMENT_CHARACTER_RATIO",

        "null_byte_free":
            "NULL_BYTE_DETECTED",
    }

    rejection_reasons = [
        rejection_map[
            check_name
        ]
        for check_name, check_passed
        in checks.items()
        if not check_passed
    ]

    return {
        "status":
            (
                "PASS"
                if passed
                else "FAIL"
            ),

        "passed":
            passed,

        "validation_version":
            ARTICLE_VALIDATION_ENGINE_VERSION,

        "source_record_id":
            source_record_id,

        "source_url":
            source_url,

        "integrity_certificate_id":
            integrity_certificate_id,

        "article_sha256":
            article_sha256,

        "metadata_sha256":
            metadata_sha256,

        "validation_score":
            round(
                validation_score,
                2,
            ),

        "quality_grade":
            quality_grade,

        "checks":
            checks,

        "observations": {
            "repeated_content_detected":
                duplicate_ratio > 0.0,

            "duplicate_paragraph_ratio":
                round(
                    duplicate_ratio,
                    6,
                ),

            "duplicate_ratio_affects_pass_fail":
                False,

            "single_paragraph_allowed":
                True,
        },

        "statistics": {
            "word_count":
                word_count,

            "paragraph_count":
                len(
                    paragraphs
                ),

            "heading_count":
                len(
                    normalized_headings
                ),

            "h1_present":
                bool(h1),

            "duplicate_paragraph_ratio":
                round(
                    duplicate_ratio,
                    6,
                ),

            "printable_ratio":
                round(
                    printable_ratio,
                    6,
                ),

            "replacement_character_ratio":
                round(
                    replacement_ratio,
                    8,
                ),
        },

        "warnings":
            warnings,

        "errors":
            [],

        "rejection_reasons":
            rejection_reasons,

        "eligible_for_wuc":
            passed,

        "eligible_for_unified_content_document":
            passed,

        "article_body_included":
            False,

        "article_body_modified":
            False,
    }
