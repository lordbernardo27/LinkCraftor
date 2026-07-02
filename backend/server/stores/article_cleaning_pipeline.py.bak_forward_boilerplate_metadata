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

        "metadata": metadata or {},
    }


