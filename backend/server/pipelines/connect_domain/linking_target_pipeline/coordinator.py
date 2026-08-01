"""
LinkCraftor Connect Domain — Pipeline 1

LINKING TARGET PIPELINE

CONNECT DOMAIN
    -> Site Sources
    -> Site Pages
    -> Live Domain Target Pool
    -> Topic Cluster Builder
    -> Section Cluster Builder
    -> Cluster -> Target Bridge
    -> Section -> Target Bridge
    -> Enriched Live Domain Target Pool
    -> Active Target Set

Runtime registration and Universal Runtime Infrastructure wiring are
intentionally deferred.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from fastapi import HTTPException

from backend.server.pipelines.connect_domain.linking_target_pipeline.url_cleaner import clean_urls


def _site_reader():
    """
    Resolve the existing Site Reader module only when Pipeline 1 executes.

    The delayed import prevents a module-import cycle while the Connect Domain
    route delegates execution into this pipeline module.
    """
    from backend.server.routes import site_reader

    return site_reader


def run_linking_target_pipeline(payload):
    """Execute Connect Domain Pipeline 1 — Linking Target Pipeline."""
    sr = _site_reader()

    _normalize_domain = sr._normalize_domain
    _workspace_id_from_domain = sr._workspace_id_from_domain
    _http_get = sr._http_get
    _fetch_and_expand_sitemaps = sr._fetch_and_expand_sitemaps
    _domain_from_url = sr._domain_from_url
    save_site_sources = sr.save_site_sources
    save_site_pages = sr.save_site_pages
    _active_target_set_path = sr._active_target_set_path
    load_site_pages_payload = sr.load_site_pages_payload
    build_canonical_live_domain_target_pool = sr.build_canonical_live_domain_target_pool
    save_canonical_live_domain_target_pool = sr.save_canonical_live_domain_target_pool
    initialize_url_pool_from_current_active = sr.initialize_url_pool_from_current_active
    get_url_pool_stats = sr.get_url_pool_stats

    domain = _normalize_domain(payload.domain)

    if not domain:
        raise HTTPException(
            status_code=400,
            detail="A valid domain is required.",
        )

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

    cleaner_result = clean_urls(
        all_urls,
        domain,
        exclude_informational=True,
        exclude_taxonomy=True,
    )

    cleaned_urls = cleaner_result.urls
    rejected_urls = cleaner_result.rejected
    rejection_reason_counts = cleaner_result.reason_counts
    explicit_content_urls = cleaner_result.explicit_urls
    uncertain_content_urls = cleaner_result.uncertain_urls

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
                "url_cleaner_input_count": len(all_urls),
                "cleaned_urls_count": len(cleaned_urls),
                "explicit_content_urls_count": len(explicit_content_urls),
                "uncertain_content_urls_count": len(uncertain_content_urls),
                "rejected_urls_count": len(rejected_urls),
                "rejection_reason_counts": rejection_reason_counts,
            }
        ],
        "errors": sitemap_errors[:100],
        "rejected_urls_sample": rejected_urls[:200],
    })

    pages = {}
    now = datetime.now(timezone.utc).isoformat()

    for url in cleaned_urls:
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
        "active_live_domain_urls": cleaned_urls,
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
        site_pages_payload = load_site_pages_payload(
            workspace_id
        )

        certified_pages = (
            site_pages_payload.get("pages")
            or []
        )

        certified_domain = str(
            site_pages_payload.get("domain")
            or domain
        ).strip()

        live_result = build_canonical_live_domain_target_pool(
            certified_pages,
            workspace_id=workspace_id,
            domain=certified_domain,
        )

        save_canonical_live_domain_target_pool(
            live_result
        )

        live_counts = {
            "input_count": live_result.input_count,
            "created_count": live_result.created_count,
            "rejected_count": live_result.rejected_count,
        }

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
            "cleaned_urls_count": len(cleaned_urls),
        }

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "domain": domain,
        "created": created,
        "workspace_file": str(ws_meta_path),
        "sitemap_used": sitemap_used,
        "sitemap_url_count": len(all_urls),
        "cleaned_urls_count": len(cleaned_urls),
        "active_live_domain_urls_count": len(active_obj["active_live_domain_urls"]),
        "live_domain_counts": live_counts,
        "url_pool": url_pool_out,
        "url_pool_stats": url_pool_stats,
    }
