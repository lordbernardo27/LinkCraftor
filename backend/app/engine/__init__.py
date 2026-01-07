# backend/app/engine/__init__.py
from __future__ import annotations
from typing import Dict, List, Optional

def _domain_of(url: str) -> str:
    try:
        from urllib.parse import urlparse
        h = urlparse(url).hostname or ""
        parts = [p for p in h.split(".") if p]
        return h if len(parts) <= 2 else ".".join(parts[-2:])
    except Exception:
        return ""

def run_external_local(anchor: str, context: Optional[str] = None, limit: int = 8) -> List[Dict]:
    """
    Local external reference suggester.
    Returns a list of items with a stable contract:
    { title, url, domain, abstract, year, score, provider, id }
    """
    anchor = (anchor or "").strip()
    context = (context or "").strip()
    if not anchor:
        return []

    items: List[Dict] = []

    # (Your future logic can populate `items` here…)

    # Fallback: Wikipedia heuristic
    if not items:
        slug = anchor.strip().replace(" ", "_")
        url = f"https://en.wikipedia.org/wiki/{slug}"
        items = [{
            "title": anchor.title(),
            "url": url,
            "domain": _domain_of(url),
            "abstract": "(fallback) Wikipedia result constructed from anchor.",
            "year": None,
            "score": 0.50,
            "provider": "wikipedia",
            "id": f"wk:{slug.lower()}",
        }]

    # Trim and coerce to the contract
    out: List[Dict] = []
    for i in items[: max(1, int(limit or 1))]:
        title   = str(i.get("title") or "").strip()
        url     = str(i.get("url") or "").strip()
        domain  = str(i.get("domain") or _domain_of(url)).strip()
        abstract= str(i.get("abstract") or "").strip()
        year    = i.get("year", None)
        score   = float(i.get("score") or 0.0)
        provider= str(i.get("provider") or domain or "").lower() or None
        rid     = str(i.get("id") or "").strip() or None

        out.append({
            "title": title,
            "url": url,
            "domain": domain,
            "abstract": abstract,
            "year": year if (isinstance(year, int) or year is None) else None,
            "score": score,
            "provider": provider,
            "id": rid,
        })
    return out

# Re-export the entity helpers for easy imports
from .entity_map import build_entity_map, normalize_entity, wikipedia_fallback  # noqa: E402
