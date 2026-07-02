from __future__ import annotations

import re
from typing import Any, Dict, List


REMOVED_TAGS_V1 = [
    "script",
    "style",
    "noscript",
    "svg",
    "iframe",
    "form",
    "nav",
    "footer",
    "header",
    "aside",
]


def clean_raw_html_v1(
    *,
    raw_html: str,
    url: str = "",
    title: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Website HTML Cleaner.

    Responsibility:
    - Accept raw website HTML.
    - Remove non-article structural/noisy tags.
    - Preserve cleaned HTML for article extraction.
    - Does not extract article content.
    - Does not normalize article text.
    """

    metadata = metadata or {}
    original_html = str(raw_html or "")

    cleaned_html = original_html
    removed_blocks: List[Dict[str, Any]] = []

    for tag in REMOVED_TAGS_V1:
        pattern = rf"(?is)<{tag}\b[^>]*>.*?</{tag}>"
        matches = list(re.finditer(pattern, cleaned_html))

        for m in matches:
            removed_blocks.append({
                "tag": tag,
                "length": len(m.group(0)),
                "reason": "html_noise_tag",
            })

        cleaned_html = re.sub(pattern, " ", cleaned_html)

    cleaned_html = re.sub(r"(?is)<!--.*?-->", " ", cleaned_html)
    cleaned_html = re.sub(r"\s+", " ", cleaned_html).strip()

    return {
        "status": "cleaned",
        "engine": "html_cleaning_engine_v1",
        "url": url,
        "title": title,
        "cleaned_html": cleaned_html,
        "original_length": len(original_html),
        "cleaned_length": len(cleaned_html),
        "removed_block_count": len(removed_blocks),
        "removed_blocks": removed_blocks[:200],
        "metadata": metadata,
    }


def explain_html_cleaning_engine_v1() -> Dict[str, Any]:
    return {
        "engine": "html_cleaning_engine_v1",
        "stage": "HTML Cleaner",
        "input": "Raw HTML",
        "output": "Cleaned HTML",
        "removes": REMOVED_TAGS_V1,
        "does_not_extract_article": True,
        "does_not_normalize_content": True,
    }
