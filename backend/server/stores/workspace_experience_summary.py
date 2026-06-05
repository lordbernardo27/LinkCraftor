
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


BUILD_ID = "PHASE-2.4.5-WORKSPACE-EXPERIENCE-SUMMARIZATION-V1"


@dataclass(frozen=True)
class WorkspaceExperienceSummary:
    build_id: str
    advisory_only: bool
    can_change_runtime: bool

    workspace_id: str

    documents_processed: int
    accepted_links: int
    rejected_links: int

    acceptance_rate: float
    rejection_rate: float

    top_success_patterns: List[str] = field(default_factory=list)
    top_failure_patterns: List[str] = field(default_factory=list)

    dominant_anchor_purposes: List[str] = field(default_factory=list)

    dominant_reasoning_patterns: List[str] = field(default_factory=list)

    learning_snapshot: Dict[str, Any] = field(default_factory=dict)

    safety_flags: Dict[str, bool] = field(default_factory=dict)

    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def build_workspace_experience_summary_v1(
    workspace_id: str,
    documents_processed: int = 0,
    accepted_links: int = 0,
    rejected_links: int = 0,
    top_success_patterns: List[str] | None = None,
    top_failure_patterns: List[str] | None = None,
    dominant_anchor_purposes: List[str] | None = None,
    dominant_reasoning_patterns: List[str] | None = None,
) -> Dict[str, Any]:

    total = accepted_links + rejected_links

    acceptance_rate = (
        round(accepted_links / total, 4)
        if total > 0 else 0.0
    )

    rejection_rate = (
        round(rejected_links / total, 4)
        if total > 0 else 0.0
    )

    result = WorkspaceExperienceSummary(
        build_id=BUILD_ID,
        advisory_only=True,
        can_change_runtime=False,

        workspace_id=workspace_id,

        documents_processed=documents_processed,
        accepted_links=accepted_links,
        rejected_links=rejected_links,

        acceptance_rate=acceptance_rate,
        rejection_rate=rejection_rate,

        top_success_patterns=top_success_patterns or [],
        top_failure_patterns=top_failure_patterns or [],

        dominant_anchor_purposes=dominant_anchor_purposes or [],

        dominant_reasoning_patterns=dominant_reasoning_patterns or [],

        learning_snapshot={
            "summary_type": "workspace_experience_snapshot",
            "generated_from_existing_memory_layers": True,
        },

        safety_flags={
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "metadata_only": True,
        },
    )

    return asdict(result)


def explain_workspace_experience_summary_v1() -> Dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "layer": "2.4.5 Experience Summarization",
        "mode": "advisory_only",
        "purpose": (
            "Summarizes existing memory, feedback, "
            "learning, and decision intelligence."
        ),
        "runtime_permissions": {
            "can_change_scores": False,
            "can_change_targets": False,
            "can_change_urls": False,
            "can_change_highlights": False,
        },
    }
