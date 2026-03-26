# backend/app/routers/rb2_run.py
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request

from backend.server.engine.rb2_adapter import build_rb2_phrase_contexts

router = APIRouter(tags=["rb2"])


import json
from pathlib import Path
from typing import Any, Dict, Optional
from fastapi import APIRouter, Query

# If you already have router defined above, DO NOT redefine it.
# This code assumes `router` already exists in this file.


DATA_DIR = Path(__file__).resolve().parents[2] / "server" / "data"   # backend/server/data


def _safe_load_json(p: Path) -> Any:
    try:
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _count(obj: Any) -> int:
    if obj is None:
        return 0
    if isinstance(obj, list):
        return len(obj)
    if isinstance(obj, dict):
        # common containers (include phrases!)
        for k in ("items", "urls", "pages", "phrases"):
            v = obj.get(k)
            if isinstance(v, list):
                return len(v)
            if isinstance(v, dict):
                return len(v)
        return len(obj)
    return 0



def _pool(name: str, data_path: Path, meta_path: Optional[Path] = None) -> Dict[str, Any]:
    data = _safe_load_json(data_path)
    meta = _safe_load_json(meta_path) if meta_path else None
    last = ""
    if isinstance(meta, dict):
        last = meta.get("last_updated_at_utc") or meta.get("last_import_at_utc") or ""
    return {
        "pool": name,
        "count": _count(data),
        "exists": data_path.exists(),
        "data_path": str(data_path),
        "meta_path": str(meta_path) if meta_path else "",
        "last_updated_at_utc": last,
    }


@router.get("/preflight")
def rb2_preflight(workspace_id: str = Query(..., description="Workspace scope, e.g. ws_prettiereveryday_com")):
    ws = (workspace_id or "").strip()
    if not ws:
        return {"ok": False, "error": "missing_workspace_id"}

    # --- Pool file conventions (these match what we’ve been using) ---
    # Live-domain (site reader)
    site_sources = DATA_DIR / f"site_sources_{ws}.json"
    site_pages = DATA_DIR / f"site_pages_{ws}.json"
    site_phrase_index = DATA_DIR / f"site_phrase_index_{ws}.json"

    # Imported URL pool
    imported_urls = DATA_DIR / f"imported_urls_{ws}.json"
    imported_urls_meta = DATA_DIR / f"imported_urls_{ws}.meta.json"

    # Upload pool (if/when you use it)
    upload_pool = DATA_DIR / f"upload_pool_{ws}.json"
    upload_pool_meta = DATA_DIR / f"upload_pool_{ws}.meta.json"

    # Draft pool (if/when you use it)
    draft_pool = DATA_DIR / f"draft_pool_{ws}.json"
    draft_pool_meta = DATA_DIR / f"draft_pool_{ws}.meta.json"

    # If you also have any workspace-specific upload phrase index files:
    upload_phrase_index = DATA_DIR / f"upload_phrase_index_{ws}.json"
    upload_phrase_index_ws = DATA_DIR / f"upload_phrase_index_ws_{ws}.json"  # kept for compatibility

    pools = [
        _pool("live_domain_sources", site_sources),
        _pool("live_domain_pages", site_pages),
        _pool("live_domain_phrase_index", site_phrase_index),
        _pool("imported_url_pool", imported_urls, imported_urls_meta),
        _pool("upload_pool", upload_pool, upload_pool_meta),
        _pool("draft_pool", draft_pool, draft_pool_meta),
        _pool("upload_phrase_index", upload_phrase_index),
        _pool("upload_phrase_index_ws", upload_phrase_index_ws),
    ]

    total = sum(int(p.get("count", 0) or 0) for p in pools)
    any_exists = any(bool(p.get("exists")) for p in pools)

    # Hard guard: if workspace has no pool files at all, don’t let RB2 “run empty”
    if not any_exists:
        return {"ok": False, "workspace_id": ws, "error": "workspace_not_initialized", "pools": pools}

    return {"ok": True, "workspace_id": ws, "total_items_across_pools": total, "pools": pools}



# ------------------------------------------------------------
# Path anchors (avoid cwd issues)
# rb2_run.py is: backend/app/routers/rb2_run.py
# parents[0]=routers, [1]=app, [2]=backend, [3]=project root
# ------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "backend" / "server" / "data"
UPLOADS_DIR = PROJECT_ROOT / "backend" / "server" / "uploads"
RB2_RUNNER = PROJECT_ROOT / "backend" / "server" / "engine_js" / "rb2" / "run_rb2.mjs"

WORD_RE = re.compile(r"[a-z0-9]{3,}")


def _node_exe() -> str:
    return os.environ.get("NODE_EXE", "node")


WS_RE = re.compile(r"^[a-z0-9_]{3,80}$", re.IGNORECASE)

def _ws_safe(ws: str) -> str:
    ws = str(ws or "").strip()
    if not ws:
        raise HTTPException(status_code=400, detail={"ok": False, "error": "missing_workspace_id"})
    if not ws.startswith("ws_"):
        raise HTTPException(status_code=400, detail={"ok": False, "error": "workspace_id_must_start_with_ws_"})
    if not WS_RE.match(ws):
        raise HTTPException(status_code=400, detail={"ok": False, "error": "invalid_workspace_id_chars"})
    return ws


def _safe_read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _tokenize(s: str) -> List[str]:
    if not s:
        return []
    return WORD_RE.findall(str(s).lower())


def _title_from_url(u: str) -> str:
    """
    Convert slug -> readable title tokens.
    /pregnancy-due-date-calculator -> "pregnancy due date calculator"
    """
    try:
        u = str(u or "").strip()
        if not u:
            return ""
        u = u.split("#")[0].split("?")[0].rstrip("/")
        slug = u.split("/")[-1] if "/" in u else u
        slug = slug.replace("-", " ").replace("_", " ").strip()
        return " ".join(slug.split())
    except Exception:
        return ""


def _load_site_phrase_index(workspace_id: str) -> List[Dict[str, Any]]:
    """
    Loads Site Reader phrase index items for this workspace.
    File: backend/server/data/site_phrase_index_<ws>.json

    Supports shapes:
      A) {"items":[...]}
      B) [ ... ]
      C) {"phrases": { "<norm>": {item}, ... }}
    """
    ws = _ws_safe(workspace_id)
    fp = DATA_DIR / f"site_phrase_index_{ws}.json"
    if not fp.exists():
        return []

    try:
        data = json.loads(fp.read_text(encoding="utf-8"))

        # A) {"items":[...]}
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return [x for x in data["items"] if isinstance(x, dict)]

        # C) {"phrases": {k: item, ...}}
        if isinstance(data, dict) and isinstance(data.get("phrases"), dict):
            out: List[Dict[str, Any]] = []
            for _, v in data["phrases"].items():
                if isinstance(v, dict):
                    out.append(v)
            return out

        # B) [ ... ]
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]

        return []
    except Exception:
        return []


def _load_site_pages(workspace_id: str) -> List[Dict[str, Any]]:
    """
    Loads live-domain pages for this workspace.
    File: backend/server/data/site_pages_<ws>.json

    Supports shapes:
      A) {"pages": { "<url>": {...page...}, ... }}
      B) {"pages": [ ... ]}
      C) [ ... ]
    Returns list of page dicts (each should contain url/h1 if available).
    """
    ws = _ws_safe(workspace_id)
    fp = DATA_DIR / f"site_pages_{ws}.json"
    if not fp.exists():
        return []

    try:
        data = json.loads(fp.read_text(encoding="utf-8"))

        # A) {"pages": { "<url>": {...page...}, ... }}
        if isinstance(data, dict) and isinstance(data.get("pages"), dict):
            out: List[Dict[str, Any]] = []
            for url, page in data["pages"].items():
                if isinstance(page, dict):
                    p = dict(page)
                    p.setdefault("url", url)
                    out.append(p)
            return out

        # B) {"pages": [ ... ]}
        if isinstance(data, dict) and isinstance(data.get("pages"), list):
            return [p for p in data["pages"] if isinstance(p, dict)]

        # C) [ ... ]
        if isinstance(data, list):
            return [p for p in data if isinstance(p, dict)]

        return []
    except Exception:
        return []


def _build_candidate_pool(workspace_id: str, limit: int = 50000) -> List[Dict[str, Any]]:
    """
    Builds RB2 candidate TARGETS as PAGES from:
      - imported_urls_<ws>.json         (page URLs)
      - draft_topics_<ws>.json          (planned page URLs)
      - uploads/index_<ws>.json         (other docs as pages/topics)
      - site_pages_<ws>.json            (live-domain pages: URL + H1)
    And then attaches phrase_index_<ws>.json as ALIASES/SIGNALS to the correct page by source_url.

    IMPORTANT:
      - Targets are PAGES.
      - Phrase index is NOT added as standalone targets.
    """
    ws = _ws_safe(workspace_id)

    imported_path = DATA_DIR / f"imported_urls_{ws}.json"
    draft_path = DATA_DIR / f"draft_topics_{ws}.json"
    uploads_index_path = UPLOADS_DIR / f"index_{ws}.json"

    candidates: List[Dict[str, Any]] = []
    seen_keys = set()  # (url, title_lower)
    seen_ids = set()

    def _key(url: str, title: str) -> tuple:
        return (str(url or "").strip(), str(title or "").strip().lower())

    def _add_page_candidate(
        *,
        cid: str,
        url: str,
        title: str,
        origin: str,
        aliases: Optional[List[str]] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        nonlocal candidates
        url = str(url or "").strip()
        title = str(title or "").strip()
        if not url and not title:
            return

        # Prefer url for dedupe; if url missing, dedupe by title only
        k = _key(url, title)
        if k in seen_keys:
            return
        seen_keys.add(k)

        if cid in seen_ids:
            return
        seen_ids.add(cid)

        candidates.append(
            {
                "id": cid,
                "title": title or url,
                "url": url,
                "aliases": aliases or [],
                "origin": origin,
                "slugTokens": _tokenize(title) + _tokenize(_title_from_url(url)),
                "_lc_meta": meta or {},
            }
        )

    # 1) Imported URLs -> PAGE targets
    raw_urls = _safe_read_json(imported_path)
    if isinstance(raw_urls, list):
        for u in raw_urls[:limit]:
            url = str(u or "").strip()
            if not url:
                continue
            title = _title_from_url(url) or url
            _add_page_candidate(
                cid=f"u:{url}",
                url=url,
                title=title,
                origin="imported",
            )

    # 2) Draft topics -> PAGE targets (planned_url)
    raw_drafts = _safe_read_json(draft_path)
    if isinstance(raw_drafts, list):
        for r in raw_drafts[:limit]:
            if not isinstance(r, dict):
                continue
            topic_id = str(r.get("topic_id") or r.get("id") or "").strip()
            title = str(r.get("working_title") or r.get("title") or "").strip()
            planned_url = str(r.get("planned_url") or "").strip()
            aliases = r.get("aliases") if isinstance(r.get("aliases"), list) else []

            if not title and not planned_url:
                continue

            _add_page_candidate(
                cid=f"d:{topic_id or title or planned_url}",
                url=planned_url,
                title=title or _title_from_url(planned_url) or planned_url,
                origin="draft",
                aliases=[str(a).strip() for a in aliases if str(a).strip()],
                meta={"topic_id": topic_id},
            )

    # 3) Upload index -> PAGE-ish targets
    raw_index = _safe_read_json(uploads_index_path)
    if isinstance(raw_index, list):
        for it in raw_index[:limit]:
            if not isinstance(it, dict):
                continue
            doc_id = str(it.get("doc_id") or it.get("docId") or "").strip()
            title = str(it.get("title") or it.get("h1") or it.get("filename") or "").strip()
            url = str(it.get("url") or "").strip()
            if not doc_id or not title:
                continue

            _add_page_candidate(
                cid=f"doc:{doc_id}",
                url=url,
                title=title,
                origin="other-doc",
            )

    # 4) Live-domain pages (site_pages) -> PAGE targets (this is what you wanted)
    live_pages = _load_site_pages(workspace_id)
    if isinstance(live_pages, list) and live_pages:
        for p in live_pages[:limit]:
            url = str(p.get("url") or "").strip()
            if not url:
                continue
            h1 = str(p.get("h1") or p.get("title") or "").strip()
            title = h1 or _title_from_url(url) or url

            _add_page_candidate(
                cid=f"live:{url}",
                url=url,
                title=title,
                origin="live_page",
                meta={"h1": h1},
            )

    # Build URL -> candidate reference for alias attachment
    by_url: Dict[str, Dict[str, Any]] = {}
    for c in candidates:
        u = str(c.get("url") or "").strip()
        if u:
            by_url[u] = c

    # 5) Attach phrase signals as aliases to their SOURCE page target (by source_url)
    site_items = _load_site_phrase_index(workspace_id)
    if isinstance(site_items, list) and site_items:
        for it in site_items:
            if not isinstance(it, dict):
                continue

            src_url = str(it.get("source_url") or "").strip()
            phrase = str(it.get("phrase") or "").strip()
            bucket = str(it.get("bucket") or "").strip()
            ptype = str(it.get("type") or "").strip()

            if not src_url or not phrase:
                continue

            tgt = by_url.get(src_url)
            if not tgt:
                # If the page target isn't present yet (e.g., you imported URLs but didn't ingest pages),
                # we can create a minimal page target so signals have somewhere to attach.
                # This keeps "page targets unlimited" even before full ingestion.
                _add_page_candidate(
                    cid=f"live_fallback:{src_url}",
                    url=src_url,
                    title=_title_from_url(src_url) or src_url,
                    origin="live_page_fallback",
                    meta={"h1": it.get("source_h1")},
                )
                tgt = by_url.get(src_url)
                if not tgt:
                    continue

            # add phrase as alias (dedupe)
            aliases = tgt.get("aliases") if isinstance(tgt.get("aliases"), list) else []
            if phrase not in aliases:
                aliases.append(phrase)
                tgt["aliases"] = aliases

            # Keep bucket/type counts in meta (doesn't break Node if ignored)
            meta = tgt.get("_lc_meta") if isinstance(tgt.get("_lc_meta"), dict) else {}
            meta.setdefault("alias_counts", {"internal_strong": 0, "semantic_optional": 0})
            if bucket in meta["alias_counts"]:
                meta["alias_counts"][bucket] += 1
            meta.setdefault("alias_types", {})
            if ptype:
                meta["alias_types"][ptype] = int(meta["alias_types"].get(ptype, 0)) + 1
            tgt["_lc_meta"] = meta

    if len(candidates) > limit:
        candidates = candidates[:limit]

    return candidates


@router.post("/run")
async def rb2_run(request: Request) -> Dict[str, Any]:
    if not RB2_RUNNER.exists():
        raise HTTPException(status_code=500, detail=f"RB2 runner missing: {RB2_RUNNER}")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON request body.")

    workspace_id = str(payload.get("workspace_id") or payload.get("workspaceId") or "default").strip()
    ws = _ws_safe(workspace_id)

    # ✅ Attach rb2.extract.v1 contract
    try:
        doc_id = str(payload.get("docId") or payload.get("doc_id") or payload.get("id") or "doc_unknown")
        doc_html = payload.get("html")
        doc_text = payload.get("text")
        rb2_doc = build_rb2_phrase_contexts(doc_id, html=doc_html, text=doc_text)
        payload["rb2Doc"] = rb2_doc
        payload.setdefault("_rb2_extract_version", rb2_doc.get("version"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RB2 extraction failed: {e}")

    # ✅ Build + inject candidate pool (PAGE targets + phrase aliases)
    try:
        pool = _build_candidate_pool(workspace_id, limit=50000)
        payload["topicPool"] = pool

        payload["_pool_meta"] = {
            "workspace_id": workspace_id,
            "pool_size": len(pool),
            "data_dir": str(DATA_DIR),
            "has_imported_urls": (DATA_DIR / f"imported_urls_{ws}.json").exists(),
            "has_draft_topics": (DATA_DIR / f"draft_topics_{ws}.json").exists(),
            "has_uploads_index": (UPLOADS_DIR / f"index_{ws}.json").exists(),
            "has_site_pages": (DATA_DIR / f"site_pages_{ws}.json").exists(),
            "has_site_phrase_index": (DATA_DIR / f"site_phrase_index_{ws}.json").exists(),
        }


                 # ✅ HARD FAIL: prevent “silent success” when RB2 has nothing to work with
        if not isinstance(pool, list) or len(pool) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "ok": False,
                    "error": "no_input_pools",
                    "workspace_id": workspace_id,
                    "hint": "No candidate pool found. Sync sitemap (/sync_sitemap_ingest) or import URLs (/api/urls/import) for this workspace first.",
                    "checks": {
                        "has_imported_urls": (DATA_DIR / f"imported_urls_{ws}.json").exists(),
                        "has_draft_topics": (DATA_DIR / f"draft_topics_{ws}.json").exists(),
                        "has_uploads_index": (UPLOADS_DIR / f"index_{ws}.json").exists(),
                        "has_site_pages": (DATA_DIR / f"site_pages_{ws}.json").exists(),
                        "has_site_phrase_index": (DATA_DIR / f"site_phrase_index_{ws}.json").exists(),
                    },
                },
            )



        # ✅ Node runner expects input.targets (we feed PAGE targets + aliases)
        targets: List[Dict[str, Any]] = []
        for it in pool:
            if not isinstance(it, dict):
                continue
            url = str(it.get("url") or "").strip()
            title = str(it.get("title") or "").strip()
            aliases = it.get("aliases") if isinstance(it.get("aliases"), list) else []
            topic_id = str(it.get("id") or "").strip()
            if not title and not url:
                continue

            targets.append(
                {
                    "url": url,
                    "title": title,
                    "aliases": [str(a).strip() for a in aliases if str(a).strip()],
                    "topic_id": topic_id,
                    "inboundLinks": 0,
                }
            )

        # Only auto-fill if caller didn't already provide targets
        if not isinstance(payload.get("targets"), list) or len(payload.get("targets") or []) == 0:
            payload["targets"] = targets

    except HTTPException:
        # Let intentional HTTP errors (like no_input_pools) pass through unchanged
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RB2 pool build failed: {e}")


    # ✅ Serialize once (ensure we are really sending JSON)
    stdin_str = json.dumps(payload, ensure_ascii=False)
    stdin_bytes = stdin_str.encode("utf-8")

    debug = {
        "stdin_len_chars": len(stdin_str),
        "stdin_len_bytes": len(stdin_bytes),
        "has_rb2Doc": ("rb2Doc" in payload),
        "pool_size": int(len(payload.get("topicPool") or [])),
        "payload_keys": sorted(list(payload.keys()))[:120],
        "stdin_head": stdin_str[:140],
        "_pool_meta": payload.get("_pool_meta"),
    }

    try:
        proc = subprocess.run(
            [_node_exe(), str(RB2_RUNNER)],
            input=stdin_bytes,
            capture_output=True,
            cwd=str(RB2_RUNNER.parent),
            timeout=30,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Node.js not found. Ensure 'node' is on PATH or set NODE_EXE env var.",
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="RB2 runner timed out.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RB2 runner failed to start: {e}")

    stdout = (proc.stdout or b"").decode("utf-8", errors="replace").strip()
    stderr = (proc.stderr or b"").decode("utf-8", errors="replace").strip()

    if not stdout:
        raise HTTPException(
            status_code=500,
            detail={"error": "RB2 returned empty stdout", "stderr": stderr, "_debug": debug},
        )

    try:
        node_out = json.loads(stdout)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "RB2 stdout was not valid JSON",
                "stdout": stdout[:1500],
                "stderr": stderr[:1500],
                "_debug": debug,
            },
        )

    # Normalize Node output → LinkCraftor UI bucket contract
    inner = node_out.get("out") if isinstance(node_out, dict) and isinstance(node_out.get("out"), dict) else node_out
    rec = inner.get("recommended") if isinstance(inner, dict) and isinstance(inner.get("recommended"), list) else []
    opt = inner.get("optional") if isinstance(inner, dict) and isinstance(inner.get("optional"), list) else []

    return {
        "ok": True,
        "internal/strong": rec,
        "semantic/optional": opt,
        "stderr": stderr,
        "_debug": debug,
    }
