# external_service.py
#
# Minimal backend for LinkCraftor external URL resolution + logging.
# Endpoints:
#   POST /api/external/resolve
#   POST /api/external/log
#
# You can run with:
#   uvicorn external_service:app --reload --port 8002

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import time

app = FastAPI(title="LinkCraftor External Resolver")

# --------------------------------------------------------------------
# Simple file-based "database"
# --------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

CANONICAL_FILE = os.path.join(DATA_DIR, "canonical_external_map.json")
LOG_FILE       = os.path.join(DATA_DIR, "external_links_log.jsonl")


def load_canonical_map() -> Dict[str, Dict[str, Any]]:
    """
    Load canonical map from JSON file.
    Key: normalized phrase (lowercase string)
    Value: dict with url, title, providerId, providerLabel, score, etc.
    """
    if not os.path.exists(CANONICAL_FILE):
        # You can pre-seed some entries here if the file doesn't exist yet
        seed = {
            # EXAMPLE ONLY – you will replace/add your real canonical pairs
            "calculate due date": {
                "url": "https://www.acog.org/womens-health/faqs/how-is-my-due-date-calculated",
                "title": "How Is My Due Date Calculated?",
                "providerId": "acog",
                "providerLabel": "ACOG",
                "score": 0.98,
                "source": "canonical"
            },
            "calculate conception date": {
                "url": "https://www.acog.org/womens-health/faqs/how-your-due-date-is-calculated",
                "title": "How Your Due Date Is Calculated",
                "providerId": "acog",
                "providerLabel": "ACOG",
                "score": 0.95,
                "source": "canonical"
            }
        }
        with open(CANONICAL_FILE, "w", encoding="utf-8") as f:
            json.dump(seed, f, ensure_ascii=False, indent=2)
        return seed

    with open(CANONICAL_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict):
                return {}
            return data
        except Exception:
            return {}


def save_canonical_map(data: Dict[str, Dict[str, Any]]) -> None:
    with open(CANONICAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


CANONICAL_EXTERNAL_MAP = load_canonical_map()

# --------------------------------------------------------------------
# Request models
# --------------------------------------------------------------------

class ResolveContext(BaseModel):
    docCode: Optional[str] = None
    docTitle: Optional[str] = None
    lang: Optional[str] = "en"
    topic: Optional[str] = None
    source: Optional[str] = None  # e.g. "external_mark"


class ResolveRequest(BaseModel):
    phrase: str
    context: Optional[ResolveContext] = None


class ResolveCandidate(BaseModel):
    providerId: Optional[str] = None
    providerLabel: Optional[str] = None
    url: str
    title: Optional[str] = None
    score: float
    source: Optional[str] = None
    phrase: Optional[str] = None


class ResolveResponse(BaseModel):
    ok: bool
    resolved: Optional[ResolveCandidate] = None
    alternatives: Optional[List[ResolveCandidate]] = None
    error: Optional[str] = None


class LogRequest(BaseModel):
    event: str                  # "auto_apply", "modal_accept", "modal_override"
    phrase: str
    url: str
    providerId: Optional[str] = None
    providerLabel: Optional[str] = None
    docCode: Optional[str] = None
    docTitle: Optional[str] = None
    lang: Optional[str] = "en"
    source: Optional[str] = None  # "resolve", "user_manual", etc.


class LogResponse(BaseModel):
    ok: bool = True


# --------------------------------------------------------------------
# Helper: normalize phrase
# --------------------------------------------------------------------

def normalize_phrase(p: str) -> str:
    return (p or "").strip().lower()


# --------------------------------------------------------------------
# Endpoint: /api/external/resolve
# --------------------------------------------------------------------

@app.post("/api/external/resolve", response_model=ResolveResponse)
def resolve_external(req: ResolveRequest):
    phrase = (req.phrase or "").strip()
    if not phrase:
        return ResolveResponse(ok=False, error="empty_phrase")

    norm = normalize_phrase(phrase)
    ctx = req.context

    # 1) Look up in canonical map (exact normalized phrase)
    canonical_entry = CANONICAL_EXTERNAL_MAP.get(norm)
    if canonical_entry and canonical_entry.get("url"):
        resolved = ResolveCandidate(
            url=canonical_entry["url"],
            title=canonical_entry.get("title") or phrase,
            providerId=canonical_entry.get("providerId"),
            providerLabel=canonical_entry.get("providerLabel"),
            score=float(canonical_entry.get("score", 1.0)),
            source=canonical_entry.get("source", "canonical"),
            phrase=phrase
        )
        # For now we return no "alternatives" – we can add them later
        return ResolveResponse(ok=True, resolved=resolved, alternatives=[])

    # 2) No canonical match → for now, say "no_match"
    # Later we can add:
    #   - match against global dataset
    #   - fuzzy matching on similar phrases
    #   - provider-based search, etc.
    return ResolveResponse(ok=False, error="no_match")


# --------------------------------------------------------------------
# Endpoint: /api/external/log
# --------------------------------------------------------------------

@app.post("/api/external/log", response_model=LogResponse)
def log_external(req: LogRequest):
    """
    Append a JSON line for every external link that was actually used.
    This file becomes your global external URL dataset over time.
    """
    record = {
        "ts": time.time(),
        "event": req.event,
        "phrase": req.phrase,
        "url": req.url,
        "providerId": req.providerId,
        "providerLabel": req.providerLabel,
        "docCode": req.docCode,
        "docTitle": req.docTitle,
        "lang": req.lang,
        "source": req.source,
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # OPTIONAL: if you want "auto-learning" immediately,
    # you can also insert into CANONICAL_EXTERNAL_MAP when event == "modal_override"
    try:
        if req.event in ("modal_override", "modal_accept"):
            norm = normalize_phrase(req.phrase)
            if norm and req.url:
                CANONICAL_EXTERNAL_MAP[norm] = {
                    "url": req.url,
                    "title": req.phrase,
                    "providerId": req.providerId,
                    "providerLabel": req.providerLabel,
                    "score": 0.9,
                    "source": "learned"
                }
                save_canonical_map(CANONICAL_EXTERNAL_MAP)
    except Exception as e:
        # Don't block the response if saving fails
        print("[ExternalService] Error updating canonical map:", e)

    return LogResponse(ok=True)
