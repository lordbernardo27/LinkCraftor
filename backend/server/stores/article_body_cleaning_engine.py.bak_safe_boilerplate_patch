from __future__ import annotations

import html
import re
from typing import Any, Dict, List


ARTICLE_END_MARKERS_V1 = [
    "Was this article helpful",
    "Updates history",
    "Review this article",
]


EDITORIAL_METADATA_PATTERNS_V1 = [
    r"\bby\s+[A-Z][A-Za-z .,'-]+",
    r"\bmedically reviewed by\s+[A-Z][A-Za-z .,'-]+",
    r"\breviewed by\s+[A-Z][A-Za-z .,'-]+",
    r"\bfact checked by\s+[A-Z][A-Za-z .,'-]+",
    r"\bmedical review policy\b.*?(?=After spending|Key Takeaways|Newborn|Baby|$)",
    r"\beditorial policy\b.*?(?=After spending|Key Takeaways|Newborn|Baby|$)",
    r"\blearn more about our editorial.*?policies\s*\.?",
    r"\blatest update:\s*.*?(?=After spending|Key Takeaways|Newborn|Baby|$)",
    r"\|\s*[A-Z][a-z]+ \d{1,2}, \d{4}",
]


def decode_html_entities_v1(text: str) -> str:
    return html.unescape(str(text or ""))


def normalize_spacing_v1(text: str) -> str:
    text = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_editorial_metadata_v1(text: str) -> str:
    cleaned = str(text or "")

    for pattern in EDITORIAL_METADATA_PATTERNS_V1:
        cleaned = re.sub(
            pattern,
            " ",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL,
        )

    return normalize_spacing_v1(cleaned)



def trim_to_true_article_start_v1(text: str) -> str:
    markers = [
        "after spending",
        "key-takeaways",
        "key takeaways",
        "first, the good news",
        "newborn to 3 months",
    ]

    lower = str(text or "").lower()
    candidates = []

    for marker in markers:
        idx = lower.find(marker)
        if idx >= 0:
            candidates.append(idx)

    if not candidates:
        return normalize_spacing_v1(text)

    start = min(candidates)
    return normalize_spacing_v1(str(text or "")[start:])

def find_best_article_start_v1(text: str, title: str = "") -> int:
    lower = text.lower()

    if title:
        idx = lower.find(str(title).strip().lower())
        if idx >= 0:
            return idx

    fallback_markers = [
        "after spending",
        "key-takeaways",
        "key takeaways",
        "baby sleep patterns by age",
    ]

    candidates: List[int] = []

    for marker in fallback_markers:
        idx = lower.find(marker.lower())
        if idx >= 0:
            candidates.append(idx)

    return min(candidates) if candidates else 0


def find_safe_article_end_v1(text: str) -> int:
    lower = text.lower()
    candidates: List[int] = []

    for marker in ARTICLE_END_MARKERS_V1:
        idx = lower.find(marker.lower())
        if idx > 0:
            candidates.append(idx)

    return min(candidates) if candidates else len(text)


def clean_crawled_article_body_v1(
    *,
    raw_body: str,
    title: str = "",
    url: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    original = str(raw_body or "")
    decoded = decode_html_entities_v1(original)
    normalized = normalize_spacing_v1(decoded)

    start = find_best_article_start_v1(normalized, title=title)
    sliced = normalized[start:]

    end = find_safe_article_end_v1(sliced)
    sliced = sliced[:end]

    cleaned = remove_editorial_metadata_v1(sliced)
    cleaned = trim_to_true_article_start_v1(cleaned)
    cleaned = normalize_spacing_v1(cleaned)

    return {
        "status": "cleaned",
        "title": title,
        "url": url,
        "original_length": len(original),
        "decoded_length": len(decoded),
        "cleaned_length": len(cleaned),
        "original_word_count": len(original.split()),
        "cleaned_word_count": len(cleaned.split()),
        "removed_length": max(0, len(original) - len(cleaned)),
        "start_offset": start,
        "cleaned_body": cleaned,
        "metadata": metadata or {},
        "cleaning_version": "article_body_cleaner_v1_editorial_metadata_removed",
    }


