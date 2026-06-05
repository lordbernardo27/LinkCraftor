# DEPRECATED_REMOVED: HELIX_AUTH legacy route removed
# Reason: frontend does not call /api/helix_auth/run; new Helix will use resolver-based architecture

# âœ… Engine under /api/engine (frontend expects /api/engine/*)
_mount_router("backend.app.routers.engine", "router", "/api/engine", "engine")

_mount_router("backend.app.routers.files", "router", "/files", "files")
# DEPRECATED_REMOVED: references router deleted from legacy backend/app/routers
# Reason: future Helix uses resolver-based references, not /references/search
# MIGRATED_TO_BACKEND_SERVER_MAIN: convert router deleted from legacy backend/app/routers
# backend/server/main.py owns POST /api/convert/docx and POST /api/export/docx
# DEPRECATED_REMOVED: sitemap router deleted from legacy backend/app/routers
# Reason: site_reader owns sitemap expansion; frontend does not call /sitemap/scan
_mount_router("backend.app.routers.external", "router", "/api/external", "external")

# âœ… RB2 runner endpoint (Node-based)
# Exposes: POST /api/engine/rb2/run
_mount_router("backend.app.routers.rb2_run", "router", "/api/engine/rb2", "rb2")

# ----- Static + Frontend -----
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR), html=False), name="assets")
    log.info("Mounted /assets from %s", ASSETS_DIR)
else:
    log.warning("Assets folder not found: %s", ASSETS_DIR)

# âœ… Serve Owner Console at /owner/*
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




