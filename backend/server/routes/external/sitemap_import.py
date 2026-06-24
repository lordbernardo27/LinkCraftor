from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException

import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from backend.server.routes.external.shared import (
    AUTO_PATH,
    AUDIT_PATH,
    IMPORT_RUNS_INDEX_PATH,
    SNAPSHOT_DIR,
)
from backend.server.routes.external.runtime import (
    _normalize_url,
    _is_blocked,
    _safe_read_list,
    _atomic_write_json,
)
from backend.server.routes.external.import_runs import _audit

router = APIRouter(tags=["external-sitemap-import-runtime"])


# ============================================================
# Migrated sitemap helper layer copied from legacy external.py

def _get_source_config(source_label: str) -> Dict[str, Any]:
    data = _read_sources()
    src = (data.get("sources") or {}).get(source_label)
    return src if isinstance(src, dict) else {}

# ============================================================

def _new_import_run_id(prefix: str = "run") -> str:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}_{random.randint(100000, 999999)}"


def _append_import_run_index(entry: Dict[str, Any], max_keep: Optional[int] = None) -> None:

    """
    Append a run entry into import_runs_index.json.
    If max_keep is None => do not trim (unlimited).
    """
    _ensure_data_dir()

    raw = _safe_read_json(IMPORT_RUNS_INDEX_PATH)
    if not isinstance(raw, dict):
        raw = {}

    runs = raw.get("runs")
    if not isinstance(runs, list):
        runs = raw.get("items")
    if not isinstance(runs, list):
        runs = []

    runs.insert(0, entry)

   # No cap — keep full history
# (max_keep ignored intentionally)


    raw["runs"] = runs
    raw["items"] = runs
    _atomic_write_json(IMPORT_RUNS_INDEX_PATH, raw)


def _http_get_text(url: str, timeout_sec: int = 15) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "LinkCraftorControlTower/1.0 (+owner.linkcraftor.com)",
            "Accept": "text/xml,application/xml,text/plain,*/*",
            "Accept-Encoding": "gzip",
        },
        method="GET",
    )

    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        raw = resp.read()
        try:
            enc = (resp.headers.get("Content-Encoding") or "").lower().strip()
        except Exception:
            enc = ""

        is_gz = ("gzip" in enc) or url.lower().endswith(".gz")
        if is_gz:
            try:
                raw = gzip.decompress(raw)
            except Exception:
                try:
                    raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
                except Exception:
                    pass

        return raw.decode("utf-8", errors="ignore")


def _discover_sitemaps_from_robots(domain: str) -> Dict[str, Any]:
    robots_url = f"https://{domain}/robots.txt"
    text = ""
    method_used = "robots_https"

    try:
        text = _http_get_text(robots_url)
    except Exception:
        robots_url = f"http://{domain}/robots.txt"
        method_used = "robots_http"
        try:
            text = _http_get_text(robots_url)
        except Exception:
            text = ""

    sitemaps: List[str] = []
    if text:
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith("sitemap:"):
                sm = line.split(":", 1)[1].strip()
                if sm:
                    sitemaps.append(sm)

    if not sitemaps:
        method_used = "fallback_common"
        base_https = f"https://{domain}"
        sitemaps = [
            f"{base_https}/sitemap.xml",
            f"{base_https}/sitemap-index.xml",
            f"{base_https}/sitemap_index.xml",
            f"{base_https}/sitemap/sitemap.xml",
            f"{base_https}/sitemaps/sitemap.xml",
            f"{base_https}/sitemap.xml.gz",
            f"{base_https}/sitemap-index.xml.gz",
            f"{base_https}/sitemap_index.xml.gz",
        ]

    seen = set()
    deduped: List[str] = []
    for s in sitemaps:
        if s not in seen:
            seen.add(s)
            deduped.append(s)

    return {"robots_url": robots_url, "method_used": method_used, "sitemaps_found": deduped}


def _extract_loc_urls(xml_text: str) -> List[str]:
    return re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", xml_text, flags=re.IGNORECASE)


def _is_sitemap_index(xml_text: str) -> bool:
    return bool(re.search(r"<\s*sitemapindex\b", xml_text, flags=re.IGNORECASE))


def _is_probably_xml_url(u: str) -> bool:
    u2 = u.lower().split("?", 1)[0].split("#", 1)[0]
    return u2.endswith(".xml") or u2.endswith(".xml.gz") or "sitemap" in u2


def _url_has_blocked_extension(url: str, block_extensions: List[str]) -> bool:
    u = url.lower().split("?", 1)[0].split("#", 1)[0]
    for ext in (block_extensions or []):
        e = (ext or "").lower().strip()
        if not e:
            continue
        if not e.startswith("."):
            e = "." + e
        if u.endswith(e):
            return True
    return False


def _passes_path_filters(url: str, include_paths: List[str], exclude_paths: List[str]) -> bool:
    u = url.lower()
    inc = [p.lower().strip() for p in (include_paths or []) if p and p.strip()]
    exc = [p.lower().strip() for p in (exclude_paths or []) if p and p.strip()]

    if inc and not any(p in u for p in inc):
        return False
    for p in exc:
        if p in u:
            return False
    return True


def _normalize_hosts(domain: Optional[str], allowed_hosts: List[str], sitemap_url: Optional[str]) -> List[str]:
    hosts = [str(h).lower().strip() for h in (allowed_hosts or []) if str(h).strip()]
    if hosts:
        return sorted(set(hosts))

    if domain:
        d = domain.lower().strip()
        d = re.sub(r"^https?://", "", d).strip("/")
        out = {d, "www." + d}
        if d.startswith("www."):
            out.add(d.replace("www.", "", 1))
        return sorted(out)

    if sitemap_url:
        h = _host_of_url(sitemap_url)
        return [h] if h else []

    return []


def _passes_lang_filters(url: str, allow_lang_prefixes: List[str], block_lang_prefixes: List[str]) -> bool:
    try:
        path = (urlparse(url).path or "/")
    except Exception:
        path = "/"

    allow = [p.strip() for p in (allow_lang_prefixes or []) if p and p.strip()]
    block = [p.strip() for p in (block_lang_prefixes or []) if p and p.strip()]

    if allow and not any(path.startswith(p) for p in allow):
        return False
    if block and any(path.startswith(p) for p in block):
        return False
    return True


def _passes_host_scope(url: str, allowed_hosts: List[str], require_host_match: bool) -> bool:
    if not require_host_match:
        return True
    host = _host_of_url(url)
    if not host:
        return False
    allow = set([h.lower().strip() for h in (allowed_hosts or []) if h and str(h).strip()])
    return host in allow


def _write_snapshot_before_commit(run_id: str) -> str:
    _ensure_snapshot_dir()
    snap_path = _snapshot_path(run_id)
    current = _safe_read_list(AUTO_PATH)
    _ensure_data_dir()
    snap_path.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(snap_path)


def _bulk_upsert_auto_authority(
    urls: List[str],
    source_label: str,
    now: str,
    import_run_id: str,
    imported_by: str = "owner_sitemap_import",
    import_reason: str = "authority_sitemap_import",
) -> Dict[str, int]:
    dataset = _safe_read_list(AUTO_PATH)

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []

    # 1) Build an in-memory map of existing rows by normalized URL.
    #    If duplicates exist, MERGE them instead of dropping "later" rows.
    for item in dataset:
        if not isinstance(item, dict):
            continue

        raw = str(item.get("url") or "").strip()
        u = _normalize_url_for_storage(raw, prefer_no_www=True, drop_query=True)
        if not u:
            continue
        item["url"] = u

        if u not in by_url:
            by_url[u] = item
            order.append(u)
            continue

        # MERGE duplicates (same normalized URL) so we don't "lose" better titles/phrases
        existing = by_url[u]

        # keep a non-empty title if either has it
        ex_title = str(existing.get("title") or "").strip()
        new_title = str(item.get("title") or "").strip()
        if (not ex_title) and new_title:
            existing["title"] = new_title

        # keep a non-empty phrase if either has it
        ex_phrase = str(existing.get("phrase") or "").strip()
        new_phrase = str(item.get("phrase") or "").strip()
        if (not ex_phrase) and new_phrase:
            existing["phrase"] = new_phrase

        # keep the best score
        try:
            ex_score = float(existing.get("score", 1.0) or 1.0)
        except Exception:
            ex_score = 1.0
        try:
            new_score = float(item.get("score", 1.0) or 1.0)
        except Exception:
            new_score = 1.0
        existing["score"] = max(ex_score, new_score)

        # merge phrases arrays (dedup)
        ph1 = existing.get("phrases")
        if not isinstance(ph1, list):
            ph1 = []
        ph2 = item.get("phrases")
        if not isinstance(ph2, list):
            ph2 = []
        for p in ph2:
            p = (p or "").strip()
            if p and p not in ph1:
                ph1.append(p)
        existing["phrases"] = ph1

        # merge seen_count + timestamps (best-effort)
        existing["seen_count"] = int(existing.get("seen_count", 0) or 0) + int(item.get("seen_count", 0) or 0)
        existing["first_seen"] = existing.get("first_seen") or item.get("first_seen")
        existing["last_seen"] = max(str(existing.get("last_seen") or ""), str(item.get("last_seen") or ""))

        by_url[u] = existing

    added = 0
    updated = 0

    # 2) Upsert the incoming sitemap URLs.
    for raw_u in urls:
        u = _normalize_url_for_storage(raw_u, prefer_no_www=True, drop_query=True)
        if not u:
            continue
        if _is_blocked(u):
            continue

        ck = _canonical_key_from_url(u)
        score = _authority_quality_score(u, base=1.0)

        if u not in by_url:
            by_url[u] = {
                "key": ck,
                "phrase": "",
                "url": u,
                "title": "",
                "score": score,
                "source": "authority_sitemap",
                "source_label": source_label,
                "seen_count": 1,
                "first_seen": now,
                "last_seen": now,
                "phrases": [],
                "lang": "en",
                "last_event": import_reason,
                "imported_at": now,
                "import_run_id": import_run_id,
                "imported_by": imported_by,
                "import_reason": import_reason,
            }
            order.append(u)
            added += 1
        else:
            existing = by_url[u]
            if ck:
                existing["key"] = ck

            try:
                prev_score = float(existing.get("score", 1.0) or 1.0)
            except Exception:
                prev_score = 1.0
            existing["score"] = max(prev_score, score)

            existing["source"] = existing.get("source") or "authority_sitemap"
            existing["source_label"] = source_label
            existing["seen_count"] = int(existing.get("seen_count", 0) or 0) + 1
            existing["last_seen"] = now
            existing["first_seen"] = existing.get("first_seen") or now
            existing["last_event"] = import_reason

            existing["imported_at"] = now
            existing["import_run_id"] = import_run_id
            existing["imported_by"] = imported_by
            existing["import_reason"] = import_reason

            updated += 1

    out = [by_url[u] for u in order if u in by_url]
    _atomic_write_json(AUTO_PATH, out)
    return {"added": added, "updated": updated}


class SitemapFilters(BaseModel):
    include_paths: List[str] = Field(default_factory=list)
    exclude_paths: List[str] = Field(default_factory=list)
    block_extensions: List[str] = Field(default_factory=lambda: [".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".mp4"])
    block_lang_prefixes: List[str] = Field(default_factory=list)
    allow_lang_prefixes: List[str] = Field(default_factory=list)
    require_host_match: bool = True
    allowed_hosts: List[str] = Field(default_factory=list)


class OwnerSitemapImportRequest(BaseModel):
    source_label: str
    domain: Optional[str] = None
    sitemap_url: Optional[str] = None
    filters: Optional[SitemapFilters] = None
    commit: bool = False



@router.get("/sitemap_import/status")
def sitemap_import_status() -> Dict[str, Any]:
    return {
        "ok": True,
        "router": "external.sitemap_import",
        "routes": [
            "/owner/sitemap/import",
        ],
    }


@router.post("/owner/sitemap/import")
async def owner_sitemap_import(payload: OwnerSitemapImportRequest = Body(...)):
    source_label = (payload.source_label or "").strip()
    if not source_label:
        raise HTTPException(status_code=400, detail="source_label is required")

    src_cfg = _get_source_config(source_label)
    if not src_cfg:
        raise HTTPException(status_code=400, detail=f"Unknown source_label: {source_label}")

    defaults = src_cfg.get("defaults") if isinstance(src_cfg.get("defaults"), dict) else {}

    domain_in = (payload.domain or "").strip()
    sitemap_url = (payload.sitemap_url or "").strip()

    if sitemap_url:
        domain = domain_in
    else:
        domain = domain_in or str(src_cfg.get("domain") or "").strip()

    if not domain and not sitemap_url:
        raise HTTPException(status_code=400, detail="Provide domain OR sitemap_url (or set domain in source config)")
    if domain_in and sitemap_url:
        raise HTTPException(status_code=400, detail="Provide only one: domain OR sitemap_url")

    if domain:
        d = domain.lower()
        d = re.sub(r"^https?://", "", d).strip("/")
        domain = d

    def _list_or_default(v, fallback):
        return v if isinstance(v, list) else fallback

    eff_include = _list_or_default(defaults.get("include_paths"), [])
    eff_exclude = _list_or_default(defaults.get("exclude_paths"), [])
    eff_block_ext = _list_or_default(defaults.get("block_extensions"), [".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".mp4"])
    eff_block_lang = _list_or_default(defaults.get("block_lang_prefixes"), [])
    eff_allow_lang = _list_or_default(defaults.get("allow_lang_prefixes"), [])
    eff_require_host = bool(defaults.get("require_host_match", True))
    eff_allowed_hosts = _list_or_default(defaults.get("allowed_hosts"), [])

    if payload.filters is not None:
        f = payload.filters
        if f.include_paths:
            eff_include = f.include_paths
        if f.exclude_paths:
            eff_exclude = f.exclude_paths
        if f.block_extensions:
            eff_block_ext = f.block_extensions
        if f.block_lang_prefixes:
            eff_block_lang = f.block_lang_prefixes
        if f.allow_lang_prefixes:
            eff_allow_lang = f.allow_lang_prefixes
        eff_require_host = bool(f.require_host_match)
        if f.allowed_hosts:
            eff_allowed_hosts = f.allowed_hosts

    include_paths = [p.strip() for p in (eff_include or []) if p and p.strip()]
    exclude_paths = [p.strip() for p in (eff_exclude or []) if p and p.strip()]
    block_ext = [e.strip().lower() for e in (eff_block_ext or []) if e and e.strip()]
    block_lang = [p.strip() for p in (eff_block_lang or []) if p and p.strip()]
    allow_lang = [p.strip() for p in (eff_allow_lang or []) if p and p.strip()]

    require_host_match = bool(eff_require_host)
    allowed_hosts = _normalize_hosts(domain, eff_allowed_hosts or [], sitemap_url)

    _audit("owner_sitemap_import_request", {
        "source_label": source_label,
        "domain": domain or None,
        "sitemap_url": sitemap_url or None,
        "filters_used": {
            "include_paths": include_paths,
            "exclude_paths": exclude_paths,
            "block_extensions": block_ext,
            "block_lang_prefixes": block_lang,
            "allow_lang_prefixes": allow_lang,
            "require_host_match": require_host_match,
            "allowed_hosts": allowed_hosts,
        },
        "commit": bool(payload.commit),
    })

    if domain:
        discovered = _discover_sitemaps_from_robots(domain)
    else:
        discovered = {"robots_url": None, "method_used": "direct_sitemap_url", "sitemaps_found": [sitemap_url]}

    _audit("owner_sitemap_discovered", {
        "source_label": source_label,
        "method_used": discovered.get("method_used"),
        "sitemaps_found_count": len(discovered.get("sitemaps_found") or []),
    })

    MAX_URLS_RETURN_SAMPLE = 200  # UI sample only (not storage)

    queue: List[str] = list(discovered.get("sitemaps_found") or [])
    seen_sitemaps = set()

    sitemaps_processed = 0
    sitemap_indexes_seen = 0
    child_sitemaps_enqueued = 0

    urls_found_total = 0
    urls_after_filters = 0
    filtered_out = 0
    skipped_blocked = 0
    skipped_ext = 0
    skipped_host = 0
    skipped_lang = 0

    fetch_errors = 0
    fetch_error_samples: List[Dict[str, str]] = []

    accepted_sample: List[str] = []
    accepted_urls_all: List[str] = []
    seen_urls = set()

    while queue:
        sm_url = _normalize_url(queue.pop(0))
        if not sm_url or not sm_url.startswith("http"):
            continue
        if sm_url in seen_sitemaps:
            continue
        seen_sitemaps.add(sm_url)

        try:
            xml = _http_get_text(sm_url, timeout_sec=25)
        except Exception as e:
            fetch_errors += 1
            if len(fetch_error_samples) < 5:
                fetch_error_samples.append({"sitemap_url": sm_url, "error": str(e)})
            _audit("owner_sitemap_fetch_error", {
                "source_label": source_label,
                "sitemap_url": sm_url,
                "error": str(e),
            })
            continue

        sitemaps_processed += 1
        locs = _extract_loc_urls(xml)
        urls_found_total += len(locs)

        if _is_sitemap_index(xml):
            sitemap_indexes_seen += 1
            for child in locs:
                child = _normalize_url(child)
                if not child or not child.startswith("http"):
                    continue
                if child in seen_sitemaps:
                    continue
                if _is_probably_xml_url(child):
                    queue.append(child)
                    child_sitemaps_enqueued += 1
            continue

        for u in locs:
            u = _normalize_url(u)
            if not u or not u.startswith("http"):
                continue
            if u in seen_urls:
                continue
            seen_urls.add(u)

            if not _passes_host_scope(u, allowed_hosts, require_host_match):
                skipped_host += 1
                continue
            if not _passes_lang_filters(u, allow_lang, block_lang):
                skipped_lang += 1
                continue
            if _url_has_blocked_extension(u, block_ext):
                skipped_ext += 1
                continue
            if not _passes_path_filters(u, include_paths, exclude_paths):
                filtered_out += 1
                continue
            if _is_blocked(u):
                skipped_blocked += 1
                continue

            urls_after_filters += 1

            if len(accepted_sample) < MAX_URLS_RETURN_SAMPLE:
                accepted_sample.append(u)

            accepted_urls_all.append(u)

    _audit("owner_sitemap_step4_recursive", {
        "source_label": source_label,
        "sitemaps_processed": sitemaps_processed,
        "urls_found_total": urls_found_total,
        "urls_after_filters": urls_after_filters,
        "filtered_out": filtered_out,
        "skipped_ext": skipped_ext,
        "skipped_blocked": skipped_blocked,
        "skipped_host": skipped_host,
        "skipped_lang": skipped_lang,
        "fetch_errors": fetch_errors,
    })

    auto_added = 0
    auto_updated = 0
    import_run_id: Optional[str] = None
    snapshot_path: Optional[str] = None

    if payload.commit:
        now = datetime.utcnow().isoformat() + "Z"
        import_run_id = _new_import_run_id("auth")

        snapshot_path = _write_snapshot_before_commit(import_run_id)

        stats = _bulk_upsert_auto_authority(
            accepted_urls_all,
            source_label,
            now,
            import_run_id=import_run_id,
            imported_by="owner_sitemap_import",
            import_reason="authority_sitemap_import",
        )
        auto_added = int(stats.get("added", 0) or 0)
        auto_updated = int(stats.get("updated", 0) or 0)

        _audit("owner_sitemap_commit_auto", {
            "source_label": source_label,
            "auto_added": auto_added,
            "auto_updated": auto_updated,
            "written_count": len(accepted_urls_all),
            "auto_path": str(AUTO_PATH),
            "import_run_id": import_run_id,
            "snapshot_path": snapshot_path,
        })

        _append_import_run_index({
            "import_run_id": import_run_id,
            "ts": now,
            "event": "owner_sitemap_commit_auto",
            "source_label": source_label,
            "written_count": len(accepted_urls_all),
            "auto_added": auto_added,
            "auto_updated": auto_updated,
            "snapshot_path": snapshot_path,
        }, max_keep=None)

    return {
        "ok": True,
        "stage": "C4_STEP_5_COMMIT_DONE" if payload.commit else "C4_STEP_4_RECURSIVE_TRAVERSAL_DONE",
        "source_label": source_label,
        "domain": domain or None,
        "sitemap_url": sitemap_url or None,
        "filters_used": {
            "include_paths": include_paths,
            "exclude_paths": exclude_paths,
            "block_extensions": block_ext,
            "require_host_match": require_host_match,
            "allowed_hosts": allowed_hosts,
            "allow_lang_prefixes": allow_lang,
            "block_lang_prefixes": block_lang,
        },
        "import_run_id": import_run_id,
        "snapshot_path": snapshot_path,
        "robots_url": discovered.get("robots_url"),
        "method_used": discovered.get("method_used"),
        "sitemaps_seeded": len(discovered.get("sitemaps_found") or []),
        "sitemaps_processed": sitemaps_processed,
        "sitemap_indexes_seen": sitemap_indexes_seen,
        "child_sitemaps_enqueued": child_sitemaps_enqueued,
        "urls_found_total": urls_found_total,
        "urls_after_filters": urls_after_filters,
        "filtered_out": filtered_out,
        "skipped_ext": skipped_ext,
        "skipped_blocked": skipped_blocked,
        "skipped_host": skipped_host,
        "skipped_lang": skipped_lang,
        "fetch_errors": fetch_errors,
        "fetch_error_samples": fetch_error_samples,
        "accepted_sample": accepted_sample,
        "commit": bool(payload.commit),
        "auto_added": auto_added,
        "auto_updated": auto_updated,
        "auto_path": str(AUTO_PATH),
        "caps": {
            "max_sitemaps_total": "unlimited",
            "max_write_urls": "unlimited",
            "max_urls_return_sample": MAX_URLS_RETURN_SAMPLE,
        },
    }
