from __future__ import annotations

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Set, Dict, Any, Tuple
import os
import json
import re

from backend.server.engine.rb2_adapter import build_rb2_phrase_contexts


PHASE_DEFAULT = "prepublish"

FLOORS_BY_PHASE = {
    "publish": {"STRONG": 0.75, "OPTIONAL": 0.65, "MIN_OVERLAP": 2},
    "prepublish": {"STRONG": 0.70, "OPTIONAL": 0.60, "MIN_OVERLAP": 1},
}

ENGINE_RUN_BUILD = "2026-04-20-RB2-HIGHLIGHT-ONLY"

MAX_UNIQUE_PHRASES = 30
MAX_HITS_PER_PHRASE = 2
MIN_PHRASE_TOKENS = 1

WORD_RE = re.compile(r"[a-z0-9]{2,}", re.I)

router = APIRouter(prefix="/api/engine", tags=["engine-run"])


class EngineRunRequest(BaseModel):
    workspaceId: Optional[str] = Field(default="default", alias="workspace_id")
    docId: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    phase: Optional[str] = PHASE_DEFAULT
    limit: int = 2500

    class Config:
        allow_population_by_field_name = True


def _ws_safe(ws: str) -> str:
    ws = (ws or "default").strip().lower()
    return re.sub(r"[^a-z0-9_\-]", "_", ws)[:80] or "default"


def _data_dir() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _active_phrase_pool_path(ws: str) -> str:
    return os.path.join(
        _data_dir(),
        "phrase_pools",
        "active",
        f"active_phrase_pool_{_ws_safe(ws)}.json",
    )


def _safe_read_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _norm(text: str) -> str:
    return _normalize_spaces(str(text or "").lower())


def _phrase_tokens(phrase: str) -> List[str]:
    return _tokenize(phrase or "")


def _token_overlap_score(anchor_tokens: List[str], doc_tokens_set: Set[str]) -> Tuple[float, int]:
    if not anchor_tokens or not doc_tokens_set:
        return 0.0, 0

    anchor_set = set(anchor_tokens)
    overlap = anchor_set.intersection(doc_tokens_set)
    overlap_count = len(overlap)
    score = overlap_count / max(len(anchor_set), 1)
    return score, overlap_count


def _phrase_occurs_in_text(phrase: str, joined_text_norm: str) -> bool:
    p = _norm(phrase)
    if not p or not joined_text_norm:
        return False
    return p in joined_text_norm


def _best_title_from_record(phrase: str, rec: Dict[str, Any]) -> str:
    if not isinstance(rec, dict):
        return str(phrase or "").strip().title()

    snippets = rec.get("snippets")
    if isinstance(snippets, list):
        for s in snippets:
            x = _normalize_spaces(str(s or ""))
            if x:
                return x

    return _normalize_spaces(str(rec.get("phrase") or phrase or "")).title()


def _source_from_record(rec: Dict[str, Any]) -> str:
    if not isinstance(rec, dict):
        return "active_phrase_pool"

    pool_sources = rec.get("pool_sources")
    if isinstance(pool_sources, list) and pool_sources:
        joined = ",".join(str(x or "").strip() for x in pool_sources if str(x or "").strip())
        if joined:
            return joined

    return "active_phrase_pool"


def _is_clean_highlight_phrase(phrase: str, rec: Dict[str, Any]) -> bool:
    p = _norm(phrase)
    if not p:
        return False

    toks = _tokenize(p)
    if len(toks) < 2 or len(toks) > 5:
        return False

    banned_anywhere = {"put", "tied", "identify", "tends", "shift"}
    if any(t in banned_anywhere for t in toks):
        return False

    banned_middle = {"and", "or", "but", "so", "then"}
    middle = toks[1:-1]
    if any(t in banned_middle for t in middle):
        return False

    if toks[0].isdigit() and len(toks) <= 3:
        return False

    if toks[0] in {"day", "days"} and len(toks) <= 2:
        return False

    return True


def _determine_bucket(
    phrase_text: str,
    rec: Dict[str, Any],
    score: float,
    overlap: int,
    floors: Dict[str, Any],
) -> str:
    source_type = str(rec.get("source_type") or "").strip().lower()
    strong_floor = float(floors["STRONG"])
    optional_floor = float(floors["OPTIONAL"])

    if source_type in {"intent"}:
        return "semantic_optional"

    if source_type in {"entity"}:
        if score >= optional_floor:
            return "semantic_optional"

    if score >= strong_floor:
        return "internal_strong"

    if score >= optional_floor:
        return "semantic_optional"

    return ""


def _build_hit(
    phrase_text: str,
    rec: Dict[str, Any],
    score: float,
    overlap: int,
    bucket: str,
) -> Dict[str, Any]:
    return {
        "phrase": phrase_text,
        "title": _best_title_from_record(phrase_text, rec),
        "score": round(float(score), 4),
        "overlap": int(overlap),
        "bucket": bucket,
        "source": _source_from_record(rec),
        "source_type": str(rec.get("source_type") or ""),
        "vertical": str(rec.get("vertical") or ""),
        "snippet": (
            rec.get("snippets")[0]
            if isinstance(rec.get("snippets"), list) and rec.get("snippets")
            else str(rec.get("snippet") or "")
        ),
    }


@router.post("/run")
def engine_run(payload: EngineRunRequest = Body(...)):
    html = (payload.html or "").strip()
    text = (payload.text or "").strip()

    if not html and not text:
        return {"ok": False, "error": "Provide 'html' or 'text' in request body."}

    ws = _ws_safe(payload.workspaceId or "default")
    doc_id = str(payload.docId or "doc_runtime")

    phase = (payload.phase or PHASE_DEFAULT).strip().lower()
    if phase not in FLOORS_BY_PHASE:
        phase = PHASE_DEFAULT
    floors = FLOORS_BY_PHASE[phase]

    pool_path = _active_phrase_pool_path(ws)
    pool_obj = _safe_read_json(pool_path) if os.path.exists(pool_path) else None

    phrases_obj: Dict[str, Any] = {}
    if isinstance(pool_obj, dict):
        if isinstance(pool_obj.get("phrases"), dict):
            phrases_obj = pool_obj.get("phrases") or {}
        elif isinstance(pool_obj.get("items"), dict):
            phrases_obj = pool_obj.get("items") or {}
        elif isinstance(pool_obj.get("entries"), dict):
            phrases_obj = pool_obj.get("entries") or {}

    rb2_doc = build_rb2_phrase_contexts(
        doc_id,
        html=html if html else None,
        text=text if text else None,
    )

    joined_text = str(rb2_doc.get("joinedText") or "")
    limited_joined_text = joined_text[: max(0, int(payload.limit or 2500))]
    joined_text_norm = _norm(limited_joined_text)
    doc_tokens_set = set(_tokenize(limited_joined_text))

    internal_strong: List[Dict[str, Any]] = []
    semantic_optional: List[Dict[str, Any]] = []

    phrase_hits: Dict[str, int] = {}
    unique_phrases: Set[str] = set()
    hidden_debug: List[Dict[str, Any]] = []

    for phrase, rec in phrases_obj.items():
        if not isinstance(rec, dict):
            continue

        phrase_text = _normalize_spaces(str(phrase or ""))
        if not phrase_text:
            continue

        toks = _phrase_tokens(phrase_text)
        if len(toks) < MIN_PHRASE_TOKENS:
            continue

        phrase_norm = _norm(phrase_text)
        if not phrase_norm:
            continue

        if not _is_clean_highlight_phrase(phrase_text, rec):
            continue

        occurs = _phrase_occurs_in_text(phrase_text, joined_text_norm)
        score, overlap = _token_overlap_score(toks, doc_tokens_set)

        if not occurs and overlap < int(floors["MIN_OVERLAP"]):
            continue

        bucket = _determine_bucket(
            phrase_text=phrase_text,
            rec=rec,
            score=score,
            overlap=overlap,
            floors=floors,
        )
        if not bucket:
            hidden_debug.append({
                "phrase": phrase_text,
                "score": round(float(score), 4),
                "overlap": int(overlap),
                "source_type": str(rec.get("source_type") or ""),
            })
            continue

        if phrase_hits.get(phrase_norm, 0) >= MAX_HITS_PER_PHRASE:
            continue

        if phrase_norm not in unique_phrases and len(unique_phrases) >= MAX_UNIQUE_PHRASES:
            break

        item = _build_hit(
            phrase_text=phrase_text,
            rec=rec,
            score=score,
            overlap=overlap,
            bucket=bucket,
        )

        phrase_hits[phrase_norm] = phrase_hits.get(phrase_norm, 0) + 1
        unique_phrases.add(phrase_norm)

        if bucket == "internal_strong":
            internal_strong.append(item)
        else:
            semantic_optional.append(item)

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
            "phase": phase,
            "phrase_pool_count": len(phrases_obj),
            "internal_found": len(internal_strong) + len(semantic_optional),
            "internal_strong_count": len(internal_strong),
            "semantic_optional_count": len(semantic_optional),
            "unique_phrases": len(unique_phrases),
            "floors": floors,
            "rb2_extract": {
                "version": rb2_doc.get("version"),
                "paragraphs": len(rb2_doc.get("paragraphs") or []),
                "joined_text_len": len(limited_joined_text),
            },
            "hidden_sample": hidden_debug[:10],
            "pool_path": pool_path,
        },
    }