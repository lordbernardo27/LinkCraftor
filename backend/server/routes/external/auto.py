# backend/server/routes/external/auto.py
from __future__ import annotations

"""
External AUTO dataset routes.

Phase 1.19.2 only creates the scaffold.
Actual routes will be migrated gradually:

- POST /import
- POST /clear
- POST /owner/auto/cleanup
- GET  /owner/auto/cleanup
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from backend.server.routes.external.shared import (
    AUTO_PATH,
    IMPORT_RUNS_INDEX_PATH,
)

router = APIRouter()


class AutoMigrationStatus(BaseModel):
    ok: bool = True
    phase: str = "1.19.2"
    status: str = "auto_router_scaffold_created"
    auto_path: str = str(AUTO_PATH)
    import_runs_index_path: str = str(IMPORT_RUNS_INDEX_PATH)


@router.get("/auto/status")
async def auto_status() -> Dict[str, Any]:
    return AutoMigrationStatus().model_dump()

from backend.server.routes.external.runtime import (
    _safe_read_json,
    _atomic_write_json,
)


@router.post("/clear")
def clear_imported_urls(source: str = "import"):
    """
    Hard-clear imported URLs from persisted AUTO_PATH.
    This mirrors the legacy external.py /clear behavior.
    """
    try:
        _atomic_write_json(AUTO_PATH, [])
    except Exception:
        with open(AUTO_PATH, "w", encoding="utf-8") as f:
            f.write("[]")

    try:
        raw = _safe_read_json(IMPORT_RUNS_INDEX_PATH)
        if isinstance(raw, dict):
            raw["runs"] = []
            raw["items"] = []
            _atomic_write_json(IMPORT_RUNS_INDEX_PATH, raw)
    except Exception:
        pass

    return {"ok": True, "cleared": True, "path": str(AUTO_PATH)}

from fastapi import File, HTTPException, UploadFile
from backend.server.routes.external.runtime import (
    _safe_read_list,
    _normalize_url_for_storage,
    _is_blocked,
    _make_key,
)


@router.post("/import")
async def import_external_file(file: UploadFile = File(...), source: str = "import"):
    if not file:
        raise HTTPException(status_code=400, detail="file is required")

    name = (file.filename or "").lower()
    raw_bytes = await file.read()
    text = raw_bytes.decode("utf-8", errors="ignore")

    dataset = _safe_read_list(AUTO_PATH)
    now = __import__("datetime").datetime.utcnow().isoformat() + "Z"

    by_url = {}
    order = []

    for item in dataset:
        if not isinstance(item, dict):
            continue
        u = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if u and u not in by_url:
            item["url"] = u
            by_url[u] = item
            order.append(u)

    added = 0
    updated = 0
    skipped_blocked = 0
    skipped_bad = 0

    def upsert(url: str, display_phrase: str = "", title: str = ""):
        nonlocal added, updated, skipped_blocked, skipped_bad

        url2 = _normalize_url_for_storage(url, prefer_no_www=True, drop_query=True)
        if not url2:
            skipped_bad += 1
            return
        if _is_blocked(url2):
            skipped_blocked += 1
            return

        phrase2 = (display_phrase or "").strip()
        title2 = (title or "").strip() if title else None
        label = phrase2 or title2 or url2
        key = _make_key(label)

        existing = by_url.get(url2)
        if not existing:
            by_url[url2] = {
                "key": key,
                "phrase": phrase2 or label,
                "url": url2,
                "title": title2 or phrase2 or url2,
                "score": 1.0,
                "source": source or "import",
                "lang": "en",
                "added_at": now,
                "updated_at": now,
                "last_event": "import",
            }
            order.append(url2)
            added += 1
        else:
            existing["key"] = existing.get("key") or key
            existing["phrase"] = existing.get("phrase") or phrase2 or label
            existing["title"] = title2 or existing.get("title") or phrase2 or url2
            existing["source"] = existing.get("source") or (source or "import")
            existing["updated_at"] = now
            existing["last_event"] = "import_update"
            updated += 1

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        if line.startswith("#"):
            continue

        # CSV-ish: phrase,url,title OR url,title OR just url
        parts = [p.strip().strip('"').strip("'") for p in line.split(",")]

        if len(parts) >= 2 and ("http://" in parts[1] or "https://" in parts[1]):
            phrase = parts[0]
            url = parts[1]
            title = parts[2] if len(parts) >= 3 else phrase
            upsert(url, phrase, title)
        elif len(parts) >= 1 and ("http://" in parts[0] or "https://" in parts[0]):
            url = parts[0]
            title = parts[1] if len(parts) >= 2 else ""
            upsert(url, title, title)

    out = [by_url[u] for u in order if u in by_url]
    _atomic_write_json(AUTO_PATH, out)

    return {
        "ok": True,
        "path": str(AUTO_PATH),
        "added": added,
        "updated": updated,
        "skipped_blocked": skipped_blocked,
        "skipped_bad": skipped_bad,
        "filename": name,
    }


@router.post("/owner/auto/cleanup")
async def owner_auto_cleanup(preview: bool = True):
    dataset = _safe_read_list(AUTO_PATH)

    by_url = {}
    order = []

    changed = 0
    merged = 0

    for it in dataset:
        if not isinstance(it, dict):
            continue

        raw_url = str(it.get("url") or "").strip()
        norm = _normalize_url_for_storage(raw_url, prefer_no_www=True, drop_query=True)
        if not norm:
            continue

        if norm != raw_url:
            changed += 1

        it["url"] = norm

        if norm in by_url:
            merged += 1
            existing = by_url[norm]

            try:
                existing_score = float(existing.get("score", 1.0) or 1.0)
            except Exception:
                existing_score = 1.0

            try:
                new_score = float(it.get("score", 1.0) or 1.0)
            except Exception:
                new_score = 1.0

            existing["score"] = max(existing_score, new_score)

            ph1 = existing.get("phrases")
            if not isinstance(ph1, list):
                ph1 = []

            ph2 = it.get("phrases")
            if not isinstance(ph2, list):
                ph2 = []

            for p in ph2:
                if p and p not in ph1:
                    ph1.append(p)

            existing["phrases"] = ph1
            continue

        by_url[norm] = it
        order.append(norm)

    cleaned = [by_url[u] for u in order if u in by_url]

    result = {
        "ok": True,
        "preview": bool(preview),
        "before": len(dataset),
        "after": len(cleaned),
        "normalized_changed_count": changed,
        "duplicates_merged_count": merged,
        "path": str(AUTO_PATH),
    }

    if not preview:
        _atomic_write_json(AUTO_PATH, cleaned)
        result["written"] = True

    return result


@router.get("/owner/auto/cleanup")
async def owner_auto_cleanup_get(preview: bool = True):
    return await owner_auto_cleanup(preview=preview)

