# backend/app/routers/engine.py
from __future__ import annotations

from typing import Optional, Dict, Any
from fastapi import APIRouter, Body, Query
from pydantic import BaseModel

router = APIRouter()

# ----------- Internal (dummy for now) -----------
class InternalRequest(BaseModel):
    html: str | None = ""
    text: str | None = ""

@router.post("/internal")
def internal_post(req: InternalRequest) -> Dict[str, Any]:
    # minimal, just proves the route is mounted
    html = (req.html or "").strip()
    text = (req.text or "").strip()
    anchor = "content strategy" if ("content" in (html+text).lower()) else "example"
    return {
        "recommended": [
            {"anchor": anchor, "target_title": "Demo Target", "score": 0.9}
        ]
    }

# ----------- External (local) -----------
@router.get("/external/local")
def external_local_get(
    anchor: str = Query(..., min_length=1),
    context: Optional[str] = Query(None),
    limit: int = Query(8, ge=1, le=20),
) -> Dict[str, Any]:
    from ..engine import run_external_local  # <- lives in backend/app/engine/__init__.py
    items = run_external_local(anchor, context=context, limit=limit)
    return {"items": items}

@router.post("/external/local")
def external_local_post(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    from ..engine import run_external_local
    anchor = str(payload.get("anchor") or "").strip()
    context = str(payload.get("context") or "").strip()
    try:
        limit = int(payload.get("limit", 8))
    except Exception:
        limit = 8
    items = run_external_local(anchor, context=context, limit=limit)
    return {"items": items}
