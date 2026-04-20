from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Optional, List, Set, Dict, Tuple, Any

import os
import json
import re


PHASE_DEFAULT = "prepublish"

FLOORS_BY_PHASE = {
    "publish": {"STRONG": 0.75, "OPTIONAL": 0.65, "MIN_OVERLAP": 2},
    "prepublish": {"STRONG": 0.70, "OPTIONAL": 0.60, "MIN_OVERLAP": 1},
}

MAX_UNIQUE_PHRASES = 30
MAX_HITS_PER_PHRASE = 2

WORD_RE = re.compile(r"[a-z0-9]{3,}")


def tokenize(text: str) -> List[str]:
    return WORD_RE.findall((text or "").lower())


def token_overlap_score(anchor_tokens: List[str], doc_tokens_set: Set[str]) -> Tuple[float, int]:
    if not anchor_tokens or not doc_tokens_set:
        return 0.0, 0

    anchor_set = set(anchor_tokens)
    overlap = anchor_set.intersection(doc_tokens_set)
    overlap_count = len(overlap)
    score = overlap_count / max(len(anchor_set), 1)
    return score, overlap_count


router = APIRouter(prefix="/api/engine", tags=["engine-run"])
ENGINE_RUN_BUILD = "2026-04-20-RB2-ACTIVE-PHRASE-POOL"


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


def _phrase_tokens(phrase: str) -> List[str]:
    return tokenize(phrase or "")


def _best_url_from_record(rec: Dict[str, Any]) -> str:
    if not isinstance(rec, dict):
        return ""

    for key in ("planned_urls", "urls"):
        vals = rec.get(key)
        if isinstance(vals, list):
            for v in vals:
                s = str(v or "").strip()
                if s:
                    return s

    for key in ("source_url", "planned_url", "url", "link_target"):
        s = str(rec.get(key) or "").strip()
        if s:
            return s

    return ""


def _best_title_from_record(phrase: str, rec: Dict[str, Any]) -> str:
    if not isinstance(rec, dict):
        return phrase.title()

    snippets = rec.get("snippets")
    if isinstance(snippets, list):
        for s in snippets:
            x = str(s or "").strip()
            if x:
                return x

    return str(rec.get("phrase") or phrase).strip().title()


class EngineRunRequest(BaseModel):
    workspaceId: Optional[str] = "default"
    docId: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    phase: Optional[str] = PHASE_DEFAULT
    limit: int = 2500


@router.post("/run")
def engine_run(payload: EngineRunRequest = Body(...)):
    html = (payload.html or "").strip()
    text = (payload.text or "").strip()

    if not html and not text:
        return {"ok": False, "error": "Provide 'html' or 'text' in request body."}

    ws = payload.workspaceId or "default"
    phase = (payload.phase or PHASE_DEFAULT).strip().lower()
    if phase not in FLOORS_BY_PHASE:
        phase = PHASE_DEFAULT

    floors = FLOORS_BY_PHASE[phase]

    pool_path = _active_phrase_pool_path(ws)
    pool_obj = _safe_read_json(pool_path) if os.path.exists(pool_path) else None
    phrases_obj = (
        pool_obj.get("phrases")
        if isinstance(pool_obj, dict) and isinstance(pool_obj.get("phrases"), dict)
        else {}
    )

    source_text = html if html else text
    limited_text = source_text[: max(0, int(payload.limit or 2500))]
    doc_tokens_set = set(tokenize(limited_text))

    combined = []
    phrase_hits: Dict[str, int] = {}
    unique_phrases: Set[str] = set()

    for phrase, rec in phrases_obj.items():
        if not isinstance(rec, dict):
            continue

        phrase_text = str(phrase or "").strip()
        if not phrase_text:
            continue

        toks = _phrase_tokens(phrase_text)
        if not toks:
            continue

        score, overlap = token_overlap_score(toks, doc_tokens_set)

        if overlap < int(floors["MIN_OVERLAP"]):
            continue

        optional_floor = float(floors["OPTIONAL"])
        if len(toks) <= 3:
            optional_floor = min(optional_floor, 0.50)

        if score >= float(floors["STRONG"]):
            strength = "strong"
        elif score >= optional_floor:
            strength = "optional"
        else:
            continue

        phrase_norm = phrase_text.lower()

        if phrase_hits.get(phrase_norm, 0) >= MAX_HITS_PER_PHRASE:
            continue

        if phrase_norm not in unique_phrases and len(unique_phrases) >= MAX_UNIQUE_PHRASES:
            break

        url = _best_url_from_record(rec)
        title = _best_title_from_record(phrase_text, rec)

        phrase_hits[phrase_norm] = phrase_hits.get(phrase_norm, 0) + 1
        unique_phrases.add(phrase_norm)

        combined.append({
            "phrase": phrase_text,
            "title": title,
            "url": url,
            "score": round(float(score), 4),
            "overlap": int(overlap),
            "strength": strength,
            "source": ",".join(rec.get("pool_sources", [])) if isinstance(rec.get("pool_sources"), list) else "active_phrase_pool",
            "source_type": str(rec.get("source_type") or ""),
            "vertical": str(rec.get("vertical") or ""),
        })

    internal_strong = [x for x in combined if x["strength"] == "strong"]
    semantic_optional = [x for x in combined if x["strength"] != "strong"]

    return {
        "ok": True,
        "engine": "RB2",
        "workspaceId": ws,
        "docId": payload.docId,
        "internal_strong": internal_strong,
        "semantic_optional": semantic_optional,
        "meta": {
            "build": ENGINE_RUN_BUILD,
            "phrase_pool_count": len(phrases_obj),
            "internal_found": len(combined),
            "internal_strong_count": len(internal_strong),
            "semantic_optional_count": len(semantic_optional),
            "unique_phrases": len(unique_phrases),
            "floors": floors,
        }
    }