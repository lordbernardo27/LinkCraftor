# backend/server/main.py
# -------------------------------
# Minimal FastAPI backend exposing:
#  - GET  /health + /api/health
#  - POST /api/convert/docx
#  - POST /api/export/docx
#  - GET  /api/external/resolve
#  - POST /api/external/log
#  - FRONTEND served at /
#  - Static assets at /assets/*
#  - Static UI pages at /static/*
#
# Uses python-mammoth to convert .docx -> HTML.

import os
import json
import io
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import mammoth

# ✅ Create app ONCE (MUST be before include_router)
app = FastAPI()

# ✅ Base dir for backend/server
BASE_DIR = Path(__file__).resolve().parent

# ✅ Serve backend static UI files safely (avoid crash if folder missing)
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# -----------------------
# CORS (loose for local dev)
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Frontend serving (single URL)
# =========================
FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public")
)
ASSETS_DIR = os.path.join(FRONTEND_DIR, "assets")

# Mount /assets only if folder exists (prevents crash)
if os.path.isdir(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

@app.get("/")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.isfile(index_path):
        raise HTTPException(status_code=404, detail=f"Missing frontend file: {index_path}")
    return FileResponse(index_path)

# ✅ Favicon: avoid 404 spam (return 204 if no icon exists)
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    icon_path = STATIC_DIR / "favicon.ico"
    if icon_path.is_file():
        return FileResponse(str(icon_path))
    return Response(status_code=204)

# =========================
# Router imports + includes (AFTER app exists)
# =========================

# ✅ Use relative imports (recommended inside the backend.server package)
from .routes.imported_urls import router as imported_urls_router
from .routes.draft_topics import router as draft_router
from .routes.planning import router as planning_router
from .routes.engine_scoring import router as engine_scoring_router

# ✅ Decision Intelligence Layer 1 router
from backend.server.routes.engine_decisions import router as engine_decisions_router

app.include_router(imported_urls_router)
app.include_router(draft_router)
app.include_router(planning_router)
app.include_router(engine_scoring_router)
app.include_router(engine_decisions_router)

# =========================
# Helpers
# =========================

def _data_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "data")

def _path_manual() -> str:
    return os.path.join(_data_dir(), "global_external_manual.json")

def _path_auto() -> str:
    return os.path.join(_data_dir(), "global_external_auto.json")

def _path_blacklist() -> str:
    return os.path.join(_data_dir(), "blacklist_urls.json")

def _safe_read_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception:
        return None

def _safe_read_json_list(path: str) -> List[Dict[str, Any]]:
    raw = _safe_read_json(path)
    return [x for x in raw if isinstance(x, dict)] if isinstance(raw, list) else []

def _safe_read_blacklist() -> List[str]:
    raw = _safe_read_json(_path_blacklist())
    if isinstance(raw, list):
        return [str(x).strip().lower() for x in raw if str(x).strip()]
    return []

def _atomic_write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def _norm(s: str) -> str:
    return " ".join((s or "").strip().lower().split())

def _url_is_blacklisted(url: str, blacklist: List[str]) -> bool:
    u = (url or "").strip().lower()
    if not u:
        return True
    for b in blacklist:
        if b and b in u:
            return True
    return False

# -----------------------
# Health check (aliases)
# -----------------------
@app.get("/health")
@app.get("/api/health")
def health():
    return {"ok": True}

# -----------------------
# Debug: list routes
# -----------------------
@app.get("/__routes")
def routes():
    out = []
    for r in app.router.routes:
        methods = sorted(list(getattr(r, "methods", []) or []))
        path = getattr(r, "path", None)
        if path:
            out.append({"path": path, "methods": methods})
    return {"routes": out}

# -----------------------
# DOCX → HTML converter
# -----------------------
@app.post("/api/convert/docx")
async def convert_docx(file: UploadFile = File(...)):
    if file is None or not (file.filename or "").lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Please upload a .docx file.")

    try:
        data = await file.read()

        with io.BytesIO(data) as buff:
            result = mammoth.convert_to_html(buff)
            html = result.value or ""

        try:
            with io.BytesIO(data) as buff2:
                raw = mammoth.extract_raw_text(buff2)
                text = raw.value or ""
        except Exception:
            text = ""

        return {"filename": file.filename, "ext": ".docx", "html": html, "text": text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX conversion error: {e}")

# ================================
# Export simple HTML → .docx
# ================================
@app.post("/api/export/docx")
async def export_docx(payload: dict = Body(...)):
    html = (payload or {}).get("html", "")
    filename = (payload or {}).get("filename", "export.docx")

    if not html or not str(html).strip():
        raise HTTPException(status_code=400, detail="html is required")

    try:
        from io import BytesIO
        from bs4 import BeautifulSoup
        from docx import Document
    except Exception as ie:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Export dependencies missing: {ie}. "
                "Install with: pip install python-docx bs4"
            ),
        )

    soup = BeautifulSoup(html, "html.parser")
    root = soup.body or soup
    doc = Document()

    def add_text_block(text: str):
        t = (text or "").strip()
        if t:
            doc.add_paragraph(t)

    for el in getattr(root, "children", []):
        if getattr(el, "name", None) is None:
            add_text_block(str(el))
            continue

        name = (el.name or "").lower()
        text = el.get_text(" ", strip=True)

        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = min(int(name[1]), 9)
            doc.add_heading(text, level=level)
        elif name == "p":
            doc.add_paragraph(text)
        elif name in ("ul", "ol"):
            bullet = (name == "ul")
            for li in el.find_all("li", recursive=False):
                p = doc.add_paragraph(li.get_text(" ", strip=True))
                p.style = "List Bullet" if bullet else "List Number"
        elif name == "br":
            doc.add_paragraph("")
        else:
            if text:
                doc.add_paragraph(text)

    if not filename.lower().endswith(".docx"):
        filename += ".docx"

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

# ==========================================
# External resolver (manual wins, then auto)
# ==========================================

class ExternalCandidate(BaseModel):
    phrase: str
    url: str
    title: Optional[str] = None
    score: float = 1.0
    source: str = "backend"

def _find_matches(phrase_clean: str, lang: str, rows: List[Dict[str, Any]]) -> List[ExternalCandidate]:
    q = _norm(phrase_clean)
    out: List[ExternalCandidate] = []

    for item in rows:
        p = str(item.get("phrase") or item.get("key") or "").strip()
        u = str(item.get("url") or "").strip()
        if not p or not u:
            continue

        item_lang = str(item.get("lang") or "en").strip().lower()
        if lang and item_lang != str(lang).strip().lower():
            continue

        pk = _norm(p)
        if pk in q or q in pk:
            out.append(
                ExternalCandidate(
                    phrase=phrase_clean,
                    url=u,
                    title=item.get("title") or phrase_clean,
                    score=float(item.get("score", 1.0) or 1.0),
                    source=str(item.get("source") or "dataset"),
                )
            )

    out.sort(key=lambda x: x.score, reverse=True)
    return out

@app.get("/api/external/resolve", response_model=List[ExternalCandidate])
async def external_resolve(phrase: str, lang: str = "en"):
    phrase_clean = (phrase or "").strip()
    if not phrase_clean:
        return []

    blacklist = _safe_read_blacklist()

    manual_rows = _safe_read_json_list(_path_manual())
    manual_matches = [m for m in _find_matches(phrase_clean, lang, manual_rows)
                      if not _url_is_blacklisted(m.url, blacklist)]
    if manual_matches:
        return manual_matches[:8]

    auto_rows = _safe_read_json_list(_path_auto())
    auto_matches = [m for m in _find_matches(phrase_clean, lang, auto_rows)
                    if not _url_is_blacklisted(m.url, blacklist)]
    return auto_matches[:8]

# ==========================================
# External logger (writes ONLY to auto)
# ==========================================

class ExternalLogEvent(BaseModel):
    event: str = "auto_apply"
    phrase: str
    url: str
    title: Optional[str] = None
    providerId: Optional[str] = None
    providerLabel: Optional[str] = None
    docCode: Optional[str] = None
    docTitle: Optional[str] = None
    lang: str = "en"
    source: str = "auto_link"

@app.post("/api/external/log")
async def external_log(payload: ExternalLogEvent = Body(...)):
    url = (payload.url or "").strip()
    phrase = (payload.phrase or "").strip()
    if not url or not phrase:
        return {"ok": False, "error": "Missing url or phrase"}

    blacklist = _safe_read_blacklist()
    if _url_is_blacklisted(url, blacklist):
        return {"ok": False, "error": "URL is blacklisted", "url": url}

    path = _path_auto()
    dataset = _safe_read_json_list(path)
    now = datetime.utcnow().isoformat() + "Z"

    idx = None
    for i, item in enumerate(dataset):
        if isinstance(item, dict) and str(item.get("url", "")).strip() == url:
            idx = i
            break

    if idx is None:
        entry = {
            "phrase": phrase,
            "key": _norm(phrase),
            "url": url,
            "title": payload.title or phrase,
            "score": 1.0,
            "source": payload.source or "auto_log",
            "seen_count": 1,
            "first_seen": now,
            "last_seen": now,
            "phrases": [phrase],
            "providerId": payload.providerId,
            "providerLabel": payload.providerLabel,
            "lang": payload.lang,
            "last_event": payload.event,
            "docCode": payload.docCode,
            "docTitle": payload.docTitle,
        }
        dataset.append(entry)
        _atomic_write_json(path, dataset)
        return {"ok": True, "action": "added", "path": path}

    existing = dataset[idx] if isinstance(dataset[idx], dict) else {}
    existing["url"] = url
    existing["phrase"] = existing.get("phrase") or phrase
    existing["key"] = existing.get("key") or _norm(phrase)
    existing["title"] = payload.title or existing.get("title") or phrase
    existing["source"] = existing.get("source") or (payload.source or "auto_log")

    existing["seen_count"] = int(existing.get("seen_count", 0) or 0) + 1
    existing["last_seen"] = now
    existing["first_seen"] = existing.get("first_seen") or now

    phrases = existing.get("phrases")
    if not isinstance(phrases, list):
        phrases = []
    if phrase not in phrases:
        phrases.append(phrase)
    existing["phrases"] = phrases[-50:]

    existing["providerId"] = payload.providerId or existing.get("providerId")
    existing["providerLabel"] = payload.providerLabel or existing.get("providerLabel")
    existing["lang"] = payload.lang or existing.get("lang")
    existing["last_event"] = payload.event
    existing["docCode"] = payload.docCode or existing.get("docCode")
    existing["docTitle"] = payload.docTitle or existing.get("docTitle")

    dataset[idx] = existing
    _atomic_write_json(path, dataset)

    return {"ok": True, "action": "updated", "seen_count": existing["seen_count"], "path": path}
