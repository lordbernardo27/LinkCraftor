# backend/app/routers/helix_auth_run.py
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from bs4 import BeautifulSoup
from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(tags=["helix_auth"])


# -----------------------------
# Input model
# -----------------------------
class HelixAuthRunIn(BaseModel):
    workspaceId: str = Field(default="default")
    docId: str = Field(default="doc_demo")
    html: str = Field(default="")
    text: str = Field(default="")


# -----------------------------
# Minimal tokenization + gates
# -----------------------------
_RX_WORD = re.compile(r"[\w’'-]+", re.UNICODE)

DEFAULT_STOPWORDS = {
    "a","an","the","and","or","but","if","then","else","when","while","with","without",
    "to","of","for","in","on","at","by","from","as","is","are","was","were","be","been",
    "this","that","these","those","it","its","into","over","under","about","also","than",
    "can","could","may","might","should","would","will","just","very","more","most","such",
}

CONNECTORS = {"of","for","in","on","to","and","with","vs","&","or","the","a","an","by","from"}

def norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def tokens(s: str) -> List[str]:
    return [t.lower() for t in (_RX_WORD.findall(s or "")) if t.strip()]

def content_ratio(tok: List[str]) -> float:
    if not tok:
        return 0.0
    content = [t for t in tok if t not in DEFAULT_STOPWORDS and len(t) >= 4]
    return len(content) / max(1, len(tok))

def no_stop_edges(tok: List[str]) -> bool:
    if not tok:
        return False
    return tok[0] not in DEFAULT_STOPWORDS and tok[-1] not in DEFAULT_STOPWORDS

def looks_like_authority_phrase(phrase: str) -> bool:
    """
    This is the HELIX_AUTH “candidate gate” (NOT matching yet).
    We keep it broad because LinkCraftor must work in any niche.
    """
    p = norm_space(phrase)
    if not p:
        return False

    tok = tokens(p)
    n = len(tok)

    # size window
    if n < 2 or n > 12:
        return False

    # stopword edges
    if not no_stop_edges(tok):
        return False

    # quality
    if content_ratio(tok) < 0.55:
        return False

    # avoid “connector soup” phrases
    if all(t in CONNECTORS for t in tok):
        return False

    # avoid mostly-numeric or url-like junk
    if sum(1 for t in tok if t.isdigit()) >= max(2, n // 2):
        return False
    if "http" in p.lower() or "www." in p.lower():
        return False

    return True


# -----------------------------
# Pool loaders (Authority Domain Pool already working)
# -----------------------------
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
AUTO_FP = DATA_DIR / "global_external_auto.json"
MANUAL_FP = DATA_DIR / "global_external_manual.json"

def _safe_read_json(fp: Path) -> Any:
    try:
        if not fp.exists():
            return None
        return json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        return None

def load_authority_domain_pool() -> List[Dict[str, Any]]:
    """
    Uses only keys you specified: phrase, title, vertical, confidence.
    Note: url key is ignored by design.
    """
    out: List[Dict[str, Any]] = []

    for fp, src in [(AUTO_FP, "auto"), (MANUAL_FP, "manual")]:
        obj = _safe_read_json(fp)
        if not obj:
            continue

        # tolerate shapes: {items:[...]} or [...] or {phrase->...}
        items = None
        if isinstance(obj, dict) and isinstance(obj.get("items"), list):
            items = obj["items"]
        elif isinstance(obj, list):
            items = obj
        elif isinstance(obj, dict):
            # maybe stored by phrase key
            items = []
            for k, v in obj.items():
                if isinstance(v, dict):
                    vv = dict(v)
                    vv.setdefault("phrase", k)
                    items.append(vv)

        if not isinstance(items, list):
            continue

        for it in items:
            if not isinstance(it, dict):
                continue
            phrase = norm_space(str(it.get("phrase") or ""))
            title = norm_space(str(it.get("title") or ""))
            vertical = norm_space(str(it.get("vertical") or ""))
            conf = it.get("confidence", 0.0)

            try:
                conf_f = float(conf)
            except Exception:
                conf_f = 0.0

            if not phrase and not title:
                continue

            out.append({
                "phrase": phrase,
                "title": title,
                "vertical": vertical,
                "confidence": conf_f,
                "source": src,
            })

    return out


# -----------------------------
# Candidate extraction (THIS STEP)
# -----------------------------
def extract_authority_candidates(html: str, text: str) -> List[str]:
    """
    Extracts candidate phrases from document headings + paragraph-ish blocks.
    Returns unique phrases, preserving rough quality.
    """
    phrases: List[str] = []
    seen: Set[str] = set()

    html = html or ""
    text = text or ""

    if html.strip():
        soup = BeautifulSoup(html, "html.parser")

        # headings first (h1-h4)
        for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
            s = norm_space(tag.get_text(" ", strip=True))
            if not s:
                continue
            if looks_like_authority_phrase(s):
                key = s.lower()
                if key not in seen:
                    seen.add(key)
                    phrases.append(s)

        # paragraph-like blocks
        for tag in soup.find_all(["p", "li", "blockquote"]):
            s = norm_space(tag.get_text(" ", strip=True))
            if not s:
                continue

            # split long blocks into “sentence-ish” chunks to surface candidate ngrams
            chunks = re.split(r"[.;:!?]\s+", s)
            for ch in chunks:
                ch = norm_space(ch)
                if not ch:
                    continue
                # we’ll consider mid-length chunks as candidates too
                if looks_like_authority_phrase(ch):
                    key = ch.lower()
                    if key not in seen:
                        seen.add(key)
                        phrases.append(ch)

    # fallback: if no html or nothing found, mine from plain text
    if not phrases and text.strip():
        raw = norm_space(text)
        chunks = re.split(r"[.;:!?]\s+|\n{2,}", raw)
        for ch in chunks:
            ch = norm_space(ch)
            if not ch:
                continue
            if looks_like_authority_phrase(ch):
                key = ch.lower()
                if key not in seen:
                    seen.add(key)
                    phrases.append(ch)

    return phrases


# -----------------------------
# Endpoint
# -----------------------------
@router.post("/run")
def helix_auth_run(payload: HelixAuthRunIn):
    # Load pools (domain pool already validated by your counts)
    authority_domain_pool = load_authority_domain_pool()

    # Step 2: extract candidates (this step)
    candidates = extract_authority_candidates(payload.html, payload.text)

    # Matching not implemented yet (next step)
    external_out: List[Dict[str, Any]] = []

    return {
        "ok": True,
        "external": external_out,
        "meta": {
            "engine": "HELIX_AUTH",
            "workspace_id": payload.workspaceId,
            "doc_id": payload.docId,
            "counts": {
                "authority_domain_pool": len(authority_domain_pool),
                "authority_draft_pool": 0,
                "authority_imported_pool": 0,
                "candidates_in": len(candidates),
                "external_out": len(external_out),
            },
            "sample": {
                "candidates_first_10": candidates[:10],
            },
            "notes": "Step2 implemented: candidate extraction only. Matching comes next.",
        },
    }