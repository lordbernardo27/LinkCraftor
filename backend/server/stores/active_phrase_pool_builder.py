from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from backend.server.stores.active_phrase_set_store import load_active_phrase_set


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    server_dir = here.parents[1]  # .../backend/server
    return server_dir / "data"


def _ws_safe(ws: str) -> str:
    raw = (ws or "default").strip()
    if not raw:
        return "default"
    if raw.lower() == "default":
        return "default"
    if raw.lower().startswith("ws_"):
        return raw

    s = raw.lower()
    s = s.replace(".", "_").replace("-", "_").replace(" ", "_")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "workspace"
    return f"ws_{s}"[:80]


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _upload_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "upload" / f"upload_phrase_pool_{_ws_safe(ws)}.json"

def _live_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "live_domain" / f"live_domain_phrase_pool_{_ws_safe(ws)}.json"


def _draft_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "draft" / f"draft_phrase_pool_{_ws_safe(ws)}.json"


def _imported_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "imported" / f"imported_phrase_pool_{_ws_safe(ws)}.json"


def _active_phrase_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "active" / f"active_phrase_pool_{_ws_safe(ws)}.json"


def build_active_phrase_pool(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)

    active_obj = load_active_phrase_set(ws)

    active_document_ids = [
    str(x).strip()
    for x in (
        active_obj.get("active_upload_ids")
        or active_obj.get("active_document_ids")
        or []
    )
    if str(x).strip()
]


    active_draft_ids = [
        str(x).strip()
        for x in (active_obj.get("active_draft_ids") or [])
        if str(x).strip()
    ]
    active_live_domain_urls = [
        str(x).strip()
        for x in (active_obj.get("active_live_domain_urls") or [])
        if str(x).strip()
    ]
    active_imported_urls = [
        str(x).strip()
        for x in (
            (active_obj.get("active_imported_urls") or active_obj.get("active_import_ids") or [])
        )
        if str(x).strip()
    ]

    source_paths: Dict[str, Path] = {}

    if active_document_ids:
        source_paths["upload"] = _upload_pool_path(ws)

    if active_live_domain_urls:
        source_paths["live_domain"] = _live_pool_path(ws)

    if active_draft_ids:
        source_paths["draft"] = _draft_pool_path(ws)

    if active_imported_urls:
        source_paths["imported"] = _imported_pool_path(ws)

    merged: Dict[str, Dict[str, Any]] = {}
    counts_by_source: Dict[str, int] = {}
    sources_used: Dict[str, bool] = {
        "upload": False,
        "live_domain": False,
        "draft": False,
        "imported": False,
    }

    for source_name, path in source_paths.items():
        obj = _safe_read_json(path) if path.exists() else None
        phrases = obj.get("phrases") if isinstance(obj, dict) and isinstance(obj.get("phrases"), dict) else {}

        counts_by_source[source_name] = len(phrases)
        sources_used[source_name] = bool(path.exists())

        for phrase, rec in phrases.items():
            if not isinstance(rec, dict):
                continue

            key = str(phrase).strip()
            if not key:
                continue

            if key not in merged:
                new_rec = dict(rec)
                new_rec["pool_sources"] = [source_name]
                merged[key] = new_rec
            else:
                existing = merged[key]
                existing.setdefault("pool_sources", [])
                if source_name not in existing["pool_sources"]:
                    existing["pool_sources"].append(source_name)

    for source_name in ("upload", "live_domain", "draft", "imported"):
        counts_by_source.setdefault(source_name, 0)

    out = {
        "workspace_id": ws,
        "type": "active_phrase_pool",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "counts_by_source": counts_by_source,
        "sources_used": sources_used,
        "active_phrase_set_used": {
            "active_document_ids_count": len(active_document_ids),
            "active_draft_ids_count": len(active_draft_ids),
            "active_live_domain_urls_count": len(active_live_domain_urls),
            "active_imported_urls_count": len(active_imported_urls),
        },
        "phrase_count": len(merged),
        "phrases": merged,
    }

    out_path = _active_phrase_pool_path(ws)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out