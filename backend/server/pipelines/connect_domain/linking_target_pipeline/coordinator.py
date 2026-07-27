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
    build_live_domain_target_pool = sr.build_live_domain_target_pool
    build_workspace_topic_clusters = sr.build_workspace_topic_clusters
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
