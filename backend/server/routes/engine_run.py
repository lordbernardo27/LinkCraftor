from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Optional, List, Set, Dict, Tuple, Any

import os
import json
import re
import zlib
import csv
import xml.etree.ElementTree as ET


# =========================
# HELIX TOKEN-OVERLAP RULES
# =========================

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
ENGINE_RUN_BUILD = "2026-03-01-WS-TARGETS"


# =========================
# Workspace helpers
# =========================

def _ws_safe(ws: str) -> str:
    ws = (ws or "default").strip().lower()
    return re.sub(r"[^a-z0-9_\-]", "_", ws)[:80] or "default"


def _data_dir() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


# =========================
# NEW: Imported Targets Loader
# =========================

def _load_imported_targets(ws: str) -> List[str]:
    """
    Reads:
        imported_targets_<ws>.csv
        imported_targets_<ws>.txt
        imported_targets_<ws>.xml
    Returns list of URLs.
    """

    ws_safe = _ws_safe(ws)
    base = _data_dir()

    urls: List[str] = []

    # ---- CSV ----
    csv_path = os.path.join(base, f"imported_targets_{ws_safe}.csv")
    if os.path.exists(csv_path):
        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    u = (row.get("URL") or row.get("url") or "").strip()
                    if u:
                        urls.append(u)
        except Exception:
            pass

    # ---- TXT ----
    txt_path = os.path.join(base, f"imported_targets_{ws_safe}.txt")
    if os.path.exists(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                for line in f:
                    u = line.strip()
                    if u:
                        urls.append(u)
        except Exception:
            pass

    # ---- XML ----
    xml_path = os.path.join(base, f"imported_targets_{ws_safe}.xml")
    if os.path.exists(xml_path):
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for el in root.findall(".//{*}loc"):
                if el.text:
                    urls.append(el.text.strip())
        except Exception:
            pass

    # Deduplicate
    seen = set()
    clean = []
    for u in urls:
        if u and u not in seen:
            seen.add(u)
            clean.append(u)

    return clean


# =========================
# Models
# =========================

class EngineRunRequest(BaseModel):
    workspaceId: Optional[str] = "default"
    docId: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    phase: Optional[str] = PHASE_DEFAULT
    limit: int = 2500


# =========================
# URL slug tokenizer
# =========================

def slug_tokens(url: str) -> List[str]:
    u = (url or "").strip().lower()
    if not u:
        return []

    u = u.split("#", 1)[0].split("?", 1)[0]

    if "://" in u:
        u = u.split("://", 1)[1]

    path = u.split("/", 1)[1] if "/" in u else ""
    path = re.sub(r"[^a-z0-9\-_ ]", " ", path)
    parts = re.split(r"[\s\-_]+", path)

    toks = [p for p in parts if len(p) >= 3]
    return list(dict.fromkeys(toks))[:20]


# ============================================================
# ENGINE RUN (UPDATED TO NEW STORE)
# ============================================================

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

    # ✅ NEW STORE
    urls = _load_imported_targets(ws)

    limited_text = text[: max(0, int(payload.limit or 2500))]
    doc_tokens_set = set(tokenize(limited_text))

    combined = []
    phrase_hits: Dict[str, int] = {}
    unique_phrases: Set[str] = set()

    for url in urls:
        toks = slug_tokens(url)
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

        matched = [t for t in toks if t in doc_tokens_set]
        if not matched:
            continue

        phrase = " ".join(matched[:6]).strip()
        if not phrase:
            continue

        phrase_norm = phrase.lower()

        if phrase_hits.get(phrase_norm, 0) >= MAX_HITS_PER_PHRASE:
            continue

        if phrase_norm not in unique_phrases and len(unique_phrases) >= MAX_UNIQUE_PHRASES:
            break

        phrase_hits[phrase_norm] = phrase_hits.get(phrase_norm, 0) + 1
        unique_phrases.add(phrase_norm)

        combined.append({
            "phrase": phrase,
            "title": phrase.title(),
            "url": url,
            "score": round(float(score), 4),
            "overlap": int(overlap),
            "strength": strength,
            "source": "imported_targets",
        })

    recommended = [x for x in combined if x["strength"] == "strong"]
    optional = [x for x in combined if x["strength"] != "strong"]

    return {
        "ok": True,
        "engine": "HELIX",
        "workspaceId": ws,
        "recommended": recommended,
        "optional": optional,
        "external": [],
        "meta": {
            "build": ENGINE_RUN_BUILD,
            "urls_count": len(urls),
            "internal_found": len(combined),
            "unique_phrases": len(unique_phrases),
            "floors": floors,
        }
    }