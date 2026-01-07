# backend/app/engine/external_local.py
from __future__ import annotations
from typing import List, Dict, Any

def run_external_local(anchor: str, context: str = "", limit: int = 8) -> List[Dict[str, Any]]:
    base = (anchor or "").strip()
    if not base:
        return []
    titled = base.title()
    items = [
        {
            "title": f"{titled} — Wikipedia",
            "url": f"https://en.wikipedia.org/wiki/{titled.replace(' ', '_')}",
            "domain": "wikipedia.org",
            "abstract": f"Overview page for {titled}.",
            "year": None,
            "score": 0.85,
        },
        {
            "title": f"{titled} (disambiguation) — Wikipedia",
            "url": f"https://en.wikipedia.org/wiki/{titled.replace(' ', '_')}_(disambiguation)",
            "domain": "wikipedia.org",
            "abstract": "Disambiguation page.",
            "year": None,
            "score": 0.78,
        },
    ]
    limit = max(1, min(int(limit or 8), 8))
    return items[:limit]
