from __future__ import annotations

import os
import re
import csv
from typing import List, Dict, Any, Optional, Tuple
import xml.etree.ElementTree as ET

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Request
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/api/urls", tags=["urls-compat"])
IMPORTS_COMPAT_BUILD = "2026-03-01-URLS-COMPAT-B"


# -------------------------
# Workspace-safe helpers
# -------------------------
_WS_RE = re.compile(r"[^a-z0-9_\-]")

def _ws_safe(ws: str) -> str:
    ws = (ws or "default").strip().lower()
    return (_WS_RE.sub("_", ws)[:80] or "default")

def _data_dir() -> str:
    # backend/server/data
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def _targets_base(ws: str) -> str:
    return os.path.join(_data_dir(), f"imported_targets_{_ws_safe(ws)}")

def _paths(ws: str) -> Dict[str, str]:
    base = _targets_base(ws)
    return {"csv": base + ".csv", "txt": base + ".txt", "xml": base + ".xml"}

def _ensure_data_dir() -> None:
    os.makedirs(_data_dir(), exist_ok=True)

def _dedupe(urls: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for u in urls:
        u = (u or "").strip()
        if not u:
            continue
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out

def _is_url(s: str) -> bool:
    s = (s or "").strip()
    return s.startswith("http://") or s.startswith("https://")


# -------------------------
# Readers (WS-only files)
# -------------------------
def _read_csv(path: str) -> List[str]:
    if not os.path.exists(path):
        return []
    out: List[str] = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = (row.get("URL") or row.get("url") or row.get("Url") or "").strip()
                if _is_url(u):
                    out.append(u)
    except Exception:
        return []
    return out

def _read_txt(path: str) -> List[str]:
    if not os.path.exists(path):
        return []
    out: List[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                u = (line or "").strip()
                if _is_url(u):
                    out.append(u)
    except Exception:
        return []
    return out

def _read_xml(path: str) -> List[str]:
    if not os.path.exists(path):
        return []
    out: List[str] = []
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        for el in root.findall(".//{*}loc"):
            if el is not None and el.text and el.text.strip():
                u = el.text.strip()
                if _is_url(u):
                    out.append(u)
    except Exception:
        return []
    return out

def _load_all(ws: str) -> Dict[str, Any]:
    p = _paths(ws)
    urls_csv = _read_csv(p["csv"])
    urls_txt = _read_txt(p["txt"])
    urls_xml = _read_xml(p["xml"])
    merged = _dedupe(urls_csv + urls_txt + urls_xml)
    return {
        "paths": p,
        "counts": {
            "csv": len(urls_csv),
            "txt": len(urls_txt),
            "xml": len(urls_xml),
            "total_unique": len(merged),
        },
        "urls": merged,
    }


# -------------------------
# WorkspaceId shim (frontend may send workspaceId)
# -------------------------
def _pick_ws(workspace_id: Optional[str], workspaceId: Optional[str]) -> str:
    """
    Frontend sometimes sends workspace_id=default even when user selected a workspace.
    Temporary server-side override:
      - If workspace is missing or 'default', route to ws_betterhealthcheck_com.
    Change DEFAULT_FALLBACK_WS to your preferred workspace.
    """
    DEFAULT_FALLBACK_WS = "ws_betterhealthcheck_com"

    ws = (workspace_id or workspaceId or "").strip()
    if not ws or ws.lower() == "default":
        ws = DEFAULT_FALLBACK_WS
    return ws


# -------------------------
# Endpoints
# -------------------------
@router.get("/list")
def list_urls(
    workspace_id: Optional[str] = Query(None),
    workspaceId: Optional[str] = Query(None),
    limit: int = Query(200000, ge=1, le=500000),
):
    ws = _pick_ws(workspace_id, workspaceId)
    data = _load_all(ws)
    urls = data["urls"][: int(limit)]
    return {
        "ok": True,
        "build": IMPORTS_COMPAT_BUILD,
        "workspace_id": ws,
        "count": len(urls),
        "counts": data["counts"],
        "paths": data["paths"],
        "urls": urls,
    }


async def _extract_upload_from_request(request: Request) -> Tuple[Optional[str], bytes]:
    """
    Accepts:
      - multipart/form-data with many possible file field names
      - raw body (text/plain, text/csv, application/xml, etc.)
    Returns (filename, bytes).
    """
    ct = (request.headers.get("content-type") or "").lower()

    def _is_uploadfile_like(v: Any) -> bool:
        # Starlette/FastAPI UploadFile-like: has .filename and async .read()
        return hasattr(v, "filename") and hasattr(v, "read")

    # multipart
    if "multipart/form-data" in ct:
        form = await request.form()

        # common keys first
        for key in ("file", "upload", "uploads", "files", "files[]", "sitemap", "sitemapFile"):
            v = form.get(key)
            if v is None:
                continue

            # if multiple files
            if isinstance(v, list) and v:
                v = v[0]

            # UploadFile-like
            if _is_uploadfile_like(v):
                data = await v.read()
                return (getattr(v, "filename", None) or "upload.bin"), (data or b"")

            # sometimes frameworks put raw bytes/string in the form
            if isinstance(v, (bytes, bytearray)):
                return ("upload.bin", bytes(v))
            if isinstance(v, str) and v.strip():
                return ("upload.txt", v.encode("utf-8"))

        # fallback: grab the first UploadFile-like entry anywhere in form
        try:
            items = form.multi_items()
        except Exception:
            items = list(form.items())

        for _, v in items:
            if isinstance(v, list) and v:
                v = v[0]

            if _is_uploadfile_like(v):
                data = await v.read()
                return (getattr(v, "filename", None) or "upload.bin"), (data or b"")

            if isinstance(v, (bytes, bytearray)):
                return ("upload.bin", bytes(v))
            if isinstance(v, str) and v.strip():
                return ("upload.txt", v.encode("utf-8"))

        return (None, b"")

    # raw body
    data = await request.body()
    return ("upload.bin", data or b"")


def _infer_ext(filename: str, content_type: str) -> str:
    fn = (filename or "").lower().strip()

    if fn.endswith(".csv"):
        return "csv"
    if fn.endswith(".txt"):
        return "txt"
    if fn.endswith(".xml"):
        return "xml"

    ct = (content_type or "").lower()
    if "text/csv" in ct:
        return "csv"
    if "application/xml" in ct or "text/xml" in ct:
        return "xml"
    if "text/plain" in ct:
        return "txt"

    # default safest
    return "txt"


@router.post("/upload")
async def upload_urls(
    request: Request,
    workspace_id: Optional[str] = Query(None),
    workspaceId: Optional[str] = Query(None),
):
    """
    Frontend legacy upload -> writes to WS-only imported_targets_<ws>.<ext>.
    Supports multipart OR raw body.
    """
    ws = _pick_ws(workspace_id, workspaceId)

    filename, data = await _extract_upload_from_request(request)
    if not data:
        raise HTTPException(status_code=400, detail="Empty upload")

    _ensure_data_dir()
    p = _paths(ws)

    ext = _infer_ext(filename or "", request.headers.get("content-type") or "")
    out_path = p.get(ext)
    if not out_path:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        with open(out_path, "wb") as f:
            f.write(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save: {e}")

    after = _load_all(ws)
    return {
        "ok": True,
        "build": IMPORTS_COMPAT_BUILD,
        "workspace_id": ws,
        "saved_to": out_path,
        "counts": after["counts"],
        "total_unique": after["counts"]["total_unique"],
    }


# Alias: some frontend code uses /api/urls/import instead of /upload
@router.post("/import")
async def import_urls(
    request: Request,
    workspace_id: Optional[str] = Query(None),
    workspaceId: Optional[str] = Query(None),
):
    return await upload_urls(request=request, workspace_id=workspace_id, workspaceId=workspaceId)


@router.post("/clear")
def clear_urls(
    workspace_id: Optional[str] = Query(None),
    workspaceId: Optional[str] = Query(None),
):
    ws = _pick_ws(workspace_id, workspaceId)
    p = _paths(ws)
    removed = []
    for _, path in p.items():
        if os.path.exists(path):
            try:
                os.remove(path)
                removed.append(path)
            except Exception:
                pass
    after = _load_all(ws)
    return {
        "ok": True,
        "build": IMPORTS_COMPAT_BUILD,
        "workspace_id": ws,
        "removed": removed,
        "counts": after["counts"],
    }