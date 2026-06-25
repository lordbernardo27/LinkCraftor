from __future__ import annotations

import importlib
import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from backend.server.routes.external.resolver import router as resolver_runtime_router

log = logging.getLogger("linkcraftor")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="LinkCraftor Legacy App", version="legacy-compat")

ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT / "frontend" / "public"
INDEX_HTML = FRONTEND_DIR / "index.html"
ASSETS_DIR = FRONTEND_DIR / "assets"
OWNER_DIR = ROOT / "backend" / "server" / "owner"


def _mount_router(module_path: str, attr: str, prefix: str, tag: str):
    try:
        mod = importlib.import_module(module_path)
        router = getattr(mod, attr)
        app.include_router(router, prefix=prefix, tags=[tag])
        app.include_router(resolver_runtime_router, prefix="/api/external/resolver_runtime")
        log.info("Mounted %s at %s", module_path, prefix)
    except Exception as e:
        log.error("Failed to mount %s (%s): %s", module_path, attr, e, exc_info=True)


# Remaining legacy routers only
# DEPRECATED_REMOVED: legacy engine router removed; backend/server/routes owns /api/engine/*
# DEPRECATED_REMOVED: legacy files router removed; backend/server/routes/files.py owns /api/files/*
# RETIRED_EXTERNAL_ROUTER_PHASE_1_37: legacy external router retired; backend.server.routes.external owns external routes.
# MIGRATED_TO_BACKEND_SERVER_MAIN: rb2_run router moved to backend/server/routes/rb2_run.py


if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR), html=False), name="assets")

if OWNER_DIR.exists():
    app.mount("/owner", StaticFiles(directory=str(OWNER_DIR), html=True), name="owner")


@app.get("/owner")
def owner_root():
    return RedirectResponse(url="/owner/")


OWNER_KEY_ENV = "LINKCRAFTOR_OWNER_KEY"
OWNER_COOKIE = "lc_owner"


def _get_owner_key() -> str:
    return (os.getenv(OWNER_KEY_ENV) or "").strip()


def _authorized(request: Request) -> bool:
    owner_key = _get_owner_key()
    if not owner_key:
        return False
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
        secure=False,
        samesite="lax",
        path="/",
    )
    return resp


@app.post("/owner-api/logout")
async def owner_logout():
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(key=OWNER_COOKIE, path="/")
    return resp


@app.get("/health")
def health():
    return {"ok": True, "app": "legacy"}


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


@app.get("/", response_class=HTMLResponse)
def serve_index():
    if INDEX_HTML.exists():
        return FileResponse(str(INDEX_HTML))
    return HTMLResponse(
        f"<h1>Frontend not found</h1><p>Expected at: {INDEX_HTML}</p>",
        status_code=404,
    )



