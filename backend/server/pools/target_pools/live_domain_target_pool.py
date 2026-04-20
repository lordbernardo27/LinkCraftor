# backend/server/pools/target_pools/live_domain_target_pool.py

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse

from backend.server.utils.text_normalization import fix_mojibake_text


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    server_dir = here.parents[2]  # .../backend/server
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
    if u.endswith("/"):
        u = u[:-1]
    return u


def _norm_seed_path(p: str) -> str:
    p = (p or "").strip()
    if not p:
        return ""
    if not p.startswith("/"):
        p = "/" + p
    p = p.rstrip("/")
    return p or ""


def _path_matches_seed_paths(url: str, seed_paths: List[str]) -> bool:
    if not seed_paths:
        return True

    try:
        path = (urlparse(url).path or "/").rstrip("/")
    except Exception:
        return False

    for sp in seed_paths:
        if not sp:
            continue

        if path == sp:
            return True

        if path.startswith(sp + "/"):
            return True

        if sp.endswith("-") and path.startswith(sp):
            return True

    return False


def build_live_domain_target_pool(workspace_id: str) -> Dict[str, Any]:
    """
    Live Domain Target Pool (FAST + STRICT BLOG ONLY):
      - Candidate URLs come from site_sources_<ws>.json -> sources[].sitemap_urls
      - We then enforce blog-only using sources[].seed_paths (e.g. ['/blog'])
      - H1 comes from site_pages_<ws>.json -> pages[url].h1
      - Output items are ONLY: {url, h1}
      - if active_target_set_<ws>.json exists, only keeps active live-domain URLs
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
                _norm_url(str(x).strip()) for x in raw_urls if str(x).strip()
            ]

    active_live_domain_url_set = set(active_live_domain_urls)

    sources = sources_obj.get("sources") or []
    if not isinstance(sources, list):
        sources = []

    pages = pages_obj.get("pages") or {}
    if not isinstance(pages, dict):
        pages = {}

    candidate_urls: List[str] = []
    seed_paths: List[str] = []

    for s in sources:
        if not isinstance(s, dict):
            continue

        sp = s.get("seed_paths") or []
        if isinstance(sp, list):
            for x in sp:
                nx = _norm_seed_path(str(x or ""))
                if nx:
                    seed_paths.append(nx)

        arr = s.get("sitemap_urls") or []
        if isinstance(arr, list) and arr:
            candidate_urls.extend(
                [str(u or "").strip() for u in arr if str(u or "").strip()]
            )

    sp_seen: set[str] = set()
    seed_paths = [p for p in seed_paths if p and (p not in sp_seen and not sp_seen.add(p))]

    seen_u: set[str] = set()
    candidate_urls = [
        u
        for u in candidate_urls
        if u and (_norm_url(u) not in seen_u and not seen_u.add(_norm_url(u)))
    ]

    before_seed_filter = len(candidate_urls)
    candidate_urls = [
        _norm_url(u) for u in candidate_urls if _path_matches_seed_paths(u, seed_paths)
    ]
    after_seed_filter = len(candidate_urls)

    before_active_filter = len(candidate_urls)
    if active_fp.exists():
        candidate_urls = [u for u in candidate_urls if u in active_live_domain_url_set]
    after_active_filter = len(candidate_urls)

    items: List[Dict[str, str]] = []
    missing_h1 = 0

    for u in candidate_urls:
        nu = _norm_url(u)
        rec = pages.get(u) or pages.get(nu) or pages.get(nu + "/") or {}
        h1 = (rec.get("h1") if isinstance(rec, dict) else "") or ""
        h1 = fix_mojibake_text(str(h1).strip())
        if not h1:
            missing_h1 += 1
            continue
        items.append({"url": nu, "h1": h1})

    out: Dict[str, Any] = {
        "workspace_id": ws,
        "type": "live",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "site_sources.sitemap_urls + seed_paths enforcement (blog only)",
        "seed_paths": seed_paths,
        "active_target_set_used": active_fp.exists(),
        "active_live_domain_urls_count": len(active_live_domain_urls),
        "counts": {
            "candidate_urls_before_seed_paths": before_seed_filter,
            "candidate_urls_after_seed_paths": after_seed_filter,
            "candidate_urls_before_active_filter": before_active_filter,
            "candidate_urls_after_active_filter": after_active_filter,
            "missing_h1": missing_h1,
            "items_written": len(items),
        },
        "items": items,
    }

    out_fp = _pool_path(ws)
    out_fp.parent.mkdir(parents=True, exist_ok=True)
    out_fp.write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return out