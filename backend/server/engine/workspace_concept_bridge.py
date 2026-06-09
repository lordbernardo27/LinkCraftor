from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    return here.parents[1] / "data"


def _safe_ws(workspace_id: str) -> str:
    ws = str(workspace_id or "default").strip()
    return ws if ws else "default"


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def _tokens(value: Any) -> set[str]:
    stop = {
        "a","an","and","are","as","at","be","by","for","from",
        "how","in","into","is","it","of","on","or","the","to",
        "what","when","where","why","with","your","you","this",
        "that","these","those"
    }
    return {
        t for t in re.findall(r"[a-z0-9]+", _norm(value))
        if len(t) >= 3 and t not in stop
    }


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def bridge_workspace_phrase_to_targets(
    workspace_id: str,
    phrase: str,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Workspace Concept Bridge v1.

    Generic fallback:
    - Uses active 2,000 site pages.
    - Uses token + cluster-style broad overlap.
    - Does NOT force a URL if evidence is weak.
    """

    ws = _safe_ws(workspace_id)
    data_dir = _data_dir()

    pages_fp = data_dir / f"site_pages_{ws}.json"
    pages = _read_json(pages_fp, {}).get("pages", {})

    phrase_norm = _norm(phrase)
    phrase_tokens = _tokens(phrase_norm)

    if not phrase_tokens or not isinstance(pages, dict):
        return []

    candidates: List[Dict[str, Any]] = []

    for url, rec in pages.items():
        if not isinstance(rec, dict):
            continue

        title = _norm(rec.get("title") or rec.get("h1") or "")
        h1 = _norm(rec.get("h1") or "")
        slug = _norm(str(url or "").replace("-", " ").replace("/", " "))

        target_text = " ".join([title, h1, slug])
        target_tokens = _tokens(target_text)

        if not target_tokens:
            continue

        overlap = phrase_tokens & target_tokens
        ratio = len(overlap) / max(1, len(phrase_tokens))

        exact = phrase_norm in target_text or title in phrase_norm

        score = 0.0
        if exact:
            score += 0.70
        score += ratio * 0.60

        # Strong two-token overlap is usually safe.
        if len(overlap) >= 2:
            score += 0.20

        # Reject weak one-token generic drift.
        if len(overlap) < 2 and score < 0.55:
            continue

        if score < 0.45:
            continue

        candidates.append({
            "url": url,
            "title": rec.get("title") or rec.get("h1") or url,
            "bridge_score": round(min(1.0, score), 4),
            "bridge_overlap_tokens": sorted(overlap),
            "bridge_reason": "workspace_concept_bridge_v1",
        })

    candidates.sort(key=lambda x: x["bridge_score"], reverse=True)
    return candidates[: max(1, int(limit or 5))]
