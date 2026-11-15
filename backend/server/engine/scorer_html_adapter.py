"""Conservative HTML-to-Scorer document adapter, I2-A1.

Supports an explicit <article> containing direct heading and paragraph
children with simple inline formatting and hyperlinks.

Unsupported structures fail closed. No document is modified.
"""

from __future__ import annotations

import hashlib
import re
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

from backend.server.engine.scorer_document_contract import (
    SCORER_DOCUMENT_CONTRACT_VERSION,
    validate_scorer_document_contract,
)


class ScorerHtmlAdapterError(ValueError):
    pass


INLINE_TAGS = frozenset({
    "a", "strong", "b", "em", "i", "span", "u",
    "small", "sub", "sup", "code",
})
HEADING_TAGS = frozenset({
    "h1", "h2", "h3", "h4", "h5", "h6",
})
FAQ_TITLES = frozenset({
    "faq", "faqs", "frequently asked questions",
})
REFERENCE_TITLES = frozenset({
    "references", "bibliography", "works cited",
    "sources", "further reading",
})


def _verify_attributes(node, *, hyperlink=False):
    """Reject attributes without an approved structural meaning."""
    allowed = {"href"} if hyperlink else set()

    for key in node.attrs:
        if str(key).lower() not in allowed:
            raise ScorerHtmlAdapterError(
                "unsupported HTML attribute: " + str(key)
            )


def _verify_href(href):
    if not isinstance(href, str) or not href.strip():
        raise ScorerHtmlAdapterError(
            "hyperlink destination missing"
        )

    value = href.strip()

    if any(ord(c) < 33 or ord(c) == 127 for c in value):
        raise ScorerHtmlAdapterError(
            "unsafe hyperlink destination characters"
        )

    parsed = urlsplit(value)
    if parsed.scheme.lower() not in {
        "", "http", "https", "mailto", "tel",
    }:
        raise ScorerHtmlAdapterError(
            "unsupported hyperlink destination scheme"
        )

    return value


def _paragraph_parts(node):
    """Read text and anchor offsets in parsed-DOM text order."""
    parts = []
    links = []
    length = 0

    def walk(element, inside_link=False):
        nonlocal length

        for child in element.children:
            if isinstance(child, NavigableString):
                value = str(child)
                parts.append(value)
                length += len(value)
                continue

            if not isinstance(child, Tag):
                raise ScorerHtmlAdapterError(
                    "unsupported paragraph child"
                )

            name = str(child.name).lower()

            if name not in INLINE_TAGS or name == "code":
                raise ScorerHtmlAdapterError(
                    "unsupported paragraph element: " + name
                )

            _verify_attributes(
                child, hyperlink=(name == "a")
            )

            if name == "a":
                if inside_link:
                    raise ScorerHtmlAdapterError("nested hyperlink")

                href = _verify_href(
                    child.get("href")
                )

                start = length
                walk(child, True)
                end = length

                if start == end:
                    raise ScorerHtmlAdapterError("empty hyperlink")

                links.append((start, end, href.strip()))
            else:
                walk(child, inside_link)

    walk(node)
    text = "".join(parts)

    # This initial adapter does not silently normalize away
    # whitespace that would invalidate source coordinates.
    if not text or text != " ".join(text.split()):
        raise ScorerHtmlAdapterError(
            "paragraph requires exact whitespace preservation"
        )

    return text, sorted(links)


def adapt_html_for_scorer(
    *,
    html: str,
    workspace_id: str,
    document_id: str,
    content_version: str,
):
    if not isinstance(html, str) or not html.strip():
        raise ScorerHtmlAdapterError("HTML source required")

    soup = BeautifulSoup(html, "html.parser")
    articles = soup.find_all("article")

    if len(articles) != 1:
        raise ScorerHtmlAdapterError(
            "exactly one article element required"
        )

    article = articles[0]
    _verify_attributes(article)

    # Comments are not editorial prose. Reject rather than
    # silently introducing them into canonical article text.
    if article.find_all(
        string=lambda value: isinstance(value, Comment)
    ):
        raise ScorerHtmlAdapterError(
            "HTML comments inside article are unsupported"
        )

    source_sha256 = hashlib.sha256(
        html.encode("utf-8")
    ).hexdigest()

    regions = []
    protected = []
    paragraphs = []
    eligible_words = 0
    current_section = "root"
    current_type = "article_body"
    current_level = 0
    protected_level = None

    children = list(article.children)

    for index, node in enumerate(children):
        if isinstance(node, NavigableString):
            if str(node).strip():
                raise ScorerHtmlAdapterError(
                    "unstructured article text"
                )
            continue

        if not isinstance(node, Tag):
            raise ScorerHtmlAdapterError(
                "unsupported article child"
            )

        name = str(node.name).lower()

        _verify_attributes(node)

        if name in HEADING_TAGS:
            if node.find(True):
                raise ScorerHtmlAdapterError(
                    "complex heading unsupported"
                )

            heading = node.get_text(strip=True)
            if not heading:
                raise ScorerHtmlAdapterError("empty heading")

            level = int(name[1])
            title = " ".join(heading.casefold().split())

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

            current_section = f"section_{index}"

            regions.append({
                "region_id": f"heading_{index}",
                "region_type": "heading",
                "eligible_for_linking": False,
            })
            current_level = level
            continue

        if name != "p":
            raise ScorerHtmlAdapterError(
                "unsupported article block: " + name
            )

        paragraph, anchors = _paragraph_parts(node)
        offset = sum(len(p) + 2 for p in paragraphs)
        end = offset + len(paragraph)
        node_id = f"html_article_child_{index}"
        node_path = f"article/child[{index}]"
        eligible = current_type not in {
            "faq", "references",
        }

        if eligible:
            eligible_words += len(paragraph.split())

        lineage = [{
            "section_id": "root",
            "section_type": "article_body",
        }]

        if current_section != "root":
            lineage.append({
                "section_id": current_section,
                "section_type": current_type,
            })

        regions.append({
            "region_id": f"paragraph_{index}",
            "region_type": "body_paragraph",
            "eligible_for_linking": eligible,
            "source_mapping_verified": True,
            "source_node_id": node_id,
            "source_node_path": node_path,
            "section_id": current_section,
            "section_lineage": lineage,
            "char_start": offset,
            "char_end": end,
            "text": paragraph,
            "word_count": len(paragraph.split()),
        })

        for link_index, (start, stop, href) in enumerate(anchors):
            protected.append({
                "span_id": f"anchor_{index}_{link_index}",
                "kind": "hyperlink",
                "char_start": offset + start,
                "char_end": offset + stop,
                "text": paragraph[start:stop],
                "source_node_id": node_id,
                "source_node_path": node_path,
                "destination": href,
            })

        paragraphs.append(paragraph)

    canonical_text = "\n\n".join(paragraphs)

    document = {
        "schema_version": SCORER_DOCUMENT_CONTRACT_VERSION,
        "workspace_id": workspace_id,
        "document_id": document_id,
        "content_version": content_version,
        "source_format": "html",
        "canonical_text": canonical_text,
        "content_sha256": hashlib.sha256(
            canonical_text.encode("utf-8")
        ).hexdigest(),
        "structure_complete": True,
        "regions": regions,
        "eligible_body_word_count": eligible_words,
        "protected_spans_complete": True,
        "protected_spans": protected,
        "source_adapter": "scorer_html_adapter_i2_a3",
        "source_html_sha256": source_sha256,
        "source_parser": "html.parser",
        "source_mapping_scope": "canonical_dom_text_only",
        "original_source_insertion_verified": False,
    }

    return validate_scorer_document_contract(document)
