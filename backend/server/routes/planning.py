from fastapi import APIRouter, HTTPException, Query
import os, json, re
from typing import Any, Dict, List, Tuple

router = APIRouter(prefix="/api/planning", tags=["planning"])

def _data_dir() -> str:
    # backend/server/data
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def _ws_safe(ws: str) -> str:
    ws = (ws or "default").strip().lower()
    return re.sub(r"[^a-z0-9_\-]", "_", ws)[:80] or "default"

def _safe_read_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception:
        return None

def _path_imported_urls(workspace_id: str) -> str:
    ws = _ws_safe(workspace_id)
    return os.path.join(_data_dir(), f"imported_urls_{ws}.json")

def _path_draft_topics(workspace_id: str) -> str:
    ws = _ws_safe(workspace_id)
    return os.path.join(_data_dir(), f"draft_topics_{ws}.json")

def _norm_url(u: str) -> str:
    u = (u or "").strip().strip('"')
    if not u:
        return ""
    # remove fragment
    u = u.split("#", 1)[0]
    # trim trailing slash (but keep "https://x.com/" -> "https://x.com")
    if u.endswith("/") and len(u) > 8:
        u = u.rstrip("/")
    return u

@router.get("/draft_audit")
async def draft_audit(
    workspace_id: str = Query("default"),
    limit: int = Query(5000, ge=1, le=200000),
):
    """
    Compare draft planned_url vs imported sitemap URLs.

    Returns:
      - matched: draft topics whose planned_url exists in sitemap
      - missing: draft topics whose planned_url is NOT in sitemap
      - counts + small samples (up to `limit`)
    """
    imported_path = _path_imported_urls(workspace_id)
    draft_path = _path_draft_topics(workspace_id)

    imported_raw = _safe_read_json(imported_path)
    draft_raw = _safe_read_json(draft_path)

    imported_list = imported_raw if isinstance(imported_raw, list) else []
    draft_list = draft_raw if isinstance(draft_raw, list) else []

    # Build normalized sitemap URL set
    sitemap_set = set()
    for u in imported_list:
        nu = _norm_url(str(u))
        if nu:
            sitemap_set.add(nu)

    matched: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []
    no_planned_url: List[Dict[str, Any]] = []

    for t in draft_list:
        if not isinstance(t, dict):
            continue
        topic_id = str(t.get("topic_id") or "").strip()
        title = str(t.get("working_title") or "").strip()
        planned_url = str(t.get("planned_url") or "").strip()

        if not planned_url:
            no_planned_url.append({
                "topic_id": topic_id,
                "working_title": title,
                "planned_url": "",
            })
            continue

        nu = _norm_url(planned_url)
        if not nu:
            no_planned_url.append({
                "topic_id": topic_id,
                "working_title": title,
                "planned_url": planned_url,
            })
            continue

        row = {
            "topic_id": topic_id,
            "working_title": title,
            "planned_url": planned_url,
            "normalized": nu,
        }

        if nu in sitemap_set:
            matched.append(row)
        else:
            missing.append(row)

    # apply limit
    matched_out = matched[:limit]
    missing_out = missing[:limit]
    noplan_out  = no_planned_url[:limit]

    return {
        "workspace_id": _ws_safe(workspace_id),
        "paths": {
            "imported_urls": imported_path,
            "draft_topics": draft_path,
        },
        "counts": {
            "sitemap_urls": len(sitemap_set),
            "draft_topics_total": len(draft_list),
            "matched": len(matched),
            "missing": len(missing),
            "no_planned_url": len(no_planned_url),
        },
        "matched": matched_out,
        "missing": missing_out,
        "no_planned_url": noplan_out,
    }
