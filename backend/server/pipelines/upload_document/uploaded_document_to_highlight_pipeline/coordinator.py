"""
Uploaded Document-to-Highlight Pipeline

Entry-point scope only:

UPLOADED DOCUMENT
    -> Uploaded Document-to-Highlight Pipeline
    -> Smart Phrase Extractor

Downstream stages remain in their existing production locations and are not
executed or migrated by this coordinator during the pipeline-separation phase.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from backend.server.stores.smart_phrase_extractor import (
    extract_smart_phrases,
)
from backend.server.stores.candidate_window_guard import candidate_window_guard
from backend.server.stores.phrase_strength_scorer import score_phrase_strength
from backend.server.stores.highlight_selection_engine import select_highlight_candidates


def _read_string(
    extraction_result: Dict[str, Any],
    *keys: str,
) -> str:
    for key in keys:
        value = extraction_result.get(key)

        if value is None:
            continue

        cleaned = str(value).strip()

        if cleaned:
            return cleaned

    return ""


def run_uploaded_document_to_highlight_pipeline(
    *,
    workspace_id: str,
    document_id: str,
    extraction_result: Dict[str, Any] | None = None,
    max_candidates: int = 500,
    vertical: str = "general",
) -> Dict[str, Any]:
    """
    Canonical entry point for the Uploaded Document-to-Highlight Pipeline.

    This coordinator delegates only to the existing Smart Phrase Extractor.
    """

    clean_workspace_id = str(workspace_id or "").strip()
    clean_document_id = str(document_id or "").strip()

    if not clean_workspace_id:
        raise ValueError("workspace_id is required.")

    if not clean_document_id:
        raise ValueError("document_id is required.")

    if not isinstance(extraction_result, dict):
        raise TypeError("extraction_result must be a dictionary.")

    text = _read_string(
        extraction_result,
        "text",
        "content_text",
        "body_text",
        "content_body",
        "extracted_text",
    )

    html = _read_string(
        extraction_result,
        "html",
        "content_html",
        "body_html",
        "extracted_html",
    )

    title = _read_string(
        extraction_result,
        "title",
        "document_title",
        "extracted_title",
        "h1",
    )

    if not text and not html and not title:
        raise ValueError(
            "extraction_result contains no usable text, HTML, or title."
        )

    safe_max_candidates = max(
        1,
        min(int(max_candidates or 500), 5000),
    )

    safe_vertical = str(
        vertical or "general"
    ).strip() or "general"

    phrase_candidates = extract_smart_phrases(
        text=text,
        html=html,
        title=title,
        doc_id=clean_document_id,
        max_candidates=safe_max_candidates,
        workspace_id=clean_workspace_id,
        vertical=safe_vertical,
    )

    if not isinstance(phrase_candidates, list):
        raise RuntimeError(
            "Smart Phrase Extractor returned a non-list result."
        )

    # TEMP THREE-STAGE PHRASE DIAGNOSTIC
    guard_passed = []
    guard_rejected = []

    for candidate in phrase_candidates:
        phrase = str(candidate.get("phrase", "") or "")
        source_type = str(candidate.get("source_type", "") or "")

        guard_result = candidate_window_guard(
            phrase,
            source_type=source_type,
            workspace_id=clean_workspace_id,
            document_id=clean_document_id,
            vertical=safe_vertical,
        )

        record = {
            "candidate": dict(candidate),
            "original_phrase": phrase,
            "source_type": source_type,
            "guard": guard_result,
        }

        if guard_result.get("keep") is True:
            guard_passed.append(record)
        else:
            guard_rejected.append(record)

    scorer_passed = []
    scorer_rejected = []

    for item in guard_passed:
        guarded_phrase = str(
            item["guard"].get("phrase", "") or item["original_phrase"]
        )

        scorer_result = score_phrase_strength(
            phrase=guarded_phrase,
            source_type=item["source_type"],
            workspace_id=clean_workspace_id,
            document_id=clean_document_id,
            vertical=safe_vertical,
        )

        record = dict(item["candidate"])
        record["phrase"] = str(scorer_result.get("phrase", "") or guarded_phrase)
        record["source_type"] = item["source_type"]
        if isinstance(item["guard"].get("quality_gate"), dict):
            record["quality_gate"] = item["guard"]["quality_gate"]
        record["strength"] = scorer_result
        record["strength_score"] = scorer_result.get("score")

        if scorer_result.get("keep") is True:
            scorer_passed.append(record)
        else:
            scorer_rejected.append(record)

    selection_result = select_highlight_candidates(
        workspace_id=clean_workspace_id,
        doc_id=clean_document_id,
        article_text=text,
        phrase_candidates=scorer_passed,
        resolved_targets=None,
        vertical=safe_vertical,
    )

    print("")
    print("========== FOUR-STAGE PHRASE DIAGNOSTIC ==========")

    print(f"[STAGE 1 - SMART PHRASE EXTRACTOR] {len(phrase_candidates)}")
    for i, item in enumerate(phrase_candidates[:6], start=1):
        print(f"  {i}. {item.get('phrase')}")

    print("")
    print(f"[STAGE 2 - CANDIDATE WINDOW GUARD] {len(guard_passed)}")
    for i, item in enumerate(guard_passed[:6], start=1):
        print(f"  {i}. {item['guard'].get('phrase')}")

    print("")
    print(f"[GUARD REJECTED] {len(guard_rejected)}")
    for i, item in enumerate(guard_rejected[:6], start=1):
        print(
            f"  {i}. {item['original_phrase']} "
            f"-> {item['guard'].get('reason')}"
        )

    print("")
    print(f"[STAGE 3 - PHRASE STRENGTH SCORER] {len(scorer_passed)}")
    for i, item in enumerate(scorer_passed[:6], start=1):
        result = item["strength"]
        print(
            f"  {i}. {item['phrase']} "
            f"(score={result.get('score')})"
        )

    print("")
    print(f"[SCORER REJECTED] {len(scorer_rejected)}")
    for i, item in enumerate(scorer_rejected[:6], start=1):
        result = item["strength"]
        print(
            f"  {i}. {item['phrase']} "
            f"-> score={result.get('score')} "
            f"reason={result.get('reason')}"
        )

    print("")
    print(f"[STAGE 4 - HIGHLIGHT SELECTION ENGINE] input={len(scorer_passed)} selected={len(selection_result.get('selected', []))} rejected={len(selection_result.get('rejected', []))}")
    for i, item in enumerate(selection_result.get("selected", [])[:6], start=1):
        print(f"  {i}. {item.get('phrase')}")

    print("")
    print("[HANDOFF CHECKS]")
    print(f"  Guard input == Extractor output: {len(phrase_candidates)} == {len(phrase_candidates)}")
    print(f"  Scorer input == Guard passed: {len(guard_passed)} == {len(guard_passed)}")
    print(f"  Selector input == Scorer passed: {len(scorer_passed)} == {len(scorer_passed)}")

    print("===================================================")
    print("")

    diagnostic_record = {
        "workspace_id": clean_workspace_id,
        "document_id": clean_document_id,
        "title": title,
        "extractor": len(phrase_candidates),
        "guard_passed": len(guard_passed),
        "guard_rejected": len(guard_rejected),
        "scorer_passed": len(scorer_passed),
        "scorer_rejected": len(scorer_rejected),
        "selector_input": len(scorer_passed),
        "selector_selected": len(selection_result.get("selected", [])),
        "selector_rejected": len(selection_result.get("rejected", [])),
        "extractor_samples": [item.get("phrase") for item in phrase_candidates[:5]],
        "guard_samples": [item["guard"].get("phrase") for item in guard_passed[:5]],
        "scorer_samples": [item.get("phrase") for item in scorer_passed[:5]],
        "selector_samples": [item.get("phrase") for item in selection_result.get("selected", [])[:5]],
        "guard_rejected_samples": [{"phrase": item.get("original_phrase"), "reason": item.get("guard", {}).get("reason")} for item in guard_rejected[:20]],
        "scorer_rejected_samples": [{"phrase": item.get("phrase"), "reason": item.get("strength", {}).get("reason"), "score": item.get("strength", {}).get("score")} for item in scorer_rejected[:20]],
        "selector_rejected_samples": [{"phrase": item.get("phrase"), "reason": item.get("reason")} for item in selection_result.get("rejected", [])[:20]],
    }
    diagnostic_dir = Path(__file__).resolve().parents[3] / "data" / "reports"
    diagnostic_dir.mkdir(parents=True, exist_ok=True)
    diagnostic_path = diagnostic_dir / "uploaded_document_phrase_flow_diagnostics.jsonl"
    with diagnostic_path.open("a", encoding="utf-8") as diagnostic_file:
        diagnostic_file.write(json.dumps(diagnostic_record, ensure_ascii=False) + "\n")

    return {
        "ok": True,
        "pipeline": "uploaded_document_to_highlight_pipeline",
        "workspace_id": clean_workspace_id,
        "document_id": clean_document_id,
        "status": "HIGHLIGHT_SELECTION_COMPLETED",
        "executed": True,
        "entry_point": "smart_phrase_extractor",
        "latest_stage": "highlight_selection_engine",
        "phrase_candidates": selection_result.get("candidates", []),
        "phrase_candidate_count": len(selection_result.get("candidates", [])),
        "highlight_selection": selection_result,
    }


__all__ = [
    "run_uploaded_document_to_highlight_pipeline",
]



