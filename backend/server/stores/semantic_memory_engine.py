from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DATA_ROOT = Path("backend/server/data")
MEMORY_DIR = DATA_ROOT / "semantic_memory"


def _safe_workspace_id_v1(workspace_id: str) -> str:
    return "".join(
        c if c.isalnum() or c in ("_", "-") else "_"
        for c in str(workspace_id or "default")
    )


def _memory_path_v1(workspace_id: str) -> Path:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    return MEMORY_DIR / f"semantic_memory_{_safe_workspace_id_v1(workspace_id)}.json"


def load_semantic_memory_store_v1(workspace_id: str) -> Dict[str, Any]:
    path = _memory_path_v1(workspace_id)

    if not path.exists():
        return {
            "version": "semantic_memory_store_v1",
            "workspace_id": workspace_id,
            "memories": {},
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "stats": {
                "memory_count": 0,
            },
        }

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "version": "semantic_memory_store_v1",
            "workspace_id": workspace_id,
            "memories": {},
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "recovered_from_error": True,
            "stats": {
                "memory_count": 0,
            },
        }


def save_semantic_memory_store_v1(
    workspace_id: str,
    store: Dict[str, Any],
) -> Path:
    path = _memory_path_v1(workspace_id)
    store["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    store["stats"] = {
        "memory_count": len(store.get("memories", {})),
    }
    path.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def ingest_semantic_memory_feed_v1(
    *,
    workspace_id: str,
    memory_feed: Dict[str, Any],
) -> Dict[str, Any]:
    store = load_semantic_memory_store_v1(workspace_id)

    memories = store.setdefault("memories", {})
    observations = memory_feed.get("observations", []) or []

    created = 0
    updated = 0

    now = datetime.now(timezone.utc).isoformat()

    for obs in observations:
        memory_id = obs.get("memory_id")

        if not memory_id:
            continue

        existing = memories.get(memory_id)

        if existing:
            updated += 1
            existing["last_seen_at"] = now
            existing["canonical"] = obs.get("canonical", existing.get("canonical"))
            existing["semantic_type"] = obs.get("semantic_type", existing.get("semantic_type"))
            existing["confidence"] = obs.get("confidence", existing.get("confidence", 0.0))
            existing["confidence_factors"] = obs.get("confidence_factors", existing.get("confidence_factors", {}))
            existing["aliases"] = sorted(set((existing.get("aliases") or []) + (obs.get("aliases") or [])))
            existing["source_count"] = max(existing.get("source_count", 0), obs.get("source_count", 0))
            existing["evidence_count"] = max(existing.get("evidence_count", 0), obs.get("evidence_count", 0))
            existing["ingestion_count"] = existing.get("ingestion_count", 1) + 1
        else:
            created += 1
            memories[memory_id] = {
                "memory_id": memory_id,
                "memory_type": obs.get("memory_type", "semantic_concept"),
                "canonical": obs.get("canonical"),
                "semantic_type": obs.get("semantic_type"),
                "confidence": obs.get("confidence", 0.0),
                "confidence_factors": obs.get("confidence_factors", {}),
                "aliases": obs.get("aliases", []),
                "source_count": obs.get("source_count", 0),
                "evidence_count": obs.get("evidence_count", 0),
                "first_seen_at": now,
                "last_seen_at": now,
                "ingestion_count": 1,
                "source_feed_version": memory_feed.get("version"),
            }

    save_semantic_memory_store_v1(workspace_id, store)

    return {
        "status": "ingested",
        "workspace_id": workspace_id,
        "created_count": created,
        "updated_count": updated,
        "memory_count": len(memories),
        "store_path": str(_memory_path_v1(workspace_id)),
    }
