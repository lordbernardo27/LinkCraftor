from __future__ import annotations

from typing import Any, Dict, List


def validate_bulk_apply_candidate_v1(candidate: Dict[str, Any]) -> Dict[str, Any]:
    candidate = candidate or {}

    url = str(candidate.get("url") or "").strip()
    decision = str(candidate.get("resolver_decision") or "").strip().upper()
    auto_link_allowed = bool(candidate.get("auto_link_allowed"))

    reasons = []

    if not url:
        reasons.append("missing_url")

    if decision != "AUTO_LINK":
        reasons.append("decision_not_autolink")

    if not auto_link_allowed:
        reasons.append("auto_link_not_allowed")

    allowed = bool(url) and decision == "AUTO_LINK" and auto_link_allowed

    return {
        "bulk_apply_allowed": allowed,
        "bulk_apply_reasons": reasons,
        "url": url,
        "resolver_decision": decision,
        "auto_link_allowed": auto_link_allowed,
    }


def validate_bulk_apply_batch_v1(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    checked = [validate_bulk_apply_candidate_v1(c) for c in candidates or []]

    return {
        "total": len(checked),
        "allowed": sum(1 for x in checked if x["bulk_apply_allowed"]),
        "blocked": sum(1 for x in checked if not x["bulk_apply_allowed"]),
        "results": checked,
    }
