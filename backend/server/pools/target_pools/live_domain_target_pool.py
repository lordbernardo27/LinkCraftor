# backend/server/pools/target_pools/live_domain_target_pool.py

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse, unquote

from backend.server.utils.text_normalization import fix_mojibake_text


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    server_dir = here.parents[2]
    return server_dir / "data"


def _pool_path(ws: str) -> Path:
    return _data_dir() / "target_pools" / "live_domain" / f"live_domain_target_pool_{ws}.json"


def _site_pages_path(ws: str) -> Path:
    return _data_dir() / f"site_pages_{ws}.json"


def _site_sources_path(ws: str) -> Path:
    return _data_dir() / f"site_sources_{ws}.json"


def _active_target_set_path(ws: str) -> Path:
    return _data_dir() / "target_pools" / f"active_target_set_{ws}.json"


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _norm_url(u: str) -> str:
    u = (u or "").strip()
    u = u.split("#")[0].split("?")[0]
    return u.rstrip("/")


def _norm_seed_path(p: str) -> str:
    p = (p or "").strip()

    if not p:
        return ""

    if not p.startswith("/"):
        p = "/" + p

    return p.rstrip("/") or ""


def _path_matches_seed_paths(url: str, seed_paths: List[str]) -> bool:
    if not seed_paths:
        return False

    try:
        path = (urlparse(url).path or "/").rstrip("/")
    except Exception:
        return False

    for sp in seed_paths:
        if path == sp:
            return True

        if path.startswith(sp + "/"):
            return True

        if sp.endswith("-") and path.startswith(sp):
            return True

    return False


def _is_primary_english_url(url: str) -> bool:
    low = url.lower()

    blocked_patterns = [
        "%d8%",              # encoded Arabic
        "calculateur-",      # French
        "calculadora-",      # Spanish
        "fecha-de-parto",
        "daccouchement",
        "deficit-calorique",
        "deficit-calorico",
    ]

    for pat in blocked_patterns:
        if pat in low:
            return False

    return True


def _is_noisy_url(url: str) -> Tuple[bool, str]:
    try:
        parsed = urlparse(url)
        path = (parsed.path or "/").lower()

    except Exception:
        return True, "invalid_url"

    noisy_parts = [
        "/wp-admin",
        "/wp-login",
        "/login",
        "/cart",
        "/checkout",
        "/my-account",
        "/account",
        "/tag/",
        "/author/",
        "/feed",
        "/comments",
        "/page/",
    ]

    for part in noisy_parts:
        if part in path:
            return True, f"excluded_path:{part}"

    if path.endswith(".xml") or path.endswith(".json"):
        return True, "excluded_file_type"

    return False, ""


def _slug_title_from_url(url: str) -> str:
    try:
        path = unquote(urlparse(url).path or "")
        slug = path.strip("/").split("/")[-1]

    except Exception:
        slug = ""

    slug = slug.replace("-", " ").replace("_", " ").strip()

    return slug.title() if slug else "Untitled Page"


def _extract_title(rec: Any, url: str) -> Tuple[str, str]:
    if not isinstance(rec, dict):
        return _slug_title_from_url(url), "slug"

    for key in [
        "h1",
        "title",
        "meta_title",
        "metaTitle",
        "page_title",
        "name",
    ]:
        val = rec.get(key)

        if val:
            title = fix_mojibake_text(str(val).strip())

            if title:
                return title, key

    return _slug_title_from_url(url), "slug"

def _page_type_hint(url: str, title: str) -> str:
    """
    Intelligent Page-Type Classifier v1.1.

    Uses scoring-based classification:
    - Multiple page types can gain scores.
    - Highest-confidence type wins.
    - Fallback remains generic_content.
    - Stable deterministic output for RB2/scoring compatibility.
    """

    combined = f"{url} {title}".lower()

    scores = {
        "calculator": 0,
        "tool": 0,
        "service": 0,
        "product": 0,
        "category": 0,
        "landing_page": 0,
        "blog": 0,
        "article": 0,
        "guide": 0,
        "how_to": 0,
        "comparison": 0,
        "documentation": 0,
        "pillar": 0,
        "glossary": 0,
        "faq": 0,
        "case_study": 0,
        "review": 0,
        "news": 0,
        "research": 0,
        "resource": 0,
        "template": 0,
        "download": 0,
        "course": 0,
        "local_page": 0,
        "condition_page": 0,
        "symptom_page": 0,
        "treatment_page": 0,
        "pricing_page": 0,
        "generic_content": 1,
    }

    patterns = {
        "calculator": ["calculator", "calculateur", "calculadora", "bmi", "calorie", "deficit", "due date", "ovulation"],
        "tool": ["/tool/", "generator", "checker", "analyzer", "validator", "estimator", "tracker", "planner"],
        "service": ["/service/", "/services/", "consulting", "agency", "management", "done for you", "hire us"],
        "product": ["/product/", "/products/", "software", "platform", "app", "plugin", "extension"],
        "category": ["/category/", "/categories/", "/topics/", "/collections/", "/tag/"],
        "landing_page": ["get started", "start free", "book demo", "sign up", "try free", "request demo"],
        "blog": ["/blog/", "/posts/", "/articles/"],
        "article": ["what is", "why", "when", "where", "explained", "tips", "benefits"],
        "guide": ["guide", "ultimate guide", "complete guide", "beginner guide", "step by step"],
        "how_to": ["/how-to-", "how to", "ways to", "steps to", "learn how"],
        "comparison": [" vs ", "versus", "compare", "comparison", "difference between", "alternative"],
        "documentation": ["/docs/", "/documentation/", "api reference", "developer docs", "manual"],
        "pillar": ["ultimate", "complete", "comprehensive", "everything you need", "master guide"],
        "glossary": ["/glossary/", "definition of", "meaning of", "terms"],
        "faq": ["/faq", "frequently asked questions", "questions and answers"],
        "case_study": ["case study", "success story", "customer story"],
        "review": ["review", "reviews", "best", "top", "rating"],
        "news": ["/news/", "latest", "breaking", "announced", "update"],
        "research": ["study", "research", "clinical trial", "evidence", "report"],
        "resource": ["/resources/", "resource", "library", "hub"],
        "template": ["template", "checklist", "worksheet", "swipe file"],
        "download": ["download", "pdf", "ebook", "whitepaper"],
        "course": ["course", "training", "lesson", "certification", "academy"],
        "local_page": ["near me", "in accra", "in london", "in new york", "location"],
        "condition_page": ["symptoms of", "causes of", "condition", "disease", "disorder"],
        "symptom_page": ["symptom", "signs of", "warning signs"],
        "treatment_page": ["treatment", "medicine", "medication", "therapy", "remedy"],
        "pricing_page": ["pricing", "price", "plans", "subscription", "cost"],
    }

    weights = {
        "calculator": 5,
        "tool": 4,
        "service": 4,
        "product": 4,
        "category": 3,
        "landing_page": 4,
        "blog": 3,
        "article": 2,
        "guide": 4,
        "how_to": 5,
        "comparison": 5,
        "documentation": 5,
        "pillar": 4,
        "glossary": 4,
        "faq": 4,
        "case_study": 4,
        "review": 3,
        "news": 3,
        "research": 4,
        "resource": 3,
        "template": 4,
        "download": 4,
        "course": 4,
        "local_page": 3,
        "condition_page": 4,
        "symptom_page": 4,
        "treatment_page": 4,
        "pricing_page": 5,
    }

    for page_type, pats in patterns.items():
        for pat in pats:
            if pat in combined:
                scores[page_type] += weights.get(page_type, 1)

    # Strong-intent overrides:
    # Prevent generic /blog/ from overpowering clearer page intent.
    if "how to" in combined or "/how-to-" in combined:
        scores["how_to"] += 8

    if "calculator" in combined or "bmi" in combined or "due date" in combined or "ovulation" in combined:
        scores["calculator"] += 8

    if "pricing" in combined or "plans" in combined or "subscription" in combined or "cost" in combined:
        scores["pricing_page"] += 8

    if "guide" in combined or "complete guide" in combined or "ultimate guide" in combined:
        scores["guide"] += 6

    if " vs " in combined or "versus" in combined or "difference between" in combined:
        scores["comparison"] += 8

    if "/blog/" in combined:
        # Blog is a container signal, not always the true page intent.
        # Keep it useful but weaker than explicit content intent.
        scores["blog"] = min(scores.get("blog", 0), 3)

    priority_order = [
        "pricing_page",
        "documentation",
        "comparison",
        "calculator",
        "how_to",
        "tool",
        "service",
        "product",
        "condition_page",
        "symptom_page",
        "treatment_page",
        "course",
        "template",
        "download",
        "case_study",
        "research",
        "pillar",
        "guide",
        "faq",
        "glossary",
        "landing_page",
        "category",
        "review",
        "news",
        "resource",
        "blog",
        "article",
        "local_page",
        "generic_content",
    ]

    winner = "generic_content"
    best_score = scores["generic_content"]

    for page_type in priority_order:
        score = scores.get(page_type, 0)
        if score > best_score:
            winner = page_type
            best_score = score

    return winner


def _priority_bucket(url: str, title: str = "", page_type_hint: str = "", seed_match: bool = False) -> str:
    """
    Universal Target Priority Classifier v1 for Live-Domain.

    Preserves live-domain seed intelligence while adding universal
    cross-niche target priority logic.
    """

    text = f"{url} {title}".lower()

    try:
        path = (urlparse(url).path or "/").strip("/")
    except Exception:
        path = ""

    depth = len([x for x in path.split("/") if x]) if path else 0
    page_type = str(page_type_hint or "").lower().strip()

    utility_patterns = [
        "/privacy",
        "/terms",
        "/contact",
        "/about",
        "/login",
        "/account",
        "/cart",
        "/checkout",
        "/feed",
        "/tag/",
        "/author/",
    ]

    if any(pat in text for pat in utility_patterns):
        return "utility"

    # Preserve connected-domain seed intelligence.
    if seed_match:
        if page_type in {"pricing_page", "service", "product", "landing_page"}:
            return "commercial"
        if page_type in {"category", "resource", "course", "documentation", "glossary"}:
            return "hub"
        if page_type in {"calculator", "tool", "template", "download", "comparison", "case_study", "review", "pillar"}:
            return "strategic"
        return "core"

    if page_type in {"homepage", "pillar"}:
        return "core"

    if page_type in {"pricing_page", "service", "product", "landing_page"}:
        return "commercial"

    if page_type in {"category", "resource", "course", "documentation", "glossary"}:
        return "hub"

    if page_type in {"calculator", "tool", "template", "download", "comparison", "case_study", "review"}:
        return "strategic"

    if page_type in {
        "article",
        "blog",
        "guide",
        "how_to",
        "research",
        "news",
        "faq",
        "condition_page",
        "symptom_page",
        "treatment_page",
        "local_page",
        "generic_content",
        "page",
    }:
        if depth <= 1 and page_type in {"guide", "how_to", "research"}:
            return "strategic"
        return "standard"

    if depth <= 1:
        return "standard"

    return "supporting"


def build_live_domain_target_pool(workspace_id: str) -> Dict[str, Any]:
    """
    Live-Domain Target Pool Builder v2 (English-only).

    Behavior:
    - Reads sitemap URLs from connected domain
    - Removes noisy/system URLs
    - Removes non-English URLs
    - Uses seed_paths as priority signals only
    - Keeps all valid English content URLs
    """

    ws = (workspace_id or "").strip()

    if not ws:
        raise ValueError("workspace_id is required")

    src_fp = _site_sources_path(ws)
    pages_fp = _site_pages_path(ws)

    if not src_fp.exists():
        raise FileNotFoundError(f"Missing site sources file: {src_fp}")

    if not pages_fp.exists():
        raise FileNotFoundError(f"Missing site pages file: {pages_fp}")

    sources_obj = json.loads(src_fp.read_text(encoding="utf-8"))
    pages_obj = json.loads(pages_fp.read_text(encoding="utf-8"))

    active_fp = _active_target_set_path(ws)
    active_obj = _safe_read_json(active_fp) if active_fp.exists() else None

    active_live_domain_urls: List[str] = []

    if isinstance(active_obj, dict):
        raw_urls = active_obj.get("active_live_domain_urls") or []

        if isinstance(raw_urls, list):
            active_live_domain_urls = [
                _norm_url(str(x))
                for x in raw_urls
                if str(x).strip()
            ]

    active_live_domain_url_set = set(active_live_domain_urls)

    sources = sources_obj.get("sources") or []

    if not isinstance(sources, list):
        sources = []

    pages = pages_obj.get("pages") or {}

    if not isinstance(pages, dict):
        pages = {}

    seed_paths: List[str] = []
    candidate_urls: List[str] = []

    for source in sources:
        if not isinstance(source, dict):
            continue

        for raw_seed in source.get("seed_paths") or []:
            seed = _norm_seed_path(str(raw_seed or ""))

            if seed and seed not in seed_paths:
                seed_paths.append(seed)

        for raw_url in source.get("sitemap_urls") or []:
            url = _norm_url(str(raw_url or ""))

            if url and url not in candidate_urls:
                candidate_urls.append(url)

    before_quality_filter = len(candidate_urls)

    rejected: List[Dict[str, str]] = []
    quality_urls: List[str] = []

    for url in candidate_urls:
        noisy, reason = _is_noisy_url(url)

        if noisy:
            rejected.append({
                "url": url,
                "reason": reason,
            })
            continue

        if not _is_primary_english_url(url):
            rejected.append({
                "url": url,
                "reason": "non_primary_language",
            })
            continue

        quality_urls.append(url)

    after_quality_filter = len(quality_urls)

    before_active_filter = len(quality_urls)

    # Safety:
    # only apply active filtering when active URLs exist
    if active_live_domain_url_set:
        quality_urls = [
            u for u in quality_urls
            if u in active_live_domain_url_set
        ]

    after_active_filter = len(quality_urls)

    items: List[Dict[str, Any]] = []

    for url in quality_urls:
        rec = pages.get(url) or pages.get(url + "/") or {}

        title, title_source = _extract_title(rec, url)

        seed_match = _path_matches_seed_paths(url, seed_paths)

        page_type = _page_type_hint(url, title)
        priority_bucket = _priority_bucket(
            url,
            title,
            page_type,
            seed_match,
        )

        item = {
            "url": url,

            # Universal target display label
            # shared across imported/live-domain/future pools.
            "label": title,

            "h1": title,
            "title": title,
            "title_source": title_source,
            "path": urlparse(url).path or "/",
            "source_type": "live_domain",
            "source_origin": "connected_domain",
            "priority_bucket": priority_bucket,

            # Preserve Live-Domain seed intelligence separately.
            "seed_path_match": seed_match,
            "seed_priority_bucket": (
                "seed_match"
                if seed_match
                else "valid_content"
            ),
            "page_type_hint": page_type,

            # Universal metadata block
            "metadata": {
                "builder_version": "live_domain_target_pool_v2",
                "source_file": str(pages_fp),
                "title_fallback_used": title_source == "slug",
                "seed_path_match": seed_match,
                "title_source": title_source,
            },
        }

        items.append(item)

    out: Dict[str, Any] = {
        "workspace_id": ws,
        "type": "live_domain",
        "version": "v2_english_only",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": (
            "site_sources.sitemap_urls + "
            "english-only quality filtering + "
            "seed priority"
        ),
        "seed_paths": seed_paths,
        "active_target_set_used": bool(active_fp.exists()),
        "active_filter_applied": bool(active_live_domain_url_set),
        "active_live_domain_urls_count": len(active_live_domain_urls),

        "counts": {
            "candidate_urls_before_quality_filter": before_quality_filter,
            "candidate_urls_after_quality_filter": after_quality_filter,
            "candidate_urls_before_active_filter": before_active_filter,
            "candidate_urls_after_active_filter": after_active_filter,
            "rejected_urls": len(rejected),
            "items_written": len(items),
        },

        "rejected_examples": rejected[:25],
        "items": items,
    }

    out_fp = _pool_path(ws)

    out_fp.parent.mkdir(parents=True, exist_ok=True)

    out_fp.write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return out