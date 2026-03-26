from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


# ------------------------------------------------------------
# Draft Topic Pool (workspace-scoped)
#   - Items file: draft_topics_<ws>.json
#   - Meta file : draft_topics_meta_<ws>.json
# ------------------------------------------------------------
def draft_topics_path(ws: str) -> Path:
    return _data_dir() / f"draft_topics_{ws}.json"


def draft_topics_meta_path(ws: str) -> Path:
    return _data_dir() / f"draft_topics_meta_{ws}.json"


def load_draft_items_ws(ws: str) -> List[Dict[str, Any]]:
    """
    Loads the Draft Topic Pool items for a workspace.
    File format: JSON list[dict]
    """
    fp = draft_topics_path(ws)
    if not fp.exists():
        return []

    try:
        obj = json.loads(fp.read_text(encoding="utf-8"))
        return obj if isinstance(obj, list) else []
    except Exception:
        return []


def save_draft_items_ws(ws: str, items: List[Dict[str, Any]]) -> None:
    """
    Saves Draft Topic Pool items for a workspace.
    """
    fp = draft_topics_path(ws)
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def load_draft_meta_ws(ws: str) -> Dict[str, Any]:
    """
    Loads Draft Topic Pool meta for a workspace.
    File format: JSON dict
    """
    fp = draft_topics_meta_path(ws)
    if not fp.exists():
        return {}

    try:
        obj = json.loads(fp.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def save_draft_meta_ws(ws: str, meta: Dict[str, Any]) -> None:
    """
    Saves Draft Topic Pool meta for a workspace.
    """
    fp = draft_topics_meta_path(ws)
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")