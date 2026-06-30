# backend/app/routers/rb2_run.py
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request, Query

from backend.server.pools.target_pools.live_domain_target_intelligence import load_live_domain_targets
from backend.server.pools.target_pools.live_domain_target_intelligence import score_live_domain_target
from backend.server.pools.target_pools.imported_target_intelligence import score_imported_target
from backend.server.engine.intelligence_target_resolver import resolve_intelligent_targets
from backend.server.engine.rb2_adapter import build_rb2_phrase_contexts

router = APIRouter(tags=["rb2"])


# ------------------------------------------------------------
# Path anchors (avoid cwd issues)
# rb2_run.py is: backend/app/routers/rb2_run.py
# parents[0]=routers, [1]=app, [2]=backend, [3]=project root
# FIX: DATA_DIR and the stdlib/fastapi imports above were previously declared
# twice in this module. Consolidated to a single definition here.
# ------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "backend" / "server" / "data"
UPLOADS_DIR = PROJECT_ROOT / "backend" / "server" / "uploads"
RB2_RUNNER = PROJECT_ROOT / "backend" / "server" / "engine_js" / "rb2" / "run_rb2.mjs"

WORD_RE = re.compile(r"[a-z0-9]{3,}")
WS_RE = re.compile(r"^[a-z0-9_]{3,80}$", re.IGNORECASE)


def _node_exe() -> str:
    return os.environ.get("NODE_EXE", "node")


def _ws_safe(ws: str) -> str:
    ws = str(ws or "").strip()
    if not ws:
        raise HTTPException(status_code=400, detail={"ok": False, "error": "missing_workspace_id"})
    if not ws.startswith("ws_"):
        raise HTTPException(status_code=400, detail={"ok": False, "error": "workspace_id_must_start_with_ws_"})
    if not WS_RE.match(ws):
        raise HTTPException(status_code=400, detail={"ok": False, "error": "invalid_workspace_id_chars"})
    return ws


def _safe_load_json(p: Path) -> Any:
    try:
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _safe_read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
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
    raw_ws = (workspace_id or "").strip()
    if not raw_ws:
        return {"ok": False, "error": "missing_workspace_id"}

    # FIX: run the workspace id through the SAME sanitizer the other endpoints
    # use, so a value with path separators / traversal can't be interpolated
    # into the file paths below. Return a soft error (this endpoint's contract)
    # rather than raising, to preserve the existing response shape.
    try:
        ws = _ws_safe(raw_ws)
    except HTTPException as exc:
        detail = exc.detail if isinstance(exc.detail, dict) else {"error": str(exc.detail)}
        return {"ok": False, **detail}

    # --- Pool file conventions (these match what we've been using) ---
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

    # Hard guard: if workspace has no pool files at all, don't let RB2 run empty
    if not any_exists:
        return {"ok": False, "workspace_id": ws, "error": "workspace_not_initialized", "pools": pools}

    return {"ok": True, "workspace_id": ws, "total_items_across_pools": total, "pools": pools}


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


def _draft_title_phrase_aliases(title: str) -> list[str]:
    s = str(title or "").strip()
    if not s:
        return []

    if s.lower().startswith("drafts "):
        s = s[7:].strip()

    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return []

    tokens = [t for t in re.findall(r"[A-Za-z0-9]+", s.lower()) if t]
    if len(tokens) < 2:
        return []

    STOPWORDS = {
        "and", "or", "the", "a", "an", "of", "to", "in", "on", "for", "with",
        "by", "at", "from", "as", "is", "are", "was", "were", "be", "can",
        "during"
    }

    def is_valid_phrase(parts: list[str]) -> bool:
        if len(parts) < 2 or len(parts) > 8:
            return False

        if parts[0] in STOPWORDS or parts[-1] in STOPWORDS:
            return False

        meaningful = [p for p in parts if p not in STOPWORDS]
        if len(meaningful) < 2:
            return False

        return True

    out: list[str] = []
    seen = set()

    n = len(tokens)
    for i in range(n):
        for j in range(i + 2, min(i + 9, n + 1)):
            phrase_tokens = tokens[i:j]

            if not is_valid_phrase(phrase_tokens):
                continue

            phrase = " ".join(phrase_tokens).strip()
            if phrase and phrase not in seen:
                seen.add(phrase)
                out.append(phrase)

    full = " ".join(tokens).strip()
    if is_valid_phrase(tokens) and full not in seen:
        out.insert(0, full)

    return out


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
      - Imported URLs are tagged origin="imported" (the scoring dispatch in
        rb2_run matches on that exact value).
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
            raw_title = str(r.get("working_title") or r.get("title") or "").strip()

            # remove "Drafts " prefix
            if raw_title.lower().startswith("drafts "):
                raw_title = raw_title[7:].strip()

            title = raw_title
            planned_url = str(r.get("planned_url") or "").strip()
            raw_aliases = r.get("aliases") if isinstance(r.get("aliases"), list) else []

            base_aliases = [str(a).strip() for a in raw_aliases if str(a).strip()]
            draft_aliases = _draft_title_phrase_aliases(title)

            STOPWORDS = {
                "and", "or", "the", "a", "an", "of", "to", "in", "on", "for", "with",
                "by", "at", "from", "as", "is", "are", "was", "were", "be", "can",
            }

            def _keep_alias(p: str) -> bool:
                parts = [x for x in str(p or "").lower().split() if x]
                if len(parts) < 2 or len(parts) > 8:
                    return False
                if parts[0] in STOPWORDS or parts[-1] in STOPWORDS:
                    return False
                meaningful = [x for x in parts if x not in STOPWORDS]
                return len(meaningful) >= 2

            aliases = []
            seen = set()

            for a in base_aliases + draft_aliases:
                a = str(a).strip()
                if not a:
                    continue
                if not _keep_alias(a):
                    continue
                key = a.lower()
                if key in seen:
                    continue
                seen.add(key)
                aliases.append(a)

            if not title and not planned_url:
                continue

            _add_page_candidate(
                cid=f"d:{topic_id or title or planned_url}",
                url=planned_url,
                title=title or _title_from_url(planned_url) or planned_url,
                origin="draft",
                aliases=aliases,
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

    # 4) Live-Domain Target Pool -> PAGE targets
    # Uses Builder v2/v2.1 output instead of raw site_pages.
    live_targets = load_live_domain_targets(workspace_id)

    if isinstance(live_targets, list) and live_targets:
        for p in live_targets[:limit]:
            if not isinstance(p, dict):
                continue

            url = str(p.get("url") or "").strip()
            if not url:
                continue

            title = str(p.get("title") or p.get("h1") or "").strip()
            title = title or _title_from_url(url) or url

            _add_page_candidate(
                cid=f"live:{url}",
                url=url,
                title=title,
                origin="live_domain_target_pool",
                meta={
                    "h1": p.get("h1"),
                    "page_type_hint": p.get("page_type_hint"),
                    "priority_bucket": p.get("priority_bucket"),
                    "seed_path_match": p.get("seed_path_match"),
                    "source_type": p.get("source_type") or "live_domain",
                    "title_source": p.get("title_source"),
                },
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


def _active_target_set_path_for_rb2(workspace_id: str) -> Path:
    ws = _ws_safe(workspace_id)
    return DATA_DIR / "target_pools" / f"active_target_set_{ws}.json"


def _load_active_target_set_for_rb2(workspace_id: str) -> Dict[str, Any]:
    fp = _active_target_set_path_for_rb2(workspace_id)
    if not fp.exists():
        return {}
    try:
        obj = json.loads(fp.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _filter_candidate_pool_by_active_membership(
    workspace_id: str,
    pool: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    active = _load_active_target_set_for_rb2(workspace_id)
    if not active:
        return pool

    live_urls = set(str(x).strip() for x in active.get("active_live_domain_urls") or [] if str(x).strip())
    imported_urls = set(str(x).strip() for x in active.get("active_imported_urls") or [] if str(x).strip())
    draft_ids = set(str(x).strip() for x in active.get("active_draft_ids") or [] if str(x).strip())
    document_ids = set(str(x).strip() for x in active.get("active_document_ids") or [] if str(x).strip())

    if not (live_urls or imported_urls or draft_ids or document_ids):
        return pool

    out: List[Dict[str, Any]] = []

    for item in pool or []:
        if not isinstance(item, dict):
            continue

        origin = str(item.get("origin") or "").strip()
        url = str(item.get("url") or "").strip()
        cid = str(item.get("id") or "").strip()
        meta = item.get("_lc_meta") if isinstance(item.get("_lc_meta"), dict) else {}

        keep = False

        if origin in {"live_domain_target_pool", "live_page_fallback"}:
            keep = bool(url and url in live_urls)

        elif origin == "imported":
            keep = bool(url and url in imported_urls)

        elif origin == "draft":
            topic_id = str(meta.get("topic_id") or "").strip()
            clean_cid = cid[2:] if cid.startswith("d:") else cid
            keep = bool(
                (topic_id and topic_id in draft_ids)
                or (clean_cid and clean_cid in draft_ids)
                or (url and url in draft_ids)
            )

        elif origin == "other-doc":
            clean_cid = cid[4:] if cid.startswith("doc:") else cid
            keep = bool(clean_cid and clean_cid in document_ids)

        if keep:
            out.append(item)

    return out


@router.post("/run")
async def rb2_run(request: Request) -> Dict[str, Any]:
    if not RB2_RUNNER.exists():
        raise HTTPException(status_code=500, detail=f"RB2 runner missing: {RB2_RUNNER}")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON request body.")

    # FIX: removed the misleading `or "default"` fallback. _ws_safe requires a
    # ws_-prefixed id and raises otherwise, so "default" could never have
    # survived validation — the fallback was dead and hid the real contract.
    workspace_id = str(payload.get("workspace_id") or payload.get("workspaceId") or "").strip()
    ws = _ws_safe(workspace_id)

    #  Attach rb2.extract.v1 contract
    try:
        doc_id = str(payload.get("docId") or payload.get("doc_id") or payload.get("id") or "doc_unknown")
        doc_html = payload.get("html")
        doc_text = payload.get("text")
        rb2_doc = build_rb2_phrase_contexts(doc_id, html=doc_html, text=doc_text)
        payload["rb2Doc"] = rb2_doc
        payload.setdefault("_rb2_extract_version", rb2_doc.get("version"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RB2 extraction failed: {e}")

    #  Build + inject candidate pool (PAGE targets + phrase aliases)
    try:
        full_pool = _build_candidate_pool(workspace_id, limit=50000)
        pool = _filter_candidate_pool_by_active_membership(workspace_id, full_pool)
        payload["topicPool"] = pool

        payload["_pool_meta"] = {
            "workspace_id": workspace_id,
            "pool_size": len(pool),
            "full_pool_size_before_active_filter": len(full_pool),
            "active_membership_filter_used": len(pool) != len(full_pool),
            "data_dir": str(DATA_DIR),
            "has_imported_urls": (DATA_DIR / f"imported_urls_{ws}.json").exists(),
            "has_draft_topics": (DATA_DIR / f"draft_topics_{ws}.json").exists(),
            "has_uploads_index": (UPLOADS_DIR / f"index_{ws}.json").exists(),
            "has_site_pages": (DATA_DIR / f"site_pages_{ws}.json").exists(),
            "has_site_phrase_index": (DATA_DIR / f"site_phrase_index_{ws}.json").exists(),
        }

        #  HARD FAIL: prevent silent success when RB2 has nothing to work with
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

        #  Node runner expects input.targets (we feed PAGE targets + aliases)
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

            clean_aliases = [str(a).strip() for a in aliases if str(a).strip()]

            lc_meta = it.get("_lc_meta") if isinstance(it.get("_lc_meta"), dict) else {}
            intelligence = {}

            if it.get("origin") == "live_domain_target_pool":
                # Use title + aliases as the scoring phrase context.
                phrase_context = " ".join([title] + clean_aliases).strip()

                intelligence = score_live_domain_target(
                    phrase_context,
                    {
                        "url": url,
                        "title": title,
                        "h1": lc_meta.get("h1") or title,
                        "page_type_hint": lc_meta.get("page_type_hint"),
                        "priority_bucket": lc_meta.get("priority_bucket"),
                        "seed_path_match": lc_meta.get("seed_path_match"),
                    },
                )

                # Intelligence-first resolver support:
                # Store resolver matches for future runtime use/debugging.
                try:
                    resolver_matches = resolve_intelligent_targets(
                        workspace_id,
                        phrase_context,
                        limit=3,
                    )
                except Exception:
                    resolver_matches = []

                lc_meta["resolver_matches"] = resolver_matches
                lc_meta["resolver_enabled"] = True

            # FIX: was `== "imported_target_pool"`, a value nothing ever sets, so
            # imported targets were never scored or resolver-matched. The pool
            # builder tags imported URLs origin="imported" (and the active-
            # membership filter already matches that), so dispatch on it here.
            elif it.get("origin") == "imported":
                # Use title + aliases as the scoring phrase context.
                phrase_context = " ".join([title] + clean_aliases).strip()

                intelligence = score_imported_target(
                    phrase_context,
                    {
                        "url": url,
                        "title": title,
                        "h1": lc_meta.get("h1") or title,
                        "page_type_hint": lc_meta.get("page_type_hint"),
                        "priority_bucket": lc_meta.get("priority_bucket"),
                        "import_source": lc_meta.get("import_source"),
                        "path": lc_meta.get("path"),
                    },
                )

                # Multi-source intelligent resolver support.
                # Resolver now includes live-domain + imported targets.
                try:
                    resolver_matches = resolve_intelligent_targets(
                        workspace_id,
                        phrase_context,
                        limit=3,
                    )
                except Exception:
                    resolver_matches = []

                lc_meta["resolver_matches"] = resolver_matches
                lc_meta["resolver_enabled"] = True

            resolver_matches_for_target = (
                lc_meta.get("resolver_matches")
                if isinstance(lc_meta.get("resolver_matches"), list)
                else []
            )
            best_resolver_match = (
                resolver_matches_for_target[0]
                if resolver_matches_for_target and isinstance(resolver_matches_for_target[0], dict)
                else {}
            )

            auto_link_allowed = best_resolver_match.get("auto_link_allowed")
            suggest_only = best_resolver_match.get("suggest_only")
            confidence_reason = best_resolver_match.get("confidence_reason")
            cluster_confidence_floor = best_resolver_match.get("cluster_confidence_floor")

            lc_meta["auto_link_allowed"] = auto_link_allowed
            lc_meta["suggest_only"] = suggest_only
            lc_meta["confidence_reason"] = confidence_reason
            lc_meta["cluster_confidence_floor"] = cluster_confidence_floor

            targets.append(
                {
                    "url": url,
                    "title": title,
                    "aliases": clean_aliases,
                    "topic_id": topic_id,
                    "inboundLinks": 0,
                    "origin": it.get("origin"),
                    "auto_link_allowed": auto_link_allowed,
                    "suggest_only": suggest_only,
                    "confidence_reason": confidence_reason,
                    "cluster_confidence_floor": cluster_confidence_floor,
                    "_lc_meta": lc_meta,
                    "_target_intelligence": intelligence,
                    "_resolver_intelligence": best_resolver_match,
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

    #  Serialize once (ensure we are really sending JSON)
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

    # Normalize Node output to LinkCraftor UI bucket contract.
    # Unified contract: Node RB2 now returns internal/strong and semantic/optional directly.
    inner = node_out.get("out") if isinstance(node_out, dict) and isinstance(node_out.get("out"), dict) else node_out

    strong = []
    optional = []

    if isinstance(inner, dict):
        strong = inner.get("internal/strong") if isinstance(inner.get("internal/strong"), list) else []
        optional = inner.get("semantic/optional") if isinstance(inner.get("semantic/optional"), list) else []

        # Backward compatibility only, for older cached/local RB2 outputs.
        if not strong and isinstance(inner.get("recommended"), list):
            strong = inner.get("recommended") or []

        if not optional and isinstance(inner.get("optional"), list):
            optional = inner.get("optional") or []

    hidden = []
    meta = {}

    if isinstance(inner, dict):
        hidden = inner.get("hidden") if isinstance(inner.get("hidden"), list) else []
        meta = inner.get("meta") if isinstance(inner.get("meta"), dict) else {}

    def _anchor_text(x):
        if not isinstance(x, dict):
            return ""
        for k in ("phrase", "phrase_text", "text", "label"):
            v = str(x.get(k) or "").strip()
            if v:
                return v.lower()
        anchor = x.get("anchor")
        if isinstance(anchor, dict):
            return str(anchor.get("text") or anchor.get("raw") or "").strip().lower()
        return ""

    def _target_from_hidden_match(h):
        if not isinstance(h, dict):
            return None
        t = h.get("target")
        if not isinstance(t, dict):
            return None
        url = str(t.get("url") or "").strip()
        title = str(t.get("title") or "").strip()
        if not url:
            return None
        return {
            "url": url,
            "title": title,
            "source_type": "live_domain",
            "runtime_score": h.get("score", 0),
            "via": h.get("via", ""),
        }

    hidden_by_anchor = {}
    for h in hidden:
        key = _anchor_text(h)
        tgt = _target_from_hidden_match(h)
        if not key or not tgt:
            continue
        hidden_by_anchor.setdefault(key, []).append(tgt)

    def _fallback_targets_for_anchor(anchor_text, target_rows, limit=3):
        phrase = str(anchor_text or "").strip().lower()
        phrase_tokens = set(re.findall(r"[a-z0-9]{3,}", phrase))
        if not phrase_tokens:
            return []

        scored = []
        for t in target_rows or []:
            if not isinstance(t, dict):
                continue

            url = str(t.get("url") or "").strip()
            title = str(t.get("title") or "").strip()
            aliases = t.get("aliases") if isinstance(t.get("aliases"), list) else []
            origin = str(t.get("origin") or "live_domain").strip()

            haystack = " ".join([title, url] + [str(a) for a in aliases if str(a).strip()]).lower()
            hay_tokens = set(re.findall(r"[a-z0-9]{3,}", haystack))
            if not hay_tokens:
                continue

            overlap = len(phrase_tokens & hay_tokens)
            score = overlap / max(1, len(phrase_tokens))

            if phrase in haystack:
                score += 0.35

            if score >= 0.34 and url:
                scored.append({
                    "url": url,
                    "title": title or url,
                    "source_type": origin or "live_domain",
                    "runtime_score": round(score, 4),
                    "via": "backend_fallback_target_match",
                    "auto_link_allowed": t.get("auto_link_allowed"),
                    "suggest_only": t.get("suggest_only"),
                    "confidence_reason": t.get("confidence_reason"),
                    "cluster_confidence_floor": t.get("cluster_confidence_floor"),
                    "_resolver_intelligence": t.get("_resolver_intelligence"),
                })

        scored.sort(key=lambda x: x.get("runtime_score", 0), reverse=True)
        return scored[:limit]

    # NOTE: fallback matching runs against the locally built `targets`. If a
    # caller supplied their own payload["targets"], those are sent to Node but
    # this fallback still uses the backend-built rows for anchor matching.
    fallback_target_rows = targets

    def _enrich_bucket(items):
        out = []
        for item in items or []:
            if not isinstance(item, dict):
                out.append(item)
                continue

            key = _anchor_text(item)
            matches = hidden_by_anchor.get(key) or []

            # Fallback: if Node RB2 did not produce hidden target matches,
            # match the selected phrase directly against backend live-domain targets.
            if not matches and key:
                try:
                    matches = _fallback_targets_for_anchor(key, fallback_target_rows, limit=3)
                except Exception:
                    matches = []

            if matches and not str(item.get("best_target_url") or "").strip():
                best = matches[0]
                item = dict(item)
                item["resolved_targets"] = matches[:3]
                item["best_target"] = best
                item["best_target_url"] = best.get("url", "")
                item["best_target_title"] = best.get("title", "")
                item["best_target_source_type"] = best.get("source_type", "")
                item["best_target_runtime_score"] = best.get("runtime_score", 0)
                item["auto_link_allowed"] = best.get("auto_link_allowed")
                item["suggest_only"] = best.get("suggest_only")
                item["confidence_reason"] = best.get("confidence_reason")
                item["cluster_confidence_floor"] = best.get("cluster_confidence_floor")
                item["_resolver_intelligence"] = best.get("_resolver_intelligence")

                ri = item.get("runtime_intelligence")
                if isinstance(ri, dict):
                    ri = dict(ri)
                    ri["resolver_target_count"] = len(matches)
                    ri["best_target_url"] = best.get("url", "")
                    ri["best_target_source_type"] = best.get("source_type", "")
                    ri["auto_link_allowed"] = best.get("auto_link_allowed")
                    ri["suggest_only"] = best.get("suggest_only")
                    ri["confidence_reason"] = best.get("confidence_reason")
                    ri["cluster_confidence_floor"] = best.get("cluster_confidence_floor")
                    item["runtime_intelligence"] = ri

            out.append(item)
        return out

    strong = _enrich_bucket(strong)
    optional = _enrich_bucket(optional)

    debug["postprocess_target_bridge"] = {
        "hidden_matches_indexed": sum(len(v) for v in hidden_by_anchor.values()),
        "hidden_anchor_keys": len(hidden_by_anchor),
        "strong_with_url": sum(1 for x in strong if isinstance(x, dict) and x.get("best_target_url")),
        "optional_with_url": sum(1 for x in optional if isinstance(x, dict) and x.get("best_target_url")),
    }

    return {
        "ok": True,
        "internal/strong": strong,
        "semantic/optional": optional,
        "hidden": hidden,
        "meta": meta,
        "stderr": stderr,
        "_debug": debug,
    }


@router.post("/resolver-debug")
async def rb2_resolver_debug(request: Request) -> Dict[str, Any]:
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON request body.")

    workspace_id = str(payload.get("workspace_id") or payload.get("workspaceId") or "default").strip()
    phrase = str(payload.get("phrase") or payload.get("anchor_phrase") or "").strip()
    limit = int(payload.get("limit") or 10)

    if not phrase:
        raise HTTPException(status_code=400, detail="Missing phrase.")

    rows = resolve_intelligent_targets(
        workspace_id=workspace_id,
        anchor_phrase=phrase,
        limit=limit,
    )

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "phrase": phrase,
        "count": len(rows),
        "rows": rows,
    }