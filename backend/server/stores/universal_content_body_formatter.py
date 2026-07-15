from __future__ import annotations

import html
import re
from typing import Any, Dict, List


def _normalize_inline_spacing_v2(value: str) -> str:
    """
    Normalize spaces inside one line without changing word order.
    """
    value = html.unescape(str(value or ""))
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[ \t]+", " ", value)
    return value.strip()


def _heading_text_v2(item: Any) -> str:
    if isinstance(item, dict):
        value = (
            item.get("text")
            or item.get("title")
            or item.get("heading")
            or ""
        )
    else:
        value = item

    return _normalize_inline_spacing_v2(value)


def _paragraph_blocks_from_text_v2(
    text: str,
) -> List[str]:
    """
    Preserve existing blank-line paragraph boundaries.

    Lines inside the same block are joined with one space.
    No text is deleted, deduplicated, inferred, or reordered.
    """
    normalized = html.unescape(str(text or ""))
    normalized = normalized.replace("\r\n", "\n")
    normalized = normalized.replace("\r", "\n")
    normalized = normalized.replace("\u00a0", " ")

    raw_blocks = re.split(
        r"\n[ \t]*\n+",
        normalized,
    )

    blocks: List[str] = []

    for raw_block in raw_blocks:
        lines = []

        for raw_line in raw_block.split("\n"):
            line = _normalize_inline_spacing_v2(
                raw_line
            )

            if line:
                lines.append(line)

        if lines:
            blocks.append(" ".join(lines))

    return blocks


def _paragraph_blocks_from_supplied_v2(
    paragraphs: List[Any],
) -> List[str]:
    blocks: List[str] = []

    for item in paragraphs:
        if isinstance(item, dict):
            value = item.get("text") or ""
        else:
            value = item

        value = html.unescape(str(value or ""))
        value = value.replace("\r\n", "\n")
        value = value.replace("\r", "\n")
        value = value.replace("\u00a0", " ")

        lines = [
            _normalize_inline_spacing_v2(line)
            for line in value.split("\n")
            if _normalize_inline_spacing_v2(line)
        ]

        if lines:
            blocks.append(" ".join(lines))

    return blocks


def format_universal_content_body_v1(
    *,
    text: str,
    headings: List[Any] | None = None,
    paragraphs: List[Any] | None = None,
    title: str = "",
) -> Dict[str, Any]:
    """
    Lossless canonical content-body formatter.

    Guarantees:
    - preserves all words in their original order;
    - never removes duplicate blocks;
    - never guesses new headings;
    - never performs extraction or boilerplate removal;
    - changes formatting only.

    It may use known headings for reporting, but it does not
    split prose based on heuristic heading detection.
    """

    heading_values = [
        value
        for value in (
            _heading_text_v2(item)
            for item in (headings or [])
        )
        if value
    ]

    heading_lookup = {
        value.casefold()
        for value in heading_values
    }

    if paragraphs:
        blocks = _paragraph_blocks_from_supplied_v2(
            list(paragraphs)
        )
        source_mode = "supplied_paragraphs"
    else:
        blocks = _paragraph_blocks_from_text_v2(
            str(text or "")
        )
        source_mode = "existing_text_blocks"

    content_body = "\n\n".join(blocks).strip()

    matched_heading_count = sum(
        1
        for block in blocks
        if block.casefold() in heading_lookup
    )

    return {
        "ok": bool(content_body),
        "formatter":
            "universal_content_body_formatter_v2_lossless",
        "format":
            "canonical_paragraph_plain_text_v2",
        "source_mode": source_mode,
        "title": _normalize_inline_spacing_v2(title),
        "content_body": content_body,
        "article_body": content_body,
        "paragraphs": blocks,
        "paragraph_count": len(blocks),
        "heading_count": matched_heading_count,
        "word_count": len(content_body.split()),
        "content_length": len(content_body),
        "lossless_contract": {
            "deletes_words": False,
            "reorders_words": False,
            "deduplicates_blocks": False,
            "infers_headings": False,
        },
    }


def explain_universal_content_body_formatter_v1() -> Dict[str, Any]:
    return {
        "engine":
            "universal_content_body_formatter_v2_lossless",
        "output_format":
            "canonical_paragraph_plain_text_v2",
        "block_separator":
            "two newline characters",
        "guarantees": [
            "word order preserved",
            "no text deletion",
            "no block deduplication",
            "no heuristic heading inference",
            "existing paragraph boundaries preserved",
        ],
        "does_not": [
            "extract main content",
            "remove boilerplate",
            "classify page types",
            "change semantic meaning",
        ],
        "supported_sources": [
            "website",
            "docx",
            "pdf",
            "txt",
            "html",
            "markdown",
            "future knowledge connectors",
        ],
    }
