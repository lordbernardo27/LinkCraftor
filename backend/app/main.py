# backend/app/main.py
from __future__ import annotations

import importlib
import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

# Routers (direct imports where you want certainty)
from backend.app.routers.site_reader import router as site_reader_router
from backend.app.routers.helix_auth_run import router as helix_auth_router

log = logging.getLogger("linkcraftor")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="LinkCraftor API", version="0.1.0")

# ==========================================================
# ✅ FORCE UTF-8 + DISABLE CACHE (DEV) to kill mojibake/stale assets
# ==========================================================
class ForceUtf8AndNoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        resp = await call_next(request)

        path = request.url.path or ""
        ct = (resp.headers.get("content-type", "") or "").lower()

        is_text_like = (
            ct.startswith("text/")
            or "javascript" in ct
            or ct.startswith("application/json")
        )

        # 1) Ensure charset=utf-8 for text-like responses
        if is_text_like and "charset=" not in ct:
            orig = resp.headers.get("content-type", "")
            resp.headers["content-type"] = (orig + "; charset=utf-8") if orig else "text/plain; charset=utf-8"

        # 2) DEV: prevent browser caching stale HTML/JS/CSS
        if path == "/" or path.startswith("/assets/") or path.startswith("/owner/"):
            resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            resp.headers["Pragma"] = "no-cache"
            resp.headers["Expires"] = "0"

        return resp

app.add_middleware(ForceUtf8AndNoCacheMiddleware)

# ----- CORS (dev-wide; tighten for prod) -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Paths (robust regardless of where uvicorn is launched) -----
# main.py is at backend/app/main.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]

FRONTEND_PUBLIC = PROJECT_ROOT / "frontend" / "public"
INDEX_HTML = FRONTEND_PUBLIC / "index.html"
ASSETS_DIR = FRONTEND_PUBLIC / "assets"

# ✅ Owner Console (LOCKED canonical path)
OWNER_DIR = PROJECT_ROOT / "backend" / "app" / "static" / "owner"

def _mount_router(module_path: str, attr: str, prefix: str, tag: str):
    try:
        mod = importlib.import_module(module_path)
        router = getattr(mod, attr)
        app.include_router(router, prefix=prefix, tags=[tag])
        log.info("Mounted %s at %s", module_path, prefix)
    except Exception as e:
        log.error("Failed to mount %s (%s): %s", module_path, attr, e, exc_info=True)

# ==========================================================
# ✅ Core routers
# ==========================================================
# Site reader (router likely already has prefix="/api/site" inside it; keep as-is)
app.include_router(site_reader_router)

# ✅ HELIX_AUTH: mounted at /api/helix_auth/*
app.include_router(helix_auth_router, prefix="/api/helix_auth", tags=["helix_auth"])
log.info("Mounted helix_auth at /api/helix_auth")

# ✅ Engine under /api/engine (frontend expects /api/engine/*)
_mount_router("backend.app.routers.engine", "router", "/api/engine", "engine")

_mount_router("backend.app.routers.files", "router", "/files", "files")
_mount_router("backend.app.routers.references", "router", "/references", "references")
_mount_router("backend.app.routers.convert", "router", "/api/convert", "convert")
_mount_router("backend.app.routers.sitemap", "router", "/sitemap", "sitemap")
_mount_router("backend.app.routers.external", "router", "/api/external", "external")

# ✅ RB2 runner endpoint (Node-based)
# Exposes: POST /api/engine/rb2/run
_mount_router("backend.app.routers.rb2_run", "router", "/api/engine/rb2", "rb2")

# ----- Static + Frontend -----
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR), html=False), name="assets")
    log.info("Mounted /assets from %s", ASSETS_DIR)
else:
    log.warning("Assets folder not found: %s", ASSETS_DIR)

# ✅ Serve Owner Console at /owner/*
if OWNER_DIR.exists():
    app.mount("/owner", StaticFiles(directory=str(OWNER_DIR), html=True), name="owner")
    log.info("Mounted Owner Console at /owner from %s", OWNER_DIR)
else:
    log.warning("Owner Console folder not found at: %s", OWNER_DIR)

@app.get("/owner")
def owner_root():
    return RedirectResponse(url="/owner/")

# ============================
# Owner Console Security (Cookie-based)
# ============================
OWNER_KEY_ENV = "LINKCRAFTOR_OWNER_KEY"
OWNER_COOKIE = "lc_owner"

def _get_owner_key() -> str:
    return (os.getenv(OWNER_KEY_ENV) or "").strip()

def _authorized(request: Request) -> bool:
    owner_key = _get_owner_key()
    if not owner_key:
        return False  # fail closed
    return request.cookies.get(OWNER_COOKIE) == owner_key

@app.middleware("http")
async def owner_protect_middleware(request: Request, call_next):
    path = request.url.path

    needs_owner = (
        path.startswith("/api/external/manual")
        or path.startswith("/api/external/owner/")
    )

    if needs_owner and not _authorized(request):
        return JSONResponse({"ok": False, "error": "owner_auth_required"}, status_code=401)

    return await call_next(request)

@app.post("/owner-api/login")
async def owner_login(payload: dict):
    key = str(payload.get("key") or "").strip()
    owner_key = _get_owner_key()
    if not owner_key:
        return JSONResponse({"ok": False, "error": "owner_key_not_configured"}, status_code=500)

    if key != owner_key:
        return JSONResponse({"ok": False, "error": "invalid_key"}, status_code=401)

    resp = JSONResponse({"ok": True})
    resp.set_cookie(
        key=OWNER_COOKIE,
        value=owner_key,
        httponly=True,
        secure=False,   # True in production (HTTPS)
        samesite="lax",
        path="/",
    )
    return resp

@app.post("/owner-api/logout")
async def owner_logout():
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(key=OWNER_COOKIE, path="/")
    return resp

# ----- Diagnostics -----
@app.get("/health")
def health():
    return {"ok": True}

@app.get("/__routes")
def list_routes():
    items = []
    for r in app.routes:
        methods = sorted(getattr(r, "methods", []) or [])
        path = getattr(r, "path", None) or getattr(r, "path_format", "")
        if path:
            items.append({"path": path, "methods": methods})
    items.sort(key=lambda x: x["path"])
    return {"routes": items}

# Serve index.html at /
@app.get("/", response_class=HTMLResponse)
def serve_index():
    if INDEX_HTML.exists():
        return FileResponse(str(INDEX_HTML))
    return HTMLResponse(
        f"<h1>Frontend not found</h1><p>Expected at: {INDEX_HTML}</p>",
        status_code=404,
    )