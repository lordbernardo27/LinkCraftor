# backend/server/pools/target_pools/live_domain_target_pool.py

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse, unquote

from backend.server.utils.text_normalization import fix_mojibake_text
from backend.server.pools.target_pools.url_pool_manager import classify_url_for_pool


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
        if part == "/feed":
            if re.search(r"(^|/)feed/?$", path):
                return True, f"excluded_path:{part}"
            continue

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

def _active_phrase_pool_path(workspace_id: str) -> Path:
    return _data_dir() / "phrase_pools" / "active" / f"active_phrase_pool_{str(workspace_id or '').strip()}.json"




def _priority_phrase_set_path(workspace_id: str) -> Path:
    safe_ws = str(workspace_id or "default").strip() or "default"
    return Path("backend/server/data/phrase_pools/priority") / f"priority_phrase_set_{safe_ws}.json"


def _load_priority_phrases_for_target_pool(workspace_id: str, limit: int | None = None) -> List[str]:
    path = _priority_phrase_set_path(workspace_id)

    try:
        if not path.exists():
            return []

        obj = json.loads(path.read_text(encoding="utf-8"))
        raw = obj.get("phrases") or []

        phrases: List[str] = []
        seen = set()

        for item in raw:
            if isinstance(item, dict):
                phrase = str(item.get("phrase") or item.get("canonical") or "").strip()
            else:
                phrase = str(item or "").strip()

            if not phrase:
                continue

            key = phrase.lower()
            if key in seen:
                continue

            seen.add(key)
            phrases.append(phrase)

            if limit is not None and len(phrases) >= limit:
                break

        return phrases

    except Exception:
        return []


def _load_active_phrases_for_target_pool(workspace_id: str, limit: int | None = None) -> List[str]:
    fp = _active_phrase_pool_path(workspace_id)
    if not fp.exists():
        return []

    try:
        obj = json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        return []

    raw = []
    if isinstance(obj, dict):
        phrases = obj.get("phrases") or obj.get("items") or []
        if isinstance(phrases, dict):
            raw = list(phrases.values())
        elif isinstance(phrases, list):
            raw = phrases
    elif isinstance(obj, list):
        raw = obj

    out: List[str] = []
    seen = set()

    for item in raw:
        if isinstance(item, dict):
            phrase = (
                item.get("phrase")
                or item.get("phrase_text")
                or item.get("text")
                or item.get("label")
                or ""
            )
        else:
            phrase = str(item or "")

        phrase = str(phrase or '').lower().strip()
        if not phrase or phrase in seen:
            continue

        seen.add(phrase)
        out.append(phrase)

        if limit is not None and len(out) >= limit:
            break

    return out


def _phrase_tokens_for_target_pool(text: str) -> set:
    stop = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "how", "in", "into", "is", "it", "of", "on", "or", "the", "to",
        "what", "when", "where", "why", "with", "your", "you", "this",
        "that", "these", "those"
    }
    return {
        t for t in re.findall(r"[a-z0-9]{3,}", str(text or "").lower())
        if t not in stop
    }


def _score_target_against_active_phrases(url: str, title: str, active_phrases: List[str], max_matches: int = 12) -> Dict[str, Any]:
    haystack = " ".join([
        str(title or ""),
        str(url or "").replace("-", " ").replace("/", " "),
    ])
    hay_tokens = _phrase_tokens_for_target_pool(haystack)

    matches: List[Dict[str, Any]] = []

    for phrase in active_phrases or []:
        phrase_tokens = _phrase_tokens_for_target_pool(phrase)
        if not phrase_tokens or not hay_tokens:
            continue

        overlap = phrase_tokens & hay_tokens
        if not overlap:
            continue

        overlap_ratio = len(overlap) / max(1, len(phrase_tokens))
        exact_bonus = 0.35 if str(phrase or '').lower().strip() in str(haystack or '').lower() else 0.0
        phrase_score = round(overlap_ratio + exact_bonus, 4)

        # Do not store weak accidental matches.
        # Target-pool phrase memory must require strong, multi-token evidence.
        if phrase_score < 0.75:
            continue

        if len(overlap) < 2:
            continue

        matches.append({
            "phrase": phrase,
            "score": phrase_score,
            "matched_tokens": sorted(overlap),
        })

    matches.sort(key=lambda x: x.get("score", 0), reverse=True)
    top = matches[:max_matches]

    semantic_route_score = round(sum(float(x.get("score") or 0) for x in top), 4)
    target_score = round((semantic_route_score * 100) + (len(top) * 5), 4)

    return {
        "matched_phrases": [x["phrase"] for x in top],
        "active_phrase_matches": len(top),
        # Do not manufacture aliases from historical phrase matches.
        "aliases": [],
        "phrase_match_details": top,
        "semantic_route_score": semantic_route_score,
        "target_score": target_score,
    }



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


    def _load_section_membership_index() -> Dict[str, Dict[str, Any]]:
        """
        Bridge: section clusters -> live domain target items.
        Adds broad URL-section evidence without polluting strict topic clusters.
        """
        section_fp = _data_dir() / "topic_clusters" / f"workspace_section_clusters_{ws}.json"
        obj = _safe_read_json(section_fp) if section_fp.exists() else {}

        sections = obj.get("sections") if isinstance(obj, dict) else {}
        rows = sections.values() if isinstance(sections, dict) else sections if isinstance(sections, list) else []

        index: Dict[str, Dict[str, Any]] = {}

        for sec in rows:
            if not isinstance(sec, dict):
                continue

            section_id = str(sec.get("section_id") or "").strip()
            section_name = str(sec.get("name") or section_id).strip()
            section_keywords = sec.get("keywords") or []
            section_score = sec.get("confidence") or 0

            for u in sec.get("urls") or []:
                if isinstance(u, dict):
                    raw_url = u.get("url")
                    matched_terms = u.get("matched_terms") or []
                else:
                    raw_url = u
                    matched_terms = []

                url_key = _norm_url(str(raw_url or ""))
                if not url_key:
                    continue

                existing = index.setdefault(url_key, {
                    "section_ids": [],
                    "section_names": [],
                    "section_keywords": [],
                    "section_matched_terms": [],
                    "section_score": 0,
                })

                if section_id and section_id not in existing["section_ids"]:
                    existing["section_ids"].append(section_id)

                if section_name and section_name not in existing["section_names"]:
                    existing["section_names"].append(section_name)

                for kw in section_keywords:
                    kw = str(kw or "").strip()
                    if kw and kw not in existing["section_keywords"]:
                        existing["section_keywords"].append(kw)

                for mt in matched_terms:
                    mt = str(mt or "").strip()
                    if mt and mt not in existing["section_matched_terms"]:
                        existing["section_matched_terms"].append(mt)

                try:
                    existing["section_score"] = max(float(existing["section_score"] or 0), float(section_score or 0))
                except Exception:
                    pass

        return index


    def _load_cluster_membership_index() -> Dict[str, Dict[str, Any]]:
        """
        Bridge: topic clusters -> live domain target items.
        Builds URL -> cluster metadata index so every target carries cluster evidence.
        """
        cluster_fp = _data_dir() / "topic_clusters" / f"workspace_topic_clusters_{ws}.json"
        obj = _safe_read_json(cluster_fp) if cluster_fp.exists() else {}

        clusters = obj.get("clusters") if isinstance(obj, dict) else {}
        rows = clusters.values() if isinstance(clusters, dict) else clusters if isinstance(clusters, list) else []

        index: Dict[str, Dict[str, Any]] = {}

        for c in rows:
            if not isinstance(c, dict):
                continue

            cluster_id = str(c.get("cluster_id") or "").strip()
            cluster_name = str(c.get("name") or c.get("label") or c.get("primary_token") or cluster_id).strip()
            cluster_keywords = c.get("keywords") or []
            cluster_score = c.get("confidence") or c.get("score") or 0
            purity_score = c.get("purity_score") or 0

            for u in c.get("urls") or []:
                if isinstance(u, dict):
                    raw_url = u.get("url")
                    matched_terms = u.get("matched_terms") or []
                else:
                    raw_url = u
                    matched_terms = []

                url_key = _norm_url(str(raw_url or ""))
                if not url_key:
                    continue

                existing = index.setdefault(url_key, {
                    "cluster_ids": [],
                    "cluster_names": [],
                    "cluster_keywords": [],
                    "cluster_matched_terms": [],
                    "cluster_score": 0,
                    "cluster_purity_score": 0,
                })

                if cluster_id and cluster_id not in existing["cluster_ids"]:
                    existing["cluster_ids"].append(cluster_id)

                if cluster_name and cluster_name not in existing["cluster_names"]:
                    existing["cluster_names"].append(cluster_name)

                for kw in cluster_keywords:
                    kw = str(kw or "").strip()
                    if kw and kw not in existing["cluster_keywords"]:
                        existing["cluster_keywords"].append(kw)

                for mt in matched_terms:
                    mt = str(mt or "").strip()
                    if mt and mt not in existing["cluster_matched_terms"]:
                        existing["cluster_matched_terms"].append(mt)

                try:
                    existing["cluster_score"] = max(float(existing["cluster_score"] or 0), float(cluster_score or 0))
                except Exception:
                    pass

                try:
                    existing["cluster_purity_score"] = max(float(existing["cluster_purity_score"] or 0), float(purity_score or 0))
                except Exception:
                    pass

        return index

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

    # Live Domain Target Pool must be built from cleaned Site Pages,
    # not directly from raw sitemap URLs.
    for raw_url in pages.keys():
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

        classification = classify_url_for_pool(url, ws)
        if classification.get("decision") != "keep":
            rejected.append({
                "url": url,
                "reason": classification.get("reason") or "url_pool_manager_reject",
                "class": classification.get("class"),
            })
            continue

        quality_urls.append(url)

    after_quality_filter = len(quality_urls)

    before_active_filter = len(quality_urls)

    # Phrase-aware active URL promotion:
    # Priority pass scans RB2 final-highlight phrases first.
    # Secondary pass scans the remaining active phrase pool phrases second.
    active_phrases = _load_active_phrases_for_target_pool(ws, limit=None)
    priority_phrases = _load_priority_phrases_for_target_pool(ws, limit=None)

    priority_phrase_keys = {
        str(x or "").strip().lower()
        for x in priority_phrases
        if str(x or "").strip()
    }

    secondary_phrases = [
        p for p in active_phrases
        if str(p or "").strip().lower() not in priority_phrase_keys
    ]

    phrase_promoted_urls_count = 0
    priority_phrase_promoted_urls_count = 0
    secondary_phrase_promoted_urls_count = 0
    phrase_aware_selection_applied = False

    if active_live_domain_url_set:
        active_limit = max(1, len(active_live_domain_url_set))

        priority_scored_urls = []
        secondary_scored_urls = []
        filler_urls = []

        for u in quality_urls:
            lower_u = str(u or "").lower()

            if (
                "images." in lower_u
                or "/images/" in lower_u
                or "/gcms/" in lower_u
                or lower_u.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif", ".pdf"))
            ):
                continue

            rec = pages.get(u) or pages.get(u + "/") or {}
            title, _title_source = _extract_title(rec, u)

            priority_awareness = _score_target_against_active_phrases(
                url=u,
                title=title,
                active_phrases=priority_phrases,
            )

            priority_match_count = int(priority_awareness.get("active_phrase_matches") or 0)
            priority_score = float(priority_awareness.get("target_score") or 0)

            if priority_match_count >= 2:
                priority_scored_urls.append((priority_score, priority_match_count, u))
                continue

            secondary_awareness = _score_target_against_active_phrases(
                url=u,
                title=title,
                active_phrases=secondary_phrases,
            )

            secondary_match_count = int(secondary_awareness.get("active_phrase_matches") or 0)
            secondary_score = float(secondary_awareness.get("target_score") or 0)

            if secondary_match_count >= 2:
                secondary_scored_urls.append((secondary_score, secondary_match_count, u))
            elif u in active_live_domain_url_set:
                filler_urls.append(u)

        priority_scored_urls.sort(key=lambda x: (x[0], x[1]), reverse=True)
        secondary_scored_urls.sort(key=lambda x: (x[0], x[1]), reverse=True)

        promoted = []
        seen_promoted = set()

        for _score, _match_count, u in priority_scored_urls:
            if u in seen_promoted:
                continue
            promoted.append(u)
            seen_promoted.add(u)
            if len(promoted) >= active_limit:
                break

        for _score, _match_count, u in secondary_scored_urls:
            if len(promoted) >= active_limit:
                break
            if u in seen_promoted:
                continue
            promoted.append(u)
            seen_promoted.add(u)

        # Live Domain Target Pool must remain a full valid site-page inventory.
        # Phrase-aware promotion is diagnostic only here.
        # Do NOT replace quality_urls with promoted URLs at this stage.
        priority_phrase_promoted_urls_count = len([x for x in priority_scored_urls if x[2] in seen_promoted])
        secondary_phrase_promoted_urls_count = len([x for x in secondary_scored_urls if x[2] in seen_promoted])
        phrase_promoted_urls_count = priority_phrase_promoted_urls_count + secondary_phrase_promoted_urls_count
        phrase_aware_selection_applied = False

    after_active_filter = len(quality_urls)

    items: List[Dict[str, Any]] = []

    cluster_membership_index = _load_cluster_membership_index()
    section_membership_index = _load_section_membership_index()

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

        phrase_awareness = _score_target_against_active_phrases(
            url=url,
            title=title,
            active_phrases=(priority_phrases + secondary_phrases),
        )

        cluster_meta = (
            cluster_membership_index.get(url)
            or cluster_membership_index.get(_norm_url(url))
            or {}
        )

        section_meta = (
            section_membership_index.get(url)
            or section_membership_index.get(_norm_url(url))
            or {}
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

            # Phrase-aware target intelligence from active phrase pool.
            "aliases": phrase_awareness.get("aliases", []),
            "matched_phrases": phrase_awareness.get("matched_phrases", []),
            "active_phrase_matches": phrase_awareness.get("active_phrase_matches", 0),
            "phrase_match_details": phrase_awareness.get("phrase_match_details", []),
            "semantic_route_score": phrase_awareness.get("semantic_route_score", 0),
            "target_score": phrase_awareness.get("target_score", 0),

            # Cluster -> Target bridge enrichment.
            "cluster_ids": cluster_meta.get("cluster_ids", []),
            "cluster_names": cluster_meta.get("cluster_names", []),
            "cluster_keywords": cluster_meta.get("cluster_keywords", [])[:30],
            "cluster_matched_terms": cluster_meta.get("cluster_matched_terms", [])[:30],
            "cluster_score": cluster_meta.get("cluster_score", 0),
            "cluster_purity_score": cluster_meta.get("cluster_purity_score", 0),

            # Section -> Target bridge enrichment.
            "section_ids": section_meta.get("section_ids", []),
            "section_names": section_meta.get("section_names", []),
            "section_keywords": section_meta.get("section_keywords", [])[:30],
            "section_matched_terms": section_meta.get("section_matched_terms", [])[:30],
            "section_score": section_meta.get("section_score", 0),

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
        "active_phrase_pool_used": bool(active_phrases),
        "active_phrase_count": len(active_phrases),
        "priority_phrase_set_used": bool(priority_phrases),
        "priority_phrase_count": len(priority_phrases),
        "secondary_phrase_count": len(secondary_phrases),

        "counts": {
            "candidate_urls_before_quality_filter": before_quality_filter,
            "candidate_urls_after_quality_filter": after_quality_filter,
            "candidate_urls_before_active_filter": before_active_filter,
            "candidate_urls_after_active_filter": after_active_filter,
            "phrase_aware_selection_applied": phrase_aware_selection_applied,
            "phrase_promoted_urls_count": phrase_promoted_urls_count,
            "priority_phrase_promoted_urls_count": priority_phrase_promoted_urls_count,
            "secondary_phrase_promoted_urls_count": secondary_phrase_promoted_urls_count,
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