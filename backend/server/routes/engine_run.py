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
    "prepublish": {"STRONG": 0.70, "OPTIONAL": 0.60, "MIN_OVERLAP": 2},
}

ENGINE_RUN_BUILD = "2026-05-06-RUNTIME-INTELLIGENCE"

MAX_UNIQUE_PHRASES = 30
MAX_HITS_PER_PHRASE = 2
MIN_PHRASE_TOKENS = 1

WORD_RE = re.compile(r"[a-z0-9]{2,}", re.I)

RUNTIME_INTELLIGENCE_LAYERS = [
    "logical_inference",
    "goal_driven_planning",
    "content_aware_context",
    "memory_feedback",
    "topic_coherence",
    "long_context_compression",
    "knowledge_retrieval",
    "multi_agent_reasoning",
    "autonomous_linking_orchestrator",
    "multi_objective_optimization",
    "runtime_conflict_intelligence",
    "explainability",
    "qa_regression_readiness",
]

CONNECTORS = {
    "about", "after", "before", "because", "by", "during", "for",
    "from", "in", "into", "of", "on", "than", "that", "to",
    "with", "without", "while", "whether", "rather",
}


RUNTIME_BAD_STARTS = {
    "from", "with", "without", "before", "after", "during", "because",
    "rather", "inside", "outside", "into", "based", "confirm", "estimate",
    "guess", "guessing", "identify", "put", "shift",
}

RUNTIME_BAD_ENDS = {
    "from", "with", "without", "before", "after", "during", "because",
    "rather", "the", "a", "an", "of", "to", "and", "or", "but",
    "guesswork",
}

RUNTIME_BAD_PATTERNS = (
    r"\bfrom guesswork\b",
    r"\bconfirm the\b",
    r"\bestimate the\b",
    r"\bbased on\b",
    r"\brather than\b",
)

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


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _normalize_unit_score(value: float) -> float:
    value = _safe_float(value, 0.0)
    if value > 1.0:
        value = value / 100.0
    return max(0.0, min(1.0, value))


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
        joined = ",".join(
            str(x or "").strip()
            for x in pool_sources
            if str(x or "").strip()
        )

        if joined:
            return joined

    return "active_phrase_pool"


def _content_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in CONNECTORS]


def _semantic_root(tokens: List[str]) -> str:
    if not tokens:
        return ""

    important = _content_tokens(tokens)

    if not important:
        important = tokens

    return " ".join(important[:2])


def _semantic_overlap(a: str, b: str) -> float:
    ta = set(_phrase_tokens(a))
    tb = set(_phrase_tokens(b))

    if not ta or not tb:
        return 0.0

    inter = len(ta & tb)
    union = len(ta | tb)

    return inter / max(1, union)


def _is_runtime_competitor(a: str, b: str) -> bool:
    a = _norm(a)
    b = _norm(b)

    if not a or not b:
        return False

    if a == b:
        return True

    if a in b or b in a:
        shorter = min(len(_phrase_tokens(a)), len(_phrase_tokens(b)))

        if shorter >= 2:
            return True

    if _semantic_overlap(a, b) >= 0.60:
        return True

    ra = _semantic_root(_phrase_tokens(a))
    rb = _semantic_root(_phrase_tokens(b))

    if ra and rb and ra == rb:
        return True

    return False

def _is_runtime_dirty_phrase(phrase: str) -> bool:
    p = _norm(phrase)
    toks = _tokenize(p)

    if not p or not toks:
        return True

    if toks[0] in RUNTIME_BAD_STARTS:
        return True

    if toks[-1] in RUNTIME_BAD_ENDS:
        return True

    if any(re.search(pattern, p) for pattern in RUNTIME_BAD_PATTERNS):
        return True

    return False


def _is_clean_highlight_phrase(phrase: str, rec: Dict[str, Any]) -> bool:
    p = _norm(phrase)

    if not p:
        return False
    if _is_runtime_dirty_phrase(p):
       return False

    toks = _tokenize(p)

    if len(toks) < 2 or len(toks) > 5:
        return False

    banned_anywhere = {
        "put", "tied", "identify", "tends", "shift",
    }

    if any(t in banned_anywhere for t in toks):
        return False

    banned_middle = {
        "and", "or", "but", "so", "then",
    }

    middle = toks[1:-1]

    if any(t in banned_middle for t in middle):
        return False

    if toks[0].isdigit() and len(toks) <= 3:
        return False

    if toks[0] in {"day", "days"} and len(toks) <= 2:
        return False

    return True


def _legacy_score_from_record(rec: Dict[str, Any]) -> float:
    legacy_score = 0.0

    for key in ("builder_score", "score", "quality_score", "strength_score"):
        legacy_score = max(legacy_score, _safe_float(rec.get(key), 0.0))

    return _normalize_unit_score(legacy_score)


def _runtime_score(
    phrase_text: str,
    rec: Dict[str, Any],
    overlap_score: float,
    overlap_count: int,
    occurs: bool,
) -> Dict[str, Any]:

    extractor_score = _normalize_unit_score(
        (rec.get("extractor_intelligence") or {}).get("score", 0.0)
    )

    quality_gate_score = _normalize_unit_score(
        (rec.get("quality_gate") or {}).get("quality_gate_score", 0.0)
    )

    builder_score = _normalize_unit_score(
        (rec.get("builder_intelligence") or {}).get("builder_score", 0.0)
    )

    selector_score = _normalize_unit_score(
        (rec.get("selector_intelligence") or {}).get("selector_score", 0.0)
    )

    legacy_score = _legacy_score_from_record(rec)

    if not builder_score:
        builder_score = legacy_score

    if not selector_score:
        selector_score = legacy_score

    if not quality_gate_score:
        quality_gate_score = legacy_score

    if not extractor_score:
        extractor_score = legacy_score

    occurrence_signal = 1.0 if occurs else 0.5
    overlap_signal = _normalize_unit_score(overlap_score)

    phrase_len = len(_phrase_tokens(phrase_text))
    readability_signal = 1.0

    if phrase_len >= 5:
        readability_signal = 0.80

    runtime_score = (
        (extractor_score * 0.10)
        + (quality_gate_score * 0.20)
        + (builder_score * 0.20)
        + (selector_score * 0.25)
        + (occurrence_signal * 0.15)
        + (overlap_signal * 0.10)
    )

    runtime_score *= readability_signal
    runtime_score = max(0.0, min(1.0, runtime_score))

    return {
        "runtime_score": round(runtime_score, 4),
        "signals": {
            "extractor_score": round(extractor_score, 4),
            "quality_gate_score": round(quality_gate_score, 4),
            "builder_score": round(builder_score, 4),
            "selector_score": round(selector_score, 4),
            "legacy_score": round(legacy_score, 4),
            "occurrence_signal": round(occurrence_signal, 4),
            "overlap_signal": round(overlap_signal, 4),
            "readability_signal": round(readability_signal, 4),
            "overlap_count": int(overlap_count),
        },
        "layers": RUNTIME_INTELLIGENCE_LAYERS,
    }


def _determine_bucket(
    phrase_text: str,
    rec: Dict[str, Any],
    runtime_score: float,
    overlap: int,
    floors: Dict[str, Any],
) -> str:

    source_type = str(rec.get("source_type") or "").strip().lower()

    strong_floor = float(floors["STRONG"])
    optional_floor = float(floors["OPTIONAL"])

    if source_type in {"intent"}:
        return "semantic_optional"

    if source_type in {"entity"}:
        if runtime_score >= optional_floor:
            return "semantic_optional"

    if runtime_score >= strong_floor:
        return "internal_strong"

    if runtime_score >= optional_floor:
        return "semantic_optional"

    return ""


def _build_hit(
    phrase_text: str,
    rec: Dict[str, Any],
    runtime_data: Dict[str, Any],
    overlap: int,
    bucket: str,
) -> Dict[str, Any]:

    runtime_score = float(runtime_data.get("runtime_score") or 0.0)

    return {
        "phrase": phrase_text,
        "title": _best_title_from_record(phrase_text, rec),
        "score": round(runtime_score, 4),
        "overlap": int(overlap),
        "bucket": bucket,
        "source": _source_from_record(rec),
        "source_type": str(rec.get("source_type") or ""),
        "vertical": str(rec.get("vertical") or ""),
        "snippet": (
            rec.get("snippets")[0]
            if isinstance(rec.get("snippets"), list)
            and rec.get("snippets")
            else str(rec.get("snippet") or "")
        ),
        "runtime_intelligence": runtime_data,
    }


@router.post("/run")
def engine_run(payload: EngineRunRequest = Body(...)):

    html = (payload.html or "").strip()
    text = (payload.text or "").strip()

    if not html and not text:
        return {
            "ok": False,
            "error": "Provide 'html' or 'text' in request body.",
        }

    ws = _ws_safe(payload.workspaceId or "default")
    doc_id = str(payload.docId or "doc_runtime")

    phase = (payload.phase or PHASE_DEFAULT).strip().lower()

    if phase not in FLOORS_BY_PHASE:
        phase = PHASE_DEFAULT

    floors = FLOORS_BY_PHASE[phase]

    pool_path = _active_phrase_pool_path(ws)

    pool_obj = (
        _safe_read_json(pool_path)
        if os.path.exists(pool_path)
        else None
    )

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

    limited_joined_text = joined_text[
        : max(0, int(payload.limit or 2500))
    ]

    joined_text_norm = _norm(limited_joined_text)

    doc_tokens_set = set(
        _tokenize(limited_joined_text)
    )

    internal_strong: List[Dict[str, Any]] = []
    semantic_optional: List[Dict[str, Any]] = []

    phrase_hits: Dict[str, int] = {}
    unique_phrases: Set[str] = set()

    hidden_debug: List[Dict[str, Any]] = []

    runtime_selected: List[str] = []

    ranked_candidates: List[Dict[str, Any]] = []

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

        occurs = _phrase_occurs_in_text(
            phrase_text,
            joined_text_norm,
        )

        overlap_score, overlap_count = _token_overlap_score(
            toks,
            doc_tokens_set,
        )

        if (
            not occurs
            and overlap_count < int(floors["MIN_OVERLAP"])
        ):
            continue

        runtime_data = _runtime_score(
            phrase_text=phrase_text,
            rec=rec,
            overlap_score=overlap_score,
            overlap_count=overlap_count,
            occurs=occurs,
        )

        runtime_score = float(
            runtime_data.get("runtime_score") or 0.0
        )

        ranked_candidates.append({
            "phrase_text": phrase_text,
            "rec": rec,
            "runtime_data": runtime_data,
            "runtime_score": runtime_score,
            "overlap_count": overlap_count,
        })

    ranked_candidates = sorted(
        ranked_candidates,
        key=lambda x: -float(x.get("runtime_score") or 0),
    )

    for row in ranked_candidates:

        phrase_text = str(row.get("phrase_text") or "")
        rec = row.get("rec") or {}

        runtime_data = row.get("runtime_data") or {}

        runtime_score = float(
            row.get("runtime_score") or 0.0
        )

        overlap_count = int(
            row.get("overlap_count") or 0
        )

        phrase_norm = _norm(phrase_text)

        if any(
            _is_runtime_competitor(
                phrase_text,
                existing,
            )
            for existing in runtime_selected
        ):
            hidden_debug.append({
                "phrase": phrase_text,
                "reason": "runtime_semantic_competitor",
                "runtime_score": runtime_score,
            })
            continue

        bucket = _determine_bucket(
            phrase_text=phrase_text,
            rec=rec,
            runtime_score=runtime_score,
            overlap=overlap_count,
            floors=floors,
        )

        if not bucket:
            hidden_debug.append({
                "phrase": phrase_text,
                "runtime_score": runtime_score,
                "overlap": overlap_count,
                "source_type": str(rec.get("source_type") or ""),
            })
            continue

        if phrase_hits.get(phrase_norm, 0) >= MAX_HITS_PER_PHRASE:
            continue

        if (
            phrase_norm not in unique_phrases
            and len(unique_phrases) >= MAX_UNIQUE_PHRASES
        ):
            break

        item = _build_hit(
            phrase_text=phrase_text,
            rec=rec,
            runtime_data=runtime_data,
            overlap=overlap_count,
            bucket=bucket,
        )

        phrase_hits[phrase_norm] = (
            phrase_hits.get(phrase_norm, 0) + 1
        )

        unique_phrases.add(phrase_norm)

        runtime_selected.append(phrase_text)

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
            "internal_found": (
                len(internal_strong)
                + len(semantic_optional)
            ),
            "internal_strong_count": len(internal_strong),
            "semantic_optional_count": len(semantic_optional),
            "unique_phrases": len(unique_phrases),
            "runtime_intelligence_layers": RUNTIME_INTELLIGENCE_LAYERS,
            "floors": floors,
            "rb2_extract": {
                "version": rb2_doc.get("version"),
                "paragraphs": len(
                    rb2_doc.get("paragraphs") or []
                ),
                "joined_text_len": len(
                    limited_joined_text
                ),
            },
            "hidden_sample": hidden_debug[:10],
            "pool_path": pool_path,
        },
    }