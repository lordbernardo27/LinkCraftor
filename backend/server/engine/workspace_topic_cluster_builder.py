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
        "http","https","www","com","org","net","whattoexpect",
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


def _broad_cluster_tokens() -> Set[str]:
    return {
        "baby", "babies", "pregnant", "pregnancy", "health", "children",
        "childrens", "toddler", "toddlers", "moms", "parents", "family",
        "women", "birth", "second", "another", "questions", "help",

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

    # 5. Taxonomy/listing/profile/search paths.
    if re.search(r"/(?:tag|tags|category|categories|author|profile|search|archive|archives)/", path):
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
        if not terms:
            continue

        token_counter.update(terms)
        item_terms.append({
            "url": item.get("url"),
            "title": item.get("title") or item.get("h1") or item.get("label") or item.get("url"),
            "terms": terms,
            "source_type": item.get("source_type") or "live_domain",
        })

    strong_tokens = {
        token for token, count in token_counter.items()
        if count >= min_token_frequency
    }

    clusters: Dict[str, Dict[str, Any]] = {}
    rejected_clusters: List[Dict[str, Any]] = []

    for token in strong_tokens:
        members = []
        evidence_terms = Counter()

        for row in item_terms:
            terms = row["terms"]
            if token not in terms:
                continue

            shared = sorted(list(terms & strong_tokens))[:20]
            evidence_terms.update(shared)

            members.append({
                "url": row["url"],
                "title": row["title"],
                "matched_terms": shared,
            })

        if len(members) < 2:
            continue

        top_terms = [t for t, _c in evidence_terms.most_common(20)]

        # Avoid very broad/noisy clusters.
        if len(members) > max_urls_per_cluster * 3:
            continue

        purity = _cluster_purity(token, top_terms, members)

        if purity.get("is_noisy"):
            rejected_clusters.append({
                "cluster_id": f"cluster_{token}",
                "name": token,
                "primary_token": token,
                "reason": "noisy_or_low_purity_cluster",
                "url_count": len(members),
                "keywords": top_terms[:20],
                "confidence": round(min(1.0, len(members) / 25), 4),
                "purity_score": purity.get("purity_score"),
                "primary_coverage": purity.get("primary_coverage"),
                "broad_terms": purity.get("broad_terms"),
                "source": "workspace_topic_cluster_builder_v2_purity",
            })
            continue

        cluster_id = f"cluster_{token}"
        clusters[cluster_id] = {
            "cluster_id": cluster_id,
            "name": token,
            "primary_token": token,
            "keywords": top_terms,
            "url_count": len(members),
            "urls": members[:max_urls_per_cluster],
            "confidence": round(min(1.0, len(members) / 25), 4),
            "purity_score": purity.get("purity_score"),
            "primary_coverage": purity.get("primary_coverage"),
            "broad_terms": purity.get("broad_terms"),
            "source": "workspace_topic_cluster_builder_v2_purity",
        }

    # Sort clusters by strength and keep top N.
    sorted_clusters = sorted(
        clusters.values(),
        key=lambda x: (float(x.get("confidence") or 0), int(x.get("url_count") or 0)),
        reverse=True,
    )[:max_clusters]

    final_clusters = {c["cluster_id"]: c for c in sorted_clusters}

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
