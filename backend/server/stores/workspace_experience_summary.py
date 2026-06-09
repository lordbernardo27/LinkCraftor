
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



SUCCESS_PATTERN_RULES = {
    "strong_reasoning_support": {
        "keys": ["logical_inference", "decision"],
        "values": ["strong_reasoning_support"],
    },
    "moderate_analogical_support": {
        "keys": ["analogical_reasoning", "decision"],
        "values": ["moderate_analogical_support", "strong_analogical_support"],
    },
    "high_anchor_purpose_alignment": {
        "keys": ["anchor_purpose", "confidence"],
        "min_value": 0.70,
    },
    "high_final_score": {
        "keys": ["score"],
        "min_value": 0.70,
    },
    "accepted_user_feedback": {
        "keys": ["feedback", "accepts"],
        "min_value": 1,
    },
}


def _nested_get(data: Dict[str, Any], keys: List[str]) -> Any:
    cur: Any = data
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def aggregate_success_patterns_v1(
    decision_items: List[Dict[str, Any]] | None = None,
    max_patterns: int = 10,
) -> Dict[str, Any]:
    """
    2.4.5.2 Success Pattern Aggregation.

    Advisory only:
    - Reads existing decision/result metadata.
    - Aggregates recurring positive patterns.
    - Does not change scoring, targets, URLs, highlights, or runtime.
    """

    decision_items = decision_items or []
    pattern_counts: Dict[str, int] = {}

    accepted_count = 0

    for item in decision_items:
        if not isinstance(item, dict):
            continue

        feedback = item.get("feedback") if isinstance(item.get("feedback"), dict) else {}
        accepted = bool(item.get("accepted")) or int(feedback.get("accepts") or 0) > 0

        if accepted:
            accepted_count += 1

        for pattern_name, rule in SUCCESS_PATTERN_RULES.items():
            value = _nested_get(item, rule.get("keys", []))

            matched = False

            if "values" in rule:
                matched = value in rule["values"]

            elif "min_value" in rule:
                try:
                    matched = float(value or 0) >= float(rule["min_value"])
                except Exception:
                    matched = False

            if matched:
                pattern_counts[pattern_name] = pattern_counts.get(pattern_name, 0) + 1

    ranked = sorted(
        pattern_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:max_patterns]

    return {
        "build_id": BUILD_ID,
        "layer": "2.4.5.2 Success Pattern Aggregation",
        "advisory_only": True,
        "can_change_runtime": False,
        "input_decision_items": len(decision_items),
        "accepted_count": accepted_count,
        "top_success_patterns": [
            {"pattern": name, "count": count}
            for name, count in ranked
        ],
        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "metadata_only": True,
        },
    }



FAILURE_PATTERN_RULES = {
    "weak_reasoning_support": {
        "keys": ["logical_inference", "decision"],
        "values": ["weak_reasoning_support"],
    },
    "weak_analogical_support": {
        "keys": ["analogical_reasoning", "decision"],
        "values": ["weak_analogical_support"],
    },
    "low_anchor_purpose_confidence": {
        "keys": ["anchor_purpose", "confidence"],
        "max_value": 0.30,
    },
    "low_final_score": {
        "keys": ["score"],
        "max_value": 0.30,
    },
    "rejected_user_feedback": {
        "keys": ["feedback", "rejects"],
        "min_value": 1,
    },
    "dis_rejection_pattern_match": {
        "keys": ["dis_pattern_match"],
        "values": [True],
    },
    "low_target_relevance": {
        "keys": ["di_score_adjustments", "target_score"],
        "max_value": 0.20,
    },
}


def aggregate_failure_patterns_v1(
    decision_items: List[Dict[str, Any]] | None = None,
    max_patterns: int = 10,
) -> Dict[str, Any]:
    """
    2.4.5.3 Failure Pattern Aggregation.

    Advisory only:
    - Reads existing decision/result metadata.
    - Aggregates recurring negative/rejection patterns.
    - Does not change scoring, targets, URLs, highlights, or runtime.
    """

    decision_items = decision_items or []
    pattern_counts: Dict[str, int] = {}

    rejected_count = 0

    for item in decision_items:
        if not isinstance(item, dict):
            continue

        feedback = item.get("feedback") if isinstance(item.get("feedback"), dict) else {}
        rejected = bool(item.get("rejected")) or int(feedback.get("rejects") or 0) > 0

        if rejected:
            rejected_count += 1

        for pattern_name, rule in FAILURE_PATTERN_RULES.items():
            value = _nested_get(item, rule.get("keys", []))

            matched = False

            if "values" in rule:
                matched = value in rule["values"]

            elif "min_value" in rule:
                try:
                    matched = float(value or 0) >= float(rule["min_value"])
                except Exception:
                    matched = False

            elif "max_value" in rule:
                try:
                    matched = float(value or 0) <= float(rule["max_value"])
                except Exception:
                    matched = False

            if matched:
                pattern_counts[pattern_name] = pattern_counts.get(pattern_name, 0) + 1

    ranked = sorted(
        pattern_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:max_patterns]

    return {
        "build_id": BUILD_ID,
        "layer": "2.4.5.3 Failure Pattern Aggregation",
        "advisory_only": True,
        "can_change_runtime": False,
        "input_decision_items": len(decision_items),
        "rejected_count": rejected_count,
        "top_failure_patterns": [
            {"pattern": name, "count": count}
            for name, count in ranked
        ],
        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "metadata_only": True,
        },
    }



def build_decision_intelligence_summary_v1(
    workspace_id: str,
    decision_items: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    2.4.5.4 Decision Intelligence Summary.

    Advisory only:
    - Summarizes existing decision metadata.
    - Reuses success and failure aggregation.
    - Does not create decisions.
    - Does not modify scores, targets, URLs, highlights, or runtime.
    """

    decision_items = decision_items or []

    accepted = 0
    rejected = 0
    anchor_purpose_counts: Dict[str, int] = {}
    reasoning_counts: Dict[str, int] = {}

    for item in decision_items:
        if not isinstance(item, dict):
            continue

        feedback = item.get("feedback") if isinstance(item.get("feedback"), dict) else {}

        is_accepted = bool(item.get("accepted")) or int(feedback.get("accepts") or 0) > 0
        is_rejected = bool(item.get("rejected")) or int(feedback.get("rejects") or 0) > 0

        if is_accepted:
            accepted += 1
        if is_rejected:
            rejected += 1

        anchor_purpose = (
            item.get("anchor_purpose", {}).get("primary_purpose")
            if isinstance(item.get("anchor_purpose"), dict)
            else None
        )
        if anchor_purpose:
            anchor_purpose_counts[anchor_purpose] = anchor_purpose_counts.get(anchor_purpose, 0) + 1

        logical_decision = (
            item.get("logical_inference", {}).get("decision")
            if isinstance(item.get("logical_inference"), dict)
            else None
        )
        analogical_decision = (
            item.get("analogical_reasoning", {}).get("decision")
            if isinstance(item.get("analogical_reasoning"), dict)
            else None
        )

        for d in [logical_decision, analogical_decision]:
            if d:
                reasoning_counts[d] = reasoning_counts.get(d, 0) + 1

    total = len(decision_items)
    acceptance_rate = round(accepted / total, 4) if total else 0.0
    rejection_rate = round(rejected / total, 4) if total else 0.0

    success = aggregate_success_patterns_v1(decision_items)
    failure = aggregate_failure_patterns_v1(decision_items)

    dominant_anchor_purposes = [
        {"purpose": k, "count": v}
        for k, v in sorted(anchor_purpose_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    dominant_reasoning_patterns = [
        {"pattern": k, "count": v}
        for k, v in sorted(reasoning_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    most_successful_pattern = (
        success.get("top_success_patterns", [{}])[0].get("pattern")
        if success.get("top_success_patterns")
        else None
    )

    largest_failure_pattern = (
        failure.get("top_failure_patterns", [{}])[0].get("pattern")
        if failure.get("top_failure_patterns")
        else None
    )

    if total == 0:
        workspace_health = "no_decision_data"
    elif acceptance_rate >= 0.80 and rejection_rate <= 0.20:
        workspace_health = "healthy"
    elif acceptance_rate >= 0.60:
        workspace_health = "watch"
    else:
        workspace_health = "needs_review"

    return {
        "build_id": BUILD_ID,
        "layer": "2.4.5.4 Decision Intelligence Summary",
        "advisory_only": True,
        "can_change_runtime": False,
        "workspace_id": workspace_id,
        "total_decisions": total,
        "accepted_decisions": accepted,
        "rejected_decisions": rejected,
        "acceptance_rate": acceptance_rate,
        "rejection_rate": rejection_rate,
        "top_success_patterns": success.get("top_success_patterns", []),
        "top_failure_patterns": failure.get("top_failure_patterns", []),
        "dominant_anchor_purposes": dominant_anchor_purposes,
        "dominant_reasoning_patterns": dominant_reasoning_patterns,
        "summary": {
            "most_successful_pattern": most_successful_pattern,
            "largest_failure_pattern": largest_failure_pattern,
            "workspace_health": workspace_health,
        },
        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "metadata_only": True,
        },
    }



def build_learning_snapshot_v1(
    workspace_id: str,
    decision_items: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    2.4.5.5 Learning Snapshot Builder.

    Advisory only:
    - Reads existing learning outputs.
    - Reads decision intelligence summaries.
    - Builds a workspace learning snapshot.
    - Does not change runtime.
    - Does not change scores.
    - Does not change targets.
    - Does not change URLs.
    """

    decision_items = decision_items or []

    decision_summary = build_decision_intelligence_summary_v1(
        workspace_id=workspace_id,
        decision_items=decision_items,
    )

    return {
        "build_id": BUILD_ID,
        "layer": "2.4.5.5 Learning Snapshot Builder",
        "advisory_only": True,
        "can_change_runtime": False,

        "workspace_id": workspace_id,

        "learning_snapshot": {
            "top_success_patterns":
                decision_summary.get("top_success_patterns", []),

            "top_failure_patterns":
                decision_summary.get("top_failure_patterns", []),

            "dominant_anchor_purposes":
                decision_summary.get(
                    "dominant_anchor_purposes",
                    [],
                ),

            "dominant_reasoning_patterns":
                decision_summary.get(
                    "dominant_reasoning_patterns",
                    [],
                ),

            "workspace_health":
                decision_summary.get(
                    "summary",
                    {},
                ).get(
                    "workspace_health"
                ),

            "most_successful_pattern":
                decision_summary.get(
                    "summary",
                    {},
                ).get(
                    "most_successful_pattern"
                ),

            "largest_failure_pattern":
                decision_summary.get(
                    "summary",
                    {},
                ).get(
                    "largest_failure_pattern"
                ),
        },

        "snapshot_metadata": {
            "generated_from_existing_memory_layers": True,
            "generated_from_decision_intelligence": True,
            "generated_from_success_patterns": True,
            "generated_from_failure_patterns": True,
        },

        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "metadata_only": True,
        },
    }
