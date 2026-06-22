from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException

from backend.app.routers.external import (
    OwnerSitemapImportRequest,
    _get_source_config,
    _discover_sitemaps_from_robots,
    _normalize_hosts,
    _normalize_url,
    _http_get_text,
    _extract_loc_urls,
    _is_sitemap_index,
    _is_probably_xml_url,
    _passes_host_scope,
    _passes_lang_filters,
    _url_has_blocked_extension,
    _passes_path_filters,
    _is_blocked,
    _bulk_upsert_auto_authority,
    _new_import_run_id,
    _write_snapshot_before_commit,
    _append_import_run_index,
    AUTO_PATH,
    _audit,
)

router = APIRouter(tags=["external-sitemap-import-runtime"])


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
