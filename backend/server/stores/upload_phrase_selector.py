from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List

from backend.server.stores.phrase_strength_scorer import (
    canonical_phrase,
    dedupe_phrase_rows,
    score_phrase_strength,
)
from backend.server.stores.smart_phrase_extractor import (
    extract_paragraphs,
    extract_smart_phrases,
)


def _canonical_phrase(s: str) -> str:
    return canonical_phrase(s)


def is_strong_upload_phrase(
    phrase: str,
    source_type: str = "",
    vertical: str = "general",
    context: str = "",
) -> bool:
    result = score_phrase_strength(
        phrase=phrase,
        source_type=source_type or "",
    )
    return bool(result.get("keep"))


def _source_type_bonus(source_type: str) -> float:
    if source_type in {"title", "heading_h1"}:
        return 20.0
    if source_type in {"heading_h2", "heading_h3"}:
        return 15.0
    if source_type in {"entity", "intent"}:
        return 12.0
    if source_type == "list_item":
        return 8.0
    if source_type == "action_object":
        return 8.0
    if source_type == "condition_phrase":
        return 6.0
    if source_type == "noun_phrase":
        return 4.0
    return 0.0


def _score_candidate(
    phrase: str,
    source_type: str,
    freq: int = 1,
    vertical: str = "general",
    context: str = "",
) -> float:
    result = score_phrase_strength(
        phrase=phrase,
        source_type=source_type or "",
    )

    if not result.get("keep"):
        return 0.0

    score = float(result.get("score") or 0.0) * 100.0
    score += _source_type_bonus(source_type)

    if freq >= 2:
        score += min(freq * 1.2, 8.0)

    return round(float(score), 4)


def _dedupe_and_rank(
    candidates: List[Dict[str, Any]],
    vertical: str = "general",
) -> List[Dict[str, Any]]:
    counter = Counter(
        _canonical_phrase(str(c.get("phrase") or ""))
        for c in candidates
        if c.get("phrase")
    )

    scored_rows: List[Dict[str, Any]] = []

    for c in candidates:
        phrase = _canonical_phrase(str(c.get("phrase") or ""))
        if not phrase:
            continue

        source_type = str(c.get("source_type") or "unknown")
        context = str(c.get("snippet") or "")

        quality = score_phrase_strength(
            phrase=phrase,
            source_type=source_type,
        )

        score = _score_candidate(
            phrase=phrase,
            source_type=source_type,
            freq=counter.get(phrase, 1),
            vertical=vertical,
            context=context,
        )

        row = {
            "phrase": phrase,
            "canonical": phrase,
            "source_type": source_type,
            "score": round(float(score), 4),
            "quality_score": quality.get("score"),
            "quality_reason": quality.get("reason"),
            "keep": bool(quality.get("keep")),
            "section_id": c.get("section_id", ""),
            "snippet": context,
        }

        scored_rows.append(row)

    deduped = dedupe_phrase_rows(scored_rows)

    selected = [
        {
            "phrase": row.get("phrase", ""),
            "canonical": row.get("canonical") or row.get("phrase", ""),
            "source_type": row.get("source_type", "unknown"),
            "score": round(float(row.get("score") or 0.0), 4),
            "quality_score": row.get("quality_score"),
            "quality_reason": row.get("quality_reason"),
            "section_id": row.get("section_id", ""),
            "snippet": row.get("snippet", ""),
        }
        for row in deduped
        if row.get("keep")
    ]

    ranked = sorted(
        selected,
        key=lambda x: (-float(x.get("score") or 0), str(x.get("phrase") or "")),
    )

    return ranked


def select_upload_phrases(
    workspace_id: str,
    doc_id: str,
    original_name: str,
    html: str,
    text: str,
) -> Dict[str, Any]:
    paragraphs = extract_paragraphs(html=html or "", text=text or "")

    candidates = extract_smart_phrases(
        text=text or "",
        html=html or "",
        title=original_name or "",
        doc_id=doc_id or "",
        max_candidates=500,
    )

    selected = _dedupe_and_rank(candidates, vertical="universal")

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "doc_id": doc_id,
        "vertical": "universal",
        "paragraph_count": len(paragraphs),
        "candidate_count": len(candidates),
        "selected_count": len(selected),
        "phrases": selected,
    }