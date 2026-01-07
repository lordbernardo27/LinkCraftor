from fastapi import APIRouter, UploadFile, File, HTTPException, Query
import os, json, re
from typing import Any, Dict, List
from datetime import datetime, timezone

router = APIRouter(prefix="/api/draft", tags=["draft"])

MAX_BYTES = 5 * 1024 * 1024  # 5MB
MAX_ROWS  = 200000


# -------------------------
# Storage helpers (JSON)
# -------------------------
def _data_dir() -> str:
    # backend/server/data
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def _ws_safe(ws: str) -> str:
    ws = (ws or "default").strip().lower()
    return re.sub(r"[^a-z0-9_\-]", "_", ws)[:80] or "default"

def _path_for_workspace(workspace_id: str) -> str:
    ws = _ws_safe(workspace_id)
    return os.path.join(_data_dir(), f"draft_topics_{ws}.json")

def _meta_path_for_workspace(workspace_id: str) -> str:
    ws = _ws_safe(workspace_id)
    return os.path.join(_data_dir(), f"draft_topics_{ws}.meta.json")

def _safe_read_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception:
        return None

def _atomic_write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def _write_meta(workspace_id: str, filename: str, added: int, updated: int, total: int, data_path: str) -> None:
    meta_path = _meta_path_for_workspace(workspace_id)
    payload = {
        "workspace_id": _ws_safe(workspace_id),
        "last_import_at_utc": datetime.now(timezone.utc).isoformat(),
        "last_import_filename": filename or "",
        "last_import_added": int(added or 0),
        "last_import_updated": int(updated or 0),
        "total_topics": int(total or 0),
        "data_path": data_path,  # OK for local dev; later on AWS you can make this relative
    }
    _atomic_write_json(meta_path, payload)


# -------------------------
# Parsing
# Supports:
# 1) URL-ish draft map (any lines containing URLs)
# 2) CSV with header: topic_id, working_title, planned_slug, planned_url, aliases, priority, canonical
# 3) Pipe format: topic_id|working_title|planned_slug|planned_url|aliases|priority|canonical
# -------------------------
def _parse_draft_text(text: str) -> List[Dict[str, Any]]:
    lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
    if not lines:
        return []

    # -------------------------
    # URL-ish draft map support (tolerant)
    # Extract first URL from each line (works for CSV, numbered lists, pipes, etc.)
    # If >= 60% of lines contain a URL, treat as URL-only draft map.
    # -------------------------
    url_hits: List[str] = []
    for line in lines:
        m = re.search(r"(https?://\S+)", line, flags=re.I)
        if m:
            url_hits.append(m.group(1).rstrip('",)'))  # trim common trailing chars

    if url_hits and (len(url_hits) / max(1, len(lines)) >= 0.6):
        out: List[Dict[str, Any]] = []
        seen = set()

        def clean_url(u: str) -> str:
            u = (u or "").strip().strip('"')
            u = u.split("#", 1)[0]
            return u

        def make_topic_id(u: str) -> str:
            u2 = clean_url(u)
            u2 = re.sub(r"^https?://", "", u2, flags=re.I)
            u2 = re.sub(r"[^a-z0-9]+", "-", u2.lower()).strip("-")
            return u2[:120] or "draft"

        def title_from_url(u: str) -> str:
            u2 = clean_url(u)
            path = re.sub(r"^https?://[^/]+", "", u2, flags=re.I)
            segs = [s for s in re.split(r"[\/\-_]+", path) if s]
            tail = segs[-6:] if segs else []
            if not tail:
                return u2[:120]
            return " ".join([t[:1].upper() + t[1:] for t in tail])[:120]

        for u in url_hits[:MAX_ROWS]:
            u = clean_url(u)
            if not re.match(r"^https?://", u, flags=re.I):
                continue
            tid = make_topic_id(u)
            if tid in seen:
                continue
            seen.add(tid)

            out.append({
                "topic_id": tid,
                "working_title": title_from_url(u),
                "planned_slug": "",
                "planned_url": u,
                "aliases": [],
                "priority": 0,
                "canonical": False,
            })

        return out

    # -------------------------
    # CSV / pipe parsing
    # -------------------------
    def norm_bool(s: str) -> bool:
        return str(s or "").strip().lower() in ("1", "true", "yes", "y")

    out: List[Dict[str, Any]] = []

    head = [h.strip().lower() for h in lines[0].split(",")]
    looks_csv = ("topic_id" in head) or ("working_title" in head) or ("planned_slug" in head)

    if looks_csv:
        header = head

        def idx(name: str) -> int:
            try:
                return header.index(name)
            except ValueError:
                return -1

        for row in lines[1:MAX_ROWS+1]:
            parts = [p.strip() for p in row.split(",")]

            def get(name: str) -> str:
                i = idx(name)
                return parts[i] if (i >= 0 and i < len(parts)) else ""

            topic_id = get("topic_id") or get("id")
            working_title = get("working_title") or get("title")
            planned_slug = get("planned_slug")
            planned_url  = get("planned_url")
            aliases_str  = get("aliases")
            priority_raw = get("priority")
            canonical    = norm_bool(get("canonical"))

            if not topic_id or not working_title:
                continue

            try:
                priority = int(priority_raw or "0")
            except Exception:
                priority = 0

            aliases = [a.strip() for a in (aliases_str or "").split("|") if a.strip()]

            out.append({
                "topic_id": topic_id,
                "working_title": working_title,
                "planned_slug": planned_slug,
                "planned_url": planned_url,
                "aliases": aliases,
                "priority": priority,
                "canonical": canonical,
            })
    else:
        for row in lines[:MAX_ROWS]:
            parts = [p.strip() for p in row.split("|")]
            while len(parts) < 7:
                parts.append("")

            topic_id, working_title, planned_slug, planned_url, aliases_str, priority_str, canonical_str = parts[:7]

            if not topic_id or not working_title:
                continue

            aliases = [a.strip() for a in (aliases_str or "").split(",") if a.strip()] or \
                      [a.strip() for a in (aliases_str or "").split("|") if a.strip()]

            try:
                priority = int(priority_str or "0")
            except Exception:
                priority = 0

            out.append({
                "topic_id": topic_id,
                "working_title": working_title,
                "planned_slug": planned_slug,
                "planned_url": planned_url,
                "aliases": aliases,
                "priority": priority,
                "canonical": norm_bool(canonical_str),
            })

    return out


# -------------------------
# Routes
# -------------------------
@router.post("/import")
async def import_draft(
    file: UploadFile = File(...),
    workspace_id: str = Query("default"),
):
    raw = await file.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")

    text = raw.decode("utf-8", errors="replace")
    parsed = _parse_draft_text(text)

    path = _path_for_workspace(workspace_id)

    existing = _safe_read_json(path)
    existing_list = existing if isinstance(existing, list) else []
    index: Dict[str, Dict[str, Any]] = {}

    for item in existing_list:
        if isinstance(item, dict) and item.get("topic_id"):
            index[str(item["topic_id"]).strip()] = item

    added = 0
    updated = 0
    for item in parsed:
        tid = str(item.get("topic_id") or "").strip()
        if not tid:
            continue
        if tid in index:
            index[tid].update(item)
            updated += 1
        else:
            index[tid] = item
            added += 1

    merged = list(index.values())
    _atomic_write_json(path, merged)

    # ✅ write meta file
    _write_meta(workspace_id, file.filename or "", added, updated, len(merged), path)

    return {
        "ok": True,
        "workspace_id": _ws_safe(workspace_id),
        "added": added,
        "updated": updated,
        "total": len(merged),
    }

@router.get("/list")
async def list_draft(
    workspace_id: str = Query("default"),
    limit: int = Query(50000, ge=1, le=200000),
):
    path = _path_for_workspace(workspace_id)
    raw = _safe_read_json(path)
    items = raw if isinstance(raw, list) else []
    if len(items) > limit:
        items = items[:limit]
    return {"workspace_id": _ws_safe(workspace_id), "count": len(items), "topics": items}

@router.get("/meta")
async def draft_meta(workspace_id: str = Query("default")):
    meta_path = _meta_path_for_workspace(workspace_id)
    raw = _safe_read_json(meta_path)
    return raw if isinstance(raw, dict) else {"workspace_id": _ws_safe(workspace_id), "meta": None}

@router.post("/clear")
async def clear_draft(workspace_id: str = Query("default")):
    path = _path_for_workspace(workspace_id)
    _atomic_write_json(path, [])
    # also clear meta (optional: set to empty)
    _atomic_write_json(_meta_path_for_workspace(workspace_id), {
        "workspace_id": _ws_safe(workspace_id),
        "last_import_at_utc": None,
        "last_import_filename": "",
        "last_import_added": 0,
        "last_import_updated": 0,
        "total_topics": 0,
        "data_path": path,
    })
    return {"ok": True, "workspace_id": _ws_safe(workspace_id), "cleared": True}
