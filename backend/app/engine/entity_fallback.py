# backend/app/engine/entity_fallback.py
from __future__ import annotations
from typing import Dict

def wikipedia_fallback(anchor: str) -> Dict:
    slug = (anchor or "").strip().replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{slug}"
    return {
        "title": (anchor or "").strip().title(),
        "url": url,
        "domain": "wikipedia.org",
        "abstract": "(fallback) Wikipedia result constructed from anchor.",
        "year": None,
        "score": 0.50,
        "provider": "wikipedia",
        "id": f"wk:{slug.lower()}",
    }
