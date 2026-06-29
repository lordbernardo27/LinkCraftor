from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DATA_ROOT = Path("backend/server/data")
LEARNING_DIR = DATA_ROOT / "semantic_learning"


def _safe_workspace_id_v1(workspace_id: str) -> str:
    return "".join(
        c if c.isalnum() or c in ("_", "-") else "_"
        for c in str(workspace_id or "default")
    )


def _learning_path_v1(workspace_id: str) -> Path:
    LEARNING_DIR.mkdir(parents=True, exist_ok=True)
    return LEARNING_DIR / f"semantic_learning_{_safe_workspace_id_v1(workspace_id)}.json"


def build_learning_signals_from_memory_v1(
    *,
    workspace_id: str,
    memory_store: Dict[str, Any],
) -> Dict[str, Any]:
    memories = memory_store.get("memories", {}) or {}

    signals = {}

    for memory_id, memory in memories.items():
        confidence = float(memory.get("confidence", 0.0) or 0.0)
        evidence_count = int(memory.get("evidence_count", 0) or 0)
        source_count = int(memory.get("source_count", 0) or 0)
        ingestion_count = int(memory.get("ingestion_count", 1) or 1)

        learning_weight = round(
            min(
                1.0,
                (confidence * 0.55)
                + (min(evidence_count, 20) / 20 * 0.25)
                + (min(source_count, 10) / 10 * 0.15)
                + (min(ingestion_count, 5) / 5 * 0.05),
            ),
            4,
        )

        signals[memory_id] = {
            "learning_id": f"learn_{memory_id}",
            "memory_id": memory_id,
            "canonical": memory.get("canonical"),
            "semantic_type": memory.get("semantic_type"),
            "aliases": memory.get("aliases", []),
            "confidence": confidence,
            "evidence_count": evidence_count,
            "source_count": source_count,
            "ingestion_count": ingestion_count,
            "learning_weight": learning_weight,
            "learning_status": "active" if learning_weight >= 0.5 else "weak",
            "created_from": "semantic_memory_store_v1",
        }

    return {
        "version": "semantic_learning_signals_v1",
        "workspace_id": workspace_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "signal_count": len(signals),
        "signals": signals,
    }


def save_semantic_learning_signals_v1(
    *,
    workspace_id: str,
    learning_signals: Dict[str, Any],
) -> Path:
    path = _learning_path_v1(workspace_id)
    path.write_text(
        json.dumps(learning_signals, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path
