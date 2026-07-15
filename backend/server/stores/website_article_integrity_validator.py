from __future__ import annotations

import hashlib
import re
from collections import Counter
from typing import Any, Dict, List


ENGINE_NAME = (
    "website_article_integrity_validator_v1_non_mutating"
)


def _normalize_newlines_v1(
    value: str,
) -> str:
    """
    Normalize operating-system newline encoding only.

    Article wording, block boundaries and order are not changed.
    """

    return (
        str(value or "")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )


def _blocks_v1(
    value: str,
) -> List[str]:
    return [
        block.strip()
        for block in re.split(
            r"\n[ \t]*\n",
            str(value or "").strip(),
        )
        if block.strip()
    ]


def _tokens_v1(
    value: str,
) -> List[str]:
    return re.findall(
        r"\b[\w?'-]+\b",
        str(value or ""),
        flags=re.UNICODE,
    )


def _printable_ratio_v1(
    value: str,
) -> float:
    text = str(value or "")

    if not text:
        return 1.0

    printable_count = sum(
        1
        for character in text
        if (
            character.isprintable()
            or character in "\n\r\t"
        )
    )

    return printable_count / len(text)


def _duplicate_block_ratio_v1(
    blocks: List[str],
) -> float:
    if not blocks:
        return 0.0

    normalized = [
        re.sub(
            r"\s+",
            " ",
            block.casefold(),
        ).strip()
        for block in blocks
    ]

    counts = Counter(normalized)

    duplicate_instances = sum(
        count - 1
        for count in counts.values()
        if count > 1
    )

    return duplicate_instances / len(blocks)


def _contains_html_leakage_v1(
    value: str,
) -> bool:
    text = str(value or "")

    return bool(
        re.search(
            r"<\s*/?\s*"
            r"(?:html|body|article|main|section|div|p|h[1-6]|"
            r"script|style|nav|footer|aside|iframe)"
            r"\b[^>]*>",
            text,
            flags=re.IGNORECASE,
        )
    )


def _stable_hash_v1(
    value: str,
) -> str:
    return hashlib.sha256(
        str(value or "").encode("utf-8")
    ).hexdigest()


def build_website_article_integrity_result_v1(
    *,
    raw_main_html: str,
    raw_article_text: str,
    headings: List[str] | None = None,
    title: str = "",
    url: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Validate an already-reconstructed UDARE article without editing it.

    Compatibility rule:
    The function returns cleaned_article_text because existing website
    orchestration code currently consumes that key. Despite the legacy
    field name, the value is the untouched UDARE article body.

    This validator never:
    - removes text;
    - rewrites sentences;
    - changes word order;
    - deduplicates blocks;
    - collapses paragraph boundaries;
    - interprets phrases as boilerplate.
    """

    original_text = str(
        raw_article_text or ""
    )

    normalized_newline_text = (
        _normalize_newlines_v1(
            original_text
        )
    )

    # UDARE currently emits LF newlines. This check protects against
    # accidental mutation while allowing CRLF-to-LF normalization.
    original_tokens = _tokens_v1(
        original_text
    )

    output_tokens = _tokens_v1(
        normalized_newline_text
    )

    blocks = _blocks_v1(
        normalized_newline_text
    )

    heading_list = [
        str(heading).strip()
        for heading in list(headings or [])
        if str(heading).strip()
    ]

    word_count = len(output_tokens)
    block_count = len(blocks)
    printable_ratio = _printable_ratio_v1(
        normalized_newline_text
    )

    duplicate_ratio = (
        _duplicate_block_ratio_v1(
            blocks
        )
    )

    html_leakage = (
        _contains_html_leakage_v1(
            normalized_newline_text
        )
    )

    checks = {
        "content_present":
            bool(normalized_newline_text.strip()),

        "minimum_article_words":
            word_count >= 20,

        "article_block_structure":
            block_count >= 2,

        "word_sequence_preserved":
            original_tokens == output_tokens,

        "printable_text":
            printable_ratio >= 0.98,

        "no_html_leakage":
            not html_leakage,

        "duplicate_block_ratio_acceptable":
            duplicate_ratio <= 0.20,
    }

    passed = all(
        checks.values()
    )

    warnings: List[str] = []
    errors: List[str] = []

    if word_count < 150:
        warnings.append(
            "ARTICLE_BODY_BELOW_150_WORDS"
        )

    if block_count < 5:
        warnings.append(
            "LOW_ARTICLE_BLOCK_COUNT"
        )

    if duplicate_ratio > 0:
        warnings.append(
            "DUPLICATE_BLOCKS_DETECTED"
        )

    if not checks["content_present"]:
        errors.append(
            "EMPTY_ARTICLE_BODY"
        )

    if not checks["word_sequence_preserved"]:
        errors.append(
            "WORD_SEQUENCE_CHANGED"
        )

    if html_leakage:
        errors.append(
            "HTML_LEAKAGE_DETECTED"
        )

    if not checks["printable_text"]:
        errors.append(
            "INVALID_TEXT_ENCODING"
        )

    metadata_result = {
        **dict(metadata or {}),
        "article_integrity": {
            "engine": ENGINE_NAME,
            "mode": "non_mutating_validation",
            "passed": passed,
            "checks": checks,
            "input_hash":
                _stable_hash_v1(original_text),
            "output_hash":
                _stable_hash_v1(
                    normalized_newline_text
                ),
            "content_modified":
                original_text
                != normalized_newline_text,
            "word_sequence_preserved":
                original_tokens == output_tokens,
        },
    }

    return {
        "status":
            "validated"
            if passed
            else "validation_failed",

        "ok": passed,
        "passed": passed,
        "engine": ENGINE_NAME,

        "pipeline_version": ENGINE_NAME,
        "cleaning_version":
            "not_applicable_cleaner_retired",

        "title": str(title or ""),
        "url": str(url or ""),

        # Compatibility contract for existing callers.
        # This is the original reconstructed body, not cleaned text.
        "raw_main_html":
            str(raw_main_html or ""),
        "raw_article_text":
            original_text,
        "cleaned_article_text":
            normalized_newline_text,

        "article_body":
            normalized_newline_text,
        "content_body":
            normalized_newline_text,

        "headings":
            heading_list,
        "paragraphs":
            blocks,

        # No content is removed by validation.
        "removed_sections": [],

        "checks": checks,
        "warnings": warnings,
        "errors": errors,

        "statistics": {
            "word_count": word_count,
            "paragraph_count": block_count,
            "block_count": block_count,
            "heading_count":
                len(heading_list),
            "duplicate_block_ratio":
                round(
                    duplicate_ratio,
                    6,
                ),
            "printable_ratio":
                round(
                    printable_ratio,
                    6,
                ),
            "html_leakage":
                html_leakage,
            "word_sequence_preserved":
                original_tokens
                == output_tokens,
            "content_modified":
                original_text
                != normalized_newline_text,
            "input_length":
                len(original_text),
            "output_length":
                len(
                    normalized_newline_text
                ),
            "removed_word_count": 0,
            "removed_section_count": 0,
        },

        "cleaning_report": {
            "cleaner_retired": True,
            "replacement_engine":
                ENGINE_NAME,
            "mode":
                "non_mutating_validation",
            "content_modified":
                original_text
                != normalized_newline_text,
            "word_sequence_preserved":
                original_tokens
                == output_tokens,
            "removed_length": 0,
            "removed_word_count": 0,
        },

        "metadata":
            metadata_result,
    }


def explain_website_article_integrity_validator_v1(
) -> Dict[str, Any]:
    return {
        "engine": ENGINE_NAME,
        "responsibility": (
            "Validate reconstructed website article bodies "
            "without modifying their content."
        ),
        "modifies_article_body": False,
        "removes_content": False,
        "rewrites_content": False,
        "checks": [
            "content present",
            "minimum article length",
            "article block structure",
            "word sequence preservation",
            "printable text",
            "HTML leakage",
            "duplicate block ratio",
        ],
        "canonical_flow": [
            "Raw HTML Store",
            "UDARE v1.4",
            "Website Article Integrity Validator",
            "Universal Content Body Formatter",
            "Website Unified Content",
        ],
    }
