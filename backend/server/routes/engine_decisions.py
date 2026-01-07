# backend/server/routes/engine_decisions.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
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
            out.append(json.loads(line))
        except Exception:
            continue

    return out

def _safe_norm(s: Any) -> str:
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

def get_aggregated_link_feedback(workspaceId: str, docId: str | None = None, limit_scan: int = 50000) -> Dict[str, Dict[str, Any]]:
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

        et = ev.get("eventType") or ""
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


# ----------------------------
# Routes
# ----------------------------

@router.post("/decision", response_model=DecisionWriteResponse)
def ingest_decision(event: DecisionEvent):
    # ---- Layer 0: warning rule ----
    if event.eventType == "WARNING_SHOWN":
        leads = bool(event.payload.get("leadsToDecision"))
        if not leads:
            raise HTTPException(
                status_code=400,
                detail="WARNING_SHOWN is not stored unless payload.leadsToDecision=true"
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
