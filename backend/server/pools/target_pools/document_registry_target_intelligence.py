from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    server_dir = here.parents[2]
    return server_dir / "data"


def _ws_safe(ws: str) -> str:
    raw = (ws or "default").strip()
    if not raw:
        return "default"
    if raw.lower().startswith("ws_"):
        return raw
    s = raw.lower().replace(".", "_").replace("-", "_").replace(" ", "_")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return f"ws_{s or 'workspace'}"[:80]


def _pool_path(workspace_id: str) -> Path:
    ws = _ws_safe(workspace_id)
    return (
        _data_dir()
        / "target_pools"
        / "document_registry"
        / f"document_registry_{ws}.json"
    )


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _norm_text(value: Any) -> str:
    s = str(value or "").lower()
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _tokens(value: Any) -> List[str]:
    return [t for t in _norm_text(value).split() if len(t) > 2]


def _jaccard(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / max(1, len(sa | sb))


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def load_document_registry_targets(workspace_id: str) -> List[Dict[str, Any]]:
    obj = _safe_read_json(_pool_path(workspace_id))
    if not isinstance(obj, dict):
        return []
    items = obj.get("items") or []
    if not isinstance(items, list):
        return []
    return [x for x in items if isinstance(x, dict)]


def semantic_route_score(phrase: str, target: Dict[str, Any]) -> float:
    phrase_tokens = _tokens(phrase)
    target_text = " ".join([
        str(target.get("title") or ""),
        str(target.get("label") or ""),
        str(target.get("h1") or ""),
    ])
    target_tokens = _tokens(target_text)

    score = _jaccard(phrase_tokens, target_tokens)

    phrase_norm = _norm_text(phrase)
    target_norm = _norm_text(target_text)

    if phrase_norm and phrase_norm in target_norm:
        score += 0.35

    if target_norm and target_norm in phrase_norm:
        score += 0.15

    return _clamp(score)


def semantic_intent_score(phrase: str, target: Dict[str, Any]) -> float:
    signals = target.get("semantic_intent_signals") or {}
    phrase_norm = _norm_text(phrase)

    score = 0.35

    if signals.get("has_tool_intent") and any(x in phrase_norm for x in ["calculator", "tool", "checker", "estimator"]):
        score += 0.25

    if signals.get("has_guide_intent") and any(x in phrase_norm for x in ["guide", "how", "what", "complete", "explained"]):
        score += 0.25

    if signals.get("has_question_intent") and any(x in phrase_norm.split() for x in ["how", "what", "why", "when", "where"]):
        score += 0.15

    return _clamp(score)


def authority_score(target: Dict[str, Any]) -> float:
    source = str(target.get("title_source") or "")
    if source in {"h1", "first_heading"}:
        return 0.82
    if source == "filename":
        return 0.62
    if source == "first_meaningful_line":
        return 0.55
    return 0.45


def topic_graph_score(phrase: str, target: Dict[str, Any]) -> float:
    # Lightweight graph proxy: shared title/heading tokens.
    return semantic_route_score(phrase, target)


def freshness_score(target: Dict[str, Any]) -> float:
    meta = target.get("metadata") or {}
    if meta.get("updated_at"):
        return 0.75
    if meta.get("uploaded_at"):
        return 0.68
    return 0.50


def transition_score(target: Dict[str, Any]) -> float:
    # Published URL is stronger; placeholder is still valid for editor cross-document links.
    if target.get("is_placeholder_url") is False:
        return 0.85
    if target.get("placeholder_url"):
        return 0.65
    return 0.40


def rb2_weight_score(target: Dict[str, Any]) -> float:
    bucket = str(target.get("priority_bucket") or "")
    if bucket == "published_cross_document_target":
        return 0.88
    if bucket == "strong_cross_document_target":
        return 0.78
    if bucket == "standard_cross_document_target":
        return 0.62
    return 0.42


def normalized_target_score(phrase: str, target: Dict[str, Any]) -> float:
    route = semantic_route_score(phrase, target)
    intent = semantic_intent_score(phrase, target)
    authority = authority_score(target)
    graph = topic_graph_score(phrase, target)
    fresh = freshness_score(target)
    transition = transition_score(target)
    rb2 = rb2_weight_score(target)

    score = (
        route * 0.34
        + intent * 0.14
        + authority * 0.14
        + graph * 0.12
        + fresh * 0.08
        + transition * 0.08
        + rb2 * 0.10
    )

    return _clamp(score)


def semantic_gate_allows(phrase: str, target: Dict[str, Any], min_score: float = 0.42) -> bool:
    if not phrase or not target:
        return False

    title = target.get("title") or target.get("label") or target.get("h1") or ""
    if not title:
        return False

    if target.get("source_type") != "document_registry":
        return False

    return normalized_target_score(phrase, target) >= min_score


def runtime_safe_payload(phrase: str, target: Dict[str, Any]) -> Dict[str, Any]:
    score = normalized_target_score(phrase, target)
    allowed = semantic_gate_allows(phrase, target)

    url = target.get("url") if allowed else ""

    return {
        "anchor": phrase,
        "url": url or "",
        "title": target.get("title") or "",
        "label": target.get("label") or target.get("title") or "",
        "source_type": "document_registry",
        "source_origin": target.get("source_origin") or "uploaded_editor_documents",
        "score": score,
        "allowed": allowed,
        "document_id": target.get("document_id") or "",
        "cross_document_linking": bool(target.get("cross_document_linking")),
        "is_placeholder_url": bool(target.get("is_placeholder_url")),
        "placeholder_url": target.get("placeholder_url") or "",
        "published_url": target.get("published_url") or "",
        "diagnostics": {
            "semantic_route_score": semantic_route_score(phrase, target),
            "semantic_intent_score": semantic_intent_score(phrase, target),
            "authority_score": authority_score(target),
            "topic_graph_score": topic_graph_score(phrase, target),
            "freshness_score": freshness_score(target),
            "transition_score": transition_score(target),
            "rb2_weight_score": rb2_weight_score(target),
            "semantic_gate_allowed": allowed,
        },
    }


def rank_document_registry_targets(
    phrase: str,
    workspace_id: str,
    limit: int = 10,
    exclude_document_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    targets = load_document_registry_targets(workspace_id)
    ranked: List[Dict[str, Any]] = []

    for target in targets:
        if exclude_document_id and str(target.get("document_id") or "") == str(exclude_document_id):
            continue

        payload = runtime_safe_payload(phrase, target)
        if payload["allowed"]:
            ranked.append(payload)

    ranked.sort(key=lambda x: x.get("score", 0), reverse=True)
    return ranked[:limit]


def diagnostics_for_document_registry_targets(workspace_id: str) -> Dict[str, Any]:
    targets = load_document_registry_targets(workspace_id)
    return {
        "workspace_id": _ws_safe(workspace_id),
        "source_type": "document_registry",
        "targets_loaded": len(targets),
        "has_runtime_safe_payloads": True,
        "supports_cross_document_linking": True,
        "supports_placeholder_url": True,
        "supports_published_url": True,
    }
