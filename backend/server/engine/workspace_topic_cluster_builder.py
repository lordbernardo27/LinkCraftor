from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

from backend.server.engine.workspace_topic_cluster_store import (
    normalize_topic_text,
    save_workspace_topic_clusters,
)


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    return here.parents[1] / "data"


def _safe_ws(workspace_id: str) -> str:
    ws = str(workspace_id or "default").strip()
    return ws if ws else "default"


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _tokens(text: Any) -> List[str]:
    stop = {
        "a","an","and","are","as","at","be","by","for","from","how","into",
        "in","is","it","of","on","or","the","to","what","when","where","why",
        "with","your","you","this","that","these","those","can","will","may",
        "new","old","best","top","guide","tips","article","aspx","html","page",
        "during","after","before","about","more","howto","learn",
        "http","https","www","com","org","net",
        "products","product","ask","heidi","getting","first","year",
        "today","survey","list","start",
        "care","month","week","well","like","have","while"
    }

    return [
        t for t in re.findall(r"[a-z0-9]+", normalize_topic_text(text))
        if len(t) >= 3 and t not in stop
    ]


def _target_terms(item: Dict[str, Any]) -> Set[str]:
    parts: List[str] = []

    for k in ("title", "h1", "label", "path", "url"):
        parts.append(str(item.get(k) or ""))

    for k in ("matched_phrases", "aliases"):
        vals = item.get(k) or []
        if isinstance(vals, list):
            parts.extend(str(v or "") for v in vals)

    return set(_tokens(" ".join(parts)))


def _dedupe_consecutive_tokens(tokens: List[str]) -> List[str]:
    out: List[str] = []
    for t in tokens:
        if not out or out[-1] != t:
            out.append(t)
    return out


def _is_bad_phrase_label(phrase: str) -> bool:
    toks = phrase.split()
    if len(toks) < 2:
        return True

    if len(set(toks)) < len(toks):
        return True

    broad = _broad_cluster_tokens()
    if toks[-1] in broad:
        return True

    weak_endings = {
        "info", "guide", "tips", "page", "article", "review", "reviews",
        "know", "should", "things", "good", "best", "top", "time",
    }
    if toks[-1] in weak_endings:
        return True

    # Reject phrases made only of broad words.
    if set(toks).issubset(broad):
        return True

    return False


def _canonical_cluster_phrase(phrase: str) -> str:
    """
    Universal topic-entity canonicalizer.
    Converts noisy phrase variants into stable topic labels.
    Not niche-specific.
    """
    toks = [t for t in str(phrase or "").lower().split() if t]

    if len(toks) < 2:
        return ""

    broad_prefix = {
        "health", "general", "basic", "common", "main", "major",
        "best", "top", "new", "old", "good", "bad",
        "baby", "babies", "child", "children", "toddler", "toddlers",
        "pregnancy", "pregnant", "family", "parent", "parents",
    }

    weak_tokens = {
        "whattoexpect", "info", "information", "guide", "tips", "article",
        "page", "review", "reviews", "know", "should", "things", "someone",
        "told", "had", "much", "get", "make", "use", "using", "used",
        "ways", "about", "during", "before", "after",
    }

    toks = [t for t in toks if t not in weak_tokens]

    while len(toks) > 2 and toks[0] in broad_prefix:
        toks = toks[1:]

    if len(toks) < 2:
        return ""

    # Remove duplicate tokens while preserving order.
    deduped = []
    for t in toks:
        if t not in deduped:
            deduped.append(t)
    toks = deduped

    if len(toks) < 2:
        return ""

    # Normalize reversed 2-token variants:
    # "development fetal" -> "fetal development"
    preferred_heads = {
        "fetal", "prenatal", "postpartum", "sleep", "fertility",
        "breast", "pelvic", "gender", "baby", "toddler",
        "labor", "delivery", "childhood", "pregnancy",
    }

    if len(toks) == 2:
        a, b = toks
        if b in preferred_heads and a not in preferred_heads:
            toks = [b, a]

    # Prefer compact 2-word topic labels unless the 3rd word is important.
    important_third = {
        "testing", "training", "treatments", "symptoms", "complications",
        "development", "screening", "schedule", "regression", "supply",
        "therapy", "announcement", "leave",
    }

    if len(toks) >= 3:
        if toks[2] in important_third:
            toks = toks[:3]
        else:
            toks = toks[:2]

    phrase = " ".join(toks).strip()

    universal_replacements = {
        "development fetal": "fetal development",
        "screenings tests": "screening tests",
        "tests treatments": "treatments",
        "testing tests": "testing",
        "sex relationships": "relationships",
        "health postpartum": "postpartum health",
        "health sex": "sexual health",
        "postpartum health sex": "postpartum sexual health",
        "diapering potty": "potty training",
        "training potty": "potty training",
        "toddler potty": "potty training",
    }

    phrase = universal_replacements.get(phrase, phrase)

    if not phrase or _is_bad_phrase_label(phrase):
        return ""

    return phrase


def _phrase_candidates(item: Dict[str, Any]) -> Set[str]:
    """
    Universal canonical phrase extractor for topic clustering.
    Uses titles/slugs to produce stable 2-3 word topic phrases.
    Avoids sliding-window loops like "sleep regression sleep".
    """
    raw_parts: List[str] = []

    for k in ("title", "h1", "label"):
        val = str(item.get(k) or "").strip()
        if val:
            raw_parts.append(val)

    path = str(item.get("path") or "")
    if path:
        raw_parts.append(path.replace("/", " ").replace("-", " ").replace("_", " "))

    for k in ("matched_phrases", "aliases"):
        vals = item.get(k) or []
        if isinstance(vals, list):
            raw_parts.extend(str(v or "") for v in vals if str(v or "").strip())

    out: Set[str] = set()

    for raw in raw_parts:
        clean = re.sub(r"\.aspx\b", " ", str(raw), flags=re.I)
        clean = re.sub(r"\b\d+\b", " ", clean)
        toks = _dedupe_consecutive_tokens(_tokens(clean))

        if len(toks) < 2:
            continue

        # Prefer first meaningful 2-word and 3-word title phrases.
        for n in (2, 3):
            if len(toks) >= n:
                phrase = " ".join(toks[:n]).strip()
                if not _is_bad_phrase_label(phrase):
                    out.add(phrase)

        # Also allow adjacent phrase pairs where both tokens are meaningful.
        for i in range(0, max(0, len(toks) - 1)):
            phrase = " ".join(toks[i:i+2]).strip()
            if not _is_bad_phrase_label(phrase):
                out.add(phrase)

    return out


def _broad_cluster_tokens() -> Set[str]:
    return {
        # Broad audience/domain words. These are allowed as keywords,
        # but too broad to become cluster labels.
        "baby", "babies", "pregnant", "pregnancy", "health", "children",
        "childrens", "toddler", "toddlers", "moms", "parents", "family",
        "women", "birth",

        "second", "another", "questions", "help",

        # Universal weak cluster labels.
        "review", "reviews", "reviewer", "reviewers",
        "info", "information", "know", "should", "high", "big",
        "expect", "date", "due", "one", "get", "time", "things",
        "someone", "told", "had", "good", "much",

        # Generic/broad cluster names that are too weak for auto-linking.
        "names", "name", "solutions", "solution", "kids", "kid",
        "girl", "girls", "boy", "boys", "common", "unique",

        # Universal weak action/utility cluster names.
        "calculate", "calculating", "calculator", "calculations",
        "result", "results", "estimate", "estimated", "checker",
        "generator", "finder", "planner", "search", "filter",
        "sort", "listing", "index", "archive", "archives",
    }


def _cluster_purity(primary_token: str, top_terms: List[str], members: List[Dict[str, Any]]) -> Dict[str, Any]:
    broad = _broad_cluster_tokens()
    terms = [str(t or "").strip().lower() for t in top_terms if str(t or "").strip()]
    broad_hits = [t for t in terms if t in broad]

    member_count = max(1, len(members))
    primary_hits = 0
    for m in members:
        mt = set(str(x or "").strip().lower() for x in (m.get("matched_terms") or []))
        if primary_token in mt:
            primary_hits += 1

    primary_coverage = primary_hits / member_count
    broad_penalty = min(0.55, len(broad_hits) * 0.08)

    purity = max(0.0, min(1.0, primary_coverage - broad_penalty))

    return {
        "purity_score": round(purity, 4),
        "primary_coverage": round(primary_coverage, 4),
        "broad_terms": broad_hits[:12],
        "is_noisy": bool(primary_token in broad or purity < 0.70),
    }



def _is_utility_or_result_target(item: Dict[str, Any]) -> bool:
    """
    Universal cluster-only suppressor.

    Prevents utility/listing/generated-result pages from forming topic clusters.
    Does NOT delete targets from the live-domain target pool.
    """
    url = str(item.get("url") or "").lower()
    path = str(item.get("path") or "").lower()
    title = str(item.get("title") or item.get("h1") or item.get("label") or "").lower()
    hint = str(item.get("page_type_hint") or "").lower()

    text = " ".join([url, path, title, hint])

    # 1. Explicit utility/result hints.
    utility_hints = {
        "calculator_result",
        "generated_result",
        "result_page",
        "search",
        "search_results",
        "archive",
        "tag",
        "taxonomy",
        "author",
        "profile",
        "pagination",
        "listing",
        "index",
    }
    if hint in utility_hints:
        return True

    # 2. Generated result paths across niches:
    # /calculator/result/x, /tools/result/x, /quiz/results/x, etc.
    if re.search(r"/(?:result|results|output|estimate|calculator-result|generated)/", path):
        if re.search(r"/(?:calculator|tool|tools|quiz|test|checker|estimator|generator|predictor|finder|planner)[^/]*/", path):
            return True

    # 3. Calendar/date archive or generated date-result pages.
    if re.search(r"/(?:19|20)\d{2}/(?:0?[1-9]|1[0-2])(?:/|$)", path):
        return True

    if re.search(r"/(?:january|february|march|april|may|june|july|august|september|october|november|december)[-_]?\d{1,2}(?:/|$)", path):
        return True

    # 4. Pagination/list pages.
    if re.search(r"/(?:page|p)/\d+(?:/|$)", path):
        return True

    if re.search(r"(?:\?|&)(?:page|paged|sort|filter|orderby|view|ref|utm_)", url):
        return True

    # 5. Taxonomy/listing/profile/search/entity pages.
    if re.search(
        r"/(?:tag|tags|category|categories|author|authors|reviewer|reviewers|profile|profiles|team|staff|member|members|search|archive|archives)/",
        path,
    ):
        return True

    # 6. Thin generated slugs dominated by generic utility words.
    generic_tokens = set(_tokens(text))
    weak_terms = {
        "result", "results", "calculator", "calculate", "calculating",
        "search", "page", "archive", "tag", "category", "author",
        "filter", "sort", "index", "listing"
    }
    if generic_tokens and len(generic_tokens & weak_terms) >= 2 and len(generic_tokens) <= 8:
        return True

    return False

def _cluster_history_path(workspace_id: str) -> Path:
    return _data_dir() / "topic_clusters" / f"workspace_topic_cluster_history_{_safe_ws(workspace_id)}.json"


def _append_cluster_history(workspace_id: str, snapshot: Dict[str, Any]) -> None:
    path = _cluster_history_path(workspace_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    history = _read_json(path, {"workspace_id": _safe_ws(workspace_id), "history": []})
    if not isinstance(history, dict):
        history = {"workspace_id": _safe_ws(workspace_id), "history": []}

    rows = history.get("history")
    if not isinstance(rows, list):
        rows = []

    rows.append({
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "cluster_count": snapshot.get("cluster_count", 0),
        "rejected_cluster_count": len(snapshot.get("rejected_clusters") or []),
        "noisy_cluster_count": len(snapshot.get("noisy_clusters") or []),
        "metadata": snapshot.get("metadata") or {},
    })

    history["workspace_id"] = _safe_ws(workspace_id)
    history["history"] = rows[-100:]

    path.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")




def _topic_cluster_quality_gate(cluster: Dict[str, Any]) -> bool:
    name = str(cluster.get("name") or "").lower().strip()
    toks = _tokens(name)
    urls = cluster.get("urls") or []
    url_count = int(cluster.get("url_count") or len(urls) or 0)

    if url_count < 5:
        return False

    bad_tokens = {
        "whose", "keeping", "real", "advice", "solutions", "starting",
        "issues", "someone", "told", "had", "thing", "things", "day",
        "out", "get", "make", "use", "using", "used", "know", "should",
        "high", "big", "good", "best", "top", "info", "information",
    }

    if any(t in bad_tokens for t in toks):
        return False

    # Require phrase evidence in at least one member title.
    for u in urls:
        title_tokens = set(_tokens(u.get("title") or ""))
        if toks and set(toks).issubset(title_tokens):
            return True

    return False


def _cluster_merge_key(cluster: Dict[str, Any]) -> str:
    name = str(cluster.get("name") or "").lower().strip()
    toks = [t for t in _tokens(name) if t not in _broad_cluster_tokens()]

    if len(toks) >= 2:
        return "_".join(sorted(toks[:3]))

    kws = [
        t for t in (cluster.get("keywords") or [])
        if t not in _broad_cluster_tokens()
    ]

    return "_".join(sorted(kws[:3]))


def _postprocess_topic_clusters(
    clusters: Dict[str, Dict[str, Any]],
    rejected_clusters: List[Dict[str, Any]],
    max_clusters: int,
) -> Dict[str, Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}

    for c in clusters.values():
        if not _topic_cluster_quality_gate(c):
            rejected_clusters.append({
                "cluster_id": c.get("cluster_id"),
                "name": c.get("name"),
                "reason": "failed_topic_quality_gate",
                "url_count": c.get("url_count"),
                "keywords": c.get("keywords") or [],
                "source": "workspace_topic_cluster_builder_v4_quality_gate",
            })
            continue

        key = _cluster_merge_key(c)
        if not key:
            continue

        if key not in merged:
            merged[key] = dict(c)
            merged[key]["source"] = "workspace_topic_cluster_builder_v4_phrase_quality_merge"
            continue

        existing = merged[key]

        seen = {x.get("url") for x in existing.get("urls", []) if isinstance(x, dict)}
        combined_urls = list(existing.get("urls") or [])

        for u in c.get("urls") or []:
            if not isinstance(u, dict):
                continue
            url = u.get("url")
            if url and url not in seen:
                combined_urls.append(u)
                seen.add(url)

        keyword_counter = Counter()
        keyword_counter.update(existing.get("keywords") or [])
        keyword_counter.update(c.get("keywords") or [])

        existing["urls"] = combined_urls
        existing["url_count"] = len(combined_urls)
        existing["keywords"] = [k for k, _ in keyword_counter.most_common(20)]
        existing["confidence"] = round(min(1.0, len(combined_urls) / 25), 4)

    sorted_clusters = sorted(
        merged.values(),
        key=lambda x: (float(x.get("confidence") or 0), int(x.get("url_count") or 0)),
        reverse=True,
    )[:max_clusters]

    return {c["cluster_id"]: c for c in sorted_clusters}



def build_workspace_topic_clusters(
    workspace_id: str,
    min_token_frequency: int = 3,
    max_clusters: int = 80,
    max_urls_per_cluster: int = 80,
) -> Dict[str, Any]:
    ws = _safe_ws(workspace_id)
    data_dir = _data_dir()

    live_pool_fp = data_dir / "target_pools" / "live_domain" / f"live_domain_target_pool_{ws}.json"
    live_pool = _read_json(live_pool_fp, {}).get("items", [])

    if not isinstance(live_pool, list):
        live_pool = []

    phrase_counter: Counter = Counter()
    token_counter: Counter = Counter()
    item_terms: List[Dict[str, Any]] = []
    utility_result_targets_skipped = 0

    for item in live_pool:
        if not isinstance(item, dict):
            continue

        if _is_utility_or_result_target(item):
            utility_result_targets_skipped += 1
            continue

        terms = _target_terms(item)
        raw_phrases = _phrase_candidates(item)
        phrases = {
            p for p in (_canonical_cluster_phrase(x) for x in raw_phrases)
            if p
        }

        if not terms and not phrases:
            continue

        token_counter.update(terms)
        phrase_counter.update(phrases)

        item_terms.append({
            "url": item.get("url"),
            "title": item.get("title") or item.get("h1") or item.get("label") or item.get("url"),
            "terms": terms,
            "phrases": phrases,
            "source_type": item.get("source_type") or "live_domain",
        })

    strong_phrases = {
        phrase for phrase, count in phrase_counter.items()
        if count >= min_token_frequency
    }

    strong_tokens = {
        token for token, count in token_counter.items()
        if count >= min_token_frequency
    }

    clusters: Dict[str, Dict[str, Any]] = {}
    rejected_clusters: List[Dict[str, Any]] = []

    for phrase in strong_phrases:
        phrase_tokens = set(phrase.split())
        members = []
        evidence_terms = Counter()

        for row in item_terms:
            phrases = row.get("phrases") or set()
            terms = row.get("terms") or set()

            if phrase not in phrases:
                continue

            shared_tokens = sorted(list((terms & strong_tokens) | phrase_tokens))[:20]
            evidence_terms.update(shared_tokens)

            members.append({
                "url": row["url"],
                "title": row["title"],
                "matched_terms": shared_tokens,
                "matched_phrase": phrase,
            })

        if len(members) < 2:
            continue

        top_terms = [t for t, _c in evidence_terms.most_common(20)]

        if len(members) > max_urls_per_cluster * 3:
            continue

        primary_token = phrase.split()[-1] if phrase.split() else phrase
        purity = _cluster_purity(primary_token, top_terms, members)

        if purity.get("is_noisy"):
            rejected_clusters.append({
                "cluster_id": f"cluster_{phrase.replace(' ', '_')}",
                "name": phrase,
                "primary_token": primary_token,
                "reason": "noisy_or_low_purity_phrase_cluster",
                "url_count": len(members),
                "keywords": top_terms[:20],
                "confidence": round(min(1.0, len(members) / 25), 4),
                "purity_score": purity.get("purity_score"),
                "primary_coverage": purity.get("primary_coverage"),
                "broad_terms": purity.get("broad_terms"),
                "source": "workspace_topic_cluster_builder_v3_phrase_based",
            })
            continue

        cluster_id = f"cluster_{phrase.replace(' ', '_')}"
        clusters[cluster_id] = {
            "cluster_id": cluster_id,
            "name": phrase,
            "primary_token": primary_token,
            "keywords": top_terms,
            "url_count": len(members),
            "urls": members[:max_urls_per_cluster],
            "confidence": round(min(1.0, len(members) / 25), 4),
            "purity_score": purity.get("purity_score"),
            "primary_coverage": purity.get("primary_coverage"),
            "broad_terms": purity.get("broad_terms"),
            "source": "workspace_topic_cluster_builder_v3_phrase_based",
        }

    # Quality gate + duplicate merge + final top-N selection.
    final_clusters = _postprocess_topic_clusters(
        clusters,
        rejected_clusters,
        max_clusters,
    )

    # Fallback topical clusters:
    # Strict phrase clusters are high-precision but low-coverage.
    # This adds universal title/path-based clusters for pages not already clustered.
    clustered_urls = set()
    for c in final_clusters.values():
        for u in c.get("urls") or []:
            if isinstance(u, dict) and u.get("url"):
                clustered_urls.add(str(u.get("url")).rstrip("/"))

    fallback_groups: Dict[str, Dict[str, Any]] = {}

    for row in item_terms:
        url = str(row.get("url") or "").rstrip("/")
        title = str(row.get("title") or "")
        terms = set(row.get("terms") or [])

        if not url or url in clustered_urls:
            continue

        usable_terms = [
            t for t in terms
            if t not in _broad_cluster_tokens()
            and len(t) >= 4
        ]

        if len(usable_terms) < 2:
            continue

        # Build a stable fallback key from the strongest first terms.
        key_terms = sorted(usable_terms)[:2]
        cluster_key = " ".join(key_terms).strip()

        if not cluster_key:
            continue

        c = fallback_groups.setdefault(cluster_key, {
            "cluster_id": "fallback_cluster_" + re.sub(r"[^a-z0-9]+", "_", cluster_key.lower()).strip("_"),
            "name": cluster_key,
            "primary_token": cluster_key,
            "keywords": [],
            "urls": [],
            "url_count": 0,
            "confidence": 0.45,
            "purity_score": 0.65,
            "primary_coverage": 0.65,
            "broad_terms": [],
            "source": "workspace_topic_cluster_builder_v5_fallback_title_path",
        })

        c["urls"].append({
            "url": url,
            "title": title,
            "matched_terms": key_terms,
        })

        for t in usable_terms[:12]:
            if t not in c["keywords"]:
                c["keywords"].append(t)

    # Keep fallback clusters only if they have enough members.
    for key, c in fallback_groups.items():
        c["url_count"] = len(c.get("urls") or [])
        if c["url_count"] < 3:
            continue

        c["confidence"] = round(min(0.78, max(0.45, c["url_count"] / 30)), 4)

        if c["cluster_id"] not in final_clusters:
            final_clusters[c["cluster_id"]] = c

    # Path-section fallback clusters:
    # Universal fallback for pages that share the same URL section.
    # Example:
    # /getting-pregnant/ovulation/late-ovulation
    # -> getting pregnant ovulation
    path_groups: Dict[str, Dict[str, Any]] = {}

    clustered_urls = set()
    for c in final_clusters.values():
        for u in c.get("urls") or []:
            if isinstance(u, dict) and u.get("url"):
                clustered_urls.add(str(u.get("url")).rstrip("/"))

    for row in item_terms:
        url = str(row.get("url") or "").rstrip("/")
        title = str(row.get("title") or "")

        if not url or url in clustered_urls:
            continue

        try:
            from urllib.parse import urlparse
            path_parts = [
                part.replace("-", " ").replace("_", " ").strip()
                for part in urlparse(url).path.split("/")
                if part.strip()
            ]
        except Exception:
            path_parts = []

        if len(path_parts) < 2:
            continue

        # Use first 2-3 meaningful path sections.
        raw_section_terms = []
        for part in path_parts[:3]:
            toks = [
                t for t in _tokens(part)
                if t not in _broad_cluster_tokens()
                and len(t) >= 3
            ]
            if toks:
                raw_section_terms.extend(toks)

        if len(raw_section_terms) < 2:
            continue

        section_terms = raw_section_terms[:3]
        cluster_key = " ".join(section_terms).strip()

        if not cluster_key:
            continue

        c = path_groups.setdefault(cluster_key, {
            "cluster_id": "path_cluster_" + re.sub(r"[^a-z0-9]+", "_", cluster_key.lower()).strip("_"),
            "name": cluster_key,
            "primary_token": cluster_key,
            "keywords": [],
            "urls": [],
            "url_count": 0,
            "confidence": 0.42,
            "purity_score": 0.60,
            "primary_coverage": 0.60,
            "broad_terms": [],
            "source": "workspace_topic_cluster_builder_v6_path_section_fallback",
        })

        c["urls"].append({
            "url": url,
            "title": title,
            "matched_terms": section_terms,
        })

        for t in section_terms:
            if t not in c["keywords"]:
                c["keywords"].append(t)

    for key, c in path_groups.items():
        c["url_count"] = len(c.get("urls") or [])

        if c["url_count"] < 3:
            continue

        c["confidence"] = round(min(0.74, max(0.42, c["url_count"] / 40)), 4)

        if c["cluster_id"] not in final_clusters:
            final_clusters[c["cluster_id"]] = c


    # Re-sort and cap.
    final_sorted = sorted(
        final_clusters.values(),
        key=lambda x: (float(x.get("confidence") or 0), int(x.get("url_count") or 0)),
        reverse=True,
    )[:max_clusters]

    final_clusters = {c["cluster_id"]: c for c in final_sorted}


    out = {
        "workspace_id": ws,
        "type": "workspace_topic_clusters",
        "cluster_count": len(final_clusters),
        "clusters": final_clusters,
        "rejected_clusters": rejected_clusters,
        "noisy_clusters": rejected_clusters,
        "metadata": {
            "source": "live_domain_target_pool",
            "version": "workspace_topic_clusters_v2_purity",
            "min_token_frequency": min_token_frequency,
            "max_clusters": max_clusters,
            "utility_result_targets_skipped": utility_result_targets_skipped,
            "cluster_input_items_after_utility_filter": len(item_terms),
        },
    }

    _append_cluster_history(ws, out)
    return save_workspace_topic_clusters(ws, out)
