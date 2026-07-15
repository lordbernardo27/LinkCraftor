from __future__ import annotations

import html
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup, NavigableString, Tag


REMOVABLE_TAGS_V1 = {
    "script",
    "style",
    "noscript",
    "template",
    "svg",
    "canvas",
    "iframe",
    "form",
    "nav",
    "footer",
}

REMOVABLE_SIGNAL_TERMS_V1 = {
    "advertisement",
    "ad-container",
    "ad-wrapper",
    "ad-slot",
    "affiliate",
    "breadcrumb",
    "breadcrumbs",
    "cookie",
    "consent",
    "footer",
    "inline-form",
    "lightbox",
    "newsletter",
    "pagination",
    "promo",
    "recommended-products",
    "share",
    "sharing",
    "signup",
    "social",
    "sponsored",
    "subscribe",
    "video-player",
}

EDITORIAL_METADATA_PATTERNS_V1 = [
    re.compile(
        r"^\s*medically reviewed(?:\s+by)?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*fact[- ]checked(?:\s+by)?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*reviewed\s+[A-Z][a-z]+\s+\d{1,2},\s+\d{4}\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*latest update\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*medical review policy\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*editorial policy\b",
        re.IGNORECASE,
    ),
]

UI_TEXT_PATTERNS_V1 = [
    re.compile(r"^\s*previous item\s*$", re.IGNORECASE),
    re.compile(r"^\s*next item\s*$", re.IGNORECASE),
    re.compile(r"^\s*back to top\s*$", re.IGNORECASE),
    re.compile(r"^\s*see more\s*$", re.IGNORECASE),
    re.compile(r"^\s*recommended products\s*$", re.IGNORECASE),
]


def _normalize_text_v1(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = text.replace("\u00a0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    return text.strip()


def _node_signals_v1(node: Tag) -> str:
    values: List[str] = []

    node_id = node.get("id")
    if node_id:
        values.append(str(node_id))

    classes = node.get("class") or []
    values.extend(str(value) for value in classes)

    for key in (
        "role",
        "aria-label",
        "data-component",
        "data-module",
        "data-testid",
    ):
        value = node.get(key)
        if value:
            values.append(str(value))

    return " ".join(values).casefold()


def _has_removable_signal_v1(node: Tag) -> bool:
    signals = _node_signals_v1(node)

    return any(
        term in signals
        for term in REMOVABLE_SIGNAL_TERMS_V1
    )


def _remove_unwanted_nodes_v1(root: Tag) -> int:
    removed = 0

    for node in list(root.find_all(True)):
        if node.name in REMOVABLE_TAGS_V1:
            node.decompose()
            removed += 1
            continue

        if _has_removable_signal_v1(node):
            node.decompose()
            removed += 1

    return removed


def _is_metadata_or_ui_v1(text: str) -> bool:
    normalized = _normalize_text_v1(text)

    if not normalized:
        return True

    for pattern in EDITORIAL_METADATA_PATTERNS_V1:
        if pattern.search(normalized):
            return True

    for pattern in UI_TEXT_PATTERNS_V1:
        if pattern.fullmatch(normalized):
            return True

    return False


def _nearest_selected_ancestor_v1(
    node: Tag,
    selected_names: set[str],
) -> Optional[Tag]:
    parent = node.parent

    while isinstance(parent, Tag):
        if parent.name in selected_names:
            return parent
        parent = parent.parent

    return None


def _extract_list_item_text_v1(node: Tag) -> str:
    clone = BeautifulSoup(
        str(node),
        "html5lib",
    ).find("li")

    if not isinstance(clone, Tag):
        return _normalize_text_v1(node.get_text(" ", strip=True))

    for nested in list(clone.find_all(["ul", "ol"])):
        nested.decompose()

    return _normalize_text_v1(
        clone.get_text(" ", strip=True)
    )


def extract_dom_article_structure_v1(
    *,
    html_text: str,
    url: str = "",
    title: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Parse malformed or browser-tolerated article HTML into ordered,
    paragraph-preserving plain-text blocks.

    This function:
    - repairs implicit HTML element closures through html5lib;
    - reads headings and paragraphs in DOM order;
    - preserves paragraph boundaries;
    - does not infer paragraph boundaries from flattened prose;
    - does not write any stores.
    """

    source_html = str(html_text or "")

    soup = BeautifulSoup(
        source_html,
        "html5lib",
    )

    root = soup.find("article")

    root_mode = "article"

    if not isinstance(root, Tag):
        root = soup.find("main")
        root_mode = "main"

    if not isinstance(root, Tag):
        root = soup.body or soup
        root_mode = "body_fallback"

    removed_node_count = _remove_unwanted_nodes_v1(root)

    selected_names = {
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "p",
        "li",
        "blockquote",
    }

    blocks: List[Dict[str, Any]] = []
    headings: List[Dict[str, Any]] = []
    paragraphs: List[str] = []

    previous_key = ""

    for node in root.find_all(
        [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "p",
            "li",
            "blockquote",
        ]
    ):
        if not isinstance(node, Tag):
            continue

        ancestor = _nearest_selected_ancestor_v1(
            node,
            selected_names,
        )

        if ancestor is not None:
            continue

        tag_name = str(node.name or "").lower()

        if tag_name == "li":
            text = _extract_list_item_text_v1(node)
        else:
            text = _normalize_text_v1(
                node.get_text(" ", strip=True)
            )

        if not text:
            continue

        if _is_metadata_or_ui_v1(text):
            continue

        block_type = (
            "heading"
            if tag_name.startswith("h")
            else "paragraph"
        )

        key = (
            block_type
            + ":"
            + re.sub(r"\s+", " ", text).casefold()
        )

        # Only remove adjacent DOM duplicates, not repeated prose elsewhere.
        if key == previous_key:
            continue

        previous_key = key

        block = {
            "index": len(blocks),
            "type": block_type,
            "tag": tag_name,
            "level": (
                int(tag_name[1])
                if tag_name.startswith("h")
                and len(tag_name) == 2
                and tag_name[1].isdigit()
                else None
            ),
            "text": text,
            "word_count": len(text.split()),
        }

        blocks.append(block)

        if block_type == "heading":
            headings.append({
                "level": block["level"],
                "text": text,
            })
        else:
            paragraphs.append(text)

    article_body = "\n\n".join(
        block["text"]
        for block in blocks
    ).strip()

    detected_title = _normalize_text_v1(title)

    if not detected_title:
        h1 = next(
            (
                item["text"]
                for item in blocks
                if item["tag"] == "h1"
            ),
            "",
        )

        detected_title = h1

    return {
        "ok": bool(article_body),
        "engine": "dom_article_structure_extractor_v1",
        "parser": "beautifulsoup_html5lib",
        "root_mode": root_mode,
        "url": url,
        "title": detected_title,
        "article_body": article_body,
        "content_body": article_body,
        "blocks": blocks,
        "headings": headings,
        "paragraphs": paragraphs,
        "statistics": {
            "source_html_length": len(source_html),
            "removed_node_count": removed_node_count,
            "block_count": len(blocks),
            "heading_count": len(headings),
            "paragraph_count": len(paragraphs),
            "article_word_count": len(article_body.split()),
            "article_length": len(article_body),
        },
        "metadata": {
            **(metadata or {}),
            "structural_extraction": {
                "engine": "dom_article_structure_extractor_v1",
                "parser": "beautifulsoup_html5lib",
                "root_mode": root_mode,
            },
        },
    }


def explain_dom_article_structure_extractor_v1() -> Dict[str, Any]:
    return {
        "engine": "dom_article_structure_extractor_v1",
        "parser": "beautifulsoup_html5lib",
        "purpose": (
            "Extract ordered headings and paragraphs from valid, "
            "invalid, and browser-tolerated HTML"
        ),
        "preserves": [
            "DOM content order",
            "heading boundaries",
            "paragraph boundaries",
            "list-item boundaries",
            "blockquote boundaries",
        ],
        "does_not": [
            "write WUC",
            "write UUCD",
            "infer paragraphs from flattened prose",
            "perform semantic interpretation",
        ],
    }
