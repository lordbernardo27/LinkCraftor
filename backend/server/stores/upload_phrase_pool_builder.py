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


def _upload_phrase_index_path(ws: str) -> Path:
    return _data_dir() / f"upload_phrase_index_{_ws_safe(ws)}.json"


def _upload_phrase_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "upload" / f"upload_phrase_pool_{_ws_safe(ws)}.json"


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_upload_phrase_pool(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    src_path = _upload_phrase_index_path(ws)
    out_path = _upload_phrase_pool_path(ws)

    if not src_path.exists():
        raise FileNotFoundError(f"Missing upload phrase index file: {src_path}")

    raw = _safe_read_json(src_path)
    if not isinstance(raw, dict):
        raw = {}

    source_phrases = raw.get("phrases") if isinstance(raw.get("phrases"), dict) else {}

    active_obj = load_active_phrase_set(ws)
    active_upload_ids = [
        str(x).strip()
        for x in (active_obj.get("active_upload_ids") or [])
        if str(x).strip()
    ]
    active_upload_id_set = set(active_upload_ids)
    use_all_uploads = "ALL" in active_upload_id_set


    phrases: Dict[str, Dict[str, Any]] = {}
    source_phrase_count = 0
    kept_phrase_count = 0

    for phrase, rec in source_phrases.items():
        if not isinstance(rec, dict):
            continue

        source_phrase_count += 1

        docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}
        doc_ids = [str(k).strip() for k in docs.keys() if str(k).strip()]


        if active_upload_id_set and not use_all_uploads:
            matched_doc_ids = [d for d in doc_ids if d in active_upload_id_set]
            if not matched_doc_ids:
                continue

            filtered_docs = {k: v for k, v in docs.items() if str(k).strip() in active_upload_id_set}
            new_rec = dict(rec)
            new_rec["docs"] = filtered_docs
            phrases[str(phrase)] = new_rec
        else:
            phrases[str(phrase)] = rec

        kept_phrase_count += 1

    out_obj = {
        "workspace_id": ws,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source_phrase_count": source_phrase_count,
        "phrase_count": kept_phrase_count,
        "active_phrase_set_used": bool(active_upload_id_set),
        "active_upload_ids_count": len(active_upload_ids),
        "phrases": phrases,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out_obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_obj