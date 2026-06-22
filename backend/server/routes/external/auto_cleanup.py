from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from backend.app.routers.external import (
    AUTO_PATH,
    _safe_read_list,
    _atomic_write_json,
)

router = APIRouter(tags=["external-auto-cleanup-runtime"])


@router.get("/auto_cleanup/status")
def auto_cleanup_status() -> Dict[str, Any]:
    return {
        "ok": True,
        "router": "external.auto_cleanup",
        "routes": [
            "/owner/auto/cleanup",
        ],
    }


@router.post("/owner/auto/cleanup")
async def owner_auto_cleanup(preview: bool = True):
    dataset = _safe_read_list(AUTO_PATH)

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []

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
            existing["phrases"] = ph1  # no trimming

            existing["seen_count"] = int(existing.get("seen_count", 0) or 0) + int(it.get("seen_count", 0) or 0)
            existing["last_seen"] = max(str(existing.get("last_seen") or ""), str(it.get("last_seen") or ""))

            by_url[norm] = existing
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
