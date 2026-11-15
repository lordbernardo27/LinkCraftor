"""Restricted Markdown structural adapter for Original Scorer.

Does not authorize insertion. Unsupported Markdown fails closed.
"""

from __future__ import annotations

import hashlib
import re
from urllib.parse import urlsplit

from backend.server.engine.scorer_document_contract import (
    SCORER_DOCUMENT_CONTRACT_VERSION,
    validate_scorer_document_contract,
)


class ScorerMarkdownAdapterError(ValueError):
    pass


HEADING = re.compile(r"^(#{1,6}) ([^\n]+)$")
LINK = re.compile(r"\[([^\[\]\n]+)\]\(([^()\s]+)\)")

FAQ_TITLES = {
    "faq", "faqs", "frequently asked questions"
}

REFERENCE_TITLES = {
    "references", "bibliography", "works cited",
    "sources", "further reading"
}


def _parse_paragraph(line):
    parts = []
    links = []
    cursor = 0
    length = 0

    for match in LINK.finditer(line):
        plain = line[cursor:match.start()]

        if any(c in plain for c in "[]`<>*_!"):
            raise ScorerMarkdownAdapterError(
                "unsupported Markdown paragraph syntax"
            )

        parts.append(plain)
        length += len(plain)

        label, destination = match.groups()
        if any(c in label for c in "`<>*_!"):
            raise ScorerMarkdownAdapterError(
                "unsupported link label syntax"
            )

        parsed = urlsplit(destination)
        if (
            parsed.scheme.lower() not in {"", "http", "https"}
            or any(ord(c) < 33 or ord(c) == 127 for c in destination)
        ):
            raise ScorerMarkdownAdapterError(
                "unsupported Markdown link destination"
            )

        start = length
        parts.append(label)
        length += len(label)
        links.append((start, length, destination))
        cursor = match.end()

    remainder = line[cursor:]
    if any(c in remainder for c in "[]`<>*_!"):
        raise ScorerMarkdownAdapterError(
            "unsupported Markdown paragraph syntax"
        )

    parts.append(remainder)
    text = "".join(parts)

    if not text or text != " ".join(text.split()):
        raise ScorerMarkdownAdapterError(
            "unsupported whitespace in Markdown paragraph"
        )

    return text, links


def adapt_markdown_for_scorer(
    *,
    markdown: str,
    workspace_id: str,
    document_id: str,
    content_version: str,
    source_format: str = "md",
):
    if source_format not in {"md", "markdown"}:
        raise ScorerMarkdownAdapterError(
            "unsupported Markdown extension"
        )

    if not isinstance(markdown, str) or not markdown.strip():
        raise ScorerMarkdownAdapterError(
            "Markdown source required"
        )

    regions = []
    protected = []
    paragraphs = []
    eligible_words = 0
    current_section = "root"
    current_type = "article_body"
    protected_level = None
    heading_seen = False
    previous_was_paragraph = False

    for line_number, raw in enumerate(markdown.splitlines(), 1):
        if not raw.strip():
            previous_was_paragraph = False
            continue

        if raw != raw.strip():
            raise ScorerMarkdownAdapterError(
                "indented or trailing-space Markdown unsupported"
            )

        match = HEADING.fullmatch(raw)

        if match:
            heading_seen = True
            previous_was_paragraph = False
            level = len(match.group(1))
            title = match.group(2).casefold().strip()

            if any(c in title for c in "[]`<>*_!"):
                raise ScorerMarkdownAdapterError(
                    "complex Markdown heading unsupported"
                )

            if title in FAQ_TITLES:
                current_type = "faq"
                protected_level = level
            elif title in REFERENCE_TITLES:
                current_type = "references"
                protected_level = level
            elif (
                protected_level is None
                or level <= protected_level
            ):
                current_type = "editorial_section"
                protected_level = None

            current_section = f"section_{line_number}"
            regions.append({
                "region_id": f"heading_{line_number}",
                "region_type": "heading",
                "eligible_for_linking": False,
                "source_line": line_number,
            })
            continue

        if not heading_seen:
            raise ScorerMarkdownAdapterError(
                "first content must be a Markdown heading"
            )

        if raw.startswith(("#", ">", "-", "+", "|", "```", "~~~")):
            raise ScorerMarkdownAdapterError(
                "unsupported Markdown block"
            )

        if previous_was_paragraph:
            raise ScorerMarkdownAdapterError(
                "multiline Markdown paragraphs unsupported"
            )

        paragraph, anchors = _parse_paragraph(raw)
        offset = sum(len(value) + 2 for value in paragraphs)
        node_id = f"markdown_line_{line_number}"
        eligible = current_type not in {"faq", "references"}

        if eligible:
            eligible_words += len(paragraph.split())

        lineage = [{
            "section_id": "root",
            "section_type": "article_body",
        }]

        lineage.append({
            "section_id": current_section,
            "section_type": current_type,
        }) if current_section != "root" else None

        regions.append({
            "region_id": f"paragraph_{line_number}",
            "region_type": "body_paragraph",
            "eligible_for_linking": eligible,
            "source_mapping_verified": True,
            "source_node_id": node_id,
            "source_line": line_number,
            "section_id": current_section,
            "section_lineage": lineage,
            "char_start": offset,
            "char_end": offset + len(paragraph),
            "text": paragraph,
            "word_count": len(paragraph.split()),
        })

        for index, (start, end, destination) in enumerate(anchors):
            protected.append({
                "span_id": f"md_link_{line_number}_{index}",
                "kind": "hyperlink",
                "char_start": offset + start,
                "char_end": offset + end,
                "text": paragraph[start:end],
                "source_node_id": node_id,
                "destination": destination,
            })

        paragraphs.append(paragraph)
        previous_was_paragraph = True

    if not heading_seen:
        raise ScorerMarkdownAdapterError(
            "Markdown heading required"
        )

    canonical_text = "\n\n".join(paragraphs)

    document = {
        "schema_version": SCORER_DOCUMENT_CONTRACT_VERSION,
        "workspace_id": workspace_id,
        "document_id": document_id,
        "content_version": content_version,
        "source_format": source_format,
        "canonical_text": canonical_text,
        "content_sha256": hashlib.sha256(
            canonical_text.encode("utf-8")
        ).hexdigest(),
        "source_markdown_sha256": hashlib.sha256(
            markdown.encode("utf-8")
        ).hexdigest(),
        "structure_complete": True,
        "regions": regions,
        "eligible_body_word_count": eligible_words,
        "protected_spans_complete": True,
        "protected_spans": protected,
        "source_mapping_scope": "canonical_markdown_text_only",
        "original_source_insertion_verified": False,
        "source_adapter": "scorer_markdown_adapter_i2_b1",
    }

    return validate_scorer_document_contract(document)
