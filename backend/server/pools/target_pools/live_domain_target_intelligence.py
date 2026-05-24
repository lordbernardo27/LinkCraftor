from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    return here.parents[2] / "data"


def _pool_path(workspace_id: str) -> Path:
    return (
        _data_dir()
        / "target_pools"
        / "live_domain"
        / f"live_domain_target_pool_{workspace_id}.json"
    )


def _norm_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def _tokens(value: Any) -> set[str]:
    text = _norm_text(value)
    return {
        t
        for t in re.split(r"[^a-z0-9]+", text)
        if len(t) >= 3
    }


def load_live_domain_targets(workspace_id: str) -> List[Dict[str, Any]]:
    path = _pool_path(workspace_id)

    if not path.exists():
        return []

    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    items = obj.get("items") if isinstance(obj, dict) else []

    if not isinstance(items, list):
        return []

    return [x for x in items if isinstance(x, dict)]


def _page_type_weight(page_type: str) -> int:
    weights = {
        "how_to": 30,
        "guide": 28,
        "pillar": 26,
        "calculator": 24,
        "tool": 24,
        "article": 20,
        "blog": 18,
        "service": 16,
        "product": 16,
        "category": 10,
        "generic_content": 8,
    }

    return weights.get(str(page_type or "").strip(), 8)


def score_live_domain_target(
    phrase: str,
    target: Dict[str, Any],
) -> Dict[str, Any]:
    phrase_norm = _norm_text(phrase)

    title = target.get("title") or target.get("h1") or ""
    url = target.get("url") or ""
    page_type = target.get("page_type_hint") or "generic_content"
    priority_bucket = target.get("priority_bucket") or ""
    seed_match = bool(target.get("seed_path_match"))

    phrase_tokens = _tokens(phrase_norm)
    title_tokens = _tokens(title)
    url_tokens = _tokens(url.replace("-", " "))

    semantic_overlap = len(phrase_tokens & title_tokens)
    slug_overlap = len(phrase_tokens & url_tokens)

    semantic_route_score = semantic_overlap * 12
    topic_graph_score = (semantic_overlap + slug_overlap) * 8

    authority_score = 0
    if seed_match:
        authority_score += 20

    if priority_bucket == "seed_match":
        authority_score += 15

    if page_type in {"how_to", "guide", "pillar", "calculator", "tool"}:
        authority_score += 10

    rb2_weight_score = _page_type_weight(page_type)

    path = str(target.get("path") or "")
    clean_path = path.strip("/")
    path_depth = len([x for x in clean_path.split("/") if x]) if clean_path else 0

    path_score = (
        10 if path_depth <= 1
        else 6 if path_depth <= 3
        else 2
    )

    total_score = (
        semantic_route_score
        + topic_graph_score
        + authority_score
        + rb2_weight_score
        + path_score
    )

    return {
        "url": url,
        "title": title,
        "page_type_hint": page_type,
        "priority_bucket": priority_bucket,
        "seed_path_match": seed_match,
        "semantic_route_score": semantic_route_score,
        "authority_score": authority_score,
        "topic_graph_score": topic_graph_score,
        "rb2_weight_score": rb2_weight_score,
        "path_score": path_score,
        "target_score": total_score,
        "matched_title_tokens": sorted(phrase_tokens & title_tokens),
        "matched_url_tokens": sorted(phrase_tokens & url_tokens),
        "source_type": "live_domain",
    }


def rank_live_domain_targets(
    workspace_id: str,
    phrase: str,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    targets = load_live_domain_targets(workspace_id)

    scored = [
        score_live_domain_target(phrase, target)
        for target in targets
    ]

    scored.sort(
        key=lambda x: (
            x.get("target_score", 0),
            x.get("semantic_route_score", 0),
            x.get("authority_score", 0),
        ),
        reverse=True,
    )

    return scored[: max(1, int(limit or 5))]


def best_live_domain_target(
    workspace_id: str,
    phrase: str,
) -> Optional[Dict[str, Any]]:
    ranked = rank_live_domain_targets(workspace_id, phrase, limit=1)
    return ranked[0] if ranked else None