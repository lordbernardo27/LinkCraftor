# backend/server/routes/external/manual.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from backend.server.routes.external.runtime import (
    MANUAL_PATH,
    _safe_read_list,
    _atomic_write_json,
    _normalize_url_for_storage,
    _is_blocked,
    _make_key,
)

router = APIRouter()


def _audit(event: str, payload: Dict[str, Any]) -> None:
    # Temporary no-op for Phase 1.18.1.
    # Full audit migration comes later.
    return None


class ManualAddRequest(BaseModel):
    phrase: str
    url: str
    title: Optional[str] = None
    score: float = 5.0
    source: str = "manual-owner"
    lang: str = "en"


class ManualUpdateRequest(BaseModel):
    url: str
    phrase: Optional[str] = None
    title: Optional[str] = None
    score: Optional[float] = None
    disabled: Optional[bool] = None
    source: Optional[str] = None
    lang: Optional[str] = None


class ManualToggleRequest(BaseModel):
    url: str
    disabled: bool = True


class ManualDeleteRequest(BaseModel):
    url: str


@router.get("/manual/list")
async def manual_list(limit: int = 200):
    data = _safe_read_list(MANUAL_PATH)
    limit = max(1, int(limit or 200))
    return {"ok": True, "count": len(data), "items": data[:limit]}


@router.post("/manual/add")
async def manual_add(payload: ManualAddRequest = Body(...)):
    phrase = (payload.phrase or "").strip()
    url = _normalize_url_for_storage(payload.url, prefer_no_www=True, drop_query=True)
    title = (payload.title or "").strip() if payload.title else None

    if not phrase or not url:
        raise HTTPException(status_code=400, detail="phrase and url are required")
    if _is_blocked(url):
        raise HTTPException(status_code=400, detail="URL blocked by blacklist")

    dataset = _safe_read_list(MANUAL_PATH)
    now = datetime.utcnow().isoformat() + "Z"
    key = _make_key(phrase)

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []

    for item in dataset:
        if not isinstance(item, dict):
            continue
        u = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if u and u not in by_url:
            item["url"] = u
            by_url[u] = item
            order.append(u)

    entry = {
        "key": key,
        "phrase": phrase,
        "url": url,
        "title": title or phrase,
        "score": float(payload.score or 5.0),
        "source": payload.source or "manual-owner",
        "lang": payload.lang or "en",
        "disabled": False,
        "added_at": now,
        "updated_at": now,
        "last_event": "manual_add",
    }

    if url not in by_url:
        by_url[url] = entry
        order.append(url)
        _atomic_write_json(MANUAL_PATH, [by_url[u] for u in order if u in by_url])
        _audit("manual_add", {"url": url, "phrase": phrase, "title": entry["title"]})
        return {"ok": True, "action": "added", "path": str(MANUAL_PATH)}

    existing = by_url[url]
    existing.update(entry)
    _atomic_write_json(MANUAL_PATH, [by_url[u] for u in order if u in by_url])
    _audit("manual_add_update", {"url": url, "phrase": phrase, "title": entry["title"]})
    return {"ok": True, "action": "updated", "path": str(MANUAL_PATH)}


@router.post("/manual/update")
async def manual_update(payload: ManualUpdateRequest = Body(...)):
    url = _normalize_url_for_storage(payload.url, prefer_no_www=True, drop_query=True)
    if not url:
        raise HTTPException(status_code=400, detail="url is required")

    dataset = _safe_read_list(MANUAL_PATH)
    now = datetime.utcnow().isoformat() + "Z"

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []

    for item in dataset:
        if not isinstance(item, dict):
            continue
        u = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if u and u not in by_url:
            item["url"] = u
            by_url[u] = item
            order.append(u)

    existing = by_url.get(url)
    if not existing:
        raise HTTPException(status_code=404, detail="manual item not found")

    new_phrase = payload.phrase if payload.phrase is not None else existing.get("phrase")
    new_title = payload.title if payload.title is not None else existing.get("title")
    new_score = payload.score if payload.score is not None else existing.get("score", 5.0)
    new_disabled = payload.disabled if payload.disabled is not None else existing.get("disabled", False)
    new_source = payload.source if payload.source is not None else existing.get("source", "manual-owner")
    new_lang = payload.lang if payload.lang is not None else existing.get("lang", "en")

    existing.update({
        "phrase": new_phrase,
        "key": _make_key(new_phrase) if new_phrase else existing.get("key"),
        "title": new_title or new_phrase,
        "score": float(new_score or 5.0),
        "disabled": bool(new_disabled),
        "source": new_source,
        "lang": new_lang,
        "updated_at": now,
        "last_event": "manual_update",
    })

    _atomic_write_json(MANUAL_PATH, [by_url[u] for u in order if u in by_url])
    _audit("manual_update", {"url": url, "disabled": bool(new_disabled), "phrase": new_phrase})
    return {"ok": True, "action": "updated", "path": str(MANUAL_PATH)}


@router.post("/manual/toggle")
async def manual_toggle(payload: ManualToggleRequest = Body(...)):
    url = _normalize_url_for_storage(payload.url, prefer_no_www=True, drop_query=True)
    if not url:
        raise HTTPException(status_code=400, detail="url is required")

    dataset = _safe_read_list(MANUAL_PATH)

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []

    for item in dataset:
        if not isinstance(item, dict):
            continue
        u = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if u and u not in by_url:
            item["url"] = u
            by_url[u] = item
            order.append(u)

    existing = by_url.get(url)
    if not existing:
        raise HTTPException(status_code=404, detail="manual item not found")

    existing["disabled"] = bool(payload.disabled)
    existing["updated_at"] = datetime.utcnow().isoformat() + "Z"
    existing["last_event"] = "manual_toggle"

    _atomic_write_json(MANUAL_PATH, [by_url[u] for u in order if u in by_url])
    _audit("manual_toggle", {"url": url, "disabled": bool(payload.disabled)})
    return {"ok": True, "action": "toggled", "disabled": bool(payload.disabled)}


@router.post("/manual/delete")
async def manual_delete(payload: ManualDeleteRequest = Body(...)):
    url = _normalize_url_for_storage(payload.url, prefer_no_www=True, drop_query=True)
    if not url:
        raise HTTPException(status_code=400, detail="url is required")

    dataset = _safe_read_list(MANUAL_PATH)

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []

    for item in dataset:
        if not isinstance(item, dict):
            continue
        u = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if u and u not in by_url:
            item["url"] = u
            by_url[u] = item
            order.append(u)

    if url not in by_url:
        raise HTTPException(status_code=404, detail="manual item not found")

    by_url.pop(url, None)
    order = [u for u in order if u != url]

    _atomic_write_json(MANUAL_PATH, [by_url[u] for u in order if u in by_url])
    _audit("manual_delete", {"url": url})
    return {"ok": True, "action": "deleted", "removed": 1}
