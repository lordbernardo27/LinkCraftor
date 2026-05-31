
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import json

from backend.server.stores.upload_phrase_pool_builder import build_upload_phrase_pool
from backend.server.stores.active_phrase_pool_builder import build_active_phrase_pool
from backend.server.stores.active_phrase_set_store import load_active_phrase_set, save_active_phrase_set
from backend.server.stores.reload_governance import queue_reload_event


DATA_DIR = Path("backend/server/data/rebuild_governance")
DATA_DIR.mkdir(parents=True, exist_ok=True)


REBUILD_RULES_V2 = {
    "version": "rebuild_governance_v2",
    "primary_mode": "event_driven_rebuild",
    "secondary_mode": "stale_safety_sweep",
    "sweep_interval_seconds": 180,
    "manual_rebuild_enabled": True,
    "upload_triggers_rebuild": True,
    "clear_session_runs_stale_detector": True,
    "reload_runs_stale_detector": True,
    "rules": {
        "document_changed": [
            "document_structure",
            "upload_phrase_pool",
            "active_phrase_set",
            "active_phrase_pool",
            "rb2_runtime",
            "editor_repaint",
        ],
        "extractor_changed": [
            "upload_phrase_pool",
            "active_phrase_pool",
            "rb2_runtime",
            "editor_repaint",
        ],
        "semantic_repair_changed": [
            "upload_phrase_pool",
            "active_phrase_pool",
            "rb2_runtime",
            "editor_repaint",
        ],
        "guard_changed": [
            "guarded_candidate_set",
            "upload_phrase_pool",
            "active_phrase_pool",
            "rb2_runtime",
            "editor_repaint",
        ],
        "scorer_changed": [
            "upload_phrase_pool_scores",
            "active_phrase_pool",
            "rb2_runtime",
            "editor_repaint",
        ],
        "source_membership_changed": [
            "active_phrase_set",
            "active_phrase_pool",
            "rb2_runtime",
            "editor_repaint",
        ],
        "upload_pool_changed": [
            "active_phrase_pool",
            "rb2_runtime",
            "editor_repaint",
        ],
        "supporting_intelligence_changed": [
            "supporting_intelligence_maps",
            "supporting_scores",
        ],
        "target_pool_changed": [
            "active_target_pool",
            "target_resolution_map",
            "rb2_runtime",
            "editor_repaint",
        ],
        "url_source_changed": [
            "target_resolution_map",
            "active_target_pool",
            "rb2_runtime",
            "editor_repaint",
        ],
        "highlight_selection_changed": [
            "selected_highlight_candidates",
            "rb2_runtime",
            "editor_repaint",
        ],
        "highlight_density_changed": [
            "highlight_count_allocation",
            "rb2_runtime",
            "editor_repaint",
        ],
        "runtime_changed": [
            "rb2_runtime",
            "editor_repaint",
        ],
        "frontend_editor_changed": [
            "editor_state",
            "editor_repaint",
        ],
        "decision_intelligence_changed": [
            "decision_knowledge_cache",
            "dis_rejection_pattern_cache",
            "rb2_runtime",
            "editor_repaint",
        ],
    },
}


@dataclass
class RebuildEvent:
    workspace_id: str
    trigger: str
    affected_layers: List[str]
    status: str = "queued"
    created_at: str = ""
    metadata: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if not data["created_at"]:
            data["created_at"] = datetime.now(timezone.utc).isoformat()
        if data["metadata"] is None:
            data["metadata"] = {}
        return data


def _queue_path(workspace_id: str) -> Path:
    safe = str(workspace_id or "default").replace("/", "_").replace("\\", "_")
    return DATA_DIR / f"rebuild_queue_{safe}.json"


def _state_path(workspace_id: str) -> Path:
    safe = str(workspace_id or "default").replace("/", "_").replace("\\", "_")
    return DATA_DIR / f"rebuild_state_{safe}.json"


def load_rebuild_queue(workspace_id: str) -> List[Dict[str, Any]]:
    path = _queue_path(workspace_id)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_rebuild_queue(workspace_id: str, queue: List[Dict[str, Any]]) -> None:
    _queue_path(workspace_id).write_text(
        json.dumps(queue, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def queue_rebuild_event(
    workspace_id: str,
    trigger: str,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    affected_layers = REBUILD_RULES_V2["rules"].get(trigger, [])

    event = RebuildEvent(
        workspace_id=workspace_id,
        trigger=trigger,
        affected_layers=affected_layers,
        metadata=metadata or {},
    ).to_dict()

    queue = load_rebuild_queue(workspace_id)
    queue.append(event)
    save_rebuild_queue(workspace_id, queue)

    return event


def get_rebuild_state(workspace_id: str) -> Dict[str, Any]:
    path = _state_path(workspace_id)
    if not path.exists():
        return {
            "workspace_id": workspace_id,
            "rules_version": REBUILD_RULES_V2["version"],
            "layer_versions": {},
            "last_sweep_at": None,
            "stale_layers": [],
        }

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_rebuild_state(workspace_id: str, state: Dict[str, Any]) -> None:
    state["workspace_id"] = workspace_id
    state["rules_version"] = REBUILD_RULES_V2["version"]
    _state_path(workspace_id).write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def mark_layer_rebuilt(workspace_id: str, layer: str) -> Dict[str, Any]:
    state = get_rebuild_state(workspace_id)
    layer_versions = state.setdefault("layer_versions", {})

    current = int(layer_versions.get(layer, 0) or 0)
    layer_versions[layer] = current + 1
    state["last_updated_at"] = datetime.now(timezone.utc).isoformat()

    save_rebuild_state(workspace_id, state)
    return state


def detect_stale_layers(workspace_id: str) -> Dict[str, Any]:
    state = get_rebuild_state(workspace_id)
    versions = state.get("layer_versions", {}) or {}

    stale = []

    dependency_pairs = [
        ("document_structure", "upload_phrase_pool"),
        ("upload_phrase_pool", "active_phrase_pool"),
        ("active_phrase_pool", "rb2_runtime"),
        ("active_target_pool", "rb2_runtime"),
        ("rb2_runtime", "editor_repaint"),
    ]

    for source, derived in dependency_pairs:
        source_v = int(versions.get(source, 0) or 0)
        derived_v = int(versions.get(derived, 0) or 0)

        if source_v > derived_v:
            stale.append({
                "source_layer": source,
                "derived_layer": derived,
                "source_version": source_v,
                "derived_version": derived_v,
            })

    state["stale_layers"] = stale
    state["last_sweep_at"] = datetime.now(timezone.utc).isoformat()
    save_rebuild_state(workspace_id, state)

    return {
        "workspace_id": workspace_id,
        "is_stale": bool(stale),
        "stale_layers": stale,
        "rules_version": REBUILD_RULES_V2["version"],
    }


def queue_stale_repair_if_needed(workspace_id: str) -> Dict[str, Any]:
    report = detect_stale_layers(workspace_id)

    if not report["is_stale"]:
        return {
            "workspace_id": workspace_id,
            "queued": False,
            "reason": "no_stale_layers_detected",
            "report": report,
        }

    event = queue_rebuild_event(
        workspace_id=workspace_id,
        trigger="runtime_changed",
        metadata={
            "source": "stale_detector",
            "stale_layers": report["stale_layers"],
        },
    )

    return {
        "workspace_id": workspace_id,
        "queued": True,
        "event": event,
        "report": report,
    }



def run_stale_safety_sweep(workspace_id: str) -> Dict[str, Any]:
    """
    3-minute stale safety sweep.

    This does NOT blindly rebuild everything.
    It detects stale layer mismatches and queues repair only when needed.
    """

    result = queue_stale_repair_if_needed(workspace_id)

    return {
        "workspace_id": workspace_id,
        "mode": "stale_safety_sweep",
        "interval_seconds": REBUILD_RULES_V2["sweep_interval_seconds"],
        "blind_full_rebuild": False,
        "result": result,
    }



def process_rebuild_queue(workspace_id: str, limit: int = 20) -> Dict[str, Any]:
    """
    Process queued rebuild events.

    Current v1 behavior:
    - consumes queued events
    - marks affected layers as rebuilt
    - records processed events
    - does not yet execute heavy rebuild jobs directly

    Later this can call real builders/workers per layer.
    """

    queue = load_rebuild_queue(workspace_id)
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

    processed_events = []

    for event in to_process:
        affected_layers = list(event.get("affected_layers") or [])

        for layer in affected_layers:
            try:
                builder_result = None

                if layer == "upload_phrase_pool":
                    builder_result = build_upload_phrase_pool(workspace_id)

                elif layer == "active_phrase_pool":
                    builder_result = build_active_phrase_pool(workspace_id)

                elif layer == "active_phrase_set":
                    active_obj = load_active_phrase_set(workspace_id)
                    builder_result = save_active_phrase_set(workspace_id, active_obj)

                event.setdefault("builder_results", []).append({
                    "layer": layer,
                    "ran_builder": builder_result is not None,
                    "result_ok": (
                        bool(builder_result.get("ok"))
                        if isinstance(builder_result, dict) and "ok" in builder_result
                        else True
                    ),
                    "result_keys": (
                        sorted(list(builder_result.keys()))
                        if isinstance(builder_result, dict)
                        else []
                    ),
                })

                mark_layer_rebuilt(workspace_id, layer)

            except Exception as e:
                event.setdefault("errors", []).append({
                    "layer": layer,
                    "error": repr(e),
                })

        event["status"] = "processed"
        event["processed_at"] = datetime.now(timezone.utc).isoformat()
        processed_events.append(event)

    reload_event = None

    if processed_events:
        try:
            reload_event = queue_reload_event(
                workspace_id=workspace_id,
                trigger="rebuild_processed",
                metadata={
                    "source": "rebuild_queue_processor",
                    "processed_rebuild_events": len(processed_events),
                },
            )
        except Exception as e:
            reload_event = {
                "error": repr(e),
                "source": "rebuild_queue_processor",
            }

    save_rebuild_queue(workspace_id, remaining)

    return {
        "workspace_id": workspace_id,
        "processed": len(processed_events),
        "reload_event": reload_event,
        "remaining": len(remaining),
        "events": processed_events,
    }
