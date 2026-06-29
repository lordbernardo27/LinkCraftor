from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DATA_ROOT = Path("backend/server/data")
EXPLAINABILITY_DIR = DATA_ROOT / "semantic_explainability"


def _safe_workspace_id_v1(workspace_id: str) -> str:
    return "".join(
        c if c.isalnum() or c in ("_", "-") else "_"
        for c in str(workspace_id or "default")
    )


def _explainability_path_v1(workspace_id: str) -> Path:
    EXPLAINABILITY_DIR.mkdir(parents=True, exist_ok=True)
    return EXPLAINABILITY_DIR / f"semantic_explainability_{_safe_workspace_id_v1(workspace_id)}.json"


def build_semantic_explanations_v1(
    *,
    workspace_id: str,
    reasoning: Dict[str, Any],
) -> Dict[str, Any]:

    reasoning_items = reasoning.get("reasoning_items", {}) or {}

    explanations = {}

    for reasoning_id, item in reasoning_items.items():

        strength = float(item.get("semantic_link_strength", 0.0) or 0.0)
        confidence = float(item.get("confidence", 0.0) or 0.0)
        learning_weight = float(item.get("learning_weight", 0.0) or 0.0)
        evidence_count = int(item.get("evidence_count", 0) or 0)
        source_count = int(item.get("source_count", 0) or 0)

        explanation_id = f"explain_{reasoning_id}"

        explanations[explanation_id] = {
            "explanation_id": explanation_id,
            "reasoning_id": reasoning_id,
            "workspace_id": workspace_id,
            "explanation_type": "semantic_linking_explanation",

            "canonical": item.get("canonical"),
            "semantic_type": item.get("semantic_type"),
            "aliases": item.get("aliases", []),

            "decision": item.get("decision"),
            "resolver_signal": item.get("resolver_signal"),
            "semantic_link_strength": strength,
            "confidence": confidence,

            "concept_evidence": {
                "canonical": item.get("canonical"),
                "aliases": item.get("aliases", []),
                "semantic_type": item.get("semantic_type"),
            },

            "learning_evidence": {
                "learning_id": item.get("learning_id"),
                "learning_weight": learning_weight,
                "confidence": confidence,
                "evidence_count": evidence_count,
                "source_count": source_count,
            },

            "reasoning_evidence": {
                "semantic_link_strength": strength,
                "decision": item.get("decision"),
                "resolver_signal": item.get("resolver_signal"),
                "factors": (item.get("explanation") or {}).get("factors", {}),
            },

            "confidence_breakdown": {
                "learning_weight": learning_weight,
                "concept_confidence": confidence,
                "evidence_strength": round(min(evidence_count, 20) / 20, 4),
                "source_diversity": round(min(source_count, 10) / 10, 4),
                "final_semantic_link_strength": strength,
            },

            "contradictions": [],

            "human_summary": (
                f"The concept '{item.get('canonical')}' has a "
                f"{item.get('decision')} with semantic link strength {strength}. "
                f"The resolver should use signal '{item.get('resolver_signal')}'."
            ),

            "created_from": "semantic_linking_reasoning_v1",
        }

    return {
        "version": "semantic_explainability_v1",
        "workspace_id": workspace_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "explanation_count": len(explanations),
        "explanations": explanations,
    }


def save_semantic_explanations_v1(
    *,
    workspace_id: str,
    explanations: Dict[str, Any],
) -> Path:
    path = _explainability_path_v1(workspace_id)
    path.write_text(
        json.dumps(explanations, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path
