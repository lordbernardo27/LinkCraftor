
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


BUILD_ID = "PHASE-2.5.1-TRANSFER-LEARNING-SNAPSHOT-V1-ADVISORY-ONLY"


@dataclass(frozen=True)
class TransferLearningSnapshot:
    build_id: str
    layer: str
    advisory_only: bool
    can_change_runtime: bool

    source_workspace_id: str
    source_learning_snapshot: Dict[str, Any]

    transferable_success_patterns: List[Dict[str, Any]] = field(default_factory=list)
    transferable_failure_patterns: List[Dict[str, Any]] = field(default_factory=list)
    transferable_anchor_purposes: List[Dict[str, Any]] = field(default_factory=list)
    transferable_reasoning_patterns: List[Dict[str, Any]] = field(default_factory=list)

    transfer_summary: Dict[str, Any] = field(default_factory=dict)
    safety_flags: Dict[str, bool] = field(default_factory=dict)

    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _as_list(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [x for x in value if isinstance(x, dict)]


def build_transfer_learning_snapshot_v1(
    source_workspace_id: str,
    source_learning_snapshot: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    2.5.1 Transfer Learning Snapshot.

    Advisory only:
    - Reads a workspace learning snapshot.
    - Extracts transferable pattern metadata.
    - Does not apply learning to another workspace.
    - Does not change scoring, targets, URLs, highlights, or runtime.
    """

    source_learning_snapshot = source_learning_snapshot or {}

    learning = (
        source_learning_snapshot.get("learning_snapshot")
        if isinstance(source_learning_snapshot.get("learning_snapshot"), dict)
        else source_learning_snapshot
    )

    success_patterns = _as_list(learning.get("top_success_patterns"))
    failure_patterns = _as_list(learning.get("top_failure_patterns"))
    anchor_purposes = _as_list(learning.get("dominant_anchor_purposes"))
    reasoning_patterns = _as_list(learning.get("dominant_reasoning_patterns"))

    transfer_summary = {
        "source_workspace_id": source_workspace_id,
        "success_pattern_count": len(success_patterns),
        "failure_pattern_count": len(failure_patterns),
        "anchor_purpose_count": len(anchor_purposes),
        "reasoning_pattern_count": len(reasoning_patterns),
        "transfer_readiness": "ready" if success_patterns or failure_patterns else "insufficient_data",
        "application_mode": "advisory_recommendation_only",
    }

    result = TransferLearningSnapshot(
        build_id=BUILD_ID,
        layer="2.5.1 Transfer Learning Snapshot",
        advisory_only=True,
        can_change_runtime=False,

        source_workspace_id=source_workspace_id,
        source_learning_snapshot=source_learning_snapshot,

        transferable_success_patterns=success_patterns,
        transferable_failure_patterns=failure_patterns,
        transferable_anchor_purposes=anchor_purposes,
        transferable_reasoning_patterns=reasoning_patterns,

        transfer_summary=transfer_summary,

        safety_flags={
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "applies_learning_to_target_workspace": False,
            "metadata_only": True,
        },
    )

    return asdict(result)


def explain_transfer_learning_snapshot_v1() -> Dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "layer": "2.5.1 Transfer Learning Snapshot",
        "status": "available",
        "mode": "advisory_only",
        "purpose": "Extract transferable learning metadata from an existing workspace learning snapshot.",
        "runtime_permissions": {
            "can_change_highlights": False,
            "can_change_scores": False,
            "can_change_targets": False,
            "can_assign_urls": False,
            "can_apply_learning_to_workspace": False,
        },
    }
