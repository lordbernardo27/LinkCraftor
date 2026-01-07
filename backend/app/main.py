# backend/app/main.py
from __future__ import annotations

import importlib
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

import os
from fastapi import Request
from fastapi.responses import JSONResponse


log = logging.getLogger("linkcraftor")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="LinkCraftor API", version="0.1.0")

# ----- Paths (robust regardless of where uvicorn is launched) -----
# main.py is at backend/app/main.py -> project root is parents[2]
BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_PUBLIC = BASE_DIR / "frontend" / "public"
INDEX_HTML = FRONTEND_PUBLIC / "index.html"
ASSETS_DIR = FRONTEND_PUBLIC / "assets"

# ✅ Owner Console static directory
OWNER_DIR = BASE_DIR / "backend" / "app" / "static" / "owner"

# ----- CORS (dev-wide; tighten for prod) -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _mount_router(module_path: str, attr: str, prefix: str, tag: str):
    try:
        mod = importlib.import_module(module_path)
        router = getattr(mod, attr)
        app.include_router(router, prefix=prefix, tags=[tag])
        log.info("Mounted %s at %s", module_path, prefix)
    except Exception as e:
        log.error("Failed to mount %s (%s): %s", module_path, attr, e, exc_info=True)

_mount_router("backend.app.routers.engine", "router", "/engine", "engine")
_mount_router("backend.app.routers.files", "router", "/files", "files")
_mount_router("backend.app.routers.references", "router", "/references", "references")
_mount_router("backend.app.routers.convert", "router", "/api/convert", "convert")
_mount_router("backend.app.routers.sitemap", "router", "/sitemap", "sitemap")
_mount_router("backend.app.routers.external", "router", "/api/external", "external")

# ----- Static + Frontend -----
# Serve /assets/* exactly from frontend/public/assets (matches your HTML paths)
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR), html=False), name="assets")

# ✅ Serve Owner Console at /owner/*
# This expects: backend/app/static/owner/index.html
if OWNER_DIR.exists():
    app.mount("/owner", StaticFiles(directory=str(OWNER_DIR), html=True), name="owner")
    log.info("Mounted Owner Console at /owner from %s", OWNER_DIR)
else:
    log.warning("Owner Console folder not found at: %s", OWNER_DIR)


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
        # If not set, fail CLOSED (more secure)
        return False
    return request.cookies.get(OWNER_COOKIE) == owner_key

@app.middleware("http")
async def owner_protect_middleware(request: Request, call_next):
    path = request.url.path

    # ✅ Protect ONLY the owner-only API routes.
    # Allow /owner static UI to load so JS can prompt + login.
    needs_owner = (
    path.startswith("/api/external/manual")
    or path.startswith("/api/external/owner/")
)




    if needs_owner and not _authorized(request):
        return JSONResponse({"ok": False, "error": "owner_auth_required"}, status_code=401)

    return await call_next(request)


@app.post("/owner-api/login")
async def owner_login(payload: dict):


    """
    POST { "key": "..." } -> sets HttpOnly cookie if correct.
    """
    key = str(payload.get("key") or "").strip()
    owner_key = _get_owner_key()
    if not owner_key:
        return JSONResponse({"ok": False, "error": "owner_key_not_configured"}, status_code=500)

    if key != owner_key:
        return JSONResponse({"ok": False, "error": "invalid_key"}, status_code=401)

    resp = JSONResponse({"ok": True})
    # HttpOnly so JS can't read it; browser will send it automatically on requests
    resp.set_cookie(
        key=OWNER_COOKIE,
        value=owner_key,
        httponly=True,
        secure=False,   # set True in production (HTTPS)
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
    return {"status": "ok"}

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
