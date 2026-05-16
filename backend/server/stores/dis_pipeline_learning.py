from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.server.stores.dis_pattern_signature import build_rejection_pattern_signature
from backend.server.stores.dis_rejection_pattern_store import append_rejection_pattern_event


VALID_PIPELINE_STAGES = {
    "smart_extractor",
    "candidate_window_guard",
    "phrase_strength_scorer",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sample_phrase_from_candidate(candidate: Any) -> str:
    if isinstance(candidate, dict):
        return str(
            candidate.get("phrase")
            or candidate.get("text")
            or candidate.get("candidate")
            or candidate.get("value")
            or ""
        ).strip()

    return str(candidate or "").strip()


def build_pipeline_rejection_learning_event(
    *,
    workspace_id: str,
    document_id: str,
    vertical: str,
    pipeline_stage: str,
    candidate: Any,
    rejection_reason: Any,
    evidence: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    stage = str(pipeline_stage or "").strip().lower()

    if stage not in VALID_PIPELINE_STAGES:
        stage = "unknown_pipeline_stage"

    signature = build_rejection_pattern_signature(
        candidate=candidate,
        rejection_reason=rejection_reason,
        pipeline_stage=stage,
        vertical=vertical or "general",
    )

    return {
        "event_type": "PIPELINE_REJECTION_PATTERN_LEARNED",
        "learning_domain": "pipeline_rejection_learning",
        "learning_mode": "rejected_candidates_only",

        "workspace_id": workspace_id,
        "document_id": document_id,
        "vertical": str(vertical or "general").strip().lower() or "general",
        "pipeline_stage": stage,
        "timestamp": _utc_now(),

        "example_rejected_candidate": {
            "sample_phrase": _sample_phrase_from_candidate(candidate),
            "stored_for_debug_only": True,
            "used_for_matching": False,
            "used_as_rule": False
        },

        "pattern_signature": signature,

        "rc2_pipeline_rules": {
            "learns_from_pipeline_rejections": True,
            "learns_from_pipeline_passed_candidates": False,
            "learns_from_active_phrase_pool_candidates": False,
            "learns_from_editor_highlighted_candidates": False,
            "learns_from_user_approved_editor_phrases": False,
            "learns_from_accepted_link_decisions": False
        },

        "privacy_and_scope": {
            "stores_exact_phrase_as_rule": False,
            "stores_individual_words": False,
            "stores_alphabets": False,
            "stores_pattern_only": True
        },

        "future_usage": {
            "used_by": [
                "highlight_selection_engine",
                "highlight_density_engine"
            ],
            "purpose": "avoid_selecting_candidates_with_matching_rejection_signature",
            "can_filter_current_pipeline": False,
            "can_inform_future_selection": True
        },

        "evidence": evidence or {
            "observed_rejection_count": 1,
            "affected_documents_count": 1,
            "affected_verticals": [str(vertical or "general").strip().lower() or "general"],
            "confidence": 0.50
        }
    }


def learn_from_pipeline_rejection(
    *,
    workspace_id: str,
    document_id: str,
    vertical: str,
    pipeline_stage: str,
    candidate: Any,
    rejection_reason: Any,
    evidence: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    event = build_pipeline_rejection_learning_event(
        workspace_id=workspace_id,
        document_id=document_id,
        vertical=vertical,
        pipeline_stage=pipeline_stage,
        candidate=candidate,
        rejection_reason=rejection_reason,
        evidence=evidence,
    )

    return append_rejection_pattern_event(workspace_id, event)
