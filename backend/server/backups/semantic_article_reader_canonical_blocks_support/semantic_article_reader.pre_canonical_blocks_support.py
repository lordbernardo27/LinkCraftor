from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional


_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_BULLET_RE = re.compile(r"^\s*[-*•]\s+(.+)$")
_NUMBERED_RE = re.compile(r"^\s*\d+[\.)]\s+(.+)$")
_QUOTE_RE = re.compile(r"^\s*>\s+(.+)$")
_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)|<img\b", re.IGNORECASE)
_CODE_RE = re.compile(r"^\s*```|`[^`]+`|<code\b", re.IGNORECASE)
_TABLE_RE = re.compile(r"^\s*\|.+\|\s*$")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def _split_sentences(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    return [s.strip() for s in _SENTENCE_RE.split(text) if s.strip()]


def _line_offsets(article_text: str) -> List[Dict[str, int]]:
    offsets = []
    cursor = 0

    for line in article_text.splitlines():
        start = cursor
        end = cursor + len(line)
        offsets.append({"start_char": start, "end_char": end})
        cursor = end + 1

    return offsets


def _classify_line(line: str) -> Dict[str, Any]:
    stripped = line.strip()

    heading = _HEADING_RE.match(stripped)
    if heading:
        return {
            "block_type": "heading",
            "heading_level": len(heading.group(1)),
            "list_type": None,
            "text": heading.group(2).strip(),
        }

    bullet = _BULLET_RE.match(stripped)
    if bullet:
        return {
            "block_type": "list_item",
            "list_type": "bullet",
            "heading_level": None,
            "text": bullet.group(1).strip(),
        }

    numbered = _NUMBERED_RE.match(stripped)
    if numbered:
        return {
            "block_type": "list_item",
            "list_type": "numbered",
            "heading_level": None,
            "text": numbered.group(1).strip(),
        }

    quote = _QUOTE_RE.match(stripped)
    if quote:
        return {
            "block_type": "quote",
            "list_type": None,
            "heading_level": None,
            "text": quote.group(1).strip(),
        }

    if _IMAGE_RE.search(stripped):
        return {
            "block_type": "image",
            "list_type": None,
            "heading_level": None,
            "text": stripped,
        }

    if _TABLE_RE.match(stripped):
        return {
            "block_type": "table",
            "list_type": None,
            "heading_level": None,
            "text": stripped,
        }

    if _CODE_RE.search(stripped):
        return {
            "block_type": "code",
            "list_type": None,
            "heading_level": None,
            "text": stripped,
        }

    lowered = stripped.lower()
    if lowered.startswith(("faq:", "q:", "question:")):
        block_type = "faq"
    elif lowered.startswith(("note:", "warning:", "important:", "tip:")):
        block_type = "callout"
    elif "reference" in lowered or lowered in {"sources", "source", "references"}:
        block_type = "reference"
    else:
        block_type = "paragraph"

    return {
        "block_type": block_type,
        "list_type": None,
        "heading_level": None,
        "text": stripped,
    }


def _contains_links(text: str) -> bool:
    return "http://" in text or "https://" in text or "<a " in text.lower()


def _structural_metadata(text: str, *, sentence_count: int = 0, heading_level: Optional[int] = None) -> Dict[str, Any]:
    lowered = text.lower()
    return {
        "heading_level": heading_level,
        "word_count": _word_count(text),
        "character_count": len(text),
        "sentence_count": sentence_count,
        "contains_links": _contains_links(text),
        "contains_bold": "**" in text or "<strong>" in lowered or "<b>" in lowered,
        "contains_italic": "*" in text or "<em>" in lowered or "<i>" in lowered,
        "contains_code": "`" in text or "<code" in lowered,
        "contains_image": bool(_IMAGE_RE.search(text)),
        "contains_references": "reference" in lowered or "sources" in lowered,
    }


def _validate_semantic_reading_model_v1(model: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []

    sections = model.get("sections", [])
    blocks = model.get("blocks", [])
    reading_order = model.get("reading_order", [])

    section_ids = [s["section_id"] for s in sections]
    block_ids = [b["block_id"] for b in blocks]

    if len(section_ids) != len(set(section_ids)):
        errors.append("duplicate section IDs detected")

    if len(block_ids) != len(set(block_ids)):
        errors.append("duplicate block IDs detected")

    if len(reading_order) != len(blocks):
        errors.append("reading order length does not match block count")

    if set(reading_order) != set(block_ids):
        errors.append("reading order does not contain every block exactly once")

    section_id_set = set(section_ids)
    block_id_set = set(block_ids)

    for block in blocks:
        if block["section_id"] not in section_id_set:
            errors.append(f"orphan block detected: {block['block_id']}")

    for section in sections:
        for block_id in section.get("block_ids", []):
            if block_id not in block_id_set:
                errors.append(f"section references missing block: {block_id}")

    for index, block in enumerate(blocks):
        previous_expected = blocks[index - 1]["block_id"] if index > 0 else None
        next_expected = blocks[index + 1]["block_id"] if index < len(blocks) - 1 else None

        if block.get("previous_block_id") != previous_expected:
            errors.append(f"bad previous pointer: {block['block_id']}")

        if block.get("next_block_id") != next_expected:
            errors.append(f"bad next pointer: {block['block_id']}")

    paragraph_ids = []
    sentence_ids = []

    for block in blocks:
        paragraph_id = block.get("paragraph_id")
        if paragraph_id:
            paragraph_ids.append(paragraph_id)

        for sentence in block.get("sentences", []):
            sentence_ids.append(sentence["sentence_id"])

            if sentence["section_id"] != block["section_id"]:
                errors.append(f"sentence section mismatch: {sentence['sentence_id']}")

            if paragraph_id and sentence["paragraph_id"] != paragraph_id:
                errors.append(f"sentence paragraph mismatch: {sentence['sentence_id']}")

    if len(sentence_ids) != len(set(sentence_ids)):
        errors.append("duplicate sentence IDs detected")

    return {
        "valid": not errors,
        "errors": errors,
        "checks": [
            "no duplicate section IDs",
            "no duplicate block IDs",
            "reading order contains every block exactly once",
            "every block belongs to one section",
            "every section block reference exists",
            "previous and next block pointers are reciprocal",
            "sentences belong to their parent paragraph and section",
            "no duplicate sentence IDs",
        ],
    }


def read_semantic_article_v1(
    article_text: str,
    *,
    article_id: Optional[str] = None,
    source_url: Optional[str] = None,
    title: Optional[str] = None,
    canonical_structure: Optional[Dict[str, Any]] = None,
    canonical_h1: Optional[str] = None,
) -> Dict[str, Any]:
    article_text = article_text or ""
    normalized_lines = [line.rstrip() for line in article_text.splitlines()]
    line_offsets = _line_offsets(article_text)

    canonical_heading_by_char: Dict[int, Dict[str, Any]] = {}
    canonical_structure_used = False

    if isinstance(canonical_structure, dict):
        heading_map = canonical_structure.get("heading_map")

        if isinstance(heading_map, list) and heading_map:
            for entry in heading_map:
                if not isinstance(entry, dict):
                    continue

                char_position = entry.get("char_position")
                heading_text = entry.get("heading")

                if (
                    not isinstance(char_position, int)
                    or char_position < 0
                    or not isinstance(heading_text, str)
                    or not heading_text.strip()
                ):
                    continue

                raw_level = entry.get("level")
                heading_level = (
                    raw_level
                    if isinstance(raw_level, int) and 1 <= raw_level <= 6
                    else None
                )

                if (
                    heading_level is None
                    and isinstance(canonical_h1, str)
                    and canonical_h1.strip()
                    and heading_text.strip() == canonical_h1.strip()
                ):
                    heading_level = 1

                canonical_heading_by_char[char_position] = {
                    "text": heading_text.strip(),
                    "heading_level": heading_level,
                }

            canonical_structure_used = bool(canonical_heading_by_char)

    indexed_lines = [
        {
            "original_line_index": index,
            "line": line,
            "start_char": line_offsets[index]["start_char"] if index < len(line_offsets) else 0,
            "end_char": line_offsets[index]["end_char"] if index < len(line_offsets) else 0,
        }
        for index, line in enumerate(normalized_lines)
        if line.strip()
    ]

    if not article_id:
        article_id = _stable_id("article", source_url or "", title or "", article_text[:500])

    sections: List[Dict[str, Any]] = []
    blocks: List[Dict[str, Any]] = []
    reading_order: List[str] = []

    current_section: Optional[Dict[str, Any]] = None
    section_stack: List[Dict[str, Any]] = []

    section_index = -1
    paragraph_index = 0
    sentence_global_index = 0

    for item in indexed_lines:
        raw_index = item["original_line_index"]
        line = item["line"]

        canonical_heading = canonical_heading_by_char.get(
            item["start_char"]
        )

        if canonical_heading is not None:
            if line.strip() != canonical_heading["text"]:
                raise ValueError(
                    "Canonical UUCD heading does not match Body Store text "
                    f"at character position {item['start_char']}."
                )

            classified = {
                "block_type": "heading",
                "heading_level": canonical_heading["heading_level"],
                "list_type": None,
                "text": canonical_heading["text"],
            }
        else:
            classified = _classify_line(line)

        block_type = classified["block_type"]
        text = classified["text"]
        heading_level = classified.get("heading_level")

        if block_type == "heading" or current_section is None:
            if block_type == "heading":
                section_index += 1
                section_title = text

                if canonical_heading is not None:
                    section_heading_level = heading_level
                else:
                    section_heading_level = heading_level or 1
            else:
                section_index += 1
                section_title = title or "Introduction"
                section_heading_level = 1

            if isinstance(section_heading_level, int):
                while (
                    section_stack
                    and isinstance(
                        section_stack[-1].get("heading_level"),
                        int,
                    )
                    and section_stack[-1]["heading_level"]
                    >= section_heading_level
                ):
                    section_stack.pop()

                parent_section_id = (
                    section_stack[-1]["section_id"]
                    if section_stack
                    else None
                )
            else:
                section_stack.clear()
                parent_section_id = None

            current_section = {
                "section_id": _stable_id("section", article_id, section_index, section_title),
                "article_id": article_id,
                "section_index": section_index,
                "section_title": section_title,
                "heading_level": section_heading_level,
                "section_depth": section_heading_level,
                "parent_section_id": parent_section_id,
                "children_section_ids": [],
                "block_ids": [],
                "paragraph_ids": [],
                "start_line": raw_index,
                "end_line": raw_index,
                "start_char": item["start_char"],
                "end_char": item["end_char"],
                "metadata": {
                    "word_count": 0,
                    "character_count": 0,
                    "paragraph_count": 0,
                    "sentence_count": 0,
                    "block_count": 0,
                    "heading_level": section_heading_level,
                    "section_word_count": 0,
                    "section_sentence_count": 0,
                    "section_paragraph_count": 0,
                    "section_heading_level": section_heading_level,
                },
            }

            sections.append(current_section)

            if parent_section_id:
                for existing_section in sections:
                    if existing_section["section_id"] == parent_section_id:
                        existing_section["children_section_ids"].append(current_section["section_id"])
                        break

            if isinstance(section_heading_level, int):
                section_stack.append(current_section)

            if block_type == "heading":
                block_id = _stable_id("block", article_id, raw_index, "heading", text)

                block = {
                    "block_id": block_id,
                    "article_id": article_id,
                    "section_id": current_section["section_id"],
                    "paragraph_id": None,
                    "block_index": len(blocks),
                    "source_line_index": raw_index,
                    "start_line": raw_index,
                    "end_line": raw_index,
                    "start_char": item["start_char"],
                    "end_char": item["end_char"],
                    "block_type": "heading",
                    "list_type": None,
                    "heading_depth": section_heading_level,
                    "section_depth": section_heading_level,
                    "block_depth": section_heading_level,
                    "article_progress": 0.0,
                    "text": text,
                    "sentences": [],
                    "metadata": _structural_metadata(text, sentence_count=0, heading_level=section_heading_level),
                }

                blocks.append(block)
                reading_order.append(block_id)

                current_section["block_ids"].append(block_id)
                current_section["end_line"] = raw_index
                current_section["end_char"] = item["end_char"]
                current_section["metadata"]["block_count"] += 1
                current_section["metadata"]["word_count"] += _word_count(text)
                current_section["metadata"]["character_count"] += len(text)
                current_section["metadata"]["section_word_count"] += _word_count(text)

                continue

        block_id = _stable_id("block", article_id, raw_index, block_type, text)
        paragraph_id = _stable_id("paragraph", article_id, paragraph_index, text[:80])
        sentences = []

        split_sentences = _split_sentences(text)

        for sentence_index, sentence in enumerate(split_sentences):
            sentence_id = _stable_id("sentence", article_id, paragraph_id, sentence_index, sentence[:80])
            sentences.append({
                "sentence_id": sentence_id,
                "article_id": article_id,
                "section_id": current_section["section_id"],
                "paragraph_id": paragraph_id,
                "sentence_index": sentence_index,
                "sentence_global_index": sentence_global_index,
                "article_position": len(blocks),
                "text": sentence,
                "metadata": {
                    "word_count": _word_count(sentence),
                    "character_count": len(sentence),
                },
            })
            sentence_global_index += 1

        block_depth = current_section["section_depth"] if current_section else 1

        block = {
            "block_id": block_id,
            "article_id": article_id,
            "section_id": current_section["section_id"],
            "paragraph_id": paragraph_id,
            "block_index": len(blocks),
            "source_line_index": raw_index,
            "start_line": raw_index,
            "end_line": raw_index,
            "start_char": item["start_char"],
            "end_char": item["end_char"],
            "block_type": block_type,
            "list_type": classified.get("list_type"),
            "heading_depth": None,
            "section_depth": current_section["section_depth"],
            "block_depth": block_depth,
            "article_progress": 0.0,
            "text": text,
            "sentences": sentences,
            "metadata": _structural_metadata(text, sentence_count=len(sentences)),
        }

        blocks.append(block)
        reading_order.append(block_id)

        current_section["block_ids"].append(block_id)
        current_section["paragraph_ids"].append(paragraph_id)
        current_section["end_line"] = raw_index
        current_section["end_char"] = item["end_char"]

        current_section["metadata"]["block_count"] += 1
        current_section["metadata"]["paragraph_count"] += 1
        current_section["metadata"]["sentence_count"] += len(sentences)
        current_section["metadata"]["word_count"] += _word_count(text)
        current_section["metadata"]["character_count"] += len(text)
        current_section["metadata"]["section_word_count"] += _word_count(text)
        current_section["metadata"]["section_sentence_count"] += len(sentences)
        current_section["metadata"]["section_paragraph_count"] += 1

        paragraph_index += 1

    total_blocks = len(blocks)

    for index, block in enumerate(blocks):
        block["previous_block_id"] = blocks[index - 1]["block_id"] if index > 0 else None
        block["next_block_id"] = blocks[index + 1]["block_id"] if index < total_blocks - 1 else None
        block["article_progress"] = round(index / max(total_blocks - 1, 1), 4) if total_blocks else 0.0

    block_type_counts: Dict[str, int] = {}
    heading_distribution: Dict[str, int] = {}

    paragraph_lengths = []
    sentence_lengths = []

    for block in blocks:
        block_type_counts[block["block_type"]] = block_type_counts.get(block["block_type"], 0) + 1

        if block["block_type"] == "heading":
            level_key = f"h{block['metadata'].get('heading_level')}"
            heading_distribution[level_key] = heading_distribution.get(level_key, 0) + 1

        if block.get("paragraph_id"):
            paragraph_lengths.append(block["metadata"]["word_count"])

        for sentence in block.get("sentences", []):
            sentence_lengths.append(sentence["metadata"]["word_count"])

    statistics = {
        "sections": len(sections),
        "blocks": len(blocks),
        "paragraphs": paragraph_index,
        "sentences": sentence_global_index,
        "headings": block_type_counts.get("heading", 0),
        "lists": block_type_counts.get("list_item", 0),
        "quotes": block_type_counts.get("quote", 0),
        "tables": block_type_counts.get("table", 0),
        "images": block_type_counts.get("image", 0),
        "code_blocks": block_type_counts.get("code", 0),
        "block_type_counts": block_type_counts,
        "average_paragraph_length": round(mean(paragraph_lengths), 2) if paragraph_lengths else 0,
        "average_sentence_length": round(mean(sentence_lengths), 2) if sentence_lengths else 0,
        "heading_distribution": heading_distribution,
    }

    model = {
        "schema_version": "semantic_article_reader_v1",
        "phase": "4.6.1",
        "patch": "4.6.1A",
        "created_at": _now_iso(),
        "article": {
            "article_id": article_id,
            "title": title,
            "source_url": source_url,
            "body_included": False,
            "navigation": {
                "first_block_id": blocks[0]["block_id"] if blocks else None,
                "last_block_id": blocks[-1]["block_id"] if blocks else None,
                "first_section_id": sections[0]["section_id"] if sections else None,
                "last_section_id": sections[-1]["section_id"] if sections else None,
            },
            "metadata": {
                "line_count": len(indexed_lines),
                "section_count": len(sections),
                "block_count": len(blocks),
                "paragraph_count": paragraph_index,
                "sentence_count": sentence_global_index,
                "word_count": _word_count(article_text),
                "character_count": len(article_text),
            },
        },
        "sections": sections,
        "blocks": blocks,
        "reading_order": reading_order,
        "statistics": statistics,
        "structure_source": (
            "canonical_uucd"
            if canonical_structure_used
            else "line_classifier"
        ),
        "canonical_rule": (
            "The Semantic Article Reader is the canonical source of article structure. "
            "Downstream semantic components must consume this Semantic Reading Model "
            "instead of reparsing raw article text."
        ),
    }

    model["validation"] = _validate_semantic_reading_model_v1(model)

    return model


def save_semantic_article_reading_v1(
    article_text: str,
    output_path: str | Path,
    *,
    article_id: Optional[str] = None,
    source_url: Optional[str] = None,
    title: Optional[str] = None,
) -> Dict[str, Any]:
    model = read_semantic_article_v1(
        article_text,
        article_id=article_id,
        source_url=source_url,
        title=title,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(model, indent=2, ensure_ascii=False), encoding="utf-8")
    return model


def explain_semantic_article_reader_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.1",
        "patch": "4.6.1A",
        "name": "Semantic Article Reader",
        "purpose": "Convert cleaned article text into a deterministic structural reading model.",
        "does": [
            "preserves article order",
            "detects structural blocks",
            "preserves section boundaries",
            "preserves paragraph order",
            "preserves sentence order",
            "assigns stable IDs",
            "preserves document hierarchy",
            "stores structural metadata",
            "records previous and next block relationships",
            "preserves original text",
            "stores parent and child section relationships",
            "stores character offsets",
            "stores start and end line positions",
            "stores block depth and section depth",
            "stores article progress position",
            "stores document navigation pointers",
            "generates structural statistics",
            "validates structural integrity",
        ],
        "does_not": [
            "extract entities",
            "extract concepts",
            "build semantic relationships",
            "build graphs",
            "score relevance",
            "infer intent",
            "write memory",
            "perform reasoning",
            "generate explanations",
        ],
        "supported_block_types": [
            "heading",
            "paragraph",
            "list_item",
            "quote",
            "table",
            "code",
            "image",
            "callout",
            "faq",
            "reference",
            "unknown",
        ],
        "output": "Semantic Reading Model",
    }
