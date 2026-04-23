from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/link_decisions")

REQUIRED_TOP_LEVEL_KEYS = {
    "workspaceId",
    "docId",
    "sectionId",
    "position",
    "phraseText",
    "contextText",
    "selectedTarget",
    "decision",
    "scores",
    "feedback",
}


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _workspace_file(workspace_id: str) -> Path:
    safe = str(workspace_id or "default").strip() or "default"
    return DATA_DIR / f"{safe}.json"


def _is_valid_decision(decision: Dict[str, Any]) -> bool:
    if not isinstance(decision, dict):
        return False

    missing = REQUIRED_TOP_LEVEL_KEYS - set(decision.keys())
    if missing:
        return False

    if not isinstance(decision.get("selectedTarget"), dict):
        return False
    if not isinstance(decision.get("decision"), dict):
        return False
    if not isinstance(decision.get("scores"), dict):
        return False
    if not isinstance(decision.get("feedback"), dict):
        return False

    return True


def load_link_decisions(workspace_id: str) -> List[Dict[str, Any]]:
    _ensure_dir()
    fp = _workspace_file(workspace_id)

    if not fp.exists():
        return []

    try:
        raw = json.loads(fp.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            return raw
        return []
    except Exception:
        return []


def save_link_decision(workspace_id: str, decision: Dict[str, Any]) -> Dict[str, Any]:
    if not _is_valid_decision(decision):
        return {
            "ok": False,
            "workspaceId": workspace_id,
            "count": len(load_link_decisions(workspace_id)),
            "error": "invalid_decision_shape",
        }

    rows = load_link_decisions(workspace_id)
    rows.append(decision)

    fp = _workspace_file(workspace_id)
    fp.write_text(
        json.dumps(rows, indent=2),
        encoding="utf-8",
    )

    return {
        "ok": True,
        "workspaceId": workspace_id,
        "count": len(rows),
    }