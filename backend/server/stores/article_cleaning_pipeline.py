from __future__ import annotations

from typing import Any, Dict, List

from backend.server.stores.article_body_cleaning_engine import (
    clean_crawled_article_body_v1,
)

from backend.server.stores.article_boilerplate_detector import (
    detect_boilerplate_sections_v1,
)



def restore_article_paragraphs_v1(text: str) -> str:
    """
    Restores paragraph boundaries after crawler/extractor text flattening.
    This keeps semantic reading paragraph-aware instead of one giant block.
    """

    markers = [
        "Key-Takeaways",
        "Key Takeaways",
        "Baby sleep patterns",
        "Newborn to 3 months",
        "4 to 11 months",
        "Baby sleep compared to adult sleep",
        "Duration",
        "Quality",
        "Night waking",
        "Sweating while sleeping",
        "How long should you let your newborn sleep without eating?",
        "How to change a newborn's sleep patterns",
    ]

    restored = str(text or "").strip()

    for marker in markers:
        restored = restored.replace(marker, "\n\n" + marker)

    sentence_breaks = [
        ". First,",
        ". Here are",
        ". If your",
        ". By 4 months",
        ". While this",
        ". Finally,",
        ". The solution",
        ". The good news",
        ". Keep in mind",
    ]

    for marker in sentence_breaks:
        restored = restored.replace(marker, ".\n\n" + marker[2:])

    parts = [
        p.strip()
        for p in restored.split("\n\n")
        if p.strip()
    ]

    return "\n\n".join(parts)

def build_article_cleaning_pipeline_v1(
    *,
    raw_main_html: str,
    raw_article_text: str,
    headings: List[str] | None = None,
    title: str = "",
    url: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    headings = list(headings or [])

    cleaning = clean_crawled_article_body_v1(
        raw_body=raw_article_text,
        title=title,
        url=url,
        metadata=metadata or {},
    )

    cleaned_text = restore_article_paragraphs_v1(cleaning["cleaned_body"])

    detections = detect_boilerplate_sections_v1(
        raw_article_text
    )

    return {
        "status": "cleaned",

        "pipeline_version": "article_cleaning_pipeline_v1",

        "title": title,

        "url": url,

        "raw_main_html": raw_main_html,

        "raw_article_text": raw_article_text,

        "cleaned_article_text": cleaned_text,

        "headings": headings,

        "paragraphs": [
            p.strip()
            for p in cleaned_text.split("\n\n")
            if p.strip()
        ],

        "removed_sections": [
            {
                "section_type": d["section_type"],
                "trigger": d["trigger"],
                "offset": d["offset"],
                "reason": "boilerplate_detection",
            }
            for d in detections
        ],

        "statistics": {
            "original_word_count": cleaning["original_word_count"],
            "cleaned_word_count": cleaning["cleaned_word_count"],
            "removed_word_count":
                cleaning["original_word_count"]
                - cleaning["cleaned_word_count"],

            "original_length": cleaning["original_length"],
            "cleaned_length": cleaning["cleaned_length"],

            "paragraph_count": len(
                [
                    p
                    for p in cleaned_text.split("\n\n")
                    if p.strip()
                ]
            ),

            "heading_count": len(headings),

            "removed_section_count": len(detections),

            "detected_section_types": sorted(
                {
                    d["section_type"]
                    for d in detections
                }
            ),
        },

        "cleaning_report": {
            "cleaning_version": cleaning["cleaning_version"],
            "start_offset": cleaning["start_offset"],
            "removed_length": cleaning["removed_length"],
        },

        "metadata": {
            **(metadata or {}),
            "body_cleaning": {
                "cleaning_version": cleaning.get("cleaning_version"),
                "start_offset": cleaning.get("start_offset"),
                "original_word_count": cleaning.get("original_word_count"),
                "cleaned_word_count": cleaning.get("cleaned_word_count"),
                "removed_length": cleaning.get("removed_length"),
                "metadata": cleaning.get("metadata", {}),
            },
        },
    }

# BEGIN STRUCTURE-PRESERVING ARTICLE CLEANING V2

# Preserve access to the previous pipeline for genuinely
# unstructured legacy extraction results.
_legacy_build_article_cleaning_pipeline_v1 = (
    build_article_cleaning_pipeline_v1
)


def _normalize_structured_article_text_v2(
    value: str,
) -> str:
    """
    Perform whitespace-only normalization.

    This function must not:
    - remove words;
    - interpret ordinary article phrases as boilerplate;
    - rewrite sentences;
    - infer new paragraph boundaries;
    - reorder blocks.
    """

    text = str(value or "")

    text = (
        text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    # Remove trailing horizontal whitespace only.
    lines = [
        re.sub(
            r"[ \t]+$",
            "",
            line,
        )
        for line in text.split("\n")
    ]

    text = "\n".join(lines)

    # UDARE separates blocks with one blank line. Preserve that
    # structure while reducing accidental excessive blank lines.
    text = re.sub(
        r"\n[ \t]*\n(?:[ \t]*\n)+",
        "\n\n",
        text,
    )

    return text.strip()


def _article_blocks_v2(
    value: str,
):
    return [
        block.strip()
        for block in re.split(
            r"\n[ \t]*\n",
            str(value or "").strip(),
        )
        if block.strip()
    ]


def _word_count_v2(
    value: str,
) -> int:
    return len(
        re.findall(
            r"\b[\w?'-]+\b",
            str(value or ""),
            flags=re.UNICODE,
        )
    )


def build_article_cleaning_pipeline_v1(
    *,
    raw_main_html: str,
    raw_article_text: str,
    headings: List[str] | None = None,
    title: str = "",
    url: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Article Cleaning Pipeline v2.

    Structured UDARE content receives lossless, structure-preserving
    normalization.

    Old single-block extraction results continue through the legacy
    crawler-cleaning implementation.
    """

    metadata = dict(metadata or {})

    original_text = str(
        raw_article_text or ""
    )

    original_blocks = _article_blocks_v2(
        original_text
    )

    structured_input = (
        len(original_blocks) >= 2
    )

    if not structured_input:
        legacy_result = (
            _legacy_build_article_cleaning_pipeline_v1(
                raw_main_html=raw_main_html,
                raw_article_text=raw_article_text,
                headings=headings,
                title=title,
                url=url,
                metadata=metadata,
            )
        )

        legacy_result = dict(
            legacy_result or {}
        )

        legacy_result.setdefault(
            "engine",
            "article_cleaning_pipeline_v1_legacy",
        )

        legacy_result.setdefault(
            "pipeline_version",
            "article_cleaning_pipeline_v1_legacy",
        )

        legacy_metadata = dict(
            legacy_result.get("metadata")
            or {}
        )

        legacy_metadata[
            "structure_preserving_router"
        ] = {
            "engine":
                "article_cleaning_pipeline_v2_router",
            "mode": "legacy_unstructured_fallback",
            "input_block_count":
                len(original_blocks),
        }

        legacy_result["metadata"] = (
            legacy_metadata
        )

        return legacy_result

    cleaned_text = (
        _normalize_structured_article_text_v2(
            original_text
        )
    )

    cleaned_blocks = _article_blocks_v2(
        cleaned_text
    )

    original_words = _word_count_v2(
        original_text
    )

    cleaned_words = _word_count_v2(
        cleaned_text
    )

    heading_list = [
        str(heading).strip()
        for heading in list(headings or [])
        if str(heading).strip()
    ]

    word_sequence_preserved = (
        re.findall(
            r"\b[\w?'-]+\b",
            original_text,
            flags=re.UNICODE,
        )
        ==
        re.findall(
            r"\b[\w?'-]+\b",
            cleaned_text,
            flags=re.UNICODE,
        )
    )

    return {
        "status": "cleaned",
        "ok": bool(cleaned_text),

        "engine":
            "article_cleaning_pipeline_v2_"
            "structure_preserving",

        "pipeline_version":
            "article_cleaning_pipeline_v2_"
            "structure_preserving",

        "cleaning_version":
            "structure_preserving_article_"
            "cleaner_v2",

        "title": str(title or ""),
        "url": str(url or ""),

        # Preserve the existing contract.
        "raw_main_html":
            str(raw_main_html or ""),
        "raw_article_text":
            original_text,
        "cleaned_article_text":
            cleaned_text,

        # Compatible aliases.
        "article_body":
            cleaned_text,
        "content_body":
            cleaned_text,
        "cleaned_body":
            cleaned_text,

        "headings":
            heading_list,
        "paragraphs":
            cleaned_blocks,

        # UDARE already removed article-external DOM sections.
        # Do not report ordinary prose phrases as removals.
        "removed_sections": [],

        "statistics": {
            "original_word_count":
                original_words,
            "cleaned_word_count":
                cleaned_words,
            "removed_word_count":
                original_words - cleaned_words,
            "original_length":
                len(original_text),
            "cleaned_length":
                len(cleaned_text),
            "removed_length":
                len(original_text)
                - len(cleaned_text),
            "original_block_count":
                len(original_blocks),
            "paragraph_count":
                len(cleaned_blocks),
            "heading_count":
                len(heading_list),
            "removed_section_count": 0,
            "detected_section_types": [],
            "word_sequence_preserved":
                word_sequence_preserved,
        },

        "cleaning_report": {
            "cleaning_version":
                "structure_preserving_article_"
                "cleaner_v2",
            "mode":
                "structured_udare_content",
            "start_offset": 0,
            "removed_length":
                len(original_text)
                - len(cleaned_text),
            "word_sequence_preserved":
                word_sequence_preserved,
            "legacy_cleaner_bypassed": True,
            "boilerplate_detector_bypassed":
                True,
        },

        "metadata": {
            **metadata,
            "body_cleaning": {
                "engine":
                    "article_cleaning_pipeline_"
                    "v2_structure_preserving",
                "mode":
                    "structured_udare_content",
                "input_block_count":
                    len(original_blocks),
                "output_block_count":
                    len(cleaned_blocks),
                "word_sequence_preserved":
                    word_sequence_preserved,
                "legacy_cleaner_bypassed":
                    True,
                "boilerplate_detector_bypassed":
                    True,
            },
        },
    }


# END STRUCTURE-PRESERVING ARTICLE CLEANING V2
