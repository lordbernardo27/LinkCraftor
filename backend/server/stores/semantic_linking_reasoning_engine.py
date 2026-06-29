from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DATA_ROOT = Path("backend/server/data")
REASONING_DIR = DATA_ROOT / "semantic_reasoning"


def _safe_workspace_id_v1(workspace_id: str) -> str:
    return "".join(
        c if c.isalnum() or c in ("_", "-") else "_"
        for c in str(workspace_id or "default")
    )


def _reasoning_path_v1(workspace_id: str) -> Path:
    REASONING_DIR.mkdir(parents=True, exist_ok=True)
    return REASONING_DIR / f"semantic_reasoning_{_safe_workspace_id_v1(workspace_id)}.json"


def build_semantic_linking_reasoning_v1(
    *,
    workspace_id: str,
    learning_signals: Dict[str, Any],
) -> Dict[str, Any]:

    signals = learning_signals.get("signals", {}) or {}

    reasoning_items = {}

    for memory_id, signal in signals.items():

        learning_weight = float(signal.get("learning_weight", 0.0) or 0.0)
        confidence = float(signal.get("confidence", 0.0) or 0.0)
        evidence_count = int(signal.get("evidence_count", 0) or 0)
        source_count = int(signal.get("source_count", 0) or 0)

        semantic_link_strength = round(
            min(
                1.0,
                (learning_weight * 0.55)
                + (confidence * 0.30)
                + (min(evidence_count, 20) / 20 * 0.10)
                + (min(source_count, 10) / 10 * 0.05),
            ),
            4,
        )

        if semantic_link_strength >= 0.75:
            decision = "strong_semantic_relationship"
            resolver_signal = "promote_semantic_link_candidate"
        elif semantic_link_strength >= 0.55:
            decision = "moderate_semantic_relationship"
            resolver_signal = "support_semantic_link_candidate"
        else:
            decision = "weak_semantic_relationship"
            resolver_signal = "observe_only"

        reasoning_id = f"reason_{memory_id}"

        reasoning_items[reasoning_id] = {
            "reasoning_id": reasoning_id,
            "reasoning_type": "semantic_linking_reasoning",
            "workspace_id": workspace_id,
            "memory_id": memory_id,
            "learning_id": signal.get("learning_id"),
            "canonical": signal.get("canonical"),
            "semantic_type": signal.get("semantic_type"),
            "aliases": signal.get("aliases", []),
            "learning_weight": learning_weight,
            "confidence": confidence,
            "evidence_count": evidence_count,
            "source_count": source_count,
            "semantic_link_strength": semantic_link_strength,
            "decision": decision,
            "resolver_signal": resolver_signal,
            "explanation": {
                "summary": "Semantic relationship strength calculated from learning weight, confidence, evidence count, and source diversity.",
                "factors": {
                    "learning_weight": learning_weight,
                    "confidence": confidence,
                    "evidence_count": evidence_count,
                    "source_count": source_count,
                },
            },
            "created_from": "semantic_learning_signals_v1",
        }

    return {
        "version": "semantic_linking_reasoning_v1",
        "workspace_id": workspace_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "reasoning_count": len(reasoning_items),
        "reasoning_items": reasoning_items,
    }


def save_semantic_linking_reasoning_v1(
    *,
    workspace_id: str,
    reasoning: Dict[str, Any],
) -> Path:
    path = _reasoning_path_v1(workspace_id)
    path.write_text(
        json.dumps(reasoning, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path
