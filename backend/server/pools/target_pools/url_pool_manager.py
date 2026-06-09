# backend/server/pools/target_pools/url_pool_manager.py
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data")
TARGET_POOLS_DIR = DATA_DIR / "target_pools"
URL_POOL_DIR = TARGET_POOLS_DIR / "url_pool_manager"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _site_sources_path(workspace_id: str) -> Path:
    return DATA_DIR / f"site_sources_{workspace_id}.json"


def _site_pages_path(workspace_id: str) -> Path:
    return DATA_DIR / f"site_pages_{workspace_id}.json"


def _active_target_set_path(workspace_id: str) -> Path:
    return TARGET_POOLS_DIR / f"active_target_set_{workspace_id}.json"


def _reserve_urls_path(workspace_id: str) -> Path:
    return URL_POOL_DIR / f"reserve_urls_{workspace_id}.json"


def _read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _write_json(path: Path, obj: Any) -> Any:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return obj


def _unique_clean(urls: List[str]) -> List[str]:
    seen = set()
    out = []
    for raw in urls or []:
        url = str(raw or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(url)
    return out


def _domain_from_url(url: str) -> str:
    try:
        u = urlparse((url or "").strip())
        return (u.netloc or "").strip().lower().split(":")[0]
    except Exception:
        return ""


def classify_url_for_pool(url: str, workspace_id: str) -> Dict[str, Any]:
    """
    URL Pool Manager safety classification.

    This is NOT relevance scoring.
    This only classifies whether a URL is allowed into URL pool lifecycle.
    """
    u = str(url or "").strip()
    if not u:
        return {"decision": "reject", "class": "reject", "reason": "empty_url"}

    lower_url = u.lower()
    path = urlparse(u).path or ""
    path_lower = path.lower().strip()
    host = _domain_from_url(u)

    domain_hint = workspace_id.replace("ws_", "").replace("_", ".")

    # 17. non-domain
    if domain_hint and domain_hint not in host:
        return {"decision": "reject", "class": "reject", "reason": "non_domain"}

    # 1. homepage/root
    if path_lower in {"", "/"}:
        return {"decision": "reject", "class": "reject", "reason": "homepage_root"}

    # 2 + 3. images/media/CDN + files/downloads
    if re.search(r"\.(jpg|jpeg|png|gif|webp|svg|ico|pdf|doc|docx|ppt|pptx|xls|xlsx|zip|rar|7z|tar|gz|mp3|mp4|m4a|wav|mov|avi|webm|woff|woff2|ttf|otf|eot)(\?|$)", lower_url):
        return {"decision": "reject", "class": "reject", "reason": "media_file_or_download"}

    if "images." in lower_url or "/images/" in lower_url or "/uploads/" in lower_url or "cdn." in lower_url:
        return {"decision": "reject", "class": "reject", "reason": "image_media_cdn"}

    # 4. community/forum/profile
    if re.search(r"/(community|forums?|profile|member|user|users|groups?)(/|$)", path_lower):
        return {"decision": "reject", "class": "reject", "reason": "community_forum_profile"}

    # 5. news/deals/promos
    if re.search(r"/(news|deals?|offers?|coupon|coupons|promo|promotions?)(/|$)", path_lower):
        return {"decision": "reject", "class": "reject", "reason": "news_deals_promos"}

    # 6. giveaway/rules/contest
    if re.search(r"(giveaway|contest|sweepstakes|rules|terms-of-entry)", path_lower):
        return {"decision": "reject", "class": "reject", "reason": "giveaway_rules_contest"}

    # 7. search pages
    if re.search(r"/search(/|$)|[?&](s|q|query|search)=", lower_url):
        return {"decision": "reject", "class": "reject", "reason": "search_page"}

    # 8. tag/category/archive
    if re.search(r"/(tag|tags|category|categories|archive|archives)(/|$)", path_lower):
        return {"decision": "reject", "class": "reject", "reason": "tag_category_archive"}

    # 9. author pages
    if re.search(r"/(author|authors|byline|contributors?)(/|$)", path_lower):
        return {"decision": "reject", "class": "reject", "reason": "author_page"}

    # 10. pagination
    if re.search(r"/page/\d+/?$", path_lower) or re.search(r"[?&](paged|page)=\d+", lower_url):
        return {"decision": "reject", "class": "reject", "reason": "pagination"}

    # 11. login/account/cart/checkout
    if re.search(r"/(login|logout|register|signup|sign-in|account|my-account|cart|checkout|orders|wishlist)(/|$)", path_lower):
        return {"decision": "reject", "class": "reject", "reason": "login_account_cart_checkout"}

    # 12. api/wp-json/admin/system
    if re.search(r"/(api|graphql|rest|ajax|admin|wp-admin|wp-json)(/|$)", path_lower) or "xmlrpc.php" in path_lower:
        return {"decision": "reject", "class": "reject", "reason": "api_admin_system"}

    # 13. feed/RSS/Atom
    if re.search(r"/(feed|rss|atom)/?$", path_lower) or path_lower.endswith((".rss", ".atom")):
        return {"decision": "reject", "class": "reject", "reason": "feed_rss_atom"}

    # 14. privacy/terms/contact/about
    if re.search(r"/(privacy|privacy-policy|terms|terms-and-conditions|cookie|cookie-policy|contact|about|faq|help|support|advertise|newsletter|disclaimer|editorial-policy|affiliate-disclosure)(/|$)", path_lower):
        return {"decision": "reject", "class": "reject", "reason": "privacy_terms_contact_about"}

    # 15. tracking/query URLs
    if re.search(r"[?&](utm_|gclid|fbclid|msclkid|yclid|_ga|_gl|ref|source|campaign|adgroup|adid|affiliate|aff|srsltid)=", lower_url):
        return {"decision": "reject", "class": "reject", "reason": "tracking_query_url"}

    # 19. old campaign/promo pages
    if re.search(r"(campaign|landing|black-friday|cyber-monday|prime-day|memorial-day|sale|discount)", path_lower):
        return {"decision": "reject", "class": "reject", "reason": "old_campaign_promo"}

    # 18. weak shallow hubs
    slug = path_lower.strip("/").split("/")[-1] if path_lower.strip("/") else ""
    slug_words = [w for w in re.split(r"[-_/]+", slug) if len(w) >= 3]
    path_parts = [p for p in path_lower.strip("/").split("/") if p]

    article_structure_hint = (
        len(slug_words) >= 3
        or path_lower.endswith(".aspx")
        or re.search(r"/(article|articles|guide|guides|how-to|howto|learn|resources|blog|blogs|post|posts)(/|$)", path_lower)
    )

    if path_lower.count("/") <= 1 and not article_structure_hint:
        return {"decision": "reject", "class": "reject", "reason": "weak_shallow_hub"}

    # 20. thin/no article slug
    if len(slug_words) < 2 and not article_structure_hint:
        if len(path_parts) >= 2 and len(slug_words) >= 1:
            return {"decision": "keep", "class": "keep_low_priority", "reason": "short_slug_but_usable_path"}
        return {"decision": "reject", "class": "reject", "reason": "thin_no_article_slug"}

    # Kept URL classification ? niche-safe, structure-based
    if article_structure_hint and len(path_parts) >= 2:
        return {"decision": "keep", "class": "keep_high_priority", "reason": "article_like_structure"}

    if len(slug_words) >= 3:
        return {"decision": "keep", "class": "keep_high_priority", "reason": "topic_rich_slug"}

    if len(path_parts) >= 3:
        return {"decision": "keep", "class": "keep_normal", "reason": "normal_content_depth"}

    return {"decision": "keep", "class": "keep_low_priority", "reason": "weak_but_usable_hub"}


def _is_safe_reserve_url(url: str, workspace_id: str) -> bool:
    return classify_url_for_pool(url, workspace_id).get("decision") == "keep"


def load_all_sitemap_urls(workspace_id: str) -> List[str]:
    """
    Returns full usable URL inventory from site_sources.

    This is for URL Pool Manager lifecycle:
    - active URLs are in active_target_set
    - reserve URLs come from full sitemap inventory minus active URLs
    - this function only applies safety cleanup, not scoring or ranking
    """
    obj = _read_json(_site_sources_path(workspace_id), {})
    urls: List[str] = []

    for source in obj.get("sources") or []:
        if not isinstance(source, dict):
            continue
        for u in source.get("sitemap_urls") or []:
            if str(u).strip() and _is_safe_reserve_url(str(u).strip(), workspace_id):
                urls.append(str(u).strip())

    return _unique_clean(urls)


def load_active_urls(workspace_id: str) -> List[str]:
    obj = _read_json(_active_target_set_path(workspace_id), {})
    return _unique_clean(obj.get("active_live_domain_urls") or [])


def save_active_urls(workspace_id: str, urls: List[str]) -> Dict[str, Any]:
    path = _active_target_set_path(workspace_id)
    obj = _read_json(path, {})

    if not isinstance(obj, dict):
        obj = {}

    obj["workspace_id"] = workspace_id
    obj["active_live_domain_urls"] = _unique_clean(urls)
    obj["updated_at"] = _now()

    obj.setdefault("active_document_ids", [])
    obj.setdefault("active_draft_ids", [])
    obj.setdefault("active_imported_urls", [])

    return _write_json(path, obj)


def load_reserve_urls(workspace_id: str) -> List[str]:
    obj = _read_json(_reserve_urls_path(workspace_id), {})
    return _unique_clean(obj.get("reserve_live_domain_urls") or [])


def save_reserve_urls(workspace_id: str, urls: List[str]) -> Dict[str, Any]:
    obj = {
        "workspace_id": workspace_id,
        "type": "url_pool_reserve",
        "updated_at": _now(),
        "reserve_live_domain_urls": _unique_clean(urls),
    }
    return _write_json(_reserve_urls_path(workspace_id), obj)


def initialize_url_pool_from_current_active(workspace_id: str) -> Dict[str, Any]:
    all_urls = load_all_sitemap_urls(workspace_id)
    active_urls = load_active_urls(workspace_id)

    active_set = set(active_urls)
    reserve_urls = [u for u in all_urls if u not in active_set]

    save_reserve_urls(workspace_id, reserve_urls)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "all_urls_count": len(all_urls),
        "active_urls_count": len(active_urls),
        "reserve_urls_count": len(reserve_urls),
    }


def promote_url(workspace_id: str, url: str, max_active: int = 2000) -> Dict[str, Any]:
    clean_url = str(url or "").strip()
    if not clean_url:
        return {"ok": False, "workspace_id": workspace_id, "error": "empty_url"}

    active = load_active_urls(workspace_id)
    reserve = load_reserve_urls(workspace_id)

    if clean_url not in active:
        active.append(clean_url)

    reserve = [u for u in reserve if u != clean_url]

    demoted = None
    if len(active) > max_active:
        demoted = active.pop(0)
        if demoted and demoted not in reserve:
            reserve.append(demoted)

    save_active_urls(workspace_id, active)
    save_reserve_urls(workspace_id, reserve)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "promoted_url": clean_url,
        "demoted_url": demoted,
        "active_urls_count": len(active),
        "reserve_urls_count": len(reserve),
    }


def demote_url(workspace_id: str, url: str) -> Dict[str, Any]:
    clean_url = str(url or "").strip()
    if not clean_url:
        return {"ok": False, "workspace_id": workspace_id, "error": "empty_url"}

    active = load_active_urls(workspace_id)
    reserve = load_reserve_urls(workspace_id)

    active = [u for u in active if u != clean_url]

    if clean_url not in reserve:
        reserve.append(clean_url)

    save_active_urls(workspace_id, active)
    save_reserve_urls(workspace_id, reserve)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "demoted_url": clean_url,
        "active_urls_count": len(active),
        "reserve_urls_count": len(reserve),
    }


def classify_url_list(workspace_id: str, urls: List[str], limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    clean_urls = _unique_clean(urls)
    selected = clean_urls[offset: offset + limit]

    items = []
    counts = {
        "keep_high_priority": 0,
        "keep_normal": 0,
        "keep_low_priority": 0,
        "reject": 0,
    }

    for url in clean_urls:
        c = classify_url_for_pool(url, workspace_id)
        cls = c.get("class") or "reject"
        if cls not in counts:
            counts[cls] = 0
        counts[cls] += 1

    for url in selected:
        c = classify_url_for_pool(url, workspace_id)
        items.append({
            "url": url,
            "decision": c.get("decision"),
            "class": c.get("class"),
            "reason": c.get("reason"),
        })

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "total": len(clean_urls),
        "limit": limit,
        "offset": offset,
        "counts": counts,
        "items": items,
    }


def get_url_pool_stats(workspace_id: str) -> Dict[str, Any]:
    all_urls = load_all_sitemap_urls(workspace_id)
    active_urls = load_active_urls(workspace_id)
    reserve_urls = load_reserve_urls(workspace_id)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "all_urls_count": len(all_urls),
        "active_urls_count": len(active_urls),
        "reserve_urls_count": len(reserve_urls),
        "has_site_sources": _site_sources_path(workspace_id).exists(),
        "has_active_target_set": _active_target_set_path(workspace_id).exists(),
        "has_reserve_pool": _reserve_urls_path(workspace_id).exists(),
    }
