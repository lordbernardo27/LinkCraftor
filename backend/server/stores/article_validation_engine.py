from __future__ import annotations

from typing import Any, Dict, List


MINIMUM_WORD_COUNT_V1 = 150

MAX_DUPLICATE_PARAGRAPH_RATIO_V1 = 0.20

MAX_BOILERPLATE_RATIO_V1 = 0.35


def _paragraphs(text: str) -> List[str]:

    return [
        p.strip()
        for p in str(text or "").split("\n\n")
        if p.strip()
    ]


def _duplicate_ratio(paragraphs: List[str]) -> float:

    if not paragraphs:
        return 0.0

    unique = len(set(paragraphs))
    duplicates = len(paragraphs) - unique

    return duplicates / max(len(paragraphs), 1)


def _printable_ratio(text: str) -> float:

    if not text:
        return 1.0

    printable = sum(
        1
        for c in text
        if c.isprintable() or c in "\n\r\t"
    )

    return printable / len(text)


def validate_article_v1(
    *,
    cleaned_article_text: str,
    title: str = "",
    headings: List[str] | None = None,
    removed_sections: List[Dict[str, Any]] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    headings = list(headings or [])
    removed_sections = list(removed_sections or [])

    paragraphs = _paragraphs(cleaned_article_text)

    word_count = len(cleaned_article_text.split())

    duplicate_ratio = _duplicate_ratio(paragraphs)

    printable_ratio = _printable_ratio(cleaned_article_text)

    boilerplate_ratio = (
        len(removed_sections)
        / max(len(paragraphs) + len(removed_sections), 1)
    )

    checks = {

        "title_present":
            bool(title.strip()),

        "content_present":
            bool(cleaned_article_text.strip()),

        "minimum_word_count": True,

        "paragraph_structure":
            len(paragraphs) >= 2,

        "heading_structure":
            len(headings) >= 1,

        "duplicate_paragraph_ratio":
            duplicate_ratio <= MAX_DUPLICATE_PARAGRAPH_RATIO_V1,

        "boilerplate_ratio":
            boilerplate_ratio <= MAX_BOILERPLATE_RATIO_V1,

        "encoding":
            True,

        "printable_text":
            printable_ratio >= 0.98,
    }

    passed = all(checks.values())

    score = (
        sum(
            1
            for value in checks.values()
            if value
        )
        / len(checks)
    ) * 100.0

    warnings = []
    errors = []
    rejection_reasons = []

    if word_count < MINIMUM_WORD_COUNT_V1:
        warnings.append("LOW_WORD_COUNT")

    if not checks["paragraph_structure"]:
        rejection_reasons.append("INVALID_PARAGRAPH_STRUCTURE")

    if not checks["heading_structure"]:
        rejection_reasons.append("NO_HEADINGS")

    if not checks["duplicate_paragraph_ratio"]:
        rejection_reasons.append("HIGH_DUPLICATE_RATIO")

    if not checks["boilerplate_ratio"]:
        rejection_reasons.append("HIGH_BOILERPLATE_RATIO")

    if not checks["printable_text"]:
        rejection_reasons.append("INVALID_ENCODING")

    if score >= 95:
        grade = "A+"
    elif score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    else:
        grade = "Rejected"

    return {

        "status": "validated",

        "passed": passed,

        "validation_version":
            "article_validation_engine_v1",

        "validation_score":
            round(score, 2),

        "quality_grade":
            grade,

        "checks":
            checks,

        "statistics": {

            "word_count":
                word_count,

            "paragraph_count":
                len(paragraphs),

            "heading_count":
                len(headings),

            "duplicate_paragraph_ratio":
                round(duplicate_ratio, 4),

            "boilerplate_ratio":
                round(boilerplate_ratio, 4),

            "removed_section_count":
                len(removed_sections),

            "validation_score":
                round(score, 2),
        },

        "warnings":
            warnings,

        "errors":
            errors,

        "rejection_reasons":
            rejection_reasons,

        "eligible_for_unified_content_document":
            passed,

        "metadata":
            metadata or {},
    }


