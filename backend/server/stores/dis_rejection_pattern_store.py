from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


DATA_DIR = Path("backend/server/data/dis/rejection_patterns")

REQUIRED_TOP_LEVEL_KEYS = {
    "event_type",
    "learning_domain",
    "learning_mode",
    "workspace_id",
    "document_id",
    "vertical",
    "pipeline_stage",
    "timestamp",
    "example_rejected_candidate",
    "pattern_signature",
    "rc2_pipeline_rules",
    "privacy_and_scope",
    "future_usage",
    "evidence",
}


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _workspace_file(workspace_id: str) -> Path:
    safe = str(workspace_id or "default").strip() or "default"
    return DATA_DIR / f"{safe}.json"


def _is_valid_rejection_pattern_event(event: Dict[str, Any]) -> bool:
    if not isinstance(event, dict):
        return False

    missing = REQUIRED_TOP_LEVEL_KEYS - set(event.keys())
    if missing:
        return False

    if event.get("event_type") != "PIPELINE_REJECTION_PATTERN_LEARNED":
        return False

    if event.get("learning_domain") != "pipeline_rejection_learning":
        return False

    if event.get("learning_mode") != "rejected_candidates_only":
        return False

    if not isinstance(event.get("example_rejected_candidate"), dict):
        return False

    if not isinstance(event.get("pattern_signature"), dict):
        return False

    if not isinstance(event.get("rc2_pipeline_rules"), dict):
        return False

    if not isinstance(event.get("privacy_and_scope"), dict):
        return False

    if not isinstance(event.get("future_usage"), dict):
        return False

    if not isinstance(event.get("evidence"), dict):
        return False

    privacy = event.get("privacy_and_scope") or {}

    if privacy.get("stores_exact_phrase_as_rule") is not False:
        return False

    if privacy.get("stores_individual_words") is not False:
        return False

    if privacy.get("stores_alphabets") is not False:
        return False

    if privacy.get("stores_pattern_only") is not True:
        return False

    rules = event.get("rc2_pipeline_rules") or {}

    if rules.get("learns_from_pipeline_rejections") is not True:
        return False

    if rules.get("learns_from_pipeline_passed_candidates") is not False:
        return False

    return True


def load_rejection_pattern_events(workspace_id: str) -> List[Dict[str, Any]]:
    _ensure_dir()
    fp = _workspace_file(workspace_id)

    if not fp.exists():
        return []

    try:
        raw = json.loads(fp.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            return raw
        return []
    except Exception:
        return []


def save_rejection_pattern_events(
    workspace_id: str,
    events: List[Dict[str, Any]],
) -> Dict[str, Any]:
    _ensure_dir()

    clean_events = [
        event for event in events
        if isinstance(event, dict) and _is_valid_rejection_pattern_event(event)
    ]

    fp = _workspace_file(workspace_id)
    fp.write_text(
        json.dumps(clean_events, indent=2),
        encoding="utf-8",
    )

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "count": len(clean_events),
    }


def append_rejection_pattern_event(
    workspace_id: str,
    event: Dict[str, Any],
) -> Dict[str, Any]:
    if not _is_valid_rejection_pattern_event(event):
        return {
            "ok": False,
            "workspace_id": workspace_id,
            "count": len(load_rejection_pattern_events(workspace_id)),
            "error": "invalid_rejection_pattern_event_shape",
        }

    rows = load_rejection_pattern_events(workspace_id)
    rows.append(event)

    fp = _workspace_file(workspace_id)
    fp.write_text(
        json.dumps(rows, indent=2),
        encoding="utf-8",
    )

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "count": len(rows),
    }


def get_rejection_pattern_knowledge(
    workspace_id: str,
    vertical: Optional[str] = None,
) -> Dict[str, Any]:
    events = load_rejection_pattern_events(workspace_id)

    if vertical:
        v = str(vertical).strip().lower()
        events = [
            event for event in events
            if str(event.get("vertical", "")).strip().lower() == v
        ]

    by_pattern: Dict[str, Dict[str, Any]] = {}

    for event in events:
        signature = event.get("pattern_signature") or {}
        pattern_id = str(signature.get("pattern_id") or "").strip()

        if not pattern_id:
            continue

        if pattern_id not in by_pattern:
            by_pattern[pattern_id] = {
                "pattern_id": pattern_id,
                "verticals": set(),
                "pipeline_stages": set(),
                "failure_categories": set(),
                "failure_reasons": set(),
                "observed_count": 0,
                "latest_event": event,
            }

        row = by_pattern[pattern_id]
        row["observed_count"] += 1
        row["verticals"].add(str(event.get("vertical", "")).strip())
        row["pipeline_stages"].add(str(event.get("pipeline_stage", "")).strip())
        row["failure_categories"].add(str(signature.get("failure_category", "")).strip())
        row["failure_reasons"].add(str(signature.get("failure_reason", "")).strip())
        row["latest_event"] = event

    normalized = []

    for row in by_pattern.values():
        normalized.append({
            "pattern_id": row["pattern_id"],
            "verticals": sorted([x for x in row["verticals"] if x]),
            "pipeline_stages": sorted([x for x in row["pipeline_stages"] if x]),
            "failure_categories": sorted([x for x in row["failure_categories"] if x]),
            "failure_reasons": sorted([x for x in row["failure_reasons"] if x]),
            "observed_count": row["observed_count"],
            "latest_event": row["latest_event"],
        })

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "vertical": vertical,
        "event_count": len(events),
        "pattern_count": len(normalized),
        "patterns": normalized,
    }
