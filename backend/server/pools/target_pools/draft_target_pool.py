# backend/server/pools/target_pools/draft_target_pool.py

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    server_dir = here.parents[2]  # .../backend/server
    return server_dir / "data"


def _pool_path(ws: str) -> Path:
    return _data_dir() / "target_pools" / "draft" / f"draft_target_pool_{ws}.json"


# Draft import can be CSV or TXT. We will read *topics* from them.
def _draft_csv_path(ws: str) -> Path:
    return _data_dir() / f"draft_targets_{ws}.csv"


def _draft_txt_path(ws: str) -> Path:
    return _data_dir() / f"draft_targets_{ws}.txt"


def _site_sources_path(ws: str) -> Path:
    return _data_dir() / f"site_sources_{ws}.json"


def _active_target_set_path(ws: str) -> Path:
    return _data_dir() / "target_pools" / f"active_target_set_{ws}.json"


def _clean(s: str) -> str:
    return str(s or "").strip().strip("\ufeff").strip()


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _domain_from_sources_or_ws(ws: str) -> str:
    """
    Prefer site_sources_<ws>.json -> sources[0].domain
    Fallback: ws_betterhealthcheck_com -> betterhealthcheck.com
    """
    fp = _site_sources_path(ws)
    if fp.exists():
        try:
            obj = json.loads(fp.read_text(encoding="utf-8"))
            arr = obj.get("sources") or []
            if isinstance(arr, list) and arr:
                dom = str((arr[0] or {}).get("domain") or "").strip().lower()
                dom = dom[4:] if dom.startswith("www.") else dom
                if dom:
                    return dom
        except Exception:
            pass

    s = ws
    if s.startswith("ws_"):
        s = s[3:]
    return s.replace("_", ".").strip(".").lower()


_slug_re = re.compile(r"[^a-z0-9]+")


def _slugify(topic: str) -> str:
    t = _clean(topic).lower()
    t = _slug_re.sub("-", t)
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t or "draft"


def _read_topics_from_csv(fp: Path) -> List[str]:
    """
    CSV supported formats:
      - Title
      - Title,URL  (URL ignored)
    Header row optional: Title,URL or Topic,URL
    """
    out: List[str] = []
    with fp.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if not row:
                continue

            c0 = _clean(row[0]) if len(row) >= 1 else ""
            c1 = _clean(row[1]) if len(row) >= 2 else ""

            if i == 0 and c0.lower() in {"title", "topic"}:
                continue
            if i == 0 and c0.lower() in {"title", "topic"} and c1.lower() in {"url", "link"}:
                continue

            if c0:
                out.append(c0)
    return out


def _read_topics_from_txt(fp: Path) -> List[str]:
    """
    TXT supported formats:
      - One topic per line
      - Or "Title,URL" per line (URL ignored)
    """
    out: List[str] = []
    for line in fp.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        try:
            parsed = next(csv.reader([line]))
            c0 = _clean(parsed[0]) if parsed else ""
        except Exception:
            c0 = _clean(line)

        if c0.lower() in {"title", "topic"}:
            continue
        if c0:
            out.append(c0)

    return out


def build_draft_target_pool(
    workspace_id: str,
    *,
    drafts_path: str = "/drafts",
) -> Dict[str, Any]:
    """
    Draft Target Pool (Option A):
      - reads draft topics (topics only) from CSV/TXT
      - generates placeholder URL for each topic during build:
          https://{domain}{drafts_path}/{slug}
      - writes items: {draft_topic_id, topic, url}
      - if active_target_set_<ws>.json exists, only keeps active draft ids
    """
    ws = _clean(workspace_id)
    if not ws:
        raise ValueError("workspace_id is required")

    csv_fp = _draft_csv_path(ws)
    txt_fp = _draft_txt_path(ws)

    source_used = ""
    topics: List[str] = []

    if csv_fp.exists():
        topics = _read_topics_from_csv(csv_fp)
        source_used = str(csv_fp)
    elif txt_fp.exists():
        topics = _read_topics_from_txt(txt_fp)
        source_used = str(txt_fp)
    else:
        raise FileNotFoundError(
            f"No draft input found. Expected one of: {csv_fp.name}, {txt_fp.name}"
        )

    seen: set[str] = set()
    uniq: List[str] = []
    for t in topics:
        k = _clean(t).lower()
        if not k or k in seen:
            continue
        seen.add(k)
        uniq.append(_clean(t))

    domain = _domain_from_sources_or_ws(ws)
    base = f"https://{domain}".rstrip("/")
    dp = "/" + str(drafts_path or "/drafts").lstrip("/")
    dp = dp.rstrip("/")

    active_fp = _active_target_set_path(ws)
    active_obj = _safe_read_json(active_fp) if active_fp.exists() else None
    active_draft_ids: List[str] = []

    if isinstance(active_obj, dict):
        raw_ids = active_obj.get("active_draft_ids") or []
        if isinstance(raw_ids, list):
            active_draft_ids = [str(x).strip() for x in raw_ids if str(x).strip()]

    active_draft_id_set = set(active_draft_ids)

    items: List[Dict[str, str]] = []
    topics_seen = 0
    items_kept_after_active_filter = 0

    for i, topic in enumerate(uniq, start=1):
        topics_seen += 1
        draft_topic_id = f"draft_{i:04d}"

        if active_fp.exists() and draft_topic_id not in active_draft_id_set:
            continue

        slug = _slugify(topic)
        url = f"{base}{dp}/{slug}"
        items.append(
            {
                "draft_topic_id": draft_topic_id,
                "topic": topic,
                "url": url,
            }
        )
        items_kept_after_active_filter += 1

    out: Dict[str, Any] = {
        "workspace_id": ws,
        "type": "draft",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source_used,
        "drafts_path": dp,
        "domain": domain,
        "active_target_set_used": active_fp.exists(),
        "active_draft_ids_count": len(active_draft_ids),
        "counts": {
            "topics_read": len(topics),
            "topics_deduped": len(uniq),
            "topics_seen": topics_seen,
            "items_written": len(items),
            "items_kept_after_active_filter": items_kept_after_active_filter,
        },
        "items": items,
    }

    out_fp = _pool_path(ws)
    out_fp.parent.mkdir(parents=True, exist_ok=True)
    out_fp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out