
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



def _pattern_names(items: List[Dict[str, Any]], key: str = "pattern") -> set[str]:
    out: set[str] = set()
    for item in items or []:
        if not isinstance(item, dict):
            continue
        value = str(item.get(key) or "").strip()
        if value:
            out.add(value)
    return out


def _jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    return round(len(a & b) / max(1, len(a | b)), 4)


def analyze_workspace_similarity_v1(
    source_transfer_snapshot: Dict[str, Any],
    target_transfer_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    source_success = _as_list(source_transfer_snapshot.get("transferable_success_patterns"))
    target_success = _as_list(target_transfer_snapshot.get("transferable_success_patterns"))

    source_failure = _as_list(source_transfer_snapshot.get("transferable_failure_patterns"))
    target_failure = _as_list(target_transfer_snapshot.get("transferable_failure_patterns"))

    source_purpose = _as_list(source_transfer_snapshot.get("transferable_anchor_purposes"))
    target_purpose = _as_list(target_transfer_snapshot.get("transferable_anchor_purposes"))

    source_reasoning = _as_list(source_transfer_snapshot.get("transferable_reasoning_patterns"))
    target_reasoning = _as_list(target_transfer_snapshot.get("transferable_reasoning_patterns"))

    source_success_names = _pattern_names(source_success, "pattern")
    target_success_names = _pattern_names(target_success, "pattern")
    source_failure_names = _pattern_names(source_failure, "pattern")
    target_failure_names = _pattern_names(target_failure, "pattern")
    source_purpose_names = _pattern_names(source_purpose, "purpose")
    target_purpose_names = _pattern_names(target_purpose, "purpose")
    source_reasoning_names = _pattern_names(source_reasoning, "pattern")
    target_reasoning_names = _pattern_names(target_reasoning, "pattern")

    success_similarity = _jaccard_similarity(source_success_names, target_success_names)
    failure_similarity = _jaccard_similarity(source_failure_names, target_failure_names)
    purpose_similarity = _jaccard_similarity(source_purpose_names, target_purpose_names)
    reasoning_similarity = _jaccard_similarity(source_reasoning_names, target_reasoning_names)

    overall_similarity_score = round(
        (
            success_similarity * 0.35
            + failure_similarity * 0.20
            + purpose_similarity * 0.25
            + reasoning_similarity * 0.20
        ),
        4,
    )

    if overall_similarity_score >= 0.70:
        transfer_suitability = "high"
    elif overall_similarity_score >= 0.40:
        transfer_suitability = "moderate"
    elif overall_similarity_score > 0:
        transfer_suitability = "low"
    else:
        transfer_suitability = "insufficient_overlap"

    return {
        "build_id": BUILD_ID,
        "layer": "2.5.2 Workspace Similarity Analysis",
        "advisory_only": True,
        "can_change_runtime": False,
        "source_workspace_id": source_transfer_snapshot.get("source_workspace_id"),
        "target_workspace_id": target_transfer_snapshot.get("source_workspace_id"),
        "similarity_scores": {
            "success_similarity": success_similarity,
            "failure_similarity": failure_similarity,
            "anchor_purpose_similarity": purpose_similarity,
            "reasoning_similarity": reasoning_similarity,
            "overall_similarity_score": overall_similarity_score,
        },
        "shared_patterns": {
            "shared_success_patterns": sorted(source_success_names & target_success_names),
            "shared_failure_patterns": sorted(source_failure_names & target_failure_names),
            "shared_anchor_purposes": sorted(source_purpose_names & target_purpose_names),
            "shared_reasoning_patterns": sorted(source_reasoning_names & target_reasoning_names),
        },
        "transfer_suitability": transfer_suitability,
        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "applies_learning_to_target_workspace": False,
            "metadata_only": True,
        },
    }



def build_experience_transfer_recommendations_v1(
    source_transfer_snapshot: Dict[str, Any],
    target_transfer_snapshot: Dict[str, Any],
    similarity_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """
    2.5.3 Experience Transfer Recommendations.

    Advisory only:
    - Reviews transfer snapshots.
    - Reviews similarity analysis.
    - Produces transfer recommendations.
    - Does NOT apply learning.
    - Does NOT modify runtime.
    - Does NOT modify scores.
    - Does NOT modify targets.
    - Does NOT modify URLs.
    """

    similarity_scores = (
        similarity_analysis.get("similarity_scores")
        if isinstance(similarity_analysis.get("similarity_scores"), dict)
        else {}
    )

    overall_similarity = float(
        similarity_scores.get("overall_similarity_score") or 0
    )

    source_success = _as_list(
        source_transfer_snapshot.get(
            "transferable_success_patterns"
        )
    )

    source_failure = _as_list(
        source_transfer_snapshot.get(
            "transferable_failure_patterns"
        )
    )

    source_anchor_purposes = _as_list(
        source_transfer_snapshot.get(
            "transferable_anchor_purposes"
        )
    )

    source_reasoning_patterns = _as_list(
        source_transfer_snapshot.get(
            "transferable_reasoning_patterns"
        )
    )

    if overall_similarity >= 0.70:
        recommendation_strength = "high"

    elif overall_similarity >= 0.40:
        recommendation_strength = "moderate"

    elif overall_similarity > 0:
        recommendation_strength = "low"

    else:
        recommendation_strength = "insufficient_overlap"

    recommended_success_patterns = [
        x.get("pattern")
        for x in source_success
        if isinstance(x, dict)
        and x.get("pattern")
    ]

    recommended_failure_patterns_to_avoid = [
        x.get("pattern")
        for x in source_failure
        if isinstance(x, dict)
        and x.get("pattern")
    ]

    recommended_anchor_purposes = [
        x.get("purpose")
        for x in source_anchor_purposes
        if isinstance(x, dict)
        and x.get("purpose")
    ]

    recommended_reasoning_patterns = [
        x.get("pattern")
        for x in source_reasoning_patterns
        if isinstance(x, dict)
        and x.get("pattern")
    ]

    return {
        "build_id": BUILD_ID,
        "layer": "2.5.3 Experience Transfer Recommendations",
        "advisory_only": True,
        "can_change_runtime": False,

        "source_workspace_id":
            source_transfer_snapshot.get(
                "source_workspace_id"
            ),

        "target_workspace_id":
            target_transfer_snapshot.get(
                "source_workspace_id"
            ),

        "recommendation_strength":
            recommendation_strength,

        "transfer_readiness":
            "ready"
            if overall_similarity > 0
            else "insufficient_overlap",

        "recommended_success_patterns":
            recommended_success_patterns,

        "recommended_failure_patterns_to_avoid":
            recommended_failure_patterns_to_avoid,

        "recommended_anchor_purposes":
            recommended_anchor_purposes,

        "recommended_reasoning_patterns":
            recommended_reasoning_patterns,

        "similarity_score":
            overall_similarity,

        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "applies_learning_to_target_workspace": False,
            "metadata_only": True,
        },
    }



def build_transfer_learning_summary_v1(
    source_transfer_snapshot: Dict[str, Any],
    target_transfer_snapshot: Dict[str, Any],
    similarity_analysis: Dict[str, Any],
    transfer_recommendations: Dict[str, Any],
) -> Dict[str, Any]:
    """
    2.5.4 Transfer Learning Summary.

    Advisory only:
    - Summarizes 2.5.1, 2.5.2, and 2.5.3 outputs.
    - Does not apply transfer learning.
    - Does not modify runtime.
    - Does not modify scores, targets, URLs, highlights, or linking.
    """

    similarity_scores = (
        similarity_analysis.get("similarity_scores")
        if isinstance(similarity_analysis.get("similarity_scores"), dict)
        else {}
    )

    overall_similarity = float(
        similarity_scores.get("overall_similarity_score") or 0
    )

    transfer_suitability = str(
        similarity_analysis.get("transfer_suitability")
        or "unknown"
    )

    recommendation_strength = str(
        transfer_recommendations.get("recommendation_strength")
        or "unknown"
    )

    recommended_success_patterns = transfer_recommendations.get(
        "recommended_success_patterns",
        [],
    )

    recommended_failure_patterns_to_avoid = transfer_recommendations.get(
        "recommended_failure_patterns_to_avoid",
        [],
    )

    recommended_anchor_purposes = transfer_recommendations.get(
        "recommended_anchor_purposes",
        [],
    )

    recommended_reasoning_patterns = transfer_recommendations.get(
        "recommended_reasoning_patterns",
        [],
    )

    if transfer_suitability in {"high", "moderate"}:
        final_advisory_decision = "transfer_recommendations_supported"
    elif transfer_suitability == "low":
        final_advisory_decision = "transfer_recommendations_low_confidence"
    else:
        final_advisory_decision = "transfer_not_recommended"

    return {
        "build_id": BUILD_ID,
        "layer": "2.5.4 Transfer Learning Summary",
        "advisory_only": True,
        "can_change_runtime": False,

        "source_workspace_id":
            source_transfer_snapshot.get("source_workspace_id"),

        "target_workspace_id":
            target_transfer_snapshot.get("source_workspace_id"),

        "overall_similarity_score":
            overall_similarity,

        "transfer_suitability":
            transfer_suitability,

        "recommendation_strength":
            recommendation_strength,

        "recommended_success_patterns":
            recommended_success_patterns,

        "recommended_failure_patterns_to_avoid":
            recommended_failure_patterns_to_avoid,

        "recommended_anchor_purposes":
            recommended_anchor_purposes,

        "recommended_reasoning_patterns":
            recommended_reasoning_patterns,

        "final_advisory_decision":
            final_advisory_decision,

        "summary":
            {
                "source_ready":
                    bool(source_transfer_snapshot.get("transfer_summary")),

                "target_ready":
                    bool(target_transfer_snapshot.get("transfer_summary")),

                "has_similarity_analysis":
                    bool(similarity_analysis),

                "has_transfer_recommendations":
                    bool(transfer_recommendations),

                "transfer_application_mode":
                    "manual_review_only",
            },

        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "applies_learning_to_target_workspace": False,
            "metadata_only": True,
        },
    }



def validate_transfer_safety_v1(
    transfer_summary: Dict[str, Any],
) -> Dict[str, Any]:
    """
    2.5.5.1 Transfer Safety Validation.

    Advisory only:
    - Reviews transfer summary.
    - Determines whether transfer is safe enough for advisory recommendation.
    - Does NOT apply transfer learning.
    - Does NOT modify runtime, scores, targets, URLs, highlights, or linking.
    """

    overall_similarity = float(
        transfer_summary.get("overall_similarity_score") or 0
    )

    transfer_suitability = str(
        transfer_summary.get("transfer_suitability") or "unknown"
    )

    recommendation_strength = str(
        transfer_summary.get("recommendation_strength") or "unknown"
    )

    summary = (
        transfer_summary.get("summary")
        if isinstance(transfer_summary.get("summary"), dict)
        else {}
    )

    source_ready = bool(summary.get("source_ready"))
    target_ready = bool(summary.get("target_ready"))
    has_similarity_analysis = bool(summary.get("has_similarity_analysis"))
    has_transfer_recommendations = bool(summary.get("has_transfer_recommendations"))

    validation_reasons = []

    if not source_ready:
        validation_reasons.append("source_workspace_not_ready")

    if not target_ready:
        validation_reasons.append("target_workspace_not_ready")

    if not has_similarity_analysis:
        validation_reasons.append("missing_similarity_analysis")

    if not has_transfer_recommendations:
        validation_reasons.append("missing_transfer_recommendations")

    if overall_similarity <= 0:
        validation_reasons.append("no_similarity_overlap")

    if transfer_suitability in {"unknown", "insufficient_overlap"}:
        validation_reasons.append("transfer_suitability_insufficient")

    if recommendation_strength in {"unknown", "insufficient_overlap"}:
        validation_reasons.append("recommendation_strength_insufficient")

    transfer_safe = (
        source_ready
        and target_ready
        and has_similarity_analysis
        and has_transfer_recommendations
        and overall_similarity > 0
        and transfer_suitability not in {"unknown", "insufficient_overlap"}
        and recommendation_strength not in {"unknown", "insufficient_overlap"}
    )

    transfer_blocked = not transfer_safe

    return {
        "build_id": BUILD_ID,
        "layer": "2.5.5.1 Transfer Safety Validation",
        "advisory_only": True,
        "can_change_runtime": False,

        "source_workspace_id": transfer_summary.get("source_workspace_id"),
        "target_workspace_id": transfer_summary.get("target_workspace_id"),

        "transfer_safe": transfer_safe,
        "transfer_blocked": transfer_blocked,
        "validation_reasons": validation_reasons,

        "safety_inputs": {
            "overall_similarity_score": overall_similarity,
            "transfer_suitability": transfer_suitability,
            "recommendation_strength": recommendation_strength,
            "source_ready": source_ready,
            "target_ready": target_ready,
            "has_similarity_analysis": has_similarity_analysis,
            "has_transfer_recommendations": has_transfer_recommendations,
        },

        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "applies_learning_to_target_workspace": False,
            "metadata_only": True,
        },
    }
