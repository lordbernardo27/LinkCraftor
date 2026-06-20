from __future__ import annotations

from typing import Any, Dict, List

from backend.server.engine.bulk_apply_safety_validator import (
    validate_bulk_apply_batch_v1,
)


def prepare_bulk_apply_v1(
    candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Backend safety gate for bulk apply.

    This does not mutate editor content yet.
    It separates safe AUTO_LINK candidates from blocked candidates.
    """
    validation = validate_bulk_apply_batch_v1(candidates)

    safe_items = []
    blocked_items = []

    for candidate, check in zip(candidates or [], validation.get("results") or []):
        item = dict(candidate or {})
        item["bulk_apply_safety"] = check

        if check.get("bulk_apply_allowed"):
            safe_items.append(item)
        else:
            blocked_items.append(item)

    return {
        "bulk_apply_ready": True,
        "total": validation.get("total"),
        "allowed": validation.get("allowed"),
        "blocked": validation.get("blocked"),
        "safe_items": safe_items,
        "blocked_items": blocked_items,
    }
