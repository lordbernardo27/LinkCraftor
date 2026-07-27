"""Fresh non-persistent Website Unified Content engine.

The engine preserves the complete validated article content in reading order.
It performs structural conversion only. It never summarizes, truncates,
filters by word count, or writes an intermediate content store.
"""

from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser
from typing import Any, Mapping


WUC_ENGINE_VERSION = (
    "website_unified_content_engine_v1_"
    "complete_content_preservation"
)


class WebsiteUnifiedContentEngineError(
    RuntimeError
):
    """Raised when a transient WUC package cannot be produced."""


def _normalize_text(
    value: Any,
) -> str:
    return re.sub(
        r"\s+",
        " ",
        str(
            value or ""
        ),
    ).strip()


def _sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def _word_count(
    value: str,
) -> int:
    return len(
        re.findall(
            r"\b[\w’'-]+\b",
            value,
            flags=re.UNICODE,
        )
    )


class _WucHtmlParser(
    HTMLParser
):
    """Read semantic article blocks from certified reader-ready HTML."""

    BODY_BLOCK_TAGS = {
        "p",
        "li",
        "blockquote",
        "figcaption",
        "dd",
        "dt",
        "td",
        "th",
        "pre",
    }

    HEADING_TAGS = {
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }

    IGNORED_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
        "template",
    }

    def __init__(
        self,
    ) -> None:
        super().__init__(
            convert_charrefs=True,
        )

        self._ignored_depth = 0
        self._captures: list[
            dict[str, Any]
        ] = []

        self._title_capture = False
        self._title_parts: list[str] = []

        self.title = ""
        self.h1 = ""

        self.headings: list[
            dict[str, Any]
        ] = []

        self.blocks: list[
            dict[str, Any]
        ] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[
            tuple[str, str | None]
        ],
    ) -> None:
        del attrs

        normalized = tag.casefold()

        if normalized in self.IGNORED_TAGS:
            self._ignored_depth += 1
            return

        if self._ignored_depth:
            return

        if normalized == "title":
            self._title_capture = True
            self._title_parts = []
            return

        if (
            normalized in self.BODY_BLOCK_TAGS
            or normalized in self.HEADING_TAGS
        ):
            self._captures.append(
                {
                    "tag":
                        normalized,

                    "parts":
                        [],
                }
            )

    def handle_endtag(
        self,
        tag: str,
    ) -> None:
        normalized = tag.casefold()

        if normalized in self.IGNORED_TAGS:
            if self._ignored_depth:
                self._ignored_depth -= 1

            return

        if self._ignored_depth:
            return

        if normalized == "title":
            self._title_capture = False

            title = _normalize_text(
                " ".join(
                    self._title_parts
                )
            )

            if title:
                self.title = title

            return

        for index in range(
            len(
                self._captures
            )
            - 1,
            -1,
            -1,
        ):
            capture = self._captures[
                index
            ]

            if capture[
                "tag"
            ] != normalized:
                continue

            self._captures.pop(
                index
            )

            text = _normalize_text(
                " ".join(
                    capture[
                        "parts"
                    ]
                )
            )

            if not text:
                return

            block_index = len(
                self.blocks
            )

            if normalized in self.HEADING_TAGS:
                level = int(
                    normalized[
                        1:
                    ]
                )

                block_type = "heading"

                heading = {
                    "heading_id":
                        (
                            "heading_"
                            + str(
                                len(
                                    self.headings
                                )
                            ).zfill(
                                5
                            )
                        ),

                    "level":
                        level,

                    "text":
                        text,

                    "block_index":
                        block_index,
                }

                self.headings.append(
                    heading
                )

                if (
                    normalized == "h1"
                    and not self.h1
                ):
                    self.h1 = text

            else:
                block_type = normalized

            self.blocks.append(
                {
                    "block_id":
                        (
                            "block_"
                            + str(
                                block_index
                            ).zfill(
                                6
                            )
                        ),

                    "block_index":
                        block_index,

                    "block_type":
                        block_type,

                    "tag":
                        normalized,

                    "text":
                        text,

                    "text_sha256":
                        _sha256_text(
                            text
                        ),

                    "word_count":
                        _word_count(
                            text
                        ),
                }
            )

            return

    def handle_data(
        self,
        data: str,
    ) -> None:
        if self._ignored_depth:
            return

        if self._title_capture:
            self._title_parts.append(
                data
            )

        for capture in self._captures:
            capture[
                "parts"
            ].append(
                data
            )


def build_transient_website_unified_content_v1(
    *,
    certified_source: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a complete, transient Website Unified Content package."""

    descriptor = certified_source.get(
        "descriptor"
    )

    if not isinstance(
        descriptor,
        Mapping,
    ):
        raise WebsiteUnifiedContentEngineError(
            "Certified WUC descriptor is missing."
        )

    html = str(
        certified_source.get(
            "udare_html"
        )
        or ""
    )

    if not html.strip():
        raise WebsiteUnifiedContentEngineError(
            "Certified UDARE HTML is empty."
        )

    metadata_value = certified_source.get(
        "udare_metadata"
    )

    metadata = (
        dict(
            metadata_value
        )
        if isinstance(
            metadata_value,
            Mapping,
        )
        else {}
    )

    parser = _WucHtmlParser()

    parser.feed(
        html
    )

    parser.close()

    if not parser.blocks:
        raise WebsiteUnifiedContentEngineError(
            "WUC engine found no semantic article blocks."
        )

    # Complete content preservation:
    # headings and body blocks remain in original reading order.
    content_body = "\n\n".join(
        block[
            "text"
        ]
        for block in parser.blocks
    ).strip()

    if not content_body:
        raise WebsiteUnifiedContentEngineError(
            "WUC engine produced an empty content body."
        )

    source_record_id = _normalize_text(
        descriptor.get(
            "source_record_id"
        )
    )

    workspace_id = _normalize_text(
        descriptor.get(
            "workspace_id"
        )
    )

    if not source_record_id:
        raise WebsiteUnifiedContentEngineError(
            "source_record_id is required."
        )

    if not workspace_id:
        raise WebsiteUnifiedContentEngineError(
            "workspace_id is required."
        )

    title = _normalize_text(
        descriptor.get(
            "display_title"
        )
        or metadata.get(
            "title"
        )
        or parser.title
        or parser.h1
    )

    h1 = _normalize_text(
        metadata.get(
            "h1"
        )
        or parser.h1
        or title
    )

    canonical_url = _normalize_text(
        descriptor.get(
            "source_url"
        )
        or metadata.get(
            "canonical_url"
        )
        or metadata.get(
            "source_url"
        )
        or metadata.get(
            "url"
        )
    )

    content_id = (
        "wuc_"
        + source_record_id.removeprefix(
            "raw_html_"
        )
    )

    body_word_count = _word_count(
        content_body
    )

    block_word_count = sum(
        int(
            block.get(
                "word_count"
            )
            or 0
        )
        for block in parser.blocks
    )

    if body_word_count != block_word_count:
        raise WebsiteUnifiedContentEngineError(
            "Complete-content accounting failed: "
            f"{body_word_count} != {block_word_count}"
        )

    return {
        "schema_version":
            "website_unified_content_v1",

        "engine_version":
            WUC_ENGINE_VERSION,

        "content_id":
            content_id,

        "document_id":
            source_record_id,

        "workspace_id":
            workspace_id,

        "source_type":
            "website",

        "source_format":
            "html",

        "source_identity": {
            "source_record_id":
                source_record_id,

            "canonical_url":
                canonical_url,

            "udare_article_path":
                descriptor.get(
                    "article_path"
                ),

            "udare_article_sha256":
                descriptor.get(
                    "article_sha256"
                ),
        },

        "title":
            title,

        "h1":
            h1,

        "headings":
            parser.headings,

        "canonical_url":
            canonical_url,

        "content_body":
            content_body,

        "content_hash":
            _sha256_text(
                content_body
            ),

        "body_length":
            len(
                content_body
            ),

        "body_word_count":
            body_word_count,

        "structure": {
            "block_count":
                len(
                    parser.blocks
                ),

            "heading_count":
                len(
                    parser.headings
                ),

            "content_word_count":
                body_word_count,

            "blocks":
                parser.blocks,
        },

        "metadata": {
            "article_validation_status":
                descriptor.get(
                    "article_validation_status"
                ),

            "article_validation_run_id":
                descriptor.get(
                    "article_validation_run_id"
                ),

            "article_validation_certificate_id":
                descriptor.get(
                    "article_validation_certificate_id"
                ),

            "wuc_persistence_mode":
                "TRANSIENT",

            "complete_content_preserved":
                True,

            "content_reduction_performed":
                False,

            "summarization_performed":
                False,

            "truncation_performed":
                False,

            "word_count_limit_applied":
                False,

            "article_body_persisted_by_wuc":
                False,

            "intermediate_wuc_store_created":
                False,

            "performs_reconstruction":
                False,

            "performs_article_validation":
                False,

            "performs_semantic_analysis":
                False,
        },

        "handoff": {
            "next_stage":
                "universal_unified_content_document",

            "eligible_for_uucd":
                True,

            "body_field":
                "content_body",

            "full_body_handoff":
                True,
        },
    }
