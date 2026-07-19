# backend/app/routers/site_reader.py
from __future__ import annotations

from fastapi import HTTPException

import gzip
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

import requests
from fastapi import APIRouter, Query
from backend.server.runtime.live_route_orchestration_hooks import enqueue_and_run_website_ingestion_job_v1
from pydantic import BaseModel, Field

class ActiveTargetSetPayload(BaseModel):
    workspace_id: str
    active_document_ids: list[str] | None = None
    active_draft_ids: list[str] | None = None
    active_imported_urls: list[str] | None = None
    active_live_domain_urls: list[str] | None = None


from backend.server.pools.target_pools.document_registry_pool import build_document_registry_pool
from backend.server.pools.target_pools.draft_target_pool import build_draft_target_pool
from backend.server.pools.target_pools.imported_target_pool import build_imported_target_pool
from backend.server.pools.target_pools.live_domain_target_pool import build_live_domain_target_pool
from backend.server.engine.workspace_topic_cluster_builder import build_workspace_topic_clusters
from backend.server.pools.target_pools.url_pool_manager import (
    initialize_url_pool_from_current_active,
    get_url_pool_stats,
    load_active_urls,
    load_reserve_urls,
    classify_url_list,
    promote_url,
    demote_url,
)
from backend.server.site_reader.html_extract import extract_headings_and_body
from backend.server.stores.upload_phrase_pool_builder import build_upload_phrase_pool
from backend.server.site_reader.phrase_generators import (
    generate_phrase_bundle_for_page,
)

from backend.server.site_reader.store import (
    load_site_pages,
    load_site_phrase_index,
    load_site_sources,
    save_site_pages,
    save_site_phrase_index,
    save_site_sources,
)
from backend.server.stores.draft_pool_store import (
    load_draft_items_ws,
    load_draft_meta_ws,
    save_draft_items_ws,
    save_draft_meta_ws,
)

router = APIRouter(tags=["site-reader"])

# ------------------------------------------------------------
# HTTP hardening (sitemap + page fetch)
# ------------------------------------------------------------
UA = "Mozilla/5.0 (LinkCraftorBot/1.0; +https://linkcraftor.com)"
DEFAULT_TIMEOUT = (8, 20)  # (connect_timeout, read_timeout)

# Keep parsing bounded so one huge page doesn't stall the request
MAX_HTML_BYTES = 900_000
MAX_BODY_CHARS = 200_000

# ------------------------------------------------------------
# Workspace safety (prevents cross-contamination)
# ------------------------------------------------------------
WS_RE = re.compile(r"^[a-z0-9_]{3,80}$", re.IGNORECASE)


def _ws_safe(workspace_id: str) -> str:
    ws = str(workspace_id or "").strip()
    if not ws:
        raise ValueError("missing_workspace_id")
    if not ws.startswith("ws_"):
        raise ValueError("workspace_id_must_start_with_ws_")
    if not WS_RE.match(ws):
        raise ValueError("invalid_workspace_id_chars")
    return ws


def _ws_or_error(workspace_id: str) -> tuple[str | None, dict | None]:
    try:
        return _ws_safe(workspace_id), None
    except ValueError as e:
        return None, {"ok": False, "error": str(e)}


def _active_target_set_path(ws: str) -> Path:
    return Path("backend/server/data/target_pools") / f"active_target_set_{ws}.json"


def _now_ts() -> float:
    return time.time()


def _time_left(deadline_ts: float | None) -> float:
    if deadline_ts is None:
        return 999999.0
    return max(0.0, float(deadline_ts) - _now_ts())


def _near_deadline(deadline_ts: float | None, *, min_left: float = 1.5) -> bool:
    return _time_left(deadline_ts) <= float(min_left)


_CHARSET_RE = re.compile(r"charset\s*=\s*([a-zA-Z0-9_\-:]+)", re.IGNORECASE)


def _decode_html_bytes(content: bytes, content_type: str = "") -> str:
    """
    Decode bounded HTML bytes to text, honoring charset from Content-Type when present.
    Falls back safely to avoid mojibake later.
    """
    if not isinstance(content, (bytes, bytearray)):
        return ""

    if len(content) > MAX_HTML_BYTES:
        content = content[:MAX_HTML_BYTES]

    ct = (content_type or "").lower()
    enc = None
    m = _CHARSET_RE.search(ct)
    if m:
        enc = (m.group(1) or "").strip().strip('"').strip("'")

    if enc:
        try:
            return content.decode(enc, errors="strict")
        except Exception:
            pass

    for fallback in ("utf-8", "windows-1252", "latin-1"):
        try:
            return content.decode(fallback, errors="strict" if fallback == "utf-8" else "replace")
        except Exception:
            continue

    return content.decode("latin-1", errors="replace")


def _http_get(
    url: str,
    *,
    deadline_ts: float | None = None,
    session: requests.Session | None = None,
) -> Tuple[int, bytes, str]:
    """
    Deadline-aware fetch with lightweight resiliency:
    - Try as-is
    - If 404 and hostname starts with www., retry non-www
    - If still 404 and no trailing slash, retry with trailing slash
    Retries only happen if enough time remains per deadline_ts.
    """

    def _remaining() -> float:
        return _time_left(deadline_ts)

    def _timeout_tuple() -> tuple[float, float]:
        rem = _remaining()
        connect = min(3.0, max(0.5, rem))
        read = min(7.0, max(0.5, rem))
        return (connect, read)

    def _fetch(u: str) -> Tuple[int, bytes, str]:
        if _remaining() <= 0.2:
            return 0, b"", ""
        headers = {"User-Agent": UA, "Accept": "application/xml,text/xml,text/html,*/*"}
        getter = (session.get if isinstance(session, requests.Session) else requests.get)
        r = getter(u, headers=headers, timeout=_timeout_tuple(), allow_redirects=True)
        ct = (r.headers.get("content-type") or "").lower()
        return r.status_code, r.content, ct

    url = (url or "").strip()
    if not url:
        return 0, b"", ""

    code, content, ct = _fetch(url)
    if code != 404:
        return code, content, ct

    if _remaining() < 2.0:
        return code, content, ct

    try:
        pu = urlparse(url)
        host = (pu.hostname or "").strip()
        path = pu.path or ""
        qs = (("?" + pu.query) if pu.query else "")
        frag = (("#" + pu.fragment) if pu.fragment else "")
        scheme = pu.scheme or "https"
    except Exception:
        return code, content, ct

    if host.lower().startswith("www.") and _remaining() >= 2.0:
        alt_host = host[4:]
        alt_url = f"{scheme}://{alt_host}{path}{qs}{frag}"
        code2, content2, ct2 = _fetch(alt_url)
        if code2 != 404:
            return code2, content2, ct2
        code, content, ct = code2, content2, ct2

    if path and not path.endswith("/") and _remaining() >= 2.0:
        slash_url = f"{scheme}://{host}{path}/{qs}{frag}"
        code3, content3, ct3 = _fetch(slash_url)
        if code3 != 404:
            return code3, content3, ct3

        if host.lower().startswith("www.") and _remaining() >= 2.0:
            alt_host = host[4:]
            slash_alt_url = f"{scheme}://{alt_host}{path}/{qs}{frag}"
            code4, content4, ct4 = _fetch(slash_alt_url)
            if code4 != 404:
                return code4, content4, ct4

    return code, content, ct


def _maybe_decompress(url: str, content: bytes, content_type: str) -> bytes:
    u = (url or "").lower()
    if u.endswith(".gz") or "application/x-gzip" in content_type or "gzip" in content_type:
        return gzip.decompress(content)
    return content


def _parse_sitemap_kind_and_locs(xml_bytes: bytes) -> Tuple[str, List[str]]:
    root = ET.fromstring(xml_bytes)
    tag = (root.tag or "").lower()
    locs = [
        el.text.strip()
        for el in root.findall(".//{*}loc")
        if el is not None and el.text and el.text.strip()
    ]
    if tag.endswith("sitemapindex"):
        return "index", locs
    if tag.endswith("urlset"):
        return "urlset", locs
    return "unknown", []


def _fetch_and_expand_sitemaps(
    sitemap_url: str,
    max_sitemaps: int = 250,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Recursively expands sitemap indexes to URL lists.
    Returns (urls, errors)
    """
    seen: set[str] = set()
    urls: List[str] = []
    errors: List[Dict[str, Any]] = []

    sess = requests.Session()

    queue: List[str] = [(sitemap_url or "").strip()]
    while queue and len(seen) < max_sitemaps:
        sm = queue.pop(0).strip()
        if not sm or sm in seen:
            continue
        seen.add(sm)

        try:
            code, content, ct = _http_get(sm, session=sess)
            if code >= 400:
                errors.append({"url": sm, "code": code, "error": "sitemap_fetch_failed"})
                continue

            xml_bytes = _maybe_decompress(sm, content, ct)
            kind, locs = _parse_sitemap_kind_and_locs(xml_bytes)

            if kind == "index":
                for loc in locs:
                    if loc and loc not in seen:
                        queue.append(loc)
            elif kind == "urlset":
                urls.extend(locs)
            else:
                errors.append({"url": sm, "code": code, "error": "unknown_sitemap_format"})
        except Exception as e:
            errors.append({"url": sm, "code": 0, "error": str(e)})

    return urls, errors


ARTICLE_ALLOW_RE = re.compile(r"(/blog/|/blogs/|/post/|/posts/|/article/|/articles/|/news/)", re.IGNORECASE)

ARTICLE_EXCLUDE_RE = re.compile(
    r"("
    r"\.(?:jpg|jpeg|png|gif|webp|svg|ico|pdf|doc|docx|ppt|pptx|xls|xlsx|zip|rar|7z|tar|gz|mp3|mp4|m4a|wav|mov|avi|webm|woff2?|ttf|otf|eot)$|"
    r"/robots\.txt$|/humans\.txt$|/ads\.txt$|"
    r"/sitemap(?:[_-]index)?\.xml$|/wp-sitemap\.xml$|"
    r"/feed/?$|/rss/?$|/atom/?$|"
    r"/wp-admin/|/wp-login\.php|/xmlrpc\.php|/wp-json/|"
    r"/api/|/graphql$|/rest/|/ajax/|/admin/|/login/?$|/logout/?$|"
    r"/search/?$|/search/|"
    r"/page/\d+/?$|"
    r"/tag/|/tags/|/category/|/categories/|/author/|"
    r"/archives?/|/archive/|"
    r"/embed/?$|/trackback/?$|/comments/?$|"
    r"/cart/?$|/checkout/?$|/my-account/?$|/account/?$|/orders/?$|/wishlist/?$|"
    r"/compare/?$|/subscriptions?/?$|"
    r"/privacy(?:-policy)?/?$|/cookie(?:-policy)?/?$|"
    r"/terms(?:-and-conditions?)?/?$|/disclaimer/?$|"
    r"/about/?$|/contact/?$|/faq/?$|/help/?$|/support/?$|"
    r"/newsletter/?$|/advertise/?$|/affiliate-disclosure/?$|/editorial-policy/?$|/image-usage-policy/?$|/edit-profile/?$|"
    r"/elementor-|/elementor/|/elementskit-|/elementskit/|/elementskit-content/|"
    r"/wp-content/uploads/elementor/|"
    r"megamenu|menuitem\d+|dynamic-content|template|header|footer|"
    r"[?&](?:utm_[^=]+|gclid|fbclid|msclkid|yclid|_ga|_gl|ref|ref_src|source|campaign|adgroup|adid|affiliate|aff|srsltid)="
    r"|[?&](?:preview|preview_id|preview_nonce|customize_changeset_uuid|customize_theme|customize_messenger_channel)="
    r"|[?&](?:elementor-preview|elementor_library|elementskit_template|et_fb|ver|v)="
    r")",
    re.IGNORECASE,
)

ARTICLE_HUB_LIKE_PATH_RE = re.compile(
    r"^/(?:"  # category hubs
    r"makeup|nails|skin-care|hair-care|fashion|relationship|health-wellness|body-art|travel|horoscope|politics|entertainment|news"
    r")(?:/|$)"
    r"|^/(?:"  # category sub hubs
    r"makeup|nails|skin-care|hair-care|fashion|relationship|health-wellness|body-art|travel|horoscope|politics|entertainment|news"
    r")/[a-z0-9-]{2,50}/?$",
    re.IGNORECASE,
)

THEME_JUNK_RE = re.compile(
    r"("
    r"elementor|elementskit|megamenu|menuitem\d+|dynamic content|content widget|"
    r"wp-block|site-logo|nav-menu|menu item|breadcrumb|pagination|skip to content|read more|"
    r"header|footer|sidebar|cookie banner|newsletter|subscribe|related posts"
    r")",
    re.IGNORECASE,
)


def _bucket_rank(b: str) -> int:
    return 0 if (b or "") == "internal_strong" else 1


def _bucket_prio(b: str) -> int:
    return 2 if (b or "") == "internal_strong" else 1


def _normalize_domain(domain_or_url: str) -> str:
    raw = (domain_or_url or "").strip()
    if not raw:
        return ""
    if "://" not in raw:
        raw = "https://" + raw
    u = urlparse(raw)
    host = (u.hostname or u.netloc or "").strip().lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    return host


def _domain_from_url(url: str) -> str:
    try:
        u = urlparse((url or "").strip())
        return (u.netloc or "").strip().lower().split(":")[0]
    except Exception:
        return ""


def _base_from_host(host: str) -> str:
    host = (host or "").strip().lower()
    return f"https://{host}" if host else ""


_TITLE_TAG_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_H1_TAGS_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
_TAG_STRIP_RE = re.compile(r"<[^>]+>")

_META_TAG_RE = re.compile(r"<meta\b[^>]*?>", re.IGNORECASE | re.DOTALL)
_ATTR_RE = re.compile(
    r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(".*?"|\'.*?\'|[^\s"\'>]+)',
    re.DOTALL,
)


def _clean_text(s: str) -> str:
    s = unescape(s or "")
    s = _TAG_STRIP_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _parse_meta_attrs(tag: str) -> dict:
    attrs: dict = {}
    for m in _ATTR_RE.finditer(tag or ""):
        k = (m.group(1) or "").strip().lower()
        v = (m.group(2) or "").strip()
        if v.startswith(("'", '"')) and v.endswith(("'", '"')) and len(v) >= 2:
            v = v[1:-1]
        attrs[k] = unescape(v)
    return attrs


def _meta_content(html: str, *, name: str | None = None, prop: str | None = None) -> str:
    want_name = (name or "").strip().lower()
    want_prop = (prop or "").strip().lower()
    for mt in _META_TAG_RE.findall(html or ""):
        attrs = _parse_meta_attrs(mt)
        if want_name and (attrs.get("name", "").strip().lower() == want_name):
            return _clean_text(attrs.get("content", ""))
        if want_prop and (attrs.get("property", "").strip().lower() == want_prop):
            return _clean_text(attrs.get("content", ""))
    return ""


def _extract_title_and_meta(html: str) -> tuple[str, str]:
    title = _meta_content(html, prop="og:title")
    if not title:
        m = _TITLE_TAG_RE.search(html or "")
        title = _clean_text(m.group(1)) if m else ""
    meta_desc = _meta_content(html, name="description")
    return title, meta_desc


def _norm_site(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def _h1_candidates_from_block(block_html: str) -> list[str]:
    cands = [_clean_text(x) for x in _H1_TAGS_RE.findall(block_html or "")]
    return [c for c in cands if c]


def _is_site_like_text(text: str, site_name: str = "", host: str = "") -> bool:
    t = (text or "").strip().lower()
    if not t:
        return True
    sn = (site_name or "").strip().lower()
    h = (host or "").strip().lower()
    h = h[4:] if h.startswith("www.") else h
    h_root = h.split(".")[0] if h else ""
    if sn and t == sn:
        return True
    if h and t == h:
        return True
    if h_root and t == h_root:
        return True
    if sn and (t.startswith(sn + " ") or t.endswith(" " + sn)):
        return True
    return False


def _pick_best_h1(html: str, fallback_h1: str, site_name: str = "", title_hint: str = "") -> str:
    sn = _norm_site(site_name)
    fb = (fallback_h1 or "").strip()
    th = (title_hint or "").strip()

    def is_site_like(txt: str) -> bool:
        t = _norm_site(txt)
        if not t:
            return True
        if sn and (t == sn or sn in t):
            return True
        return False

    def pick_best(cands: list[str]) -> str:
        best = ""
        best_score = -1
        for c in cands:
            if is_site_like(c):
                continue
            score = (len(c.split()) * 10) + len(c)
            if score > best_score:
                best_score = score
                best = c
        return best

    for blk in re.findall(r"<main\b[^>]*>.*?</main>", html or "", flags=re.I | re.S):
        best = pick_best(_h1_candidates_from_block(blk))
        if best:
            return best

    for blk in re.findall(r"<article\b[^>]*>.*?</article>", html or "", flags=re.I | re.S):
        best = pick_best(_h1_candidates_from_block(blk))
        if best:
            return best

    best = pick_best(_h1_candidates_from_block(html or ""))
    if best:
        return best
    if th:
        return th
    return fb if fb else "Untitled"


def ingest_one_page(workspace_id: str, url: str) -> dict:
    ws = _ws_safe(workspace_id)

    # 1. Fetch page
    code, content, ct = _http_get(url)
    if code >= 400:
        return {"ok": False, "url": url, "error": f"fetch_failed_{code}"}

    html = _decode_html_bytes(content, ct)

    # 2. Extract structure
    h1, h2, h3, body = extract_headings_and_body(html)

    # 3. Generate phrases (THIS is your new system)
    bundle = generate_phrase_bundle_for_page(
        url=url,
        h1=h1,
        h2_headings=h2,
        h3_headings=h3,
        body_text=body,
        max_body_phrases=120,
    )

    # 4. Load existing store
    pages = load_site_pages(ws)
    phrase_index = load_site_phrase_index(ws)

    pages_data = pages.get("pages", {})
    phrases_data = phrase_index.get("phrases", {})

    # 5. Save page
    pages_data[url] = {
        "url": url,
        "h1": h1,
        "headings": h2 + h3,
    }

       # 6. Remove old phrases for this same source_url first
    phrases_data = {
        k: v
        for k, v in phrases_data.items()
        if not (isinstance(v, dict) and v.get("source_url") == url)
    }

    # 7. Save fresh phrases for this page
    for group in bundle.values():
        for p in group:
            phrases_data[p["norm"]] = {
                **p,
                "source_url": url,
            }

    # 8. Persist
    save_site_pages(ws, {"pages": pages_data})
    save_site_phrase_index(ws, {"phrases": phrases_data})

    return {
        "ok": True,
        "universal_knowledge_orchestration": orchestration_result if "orchestration_result" in locals() else None,
        "url": url,
        "h1": h1,
        "phrases_added": sum(len(v) for v in bundle.values()),
    }

@router.post("/ingest_one")
def ingest_one(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    url: str = Query(..., description="Full article URL to ingest"),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    return ingest_one_page(ws, url)


# ------------------------------------------------------------
# Health + Debug
# ------------------------------------------------------------
@router.get("/health")
def site_reader_health():
    return {"ok": True, "module": "site-reader"}


@router.get("/debug/state")
def site_reader_debug_state(workspace_id: str = Query(..., description="Workspace scope (must start with ws_)")):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    sources = load_site_sources(ws)
    pages = load_site_pages(ws)
    phrases = load_site_phrase_index(ws)

    return {
        "ok": True,
        "workspace_id": ws,
        "sources_count": len(sources.get("sources", []) or []),
        "pages_count": len((pages.get("pages", {}) or {})),
        "phrases_count": len((phrases.get("phrases", {}) or {})),
        "paths": {
            "sources": f"backend/server/data/site_sources_{ws}.json",
            "pages": f"backend/server/data/site_pages_{ws}.json",
            "phrase_index": f"backend/server/data/site_phrase_index_{ws}.json",
        },
    }

@router.post("/target_pools/rebuild_all")
def rebuild_all_target_pools(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    results: Dict[str, Any] = {
    "document_registry": None,
    "draft": None,
    "imported": None,
    "live_domain": None,
    "upload": None,
}

    try:
        doc_out = build_document_registry_pool(ws)
        results["document_registry"] = {
            "ok": True,
            "counts": doc_out.get("counts", {}),
            "path": f"backend/server/data/target_pools/document_registry/document_registry_{ws}.json",
        }
    except Exception as e:
        results["document_registry"] = {
            "ok": False,
            "error": str(e)[:200],
        }

    try:
        draft_out = build_draft_target_pool(ws)
        results["draft"] = {
            "ok": True,
            "counts": draft_out.get("counts", {}),
            "path": f"backend/server/data/target_pools/draft/draft_target_pool_{ws}.json",
        }
    except Exception as e:
        results["draft"] = {
            "ok": False,
            "error": str(e)[:200],
        }

    try:
        imported_out = build_imported_target_pool(ws)
        results["imported"] = {
            "ok": True,
            "counts": imported_out.get("counts", {}),
            "path": f"backend/server/data/target_pools/imported/imported_target_pool_{ws}.json",
        }
    except Exception as e:
        results["imported"] = {
            "ok": False,
            "error": str(e)[:200],
        }

    try:
        live_out = build_live_domain_target_pool(ws)
        results["live_domain"] = {
            "ok": True,
            "counts": live_out.get("counts", {}),
            "path": f"backend/server/data/target_pools/live_domain/live_domain_target_pool_{ws}.json",
        }
    except Exception as e:
        results["live_domain"] = {
            "ok": False,
            "error": str(e)[:200],
        }

    try:
        upload_out = build_upload_phrase_pool(ws)
        results["upload"] = {
            "ok": True,
            "counts": {
                "phrase_count": upload_out.get("phrase_count", 0),
            },
            "path": f"backend/server/data/phrase_pools/upload/upload_phrase_pool_{ws}.json",
        }
    except Exception as e:
        results["upload"] = {
            "ok": False,
            "error": str(e)[:200],
        }

    overall_ok = all(v and v.get("ok") for v in results.values())

    return {
        "ok": overall_ok,
        "workspace_id": ws,
        "results": results,
    }


@router.get("/target_pools/active_target_set")
def get_active_target_set(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    fp = _active_target_set_path(ws)
    if not fp.exists():
        return {
            "ok": True,
            "workspace_id": ws,
            "exists": False,
            "active_target_set": {
                "workspace_id": ws,
                "active_document_ids": [],
                "active_draft_ids": [],
                "active_imported_urls": [],
                "active_live_domain_urls": [],
            },
        }

    try:
        obj = json.loads(fp.read_text(encoding="utf-8-sig"))
    except Exception as e:
        return {
            "ok": False,
            "workspace_id": ws,
            "error": "active_target_set_read_failed",
            "detail": str(e)[:200],
        }

    return {
        "ok": True,
        "workspace_id": ws,
        "exists": True,
        "active_target_set": {
            "workspace_id": ws,
            "active_document_ids": obj.get("active_document_ids") or [],
            "active_draft_ids": obj.get("active_draft_ids") or [],
            "active_imported_urls": obj.get("active_imported_urls") or [],
            "active_live_domain_urls": obj.get("active_live_domain_urls") or [],
            "updated_at": obj.get("updated_at"),
        },
    }


@router.post("/target_pools/active_target_set/clear")
def clear_active_target_set(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    fp = _active_target_set_path(ws)
    fp.parent.mkdir(parents=True, exist_ok=True)

    obj = {
        "workspace_id": ws,
        "active_document_ids": [],
        "active_draft_ids": [],
        "active_imported_urls": [],
        "active_live_domain_urls": [],
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "cleared": True,
    }

    fp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "workspace_id": ws,
        "path": str(fp),
        "cleared": True,
        "counts": {
            "active_document_ids": 0,
            "active_draft_ids": 0,
            "active_imported_urls": 0,
            "active_live_domain_urls": 0,
        },
    }

class ConnectDomainPayload(BaseModel):
    domain: str = Field(..., description="Domain entered by the user")
    workspace_id: str | None = Field(None, description="Optional existing workspace_id to connect domain into")



def _workspace_id_from_domain(domain: str) -> str:
    clean = domain.replace(".", "_")
    return f"ws_{clean}"

@router.post("/workspace/connect_domain")
def connect_domain(payload: ConnectDomainPayload):
    domain = _normalize_domain(payload.domain)

    if not domain:
        raise HTTPException(
            status_code=400,
            detail="A valid domain is required.",
        )

    workspace_id = _workspace_id_from_domain(
        domain
    )

    try:

        orchestration_result = enqueue_and_run_website_ingestion_job_v1(
            workspace_id=workspace_id,
            domain=domain if "domain" in locals() else "",
            payload={
                "route": "/api/site/workspace/connect_domain",
            },
        )
    except Exception as e:
        orchestration_result = {
            "ok": False,
            "error": f"website_orchestration_failed:{str(e)[:160]}",
        }

return {"ok": False, "error": "invalid_domain"}

    # LC_CONNECT_DOMAIN_EXISTING_WORKSPACE_6_3
    requested_workspace_id = str(payload.workspace_id or "").strip()
    workspace_id = requested_workspace_id or _workspace_id_from_domain(domain)

    data_dir = Path("backend/server/data")
    data_dir.mkdir(parents=True, exist_ok=True)

    ws_meta_path = data_dir / f"workspace_{workspace_id}.json"

    created = False

    if not ws_meta_path.exists():
        obj = {
            "workspace_id": workspace_id,
            "domain": domain,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        ws_meta_path.write_text(
            json.dumps(obj, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        created = True

    sitemap_candidates = [
        f"https://{domain}/sitemap.xml",
        f"https://{domain}/sitemap_index.xml",
        f"https://{domain}/sitemap-index.xml",
        f"https://{domain}/wp-sitemap.xml",
        f"https://www.{domain}/sitemap.xml",
        f"https://www.{domain}/sitemap_index.xml",
        f"https://www.{domain}/sitemap-index.xml",
        f"https://www.{domain}/wp-sitemap.xml",
    ]

    # Also discover sitemap URLs declared inside robots.txt.
    for robots_url in [f"https://{domain}/robots.txt", f"https://www.{domain}/robots.txt"]:
        try:
            code, content, ct = _http_get(robots_url)
            if code < 400 and content:
                robots_txt = content.decode("utf-8", errors="replace")
                for line in robots_txt.splitlines():
                    line = line.strip()
                    if line.lower().startswith("sitemap:"):
                        sm = line.split(":", 1)[1].strip()
                        if sm and sm not in sitemap_candidates:
                            sitemap_candidates.append(sm)
        except Exception:
            pass

    all_urls = []
    sitemap_errors = []
    sitemap_used = None

    for sitemap_url in sitemap_candidates:
        urls, errors = _fetch_and_expand_sitemaps(sitemap_url)
        sitemap_errors.extend(errors or [])

        if urls:
            all_urls = [str(u).strip() for u in urls if str(u).strip()]
            sitemap_used = sitemap_url
            break

    if not all_urls:
        return {
            "ok": False,
            "workspace_id": workspace_id,
            "domain": domain,
            "created": created,
            "error": "no_sitemap_urls_found",
            "sitemap_candidates": sitemap_candidates,
            "sitemap_errors": sitemap_errors[:20],
        }

    rejected_urls = []
    high_priority_urls = []
    normal_priority_urls = []
    low_priority_urls = []
    seen_page_urls = set()

    for raw_url in all_urls:
        url = str(raw_url or "").strip()
        if not url:
            continue

        if url in seen_page_urls:
            rejected_urls.append({"url": url, "reason": "duplicate_url"})
            continue

        seen_page_urls.add(url)

        parsed = urlparse(url)
        path = parsed.path or ""
        path_lower = path.lower().strip()
        lower_url = url.lower()
        host = _domain_from_url(url)

        reason = ""

        if domain not in host:
            reason = "non_domain_url"
        elif path_lower in {"", "/"}:
            reason = "homepage_root_url"
        elif re.search(r"\.(jpg|jpeg|png|gif|webp|svg|ico|pdf|doc|docx|ppt|pptx|xls|xlsx|zip|rar|7z|tar|gz|mp3|mp4|m4a|wav|mov|avi|webm|woff|woff2|ttf|otf|eot)(\?|$)", lower_url):
            reason = "media_file_or_download"
        elif "images." in lower_url or "/images/" in lower_url or "/uploads/" in lower_url:
            reason = "image_or_upload_asset"
        elif re.search(r"/(community|forums?|profile|member|user|users|groups?)(/|$)", path_lower):
            reason = "community_forum_profile_page"
        elif re.search(r"/(news|deals?|offers?|coupon|coupons|promo|promotions?)(/|$)", path_lower):
            reason = "news_deal_promo_page"
        elif re.search(r"(giveaway|contest|sweepstakes|rules|terms-of-entry)", path_lower):
            reason = "giveaway_contest_rules_page"
        elif re.search(r"/search(/|$)|[?&](s|q|query|search)=", lower_url):
            reason = "search_page"
        elif re.search(r"/(tag|tags|category|categories|archive|archives)(/|$)", path_lower):
            reason = "tag_category_archive_page"
        elif re.search(r"/author|/authors|/byline|/contributors?", path_lower):
            reason = "author_contributor_page"
        elif re.search(r"/page/\d+/?$", path_lower) or re.search(r"[?&](paged|page)=\d+", lower_url):
            reason = "pagination_page"
        elif re.search(r"/(login|logout|register|signup|sign-in|account|my-account|cart|checkout|orders|wishlist)(/|$)", path_lower):
            reason = "account_commerce_page"
        elif re.search(r"/(api|graphql|rest|ajax|admin|wp-admin|wp-json)(/|$)", path_lower) or "xmlrpc.php" in path_lower:
            reason = "api_admin_system_url"
        elif re.search(r"/(feed|rss|atom)(/|$)", path_lower) or path_lower.endswith((".rss", ".atom")):
            reason = "feed_rss_atom_url"
        elif re.search(r"/(privacy|privacy-policy|terms|terms-and-conditions|cookie|cookie-policy|contact|about|faq|help|support|advertise|newsletter|disclaimer|editorial-policy|affiliate-disclosure)(/|$)", path_lower):
            reason = "legal_support_or_brand_page"
        elif re.search(r"[?&](utm_|gclid|fbclid|msclkid|yclid|_ga|_gl|ref|source|campaign|adgroup|adid|affiliate|aff|srsltid)=", lower_url):
            reason = "tracking_query_url"
        elif re.search(r"(campaign|landing|black-friday|cyber-monday|prime-day|sale|discount)", path_lower):
            reason = "campaign_promo_page"
        else:
            slug = path_lower.strip("/").split("/")[-1] if path_lower.strip("/") else ""
            slug_words = [w for w in re.split(r"[-_/]+", slug) if len(w) >= 3]
            path_parts = [p for p in path_lower.strip("/").split("/") if p]

            article_structure_hint = (
                len(slug_words) >= 3
                or path_lower.endswith(".aspx")
                or re.search(r"/(article|articles|guide|guides|how-to|howto|learn|resources|blog|blogs|post|posts)(/|$)", path_lower)
            )

            if path_lower.count("/") <= 1 and not article_structure_hint:
                reason = "weak_shallow_hub"

            elif len(slug_words) < 2 and not article_structure_hint:
                reason = "thin_or_non_article_slug"

        # Full 20-rule URL cleaner applied before seed_urls/site_pages/active set.
        lower_url = str(url or "").lower()
        path_lower = (urlparse(url).path or "").lower().strip()

        if reason:
            rejected_urls.append({"url": url, "reason": reason})
            continue

        # 1. homepage/root
        if path_lower in {"", "/"}:
            rejected_urls.append({"url": url, "reason": "homepage_root"})
            continue

        # 2 + 3. images/media/CDN + files/downloads
        if re.search(r"\.(jpg|jpeg|png|gif|webp|svg|ico|pdf|doc|docx|ppt|pptx|xls|xlsx|zip|rar|7z|tar|gz|mp3|mp4|m4a|wav|mov|avi|webm|woff|woff2|ttf|otf|eot)(\?|$)", lower_url):
            rejected_urls.append({"url": url, "reason": "media_file_or_download"})
            continue

        if "images." in lower_url or "/images/" in lower_url or "/uploads/" in lower_url or "cdn." in lower_url or "/gcms/" in lower_url:
            rejected_urls.append({"url": url, "reason": "image_media_cdn"})
            continue

        # 4. community/forum/profile
        if re.search(r"/(community|forums?|profile|member|user|users|groups?)(/|$)", path_lower):
            rejected_urls.append({"url": url, "reason": "community_forum_profile"})
            continue

        # 5. news/deals/promos
        if re.search(r"/(news|deals?|offers?|coupon|coupons|promo|promotions?)(/|$)", path_lower):
            rejected_urls.append({"url": url, "reason": "news_deals_promos"})
            continue

        # 6. giveaway/rules/contest
        if re.search(r"(giveaway|contest|sweepstakes|rules|terms-of-entry)", path_lower):
            rejected_urls.append({"url": url, "reason": "giveaway_rules_contest"})
            continue

        # 7. search pages
        if re.search(r"/search(/|$)|[?&](s|q|query|search)=", lower_url):
            rejected_urls.append({"url": url, "reason": "search_page"})
            continue

        # 8. tag/category/archive
        if re.search(r"/(tag|tags|category|categories|archive|archives)(/|$)", path_lower):
            rejected_urls.append({"url": url, "reason": "tag_category_archive"})
            continue

        # 9. author pages
        if re.search(r"/(author|authors|byline|contributors?)(/|$)", path_lower):
            rejected_urls.append({"url": url, "reason": "author_page"})
            continue

        # 10. pagination
        if re.search(r"/page/\d+/?$", path_lower) or re.search(r"[?&](paged|page)=\d+", lower_url):
            rejected_urls.append({"url": url, "reason": "pagination"})
            continue

        # 11. login/account/cart/checkout
        if re.search(r"/(login|logout|register|signup|sign-in|account|my-account|cart|checkout|orders|wishlist)(/|$)", path_lower):
            rejected_urls.append({"url": url, "reason": "login_account_cart_checkout"})
            continue

        # 12. api/wp-json/admin/system
        if re.search(r"/(api|graphql|rest|ajax|admin|wp-admin|wp-json)(/|$)", path_lower) or "xmlrpc.php" in path_lower:
            rejected_urls.append({"url": url, "reason": "api_admin_system"})
            continue

        # 13. feed/RSS/Atom
        if re.search(r"/(feed|rss|atom)/?$", path_lower) or path_lower.endswith((".rss", ".atom")):
            rejected_urls.append({"url": url, "reason": "feed_rss_atom"})
            continue

        # 14. privacy/terms/contact/about
        if re.search(r"/(privacy|privacy-policy|terms|terms-and-conditions|cookie|cookie-policy|contact|about|faq|help|support|advertise|newsletter|disclaimer|editorial-policy|affiliate-disclosure)(/|$)", path_lower):
            rejected_urls.append({"url": url, "reason": "privacy_terms_contact_about"})
            continue

        # 15. tracking/query URLs
        if re.search(r"[?&](utm_|gclid|fbclid|msclkid|yclid|_ga|_gl|ref|source|campaign|adgroup|adid|affiliate|aff|srsltid)=", lower_url):
            rejected_urls.append({"url": url, "reason": "tracking_query_url"})
            continue

        # 16. calculator-generated result pages
        if re.search(r"/(due-date-calculator|ovulation-calculator|pregnancy-calculator)/result/", path_lower):
            rejected_urls.append({"url": url, "reason": "calculator_generated_result_page"})
            continue

        # 17. old campaign/promo pages
        if re.search(r"(campaign|landing|black-friday|cyber-monday|prime-day|sale|discount)", path_lower):
            rejected_urls.append({"url": url, "reason": "old_campaign_promo"})
            continue

        # 18. weak shallow hubs
        topic_hint = re.search(
            r"(pregnancy|fertility|ovulation|trimester|labor|delivery|baby|newborn|toddler|symptoms|health|nutrition|breastfeeding|postpartum|getting-pregnant)",
            path_lower,
        )

        if path_lower.count("/") <= 1 and not topic_hint:
            rejected_urls.append({"url": url, "reason": "weak_shallow_hub"})
            continue

        # 19. thin/no article slug
        slug = path_lower.strip("/").split("/")[-1] if path_lower.strip("/") else ""
        slug_words = [w for w in re.split(r"[-_/]+", slug) if len(w) >= 3]

        if len(slug_words) < 2 and not topic_hint:
            rejected_urls.append({"url": url, "reason": "thin_no_article_slug"})
            continue

        # 20. keep only usable content pages from here onward.

        # 4-way production classification.
        if re.search(r"/(article|articles|guide|guides|how-to|howto|pregnancy|getting-pregnant|baby|toddler|labor-and-delivery|fertility|ovulation|symptoms-and-solutions|your-health|diet)(/|$)", path_lower):
            high_priority_urls.append(url)
        elif re.search(r"(pregnancy|fertility|ovulation|trimester|labor|delivery|baby|newborn|toddler|symptoms|health|nutrition|breastfeeding|postpartum)", path_lower):
            high_priority_urls.append(url)
        elif path_lower.count("/") <= 2:
            low_priority_urls.append(url)
        else:
            normal_priority_urls.append(url)

    # Use all cleaned/qualified URLs after URL cleaning.
    # Do not cap at 2,000; large domains and batch auto-linking need the full cleaned set.
    seed_urls = high_priority_urls + normal_priority_urls + low_priority_urls

    save_site_sources(workspace_id, {
        "workspace_id": workspace_id,
        "domain": domain,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "sources": [
            {
                "source_type": "connected_domain",
                "domain": domain,
                "sitemap_url": sitemap_used,
                "sitemap_urls": all_urls,
                "sitemap_urls_count": len(all_urls),
                "rejected_urls_count": len(rejected_urls),
                "high_priority_urls_count": len(high_priority_urls),
                "normal_priority_urls_count": len(normal_priority_urls),
                "low_priority_urls_count": len(low_priority_urls),
                "seed_urls_count": len(seed_urls),
            }
        ],
        "errors": sitemap_errors[:100],
        "rejected_urls_sample": rejected_urls[:200],
    })

    pages = {}
    now = datetime.now(timezone.utc).isoformat()

    for url in seed_urls:
        path = urlparse(url).path or ""
        slug = path.strip("/").split("/")[-1] if path.strip("/") else url
        title = re.sub(r"[-_]+", " ", slug).strip().title() if slug else url

        pages[url] = {
            "url": url,
            "domain": domain,
            "title": title,
            "h1": title,
            "description": "",
            "headings": [],
            "body_text": "",
            "source": "sitemap_seed",
            "source_type": "connected_domain_seed",
            "ingested_at": now,
            "metadata": {
                "seed_only": True,
                "selection_reason": "generic_structure_cleaner_v2_priority_seed"
            }
        }

    save_site_pages(workspace_id, {
        "workspace_id": workspace_id,
        "domain": domain,
        "updated_at": now,
        "pages": pages,
    })

    active_fp = _active_target_set_path(workspace_id)
    active_fp.parent.mkdir(parents=True, exist_ok=True)

    active_obj = {
        "workspace_id": workspace_id,
        "active_document_ids": [],
        "active_draft_ids": [],
        "active_imported_urls": [],
        "active_live_domain_urls": seed_urls,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    if active_fp.exists():
        try:
            old_obj = json.loads(active_fp.read_text(encoding="utf-8"))
            if isinstance(old_obj, dict):
                active_obj["active_document_ids"] = old_obj.get("active_document_ids") or []
                active_obj["active_draft_ids"] = old_obj.get("active_draft_ids") or []
                active_obj["active_imported_urls"] = old_obj.get("active_imported_urls") or []
        except Exception:
            pass

    active_fp.write_text(
        json.dumps(active_obj, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # LC_CONNECT_DOMAIN_EXISTING_WORKSPACE_6_3
    try:
        workspace_profile_dir = Path("backend/server/data/workspaces") / workspace_id
        workspace_profile_dir.mkdir(parents=True, exist_ok=True)
        workspace_profile_path = workspace_profile_dir / "workspace_profile.json"

        profile = {}
        if workspace_profile_path.exists():
            try:
                profile = json.loads(workspace_profile_path.read_text(encoding="utf-8"))
                if not isinstance(profile, dict):
                    profile = {}
            except Exception:
                profile = {}

        now_profile = datetime.now(timezone.utc).isoformat()

        profile["workspace_id"] = workspace_id
        profile["workspace_name"] = profile.get("workspace_name") or workspace_id.replace("ws_", "").replace("_", " ").title()
        profile["workspace_mode"] = profile.get("workspace_mode") or "domain"
        profile["domain"] = domain
        profile["connection_status"] = "connected"
        profile["connected_at"] = profile.get("connected_at") or now_profile
        profile["updated_at"] = now_profile

        if not profile.get("source_type"):
            profile["source_type"] = "domain"

        if "site_url" not in profile:
            profile["site_url"] = ""

        workspace_profile_path.write_text(
            json.dumps(profile, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as profile_err:
        print("[connect_domain] workspace profile update failed:", profile_err)

    try:
        live_out = build_live_domain_target_pool(workspace_id)
        live_counts = live_out.get("counts", {}) if isinstance(live_out, dict) else {}

        cluster_out = build_workspace_topic_clusters(workspace_id)
        cluster_counts = {
            "cluster_count": (
                cluster_out.get("cluster_count")
                or cluster_out.get("data", {}).get("cluster_count")
                or 0
            )
        } if isinstance(cluster_out, dict) else {"cluster_count": 0}

        url_pool_out = initialize_url_pool_from_current_active(workspace_id)
        url_pool_stats = get_url_pool_stats(workspace_id)
    except Exception as e:
        return {
            "ok": False,
            "workspace_id": workspace_id,
            "domain": domain,
            "created": created,
            "error": "live_domain_target_pool_build_failed",
            "detail": str(e)[:300],
            "sitemap_url_count": len(all_urls),
            "seed_urls_count": len(seed_urls),
        }

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "domain": domain,
        "created": created,
        "workspace_file": str(ws_meta_path),
        "sitemap_used": sitemap_used,
        "sitemap_url_count": len(all_urls),
        "seed_urls_count": len(seed_urls),
        "active_live_domain_urls_count": len(active_obj["active_live_domain_urls"]),
        "live_domain_counts": live_counts,
        "topic_cluster_counts": cluster_counts,
        "url_pool": url_pool_out,
        "url_pool_stats": url_pool_stats,
    }


# -------------------------
# URL Pool Manager
# -------------------------
@router.get("/url_pool/stats")
def url_pool_stats(workspace_id: str = Query(..., description="Workspace scope (must start with ws_)")):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err
    return get_url_pool_stats(ws)


@router.post("/url_pool/initialize")
def url_pool_initialize(workspace_id: str = Query(..., description="Workspace scope (must start with ws_)")):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err
    return initialize_url_pool_from_current_active(ws)


@router.get("/url_pool/active")
def url_pool_active(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    urls = load_active_urls(ws)
    return {
        "ok": True,
        "workspace_id": ws,
        "total": len(urls),
        "limit": limit,
        "offset": offset,
        "items": urls[offset: offset + limit],
    }


@router.get("/url_pool/reserve")
def url_pool_reserve(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    urls = load_reserve_urls(ws)
    return {
        "ok": True,
        "workspace_id": ws,
        "total": len(urls),
        "limit": limit,
        "offset": offset,
        "items": urls[offset: offset + limit],
    }



@router.get("/url_pool/classify")
def url_pool_classify(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    pool: str = Query("reserve", description="active or reserve"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    if pool == "active":
        urls = load_active_urls(ws)
    else:
        urls = load_reserve_urls(ws)

    return classify_url_list(ws, urls, limit=limit, offset=offset)


@router.post("/url_pool/promote")
def url_pool_promote(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    url: str = Query(..., description="URL to promote from reserve to active"),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err
    return promote_url(ws, url)


@router.post("/url_pool/demote")
def url_pool_demote(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    url: str = Query(..., description="URL to demote from active to reserve"),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err
    return demote_url(ws, url)


# -------------------------
# Target Pools: Live Domain
# -------------------------
@router.get("/target_pools/live_domain/preview")
def preview_live_domain_target_pool(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0, le=200000),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    fp = Path(f"backend/server/data/target_pools/live_domain/live_domain_target_pool_{ws}.json")
    if not fp.exists():
        return {"ok": False, "workspace_id": ws, "error": "pool_file_missing"}

    obj = json.loads(fp.read_text(encoding="utf-8"))
    items = obj.get("items") or []
    if not isinstance(items, list):
        items = []

    slice_ = items[offset : offset + limit]

    return {
        "ok": True,
        "workspace_id": ws,
        "pool": "live_domain",
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "items": slice_,
    }


@router.post("/target_pools/live_domain/rebuild")
def rebuild_live_domain_target_pool(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    try:
        out = build_live_domain_target_pool(ws)
        return {
            "ok": True,
            "workspace_id": ws,
            "pool": "live_domain",
            "counts": out.get("counts", {}),
            "path": f"backend/server/data/target_pools/live_domain/live_domain_target_pool_{ws}.json",
        }
    except FileNotFoundError as e:
        return {"ok": False, "workspace_id": ws, "error": "missing_required_source_file", "detail": str(e)}
    except Exception as e:
        return {"ok": False, "workspace_id": ws, "error": "rebuild_failed", "detail": str(e)[:200]}


# -------------------------
# Target Pools: Imported
# -------------------------
@router.post("/target_pools/imported/rebuild")
def rebuild_imported_target_pool(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    placeholder_path: str = Query("/drafts", description="Where to generate placeholder URLs for topic-only rows"),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    try:
        out = build_imported_target_pool(ws, placeholder_path=placeholder_path)
        return {
            "ok": True,
            "workspace_id": ws,
            "pool": "imported",
            "counts": out.get("counts", {}),
            "merge_all": out.get("merge_all"),
            "sources_used": out.get("sources_used"),
            "per_source_counts": out.get("per_source_counts"),
            "placeholder_path": out.get("placeholder_path"),
            "path": f"backend/server/data/target_pools/imported/imported_target_pool_{ws}.json",
        }
    except FileNotFoundError as e:
        return {"ok": False, "workspace_id": ws, "error": "missing_import_input_file", "detail": str(e)}
    except Exception as e:
        return {"ok": False, "workspace_id": ws, "error": "rebuild_failed", "detail": str(e)[:200]}


@router.get("/target_pools/imported/preview")
def preview_imported_target_pool(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0, le=200000),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    fp = Path(f"backend/server/data/target_pools/imported/imported_target_pool_{ws}.json")
    if not fp.exists():
        return {"ok": False, "workspace_id": ws, "error": "pool_file_missing"}

    obj = json.loads(fp.read_text(encoding="utf-8"))
    items = obj.get("items") or []
    if not isinstance(items, list):
        items = []

    slice_ = items[offset : offset + limit]

    return {
        "ok": True,
        "workspace_id": ws,
        "pool": "imported",
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "items": slice_,
    }


# -------------------------
# Target Pools: Document Registry
# -------------------------
@router.get("/target_pools/document_registry/preview")
def preview_document_registry_pool(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0, le=200000),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    data = build_document_registry_pool(ws)

    items = data.get("items") or []
    if not isinstance(items, list):
        items = []

    slice_ = items[offset : offset + limit]

    return {
        "ok": True,
        "workspace_id": ws,
        "pool": "document_registry",
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "items": slice_,
    }


@router.post("/target_pools/document_registry/rebuild")
def rebuild_document_registry_pool(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    try:
        out = build_document_registry_pool(ws)
        return {
            "ok": True,
            "workspace_id": ws,
            "pool": "document_registry",
            "counts": out.get("counts", {}),
            "path": f"backend/server/data/target_pools/document_registry/document_registry_{ws}.json",
        }
    except FileNotFoundError as e:
        return {"ok": False, "workspace_id": ws, "error": "missing_uploads_index", "detail": str(e)}
    except Exception as e:
        return {"ok": False, "workspace_id": ws, "error": "rebuild_failed", "detail": str(e)[:200]}


# -------------------------
# Target Pools: Draft
# -------------------------
@router.post("/target_pools/draft/rebuild")
def rebuild_draft_target_pool(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    try:
        out = build_draft_target_pool(ws)
        return {
            "ok": True,
            "workspace_id": ws,
            "pool": "draft",
            "counts": out.get("counts", {}),
            "source": out.get("source"),
            "path": f"backend/server/data/target_pools/draft/draft_target_pool_{ws}.json",
        }
    except FileNotFoundError as e:
        return {"ok": False, "workspace_id": ws, "error": "missing_draft_input_file", "detail": str(e)}
    except Exception as e:
        return {"ok": False, "workspace_id": ws, "error": "rebuild_failed", "detail": str(e)[:200]}


@router.get("/target_pools/draft/preview")
def preview_draft_target_pool(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0, le=200000),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    fp = Path(f"backend/server/data/target_pools/draft/draft_target_pool_{ws}.json")
    if not fp.exists():
        return {"ok": False, "workspace_id": ws, "error": "pool_file_missing"}

    obj = json.loads(fp.read_text(encoding="utf-8"))
    items = obj.get("items") or []
    if not isinstance(items, list):
        items = []

    slice_ = items[offset : offset + limit]

    return {
        "ok": True,
        "workspace_id": ws,
        "pool": "draft",
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "items": slice_,
    }

# -------------------------
# Target Pools: Upload
# -------------------------
@router.get("/target_pools/upload/preview")
def preview_upload_target_pool(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0, le=200000),
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    fp = Path(f"backend/server/data/phrase_pools/upload/upload_phrase_pool_{ws}.json")
    if not fp.exists():
        return {"ok": False, "workspace_id": ws, "error": "pool_file_missing"}

    obj = json.loads(fp.read_text(encoding="utf-8"))
    phrases = obj.get("phrases") or {}
    if not isinstance(phrases, dict):
        phrases = {}

    phrase_keys = list(phrases.keys())
    slice_keys = phrase_keys[offset : offset + limit]

    items = []
    for k in slice_keys:
        rec = phrases.get(k)
        if isinstance(rec, dict):
            items.append(rec)

    return {
        "ok": True,
        "workspace_id": ws,
        "pool": "upload",
        "total": len(phrases),
        "limit": limit,
        "offset": offset,
        "items": items,
        "phrase_count": int(obj.get("phrase_count", len(phrases))),
    }


@router.post("/target_pools/active_target_set/save")
def save_active_target_set(payload: ActiveTargetSetPayload):
    ws, err = _ws_or_error(payload.workspace_id)
    if err:
        return err

    fp = _active_target_set_path(ws)
    fp.parent.mkdir(parents=True, exist_ok=True)

    existing = {
        "workspace_id": ws,
        "active_document_ids": [],
        "active_draft_ids": [],
        "active_imported_urls": [],
        "active_live_domain_urls": [],
    }

    if fp.exists():
        try:
            raw = json.loads(fp.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                existing["active_document_ids"] = raw.get("active_document_ids") or []
                existing["active_draft_ids"] = raw.get("active_draft_ids") or []
                existing["active_imported_urls"] = raw.get("active_imported_urls") or []
                existing["active_live_domain_urls"] = raw.get("active_live_domain_urls") or []
        except Exception:
            pass

    def clean_list(value):
        out = []
        seen = set()

        for x in (value or []):
            s = str(x).strip()
            if not s:
                continue
            if s in seen:
                continue
            out.append(s)
            seen.add(s)

        return out

    obj = {
        "workspace_id": ws,
        "active_document_ids": clean_list(payload.active_document_ids) if payload.active_document_ids is not None else clean_list(existing["active_document_ids"]),
        "active_draft_ids": clean_list(payload.active_draft_ids) if payload.active_draft_ids is not None else clean_list(existing["active_draft_ids"]),
        "active_imported_urls": clean_list(payload.active_imported_urls) if payload.active_imported_urls is not None else clean_list(existing["active_imported_urls"]),
        "active_live_domain_urls": clean_list(payload.active_live_domain_urls) if payload.active_live_domain_urls is not None else clean_list(existing["active_live_domain_urls"]),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    fp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "workspace_id": ws,
        "path": str(fp),
        "counts": {
            "active_document_ids": len(obj["active_document_ids"]),
            "active_draft_ids": len(obj["active_draft_ids"]),
            "active_imported_urls": len(obj["active_imported_urls"]),
            "active_live_domain_urls": len(obj["active_live_domain_urls"]),
        },
    }


@router.get("/debug/module_paths")
def debug_module_paths():
    import backend.server.routes.site_reader as sr
    import backend.server.pools.target_pools.document_registry_pool as dr

    return {
        "ok": True,
        "site_reader_file": getattr(sr, "__file__", ""),
        "document_registry_pool_file": getattr(dr, "__file__", ""),
    }


# ------------------------------------------------------------
# Draft store endpoints (existing)
# ------------------------------------------------------------
@router.get("/draft/state")
def draft_state(workspace_id: str = Query(..., description="Workspace scope (must start with ws_)")):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    items = load_draft_items_ws(ws)
    meta = load_draft_meta_ws(ws)

    return {
        "ok": True,
        "workspace_id": ws,
        "count": len(items) if isinstance(items, list) else 0,
        "last_updated_at_utc": meta.get("last_updated_at_utc"),
        "source": meta.get("source"),
        "last_added": meta.get("last_added"),
        "paths": {
            "items": f"backend/server/data/draft_topics_{ws}.json",
            "meta": f"backend/server/data/draft_topics_meta_{ws}.json",
        },
    }


class DraftItem(BaseModel):
    url: str = Field(..., description="Planned URL (future or staging)")
    title: str = Field("", description="Planned page title")
    h1: str = Field("", description="Optional H1")
    h2: list[str] = Field(default_factory=list)
    h3: list[str] = Field(default_factory=list)
    body_text: str = Field("", description="Optional summary/body text")


class DraftImportRequest(BaseModel):
    items: list[DraftItem] = Field(default_factory=list)
    source: str = Field("manual", description="manual/csv/json")


@router.post("/draft/import")
def draft_import(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    payload: DraftImportRequest | None = None,
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err
    if payload is None:
        return {"ok": False, "workspace_id": ws, "error": "missing_payload"}

    seen: set[str] = set()
    out: list[dict] = []

    for it in (payload.items or []):
        u = (it.url or "").strip()
        if not u:
            continue
        if u in seen:
            continue
        seen.add(u)

        out.append(
            {
                "url": u,
                "title": (it.title or "").strip(),
                "h1": (it.h1 or "").strip(),
                "h2": [str(x).strip() for x in (it.h2 or []) if str(x).strip()],
                "h3": [str(x).strip() for x in (it.h3 or []) if str(x).strip()],
                "body_text": (it.body_text or "").strip(),
            }
        )

    save_draft_items_ws(ws, out)

    meta = {
        "last_updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": (payload.source or "manual"),
        "last_added": len(out),
    }
    save_draft_meta_ws(ws, meta)

    return {
        "ok": True,
        "workspace_id": ws,
        "count": len(out),
        **meta,
        "paths": {
            "items": f"backend/server/data/draft_topics_{ws}.json",
            "meta": f"backend/server/data/draft_topics_meta_{ws}.json",
        },
    }


# =========================
# Highlight Test
# =========================
class HighlightTestRequest(BaseModel):
    text: str = Field(..., description="Raw document text to test phrase detection")


@router.post("/highlight_test")
def site_highlight_test(
    workspace_id: str = Query(..., description="Workspace scope (must start with ws_)"),
    payload: HighlightTestRequest | None = None,
):
    ws, err = _ws_or_error(workspace_id)
    if err:
        return err

    if payload is None:
        return {"ok": False, "workspace_id": ws, "error": "missing_payload"}

    text = payload.text or ""
    if not text.strip():
        return {"ok": True, "workspace_id": ws, "matches": []}

    phrase_index = load_site_phrase_index(ws)
    phrases = phrase_index.get("phrases", {})
    if not isinstance(phrases, dict):
        phrases = {}

    hay = " " + re.sub(r"\s+", " ", text.lower()) + " "

    hits: list[dict] = []
    for norm, rec in phrases.items():
        n = (norm or "").strip().lower()
        if not n:
            continue
        pattern = r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])"
        count = len(re.findall(pattern, hay))
        if count > 0:
            hits.append(
                {
                    "phrase": (rec.get("phrase") if isinstance(rec, dict) else None) or n,
                    "norm": n,
                    "bucket": rec.get("bucket") if isinstance(rec, dict) else None,
                    "type": rec.get("type") if isinstance(rec, dict) else None,
                    "confidence": rec.get("confidence") if isinstance(rec, dict) else None,
                    "count": count,
                }
            )

    hits.sort(
        key=lambda x: (
            _bucket_rank(x.get("bucket")),
            -len(str(x.get("norm", "")).split()),
            -int(x.get("count", 0) or 0),
            -float(x.get("confidence", 0.0) or 0.0),
        )
    )

    hay_low = text.lower()
    kept: list[dict] = []
    occupied: list[tuple[int, int]] = []

    def _overlaps(a: tuple[int, int], b: tuple[int, int]) -> bool:
        return not (a[1] <= b[0] or b[1] <= a[0])

    for item in hits:
        n = (item.get("norm") or "").strip().lower()
        if not n:
            continue
        pattern = r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])"
        spans = [(m.start(), m.end()) for m in re.finditer(pattern, hay_low)]
        if not spans:
            continue

        accepted_any = False
        for sp in spans:
            if all(not _overlaps(sp, occ) for occ in occupied):
                occupied.append(sp)
                accepted_any = True

        if accepted_any:
            kept.append(item)

    kept.sort(
        key=lambda x: (
            _bucket_rank(x.get("bucket")),
            -int(x.get("count", 0) or 0),
            -float(x.get("confidence", 0.0) or 0.0),
            -len(str(x.get("norm", "")).split()),
        )
    )

    return {"ok": True, "workspace_id": ws, "matches": kept}


# NOTE: You truncated the file in your paste at this point previously.
# If your original file continues with /connect, /ingest_imported_urls, /sync_test_one, /ingest_one, /phrases/list,
# keep those sections as-is from your current working copy.
