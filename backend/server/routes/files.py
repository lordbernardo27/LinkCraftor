# backend/server/routes/files.py
from __future__ import annotations

from __future__ import annotations

import os
import json
import uuid
import re
import html
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Body
from fastapi.responses import FileResponse

import mammoth

from backend.server.stores.upload_intel_store import build_upload_intelligence

# ✅ Strict DOCX style-based H1 extraction (no fallbacks)
try:
    from docx import Document as DocxDocument  # python-docx
except Exception:
    DocxDocument = None


router = APIRouter(prefix="/api/files", tags=["files"])
legacy_router = APIRouter(prefix="/api", tags=["legacy"])

ALLOWED_EXT = {".docx", ".txt", ".md", ".html", ".htm"}

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/server
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"

TEXT_LIMIT = 200_000

# -------------------------
# STRICT H1 extraction helpers (NO FALLBACKS)
# -------------------------
_H1_TAG_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
_TAG_STRIP_RE = re.compile(r"<[^>]+>")
_WS_SAFE_RE = re.compile(r"[^a-z0-9_]+", re.IGNORECASE)


def _strip_tags_basic(s: str) -> str:
    s = _TAG_STRIP_RE.sub(" ", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _quality_gate_h1(h: str) -> Tuple[bool, str]:
    t = (h or "").strip()
    if len(t) < 4:
        return False, "too_short"
    if len(t) > 140:
        return False, "too_long"

    letters_digits = sum(ch.isalnum() for ch in t)
    if letters_digits < max(3, int(len(t) * 0.35)):
        return False, "too_symbolic"

    low = t.lower()
    generic = {
        "introduction",
        "overview",
        "table of contents",
        "contents",
        "home",
        "welcome",
        "summary",
        "conclusion",
    }
    if low in generic:
        return False, "generic_heading"

    return True, ""


def _normalize_docx_title_in_place(stored_path: str) -> Dict[str, Any]:
    if not stored_path:
        return {"ok": False, "error": "docx_missing_path"}
    if DocxDocument is None:
        return {"ok": False, "error": "python_docx_not_available"}

    try:
        doc = DocxDocument(stored_path)
    except Exception as e:
        return {"ok": False, "error": f"docx_read_failed:{str(e)[:120]}"}

    paras = getattr(doc, "paragraphs", []) or []
    if not paras:
        return {"ok": True, "changed": False, "reason": "no_paragraphs"}

    first_h2_idx = None
    for i, p in enumerate(paras):
        try:
            sname = (p.style.name or "").strip()
        except Exception:
            sname = ""
        if sname in ("Heading 2", "Heading 3", "Heading 4", "Heading 5", "Heading 6"):
            first_h2_idx = i
            break

    search_upto = first_h2_idx if first_h2_idx is not None else len(paras)
    target_i = None
    target_p = None

    for i in range(search_upto):
        p = paras[i]
        txt = (getattr(p, "text", "") or "").strip()
        if not txt:
            continue
        target_i = i
        target_p = p
        break

    if target_p is None:
        return {"ok": True, "changed": False, "reason": "no_nonempty_para"}

    try:
        cur_style = (target_p.style.name or "").strip()
    except Exception:
        cur_style = ""

    if cur_style in ("Title", "Heading 1"):
        return {"ok": True, "changed": False, "reason": f"already_{cur_style}", "para_index": target_i}

    ok, reason = _quality_gate_h1((getattr(target_p, "text", "") or "").strip())
    if not ok:
        return {"ok": True, "changed": False, "reason": f"failed_quality_gate:{reason}", "para_index": target_i}

    try:
        target_p.style = "Title"
    except Exception as e:
        return {"ok": False, "error": f"set_style_failed:{str(e)[:120]}", "para_index": target_i}

    try:
        doc.save(stored_path)
    except Exception as e:
        return {"ok": False, "error": f"docx_save_failed:{str(e)[:120]}", "para_index": target_i}

    return {
        "ok": True,
        "changed": True,
        "reason": "promoted_first_para_to_Title",
        "para_index": target_i,
        "from_style": cur_style,
    }


def _strict_h1_from_docx_file(stored_path: str) -> Tuple[str, str, str]:
    if not stored_path:
        return "", "", "docx_missing_path"
    if DocxDocument is None:
        return "", "", "docx_reader_unavailable"

    try:
        doc = DocxDocument(stored_path)
    except Exception as e:
        return "", "", f"docx_read_failed:{str(e)[:120]}"

    for p in getattr(doc, "paragraphs", []) or []:
        txt = (getattr(p, "text", "") or "").strip()
        if not txt:
            continue

        style_name = ""
        try:
            style_name = (p.style.name or "").strip()
        except Exception:
            style_name = ""

        if style_name in ("Heading 1", "Title"):
            ok, reason = _quality_gate_h1(txt)
            if not ok:
                return "", "", f"failed_quality_gate:{reason}"
            return txt, f"docx:{style_name}", ""

    return "", "", "no_strict_h1_found"


def _strict_h1_from_html(preview_html: str) -> Tuple[str, str, str]:
    html_in = preview_html or ""
    m = _H1_TAG_RE.search(html_in)
    if not m:
        return "", "", "no_strict_h1_found"

    cand = _strip_tags_basic(m.group(1) or "")
    ok, reason = _quality_gate_h1(cand)
    if not ok:
        return "", "", f"failed_quality_gate:{reason}"
    return cand, "html:h1", ""


def _strict_h1_from_md(preview_text: str) -> Tuple[str, str, str]:
    txt = preview_text or ""
    for line in txt.splitlines():
        line = (line or "").strip()
        if line.startswith("# "):
            cand = line[2:].strip()
            ok, reason = _quality_gate_h1(cand)
            if not ok:
                return "", "", f"failed_quality_gate:{reason}"
            return cand, "md:#", ""
    return "", "", "no_strict_h1_found"


def _derive_h1_for_index(
    *,
    ext: str,
    preview_html: str,
    preview_text: str,
    stored_path: str | None = None,
) -> Tuple[str, str, str]:
    e = (ext or "").lower().strip()

    if e == ".docx":
        return _strict_h1_from_docx_file(stored_path or "")

    if e in (".html", ".htm"):
        return _strict_h1_from_html(preview_html or "")

    if e in (".md", ".markdown"):
        return _strict_h1_from_md(preview_text or "")

    if e == ".txt":
        return "", "", "txt_no_structural_h1"

    return "", "", "no_strict_h1_found"


# -------------------------
# Workspace helpers (WS-only)
# -------------------------
def _ws(workspace_id: str) -> str:
    raw = (workspace_id or "default").strip()
    if not raw:
        return "default"

    if raw.lower() == "default":
        return "default"

    raw = raw.lower()
    if raw.startswith("ws_ws_"):
        raw = raw[3:]

    if raw.startswith("ws_"):
        return raw

    s = raw.replace(".", "_").replace("-", "_").replace(" ", "_")
    s = _WS_SAFE_RE.sub("_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        return "default"
    return f"ws_{s}"[:80]


def _ws_dir(workspace_id: str) -> Path:
    return DOCS_DIR / _ws(workspace_id)


def _index_path(workspace_id: str) -> Path:
    return _ws_dir(workspace_id) / "index.json"


def _safe_read_index(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [x for x in data if isinstance(x, dict)] if isinstance(data, list) else []
    except Exception:
        return []


def _safe_write_index(path: Path, items: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _guess_ext(filename: str) -> str:
    return (Path((filename or "").strip()).suffix or "").lower()


def _strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


# -------------------------
# Work Folder index (backend ledger)
# -------------------------
def _work_index_path(workspace_id: str) -> Path:
    return _ws_dir(workspace_id) / "work_index.json"


def _safe_read_work_index(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [x for x in data if isinstance(x, dict)] if isinstance(data, list) else []
    except Exception:
        return []


def _safe_write_work_index(path: Path, items: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _work_append(workspace_id: str, entry: Dict[str, Any]) -> None:
    p = _work_index_path(workspace_id)
    items = _safe_read_work_index(p)
    items.append(entry)
    _safe_write_work_index(p, items)


# -------------------------
# Save snapshots
# -------------------------
def _snapshot_dir(workspace_id: str) -> Path:
    p = _ws_dir(workspace_id) / "snapshots"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _safe_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content or "", encoding="utf-8")
    os.replace(tmp, path)


# -------------------------
# Preview helpers
# -------------------------
def _html_escape(s: str) -> str:
    return html.escape(s or "", quote=False)


def _decode_text_bytes(raw: bytes) -> str:
    try:
        s = raw.decode("utf-8")
    except Exception:
        try:
            s = raw.decode("utf-8", errors="ignore")
        except Exception:
            s = raw.decode(errors="ignore")
    return (s or "").lstrip("\ufeff")


def _extract_preview_from_bytes(filename: str, ext: str, raw: bytes) -> Dict[str, Any]:
    ext = (ext or "").lower().strip()

    text: str = ""
    html_out: str = ""
    is_html: bool = False
    truncated: bool = False

    if ext == ".txt":
        text = _decode_text_bytes(raw)
        html_out = "<pre>" + _html_escape(text) + "</pre>"
        is_html = False

    elif ext == ".md":
        md = _decode_text_bytes(raw)
        try:
            import markdown2
            html_out = markdown2.markdown(md)
            text = _strip_tags(html_out)
            is_html = True
        except Exception:
            text = md
            html_out = "<pre>" + _html_escape(md) + "</pre>"
            is_html = False

    elif ext in (".html", ".htm"):
        html_raw = _decode_text_bytes(raw)
        html_out = html_raw
        text = _strip_tags(html_raw)
        is_html = True

    elif ext == ".docx":
        import io
        with io.BytesIO(raw) as buff:
            result = mammoth.convert_to_html(buff)
            html_out = result.value or ""
        try:
            with io.BytesIO(raw) as buff2:
                raw_text = mammoth.extract_raw_text(buff2)
                text = (raw_text.value or "").strip()
        except Exception:
            text = _strip_tags(html_out or "")
        is_html = True

    else:
        text = _decode_text_bytes(raw)
        html_out = "<pre>" + _html_escape(text) + "</pre>"
        is_html = False

    if len(text) > TEXT_LIMIT:
        text = text[:TEXT_LIMIT]
        truncated = True

    return {
        "filename": Path(filename).name,
        "ext": ext,
        "text": text,
        "html": html_out,
        "is_html": bool(is_html),
        "truncated": bool(truncated),
    }


def _store_and_index(
    workspace_id: str,
    file: UploadFile,
    raw: bytes,
    *,
    preview_html: str,
    preview_text: str,
) -> Dict[str, Any]:
    ext = _guess_ext(file.filename)
    ws_dir = _ws_dir(workspace_id)
    ws_dir.mkdir(parents=True, exist_ok=True)

    doc_id = uuid.uuid4().hex
    safe_name = Path(file.filename).name
    stored_name = f"{doc_id}__{safe_name}"
    stored_path = ws_dir / stored_name
    stored_path.write_bytes(raw)

    normalize_info: Dict[str, Any] = {}
    if ext == ".docx":
        normalize_info = _normalize_docx_title_in_place(str(stored_path))

    h1, h1_source, h1_error = _derive_h1_for_index(
        ext=ext,
        preview_html=preview_html or "",
        preview_text=preview_text or "",
        stored_path=str(stored_path),
    )

    meta = {
        "doc_id": doc_id,
        "filename": safe_name,
        "ext": ext,
        "bytes": len(raw),
        "content_type": file.content_type or "",
        "uploaded_at": datetime.utcnow().isoformat() + "Z",
        "stored_name": stored_name,
        "h1": h1,
        "h1_source": h1_source,
        "h1_error": h1_error,
        "docx_normalize": normalize_info if ext == ".docx" else {},
    }

    idx_path = _index_path(workspace_id)
    items = _safe_read_index(idx_path)
    items.append(meta)
    _safe_write_index(idx_path, items)
    return meta


def _update_index_h1(
    workspace_id: str,
    doc_id: str,
    *,
    ext: str,
    html_in: str,
    text_in: str,
) -> Dict[str, Any] | None:
    idxp = _index_path(workspace_id)
    items = _safe_read_index(idxp)

    ws_dir = _ws_dir(workspace_id)

    for rec in items:
        if isinstance(rec, dict) and str(rec.get("doc_id") or "") == doc_id:
            stored_name = str(rec.get("stored_name") or "")
            stored_path = str(ws_dir / stored_name) if stored_name else None

            if (ext or "").lower().strip() == ".docx" and stored_path:
                _normalize_docx_title_in_place(stored_path)

            h1, h1_source, h1_error = _derive_h1_for_index(
                ext=ext,
                preview_html=html_in or "",
                preview_text=text_in or "",
                stored_path=stored_path,
            )
            rec["h1"] = h1
            rec["h1_source"] = h1_source
            rec["h1_error"] = h1_error
            rec["h1_updated_at"] = datetime.utcnow().isoformat() + "Z"
            _safe_write_index(idxp, items)
            return rec
    return None


# -------------------------
# API
# -------------------------
@router.post("/upload")
async def upload_file(workspace_id: str = Query("ws_betterhealthcheck_com"), file: UploadFile = File(...)):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    ext = _guess_ext(file.filename)
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"File type not allowed: {ext}")

    ws_norm = _ws(workspace_id)

    raw = await file.read()
    preview = _extract_preview_from_bytes(Path(file.filename).name, ext, raw)

    meta = _store_and_index(
        ws_norm,
        file,
        raw,
        preview_html=str(preview.get("html") or ""),
        preview_text=str(preview.get("text") or ""),
    )

    @router.post("/upload")
    async def upload_file(workspace_id: str = Query("ws_betterhealthcheck_com"), file: UploadFile = File(...)):
     if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    ext = _guess_ext(file.filename)
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"File type not allowed: {ext}")

    ws_norm = _ws(workspace_id)

    raw = await file.read()
    preview = _extract_preview_from_bytes(Path(file.filename).name, ext, raw)

    meta = _store_and_index(
        ws_norm,
        file,
        raw,
        preview_html=str(preview.get("html") or ""),
        preview_text=str(preview.get("text") or ""),
    )

    try:
        stored_path = str(_ws_dir(ws_norm) / (meta.get("stored_name") or ""))
        intel_result = build_upload_intelligence(
            workspace_id=ws_norm,
            doc_id=str(meta.get("doc_id") or ""),
            stored_path=stored_path,
            original_name=str(meta.get("filename") or ""),
            html=str(preview.get("html") or ""),
            text=str(preview.get("text") or ""),
        )
        print("[UPLOAD_INTEL_OK]", json.dumps(intel_result, ensure_ascii=False))
    except Exception as e:
        print("[UPLOAD_INTEL_ERROR]", repr(e))
        traceback.print_exc()

    _work_append(ws_norm, {
        "ts": datetime.utcnow().isoformat() + "Z",
        "type": "upload",
        "doc_id": meta.get("doc_id"),
        "filename": meta.get("filename"),
        "h1": meta.get("h1"),
        "h1_source": meta.get("h1_source"),
        "h1_error": meta.get("h1_error"),
        "docx_normalize": meta.get("docx_normalize") or {},
    })

    return {
        "ok": True,
        "workspace_id": ws_norm,
        "doc": meta,
        "filename": preview.get("filename"),
        "ext": preview.get("ext"),
        "text": preview.get("text"),
        "html": preview.get("html"),
        "is_html": bool(preview.get("is_html")),
        "truncated": bool(preview.get("truncated")),
    }


    _work_append(ws_norm, {
        "ts": datetime.utcnow().isoformat() + "Z",
        "type": "upload",
        "doc_id": meta.get("doc_id"),
        "filename": meta.get("filename"),
        "h1": meta.get("h1"),
        "h1_source": meta.get("h1_source"),
        "h1_error": meta.get("h1_error"),
        "docx_normalize": meta.get("docx_normalize") or {},
    })

    return {
        "ok": True,
        "workspace_id": ws_norm,
        "doc": meta,
        "filename": preview.get("filename"),
        "ext": preview.get("ext"),
        "text": preview.get("text"),
        "html": preview.get("html"),
        "is_html": bool(preview.get("is_html")),
        "truncated": bool(preview.get("truncated")),
    }


@router.get("/list")
def list_files(workspace_id: str = Query("ws_betterhealthcheck_com")):
    ws_norm = _ws(workspace_id)
    items = _safe_read_index(_index_path(ws_norm))
    items.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)

    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        out.append({
            "doc_id": it.get("doc_id"),
            "filename": it.get("filename"),
            "stored_name": it.get("stored_name"),
            "uploaded_at": it.get("uploaded_at"),
            "h1": it.get("h1") or "",
            "h1_source": it.get("h1_source") or "",
            "h1_error": it.get("h1_error") or "",
        })

    return {"ok": True, "workspace_id": ws_norm, "items": out}


@router.get("/h1s")
def list_h1s(workspace_id: str = Query("ws_betterhealthcheck_com")):
    ws_norm = _ws(workspace_id)
    items = _safe_read_index(_index_path(ws_norm))

    h1s: List[str] = []
    seen: set[str] = set()

    for it in items:
        if not isinstance(it, dict):
            continue
        h = str(it.get("h1") or "").strip()
        if not h:
            continue
        if h in seen:
            continue
        seen.add(h)
        h1s.append(h)

    return {"ok": True, "workspace_id": ws_norm, "h1s": h1s}


@router.post("/reindex_h1s")
def reindex_h1s(workspace_id: str = Query("ws_betterhealthcheck_com")):
    ws_norm = _ws(workspace_id)
    ws_dir = _ws_dir(ws_norm)
    ws_dir.mkdir(parents=True, exist_ok=True)

    entries: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for p in ws_dir.iterdir():
        if not p.is_file():
            continue
        name = p.name
        if name == "index.json" or name == "work_index.json":
            continue
        if name.endswith(".tmp"):
            continue
        if "__" not in name:
            continue

        doc_id, safe_name = name.split("__", 1)
        doc_id = (doc_id or "").strip()
        safe_name = (safe_name or "").strip()
        if not doc_id or len(doc_id) < 16:
            continue

        ext = _guess_ext(safe_name)
        if ext not in ALLOWED_EXT:
            continue

        if ext == ".docx":
            _normalize_docx_title_in_place(str(p))

        try:
            raw = p.read_bytes()
        except Exception as e:
            errors.append({"file": name, "error": "read_failed", "detail": str(e)[:120]})
            continue

        preview = _extract_preview_from_bytes(safe_name, ext, raw)
        h1, h1_source, h1_error = _derive_h1_for_index(
            ext=ext,
            preview_html=str(preview.get("html") or ""),
            preview_text=str(preview.get("text") or ""),
            stored_path=str(p),
        )

        try:
            uploaded_at = datetime.utcfromtimestamp(p.stat().st_mtime).isoformat() + "Z"
            size_bytes = int(p.stat().st_size)
        except Exception:
            uploaded_at = datetime.utcnow().isoformat() + "Z"
            size_bytes = len(raw)

        entries.append({
            "doc_id": doc_id,
            "filename": safe_name,
            "ext": ext,
            "bytes": size_bytes,
            "content_type": "",
            "uploaded_at": uploaded_at,
            "stored_name": name,
            "h1": h1,
            "h1_source": h1_source,
            "h1_error": h1_error,
        })

    entries.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
    idx_path = _index_path(ws_norm)
    _safe_write_index(idx_path, entries)

    return {
        "ok": True,
        "workspace_id": ws_norm,
        "reindexed": len(entries),
        "with_h1": sum(1 for e in entries if (e.get("h1") or "").strip()),
        "missing_h1": sum(1 for e in entries if not (e.get("h1") or "").strip()),
        "errors": errors,
        "index_path": str(idx_path),
    }


@router.get("/docx_style_debug")
def docx_style_debug(
    workspace_id: str = Query("ws_betterhealthcheck_com"),
    doc_id: str = Query(...),
    limit: int = Query(40, ge=1, le=200),
):
    ws_norm = _ws(workspace_id)

    items = _safe_read_index(_index_path(ws_norm))
    hit = next((x for x in items if x.get("doc_id") == doc_id), None)
    if not hit:
        raise HTTPException(status_code=404, detail="doc_id not found")

    ext = str(hit.get("ext") or "").lower()
    if ext != ".docx":
        raise HTTPException(status_code=400, detail="docx_only")

    stored_name = str(hit.get("stored_name") or "")
    p = _ws_dir(ws_norm) / stored_name
    if not p.exists():
        raise HTTPException(status_code=404, detail="stored_file_missing")

    if DocxDocument is None:
        raise HTTPException(status_code=500, detail="python_docx_not_available")

    try:
        doc = DocxDocument(str(p))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"docx_read_failed:{str(e)[:160]}")

    out = []
    paras = getattr(doc, "paragraphs", []) or []
    for i, para in enumerate(paras[:limit]):
        txt = (getattr(para, "text", "") or "").strip()
        if not txt:
            continue
        try:
            style_name = (para.style.name or "").strip()
        except Exception:
            style_name = ""
        out.append({"i": i, "style": style_name, "text": txt[:200]})

    return {
        "ok": True,
        "workspace_id": ws_norm,
        "doc_id": doc_id,
        "filename": hit.get("filename"),
        "items": out,
    }


@router.post("/save")
async def save_doc(
    workspace_id: str = Query("ws_betterhealthcheck_com"),
    doc_id: str = Query(...),
    payload: Dict[str, Any] = Body(default_factory=dict),
):
    ws_norm = _ws(workspace_id)

    doc_id = (doc_id or "").strip()
    if not doc_id:
        raise HTTPException(status_code=400, detail="doc_id is required")

    items = _safe_read_index(_index_path(ws_norm))
    hit = next((x for x in items if x.get("doc_id") == doc_id), None)
    if not hit:
        raise HTTPException(status_code=404, detail="doc_id not found")

    html_in = str((payload or {}).get("html") or "").strip()
    text_in = str((payload or {}).get("text") or "")

    if not html_in:
        raise HTTPException(status_code=400, detail="html is required")

    ts_compact = datetime.utcnow().isoformat().replace(":", "").replace("-", "") + "Z"
    snap_name = f"{doc_id}__{ts_compact}.html"
    snap_path = _snapshot_dir(ws_norm) / snap_name
    _safe_write_text(snap_path, html_in)

    ext = str(hit.get("ext") or "").lower()
    updated_rec = _update_index_h1(ws_norm, doc_id, ext=ext, html_in=html_in, text_in=text_in)

    return {
        "ok": True,
        "workspace_id": ws_norm,
        "doc_id": doc_id,
        "snapshot": snap_name,
        "h1": (updated_rec.get("h1") if isinstance(updated_rec, dict) else ""),
        "h1_source": (updated_rec.get("h1_source") if isinstance(updated_rec, dict) else ""),
        "h1_error": (updated_rec.get("h1_error") if isinstance(updated_rec, dict) else ""),
    }


@router.get("/get")
def get_file(workspace_id: str = Query("ws_betterhealthcheck_com"), doc_id: str = Query(...)):
    ws_norm = _ws(workspace_id)

    doc_id = (doc_id or "").strip()
    if not doc_id:
        raise HTTPException(status_code=400, detail="doc_id is required")

    items = _safe_read_index(_index_path(ws_norm))
    hit = next((x for x in items if x.get("doc_id") == doc_id), None)
    if not hit:
        raise HTTPException(status_code=404, detail="doc_id not found")

    path = _ws_dir(ws_norm) / (hit.get("stored_name") or "")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Stored file missing on disk")

    return FileResponse(
        str(path),
        filename=hit.get("filename") or "document",
        media_type=hit.get("content_type") or "application/octet-stream",
    )


@router.get("/preview")
def preview_file(workspace_id: str = Query("ws_betterhealthcheck_com"), doc_id: str = Query(...)):
    ws_norm = _ws(workspace_id)

    doc_id = (doc_id or "").strip()
    if not doc_id:
        raise HTTPException(status_code=400, detail="doc_id is required")

    items = _safe_read_index(_index_path(ws_norm))
    hit = next((x for x in items if x.get("doc_id") == doc_id), None)
    if not hit:
        raise HTTPException(status_code=404, detail="doc_id not found")

    path = _ws_dir(ws_norm) / (hit.get("stored_name") or "")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Stored file missing on disk")

    raw = path.read_bytes()
    ext = str(hit.get("ext") or _guess_ext(hit.get("filename") or "")).lower()
    preview = _extract_preview_from_bytes(hit.get("filename") or "document", ext, raw)

    return {
        "ok": True,
        "workspace_id": ws_norm,
        "doc_id": hit.get("doc_id"),
        "filename": hit.get("filename"),
        "ext": ext,
        "h1": (hit.get("h1") or ""),
        "h1_source": (hit.get("h1_source") or ""),
        "h1_error": (hit.get("h1_error") or ""),
        "text": preview.get("text"),
        "html": preview.get("html"),
        "is_html": bool(preview.get("is_html")),
        "truncated": bool(preview.get("truncated")),
    }


@legacy_router.post("/upload")
async def legacy_upload(workspace_id: str = Query("ws_betterhealthcheck_com"), file: UploadFile = File(...)):
    return await upload_file(workspace_id=workspace_id, file=file)