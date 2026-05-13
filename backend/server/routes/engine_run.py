from __future__ import annotations

from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Tuple
import os
import json
import re

from backend.server.engine.rb2_adapter import build_rb2_phrase_contexts
from backend.server.stores.highlight_selection_engine import select_highlight_candidates
from backend.server.stores.highlight_density_engine import apply_highlight_density

PHASE_DEFAULT = "prepublish"
ENGINE_RUN_BUILD = "2026-05-12-RB2-C5-DOC-SPECIFIC-POOL"

router = APIRouter(prefix="/api/engine", tags=["engine-run"])


class EngineRunRequest(BaseModel):
    workspaceId: Optional[str] = None
    workspace_id: Optional[str] = None
    docId: Optional[str] = None
    doc_id: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    phase: Optional[str] = PHASE_DEFAULT
    limit: int = 2500

    class Config:
        extra = "allow"
        allow_population_by_field_name = True


def _ws_safe(ws: str) -> str:
    ws = (ws or "default").strip().lower()
    ws = re.sub(r"[^a-z0-9_\-]", "_", ws)[:80] or "default"
    if ws.startswith("ws_ws_"):
        ws = ws[3:]
    return ws


def _doc_safe(doc_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", str(doc_id or "").strip())


def _data_dir() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _upload_phrase_pool_path(ws: str) -> str:
    return os.path.join(
        _data_dir(),
        "phrase_pools",
        "upload",
        f"upload_phrase_pool_{_ws_safe(ws)}.json",
    )


def _upload_phrase_pool_doc_path(ws: str, doc_id: str) -> str:
    return os.path.join(
        _data_dir(),
        "phrase_pools",
        "upload",
        f"upload_phrase_pool_{_ws_safe(ws)}_{_doc_safe(doc_id)}.json",
    )


def _resolve_pool_path(ws: str, doc_id: str) -> Tuple[str, str]:
    doc_pool_path = _upload_phrase_pool_doc_path(ws, doc_id)
    if os.path.exists(doc_pool_path):
        return doc_pool_path, "document_specific"

    fallback_pool_path = _upload_phrase_pool_path(ws)
    return fallback_pool_path, "workspace_active_fallback"


def _safe_read_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _resolve_workspace(payload: EngineRunRequest) -> str:
    raw_ws = (
        getattr(payload, "workspaceId", None)
        or getattr(payload, "workspace_id", None)
        or "default"
    )
    return _ws_safe(raw_ws)


def _resolve_doc_id(payload: EngineRunRequest) -> str:
    return str(
        getattr(payload, "docId", None)
        or getattr(payload, "doc_id", None)
        or "doc_runtime"
    )


def _best_title_from_candidate(candidate: Dict[str, Any]) -> str:
    phrase = str(
        candidate.get("phrase")
        or candidate.get("phrase_text")
        or candidate.get("text")
        or ""
    ).strip()

    examples = candidate.get("examples")
    if isinstance(examples, list):
        for ex in examples:
            if isinstance(ex, dict):
                snippet = _normalize_spaces(str(ex.get("snippet") or ""))
                if snippet:
                    return snippet

    snippets = candidate.get("snippets")
    if isinstance(snippets, list):
        for s in snippets:
            snippet = _normalize_spaces(str(s or ""))
            if snippet:
                return snippet

    return phrase.title()


def _source_from_candidate(candidate: Dict[str, Any]) -> str:
    source_type = str(candidate.get("source_type") or "").strip()
    if source_type:
        return f"upload_phrase_pool:{source_type}"
    return "upload_phrase_pool"


def _build_rb2_hit(candidate: Dict[str, Any], bucket: str = "internal_strong") -> Dict[str, Any]:
    phrase = str(
        candidate.get("phrase")
        or candidate.get("phrase_text")
        or candidate.get("text")
        or ""
    ).strip()

    selection_score = candidate.get("selection_score", 0)
    try:
        normalized_score = float(selection_score) / 100.0
    except Exception:
        normalized_score = 0.0

    normalized_score = max(0.0, min(1.0, normalized_score))

    return {
        "phrase": phrase,
        "phrase_text": phrase,
        "text": phrase,
        "label": phrase,
        "title": _best_title_from_candidate(candidate),
        "score": round(normalized_score, 4),
        "overlap": int(candidate.get("occurrence_count") or 1),
        "bucket": bucket,
        "source": _source_from_candidate(candidate),
        "source_type": str(candidate.get("source_type") or ""),
        "vertical": str(candidate.get("vertical") or ""),
        "snippet": _best_title_from_candidate(candidate),
        "runtime_intelligence": {
            "runtime_score": round(normalized_score, 4),
            "selection_score": candidate.get("selection_score"),
            "anchor_quality_score": candidate.get("anchor_quality_score"),
            "article_relevance_score": candidate.get("article_relevance_score"),
            "link_opportunity_score": candidate.get("link_opportunity_score"),
            "occurrence_count": candidate.get("occurrence_count"),
            "selection_status": candidate.get("selection_status"),
            "selection_reason": candidate.get("selection_reason"),
            "document_specific_pool": candidate.get("document_specific_pool"),
            "document_id": candidate.get("document_id"),
            "layers": [
                "highlight_selection_engine_v1",
                "highlight_density_engine_v1",
                "document_specific_upload_pool",
                "rb2_runtime_bridge",
            ],
        },
    }


@router.post("/run")
def engine_run(payload: EngineRunRequest = Body(...)):
    html = (payload.html or "").strip()
    text = (payload.text or "").strip()

    if not html and not text:
        return {"ok": False, "error": "Provide 'html' or 'text' in request body."}

    ws = _resolve_workspace(payload)
    doc_id = _resolve_doc_id(payload)

    phase = (payload.phase or PHASE_DEFAULT).strip().lower()
    if not phase:
        phase = PHASE_DEFAULT

    rb2_doc = build_rb2_phrase_contexts(
        doc_id,
        html=html if html else None,
        text=text if text else None,
    )

    joined_text = text if text else str(rb2_doc.get("joinedText") or "")

    pool_path, pool_resolution = _resolve_pool_path(ws, doc_id)
    pool_obj = _safe_read_json(pool_path) if os.path.exists(pool_path) else None

    if not isinstance(pool_obj, dict):
        return {
            "ok": True,
            "engine": "RB2",
            "mode": "highlight_only",
            "workspaceId": ws,
            "docId": doc_id,
            "internal_strong": [],
            "semantic_optional": [],
            "meta": {
                "build": ENGINE_RUN_BUILD,
                "resolved_workspace": ws,
                "phase": phase,
                "pool_path": pool_path,
                "pool_resolution": pool_resolution,
                "pool_loaded": False,
                "error": "upload_phrase_pool_not_found_or_invalid",
                "internal_found": 0,
                "internal_strong_count": 0,
                "semantic_optional_count": 0,
                "rb2_extract": {
                    "version": rb2_doc.get("version"),
                    "paragraphs": len(rb2_doc.get("paragraphs") or []),
                    "joined_text_len": len(joined_text),
                    "payload_text_len": len(text),
                    "adapter_joined_text_len": len(str(rb2_doc.get("joinedText") or "")),
                },
            },
        }

    selection_result = select_highlight_candidates(
        workspace_id=ws,
        doc_id=doc_id,
        article_text=joined_text,
        active_phrase_pool=pool_obj,
    )

    density_result = apply_highlight_density(
        article_text=joined_text,
        selected_candidates=selection_result.get("selected", []),
    )

    final_highlights = density_result.get("final_highlights", []) or []

    internal_strong: List[Dict[str, Any]] = [
        _build_rb2_hit(candidate, bucket="internal_strong")
        for candidate in final_highlights
        if isinstance(candidate, dict)
        and str(candidate.get("phrase") or "").strip()
    ]

    semantic_optional: List[Dict[str, Any]] = []

    return {
        "ok": True,
        "engine": "RB2",
        "mode": "highlight_only",
        "workspaceId": ws,
        "docId": doc_id,
        "internal_strong": internal_strong,
        "semantic_optional": semantic_optional,
        "meta": {
            "build": ENGINE_RUN_BUILD,
            "resolved_workspace": ws,
            "phase": phase,
            "pool_path": pool_path,
            "pool_resolution": pool_resolution,
            "pool_loaded": True,
            "document_specific_pool": bool(pool_obj.get("document_specific_pool")),
            "document_id_from_pool": pool_obj.get("document_id"),
            "phrase_pool_count": int(pool_obj.get("phrase_count") or 0),
            "source_phrase_count": int(pool_obj.get("source_phrase_count") or 0),
            "quality_filtered_source_count": int(pool_obj.get("quality_filtered_source_count") or 0),
            "active_phrase_set_used": bool(pool_obj.get("active_phrase_set_used")),
            "active_filter_reason": pool_obj.get("active_filter_reason"),
            "selection_stats": selection_result.get("stats", {}),
            "density_stats": density_result.get("stats", {}),
            "selection_rejected_sample": selection_result.get("rejected", [])[:10],
            "final_highlight_count": len(final_highlights),
            "internal_found": len(internal_strong) + len(semantic_optional),
            "internal_strong_count": len(internal_strong),
            "semantic_optional_count": len(semantic_optional),
            "unique_phrases": len({x.get("phrase") for x in internal_strong if x.get("phrase")}),
            "runtime_intelligence_layers": [
                "highlight_selection_engine_v1",
                "highlight_density_engine_v1",
                "document_specific_upload_pool",
                "rb2_runtime_bridge",
            ],
            "rb2_extract": {
                "version": rb2_doc.get("version"),
                "paragraphs": len(rb2_doc.get("paragraphs") or []),
                "joined_text_len": len(joined_text),
                "payload_text_len": len(text),
                "adapter_joined_text_len": len(str(rb2_doc.get("joinedText") or "")),
            },
        },
    }