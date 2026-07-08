from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


LIFECYCLE_CONTROL_SCHEMA_VERSION = "source_lifecycle_control_v1"

DATA_ROOT = Path("backend/server/data")
LIFECYCLE_CONTROL_DIR = DATA_ROOT / "source_lifecycle_controls"
PURGE_LEDGER_DIR = DATA_ROOT / "source_purge_ledgers"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_ws(workspace_id: str) -> str:
    return (workspace_id or "default").strip().replace("/", "_").replace("\\", "_")


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)
    return path


def _event_id(*parts: str) -> str:
    raw = "|".join(str(p or "") for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def lifecycle_control_path(workspace_id: str) -> Path:
    ws = _safe_ws(workspace_id)
    return LIFECYCLE_CONTROL_DIR / ws / f"source_lifecycle_control_{ws}.json"


def purge_ledger_path(workspace_id: str) -> Path:
    ws = _safe_ws(workspace_id)
    return PURGE_LEDGER_DIR / ws / f"source_purge_ledger_{ws}.json"


def load_lifecycle_control(workspace_id: str) -> Dict[str, Any]:
    path = lifecycle_control_path(workspace_id)
    return _read_json(path, {
        "schema_version": LIFECYCLE_CONTROL_SCHEMA_VERSION,
        "workspace_id": _safe_ws(workspace_id),
        "sources": {},
        "events": [],
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    })


def save_lifecycle_control(workspace_id: str, registry: Dict[str, Any]) -> Path:
    registry["updated_at"] = _now_iso()
    return _write_json(lifecycle_control_path(workspace_id), registry)


def _source_key(source_type: str, source_id: str) -> str:
    return f"{source_type or 'unknown'}::{source_id or 'unknown'}"


def _record_event(
    registry: Dict[str, Any],
    *,
    event_type: str,
    source_type: str,
    source_id: str,
    document_ids: List[str] | None = None,
    reason: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    event = {
        "event_id": _event_id(event_type, source_type, source_id, _now_iso()),
        "event_type": event_type,
        "source_type": source_type,
        "source_id": source_id,
        "document_ids": document_ids or [],
        "reason": reason,
        "metadata": metadata or {},
        "created_at": _now_iso(),
    }
    registry.setdefault("events", []).append(event)
    return event


def register_or_update_source(
    *,
    workspace_id: str,
    source_type: str,
    source_id: str,
    source_name: str = "",
    document_ids: List[str] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    registry = load_lifecycle_control(workspace_id)
    key = _source_key(source_type, source_id)

    existing = registry.setdefault("sources", {}).get(key, {})

    record = {
        **existing,
        "source_key": key,
        "source_type": source_type,
        "source_id": source_id,
        "source_name": source_name or existing.get("source_name", ""),
        "status": "active",
        "document_ids": sorted(set((existing.get("document_ids") or []) + (document_ids or []))),
        "metadata": {
            **(existing.get("metadata") or {}),
            **(metadata or {}),
        },
        "updated_at": _now_iso(),
    }

    record.setdefault("created_at", _now_iso())
    registry["sources"][key] = record

    event = _record_event(
        registry,
        event_type="source_registered_or_updated",
        source_type=source_type,
        source_id=source_id,
        document_ids=document_ids or [],
        metadata=metadata or {},
    )

    save_lifecycle_control(workspace_id, registry)

    return {"ok": True, "source": record, "event": event}


def disconnect_source(
    *,
    workspace_id: str,
    source_type: str,
    source_id: str,
    reason: str = "",
) -> Dict[str, Any]:
    registry = load_lifecycle_control(workspace_id)
    key = _source_key(source_type, source_id)

    source = registry.setdefault("sources", {}).setdefault(key, {
        "source_key": key,
        "source_type": source_type,
        "source_id": source_id,
        "source_name": "",
        "document_ids": [],
        "metadata": {},
        "created_at": _now_iso(),
    })

    source["status"] = "disconnected"
    source["sync_allowed"] = False
    source["preserve_history"] = True
    source["updated_at"] = _now_iso()

    event = _record_event(
        registry,
        event_type="source_disconnected",
        source_type=source_type,
        source_id=source_id,
        document_ids=source.get("document_ids", []),
        reason=reason,
        metadata={
            "delete_uucd": False,
            "delete_body_files": False,
            "preserve_snapshots": True,
            "prevent_future_sync": True,
        },
    )

    save_lifecycle_control(workspace_id, registry)
    return {"ok": True, "source": source, "event": event}


def editor_delete_source(
    *,
    workspace_id: str,
    source_type: str,
    source_id: str,
    document_ids: List[str] | None = None,
    reason: str = "",
) -> Dict[str, Any]:
    registry = load_lifecycle_control(workspace_id)
    key = _source_key(source_type, source_id)

    source = registry.setdefault("sources", {}).setdefault(key, {
        "source_key": key,
        "source_type": source_type,
        "source_id": source_id,
        "source_name": "",
        "document_ids": document_ids or [],
        "metadata": {},
        "created_at": _now_iso(),
    })

    if document_ids:
        source["document_ids"] = sorted(set((source.get("document_ids") or []) + document_ids))

    source["status"] = "deleted"
    source["active_semantic_processing"] = False
    source["physical_delete_pending_explicit_purge"] = True
    source["updated_at"] = _now_iso()

    event = _record_event(
        registry,
        event_type="editor_delete",
        source_type=source_type,
        source_id=source_id,
        document_ids=source.get("document_ids", []),
        reason=reason,
        metadata={
            "remove_from_active_semantic_processing": True,
            "physical_delete": False,
            "requires_explicit_purge_for_destruction": True,
        },
    )

    save_lifecycle_control(workspace_id, registry)
    return {"ok": True, "source": source, "event": event}


def update_source_version(
    *,
    workspace_id: str,
    source_type: str,
    source_id: str,
    document_ids: List[str] | None = None,
    snapshot_id: str = "",
    asset_version_id: str = "",
    content_hash: str = "",
    reason: str = "",
) -> Dict[str, Any]:
    registry = load_lifecycle_control(workspace_id)
    key = _source_key(source_type, source_id)

    source = registry.setdefault("sources", {}).setdefault(key, {
        "source_key": key,
        "source_type": source_type,
        "source_id": source_id,
        "source_name": "",
        "document_ids": [],
        "metadata": {},
        "created_at": _now_iso(),
    })

    if document_ids:
        source["document_ids"] = sorted(set((source.get("document_ids") or []) + document_ids))

    versions = source.setdefault("versions", [])
    version_record = {
        "snapshot_id": snapshot_id or _event_id("snapshot", source_type, source_id, content_hash),
        "asset_version_id": asset_version_id or _event_id("asset", source_type, source_id, content_hash),
        "content_hash": content_hash,
        "document_ids": document_ids or [],
        "created_at": _now_iso(),
    }

    versions.append(version_record)

    source["status"] = "active"
    source["sync_allowed"] = True
    source["latest_snapshot_id"] = version_record["snapshot_id"]
    source["latest_asset_version_id"] = version_record["asset_version_id"]
    source["updated_at"] = _now_iso()

    event = _record_event(
        registry,
        event_type="source_updated",
        source_type=source_type,
        source_id=source_id,
        document_ids=document_ids or [],
        reason=reason,
        metadata=version_record,
    )

    save_lifecycle_control(workspace_id, registry)
    return {"ok": True, "source": source, "event": event, "version": version_record}


def explicit_purge_source(
    *,
    workspace_id: str,
    source_type: str,
    source_id: str,
    reason: str = "",
) -> Dict[str, Any]:
    registry = load_lifecycle_control(workspace_id)
    key = _source_key(source_type, source_id)

    source = registry.get("sources", {}).get(key, {
        "source_key": key,
        "source_type": source_type,
        "source_id": source_id,
        "document_ids": [],
    })

    purge_event = {
        "purge_id": _event_id("purge", workspace_id, source_type, source_id, _now_iso()),
        "workspace_id": _safe_ws(workspace_id),
        "source_type": source_type,
        "source_id": source_id,
        "document_ids": source.get("document_ids", []),
        "reason": reason,
        "removes_uucd": True,
        "removes_body_files": True,
        "removes_lifecycle_records": True,
        "removes_asset_versions": True,
        "removes_snapshots": True,
        "removes_authorization_records": True,
        "created_at": _now_iso(),
        "note": "This ledger records the purge instruction. Physical deletion should be performed by the purge executor.",
    }

    ledger_path = purge_ledger_path(workspace_id)
    ledger = _read_json(ledger_path, {
        "schema_version": "source_purge_ledger_v1",
        "workspace_id": _safe_ws(workspace_id),
        "purges": [],
    })

    ledger.setdefault("purges", []).append(purge_event)
    _write_json(ledger_path, ledger)

    registry.get("sources", {}).pop(key, None)
    _record_event(
        registry,
        event_type="explicit_purge_requested",
        source_type=source_type,
        source_id=source_id,
        document_ids=source.get("document_ids", []),
        reason=reason,
        metadata=purge_event,
    )

    save_lifecycle_control(workspace_id, registry)

    return {
        "ok": True,
        "purge_event": purge_event,
        "purge_ledger_path": str(ledger_path),
        "lifecycle_control_path": str(lifecycle_control_path(workspace_id)),
    }


def explain_source_lifecycle_control_v1() -> Dict[str, Any]:
    return {
        "stage": "Verification 6F",
        "component": "Source Authorization + Lifecycle + Version Control",
        "schema_version": LIFECYCLE_CONTROL_SCHEMA_VERSION,
        "behaviors": [
            "register_or_update_source",
            "disconnect_source",
            "editor_delete_source",
            "update_source_version",
            "explicit_purge_source",
        ],
        "rules": {
            "disconnect_deletes_data": False,
            "editor_delete_deletes_data": False,
            "update_preserves_previous_versions": True,
            "explicit_purge_is_only_destructive_operation": True,
        },
        "next_stage": "Verification 6G — Universal Article Body Store",
    }
