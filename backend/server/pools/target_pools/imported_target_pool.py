# backend/server/pools/target_pools/imported_target_pool.py

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse, unquote


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    server_dir = here.parents[2]  # .../backend/server
    return server_dir / "data"


def _pool_path(ws: str) -> Path:
    return _data_dir() / "target_pools" / "imported" / f"imported_target_pool_{ws}.json"


def _csv_path(ws: str) -> Path:
    return _data_dir() / f"imported_targets_{ws}.csv"


def _txt_path(ws: str) -> Path:
    return _data_dir() / f"imported_targets_{ws}.txt"


def _xml_path(ws: str) -> Path:
    return _data_dir() / f"imported_targets_{ws}.xml"


def _site_sources_path(ws: str) -> Path:
    return _data_dir() / f"site_sources_{ws}.json"


def _active_target_set_path(ws: str) -> Path:
    return _data_dir() / "target_pools" / f"active_target_set_{ws}.json"


def _clean(s: str) -> str:
    return str(s or "").strip().strip("\ufeff").strip()


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _is_http_url(u: str) -> bool:
    u = (u or "").strip().lower()
    return u.startswith("http://") or u.startswith("https://")


def _domain_from_sources_or_ws(ws: str) -> str:
    """
    Derive domain for placeholder URL generation.
    Prefer site_sources_<ws>.json sources[0].domain if present.
    Otherwise derive from ws name: ws_example_com -> example.com
    """
    fp = _site_sources_path(ws)
    if fp.exists():
        try:
            obj = json.loads(fp.read_text(encoding="utf-8"))
            arr = obj.get("sources") or []
            if isinstance(arr, list) and arr:
                dom = str((arr[0] or {}).get("domain") or "").strip().lower()
                dom = dom[4:] if dom.startswith("www.") else dom
                if dom:
                    return dom
        except Exception:
            pass

    s = ws
    if s.startswith("ws_"):
        s = s[3:]
    return s.replace("_", ".").strip(".").lower()


_slug_re = re.compile(r"[^a-z0-9]+")


def _slugify(s: str) -> str:
    s = _clean(s).lower()
    s = _slug_re.sub("-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "imported"


def _norm_url(u: str) -> str:
    u = _clean(u)
    return u[:-1] if u.endswith("/") else u


def _clean_label(label: str) -> str:
    label = _clean(label)
    if not label:
        return "Untitled"

    label = label.replace("-", " ").replace("_", " ")
    label = re.sub(r"\s+", " ", label).strip()

    word_map = {
        "whats": "What's",
        "hcg": "HCG",
        "ivf": "IVF",
        "lmp": "LMP",
        "c": "C",
    }

    small_words = {
        "a", "an", "and", "as", "at", "by", "for", "in", "of", "on", "or", "the", "to", "vs"
    }

    parts = label.split(" ")
    out: List[str] = []

    for i, part in enumerate(parts):
        low = part.lower()
        if low in word_map:
            out.append(word_map[low])
        elif low == "section":
            out.append("Section")
        elif low == "api":
            out.append("API")
        elif low == "seo":
            out.append("SEO")
        elif low == "url":
            out.append("URL")
        elif low == "h1":
            out.append("H1")
        elif low == "h2":
            out.append("H2")
        elif low == "h3":
            out.append("H3")
        elif low in small_words and i != 0:
            out.append(low)
        elif low.isdigit():
            out.append(low)
        else:
            out.append(low.capitalize())

    cleaned = " ".join(out)

    cleaned = re.sub(r"\bC Section\b", "C-Section", cleaned)
    cleaned = re.sub(r"\bWeek (\d{1,2}) (\d{1,2})\b", r"Week \1-\2", cleaned)
    cleaned = re.sub(r"\bWhat To\b", "What to", cleaned)
    cleaned = re.sub(r"\bHow To\b", "How to", cleaned)

    return cleaned or "Untitled"


def _slug_label_from_url(url: str) -> str:
    try:
        u = urlparse((url or "").strip())
        path = unquote(u.path or "").strip().rstrip("/")
        seg = path.split("/")[-1] if path else ""
        seg = (seg or "").strip()
        if not seg:
            return "Untitled"
        seg = seg.replace("-", " ").replace("_", " ").strip()
        seg = re.sub(r"\s+", " ", seg)
        return _clean_label(seg)
    except Exception:
        return "Untitled"


def _read_csv(fp: Path) -> List[Tuple[str, str]]:
    """
    Accept:
      - URL
      - Title
      - Title,URL
      - URL,Title
      - header forms supported (url/title/label/topic/name)
    Returns: (title, url_or_empty)
    """
    rows: List[Tuple[str, str]] = []
    with fp.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = None
        for i, r in enumerate(reader):
            if not r:
                continue

            if i == 0:
                low = [_clean(x).lower() for x in r]
                if any(x in {"url", "link", "href"} for x in low) or any(
                    x in {"title", "topic", "label", "name"} for x in low
                ):
                    header = low
                    continue

            if header:
                rec = {header[j]: _clean(r[j]) if j < len(r) else "" for j in range(len(header))}
                url = rec.get("url") or rec.get("link") or rec.get("href") or ""
                title = rec.get("title") or rec.get("topic") or rec.get("name") or rec.get("label") or ""
                rows.append((_clean(title), _clean(url)))
            else:
                c0 = _clean(r[0]) if len(r) >= 1 else ""
                c1 = _clean(r[1]) if len(r) >= 2 else ""

                if len(r) == 1:
                    if _is_http_url(c0):
                        rows.append(("", c0))
                    else:
                        rows.append((c0, ""))
                    continue

                if _is_http_url(c0):
                    rows.append((c1, c0))
                elif _is_http_url(c1):
                    rows.append((c0, c1))
                else:
                    rows.append((c0, ""))
    return rows


def _read_txt(fp: Path) -> List[Tuple[str, str]]:
    """
    Accept:
      - URL per line
      - Title per line
      - Title,URL per line
    Returns: (title, url_or_empty)
    """
    rows: List[Tuple[str, str]] = []
    for line in fp.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        try:
            parsed = next(csv.reader([line]))
        except Exception:
            parsed = [line]

        if not parsed:
            continue

        if len(parsed) == 1:
            c0 = _clean(parsed[0])
            if _is_http_url(c0):
                rows.append(("", c0))
            else:
                rows.append((c0, ""))
            continue

        c0 = _clean(parsed[0])
        c1 = _clean(parsed[1])

        if _is_http_url(c0):
            rows.append((c1, c0))
        elif _is_http_url(c1):
            rows.append((c0, c1))
        else:
            rows.append((c0, ""))
    return rows


def _read_xml_sitemap(fp: Path) -> List[Tuple[str, str]]:
    """
    Accept sitemap-like XML:
      <urlset> ... <loc>https://...</loc> ...
    Returns: (title_empty, url)
    """
    rows: List[Tuple[str, str]] = []
    root = ET.fromstring(fp.read_bytes())
    for el in root.findall(".//{*}loc"):
        if el is not None and el.text and el.text.strip():
            u = el.text.strip()
            if _is_http_url(u):
                rows.append(("", u))
    return rows



def _import_source_from_name(source_name: str) -> str:
    n = str(source_name or "").lower()
    if n.endswith(".csv"):
        return "csv"
    if n.endswith(".txt"):
        return "txt"
    if n.endswith(".xml"):
        return "xml"
    return "unknown"


def _path_from_url(url: str) -> str:
    try:
        from urllib.parse import urlparse
        path = urlparse(url).path or "/"
        return path if path.startswith("/") else "/" + path
    except Exception:
        return "/"


def _page_type_hint(url: str, label: str = "") -> str:
    """
    Imported Intelligent Page-Type Classifier v1.1.

    Mirrors the Live-Domain scoring-based classifier pattern:
    - Multiple page types can gain scores.
    - Highest-confidence type wins.
    - Fallback remains generic_content.
    - Stable deterministic output for RB2/scoring compatibility.
    """

    combined = f"{url} {label}".lower()

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

def _priority_bucket(url: str, label: str = "", page_type_hint: str = "") -> str:
    """
    Universal Target Priority Classifier v1.

    Works across niches:
    - Health
    - Finance
    - Legal
    - SaaS
    - E-commerce
    - Education
    - Real estate
    - Travel
    - News
    - Technology
    - Local business
    """

    text = f"{url} {label}".lower()
    path = _path_from_url(url).strip("/")
    depth = len([x for x in path.split("/") if x]) if path else 0
    page_type = str(page_type_hint or "").lower().strip()

    core_types = {
        "homepage",
        "pillar",
    }

    commercial_types = {
        "pricing_page",
        "service",
        "product",
        "landing_page",
    }

    hub_types = {
        "category",
        "resource",
        "course",
        "documentation",
        "glossary",
    }

    strategic_types = {
        "calculator",
        "tool",
        "template",
        "download",
        "comparison",
        "case_study",
        "review",
    }

    standard_types = {
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
    }

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

    if page_type in core_types:
        return "core"

    if page_type in commercial_types:
        return "commercial"

    if page_type in hub_types:
        return "hub"

    if page_type in strategic_types:
        return "strategic"

    if page_type in standard_types:
        if depth <= 1 and page_type in {"guide", "how_to", "research"}:
            return "strategic"
        return "standard"

    if depth <= 1:
        return "standard"

    if depth <= 3:
        return "supporting"

    return "supporting"


def _host_matches_domain(url: str, domain: str) -> bool:
    try:
        host = urlparse(str(url or "")).netloc.lower().strip()
        host = host[4:] if host.startswith("www.") else host
        dom = str(domain or "").lower().strip()
        dom = dom[4:] if dom.startswith("www.") else dom
        return bool(host and dom and (host == dom or host.endswith("." + dom)))
    except Exception:
        return False


def build_imported_target_pool(
    workspace_id: str,
    *,
    placeholder_path: str = "/drafts",
    merge_all: bool = True,
) -> Dict[str, Any]:
    """
    Imported Target Pool (WS ONLY, formats ONLY):
      - Reads ONLY ws-scoped inputs: imported_targets_<ws>.(csv|txt|xml)
      - Topic-only rows become placeholder URLs under placeholder_path.
      - Dedup by URL; prefer an explicit title/label when duplicates exist.
      - Output items: {url, label}
      - if active_target_set_<ws>.json exists, only keeps active imported URLs
    """
    ws = _clean(workspace_id)
    if not ws:
        raise ValueError("workspace_id is required")

    domain = _domain_from_sources_or_ws(ws)
    base = f"https://{domain}".rstrip("/")
    pp = "/" + str(placeholder_path or "/drafts").lstrip("/")
    pp = pp.rstrip("/")

    sources_used: List[str] = []
    per_source_counts: Dict[str, int] = {}
    all_pairs: List[Tuple[str, str]] = []

    def add_pairs(name: str, pairs: List[Tuple[str, str]]) -> None:
        if not pairs:
            return
        sources_used.append(name)
        per_source_counts[name] = len(pairs)
        all_pairs.extend(pairs)

    csv_fp = _csv_path(ws)
    txt_fp = _txt_path(ws)
    xml_fp = _xml_path(ws)

    if merge_all:
        if csv_fp.exists():
            add_pairs(str(csv_fp), _read_csv(csv_fp))
        if txt_fp.exists():
            add_pairs(str(txt_fp), _read_txt(txt_fp))
        if xml_fp.exists():
            add_pairs(str(xml_fp), _read_xml_sitemap(xml_fp))
    else:
        if csv_fp.exists():
            add_pairs(str(csv_fp), _read_csv(csv_fp))
        elif txt_fp.exists():
            add_pairs(str(txt_fp), _read_txt(txt_fp))
        elif xml_fp.exists():
            add_pairs(str(xml_fp), _read_xml_sitemap(xml_fp))

    if not all_pairs:
        raise FileNotFoundError(
            "No imported target inputs found (or all were empty). Looked for: "
            f"{csv_fp.name}, {txt_fp.name}, {xml_fp.name} in backend/server/data/"
        )

    active_fp = _active_target_set_path(ws)
    active_obj = _safe_read_json(active_fp) if active_fp.exists() else None
    active_imported_urls: List[str] = []

    if isinstance(active_obj, dict):
        raw_urls = active_obj.get("active_imported_urls") or []
        if isinstance(raw_urls, list):
            active_imported_urls = [_norm_url(str(x).strip()) for x in raw_urls if str(x).strip()]

    active_imported_url_set = set(active_imported_urls)

    placeholders_generated = 0
    rejection_audit: List[Dict[str, Any]] = []

    # Dedup map: url -> enriched imported target
    url_to_item: Dict[str, Dict[str, Any]] = {}

    for source_name, pairs in [
        (str(csv_fp), _read_csv(csv_fp) if csv_fp.exists() else []),
        (str(txt_fp), _read_txt(txt_fp) if txt_fp.exists() else []),
        (str(xml_fp), _read_xml_sitemap(xml_fp) if xml_fp.exists() else []),
    ]:
        import_source = _import_source_from_name(source_name)

        for title, url in pairs:
            raw_title = _clean(title)
            raw_url = _norm_url(url)
            placeholder_generated = False

            if (not _is_http_url(raw_url)) and raw_title:
                raw_url = f"{base}{pp}/{_slugify(raw_title)}"
                placeholders_generated += 1
                placeholder_generated = True

            if not _is_http_url(raw_url):
                rejection_audit.append({
                    "reason": "invalid_or_missing_url",
                    "title": raw_title,
                    "url": raw_url,
                    "import_source": import_source,
                })
                continue

            if not _host_matches_domain(raw_url, domain):
                rejection_audit.append({
                    "reason": "domain_mismatch",
                    "expected_domain": domain,
                    "title": raw_title,
                    "url": raw_url,
                    "import_source": import_source,
                })
                continue

            if "example.com" in raw_url.lower() or "openai.com" in raw_url.lower():
                rejection_audit.append({
                    "reason": "demo_or_test_url",
                    "title": raw_title,
                    "url": raw_url,
                    "import_source": import_source,
                })
                continue

            fallback_label = _slug_label_from_url(raw_url)
            label = _clean_label(raw_title) if raw_title else fallback_label
            title_value = _clean_label(raw_title) if raw_title else label

            if label.strip().lower() == "untitled":
                rejection_audit.append({
                    "reason": "untitled_label",
                    "title": raw_title,
                    "url": raw_url,
                    "import_source": import_source,
                })
                continue

            path = _path_from_url(raw_url)
            page_type = _page_type_hint(raw_url, label)
            bucket = _priority_bucket(raw_url, label, page_type)

            item = {
                "url": raw_url,
                "label": label,

                # RB2/scoring compatibility fields
                "title": title_value,
                "h1": title_value,
                "title_source": (
                    f"{import_source}_title"
                    if raw_title
                    else "slug_fallback"
                ),

                # Imported Target Pool v2 intelligence fields
                "source_type": "imported",
            "source_origin": "manual_import",
                "import_source": import_source,
                "page_type_hint": page_type,
                "priority_bucket": bucket,
                "path": path,
                "metadata": {
                    "builder_version": "imported_target_pool_v2",
                    "title_fallback_used": not bool(raw_title),
                    "placeholder_generated": placeholder_generated,
                    "source_file": source_name,
                },
            }

            existing = url_to_item.get(raw_url)
            if existing is None:
                url_to_item[raw_url] = item
            else:
                # Prefer explicit titles over fallback-derived labels.
                if raw_title and existing.get("metadata", {}).get("title_fallback_used"):
                    url_to_item[raw_url] = item

    filtered_urls = sorted(url_to_item.keys())

    # Safety rule:
    # Only restrict by active_imported_urls when the active list actually has URLs.
    # Never allow an empty active_imported_urls list to wipe the whole imported pool.
    if active_imported_url_set:
        filtered_urls = [u for u in filtered_urls if u in active_imported_url_set]

    items = [url_to_item[u] for u in filtered_urls]

    out: Dict[str, Any] = {
        "workspace_id": ws,
        "type": "imported",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "merge_all": bool(merge_all),
        "sources_used": sources_used,
        "per_source_counts": per_source_counts,
        "placeholder_path": pp,
        "domain": domain,
        "active_target_set_used": active_fp.exists(),
        "active_filter_applied": bool(active_imported_url_set),
        "active_imported_urls_count": len(active_imported_urls),
        "counts": {
            "rows_read_total": len(all_pairs),
            "placeholders_generated": placeholders_generated,
            "unique_urls_before_active_filter": len(url_to_item),
            "unique_urls_written": len(items),
            "rejected_rows": len(rejection_audit),
        },
        "rejected_examples": rejection_audit[:25],
        "rejection_audit": rejection_audit,
        "items": items,
    }

    out_fp = _pool_path(ws)
    out_fp.parent.mkdir(parents=True, exist_ok=True)
    out_fp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out