# backend/server/routes/external/runtime.py
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from backend.server.routes.external.shared import (
    AUTO_PATH,
    MANUAL_PATH,
    BLACKLIST_PATH,
    DATA_DIR,
)

router = APIRouter()

_CACHE: Dict[str, Any] = {}

_RESOLVE_INDEX: Dict[str, Any] = {
    "manual_mtime": None,
    "auto_mtime": None,
    "manual_by_key": {},
    "auto_by_key": {},
}


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _invalidate_cache(path: Path) -> None:
    try:
        _CACHE.pop(str(path), None)
    except Exception:
        pass


def _invalidate_resolve_index() -> None:
    _RESOLVE_INDEX["manual_mtime"] = None
    _RESOLVE_INDEX["auto_mtime"] = None
    _RESOLVE_INDEX["manual_by_key"] = {}
    _RESOLVE_INDEX["auto_by_key"] = {}


def _atomic_write_json(path: Path, data: Any) -> None:
    _ensure_data_dir()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    _invalidate_cache(path)
    _invalidate_resolve_index()


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [] if path.name.endswith(".json") else {}
    except Exception:
        return []


def _cached_read_json(path: Path) -> Any:
    try:
        st = path.stat()
        key = str(path)
        cached = _CACHE.get(key)
        if cached and cached[0] == st.st_mtime:
            return cached[1]
        data = _safe_read_json(path)
        _CACHE[key] = (st.st_mtime, data)
        return data
    except Exception:
        return _safe_read_json(path)


def _safe_read_list(path: Path) -> List[Dict[str, Any]]:
    raw = _cached_read_json(path)
    return raw if isinstance(raw, list) else []


def _ensure_files_exist() -> None:
    _ensure_data_dir()
    if not AUTO_PATH.exists():
        _atomic_write_json(AUTO_PATH, [])
    if not MANUAL_PATH.exists():
        _atomic_write_json(MANUAL_PATH, [])
    if not BLACKLIST_PATH.exists():
        _atomic_write_json(BLACKLIST_PATH, {"blocked_domains": [], "blocked_urls": []})


def _make_key(phrase: str) -> str:
    return " ".join((phrase or "").strip().lower().split())


def _normalize_url(url: str) -> str:
    return (url or "").strip()


def _extract_domain(url: str) -> str:
    u = (url or "").strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = u.split("/")[0]
    u = u.split(":")[0]
    return u


def _normalize_url_for_storage(url: str, prefer_no_www: bool = True, drop_query: bool = True) -> str:
    raw = (url or "").strip()
    if not raw:
        return ""

    if not re.match(r"^https?://", raw, flags=re.I):
        raw = "https://" + raw

    try:
        from urllib.parse import urlparse, urlunparse
        p = urlparse(raw)
        scheme = (p.scheme or "https").lower()
        netloc = (p.netloc or "").lower().strip()
        if prefer_no_www and netloc.startswith("www."):
            netloc = netloc[4:]
        path = p.path or "/"
        if path != "/" and path.endswith("/"):
            path = path[:-1]
        query = "" if drop_query else (p.query or "")
        return urlunparse((scheme, netloc, path, "", query, ""))
    except Exception:
        return raw.strip()


def _get_mtime_safe(path: Path) -> Optional[float]:
    try:
        return path.stat().st_mtime
    except Exception:
        return None


def _read_blacklist() -> Dict[str, List[str]]:
    raw = _cached_read_json(BLACKLIST_PATH)
    if not isinstance(raw, dict):
        return {"blocked_domains": [], "blocked_urls": []}
    bd = raw.get("blocked_domains") if isinstance(raw.get("blocked_domains"), list) else []
    bu = raw.get("blocked_urls") if isinstance(raw.get("blocked_urls"), list) else []
    return {"blocked_domains": bd, "blocked_urls": bu}


def _is_blocked(url: str) -> bool:
    url = _normalize_url(url)
    if not url:
        return True
    bl = _read_blacklist()
    domain = _extract_domain(url)
    blocked_urls = set(map(str, bl["blocked_urls"]))
    blocked_domains = set(map(lambda x: str(x).lower().strip(), bl["blocked_domains"]))
    return (url in blocked_urls) or (domain in blocked_domains)


def _extra_keys_from_url(url: str) -> List[str]:
    try:
        from urllib.parse import urlparse
        path = (urlparse(url).path or "").strip("/")
    except Exception:
        return []
    parts = [p for p in path.split("/") if p]
    slug = parts[-1] if parts else ""
    slug = re.sub(r"[-_]+", " ", slug).strip()
    return [_make_key(slug)] if slug else []


def _index_rows_by_key(rows: List[Dict[str, Any]], is_manual: bool) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}

    for item in rows:
        if not isinstance(item, dict):
            continue

        url = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if not url:
            continue
        if _is_blocked(url):
            continue

        item["url"] = url

        if is_manual and bool(item.get("disabled") is True):
            continue

        stored = str(item.get("key") or item.get("phrase") or "").strip()
        k = _make_key(stored)
        if k:
            out.setdefault(k, []).append(item)

        if not is_manual:
            for ek in _extra_keys_from_url(url):
                out.setdefault(ek, []).append(item)

    def _score(x: Dict[str, Any]) -> float:
        try:
            return float(x.get("score", 1.0) or 1.0)
        except Exception:
            return 1.0

    def _last_seen(x: Dict[str, Any]) -> str:
        return str(x.get("last_seen") or x.get("updated_at") or x.get("added_at") or "")

    for kk, lst in out.items():
        lst.sort(key=lambda x: (-_score(x), _last_seen(x), str(x.get("url") or "")))

    return out


def _ensure_resolve_index_uptodate() -> None:
    _ensure_files_exist()

    manual_mtime = _get_mtime_safe(MANUAL_PATH)
    auto_mtime = _get_mtime_safe(AUTO_PATH)

    if _RESOLVE_INDEX["manual_mtime"] != manual_mtime:
        manual_rows = _safe_read_list(MANUAL_PATH)
        _RESOLVE_INDEX["manual_by_key"] = _index_rows_by_key(manual_rows, is_manual=True)
        _RESOLVE_INDEX["manual_mtime"] = manual_mtime

    if _RESOLVE_INDEX["auto_mtime"] != auto_mtime:
        auto_rows = _safe_read_list(AUTO_PATH)
        _RESOLVE_INDEX["auto_by_key"] = _index_rows_by_key(auto_rows, is_manual=False)
        _RESOLVE_INDEX["auto_mtime"] = auto_mtime


class ExternalCandidate(BaseModel):
    phrase: str
    url: str
    title: Optional[str] = None
    score: float = 1.0
    source: str = "backend"
    source_label: Optional[str] = None


class ExternalLogEvent(BaseModel):
    event: str = "auto_apply"
    phrase: str
    url: str
    title: Optional[str] = None
    providerId: Optional[str] = None
    source: str = "auto_link"


@router.post("/log")
async def external_log(payload: ExternalLogEvent = Body(...)):
    phrase = (payload.phrase or "").strip()
    url = _normalize_url_for_storage(payload.url, prefer_no_www=True, drop_query=True)

    if not phrase or not url:
        raise HTTPException(status_code=400, detail="Missing phrase or url")
    if _is_blocked(url):
        raise HTTPException(status_code=400, detail="URL blocked by blacklist")

    dataset = _safe_read_list(AUTO_PATH)
    now = datetime.utcnow().isoformat() + "Z"

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []

    for it in dataset:
        if not isinstance(it, dict):
            continue
        u = _normalize_url_for_storage(str(it.get("url") or ""), prefer_no_www=True, drop_query=True)
        if not u:
            continue
        it["url"] = u
        if u not in by_url:
            by_url[u] = it
            order.append(u)

    existing = by_url.get(url)

    if not existing:
        entry = {
            "key": _make_key(phrase),
            "phrase": phrase,
            "url": url,
            "title": payload.title or phrase,
            "score": 1.0,
            "source": payload.source or "auto-log",
            "providerId": payload.providerId,
            "seen_count": 1,
            "first_seen": now,
            "last_seen": now,
            "last_event": payload.event or "auto_apply",
        }
        by_url[url] = entry
        order.append(url)
        _atomic_write_json(AUTO_PATH, [by_url[u] for u in order if u in by_url])
        return {"ok": True, "action": "added", "normalized_url": url, "path": str(AUTO_PATH)}

    existing["url"] = url
    existing["title"] = payload.title or existing.get("title") or phrase
    existing["phrase"] = existing.get("phrase") or phrase
    existing["key"] = _make_key(existing.get("phrase") or phrase)
    existing["source"] = existing.get("source") or (payload.source or "auto-log")
    existing["seen_count"] = int(existing.get("seen_count", 0) or 0) + 1
    existing["last_seen"] = now
    existing["first_seen"] = existing.get("first_seen") or now
    existing["last_event"] = payload.event or existing.get("last_event") or "auto_apply"

    by_url[url] = existing
    _atomic_write_json(AUTO_PATH, [by_url[u] for u in order if u in by_url])
    return {
        "ok": True,
        "action": "updated",
        "normalized_url": url,
        "seen_count": existing["seen_count"],
        "path": str(AUTO_PATH),
    }
