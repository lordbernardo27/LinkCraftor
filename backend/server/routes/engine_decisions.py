# backend/server/routes/engine_decisions.py
from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Tuple
import json
import os
import time

router = APIRouter(prefix="/api/engine", tags=["engine-decisions"])

# Path: backend/server/data/decisions.jsonl
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DECISIONS_PATH = os.path.join(DATA_DIR, "decisions.jsonl")


# ----------------------------
# Models
# ----------------------------

class DecisionEvent(BaseModel):
    # Layer 0 required fields
    workspaceId: str = Field(..., min_length=1)
    userId: str = Field(..., min_length=1)  # can be "anonymous"
    docId: str = Field(..., min_length=1)

    eventType: str = Field(..., min_length=1)
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000))

    # Event-specific data (phrase/target/section/provider/thresholds/errors...)
    payload: Dict[str, Any] = Field(default_factory=dict)

    # Optional but useful for attribution & tracing
    requestId: Optional[str] = None
    source: Optional[str] = None  # "web" | "wp_plugin" | "api" | etc.


class DecisionWriteResponse(BaseModel):
    ok: bool = True
    written: bool = True
    path: str
    eventType: str
    timestamp: int


# ----------------------------
# Helpers
# ----------------------------

WARNING_OUTCOME_EVENTS = {
    "WARNING_ACCEPTED_AND_FIXED",
    "WARNING_IGNORED",
    "WARNING_OVERRIDDEN",
    "WARNING_MARKED_FALSE_POSITIVE",
}

def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

def _append_jsonl(obj: Dict[str, Any]) -> None:
    _ensure_data_dir()
    with open(DECISIONS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def _read_recent_jsonl(limit: int) -> List[Dict[str, Any]]:
    if limit <= 0:
        return []
    if not os.path.exists(DECISIONS_PATH):
        return []

    with open(DECISIONS_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    out: List[Dict[str, Any]] = []
    for line in reversed(lines):
        if len(out) >= limit:
            break
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue

        # Layer 1.7: keep "recent" clean — never return WARNING_SHOWN entries
        if obj.get("eventType") == "WARNING_SHOWN":
            continue

        out.append(obj)

    return out

def _safe_norm(s: Any) -> str:
    # Note: this is not regex; kept as-is from your current file.
    return str(s or "").lower().strip().replace("\s+", " ")

def _make_feedback_key(phrase_text: str, payload: Dict[str, Any]) -> Optional[str]:
    pnorm = _safe_norm(phrase_text)
    if not pnorm:
        return None

    # Prefer targetId, else url, else title
    tkey = payload.get("targetId") or payload.get("url") or payload.get("title")
    if not tkey:
        return None

    return f"{pnorm}||{str(tkey).strip()}"

def get_aggregated_link_feedback(
    workspaceId: str,
    docId: str | None = None,
    limit_scan: int = 50000
) -> Dict[str, Dict[str, Any]]:
    """
    Returns:
      { "phrase||target": {accepts, rejects, lastOutcome, lastAt} }
    Only for LINK_SUGGESTION_ACCEPTED / LINK_SUGGESTION_REJECTED.
    """
    if not os.path.exists(DECISIONS_PATH):
        return {}

    with open(DECISIONS_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    results: Dict[str, Dict[str, Any]] = {}
    scanned = 0

    for line in reversed(lines):
        if scanned >= limit_scan:
            break
        line = line.strip()
        if not line:
            continue

        try:
            ev = json.loads(line)
        except Exception:
            continue

        scanned += 1

        if ev.get("workspaceId") != workspaceId:
            continue
        if docId and ev.get("docId") != docId:
            continue

        et = (ev.get("eventType") or "").strip()
        if et not in ("LINK_SUGGESTION_ACCEPTED", "LINK_SUGGESTION_REJECTED"):
            continue

        payload = ev.get("payload") or {}
        phrase_text = payload.get("phraseText") or payload.get("phrase") or ""
        key = _make_feedback_key(phrase_text, payload)
        if not key:
            continue

        rec = results.get(key)
        if not rec:
            rec = {"accepts": 0, "rejects": 0, "lastOutcome": None, "lastAt": None}
            results[key] = rec

        if et == "LINK_SUGGESTION_ACCEPTED":
            rec["accepts"] += 1
            rec["lastOutcome"] = "accept"
            rec["lastAt"] = ev.get("timestamp")
        else:
            rec["rejects"] += 1
            rec["lastOutcome"] = "reject"
            rec["lastAt"] = ev.get("timestamp")

    return results


def get_aggregated_warning_outcomes(
    workspaceId: str,
    docId: Optional[str] = None,
    limit_scan: int = 50000
) -> Dict[str, Dict[str, Any]]:
    """
    Layer 1.10: Warning analytics aggregation.
    (keeps 'unknown' bucket removed)
    """
    if not os.path.exists(DECISIONS_PATH):
        return {}

    with open(DECISIONS_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    results: Dict[str, Dict[str, Any]] = {}
    scanned = 0

    def _bucket(code: str) -> Dict[str, Any]:
        # Layer 1.11: skip useless "unknown" bucket
        code = str(code or "").strip()
        if not code or code == "unknown":
            return {}
        rec = results.get(code)
        if not rec:
            rec = {
                "shown": 0,
                "accepted_and_fixed": 0,
                "ignored": 0,
                "overridden": 0,
                "false_positive": 0,
                "lastOutcome": None,
                "lastAt": None,
            }
            results[code] = rec
        return rec

    for line in reversed(lines):
        if scanned >= limit_scan:
            break
        line = line.strip()
        if not line:
            continue

        try:
            ev = json.loads(line)
        except Exception:
            continue

        scanned += 1

        if ev.get("workspaceId") != workspaceId:
            continue
        if docId and ev.get("docId") != docId:
            continue

        et = (ev.get("eventType") or "").strip()
        payload = ev.get("payload") or {}

        warning_code = str(payload.get("warningCode") or "").strip()
        rec = _bucket(warning_code)
        if not rec:
            continue

        if et == "WARNING_SHOWN":
            # Count only auditable warnings that lead to a decision.
            if bool(payload.get("leadsToDecision")):
                rec["shown"] += 1
            continue

        if et not in WARNING_OUTCOME_EVENTS:
            continue

        if et == "WARNING_ACCEPTED_AND_FIXED":
            rec["accepted_and_fixed"] += 1
            rec["lastOutcome"] = "accepted_and_fixed"
        elif et == "WARNING_IGNORED":
            rec["ignored"] += 1
            rec["lastOutcome"] = "ignored"
        elif et == "WARNING_OVERRIDDEN":
            rec["overridden"] += 1
            rec["lastOutcome"] = "overridden"
        elif et == "WARNING_MARKED_FALSE_POSITIVE":
            rec["false_positive"] += 1
            rec["lastOutcome"] = "false_positive"

        rec["lastAt"] = ev.get("timestamp")

    return results


# ----------------------------
# Layer 2.0: Cache for feedback aggregation
# ----------------------------
_FEEDBACK_CACHE: Dict[Tuple[str, Optional[str], int], Dict[str, Any]] = {}
_FEEDBACK_CACHE_TTL_SECONDS = 10  # small TTL; auto-invalidates on file changes too

def _decisions_mtime() -> int:
    try:
        return int(os.path.getmtime(DECISIONS_PATH))
    except Exception:
        return 0

def get_aggregated_link_feedback_cached(
    workspaceId: str,
    docId: Optional[str] = None,
    limit_scan: int = 50000,
    ttl_seconds: int = _FEEDBACK_CACHE_TTL_SECONDS,
) -> Dict[str, Dict[str, Any]]:
    """
    Cache invalidation rules:
      - If decisions.jsonl mtime changes => refresh
      - If TTL expires => refresh
    """
    key = (workspaceId, docId, int(limit_scan))
    now = int(time.time())

    mtime = _decisions_mtime()
    cached = _FEEDBACK_CACHE.get(key)

    if cached:
        if cached.get("mtime") == mtime and (now - int(cached.get("ts", 0))) <= int(ttl_seconds):
            return cached.get("data") or {}

    data = get_aggregated_link_feedback(workspaceId=workspaceId, docId=docId, limit_scan=limit_scan)
    _FEEDBACK_CACHE[key] = {"mtime": mtime, "ts": now, "data": data}
    return data


# ----------------------------
# Routes
# ----------------------------

@router.post("/decision", response_model=DecisionWriteResponse)
def ingest_decision(event: DecisionEvent):
    # ---- Layer 1.7: WARNING_SHOWN is held, not stored ----
    if event.eventType == "WARNING_SHOWN":
        return DecisionWriteResponse(
            ok=True,
            written=False,
            path=os.path.abspath(DECISIONS_PATH),
            eventType=event.eventType,
            timestamp=event.timestamp,
        )

    obj = event.model_dump()
    _append_jsonl(obj)

    return DecisionWriteResponse(
        ok=True,
        written=True,
        path=os.path.abspath(DECISIONS_PATH),
        eventType=event.eventType,
        timestamp=event.timestamp,
    )

@router.get("/decisions/recent")
def recent_decisions(limit: int = Query(20, ge=1, le=200)):
    items = _read_recent_jsonl(limit)
    return {"ok": True, "count": len(items), "results": items}

@router.get("/decisions/aggregate")
def aggregate_decisions(
    workspaceId: str = Query(..., min_length=1),
    docId: Optional[str] = None,
    limit_scan: int = Query(5000, ge=100, le=200000),
):
    results = get_aggregated_link_feedback(workspaceId=workspaceId, docId=docId, limit_scan=limit_scan)
    return {"ok": True, "count": len(results), "results": results}

# Layer 2.0: same output as /decisions/aggregate, but cached
@router.get("/decisions/aggregate_fast")
def aggregate_decisions_fast(
    workspaceId: str = Query(..., min_length=1),
    docId: Optional[str] = None,
    limit_scan: int = Query(5000, ge=100, le=200000),
    ttl_seconds: int = Query(_FEEDBACK_CACHE_TTL_SECONDS, ge=1, le=300),
):
    results = get_aggregated_link_feedback_cached(
        workspaceId=workspaceId,
        docId=docId,
        limit_scan=limit_scan,
        ttl_seconds=ttl_seconds,
    )
    return {"ok": True, "count": len(results), "results": results}

# ---- Layer 1.10: Warning analytics aggregation ----
@router.get("/decisions/warnings/aggregate")
def aggregate_warning_outcomes(
    workspaceId: str = Query(..., min_length=1),
    docId: Optional[str] = None,
    limit_scan: int = Query(5000, ge=100, le=200000),
):
    results = get_aggregated_warning_outcomes(workspaceId=workspaceId, docId=docId, limit_scan=limit_scan)
    return {"ok": True, "count": len(results), "results": results}
