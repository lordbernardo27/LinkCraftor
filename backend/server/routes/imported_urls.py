from fastapi import APIRouter, UploadFile, File, HTTPException, Query
import os
import json
import re
from typing import Any, List
from datetime import datetime, timezone

router = APIRouter(prefix="/api/urls", tags=["urls"])

MAX_BYTES = 10 * 1024 * 1024  # 10MB
MAX_URLS_PER_IMPORT = 200000  # hard guard

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
    return os.path.join(_data_dir(), f"imported_urls_{ws}.json")

def _meta_path_for_workspace(workspace_id: str) -> str:
    ws = _ws_safe(workspace_id)
    return os.path.join(_data_dir(), f"imported_urls_{ws}.meta.json")

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

def _load_urls(path: str) -> List[str]:
    raw = _safe_read_json(path)
    if isinstance(raw, list):
        out = []
        for x in raw:
            s = str(x).strip()
            if s:
                out.append(s)
        return out
    return []

def _load_meta(meta_path: str) -> dict:
    raw = _safe_read_json(meta_path)
    return raw if isinstance(raw, dict) else {}

# -------------------------
# Parsing + normalization
# -------------------------

def _normalize_url(url: str) -> str:
    url = (url or "").strip().strip('"')
    if not re.match(r"^https?://", url, flags=re.I):
        return ""
    url = url.split("#", 1)[0]  # remove fragment
    return url

def _parse_txt(text: str):
    for line in text.splitlines():
        u = _normalize_url(line)
        if u:
            yield u

def _parse_csv(text: str):
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        cand = next((p for p in parts if re.match(r"^https?://", p, flags=re.I)), "")
        u = _normalize_url(cand)
        if u:
            yield u

def _parse_xml(text: str):
    # Minimal <loc> extraction without DOM building
    for m in re.finditer(r"<loc>\s*([^<\s]+)\s*</loc>", text, flags=re.I):
        u = _normalize_url(m.group(1))
        if u:
            yield u

# -------------------------
# Routes
# -------------------------

@router.post("/import")
async def import_urls(
    file: UploadFile = File(...),
    workspace_id: str = Query("default"),
):
    raw = await file.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")

    text = raw.decode("utf-8", errors="replace")
    name = (file.filename or "").lower()

    if name.endswith(".csv"):
        incoming = list(_parse_csv(text))
    elif name.endswith(".xml"):
        incoming = list(_parse_xml(text))
    else:
        incoming = list(_parse_txt(text))

    # Hard cap
    if len(incoming) > MAX_URLS_PER_IMPORT:
        incoming = incoming[:MAX_URLS_PER_IMPORT]

    path = _path_for_workspace(workspace_id)
    meta_path = _meta_path_for_workspace(workspace_id)

    existing = _load_urls(path)
    s = set(existing)

    added = 0
    for u in incoming:
        if u not in s:
            s.add(u)
            added += 1

    merged = sorted(s)
    _atomic_write_json(path, merged)

    # Write meta (stats)
    meta = _load_meta(meta_path)
    meta.update({
        "workspace_id": _ws_safe(workspace_id),
        "last_import_at_utc": datetime.now(timezone.utc).isoformat(),
        "last_import_filename": file.filename or "",
        "last_import_added": int(added),
        "total_urls": int(len(merged)),
        "data_path": path,
    })
    _atomic_write_json(meta_path, meta)

    return {"added": added, "total": len(merged), "workspace_id": _ws_safe(workspace_id)}

@router.get("/list")
async def list_urls(
    workspace_id: str = Query("default"),
    limit: int = Query(50000, ge=1, le=200000),
):
    path = _path_for_workspace(workspace_id)
    urls = _load_urls(path)
    if limit and len(urls) > limit:
        urls = urls[:limit]
    return {"workspace_id": _ws_safe(workspace_id), "count": len(urls), "urls": urls}

@router.get("/stats")
async def stats_urls(workspace_id: str = Query("default")):
    path = _path_for_workspace(workspace_id)
    meta_path = _meta_path_for_workspace(workspace_id)

    urls = _load_urls(path)
    meta = _load_meta(meta_path)

    # Always return something useful even if meta missing
    return {
        "workspace_id": _ws_safe(workspace_id),
        "total_urls": len(urls),
        "last_import_at_utc": meta.get("last_import_at_utc", ""),
        "last_import_filename": meta.get("last_import_filename", ""),
        "last_import_added": meta.get("last_import_added", 0),
        "data_path": meta.get("data_path", path),
        "meta_path": meta_path,
    }

@router.post("/clear")
async def clear_urls(workspace_id: str = Query("default")):
    path = _path_for_workspace(workspace_id)
    meta_path = _meta_path_for_workspace(workspace_id)

    _atomic_write_json(path, [])
    _atomic_write_json(meta_path, {
        "workspace_id": _ws_safe(workspace_id),
        "last_import_at_utc": "",
        "last_import_filename": "",
        "last_import_added": 0,
        "total_urls": 0,
        "data_path": path,
    })

    return {"workspace_id": _ws_safe(workspace_id), "cleared": True}
