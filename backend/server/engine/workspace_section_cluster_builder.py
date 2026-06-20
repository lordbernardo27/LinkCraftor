
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    return here.parents[1] / "data"


def _safe_ws(workspace_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", str(workspace_id or "default")).strip("_") or "default"


def _read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _tokens(text: str) -> List[str]:
    stop = {
        "http", "https", "www", "com", "org", "net",
        "page", "html", "aspx", "article",
        "the", "and", "for", "with", "from", "into", "your",
    }

    return [
        t for t in re.findall(r"[a-z0-9]+", str(text or "").lower())
        if len(t) >= 3 and t not in stop
    ]


def _section_key_from_url(url: str) -> str:
    path = urlparse(str(url or "")).path
    parts = [
        p.replace("-", " ").replace("_", " ").strip()
        for p in path.split("/")
        if p.strip()
    ]

    if len(parts) >= 3:
        chosen = parts[:3]
    elif len(parts) >= 2:
        chosen = parts[:2]
    else:
        chosen = parts[:1]

    toks: List[str] = []
    for part in chosen:
        toks.extend(_tokens(part))

    return " ".join(toks[:4]).strip()


def build_workspace_section_clusters(workspace_id: str, min_urls_per_section: int = 2) -> Dict[str, Any]:
    ws = _safe_ws(workspace_id)

    pool_fp = _data_dir() / "target_pools" / "live_domain" / f"live_domain_target_pool_{ws}.json"
    pool = _read_json(pool_fp, {})
    items = pool.get("items") if isinstance(pool, dict) else []

    if not isinstance(items, list):
        items = []

    groups: Dict[str, Dict[str, Any]] = {}

    for item in items:
        if not isinstance(item, dict):
            continue

        url = str(item.get("url") or "").strip()
        title = str(item.get("title") or item.get("label") or "").strip()

        if not url:
            continue

        key = _section_key_from_url(url)
        if not key:
            continue

        section_id = "section_" + re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")

        group = groups.setdefault(section_id, {
            "section_id": section_id,
            "name": key,
            "keywords": [],
            "urls": [],
            "url_count": 0,
            "confidence": 0.50,
            "source": "workspace_section_cluster_builder_v1_path_sections",
        })

        group["urls"].append({
            "url": url,
            "title": title,
            "matched_terms": _tokens(key),
        })

        for t in _tokens(key + " " + title):
            if t not in group["keywords"]:
                group["keywords"].append(t)

    final_sections = {}

    for section_id, group in groups.items():
        group["url_count"] = len(group.get("urls") or [])

        if group["url_count"] < min_urls_per_section:
            continue

        group["confidence"] = round(min(0.86, max(0.50, group["url_count"] / 50)), 4)
        group["keywords"] = group["keywords"][:30]
        final_sections[section_id] = group

    out = {
        "workspace_id": ws,
        "type": "workspace_section_clusters",
        "version": "workspace_section_clusters_v1",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "section_count": len(final_sections),
        "sections": final_sections,
        "metadata": {
            "source": "live_domain_target_pool",
            "input_items": len(items),
            "min_urls_per_section": min_urls_per_section,
        },
    }

    out_fp = _data_dir() / "topic_clusters" / f"workspace_section_clusters_{ws}.json"
    out_fp.parent.mkdir(parents=True, exist_ok=True)
    out_fp.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    return out
