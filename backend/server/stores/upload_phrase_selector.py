from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List

from backend.server.stores.candidate_window_guard import candidate_window_guard
from backend.server.stores.phrase_strength_scorer import (
    canonical_phrase,
    score_phrase_strength,
)
from backend.server.stores.phrase_vertical_policy import (
    apply_vertical_policy_score,
    detect_vertical,
)
from backend.server.stores.smart_phrase_extractor import (
    extract_paragraphs,
    extract_smart_phrases,
)


def _canonical_phrase(s: str) -> str:
    return canonical_phrase(s)


def _tokens(phrase: str) -> List[str]:
    return _canonical_phrase(phrase).split()


def _clean_selector_phrase(phrase: str, source_type: str = "") -> str:
    clean = _canonical_phrase(phrase)
    if not clean:
        return ""

    guard = candidate_window_guard(clean, source_type=source_type or "")
    if isinstance(guard, dict):
        guarded_phrase = _canonical_phrase(str(guard.get("phrase") or ""))
        if guarded_phrase:
            return guarded_phrase

    return clean


def _passes_guard(phrase: str, source_type: str = "") -> bool:
    clean = _canonical_phrase(phrase)
    if not clean:
        return False

    guard = candidate_window_guard(clean, source_type=source_type or "")
    if not isinstance(guard, dict):
        return True

    return bool(guard.get("keep"))


def _score_with_strength(
    phrase: str,
    source_type: str,
    vertical: str,
    freq: int = 1,
) -> Dict[str, Any]:
    clean = _canonical_phrase(phrase)
    if not clean:
        return {"keep": False, "score": 0.0, "reason": "empty_phrase"}

    try:
        result = score_phrase_strength(
            phrase=clean,
            source_type=source_type or "",
            vertical=vertical,
            frequency=freq,
        )
    except TypeError:
        try:
            result = score_phrase_strength(
                phrase=clean,
                source_type=source_type or "",
            )
        except Exception:
            result = {"keep": False, "score": 0.0, "reason": "score_error"}
    except Exception:
        result = {"keep": False, "score": 0.0, "reason": "score_error"}

    if not isinstance(result, dict):
        return {
            "keep": bool(result),
            "score": float(result or 0.0),
            "reason": "numeric_result",
        }

    return result


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


def _final_quality_gate(row: Dict[str, Any]) -> bool:
    phrase = _canonical_phrase(str(row.get("phrase") or ""))
    if not phrase:
        return False

    tokens = phrase.split()

    if len(tokens) < 2 or len(tokens) > 8:
        return False

    if len(set(tokens)) < len(tokens):
        return False

    if not bool(row.get("keep")):
        return False

    if float(row.get("score") or 0.0) <= 0:
        return False

    return True


def _local_dedupe_phrase_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    best_by_canonical: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        phrase = _canonical_phrase(str(row.get("phrase") or ""))
        canonical = _canonical_phrase(str(row.get("canonical") or phrase))

        if not phrase or not canonical:
            continue

        row["phrase"] = phrase
        row["canonical"] = canonical

        current = best_by_canonical.get(canonical)
        if current is None:
            best_by_canonical[canonical] = row
            continue

        row_score = float(row.get("score") or 0.0)
        current_score = float(current.get("score") or 0.0)

        row_quality = float(row.get("quality_score") or 0.0)
        current_quality = float(current.get("quality_score") or 0.0)

        if (row_score, row_quality, -len(phrase)) > (
            current_score,
            current_quality,
            -len(str(current.get("phrase") or "")),
        ):
            best_by_canonical[canonical] = row

    return list(best_by_canonical.values())


def _dedupe_and_rank(
    candidates: List[Dict[str, Any]],
    vertical: str = "universal",
) -> List[Dict[str, Any]]:
    cleaned_phrases = [
        _clean_selector_phrase(
            str(c.get("phrase") or ""),
            str(c.get("source_type") or "unknown"),
        )
        for c in candidates
        if c.get("phrase")
    ]

    counter = Counter(p for p in cleaned_phrases if p)
    scored_rows: List[Dict[str, Any]] = []

    for c in candidates:
        original_phrase = _canonical_phrase(str(c.get("phrase") or ""))
        source_type = str(c.get("source_type") or "unknown")
        context = str(c.get("snippet") or "")

        phrase = _clean_selector_phrase(original_phrase, source_type=source_type)
        if not phrase:
            continue

        if not _passes_guard(phrase, source_type=source_type):
            continue

        freq = counter.get(phrase, 1)

        quality = _score_with_strength(
            phrase=phrase,
            source_type=source_type,
            vertical=vertical,
            freq=freq,
        )

        if not quality.get("keep"):
            continue

        raw_score = float(quality.get("score") or 0.0)

        if raw_score <= 1.0:
            score = raw_score * 100.0
        else:
            score = raw_score

        score += _source_type_bonus(source_type)

        if freq >= 2:
            score += min(freq * 1.2, 8.0)

        score = apply_vertical_policy_score(phrase, score, vertical)

        row = {
            "phrase": phrase,
            "canonical": phrase,
            "source_type": source_type,
            "score": round(float(score), 4),
            "quality_score": quality.get("score"),
            "quality_reason": quality.get("reason"),
            "keep": True,
            "section_id": c.get("section_id", ""),
            "snippet": context,
            "original_phrase": original_phrase,
            "frequency": freq,
        }

        if _final_quality_gate(row):
            scored_rows.append(row)

    deduped = _local_dedupe_phrase_rows(scored_rows)

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
            "original_phrase": row.get("original_phrase", ""),
            "frequency": row.get("frequency", 1),
        }
        for row in deduped
        if _final_quality_gate(row)
    ]

    ranked = sorted(
        selected,
        key=lambda x: (
            -float(x.get("score") or 0),
            len(str(x.get("phrase") or "")),
            str(x.get("phrase") or ""),
        ),
    )

    return ranked[:80]


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

    combined_text = "\n".join([
        original_name or "",
        text or "",
    ])

    vertical = detect_vertical(combined_text.lower()) or "universal"

    selected = _dedupe_and_rank(candidates, vertical=vertical)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "doc_id": doc_id,
        "vertical": vertical,
        "paragraph_count": len(paragraphs),
        "candidate_count": len(candidates),
        "selected_count": len(selected),
        "phrases": selected,
    }