from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


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


def _active_phrase_set_path(workspace_id: str) -> Path:
    ws = _ws_safe(workspace_id)
    return _data_dir() / "phrase_pools" / "active" / f"active_phrase_set_{ws}.json"


def _default_obj(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    return {
        "workspace_id": ws,
        "type": "active_phrase_set",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "active_upload_ids": [],
        "active_draft_ids": [],
        "active_live_domain_urls": [],
        "active_import_ids": [],
    }


def load_active_phrase_set(workspace_id: str) -> Dict[str, Any]:
    path = _active_phrase_set_path(workspace_id)
    if not path.exists():
        return _default_obj(workspace_id)

    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            return _default_obj(workspace_id)
    except Exception:
        return _default_obj(workspace_id)

    base = _default_obj(workspace_id)
    for key in (
        "active_upload_ids",
        "active_draft_ids",
        "active_live_domain_urls",
        "active_import_ids",
    ):
        raw = obj.get(key) or []
        base[key] = [str(x).strip() for x in raw if str(x).strip()]

    base["updated_at"] = obj.get("updated_at") or base["updated_at"]
    return base


def save_active_phrase_set(workspace_id: str, obj: Dict[str, Any]) -> Dict[str, Any]:
    path = _active_phrase_set_path(workspace_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    base = _default_obj(workspace_id)
    for key in (
        "active_upload_ids",
        "active_draft_ids",
        "active_live_domain_urls",
        "active_import_ids",
    ):
        raw = obj.get(key) or []
        vals = [str(x).strip() for x in raw if str(x).strip()]
        seen = set()
        deduped = []
        for v in vals:
            if v in seen:
                continue
            seen.add(v)
            deduped.append(v)
        base[key] = deduped

    base["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(base, ensure_ascii=False, indent=2), encoding="utf-8")
    return base