from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.server.routes.external.shared import (
    AUTO_PATH,
    IMPORT_RUNS_INDEX_PATH,
)
from backend.server.routes.external.runtime import (
    _safe_read_list,
    _safe_read_json,
    _atomic_write_json,
    _normalize_url_for_storage,
    _is_blocked,
    _make_key,
)

router = APIRouter(tags=["external-import-clear-runtime"])


@router.get("/import_clear/status")
def import_clear_status() -> Dict[str, Any]:
    return {
        "ok": True,
        "router": "external.import_clear",
        "routes": [
            "/import",
            "/clear",
        ],
    }


@router.post("/import")
async def import_external_file(file: UploadFile = File(...), source: str = "import"):
    if not file:
        raise HTTPException(status_code=400, detail="file is required")

    name = (file.filename or "").lower()
    raw_bytes = await file.read()
    text = raw_bytes.decode("utf-8", errors="ignore")

    dataset = _safe_read_list(AUTO_PATH)
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

    added = 0
    updated = 0
    skipped_blocked = 0
    skipped_bad = 0

    def upsert(display_phrase: str, url: str, title: Optional[str], score: float):
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
                "score": float(score or 1.0),
                "source": source,
                "seen_count": 1,
                "first_seen": now,
                "last_seen": now,
                "phrases": [phrase2] if phrase2 else [],
                "lang": "en",
                "last_event": "import",
                "imported_at": now,
            }
            order.append(url2)
            added += 1
            return

        existing["url"] = url2
        existing["key"] = key
        existing["phrase"] = existing.get("phrase") or (phrase2 or label)
        existing["title"] = title2 or existing.get("title") or phrase2 or url2

        try:
            prev = float(existing.get("score", 1.0) or 1.0)
        except Exception:
            prev = 1.0
        existing["score"] = max(prev, float(score or 1.0))

        existing["source"] = existing.get("source") or source
        existing["seen_count"] = int(existing.get("seen_count", 0) or 0) + 1
        existing["last_seen"] = now
        existing["first_seen"] = existing.get("first_seen") or now

        phrases = existing.get("phrases")
        if not isinstance(phrases, list):
            phrases = []
        if phrase2 and phrase2 not in phrases:
            phrases.append(phrase2)
        existing["phrases"] = phrases  # no trimming

        updated += 1

    if name.endswith(".csv"):
        reader = csv.DictReader(text.splitlines())
        for row in reader:
            if not isinstance(row, dict):
                continue
            phrase = (row.get("phrase") or "").strip()
            key_in = (row.get("key") or "").strip()
            url = (row.get("url") or "").strip()
            title = (row.get("title") or "").strip() or None
            try:
                score = float(row.get("score") or 1.0)
            except Exception:
                score = 1.0
            upsert(phrase or key_in, url, title, score)
    else:
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "|" in line:
                url_part, title_part = [x.strip() for x in line.split("|", 1)]
                upsert("", url_part, title_part or None, 1.0)
            else:
                upsert("", line, None, 1.0)

    out = [by_url[u] for u in order if u in by_url]
    _atomic_write_json(AUTO_PATH, out)
    return {
        "ok": True,
        "path": str(AUTO_PATH),
        "added": added,
        "updated": updated,
        "skipped_blocked": skipped_blocked,
        "skipped_bad": skipped_bad,
    }


@router.post("/clear")
def clear_imported_urls(source: str = "import"):
    """
    Hard-clear imported URLs from persisted storage (AUTO_PATH).
    This ensures they do NOT reappear after reload.
    """
    try:
        _atomic_write_json(AUTO_PATH, [])
    except Exception:
        # Fallback if your helper differs
        with open(AUTO_PATH, "w", encoding="utf-8") as f:
            f.write("[]")

    # Optional: clear the import runs index too (keeps history clean)
    try:
        raw = _safe_read_json(IMPORT_RUNS_INDEX_PATH)
        if isinstance(raw, dict):
            raw["runs"] = []
            raw["items"] = []
            _atomic_write_json(IMPORT_RUNS_INDEX_PATH, raw)
    except Exception:
        pass

    return {"ok": True, "cleared": True, "path": str(AUTO_PATH)}
