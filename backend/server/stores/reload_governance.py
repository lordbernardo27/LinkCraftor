
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/reload_governance")
DATA_DIR.mkdir(parents=True, exist_ok=True)


RELOAD_RULES_V1 = {
    "version": "reload_governance_v1",
    "primary_mode": "state_refresh_not_data_rebuild",
    "rebuild_before_reload": True,
    "ui_button_required": False,
    "reload_triggers": {
        "workspace_opened": [
            "backend_state_reload",
            "runtime_refresh",
            "highlight_repaint",
            "panel_refresh",
        ],
        "rebuild_processed": [
            "backend_state_reload",
            "runtime_refresh",
            "highlight_repaint",
            "panel_refresh",
        ],
        "clear_session_completed": [
            "backend_state_reload",
            "runtime_refresh",
            "highlight_repaint",
            "panel_refresh",
        ],
        "active_phrase_pool_changed": [
            "backend_state_reload",
            "runtime_refresh",
            "highlight_repaint",
            "panel_refresh",
        ],
        "document_uploaded": [
            "backend_state_reload",
            "runtime_refresh",
            "highlight_repaint",
            "panel_refresh",
        ],
    },
}


@dataclass
class ReloadEvent:
    workspace_id: str
    trigger: str
    affected_layers: List[str]
    status: str = "queued"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


def _ws_safe(workspace_id: str) -> str:
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in str(workspace_id or "default"))


def _queue_path(workspace_id: str) -> Path:
    return DATA_DIR / f"reload_queue_{_ws_safe(workspace_id)}.json"


def _state_path(workspace_id: str) -> Path:
    return DATA_DIR / f"reload_state_{_ws_safe(workspace_id)}.json"


def load_reload_queue(workspace_id: str) -> List[Dict[str, Any]]:
    path = _queue_path(workspace_id)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_reload_queue(workspace_id: str, queue: List[Dict[str, Any]]) -> None:
    path = _queue_path(workspace_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, indent=2), encoding="utf-8")


def queue_reload_event(
    workspace_id: str,
    trigger: str,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    affected_layers = RELOAD_RULES_V1["reload_triggers"].get(trigger, [])

    event = ReloadEvent(
        workspace_id=workspace_id,
        trigger=trigger,
        affected_layers=affected_layers,
        metadata=metadata or {},
    )

    queue = load_reload_queue(workspace_id)
    queue.append(asdict(event))
    save_reload_queue(workspace_id, queue)

    return asdict(event)


def get_reload_state(workspace_id: str) -> Dict[str, Any]:
    path = _state_path(workspace_id)
    if not path.exists():
        return {
            "workspace_id": workspace_id,
            "rules_version": RELOAD_RULES_V1["version"],
            "last_reload_at": None,
            "processed_count": 0,
            "layers": {},
        }

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "workspace_id": workspace_id,
            "rules_version": RELOAD_RULES_V1["version"],
            "last_reload_at": None,
            "processed_count": 0,
            "layers": {},
        }


def save_reload_state(workspace_id: str, state: Dict[str, Any]) -> None:
    path = _state_path(workspace_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    state["rules_version"] = RELOAD_RULES_V1["version"]
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def process_reload_queue(workspace_id: str, limit: int = 20) -> Dict[str, Any]:
    queue = load_reload_queue(workspace_id)

    if not queue:
        return {
            "workspace_id": workspace_id,
            "processed": 0,
            "remaining": 0,
            "events": [],
        }

    limit = max(1, int(limit or 20))
    to_process = queue[:limit]
    remaining = queue[limit:]

    state = get_reload_state(workspace_id)
    processed_events = []

    for event in to_process:
        event["status"] = "processed"
        event["processed_at"] = datetime.now(timezone.utc).isoformat()

        event["reload_actions"] = []

        for layer in event.get("affected_layers") or []:

            state.setdefault("layers", {})[layer] = {
                "last_reload_requested_at": event["processed_at"],
                "status": "refresh_requested",
            }

            event["reload_actions"].append({
                "layer": layer,
                "action_requested": True,
            })

        processed_events.append(event)

    state["last_reload_at"] = datetime.now(timezone.utc).isoformat()
    state["processed_count"] = int(state.get("processed_count") or 0) + len(processed_events)

    save_reload_state(workspace_id, state)
    save_reload_queue(workspace_id, remaining)

    return {
        "workspace_id": workspace_id,
        "processed": len(processed_events),
        "remaining": len(remaining),
        "events": processed_events,
    }

