from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fingerprint(*parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _safe_words(text: str) -> List[str]:
    return [w.strip(".,!?;:()[]{}\"'").lower() for w in (text or "").split() if w.strip()]


def _context_window(blocks: List[Dict[str, Any]], index: int, radius: int = 1) -> Dict[str, Any]:
    previous_blocks = blocks[max(0, index - radius):index]
    next_blocks = blocks[index + 1:index + 1 + radius]

    return {
        "previous_block_ids": [b["block_id"] for b in previous_blocks],
        "next_block_ids": [b["block_id"] for b in next_blocks],
        "previous_text": " ".join(b.get("text", "") for b in previous_blocks).strip(),
        "current_text": blocks[index].get("text", "").strip(),
        "next_text": " ".join(b.get("text", "") for b in next_blocks).strip(),
    }


def _heading_ancestry(section: Dict[str, Any], section_by_id: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    ancestry = []
    current = section

    while current:
        ancestry.append({
            "section_id": current["section_id"],
            "section_title": current["section_title"],
            "heading_level": current["heading_level"],
        })

        parent_id = current.get("parent_section_id")
        current = section_by_id.get(parent_id) if parent_id else None

    return list(reversed(ancestry))


def _breadcrumb(section: Dict[str, Any], section_by_id: Dict[str, Dict[str, Any]]) -> str:
    return " > ".join(item["section_title"] for item in _heading_ancestry(section, section_by_id))


def _build_cross_reference_index(
    sections: List[Dict[str, Any]],
    blocks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    block_to_section = {}
    block_to_paragraph = {}
    paragraph_to_block = {}
    paragraph_to_section = {}
    sentence_to_block = {}
    sentence_to_paragraph = {}
    sentence_to_section = {}
    section_to_blocks = {}
    section_to_paragraphs = {}
    section_to_sentences = {}

    for section in sections:
        section_to_blocks[section["section_id"]] = list(section.get("block_ids", []))
        section_to_paragraphs[section["section_id"]] = list(section.get("paragraph_ids", []))
        section_to_sentences[section["section_id"]] = []

    for block in blocks:
        block_id = block["block_id"]
        section_id = block["section_id"]
        paragraph_id = block.get("paragraph_id")

        block_to_section[block_id] = section_id
        block_to_paragraph[block_id] = paragraph_id

        if paragraph_id:
            paragraph_to_block[paragraph_id] = block_id
            paragraph_to_section[paragraph_id] = section_id

        for sentence in block.get("sentences", []):
            sentence_id = sentence["sentence_id"]

            sentence_to_block[sentence_id] = block_id
            sentence_to_paragraph[sentence_id] = sentence["paragraph_id"]
            sentence_to_section[sentence_id] = section_id
            section_to_sentences.setdefault(section_id, []).append(sentence_id)

    return {
        "block_to_section": block_to_section,
        "block_to_paragraph": block_to_paragraph,
        "paragraph_to_block": paragraph_to_block,
        "paragraph_to_section": paragraph_to_section,
        "sentence_to_block": sentence_to_block,
        "sentence_to_paragraph": sentence_to_paragraph,
        "sentence_to_section": sentence_to_section,
        "section_to_blocks": section_to_blocks,
        "section_to_paragraphs": section_to_paragraphs,
        "section_to_sentences": section_to_sentences,
    }


def build_semantic_context_v1(
    semantic_reading_model: Dict[str, Any],
    *,
    context_radius: int = 1,
) -> Dict[str, Any]:
    article = semantic_reading_model.get("article", {})
    sections = semantic_reading_model.get("sections", [])
    blocks = semantic_reading_model.get("blocks", [])

    block_contexts: List[Dict[str, Any]] = []
    section_contexts: List[Dict[str, Any]] = []
    sentence_contexts: List[Dict[str, Any]] = []

    section_by_id = {s["section_id"]: s for s in sections}
    blocks_by_section: Dict[str, List[Dict[str, Any]]] = {}

    for block in blocks:
        blocks_by_section.setdefault(block["section_id"], []).append(block)

    cross_reference_index = _build_cross_reference_index(sections, blocks)

    document_text = " ".join(b.get("text", "") for b in blocks).strip()

    for index, block in enumerate(blocks):
        section = section_by_id.get(block["section_id"], {})
        section_blocks = blocks_by_section.get(block["section_id"], [])

        window = _context_window(blocks, index, radius=context_radius)
        local_words = _safe_words(
            f"{window['previous_text']} {window['current_text']} {window['next_text']}"
        )

        section_text = " ".join(b.get("text", "") for b in section_blocks).strip()
        ancestry = _heading_ancestry(section, section_by_id) if section else []

        block_contexts.append({
            "block_id": block["block_id"],
            "article_id": block["article_id"],
            "section_id": block["section_id"],
            "paragraph_id": block.get("paragraph_id"),
            "block_index": block["block_index"],
            "block_type": block["block_type"],
            "context_radius": context_radius,
            "context_fingerprint": _fingerprint(
                block["block_id"],
                window["previous_text"],
                window["current_text"],
                window["next_text"],
            ),
            "context": {
                **window,
                "section_text": section_text,
                "document_title": article.get("title"),
                "breadcrumb": _breadcrumb(section, section_by_id) if section else "",
                "heading_ancestry": ancestry,
                "section_entry_block_id": section_blocks[0]["block_id"] if section_blocks else None,
                "section_exit_block_id": section_blocks[-1]["block_id"] if section_blocks else None,
                "document_first_block_id": blocks[0]["block_id"] if blocks else None,
                "document_last_block_id": blocks[-1]["block_id"] if blocks else None,
            },
            "context_metadata": {
                "local_word_count": len(local_words),
                "current_word_count": block.get("metadata", {}).get("word_count", 0),
                "section_word_count": section.get("metadata", {}).get("section_word_count", 0),
                "document_word_count": article.get("metadata", {}).get("word_count", 0),
                "has_previous_context": bool(window["previous_block_ids"]),
                "has_next_context": bool(window["next_block_ids"]),
                "is_section_entry": bool(section_blocks and section_blocks[0]["block_id"] == block["block_id"]),
                "is_section_exit": bool(section_blocks and section_blocks[-1]["block_id"] == block["block_id"]),
                "section_depth": block.get("section_depth"),
                "article_progress": block.get("article_progress"),
                "heading_ancestry_depth": len(ancestry),
            },
        })

        sentences = block.get("sentences", [])

        for sentence_index, sentence in enumerate(sentences):
            previous_sentence = sentences[sentence_index - 1] if sentence_index > 0 else None
            next_sentence = sentences[sentence_index + 1] if sentence_index < len(sentences) - 1 else None

            current_sentence_text = sentence["text"]

            sentence_contexts.append({
                "sentence_id": sentence["sentence_id"],
                "article_id": sentence["article_id"],
                "section_id": sentence["section_id"],
                "paragraph_id": sentence["paragraph_id"],
                "block_id": block["block_id"],
                "sentence_index": sentence["sentence_index"],
                "sentence_global_index": sentence["sentence_global_index"],
                "context_fingerprint": _fingerprint(
                    sentence["sentence_id"],
                    previous_sentence["text"] if previous_sentence else "",
                    current_sentence_text,
                    next_sentence["text"] if next_sentence else "",
                    block.get("text", ""),
                ),
                "context": {
                    "previous_sentence_id": previous_sentence["sentence_id"] if previous_sentence else None,
                    "next_sentence_id": next_sentence["sentence_id"] if next_sentence else None,
                    "previous_sentence_text": previous_sentence["text"] if previous_sentence else "",
                    "current_sentence_text": current_sentence_text,
                    "next_sentence_text": next_sentence["text"] if next_sentence else "",
                    "parent_block_text": block.get("text", ""),
                    "parent_section_title": section.get("section_title"),
                    "breadcrumb": _breadcrumb(section, section_by_id) if section else "",
                    "heading_ancestry": ancestry,
                    "previous_block_text": window["previous_text"],
                    "next_block_text": window["next_text"],
                },
                "context_metadata": {
                    "sentence_word_count": sentence.get("metadata", {}).get("word_count", 0),
                    "parent_block_word_count": block.get("metadata", {}).get("word_count", 0),
                    "has_previous_sentence": previous_sentence is not None,
                    "has_next_sentence": next_sentence is not None,
                    "sentence_is_block_entry": sentence_index == 0,
                    "sentence_is_block_exit": sentence_index == len(sentences) - 1,
                },
            })

    for section in sections:
        section_blocks = blocks_by_section.get(section["section_id"], [])
        section_text = " ".join(b.get("text", "") for b in section_blocks).strip()

        parent_section = section_by_id.get(section.get("parent_section_id"))
        child_sections = [
            section_by_id[child_id]
            for child_id in section.get("children_section_ids", [])
            if child_id in section_by_id
        ]

        previous_section = sections[section["section_index"] - 1] if section["section_index"] > 0 else None
        next_section = sections[section["section_index"] + 1] if section["section_index"] < len(sections) - 1 else None
        ancestry = _heading_ancestry(section, section_by_id)

        section_contexts.append({
            "section_id": section["section_id"],
            "article_id": section["article_id"],
            "section_index": section["section_index"],
            "section_title": section["section_title"],
            "heading_level": section["heading_level"],
            "parent_section_id": section.get("parent_section_id"),
            "children_section_ids": section.get("children_section_ids", []),
            "context_fingerprint": _fingerprint(
                section["section_id"],
                parent_section.get("section_title") if parent_section else "",
                section_text,
                "|".join(s["section_title"] for s in child_sections),
            ),
            "context": {
                "section_text": section_text,
                "parent_section_title": parent_section.get("section_title") if parent_section else None,
                "child_section_titles": [s["section_title"] for s in child_sections],
                "previous_section_id": previous_section["section_id"] if previous_section else None,
                "next_section_id": next_section["section_id"] if next_section else None,
                "previous_section_title": previous_section["section_title"] if previous_section else None,
                "next_section_title": next_section["section_title"] if next_section else None,
                "heading_ancestry": ancestry,
                "breadcrumb": _breadcrumb(section, section_by_id),
                "block_ids": [b["block_id"] for b in section_blocks],
                "entry_block_id": section_blocks[0]["block_id"] if section_blocks else None,
                "exit_block_id": section_blocks[-1]["block_id"] if section_blocks else None,
                "document_title": article.get("title"),
            },
            "context_metadata": {
                "section_word_count": section.get("metadata", {}).get("section_word_count", 0),
                "section_sentence_count": section.get("metadata", {}).get("section_sentence_count", 0),
                "section_paragraph_count": section.get("metadata", {}).get("section_paragraph_count", 0),
                "block_count": len(section_blocks),
                "has_parent_section": parent_section is not None,
                "child_section_count": len(child_sections),
                "has_previous_section": previous_section is not None,
                "has_next_section": next_section is not None,
                "heading_ancestry_depth": len(ancestry),
            },
        })

    context_model = {
        "schema_version": "semantic_context_builder_v1",
        "phase": "4.6.2",
        "patch": "4.6.2A",
        "created_at": _now_iso(),
        "source_schema_version": semantic_reading_model.get("schema_version"),
        "source_phase": semantic_reading_model.get("phase"),
        "source_patch": semantic_reading_model.get("patch"),
        "article": {
            "article_id": article.get("article_id"),
            "title": article.get("title"),
            "source_url": article.get("source_url"),
        },
        "context_radius": context_radius,
        "document_context": {
            "document_fingerprint": _fingerprint(article.get("article_id"), document_text),
            "document_text": document_text,
            "first_block_id": article.get("navigation", {}).get("first_block_id"),
            "last_block_id": article.get("navigation", {}).get("last_block_id"),
            "first_section_id": article.get("navigation", {}).get("first_section_id"),
            "last_section_id": article.get("navigation", {}).get("last_section_id"),
        },
        "cross_reference_index": cross_reference_index,
        "section_contexts": section_contexts,
        "block_contexts": block_contexts,
        "sentence_contexts": sentence_contexts,
        "metadata": {
            "section_context_count": len(section_contexts),
            "block_context_count": len(block_contexts),
            "sentence_context_count": len(sentence_contexts),
            "has_document_context": True,
            "has_cross_reference_index": True,
            "has_context_fingerprints": True,
        },
        "boundary_rule": (
            "The Semantic Context Builder creates structural context neighborhoods only. "
            "It does not extract entities, infer concepts, assign intent, score relevance, "
            "build graphs, write memory, or perform reasoning."
        ),
    }

    return context_model


def save_semantic_context_v1(
    semantic_reading_model: Dict[str, Any],
    output_path: str | Path,
    *,
    context_radius: int = 1,
) -> Dict[str, Any]:
    context_model = build_semantic_context_v1(
        semantic_reading_model,
        context_radius=context_radius,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(context_model, indent=2, ensure_ascii=False), encoding="utf-8")
    return context_model


def explain_semantic_context_builder_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.2",
        "patch": "4.6.2A",
        "name": "Semantic Context Builder",
        "purpose": "Build local and structural context neighborhoods from the Semantic Reading Model.",
        "input": "Semantic Reading Model from Phase 4.6.1",
        "output": "Semantic Context Model",
        "does": [
            "builds section context",
            "builds block context",
            "builds sentence context",
            "preserves parent and child section context",
            "preserves previous and next block context",
            "preserves previous and next sentence context",
            "preserves article progress and section depth signals",
            "adds heading ancestry context",
            "adds document breadcrumb paths",
            "adds section entry and exit context",
            "adds document-level context",
            "adds context fingerprints for deterministic caching",
            "adds cross-reference indices between sections, blocks, paragraphs, and sentences",
            "prepares contextual neighborhoods for later semantic extraction",
        ],
        "does_not": [
            "extract entities",
            "extract concepts",
            "infer intent",
            "score relevance",
            "build semantic graphs",
            "write memory",
            "perform reasoning",
            "generate explanations",
        ],
    }
